# coding: utf-8

from ellipse_rig.library import lib_names
from ellipse_rig.library import lib_glossary as gloss
reload(lib_names)
reload(gloss)

import maya.cmds as mc


def connectAxis(driver,slave,pos=True,rot=True,scl=True,rotOrder=True):
    if pos is True:
        mc.connectAttr(driver+'.translate', slave+'.translate', f=True)
    if rot is True:
        mc.connectAttr(driver+'.rotate', slave+'.rotate', f=True)
        mc.connectAttr(driver+'.shear', slave+'.shear', f=True)
    if scl is True:
        mc.connectAttr(driver+'.scale', slave+'.scale', f=True)
    if rotOrder is True:
        mc.connectAttr(driver+'.rotateOrder', slave+'.rotateOrder', f=True)

def connectMatrixAxis(driver=None,slave=None):
    splitName = driver.split("_")
    nodeMatrix = gloss.renameSplit(selObj=driver, namePart=[splitName[0]], newNamePart=[gloss.lexicon('dM')])
    Matrix = mc.createNode("decomposeMatrix", n=nodeMatrix)
    mc.connectAttr(driver + ".worldMatrix[0]", (Matrix + ".inputMatrix"))
    mc.connectAttr(Matrix + ".outputTranslate", (slave + ".translate"))
    mc.connectAttr(Matrix + ".outputRotate", (slave + ".rotate"))
    mc.connectAttr(Matrix + ".outputScale", (slave + ".scale"))
    mc.connectAttr(Matrix + ".outputShear", (slave + ".shear"))


def connectSquash(shpAttr,instanceShpLst=None):
    # adjust attributs
    mc.addAttr(shpAttr, ln="Ubi_Squash", nn="Ubi Squash", at="double", min=-10, max=10, dv=0)
    mc.setAttr(shpAttr + ".Ubi_Squash", e=True, k=True)
    mc.addAttr(shpAttr, ln="Ubi_Low_Bound", nn="Ubi Low Bound", at="double", min=0, max=10, dv=5)
    mc.setAttr(shpAttr + ".Ubi_Low_Bound", e=True, k=True)
    mc.addAttr(shpAttr, ln="Ubi_High_Bound", nn="Ubi High Bound", at="double", min=0, max=10, dv=5)
    mc.setAttr(shpAttr + ".Ubi_High_Bound", e=True, k=True)
    # add Shape attributs with Controls
    for eachShp in instanceShpLst:
        mc.parent(shpAttr, eachShp, s=True, add=True)


def switchConstraints(typeCons1,typeCons2,attrib="",attribType="",nameObj="",name="",side="",inc="",*args,**kwargs):
    # names ###
    nMultMat = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name= name, nSide=side,incP= inc)
    nDblLin = gloss.name_format(prefix=gloss.lexicon('dblLin'),name= name, nSide=side,incP= inc)
    nAddDblLin = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name= name, nSide=side,incP= inc)
    # get Connection ###
    createCons1 = typeCons1()
    firstOrientCons = mc.listConnections(mc.listRelatives(nameObj, type="constraint")[0] + ".target", p=True)[-1]
    createCons2 = typeCons2()
    secondOrientCons = mc.listConnections(mc.listRelatives(nameObj, type="constraint")[0] + ".target", p=True)[-1]
    # create nodes for switch constraint orient ###
    NodeMultDiv = mc.createNode("multiplyDivide", n=nMultMat)
    mc.setAttr(NodeMultDiv + ".operation", 2)
    mc.setAttr(NodeMultDiv + ".input2X", 10)
    NodeMultDblLinear = mc.createNode("multDoubleLinear", n=nDblLin)
    mc.setAttr(NodeMultDblLinear + ".input2", -1)
    NodeAddDblLinear = mc.createNode("addDoubleLinear", n=nAddDblLin)
    mc.setAttr(NodeAddDblLinear + ".input2", 1)
    # connect ###
    mc.connectAttr("%s.%s" % (attrib, attribType), "%s.input1X" % (NodeMultDiv), force=True)
    mc.connectAttr("%s.outputX" % (NodeMultDiv), "%s" % (firstOrientCons), force=True)
    mc.connectAttr("%s" % (firstOrientCons), "%s.input1" % (NodeMultDblLinear), force=True)
    mc.connectAttr("%s.output" % (NodeMultDblLinear), "%s.input1" % (NodeAddDblLinear), force=True)
    mc.connectAttr("%s.output" % (NodeAddDblLinear), "%s" % (secondOrientCons), force=True)



