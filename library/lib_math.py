import maya.cmds as mc
import math as math
from ellipse_rig.library import lib_deformers
reload(lib_deformers)

def getNearestTrans(trs, lObj):
    #DKatz
    nearestObj = lObj[0]
    pivTrs = mc.xform(trs, query=True, rp=True, worldSpace=True)
    initDiff = mc.xform(nearestObj, query=True, t=True, worldSpace=True)
    diff = math.sqrt(pow(pivTrs[0]-initDiff[0], 2)+pow(pivTrs[1]-initDiff[1], 2)+pow(pivTrs[2]-initDiff[2], 2))
    for obj in lObj :
        if mc.objectType(obj, i='nurbsCurve') or mc.objectType(obj, i='nurbsSurface') or mc.objectType(obj, i='mesh'):
            getPiv = mc.xform(obj, q=True, ws=True, t=True)
            if len(getPiv) > 3:
                lPivX = []
                lPivY = []
                lPivZ = []
                x = 0
                y = 1
                z = 2
                for i in range(0, len(getPiv) / 3):
                    lPivX.append(getPiv[x])
                    lPivY.append(getPiv[y])
                    lPivZ.append(getPiv[z])
                    x += 3
                    y += 3
                    z += 3
                pivX = 0
                pivY = 0
                pivZ = 0
                for i in range(0, len(getPiv) / 3):
                    pivX += lPivX[i]
                    pivY += lPivY[i]
                    pivZ += lPivZ[i]
                    pivObj = [pivX / (len(getPiv) / 3), pivY / (len(getPiv) / 3), pivZ / (len(getPiv) / 3)]
            else:
                pivObj = getPiv
        else:
            pivObj = pivObj = mc.xform(obj, q=True, ws=True, rp=True)
        if math.sqrt(pow(pivTrs[0]-pivObj[0], 2)+pow(pivTrs[1]-pivObj[1], 2)+pow(pivTrs[2]-pivObj[2], 2)) < diff :
            diff = math.sqrt(pow(pivTrs[0]-pivObj[0], 2)+pow(pivTrs[1]-pivObj[1], 2)+pow(pivTrs[2]-pivObj[2], 2))
            nearestObj = obj
    return nearestObj

def setRange(oldMin, oldMax, min, max, val):
    # DKatz
    ##be sure to give FLOAT in the arguments values -> 1.0, 3.5, 2.5, 7.0, 6.23)
    newVal = min + ((max - min) * (((val / (oldMax - oldMin)) * 100.0) / 100.0))
    return newVal
# setRange(2.0, 4.0, 3.0, 6.0, 1.0)


def averageVectors(lObj):
    # DKatz
    dicMat = {}
    averagePiv = []
    ratio = len(lObj)
    for obj in lObj:
        if mc.objectType(obj, i='nurbsCurve') or mc.objectType(obj, i='nurbsSurface') or mc.objectType(obj, i='mesh'):
            getPiv = mc.xform(obj, q=True, ws=True, t=True)
            if len(getPiv)>3:
                #ratio += (len(getPiv)/3)-1
                lPivX=[]
                lPivY=[]
                lPivZ=[]
                x = 0
                y = 1
                z = 2
                for i in range(0, len(getPiv)/3):
                    lPivX.append(getPiv[x])
                    lPivY.append(getPiv[y])
                    lPivZ.append(getPiv[z])
                    x += 3
                    y += 3
                    z += 3
                pivX = 0
                pivY = 0
                pivZ = 0
                for i in range(0, len(getPiv)/3):
                    pivX += lPivX[i]
                    pivY += lPivY[i]
                    pivZ += lPivZ[i]
                dicMat[obj] = [pivX/(len(getPiv)/3), pivY/(len(getPiv)/3), pivZ/(len(getPiv)/3)]
            else:
                dicMat[obj] = getPiv
        else:
            dicMat[obj] = mc.xform(obj, q=True, ws=True, rp=True)
        pivX = 0
        pivY = 0
        pivZ = 0
        for obj in  dicMat.keys():
            pivX += dicMat[obj][0]
            pivY += dicMat[obj][1]
            pivZ += dicMat[obj][2]
        averagePiv = [pivX/ratio, pivY/ratio, pivZ/ratio]
    return averagePiv

