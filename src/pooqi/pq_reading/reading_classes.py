# -*- coding: utf-8 -*-
"""Reading classes."""

from pooqi.tools.all_constants import LEG_FONT_SIZE


class Curve(object):

    """This class describe a curve"""

    def __init__(self, row, column, legend, color, symbol=None):
        self.row = row
        self.column = column
        self.legend_txt = legend

        if symbol in ['o', 'x']:
            self.symbol = symbol
        else:
            self.symbol = None

        try:
            legend = legend.decode("utf-8")
        except AttributeError:
            pass

        self.legend = "<font size='%d'>%s</font>" % (
            LEG_FONT_SIZE, legend)
        self.color = color


class Figure(object):

    """This class describes a figure"""

    def __init__(self, title, label_y, unit_y, min_y, max_y,
                 grid_x, grid_y, link, line, spectrogram, opacity, window,
                 rescale, tick_pos):
        try:
            self.title = title.decode("utf-8")
        except AttributeError:
            self.title = title

        try:
            self.label_y = label_y.decode("utf-8")
        except AttributeError:
            self.label_y = label_y

        try:
            self.unit_y = unit_y.decode("utf-8")
        except AttributeError:
            self.unit_y = unit_y

        self.min_y = min_y
        self.max_y = max_y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.link = link
        self.line = line
        self.spectrogram = spectrogram

        if opacity < 0.:
            opacity = 0.
        if opacity > 1.:
            opacity = 1.

        self.opacity = opacity
        self.window = window
        self.rescale = rescale
        self.tick_pos = tick_pos
