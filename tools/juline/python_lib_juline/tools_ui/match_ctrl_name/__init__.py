# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os, ast
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QListWidgetItem

from ......library import lib_pipe
from ...library import attributesLib
from ...utils.maya_widget import MayaWidget, load_ui
import maya.cmds as mc


INFO_JSON = "INFO_JSON"
OLD_NAME_ATTR = "oldName"


class MatchCtrlNameWindow(MayaWidget):
    def __init__(self, parent=None):
        MayaWidget.__init__(self, name="Match ctrl name BG", parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'match_ctrl_name.ui'))
        self.main_layout.addWidget(self.ui)

        self.dic_ctrl_position = {}
        self.dic_geo_position = {}

        self.ui.btn_crt_dic_ctrl_pos.clicked.connect(self.create_dic_ctrl)
        self.ui.btn_crt_dic_geo_pos.clicked.connect(self.create_dic_geo)
        self.ui.btn_set_dic_ctrl.clicked.connect(self.set_dic_ctrl)
        self.ui.btn_set_dic_geo.clicked.connect(self.set_dic_geo)
        self.ui.btn_compare.clicked.connect(self.compare_dics)
        self.ui.btn_unic_old_name.clicked.connect(self.get_no_unic_old_name)
        self.ui.btn_store_match.clicked.connect(self.store_match)
        self.ui.btn_restore_match.clicked.connect(self.restore_match)

    def create_dic_ctrl(self):
        self.dic_ctrl_position = create_dic_ctrl_position()
        set_dic_info('dic_ctrl_pos', self.dic_ctrl_position)
        self.ui.line_dic_ctrl.clear()
        self.ui.line_dic_ctrl.setText(str(self.dic_ctrl_position))

    def create_dic_geo(self):
        self.dic_geo_position = create_dic_geo_position()
        set_dic_info('dic_geo_pos', self.dic_geo_position)
        self.ui.line_dic_geo.clear()
        self.ui.line_dic_geo.setText(str(self.dic_geo_position))

    def set_dic_ctrl(self):
        if mc.objExists(INFO_JSON + '.dic_ctrl_pos'):
            str_dic_ctrl = mc.getAttr(INFO_JSON + '.dic_ctrl_pos')
            self.ui.line_dic_ctrl.clear()
            self.ui.line_dic_ctrl.setText(str_dic_ctrl)
            self.dic_ctrl_position = ast.literal_eval(str_dic_ctrl)
        else:
            print "No dic ctrl pos exists"

    def set_dic_geo(self):
        if mc.objExists(INFO_JSON + '.dic_geo_pos'):
            str_dic_geo = mc.getAttr(INFO_JSON + '.dic_geo_pos')
            self.ui.line_dic_geo.clear()
            self.ui.line_dic_geo.setText(str_dic_geo)
            self.dic_geo_position = ast.literal_eval(str_dic_geo)
        else:
            print "No dic geo pos exists"

    def compare_dics(self):
        dic_multiple_match, ls_error_match, ls_match_find = compare_position(self.dic_geo_position, self.dic_ctrl_position)
        unique_value = list(set([str(x) for x in dic_multiple_match.values()]))

        # you can't have list as key in dict so >> convert dic_multiple_match, to a list of list
        # for simplify display on list widget multiple match
        # ex : [ [ [geo1, geo2], [ctrl1, ctrl2] ], [ [geo3, geo4], [ctrl3, ctrl4] ] ]
        ls_multiple_match = []
        for each in dic_multiple_match.values():
            if not each in unique_value:
                ls_multiple_match.append([[x for x in dic_multiple_match if dic_multiple_match[x] == each], each])

        print "\n\nMULTIPLE MATCH\n"
        print ls_multiple_match, dic_multiple_match
        self.ui.ls_manual.clear()

        for ls_match in ls_multiple_match:
            print ls_match[0], ls_match[1]
            item = QListWidgetItem()
            item.setText(str(ls_match[0]) + " // " + str(ls_match[1]))
            self.ui.ls_manual.addItem(item)

        print "\n\nWARNING : NOTHING MATCH WITH\n", str(ls_error_match)
        self.ui.ls_error.clear()
        for error in ls_error_match:
            item = QListWidgetItem()
            item.setText(error)
            self.ui.ls_error.addItem(item)

        print "\n\nGREAT : MATCH FIND & ATTR ADD on\n", str(ls_match_find)

    def get_no_unic_old_name(self):
        ls_old_name_node = attributesLib.filter_attr(attrTarget="oldName", extra=True)
        ls_old_name = []
        for node in ls_old_name_node:
            ls_old_name.append(mc.getAttr(node + '.oldName'))
        ls_multi = []
        # find multiple oldName set
        for old_name in ls_old_name:
            if ls_old_name.count(old_name) > 1:
                if old_name != None:
                    ls_multi.append(old_name)

        ls_multi = list(set(ls_multi))
        ls_geo_not_unique = []
        for ctrl_name in ls_multi:
            ls_same_old_name = [ctrl_name]
            ls_same_old_name.append(attributesLib.get_attr_state(attrTarget="oldName", stateTarget=ctrl_name))
            ls_geo_not_unique.append(ls_same_old_name)
        print "Same OldName Find"
        print ls_geo_not_unique

    def store_match(self):
        ls_oldName = attributesLib.filter_attr("oldName")
        dic_match = {}
        for geo in ls_oldName:
            dic_match[geo] = mc.getAttr(geo + '.oldName')

        if not mc.objExists(INFO_JSON + '.match'):
            mc.addAttr(INFO_JSON, longName='match', dataType='string')
        mc.setAttr(INFO_JSON + '.match', str(dic_match), type='string')

    def restore_match(self):
        str_dic = mc.getAttr(INFO_JSON + '.match')
        dic_match = ast.literal_eval(str_dic)
        for key_geo in dic_match.keys():
            if not mc.objExists(key_geo + '.' + OLD_NAME_ATTR):
                mc.addAttr(key_geo, longName=OLD_NAME_ATTR, dataType='string')
            old_name = dic_match[key_geo]
            if old_name:
                mc.setAttr(key_geo + '.' + OLD_NAME_ATTR, old_name, type='string')