#averagePiv(mc.ls(sl=True, fl=True))  be sure the list of obj you are guiving is flatten turned on


def getNormal(vecA, vecB, vecC):
    # DKatz
    obj = vecA
    if not isinstance(obj, list):
        mat = mc.xform(obj, query=True, ws=True, matrix=True)
        vecA = [mat[12], mat[13], mat[14]]
    obj = vecB
    if not isinstance(obj, list):
        mat = mc.xform(obj, query=True, ws=True, matrix=True)
        vecB = [mat[12], mat[13], mat[14]]
    obj = vecC
    if not isinstance(obj, list):
        mat = mc.xform(obj, query=True, ws=True, matrix=True)
        vecC = [mat[12], mat[13], mat[14]]
    vAB = [vecB[0] - vecA[0], vecB[1] - vecA[1], vecB[2] - vecA[2]]
    vAC = [vecC[0] - vecA[0], vecC[1] - vecA[1], vecC[2] - vecA[2]]
    vN = [(vAB[1] * vAC[2]) - (vAB[2] * vAC[1]), (vAB[2] * vAC[0]) - (vAB[0] * vAC[2]),
          (vAB[0] * vAC[1]) - (vAB[1] * vAC[0])]
    ##get lenght of vercor vN
    length = math.sqrt(vN[0] * vN[0] + vN[1] * vN[1] + vN[2] * vN[2])
    ##normalize vector vN
    vN = [vN[0] / length, vN[1] / length, vN[2] / length]
    # loc = mc.spaceLocator()[0]
    # mc.xform(loc, ws=True, m=[vAB[0], vAB[1], vAB[2], 0, vAC[0], vAC[1], vAC[2], 0, vN[0], vN[1], vN[2], 0, (vecA[0]+vecB[0]+vecC[0])/3, (vecA[1]+vecB[1]+vecC[1])/3, (vecA[2]+vecB[2]+vecC[2])/3, 1])
    return vN
#getNormal('WORLD:LEG_7:locator1', 'WORLD:LEG_7:joint1', [1, 3, 6])


def getVectorInObjSpace(obj, vec):
    # DKatz
    objInvMat = mc.getAttr(obj + '.inverseMatrix')
    vecInObjSpace = []
    for i in range(0, 3):
        vecInObjSpace.append(
            objInvMat[4 * 0 + i] * vec[0] + objInvMat[4 * 1 + i] * vec[1] + objInvMat[4 * 2 + i] * vec[2] + objInvMat[
                4 * 3 + i] * 1.0)
    return vecInObjSpace


def getBBoxCenter(node):
    bBCenter=[]
    bBMin = mc.getAttr(node+'.boundingBoxMin')
    bBMax = mc.getAttr(node+'.boundingBoxMax')
    bBWorld = mc.exactWorldBoundingBox(node)
    bBCenter.append(setRange(0, 1, bBWorld[0], bBWorld[3], .5))
    bBCenter.append(setRange(0, 1, bBWorld[1], bBWorld[4], .5))
    bBCenter.append(setRange(0, 1, bBWorld[2], bBWorld[5], .5))
    return bBCenter

def compareFloats(refFloat, currentFloat, precision):
    # DKatz
    return math.fabs(refFloat - currentFloat) < precision
# compareFloats(0.5, 0.48952999, 0.000001)

#SYM________________________________________________________
def symMap(obj):
    lib_deformers.activeDef(obj, 0)
    vtxs = mc.polyEvaluate(obj, v=True)
    dicSym = {}
    dicSym['mid'] = []
    dicSym['sided'] = {}
    lVtxTrgt = []
    for i in range(0, vtxs):
        pos = mc.xform(obj+'.vtx['+str(i)+']', q=True, os=True, t=True)
        if compareFloats(0.0, pos[0], 0.000001) == False:
            if pos[0]>0:
                dicSym['sided'][str(i)] = ''
        else:
            dicSym['mid'].append(str(i))
    cPOM = mc.createNode('closestPointOnMesh')
    shp = mc.listRelatives(obj, s=True, ni=True)[0]
    mc.connectAttr(shp+'.outMesh', cPOM+'.inMesh')
    for id in dicSym['sided'].keys():
        poseSrc = mc.xform(obj+'.vtx['+id+']', q=True, os=True, t=True)
        poseTrgt = [poseSrc[0]*-1, poseSrc[1], poseSrc[2]]
        mc.setAttr(cPOM+'.inPosition', *poseTrgt)
        idSym = mc.getAttr(cPOM+'.closestVertexIndex')
        dicSym['sided'][id] = str(idSym)
    mc.delete(cPOM)
    lib_deformers.activeDef(obj, 1)
    return dicSym
