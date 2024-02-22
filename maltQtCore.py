#!/usr/bin/env python3
"""
A Qt interface to reading Malt JSON output
All in one file because I'm lazy.

Author: Sriram Swaminarayan sriram@lanl.gov
"""

import os
import sys
from PySide6 import QtGui
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)

from maltReaderJSON import MaltReaderJSON
from maltQtTimeline import MaltQtTimeline
from maltQtGlobalMax import MaltQtGlobalMax
from maltQtLeaks import MaltQtLeaks
from maltQtPreferences import MaltQtPreferences


class MaltQtCore:
    class MainWindow(QMainWindow):
        def __init__(self, title="unnamed"):
            super().__init__()
            self.setWindowTitle(title)
            self.setMinimumWidth(800)
            self.setMinimumHeight(900)

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
        QtGui.qt_set_sequence_auto_mnemonic(True)
        # set layout of main window
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        tabs.setStyleSheet(
            """QTabBar::tab:selected {font-size:18pt;background-color:rgb(255,255,230)} 
               QTabBar::tab:!selected {font-size:12pt;background-color:rgb(230,230,230)} 
            """
        )

        # Now add different tabs
        # A tab for stacks at global maximum
        self.gm = MaltQtGlobalMax(self.data)
        tabs.addTab(self.gm, " &Global Peak Stacks")

        self.leaks = MaltQtLeaks(self.data)
        tabs.addTab(self.leaks, " &Leaks")

        self.tv = MaltQtTimeline(self.window, self.data)
        tabs.addTab(self.tv, " &Timeline")

        self.prefs = MaltQtPreferences()
        tabs.addTab(self.prefs, " &Preferences")

        # Connect the preferences dirschanged signal to the reload slot of
        # Global peak file area
        self.prefs.dirsChanged.connect(self.gm.fileArea.reload)

        # Attach tab to window
        self.window.setCentralWidget(tabs)
        self.window.show()

        # Set focus to the searchbox in the timeline
        # self.tv.searchBox.setFocus()
        self.tv.chart_view.setFocus()


if __name__ == "__main__":
    import sys

    # generate the window!
    app = QApplication(sys.argv)
    qtm = []
    for f in sys.argv[1:]:
        try:
            qtm.append(MaltQtCore(f))
        except Exception as e:
            print(e)
            print(f"Unable to load file {f}")
            raise e
    if len(qtm) > 0:
        sys.exit(app.exec())
