# coding=utf-8
import sys
import maya.cmds as mc
import maya.mel as mel
import json
import maya.OpenMaya as OpenMaya
import traceback

# WEIGHT TOOLS__________________________________________________________________________________________________________
class CopyPasteWeight:

    valModif =[]

    # COPY SKINNING_________________________________________________________________________________________________________
    def copySkin(*args):
        # get list selection
        lsObj = mc.ls(sl=True)
        # get skinCluster
        skinCls = mc.listConnections(mc.ls(lsObj[0],o=True)[0],t="skinCluster")[0]
        # list vertex
        lsVtx = mc.filterExpand(lsObj,sm=(31,28,36,47,46))
        # joints influences
        lsJntInf = [mc.skinCluster(skinCls,q=True,wi=True) for each in lsVtx]
        # values skinning
        lsValSkin =[[mc.skinPercent(skinCls, lsVtx[i], query=True,t=jt) for jt in jnt] for i, jnt in enumerate(lsJntInf)]
        # zip list
        lsZip = zip(*lsValSkin)
        # concat list
        lsConcat=[sum(each) for each in lsZip]
        # result new skin
        valSkin =[round(float(each/(len(lsValSkin))),5) for each in lsConcat]
        infoSk = zip(lsJntInf[0],valSkin)
        CopyPasteWeight.valModif = infoSk
        return infoSk

    # PASTE SKINNING________________________________________________________________________________________________________
    def pasteSkin(*args):
        # get list selection
        lsObj = mc.ls(sl=True)
        # get skinCluster
        skinCls = mc.listConnections(mc.ls(lsObj[0], o=True)[0], t="skinCluster")[0]
        # list vertex
        lsVtx = mc.filterExpand(lsObj, sm=(31, 28, 36, 47, 46))
        # disable weight normalisation
        mc.setAttr(skinCls + ".normalizeWeights", 0)
        # paste skin values
        for i, eachPoint in enumerate(lsVtx):
            for j, jnt in enumerate(CopyPasteWeight.valModif):
                mc.skinPercent(skinCls, eachPoint, r=False, transformValue=[(jnt[0],jnt[1])])
        # re-Enable weight normalisation
        mc.setAttr(skinCls + ".normalizeWeights", 1)
        mc.skinPercent(skinCls, normalize=True)


# WEIGHT TOOLS__________________________________________________________________________________________________________
inst = CopyPasteWeight()
def weightsTools(*args):
    if mc.window("weightsUi", q=1, exists=1) == True:
        mc.deleteUI("weightsUi")

    mc.window("weightsUi", width=150, height=200, mxb=False, mnb=True)
    mc.columnLayout("weightMainLayout", width=150, height=100, parent="weightsUi")
    mc.text(label="Weights", width=100, height=30, align="center")

    mc.rowLayout("weightBtnLayout", numberOfColumns=2, width=150, height=25, parent="weightsUi")
    copy = CopyPasteWeight
    mc.button("CopyB", width=72, label="Copy", command=inst.copySkin, parent="weightBtnLayout")

    mc.button("PasteB", width=72, label="Paste", command=inst.pasteSkin, parent="weightBtnLayout")
    mc.showWindow("weightsUi")
#weightsTools()


### GET SKIN CLUSTER_____________________________________________________________________________________________
def returnSkinCluster(obj=None):
    ls_shape = mc.listRelatives(obj, shapes=True) or []
    for shape in ls_shape:
        ls_setNode = mc.listConnections(shape, type='objectSet') or []
        for setNode in ls_setNode:
            skin = mc.listConnections(setNode, type='skinCluster') or []
            if skin:
                ls_skin_cluster = list(set(skin))
                skin_cluster = ls_skin_cluster[0]
                return skin_cluster


### GET INFLUENCE JOINT_____________________________________________________________________________________________
def getInfluencingjoints(mesh=None):
    '''returns all the joints that influence the mesh'''
    skinClusterName = returnSkinCluster(obj=mesh)
    if skinClusterName != None:
        jointInfls = mc.skinCluster(skinClusterName, q=True, inf=True)
        return jointInfls


