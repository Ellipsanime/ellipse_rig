# coding: utf-8

import maya.cmds as mc
import maya.mel as mel
import re
import math
from functools import partial
from ellipse_rig.library import lib_names,lib_rigs,lib_shapes
from ellipse_rig.library import lib_glossary as gloss
reload(lib_names)
reload(lib_rigs)
reload(lib_shapes)
reload(gloss)

### offsetCurve ###
def offsetCrv(crv=None, obj=None, axis=None, offset=None, *args, **kwargs):
    dicAxis = {}
    dicAxis['X'] = 0;
    dicAxis['Z'] = 2
    axis = dicAxis[axis]
    # create tmp joint to adjust crv position
    positions = mc.xform(obj[0], q=True, ws=True, translation=True)
    rotations = mc.xform(obj[0], q=True, ws=True, rotation=True)
    mc.select(cl=True)
    for each in obj:
        if each == obj[-1]:
            splitObj = obj[-1].split("_")
            nCnsAim= gloss.renameSplit(selObj=obj[-1], namePart=[splitObj[0]],newNamePart=["cnsAimTmp"], reNme=False)
            nUpV = gloss.renameSplit(selObj=obj[-1], namePart=[splitObj[0]],newNamePart=["upVTmp"], reNme=False)
            cnsAim = mc.joint(n=nCnsAim, p=positions)
            mc.select(cl=True)
            upV = mc.joint(n=nUpV, p=positions,o=rotations)
            mc.move(0, 0, 2,upV,r=True,os=True,wd=True)
    mc.aimConstraint(obj[-1], cnsAim, aim=(0, -1, 0), u=(0, 0, -1), wut='object', wuo=upV)
    mc.parent(crv, cnsAim)

    lenCrv = len(mc.getAttr(crv + ".cv[*]"))
    for i in range(lenCrv):
        if i == 0:
            piv = mc.xform(obj[i + 1], query=True, matrix=True)
        else:
            piv = mc.xform(obj[i], query=True,matrix=True)
        mc.move((offset * piv[axis * 4 + 0]), (offset * piv[axis * 4 + 1]), (offset * piv[axis * 4 + 2]),
                crv + ".cv[" + str(i) + "]",r=True, ls=True)
    # unparent and delete cnsAim joint
    mc.parent(crv, w=True)
    mc.delete(cnsAim); mc.delete(upV)


########################################################
def createDoubleCrv(objLst=None, axis=None, offset=None, father=None,subDiv=0,subDivKnot=0,degree=1):
    dicCrv ={}
    # get position and rotateOrder of jts ###
    positions = [mc.xform(each, q=True, ws=True, translation=True) for each in objLst]
    ''' names '''
    lCurve =[]
    for val in range(2):
        splitName = objLst[val].split("_")
        nameCrv1=lib_names.renameSplit(selObj=objLst[val], namePart=[splitName[0], splitName[1]], newNamePart=[lib_names.type_name('cv'), splitName[1][:-1]])
        ''' create two curveLinear for surface '''
        curve1 = lib_rigs.createObj(partial(mc.curve, **{'n': nameCrv1, 'p':positions, 'd':1}), refObj=objLst)
        if father != None:
            mc.parent(curve1,father)
        crvSub1= crvSubdivide(crv=nameCrv1, subDiv=subDiv, subDivKnot=subDivKnot, degree=degree)
        lCurve.append(crvSub1)

    offsetCrv(crv =lCurve[-1],obj=objLst,axis= axis, offset=-offset)
    offsetCrv(crv =lCurve[0],obj=objLst,axis= axis, offset=offset)
    dicCrv['crv']= lCurve
    return dicCrv

#sel = mc.ls(sl=True)
#createDoubleCrv(objLst=sel, axis='Z', offset=0.2)