def surfAttach(selObj=None, lNumb=None, fixPosU=False, fixPosV=True, parentInSA=False, parentSA=None, delKnot=None, nameRef=None):
    # Select the NURBS and the OBJECTS to attached
    # Find nurbs surface
    lSlave = [];
    nbs = ''
    for obj in selObj:
        lShp = mc.listRelatives(obj, shapes=True) or []
        for shp in lShp:
            if mc.nodeType(shp) == 'nurbsSurface':
                nbs = obj
                # get max Range in loft ###
                valmaxU = (mc.getAttr(nbs + ".minMaxRangeU"))[0][1]
                valmaxV = (mc.getAttr(nbs + ".minMaxRangeV"))[0][1]
        if nbs == '':
            lSlave.append(obj)
    if lNumb != None:
        if delKnot is True:
            lNumb +=2
        lSlave = []
        for each in range(lNumb):
            lSlave.append(each)
        parentInSA = False
    if nbs == '':
        mc.warning('please select nurbs')
    else:
        dicConnect ={}
        lSa = []
        lLoc = []
        for i in lSlave:
            if delKnot is True:
                val = i
            else:
                val = i+1
            # NAMES
            if nameRef != None:
                nRef = nameRef
            else:
                nRef = nbs
            splitObj = nRef.split("_")
            # adjust gloss.lexicon if word tpl in split [0]
            lexSa = gloss.lexicon('tplSa') if "tpl" in splitObj[0] else gloss.lexicon('sa')
            lexLoc = gloss.lexicon('tplUv') if "tpl" in splitObj[0] else gloss.lexicon('UV')
            lexPtOnSurfI = gloss.lexicon('tplPtOnSurfI') if "tpl" in splitObj[0] else gloss.lexicon('ptOnSurfI')
            lexMtxFour = gloss.lexicon('tplMtxFour') if "tpl" in splitObj[0] else gloss.lexicon('mtxFour')
            lexMtxMlt = gloss.lexicon('tplMtxMlt') if "tpl" in splitObj[0] else gloss.lexicon('mtxMlt')
            lexMtxDcp = gloss.lexicon('tplMtxDcp') if "tpl" in splitObj[0] else gloss.lexicon('mtxDcp')
            lexClsSurf = gloss.lexicon('tplClsSurf') if "tpl" in splitObj[0] else gloss.lexicon('clsSurf')

            nSa = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexSa,(splitObj[1]+str(val))], reNme=False)
            nPOSI = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexPtOnSurfI,(splitObj[1]+str(val))], reNme=False)
            nFBFMat = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexMtxFour,(splitObj[1]+str(val))], reNme=False)
            nMltMat = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexMtxMlt,(splitObj[1]+str(val))], reNme=False)
            nDMat = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexMtxDcp,(splitObj[1]+str(val))], reNme=False)
            nCPOS = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexClsSurf ,(splitObj[1]+str(val))], reNme=False)
            nLoc = gloss.renameSplit(selObj=nRef, namePart=[splitObj[0],splitObj[1]],
                  newNamePart=[lexLoc,(splitObj[1]+str(val))], reNme=False)

                # CREATE NODE
            sa = mc.createNode('transform', n=nSa)
            pOSI = mc.createNode('pointOnSurfaceInfo', n=nPOSI)
            fBFMat = mc.createNode('fourByFourMatrix', n=nFBFMat)
            mltMat = mc.createNode('multMatrix', n=nMltMat)
            dMat = mc.createNode('decomposeMatrix', n=nDMat)
            cPOS = mc.createNode('closestPointOnSurface', n=nCPOS)

            # CONNECTIONS
            # connect le nurbs to the pOSI
            shp = mc.listRelatives(nbs, s=True)[0]
            mc.connectAttr(shp + '.worldSpace[0]', pOSI + '.inputSurface', f=True)
            # connect le pointOnSurfaceInfo au fourByfourMatrix
            mc.connectAttr(pOSI + '.normalizedNormalX', fBFMat + '.in10', f=True)
            mc.connectAttr(pOSI + '.normalizedNormalY', fBFMat + '.in11', f=True)
            mc.connectAttr(pOSI + '.normalizedNormalZ', fBFMat + '.in12', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentUX', fBFMat + '.in00', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentUY', fBFMat + '.in01', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentUZ', fBFMat + '.in02', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentVX', fBFMat + '.in20', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentVY', fBFMat + '.in21', f=True)
            mc.connectAttr(pOSI + '.normalizedTangentVZ', fBFMat + '.in22', f=True)
            mc.connectAttr(pOSI + '.positionX', fBFMat + '.in30', f=True)
            mc.connectAttr(pOSI + '.positionY', fBFMat + '.in31', f=True)
            mc.connectAttr(pOSI + '.positionZ', fBFMat + '.in32', f=True)
            # connect le fourByfourMatrix au multMatrix
            mc.connectAttr(fBFMat + '.output', mltMat + '.matrixIn[0]', f=True)
            # connect le multMatrix au decomposeMatrix
            mc.connectAttr(mltMat + '.matrixSum', dMat + '.inputMatrix', f=True)
            # connect le null au multMatrix
            mc.connectAttr(sa + '.parentInverseMatrix', mltMat + '.matrixIn[1]', f=True)
            # connect le decomposeMatrix au null
            mc.connectAttr(dMat + '.outputRotate', sa + '.r', f=True)
            mc.connectAttr(dMat + '.outputTranslate', sa + '.t', f=True)

            # LOCATOR
            mc.spaceLocator(n=nLoc)
            mc.setAttr(nLoc+'.visibility',0)
            mc.parent(nLoc, sa)
            mc.setAttr(nLoc + '.t', 0, 0, 0)
            mc.setAttr(nLoc + '.r', 0, 0, 0)
            mc.addAttr(nLoc, ln='U', at='double', dv=0.5)
            mc.setAttr(nLoc + '.U', e=True, keyable=True)
            mc.addAttr(nLoc, ln='V', at='double', dv=0.5)
            mc.setAttr(nLoc + '.V', e=True, keyable=True)
            mc.connectAttr(nLoc + '.U', pOSI + '.parameterU', f=True)
            mc.connectAttr(nLoc + '.V', pOSI + '.parameterV', f=True)

            # CLOSETS POINT ON SURFACE
            mc.createNode('closestPointOnSurface', n=cPOS)
            mc.connectAttr(shp + '.worldSpace[0]', cPOS + '.inputSurface', f=True)
            if type(i) == int:
                if fixPosU == True:
                    spacingU = valmaxU / 2
                else:
                    spacingU = (float(i) / float(lNumb - 1)) * valmaxU
                if fixPosV == True:
                    spacingV = valmaxV / 2
                else:
                    spacingV = (float(i) / float(lNumb - 1)) * valmaxV

                mc.setAttr(nLoc + '.U', spacingU)
                mc.setAttr(nLoc + '.V', spacingV)
            else:
                mc.connectAttr(i + '.t', cPOS + '.inPosition', f=True)
                mc.setAttr(nLoc + '.U', mc.getAttr(cPOS + '.parameterU'))
                mc.setAttr(nLoc + '.V', mc.getAttr(cPOS + '.parameterV'))
                if parentInSA:
                    try:
                        mc.parent(i, sa)
                    except:
                        print i, " can't be parented in ", sa
            mc.delete(cPOS)

            lSa.append(sa)
            lLoc.append(nLoc)
        dicConnect['sa']=lSa
        dicConnect['loc']=lLoc[1:-1]
        if  parentSA!=None:
            for each in lSa:
                mc.parent(each,parentSA)

        if delKnot is True:
            mc.delete(lSa[0])
            mc.delete(lSa[-1])
            del lSa[0]
            del lSa[-1]
        return dicConnect


# surfAttach(selObj=lObj, parentInSA=True) ''' version object select '''
# surfAttach(selObj=lObj, lNumb=7, parentInSA=True) ''' version define number '''


def ConnectCurve(curvLen,tread,numb,count,name,incPart,curveSpline,side,*args):
    # names ###
    nameFourMat = gloss.name_format(prefix=gloss.lexicon('mtxFour'),name=name,nFunc=gloss.lexicon('cv')+str(count+1), nSide=side,incP=incPart)
    nMultMat = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=name,nFunc=gloss.lexicon('cv')+str(count+1), nSide=side,incP=incPart)
    nameDecomptMat = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=name,nFunc=gloss.lexicon('cv')+str(count+1), nSide=side,incP=incPart)
    nameTransfom = gloss.name_format(prefix=gloss.lexicon('trfNod'),name=name,nFunc=gloss.lexicon('cv')+str(count+1), nSide=side,incP=incPart)
    # recup Shape Surface
    shapeCurve = mc.listRelatives(curveSpline, c=True)[0]
    # create ###

    trd_spacing = (tread*count)/curvLen
    #trd_spacing = (curvLen/numb)*count
    # create node poinOnsurfaceInfo ###
    pointOnCurveI = mc.createNode("pointOnCurveInfo", n="posOnCvInf_%s_%s" %(name,incPart))
    # connect shapeSurf and Node poinOnsurfaceInfo ###
    mc.connectAttr((shapeCurve  + ".worldSpace[0]"), (pointOnCurveI + ".inputCurve"))
    fourMatrix = mc.createNode("fourByFourMatrix", n=nameFourMat)
    # connect Node poinOnsurfaceInfo and Node fourByFourMatrix ###
    mc.connectAttr((pointOnCurveI   + ".normalizedTangentX"), (fourMatrix+ ".in00"))
    mc.connectAttr((pointOnCurveI  + ".normalizedTangentY"), (fourMatrix+ ".in01"))
    mc.connectAttr((pointOnCurveI   + ".normalizedTangentZ"), (fourMatrix+ ".in02"))
    mc.connectAttr((pointOnCurveI   + ".normalizedNormalX"), (fourMatrix+ ".in10"))
    mc.connectAttr((pointOnCurveI   + ".normalizedNormalY"), (fourMatrix+ ".in11"))
    mc.connectAttr((pointOnCurveI   + ".normalizedNormalZ"), (fourMatrix+ ".in12"))
    mc.connectAttr((pointOnCurveI  + ".positionX"), (fourMatrix+ ".in30"))
    mc.connectAttr((pointOnCurveI   + ".positionY"), (fourMatrix+ ".in31"))
    mc.connectAttr((pointOnCurveI   + ".positionZ"), (fourMatrix+ ".in32"))
    multMatrix = mc.createNode("multMatrix", n=nMultMat)
    # connect Node fourByFourMatrix and Node fourByFourMatrix(multMatrix) ###
    mc.connectAttr((fourMatrix + ".output"), (multMatrix+ ".matrixIn[0]"))
    decompMatrix = mc.shadingNode("decomposeMatrix", n=nameDecomptMat, asUtility=True)
    # connect Node fourByFourMatrix and Node decomposeMatrix ###
    mc.connectAttr((multMatrix  + ".matrixSum"), (decompMatrix+ ".inputMatrix"))
    # connect Node decomposeMatrix and Node Transform Locator ###
    transformNode = mc.createNode("transform", n=nameTransfom)
    # create Attributs
    createAttribU = mc.addAttr(transformNode,ln="ParameterAlongCurve", at="double", dv=((trd_spacing)))
    mc.setAttr(transformNode+ ".ParameterAlongCurve", e=True, k=True)
    # connect Node decomposeMatrix and Node Transform Locator ###
    mc.connectAttr((decompMatrix + ".outputRotate"), (transformNode+ ".rotate"))
    mc.connectAttr((decompMatrix + ".outputTranslate"), (transformNode+ ".translate"))
    mc.setAttr(pointOnCurveI + ".turnOnPercentage",1)
    mc.connectAttr((transformNode+ ".ParameterAlongCurve"), (pointOnCurveI + ".parameter"))
    # connect expression ###
    valAlongCurve = mc.getAttr(transformNode+ ".ParameterAlongCurve")
    # connect Node Transform Locator and Node multMatrix ###
    mc.connectAttr((transformNode+ ".parentInverseMatrix[0]"), (multMatrix + ".matrixIn[1]"))
    return transformNode,pointOnCurveI,valAlongCurve


