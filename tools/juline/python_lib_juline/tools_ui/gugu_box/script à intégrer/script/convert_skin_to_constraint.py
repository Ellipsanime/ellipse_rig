# coding: utf-8
import maya.cmds as mc

def all_base_attr(t=True, r=True, s=True, v=True):
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

def convert_skin_to_constraint():
    lSkinClst = mc.ls(sl=False, type='skinCluster') or []
    for skinclst in lSkinClst:
        lJoint = mc.listConnections(skinclst + '.matrix', destination=True, exactType=True, type='joint') or []

        if len(lJoint) == 1:
            jnt = lJoint[0]
            shapeD = mc.listConnections(skinclst + '.outputGeometry')[0]
            trs = mc.listRelatives(shapeD, parent=True)
            mc.delete(skinclst)
            mc.delete(shapeD)
            shape = mc.listRelatives(trs, shape=True)[0]
            mc.setAttr(shape + '.intermediateObject', False)

            # unlock attr
                # OBJ en ref du coup passer pas les refEdit
                # ou STOCKER info dans un dico, cleaner les refEdit à la main et appliquer les constraints ensuite
            lBaseAttr = all_base_attr(t=True, r=True, s=True, v=False)
            for attr in lBaseAttr:
                mc.setAttr(trs + attr, lock=False)


        mc.parentConstraint(jnt, trs, maintainOffset=True)

