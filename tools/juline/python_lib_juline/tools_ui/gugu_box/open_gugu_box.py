# coding: utf-8
# Copyright (c) 2018 Juline BRETON

import sys
if sys.path[0] != r'D:\Script\python_lib':
    sys.path.insert(0, r'D:\Script\python_lib')

from tools_ui import gugu_box
from utils.maya_widget import get_maya_main_window

reload(gugu_box)

im = gugu_box.GuguBox(parent=get_maya_main_window())
im.show()
