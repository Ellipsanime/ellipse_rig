# coding: utf-8

import maya.cmds as mc

from ellipse_rig.library import lib_names
reload(lib_names)


def optionSetAttr(name=None,setAttr=False,**kwargs):
    if setAttr == False:
        setAttr = ""
    else:
        splitName = name.split("_")
        setAttr = lib_names.renameSplit(selObj=name, namePart=[splitName[0]], newNamePart=[lib_names.type_name('set')])
    return setAttr


def createSetProps(target=None, name=None,*args,**kwargs):
    mc.select(cl=True)
    splitName = name.split("_")
    setAttr = lib_names.renameSplit(selObj=name, namePart=[splitName[0]], newNamePart=[lib_names.type_name('set')])
    dicSet = {}
    concatName = setAttr
    if mc.objExists(concatName):
        pass
    else:
        createSet = mc.sets(n=concatName)
    createSetChild = mc.sets(target, edit=True, forceElement=concatName)
    # create set global and concat obj
    if mc.objExists("set"):
        pass
    else:
        createSet = mc.sets(n="set", em=True)
    createSetFather = mc.sets(concatName, edit=True,
                              forceElement="set")
    dicSet['setFather'] = createSetFather
    dicSet['setChild'] = createSetChild
    return dicSet



def createSet(name,setNameType,inc,attribut = "",  *args):
    concatName = attribut + "_" + inc
    nameSetSkin = lib_names.type_name('set') + "_" + setNameType
    setSkin = nameSetSkin
    createSet = concatName
    if mc.objExists(setSkin):
        pass
    else:
        setSkin = mc.sets(n=nameSetSkin, em=True)
    if attribut == "":
        mc.sets(name, edit=True, forceElement=setSkin)
    else:
        if not mc.objExists(createSet):
            createSet = mc.sets(n=concatName)
        mc.sets(name, edit=True, forceElement=createSet)
        mc.sets(createSet, edit=True, forceElement=setSkin)
    return nameSetSkin



def get_all_descendants_set(nameSet, lDescendentsSets=[]):
    lMemberSet = mc.sets(nameSet, nodesOnly=True, query=True) or []
    if not lDescendentsSets:
        lDescendentsSets = []
    for member in lMemberSet:
        if mc.nodeType(member) == 'objectSet':
            lDescendentsSets.append(member)
            get_all_descendants_set(member, lDescendentsSets=lDescendentsSets)
    return lDescendentsSets