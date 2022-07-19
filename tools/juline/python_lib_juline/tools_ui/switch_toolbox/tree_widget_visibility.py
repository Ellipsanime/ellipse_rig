# coding: utf-8
# Copyright (c) 2018 Ubisoft Juline BRETON

__author__ = "Juline BRETON"

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)
from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui

import maya.cmds as mc
from functools import partial
from pprint import pprint
import json

from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QBrush
from PySide2.QtWidgets import QTreeWidgetItem, QComboBox


import attribute_state, switch_fonction
from name_lib import SwitchName

reload(attribute_state)

class QTreeWidgetVisibility(MayaWidget):

    def __init__(self, parent=None):
        MayaWidget.__init__(self, "Tree Widget Visibility", parent=parent)
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ui/tree_widget_visibility.ui'))
        self.main_layout.addWidget(self.ui)

        # ------------------------------------------- VARIABLES ------------------------------------------- #
        self.rigadd = switch_fonction.find_rigadd()
        self.ctrl_switch, self.prefix_attr = switch_fonction.find_ctrl_switch()
        self.dict_vis = {}
        self.state = ['Hide', 'Show']
        self.prefix_drivenkey = 'dvk_'
        self.attr_info_name = SwitchName.MOD_DICT

        # ------------------------------------------ EXTERNAL UI ------------------------------------------ #
        self.attr_state = attribute_state.AttributeState()
        # ------------------------------------------- SETUP UI -------------------------------------------- #
        self.ui.layout_attribute_state.addWidget(self.attr_state)

        # ---------------------------------------- START FONCTIONS ---------------------------------------- #
        self.set_icons()
        self.set_tree_item_state()

        # ------------------------------------------ USER ACTIONS ----------------------------------------- #
        self.ui.btn_add.clicked.connect(self.update_item)
        self.ui.btn_remove.clicked.connect(self.remove_obj)
        self.ui.btn_clear.clicked.connect(self.clear_obj)
        self.ui.btn_sel_viewport.clicked.connect(self.select_in_viewport)
        self.ui.btn_set_hide.clicked.connect(partial(self.set_all, 0))
        self.ui.btn_set_show.clicked.connect(partial(self.set_all, 1))
        self.ui.btn_print_visibility.clicked.connect(self.print_state_visibility)
        self.ui.btn_set_visibility.clicked.connect(self.add_state_visibility)
        self.attr_state.ui.combo_box_attributes.currentIndexChanged.connect(self.set_tree_item_state)
        self.attr_state.ui.combo_box_switch.currentIndexChanged.connect(self.set_tree_item_state)

    def set_icons(self):
        self.ui.btn_add.setIcon(QIcon(os.path.dirname(__file__) + '/icons/add.png'))
        self.ui.btn_remove.setIcon(QIcon(os.path.dirname(__file__) + '/icons/remove.png'))
        self.ui.btn_clear.setIcon(QIcon(os.path.dirname(__file__) + 'clear.png'))
        self.ui.btn_sel_viewport.setIcon(QIcon(os.path.dirname(__file__) + 'search.png'))
        self.ui.btn_set_visibility.setIcon(QIcon(os.path.dirname(__file__) + '/icons/eye-illuminati.png'))
        self.ui.btn_set_visibility.setIconSize(QtCore.QSize(30, 30))

    def add_obj(self, obj):
        '''
          Add item on tree widget
        :param obj :type string
        :return: item
        '''
        comboBox = QComboBox(self.ui.list_obj)
        comboBox.addItems(self.state)
        comboBox.setCurrentIndex(1)
        item = QTreeWidgetItem()
        item.setText(0, obj)
        self.ui.list_obj.insertTopLevelItem(0, item)
        self.ui.list_obj.setItemWidget(item, 1, comboBox)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
        return item

    def remove_obj(self):
        '''
          Remove an item of tree widget
        :return:
        '''
        for item in self.ui.list_obj.selectedItems():
            index = self.ui.list_obj.indexFromItem(item).row()
            self.ui.list_obj.takeTopLevelItem(index)

    def clear_obj(self):
        self.ui.list_obj.clear()

    def update_item(self):
        for obj in mc.ls(sl=True):
            if not self.ui.list_obj.findItems(obj, Qt.MatchExactly|Qt.MatchRecursive, 0):
                self.add_obj(obj)

    def select_in_viewport(self):
        '''
          For MAYA
          Select in the viewport the current selection in the tree widget
        :return:
        '''
        l_items = self.ui.list_obj.selectedItems()
        l_obj = []
        for item in l_items:
            l_obj.append(item.text(0))
        mc.select(l_obj)

    def add_data_visibility(self):
        '''
          Update dict information
            dict_vis = {
                'attribute_name':
                    {'state_1':
                        {'transform_name': True/False,
                         'transform_name': True/False
                         },
                    'state_2':
                         {'transform_name': True/False,
                         'transform_name': True/False
                         }
                    }
                }
        '''
        attr = self.attr_state.ui.combo_box_attributes.currentText()
        state = str(self.attr_state.ui.combo_box_switch.currentIndex()) + '_' + self.attr_state.ui.combo_box_switch.currentText()
        l_items = self.ui.list_obj.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)

        if not attr in self.dict_vis.keys():
            self.dict_vis[attr] = {}
        if not state in self.dict_vis[attr].keys():
            self.dict_vis[attr][state] = {}
        for item in l_items:
            item.setForeground(0, QBrush(Qt.cyan))
            self.dict_vis[attr][state][item.text(0)] = self.ui.list_obj.itemWidget(item, 1).currentIndex()

    def set_all(self, index):
        '''
          Set all item of the tree widget to the same index
        :param index:
        :return:
        '''
        all_items = self.ui.list_obj.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
        for item in all_items:
            self.ui.list_obj.itemWidget(item, 1).setCurrentIndex(index)

    def print_state_visibility(self):
        pprint(self.dict_vis)

    def add_state_visibility(self):
        '''
          Update of dict information and create switch with driven key node(s)
        :return:
        '''
        self.add_data_visibility()
        self.create_state_visibility()

    def create_state_visibility(self):
        '''
          Create switch with driven key node(s)
          Update dict information and set the color of the tree widget when it's done
        '''
        if self.dict_vis:
            pprint(self.dict_vis)
            for attr in self.dict_vis.keys():
                for state in self.dict_vis[attr]:
                    for obj in self.dict_vis[attr][state]:
                        mc.setDrivenKeyframe(obj, attribute='v', currentDriver=self.ctrl_switch + '.' + attr, driverValue=float(state.split('_')[0]), value=self.dict_vis[attr][state][obj])
                # ----- STOCKAGE INFO ----- #
                if not mc.objExists(self.ctrl_switch + '.' + self.attr_info_name):
                    mc.addAttr(self.ctrl_switch, longName = self.attr_info_name, dataType='string')
                mc.setAttr(self.ctrl_switch + '.' + self.attr_info_name, json.dumps(self.dict_vis), type='string')
        else:
            print 'no info for STATE_VIS'

    def set_tree_item_state(self):
        '''
          Update the tree widget when the current attribute or state changed
        :return:
        '''
        if mc.objExists(self.ctrl_switch + '.' + self.attr_info_name):
            if mc.getAttr(self.ctrl_switch + '.' + self.attr_info_name):
                dict_vis_str = mc.getAttr(self.ctrl_switch + '.' + self.attr_info_name)
                self.dict_vis = switch_fonction.convert_unicode_to_dict(dict_vis_str)

                attr = self.attr_state.ui.combo_box_attributes.currentText()
                state = str(self.attr_state.ui.combo_box_switch.currentIndex()) + '_' + self.attr_state.ui.combo_box_switch.currentText()
                if attr in self.dict_vis.keys():
                    if str(state) in self.dict_vis[attr].keys():
                        for obj in self.dict_vis[attr][str(state)].keys():
                            l_items = self.ui.list_obj.findItems(obj, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive) or []
                            if l_items:
                                item = l_items[0]
                            else:
                                item = self.add_obj(obj)
                            self.ui.list_obj.itemWidget(item, 1).setCurrentIndex(self.dict_vis[attr][str(state)][obj])
                            item.setForeground(0, QBrush(Qt.cyan))
                    else:
                        for item in self.ui.list_obj.findItems('*', Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive):
                            item.setForeground(0, QBrush(Qt.white))
                else:
                    self.clear_obj()
            else:
                self.dict_vis = {}