# -*- coding: utf-8 -*-
"""Read esp."""

import pyqtgraph as pg
from PyQt5 import QtCore
from pooqi.tools import pq_tools
from pooqi.pq_reading import reading_tools as rt
from pooqi.pq_reading import reading_classes as rc
from pooqi.tools.all_constants import GENERAL_SECTION
from pooqi.tools.all_constants import CURVES_SECTION
from pooqi.tools.all_constants import DEFAULT_MIN
from pooqi.tools.all_constants import DEFAULT_MAX
from pooqi.tools.all_constants import MAX_COLOR_VALUE
from pooqi.tools.all_constants import MIN_COLOR_VALUE
from pooqi.tools.all_constants import DIC_COLOR


class Parameters(object):

    """Contains all parameters of configuration file"""

    def __init__(self, config_file_path):
        self.figures = {}
        self.curves = {}

        try:
            conf_dic = pq_tools.read_config_file(config_file_path)
        except BaseException:
            print("Oops ! An error occured during configuration file reading")
            print("Please, check configuration file's syntaxe")
            exit()

        # General parameters
        try:
            general_dic = conf_dic[GENERAL_SECTION]

            try:
                self.max_time = int(general_dic["MaxTime"][0])
            except BaseException:
                self.max_time = None

            try:
                self.title = str(' '.join(general_dic["Title"]))
            except BaseException:
                self.title = None

            try:
                rep = "True" in general_dic["Anti-aliasing"][0]
                self.anti_aliasing = rep
            except BaseException:
                self.anti_aliasing = True

            try:
                rep = "True" in general_dic["LinkXAll"][0]
                self.link_x_all = rep
            except BaseException:
                self.link_x_all = False

            try:
                rep = "True" in general_dic["ForceTimeToZero"][0]
                self.x_to_zero = rep
            except BaseException:
                self.x_to_zero = False

            try:
                rep = "True" in general_dic["PrintWhiteBackground"][0]
                self.whitebackground = rep
            except BaseException:
                self.whitebackground = False

            try:
                rep = "True" in general_dic["UseDarkColor"][0]
                self.darkcolor = rep
            except BaseException:
                self.darkcolor = False

            try:
                mtrack = general_dic["MouseTrack"]
                if mtrack[0] != "False":
                    try:
                        if len(mtrack[0]) > 1 and mtrack[0][0] != '#':
                            cline = DIC_COLOR[mtrack[0]]
                        else:
                            cline = mtrack[0]

                        if len(mtrack[1]) > 1 and mtrack[1][0] != '#':
                            ctext = DIC_COLOR[mtrack[1]]
                        else:
                            ctext = mtrack[1]

                        if len(mtrack[2]) > 1 and mtrack[2][0] != '#':
                            ccross = DIC_COLOR[mtrack[2]]
                        else:
                            ccross = mtrack[2]

                        self.mtrack = {
                            'cline': cline,
                            'ctext': ctext,
                            'ccross': ccross}

                    except (BaseException):
                        self.mtrack = 'default'
                else:
                    self.mtrack = None
            except (KeyError, IndexError):
                self.mtrack = None

            try:
                self.abscissa = " ".join(general_dic["Abscissa"])
            except (KeyError, IndexError):
                self.abscissa = "Time"

            try:
                self.label_x = " ".join(general_dic["LabelX"])
            except (KeyError, IndexError):
                self.label_x = self.abscissa

            try:
                self.unit_x = " ".join(general_dic["UnitX"])
            except (KeyError, IndexError):
                self.unit_x = None

        except (IndexError, KeyError):
            print("Pooqi configuration file MUST have a section named")
            print("%s like the one following :" % GENERAL_SECTION)
            print
            print("[ %s ]" % GENERAL_SECTION)
            print("MaxTime         : [maximum time]")
            print("Title           : [title]")
            print("Abscissa        : [abscissa]")
            print("LabelX          : [label of x axis]")
            print("UnitX           : [unit of x axis]")
            print("Anti-aliasing   : [anti aliasing]")
            print("LinkXAll        : [link all x axis]")
            print("MouseTrack      : [Mouse tracking]")
            print
            print("where :")
            print("- [number of rows] is the number of rows")
            print("- [number of columns] is the number of colums")
            print("- [maximum time] is the maximum time of each curve")
            print("- [title] is the title of the window")
            print("- [abscissa] is the name of abscissa in cvs file")
            print("- [label of x axis] is the label of x axis")
            print("- [unit of x axis] is the unit of x axis")
            print("- [anti aliasing] is True if you want anti aliasing to be")
            print("  applied to the window, False else")
            print(
                "- [link all x axis] is True if you want to link all x axis,")
            print("  False else")
            print(
                "- [Mouse tracking] is if you want to have values on graphs")
            print("  when you put your mouse.")
            print("  You must put color_line, color_text and color_cross")
            exit()

        except (ValueError, TypeError):
            print("There is a no valid value on %s section" % GENERAL_SECTION)
            print("Please, respect the following format :")
            print("- [number of rows] is an integer")
            print("- [number of columns] is an integer")
            print("- [maximum time] is an integer")
            print("- [title] is a string")
            print("- [abscissa] is a string")
            print("- [label of x axis] is a string")
            print("- [unit of x axis] is a string")
            print("- [anti aliasing] is True if you want anti aliasing to be")
            print("  applied to the window, False else")
            print("- [UpdateServeur] is the time between two windows refresh")

            exit()
        # Figures parameters

        # Figures dictionnary is the configuration dictionnary without
        # [General] and [Curves] sections

        # Curves parameters
        def print_help():
            """Print help"""
            print("Pooqi configuration file MUST have a section named")
            print("[Curves] like the one following :")
            print
            print("[Curves]")
            print("[CurveName] : [Row] [Column] [Legend] [Color] [Width]")
            print("[CurveName] : [Row] [Column] [Legend] [Color] [Width]")
            print("[CurveName] : [Row] [Column] [Legend] [Color] [Width]")
            print("[CurveName] : [Row] [Column] [Legend] [Color] [Width]")
            print("...")
            print
            print("where :")
            print("- [CurveName] is the name of the curve")
            print("- [Row] is the row number of the curve")
            print("- [Column] is the column number of the curve")
            print("- [Legend] is the legend of the curve (optional)")
            print("- [Color] is the color of the curve")
            print("- [Width] is an width of the curve (optional)")
        try:
            dummy_dic = conf_dic.copy()
            del dummy_dic[GENERAL_SECTION]
            del dummy_dic[CURVES_SECTION]
        except KeyError:
            print_help()
            exit()

        fig_dic_descript = dummy_dic

        for str_name, dic_fig_caract in fig_dic_descript.items():

            try:
                (str_num_row, str_num_column) = str_name.split("-")
                fig_coord = (int(str_num_row), int(str_num_column))
            except BaseException:
                print("ERROR: A section name is not good")
                print("       Please, check configuration file")
                exit()

            try:
                title = " ".join(dic_fig_caract["Title"])
            except (KeyError, IndexError):
                title = None

            try:
                label_y = " ".join(dic_fig_caract["LabelY"])
            except (KeyError, IndexError):
                label_y = None

            try:
                unit_y = " ".join(dic_fig_caract["UnitY"])
            except (KeyError, IndexError):
                unit_y = None

            try:
                min_y = float(dic_fig_caract["MinY"][0])
            except (KeyError, IndexError):
                min_y = DEFAULT_MIN
            except (ValueError, TypeError):
                print("ERROR : an error occured on MinY in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> MinY is set to default value")
                print
                min_y = DEFAULT_MIN

            try:
                max_y = float(dic_fig_caract["MaxY"][0])
            except (KeyError, IndexError):
                max_y = DEFAULT_MAX
            except (ValueError, TypeError):
                print("ERROR : an error occured on MaxY in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> MaxY is set to default value")
                print
                max_y = DEFAULT_MAX

            try:
                rep = "True" in dic_fig_caract["GridX"][0]
                grid_x = rep
            except (KeyError, IndexError):
                grid_x = False
            except (ValueError, TypeError):
                print("ERROR : an error occured on GridX in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> GridX is set to False")
                print
                grid_x = False

            try:
                rep = "True" in dic_fig_caract["GridY"][0]
                grid_y = rep
            except (KeyError, IndexError):
                grid_y = False
            except (ValueError, TypeError):
                print("ERROR : an error occured on GridY in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> GridY is set to False")
                print
                grid_y = False

            try:
                spectrogram = " ".join(dic_fig_caract["Spectrogram"])
            except (KeyError, IndexError):
                spectrogram = None

            try:
                window = int(" ".join(dic_fig_caract["Window"]))
            except (KeyError, IndexError):
                window = 1024

            try:
                opacity = float(" ".join(dic_fig_caract["Opacity"]))
            except (KeyError, IndexError):
                opacity = 1.

            try:
                bloublou = " ".join(dic_fig_caract["SpectrRescaleY"])
                rescale = [int(val) for val in bloublou.split(',')]
                rescale = (rescale[0], rescale[1])
            except (KeyError, IndexError):
                rescale = None

            try:
                plop = " ".join(dic_fig_caract["TickPos"])
                tick_pos = [float(val) for val in plop.split(',')]
            except (KeyError, IndexError):
                tick_pos = None

            try:
                if self.link_x_all is False:
                    (link_row, link_col) = dic_fig_caract["LinkX"]
                    link = (int(link_row), int(link_col))
                else:
                    link = None
            except (KeyError, IndexError):
                link = None
            except (ValueError, TypeError):
                print("ERROR : an error occured on LinkX in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> LinkX is set to None")
                print
                link = None

            try:
                vline = dic_fig_caract["VLine"]
                if len(vline[-1]) > 1 and vline[-1][0] != '#':
                    color = DIC_COLOR[vline[-1]]
                else:
                    color = vline[-1]
                color = pg.mkPen(color=color)
                vline = {'value': vline[:-1], 'color': color}
            except (KeyError, IndexError):
                vline = None
            except (ValueError, TypeError):
                print("ERROR : an error occured on Line in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> VLine is set to default value")
                print("Please put value and color in cfg")
                print
                vline = None

            try:
                hline = dic_fig_caract["HLine"]
                if len(hline[-1]) > 1 and hline[-1][0] != '#':
                    color = DIC_COLOR[hline[-1]]
                else:
                    color = hline[-1]
                color = pg.mkPen(color=color)
                hline = {'value': hline[:-1], 'color': color}
            except (KeyError, IndexError):
                hline = None
            except (ValueError, TypeError):
                print("ERROR : an error occured on Line in")
                print(
                    "   [" + str_num_row + "-" + str_num_column + "] section")
                print("   -> HLine is set to default value")
                print("Please put value and color in cfg")
                print
                hline = None

            self.figures[fig_coord] = rc.Figure(title, label_y, unit_y, min_y,
                                                max_y, grid_x, grid_y, link,
                                                [vline, hline], spectrogram,
                                                opacity, window, rescale,
                                                tick_pos)

            dic_curves = conf_dic[CURVES_SECTION]

        save_random_color = {}
        for name, parameters in dic_curves.items():
            nb_parameter = len(parameters)

            if nb_parameter >= 3:
                try:
                    str_row = parameters[0]
                    str_column = parameters[1]

                    if nb_parameter >= 4:
                        try:
                            test_param = parameters[-1]
                            test_param = int(test_param)
                            pos_color = -2
                        except (ValueError, TypeError):
                            pos_color = -1

                        legend = str(' '.join(parameters[2:pos_color]))
                        color = parameters[pos_color]

                        if pos_color == -2:
                            width = parameters[-1]
                        else:
                            width = 1
                    else:
                        color = parameters[2]
                        width = 1
                        legend = ''

                    s_color = color.split(';')
                    color = s_color[0]

                    symbol = None
                    style = None
                    if len(s_color) > 1:
                        if 'dot' in s_color:
                            style = QtCore.Qt.DotLine

                        if 'x' in s_color:
                            symbol = 'x'
                        elif 'o' in s_color:
                            symbol = 'o'

                    if color == 'random':

                        key = str_row + '-' + str_column

                        if key not in save_random_color.keys():
                            save_random_color[key] = []

                        color = rt.random_color(0, MAX_COLOR_VALUE,
                                                MIN_COLOR_VALUE,
                                                save_random_color[key])

                        save_random_color[key].append(color)

                        color = (color['red'],
                                 color['green'],
                                 color['blue'])

                    elif len(color) > 1 and color[0] != '#':
                        color = DIC_COLOR[color]

                    # to test if color has a correct format
                    color = pg.mkPen(
                        color=color, width=int(width), style=style)

                    curve = rc.Curve(
                        int(str_row), int(str_column), legend, color,
                        symbol=symbol)

                    self.curves[name] = curve

                except (ValueError, TypeError, KeyError):
                    print("There is a no valid value on [Curves] section")
                    print("Please, respect the following format :")
                    print
                    print(
                        "[CurveName]: [Row] [Column] [Legend] [Color] [Width]")
                    print
                    print("where:")
                    print("- [CurveName] is a string")
                    print("- [Row] is an integer")
                    print("- [Column] is an integer")
                    print("- [Legend] is a string (optional)")
                    print("- [Color] must be :")
                    print("          r or red")
                    print("          g or green")
                    print("          b or blue")
                    print("          c or cyan")
                    print("          m or magenta")
                    print("          y or yellow")
                    print("          k or black")
                    print("          w or white")
                    print("          (R, G, B, [A]) tuple of integers 0-255")
                    print("          hexadecimal strings; may begin with #")
                    print("- [Width] is an integer (optional)")
                    exit()

            else:
                print_help()
                exit()
