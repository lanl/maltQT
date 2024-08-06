#!/usr/bin/env python3
"""
Test qt installation - create window with title
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


from PySide2.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()
window.setWindowTitle("Now you see me...")
window.show()
app.exec_()
