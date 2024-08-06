"""
Display timeline information in a Qt Chart with
clicks to show stack information.
"""
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

import re
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import (
    QAbstractItemView,
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


class MaltQtLeaks(QWidget):
    """Creates a Memory Leak information widget"""

    def __init__(self, data):
        # Initialize the widget
        super().__init__()

        # Squirrel away data
        self.data = data
        self.fileAlloc = data.fileAlloc
        leaks = self.leaks = data.leaks
        self.info = info = QTableWidget()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        info.setSizePolicy(size)
        info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        info.setRowCount(len(leaks))
        info.setColumnCount(4)
        info.setHorizontalHeaderLabels(["memory (kB)", "count", "location", "index"])
        info.setFont("Courier New")
        alignFlags = Qt.AlignRight | Qt.AlignVCenter
        info.horizontalHeaderItem(0).setTextAlignment(alignFlags)
        info.horizontalHeaderItem(1).setTextAlignment(alignFlags)
        alignFlags = Qt.AlignLeft | Qt.AlignVCenter
        info.horizontalHeaderItem(1).setTextAlignment(alignFlags)
        sumLeak = 0
        instrMap = self.data.instrMap
        for idx, p in enumerate(leaks):
            sumLeak += p["memory"]
            count = f"{p['count']}"
            memory = f"{float(p['memory'])/1024.:>12.3f}"
            stack = p["stack"]
            stackName = (
                "no stack"
                if len(stack) == 0
                else (instrMap[stack[0]][0] if stack[0] in instrMap else stack[0])
            )
            memItem = QTableWidgetItem()
            memItem.setData(Qt.DisplayRole, memory)
            memItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            indexItem = QTableWidgetItem()
            indexItem.setData(Qt.DisplayRole, idx)
            info.setItem(idx, 0, memItem)
            info.setItem(idx, 1, leftAlignedItem(count))
            info.setItem(idx, 2, leftAlignedItem(stackName))
            info.setItem(idx, 3, indexItem)
        info.setColumnHidden(3, True)
        print("Sum of all leaks:", sumLeak, sumLeak / 1048576.0, "MB")
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

        self.rLayout = rLayout = QVBoxLayout()
        rLayout.addWidget(self.fileArea)
        rLayout.addWidget(self.stack)
        self.main_layout = QHBoxLayout()
        self.lLayout = lLayout = QVBoxLayout()
        self.lLayout.addWidget(info)
        self.main_layout.addLayout(lLayout)
        self.main_layout.addLayout(rLayout)
        self.setLayout(self.main_layout)

        info.show()
        self.cellClick(0, 0)

    def getAlloc(self, theFile):
        try:
            retval = self.fileAlloc[theFile]["leaks"]
        except:
            retval = {}
        return retval

    @Slot()
    def cellClick(self, row, column):
        """When a cell is clicked in the leak table display the stack"""
        self.info.selectRow(row)
        index = int(self.info.item(row, 3).text())
        stackIdList = self.leaks[index]["stack"]
        stack = [self.data.instrMap[x] for x in stackIdList]
        self.stack.updateStack(stack, row, index)
        self.fileShow(0, 0)

    @Slot()
    def fileShow(self, row, column):
        """When a cell is clicked in the stack table display the file"""
        theLine = int(self.stack.item(row, 0).text())
        stackId = self.stack.item(row, 2).text()
        theFile = self.data.instrMap[stackId][1]
        self.stack.selectRow(row)
        self.fileArea.loadFile(theFile, theLine, self.getAlloc(theFile))
        print(f"stack={stackId}, line={theLine}, file={theFile}")
