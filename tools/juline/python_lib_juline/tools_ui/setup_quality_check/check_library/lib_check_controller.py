# coding: utf-8
# Author : Juline BRETON

from ....utils import comment
from ....library import namesLib, attributesLib, shapesLib
from .......library import lib_controlGroup, lib_pipe

import maya.cmds as mc

reload(lib_controlGroup)

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


# CG In CTRL
# Author : Juline BRETON & Pierre FABAREZ
def check_ctrl_in_cg():
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
        dic_check = check_ctrl_in_cg()
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


def get_lonely_ctrl():  #### MODIFTY >> SEARCH MASTER CG_ALL FIRST
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


def get_all_ctrl():
    ls_ctrl = attributesLib.get_attr_state(attrTarget='nodeType', stateTarget='control', typ='transform')
    return ls_ctrl


# BINDPOSE


def check_extra_attr_bind_pose():
    """
    Check if all extra attributes keyable have a Bind Pose or if the current pose is the Base Pose
    Returns
    -------
    List_0, List_1
        0 : ls_missing_bind_pose
        1 : ls_wrong_bind_pose
    """
    ls_ctrl = get_all_ctrl()
    ls_missing_bind_pose = []
    ls_wrong_bind_pose = []
    print len(ls_wrong_bind_pose)

    for ctrl in ls_ctrl:
        # Get extraAttr keyable
        ls_extra_attr = mc.listAttr(ctrl, userDefined=True, keyable=True) or []
        for attr in ls_extra_attr:
            if mc.objExists("{}.bindPoseAttrs[*]".format(ctrl)):
                # Check if BindPoseAttr Set with the name attr
                ls_bind_pose = mc.getAttr("{}.bindPoseAttrs[*]".format(ctrl))

                if not attr in ls_bind_pose:
                    ls_missing_bind_pose.append("{}.{}".format(ctrl, attr))
                else:
                    # get index in the list for find the value of the Bind Pose
                    index = ls_extra_attr.index(attr)

                    # check if the current pose is the Bind Pose : compare values
                    bind_pose_value = mc.getAttr("{}.bindPoseValues[{}]".format(ctrl, index))
                    current_value = mc.getAttr("{}.{}".format(ctrl, attr))
                    if current_value != bind_pose_value:
                        ls_wrong_bind_pose.append("{}.{}".format(ctrl, attr))
            else:
                ls_missing_bind_pose.append("{}.{}".format(ctrl, attr))

    return ls_missing_bind_pose, ls_wrong_bind_pose


def check_set_bind_pose():
    """
    Check if the current pose is the Bind Pose
    Returns
    -------
    Dict
        dic_check for set UI
    """
    ls_missing_bind_pose, ls_wrong_bind_pose = check_extra_attr_bind_pose()
    # Set the dict for UI

    if ls_missing_bind_pose:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_missing_bind_pose
    else:
        dic_check['STATE'] = "OK"

    return dic_check


def fix_set_bind_pose(ls_problem=[]):
    """
    Set Bind Pose on extra attributes

    """
    if ls_problem:
        print "fix just this one", ls_problem
        ls_ctrl_attr = ls_problem

    ls_ctrl_attr = dic_check['NEED_FIX']
    ls_ctrl = []
    for ctrl_attr in ls_ctrl_attr:
        if ctrl_attr.split('.')[0] not in ls_ctrl:
            ls_ctrl.append(ctrl_attr.split('.')[0])

    lib_controlGroup.setBindPose(ls_ctrl)


def check_reset_bind_pose():
    """
    Check if the current pose is the Bind Pose
    Returns
    -------
    Dict
        dic_check for set UI
    """
    ls_missing_bind_pose, ls_wrong_bind_pose = check_extra_attr_bind_pose()
    # Set the dict for UI

    if ls_missing_bind_pose:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_wrong_bind_pose
    else:
        dic_check['STATE'] = "OK"

    return dic_check


# SHAPE NAME


def check_shape_name():
    """
    Check the shape(s) name on transform.nodeType == control
    Returns
    -------
    Dict
        dic_check for set UI
    """
    ls_all_ctrl = attributesLib.get_attr_state(attrTarget="nodeType", stateTarget="control", typ=['transform', 'joint'])
    ls_ctrl_bad_name_shape = []
    for ctrl in ls_all_ctrl:
        ls_shapes = mc.listRelatives(ctrl, shapes=True) or []
        for shape in ls_shapes:
            if not shape.startswith("{}Shape".format(ctrl)):
                if not ctrl in ls_ctrl_bad_name_shape:
                    ls_ctrl_bad_name_shape.append(ctrl)
    if ls_ctrl_bad_name_shape:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = ls_ctrl_bad_name_shape
    else:
        dic_check['STATE'] = "OK"

    return dic_check


def rename_shape(my_list):
    """
    Rename the shape(s) of the given list
    Parameters
    ----------
    my_list

    Returns
    -------

    """
    for obj in my_list:
        ls_shapes = mc.listRelatives(obj, shapes=True, fullPath=True) or []
        if len(ls_shapes) > 1:
            for i in range(len(ls_shapes)):
                # if not instance shape with extra attr
                if not mc.listAttr(ls_shapes[i], userDefined=True):
                    mc.rename(ls_shapes[i].split('|')[-1], obj + 'Shape' + str(i + 1))
        elif len(ls_shapes) == 1:
            # if not instance shape with extra attr
            if not mc.listAttr(ls_shapes[0], userDefined=True):
                if not mc.objExists(obj + 'Shape'):
                    try:
                        mc.rename(ls_shapes[0], obj + 'Shape')
                    except:
                        print obj + " shape(s) can't be renamed"
                else:
                    try:
                        mc.rename(ls_shapes[0], obj + 'Shape1')
                    except:
                        print obj + " shape(s) can't be renamed"


def fix_shape_name(my_list=[]):
    if my_list:
        rename_shape(my_list)
    else:
        dic_check = check_shape_name()
        if dic_check["STATE"] == "NEED_FIX":
            rename_shape(dic_check["NEED_FIX"])
