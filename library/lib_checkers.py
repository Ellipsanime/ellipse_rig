import maya.cmds as mc
from ellipse_rig.library import lib_math
reload(lib_math)

#VTX MOVE CHECKER###########################################################################################################



def vtxColor(lVtx, col):
    for vtx in lVtx:
        mc.polyColorPerVertex(vtx, cdo=True)
        if col == None:
            mc.polyColorPerVertex(vtx, rem=True, cdo=False)
            chkColSet = mc.polyColorSet(vtx, query=True, allColorSets=True) or []
            if chkColSet:
                mc.polyColorSet(vtx, delete=True)
            polCol = mc.ls(mc.listHistory(vtx), type='polyColorPerVertex') or []
            if polCol:
                mc.delete(polCol)
            polColDel = mc.ls(mc.listHistory(vtx), type='deleteColorSet') or []
            if polColDel:
                mc.delete(polColDel)
        else:
            mc.polyColorPerVertex(vtx, rgb=col)
#vtxColor(mc.ls(sl=True, fl=True), (1.0, 1.0, 0.0))
#vtxColor(mc.ls(sl=True, fl=True), None)




def geMaxDist(mshSrc, mshDest):
    vtxs = mc.polyEvaluate(mshSrc, v=True)
    posMsh = mc.xform(mshSrc, q=True, ws=True, t=True)
    posDest = mc.xform(mshDest, q=True, ws=True, t=True)

    dicDif = {}

    for vtx in range(0, vtxs):
        posVtxW = mc.xform(mshSrc+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        posVtxL = posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]
        posVtxDW = mc.xform(mshDest+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        posVtxDL = posVtxDW[0]-posDest[0], posVtxDW[1]-posDest[1], posVtxDW[2]-posDest[2]

        dif = posVtxDL[0] - posVtxL[0], posVtxDL[1] - posVtxL[1], posVtxDL[2] - posVtxL[2]
        base = 0
        for i in dif:
            if abs(i) > base:
                base = abs(i)
        if base > 0:
            if not base in dicDif.keys():
                dicDif[base] = []
            dicDif[base].append(vtx)
    oldMax = sorted(dicDif.keys())[0]
    oldMin = sorted(dicDif.keys())[-1]
    for key in sorted(dicDif.keys()):
        for i in dicDif[key]:
            val = abs(lib_math.setRange(oldMin, oldMax, 0.0, 1.5, key))
            print val
            mc.polyColorPerVertex(mshDest+'.vtx['+str(i)+']', rgb=(1.0, 1.0-val, 0.0), a=1, cdo=True)
#geMaxDist('pSphere1', 'pSphere3')



def getBsDef(obj, type):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    #_________________#
    lBs = mc.ls(type='blendShape')
    if obj:
        lHist = mc.listHistory(obj)
        lBs = []
        for node in lHist:
            if mc.nodeType(node) == 'blendShape':
                lBs.append(node)
    if type == None:
        return lBs
    else:
        for bs in lBs:
            if mc.attributeQuery('bsType', n=bs, ex=True):
                if mc.getAttr(bs+'.bsType') == type:
                    return [bs]
#getBsDef(mc.ls(sl=True)[0])


def trgtChecker(neutral):
    bs = getBsTrgt(0)[0]
    lTrgt = mc.blendShape(bs, q=True,  t=True)
    dicNeutral = {}
    #mc.setAttr(bs+'.envelope', 0)
    vtxs = mc.polyEvaluate(neutral, v=True)
    posMsh = mc.xform(neutral, q=True, ws=True, t=True)
    for i in range(0, vtxs):
        posVtxW = mc.xform(neutral+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        dicNeutral[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]
    for trgt in lTrgt:
        lVtxWeighted = []
        posTrgt = mc.xform(trgt, q=True, ws=True, t=True)
        for i in range(0, vtxs):
            posVtxW = mc.xform(trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]
            if not posVtxL == dicNeutral[i]:
                if not i in lVtxWeighted:
                    lVtxWeighted.append(i)
        sorted(lVtxWeighted)
        for vtx in lVtxWeighted:
            mc.polyColorPerVertex(trgt+'.vtx['+str(vtx)+']', rgb=(1.0, 0.0, 0.0), a=1, cdo=True)
            #mc.polyColorPerVertex('pSphere1', rem=True)
    mc.setAttr(bs+'.envelope', 1)
#trgtChecker('pSphere1')

############################################################################################################