def nurbs_attach(lsObj =None,parentInSA=False,delLoc=False,parentSA=None):
    lObj = lsObj
    # Select the NURBS and the OBJECTS to attached
    # Find nurbs surface
    #nbs = ''
    for obj in lObj:
        lShp = mc.listRelatives(obj, shapes=True) or []
        for shp in lShp:
            if mc.nodeType(shp) == 'nurbsSurface':
                nbs = obj

    lRoot = []
    for i in lObj:
        if not nbs in i:
            lRoot.append(i)
    lsSa =[]
    for i in lRoot:
        # NAMES
        ## Split NameSpace
        iNoNS = i.split(':')[-1]
        nSa = iNoNS.replace(iNoNS.split('_')[0], 'sa')
        nPOSI = iNoNS.replace(iNoNS.split('_')[0], 'pOSI')
        nFBFMat = iNoNS.replace(iNoNS.split('_')[0], 'fBfM')
        nMltMat = iNoNS.replace(iNoNS.split('_')[0], 'mltM')
        nDMat = iNoNS.replace(iNoNS.split('_')[0], 'dM')
        nCPOS = iNoNS.replace(iNoNS.split('_')[0], 'cPOS')
        nLoc = iNoNS.replace(iNoNS.split('_')[0], 'loc')
        # CREATE NODE
        sa = mc.createNode('transform', n=nSa)
        pOSI = mc.createNode('pointOnSurfaceInfo', n=nPOSI)
        fBFMat = mc.createNode('fourByFourMatrix', n=nFBFMat)
        mltMat = mc.createNode('multMatrix', n=nMltMat)
        dMat = mc.createNode('decomposeMatrix', n=nDMat)
        cPOS = mc.createNode('closestPointOnSurface', n=nCPOS)

        # CONNECTIONS
        # connect le nurbs to the pOSI
        shp = mc.listRelatives(nbs, s=True)[0]
        mc.connectAttr(shp + '.worldSpace[0]', pOSI + '.inputSurface', f=True)
        # connect le pointOnSurfaceInfo au fourByfourMatrix
        mc.connectAttr(pOSI + '.normalizedNormalX', fBFMat + '.in10', f=True)
        mc.connectAttr(pOSI + '.normalizedNormalY', fBFMat + '.in11', f=True)
        mc.connectAttr(pOSI + '.normalizedNormalZ', fBFMat + '.in12', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUX', fBFMat + '.in00', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUY', fBFMat + '.in01', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUZ', fBFMat + '.in02', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVX', fBFMat + '.in20', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVY', fBFMat + '.in21', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVZ', fBFMat + '.in22', f=True)
        mc.connectAttr(pOSI + '.positionX', fBFMat + '.in30', f=True)
        mc.connectAttr(pOSI + '.positionY', fBFMat + '.in31', f=True)
        mc.connectAttr(pOSI + '.positionZ', fBFMat + '.in32', f=True)
        # connect le fourByfourMatrix au multMatrix
        mc.connectAttr(fBFMat + '.output', mltMat + '.matrixIn[0]', f=True)
        # connect le multMatrix au decomposeMatrix
        mc.connectAttr(mltMat + '.matrixSum', dMat + '.inputMatrix', f=True)
        # connect le null au multMatrix
        mc.connectAttr(sa + '.parentInverseMatrix', mltMat + '.matrixIn[1]', f=True)
        # connect le decomposeMatrix au null
        mc.connectAttr(dMat + '.outputRotate', sa + '.r', f=True)
        mc.connectAttr(dMat + '.outputTranslate', sa + '.t', f=True)

        # LOCATOR
        mc.spaceLocator(n=nLoc)
        mc.parent(nLoc, sa)
        mc.setAttr(nLoc + '.t', 0, 0, 0)
        mc.setAttr(nLoc + '.r', 0, 0, 0)
        mc.addAttr(nLoc, ln='U', at='double', dv=0.5)
        mc.setAttr(nLoc + '.U', e=True, keyable=True)

        mc.addAttr(nLoc, ln='V', at='double', dv=0.5)
        mc.setAttr(nLoc + '.V', e=True, keyable=True)

        mc.connectAttr(nLoc + '.U', pOSI + '.parameterU', f=True)
        mc.connectAttr(nLoc + '.V', pOSI + '.parameterV', f=True)

        # CLOSETS POINT ON SURFACE
        mc.createNode('closestPointOnSurface', n=cPOS)
        mc.connectAttr(shp + '.worldSpace[0]', cPOS + '.inputSurface', f=True)
        mc.connectAttr(i + '.t', cPOS + '.inPosition', f=True)
        mc.connectAttr(cPOS + '.parameterU', nLoc + '.U', f=True)
        mc.connectAttr(cPOS + '.parameterV', nLoc + '.V', f=True)
        mc.disconnectAttr(cPOS + '.parameterU', nLoc + '.U')
        mc.disconnectAttr(cPOS + '.parameterV', nLoc + '.V')
        mc.delete(cPOS)

        if parentInSA:
            try:
                mc.parent(i, sa)
            except:
                print i, " can't be parented in ", sa

        if parentSA != None:
                mc.parent(sa, parentSA)


        if delLoc ==True:
            mc.delete(nLoc)

        lsSa.append(sa)
    return lsSa




