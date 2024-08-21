""" utilities common to all my Qt programs """
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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QFileDialog, QTableWidgetItem


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


def fileSelect(
    parent,
    caption="Select File",
    startDir=None,
    myFilter=None,
    exists=False,
    inOption=None,
):
    """Selects a file"""
    if inOption is None:
        myOptions = QFileDialog.DontUseNativeDialog
    else:
        myOptions = inOption | QFileDialog.DontUseNativeDialog

    if exists:
        newFile = QFileDialog.getOpenFileName(
            parent, caption, startDir, filter=myFilter, options=myOptions
        )
    else:
        newFile = QFileDialog.getSaveFileName(
            parent, caption, startDir, filter=myFilter, options=myOptions
        )
    newFile = None if len(newFile[0]) == 0 else newFile[0]
    return newFile
