#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


def str_to_network(string_):
    '''Transform string to network format (python v2=str, v3=bytearray)'''
    if sys.version_info >= (3, 0):
        return bytearray(string_, 'utf-8')
    return string_


VERSION = "1.9.5"

DEFAULT_CONFIG_FILE = "%s/../examples/esp/ep_example.esp" % os.path.dirname(
    __file__)
DEFAULT_DATA_FILE = ["%s/../examples/csv/example.csv" % os.path.dirname(
    __file__), "%s/../examples/wav/chirp_example.wav" % os.path.dirname(
    __file__)]
DEFAULT_ABSCISSA = "Time"

DEFAULT_PORT = 4521

DEFAULT_REFRESH_PERIOD = 0.05  # s
DEFAULT_TIME = 10  # s

PERIOD_UPDATE_RT = 25  # ms

GENERAL_SECTION = "General"
CURVES_SECTION = "Curves"
DEFAULT_MIN = None
DEFAULT_MAX = None

MAX_COLOR_VALUE = 255
MIN_COLOR_VALUE = 75

DIFF_ = 120
LIMIT_COLOR_ITERATION = 10000

# Client -> Server
IS_DATA_AVAILABLE = str_to_network("00")
GET_DATA = str_to_network("01")

TRY_LOST_CONNEXION = 10
TIME_BETWEEN_TRY = 2  # s

# Server -> Client
DATA_AVAILABLE = str_to_network("10")
NO_DATA_AVAILABLE = str_to_network("11")
ERASE_CURVES = str_to_network("12")

HTML_END = '</mark></span>'

DEFAULT_LINE_COLOR = '#6688ff'
DEFAULT_CROSS_COLOR = '#ffaa55'
DEFAULT_TEXT_COLOR = '#ffaa55'

ROUND = 2

DIC_COLOR = {'red': 'r', 'green': 'g', 'blue': 'b',
             'cyan': 'c', 'magenta': 'm', 'yellow': 'y',
             'black': 'k', 'white': 'w'}

LEG_FONT_SIZE = 3

SEPARATION_VALUE = '#!'