### curve linear ###
def crvSubdivide(crv=None, name=None, subDiv=None,subDivKnot=None, degree=None, *args, **kwargs):
    # get cv on curve
    selShape = mc.listRelatives(crv, s=True)[0]
    recCv = mc.ls(selShape + '.cv[*]', fl=True)
    # numbers cvs between curve adjust because maya it's a big dung
    numbersAdjust = subDiv + 1
    # create tmp curve linear two points
    getPosCvsTmp = []
    getCvTmp = []
    for i, each in enumerate(recCv[:-1]):
        nameCrvTmp = "tmpCv_%s" % (i)
        nameCrv = "crvSubDiv_tmp"
        # create curve linear and adjust points numbers
        listCv = [recCv[i], recCv[i + 1]]
        positions = [mc.xform(each, q=True, ws=True, translation=True) for each in listCv]
        createCrvTmp = mc.curve(n=nameCrvTmp, p=positions, d=1)

        if len(recCv[:-1]) != 1:
            if each == recCv[:-1][1] or each == recCv[-1]:
                if subDivKnot != None:
                    mc.rebuildCurve(s=numbersAdjust +subDivKnot, d=1, n=nameCrvTmp)
                else:
                    mc.rebuildCurve(s=numbersAdjust, d=1, n=nameCrvTmp)
            else:
                mc.rebuildCurve(s=numbersAdjust, d=1, n=nameCrvTmp)
        else:
            mc.rebuildCurve(s=numbersAdjust, d=1, n=nameCrvTmp)

        # get position of curve tmp
        selShapeTmp = mc.listRelatives(nameCrvTmp, s=True)[0]
        recCvTmp = mc.ls(selShapeTmp + '.cv[*]', fl=True)
        getPosTmp = [mc.pointPosition(each) for each in recCvTmp]

        if subDiv == 1:
            if i == len(recCv[:-2]):
                getPos = recCvTmp[0], recCvTmp[2], recCvTmp[-1]
                getPosCvsTmp.extend(getPos)
            else:
                getPos = recCvTmp[0], recCvTmp[2]
                getPosCvsTmp.extend(getPos)
        else:
            if i == len(recCv[:-2]):
                getPos = recCvTmp
                getPosCvsTmp.extend(getPos)
            else:
                getPos = recCvTmp[:-1]
                getPosCvsTmp.extend(getPos)

        getCvTmp.append(createCrvTmp)

    # create new curve ###
    positions = [mc.xform(each, q=True, ws=True, translation=True) for each in getPosCvsTmp]
    mc.curve(n=nameCrv, p=positions, d=1)
    mc.select(cl=True)
    # purge curve tmp ###
    deleteCrvTmp = [mc.delete(each) for each in getCvTmp]
    # adjust degree curve ###
    selShape = mc.listRelatives(nameCrv, s=True)[0]
    recCv = mc.ls(selShape + '.cv[*]', fl=True)
    getPosition = [mc.pointPosition(each) for each in recCv]
    mc.delete(crv)
    cvEnd = mc.curve(n=crv, p=getPosition, d=degree)
    # delete old curve ###
    mc.delete(nameCrv)
    # rename new curve
    return cvEnd
#crvSubdivide(crv="curve1_tmp", subDiv=3,subDivKnot=1, degree=2)
#crvSubdivide(crv="cv_ropeTpl1_1", subdivide=0, addSubdivideKnot=0, degree=1)

def createLoft(name=None,objLst=None,father=None,degree=None,deleteCrv=False,attributs={"visibility": 0}):
    '''
    :param objLst:
    :param father
    :param degree:
    :param deleteCrv:
    :return:
    '''
    if degree is None:
        degree = 3
    ''' create  '''
    loft = lib_rigs.createObj(partial(mc.loft, objLst[0], objLst[1:],
                                      **{'n': name, 'ch':False, 'u':True,'c':0,'ar':1,'d':degree,'ss':0,'rn':0,'po':0,'rsn':True})
                              , father=father, refObj=objLst, incPart=False, attributs=attributs)
    if deleteCrv == True:
        [mc.delete(each) for each in objLst]

    #mc.hide(loft)
    return loft



def weightLoft(nLoft=None,lsSk=None,nbSubDv=None,skinLoft=None):

    # concat points cv by 4 _______________________________
    recCv = mc.ls(nLoft + '.cv[*]', fl=True)
    adjustNumb = 4
    selDiv2 = int(math.ceil(float(len(recCv)) / adjustNumb))
    val = 0
    lsPoint = []
    for each2 in range(selDiv2):
        part = []
        for each in range(adjustNumb):
            part.append(recCv[each + val])
        val += adjustNumb
        lsPoint.append(part)

    # dic to param points _______________________________
    adjustNumb = nbSubDv+2
    selDiv2 = int(math.ceil(float(len(lsPoint))/adjustNumb))
    val = 0
    val2 = 0
    dictPart= {}
    for each2 in range(selDiv2):
        lsPart =[]
        for each in range(adjustNumb):
            lsPart.append(lsPoint[each+val+val2])
        val += adjustNumb
        val2 -=1
        dictPart[each2] = lsPart

    # get values Skin___________________________
    numbByPart = nbSubDv+2
    count = 0
    getVal = []
    for each in range(numbByPart):
        val = round(abs(float(count)/float(numbByPart -1)), 4)
        count += 1
        getVal.append(val)
    invertVal = getVal[::-1]
    # MODIFY SKIN VALUES LOFT CTR_________________________________________________
    for i, each in enumerate(sorted(dictPart.items())):
        for j, eachLigne in enumerate(dictPart.values()[i]):
            for k, eachPoint in enumerate(eachLigne):
                mc.skinPercent(skinLoft[0], eachPoint, r=False, transformValue=[(lsSk[i], invertVal[j]),(lsSk[i+1], getVal[j])])




