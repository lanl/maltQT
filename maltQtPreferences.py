"""Set preferences"""

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

import os

from maltQtUtils import leftAlignedItem
from pathlib import Path


class MaltQtPreferences(QWidget, QObject):
    dirs = []  # directories to search
    files = {}  # found files
    dirsChanged = Signal()  # Signal emitted when directories change

    def __init__(self, initialDirs=None):
        """The only thing in preferences is currently a directory selector"""
        super().__init__()
        self.setToolTip(
            """
        Add directories to your searchpath by clicking on the cells
        of the table here.  The search order for files is to first
        check if original file exists.  if it doesn't, we will look
        for it starting at the top directory here.

        Note that selecting a directory that is too high up in the
        stack can result in slowness since we must search all of
        the directories in there recursively for every file that is
        not found.  For best results, select the lowest possible
        search directory.

        This isn't perfect - if you put in a wrong search order, the
        only recourse is to quit and start again.
        """
        )

        self.title = title = QLabel("Select a directory by clicking a row below")
        title.setStyleSheet("QLabel {font-size: 16pt; text-align: center}")

        self.searchPaths = searchPaths = QTableWidget()
        searchPaths.setColumnCount(1)
        if initialDirs is not None:
            for d in initialDirs:
                self.dirs.append(os.path.abspath(d))
            self.searchPaths.setRowCount(len(self.dirs) + 1)
            for idx, entry in enumerate(self.dirs):
                newItem = leftAlignedItem(entry)
                self.searchPaths.setItem(idx, 0, newItem)
            # purge class known files
            MaltQtPreferences.files = {}
        else:
            searchPaths.setRowCount(1)
        searchPaths.setHorizontalHeaderLabels(
            ["Additional Source Directories (click row to add / change)"]
        )
        searchPaths.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        searchPaths.horizontalHeader().setStretchLastSection(True)
        searchPaths.horizontalHeader().hide()
        searchPaths.verticalHeader().hide()
        searchPaths.cellClicked.connect(self.dirSelect)

        self.layout = layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(searchPaths)
        self.setLayout(self.layout)

    @Slot()
    def dirSelect(self, row, column):
        """Selects a directory when the directory table is clicked"""
        idx = row
        startDir = self.dirs[row] if len(self.dirs) > row else None
        newDir = str(
            QFileDialog.getExistingDirectory(
                self, "Select Directory", startDir, QFileDialog.DontUseNativeDialog
            )
        )
        if len(newDir) == 0 or newDir in self.dirs:
            return
        if len(self.dirs) > row:
            self.dirs[row] = newDir
        else:
            self.dirs.append(newDir)
        newItem = leftAlignedItem(newDir)
        self.searchPaths.setItem(row, column, newItem)

        # Now we discard any unknown files to force search when requested next
        keys = [x for x in self.files.keys()]
        for x in keys:
            if self.files[x] == None:
                self.files.pop(x)
        self.searchPaths.setRowCount(len(self.dirs) + 1)
        self.dirsChanged.emit()

    @staticmethod
    def findFile(fname):
        """Class method that is called to find a file"""
        if fname in MaltQtPreferences.files:
            return MaltQtPreferences.files[fname]
        elif fname == "??":
            # This is the default of malt for no file
            return fname

        baseName = os.path.split(fname)[1]

        candidates = []
        for theDir in MaltQtPreferences.dirs:
            for path in Path(theDir).rglob(baseName):
                candidates.append(path)

        if len(candidates) == 0:
            MaltQtPreferences.files[fname] = None
            return fname
        elif len(candidates) > 1:
            print("_______________________________________________")
            print(f"Multiple candidates found for {baseName}")
            print(candidates)
            print(f"Using first: {candidates[0]}")

        MaltQtPreferences.files[fname] = candidates[0]
        return candidates[0]
