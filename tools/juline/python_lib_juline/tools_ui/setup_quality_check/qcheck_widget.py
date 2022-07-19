# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os, sys

pathTeamShare = r'C:\Users\juline.breton\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)

from ...utils.maya_widget import MayaWidget, load_ui

import maya.cmds as mc
from PySide2 import QtCore
from PySide2.QtGui import QIcon, QBrush, QColor, QRegion
from PySide2.QtWidgets import qApp


class SetupQCheckWidget(MayaWidget):
    def __init__(self, parent=None, title='Check Name', help='Description of the check fonction', icoPath=None,
                 checkFonctionPath=None, fixFonctionPath=None):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'setup_quality_check.ui'))
        self.main_layout.addWidget(self.ui)

        self.title = title
        self.help = help
        self.checkFonctionPath = checkFonctionPath
        self.fixFonctionPath = fixFonctionPath

        self.set_check_tab()

        self.ui.btn_check.clicked.connect(self.check_layout)
        self.ui.btn_fix.clicked.connect(self.fix_layout)

        self.ui.lView_details.hide()

        self.ls_check = [self.ui.cb_check]

        ### COLOR CODE
        self.black = "rgb(0, 0, 0);"
        self.alpha = "rgba(0, 0, 0, 0)"
        self.orange = "rgb(238, 161, 28)"
        self.green = "rgb(15, 157, 88)"
        self.red = "rgb(236, 87, 71)"

    def set_comment(self, text, color):
        self.ui.btn_state.setStyleSheet("background-color:" + color)
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color)

    def set_check_tab(self):
        self.ui.tabWidget.setTabText(0, self.title)
        self.ui.lbl_help.setText(self.help)

    def check_layout(self):
        print "Checking " + self.title + "......"
        self.ui.line_comment.clear()
        ## TURTLE NODE
        if self.ui.cb_check.isChecked():
            self.checkFonctionPath
            self.set_comment(text="Need fix", color=self.orange)
            print "======> Check " + self.title + " Finished"
            if self.ui.cb_auto_fix.isChecked():
                self.fix_layout()
        else:
            print self.title + " Not checked"
            self.ui.btn_state.setStyleSheet("background-color:" + self.black)

    def fix_layout(self):
        print "Fixing " + self.title + "......"
        try:
            # mc.delete([u'TurtleDefaultBakeLayer', u'TurtleBakeLayerManager', u'TurtleRenderOptions', u'TurtleUIOptions'])
            self.fixFonctionPath()
            self.ui.btn_state.setStyleSheet("background-color:" + self.green)
            # circle = QRegion.Ellipse
            # self.ui.btn_state.setMask(circle)
            self.ui.line_comment.setText("Fixed")
            print "======> Fix " + self.title + " Finished"
        except:
            self.set_comment(text="Pb see Details", color=self.red)
            print "======> Fix " + self.title + " ERROR <======"