###################################################################

# coding: utf-8

import maya.cmds as mc

from maya import OpenMaya
#from ump.maya.common import utils as maya_utils
import maya.api.OpenMaya as om



###CURVES
""" OLD
def moveCurveAlongAxis(crv, obj, axis, offset):
    # DKatz
    dicAxis = {}
    dicAxis['X'] = 0;
    dicAxis['Y'] = 1;
    dicAxis['Z'] = 2
    axis = dicAxis[axis]
    piv = mc.xform(obj, query=True, matrix=True)
    for i in range(len(mc.getAttr(crv + ".cv[*]"))):
        mc.move(offset * piv[axis * 4 + 0], offset * piv[axis * 4 + 1], offset * piv[axis * 4 + 2],
                crv + ".cv[" + str(i) + "]", relative=True)
#moveCurveAlongAxis("WORLD:LEG_7:curve1", 'WORLD:LEG_7:locator13', 'Z', 0.015)
"""
def moveCurveAlongAxis(crv, obj, axis, offset):
    # DKatz
    '''

    :param crv: curve
    :param obj: name or list (if listSize = nbr of cvs on the curve the matrix direction will be reevaluate from each obj for each cv)
    :param axis: ax on wich one we want to move the cvs
    :param offset: offset to apply to each cvs
    :return: nothings
    '''
    dicAxis = {}
    dicAxis['X'] = 0
    dicAxis['Y'] = 1
    dicAxis['Z'] = 2
    axis = dicAxis[axis]
    if len(obj) == len(mc.getAttr(crv + ".cv[*]")):
        for i in range(len(mc.getAttr(crv + ".cv[*]"))):
            piv = mc.xform(obj[i], query=True, matrix=True)
            mc.move(offset * piv[axis * 4 + 0], offset * piv[axis * 4 + 1], offset * piv[axis * 4 + 2],
                    crv + ".cv[" + str(i) + "]", relative=True)
    else:
        piv = mc.xform(obj, query=True, matrix=True)
        for i in range(len(mc.getAttr(crv + ".cv[*]"))):
            mc.move(offset * piv[axis * 4 + 0], offset * piv[axis * 4 + 1], offset * piv[axis * 4 + 2],
                    crv + ".cv[" + str(i) + "]", relative=True)

# moveCurveAlongAxis("curve4",'locator1', 'X', 1)
# moveCurveAlongAxis("curve4", mc.ls(sl=True), 'X', 1)


def moveCurveAlongNormal(crv, vec, offset):
    # DKatz
    for i in range(len(mc.getAttr(crv + ".cv[*]"))):
        mc.move(offset * vec[0], offset * vec[1], offset * vec[2], crv + ".cv[" + str(i) + "]", relative=True)
# moveCurveAlong("WORLD:LEG_7:curve1", 'WORLD:LEG_7:locator13', 'Z', 0.015)


def getIndiceFromCv(cv):
    # DKatz
    trunk = cv.split('[')[-1]
    indice = trunk.replace(']', '')
    return int(indice)
#getIndiceFromCv('curve1?cv[7]')

#_______________________________________________________________________________________________________________________
def convToKObject(node):
    lNodes = OM.MSelectionList()
    lNodes.add(node)
    dag = OM.MDagPath()
    mObj = OM.MObject()
    lNodes.getDagPath(0)
    return dag
"""
def getLenFromParam(node, paramU):
    curve_obj = convToKObject(node)
    curve_obj.extendToShapeDirectlyBelow(0)
    curve = OpenMaya.MFnNurbsCurve(curve_obj)
    lengthToU = curve.findLengthFromParam(paramU)
    return lengthToU

#_______________________________________________________________________________________________________________________


def getLength(crvShp, cvEnd, nPOC):
    # DKatz
    ##for OpenMaya
    crv = mc.listRelatives(crvShp, p=True)[0]
    ## return lenght of the curve betweene his cv[0] and the declared cv (cv[end])
    if nPOC == None:
        nPOC = mc.createNode('nearsetPointOnCurve')
    mc.setAttr(nPOC + '.inPosition', *cvEnd)
    paramU = mc.getAttr(nPOC + '.parameter')
    print crv
    curve_obj = convToKObject(crvShp)
    #curve_obj.extendToShapeDirectlyBelow(0)
    curve = OM.MFnNurbsCurve(curve_obj)
    lengthToU = curve.findLengthFromParam(paramU)
    return lengthToU
"""

