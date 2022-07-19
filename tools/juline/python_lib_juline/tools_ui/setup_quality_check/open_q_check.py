# coding: utf-8
# Copyright (c) 2018 Juline BRETON
from ellipse_rig.tools.juline.python_lib_juline.tools_ui import setup_quality_check
from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import get_maya_main_window

reload(setup_quality_check)

im = setup_quality_check.SetupQCheckWindow(parent=get_maya_main_window())
im.show()