def expStretch(name, incPart, ctrCog, newNameArclen, curvLen, lsSk, valAttrAdjust, numbJts, shapeAttrib,
                      lsBufJts, recupDistanceDim, valDist, side, *args):
    # NAME___________________________________________________________
    nExpSquashElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="squashElem", nSide=side,incP=incPart)
    nExpStretchElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="stretchElem", nSide=side,incP=incPart)
    nDecomptMat = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=name,nFunc="cog", nSide=side,incP=incPart)
    nMultDivScale = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="scaleGlobal", nSide=side,incP=incPart)
    nMultDivStretch = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="stretch", nSide=side,incP=incPart)
    nMultDivPower = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="power", nSide=side,incP=incPart)
    nMultDivInver = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="inv", nSide=side,incP=incPart)
    # create ###
    decompMatrixCog = mc.createNode("decomposeMatrix", n=nDecomptMat)
    mc.connectAttr((ctrCog + ".worldMatrix[0]"), (decompMatrixCog + ".inputMatrix"))

    multiDivGlobalScale = mc.createNode("multiplyDivide", n=nMultDivScale)
    mc.connectAttr((newNameArclen + ".arcLength"), (multiDivGlobalScale + ".input1X"))
    mc.connectAttr((decompMatrixCog + ".outputScaleY"), (multiDivGlobalScale + ".input2X"))
    mc.setAttr(multiDivGlobalScale + ".operation", 2)

    multiDiv = mc.createNode("multiplyDivide", n=nMultDivStretch)
    mc.connectAttr((multiDivGlobalScale + ".outputX"), (multiDiv + ".input1X"))
    mc.setAttr(multiDiv + ".operation", 2)
    mc.setAttr(multiDiv + ".input2X", float(curvLen))

    multiDivStretchPow = mc.createNode("multiplyDivide", n=nMultDivPower)
    mc.setAttr(multiDivStretchPow + ".operation", 3)
    mc.setAttr(multiDivStretchPow + ".input2X", 0.5)
    mc.connectAttr(multiDiv + ".outputX", (multiDivStretchPow + ".input1X"))

    multiDivStretchInvers = mc.createNode("multiplyDivide", n=nMultDivInver)
    mc.setAttr(multiDivStretchInvers + ".operation", 2)
    mc.setAttr(multiDivStretchInvers + ".input1X", 1)
    mc.connectAttr(multiDivStretchPow + ".outputX", (multiDivStretchInvers + ".input2X"))

    valSquash = ""
    for k, each7 in enumerate(lsSk[:-1]):
        valStretchInvers = mc.getAttr("%s.outputX" % (multiDivStretchInvers))
        expressionSliddeScaleX = "$val = float(-(%s" % (k) + "*(float(%s)" % (valAttrAdjust) + "/float(%s))));\n" % (
        numbJts)
        expressionSliddeScaleX2 = "%s" % (expressionSliddeScaleX) + "%s.scaleX" % (
        each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleX") + ";"
        expressionSliddeScaleY2 = "%s.scaleY" % (each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleY") + ";"
        expressionSliddeScaleZ2 = "%s.scaleZ" % (each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleZ") + ";\n\n"
        valSquash += "%s\n%s\n%s" % (expressionSliddeScaleX2, expressionSliddeScaleY2, expressionSliddeScaleZ2)
    mc.expression(s="%s" % (valSquash), n=nExpSquashElem)

    valStretch = ""
    for k, each6 in enumerate(lsBufJts[1:]):
        valTrans = mc.getAttr(each6 + ".translateY")
        expressionEnvTransY = "((((%s.distance" % (recupDistanceDim[k]) + "/%s)" % (
        decompMatrixCog + ".outputScaleY") + "-(%s))" % (str(valDist[k])) + "*$valAttr)" + "+(%s)" % (
        valTrans) + ")*%s" % (decompMatrixCog + ".outputScaleY") + ";"
        expressionEnvScaleConditionY = ("%s.ty = %s" % (each6, expressionEnvTransY))
        valStretch += ("%s\n" % (expressionEnvScaleConditionY))
    mc.expression(s="$valAttr = " + shapeAttrib + ".stretch" + "/%s;\n%s" % (valAttrAdjust, valStretch),
                  n=nExpStretchElem)
    return nDecomptMat





def expStretchSpine(name, incPart, ctrCog, newNameArclen, curvLen, lsSk, valAttrAdjust, numbJts, shapeAttrib,
                      lsBufJts, recupDistanceDim, valDist, side,allSk=False,*args):
    # NAME___________________________________________________________
    nExpSquashElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="squashElem", nSide=side,incP=incPart)
    nExpStretchElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="stretchElem", nSide=side,incP=incPart)
    nDecomptMat = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=name,nFunc="cog", nSide=side,incP=incPart)
    nMultDivScale = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="scaleGlobal", nSide=side,incP=incPart)
    nMultDivStretch = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="stretch", nSide=side,incP=incPart)
    nMultDivPower = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="power", nSide=side,incP=incPart)
    nMultDivInver = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="inv", nSide=side,incP=incPart)
    # create ###
    decompMatrixCog = mc.createNode("decomposeMatrix", n=nDecomptMat)
    mc.connectAttr((ctrCog + ".worldMatrix[0]"), (decompMatrixCog + ".inputMatrix"))

    multiDivGlobalScale = mc.createNode("multiplyDivide", n=nMultDivScale)
    mc.connectAttr((newNameArclen + ".arcLength"), (multiDivGlobalScale + ".input1X"))
    mc.connectAttr((decompMatrixCog + ".outputScaleY"), (multiDivGlobalScale + ".input2X"))
    mc.setAttr(multiDivGlobalScale + ".operation", 2)

    multiDiv = mc.createNode("multiplyDivide", n=nMultDivStretch)
    mc.connectAttr((multiDivGlobalScale + ".outputX"), (multiDiv + ".input1X"))
    mc.setAttr(multiDiv + ".operation", 2)
    mc.setAttr(multiDiv + ".input2X", float(curvLen))

    multiDivStretchPow = mc.createNode("multiplyDivide", n=nMultDivPower)
    mc.setAttr(multiDivStretchPow + ".operation", 3)
    mc.setAttr(multiDivStretchPow + ".input2X", 0.5)
    mc.connectAttr(multiDiv + ".outputX", (multiDivStretchPow + ".input1X"))

    multiDivStretchInvers = mc.createNode("multiplyDivide", n=nMultDivInver)
    mc.setAttr(multiDivStretchInvers + ".operation", 2)
    mc.setAttr(multiDivStretchInvers + ".input1X", 1)
    mc.connectAttr(multiDivStretchPow + ".outputX", (multiDivStretchInvers + ".input2X"))

    valSquash = "// STRETCH;\n" \
                         + "float $x =" + shapeAttrib + ".slide" + ";\n" \
                         + "float $f =" + shapeAttrib + ".frequency" + ";\n" \
                         + "float $a =" + shapeAttrib + ".squash" + ";\n" \
                         + "float $v =" + shapeAttrib + ".averageValue" + ";\n" \
                         + "float $FOA =" + shapeAttrib + ".fallOffA" + ";\n" \
                         + "float $FOB=" + shapeAttrib + ".fallOffB" + ";\n\n"

    if allSk is False:
        listSk = lsSk[:-1]
    else:
        listSk = lsSk

    for k, each in enumerate(listSk):
        valSquash += "%s.scaleX" % (each) + "=" + "(((clamp(0,$a,$FOA+%s"%(int(numbJts)-k)+"))-$a)" \
                     "*((clamp(0,$a,$FOB-%s"%(int(numbJts)-k)+"))-$a)*sin($x+(%s)"%(k+1)+"/$f)+$v)" \
                     "*(%s.outputX-1)"%(multiDivStretchInvers)+"*(%s.outputX)"%(multiDivStretchInvers)+"+(1*%s.outputScaleX)"%decompMatrixCog+";\n"

        valSquash += "%s.scaleZ" % (each) + "=" + "(((clamp(0,$a,$FOA+%s"%(int(numbJts)-k)+"))-$a)" \
                     "*((clamp(0,$a,$FOB-%s"%(int(numbJts)-k)+"))-$a)*sin($x+(%s)"%(k+1)+"/$f)+$v)" \
                     "*(%s.outputX-1)"%(multiDivStretchInvers)+"*(%s.outputX)"%(multiDivStretchInvers)+"+(1*%s.outputScaleZ)"%decompMatrixCog+";\n"
    mc.expression(s="%s" % (valSquash), n=nExpSquashElem)


    valRatio = float(curvLen)/numbJts
    valStretch = ""
    for k, each6 in enumerate(lsBufJts[1:]):
        valTrans = mc.getAttr(each6 + ".translateY")
        expressionEnvTransY = "((((%s.distance" % (recupDistanceDim[k]) + "/%s)" % (
        #decompMatrixCog + ".outputScaleY") + "-(%s))" % (str(valDist[k])) + "*$valAttr)" + "+(%s)" % (
        decompMatrixCog + ".outputScaleY") + "-(%s))" % (valRatio) + "*$valAttr)" + "+(%s)" % (
        valRatio) + ")*%s" % (decompMatrixCog + ".outputScaleY") + ";"
        expressionEnvScaleConditionY = ("%s.ty = %s" % (each6, expressionEnvTransY))
        valStretch += ("%s\n" % (expressionEnvScaleConditionY))
    mc.expression(s="$valAttr = " + shapeAttrib + ".stretch" + "/%s;\n%s" % (valAttrAdjust, valStretch),
                  n=nExpStretchElem)
    return nDecomptMat

