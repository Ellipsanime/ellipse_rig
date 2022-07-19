import maya.cmds as mc
import namespace
reload(namespace)


def freezeTrs(lNodes):
    if not lNodes:
        lNodes = mc.ls(type ='transform')
    dicRefs = {}
    lToFreeze = []
    for node in lNodes:
        if not mc.referenceQuery(node, inr=True):
            lToFreeze.append(node)
        else:
            father = mc.listRelatives(node, p=True)[0]
            if not mc.referenceQuery(father, inr=True):
                if not father in dicRefs.keys():
                    dicRefs[father] = []
                dicRefs[father].append(node)
    for refBox in dicRefs.values():
        mc.parent(refBox, world=True)

    for node in lToFreeze:
        mc.makeIdentity(node, a=True)
        if mc.listRelatives(node, s=True):
            if mc.nodeType(mc.listRelatives(node, s=True)[0]) == 'mesh':
                mc.select(cl=True)
                mc.select(node)
                mc.delete(mc.cluster())
                shpToKeep = mc.listRelatives(node, s=True, ni=True)[0]
                mc.delete(shpToKeep, ch=True)
                lShp = mc.listRelatives(node, s=True)
                if lShp:
                    for shp in lShp:
                        if not shp == shpToKeep:
                            if mc.objExists(shp):
                                print shp
                                mc.delete(shp)
                mc.rename(shpToKeep, node+'Shape')

    for father in dicRefs.keys():
        mc.parent(dicRefs[father], father)
#freezeTrs([])