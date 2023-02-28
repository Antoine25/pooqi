# -*- coding: utf-8 -*-
"""Pooqi connection."""

import threading
import time
import socket
import sys
import queue as Queue

from pooqi.tools.all_constants import DEFAULT_PORT
from pooqi.tools.all_constants import DEFAULT_REFRESH_PERIOD
from pooqi.tools.all_constants import TRY_LOST_CONNEXION
from pooqi.tools.all_constants import TIME_BETWEEN_TRY
from pooqi.tools.all_constants import GET_DATA
from pooqi.tools.all_constants import IS_DATA_AVAILABLE
from pooqi.tools.all_constants import DATA_AVAILABLE
from pooqi.tools.all_constants import NO_DATA_AVAILABLE
from pooqi.tools.all_constants import ERASE_CURVES
from pooqi.tools.all_constants import str_to_network


class Client(object):

    """docstring for Client"""

    def __init__(self, window, server_ip, port=DEFAULT_PORT,
                 refresh_period=DEFAULT_REFRESH_PERIOD):
        self.server_ip = server_ip
        self.port = port
        self.refresh = refresh_period
        self.win = window
        self.continue_ = True
        self.sock = None
        self.close = False

        self.list_curves_to_refresh = []

        # Create socket and connect to the server

        self.thread = threading.Thread(target=self.connect)
        self.thread.daemon = True
        self.start()

    def start(self):
        ''' start '''
        self.thread.start()

    def stop(self):
        ''' stop '''
        print('\nConnexion with %s has been stopped.' % self.server_ip)
        self.continue_ = False
        self.sock.close()
        self.close = True

    def connect(self):
        ''' thread connection '''

        cpt = 0
        flag = True
        flag_print = True

        while self.continue_:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                if flag is True:
                    self.sock.connect(
                        (socket.gethostbyname(self.server_ip), self.port))
                    print(" Connexion OK")
                    flag_print = True
                    flag = False

                while True:
                    self.get_datas()
                    cpt = 0
                    time.sleep(self.refresh)

            except (socket.error, BaseException):
                if not self.close:
                    if flag_print is True:
                        sys.stdout.write(
                            "Try to connect with %s" % self.server_ip)
                        flag_print = False
                    cpt += 1

                    if cpt <= TRY_LOST_CONNEXION:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        flag = True
                        time.sleep(TIME_BETWEEN_TRY)
                    else:
                        print(" TIME OUT")
                        self.continue_ = False

    def get_datas(self):
        """Retrieve datas from server"""
        if self.is_data_available():
            self.sock.send(GET_DATA)
            time.sleep(0.02)

            str_points_to_add = ""

            while str_points_to_add[-3:] not in ("END", "RAZ"):
                str_points_to_add += self.sock.recv(4096).decode("utf-8")

            raw_points_to_add = str_points_to_add.split(",")

            while len(raw_points_to_add) >= 3:
                (curve_name, str_data_x, str_data_y) = raw_points_to_add[:3]
                data_x = float(str_data_x)
                data_y = float(str_data_y)

                if curve_name not in self.list_curves_to_refresh:
                    self.list_curves_to_refresh.append(curve_name)

                raw_points_to_add.pop(0)  # Delete curve
                raw_points_to_add.pop(0)  # Delete data_x
                raw_points_to_add.pop(0)  # Delete data_y

                # Add point and don't plot
                self.win.add_point(curve_name, data_x, data_y, False)

            # Test if curves have to be erased
            if raw_points_to_add[-1] == "RAZ":
                self.win.curves_erase()

            self.update_curves()

    def update_curves(self):
        ''' plot curves '''
        for curve in self.list_curves_to_refresh:
            self.win.curve_display(curve)

    def is_data_available(self):
        """Ask to the server is some datas are available"""
        self.sock.send(IS_DATA_AVAILABLE)
        server_answer = self.sock.recv(2)

        if server_answer == DATA_AVAILABLE:
            data_available = True
        elif server_answer == NO_DATA_AVAILABLE:
            data_available = False
        elif server_answer == ERASE_CURVES:
            self.win.curves_erase()
            data_available = False

        return data_available


