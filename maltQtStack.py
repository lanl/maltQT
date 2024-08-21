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

import os

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from maltQtUtils import fileSelect


class MaltQtStack(QTableWidget):
    lastSavedFile = "saved_stacks.csv"

    def __init__(self):
        super().__init__()
        self.stack = None
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
        self.stack = stack
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

    def save(self, fName=None):
        if fName is None or type(fName) is type(False):
            fName = fileSelect(
                self,
                startDir=MaltQtStack.lastSavedFile,
                inOption=QFileDialog.DontConfirmOverwrite,
            )
            if fName is None:
                print("File not specified, doing nothing")
                return
        MaltQtStack.lastSavedFile = fName
        modeOpen = "w"
        if os.path.exists(fName):
            msgBox = QMessageBox(self)
            msgBox.setText(f"File Exists ({os.path.split(fName)[1]})")
            append = msgBox.addButton("Append", QMessageBox.YesRole)
            msgBox.addButton("OverWrite", QMessageBox.NoRole)
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.setDefaultButton(append)
            msgBox.show()
            msgValue = msgBox.exec_()

            if msgValue == QMessageBox.Yes or msgValue == 0:
                modeOpen = "a"
            elif msgValue == 1:
                modeOpen = "w"
            else:
                return
        header = "function,source,line,stackid\n"
        with open(fName, modeOpen) as ofp:
            if modeOpen == "a":
                ofp.write("\n______________________________\n")
            ofp.write(header)
            for row in self.stack:
                if type(row) == list:
                    ofp.write(",".join([f"{y}".strip() for y in row]) + "\n")
                else:
                    ofp.write(f"No_Stack,??,-1,??\n")
            print(f"done writing stack to file {fName}")


class MaltQtStackView(QWidget):
    def __init__(self, parent):
        # Initialize the widget
        super().__init__(parent)
        self.setGeometry(parent.geometry())

        # create stack view
        self.qtstack = MaltQtStack()
        self.qtstack.cellClicked.connect(parent.cellClick)
        self.verticalHeader = self.qtstack.verticalHeader
        self.horizontalHeader = self.qtstack.horizontalHeader
        self.item = self.qtstack.item
        self.setRow = self.qtstack.setRow
        self.updateStack = self.qtstack.updateStack
        self.selectRow = self.qtstack.selectRow
        # the save button
        self.button = QPushButton("Save Stack", self)
        self.button.clicked.connect(self.qtstack.save)

        # create the layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.qtstack)
        self.main_layout.addWidget(self.button)
        self.setLayout(self.main_layout)

    def setSizePolicy(self, size):
        super().setSizePolicy(size)
        self.qtstack.setSizePolicy(size)
