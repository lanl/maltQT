#!/usr/bin/env python3
"""
A Qt interface to reading Malt JSON output
All in one file because I'm lazy.

Author: Sriram Swaminarayan sriram@lanl.gov
"""

import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

from maltReaderJSON import MaltReaderJSON
from maltQtTimeline import MaltQtTimeline


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

        # Set focus to the searchbox in the timeline
        self.tv.searchBox.setFocus()


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
