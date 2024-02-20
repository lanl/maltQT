"""
Display timeline information in a Qt Chart with
clicks to show stack information.
"""
from PySide6 import QtCore
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCharts import QLineSeries
from maltQtStack import MaltQtStack
from maltQtChart import MaltQtChart, maltQChartView


class MaltQtTimeline(QWidget):
    """Creates a timeline widget"""

    def genSeries(self, label, idx, idy, values, scale=1.0):
        """Given a x and y index into values returns a QLineSeries"""
        series = QLineSeries()
        series.setName(label)
        idMax = idx if idx > idy else idy
        lastX = values[0][idx]
        lastY = values[0][idy]
        for v in values:
            if len(v) <= idMax:
                series.append(lastX, lastY / scale)
                continue
            series.append(v[idx], v[idy] / scale)
            lastX = v[idx]
            lastY = v[idy]
        series.clicked.connect(self.click)
        return series

    @QtCore.Slot()
    def click(self, p):
        t = p.x()
        idx = self.time.index(min(self.time, key=lambda x: abs(x - t)))
        if idx != self.lastIndex:
            self.markIndex = True
            self.memTableUpdate(idx)
            self.chart.update()
            self.lastIndex = idx

    def genString(self, idx):
        v = self.values[idx]
        t = v[self.idxT]
        pMem = v[self.idxP] / 1048576.0
        vMem = v[self.idxV] / 1048576.0
        rMem = v[self.idxR] / 1048576.0
        return f"{idx}:  t={t:.3f}, physical={pMem:.3f}MB, virtual={vMem:.3f}MB, requested={rMem:.3f}MB"

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress and widget is self.chart_view:
            key = event.key()
            modifiers = QApplication.keyboardModifiers()
            shift = 10 if modifiers & QtCore.Qt.ShiftModifier else 1
            if key == QtCore.Qt.Key_Left:
                self.memTableUpdate(self.lastIndex - shift)
                self.markIndex = True
                self.chart.update()
                return True
            elif key == QtCore.Qt.Key_Right:
                self.memTableUpdate(self.lastIndex + shift)
                self.markIndex = True
                self.chart.update()
                return True

        return QWidget.eventFilter(self, widget, event)

    def rightAlignedItem(self, theText):
        """Returns a right aligned table item"""
        item = QTableWidgetItem(theText)
        item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        item.setFont("Courier New")
        return item

    def leftAlignedItem(self, theText):
        """Returns a right aligned table item"""
        item = QTableWidgetItem(theText)
        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        item.setFont("Courier New")
        return item

    def memTableUpdate(self, idx):
        """Updates the information in the memory table"""
        v = self.values[idx]
        if idx < 0:
            idx = 0
        elif idx >= len(self.stacks):
            idx = len(self.stacks) - 1
        if len(v) < self.idxMax:
            tIdx = t = pMem = vMem = rMem = "??"
        else:
            tIdx = f"{idx}"
            t = f"{v[self.idxT]:.3f}"
            pMem = f"{v[self.idxP] / 1048576.0:.3f}"
            vMem = f"{v[self.idxV] / 1048576.0:.3f}"
            rMem = f"{v[self.idxR] / 1048576.0:.3f}"
        self.lastIndex = idx
        self.stackView.model.load_data(self.stacks[idx], idx)
        self.info.setItem(0, 0, self.rightAlignedItem(t))
        self.info.setItem(1, 0, self.rightAlignedItem(pMem))
        self.info.setItem(2, 0, self.rightAlignedItem(vMem))
        self.info.setItem(3, 0, self.rightAlignedItem(rMem))
        self.info.setItem(4, 0, self.rightAlignedItem(tIdx))

    def __init__(self, parent, data):
        # Initialize the widget
        super().__init__(parent)
        self.mem_view = None
        self.markIndex = False
        self.lastIndex = None

        self.setGeometry(parent.geometry())
        # self.setGeometry((2 * parent.width())/3, 0, parent.width()/2, parent.height())

        # Squirrel away data
        self.data = data

        # Create series for timeline
        timeline = self.data.getAnnotatedTimeline()
        values = self.values = timeline["values"]
        fields = timeline["fields"]
        idxT = self.idxT = fields.index("t")
        idxS = self.idxS = fields.index("stack")
        idxP = self.idxP = fields.index("physicalMem")
        idxR = self.idxR = fields.index("requestedMem")
        idxV = self.idxV = fields.index("virtualMem")
        self.idxMax = len(fields)
        self.time = [x[idxT] if idxT < len(x) else -1.0 for x in values]
        self.pMem = self.genSeries("Physical Memory(MB)", idxT, idxP, values, 1048576.0)
        self.rMem = self.genSeries(
            "Requested Memory(MB)", idxT, idxR, values, 1048576.0
        )
        self.vMem = self.genSeries("Virtual Memory(MB)", idxT, idxV, values, 1048576.0)
        self.stacks = [x[idxS] if idxS < len(x) else [["??", "??", -1]] for x in values]

        self.chart = MaltQtChart(self)
        self.chart.addSeries(self.pMem)
        self.chart.addSeries(self.rMem)
        self.chart.addSeries(self.vMem)
        self.chart.createDefaultAxes()

        # QWidget Layout

        # Left layout: stacks
        self.stackView = MaltQtStack()
        self.table_view = self.stackView.table_view

        resize = QHeaderView.ResizeToContents
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(resize)
        self.vertical_header.setSectionResizeMode(resize)
        self.horizontal_header.setStretchLastSection(True)

        # Generate chart
        self.chart_view = maltQChartView(self)
        self.chart_view.installEventFilter(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Left layout
        size.setHorizontalStretch(1)
        size.setVerticalStretch(27)
        self.table_view.setSizePolicy(size)

        # Right layout: chart
        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        lLayout = QVBoxLayout()
        self.info = info = QTableWidget()
        info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        info.setSelectionMode(QAbstractItemView.NoSelection)

        info.setRowCount(5)
        info.setColumnCount(2)
        info.horizontalHeader().hide()
        info.verticalHeader().hide()
        info.setItem(0, 0, self.rightAlignedItem("Click"))
        info.setItem(1, 0, self.rightAlignedItem("Timeline"))
        info.setItem(2, 0, self.rightAlignedItem("To"))
        info.setItem(3, 0, self.rightAlignedItem("Update"))
        info.setItem(4, 0, self.rightAlignedItem("Table"))

        info.setItem(0, 1, self.leftAlignedItem("walltime, s"))
        info.setItem(1, 1, self.leftAlignedItem("physical, MB"))
        info.setItem(2, 1, self.leftAlignedItem("virtual, MB"))
        info.setItem(3, 1, self.leftAlignedItem("requested, MB"))
        info.setItem(4, 1, self.leftAlignedItem("Index"))
        info.horizontalHeader().setStretchLastSection(True)

        size.setHorizontalStretch(1)
        size.setVerticalStretch(6)
        self.info.setSizePolicy(size)

        lLayout.addWidget(self.info)
        lLayout.addWidget(self.table_view)
        self.main_layout.addLayout(lLayout)
        self.main_layout.addWidget(self.chart_view)

        # Set layout to the QWidget
        self.setLayout(self.main_layout)

    @QtCore.Slot()
    def magic(self):
        self.parent().topMagic(self.text)
        # self.text.setText(random.choice(self.hello))