# RESET SKIN JOINT______________________________________________________________________________________________________
def resetSkJnts():
    getInfl = getInfluencingjoints(mesh=mc.ls(sl=True))
    if getInfl != None:
        for joint in getInfl:
            skinClusterPlugs = mc.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
            if skinClusterPlugs:
                for skinClstPlug in skinClusterPlugs:
                    index = skinClstPlug[skinClstPlug.index("[") + 1: -1]
                    skinCluster = skinClstPlug[: skinClstPlug.index(".")]
                    curInvMat = mc.getAttr(joint + ".worldInverseMatrix")
                    mc.setAttr(skinCluster + ".bindPreMatrix[%s]" % index, type="matrix", *curInvMat)
            else:
                mc.warning("no skinCluster attached to %s!" % joint)
    else:
        mc.warning('please select Mesh !!!!')
#resetSkJnts()


# TRANSFERT SKIN JOINT TO JOINT______________________________________________________________________________________________________
def transfJntToJnt(mesh=None,sourceJnt=None,targetJnt=None):
    skin = returnSkinCluster(obj=mesh)
    getInfl = getInfluencingjoints(mesh=mesh)
    [mc.skinCluster(skin, e=True, inf=eachJnt, lw=1) for eachJnt in getInfl]
    mc.skinCluster(skin, edit=True, lw=True, wt=0, ai=targetJnt)
    mc.skinCluster(skin, e=True, inf=targetJnt, lw=0)
    mc.skinCluster(skin, e=True, inf=sourceJnt, lw=0)
    mc.skinCluster(skin, edit=True, selectInfluenceVerts=sourceJnt)
    mc.skinPercent(skin, transformValue=[(sourceJnt, 0), (targetJnt, 1)])
    [mc.skinCluster(skin, e=True, inf=eachJnt, lw=0)for eachJnt in getInfl]
    mc.select(cl=True)
#transfJntToJnt(mesh=mc.ls(sl=True)[0],sourceJnt=mc.ls(sl=True)[1],targetJnt=mc.ls(sl=True)[2])


# TRANSFERT SKIN MESH TO MESH______________________________________________________________________________________________________
def transfSkin(source=None,target=None):
    skin = returnSkinCluster(obj=source)
    shpHis = mc.listHistory(target,lv=3)
    oldSkc = mc.ls(shpHis, typ='skinCluster')
    if oldSkc:
        mc.delete(oldSkc)
    jnt=mc.skinCluster(skin,weightedInfluence=True,q=True)
    newSkc= mc.skinCluster(jnt,target)
    mc.copySkinWeights(ss=skin,ds=newSkc[0],nm=True, surfaceAssociation='closestPoint')
    return newSkc[0]
#transfSkin(source=mc.ls(sl=True)[0],target=mc.ls(sl=True)[1])





# BARYCENTRIC COORDS______________________________________________________________________________________________________

