""" utilities common to all my Qt programs """
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem


def rightAlignedItem(theText):
    """Returns a right aligned table item"""
    item = QTableWidgetItem(theText)
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return item


def leftAlignedItem(theText):
    """Returns a right aligned table item"""
    item = QTableWidgetItem(theText)
    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    return item
