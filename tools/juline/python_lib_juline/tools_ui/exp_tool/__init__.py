# coding: utf-8
import maya.cmds as mc

scenePath = mc.file(sn=True, q=True)


def doModExpDataLoc():
    scenePath = mc.file(sn=True, q=True)
    lBoxs = mc.ls(assemblies=True)
    box = ''
    for node in lBoxs:
        if not mc.listRelatives(node, s=True):
            box = node
    dtNode = 'DATA'
    if not mc.objExists('DATA'):
        dtNode = mc.createNode('transform', n='DATA')
        mc.parent(dtNode, box)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    for ref in lRef:
        nSpace = mc.referenceQuery(ref, ns=True)
        assetName = nSpace[1: len(nSpace) - len(nSpace.split('_')[-1]) - 1].split(':')[-1]
        # lower case for 1 letter
        assetNameFormat = assetName.replace(assetName[0], assetName[0].lower())
        geo = nSpace + ':geo_' + assetNameFormat
        father = mc.listRelatives(geo, p=True)[0]

        loc = mc.spaceLocator(n='data_' + nSpace[1].lower() + nSpace[2:])[0]
        mc.setAttr(loc + '.overrideEnabled', 1)
        mc.setAttr(loc + '.overrideColor', 20)

        mc.addAttr(loc, ln='path', dt='string')
        mc.addAttr(loc, ln='nSpace', dt='string')
        mc.addAttr(loc, ln='father', dt='string')

        mc.setAttr(loc + '.path', ref, type='string')
        mc.setAttr(loc + '.nSpace', nSpace[1:], type='string')
        mc.setAttr(loc + '.father', father, type='string')

        mc.setAttr(loc + '.path', l=True)
        mc.setAttr(loc + '.nSpace', l=True)
        mc.setAttr(loc + '.father', l=True)
        mc.delete(mc.parentConstraint(geo, loc, mo=False))
        mc.delete(mc.scaleConstraint(geo, loc, mo=False))
        for attr in ('t', 'r', 's'):
            mc.setAttr(loc + '.' + attr, l=True)
        mc.parent(loc, dtNode)

        refNode = mc.referenceQuery(ref, rfn=True)
        lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
        mc.file(ur=refNode)
        if lEdits:
            for edit in lEdits:
                action = edit.split('|')[0]
                mc.file(cr=refNode, editCommand=action)
        mc.file(ref, rr=True)


# doModExpDataLoc()


def doModExp():
    asset = scenePath.split('_')[-4]
    newName = asset[0].lower() + asset[1:]
    geo = 'GEO'
    for child in mc.listRelatives(box, c=True):
        mc.parent(child, world=True)
        mc.addAttr(child, ln='dtType', dt='string')
        mc.setAttr(child + '.dtType', child, type='string')
        mc.setAttr(child + '.dtType', l=True)
        if child == geo:
            mc.setAttr(child + '.displayHandle', 1)
            mc.setAttr(geo + '.overrideEnabled', 1)
            mc.setAttr(geo + '.overrideColor', 17)
            geo = mc.rename(child, child.lower() + '_' + newName)
        else:
            driven = mc.rename(child, child.lower() + '_' + newName)
            mc.parentConstraint(geo, driven, mo=True)
            mc.scaleConstraint(geo, driven, mo=True)

    mc.delete(box)


# doModExp()
# coding: utf-8

from ...library import attributesLib


def create_reference_derive():
    scene = mc.ls(sl=True)
    for obj in scene:
        if obj.endswith(":DATA"):
            data = obj
    ls_data_loc = mc.listRelatives(data, children=True) or []
    for data_loc in ls_data_loc:
        path   = mc.getAttr(data_loc + '.path')
        nSpace = mc.getAttr(data_loc + '.nSpace')
        father = mc.getAttr(data_loc + '.father')

        # pop up UI for select the task EXP you want
        # add checkBox auto import STP_EXP
        mc.referenceEdit(nSpace, file=path)