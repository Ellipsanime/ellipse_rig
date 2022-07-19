# coding: utf-8
# Author : Juline BRETON

from ...library import attributesLib
from ...utils import comment
from ...library import namesLib
from ......library import lib_controlGroup
from ......library import lib_pipe

import maya.cmds as mc

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = []
dic_check['NEED_FIX'] = []
dic_check['OK'] = None

# UTILS


def get_name_asset(step='STP', task='wip'):
    '''
    Author : Juline BRETON
    :param step: STP, MOD, SHD
    :type step: str
    :param task: wip, tpl, rig, trgt
    :type task: str
    :return: asset_name
    :rtype str
    '''
    sc_name = lib_pipe.getSceneName(lib_pipe.scenePath())
    asset_name = sc_name.split("SMF_" + step + "_")[-1].split('_' + task)[0]
    return asset_name


# EXPERT MODE
# Author : Juline BRETON
attr_expert_mode = 'expertMode'


def check_expert_mode():
    '''
    List all node with an attribute 'expertMode' : True
    :return: dict
    '''
    ls_expert_mode_on = attributesLib.get_attr_state(attrTarget=attr_expert_mode, stateTarget=True)
    if ls_expert_mode_on:
        dic_check['STATE'] = "NEED_FIX"
    else:
        dic_check['STATE'] = "OK"

    return dic_check


def fix_expert_mode():
    '''
    Set expertMode False
    '''
    ls_expert_mode_on = attributesLib.get_attr_state(attrTarget=attr_expert_mode, stateTarget=True)
    if ls_expert_mode_on:
        for obj in ls_expert_mode_on:
            mc.setAttr(obj + "." + attr_expert_mode, False)


# CG In CTRL
# Author : Juline BRETON & Pierre FABAREZ
def check_cg_in_ctrl():
    '''
    Check if ctrl have CG
    FIX :
    :return:
    '''
    ls_lonely_ctrl = get_lonely_ctrl()
    if ls_lonely_ctrl:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_lonely_ctrl
    else:
        dic_check['STATE'] = "OK"

    return dic_check


def fix_cg_in_ctrl(ls_problem=[]):
    '''
    if a cg_assetName exist :
        connect the lonely ctrl inside
    else :
        create cg_assetName parent to cg_all and add ctrl inside
    :return:
    '''
    if not ls_problem:
        dic_check = check_cg_in_ctrl()
        ls_problem = dic_check['STATE']

    lonely_ctrl_fix(ls_problem)


def ctrl_in_sets_check():
    '''
    Author : Pierre FABAREZ
    :return:
    '''
    ls_empty_trsf = []
    ls_ctrl_sets_content = []
    ls_cg = lib_controlGroup.getAllCg() or []
    # get current ctrl in ctrlSet
    for cg in ls_cg:
        ls_ctrl_set = mc.listConnections('%s.ctrlSet' % cg, source=True, destination=False)
        if ls_ctrl_set:
            ls_ctrl = mc.listConnections('%s.dagSetMembers' % ls_ctrl_set[0], source=True, destination=False) or []

            # get empty transform
            for ctrl in ls_ctrl:
                shp = mc.listRelatives(ctrl, children=True, shapes=True)
                if not shp:
                    ls_empty_trsf.append(ctrl)

                elif ctrl != 'WORLD':
                    ls_ctrl_sets_content.append(ctrl)
    ls_all_ctrl = mc.ls('c_*')
    ls_wrong_ctrl_set = list(set(ls_ctrl_sets_content) - set(ls_all_ctrl))
    ls_wrong_ctrl_set.extend(ls_empty_trsf)
    return ls_wrong_ctrl_set


