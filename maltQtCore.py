#!/usr/bin/env python3
"""
A Qt interface to reading Malt JSON output
All in one file because I'm lazy.

Author: Sriram Swaminarayan sriram@lanl.gov
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

    def __init__(self, fname, sourceDirs=None):
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
        # Timeline tab
        self.tv = MaltQtTimeline(self.window, self.data)
        tabs.addTab(self.tv, " &Timeline")

        # Global Peak tab
        self.gm = MaltQtGlobalMax(self.data)
        tabs.addTab(self.gm, " &Global Peak Stacks")

        # Leak tab
        self.leaks = MaltQtLeaks(self.data)
        tabs.addTab(self.leaks, " &Leaks")

        # Preferences tab
        self.prefs = MaltQtPreferences(sourceDirs)
        tabs.addTab(self.prefs, " &Preferences")

        # Connect the preferences dirschanged signal to the reload slot of
        # Global peak file area
        self.prefs.dirsChanged.connect(self.gm.fileArea.reload)

        # force update in case sourceDirs is not null
        if sourceDirs is not None and len(sourceDirs) > 0:
            self.gm.fileArea.reload()

        # Attach tab to window
        self.window.setCentralWidget(tabs)
        self.window.show()

        # Set focus to the chart in the timeline
        self.tv.chart_view.setFocus()


if __name__ == "__main__":
    import sys
    import argparse

    # Get list of directories if needed
    parser = argparse.ArgumentParser(description="maltQtCore")
    parser.add_argument(
        "-d",
        dest="dirs",
        action="store",
        help="A list of comma separated directories for source paths",
    )
    parser.add_argument("files", help="remainder of command line", nargs="*")
    args = parser.parse_args()
    dirs = args.dirs.split(",") if args.dirs is not None else []

    # generate the window!
    app = QApplication(sys.argv)
    # app.setStyleSheet("color: black; background-color: rgb(200,200,200)");

    qtm = []
    for f in args.files:
        try:
            qtm.append(MaltQtCore(f, dirs))
        except Exception as e:
            print(e)
            print(f"Unable to load file {f}")
            raise e
    if len(qtm) > 0:
        sys.exit(app.exec())
