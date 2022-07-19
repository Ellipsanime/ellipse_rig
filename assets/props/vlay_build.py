import maya.cmds as mc
from ellipse_rig.library import lib_clean
from ellipse_rig.library import lib_shapes
from ellipse_rig.library import lib_controlGroup
reload(lib_clean)
reload(lib_shapes)
reload(lib_controlGroup)



def genCtrl():
    box = lib_clean.getAllBoxs()[0]
    geo = box.replace(box.split(':')[-1], 'GEO')
    world = lib_shapes.shp_form('square',"Index","yellow",name='WORLD')
    if world.endswith('Shape'):
        world = mc.rename(world, 'WORLD')
    cWalk  = lib_shapes.shp_form('crossArrow',"Index","brown24",name='c_WALK')
    if cWalk.endswith('Shape'):
        cWalk = mc.rename(cWalk, 'c_WALK')
    rootWalk = mc.createNode('transform', n='root_WALK')
    mc.parent(cWalk, rootWalk)
    mc.parent(rootWalk, world)
    mc.parent(world, box)
    bBoxBox = mc.exactWorldBoundingBox(box, calculateExactly=True)
    bBoxWorld = mc.exactWorldBoundingBox(world, calculateExactly=True)
    dif = [bBoxBox[3] - bBoxWorld[3], 0, bBoxBox[5] - bBoxWorld[5]]
    mc.setAttr(world+'.scale', 2+dif[0], 2+dif[1], 2+dif[2])
    mc.makeIdentity(world, a=True)
    mc.parentConstraint(cWalk, geo, mo=True)
    mc.scaleConstraint(cWalk, geo, mo=True)
    lib_controlGroup.addCtrlToCg([world, cWalk], 'cg_all')

def buildPropsVlay():
    path = mc.file(q=True, sceneName=True)
    if not '_vlay_' in path.split(r'/')[-1]:
        return 'this is not a VLAY step'
    else:
        genCtrl()

