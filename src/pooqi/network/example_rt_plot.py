# -*- coding: utf-8 -*-
"""Example rt plot."""

import argparse
import math
import time

from pooqi.network import pooqi_connection


def main():
    """Plot sinus, cosinus, droite, square and erase them every 10 seconds"""

    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--local", dest="local",
                        action="store_const",
                        const=True, default=False,
                        help="add option if server is local")

    args = parser.parse_args()
    local = args.local

    plot_server = pooqi_connection.Server(
        local_plot=local, max_points=500)
    plot_server.curves_erase()

    time_init = time.time()
    try:
        while True:
            elapsed_time = time.time() - time_init
            # if elapsed_time <= 10:
            sinus = math.sin(elapsed_time)
            cosinus = math.cos(elapsed_time)
            droite = 2 * elapsed_time - 4
            square = elapsed_time ** 2

            plot_server.add_point("Sinus", elapsed_time, sinus)
            plot_server.add_point("Cosinus", elapsed_time, cosinus)
            plot_server.add_point("Droite", elapsed_time, droite)
            plot_server.add_point("Square", elapsed_time, square)
            time.sleep(0.01)

            # else:
            #     time_init = time.time()
            #     plot_server.curves_erase()
    except KeyboardInterrupt:
        print(' Server End')
        plot_server.stop()


if __name__ == '__main__':
    main()
