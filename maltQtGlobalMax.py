"""
Display Global peak Memory information.
Click to show stack information.
"""
import re
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from maltQtUtils import leftAlignedItem, rightAlignedItem
from maltQtStack import MaltQtStack
from maltQtFile import MaltQtFile


class MaltQtGlobalMax(QWidget):
    """Creates a Global Peak Memory Usage information widget"""

    def __init__(self, data):
        # Initialize the widget
        super().__init__()

        # Squirrel away data
        self.data = data
        peaks = self.peaks = data.globalPeaks()
        self.info = info = QTableWidget()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        info.setSizePolicy(size)
        info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        info.setRowCount(len(peaks.keys()))
        info.setColumnCount(3)
        info.setHorizontalHeaderLabels(["memory (MB)", "location", "stackId"])
        info.setFont("Courier New")
        alignFlags = Qt.AlignRight | Qt.AlignVCenter
        info.horizontalHeaderItem(0).setTextAlignment(alignFlags)
        alignFlags = Qt.AlignLeft | Qt.AlignVCenter
        info.horizontalHeaderItem(1).setTextAlignment(alignFlags)
        sumGP = 0
        for idx, p in enumerate(peaks.keys()):
            s = peaks[p]
            memItem = QTableWidgetItem()
            memItem.setData(Qt.DisplayRole, f"{float(s['memory'])/1048576.:>8.3f}")
            memItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sumGP += s["memory"]
            info.setItem(idx, 0, memItem)
            info.setItem(idx, 1, leftAlignedItem(s["top"]))
            info.setItem(idx, 2, leftAlignedItem(p))
        info.setColumnHidden(2, True)
        print("Sum at global peak:", sumGP, sumGP / 1048576.0, "MB")
        info.setSortingEnabled(True)
        info.sortItems(0, Qt.DescendingOrder)
        info.cellClicked.connect(self.cellClick)

        info.horizontalHeader().setStretchLastSection(True)
        info.setTextElideMode(Qt.ElideNone)
        info.setWordWrap(True)
        info.resizeRowsToContents()

        self.stack = stack = MaltQtStack()
        stack.horizontalHeader().setStretchLastSection(True)
        stack.setSizePolicy(size)
        stack.cellClicked.connect(self.fileShow)

        self.fileArea = MaltQtFile()
        self.fileArea.setSizePolicy(size)

        # Widgets are created, now lay them out
        self.lLayout = lLayout = QVBoxLayout()
        self.lLayout.addWidget(info)

        self.rLayout = rLayout = QVBoxLayout()
        rLayout.addWidget(self.fileArea)
        rLayout.addWidget(self.stack)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(lLayout)
        self.main_layout.addLayout(rLayout)
        self.setLayout(self.main_layout)

        info.show()
        self.cellClick(0, 0)

    @Slot()
    def cellClick(self, row, column):
        self.info.selectRow(row)
        stackId = self.info.item(row, 2).text()
        if stackId in self.data.callsite:
            stack = [self.data.instrMap[x] for x in self.data.callsite[stackId]]
            self.stack.updateStack(stack, row, stackId)
            self.fileShow(0, 0)
        else:
            self.stack.update(None, None)

    @Slot()
    def fileShow(self, row, column):
        theLine = int(self.stack.item(row, 0).text())
        stackId = self.stack.item(row, 2).text()
        theFile = self.data.instrMap[stackId][1]
        self.stack.selectRow(row)
        self.fileArea.loadFile(theFile, theLine)
        print(f"stack={stackId}, line={theLine}, file={theFile}")
