# -*- coding: utf-8 -*-
"""Main."""

import argparse
import threading
import os.path
import sys
import time
import collections
import pandas
import pyqtgraph as pg
from pyqtgraph import exporters as exp
from PyQt5 import QtGui, QtCore, QtWidgets
from pooqi.network import pooqi_connection as epc
from pooqi.hmi import hmi_pq as hmi
from pooqi.tools.all_constants import DEFAULT_DATA_FILE
from pooqi.tools.all_constants import DEFAULT_CONFIG_FILE
from pooqi.tools.all_constants import DEFAULT_PORT
from pooqi.tools.all_constants import DEFAULT_REFRESH_PERIOD
from pooqi.tools.all_constants import DEFAULT_ABSCISSA
from pooqi.tools.all_constants import SEPARATION_VALUE
from pooqi.tools.all_constants import VERSION
from pooqi.tools import plot_classes


class CloseEventError(Exception):

    ''' exception to raise when user close the gui '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class WriteWindow(QtCore.QObject):

    """ Recover datas """

    runWriteCurves = QtCore.pyqtSignal()

    def __init__(self, win, data_file_list, sort, printable,
                 export_file=None, export_size=None):
        super(WriteWindow, self).__init__()

        self.data_dict = collections.OrderedDict()

        self.user_select_ts = False
        self.win = win
        self.data_file_list = data_file_list
        self.sort = sort
        self.printable = printable
        self.export_file = export_file
        self.export_size = export_size

        self.runWriteCurves.connect(self.write_curves)
        self.continue_ = True

        self.thread = threading.Thread(target=self.__panda_thread)
        self.thread.daemon = True
        self.thread.start()

    def __panda_thread(self):
        ''' thread '''

        try:
            # concate all csv files
            try:
                abscissa = self.win.abscissa
                column = self.win.parameters.curves.keys()
                # columns.append(abscissa)
                columns = []
                for each in column:
                    columns.append(each)
                columns.append(abscissa)
                if abscissa == 'Timestamp':
                    self.user_select_ts = True
                if 'Timestamp' not in columns:
                    columns.append('Timestamp')

                time_print = 0.02

                for file_ in self.data_file_list:
                    self.win.loading.loadState.emit('Checking %s' % file_)
                    time.sleep(time_print)

                    with open(file_, 'r') as fic:
                        head = fic.readline().replace(
                            '\n', '').replace('\r', '').split(',')

                    columns_cp = list(columns)
                    for elemt in columns_cp:
                        if elemt not in head:
                            columns.pop(columns.index(elemt))

                            if elemt != 'Timestamp' and \
                                    SEPARATION_VALUE not in elemt:
                                print(''.join(["\033[93mWARNING: %s" % elemt,
                                               " is not in CSV file.\033[0m"]))

                col_used = [col for col in columns
                            if SEPARATION_VALUE not in col]

                files_list = []
                for file_ in self.data_file_list:
                    self.win.loading.loadState.emit('Reading %s' % file_)
                    time.sleep(time_print)

                    files_list.append(pandas.read_csv(
                        file_,  usecols=col_used,
                        engine='c', header=0, low_memory=False))

                if len(self.data_file_list) > 1:
                    self.win.loading.loadState.emit('Concatenating files')
                    time.sleep(time_print)

                data_dict = pandas.concat(files_list).to_dict('list')
            except TypeError as err:
                print('\033[91mERROR: %s' % err)
                print('Maybe you must upgrade python-pandas\033[0m')
                self.continue_ = False

            if not self.user_select_ts:
                if len(self.data_file_list) > 1 and\
                        abscissa == 'Time' and 'Timestamp' in data_dict.keys():
                    print('Pooqi is using Timestamp instead of Time')
                    abscissa = 'Timestamp'

            # Check abscissa exists in the .csv
            # Check the non-numeric value and advice user to delete
            # them from .csv
            # file
            try:
                if self.continue_ and\
                        type(data_dict[abscissa][0]) == str:
                    print(''.join(["\033[91mERROR:",
                                   " Some values from abscissa",
                                   " data are not numeric.",
                                   "\n               ",
                                   "Please delete them and",
                                   " restart the program.",
                                   "\033[0m"]))
                    self.continue_ = False
            except KeyError:
                print(''.join(["\033[91mERROR: %s, defined as" % abscissa,
                               " abscissa, is not in CSV file.\033[0m"]))
                self.continue_ = False

            # Check each data exists in csv and recover it
            # or advice user and delete it
            # from data_dict.
            # Check there is no non-numeric value in the desired data.
            # Treatment of the keys one by one
            # in order to know each keys
            # which are not in the .csv
            if self.continue_:
                for key in self.win.parameters.curves.keys():
                    self.win.loading.loadState.emit('Treating %s' % key)
                    time.sleep(time_print)

                    if SEPARATION_VALUE in key:
                        key = key.split(SEPARATION_VALUE)[0]
                    try:
                        if type(data_dict[key][0]) == str:
                            print(''.join(["\033[93mWARNING: Some values from",
                                           " %s curve are not numeric." % key]))
                            print(
                                "     This curve will not be plotted.\033[0m")
                            del self.win.parameters.curves[key]
                        else:
                            init_time = 0
                            if not self.user_select_ts:
                                if abscissa == 'Timestamp':
                                    init_time = data_dict[abscissa][0]
                                    self.win.label_x = 'Time'
                                    self.win.unit_x = 's'
                            for cpt in range(len(data_dict[key])):
                                data_x = data_dict[abscissa][cpt] - init_time
                                data_y = data_dict[key][cpt]
                                cur_curve = self.data_dict.setdefault(key, {})
                                cur_curve.update(
                                    {cpt: plot_classes.Data(data_x, data_y)})

                    except KeyError:
                        print("\033[93mWARNING: %s is not in CSV file.\033[0m"
                              % key)
                        try:
                            del self.win.parameters.curves[key]
                        except KeyError:
                            pass

            self.win.loading.loadState.emit('Writing curves...')
            time.sleep(time_print)
            self.runWriteCurves.emit()
        except CloseEventError:
            pass

    def write_curves(self):
        ''' write curves '''
        if not self.continue_:
            pg.exit()

        self.win.remove_loading_image()
        try:
            self.win.create_all()
        except RuntimeError:
            print('Sorry, an error occured with pyqtgraph')
            print('Please restart Pooqi')
            print('If this problem append again, try to use -p option')
            pg.exit()

        self.win.fill_curves_dict()

        # Add points to the curves

        if self.sort is True:
            print('Datas will be sorted')

        for curve_name in self.win.parameters.curves.keys():

            if SEPARATION_VALUE in curve_name:
                curve = curve_name.split(SEPARATION_VALUE)[0]
            else:
                curve = curve_name

            try:
                datas_num = self.data_dict[curve].keys()

                if self.sort is True:
                    datas_dic = {self.data_dict[
                        curve][num].data_x: self.data_dict[
                        curve][num].data_y for num in datas_num}

                    datas_x = sorted(datas_dic.keys())
                    datas_y = [datas_dic[x_value] for x_value in datas_x]

                else:
                    # datas_num = sorted(datas_num)
                    datas_x = [
                        self.data_dict[curve][num].data_x
                        for num in datas_num]
                    datas_y = [
                        self.data_dict[curve][num].data_y
                        for num in datas_num]

                [self.win.add_point(curve_name, data_x, data_y, False)
                    for data_x, data_y in zip(datas_x, datas_y)]
            except KeyError:
                pass

        # Create curves
        for curve in self.win.curves:
            self.win.curve_display(curve)

        for fig in self.win.figures.values():
            fig.scale_if_needed()

        # In case of plotting from CSV file(s), hide buttons
        if self.printable is False:
            [fig.custom_plot.header.hide_all_buttons()
             for fig in self.win.figures.values()]

        if self.export_file is None:
            [fig.mouse_tracking.update()
             for fig in self.win.figures.values()
             if fig.mouse_tracking is not None]
        else:
            if self.export_size is not None:
                self.export_and_close(self.export_size[0], self.export_size[1])
            else:
                self.export_and_close()

        # TODO:find a way to avoid the strange bug cleanly
        sys.tracebacklimit = 0
        raise Exception("\r==================================================")

    def export_and_close(self, sizex=1920, sizey=1080):
        """ export scene and force window to close """
        print("Exporting : %s" % self.export_file)
        QtWidgets.QApplication.processEvents()
        self.win.resize(sizex, sizey)
        to_exp = exp.ImageExporter(self.win.scene())
        to_exp.export(self.export_file)
        self.win.close()


def chose_config_file(esp_is_file, esp_file_path, config_files_list):
    ''' return config file choise '''

    if esp_is_file:
        config_file = esp_file_path
    else:
        if (esp_file_path[len(esp_file_path) - 1] != "/" and
                esp_file_path[len(esp_file_path) - 1] != "\\"):
            esp_file_path += "/"

        config_files_list = sorted(config_files_list)

        if len(config_files_list) == 1:
            print("\033[94mYou are using %s.\033[93m" %
                  config_files_list[0])
            config_file = ''.join([esp_file_path, config_files_list[0]])
        else:
            print(''.join()
                  ["\033[94m",
                   "Which configuration file do you want to use?\033[93m"])
            total_space = 0
            mod = 10
            for cpt in range(len(config_files_list)):
                if cpt % mod == 0:
                    total_space += 1
                    mod = mod * 10

            index = 1
            mod = 10
            max_space = total_space
            for conf_file in config_files_list:
                spaces = ''.join([' ' for i in range(total_space)])
                print(''.join([spaces, "%d : %s" % (index, conf_file)]))
                index += 1
                if index % mod == 0:
                    total_space -= 1
                    mod = mod * 10

            spaces = ''.join([' ' for i in range(max_space)])
            print(''.join([spaces, "0 : Exit program\033[0m"]))

            user_input = -1
            while (user_input > len(config_files_list) or user_input < 0):
                user_input = input("".join(["Please enter the ",
                                            "desired number : "]))
                try:
                    user_input = int(user_input)
                    if user_input != 0:
                        print('You have chosen \033[93m%s\033[0m\n' %
                              config_files_list[user_input - 1])
                except (ValueError, IndexError):
                    print(''.join([
                        "\033[93m%s" % user_input,
                        "\033[91m is not a valid choice.\n",
                        "Please enter a number among",
                        " those proposed.\033[0m"]))
                except KeyboardInterrupt:
                    user_input = 0

            if user_input == 0:
                return None
            else:
                config_file = ''.join([esp_file_path,
                                       config_files_list[user_input - 1]])

    return config_file


def pooqi_main(esp_file_path, data_file_list, server_ip, port,
               refresh_period, printable, sort, abscissa, mult=None, export=None,
               export_size=None):
    """Read the configuration file, the data file and plot"""

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Pooqi')

    print('\033[95m----- Welcome in Pooqi v.%s -----\033[0m\n' % VERSION)

    try:
        id_wav = [cpt for cpt in range(
            len(data_file_list)) if ".wav" in data_file_list[cpt]]
        wav_list = [data_file_list[cpt] for cpt in id_wav]
        for cpt in sorted(id_wav, reverse=True):
            del data_file_list[cpt]

        if len(data_file_list) > 1 and sort is False and server_ip is None:
            yes = set(['YES', 'Y', 'yes', 'y', 'ye', ''])
            no_ = set(['NO', 'N', 'no', 'n'])
            continu = True
            while continu:
                print("You have parsed several data files.")
                print(''.join(["\033[94mDo you want to sort datas on abscissa?",
                               " \033[93m(YES/no)\033[0m"]))
                choice = input().lower()
                if choice in yes:
                    sort = True
                    continu = False
                    print(''.join(["Abscissa's datas will be \033[93msorted",
                                   " by ascending order\n\033[0m"]))
                elif choice in no_:
                    continu = False
                else:
                    sys.stdout.write(''.join(["\033[91mPlease respond with",
                                              " \033[93m'yes' or 'no'\033[0m",
                                              "\n\n"]))
    except KeyboardInterrupt:
        pass

    # Check if configuration file path exists
    # and if it is a file or a directory
    esp_is_file = True  # DEFAULT_CONFIG_FILE by default
    if os.path.isdir(esp_file_path):
        esp_is_file = False
    elif not os.path.isfile(esp_file_path):
        print("\033[91mERROR: File or folder '%s' cannot be found\033[0m" %
              esp_file_path)
        pg.exit()

    # Recover the list of configuration files if cfg_file_path is a directory
    config_files_list = []
    if not esp_is_file:
        files_list = os.listdir(esp_file_path)
        for file_ in files_list:
            if os.path.splitext(file_)[1] == ".esp":
                config_files_list.append(file_)

    # Error if there is no configuration file in the directory
    if not esp_is_file and len(config_files_list) < 1:
        print(''.join((["\033[91mERROR: There is no .esp file",
                        " in the folder '%s'\033[0m"
                        % esp_file_path])))
        pg.exit()

    # Test if all data files exist
    for data_file in data_file_list:
        if not os.path.isfile(data_file):
            print("\033[91mERROR: File '%s' cannot be found\033[0m" %
                  data_file)
            pg.exit()

    continue_ = True
    while continue_:

        if esp_is_file:
            continue_ = False
        try:
            config_file = chose_config_file(
                esp_is_file, esp_file_path, config_files_list)
            if config_file is None:
                continue_ = False
            else:

                if server_ip is not None:
                    print('Real Time Plotting')
                    win = hmi.Window(app, config_file=config_file,
                                     printable=printable, is_rt=True)
                    win.remove_loading_image()
                    win.create_all()
                    win.fill_curves_dict()
                    # In case of plotting from a socket,
                    # begin to ask (in another thread)
                    # if datas are avaible and plot them
                    client = epc.Client(win, server_ip, port, refresh_period)
                else:
                    # Create the window

                    # TODO: don't forget to clear this when bug will be
                    # corrected
                    sys.tracebacklimit = 42
                    # ==========================================================

                    win = hmi.Window(app, config_file=config_file,
                                     printable=printable, is_rt=False,
                                     user_abscissa=abscissa, wav_list=wav_list,
                                     mult=mult)
                    wwi = WriteWindow(win, data_file_list, sort, printable,
                                      export_file=export,
                                      export_size=export_size)

                # Display the window
                win.run()
                sys.exit(app.exec_())

                try:
                    raise CloseEventError('Application closed by User')
                except CloseEventError:
                    print

                if server_ip is not None:
                    client.stop()
                else:
                    del wwi
                del win

        except (KeyboardInterrupt, SystemExit):
            continue_ = False

    print('\033[95m----- End of Program -----\033[0m\n')
    pg.exit()


def main():

    PARSER = argparse.ArgumentParser(
        description="Plot datas from a CSV file or/and audio file")

    PARSER.add_argument("data_file_list", metavar="DATAFILE", nargs="*",
                        default=DEFAULT_DATA_FILE,
                        help="Input CSV data files and/or wav file")

    PARSER.add_argument("-c", "--configFile", dest="esp_file_path",
                        default=DEFAULT_CONFIG_FILE,
                        help="configuration plot file or folder\
                        (default: " + DEFAULT_CONFIG_FILE + ")")

    PARSER.add_argument("--export", dest="export",
                        default=None,
                        help="+path : Export figure without open pooqi")

    PARSER.add_argument("--export_size", dest="export_size",
                        default=None,
                        help="+x,y : Size of exported figure in pixels")

    PARSER.add_argument("-p", "--printable", dest="printable",
                        action="store_const",
                        const=True, default=False,
                        help="add option to run printable pooqi plotter")

    PARSER.add_argument("-i", "--IP", dest="server_ip",
                        default=None,
                        help="server IP address")

    PARSER.add_argument("-a", "--abscissa", dest="abscissa",
                        default=None,
                        help=''.join([
                            "Data to use as abscissa.",
                            "If it is not define here, it uses the data define",
                            " in the configuration file if there is one.",
                            " If it is not specified in .esp file too, ",
                            "default data is %s. " % DEFAULT_ABSCISSA,
                            "You can write 'Data,Unit' to define the unit"]))

    PARSER.add_argument("-po", "--port", dest="port", default=DEFAULT_PORT,
                        type=int,
                        help="server port (default: " + str(DEFAULT_PORT) + ")")

    PARSER.add_argument("--mult", dest="mult", default=None,
                        type=int, help="multiplication on all values")

    PARSER.add_argument("-r", "--refresh-period", dest="refresh_period",
                        type=float, default=DEFAULT_REFRESH_PERIOD,
                        help="refresh period for real time plot\
                        (default: 0.1s)")

    PARSER.add_argument("-s", "--sort", dest="sort",
                        action="store_const",
                        const=True, default=False,
                        help="sort datas on abscissa\
                        (automatic with several data files)")

    PARSER.add_argument("-v", "--version", action="version",
                        version="Pooqi v.%s" % VERSION)

    ARGS = PARSER.parse_args()

    if ARGS.server_ip is not None:
        ARGS.data_file_list = []

    printable = ARGS.printable
    SIZE = None
    if ARGS.export is not None:
        printable = True
        if ARGS.export_size is not None:
            try:
                SIZE = [int(val) for val in ARGS.export_size.split(',')]
                if len(SIZE) != 2:
                    print("Error with size of exported figure")
                    exit()
            except BaseException:
                print("Error with size of exported figure")
                exit()

    pooqi_main(ARGS.esp_file_path, ARGS.data_file_list,
               ARGS.server_ip, ARGS.port, ARGS.refresh_period, printable,
               ARGS.sort, ARGS.abscissa, ARGS.mult, ARGS.export, SIZE)


if __name__ == '__main__':
    main()
