""" simple feedback on a chart """
from PySide2.QtGui import QColor, QPainter, QPen
from PySide2.QtCore import QPointF, QRect, QRectF
from PySide2.QtCharts import QtCharts

# LANL Open Source Release ID O4736
#
# Copyright:
# © 2024. Triad National Security, LLC. All rights reserved.  This
# program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S. Department of Energy/National
# Nuclear Security Administration. All rights in the program are
# reserved by Triad National Security, LLC, and the U.S. Department of
# Energy/National Nuclear Security Administration. The Government is
# granted for itself and others acting on its behalf a nonexclusive,
# paid-up, irrevocable worldwide license in this material to reproduce,
# prepare. derivative works, distribute copies to the public, perform
# publicly and display publicly, and to permit others to do so.
#
# This program is released under the BSD-3 license.
# Please see the README.MD file for more details

from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import QPointF, QRect, QRectF
from PySide6.QtCharts import QChart, QChartView


class MaltQtChart(QtCharts.QChart):
    def __init__(self, parentx):
        super().__init__()
        self.parentx = parentx

    def mousePressEvent(self, QMouseEvent):
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))

    def mouseMoveEvent(self, QMouseEvent):
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))


class maltQChartView(QtCharts.QChartView):
    def __init__(self, parentx):
        super().__init__(parentx.chart)
        self.parentx = parentx

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """This is where we draw the red line when the timeline is clicked"""
        super().drawForeground(painter, rect)
        if not self.parentx.markIndex:
            return
        self.parentx.markIndex = True

        pen = QPen(QColor("pink"))
        pen.setWidth(0.25)
        painter.setPen(pen)

        idx = self.parentx.lastIndex
        v = self.parentx.values[idx]
        if len(v) < self.parentx.idxMax:
            return
        chart = self.parentx.chart
        area: QRect = chart.plotArea()
        t = float(v[self.parentx.idxT])
        hmin = float(chart.axisX().min())
        hmax = float(chart.axisX().max())
        ratio = (t - hmin) / (hmax - hmin)
        tpos = area.x() + area.width() * ratio
        point = QPointF(tpos, area.y())
        point2 = QPointF(tpos, area.y() + area.height())

        painter.drawLine(point, point2)