def expSin(name, incPart, ctrCog, newNameArclen, curvLen, lsSk, valAttrAdjust, numbJts, shapeAttrib,
                      lsBufJts, recupDistanceDim, valDist, side, *args):

    print lsSk
    print numbJts
    # NAME___________________________________________________________
    nExpSinElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="sinElem", nSide=side,incP=incPart)
    # create ###
    valSin = "// SIN;\n" \
                         + "float $x =" + shapeAttrib + ".distanceSide" + ";\n" \
                         + "float $f =" + shapeAttrib + ".frequencySide" + ";\n" \
                         + "float $a =" + shapeAttrib + ".amplitudeSide" + ";\n" \
                         + "float $FOA =" + shapeAttrib + ".fallOffSideA" + ";\n" \
                         + "float $FOB=" + shapeAttrib + ".fallOffSideB" + ";\n"\
                         + "float $x2 =" + shapeAttrib + ".distanceFtBk" + ";\n" \
                         + "float $f2 =" + shapeAttrib + ".frequencyFtBk" + ";\n" \
                         + "float $a2 =" + shapeAttrib + ".amplitudeFtBk" + ";\n" \
                         + "float $FOA2 =" + shapeAttrib + ".fallOffFtBkA" + ";\n" \
                         + "float $FOB2=" + shapeAttrib + ".fallOffFtBkB" + ";\n\n"
    for k, each in enumerate(lsSk):
        valSin += "%s.translateX" % (each) + "=" + "(((clamp(0,$a,$FOA+%s"%(int(numbJts)-k)+"))-$a)" \
                     "*((clamp(0,$a,$FOB-%s"%(int(numbJts)-k)+"))-$a)*sin($x+(%s)"%(k+1)+"/$f))"+";\n"
        valSin += "%s.translateZ" % (each) + "=" + "(((clamp(0,$a2,$FOA2+%s"%(int(numbJts)-k)+"))-$a2)" \
                     "*((clamp(0,$a2,$FOB2-%s"%(int(numbJts)-k)+"))-$a2)*sin($x2+(%s)"%(k+1)+"/$f2))"+";\n"
    mc.expression(s="%s" % (valSin), n=nExpSinElem)
    return nExpSinElem



