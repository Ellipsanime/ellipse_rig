# coding: utf-8
# Author : Juline BRETON
# BUILD BG

from ...library import lib_clean, lib_controlGroup
from ...tools.juline.python_lib_juline.library import attributesLib

import maya.cmds as mc

GRP_TPL = 'TPL'
WORLD = 'WORLD'


def build_bg():
    # Create the "Global" control hierarchy
    topNode = lib_clean.getRefBoxs()()[0]
    if not mc.objExists(topNode):
        mc.group(empty=True, name=topNode)

    if not mc.objExists(GRP_TPL):
        mc.createNode('transform', n=GRP_TPL)
        mc.addAttr(GRP_TPL, ln='deleteMe', at='bool', dv=1)

    if not mc.objExists(WORLD):
        mc.createNode('transform', n=WORLD)
        mc.parent(WORLD, topNode)

    # Get geo to rig
    ls_rig_me = attributesLib.get_attr_state(attrTarget="rigMe", stateTarget=True)
    ls_only_vis = attributesLib.get_attr_state(attrTarget="onlyVis", stateTarget=True)

    groups_tpl = {}
    ls_cg = []

    # Create cg_all
    cg_all = 'cg_all'
    if not mc.objExists(cg_all):
        lib_controlGroup.crtCg('all')
        ls_cg.append(cg_all)

    # Create the templates rigMe
    for i in range(len(ls_rig_me)):
        print 'creation tpl :', str(i), '/', str(len(ls_rig_me))
        groups_tpl[ls_rig_me[i]] = createTemplate(ls_rig_me[i])
        ls_cg.append(groups_tpl[ls_rig_me[i]]["cg"])

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

    # print "createTemplate("+inNode+")"

    # Retrieve metadata
    oNs = getONs(inNode)
    oPos = getOPos(inNode)
    oRt = getORt(inNode)
    oRotOrder = getORotOrder(inNode)
    old_name = mc.getAttr(inNode + '.oldName')

    #  if old_name == None:
    #      tplName = inNode[4:] if inNode.startswith("geo_") else inNode
    #      # Create the template object
    #      if (':') in inNode:
    #          tplName = inNode.split(':')[-1][len(inNode.split(':')[-1].split('_')[0]):]
    #      tplName = tplName[0].lower() + tplName[1:]
    #      tplName = "tpl{0}".format(tplName)
    #  else:
    #      tplName = old_name

    tplName = inNode[4:] if inNode.startswith("geo_") else inNode
    #  Create the template object
    if (':') in inNode:
        tplName = inNode.split(':')[-1][len(inNode.split(':')[-1].split('_')[0]):]

    tplName = tplName[0].lower() + tplName[1:]
    tplName = "tpl{0}".format(tplName)

    loc = lib_rigs.createObj(partial(mc.group, **{'empty': True, 'n': tplName}), shape=lib_rigs.Shp(["cube"], size=(0.5, 0.5, 0.5),color="yellow"))# mc.spaceLocator(name=tplName, absolute=True)[0]
    mc.setAttr(loc + ".t", type="float3", *oPos)
    mc.setAttr(loc + ".r", type="float3", *oRt)

    # Tweak thye Shape
    # Collect all polymsh shapes underneath the group
    shapes = []
    descs = mc.listRelatives(inNode, allDescendents=True)
    for desc in descs:
        shapes.extend(mc.listRelatives(desc, shapes=True) or [])

    # Get the local bounding box relative to "loc"
    x1, y1, z1, x2, y2, z2 = getBoundingBox(shapes, inRefObject=loc)
    valTrans = [(x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2]

    # offset the shape
    ctrlShapes = mc.listRelatives(loc, shapes=True)
    for ctrlShape in ctrlShapes:
        pntCount = mc.getAttr("{0}.degree".format(ctrlShape)) + mc.getAttr("{0}.spans".format(ctrlShape))

        mc.scale(
            x2-x1 + 2*inShapeBorder, y2-y1 + 2*inShapeBorder, z2-z1 + 2*inShapeBorder,
            ["{0}.cv[0:{1}]".format(ctrlShape, pntCount - 1)], relative=True
            )

        mc.move(
            valTrans[0], valTrans[1], valTrans[2],
            ["{0}.cv[0:{1}]".format(ctrlShape, pntCount - 1)], objectSpace=True, relative=True
            )

    # Strip underscores in front of increments
    regex = r"_(?=[0-9]+$)"
    oNs = re.sub(regex, "", oNs)

    # Put the template in the control group
    ctrlGroupName = "cg_" + oNs
    if not mc.objExists(ctrlGroupName):
        print 'lib_controlGroup.crtCg(oNs)', str(lib_controlGroup.crtCg(oNs))

    lib_controlGroup.addTplsToCg([loc], ctrlGroupName)

    # tweak template control group attributes
    mc.setAttr(loc + ".isMirrored", False)
    mc.setAttr(loc + ".location", 0)

    return {"tpl":loc, "ns":oNs, "pos":oPos, "rot":oRt, "ro":oRotOrder, "cg":ctrlGroupName}

