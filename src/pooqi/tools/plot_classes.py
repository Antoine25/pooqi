#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Curve(object):

    """
    curve class
    This class permits the gestion of curves in figures
    """

    def __init__(self, legend, color, plot, symbol=None):
        self.legend = legend
        self.color = color
        self.plot = plot
        self.symbol = symbol
        self.number_of_points = 0
        self.datas = {}
        self.last_x_data = None


class Data(object):

    """Class Data"""

    def __init__(self, data_x, data_y):
        self.data_x = data_x
        self.data_y = data_y
