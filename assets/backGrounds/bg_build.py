import re
from functools import partial

import maya.cmds as mc
# import maya.mel as mel

from ...library import lib_controlGroup, lib_clean, lib_rigs, lib_pipe
from ...tools.juline.python_lib_juline.library import attributesLib, namesLib
from ...tools.juline.python_lib_juline.utils import comment
reload(lib_controlGroup)
reload(lib_clean)
reload(lib_rigs)

"""
# START PYTHON

import sys

DEVPATHS = [r"C:\Users\cyril.gibaud\Documents\Dev\foundation_rig"]

for DEVPATH in DEVPATHS:
    if not DEVPATH in sys.path:
        sys.path.append(DEVPATH)

import foundation_rig.assets.backGrounds.bg_build as bg_build
reload(bg_build)

# Create a template of a node (on HovelGargLiving.ma)
print bg_build.createTemplate("geo_CageRoundA_1")

# Create a whole rig
# bg_build.build()
"""


def getBox():
    return lib_clean.getRefBoxs()

def connectColorsCtrl(box, lCtrl):
    dicColors = {}
    dicColors['Yellow'] = 17
    dicColors['LightYellow'] = 22
    dicColors['Red'] = 13
    dicColors['Blue'] = 6
    dicColors['LightBlue'] = 18
    dicColors['Green'] = 14
    dicColors['White'] = 16
    dicColors['Purpple'] = 20
    enVals = ''
    chNode = ''
    doChoiceNode = 1
    id = 0

    lChk = mc.listConnections(box, destination=True) or []
    if lChk:
        chkNode = mc.ls(lChk, type='choice') or []
        if chkNode:
            chNode = chkNode[0]
            doChoiceNode = 0
    if doChoiceNode == 1:
        chNode= mc.createNode('choice', n='cho_ctrlColor')
    for col in sorted(dicColors.keys()):
        enVals += ':'+col
        mc.setAttr(chNode+'.input['+str(id)+']', dicColors[col])
        id += 1
    if not mc.attributeQuery('ctrlColor', n=box, ex=True):
        mc.addAttr(box, ln='ctrlColor', at='enum', en=enVals)
        mc.connectAttr(box+'.ctrlColor', chNode+'.selector')
    for ctrl in lCtrl:
        mc.connectAttr(chNode+'.output', ctrl+'.overrideColor')
        mc.setAttr(ctrl+'.overrideEnabled', 1)

def getONs(node):
    """
        return the "origNs" (controlgroup name) of a node
        
        :param node: The node name to look onto
        :type node: str
        :return: The attribute value
        :rtype: str
    """
    # CGibaud
    if mc.attributeQuery('origNs', n=node, ex=True):
        return mc.getAttr(node+'.origNs')
    else:
        path = mc.file(q=True, sceneName=True)
        assetName = path.split('_')[4]
        clearName = assetName[0].lower()+assetName[1:]
        return clearName

def getOPos(node):
    """
        return the "origPiv" (global pivot) of a node
        
        :param node: The node name to look onto
        :type node: str
        :return: The attribute value
        :rtype: list[double]
    """
    # CGibaud
    if mc.attributeQuery('origPiv', n=node, ex=True):
        return mc.getAttr(node+'.origPiv')[0]
    else:
        comment.format_comment('WARNING : NO origPiv FIND ON :\n' + node)
        # get the center obj
        return mc.objectCenter(node)

def getORt(node):
    """
        return the "origRt" (global rotation) of a node
        
        :param node: The node name to look onto
        :type node: str
        :return: The attribute value
        :rtype: list[double]
    """
    # CGibaud
    if mc.attributeQuery('origRt', n=node, ex=True):
        return mc.getAttr(node+'.origRt')[0]
    else:
        comment.format_comment('WARNING : NO origRt FIND ON :\n' + node)
        return [0,0,0]


def getORotOrder(node):
    """
        return the "origRotOrder" (RotOrder) of a node
        
        :param node: The node name to look onto
        :type node: str
        :return: The attribute value
        :rtype: int
    """
    if mc.attributeQuery('origRotOrder', n=node, ex=True):
        return mc.getAttr(node+'.origRotOrder')
    else:
        comment.format_comment('WARNING : NO origRotOrder FIND ON :\n' + node)
        return 0

