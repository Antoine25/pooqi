# -*- coding: utf-8 -*-
"""Hmi esp."""

import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
from pooqi.hmi import widgets
from pooqi.hmi import mouse_tracking
from pooqi.tools.all_constants import DEFAULT_CONFIG_FILE
from pooqi.tools.all_constants import PERIOD_UPDATE_RT
from pooqi.tools.all_constants import DEFAULT_TIME
from pooqi.tools.all_constants import SEPARATION_VALUE
from pooqi.tools import plot_classes
from pooqi.tools import pq_tools
from pooqi.pq_reading import read_pq


def color_white_back(qcolor, factor=45):
    """ return new rgb component for white background """

    hue, sat, light, alpha = qcolor.getHsl()
    sat -= factor
    light -= factor / 3

    new_color = QtGui.QColor()
    new_color.setHsl(hue, sat, light, alpha)

    return new_color


class Figure(object):

    """
    Figure class
    This class permits the gestion of figures in window
    """

    def __init__(self, parent, row, column, max_time, title, label_x, unit_x,
                 label_y, unit_y, min_y, max_y, grid_x, grid_y, spectrogram=None,
                 opacity=1, window=1024, tick_pos=None, rescale=None,
                 link=None, line=None, mtrack=None, printable=False):

        super(Figure, self).__init__()

        # Figure parameters

        self.layout = parent.layout

        if title is not None:
            self.title = '<font size="5"><b>%s</b></font>' % title
        else:
            self.title = ''

        if label_x is not None:
            self.label_x = '<i>%s</i>' % label_x
        else:
            self.label_x = ''

        if unit_x is not None:
            self.unit_x = '<i>%s</i>' % unit_x
        else:
            self.unit_x = None

        if label_y is not None:
            self.label_y = '<i>%s</i>' % label_y
        else:
            self.label_y = ''

        if unit_y is not None:
            self.unit_y = '<i>%s</i>' % unit_y
        else:
            self.unit_y = None

        self.row = row
        self.column = column
        self.max_time = max_time
        self.min_y = min_y
        self.max_y = max_y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.is_legend_added = False

        self._printable = printable
        self.link = link
        self.mtrack = mtrack
        self.spectrogram = spectrogram
        self.opacity = opacity
        self.window = window
        self.rescale = rescale
        self.tick_pos = tick_pos

        self.last_data = None

        self.curves_list = []
        if self._printable is False:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_rt)
            self.timer.start(PERIOD_UPDATE_RT)
        # Figure graphicals parameters

        if printable is True:
            self.plot = parent.addPlot(title=self.title,
                                       row=self.row - 1,
                                       col=self.column - 1)

        else:
            if self.spectrogram is not None:
                self.custom_plot = widgets.SpectrogramWidget(self, self.title,
                                                             tick_pos=self.tick_pos)

                wav_file = None
                for wav_ in parent.wav_list:
                    if "%s.wav" % self.spectrogram in wav_:
                        wav_file = wav_

                if wav_file is not None:
                    wav = ep_tools.WavReader(parent.wav_list[0])
                    self.custom_plot.create_spectrogram(
                        wav.datas, fs_=wav.rate,
                        opacity=self.opacity, win_size=self.window,
                        rescale=self.rescale)
            else:
                self.custom_plot = widgets.CustomPlotWidget(self.title)

            self.layout.addWidget(self.custom_plot, self.row, self.column)
            self.plot = self.custom_plot.plot_widget

        self.viewbox = self.plot.getViewBox()
        self.viewbox.register(name=self.title)

        if self.max_time is not None:
            self.plot.setXRange(0, self.max_time)

        if self.min_y != None and self.max_y != None:
            self.plot.setYRange(self.min_y, self.max_y)

        self.plot.setLabel('bottom', self.label_x, units=self.unit_x)
        self.plot.setLabel('left', self.label_y, units=self.unit_y)
        self.plot.showGrid(x=self.grid_x, y=self.grid_y)

        if line is not None:
            if line[0] is not None:
                self.line_list = [pg.InfiniteLine(
                    pos=value, angle=90, movable=False,
                    pen=line[0]['color']) for value in line[0]['value']]

            if line[1] is not None:
                self.line_list = [pg.InfiniteLine(
                    pos=value, angle=0, movable=False,
                    pen=line[1]['color']) for value in line[1]['value']]

        try:
            [self.plot.addItem(line) for line in self.line_list]
        except AttributeError:
            pass

        if printable is False:
            plot_item = self.custom_plot.plot_item
        else:
            plot_item = self.plot

        if (self.mtrack is not None) and (printable is False):
            if self.spectrogram is not None:
                spectr = self.custom_plot.spectr_vb
            else:
                spectr = None
            if self.mtrack == 'default':
                self.mouse_tracking = mouse_tracking.CrossHair(
                    plot_item, spectr_vb=spectr)
            else:
                self.mouse_tracking = mouse_tracking.CrossHair(
                    plot_item, text_color=self.mtrack['ctext'],
                    cross_color=self.mtrack['ccross'],
                    line_color=self.mtrack['cline'], spectr_vb=spectr)
        else:
            self.mouse_tracking = None

    def add_legend(self):
        ''' add legend '''
        self.plot.addLegend(size=None, offset=(0, 1))

    def define_link(self):
        """Public method : Define link with X axes"""
        self.viewbox.linkView(axis=self.viewbox.XAxis, view=self.link.viewbox)

        if self._printable is False:
            self.custom_plot.header.hide_all_buttons()

    def unlink(self):
        """Public method : Remove link with X axes"""
        self.viewbox.linkView(axis=self.viewbox.XAxis, view=None)

        if self._printable is False:
            self.custom_plot.header.show_all_buttons()

    def update_rt(self):
        """Public method : Define actions of buttons"""
        try:
            if self.link is not None:
                self.custom_plot.header.auto_scale = \
                    self.link.custom_plot.header.auto_scale
                self.custom_plot.header.auto_range = \
                    self.link.custom_plot.header.auto_range

            if self.custom_plot.header.auto_scale is True and\
                    self.custom_plot.header.auto_range is False:
                self.plot.enableAutoRange()
            elif self.custom_plot.header.auto_scale is True and\
                    self.custom_plot.header.auto_range is True:
                self.plot.enableAutoRange(
                    axis=self.viewbox.YAxis, enable=True)
            else:
                self.plot.disableAutoRange()

            if self.custom_plot.header.auto_range is True and \
                    len(self.curves_list) > 0:
                if self.max_time is None:
                    time = DEFAULT_TIME
                else:
                    time = self.max_time

                try:
                    last_data = self.curves_list[0].last_x_data
                    if last_data is not None and last_data >= time:
                        self.plot.setXRange(last_data - time, last_data)
                except (ValueError, AttributeError):
                    pass
            else:
                pass
        except AttributeError:
            pass

    def scale_if_needed(self):
        """ scale plot if nedded """
        bounds = self.plot.getViewBox().childrenBoundingRect()

        if self.max_time is None:
            x_min = bounds.x()
            x_max = bounds.x() + bounds.width()
            self.plot.setXRange(x_min, x_max)

        if (self.min_y is None) and (self.max_y is None):
            y_min = bounds.y()
            y_max = bounds.y() + bounds.height()
            self.plot.setYRange(y_min, y_max)


