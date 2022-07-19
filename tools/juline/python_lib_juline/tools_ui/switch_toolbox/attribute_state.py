# coding: utf-8
# Copyright (c) 2019 Juline BRETON

__author__ = "Juline BRETON"

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)
from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui

import maya.cmds as mc

from PySide2 import QtCore
from PySide2.QtGui import QIcon


import switch_fonction

reload(switch_fonction)

class AttributeState(MayaWidget):

    def __init__(self, parent=None):
        MayaWidget.__init__(self, "Attribute state", parent=parent)
        self.setWindowTitle('Attribute state')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ui/attribute_state.ui'))
        self.main_layout.addWidget(self.ui)

        # ------------------------------------------- VARIABLES ------------------------------------------- #
        self.ctrl_switch, self.attr_prefix = switch_fonction.find_ctrl_switch()
        self.step = switch_fonction.get_step()

        # ---------------------------------------- START FONCTIONS ---------------------------------------- #
        self.load_asset_name()
        self.set_icons()
        self.set_step()
        self.load_ctrl_switch_attributes()
        self.load_ctrl_switch_states()

        # ------------------------------------------ USER ACTIONS ----------------------------------------- #
        self.ui.btn_gattaca.clicked.connect(open_gattaca_link)
        self.ui.combo_box_step.currentIndexChanged.connect(self.load_ctrl_switch_attributes)
        self.ui.combo_box_attributes.currentIndexChanged.connect(self.load_ctrl_switch_states)

    def set_icons(self):
        self.ui.combo_box_step.setItemIcon(0, QIcon(os.path.dirname(__file__) + '/icons/mod.png'))
        self.ui.combo_box_step.setItemIcon(1, QIcon(os.path.dirname(__file__) + '/icons/colors.png'))
        self.ui.combo_box_step.setItemIcon(2, QIcon(os.path.dirname(__file__) + '/icons/setup.png'))
        self.ui.btn_gattaca.setIcon(QIcon(os.path.dirname(__file__) + '/icons/gattaca.png'))
        self.ui.btn_gattaca.setIconSize(QtCore.QSize(25, 25))

    def set_step(self):
        '''
          Set the UI in the current step mode
        '''
        if self.step == 'modeling':
            self.ui.combo_box_step.setCurrentIndex(0)
        if self.step == 'surfacing':
            self.ui.combo_box_step.setCurrentIndex(1)
        if self.step == 'setup':
            self.ui.combo_box_step.setCurrentIndex(2)

    def load_asset_name(self):
        asset_name = switch_fonction.get_asset_name()
        self.ui.label_asset_name.setText(asset_name)

    def load_ctrl_switch_attributes(self):
        '''
          Load the extra attribute(s) of the current/selected step controller
        '''
        self.ctrl_switch, self.attr_prefix = switch_fonction.find_ctrl_switch(self.ui.combo_box_step.currentText())

        if mc.objExists(self.ctrl_switch):
            all_extra_attr = mc.listAttr(self.ctrl_switch, keyable=True, userDefined=True) or []
            l_extra_attr = []
            for extra_attr in all_extra_attr:
                if extra_attr.startswith(self.attr_prefix):
                    l_extra_attr.append(extra_attr)
            self.ui.combo_box_attributes.clear()
            if l_extra_attr:
                self.ui.combo_box_attributes.addItems(l_extra_attr)
        else:
            self.ui.combo_box_attributes.clear()
            self.ui.combo_box_switch.clear()

    def load_ctrl_switch_states(self):
        '''
          Load the enums of the selected attribute
        '''
        if self.ctrl_switch:
            attr = self.ui.combo_box_attributes.currentText()
            if attr:
                l_enum = switch_fonction.get_enum_list(self.ctrl_switch, attr)
                self.ui.combo_box_switch.clear()
                self.ui.combo_box_switch.addItems(l_enum)

def open_gattaca_link():
    '''
      Open Gattaca information page of the current Asset
    '''
    link = switch_fonction.get_gattace_link()
    os.startfile(link)
