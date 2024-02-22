"""
Display a file at given line.
Used the code from the Qt python codeEditor example at
https://doc.qt.io/qtforpython-6.2/examples/example_widgets__codeeditor.html

Added capability to load different files and hilight specified line
"""
from PySide6.QtCore import Slot, Qt, QRect, QSize, Slot
from PySide6.QtGui import QColor, QPainter, QTextFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
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

    def loadFile(self, fname, start, recurse=0):
        try:
            self.start = start
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
                Unable to read file '{fname}'
                Try specifying source directory in 'Preferences' tab
                """
                )
                self.goToLine(3)
                return
            else:
                self.loadFile(MaltQtPreferences.findFile(fname), start, 1)

    @Slot()
    def reload(self):
        self.loadFile(self.nowFile, self.start)

    def __init__(self, fname=None, start=0):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setReadOnly(True)
        self.setCenterOnScroll(True)
        self.blockCountChanged[int].connect(self.update_line_number_area_width)
        self.updateRequest[QRect, int].connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.loadFile(fname, start)

    def line_number_area_width(self):
        digits = 1
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
                number = str(block_number + 1)
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