def barycentricCoords(meshSrc, meshTgt, debug=False):
    '''
    For each vert in the target mesh, find the closest point on the source mesh,
    and compute the barycentric weights at that point.

    Args
        meshSrc
        meshTgt

    Return
        weightData      (list of tuples)
    '''

    weightData = []
    dicWeightData = {}
    # source mesh
    try:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(meshSrc)
        meshSrcDagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, meshSrcDagPath)
    except:
        print traceback.format_exc()
        return

    # target mesh
    try:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(meshTgt)
        meshTgtDagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, meshTgtDagPath)
    except:
        print traceback.format_exc()
        return

    # create mesh iterator
    comp = OpenMaya.MObject()
    currentFace = OpenMaya.MItMeshPolygon(meshSrcDagPath, comp)

    # get all points from target mesh
    meshTgtMPointArray = OpenMaya.MPointArray()
    meshTgtMFnMesh = OpenMaya.MFnMesh(meshTgtDagPath)
    meshTgtMFnMesh.getPoints(meshTgtMPointArray, OpenMaya.MSpace.kWorld)

    # create mesh intersector
    matrix = meshSrcDagPath.inclusiveMatrix()
    node = meshSrcDagPath.node()
    intersector = OpenMaya.MMeshIntersector()
    intersector.create(node, matrix)

    # create variables to store the returned data
    pointInfo = OpenMaya.MPointOnMesh()
    uUtil = OpenMaya.MScriptUtil(0.0)
    uPtr = uUtil.asFloatPtr()
    vUtil = OpenMaya.MScriptUtil(0.0)
    vPtr = vUtil.asFloatPtr()
    pointArray = OpenMaya.MPointArray()
    vertIdList = OpenMaya.MIntArray()

    # dummy variable needed in .setIndex()
    dummy = OpenMaya.MScriptUtil()
    dummyIntPtr = dummy.asIntPtr()

    # For each point on the target mesh
    # Find the closest triangle on the source mesh.
    # Get the vertIds and the barycentric coords.
    #

    for i in range(meshTgtMPointArray.length()):
        intersector.getClosestPoint(meshTgtMPointArray[i], pointInfo)
        pointInfo.getBarycentricCoords(uPtr, vPtr)
        u = uUtil.getFloat(uPtr)
        v = vUtil.getFloat(vPtr)

        faceId = pointInfo.faceIndex()
        triangleId = pointInfo.triangleIndex()

        currentFace.setIndex(faceId, dummyIntPtr)
        currentFace.getTriangle(triangleId, pointArray, vertIdList, OpenMaya.MSpace.kWorld)

        weightData.append(((vertIdList[0], vertIdList[1], vertIdList[2]), (u, v, 1 - u - v)))

        closestPoint = pointInfo.getPoint()
        '''
        dicPart['target point:%s'] = (meshTgtMPointArray[i][0], meshTgtMPointArray[i][1], meshTgtMPointArray[i][2])
        dicPart['closest pos on source:'] = (closestPoint.x, closestPoint.y, closestPoint.z)
        dicPart['source face id:'] = faceId
        dicPart['source triangle id:'] = triangleId
        dicPart['source vert ids:'] = vertIdList
        dicPart['source point0:'] = (pointArray[0].x, pointArray[0].y, pointArray[0].z)
        dicPart['source point1:'] = (pointArray[1].x, pointArray[1].y, pointArray[1].z)
        dicPart['source point2:'] = (pointArray[2].x, pointArray[2].y, pointArray[2].z)
        '''
        dicWeightData[i] = weightData[i]

        if debug:
            print  100 * ':'
            print 'target point id:', i
            print ''
            print 'target point:', meshTgtMPointArray[i][0], meshTgtMPointArray[i][1], meshTgtMPointArray[i][2]
            print 'closest pos on source:', closestPoint.x, closestPoint.y, closestPoint.z
            print 'source face id:', faceId
            print 'source triangle id:', triangleId
            print 'source vert ids:', vertIdList
            print 'source point0:', pointArray[0].x, pointArray[0].y, pointArray[0].z
            print 'source point1:', pointArray[1].x, pointArray[1].y, pointArray[1].z
            print 'source point2:', pointArray[2].x, pointArray[2].y, pointArray[2].z
            print ''
            print 'barycentric weights:', u, v, 1 - u - v
            print ''

    return dicWeightData

#sourceShp = mc.listRelatives(mc.ls(sl=True)[0], shapes=True)[0]
#targetshp = mc.listRelatives(mc.ls(sl=True)[1], shapes=True)[0]
#data = barycentricCoords(sourceShp,targetshp, debug=True)
'''
# BARYCENTRIC Skin______________________________________________________________________________________________________
def barycentricSkin(source=mc.ls(sl=True)[0],target=mc.ls(sl=True)[1]):
    # get skincluster to target
    skinClsTarget = transfSkin(source=source,target=target)
    # get values skin to vertex target
    sourceShp = mc.listRelatives(source, shapes=True)[0]
    targetshp = mc.listRelatives(target, shapes=True)[0]
    data = barycentricCoords(sourceShp,targetshp, debug=False)
    print data
    for key,val in data.items():
        #print target+'.vtx[%s]'%key
        skinCls = mc.listConnections(mc.listRelatives(source, shapes=True), type='skinCluster')[0]
        lsVtx = [source+'.vtx[%s]'%id for id in val[0]]
        # joints influences
        lsJntInf = [mc.skinCluster(skinCls,q=True,wi=True) for each in lsVtx]
        # values skinning
        lsValSkin =[[mc.skinPercent(skinCls, lsVtx[i], query=True,t=jt) for jt in jnt] for i, jnt in enumerate(lsJntInf)]
        # zip list
        lsZip = zip(*lsValSkin)
        # concat list
        lsConcat=[sum(each) for each in lsZip]
        # result new skin
        valSkin =[round(float(each/(len(lsValSkin))),5) for each in lsConcat]
        infoSk = zip(lsJntInf[0],valSkin)
        # disable weight normalisation
        mc.setAttr(skinClsTarget + ".normalizeWeights", 0)
        # paste skin values
        for j, jnt in enumerate(infoSk):
            mc.skinPercent(skinClsTarget, target+'.vtx[%s]'%key, r=False, transformValue=[(jnt[0],jnt[1])])
        # re-Enable weight normalisation
        mc.setAttr(skinClsTarget + ".normalizeWeights", 1)
        #mc.skinPercent('%s'%skinClsTarget, normalize=True)

#barycentricSkin()
'''

