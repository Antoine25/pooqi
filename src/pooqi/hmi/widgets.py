# -*- coding: utf-8 -*-
"""Widgets."""

import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
from scipy import signal


class LoadingImage(QtWidgets.QWidget):

    ''' Loading Image calss '''

    loadState = QtCore.pyqtSignal(str)

    def __init__(self):

        super(LoadingImage, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        txt = QtWidgets.QLabel(''.join(['<font size="7">Loading</font><br/>',
                                        '<font size="2">Please wait...</font>']))
        self.stat = QtWidgets.QLabel('Initialisation...')

        txt.setStyleSheet("QLabel { color : white; }")
        self.stat.setStyleSheet("QLabel { color : #ffa000; }")
        txt.setAlignment(QtCore.Qt.AlignCenter)
        self.stat.setAlignment(QtCore.Qt.AlignCenter)
        txt.setFont(QtGui.QFont("calibri", 30))
        self.stat.setFont(QtGui.QFont("Arial", 12))

        layout.addWidget(txt)
        layout.addWidget(self.stat)

        self.loadState.connect(self.change_state)

    def change_state(self, txt):
        ''' change text status '''
        self.stat.setText(txt)


class Button(QtWidgets.QWidget):

    ''' Styled Button definition '''

    def __init__(self, action,
                 text='',
                 color='#101010', color2='#505050', color_txt='white',
                 color_border='silver',
                 width=100, height=15,
                 tooltip=None):

        super(Button, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.button = QtWidgets.QPushButton(text, self)
        self.button.setFixedWidth(width)
        self.button.setFixedHeight(height)

        self.button.setStyleSheet(
            "QPushButton { color: %s;\
background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0,\
stop:0 %s, stop:1 %s);\
        border: %dpx ridge %s;\
        border-radius: 5px;\
        font-weight: normal}" % (
                color_txt, color2, color,
                int(height / 10), color_border))

        font = self.button.font()
        font.setPointSize(width / 12)
        self.button.setFont(font)

        if tooltip is not None:
            self.button.setToolTip(tooltip)
        self.button.clicked.connect(action)

        layout.addWidget(self.button)

        self.__is_hide = False
        self.__text = text

    def set_text(self, text):
        ''' set button text '''
        self.__text = text
        self.__update_view()

    def set_hide(self):
        ''' hide the button '''
        self.__is_hide = True
        self.__update_view()

    def set_visible(self):
        ''' set button visible '''
        self.__is_hide = False
        self.__update_view()

    def __update_view(self):
        ''' update button view '''
        if self.__is_hide is True:
            self.button.hide()
        else:
            self.button.show()
            self.button.setText(self.__text)


class Header(QtWidgets.QWidget):

    """
    Header class
    """

    def __init__(self, title):

        super(Header, self).__init__()

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.btn1 = Button(self.update_btn1, text='Auto Scale: ON')
        self.btn2 = Button(self.update_btn2, text='Auto Range: ON')

        font = QtGui.QFont("Calibri", 11)
        if title is not None:
            self.title = QtWidgets.QLabel(title, self)
        else:
            self.title = QtWidgets.QLabel('', self)
        self.title.setStyleSheet(
            "QLabel { color : white; }")
        self.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignRight)

        self.auto_scale = True
        self.auto_range = True

        layout.setContentsMargins(45, 0, 0, 0)
        layout.addWidget(self.btn1)
        layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addStretch(1)
        layout.addWidget(self.btn2)

    def _auto_scale_on(self):
        """Private method : Enable Auto Scale"""
        self.btn1.set_text("Auto Scale: ON")
        self.auto_scale = True

    def _auto_scale_off(self):
        """Private method : Disable Auto Scale"""
        self.btn1.set_text("Auto Scale: OFF")
        self.auto_scale = False

    def _auto_range_on(self):
        """Pritave method : Enable Auto Range"""
        self.btn2.set_text("Auto Range: ON")
        self.auto_range = True

    def _auto_range_off(self):
        """Private method : Disable Auto Range"""
        self.btn2.set_text("Auto Range: OFF")
        self.auto_range = False

    def hide_all_buttons(self):
        """Public method : Hide buttons"""
        self.btn1.set_hide()
        self.btn2.set_hide()
        self._auto_scale_off()
        self._auto_range_off()

    def show_all_buttons(self):
        """Public method : Show buttons"""
        self.btn1.set_visible()
        self.btn2.set_visible()

    def update_btn1(self):
        """Public method : Update buttons"""
        if self.auto_scale is False:
            self._auto_scale_on()
        else:
            self._auto_scale_off()

    def update_btn2(self):
        """Public method : Update buttons"""

        if self.auto_range is False:
            self._auto_range_on()
        else:
            self._auto_range_off()


class CustomPlotWidget(QtWidgets.QWidget):

    """
    CustomPlotWidget class
    """

    def __init__(self, title):
        super(CustomPlotWidget, self).__init__()

        self.plot_widget = pg.PlotWidget()

        self.header = Header(title)
        self.plot_item = self.plot_widget.getPlotItem()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.header)
        layout.addWidget(self.plot_widget)


