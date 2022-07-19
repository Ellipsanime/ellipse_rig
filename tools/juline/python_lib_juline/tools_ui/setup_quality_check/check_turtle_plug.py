# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os

from ...utils.maya_widget import MayaWidget, load_ui
from ...utils import comment
# import for PyQt
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton

import maya.cmds as mc
import maya.mel as mel


class SetupCheckSimple(MayaWidget):
    def __init__(self, parent=None, title='Check Turtle'):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'stp_qcheck_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        # SET INTERFACE
        self.title = title
        self.info_message = "Kill Turtle Plug"

        # COLOR CODE
        self.black = ["rgb(0, 0, 0);", '/ico/off_light.png']
        self.alpha = "rgba(0, 0, 0, 0)"
        self.orange = ["rgb(238, 161, 28)", '/ico/orange_light.png']
        self.green = ["rgb(15, 157, 88)", '/ico/green_light.png']
        self.red = ["rgb(236, 87, 71)", '/ico/red_light.png']
        self.blue = ["rgb(46, 132, 221)", '/ico/blue_light.png']

        self.add_btn_add_attr()
        self.set_check_tab()

        # SET BUTTONS
        self.ui.btn_check.clicked.connect(self.check)
        self.ui.btn_fix.clicked.connect(self.fix)
        self.ui.btn_attr.clicked.connect(clean_turtle_shelf)

    def set_comment(self, text, color, nb=[]):
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color[0])
        if not nb:
            nb = [self.ui.btn_state_1]
        for btn in nb:
            btn.setIcon(QIcon(os.path.dirname(__file__) + color[1]))
            btn.setIconSize(QSize(15, 15))

    def add_btn_add_attr(self):
        self.ui.btn_attr = QPushButton("Del SHELF")
        self.ui.btn_attr.setMinimumSize(90, 20)
        self.ui.btn_attr.setMaximumSize(90, 20)
        self.ui.lay_check.addWidget(self.ui.btn_attr)

    def set_check_tab(self):
        self.ui.lbl_check_name.setText(self.title)
        self.ui.lbl_check_name.setToolTip(self.info_message)
        self.ui.btn_ico.setIcon(QIcon(os.path.dirname(__file__) + '/ico/turtle.png'))
        self.ui.btn_show_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/none.png'))
        self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.btn_hide_details.hide()
        self.ui.tabWidget.hide()
        self.ui.cb_auto_fix.setCheckState(Qt.Checked)
        self.ui.line_comment.hide()

    def check(self):
        if self.ui.cb_check.isChecked():
            print "Checking " + self.title + "......"
            self.set_comment(text="Checking...", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
            turtle_node_exist = find_turtle()
            if turtle_node_exist:
                self.set_comment(text="Need fix", color=self.orange, nb=[self.ui.btn_state_1])
            else:
                self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1])
                self.set_comment(text="Good job !", color=self.green, nb=[self.ui.btn_state_2])
            print "======> Check " + self.title + " Finished"

            if self.ui.cb_auto_fix.isChecked():
                self.fix()
        else:
            print self.title + " Not checked"
            self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])

    def fix(self):
        print "Fixing " + self.title + "......"
        if mc.pluginInfo('TURTLE', query=True, loaded=True):
            mc.unloadPlugin('TURTLE', force=True)
        mel.eval("ilrClearSceneForce();")
        self.set_comment(text="Fixed", color=self.green, nb=[self.ui.btn_state_2])
        print "======> Fix " + self.title + " Finished"


def find_turtle():
    turtle_node_exist = []
    for turtle_node in [u'TurtleDefaultBakeLayer', u'TurtleBakeLayerManager', u'TurtleRenderOptions',
                        u'TurtleUIOptions']:
        if mc.objExists(turtle_node):
            turtle_node_exist.append(turtle_node)
            print turtle_node, " must be deleted"

    if mc.pluginInfo('TURTLE', query=True, loaded=True):
        turtle_node_exist.append('PLUGIN IS LOAD')
        comment.format_comment("Turtle Plugin is Load")
    return turtle_node_exist

def clean_turtle_shelf():
    if mc.shelfLayout('TURTLE', ex=True):
        mel.eval("""deleteShelfTab "TURTLE";""")