class Server(object):

    """docstring for Server"""

    def __init__(self, port=DEFAULT_PORT, local_plot=False, max_points=100000):
        # Contains the datas not yet plotted
        self.curves = {}
        self.max_points = max_points

        # Set to True if the server wants to erase all curves
        self.has_to_erase_curves = False

        # Create socket and wait for a client connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client = None
        # Get the ip adress

        self.hostname = socket.gethostname()

        if local_plot is True:
            self.ip_adress = "127.0.0.1"
        else:
            try:
                try:
                    self.ip_adress = socket.gethostbyname(
                        "%s.local" % self.hostname)
                except socket.gaierror:
                    self.ip_adress = socket.gethostbyname(self.hostname)
            except socket.gaierror:
                print("ERROR: Impossible to get host with %s" % self.hostname)
                print("       or %s.local" % self.hostname)
                exit()

        print("%s send datas at %s" % (self.hostname, self.ip_adress))

        # Bind of the socket
        self.sock.bind((self.ip_adress, port))

        # Specify only one client connection is allowed
        self.sock.listen(1)

        # Create thread
        self.__continue_ = True
        thread = threading.Thread(target=self._wait_for_client)
        thread.daemon = True
        thread.start()

    def stop(self):
        """ stop server """
        self.__continue_ = False
        if self.client is not None:
            self.client.close()
            self.client = None
        self.sock.close()

    def _wait_for_client(self):
        """Wait for a client to connnect"""
        while self.__continue_:
            # sock.accept return a tuple of 2 elements.
            # Only the first one is usefull
            try:
                self.client = self.sock.accept()[0]
            except BaseException as err:
                print('ERROR with self.sock.accept(): ' + str(err))
            if self.client is not None:
                self._client_state_machine()

    def _is_data_available(self):
        """Check if some datas are ready to be sent to the client"""
        # If the dictionnary id empty, there is no data to snd
        if self.client is not None:
            if self.curves == {}:
                self.client.send(NO_DATA_AVAILABLE)
            # In the contrary, there is data to send
            else:
                self.client.send(DATA_AVAILABLE)

    def _client_state_machine(self):
        """Engage the client state machine"""
        client_problem = False
        try:
            while not client_problem and self.__continue_:
                client_query = self.client.recv(2)

                if client_query == IS_DATA_AVAILABLE:
                    self._is_data_available()
                elif client_query == GET_DATA:
                    self._send_datas()
                # If client is dead, the function client.
                # recv will return a empty
                # string. In this case, the state machine stop,
                # and the server is waiting for another client.
                else:
                    client_problem = True
        except BaseException:
            client_problem = True

    def _send_datas(self):
        """Send available datas to the client"""

        string_to_send = ''
        for curve, datas in self.curves.items():
            while not datas.empty():
                (data_x, data_y) = datas.get()
                string_to_send = ''.join([string_to_send, "%s,%s,%s," % (
                    curve, str(data_x), str(data_y))])

        # TODO : Find a better way to do this, because this is ugly !
        if self.has_to_erase_curves:
            self.has_to_erase_curves = False
            string_to_send += "RAZ"
        else:
            string_to_send += "END"

        self.client.send(str_to_network(string_to_send))

    def add_point(self, curve_name, data_x, data_y):
        """Public method : Add a point to plot in a curve"""
        if curve_name not in self.curves:
            self.curves[curve_name] = Queue.Queue(self.max_points)

        if not self.curves[curve_name].full():
            self.curves[curve_name].put((data_x, data_y))
        else:
            if not self.curves[curve_name].empty():
                self.curves[curve_name].get()
                self.curves[curve_name].put((data_x, data_y))

    def add_list_point(self, time_elapsed, list_tuple_data):
        """
        Public method: multi add_point use.
        list_tuple_data = list of (headerName, data)
        """
        [self.add_point(x[0], time_elapsed, x[1]) for x in list_tuple_data]

    def curves_erase(self):
        """Erase all curves"""
        self.has_to_erase_curves = True
