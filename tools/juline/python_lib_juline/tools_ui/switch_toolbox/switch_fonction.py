# coding: utf-8
# Copyright (c) 2018 Ubisoft Juline BRETON

__author__ = "Juline BRETON"

import os
import json

import maya.cmds as mc
from ump.common import emon_file, emon_asset
import emon_api as eapi
from llc.pipeline.defines import LLCNodeName
import name_lib


def find_rigadd():
    '''
      Find all rigAdd of a scene
    :return:
    '''
    for obj in mc.ls(sl=0, type='transform'):
        if obj.endswith('c_rigAdd'):
            return obj
        else:
            return ''

def get_enum_list(obj, attr):
    '''
      Get the list of enum of an enum attribute
    :param obj :type string
    :param attr :type string
    :return: :type list of string
    '''
    if mc.attributeQuery(attr, node=obj, listEnum=True):
        str_enum = mc.attributeQuery(attr, node=obj, listEnum=True)[0] or []
    else:
        str_enum = []
    l_enum = []
    for i in range(str_enum.count(':')):
        if ':' in str_enum:
            enum = str_enum.split(':')[0]
            l_enum.append(enum)
            str_enum = str_enum[len(str_enum.split(':')[0]) + 1:]
            if not ':' in str_enum:
                l_enum.append(str_enum)
    return l_enum

def convert_unicode_to_dict(unicode):
    '''
      Convert type unicode to dict
    :param unicode:
    :return:
    '''
    dico = {}
    if unicode != '{}':
        dico = json.loads(unicode) or {}
    return dico

def find_ctrl_switch(step=''):
    '''
      Find CTRL switch and prefix from a step
    :param step :type string
    :return: string, string
    '''
    if not step:
        step = get_step()
    if step == 'surfacing':
        print "utiliser l'outil de switch du texturing"
        return LLCNodeName.SHD_CTRL, 'tex_'
    if step == 'modeling':
        return LLCNodeName.MOD_CTRL, 'mod_'
    if step == 'setup':
        return LLCNodeName.SETUP_CTRL_RIG_ADD, 'ubi_'
    else:
        return '', ''

def get_step():
    step = emon_file.get_step(mc.file(query=True, sceneName=True))
    return step

def get_asset_name():
    asset_file = emon_file.get_asset(mc.file(query=True, sceneName=True))
    print 'asset_file', asset_file
    if asset_file:
        asset_name = asset_file.name()
        return asset_name
    else:
        return 'NO ASSET'

def get_gattace_link():
    asset_name = get_asset_name()
    ast = eapi.Asset.get(asset_name)
    gattaca_link = emon_asset.get_gattaca_link(ast)
    return gattaca_link

def find_ctrl_from_attr_prefix(attr_name):
    # SEARCH NAMESPACE
    NS = None
    if ':' in attr_name:
        NS = attr_name.split(':')[0]
        attr_name = attr_name.split(':')[1]
    # FIND STEP FROM PREFIX
    ctrl = ''
    if attr_name.startswith('mod_'):
        ctrl = name_lib.SwitchName.MOD_CTRL
    if attr_name.startswith('tex_'):
        ctrl = name_lib.SwitchName.SHD_CTRL
    if attr_name.startswith('ubi_'):
        ctrl = name_lib.SwitchName.ANI_CTRL
    print 'CTRL', ctrl
    # RETURN NAME
    if NS:
        return NS + ':' + ctrl
    else:
        print 'ici', attr_name, ctrl
        return ctrl

def find_index_from_enum_text(ctrl_name, attr_name, state_text):
    if mc.objExists(ctrl_name + '.' + attr_name):
        str_enum = mc.attributeQuery(attr_name, node=ctrl_name, listEnum=True)[0]
        for i in range(str_enum.count(':')+1):
            if str_enum.split(':')[i] == state_text:
                return i
    else:
        print ctrl_name + '.' + attr_name + ' does not exist'

def deleting_switch(step, attr):
    if step == 'modeling':
        ctrl = name_lib.SwitchName.MOD_CTRL
        # delete driven key
        l_output = mc.listConnections(ctrl + '.' + attr, source=True) or []
        mc.delete(l_output)

        # Analyse dict for set obj driven.visibility to 1
        dict_mod =json.loads(mc.getAttr(name_lib.SwitchName.MOD_DICT_LONG))
        for state in dict_mod[attr].keys():
            for obj in dict_mod[attr][state].keys():
                print 'obj', obj
                mc.setAttr(obj + '.v', 1)
                for shape in mc.listRelatives(obj, shapes=True) or []:
                    mc.setAttr(shape + '.v', 1)
        mc.setAttr(name_lib.SwitchName.MOD_DICT_LONG, '', type='string')

    if step == 'surfacing':
        ctrl = name_lib.SwitchName.SHD_CTRL
    if step == 'setup':
        ctrl = name_lib.SwitchName.ANI_CTRL

def optimise_node_switch():
    '''
        Delete the driven key nodes connected in shape
             &
        Mutalised nodes
    '''
    # for visibility switches
    l_driven_key = mc.listConnections(name_lib.SwitchName.MOD_CTRL, source=True, type='animCurveUU') or []
    # Find driven key node connected in shapes, delete him and set the shape visibility to 1
    print l_driven_key
    for dvk in l_driven_key:
        l_mesh = mc.listConnections(dvk + '.output', source=True, shapes=True, type='mesh') or []
        l_curves = mc.listConnections(dvk + '.output', source=True, shapes=True, type='nurbsCurve') or []
        if l_mesh or l_curves:
            mc.delete(dvk)
            for mesh in l_mesh:
                mc.setAttr(mesh + '.v', 1)
            for curve in l_curves:
                mc.setAttr(curve + '.v', 1)