def expSinSnake(name=None, incPart=None,lsSk=None,numbJts=None, shapeAttrib=None,side=None,axis='Y', *args):
    # NAME___________________________________________________________
    nExpSinElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="sinElem", nSide=side,incP=incPart)
    # create ###
    valSin = "// SIN;\n" \
                         + "float $x =" + shapeAttrib + ".distanceSide"+"*" + shapeAttrib + ".distanceSpeed" + ";\n" \
                         + "float $f =" + shapeAttrib + ".frequencySide" + ";\n" \
                         + "float $a =" + shapeAttrib + ".amplitudeSide" + ";\n" \
                         + "float $FOA =" + shapeAttrib + ".fallOffSideA" + ";\n" \
                         + "float $FOB=" + shapeAttrib + ".fallOffSideB" + ";\n"
    for k, each in enumerate(lsSk):
        valSin += "%s.translate%s" % (each,axis) + "=" + "(((clamp(0,$a,$FOA+%s"%(int(numbJts)-k)+"))-$a)" \
                     "*((clamp(0,$a,$FOB-%s"%(int(numbJts)-k)+"))-$a)*sin($x+(%s)"%(k+1)+"/$f))"+";\n"
    mc.expression(s="%s" % (valSin), n=nExpSinElem)
    return nExpSinElem





