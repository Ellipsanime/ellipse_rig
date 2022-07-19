# coding: utf-8
# Copyright (c) 2018 Juline BRETON

import os
import sys
if sys.path[0] != r'D:\Script\python_lib':
    sys.path.insert(0, r'D:\Script\python_lib')

#from os.path.dirname(set_python_project) import set_python_project

from utils.maya_widget import MayaWidget, load_ui, get_maya_main_window
# import open ui
from tools_ui import attribute_box


import maya.cmds as mc

# import TOOLS to connect to the toolbox

class GuguBox(MayaWidget):
    def __init__(self, parent=None):
        MayaWidget.__init__(self, name="Setup Toolbox", parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'gugu_box.ui'))
        self.main_layout.addWidget(self.ui)

        ### TOOLS ###
        self.ui.btn_attr.clicked.connect(open_attr_box)

def open_attr_box():
    im = attribute_box.AttrBox(parent=get_maya_main_window())
    im.show()