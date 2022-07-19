# coding: utf-8

import maya.cmds as mc


def guideRollLinkAttr(tpl, nAttr):
    mc.addAttr(tpl, ln=nAttr, at='bool', dv=True)


def all_base_attr(t=True, r=True, s=True, v=True):
    """
    author : Juline BRETON
    :param t: bool : attr translate x, y, z
    :param r: bool : attr rotate x, y, z
    :param s: bool : attr scale x, y, z
    :param v: bool : visibility
    :return: list of attribute selected
    """
    lBaseAttr = []
    if t:
        lBaseAttr.append('.tx')
        lBaseAttr.append('.ty')
        lBaseAttr.append('.tz')
    if r:
        lBaseAttr.append('.rx')
        lBaseAttr.append('.ry')
        lBaseAttr.append('.rz')
    if s:
        lBaseAttr.append('.sx')
        lBaseAttr.append('.sy')
        lBaseAttr.append('.sz')
    if v:
        lBaseAttr.append('.v')
    return lBaseAttr


def filter_attr(attrTarget='', searchList=None, typ='transform', extra=False):
    """
    author : Juline BRETON
    :param attrTarget: string : attribute name
    :param searchList: list
    :param typ: string : node type
    :param extra: bool : extra attributes
    :return: list of all nodes with the attribute target
    """
    if not searchList:
        searchList = mc.ls(sl=False, type=typ)
    lAttrWanted = []
    for node in searchList:
        if extra is True:
            lAllAttr = mc.listAttr(node, userDefined=True) or []
        else:
            lAllAttr = mc.listAttr(node) or []

        if attrTarget in lAllAttr:
            lAttrWanted.append(node)
    return lAttrWanted


def get_attr_state(attrTarget, stateTarget, typ='transform'):
    """
    author : Juline BRETON
    :param attrTarget: string
    :param stateTarget: string
    :return: list of transforms with the attribute target at a specific state
    """
    lAttrWanted = filter_attr(attrTarget, typ=typ)
    lStateWanted = []
    for obj in lAttrWanted:
        state = mc.getAttr(obj + '.' + attrTarget)
        if state == stateTarget:
            lStateWanted.append(obj)
    return lStateWanted


def filter_attribute_bool(node, attr):
    node_attr = "{}.{}".format(node, attr)
    if mc.objExists(node_attr):
        if mc.getAttr(node_attr):
            return True
    else:
        return False


def transfer_attr(source, target, attr, delete):
    '''
    Author : Juline BRETON
    :return:
    '''
    source, attr, target = copy_attr(source, target, attr)
    transfer_connection(source, target, attr)
    if delete:
        mc.deleteAttr(source + '.' + attr)


def transfer_connection(source, target, attr):
    lDest = mc.listConnections(source + '.' + attr, destination=True, source=False, plugs=True) or []
    for dest in lDest:
        mc.connectAttr(target + '.' + attr, dest, force=True)
    lSource = mc.listConnections(source + '.' + attr, destination=False, source=True, plugs=True) or []
    for source in lSource:
        mc.connectAttr(source, target + '.' + attr, force=True)


def copy_attr(source, target, attr):
    '''
    Author : Juline BRETON
    :return:
    '''
    type_attr = mc.getAttr(source + '.' + attr, type=True)
    keyable = mc.attributeQuery(attr, node=source, keyable=True)
    lChannelBox = mc.listAttr(source, channelBox=True, userDefined=True) or []
    if mc.objExists(target + '.' + attr):
        print 'Sorry! the attribute : ' + attr + ' already existe on ' + target

    elif type_attr == 'float':
        mc.addAttr(target, shortName=attr,
                   defaultValue=mc.attributeQuery(attr, node=source, listDefault=True)[0], keyable=keyable)
        if mc.attributeQuery(attr, node=source, minExists=True):
            minVal = mc.attributeQuery(attr, node=source, minimum=True)[0]
            mc.addAttr(target + '.' + attr, edit=True, hasMinValue=True, minValue=minVal)
        if mc.attributeQuery(attr, node=source, maxExists=True):
            maxVal = mc.attributeQuery(attr, node=source, maximum=True)[0]
            mc.addAttr(target + '.' + attr, edit=True, hasMaxValue=True, maxValue=maxVal)

    elif type_attr == 'enum':
        mc.addAttr(target, attributeType=type_attr, shortName=attr,
                   enumName=mc.attributeQuery(attr, node=source, listEnum=True)[0], keyable=keyable)

    elif type_attr == 'bool':
        mc.addAttr(target, attributeType=type_attr, shortName=attr, keyable=keyable)

    elif type_attr == 'string':
        mc.addAttr(target, dataType=type_attr, shortName=attr, keyable=keyable)

    elif type_attr == 'message':
        mc.addAttr(target, attributeType=type_attr, shortName=attr, keyable=keyable)

    elif type_attr:
        print 'This attribute type is not supported :', type_attr

    if attr in lChannelBox:
        mc.setAttr(target + '.' + attr, channelBox=True)

    # ne fonctionne pas en fonction des type d'attr
    #if mc.getAttr(source + '.' + attr):
    #    mc.setAttr(target + '.' + attr, mc.getAttr(source + '.' + attr))

    return source, attr, target

#################################################################################################


def find_attr(attr_target='', search_list=None, node_type=['transform'], extra=False):
    """
    Parameters
    ----------
    attr_target : string
        attribute name wanted
    search_list : string
    node_type : list of string
        type of maya node
    extra : Boolean
        True if the attribute target is an extra attribute
    Returns
    -------
    List
        of all nodes with the attribute target
    """
    if not search_list:
        search_list = mc.ls(sl=False, type=node_type)
    ls_attr_wanted = []
    for node in search_list:
        if extra is True:
            ls_all_attr = mc.listAttr(node, userDefined=True) or []
        else:
            ls_all_attr = mc.listAttr(node) or []

        if attr_target in ls_all_attr:
            ls_attr_wanted.append(node)
    return ls_attr_wanted


def get_ls_attr_state(attr_target, state_target, node_type=['transform']):
    """
    Find the the
    Parameters
    ----------
    attr_target : string
        attribute name wanted
    state_target : string
        state of attribute wanted
    node_type : list of string
        type of maya node

    Returns
    -------
    list
        of transforms with the attribute target at the specific state
    """
    ls_attr_wanted = find_attr(attr_target, node_type=node_type)
    ls_tate_wanted = []
    for obj in ls_attr_wanted:
        state = mc.getAttr(obj + '.' + attr_target)
        if state == state_target:
            ls_tate_wanted.append(obj)
    return ls_tate_wanted