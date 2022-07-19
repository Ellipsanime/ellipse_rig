# coding: utf-8
# Copyright (c) 2017 Ubisoft Juline BRETON
import sys
if sys.path[0] != r'D:\Script\python_lib':
    sys.path.insert(0, r'D:\Script\python_lib')
from utils.maya_widget import load_ui
from PySide2.QtWidgets import QDialog
from PySide2.QtGui import QFont, QPixmap

import os

class WarningPopUp(QDialog):

    def __init__(self, icoPath=None, warningText='', parent=None, fontSize=8, textPrint=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('WARNING')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'warning.ui'))

        self.icoPath = icoPath
        self.warningText = warningText

        if self.icoPath:
            self.ui.labelIco.setPixmap(QPixmap(self.icoPath))

        self.ui.label.setText(self.warningText)
        self.ui.label.setFont(QFont('Times', fontSize))
        self.ui.label.setOpenExternalLinks(True)
        self.ui.label.setStyleSheet('QLabel::hover{color: rgb(251, 72, 131);}')
        if not textPrint:
            textPrint = '|------------------------------------------------------------------------------------------------------------------------\n' \
                        '|  /!\   WARNING : \n' \
                        '|                   >   ' + warningText + '\n' \
                        '|------------------------------------------------------------------------------------------------------------------------'
        print textPrint
        self.exec_()