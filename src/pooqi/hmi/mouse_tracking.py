# -*- coding: utf-8 -*-
"""Mouse tracking."""

import pyqtgraph as pg
from PyQt5 import QtCore
from pooqi.tools.all_constants import HTML_END
from pooqi.tools.all_constants import DEFAULT_LINE_COLOR
from pooqi.tools.all_constants import DEFAULT_CROSS_COLOR
from pooqi.tools.all_constants import DEFAULT_TEXT_COLOR
from pooqi.tools.all_constants import ROUND


def find_the_closer(sorted_list, key):
    ''' search the closer element from key in a list '''

    if key in sorted_list:
        return key
    else:
        for cpt in range(len(sorted_list) - 1):
            if key > sorted_list[cpt] and key < sorted_list[cpt + 1]:
                if abs(sorted_list[cpt] - key) >= abs(
                        sorted_list[cpt + 1] - key):
                    return sorted_list[cpt + 1]
                else:
                    return sorted_list[cpt]


class CrossHair(pg.PlotItem):

    """ Cross hair """

    def __init__(self, plot, text_color=DEFAULT_TEXT_COLOR,
                 cross_color=DEFAULT_CROSS_COLOR,
                 line_color=DEFAULT_LINE_COLOR, spectr_vb=None):
        super(CrossHair, self).__init__()

        self.data_list = []
        self.data_list_x_sorted = []
        self.plot = plot
        self.spectr_vb = spectr_vb

        self.text_color = pg.mkColor(text_color)
        self.cross_color = pg.mkColor(cross_color)
        self.line_color = pg.mkPen(line_color)
        self.border = pg.mkPen(self.text_color)
        self.fill = pg.mkBrush(0, 0, 0, 210)

        self.vline = pg.InfiniteLine(
            angle=90, movable=False, pen=self.line_color)
        self.hline = pg.InfiniteLine(
            angle=0, movable=False, pen=self.line_color)

        self.labelx = pg.TextItem(
            border=self.border,
            fill=self.fill, anchor=(0.5, 1.0))
        self.labely = pg.TextItem(
            border=self.border,
            fill=self.fill, anchor=(0.0, 0.5))
        if self.spectr_vb is not None:
            self.labely2 = pg.TextItem(
                border=self.border,
                fill=self.fill, anchor=(0.0, 0.5))

        self.plot.addItem(self.vline, ignoreBounds=True)
        self.plot.addItem(self.hline, ignoreBounds=True)
        self.plot.addItem(self.labelx)
        self.plot.addItem(self.labely)
        if self.spectr_vb is not None:
            self.plot.addItem(self.labely2)

        self.view_box = self.plot.getViewBox()
        self.vb_range = self.view_box.viewRange()

        self.hideAxis('left')
        self.hideAxis('bottom')
        self.hideAxis('right')
        self.hideAxis('top')

        self.vline.hide()
        self.hline.hide()
        self.labelx.hide()
        self.labely.hide()
        if self.spectr_vb is not None:
            self.labely2.hide()

        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

        self.y_text_list = []
        self.ycircle_list = []

        self.plot.scene().sigMouseMoved.connect(self.mouse_moved)

    def update(self):
        ''' update with new data '''

        curve_id = 0
        for plot_data_item in self.plot.listDataItems():
            (x_data, y_data) = plot_data_item.getData()
            x_data = x_data.tolist()
            y_data = y_data.tolist()
            color = plot_data_item.curve.opts['pen'].color().getRgb()

            self.data_list.append(
                {'color': color,
                 'data': {round(x_data[cpt], ROUND): {'x': x_data[cpt],
                                                      'y': y_data[cpt]}
                          for cpt in range(len(x_data))},
                 'txt_pos': {'x': None, 'y': None}
                 })

            self.data_list_x_sorted.append(
                sorted(self.data_list[curve_id]['data'].keys()))
            curve_id += 1

        if len(self.data_list) > 0:
            list_x = [data['x'] for data in self.data_list[0]['data'].values()]
            list_y = [data['y'] for data in self.data_list[0]['data'].values()]
            try:
                self.min_x = min(list_x)
                self.max_x = max(list_x)
                self.min_y = min(list_y)
                self.max_y = max(list_y)
            except ValueError:
                self.min_x = None
                self.max_x = None
                self.min_y = None
                self.max_y = None

        else:
            self.min_x = None
            self.max_x = None
            self.min_y = None
            self.max_y = None

        for data in self.data_list:
            self.y_text_list.append(
                pg.TextItem(
                    border=pg.mkPen(
                        color=(data['color'][0],
                               data['color'][1],
                               data['color'][2])),
                    fill=self.fill,
                    anchor=(-0.1, 0.5)))

            html_cross = '<span style="color: #%s; \
            font-size: 12px;"><mark><b>X</b>' \
            % pg.colorStr(self.cross_color)[:-2]
            html_cross += HTML_END

            self.ycircle_list.append(
                pg.TextItem(html=html_cross,
                            anchor=(0.45, 0.5)))

        for item in self.y_text_list:
            self.plot.addItem(item)
            item.hide()

        for item in self.ycircle_list:
            self.plot.addItem(item)
            item.hide()

    def mouse_moved(self, pos):
        """ using signal proxy turns original arguments into a tuple """
        if self.plot.sceneBoundingRect().contains(pos):
            mouse_point = self.view_box.mapSceneToView(pos)
            if self.spectr_vb is not None:
                mouse_point_spectr = self.spectr_vb.mapSceneToView(pos)
            else:
                mouse_point_spectr = None
            self.moved(mouse_point, mouse_point_spectr)
            self.vb_range = self.view_box.viewRange()

    def moved(self, mouse_point, mouse_point_spectr=None):
        """ print cross """

        x_value = mouse_point.x()
        y_value = mouse_point.y()

        if x_value >= self.vb_range[0][0] and\
                x_value <= self.vb_range[0][1] and\
                y_value >= self.vb_range[1][0] and\
                y_value <= self.vb_range[1][1]:

            self.vline.show()
            self.hline.show()

            self.vline.setPos(x_value)
            self.hline.setPos(y_value)

            if self.spectr_vb is None:
                self.set_line_text(x_value, y_value)
            else:
                y2_value = mouse_point_spectr.y()
                self.set_line_text(x_value, y_value, y2_value)

            if self.min_x is not None and self.max_x is not None:
                if x_value >= self.min_x and\
                        x_value <= self.max_x:
                    cpt = 0
                    for data in self.data_list:

                        try:
                            self.ycircle_list[cpt].show()

                            key = find_the_closer(
                                self.data_list_x_sorted[cpt],
                                round(x_value, ROUND))

                            posx = data['data'][key]['x']
                            posy = data['data'][key]['y']

                            pixel_point = self.view_box.mapViewToScene(
                                QtCore.QPointF(posx, posy))
                            self.ycircle_list[cpt].setPos(posx, posy)

                            self.set_cross_text(posx, posy, data['color'],
                                                cpt, pixel_point)
                        except KeyError:
                            pass

                        cpt += 1

                    self.unoverlap()
                else:
                    for item in self.ycircle_list:
                        item.hide()
                    for item in self.y_text_list:
                        item.hide()

        else:
            self.vline.hide()
            self.hline.hide()
            for item in self.ycircle_list:
                item.hide()

            self.labelx.hide()
            self.labely.hide()
            if self.spectr_vb is not None:
                self.labely2.hide()
            for item in self.y_text_list:
                item.hide()

    def set_line_text(self, x_value, y_value, freq=None):
        """ set text with mouse_point """

        textx = '%.3f' % x_value
        texty = '%.3f' % y_value
        if self.spectr_vb is not None:
            if freq < 1000 and freq > -1000:
                texty2 = '%d Hz' % freq
            else:
                texty2 = '%.2f KHz' % (float(freq) / 1000)

        html = '<span style="color: #%s;\
                font-size: 12px;"><mark>' %\
            pg.colorStr(self.text_color)[:-2]
        self.labelx.setHtml('%s%s%s' % (html, textx, HTML_END))
        self.labely.setHtml('%s%s%s' % (html, texty, HTML_END))
        if self.spectr_vb is not None:
            self.labely2.setHtml('%s%s%s' % (html, texty2, HTML_END))

        self.labelx.show()
        self.labely.show()
        if self.spectr_vb is not None:
            self.labely2.show()

        self.labelx.setPos(x_value, self.vb_range[1][0])
        self.labely.setPos(self.vb_range[0][0], y_value)
        if self.spectr_vb is not None:
            brect = self.labely2.textItem.boundingRect()
            txt_w = self.view_box.mapSceneToView(brect).boundingRect().width()
            self.labely2.setPos(self.vb_range[0][1] - txt_w, y_value)

    def set_cross_text(self, posx, posy, color, cpt, pixel_point):
        """ set text with mouse_point """

        html = '<span style="color: rgb(%s,%s,%s);\
                font-size: 12px;"><mark>' %\
            (color[0], color[1], color[2])

        text = 'x: %.3f<br>y: %.3f' % (posx, posy)
        self.y_text_list[cpt].show()
        self.y_text_list[cpt].setHtml(
            html + text + HTML_END)

        self.data_list[cpt]['txt_pos']['x'] = pixel_point.x()
        self.data_list[cpt]['txt_pos']['y'] = pixel_point.y()

    def unoverlap(self):
        """ arrange position of text to remove overlaps """

        lenth = len(self.data_list)
        pos_dic = {self.data_list[i]['txt_pos']['y']: i
                   for i in range(lenth)}

        pos_list = sorted(pos_dic.keys())

        try:
            for cpt in range(lenth - 1):

                id1 = pos_dic[pos_list[cpt]]
                id2 = pos_dic[pos_list[cpt + 1]]

                while pos_list[cpt] + 40 >= pos_list[cpt + 1]:
                    pos_list[cpt + 1] += 1

                self.data_list[id1]['txt_pos']['y'] = pos_list[cpt]
                self.data_list[id2]['txt_pos']['y'] = pos_list[cpt + 1]

                pos_dic = {self.data_list[i]['txt_pos']['y']: i
                           for i in range(lenth)}
        except IndexError:
            pass

        self.set_pos()

    def set_pos(self):
        ''' put text on position '''

        for curve_id in range(len(self.data_list)):
            pos_x = self.data_list[curve_id]['txt_pos']['x']
            pos_y = self.data_list[curve_id]['txt_pos']['y']

            pts = self.view_box.mapSceneToView(QtCore.QPointF(pos_x, pos_y))
            self.y_text_list[curve_id].setPos(pts.x(), pts.y())