def set_dic_info(attr_name, dic):
    if not mc.objExists(INFO_JSON):
        mc.createNode('transform', name=INFO_JSON)
        mc.select(INFO_JSON)
        lib_pipe.addDelMe()

    if not mc.objExists(INFO_JSON + '.' + attr_name):
        mc.addAttr(INFO_JSON, longName=attr_name, dataType='string')
    mc.setAttr(INFO_JSON + '.' + attr_name, str(dic), type='string')


def create_dic_position(my_list, loc_name='locPos'):
    '''
    Create dictionary with name and world position :
    {'Name' : [tx, ty, tz]}
    :param my_list: list object position to store
    :param loc_name: prefix name of the locator position created
    :return: dic_position
    '''
    dic_position = {}
    if mc.objExists("GRP_" + loc_name):
        mc.delete("GRP_" + loc_name)
    grp_loc = mc.createNode('transform', name="GRP_" + loc_name)
    for obj in my_list:
        loc = create_loc_position(obj, loc_name)
        if mc.objExists(obj + '.nodeType') and mc.getAttr(obj + '.nodeType') == 'control':
            position_x = round(mc.getAttr(loc + '.tx'), 3)
            position_y = round(mc.getAttr(loc + '.ty'), 3)
            position_z = round(mc.getAttr(loc + '.tz'), 3)
        if mc.objExists(obj + '.origPiv'):
            position_x = round(mc.getAttr(obj + '.origPivX'), 3)
            position_y = round(mc.getAttr(obj + '.origPivY'), 3)
            position_z = round(mc.getAttr(obj + '.origPivZ'), 3)

        dic_position[obj] = str([position_x, position_y, position_z])
        mc.parent(loc, grp_loc)
    return dic_position


def create_dic_geo_position():
    '''
    Create dict position for the transform with attr "rigMe" or "onlyVis" set True
    :return: dic_geo_position
    '''
    ls_rig_me = attributesLib.get_attr_state(attrTarget="rigMe", stateTarget=True)
    ls_only_vis = attributesLib.get_attr_state(attrTarget="onlyVis", stateTarget=True)
    ls_geo = ls_rig_me + ls_only_vis
    dic_geo_position = create_dic_position(ls_geo, loc_name='geoPos')
    return dic_geo_position


