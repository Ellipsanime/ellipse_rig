# coding: utf-8

import maya.cmds as mc

def get_ref_count():
    """
    Author : Juline BRETON
    :return: nb of reference, ls ref node
    """
    ls_ref_node = mc.ls(sl=False, type='reference') or []
    return len(ls_ref_node), ls_ref_node