#symMap(mc.ls(sl=True)[0])

def crtSymAttr(lObj):
    for obj in lObj:
        dicSym = symMap(obj)
        if not mc.attributeQuery('symTabLeft', n=obj, ex=True):
            mc.addAttr(obj, ln='symTabLeft', at='long', multi=True)
            mc.addAttr(obj, ln='symTabRight', at='long', multi=True)
            mc.addAttr(obj, ln='symTabMid', at='long', multi=True)
        inc = 0
        for key in dicSym['sided'].keys():
            vtxL = int(key)
            mc.setAttr(obj+'.symTabLeft['+str(inc)+']', vtxL)
            vtxR = int(dicSym['sided'][key])
            mc.setAttr(obj+'.symTabRight['+str(inc)+']', vtxR)
            inc += 1
        inc = 0
        for vtx in dicSym['mid']:
            vtxMid = int(vtx)
            mc.setAttr(obj+'.symTabMid['+str(inc)+']', vtxMid)
            inc += 1
        if not mc.attributeQuery('symTab', n=obj, ex=True):
            mc.addAttr(obj, ln='symTab', at='bool', dv=1, k=False)
        print 'symTab generated on :', obj

#crtSymAttr(mc.ls(sl=True))


import maya.cmds as mc

def symMap_v2(obj, compType):
    #lib_deformers.activeDef(obj, 0)
    comp = mc.polyEvaluate(obj, v=True)
    compType = 'vtx'
    if compType == 'f':
        comp = mc.polyEvaluate(obj, f=True)
    dicSym = {}
    dicSym['mid'] = []
    dicSym['sided'] = {}
    lVtxTrgt = []
    for i in range(0, comp):
        pos = mc.xform(obj+'.'+compType+'['+str(i)+']', q=True, os=True, t=True)
        if compareFloats(0.0, pos[0], 0.000001) == False:
            if pos[0]>0:
                dicSym['sided'][str(i)] = ''
        else:
            dicSym['mid'].append(str(i))
    cPOM = mc.createNode('closestPointOnMesh')
    shp = mc.listRelatives(obj, s=True, ni=True)[0]
    mc.connectAttr(shp+'.outMesh', cPOM+'.inMesh')
    for id in dicSym['sided'].keys():
        poseSrc = mc.xform(obj+'.'+compType+'['+id+']', q=True, os=True, t=True)
        poseTrgt = [poseSrc[0]*-1, poseSrc[1], poseSrc[2]]
        mc.setAttr(cPOM+'.inPosition', *poseTrgt)
        idSym = mc.getAttr(cPOM+'.closestVertexIndex')
        if compType == 'f':
            idSym = mc.getAttr(cPOM+'.closestFaceIndex')
        dicSym['sided'][id] = str(idSym)
    mc.delete(cPOM)
    #lib_deformers.activeDef(obj, 1)
    return dicSym
#symMap_v2(mc.ls(sl=True)[0], 'vtx')

