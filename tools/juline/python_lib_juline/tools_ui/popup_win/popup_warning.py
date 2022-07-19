# coding: utf-8
# Author : Juline BRETON
# 2018_11_02

import os
import sys
from python_lib_juline.utils.maya_widget import load_ui
from PySide2.QtGui import QFont, QIcon, QPixmap
from python_lib_juline.utils.maya_widget import MayaWidget

## Ajouter des types prédéfinis

class PopupWarning(MayaWidget):

    def __init__(self, title='WARNING', icoPath=os.path.join(os.path.dirname(__file__), 'ico/warning.png'), text='',
                 parent=None, fontSize=12):
        """
        :param str title:
        :param str icoPath:
        :param str text:
        :param parent:
        :param int fontSize:
        """
        MayaWidget.__init__(self, name=title, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'popup_warning.ui'))
        self.main_layout.addWidget(self.ui)
        self.setWindowIcon(QIcon(icoPath))

        if icoPath:
            self.ui.lbl_icon.setPixmap(QPixmap(icoPath).scaledToWidth(60))

        if text:
            self.ui.lbl_text.setText(text)
            self.ui.lbl_text.setFont(QFont('Corbel', fontSize))

        self.ui.lbl_signature.setPixmap(QPixmap(os.path.dirname(__file__) + '/ico/signature.png').scaledToWidth(70))

def open_warning(textWarning):
    from utils import open_ui
    from functools import partial
    open_ui.open_ui(partial(PopupWarning, text=textWarning))