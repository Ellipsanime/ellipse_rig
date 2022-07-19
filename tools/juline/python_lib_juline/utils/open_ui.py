# coding: utf-8
# Copyright (c) 2018 Juline BRETON
# 2018_11_02

# for open UI without args

import get_maya_main_window


def open_ui(my_class):
    ui = my_class(parent=get_maya_main_window())
    ui.show()