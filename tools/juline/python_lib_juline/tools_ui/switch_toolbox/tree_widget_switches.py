# coding: utf-8
# Copyright (c) 2018 Ubisoft Juline BRETON

__author__ = "Juline BRETON"

import json
import maya.cmds as mc
from pprint import pprint

import os, sys
pathTeamShare = r'C:\\STUFF\foundation_rig'
if not pathTeamShare in sys.path:
    sys.path.append(pathTeamShare)
from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QBrush, QDoubleValidator
from PySide2.QtWidgets import QTreeWidgetItem, QComboBox, QLineEdit, QAbstractItemView, QStyledItemDelegate

import switch_fonction, attribute_state, name_lib

reload(switch_fonction)
reload(attribute_state)
reload(name_lib)

class QTreeWidgetSwitches(MayaWidget):

    def __init__(self, parent=None):
        MayaWidget.__init__(self, "Tree Widget texture", parent=parent)
        self.setWindowTitle('Tree Widget texture')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ui/tree_widget_switch.ui'))

        self.main_layout.addWidget(self.ui)

        self.set_icons()
        # ------------------------------------------- VARIABLES ------------------------------------------- #
        self.rigadd = switch_fonction.find_rigadd()
        self.ctrl_switch, self.prefix_attr = switch_fonction.find_ctrl_switch()
        self.attr_info_name = name_lib.SwitchName.ALL_DICT
        self.name_switch_ctrl = name_lib.SwitchName.ALL_SWITCH_CTRL
        self.long_name = False

        self.dict_switch = {}
        self.prefixes_supported = name_lib.SwitchName.ALL_SWITCH_PREFIX

        # ------------------------------------------ EXTERNAL UI ------------------------------------------ #
        self.attr_state = attribute_state.AttributeState()
        # ------------------------------------------- SETUP UI -------------------------------------------- #
        self.ui.layout_attribute_state.addWidget(self.attr_state)

        # ---------------------------------------- START FONCTIONS ---------------------------------------- #
        self.load_switch_ctrl()
        self.get_data()

        # ------------------------------------------ USER ACTIONS ----------------------------------------- #
        self.ui.btn_set_state.clicked.connect(self.set_state)
        self.ui.btn_print_state_switch.clicked.connect(self.print_state_switch)
        self.attr_state.ui.combo_box_step.currentIndexChanged.connect(self.load_switch_ctrl)

    def set_icons(self):
        self.ui.btn_set_state.setIcon(QIcon(os.path.dirname(__file__) + '/icons/connection.png'))

    def load_switch_ctrl(self):
        '''
          Load switch controllers of the scene not set in the attribute state UI
        :return:
        '''
        self.ui.tree_switches.clear()
        self.ctrl_switch, self.prefix_attr = switch_fonction.find_ctrl_switch(self.attr_state.ui.combo_box_step.currentText())

        self.ui.tree_switches.setItemDelegateForColumn(1, ItemDelegateTexture(self.ui.tree_switches))
        self.ui.tree_switches.setEditTriggers(QAbstractItemView.AllEditTriggers)

        for scene_obj in mc.ls(sl=0, type='transform', long=self.long_name):
            if scene_obj.endswith(self.name_switch_ctrl):
                if scene_obj != self.ctrl_switch:
                    item = QTreeWidgetItem()
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    item.setCheckState(0, Qt.Checked)
                    item.setText(0, scene_obj)
                    self.ui.tree_switches.insertTopLevelItem(0, item)
                    all_extra_attr = mc.listAttr(scene_obj, userDefined=True) or []
                    l_extra_attr = []
                    for extra_attr in all_extra_attr:
                        if extra_attr != 'ubi_pipe_prim_path':
                            if extra_attr.startswith(self.prefixes_supported):
                                l_extra_attr.append(extra_attr)

                    if l_extra_attr:
                        for x in range(len(l_extra_attr)):
                            item_child = QTreeWidgetItem()
                            item_child.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                            item_child.setCheckState(0, Qt.Checked)
                            item_child.setText(0, l_extra_attr[x])
                            item.insertChild(0, item_child)

                            if mc.attributeQuery(l_extra_attr[x], node=scene_obj, enum=True):
                                l_enum = switch_fonction.get_enum_list(scene_obj, l_extra_attr[x])
                                if l_enum:
                                    comboBox = QComboBox(self.ui.tree_switches)
                                    comboBox.addItems(l_enum)
                                    comboBox.setCurrentIndex(0)
                                    self.ui.tree_switches.setItemWidget(item_child, 1, comboBox)

                            else:
                                float_value = mc.getAttr(scene_obj + '.' + l_extra_attr[x])
                                item_child.setText(1, str(float_value))
        self.ui.tree_switches.expandAll()

    def set_state(self):
        '''
          Create switch with driven key node(s)
        dict_tex = {
            'attribute_name':
                {'state_1':
                    {'SHD_name':
                        {'attr_name' : 'enumText',
                        'attr_name': 'enumText'
                     },
                'state_2':
                     {'SHD_name': 'enumText',
                     'SHD_name': 'enumText'
                     }
                }
            }
        '''
        step = self.attr_state.ui.combo_box_step.currentText()
        attr_driver_name = self.attr_state.ui.combo_box_attributes.currentText()
        state_index = str(self.attr_state.ui.combo_box_switch.currentIndex())
        state_text = str(self.attr_state.ui.combo_box_switch.currentText())
        state_driver = state_index + '_' + state_text

        l_items_mod = self.ui.tree_switches.findItems("*" + name_lib.SwitchName.MOD_CTRL, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
        l_items_shd = self.ui.tree_switches.findItems("*" + name_lib.SwitchName.SHD_CTRL, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
        l_items_ani = self.ui.tree_switches.findItems("*" + name_lib.SwitchName.ANI_CTRL, Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)

        l_items = l_items_mod + l_items_shd + l_items_ani

        self.ctrl_switch, self.prefix_attr = switch_fonction.find_ctrl_switch(step)

        if not attr_driver_name in self.dict_switch.keys():
            self.dict_switch[attr_driver_name] = {}
        if not state_driver in self.dict_switch[attr_driver_name].keys():
            self.dict_switch[attr_driver_name][state_driver] = {}
        for item in l_items:
            if item.checkState(0):
                item.setForeground(0, QBrush(Qt.cyan))
                if not item.text(1) in self.dict_switch[attr_driver_name][state_driver].keys():
                    self.dict_switch[attr_driver_name][state_driver][item.text(0)] = {}
                for i in range(item.childCount()):
                    if item.child(i).checkState(0):
                        if item.child(i).text(1):
                            self.dict_switch[attr_driver_name][state_driver][item.text(0)][item.child(i).text(0)] = item.child(i).text(1)
                        else:
                            index = self.ui.tree_switches.itemWidget(item.child(i), 1).currentIndex()
                            text = self.ui.tree_switches.itemWidget(item.child(i), 1).currentText()
                            self.dict_switch[attr_driver_name][state_driver][item.text(0)][item.child(i).text(0)] = text
                            self.create_switch(self.ctrl_switch, attr_driver_name, state_driver, item.text(0), item.child(i).text(0), text)
                        item.child(i).setForeground(0, QBrush(Qt.cyan))
                    else:
                        item.child(i).setForeground(0, QBrush(Qt.white))

            else:
                item.setForeground(0, QBrush(Qt.white))
                for i in range(item.childCount()):
                    item.child(i).setForeground(0, QBrush(Qt.white))
                    if item.text(0) in self.dict_switch[attr_driver_name][state_driver].keys():
                        del self.dict_switch[attr_driver_name][state_driver][item.text(0)]

        if any([mc.objExists(self.ctrl_switch + '.' + attr) for attr in self.attr_info_name]):
            mc.setAttr(self.ctrl_switch + '.' + attr, json.dumps(self.dict_switch), type='string')
        else:
            print "ATTR DICT INFO DOESN'T EXIST"

    def get_data(self):
        '''
          Get dict information of current switch in attribute state UI
        :return:
        '''
        for attr in self.attr_info_name:
            if mc.objExists(self.ctrl_switch + '.' + attr):
                if mc.getAttr(self.ctrl_switch + '.' + attr):
                    dict_tex_str = mc.getAttr(self.ctrl_switch + '.' + attr)
                    self.dict_switch = switch_fonction.convert_unicode_to_dict(dict_tex_str)
            else:
                self.dict_switch = {}

    def create_switch_dico(self, ctrl_driver, attr_master_name, state_master, ctrl_driven, attribute_driven, state_driven):
        '''
          Create dict info
        :param ctrl_driver :type string
        :param attr_master_name :type string
        :param state_master :type string
        :param ctrl_driven :type string
        :param attribute_driven :type string
        :param state_driven :type string
        :return:
        '''
        for attr_master_name in self.dict_switch.keys():
            for state_master in self.dict_switch[attr_master_name]:
                state_master_index = int(state_master.split('_')[0])
                for attribute_driven in self.dict_switch[attr_master_name][state_master][ctrl_driven].keys():
                    print "ctrl_driven, attribute_driven, state_driven", ctrl_driven, attribute_driven, state_driven
                    state_driven_index = switch_fonction.find_index_from_enum_text(ctrl_driven, attribute_driven,
                                                                                   state_driven)
                    print 'state_master_index', state_master_index
                    mc.setDrivenKeyframe(ctrl_driven, attribute=attribute_driven, currentDriver=ctrl_driver + '.' + attr_master_name,
                                         driverValue=state_master_index, value=state_driven_index)

    def create_switch(self, ctrl_driver, attr_master_name, state_master, ctrl_driven, attribute_driven, state_driven):
        '''
          Create switch with driven key node(s)
        :param ctrl_driver:
        :param attr_master_name:
        :param state_master:
        :param ctrl_driven:
        :param attribute_driven:
        :param state_driven:
        :return:
        '''
        state_master_index = int(state_master.split('_')[0])
        state_driven_index = switch_fonction.find_index_from_enum_text(ctrl_driven, attribute_driven, state_driven)
        mc.setDrivenKeyframe(ctrl_driven, attribute=attribute_driven, currentDriver=ctrl_driver + '.' + attr_master_name,
                             driverValue=state_master_index, value=state_driven_index)

    def print_state_switch(self):
        self.get_data()
        pprint(self.dict_switch)

class ItemDelegateTexture(QStyledItemDelegate):

    def __init__(self, parent):
        super(ItemDelegateTexture, self).__init__(parent)
        self.tree = parent

    def createEditor(self, parent, option, index):
        attr_type, node_name, attr_name_item = self.get_attribute_type()
        if attr_type:
            editor = QComboBox(parent)
            enums = switch_fonction.get_enum_list(node_name, attr_name_item.text(0))
            editor.addItems(enums)
        else:
            editor = QLineEdit(parent)
            editor.setValidator(QDoubleValidator())
        return editor

    def setEditorData(self, editor, index):
        attr_type, node_name, attr_name_item = self.get_attribute_type()
        if attr_type:
            value = index.model().data(index, Qt.DisplayRole)
            index_enum = editor.findText(value)
            if index_enum != -1:
                editor.setCurrentIndex(index_enum)
            editor.showPopup() # save one click, yeah!

    def setModelData(self, editor, model, index):
        attr_type, node_name, attr_name_item = self.get_attribute_type()
        if attr_type:
            value = editor.currentText()
        else:
            value = editor.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def get_attribute_type(self):
        """
        :return:
        attr_name_item : QTreeWidgetItem of the attribute
        node_name : string : ctrl name
        attr_type : Bool : True if Enum / False if float
        """
        attr_name_item = self.tree.currentItem()
        node_name = attr_name_item.parent().text(0)
        attr_type = mc.attributeQuery(attr_name_item.text(0), node=node_name, enum=True)
        return attr_type, node_name, attr_name_item