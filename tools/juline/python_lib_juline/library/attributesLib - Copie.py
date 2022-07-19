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

def filter_attr(attrTarget='', searchList=None, typ='transform'):
    """
    author : Juline BRETON
    :param attrTarget: string : attribute name
    :param searchList: list
    :param typ: string : node type
    :return: list of all nodes with the attribute target
    """

    if not searchList:
        searchList = mc.ls(sl=False, type=typ)
    lAttrWanted = []
    for node in searchList:
        lAllAttr = mc.listAttr(node)
        if attrTarget in lAllAttr:
            lAttrWanted.append(node)
    return lAttrWanted

def get_attr_state(attrTarget, stateTarget):
    """
    author : Juline BRETON
    :param attrTarget: string
    :param stateTarget: string
    :return: list of transforms with the attribute target at a specific state
    """
    lAttrWanted = filter_attr(attrTarget)
    lStateWanted = []
    for obj in lAttrWanted:
        state = mc.getAttr(obj + '.' + attrTarget)
        if state == stateTarget:
            lStateWanted.append(obj)
    return lStateWanted


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
