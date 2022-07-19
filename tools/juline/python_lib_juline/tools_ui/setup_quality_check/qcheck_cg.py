# coding: utf-8

# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os, sys
pathTeamShare = r"C:\Users\juline.breton\STUFF\foundation_rig"
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)

from ...utils.maya_widget import MayaWidget, load_ui
from ......library import lib_controlGroup
from ...library import attributesLib
from ...utils import comment
import qcheck_hierarchy
# import for PyQt
from PySide2.QtCore import QSize, Qt, SIGNAL
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QListWidgetItem, QPushButton
import maya.cmds as mc

class SetupQCheckWidget(MayaWidget):
    def __init__(self, parent=None, title='Check Name'):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'stp_qcheck_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        ### COLOR CODE
        self.alpha = "rgba(0, 0, 0, 0)"
        self.black = ["rgb(0, 0, 0);", '/ico/off_light.png']
        self.orange = ["rgb(238, 161, 28)", '/ico/orange_light.png']
        self.green = ["rgb(15, 157, 88)", '/ico/green_light.png']
        self.red = ["rgb(236, 87, 71)", '/ico/red_light.png']
        self.blue = ["rgb(46, 132, 221)", '/ico/blue_light.png']

        self.add_btn_add_attr()

        # SET INTERFACE
        self.title = title
        self.details = "List orphan CG"
        self.info_message = "Check if cg_all exist\n" \
                            "Check if the TOP ControlGroup is cg_all\n" \
                            "[RIGHT CLICK] select in the viewport the object(s) select in the list"
        self.set_check_tab()
        self.ui.btn_show_details.clicked.connect(self.switch_to_btn_hide)
        self.ui.btn_hide_details.clicked.connect(self.switch_to_btn_show)
        self.ui.btn_attr.clicked.connect(qcheck_hierarchy.add_attr_master_all)

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
        self.ui.btn_attr.show()

    def switch_to_btn_show(self):
        self.ui.btn_show_details.show()
        self.ui.btn_hide_details.hide()
        self.ui.tabWidget.hide()
        self.ui.btn_attr.hide()

    def set_comment(self, text, color, nb=[]):
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color[0])
        if not nb:
            nb = [self.ui.btn_state_1]
        for btn in nb:
            btn.setIcon(QIcon(os.path.dirname(__file__) + color[1]))
            btn.setIconSize(QSize(15, 15))

    def set_state_color(self, nb, color):
        if color == 'off':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/off_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'orange':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/orange_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'red':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/red_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'blue':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/blue_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'green':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/green_light.png'))
            nb.setIconSize(QSize(15, 15))

    def add_btn_add_attr(self):
        self.ui.btn_attr = QPushButton("Add attr MASTER ALL")
        self.ui.lay_vertical.addWidget(self.ui.btn_attr)

    def set_check_tab(self):
        self.ui.lbl_check_name.setText(self.title)
        self.ui.lbl_check_name.setToolTip(self.info_message)
        self.ui.lbl_help.setText(self.info_message)
        self.ui.tabWidget.setTabText(0, self.details)
        self.ui.btn_ico.setIcon(QIcon(os.path.dirname(__file__) + '/ico/outliner.png'))
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
            ls_cg = lib_controlGroup.getAllCg() or []
            ls_cg_all = find_cg_all()
            self.ls_orphan_cg = cgHierarchie_check(cgs=ls_cg)
            if not ls_cg_all:  # If no cg_all
                self.switch_to_btn_hide()
                item = QListWidgetItem()
                item.setText("WARNING : NO CG ALL")
                item.setTextColor(QColor(236, 87, 71))
                self.ui.ls_details.addItem(item)
                self.set_comment(text="ERROR", color=self.red)

            elif len(ls_cg_all) == 1:
                if self.ls_orphan_cg:  # If orphan cg
                    self.switch_to_btn_hide()
                    item = QListWidgetItem()
                    item.setText(self.details)
                    for obj in self.ls_orphan_cg:
                        item = QListWidgetItem()
                        item.setText(obj)
                        self.ui.ls_details.addItem(item)
                    self.set_comment(text="Need fix", color=self.orange, nb=[self.ui.btn_state_1])

            elif len(ls_cg_all) > 1:


                print ls_cg_all
                comment.format_comment("Multiple cg_all in scene: \n" + str(ls_cg_all) + "\nplease parent manually\n"
                                       "SOON : a popup windows for select the TOP cg_all", center=True)

            else:
                self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1])
                self.set_comment(text="Good job !", color=self.green, nb=[self.ui.btn_state_2])
            print "======> Check " + self.title + " Finished"

            if self.ui.cb_auto_fix.isChecked():
                self.fix()
        else:
            print self.title + " Not checked"
            self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
            #self.ui.btn_state_1.setStyleSheet("background-color:" + self.black[0])

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
                cgHierarchie_fix(ls_selected_items)
                self.set_comment(text="Partial Fixed", color=self.blue, nb=[self.ui.btn_state_2])
                print "======> Partial Fix " + self.title + " Finished"
            else: # FIX ALL
                cgHierarchie_fix(self.ls_orphan_cg)
                self.set_comment(text="Fixed", color=self.green, nb=[self.ui.btn_state_2])
                print "======> Fix " + self.title + " Finished"
        except:
            self.set_comment(text="ERROR", color=self.red, nb=[self.ui.btn_state_2])
            print "======> Fix " + self.title + " ERROR <======"

