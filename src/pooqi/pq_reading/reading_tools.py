# -*- coding: utf-8 -*-
"""Reading tools."""

import random
from pooqi.tools.all_constants import DIFF_
from pooqi.tools.all_constants import LIMIT_COLOR_ITERATION


def random_color(mini, maxi, minimum_luminosity, last_color_list=None):
    """return rgb value for random color"""
    continu = True
    cpt = 0

    while continu and cpt <= LIMIT_COLOR_ITERATION:
        bool_list = []
        red = random.randint(mini, maxi)
        blue = random.randint(mini, maxi)
        green = random.randint(mini, maxi)

        if ((red + blue + green) / 3) >= minimum_luminosity:
            if last_color_list is not None and len(last_color_list) > 0:
                for color in last_color_list:
                    bool_list.append(abs(color['red'] - red) < DIFF_
                                     and abs(color['green'] - green) < DIFF_
                                     and abs(color['blue'] - blue) < DIFF_)
                if True not in bool_list:
                    continu = False
            else:
                continu = False

        cpt += 1

    dic_color = {'red': red, 'green': green, 'blue': blue}
    return dic_color