def is_ctrl_set(set):
    '''
    Author : Pierre FABAREZ
    :param set: node set
    :type set: str
    :return:
    '''
    ls_cg = lib_controlGroup.getAllCg() or []
    if not mc.nodeType(set) == 'objectSet':
        return

    msg_connection = mc.connectionInfo('%s.message' % set, destinationFromSource=True) or []
    for msg in msg_connection:
        cg, cgAttr = msg.split('.')
        if cg in ls_cg and cgAttr == 'ctrlSet':
            return True


def ctr_in_sets_fix(ls_ctrl=[]):
    '''
    remove emptyCtrl from set
    :param ls_ctrl
    :type ls_ctrl: list
    '''
    for ctrl in ls_ctrl:
        ls_ctrl_set = mc.listSets(object=ctrl) or []
        for ctrl_set in ls_ctrl_set:
            if is_ctrl_set(ctrl_set):
                mc.sets(ctrl, remove=ctrl_set)


def get_lonely_ctrl(): #### MODIFTY >> SEARCH MASTER CG_ALL FIRST
    '''
    Author : Juline BRETON
    Get All CTRL
    Get ALL CG : network Node
    LONELY CTRL = ALL CTRL - CTRL connect to a CG
    :return: list of the ctrl not connected to a controlGroup
    :rtype list
    '''
    ls_all_ctrl = mc.ls('c_*', type='joint') + mc.ls('*:c_*', type='joint') + mc.ls('c_*', type='transform') + \
                  mc.ls('*:c_*', type='transform')
    ls_all_cg = lib_controlGroup.getAllCg() or []
    ls_ctrl_in_cg = []
    for cg in ls_all_cg:
        ls_ctrl_in_cg.extend(mc.listConnections(cg + ".members") or [])
    ls_lonely_ctrl = list(set(ls_all_ctrl) - set(ls_ctrl_in_cg))
    ls_lonely_ctrl.sort()
    return ls_lonely_ctrl


def lonely_ctrl_fix(ls_ctrl):
    '''
    Author : Juline BRETON
    :param ls_ctrl: list ctrl with no CG to fix
    :type ls_ctrl: list
    '''
    asset_name = namesLib.lower_case_to_camelCase(get_name_asset())
    cg_asset = 'cg_{0}'.format(asset_name)
    if not mc.objExists(cg_asset):
        print "Creating ", cg_asset
        cg_asset = lib_controlGroup.crtCg(asset_name)
    lib_controlGroup.addCtrlToCg(ls_ctrl, cg_asset)

    # Find cg_all
    ls_all_cg = lib_controlGroup.getAllCg() or []
    ls_cg_all = []
    for cg in ls_all_cg:
        if "cg_all" in cg:
            ls_cg_all.append(cg)
    # If just 1 cg_all in scene parent
    if ls_cg_all:
        if len(ls_cg_all) == 1:
            lib_controlGroup.parentCg(cg_asset, ls_cg_all[0])
    # If multiple cg_all, in CHAR or asset with EXP
    else:
        comment.format_comment("Multiple cg_all in scene, \nplease parent manually\n"
                               "SOON : a popup windows for select the TOP cg_all", center=True)


# CG HIERARCHY

def check_cg_hierarchy():
    '''
    Author : Juline BRETON
    :return:
    '''
    ls_cg = lib_controlGroup.getAllCg() or []
    cg_all = find_master_all()
    print cg_all, type(cg_all)
    ls_orphan_cg = cgHierarchie_check(cgs=ls_cg)

    if not cg_all:
        print "if not cg_all"
        dic_check['STATE'] = "ERROR"
        dic_check['ERROR'] = ["WARNING : NO CG ALL"]
    elif type(cg_all) is str or unicode:
        print "str or unicode"
        if ls_orphan_cg:
            dic_check['STATE'] = "NEED_FIX"
            dic_check['NEED_FIX'] = ls_orphan_cg
        else:
            dic_check['STATE'] = "OK"
    elif type(cg_all) is list:
        print "LIST"
        dic_check['STATE'] = "ERROR"
        dic_check['ERROR'] = ["WARNING : MULTIPLE CG ALL, choose one"] + cg_all
        print dic_check['ERROR']

    return dic_check


