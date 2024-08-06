"""Create a stack view"""
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


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class MaltQtStack(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setRowCount(0)
        self.headers = ["line", "location", "stackId"]
        self.setHorizontalHeaderLabels(self.headers)
        self.setTextElideMode(Qt.ElideNone)
        self.setWordWrap(True)
        self.setColumnHidden(2, True)
        self.lastIndex = None
        self.colIndex = [2, 0, 3]
        self.setFont("Courier New")

    def setRow(self, idx, data):
        alignFlags = Qt.AlignRight | Qt.AlignVCenter
        for icol in range(3):
            jcol = self.colIndex[icol]
            item = QTableWidgetItem(f"{data[jcol]}")
            item.setToolTip(f"{data[jcol]}\n{data[1]}")
            item.setTextAlignment(alignFlags)
            self.setItem(idx, icol, item)
            alignFlags = (
                Qt.AlignLeft | Qt.AlignVCenter
            )  # only first column is right aligned

    def updateStack(self, stack, index, name=None):
        if name is not None:
            self.headers[1] = f'Stack = "{name}"'
            self.setHorizontalHeaderLabels(self.headers)
            alignFlags = Qt.AlignRight | Qt.AlignVCenter
            self.horizontalHeaderItem(0).setTextAlignment(alignFlags)
            alignFlags = Qt.AlignLeft | Qt.AlignVCenter
            self.horizontalHeaderItem(1).setTextAlignment(alignFlags)
        if self.lastIndex != index:
            self.setRowCount(0)
            self.lastIndex = index
            if stack is None or len(stack) < 2:
                self.setRowCount(1)
                self.setRow(0, ["no stack", "??", "-1", "??"])
            else:
                self.setRowCount(len(stack))
                for idx, x in enumerate(stack):
                    self.setRow(idx, x)
