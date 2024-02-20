"""Create a stack view"""

from PySide6.QtWidgets import QWidget, QTableView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class MaltQtStackTableModel(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.row_count = 0
        self.column_count = 2
        self.lines = []
        self.functions = []
        self.lastIndex = None

    def load_data(self, stack, index):
        if self.lastIndex != index:
            if len(stack) < 2:
                self.lines = [-1]
                self.functions = ["no stack available"]
            else:
                self.lines = [x[2] for x in stack]
                self.functions = [x[0] for x in stack]
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
            return Qt.AlignLeft if column == 1 else Qt.AlignRight
        elif role == Qt.ForegroundRole:
            return QColor(Qt.black)
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        return None


class MaltQtStack(QWidget):
    def __init__(self):
        super().__init__()
        self.model = MaltQtStackTableModel()

        self.table_view = QTableView()
        self.table_view.setModel(self.model)

    def updateStack(self, stack, index):
        self.model.load_data(stack, index)

    def horizontalHeader(self):
        return self.table_view.horizontalHeader()

    def verticalHeader(self):
        return self.table_view.verticalHeader()
