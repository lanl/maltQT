#!/usr/bin/env python3
"""
A Qt interface to reading Malt JSON output
All in one file because I'm lazy.

Author: Sriram Swaminarayan sriram@lanl.gov
"""

import os
import sys
import json
import random
from enum import Enum
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtWidgets import QTabWidget, QWidget
from PySide6.QtGui import QPalette, QColor

from maltReaderJSON import MaltReaderJSON
from maltQtTimeline import MaltQtTimeline


class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MaltQtCore:
    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, title="unnamed"):
            super().__init__()
            self.setWindowTitle(title)

    def __init__(self, fname):
        """
        reads in the json from file and initializes timeline view
        """
        # First load the data
        try:
            self.data = MaltReaderJSON(fname)
        except:
            raise ValueError(f"Unable to load JSON file {fname}")
        self.modes = Enum("mode", ["timeline", "globalPeak", "leaks", "allocations"])
        self.mode = self.modes.timeline

        self.window = self.MainWindow(os.path.split(fname)[1])
        self.window.resize(1800, 900)

        # set layout of main window
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        # Initialize timeline view and display it
        self.tv = MaltQtTimeline(self.window, self.data)
        tabs.addTab(self.tv, "Timeline")

        # Attach tab to window
        self.window.setCentralWidget(tabs)
        self.window.show()


if __name__ == "__main__":
    import sys

    # generate the window!
    app = QtWidgets.QApplication(sys.argv)
    qtm = []
    for f in sys.argv[1:]:
        try:
            qtm.append(MaltQtCore(f))
        except Exception as e:
            print(e)
            print(f"Unable to load file {f}")
    if len(qtm) > 0:
        sys.exit(app.exec())