# TODO Comments
def getBoundingBox(inObjects, inLocalSpace=False, inRefObject=None):
    # Collect shapes
    shapes = []
    shapeTypes = ["mesh"]
    for object in inObjects:
        nodeType = mc.nodeType(object)

        if nodeType == "transform":
            # shapes.extend([s for s in mc.ls(mc.listRelatives(object, shapes=True), type=shapeTypes) if not mc.getAttr("{0}.intermediateObject".format(s))])
            for s in mc.ls(mc.listRelatives(object, shapes=True), type=shapeTypes):

                if not mc.getAttr("{0}.intermediateObject".format(s)):
                    shapes.extend(s)

        elif nodeType in shapeTypes and not mc.getAttr("{0}.intermediateObject".format(object)):
            shapes.append(object)


    if inRefObject is None:
        if inLocalSpace:
            mc.error("Not implemented !")

        return mc.exactWorldBoundingBox(shapes, calculateExactly=True)
    else:
        # refMatrix = mc.xform(inRefObject, query=True, worldSpace=True, matrix=True )
        grp = mc.group(empty=True)

        # mc.select([grp, inRefObject])
        # mel.eval("MatchTransform")
        # mc.select(cl=True)
        mc.matchTransform([grp, inRefObject])

        # mc.xform(grp, worldSpace=True, matrix=refMatrix)
        
        shapeTs = list(set([mc.listRelatives(s, parent=True)[0] for s in shapes]))

        # duplicate and Constrain the meshes tranforms to te ref object
        constraints = []
        duplicates = []
        duplicateShapes = []

        for shapeT in shapeTs:
            gpu = False
            if (':') in shapeT:
                chkName = shapeT.split(':')[-1]
                if chkName.startswith('rs_'):
                    shapeT = mc.listRelatives(shapeT, p=True)[0]
                    gpu = True
            dup = mc.duplicate(shapeT, name="{0}_TMPDUPLICATE".format(shapeT))[0]

            duplicates.append(dup)
            if gpu == False:

                duplicateShapes.extend([s for s in mc.ls(mc.listRelatives(dup, shapes=True), type=shapeTypes) if not mc.getAttr("{0}.intermediateObject".format(s))])
            elif gpu == True:

                duplicateShapes.append(dup)
            constraints.append(mc.parentConstraint(grp, dup, maintainOffset=True))

        # Put the ref object to identity matrix
        idMatrix = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        mc.xform(grp, worldSpace=True, matrix=idMatrix)
        
        # remove constraints
        for constraint in constraints:
            mc.delete(constraint)
        
        # Freeze transforms on duplicates otherwise "exactWorldBoundingBox" is not correct :/
        for duplicate in duplicates:
            mc.makeIdentity(duplicate, apply=True, t=True, r=True, s=True, n=False, pn=True)
        
        # get the worldBB in this pose
        print 'HERE :', duplicateShapes
        bb = mc.exactWorldBoundingBox(duplicateShapes, calculateExactly=True)
        
        # Delete the helpers
        for duplicate in duplicates:
            mc.delete(duplicate)
        
        mc.delete(grp)
            
        return bb


