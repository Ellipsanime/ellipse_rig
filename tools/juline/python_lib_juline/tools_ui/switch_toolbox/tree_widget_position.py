# coding: utf-8
# Copyright (c) 2019 Juline BRETON

__author__ = "Juline BRETON"

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)
from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui

import json
import maya.cmds as mc
from pprint import pprint

from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QBrush
from PySide2.QtWidgets import QTreeWidgetItem

import switch_fonction, attribute_state, name_lib


reload(switch_fonction)
reload(attribute_state)


class QTreeWidgetPosition(MayaWidget):

    def __init__(self, parent=None):
        MayaWidget.__init__(self, "Tree Widget position", parent=parent)
        self.setWindowTitle('Tree Widget position')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ui/tree_widget_position.ui'))

        self.main_layout.addWidget(self.ui)
        # ------------------------------------------- VARIABLES ------------------------------------------- #
        self.list_obj = []
        self.rigadd = switch_fonction.find_rigadd()
        self.attr_info_name = name_lib.SwitchName.POS_DICT
        self.dict_position = {}

        # ------------------------------------------ EXTERNAL UI ------------------------------------------ #
        self.attr_state = attribute_state.AttributeState()
        # ------------------------------------------- SETUP UI -------------------------------------------- #
        self.ui.layout_attribute_state.addWidget(self.attr_state)

        # ---------------------------------------- START FONCTIONS ---------------------------------------- #
        self.set_icons()
        #self.get_data()
        self.set_tree_item_state()

        # ------------------------------------------ USER ACTIONS ----------------------------------------- #
        self.ui.btn_add.clicked.connect(self.add_item)
        self.ui.btn_remove.clicked.connect(self.remove_obj)
        self.ui.btn_clear.clicked.connect(self.clear_obj)
        self.ui.btn_sel_viewport.clicked.connect(self.select_in_viewport)
        self.ui.btn_update.clicked.connect(self.update_tree)
        self.ui.btn_print_position.clicked.connect(self.print_state_visibility)
        self.ui.btn_set_position.clicked.connect(self.set_state_position)
        self.attr_state.ui.combo_box_attributes.currentIndexChanged.connect(self.set_tree_item_state)
        self.attr_state.ui.combo_box_switch.currentIndexChanged.connect(self.set_tree_item_state)

    def set_icons(self):
        self.ui.btn_add.setIcon(QIcon(os.path.dirname(__file__) + '/icons/add.png'))
        self.ui.btn_remove.setIcon(QIcon(os.path.dirname(__file__) + '/icons/remove.png'))
        self.ui.btn_clear.setIcon(QIcon(os.path.dirname(__file__) + 'clear.png'))
        self.ui.btn_sel_viewport.setIcon(QIcon(os.path.dirname(__file__) + 'search.png'))
        self.ui.btn_update.setIcon(QIcon(os.path.dirname(__file__) + '/icons/update.png'))
        self.ui.btn_update.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_set_position.setIcon(QIcon(os.path.dirname(__file__) + '/icons/move.png'))
        self.ui.btn_set_position.setIconSize(QtCore.QSize(30, 30))

    def get_data(self):
        # ------------ #
        #  A Modifier  #
        # ------------ #
        if mc.objExists(self.rigadd + '.' + self.attr_info_name):
            if mc.getAttr(self.rigadd + '.' + self.attr_info_name):
                dict_pos_str = mc.getAttr(self.rigadd + '.' + self.attr_info_name)
                self.dict_position = switch_fonction.convert_unicode_to_dict(dict_pos_str)
        else:
            self.dict_position = {}

    def add_obj(self, obj):
        '''
           Add/refresh object in tree widget
                &
           Add save trs/rot/scl values in dict
                dict_pos = {
                    'switch_name':
                        {'transform_name':
                            {'state_1' :
                                {'translate': (float, float, float),
                                 'rotate': (float, float, float),
                                 'scale' : (float, float, float)
                                 },
                            'state_2':
                                 {'transform_name' :
                                    {'translate': (float, float, float),
                                    'rotate': (float, float, float),
                                    'scale' : (float, float, float)
                                 },
                             },
                        }
                    }
        '''

        if self.ui.list_obj.findItems(obj, Qt.MatchExactly|Qt.MatchRecursive, 0):
            item = self.ui.list_obj.findItems(obj, Qt.MatchExactly|Qt.MatchRecursive, 0)[0]
        else:
            self.list_obj.append(obj)

            item = QTreeWidgetItem()
            item.setText(0, obj)
            self.ui.list_obj.insertTopLevelItem(0, item)

        trs = mc.getAttr(obj + '.t')[0]
        l_round_trs = tuple(round_float_for_display(trs, 3))
        self.ui.list_obj.insertTopLevelItem(1, item.setText(1, str(l_round_trs)))

        rot = mc.getAttr(obj + '.r')[0]
        l_round_rot = tuple(round_float_for_display(rot, 3))
        self.ui.list_obj.insertTopLevelItem(1, item.setText(2, str(l_round_rot)))

        scl = mc.getAttr(obj + '.s')[0]
        l_round_scl = tuple(round_float_for_display(scl, 3))
        self.ui.list_obj.insertTopLevelItem(1, item.setText(3, str(l_round_scl)))

        ## stocker dans un dico
        transform_name = item.text(0)
        switch_name = self.attr_state.ui.combo_box_attributes.currentText()
        state = self.attr_state.ui.combo_box_switch.currentIndex()

        if switch_name in self.dict_position.keys():
            if not transform_name in self.dict_position[switch_name].keys():
                self.dict_position[switch_name][transform_name] = {}
            self.dict_position[switch_name][transform_name][state] = {'trs': trs, 'rot': rot, 'scl': scl}
        else:
            self.dict_position[switch_name] = {}
            self.dict_position[switch_name][transform_name] = {}
            self.dict_position[switch_name][transform_name][state] = {'trs' : trs, 'rot' : rot, 'scl' : scl}

        return item

    def set_state_position(self):
        '''
          For MAYA
          Create switch with driven key node(s) from dict information
        :return:
        '''
        state = str(self.attr_state.ui.combo_box_switch.currentIndex()) + '_' + self.attr_state.ui.combo_box_switch.currentText()
        state_index = float(self.attr_state.ui.combo_box_switch.currentIndex())
        attr_name = self.attr_state.ui.combo_box_attributes.currentText()
        for switch_name in self.dict_position.keys():
            for transform_name in self.dict_position[switch_name]:
                for state in self.dict_position[switch_name][transform_name]:
                    mc.setDrivenKeyframe(transform_name, attribute='tx', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['trs'][0])
                    mc.setDrivenKeyframe(transform_name, attribute='ty', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['trs'][1])
                    mc.setDrivenKeyframe(transform_name, attribute='tz', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['trs'][2])
                    mc.setDrivenKeyframe(transform_name, attribute='rx', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['rot'][0])
                    mc.setDrivenKeyframe(transform_name, attribute='ry', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['rot'][1])
                    mc.setDrivenKeyframe(transform_name, attribute='rz', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['rot'][2])
                    mc.setDrivenKeyframe(transform_name, attribute='sx', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['scl'][0])
                    mc.setDrivenKeyframe(transform_name, attribute='sy', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['scl'][1])
                    mc.setDrivenKeyframe(transform_name, attribute='sz', currentDriver=self.rigadd + '.' + switch_name,
                                         driverValue=state_index,
                                         value=self.dict_position[switch_name][transform_name][state]['scl'][2])

                for item in self.ui.list_obj.findItems(transform_name, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive):
                    item.setForeground(0, QBrush(Qt.cyan))
            if not attr_name in self.dict_position.keys():
                self.dict_position[attr_name] = {}
                for item in self.ui.list_obj.findItems('*', Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive):
                    self.dict_position[attr_name][item.text(0)] = {}
                    trs = mc.getAttr(item.text(0) + '.t')[0]
                    rot = mc.getAttr(item.text(0) + '.r')[0]
                    scl = mc.getAttr(item.text(0) + '.s')[0]
                    self.dict_position[attr_name][item.text(0)][state] = {'trs': trs, 'rot': rot, 'scl': scl}
                    item.setForeground(0, QBrush(Qt.cyan))
        if not mc.objExists(self.rigadd + '.' + self.attr_info_name):
            mc.addAttr(self.rigadd, longName=self.attr_info_name, dataType='string')
        mc.setAttr(self.rigadd + '.' + self.attr_info_name, json.dumps(self.dict_position), type='string')

    def set_tree_item_state(self):
        '''
          When state's switch change, set value already set on the tree widget
        dict_pos = {
            'attr_name':
                {'transform_name':
                    {'state_1' :
                        {'translate': (float, float, float),
                         'rotate': (float, float, float),
                         'scale' : (float, float, float)
                         },
                    'state_2':
                        {'translate': (float, float, float),
                        'rotate': (float, float, float),
                        'scale' : (float, float, float)
                         },
                     },
                }
            }
        '''
        self.get_data()
        attr = self.attr_state.ui.combo_box_attributes.currentText()
        state = str(self.attr_state.ui.combo_box_switch.currentIndex()) + '_' + self.attr_state.ui.combo_box_switch.currentText()

        if attr in self.dict_position.keys():
            for transform_name in self.dict_position[attr].keys():
                if state in self.dict_position[attr][transform_name].keys():
                    l_items = self.ui.list_obj.findItems(transform_name, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive) or []
                    if l_items:
                        item = l_items[0]
                    else:
                        item = self.add_obj(transform_name)

                    l_round_trs = tuple(round_float_for_display(self.dict_position[attr][transform_name][state]['trs'], 3))
                    item.setText(1, str(l_round_trs))
                    l_round_rot = tuple(round_float_for_display(self.dict_position[attr][transform_name][state]['rot'], 3))
                    item.setText(2, str(l_round_rot))
                    l_round_scl = tuple(round_float_for_display(self.dict_position[attr][transform_name][state]['scl'], 3))
                    item.setText(3, str(l_round_scl))
                    item.setForeground(0, QBrush(Qt.cyan))
                else:
                    for item in self.ui.list_obj.findItems('*', Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive):
                        item.setForeground(0, QBrush(Qt.white))
        else:
            self.ui.list_obj.clear()

    def remove_obj(self):
        '''
          Remove object from tree widget
        :return:
        '''
        for item in self.ui.list_obj.selectedItems():
            index = self.ui.list_obj.indexFromItem(item).row()
            self.ui.list_obj.takeTopLevelItem(index)
            self.list_obj.remove(item.text(0))

    def clear_obj(self):
        '''
          Clear tree widget
        :return:
        '''
        self.ui.list_obj.clear()
        self.list_obj = []

    def add_item(self):
        self.update_item(list = mc.ls(sl=True))

    def update_item(self, list):
        for obj in list:
            self.add_obj(obj)

    def update_tree(self):
        items = self.ui.list_obj.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
        for item in items:
            self.add_obj(item.text(0))

    def select_in_viewport(self):
        '''
        Fro MAYA
          Select current selection of tree widget in the viewport
        :return:
        '''
        l_items = self.ui.list_obj.selectedItems()
        l_obj = []
        for item in l_items:
            l_obj.append(item.text(0))
        mc.select(l_obj)

    def print_state_visibility(self):
        '''
          Print the dict info, for an easier and global visualisation of switch(es)
        :return:
        '''
        self.get_data()
        pprint(self.dict_position)

def round_float_for_display(l_real_value, decimal=3):
    '''
      For a simple display, return a round value with a given decimal
    :param l_real_value :type float
    :param decimal :type float
    :return:
    '''
    l_round_value = []
    for real_value in l_real_value:
        bow_float = round(real_value, decimal)
        l_round_value.append(bow_float)
    return l_round_value