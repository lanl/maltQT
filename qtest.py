#!/usr/bin/env python3
"""
Test qt installation - create window with title
"""

from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()
window.setWindowTitle("Now you see me...")
window.show()
app.exec()