class SpectrogramWidget(QtWidgets.QWidget):

    """
    SpectrogramWidget class
    """

    def __init__(self, parent, title, grad=None, tick_pos=None):
        super(SpectrogramWidget, self).__init__()

        self.plot_widget = pg.PlotWidget()
        self.parent = parent

        self.header = Header(title)
        self.plot_item = self.plot_widget.getPlotItem()
        self.spectr_vb = pg.ViewBox()
        self.gradient = pg.GradientWidget(orientation='right')
        self.grad_legend = pg.AxisItem(orientation='left')
        self.grad_label = QtWidgets.QLabel()
        self.grad_label.setStyleSheet(
            "QLabel {color : white; font: bold;}")

        if tick_pos is None:
            tick_pos = [0., 0.25, 0.5, 0.75, 1.]

        if grad is None:
            my_grad = {'ticks': [(tick_pos[0], (0, 0, 0, 255)),
                                 (tick_pos[1], (0, 0, 100, 255)),
                                 (tick_pos[2], (0, 200, 0, 255)),
                                 (tick_pos[3], (255, 255, 0, 255)),
                                 (tick_pos[4], (255, 0, 0, 255))],
                       'mode': 'rgb'}
        else:
            my_grad = grad

        self.gradient.restoreState(my_grad)

        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.header, 1, 1, 1, 2)
        layout.addWidget(self.plot_widget, 2, 1, 2, 1)
        layout.addWidget(self.grad_label, 2, 2, 1, 1)
        layout.addWidget(self.gradient, 3, 2, 1, 1)

        self.gradient.setFixedWidth(65)

        self.plot_item.showAxis('right')
        self.plot_item.scene().addItem(self.spectr_vb)
        self.plot_item.getAxis('right').linkToView(self.spectr_vb)
        self.plot_item.getAxis('right').setLabel('Frequency [Hz]')
        self.spectr_vb.setXLink(self.plot_item)

        self.img = pg.ImageItem()

        self.spectr_vb.addItem(self.img)
        self.gradient.addItem(self.grad_legend)

        self.gradient_as_changed()
        self.gradient.sigGradientChanged.connect(self.gradient_as_changed)
        self.plot_item.vb.sigResized.connect(self.update_geometry)

    def create_spectrogram(self, datas, fs_, opacity=1, win_size=1024,
                           rescale=None):
        """ create the spectrogram """

        def search_in(tab, arg):
            """ search arg in tab """

            if arg == "min":
                to_return = min([min(line) for line in tab])
            else:
                to_return = max([max(line) for line in tab])

            return to_return

        window = signal.get_window("hann", win_size)
        freq, time, spectr = signal.spectrogram(
            np.array(datas), fs=fs_, window=window)

        if rescale is not None:
            rescaled_freq = [frq for frq in freq
                             if frq >= rescale[0] and frq <= rescale[1]]
            min_pos = list(freq).index(min(rescaled_freq))
            max_pos = list(freq).index(max(rescaled_freq))
            spectr = spectr[min_pos:max_pos]
        else:
            rescaled_freq = freq

        xscale = (time[-1]) / spectr.shape[1]
        yscale = rescaled_freq[-1] / spectr.shape[0]
        self.img.scale(xscale, yscale)

        spectr = 5 * np.log10(spectr.T)
        min_spectr = search_in(spectr, "min")
        max_spectr = search_in(spectr, "max")
        self.img.setImage(spectr,
                          opacity=opacity, autoLevels=True)

        # print min_spectr, max_spectr

        self.grad_legend.setRange(min_spectr, max_spectr)
        self.grad_label.setText("dB(FS)\nmax : %.2f" % max_spectr)

    def gradient_as_changed(self):
        """ change lut when gradient as changed """
        # set colormap
        cmap = self.gradient.colorMap()
        lut = cmap.getLookupTable()
        self.img.setLookupTable(lut)

    def update_geometry(self):
        """ set the geometry of spectrogram """
        spectr_geometry = self.plot_item.vb.sceneBoundingRect()
        self.spectr_vb.setAspectLocked(False)
        self.spectr_vb.setGeometry(spectr_geometry)

        self.grad_legend.setHeight(self.gradient.height())
        self.grad_legend.setWidth(self.gradient.width())

        self.plot_item.getAxis('right').setGrid(0)
