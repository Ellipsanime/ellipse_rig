# coding: utf-8

import re
from ellipse_rig.library import lib_names
reload(lib_names)
import maya.cmds as mc


def lockAxis(selObj, trans=False, rot=False, scl=False, axis=('x','y','z'),*args,**kwargs):
    if isinstance(selObj, unicode) or isinstance(selObj, str):
        selObj = [selObj]
    val = True
    for each in selObj:
        # translate
        if trans is True:
            if mc.getAttr(each + ".tx", l=True): val = False
            [mc.setAttr(each + '.t%s' % eachAxis, lock=val) for eachAxis in axis]
        # rotate
        if rot is True:
            if mc.getAttr(each + ".rx", l=True): val = False
            [mc.setAttr(each + '.r%s' % eachAxis, lock=val) for eachAxis in axis]
        # rotate
        if scl is True:
            if mc.getAttr(each + ".sx", l=True): val = False
            [mc.setAttr(each + '.s%s' % eachAxis, lock=val) for eachAxis in axis]

#lockAxis(mc.ls(sl=True), trans=True, rot=False, scl=False, axis=('y','z'))


def lockAndHideAxis(selObj, transVis=False, rotVis=False, sclVis=False,axisT=('x','y','z'),axisR=('x','y','z'),axisS=('x','y','z'),*args,**kwargs):
    if isinstance(selObj, unicode) or isinstance(selObj, str):
        selObj = [selObj]
    for each in selObj:
        if transVis is True:
            if mc.getAttr(each + ".tx", l=True) is False:
                [mc.setAttr(each + '.t%s' % eachAxis, l=True, k=False, ch=False) for eachAxis in axisT]
            else:
                [mc.setAttr(each + '.t%s' % eachAxis, l=False, k=True, ch=True) for eachAxis in axisT]
        if rotVis is True:
            if mc.getAttr(each + ".rx", l=True) is False:
                [mc.setAttr(each + '.r%s' % eachAxis, l=True, k=False, ch=False) for eachAxis in axisR]
            else:
                [mc.setAttr(each + '.r%s' % eachAxis, l=False, k=True, ch=True) for eachAxis in axisR]
        if sclVis is True:
            if mc.getAttr(each + ".sx", l=True) is False:
                [mc.setAttr(each + '.s%s' % eachAxis, l=True, k=False, ch=False) for eachAxis in axisS]
            else:
                [mc.setAttr(each + '.s%s' % eachAxis, l=False, k=True, ch=True) for eachAxis in axisS]

#hideAxis(selObj, transVis=True, rotVis=True, sclVis=False)


def hide_ctrl_hist(selObj=None):
    if type(selObj) is not type([]):
        selObj = [selObj]
    for node in selObj:
        shp = mc.listRelatives(node, s=True)[0]
        defaultAttr =  mc.listAttr(shp,ex=True,k=True,o=True, c=True)
        if defaultAttr is not None: [mc.setAttr(shp+'.%s'%each,k=False,cb=False) for each in defaultAttr]
#hide_ctrl_hist()


def attrUpdateCtr(selObj=None, name=None, side=None):
    val = str(side)
    if side == '': val = 'empty'
    mc.addAttr(selObj, ln='update', at="enum", en="%s:%s" % (name, val), k=True)
    mc.setAttr(selObj + '.update', e=True, cb=True)

def attrSymetrie(selObj=None, nameInfo=None):
        # add attributs symetrie
        update = mc.attributeQuery("update",node=nameInfo, listEnum=1)[0]
        nSym = "empty"
        test = selObj.split("_")
        if update.split(":")[1] == 'L':
            test[-1]='R'
            nSym = "_".join(test)
        elif update.split(":")[1] == 'R':
            test[-1]='L'
            nSym = "_".join(test)

        return nSym

def disconnectAll(node, source=True, destination=True):
    connectPairs = []
    if source:
        conns = mc.listConnections(node, plugs=True, connections=True, destination=False)
        if conns:
            connectPairs.extend(zip(conns[1::2], conns[::2]))
    if destination:
        conns = mc.listConnections(node, plugs=True, connections=True, source=False)
        if conns:
            connectPairs.extend(zip(conns[::2], conns[1::2]))

    for srcAttr, destAttr in connectPairs:
        mc.disconnectAttr(srcAttr, destAttr)

#disconnectAll(node, source=True, destination=True)