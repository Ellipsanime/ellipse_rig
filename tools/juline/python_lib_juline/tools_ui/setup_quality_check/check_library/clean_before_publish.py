# coding: utf-8
# Clean before publish

# from ellipse_rig.library import lib_controlGroup

import maya.cmds as cmds
from ....utils import exception_utils

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = ""
dic_check['NEED_FIX'] = []
dic_check['OK'] = None


def check_items_to_hide():
    """

    Returns
    -------
    dict
        For Module Quality Check
    """
    dic_check = {}
    ls_unhide_deformers = unhide_deformer_check()
    ls_shape_to_hide = item_to_hide_check()
    ls_items_to_hide = ls_unhide_deformers + ls_shape_to_hide
    if ls_items_to_hide:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_items_to_hide
        return dic_check

    else:
        dic_check['STATE'] = "OK"
        return dic_check


def fix_items_to_hide():
    # ls_unhide_deformers = unhide_deformer_check()
    # ls_shape_to_hide = item_to_hide_check()
    # ls_items_to_hide = ls_unhide_deformers + ls_shape_to_hide
    ls_items_to_hide = dic_check['NEED_FIX']
    ls_unhide_deformers_fix(ls_items_to_hide)


def unhide_deformer_check():
    """
    Author :
        Pierre Fabarez

    Check if a specified list of deformers is hide

    Returns
    -------
    List
        Of the deformers visible
    """
    ls_deform_types = ['deformBend',
                       'deformFlare',
                       'deformSine',
                       'deformSquash',
                       'deformTwist',
                       'deformWave',
                       'clusterHandle',
                       'lattice',
                       'baseLattice',
                       'blendShape',
                       'wrap',
                       'wire']
    ls_unhide_deformers = []
    ls_shapes_to_hide = []

    ls_deformers = cmds.ls(type=ls_deform_types)
    for deformer in ls_deformers:
        if cmds.nodeType(deformer) == 'blendShape':
            ls_shapes_to_hide.extend(cmds.listConnections('%s.inputTarget' % deformer, source=True, shapes=True) or [])

        elif cmds.nodeType(deformer) == 'wrap':
            ls_shapes_to_hide.extend(cmds.listConnections('%s.basePoints' % deformer, source=True, shapes=True) or [])

        elif cmds.nodeType(deformer) == 'wire':
            ls_shapes_to_hide.extend(cmds.listConnections('%s.baseWire' % deformer, source=True, shapes=True) or [])
            ls_shapes_to_hide.extend(cmds.listConnections('%s.deformedWire' % deformer, source=True, shapes=True) or [])

        else:
            ls_shapes_to_hide.append(deformer)

    for shape in ls_shapes_to_hide:
        transform_node = cmds.listRelatives(shape, parent=True)[0]
        if not cmds.getAttr('%s.visibility' % transform_node) == 0:
            ls_unhide_deformers.append(transform_node)

    return ls_unhide_deformers


def ls_unhide_deformers_fix(ls_deformers=[]):
    """
    Hide the given list of deformers

    Parameters
    ----------
    ls_deformers : list
        list of deformers

    Returns
    -------

    """
    for deformer in ls_deformers:
        if cmds.attributeQuery('%s.visibility' % deformer, lock=True):
            cmds.setAttr('%s.visibility' % deformer, lock=False)
        cmds.setAttr('%s.visibility' % deformer, 0, force=True)


