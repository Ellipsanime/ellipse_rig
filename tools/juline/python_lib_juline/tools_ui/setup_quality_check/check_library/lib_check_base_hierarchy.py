# coding: utf-8
# AUTHOR : Juline BRETON

from ....utils import comment
from ....library import attributesLib

import maya.cmds as mc

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = ""
dic_check['NEED_FIX'] = []
dic_check['OK'] = None

# FROM MOD
TOP_NODE = "ALL"
ATTR_MASTER_ALL = "MASTER_ALL"

GRP_GEO = 'GEO'
GRP_LOC = 'LOC'
GRP_FUR = 'FUR'
GRP_SHP = 'SHP'
GRP_SWC = 'SWITCHS'
# FROM RIG
GRP_RIG = 'RIG'
WORLD = 'WORLD'

TOP_NODE_CHILD = [GRP_GEO, GRP_LOC, GRP_FUR, GRP_SHP, GRP_RIG, WORLD, GRP_SWC]

# GRP_GEO = lib_glossary.lexicon("geo")
# GRP_SWC = lib_glossary.lexicon("switchs")
# TOP_NODE_CHILD = ['GEO', 'LOC', 'FUR', 'SHP', 'SWITCHS', 'RIG', 'WORLD']


def check_base_hierarchy():
    """
    Check the Base Hierarchy
    ALL
      > GEO
      > LOC
      > FUR
      > SHP
      > SWITCHS
      > RIG
      > WORLD

    Returns
    -------
    Dict
        dic_check['STATE'] = enum_string : ERROR, NEED_FIX or OK : The status of the check
        dic_check['ERROR'] = string : printed if ERROR
        dic_check['NEED_FIX'] = list : of the problems to fix
        dic_check['OK'] = None
    """
    top_node = get_master_all()

    if not top_node:
        nb_ref, ls_ref_node = get_ref_count()
        if nb_ref == 0:
            dic_check['STATE'] = "ERROR"
            dic_check['ERROR'] = [""""No TOP NODE "ALL" find"""]

        if ls_ref_node:
            ls_all_grp = []
            ls_ref_residuel = []
            # Get NameSpace of Ref
            for ref_node in ls_ref_node:
                try:
                    file = mc.referenceQuery(ref_node, filename=True) or None
                    if file:
                        name_space = mc.referenceQuery(ref_node, namespace=True) or None
                        if mc.objExists(name_space + ":" + TOP_NODE):
                            ls_all_grp.append(name_space + ":" + TOP_NODE)
                except:
                    ls_ref_residuel.append(ref_node)
                    continue
            if mc.objExists(TOP_NODE):
                ls_all_grp.append(TOP_NODE)
            dic_check['STATE'] = "ERROR"
            dic_check['ERROR'] = ["Please set a MASTER ALL"] + ls_all_grp + ["", "REF TO CLEAN"] + ls_ref_residuel
        return dic_check

    ls_wrong_hi = check_top_node_child()
    if ls_wrong_hi:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_wrong_hi
    else:
        dic_check['STATE'] = "OK"

    return dic_check


def get_ref_count():
    """
    Get reference info : how many and their reference Node
    Returns
    -------
    integer , list
        nb of reference, ls ref node
    """
    ls_ref_node = mc.ls(sl=False, type='reference') or []
    return len(ls_ref_node), ls_ref_node


def get_master_all():
    """
    Author :
        Juline BRETON
    Check if attr master_top_node exist
    else check nb ref
    Returns
    -------
    string or None
        master top node or None
    """
    nb_ref, ls_ref_node = get_ref_count()
    if nb_ref == 0:
        if mc.objExists(TOP_NODE):
            return TOP_NODE
        else:
            print "NO TOP NODE FIND"
            return None
    elif nb_ref == 1:
        # check if ref have group ALL
        name_space = mc.referenceQuery(ls_ref_node[0], namespace=True)
        if mc.objExists(name_space + ':' + TOP_NODE):
            master_top_node = name_space + ':' + TOP_NODE
            add_attr_master_all(master_top_node)
            return master_top_node
    else:
        ls_attr_master_all = attributesLib.get_attr_state(ATTR_MASTER_ALL, True)
        if len(ls_attr_master_all) == 1:
            master_top_node = ls_attr_master_all[0]
            return master_top_node
        else:
            print "Add pop up windows for select the MASTER REF\n" \
                  "For the moment : You can add a master all attribute on the group all you want as the master all"
            return None


def add_attr_master_all(node=None):
    """
    Add an attr : "MASTER_ALL" for identify the top node
    Parameters
    ----------
    node : maya transform
        the transform to add the attribute
    """
    if not node:
        node = mc.ls(sl=True)[0]

    if TOP_NODE not in node:
        comment.format_comment("""Please select a group named "ALL" """)

    else:
        if not mc.objExists(node + '.' + ATTR_MASTER_ALL):
            mc.addAttr(node, longName=ATTR_MASTER_ALL, attributeType='bool', keyable=False, defaultValue=True)
        else:
            mc.setAttr(node + '.' + ATTR_MASTER_ALL, True)


def check_top_node_child():
    """
    Check if just member of list TOP_NODE_CHILD is child of the TOP NODE
    Returns
    -------
    list
        of wrong transform child of the TOP NODE
    """
    top_node = get_master_all()
    if top_node:
        ls_children = mc.listRelatives(top_node, children=True) or []
        ls_wrong_child = []
        for child in ls_children:
            #if child.split(':')[-1] not in TOP_NODE_CHILD:
            if not child.endswith(tuple(TOP_NODE_CHILD)):
                ls_wrong_child.append(child)
        return ls_wrong_child


