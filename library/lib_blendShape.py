import maya.cmds as mc
import math
from ellipse_rig.library import lib_math
reload(lib_math)


def rerangeVtxOnvectorDir(neutralGeo, trgtGeo, newRoof):
    lVtxId = []
    lMovedVtx = []
    dicNeutGeoVtx = {}
    dicTrgtGeoVtxDif = {}
    dicTrgtGeoVtx = {}
    roof = 0.0

    vtxs = mc.polyEvaluate(neutralGeo, v=True)
    for vtx in range(0, vtxs):
        lVtxId.append(vtx)

    #get neutralGeo transform position
    posSrc = mc.xform(neutralGeo, q=True, ws=True, t=True)
    #get trgtGeo transform position
    postrgtGeo = mc.xform(trgtGeo, q=True, ws=True, t=True)
    duptrgtGeo = mc.duplicate(neutralGeo, n=trgtGeo+'Normalized')[0]
    for vtx in lVtxId:
        posVtx = mc.xform(neutralGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]

    #GET ROOf VAL FOR THE NORMALIZATION
    for vtx in lVtxId:
        #get position of vtx for trgt
        posVtxtrgtGeo = mc.xform(trgtGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        #remove transform pos from vtx pos trgt (set to world 0, 0, 0)
        posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
        #get dif betweeen sourc and trgtGeo vtx
        dif = math.sqrt(((posVtxInneutralGeo[0]-dicNeutGeoVtx[vtx][0])**2)+((posVtxInneutralGeo[1]-dicNeutGeoVtx[vtx][1])**2)+((posVtxInneutralGeo[2]-dicNeutGeoVtx[vtx][2])**2))
        #get roof
        if dif != 0.0:
            lMovedVtx.append(vtx)
            if abs(dif) > roof:
                roof = dif

        dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
        dicTrgtGeoVtxDif[vtx] = dif
    ratio = newRoof/roof

    for vtx in lMovedVtx:
        norm = [0.0, 0.0, 0.0]
        norm[0] = ratio*(dicNeutGeoVtx[vtx][0] - dicTrgtGeoVtx[vtx][0])+dicTrgtGeoVtx[vtx][0]+posSrc[0]
        norm[1] = ratio*(dicNeutGeoVtx[vtx][1] - dicTrgtGeoVtx[vtx][1])+dicTrgtGeoVtx[vtx][1]+posSrc[1]
        norm[2] = ratio*(dicNeutGeoVtx[vtx][2] - dicTrgtGeoVtx[vtx][2])+dicTrgtGeoVtx[vtx][2]+posSrc[2]



        mc.move(norm[0], norm[1], norm[2], duptrgtGeo+'.vtx['+str(vtx)+']')
        #mc.move(norm[0], norm[1], norm[2], trgtGeo+'.vtx['+str(vtx)+']')
    return duptrgtGeo

#rerangeVtxOnvectorDir('msh_headv','mo_smile_L', 1.0)
"""
for trgtGeo in mc.ls(sl=True):
    rerangeVtxOnvectorDir('msh_headBase', trgtGeo, 1)
"""



"""
def normalizeShapes(neutralGeo, trgtGeo, lVtx):
    lVtxId = []
    for vtx in lVtx:
        lVtxId.append(vtx.split('[')[-1][:-1])
    oldMaxX = 0
    oldMaxY = 0
    oldMaxZ = 0
    oldMinX = 0
    oldMinY = 0
    oldMinZ = 0
    dicNeutGeoVtx = {}
    dicTrgtGeoVtxDif = {}
    dicTrgtGeoVtx = {}
    #get neutralGeo transform position
    posSrc = mc.xform(neutralGeo, q=True, ws=True, t=True)
    #get trgtGeo transform position
    postrgtGeo = mc.xform(trgtGeo, q=True, ws=True, t=True)
    duptrgtGeo = mc.duplicate(neutralGeo, n=trgtGeo+'Normalized')[0]
    for vtx in lVtxId:
        posVtx = mc.xform(neutralGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]

    #GET ROOf VAL FOR THE NORMALIZATION
    for vtx in lVtxId:
        #get position of vtx
        posVtxtrgtGeo = mc.xform(trgtGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        #remove transform pos from vtx pos (set to world 0, 0, 0)
        posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
        dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
        #get dif betweeen sourc and trgtGeo vtx
        dif = [posVtxInneutralGeo[0]-dicNeutGeoVtx[vtx][0], posVtxInneutralGeo[1]-dicNeutGeoVtx[vtx][1], posVtxInneutralGeo[2]-dicNeutGeoVtx[vtx][2]]
        dicTrgtGeoVtxDif[vtx] = dif
        if dif[0] > 0:
            if dif[0] > oldMaxX:
                oldMaxX = dif[0]
        elif dif[0] < 0:
            if dif[0] < oldMinX:
                oldMinX = dif[0]

        if dif[1] > 0:
            if dif[1] > oldMaxY:
                oldMaxY = dif[1]
        elif dif[1] < 0:
            if dif[1] < oldMinY:
                oldMinY = dif[1]

        if dif[2] > 0:
            if dif[2] > oldMaxZ:
                oldMaxZ = dif[2]
        elif dif[2] < 0:
            if dif[2] < oldMinZ:
                oldMinZ = dif[2]

    for vtx in lVtxId:
        print vtx
        oldPos = dicTrgtGeoVtx[vtx]
        normPosX = 0
        normPosY = 0
        normPosZ = 0

        #if the X vtx moved
        if dicTrgtGeoVtxDif[vtx][0] != 0:
            #if the vtx move is positive
            if dicTrgtGeoVtxDif[vtx][0] > 0:
                #rerange X from 0 to roof move in 0 to 1+-+
                normPosX = lib_math.setRange(0, oldMaxX, 0, 1, dicTrgtGeoVtxDif[vtx][0])
            #if the vtx move is negative
            elif dicTrgtGeoVtxDif[vtx][0] < 0:
                #rerange X from 0 to floor move in -1 to 0
                normPosX = lib_math.setRange(0, oldMinX, 0, -1, dicTrgtGeoVtxDif[vtx][0])
        #______________________________________________________________________
        #if the Y vtx moved
        if oldPos[1]  - dicNeutGeoVtx[vtx][1] != 0:
            #if the vtx move is positive
            if dicTrgtGeoVtxDif[vtx] > 0:
                #rerange X from 0 to roof move in 0 to 1
                normPosY = lib_math.setRange(0, oldMaxY, 0, 1, dicTrgtGeoVtxDif[vtx][1])
            #if the vtx move is negative
            elif dicTrgtGeoVtxDif[vtx] < 0:
                #rerange X from 0 to floor move in -1 to 0
                normPosY = lib_math.setRange(0, oldMinY, 0, -1, dicTrgtGeoVtxDif[vtx][1])
        #______________________________________________________________________
        #if the Z vtx moved
        if oldPos[2]  - dicNeutGeoVtx[vtx][2] != 0:
            #if the vtx move is positive
            if dicTrgtGeoVtxDif[vtx] > 0:
                #rerange X from 0 to roof move in 0 to 1
                normPosZ = lib_math.setRange(0, oldMaxZ, 0, 1, dicTrgtGeoVtxDif[vtx][2])
            #if the vtx move is negative
            elif dicTrgtGeoVtxDif[vtx] < 0:
                #rerange X from 0 to floor move in -1 to 0
                normPosZ = lib_math.setRange(0, oldMinZ, 0, -1, dicTrgtGeoVtxDif[vtx][2])

        newPosX = normPosX+dicNeutGeoVtx[vtx][0]
        newPosY = normPosY+dicNeutGeoVtx[vtx][1]
        newPosZ = normPosZ+dicNeutGeoVtx[vtx][2]
        mc.move(newPosX, newPosY, newPosZ, duptrgtGeo+'.vtx['+str(vtx)+']')



#normalizeShapes('neutral', 'shp_ball4', mc.ls(sl=True, fl=True))
"""


