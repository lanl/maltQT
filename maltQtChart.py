""" simple feedback on a chart """
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import QPointF, QRect, QRectF
from PySide6.QtCharts import QChart, QChartView


class MaltQtChart(QChart):
    def __init__(self, parentx):
        super().__init__()
        self.parentx = parentx

    def mousePressEvent(self, QMouseEvent):
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))

    def mouseMoveEvent(self, QMouseEvent):
        self.parentx.click(self.mapToValue(QMouseEvent.pos()))


class maltQChartView(QChartView):
    def __init__(self, parentx):
        super().__init__(parentx.chart)
        self.parentx = parentx

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """This is where we draw the red line when the timeline is clicked"""
        super().drawForeground(painter, rect)
        if not self.parentx.markIndex:
            return
        self.parentx.markIndex = True

        pen = QPen(QColor("red"))
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
