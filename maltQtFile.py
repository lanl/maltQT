"""
Display a file at given line.
Used the code from the Qt python codeEditor example at
https://doc.qt.io/qtforpython-6.2/examples/example_widgets__codeeditor.html

Added capability to load different files and hilight specified line
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

from PySide2.QtCore import Slot, Qt, QRect, QSize, Slot
from PySide2.QtGui import QColor, QPainter, QTextFormat, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from maltQtPreferences import MaltQtPreferences


class LineNumberArea(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self._code_editor = editor

    def sizeHint(self):
        return QSize(self._code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._code_editor.lineNumberAreaPaintEvent(event)


class MaltQtFile(QPlainTextEdit):
    known_files = {}

    def goToLine(self, lineNum):
        myCursor = self.textCursor()
        myCursor.movePosition(QTextCursor.Start)
        myCursor.movePosition(QTextCursor.Down, n=lineNum - 1)
        self.setTextCursor(myCursor)
        self.centerCursor()

    def setAlloc(self, newAlloc):
        self.allocations = newAlloc

    def loadFile(self, fname, start, allocs={}, recurse=0):
        try:
            self.origName = fname
            self.start = start
            self.setAlloc(allocs)
            if recurse == 0:
                self.nowFile = fname
            if fname not in self.known_files:
                text = open(fname).read()
            else:
                text = self.known_files[fname]
            self.setPlainText(text)
            self.goToLine(start)
            self.update_line_number_area_width(start)
            self.known_files[fname] = text
            self.loaded = 1
        except:
            if recurse == 1 or fname is None:
                self.loaded = 0
                self.setPlainText(
                    f"""
                Unable to read file '{self.origName}'
                Try specifying source directory in 'Preferences' tab
                """
                )
                self.goToLine(3)
                return
            else:
                self.loadFile(MaltQtPreferences.findFile(fname), start, allocs, 1)

    @Slot()
    def reload(self):
        self.loadFile(self.nowFile, self.start, self.allocations)

    def __init__(self, fname=None, start=0, allocations=None):
        super().__init__()
        self.allocations = allocations
        self.line_number_area = LineNumberArea(self)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setReadOnly(True)
        self.setCenterOnScroll(True)
        self.blockCountChanged[int].connect(self.update_line_number_area_width)
        self.updateRequest[QRect, int].connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.loadFile(fname, start, allocations, 0)

    def line_number_area_width(self):
        digits = 1
        if self.allocations is not None:
            if len(self.allocations) > 0:
                digits += 8
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num *= 0.1
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        width = self.line_number_area_width()
        rect = QRect(cr.left(), cr.top(), width, cr.height())
        self.line_number_area.setGeometry(rect)

    def allocationString(self, lineNumber):
        """return formatted string for given line allocation"""
        if self.allocations is not None and lineNumber in self.allocations:
            value = self.allocations[lineNumber]
            if value < 1024:
                return f" {value:6.0f}B "
            elif value < 1048576:
                return f"{value/1024.:6.1f}kB "
            else:
                return f"{value/1048576:6.1f}MB "
        # return a blank string
        return " "

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = self.allocationString(block_number + 1) + str(block_number + 1)
                painter.setPen(Qt.black)
                width = self.line_number_area.width()
                height = self.fontMetrics().height()
                painter.drawText(0, top, width, height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

        # QPainter needs an explicit end() in PyPy. This will become a context manager in 6.3.
        painter.end()

    @Slot()
    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    @Slot()
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            width = self.line_number_area.width()
            self.line_number_area.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    @Slot()
    def highlight_current_line(self):
        extra_selections = []

        if True or not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)

            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)