def create_dic_ctrl_position():
    '''
    Create dict position for the control list
    :return: dic_rig_me_position
    '''
    ls_ctrl = attributesLib.get_attr_state(attrTarget="nodeType", stateTarget="control")
    dic_ctrl_position = create_dic_position(ls_ctrl, loc_name='cPos')
    return dic_ctrl_position


def compare_position(dic_rig_me_position, dic_ctrl_position):
    '''
    :param dic_rig_me_position:
    :param dic_ctrl_position:
    :return: dic_multiple_match, ls_error_match : NEED USER MANUAL FIX
    '''
    ls_error_match = []
    dic_multiple_match = {}
    ls_match_find = []
    for key_geo in dic_rig_me_position.keys():
        ls_match = []
        for key_ctrl in dic_ctrl_position.keys():
            if dic_rig_me_position[key_geo] == dic_ctrl_position[key_ctrl]:
                ls_match.append(key_ctrl)
        if not mc.objExists(key_geo + '.' + OLD_NAME_ATTR):
            mc.addAttr(key_geo, longName=OLD_NAME_ATTR, dataType='string')

        if len(ls_match) == 1:
            # if just 1 match add attr with name ctrl as oldName
            if not mc.objExists(key_geo + '.' + OLD_NAME_ATTR):
                ls_match_find.append(key_geo)
                #mc.addAttr(key_geo, longName='OLD_NAME_ATTR', dataType='string')

            # compare new and old name set
            if not mc.getAttr(key_geo + '.' + OLD_NAME_ATTR) == ls_match[0]:
                print "on ", key_geo, OLD_NAME_ATTR, mc.getAttr(key_geo + '.' + OLD_NAME_ATTR), "override by", ls_match[0]
                mc.setAttr(key_geo + '.' + OLD_NAME_ATTR, ls_match[0], type='string')
        elif len(ls_match) > 1:
            # if multiple match, user need to fix them manually
            dic_multiple_match[key_geo] = ls_match
            #mc.addAttr(key_geo, longName='old_name', dataType='string')
        else:
            # if nothing match, user need to fix them manually
            ls_error_match.append(key_geo)

    return dic_multiple_match, ls_error_match, ls_match_find


def create_loc_position(target, prefix='locPos'):
    '''
    Create a snap locator for get de world position of the object
    and see it in the viewport for compare with mesh or other locator position
    :param target: the object position you want
    :param prefix: the prefix name of the locator
    :return: locator name
    '''
    loc = mc.createNode('locator', name=prefix + "_" + target + "Shape")
    loc_name = mc.listRelatives(loc, parent=True)
    loc_name = mc.rename(loc_name, prefix + "_" + target)
    const = mc.pointConstraint(target, loc_name, maintainOffset=False)
    mc.delete(const)
    return loc_name


def compare_string(ls_multiple_match):
    ls_match = []
    no_match = []
    for multiple_match in ls_multiple_match:
        ls_ctrl = multiple_match[1]
        ls_geo = multiple_match[0]
        for i in range(len(ls_ctrl)):
            for i2 in range(len(ls_geo)):
                if ls_ctrl[i][1:] in ls_geo[i2]:
                    #ls_ctrl.remove(ls_ctrl[i])
                    #ls_geo.remove(ls_geo[i2])
                    print "MATCH", ls_ctrl[i][1:], ls_geo[i2]
                    ls_match.append(ls_ctrl[i][1:])
                    ls_match.append(ls_geo[i2])
                else:
                    no_match.append(ls_ctrl[i])

    return no_match, ls_match



"""
dic_geo_position = create_dic_rig_me_position()
dic_ctrl_position = create_dic_ctrl_position()

dic_multiple_match, ls_error_match = compare_position(dic_geo_position, dic_ctrl_position)
print "\n\nYOU NEED TO MATCH MANUALLY\n", str(dic_multiple_match)
print "\n\nWARNING : NOTHING MATCH WITH\n", str(ls_error_match)
"""
