# coding: utf-8
# Copyright (c) 2018 Juline BRETON

import sys

if sys.path[0] != r'D:\Script\python_lib':
    sys.path.insert(0, r'D:\Script\python_lib')

from utils import open_ui
from tools_ui import attribute_box

reload(attribute_box)

open_ui.open_ui(attribute_box.AttrBox)