def crtSymAttr_v2(lObj, compType):
    for obj in lObj:
        dicSym = {}
        if compType == 'vtx':
            dicSym = symMap(obj, 'vtx')
        if compType == 'face':
            dicSym = symMap(obj, 'f')
        if not mc.attributeQuery('symTabLeft'+compType.capitalize(), n=obj, ex=True):
            mc.addAttr(obj, ln='symTabLeft'+compType.capitalize(), at='long', multi=True)
            mc.addAttr(obj, ln='symTabRight'+compType.capitalize(), at='long', multi=True)
            mc.addAttr(obj, ln='symTabMid'+compType.capitalize(), at='long', multi=True)
        inc = 0
        for key in dicSym['sided'].keys():
            vtxL = int(key)
            mc.setAttr(obj+'.symTabLeft'+compType.capitalize()+'['+str(inc)+']', vtxL)
            vtxR = int(dicSym['sided'][key])
            mc.setAttr(obj+'.symTabRight'+compType.capitalize()+'['+str(inc)+']', vtxR)
            inc += 1
        inc = 0
        for vtx in dicSym['mid']:
            vtxMid = int(vtx)
            mc.setAttr(obj+'.symTabMid'+compType.capitalize()+'['+str(inc)+']', vtxMid)
            inc += 1
        if not mc.attributeQuery('symTab', n=obj, ex=True):
            mc.addAttr(obj, ln='symTab', at='bool', dv=1, k=False)
        print 'symTab generated on :', obj

#crtSymAttr_v2(mc.ls(sl=True))



def getNearestCompId_fromMesh(msh, root, compType):
    '''
    :param msh: mesh
    :param cPOM: closestPointOMeshNode
    :param root: transform position reference
    :param compType: type of component you want the id (face, edg, vtx)
    :return: id of the component as a int
    '''
    shp = mc.listRelatives(msh, s=True, ni=True)[0]
    cPOM = mc.createNode('closestPointOnMesh')
    mc.connectAttr(shp+'.outMesh', cPOM+'.inMesh', f=True)


    pos = mc.xform(root, q=True, ws=True, t=True)
    mc.setAttr(cPOM+'.inPosition', *pos)

    if compType == 'face':
        id = mc.getAttr(cPOM+'.closestFaceIndex')
        mc.delete(cPOM)
        return id
    if compType == 'vtx':
        id = mc.getAttr(cPOM+'.closestVertexIndex')
        mc.delete(cPOM)
        return id
    if compType == 'edg':
        id = mc.getAttr(cPOM+'.closestVertexIndex')
        mc.select(cl=True)
        mc.select(msh+'.vtx['+str(id)+']')
        lEdg = mc.ls(mc.polyListComponentConversion(fv=True, te=True), fl=True)
        mc.select(cl=True)
        mc.select(lEdg)
        lVtx = mc.ls(mc.polyListComponentConversion(fe=True, tv=True), fl=True)
        mc.select(cl=True)
        lVtx.remove(msh+'.vtx['+str(id)+']')
        findBro = getNearestTrans(root, lVtx)
        for edg in lEdg:
            mc.select(edg)
            eVtx = mc.ls(mc.polyListComponentConversion(fe=True, tv=True), fl=True)
            mc.select(cl=True)
            if findBro in eVtx:
                id = edg.split('.e[')[-1][:-1]
                mc.delete(cPOM)
                return id
#getNearestCompId_fromMesh('pSphere1', 'tpl_test2', 'edg')

def orderVTxList_nearstToFarrest(lVtx, obj):
    lOrderVtx = []
    while lVtx:
        nearest = getNearestTrans(obj, lVtx)
        lOrderVtx.append(nearest)
        lVtx.remove(nearest)
    return lOrderVtx
#orderVTxList_nearstToFarrest(['pSphere1.vtx[220]', 'pSphere1.vtx[239]', 'pSphere1.vtx[240]', 'pSphere1.vtx[259]'], 'tpl_test4')


def getVtxData(lVtx):
    dicVtxData = {}
    for vtx in lVtx:
        if not vtx in dicVtxData.keys():
            dicVtxData[vtx] = {}

        lAdjEdges = mc.polyInfo(vtx, vertexToEdge=True)[0].split(':')[-1]
        lAdjEdgFaces = mc.polyInfo(vtx, vertexToFace=True)[0].split(':')[-1]

        dicVtxData[vtx]['edges'] = []
        dicVtxData[vtx]['faces'] = []

        for edg in lAdjEdges.split(' ')[: -1]:
            if edg:
                dicVtxData[vtx]['edges'].append(edg)
        for face in lAdjEdgFaces.split(' ')[: -1]:
            if face:
                dicVtxData[vtx]['faces'].append(face)
    return dicVtxData
#getVtxData(mc.ls(sl=True, fl=True))