def item_to_hide_check():
    """
    Author :
        Pierre Fabarez

    Check if a specified list of items is hide

    Returns
    -------
    List
        Of the items visible
    """
    ls_shape_to_hide = []

    ls_ignore_items = get_delete_me_items()

    ls_item_types = ['locator',
                     'nurbsSurface',
                     'nurbsCurve',
                     'follicle',
                     'distanceDimShape']

    ls_item_shapes = cmds.ls(type=ls_item_types)
    for item_shape in ls_item_shapes:
        item_transform = cmds.listRelatives(item_shape, parent=True)[0]
        if item_transform in ls_ignore_items:
            continue

        if cmds.nodeType(item_shape) == 'nurbsCurve':
            if not is_ctrl(item_shape) and cmds.getAttr('%s.visibility' % item_transform) != 0:
                ls_shape_to_hide.append(item_transform)

        elif cmds.nodeType(item_shape) == 'follicle'and cmds.getAttr('%s.visibility' % item_shape) != 0:
            ls_shape_to_hide.append(item_shape)

        elif cmds.getAttr('%s.visibility' % item_transform) != 0 and cmds.getAttr('%s.visibility' % item_shape) != 0:
            ls_shape_to_hide.append(item_transform)

    return ls_shape_to_hide


def get_delete_me_items():
    """
    Author :
        Pierre Fabarez
    Returns
    -------

    """
    delete_me_items = []
    ls_items = cmds.ls(transforms=True)
    for item in ls_items:
        if item in delete_me_items:
            continue

        if cmds.attributeQuery('deleteMe', node=item, exists=True) and cmds.getAttr('%s.deleteMe'%item) == 1:
            child_items = cmds.listRelatives(item, allDescendents=True, type='transform') or []
            delete_me_items.extend(child_items)

    return delete_me_items


def is_ctrl(curve_shape):
    """
    Author :
        Juline BRETON

    Check if the given shape is a controller shape

    Parameters
    ----------
    curve_shape : basestring
        Name of the curve shape

    Returns
    -------
    Boolean
        True if  : it's a ctrl shape
        False if : it's not a ctrl shape
    """
    curve_transform = cmds.listRelatives(curve_shape, parent=True)[0]

    if cmds.objExists(curve_transform + ".nodeType"):
        if cmds.getAttr(curve_transform + ".nodeType") == "control":
            return True
        else:
            return False
    else:
        return False


# def is_ctrl_old(curve_shape):
#     """
#     Author :
#         Pierre Fabarez
#
#     Check if the given shape is a controller shape
#
#     Parameters
#     ----------
#     curve_shape : basestring
#         Name of the curve shape
#
#     Returns
#     -------
#     Boolean
#         True if  :
#         False if :
#     """
#     curve_transform = cmds.listRelatives(curve_shape, parent=True)[0]
#     curve_shape_history = cmds.listHistory(curve_transform)
#
#     for histNode in curve_shape_history:
#         if cmds.nodeType(histNode) != 'nurbsCurve':
#             return False
#
#     curve_sets = cmds.listSets(object=curve_transform)
#     for crvSet in curve_sets:
#         if is_ctrl_set(crvSet):
#             break
#
#     ls_curve_transform_msgs = cmds.connectionInfo('%s.message' % curve_transform, destinationFromSource=True)
#     for curve_transform_msg in ls_curve_transform_msgs:
#         if len(curve_transform_msg.split('.')) == 2:
#             cg, cg_attr = curve_transform_msg.split('.')
#             print cg, cg_attr
#             if cg in lib_controlGroup.getAllCg() and cg_attr.startswith('members'):
#                 print curve_shape, '==> TRUE'
#                 return True
#
#             else:
#                 print curve_shape, '==> FALSE'
#
#
# def is_ctrl_set(ctrl_set):
#     """
#     Author :
#         Pierre Fabarez
#     Parameters
#     ----------
#     ctrl_set
#
#     Returns
#     -------
#
#     """
#     ls_all_cgs = lib_controlGroup.getAllCg()
#     if not cmds.nodeType(ctrl_set) == 'objectSet':
#         return
#
#     ls_msg_connections = cmds.connectionInfo('%s.message'%ctrl_set, destinationFromSource=True) or []
#     for msg in ls_msg_connections:
#         cg, cg_attr = msg.split('.')
#         if cg in ls_all_cgs and cg_attr == 'ctrlSet':
#             return True
#