#Author : Pierre Fabarez
import maya.cmds as cmds
from ......library import lib_pipe, lib_controlGroup

#Constant
MOD_ALL = 'MOD:ALL'
MOD_GEO = 'MOD:GEO'
LOC_GRP = 'MOD:LOC'
RIG_GRP = 'RIG'
RIG_ADD = 'RIG_ADD'
TRASH 	= 'TRASH'
CG_ALL 	= 'cg_all' or '*:cg_all'
c_WORLD = 'WORLD'

CAMERA = ['persp', 'top', 'front', 'side']
INIT_HIERARCHIE = ['TRASH', 'MOD:ALL']
INIT_ALL_CHILD = [MOD_GEO, LOC_GRP, c_WORLD, RIG_GRP]

# Check Wrong Cg Hierarchie

def cg_all_exist(cgs=[], *args):
    # Check CgAll
    if CG_ALL not in cgs or cmds.listConnections('%s.parent' % CG_ALL):
        return False
    else:
        return True

def cgHierarchie_check(cgs=[], *args):
    orphanCg = []

    # Check allCg Parent
    for cg in cgs:
        cgHi = [cg]
        if not cg in orphanCg:
            cgParent = cmds.listConnections('%s.parent' % cg)

            while cgParent:
                cgHi.append(cgParent[0])
                cgParent = cmds.listConnections('%s.parent' % cgParent[0])

        if cgHi[-1] != CG_ALL:
            orphanCg.extend(cgHi)

    return orphanCg


def cgHierarchie_fix(cgs=[]):
    for cg in cgs:
        lib_controlGroup.parentCg(cg, CG_ALL)

def find_cg_all():
    """
    Find cg_all
    Author : Juline BRETON
    :return: cg_all or ls_cg_all
    """
    ls_all_cg = lib_controlGroup.getAllCg() or []
    ls_cg_all = []
    for cg in ls_all_cg:
        if "cg_all" in cg:
            ls_cg_all.append(cg)
    return ls_cg_all
    """
    # If juste 1 cg_all in scene parent
    if ls_cg_all:
        if len(ls_cg_all) == 1:
            cg_all = ls_cg_all[0]
            return cg_all
    else:
        comment.format_comment("Multiple cg_all in scene, \nplease parent manually\n"
                               "SOON : a popup windows for select the TOP cg_all", center=True)
        return ls_cg_all
    """

def find_master_all():
    ls_master_all = attributesLib.get_attr_state('MASTER_ALL', True) or []
    if len(ls_master_all) == 1:
        master_all = ls_master_all[0]