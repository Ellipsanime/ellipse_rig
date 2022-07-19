# coding: utf-8
# Copyright (c) 2018 Juline BRETON

from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PySide2.QtCore import Qt
from PySide2.QtUiTools import QUiLoader


class MayaWidget(QWidget):
    def __init__(self, name="", parent=None):
        QWidget.__init__(self, parent)

        self.setWindowTitle(name)
        self.setWindowFlags(Qt.Window)

        # Check if window is already open, and close it
        try:
            for win in QApplication.topLevelWindows():
                if win.objectName() == name + 'Window':
                    win.close()
        except:
            pass
        self.setObjectName(name)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)


def load_ui(ui_path):
    loader = QUiLoader()
    return loader.load(ui_path)


def get_maya_main_window():
    """
    Return Maya's main window
    :return:
    """
    from maya import OpenMayaUI as omui
    try:
        from shiboken import wrapInstance
    except:
        from shiboken2 import wrapInstance
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QMainWindow)