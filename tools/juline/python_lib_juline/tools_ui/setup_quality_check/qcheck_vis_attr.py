
# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)

from ...utils.maya_widget import MayaWidget, load_ui
from ...library import attributesLib
from ...utils import undoable, exception_utils
reload(attributesLib)
# import for PyQt
from PySide2 import QtGui
from PySide2.QtCore import QSize, Qt, SIGNAL
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QListWidgetItem
import maya.cmds as mc

class SetupQCheckWidget(MayaWidget):
    def __init__(self, parent=None, title='Check Vis Attr'):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'stp_qcheck_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        # CHECK INFO
        self.attr_prefix = "switch_"
        self.info_message = "Check if vis attributes have the prefix 'switch_' for export alembic\n" \
                            "[RIGHT CLICK] select in the viewport the object(s) select in the list ctr"

        ### COLOR CODE
        self.alpha = "rgba(0, 0, 0, 0)"
        self.black = ["rgb(0, 0, 0);", '/ico/off_light.png']
        self.orange = ["rgb(238, 161, 28)", '/ico/orange_light.png']
        self.green = ["rgb(15, 157, 88)", '/ico/green_light.png']
        self.red = ["rgb(236, 87, 71)", '/ico/red_light.png']
        self.blue = ["rgb(46, 132, 221)", '/ico/blue_light.png']

        # SET INTERFACE
        self.title = title
        self.details = "List ctrl with vis without prefix"
        self.set_check_tab()
        self.ui.btn_show_details.clicked.connect(self.switch_to_btn_hide)
        self.ui.btn_hide_details.clicked.connect(self.switch_to_btn_show)

        # SET BUTTONS
        self.ui.btn_check.clicked.connect(self.check)
        self.ui.btn_fix.clicked.connect(self.fix)


        self.ls_orphan_cg = []


        self.ui.ls_details.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ls_details.connect(self.ui.ls_details, SIGNAL("customContextMenuRequested(QPoint)"), self.right_click)

    def right_click(self):
        selected_items = self.ui.ls_details.selectedItems()
        ls_selected_items = []
        if selected_items:
            for item in selected_items:
                ls_selected_items.append(item.text())
        mc.select(ls_selected_items)

    def switch_to_btn_hide(self):
        self.ui.btn_show_details.hide()
        self.ui.btn_hide_details.show()
        self.ui.tabWidget.show()
        self.ui.ls_details.show()

    def switch_to_btn_show(self):
        self.ui.btn_show_details.show()
        self.ui.btn_hide_details.hide()
        self.ui.tabWidget.hide()

    def set_comment(self, text, color, nb=[]):
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color[0])
        if not nb:
            nb = [self.ui.btn_state_1]
        for btn in nb:
            btn.setIcon(QIcon(os.path.dirname(__file__) + color[1]))
            btn.setIconSize(QSize(15, 15))

    def set_check_tab(self):
        self.ui.lbl_check_name.setText(self.title)
        self.ui.lbl_check_name.setToolTip(self.info_message)
        self.ui.lbl_help.setText(self.info_message)
        self.ui.tabWidget.setTabText(0, self.details)
        self.ui.btn_ico.setIcon(QIcon(os.path.dirname(__file__) + '/ico/eye.png'))
        self.ui.btn_show_details.setIconSize(QSize(30, 30))
        self.ui.btn_show_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/plus_grey_75.png'))
        self.ui.btn_show_details.setIconSize(QSize(15, 15))
        self.ui.btn_hide_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/minus_grey_75.png'))
        self.ui.btn_hide_details.setIconSize(QSize(15, 15))
        self.switch_to_btn_show()
        self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.ls_details.hide()

    def check(self):
        print "Checking " + self.title + "......"
        self.set_comment(text="Checking...", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.ls_details.clear()
        self.switch_to_btn_show()

        if self.ui.cb_check.isChecked():
            ls_attr_wanted = attributesLib.filter_attr(attrTarget='vis', searchList=None, typ='transform', extra=True)
            if ls_attr_wanted:
                self.switch_to_btn_hide()
                for transform in ls_attr_wanted:
                    item = QListWidgetItem()
                    item.setText(transform)
                    self.ui.ls_details.addItem(item)
                self.set_comment(text="Need fix", color=self.orange, nb=[self.ui.btn_state_1])

                if self.ui.cb_auto_fix.isChecked():
                    self.fix()

            else:
                self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1])
                self.set_comment(text="Good job !", color=self.green, nb=[self.ui.btn_state_2])
            print "======> Check " + self.title + " Finished"
        else:
            print self.title + " Not checked"
            self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])

    @undoable.undoable
    def fix(self):
        """
        if nothing selected: FIX ALL
        else: FIX selection
        :return:
        """
        print "Fixing " + self.title + "......"
        try:
            selected_items = self.ui.ls_details.selectedItems()
            ls_selected_items = []
            if selected_items:  # PARTIAL FIX
                for item in selected_items:
                    ls_selected_items.append(item.text())
                    item.setTextColor(QColor(0, 166, 81))
                    self.ui.ls_details.setItemSelected(item, False)
                ls_attr_wanted = attributesLib.filter_attr(attrTarget='vis', searchList=ls_selected_items, typ='transform')

            else:  # FIX ALL
                ls_attr_wanted = attributesLib.filter_attr(attrTarget='vis', searchList=None, typ='transform')

            for transform in ls_attr_wanted:
                mc.renameAttr(transform + '.vis', self.attr_prefix + 'vis')

            if selected_items:
                self.set_comment(text="Partial Fixed", color=self.blue, nb=[self.ui.btn_state_2])
                print "======> Partial Fix " + self.title + " Finished"
            else:
                self.set_comment(text="Fixed", color=self.green, nb=[self.ui.btn_state_2])
                print "======> Fix " + self.title + " Finished"
        except:
            self.set_comment(text="ERROR", color=self.red, nb=[self.ui.btn_state_2])
            print "======> Fix " + self.title + " ERROR <======"
            print exception_utils.FormatException()
