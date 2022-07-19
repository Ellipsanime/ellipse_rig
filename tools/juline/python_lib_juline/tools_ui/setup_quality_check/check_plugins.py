# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os
from ...utils.maya_widget import MayaWidget, load_ui
from ...utils import comment
# import for PyQt
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QListWidgetItem

import maya.cmds as mc
import maya.mel as mel


class SetupCheckSimple(MayaWidget):
    def __init__(self, parent=None, title='Check Turtle'):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'stp_qcheck_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        # SET INTERFACE
        self.title = title
        self.details = "Plugins loaded"
        self.info_message = "Clean Plugins"

        # COLOR CODE
        self.black = ["rgb(0, 0, 0);", '/ico/off_light.png']
        self.alpha = "rgba(0, 0, 0, 0)"
        self.orange = ["rgb(238, 161, 28)", '/ico/orange_light.png']
        self.green = ["rgb(15, 157, 88)", '/ico/green_light.png']
        self.red = ["rgb(236, 87, 71)", '/ico/red_light.png']
        self.blue = ["rgb(46, 132, 221)", '/ico/blue_light.png']

        self.set_check_tab()

        # SET BUTTONS
        self.ui.btn_check.clicked.connect(self.check)
        self.ui.btn_fix.clicked.connect(self.fix)

    def set_comment(self, text, color, nb=[]):
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color[0])
        if not nb:
            nb = [self.ui.btn_state_1]
        for btn in nb:
            btn.setIcon(QIcon(os.path.dirname(__file__) + color[1]))
            btn.setIconSize(QSize(15, 15))

    def switch_to_btn_hide(self):
        self.ui.btn_show_details.hide()
        self.ui.btn_hide_details.show()
        self.ui.tabWidget.show()
        self.ui.ls_details.show()

    def switch_to_btn_show(self):
        self.ui.btn_show_details.show()
        self.ui.btn_hide_details.hide()
        self.ui.tabWidget.hide()

    def set_check_tab(self):
        self.ui.lbl_check_name.setText(self.title)
        self.ui.lbl_check_name.setToolTip(self.info_message)
        self.ui.btn_ico.setIcon(QIcon(os.path.dirname(__file__) + '/ico/puzzle_green.png'))
        self.ui.lbl_help.setText(self.info_message)
        self.ui.tabWidget.setTabText(0, self.details)
        self.ui.btn_show_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/plus_grey_75.png'))
        self.ui.btn_show_details.setIconSize(QSize(15, 15))
        self.ui.btn_hide_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/minus_grey_75.png'))
        self.ui.btn_hide_details.setIconSize(QSize(15, 15))
        self.switch_to_btn_show()
        self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.ls_details.hide()
        self.ui.cb_auto_fix.setCheckState(Qt.Checked)

    def check(self):
        if self.ui.cb_check.isChecked():
            print "Checking " + self.title + "......"
            self.set_comment(text="Checking...", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
            self.ui.ls_details.clear()
            self.switch_to_btn_show()
            message = check_plugin()
            if message:
                for plug in message:
                    item = QListWidgetItem()
                    item.setText(plug[1])
                    self.ui.ls_details.addItem(item)
                self.set_comment(text="Need fix", color=self.orange, nb=[self.ui.btn_state_1])
                self.switch_to_btn_hide()
            else:
                self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1])
                self.set_comment(text="Good job !", color=self.green, nb=[self.ui.btn_state_2])
            print "======> Check " + self.title + " Finished"

            if self.ui.cb_auto_fix.isChecked():
                self.fix()
        else:
            print self.title + " Not checked"
            self.set_comment(text="Not checked", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])



    def fix(self):
        print "Fixing " + self.title + "......"
        fix_plugin()
        self.set_comment(text="Fixed", color=self.green, nb=[self.ui.btn_state_2])
        print "======> Fix " + self.title + " Finished"


import sys
ELIE_PATH = [r"T:\00_PROGRAMMATION\PRIMARY"]
sys.path.append(ELIE_PATH)
from smurf.sanitycheck.maya import mayaPluginCheck
plugCheck = mayaPluginCheck.mayaPluginCheck()


def fix_plugin():
    plugCheck.resolve()


def check_plugin():
    message = plugCheck.check()
    return message