class Window(pg.GraphicsLayoutWidget):

    """
    Window class
    This class permits the gestion of all the window
    """

    def __init__(self, app, config_file=DEFAULT_CONFIG_FILE,
                 printable=False, is_rt=False,
                 user_abscissa=None,
                 wav_list=None, mult=None):

        super(Window, self).__init__()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.wav_list = wav_list

        self.parameters = read_pq.Parameters(config_file)

        self.app = app

        self.max_time = self.parameters.max_time
        self.title = self.parameters.title
        self.anti_aliasing = self.parameters.anti_aliasing
        self.link_x_all = self.parameters.link_x_all
        self.x_to_zero = self.parameters.x_to_zero
        self.printable = printable
        self.is_rt = is_rt
        self.mtrack = self.parameters.mtrack

        self._mult = mult

        if self.printable and self.parameters.whitebackground:
            self.whitebackground = True
            if self.parameters.darkcolor:
                for curve in self.parameters.curves.values():
                    color = curve.color.color()
                    dark_color = color_white_back(color)
                    curve.color.setColor(dark_color)
        else:
            self.whitebackground = False

        if user_abscissa is None:
            self.abscissa = self.parameters.abscissa
            self.label_x = self.parameters.label_x
            self.unit_x = self.parameters.unit_x
        else:
            split_abs = user_abscissa.split(',')
            self.abscissa = split_abs[0]
            self.label_x = split_abs[0]
            if len(split_abs) > 1:
                self.unit_x = split_abs[1]
            else:
                self.unit_x = self.parameters.unit_x

        pg.setConfigOption('foreground', 'w')
        self.setBackground('k')
        self.setStyleSheet("QWidget {background-color: #000000 }")

        self.is_loading_remove = False
        self.loading = widgets.LoadingImage()
        self.layout.addWidget(self.loading)

        self.setWindowTitle(self.title)
        self.resize(1920, 1080)
        self.showMaximized()

        pg.setConfigOptions(antialias=self.anti_aliasing)
        # pg.setConfigOptions(autoDownsample=True)
        # pg.setConfigOptions(clipToView=True)

        # A figure contains 0 or more curves
        self.figures = {}

        # A curve belong to exactly one figure
        self.curves = {}

    def create_all(self):
        ''' create all '''

        # Fill the figures dictionnary
        for pos, figure_param in self.parameters.figures.items():

            row = pos[0]
            column = pos[1]

            self.figures[pos] = Figure(self, row, column,
                                       self.max_time,
                                       figure_param.title,
                                       self.label_x,
                                       self.unit_x,
                                       figure_param.label_y,
                                       figure_param.unit_y,
                                       figure_param.min_y,
                                       figure_param.max_y,
                                       figure_param.grid_x,
                                       figure_param.grid_y,
                                       spectrogram=figure_param.spectrogram,
                                       opacity=figure_param.opacity,
                                       window=figure_param.window,
                                       rescale=figure_param.rescale,
                                       tick_pos=figure_param.tick_pos,
                                       mtrack=self.mtrack,
                                       line=figure_param.line,
                                       printable=self.printable)

        viewbox_prec = None

        for pos, figure_param in self.parameters.figures.items():
            row = pos[0]
            column = pos[1]

            if self.link_x_all is False:
                if figure_param.link is not None:
                    try:
                        self.figures[pos].link = self.figures[
                            figure_param.link]  # .viewbox
                        self.figures[pos].define_link()
                    except (IndexError, KeyError):

                        figure = str(figure_param.link).replace(", ", "-")
                        figure = figure.replace("(", "[")
                        figure = figure.replace(")", "]")

                        print(''.join(["\033[91mERROR: Figure [%s-%s]" % (
                            str(row), str(column)),
                            "can't be linked with figure %s\n" % figure,
                            "because this figure doesn't exist.\n",
                            "Please, check configuration file.",
                            "\033[0m"]))
                        pg.exit()
            else:
                if viewbox_prec is not None:
                    self.figures[pos].link = viewbox_prec
                    self.figures[pos].define_link()

                viewbox_prec = self.figures[pos]  # .viewbox

    def remove_loading_image(self):
        ''' remove loading image '''

        if not self.is_loading_remove:
            self.layout.removeWidget(self.loading)
            self.loading.deleteLater()
            self.loading = None
            self.is_loading_remove = True

        if self.whitebackground:
            pg.setConfigOption('foreground', '#303030')
            self.setBackground('w')

    def fill_curves_dict(self):
        '''Fill the curves dictionnary'''
        for name, curve_param in self.parameters.curves.items():
            curve_row = curve_param.row
            curve_column = curve_param.column

            try:
                figure = self.figures[(curve_row, curve_column)]
            except KeyError:
                print(''.join(["\033[91mERROR: Curve %s" % name,
                               " is define at [%d-%d]\n" % (curve_row,
                                                            curve_column),
                               "but there is no figure at these coordonates\n",
                               "Please, check configuration file\033[0m"]))
                pg.exit()

            if curve_param.legend_txt != '' and not figure.is_legend_added:
                figure.is_legend_added = True
                figure.add_legend()

            plot = figure.plot.plot(pen=curve_param.color,
                                    name=curve_param.legend)

            curve = plot_classes.Curve(curve_param.legend,
                                       curve_param.color,
                                       plot,
                                       symbol=curve_param.symbol)

            self.curves[name] = curve
            self.figures[(curve_row, curve_column)].curves_list.append(curve)

    def _print_error(self, curve_name):
        """Print Error in case of curve name problem with rt plot """
        if self.is_rt is True:
            print(''.join(["\033[91mERROR : The curve '%s'" % curve_name,
                           " is not present in the configuration file,",
                           " but a point has to be added to this curve.",
                           "\033[0m"]))
            pg.exit()

    def curve_display(self, curve_name):
        """Public method : Display a curve"""
        if curve_name in self.curves.keys():
            curve = self.curves[curve_name]

            datas_x, datas_y = self._dico_to_list(curve_name)

            curve.plot.setData(datas_x, datas_y, symbol=curve.symbol)

        else:
            self._print_error(curve_name)

    def add_point(self, curve_name, var_x, var_y, has_to_plot=True):
        """Public method : add points on curve"""
        if curve_name in self.curves.keys():
            curve = self.curves[curve_name]
            curve.datas[curve.number_of_points] = plot_classes.Data(var_x,
                                                                    var_y)
            curve.number_of_points += 1
            curve.last_x_data = var_x

        if has_to_plot is True:
            self.curve_display(curve_name)

    def check_curves_in_csv(self, csv_curve_list):
        """ check if curves from cfg are in csv """
        if self.is_rt is False:
            for name in self.curves.keys():
                if SEPARATION_VALUE in name:
                    name = name.split(SEPARATION_VALUE)[0]
                if name not in csv_curve_list:
                    print(
                        "\033[93mWARNING: %s is in cfg but not in csv\033[0m"
                        % name)

    def curves_erase(self):
        """Public method : Erase all curves of the window"""
        for curve in self.curves.values():
            curve.datas = {}

    def _dico_to_list(self, curve_name, decalage=0):
        """Private method : Put dictionnary in a list"""
        datas_num = self.curves[curve_name].datas.keys()
        datas_num = sorted(datas_num)

        datas_x = []
        datas_y = []

        for num in datas_num:
            datas_x.append(self.curves[curve_name].datas[num].data_x)
            datas_y.append(self.curves[curve_name].datas[num].data_y)

        if self.x_to_zero:
            begin = datas_x[0]
            datas_x = [val - begin + decalage for val in datas_x]

        if self._mult is not None:
            datas_y = [val * self._mult for val in datas_y]

        return datas_x, datas_y

    def run(self):
        """Public method : show application"""
        self.show()