def barycentricSkin2(source=None,target=None):
    # list Obj vertex
    lsVtxObj = mc.filterExpand(mc.ls(sl=True),sm=(31,28,36,47,46))
    # get joints influences source
    lsJntSkSource = getInfluencingjoints(mesh=source)
    # get if skinCkuster in target
    skClsTarget = returnSkinCluster(obj=target)
    if skClsTarget is None:
        # get skincluster to target
        skClsTarget = mc.skinCluster(lsJntSkSource, target)[0]
    else:
        # get joints influences target
        lsJntSkTarget = mc.skinCluster(skClsTarget, q=True, inf=True)
        # compare lsJntSource by lsJntTarget
        setSource = set(lsJntSkSource)
        setTarget = set(lsJntSkTarget)
        lsDiffSkCls = list(setSource.union(setTarget)- setSource.intersection(setTarget))
        # get skincluster to target
        [mc.skinCluster(skClsTarget, edit=True,lw=True,wt=0, ai=each) for each in lsDiffSkCls]
        [mc.setAttr(each + '.liw',0) for each in lsDiffSkCls]

    sourceShp = mc.listRelatives(source, shapes=True)[0]
    targetshp = mc.listRelatives(target, shapes=True)[0]
    data = barycentricCoords(sourceShp,targetshp, debug=False)
    skinCls = mc.listConnections(mc.listRelatives(source, shapes=True), type='skinCluster')[0]

    lsInfoSk = []
    lsInfoSkSelVtx = []
    for key,val in data.items():
        lsVtx = [source + '.vtx[%s]' % id for id in val[0]]
        # joints influences
        lsJntInf = [mc.skinCluster(skinCls, q=True, wi=True) for each in lsVtx]
        # values skinning
        lsValSkin = [[mc.skinPercent(skinCls, lsVtx[i], query=True, t=jt) for jt in jnt] for i, jnt in enumerate(lsJntInf)]
        # adjust lsValSkin with barycentrique values
        lsValSkinBary =[[each * val[1][i] for j, each in enumerate(infVtx)]for i, infVtx in enumerate(lsValSkin)]
        # zip list
        lsZip = zip(*lsValSkinBary)
        # concat list
        lsConcat = [sum(each) for each in lsZip]
        infoSk = zip(lsJntInf[0], lsConcat)
        lsInfoSk.append(infoSk)
        if lsVtxObj != None:
            for a, each in enumerate(lsVtxObj):
                if target + '.vtx[%s]' % key == each:
                    lsInfoSkSelVtx.append(infoSk)

    # disable weight normalisation
    mc.setAttr(skClsTarget + ".normalizeWeights", 0)
    # get if vertex selection
    if lsVtxObj != None:
        # apply only selected vertex
        for i ,infoSk in enumerate(lsInfoSkSelVtx):
            # paste skin values
            [mc.skinPercent(skClsTarget, lsVtxObj[i], r=False, tv=[(jnt[0], jnt[1])])for j, jnt in enumerate(infoSk)]
    else:
        # apply all vertex
        for i ,infoSk in enumerate(lsInfoSk):
            # paste skin values
            [mc.skinPercent(skClsTarget, target + '.vtx[%s]' % i, r=False, tv=[(jnt[0], jnt[1])])for j, jnt in enumerate(infoSk)]
    # re-Enable weight normalisation
    mc.setAttr(skClsTarget + ".normalizeWeights", 1)

#barycentricSkin2()