def expStretchTail(name, incPart, ctrCog, newNameArclen, curvLen, lsSk, valAttrAdjust, numbJts, shapeAttrib,
                      lsBufJts, recupDistanceDim, valDist, side, *args):
    # NAME___________________________________________________________
    nExpSquashElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="squashElem", nSide=side,incP=incPart)
    nExpStretchElem = gloss.name_format(prefix=gloss.lexicon('exp'),name=name,nFunc="stretchElem", nSide=side,incP=incPart)
    nDecomptMat = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=name,nFunc="cog", nSide=side,incP=incPart)
    nMultDivScale = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="scaleGlobal", nSide=side,incP=incPart)
    nMultDivStretch = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="stretch", nSide=side,incP=incPart)
    nMultDivPower = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="power", nSide=side,incP=incPart)
    nMultDivInver = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=name,nFunc="inv", nSide=side,incP=incPart)
    # create ###
    decompMatrixCog = mc.createNode("decomposeMatrix", n=nDecomptMat)
    mc.connectAttr((ctrCog + ".worldMatrix[0]"), (decompMatrixCog + ".inputMatrix"))

    multiDivGlobalScale = mc.createNode("multiplyDivide", n=nMultDivScale)
    mc.connectAttr((newNameArclen + ".arcLength"), (multiDivGlobalScale + ".input1X"))
    mc.connectAttr((decompMatrixCog + ".outputScaleY"), (multiDivGlobalScale + ".input2X"))
    mc.setAttr(multiDivGlobalScale + ".operation", 2)

    multiDiv = mc.createNode("multiplyDivide", n=nMultDivStretch)
    mc.connectAttr((multiDivGlobalScale + ".outputX"), (multiDiv + ".input1X"))
    mc.setAttr(multiDiv + ".operation", 2)
    mc.setAttr(multiDiv + ".input2X", float(curvLen))

    multiDivStretchPow = mc.createNode("multiplyDivide", n=nMultDivPower)
    mc.setAttr(multiDivStretchPow + ".operation", 3)
    mc.setAttr(multiDivStretchPow + ".input2X", 0.5)
    mc.connectAttr(multiDiv + ".outputX", (multiDivStretchPow + ".input1X"))

    multiDivStretchInvers = mc.createNode("multiplyDivide", n=nMultDivInver)
    mc.setAttr(multiDivStretchInvers + ".operation", 2)
    mc.setAttr(multiDivStretchInvers + ".input1X", 1)
    mc.connectAttr(multiDivStretchPow + ".outputX", (multiDivStretchInvers + ".input2X"))

    valSquash = ""
    for k, each7 in enumerate(lsSk):
        valStretchInvers = mc.getAttr("%s.outputX" % (multiDivStretchInvers))
        expressionSliddeScaleX = "$val = float(-(%s" % (k) + "*(float(%s)" % (valAttrAdjust) + "/float(%s))));\n" % (
        numbJts)
        expressionSliddeScaleX2 = "%s" % (expressionSliddeScaleX) + "%s.scaleX" % (
        each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleX") + ";"
        expressionSliddeScaleY2 = "%s.scaleY" % (each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleY") + ";"
        expressionSliddeScaleZ2 = "%s.scaleZ" % (each7) + "=" + "(" + shapeAttrib + ".squash" + "*(%s.outputX-%s" % (
        multiDivStretchInvers, valStretchInvers) + ")" + "/(1+abs($val+float(%s)))" % (
        shapeAttrib + ".slide") + ")" + "*(%s.outputX" % (multiDivStretchInvers) + ")+(1*%s)" % (
        decompMatrixCog + ".outputScaleZ") + ";\n\n"
        valSquash += "%s\n%s\n%s" % (expressionSliddeScaleX2, expressionSliddeScaleY2, expressionSliddeScaleZ2)
    mc.expression(s="%s" % (valSquash), n=nExpSquashElem)


    '''
    ratio = float(curvLen/numbJts)
    attrib1 = "$valAttr = " + shapeAttrib + ".stretch" + "/%s;\n"% (valAttrAdjust)
    attrib2 = "$valAttr2 = 1-(" + shapeAttrib + ".stretch)" + "/%s;\n"% (valAttrAdjust)
    decMatrixCog = decompMatrixCog + ".outputScaleY"
    valStretch = ""
    for k, each6 in enumerate(lsBufJts[1:]):
        valTrans = mc.getAttr(each6 + ".translateY")
        expressionEnvTransY = "((((%s.arcLength" % (newNameArclen) + "/%s)/%s)*$valAttr)+(%s*$valAttr2))*%s;" % (numbJts,decMatrixCog,ratio,decMatrixCog)
        expressionEnvScaleConditionY = ("%s.ty = %s" % (each6, expressionEnvTransY))
        valStretch += ("%s\n" % (expressionEnvScaleConditionY))
    mc.expression(s="%s%s\n%s" % (attrib1, attrib2,valStretch),n=nExpStretchElem)


    '''
    valStretch = ""
    for k, each6 in enumerate(lsBufJts[1:]):
        valTrans = mc.getAttr(each6 + ".translateY")
        expressionEnvTransY = "((((%s.distance" % (recupDistanceDim[k]) + "/%s)" % (
        decompMatrixCog + ".outputScaleY") + "-(%s))" % (str(valDist[k])) + "*$valAttr)" + "+(%s)" % (
        valTrans) + ")*%s" % (decompMatrixCog + ".outputScaleY") + ";"
        expressionEnvScaleConditionY = ("%s.ty = %s" % (each6, expressionEnvTransY))
        valStretch += ("%s\n" % (expressionEnvScaleConditionY))
    mc.expression(s="$valAttr = " + shapeAttrib + ".stretch" + "/%s;\n%s" % (valAttrAdjust, valStretch),
                  n=nExpStretchElem)


    return nDecomptMat





def expTwist(lsBufJts, valNumbRoot, valNumbEnd, downIK, topIK, name, side, incPart, *args):
    # names ###
    nExpTwistElem = '{}_{}{}_{}'.format(gloss.lexicon('exp'), "TwistElem" + name, side, incPart)
    # expressions ###
    mc.connectAttr((downIK + ".rotateY"), (lsBufJts[0] + ".rotateAxisY"))
    val = ""
    for each in lsBufJts[1:]:
        val += each + ".rotateAxisY" + "=(" + downIK + ".rotateY" + "-(float(%s" % (
        (downIK + ".rotateY")) + "*%s)))" % (valNumbRoot) + "+(float(%s" % ((topIK + ".rotateY")) + "/%s" % (
        valNumbEnd) + "))" + ";\n"
    mc.expression(s="%s" % (val), n=nExpTwistElem)

