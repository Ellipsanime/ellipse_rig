# coding: utf-8
# Copyright (c) 2019 Juline BRETON

__author__ = "Juline BRETON"

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)

from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui

from PySide2 import QtCore
from PySide2.QtGui import QIcon
import tree_widget_position, tree_widget_visibility, attribute_state, tree_widget_switches #, switch_fonction

#from llc.maya.setup.toolbox import setup_toolbox

from ellipse_rig.tools.juline.python_lib_juline.library import functionsLib
#### GATTACA ####
#import link_gattaca_dcc
#import emon_api as eapi

import maya.cmds as mc

reload(attribute_state)
reload(tree_widget_position)
reload(tree_widget_visibility)
reload(tree_widget_switches)
reload(switch_fonction)


class SwitchEnumToolbox(MayaWidget):

    def __init__(self, parent=None):
        MayaWidget.__init__(self, "Switch enum toolbox", parent=parent)
        self.setWindowTitle('Switch enum toolbox')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ui/switch_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        # ------------------------------------------- VARIABLES ------------------------------------------- #
        self.long_name = False

        # ------------------------------------------ EXTERNAL UI ------------------------------------------ #
        self.attr_state = attribute_state.AttributeState()
        self.tree_position = tree_widget_position.QTreeWidgetPosition()
        self.tree_visibility = tree_widget_visibility.QTreeWidgetVisibility()
        self.tree_texture = tree_widget_switches.QTreeWidgetSwitches()

        # ------------------------------------------- SETUP UI -------------------------------------------- #
        self.ui.layout_attribute_state.addWidget(self.attr_state)
        self.ui.layout_tree_position.addWidget(self.tree_position)
        self.ui.layout_tree_visibility.addWidget(self.tree_visibility)
        self.ui.layout_tree_switchs.addWidget(self.tree_texture)

        # ---------------------------------------- START FONCTIONS ---------------------------------------- #
        self.hide_attribute_state()
        self.set_icons()
        self.set_color_interface()

        # ------------------------------------------ USER ACTIONS ----------------------------------------- #
        self.ui.btn_set_switch_tech_notes.clicked.connect(self.set_switch_tech_notes)
        self.ui.btn_del_switch.clicked.connect(self.delete_existing_switch)
        #self.ui.btn_attr_toolbox.clicked.connect(setup_toolbox.attribute_tool_attr)
        self.attr_state.ui.combo_box_step.currentIndexChanged.connect(self.set_all_step)
        self.attr_state.ui.combo_box_attributes.currentIndexChanged.connect(self.set_all_attr)
        self.attr_state.ui.combo_box_switch.currentIndexChanged.connect(self.set_all_switch)

        # ----------------------------------------- BEFORE PUBLISH ---------------------------------------- #
        #self.ui.btn_optimise.clicked.connect(optimise)

    @functionsLib.undoable
    def delete_existing_switch(self):
        '''
          Only for modeling for the moment
        '''
        print 'deleting...'
        step = self.attr_state.ui.combo_box_step.currentText()
        attr = self.attr_state.ui.combo_box_attributes.currentText()
        #switch_fonction.deleting_switch(step, attr)
        if step == 'modeling':
            self.tree_visibility.ui.list_obj.clear()

    def set_all_step(self):
        '''
                 Link all attributes state ui for share informations
        '''
        # ----------------------------------------------------- #
        #  To add :                                             #
        #       > Give the posibility to load or not groupBox   #
        # ----------------------------------------------------- #
        self.tree_position.attr_state.ui.combo_box_step.setCurrentIndex(self.attr_state.ui.combo_box_step.currentIndex())
        self.tree_visibility.attr_state.ui.combo_box_step.setCurrentIndex(self.attr_state.ui.combo_box_step.currentIndex())
        self.tree_texture.attr_state.ui.combo_box_step.setCurrentIndex(self.attr_state.ui.combo_box_step.currentIndex())
        self.set_color_interface()

    def set_color_interface(self):
        '''
          For more visibility of changing step, every step has a color
        '''
        if self.attr_state.ui.combo_box_step.currentIndex() == 0:
            self.ui.position.setStyleSheet(  "QGroupBox{border-color: rgb(226, 88, 33)}")
            self.ui.switches.setStyleSheet(  "QGroupBox{border-color: rgb(226, 88, 33)}")
            self.ui.visibility.setStyleSheet("QGroupBox{border-color: rgb(226, 88, 33)}")
        if self.attr_state.ui.combo_box_step.currentIndex() == 1:
            self.ui.position.setStyleSheet(  "QGroupBox{border-color: rgb(143, 58, 199)}")
            self.ui.switches.setStyleSheet(  "QGroupBox{border-color: rgb(143, 58, 199)}")
            self.ui.visibility.setStyleSheet("QGroupBox{border-color: rgb(143, 58, 199)}")
        if self.attr_state.ui.combo_box_step.currentIndex() == 2:
            self.ui.position.setStyleSheet(  "QGroupBox{border-color: rgb(37, 174, 150)}")
            self.ui.switches.setStyleSheet(  "QGroupBox{border-color: rgb(37, 174, 150)}")
            self.ui.visibility.setStyleSheet("QGroupBox{border-color: rgb(37, 174, 150)}")

    def set_all_attr(self):
        '''
          Link all attributes state ui for share informations
        '''
        # --------------------------------------------- #
        #  To add :                                     #
        #      > Check if ui is loaded                  #
        # --------------------------------------------- #
        self.tree_position.attr_state.ui.combo_box_attributes.setCurrentIndex(self.attr_state.ui.combo_box_attributes.currentIndex())
        self.tree_visibility.attr_state.ui.combo_box_attributes.setCurrentIndex(self.attr_state.ui.combo_box_attributes.currentIndex())
        self.tree_texture.attr_state.ui.combo_box_attributes.setCurrentIndex(self.attr_state.ui.combo_box_attributes.currentIndex())

    def set_all_switch(self):
        '''
          Link all attributes state ui for share informations
        '''
        # --------------------------------------------- #
        #  To add :                                     #
        #      > Check if ui is loaded                  #
        # --------------------------------------------- #
        self.tree_position.attr_state.ui.combo_box_switch.setCurrentIndex(self.attr_state.ui.combo_box_switch.currentIndex())
        self.tree_visibility.attr_state.ui.combo_box_switch.setCurrentIndex(self.attr_state.ui.combo_box_switch.currentIndex())
        self.tree_texture.attr_state.ui.combo_box_switch.setCurrentIndex(self.attr_state.ui.combo_box_switch.currentIndex())

    def hide_attribute_state(self):
        '''
          Hide the attribute state ui of type switch ui
        '''
        # --------------------------------------------- #
        #  To add :                                     #
        #      > Check if ui is loaded                  #
        # --------------------------------------------- #
        self.tree_position.attr_state.hide()
        self.tree_visibility.attr_state.hide()
        self.tree_texture.attr_state.hide()

    def set_icons(self):
        self.ui.btn_del_switch.setIcon(QIcon(os.path.dirname(__file__) + '/icons/delete.png'))
        self.ui.btn_attr_toolbox.setIcon(QIcon(os.path.dirname(__file__) + '/icons/attr_tool.png'))
        self.ui.btn_attr_toolbox.setIconSize(QtCore.QSize(25, 25))

    def set_switch_tech_notes(self):
        '''
          Set switch(es) from Gattaca informations in :
          asset.switchMod / asset.switchTex / asset.switchAni
        '''
        # ----------------------------------------------- #
        #  Only work with Gattaca staging for the moment  #
        # ----------------------------------------------- #
        ast = eapi.Asset.get(self.attr_state.ui.label_asset_name.text())
        link_gattaca_dcc.CreateAttributSwitch(ast, self.attr_state.ui.combo_box_step.currentText())
        tree_widget_visibility.QTreeWidgetVisibility.create_state_visibility(tree_widget_visibility.QTreeWidgetVisibility())
        self.attr_state.ui.combo_box_switch.setCurrentIndex(1)
        self.attr_state.ui.combo_box_switch.setCurrentIndex(0)

def optimise():
    '''
      Delete the driven key nodes connected in shape
           &
      Mutalised nodes
    '''
    print 'OLD'
    #switch_fonction.optimise_node_switch()


