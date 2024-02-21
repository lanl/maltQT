"""
Display timeline information in a Qt Chart with
clicks to show stack information.
"""
from PySide6 import QtCore
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QToolButton,
    QSizePolicy,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCharts import QLineSeries
from maltQtStack import MaltQtStack
import re


class MaltQtGlobalMax(QWidget):
    """Creates a timeline widget"""

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
        self.markIndex = True
        self.chart.update()
        self.info.setItem(0, 0, self.rightAlignedItem(t))
        self.info.setItem(1, 0, self.rightAlignedItem(pMem))
        self.info.setItem(2, 0, self.rightAlignedItem(vMem))
        self.info.setItem(3, 0, self.rightAlignedItem(rMem))
        self.info.setItem(4, 0, self.rightAlignedItem(tIdx))

    def __init__(self, parent, data):
        # Initialize the widget
        super().__init__(parent)
        self.lastText = None
        self.mem_view = None
        self.markIndex = False
        self.lastIndex = None

        self.setGeometry(parent.geometry())

        # Squirrel away data
        peaks = self.peaks = data.globalPeaks()

        self.info = info = QTableWidget()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        size.setVerticalStretch(6)
        self.info.setSizePolicy(size)
        info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        info.setSelectionMode(QAbstractItemView.NoSelection)
        info.setRowCount(len(peaks.keys()))
        info.setColumnCount(2)
        info.setHorizontalHeaderLabels(['memory (MB)', 'location'])
        #info.horizontalHeader().hide()
        #info.verticalHeader().hide()
        sumGP = 0
        for idx,p in enumerate(peaks.keys()):
            s = peaks[p]
            memItem = QTableWidgetItem()
            memItem.setData(QtCore.Qt.DisplayRole,s['memory'])
            memItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            sumGP += s['memory']
            info.setItem(idx,0,memItem)
            info.setItem(idx,1, self.leftAlignedItem(s['top']))
        print(sumGP, sumGP/1048576.,'MB')
        info.setSortingEnabled(True)
        info.sortItems(0, QtCore.Qt.DescendingOrder)
        info.sortItems(0, QtCore.Qt.AscendingOrder)
            
        info.horizontalHeader().setStretchLastSection(True)
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(info)
        self.setLayout(self.main_layout)

        info.show()

    def filterStack(self):
        """Using the contents of the searchbox will filter the current
        data so that one can navigate only the functions / files that
        match the regular expression specified"""
        text = self.searchBox.text()
        if len(text) == 0:
            self.ifilter = 0
            self.filterIds = []
            self.prevB.setEnabled(False)
            self.nextB.setEnabled(False)
            return
        elif text == self.lastText:
            if QApplication.queryKeyboardModifiers() & QtCore.Qt.AltModifier:
                self.filterPrev()
            else:
                self.filterNext()
            return
        self.lastText = text
        self.filterIds = []
        reFilter = re.compile(text, re.IGNORECASE)
        for idx, s in enumerate(self.stacks):
            for entry in s:
                m = reFilter.search(entry[0])
                if m is None:
                    n = reFilter.search(entry[1])
                    if n is None:
                        continue
                self.filterIds.append(idx)
                break
        if len(self.filterIds) == 0:
            self.prevB.setEnabled(False)
            self.nextB.setEnabled(False)
            return
        self.prevB.setEnabled(True)
        self.nextB.setEnabled(True)
        self.ifilter = 0
        self.memTableUpdate(self.filterIds[self.ifilter])

    @QtCore.Slot()
    def filterNext(self):
        """Increments the filter stack and updated the graph"""
        if len(self.filterIds) == 0:
            return
        self.ifilter += (
            10 if QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier else 1
        )
        if self.ifilter > len(self.filterIds) - 1:
            self.ifilter = len(self.filterIds) - 1
        if self.ifilter == len(self.filterIds) - 1:
            self.nextB.setEnabled(False)
        self.prevB.setEnabled(True)
        self.memTableUpdate(self.filterIds[self.ifilter])

    @QtCore.Slot()
    def filterPrev(self):
        """Decrements the filter stack and updated the graph"""
        if len(self.filterIds) == 0:
            return
        self.ifilter -= (
            10 if QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier else 1
        )
        if self.ifilter < 0:
            self.ifilter = 0
        if self.ifilter == 0:
            self.prevB.setEnabled(False)
        self.nextB.setEnabled(True)
        self.memTableUpdate(self.filterIds[self.ifilter])

    @QtCore.Slot()
    def timerFire(self):
        """The timer ensures that we don't fire while somebody is
        typing in the search box.  Consequently the code will wait
        half a second before executing the search"""
        self.mTimer.start(500)
