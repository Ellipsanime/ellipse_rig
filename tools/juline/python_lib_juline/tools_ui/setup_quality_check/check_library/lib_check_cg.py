# coding: utf-8
# AUTHOR : Juline BRETON

from .......library import lib_reference, lib_controlGroup

from ....utils import comment
from ....library import attributesLib
reload(attributesLib)

import maya.cmds as mc

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = ""
dic_check['NEED_FIX'] = []
dic_check['OK'] = None

CG_ALL = 'cg_all'
ATTR_MASTER_CG = 'MASTER_CG'


def check_cg_hierarchy_prp_chr():
    # error if no CG_ALL and if multiple
    [nb_master_cg, master_cg] = get_master_cg()
    dic_check = {}
    if nb_master_cg == 0:
        dic_check['STATE'] = "ERROR"
        dic_check['ERROR'] = ["NO CG ALL FIND"]
        return dic_check

    elif nb_master_cg > 1:
        dic_check['STATE'] = "ERROR"
        dic_check['ERROR'] = ["__________ Please Set a MASTER CG __________"] + master_cg
        print "Add pop up windows for select the MASTER cg_all\n" \
              "For the moment : You can add a master cg all attribute on the cg you want as the master"
        return dic_check

    else:
        dic_check = check_cg_hierarchy(cg_all=master_cg)
        return dic_check

    return dic_check


def check_cg_hierarchy(cg_all='cg_all'):
    '''
    Author : Juline BRETON
    :return:
    '''
    ls_cg = lib_controlGroup.getAllCg() or []
    ls_orphan_cg = cgHierarchie_check(cgs=ls_cg, cg_all=cg_all)

    if ls_orphan_cg:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_orphan_cg
    else:
        dic_check['STATE'] = "OK"

    return dic_check

def fix_cg_hierarchy(ls_problem=[]):
    '''
    Author : Juline BRETON
    :return:
    '''
    if not ls_problem:
        dic_check = check_cg_hierarchy_prp_chr()
        ls_problem = dic_check['NEED_FIX']
    [nb_master_cg, master_cg] = get_master_cg()
    for cg in ls_problem:
        lib_controlGroup.parentCg(cg, master_cg)


def get_master_cg():
    '''
    Author : Juline BRETON
    check if attr master_cg exist
    else check nb ref
    :return: [ng cg_all, list cg_all]
    '''
    nb_ref, ls_ref_node = lib_reference.get_ref_count()
    if nb_ref == 0:
        if mc.objExists(CG_ALL):
            return [1, CG_ALL]
        else:
            return [0, None]
    else:
        ls_attr_cg_master = attributesLib.get_attr_state(ATTR_MASTER_CG, True, typ='network')
        print "ls_attr_cg_master", ls_attr_cg_master
        if len(ls_attr_cg_master) == 1:
            master_cg = ls_attr_cg_master[0]
            return [1, master_cg]
        elif len(ls_attr_cg_master) > 1:
            print "Add pop up windows for select the MASTER cg_all\n" \
                  "For the moment : You can add a master cg all attribute on the cg you want as the master"
            return [len(ls_attr_cg_master), ls_attr_cg_master]
        elif not ls_attr_cg_master:
            ls_cg = lib_controlGroup.getAllCg() or []
            ls_cg_all = []
            for cg in ls_cg:
                if cg.endswith(CG_ALL):
                    ls_cg_all.append(cg)
            if len(ls_cg_all) == 1:
                return [1, ls_cg_all[0]]
            elif len(ls_cg_all) > 1:
                return [len(ls_cg_all), ls_cg_all]
            else:
                return [0, None]
        else:
            return [0, None]

def add_attr_master_cg(node=None):
    if not node:
        node = mc.ls(sl=True)[0]

    if CG_ALL not in node:
        comment.format_comment("""Please select a group named "ALL" """)

    else:
        if not mc.objExists(node + '.' + ATTR_MASTER_CG):
            mc.lockNode(node, lock=False)
            mc.addAttr(node, longName=ATTR_MASTER_CG, attributeType='bool', keyable=False, defaultValue=True)
            mc.lockNode(node, lock=True)
        else:
            mc.setAttr(node + '.' + ATTR_MASTER_CG, True)

def cgHierarchie_check(cgs=[], cg_all='cg_all', *args):
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

        if cgHi[-1] != cg_all:
            orphanCg.extend(cgHi)

    return orphanCg

#def find_cg_master():
