
import maya.cmds as mc
import re
from functools import partial
from itertools import takewhile


def getParentObj(refObj=None):
    if refObj == []:
        lstParent = mc.warning('no object selected')
    else:
        if type(refObj) == type([]):
            refObj =refObj[0]
        lstParent =[]
        while True:
            if mc.listRelatives(refObj,p=True)!= None:
                getParent =mc.listRelatives(refObj,p=True)[0]
                refObj = getParent
                lstParent.append(refObj)
            else:
                break
    return lstParent
#getParentObj(refObj=mc.ls(sl=True))