def getLength(crvShp, cvEnd, nPOC):
    # DKatz
    ## return lenght of the curve betweene his cv[0] and the declared cv (cv[end])
    if nPOC == None:
        nPOC = mc.createNode('nearsetPointOnCurve')
    mc.setAttr(nPOC + '.inPosition', *cvEnd)
    paramU = mc.getAttr(nPOC + '.parameter')

    arcLen  = mc.createNode('arcLengthDimension')
    mc.connectAttr(crvShp+'.worldSpace', arcLen+'.nurbsGeometry')
    mc.setAttr(arcLen+'.uParamValue', paramU)

    lengthToU = mc.getAttr(arcLen+'.arcLength')
    mc.delete(mc.listRelatives(arcLen, p=True)[0])
    return lengthToU

def crvLinear(crv=None, name=None, numbSubdiv=None, smooth=None, *args, **kwargs):
    # get cv on curve
    selShape = mc.listRelatives(crv, s=True)[0]
    recCv = mc.ls(selShape + '.cv[*]', fl=True)
    # numbers cvs between curve adjust because maya it's a big dung
    if numbSubdiv <= 2:
        numbersAdjust = numbSubdiv
    else:
        numbersAdjust = numbSubdiv + 1
    # create tmp curve linear two points
    getPosCvsTmp = []
    getCvTmp = []
    for i, each in enumerate(recCv[:-1]):
        nameCrvTmp = "tmpCv_%s_%s" % (name, i)
        nameCrv = name
        # create curve linear and adjust points numbers
        listCv = [recCv[i], recCv[i + 1]]
        positions = [mc.xform(each, q=True, ws=True, translation=True) for each in listCv]
        createCrvTmp = mc.curve(n=nameCrvTmp, p=positions, d=1)
        mc.rebuildCurve(s=numbersAdjust, d=1, n=nameCrvTmp)
        # get position of curve tmp
        selShapeTmp = mc.listRelatives(nameCrvTmp, s=True)[0]
        recCvTmp = mc.ls(selShapeTmp + '.cv[*]', fl=True)
        getPosTmp = [mc.pointPosition(each) for each in recCvTmp]

        if numbSubdiv == 2:
            if i == len(recCv[:-2]):
                getPos = recCvTmp[0], recCvTmp[2], recCvTmp[4]
                getPosCvsTmp.extend(getPos)
            else:
                getPos = recCvTmp[0], recCvTmp[2]
                getPosCvsTmp.extend(getPos)
        else:
            if i == len(recCv[:-2]):
                getPos = recCvTmp
                getPosCvsTmp.extend(getPos)
            else:
                getPos = recCvTmp[:-1]
                getPosCvsTmp.extend(getPos)
        getCvTmp.append(createCrvTmp)
        # create new curve ###
    positions = [mc.xform(each, q=True, ws=True, translation=True) for each in getPosCvsTmp]
    mc.curve(n=nameCrv, p=positions, d=1)
    mc.select(cl=True)
    # purge curve tmp ###
    deleteCrvTmp = [mc.delete(each) for each in getCvTmp]

    # adjust Smooth curve ###
    selShape = mc.listRelatives(nameCrv, s=True)[0]
    recCv = mc.ls(selShape + '.cv[*]', fl=True)
    getPosition = [mc.pointPosition(each) for each in recCv]
    mc.curve(n="tmp", p=getPosition, d=2)
    # delete old curve ###
    mc.delete(nameCrv)
    # rename new curve
    mc.rename("tmp", nameCrv)




########################################################################################################################
########################################################################################################################
########################################################################################################################

##SURFACES
def name_to_node_api2(name):
    #### convert name to openMayaPython object
    try:
        selectionList = om.MSelectionList()
        selectionList.add(name)
        return selectionList.getDagPath(0)
    except:
        raise RuntimgeError('maya.api.OpenMaya.MDagPath() failed on %s' % name)

def getParamUVFromVec(shp, vec):
    # DKatz
    dicParam = {}
    nbsPath_obj = functionsLib.name_to_node_api2(shp)
    pos = om.MPoint(*vec)
    nbs = om.MFnNurbsSurface(nbsPath_obj)
    (p, u, v) = nbs.closestPoint(pos, None, None, OM.MSpace.kObject)
    dicParam['U'] = u
    dicParam['V'] = v
    return dicParam