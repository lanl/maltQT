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
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCharts import QChart, QChartView, QLineSeries

from maltReaderJSON import MaltReaderJSON
from maltQtTimeline import MaltQtTimeline

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

        self.window = self.MainWindow(os.path.split(fname)[1])
        self.window.resize(1800, 900)

        # Initialize timeline view and display it
        self.tv = MaltQtTimeline(self.window, self.data)
        self.window.show()
        
    def timelineView(self):
        """Displays the timeline view"""
        self.tView = {}
        self.tView['layout']


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
