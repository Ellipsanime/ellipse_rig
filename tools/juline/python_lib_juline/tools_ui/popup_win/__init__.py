# coding: utf-8
# Author : Juline BRETON

import os
import sys
from python_lib_juline.utils.maya_widget import load_ui
from PySide2.QtWidgets import QDialog
from PySide2.QtGui import QFont, QIcon, QPixmap

## Ajouter des types prédéfinis

class PopupWin(QDialog):

    def __init__(self, title='', icoPath=None, text='', btn1='', btn2=[], btn3=[], parent=None, fontSize=8):
        """
        :param str title:
        :param str icoPath:
        :param str text:
        :param list btn1: [ arg1 (str), arg2 (fonction) ]
        :param list btn1: [ arg1 (str), arg2 (fonction) ]
        :param list btn1: [ arg1 (str), arg2 (fonction) ]
        :param parent:
        :param int fontSize:
        """
        QDialog.__init__(self, parent)

        self.setWindowTitle(title)
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'pop_up_win.ui'))
        self.setWindowIcon(QIcon(icoPath))

        if icoPath:
            self.ui.lbl_icon.setPixmap(QPixmap(icoPath))

        if text:
            self.ui.lbl_text.setText(text)
            self.ui.lbl_text.setFont(QFont('Corbel', fontSize))

        if len(btn1) == 2:
            self.ui.btn_1.setText(btn1)
            #self.ui.btn_1.clicked.connect(btn1[1])
        else:
            self.ui.btn_1.hide()

        if len(btn2) == 2:
            self.ui.btn_2.setText(btn2[0])
            self.ui.btn_2.clicked.connect(btn2[1])
        else:
            self.ui.btn_2.hide()

        if len(btn3) == 2:
            self.ui.btn_3.setText(btn3[0])
            self.ui.btn_3.clicked.connect(btn3[1])
        else:
            self.ui.btn_3.hide()

        self.ui.btn_signature.setIcon(QIcon(os.path.dirname(__file__) + '/ico/signature.png'))

        self.exec_()