def fix_cg_hierarchy(ls_problem=[]):
    '''
    Author : Juline BRETON
    :param cgs:
    :return:
    '''
    for cg in ls_problem:
        lib_controlGroup.parentCg(cg, CG_ALL) #### FIND cg_all


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

def cg_all_exist(cgs=[], *args):
    '''
    Author : Pierre FABAREZ
    :param cgs:
    :param args:
    :return:
    '''
    # Check CgAll
    if CG_ALL not in cgs or mc.listConnections('%s.parent' % CG_ALL):
        return False
    else:
        return True

def cgHierarchie_check(cgs=[], *args):
    '''
    Author : Pierre FABAREZ
    :param cgs:
    :param args:
    :return:
    '''
    orphanCg = []

    # Check allCg Parent
    for cg in cgs:
        cgHi = [cg]
        if not cg in orphanCg:
            cgParent = mc.listConnections('%s.parent' % cg)

            while cgParent:
                cgHi.append(cgParent[0])
                cgParent = mc.listConnections('%s.parent' % cgParent[0])

        if cgHi[-1] != CG_ALL:
            orphanCg.extend(cgHi)

    return orphanCg


TOP_NODE = "ALL"
CG_ALL = "cg_all"
attr_master_all = "MASTER_ALL"
attr_master_cg_all = "MASTER_CG_ALL"


def find_cg_all(ls_all=[]):
    '''
    Author : Juline BRETON
    :return:
    '''
    if len(ls_all) == 1:
        cg_all = ls_all[0]
        return cg_all
    elif len(ls_all) > 1:
        comment.format_comment("Multiple cg_all in scene, \n" + str(ls_all) +
                               "\nplease parent manually or add a MASTER_ALL attr\n"
                               "SOON : a popup windows for select the TOP cg_all", center=True)
        # return cg_all
        return ls_all
    else:
        print "NO CG ALL"
        return None


def find_master_all():
    ls_master_all_attr = attributesLib.get_attr_state('MASTER_CG_ALL', True) or []
    master_all = find_cg_all(ls_master_all_attr)
    if not master_all:
        ls_all_cg = lib_controlGroup.getAllCg() or []
        ls_cg_all = []
        for cg in ls_all_cg:
            if CG_ALL in cg:
                ls_cg_all.append(cg)
        master_all = find_cg_all(ls_cg_all)

    return master_all



def add_attr_master_all(node=None):
    '''
    Author : Juline BRETON
    Add attribute on First selection
    :param node:
    :return:
    '''
    if not node:
        node = mc.ls(sl=True)[0]
        if not node:
            comment.format_comment("Please select something")

    if TOP_NODE not in node:
        comment.format_comment("""Please select a group named "ALL" """)

    else:
        if not mc.objExists(node + '.' + attr_master_all):
            mc.addAttr(node, longName=attr_master_all, attributeType='bool', keyable=False, defaultValue=True)
        else:
            mc.setAttr(node + '.' + attr_master_all, True)

def add_attr_master_cg_all(node=None):
    '''
    Author : Juline BRETON
    Add attribute on First selection
    :param node:
    :return:
    '''
    if not node:
        node = mc.ls(sl=True)[0]
        if not node:
            comment.format_comment("Please select a cg")

    if CG_ALL not in node:
        comment.format_comment(""" Please select a control group named "cg_all" """)

    else:
        if not mc.objExists(node + '.' + attr_master_cg_all):
            mc.lockNode(node, lock=False)
            mc.addAttr(node, longName=attr_master_cg_all, attributeType='bool', keyable=False, defaultValue=True)
            mc.lockNode(node, lock=True)
        else:
            mc.setAttr(node + '.' + attr_master_cg_all, True)

# BASE HIERARCHY

def check_base_hierarchy():
    print "check HI"

def fix_base_hierarchy():
    print "fix HI"
