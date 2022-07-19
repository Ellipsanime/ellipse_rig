# coding: utf-8

import maya.cmds as mc


def get_all_parents(obj):
    all_parents = list()
    current_parents = mc.listRelatives(obj, p=True)
    while current_parents:
        all_parents.extend(current_parents)
        current_parents = mc.listRelatives(current_parents[0], p=True)
    return all_parents
