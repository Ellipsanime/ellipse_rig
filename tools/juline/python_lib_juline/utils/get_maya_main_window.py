# coding: utf-8

from PySide2.QtWidgets import QMainWindow
from maya import OpenMayaUI as omui

def get_maya_main_window():
    """
    Return Maya's main window
    :return:
    """
    try:
        from shiboken import wrapInstance
    except:
        from shiboken2 import wrapInstance
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QMainWindow)