def createTemplate(inNode, inShapeBorder=1.0):
    """
        Create a template from a transform Node

        :param inNode: The transform node to create the template from
        :param inShapeBorder: The border of the control Shape added to the strict boundingBox
        :type inNode: str
        :type inShapeBorder: double
        :return: A dictionary of template metadata
        :rtype: dict{"tpl":str, "ns":str, "pos":list[double], "rot":list[double], "rotOrder":int}
    """

    #print "createTemplate("+inNode+")"

    # Retrieve metadata
    oNs = getONs(inNode)
    oPos = getOPos(inNode)
    oRt = getORt(inNode)
    oRotOrder = getORotOrder(inNode)

    tplName = ''

    old_name = None
    if mc.objExists(inNode + '.oldName'):
        if mc.getAttr(inNode + '.oldName'):
            old_name = mc.getAttr(inNode + '.oldName')

    # Juline : Add Name Space
    if old_name:
        tplName = old_name.replace("c_", "tpl_")

    else:
        # Create the template object
        if (':') in inNode:
            tplName = inNode.split(':')[-1]
        nTplBase = tplName[len(tplName.split('_')[0]):]
        nTplBase = nTplBase[0].lower() + nTplBase[1:]
        tplName = 'tpl'+nTplBase
        nspace = inNode[:len(inNode)-len(inNode.split(':')[-1])]
        tplName = nspace+tplName




    # tplName = inNode[4:] if inNode.startswith("geo_") else inNode
    # #  Create the template object
    # if (':') in inNode:
    #     tplName = inNode.split(':')[-1][len(inNode.split(':')[-1].split('_')[0]):]

    # tplName = tplName[0].lower() + tplName[1:]
    # tplName = "tpl{0}".format(tplName)

    loc = lib_rigs.createObj(partial(mc.group, **{'empty': True, 'n': tplName}), shape=lib_rigs.Shp(["cube"],
                            size=(0.5, 0.5, 0.5), color="yellow"))  # mc.spaceLocator(name=tplName, absolute=True)[0]
    mc.setAttr(loc + ".t", type="float3", *oPos)
    mc.setAttr(loc + ".r", type="float3", *oRt)

    # Tweak thye Shape
    # Collect all polymsh shapes underneath the group
    shapes = []
    descs = mc.listRelatives(inNode, allDescendents=True)
    print 'HERE AGAIN :', inNode, descs
    for desc in descs:
        if mc.nodeType(desc) == 'mesh':
            shapes.append(desc)
        shapes.extend(mc.listRelatives(desc, shapes=True) or [])
    print shapes

    # Get the local bounding box relative to "loc"
    x1, y1, z1, x2, y2, z2 = getBoundingBox(shapes, inRefObject=loc)
    valTrans = [(x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2]

    # offset the shape
    ctrlShapes = mc.listRelatives(loc, shapes=True)
    for ctrlShape in ctrlShapes:
        pntCount = mc.getAttr("{0}.degree".format(ctrlShape)) + mc.getAttr("{0}.spans".format(ctrlShape))

        if type(pntCount) is list:
            pntCount = pntCount[0] + pntCount[-1]

        mc.scale(
            x2-x1 + 2*inShapeBorder, y2-y1 + 2*inShapeBorder, z2-z1 + 2*inShapeBorder,
            ["{0}.cv[0:{1}]".format(ctrlShape, pntCount - 1)], relative=True
            )

        mc.move(
            valTrans[0], valTrans[1], valTrans[2],
            ["{0}.cv[0:{1}]".format(ctrlShape, pntCount - 1)], objectSpace=True, relative=True
            )

    # Strip underscores in front of increments
    cgName = inNode[len(inNode.split(':')[0]):len(inNode)-len(inNode.split(':')[-1])]
    if ":" in cgName:
        cgName = cgName.replace(':', '')

    if cgName == '':
        scenePath = mc.file(sn=True, q=True)
        cgName =  scenePath.split('/')[5]

    cgName = cgName[0].lower()+cgName[1:].replace('_', '')
    cg = lib_controlGroup.crtCg('cg_'+cgName)
    lib_controlGroup.addTplsToCg([loc], 'cg_'+cgName)


    if not mc.objExists(loc):
        loc = loc.split('|')[-1]
        print 'tututuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu', loc

    # tweak template control group attributes
    mc.setAttr(loc + ".isMirrored", False)
    mc.setAttr(loc + ".location", 0)

    return {"tpl":loc, "ns":oNs, "pos":oPos, "rot":oRt, "ro":oRotOrder, "cg":'cg_'+cgName}

def build(inRootControlGroup="all", inRootControl="WORLD"):
    """
    Auto-rig a complete scene
    """
    # Create the "Global" control hierarchy
    topNode = getBox()[0]
    if not mc.objExists(topNode):
        mc.group(empty=True, name=topNode)

    toDel = 'TPL'
    if not mc.objExists('TPL'):
        mc.createNode('transform', n='TPL')
        mc.addAttr('TPL', ln='deleteMe', at='bool', dv=1)
    masterCtrl = 'WORLD'
    if not mc.objExists('WORLD'):
        mc.createNode('transform', n='WORLD')
        mc.parent(masterCtrl, topNode)

    # Collect all "rigMe" attributes
    rigGroups = attributesLib.get_attr_state(attrTarget="rigMe", stateTarget=True)
    visGroups = attributesLib.get_attr_state(attrTarget="onlyVis", stateTarget=True)
    riggedGroups = rigGroups + visGroups

    groups_tpl = {}

    controlGroups = []

    # Create the root controlgroup
    allCtrlGroupName = "cg_" + inRootControlGroup  #
    if not mc.objExists(allCtrlGroupName):
        lib_controlGroup.crtCg(inRootControlGroup)
        controlGroups.append(allCtrlGroupName)

    # Create the root template
    # allTpl = mc.spaceLocator(name="tpl_" + inRootControl, absolute=True)[0]

    allTpl = toDel
    # Put the template in the control group
    # lib_controlGroup.addTplToCg(allTpl, allCtrlGroupName)

    # Create the templates
    for i in range(len(riggedGroups)):
        print 'creation tpl :', str(i), '/', str(len(riggedGroups))
        groups_tpl[riggedGroups[i]] = createTemplate(riggedGroups[i])
        controlGroups.append(groups_tpl[riggedGroups[i]]["cg"])


    # Re-create a hierarchy for these templates
    for riggedGroup in riggedGroups:
        tpl = groups_tpl[riggedGroup]

        # Find a "RigMe" object in the parents of the current "RigMe"
        groupParent = mc.listRelatives(riggedGroup, parent=True)
        groupParent = None if groupParent is None else groupParent[0]
        while(not groupParent in riggedGroups and not groupParent is None):
            groupParent = mc.listRelatives(groupParent, parent=True)
            groupParent = None if groupParent is None else groupParent[0]

        # If there is actually a parent, parent templates (or controlGroups)
        if not groupParent is None:
            parentCtrl = groups_tpl[groupParent]

            parentCtrlGroup = parentCtrl["cg"].replace("cg_", "tpl_")
            actualCtrlGroup = tpl["cg"].replace("cg_", "tpl_")

            if tpl["cg"] == parentCtrl["cg"]: # Same control group, parent templates
                # print "tpl",tpl,"parentCtrl",parentCtrl
                # print "PARENT TEMPLATE",tpl["tpl"],parentCtrl["tpl"]
                mc.parent(tpl["tpl"], parentCtrl["tpl"])
            else: # Different control groups, parent control Groups
                actualParent = mc.listRelatives(actualCtrlGroup, parent=True)
                actualParent = None if actualParent is None else actualParent[0]

                # Parent the transform group

                if actualParent != parentCtrlGroup:
                    # print "PARENT CONTROLGROUP",actualCtrlGroup,parentCtrlGroup
                    mc.parent(actualCtrlGroup, parentCtrlGroup)

                # Parent the control group
                lib_controlGroup.parentCg(tpl["cg"], parentCtrl["cg"])
        else: # If there no parent is found, parent (controlGroup to the "root" controlGroup)
            mc.warning("Can't find a parent for '{0}' from '{1}' ({2})".format(tpl["tpl"], riggedGroup, tpl))
            actualCtrlGroup = tpl["cg"].replace("cg_", "tpl_")

            # Parent the transform group
            actualParent = mc.listRelatives(actualCtrlGroup, parent=True)
            actualParent = None if actualParent is None else actualParent[0]

            if actualParent != allTpl:
                mc.parent(actualCtrlGroup, allTpl)

            # Parent the control group
            lib_controlGroup.parentCg(tpl["cg"], allCtrlGroupName)

    # Build
    # for controlGroup in controlGroups:
    for i in range(len(controlGroups)):
        print 'buil rig :', str(i), '/', str(len(controlGroups))
        if mc.listConnections(controlGroups[i]+'.templates'):
            lib_controlGroup.buildTplCg(controlGroups[i])

    # Parent the rig root to "ancestor"
    # mc.parent(allCtrlGroupName.replace("tpl_", "rig_"), masterCtrl)
    # print allCtrlGroupName.replace("tpl_", "rig_"), masterCtrl, 'SUCE'
    lCtrl = []
    # Constrain geos
    for riggedGroup in riggedGroups:
        rigSk = groups_tpl[riggedGroup]["tpl"].replace("tpl_", "sk_")
        ctrl = groups_tpl[riggedGroup]["tpl"].replace('tpl_', 'c_')
        lCtrl.append(ctrl)
        # mc.parentConstraint(rigSk, riggedGroup, maintainOffset=True)
        # mc.scaleConstraint(rigSk, riggedGroup, maintainOffset=True)
        mc.parentConstraint(ctrl, riggedGroup, maintainOffset=True)
        mc.scaleConstraint(ctrl, riggedGroup, maintainOffset=True)
        lib_pipe.addVisAttr(ctrl, riggedGroup)
        if mc.attributeQuery('rigMe', n=riggedGroup, ex=True):
            mc.setAttr(riggedGroup+'.rigMe', 0)
        if mc.attributeQuery('onlyVis', n=riggedGroup, ex=True):
            mc.setAttr(riggedGroup+'.onlyVis', 0)
            for attr in ['.translate', '.rotate', '.scale']:
                for channel in ['X', 'Y', 'Z']:
                    mc.setAttr(ctrl+attr+channel, k=False, lock=True)
        #  Juline : Lister les enfants des sk pour les reparenter sous le c avant de supprimer les sk
        ls_children_sk = mc.listRelatives(rigSk, children=True) or []
        for child in ls_children_sk:
            mc.parent(child, ctrl)
        mc.delete(rigSk)

    lBoxs = lib_clean.getAllBoxs()
    for box in lBoxs:
        if box.startswith('rig_'):
            mc.parent(box, 'WORLD')
    connectColorsCtrl(topNode, lCtrl)

