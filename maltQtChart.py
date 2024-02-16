""" simple feedback on a chart """
from PySide6 import QtGui, QtCore
from PySide6.QtCore import Qt, QRect, QPointF
from PySide6.QtCharts import QChart, QChartView, QLineSeries


class MaltQtChart(QChart):
    def __init__(self, parentx):
        super().__init__()
        self.parentx = parentx

    def mousePressEvent(self, QMouseEvent):
        # print mouse position
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))

    def mouseMoveEvent(self, QMouseEvent):
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))

    def keyPressEvent(self, e):
        if e.key() == Qt.key_Enter:
            print("hello")
        else:
            print(dir(e))


class maltQChartView(QChartView):
    def __init__(self, parentx):
        super().__init__(parentx.chart)
        self.parentx = parentx

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawForeground(painter, rect)
        if not self.parentx.markIndex:
            return
        self.parentx.markIndex = True

        pen = QtGui.QPen(QtGui.QColor("red"))
        pen.setWidth(0.25)
        painter.setPen(pen)

        idx = self.parentx.stackView.model.lastIndex
        if idx < 0:
            idx = 0
        elif idx >= len(self.parentx.values):
            idx = len(self.parentx.values) - 1
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
