"""Create a stack view"""

from PySide6.QtWidgets import QWidget, QHeaderView, QSizePolicy, QTableView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class MaltQtStackTableModel(QAbstractTableModel):
    def __init__(self, stacks=None):
        QAbstractTableModel.__init__(self)
        self.column_count = 2
        self.stacks = stacks
        self.lines = []
        self.functions = []
        self.lastIndex = 1
        self.load_data(0)

    def shift(self, iShift):
        self.load_data(self.lastIndex + iShift)

    def load_data(self, index):
        if index < 0:
            index = 0
        elif index >= len(self.stacks):
            index = len(self.stacks) - 1

        if self.lastIndex != index:
            self.lastIndex = index
            self.stack = self.stacks[index]
            if len(self.stack) < 2:
                self.lines = [-1]
                self.functions = ["no stack available"]
            else:
                self.lines = [x[2] for x in self.stack]
                self.functions = [x[0] for x in self.stack]
            self.column_count = 2
            self.row_count = len(self.lines)
            self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Line", "Function")[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                return f"{self.lines[row]}"
            elif column == 1:
                return self.functions[row]

        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft
        elif role == Qt.ForegroundRole:
            return QColor(Qt.black)
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)

        return None


class MaltQtStack(QWidget):
    def __init__(self, stackList):
        super().__init__()
        self.model = MaltQtStackTableModel(stackList)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)

    def updateStack(self, index):
        self.model.load_data(index)

    def horizontalHeader(self):
        return self.table_view.horizontalHeader()

    def verticalHeader(self):
        return self.table_view.verticalHeader()
