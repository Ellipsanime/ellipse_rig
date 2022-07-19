import maya.cmds as mc
import maya.mel as mel
import math
from ellipse_rig.library import lib_namespace as lNspace
reload(lNspace)

from ellipse_rig.library import lib_deformers, lib_pipe, lib_names,lib_namespace, lib_controlGroup, lib_blendShape
reload(lib_deformers)
reload(lib_pipe)
reload(lib_names)
reload(lib_namespace)
reload(lib_controlGroup)
reload(lib_blendShape)

#UTILES#################################################################################################################################################################################
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


def getBsTrgt(type):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    #_________________#
    lBs = mc.ls(type='blendShape')
    for bs in lBs:
        if mc.attributeQuery('bsType', n=bs, ex=True):
            if mc.getAttr(bs+'.bsType') == type:
                return [bs]


def getShdFromShp(shp):
    shdSG=mc.listConnections(shp,type='shadingEngine')[0]
    shd = mc.listConnections(shdSG+'.surfaceShader')[0]
    return shd
#getShdFromShp('neutral_iris_RShape')

def activeDef(shp, val):
    lDef = mc.findDeformers(shp)
    for node in lDef:
        mc.setAttr(node+'.envelope', val)
#activeDef(mc.ls(sl=True), False)

def dupShd(shdSG):
    shd = mc.listConnections(shdSG+'.surfaceShader')[0]
    nDup = shd
    if ':' in shd:
        nDup = shd.split(':')[-1]
    dupShd = nDup
    if not mc.objExists(nDup):
        dupShd = mc.duplicate(shd, n=nDup)[0]
    nDup = shd
    if ':' in shdSG:
        nDup = shdSG.split(':')[-1]
    dupShdSG = nDup
    if not mc.objExists(nDup):
        dupShdSG = mc.duplicate(shdSG, n=nDup)[0]
    #mc.connectAttr(dupShd+'.outColor', dupShdSG+'.surfaceShader')
    return dupShdSG
#dupShd(shdSG)

def crtNspace(obj):
    baseNspace = obj[len(obj.split('_')[0])+1:]
    nspace = baseNspace.upper()
    if not mc.namespace(ex=':' + nspace):
        mc.namespace(add=nspace, parent=':')
    mc.namespace(set=':' + nspace)
    return nspace
#crtNspace('neutral_head')

def getObjNameFromNspace(trgt):
    name = trgt
    if ':' in trgt:
        name = trgt.split(':')[-1]
    return name

def setRange(oldMin, oldMax, min, max, val):
    newVal = min + ((max - min) * (((val / (oldMax - oldMin)) * 100.0) / 100.0))
    return newVal
#setRange(0.0, 2.0, 0.0, 1.0, 1.570)

def bsTypeAttrr(bs, type):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    #_________________#
    mc.addAttr(bs, ln='bsType', at='enum', en='Trgt:Mix:', dv=type)
#bsTypeAttrr(mc.ls(sl=True)[0], 1)

def getActivTrgt(bs):
    dicTrgt = {}
    lTrgt = mc.blendShape(bs, q=True, t=True)
    for trgt in lTrgt:
        if ':' in trgt:
            trgt = trgt.split(':')[-1]
        if mc.attributeQuery(trgt, n=bs, ex=True):
            if not mc.getAttr(bs+'.'+trgt, l=True):
                val = mc.getAttr(bs+'.'+trgt)
                if not val == 0:
                    dicTrgt[trgt] = val
    return dicTrgt
#getActivTrgt(lTrgt)

def cleanShapes(msh):
    lShp = mc.listRelatives(msh, s=True, ni=True)[0]
    lShpInter = mc.listRelatives(msh, s=True)
    lShpInter.remove(lShp)
    mc.delete(lShpInter)
#cleanShapes(mc.ls(sl=True)[0])

def crtGrp(neutral, name):
    nspace = crtNspace(neutral)
    if not mc.objExists(nspace+':'+name):
        grp = mc.createNode('transform', n=name)
        mc.connectAttr(nspace+':geo_targets.v', grp+'.v')

def compareFloats(refFloat, currentFloat, precision):
    return math.fabs(refFloat - currentFloat) < precision
#compareFloats(0.5, 0.48952999, 0.000001)

#UI FONCTIONS#################################################################################################################################################################################
def getTrgt(bs):
    lTrgt = mc.blendShape(bs[0], q=True, t=True)
    return lTrgt
#getTrgt('bs_head')

def loadTrgt(obj):
    mc.textScrollList("targetsList", e=True, ra=True)
    mc.textScrollList("targetsChan", e=True, ra=True)
    lTrgt = getTrgt(getBsDef(obj, None))
    for trgt in lTrgt:
        chan = '//'
        sign = ''
        if not mc.attributeQuery('ctrlChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='ctrlChan', dt='string')
            mc.setAttr(trgt+'.ctrlChan', '//' , type='string')
        chan = mc.getAttr(trgt+'.ctrlChan')
        if chan == '':
            chan = '//'
        if not mc.attributeQuery('negativeChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='negativeChan', at='bool')
        if not chan == '//':
            sign = '+'
        if mc.getAttr(trgt+'.negativeChan') == 1:
            sign = '-'
        mc.textScrollList('targetsList', e=True, a=[trgt])
        mc.textScrollList('targetsChan', e=True, a=[sign+chan[0]+chan[-1]])
#loadTrgt(obj)

def isolateTrgt():
    lTrgt = mc.textScrollList('targetsList', q=True, ai=True)
    allId = mc.textScrollList('targetsList', q=True, ni=True)
    trgtLoad = mc.textScrollList('targetsList', q=True, si=True)
    lId = mc.textScrollList('targetsList', q=True, sii=True)
    for trgt in lTrgt:
        mc.setAttr(trgt+'.v', 0)
    for trgt in trgtLoad:
        mc.setAttr(trgt+'.v', 1)
    #mc.setAttr(geo_neutral+'.v', 0)
    for id in range(1, allId):
        if id in lId:
            mc.textScrollList('targetsList', e=True, lf=[id, 'fixedWidthFont'])
            mc.textScrollList('targetsChan', e=True, lf=[id, 'fixedWidthFont'])
        else:
            mc.textScrollList('targetsList', e=True, lf=[id, 'plainLabelFont'])
            mc.textScrollList('targetsChan', e=True, lf=[id, 'plainLabelFont'])
#isolateTrgt()

def showAllTrgt():
    lTrgt = mc.textScrollList('targetsList', q=True, ai=True)
    for trgt in lTrgt:
        mc.setAttr(trgt+'.v', 1)
#isolateTrgt()

def refreshTrgt():
    nspace = mc.textScrollList('targetsList', q=True, ai=True)[0].split(':')[0]
    neutral = 'neutral_'+nspace.lower()
    loadTrgt(neutral)

def selTrgt():
    lTrgt = mc.textScrollList('targetsList', q=True, si=True)
    mc.select(cl=True)
    mc.select(lTrgt)

def showNeutral():
    lNeutralGrp = mc.ls('*.neutralBox', r=True, o=True)
    val = 1
    lab = 'TRGT'
    if mc.getAttr(lNeutralGrp[0]+'.neutralBox') == 1:
        val = 0
        lab = 'NEUTRAL'
    for neutralGrp in lNeutralGrp:
        lNeutral = mc.listRelatives(neutralGrp, c=True, type='transform')
        for neutral in lNeutral:
            mc.setAttr(neutral+'.v', val)
        mc.setAttr(neutralGrp+'.v', val)
        mc.setAttr(lNeutralGrp[0]+'.neutralBox', val)
    lTrgtGrp = mc.ls('*.trgtBox', r=True, o=True)
    for trgtGrp in lTrgtGrp:
        mc.setAttr(trgtGrp+'.v', 1-val)
        mc.setAttr(trgtGrp+'.trgtBox', 1-val)

    mc.button('switch_neutralTrgt', e=True, l='SHOW '+lab)
#showNeutral()

def loadMOD(pathDir = r'T:\03_FAB\00_ASSETS\MOD\CHR'):
    path = mc.fileDialog2(dir=pathDir, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.file(path, r=True, ns='MOD')
#loadMOD(pathDir = r'T:\90_TEAM_SHARE\03_FAB\00_ASSETS\01_MOD\01_CHARS')

def unloadMOD():
    scenePath = mc.file(q=True, sceneName=True)
    #list les refs dans la scene
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nSpace = mc.referenceQuery(ref, ns=True)
            # si le namespace est MOD, on clean la ref et on remove
            if nSpace == ':MOD':
                lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
                mc.file(ur=refNode)
                if lEdits:
                    for edit in lEdits:
                        action = edit.split('|')[0]
                        mc.file(cr=refNode, editCommand=action)
                mc.file(ref, rr=True)
                print ref, 'removed'
#unloadMOD()

def addTrgt(lNeutral, ctrl):
    if not lNeutral:
        mc.warning('select neutral(s) to add the new target')
        return
    prx = mc.optionMenu('trgtTypes', q=True, v=True).split(':')[-1]
    trgt = mc.textField('newTrgtName', q=True, tx=True)
    if trgt == '':
        mc.warning('enter trgt name')
        return
    attr = mc.textField('newAttrName', q=True, tx=True)
    if attr == '':
        mc.warning('enter attr name')
        return

    valCtrl = 20
    if not mc.attributeQuery(attr, n=ctrl, ex=True):
        mc.addAttr(ctrl, ln=attr, at='float', min=0, max=20, k=True)
    elif mc.attributeQuery(attr, n=ctrl, ex=True):
        min = mc.attributeQuery(attr, n=ctrl, min=True)[0]
        if min == 0.0:
            mc.addAttr(ctrl+'.'+attr, e=True, min=-20)
            valCtrl = -20
        else:
            mc.warning('attribute is already connected in two targets, create a new attribe with an other name')
            return
    for neutral in lNeutral:
        nspace = crtNspace(neutral)
        if mc.objExists(nspace+':'+trgt):
            mc.warning(nspace+':'+trgt, 'skipped, it s already exist')
        else:
            activeDef(neutral, False)
            lNspace.setNspace(nspace)
            newTrgt = mc.duplicate(neutral, n=prx+trgt)[0]
            mc.parent(newTrgt, nspace+':geo_targets')
            lNspace.setNspace('')
            activeDef(neutral, True)

            #####################
            bs = getBsDef(neutral, 0)[0]
            lWght = mc.blendShape(bs, q=True, t=True) or []
            id = 0
            if lWght:
                id = len(lWght)
            chkTrgt = mc.blendShape(bs, q=True, t=True) or []
            if not trgt in chkTrgt:
                mc.blendShape(bs, edit=True, t=(neutral, id, newTrgt, 1.0))
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+attr, itt='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+attr, itt='linear', dv=valCtrl, v=2)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+attr, ott='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+attr, ott='linear', dv=valCtrl, v=2)

            print trgt, 'added to', neutral, 'and connected to', ctrl+'.'+attr

    if mc.window('SMF_addTrgt', ex=True, q=True):
        mc.deleteUI('SMF_addTrgt', window=True)
#addTrgt(mc.ls(sl=True), 'c_targets')

def snapShp(lMsh):
    mshSrc  = lMsh[0]
    mshTrgt = lMsh[1]
    vtxs = mc.polyEvaluate(mshSrc, v=True)
    posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
    posTrgt = mc.xform(mshTrgt, q=True, ws=True, t=True)
    for i in range(0, vtxs):
        pos = mc.xform(mshSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
        trgtPos = [pos[0]- dif[0], pos[1]- dif[1], pos[2]- dif[2]]
        mc.move(trgtPos[0], trgtPos[1], trgtPos[2], mshTrgt+'.vtx['+str(i)+']')
#snapShp(mc.ls(sl=True))

def resetShp(lMsh):
    for msh in lMsh:
        vtxs = mc.polyEvaluate(msh, v=True)
        for i in range(0, vtxs):
            mc.setAttr(msh+'.pnts['+str(i)+']',0, 0, 0)
#resetShp(mc.ls(sl=True))

def dupShp(lMsh):
    for msh in lMsh:
        nspace = ':'
        if ':' in msh:
            nspace = msh.split(':')[:-1][0]
        else:
            crtNspace(msh)
        mc.namespace(set=':' + nspace)
        dupGrp = nspace+':dup_targets'
        if not mc.objExists(dupGrp):
            dupGrp = mc.createNode('transform', n='dup_targets')
        if not mc.attributeQuery('dupList', n=msh, ex=True):
            mc.addAttr(msh, ln='dupList', at='message', multi=True)
        id = mc.getAttr(msh+'.dupList', s=True)
        dupShp = mc.duplicate(msh)[0]
        mc.parent(dupShp, dupGrp)
        mc.connectAttr(dupShp+'.message', msh+'.dupList['+str(id)+']')
        mc.namespace(set=':' + nspace)
#dupShp(mc.ls(sl=True))

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
#trgtChecker('neutral_head')




#EXTRACT SHAPE MIX#################################################################################################################################################################################
def genMixSculpt(lMsh):
    nCorr = 'mix_'
    for msh in lMsh:
        lBs = getBsDef(msh, None)
        bsTrgt = ''
        for bs in lBs:
            if mc.getAttr(bs+'.bsType') == 0:
                bsTrgt = bs

        lTrgt = mc.blendShape(bsTrgt, q=True, t=True)
        dicTrgt = getActivTrgt(bsTrgt)
        for trgt in lTrgt:
            if ':' in trgt:
                trgt = trgt.split(':')[-1]
            if not mc.getAttr(bsTrgt+'.'+trgt, l=True):
                if mc.attributeQuery(trgt, n=bsTrgt, ex=True):
                    val = mc.getAttr(bsTrgt+'.'+trgt)
                    if not val == 0:
                        nCorr = nCorr+trgt.split('_')[-1].capitalize()
        nspace = crtNspace(msh)
        mixShp = mc.duplicate(msh, n=nCorr)[0]
        if not mc.objExists(nspace+':mixSculpt'):
            grp = mc.createNode('transform', n='mixSculpt')
            mc.connectAttr(nspace+':geo_targets.v', grp+'.v')

        for attr in ('translate', 'rotate', 'scale'):
            for chan in ['X', 'Y', 'Z']:
                mc.setAttr(mixShp+'.'+attr+chan, lock=False)
        father = mc.listRelatives(mixShp, p=True) or []
        if father:
            mc.parent(mixShp, nspace+':mixSculpt')
        mc.addAttr(mixShp, ln='trgtList', dt='string', multi=True)
        mc.addAttr(mixShp, ln='trgtValues', at='float', multi=True)
        i = 0
        for key in dicTrgt.keys():
            mc.setAttr(mixShp+'.trgtList['+str(i)+']', key, type='string')
            mc.setAttr(mixShp+'.trgtValues['+str(i)+']', dicTrgt[key])
            i=i+1
        mc.addAttr(mixShp, ln='shpSource', at='message')
        mc.connectAttr(msh+'.message', mixShp+'.shpSource', f=True)
        mc.addAttr(mixShp, ln='shpResult', at='message')
        cleanShapes(mixShp)
        mc.namespace(set=':')
#genMixSculpt(mc.ls(sl=True))


def connectMixCorr(mixTrgt, mshMix, bsMix):
    lTrgt = mc.blendShape(bsMix, q=True, t=True) or []
    id = len(lTrgt)
    if not mixTrgt.split(':')[-1] in lTrgt:
        mc.blendShape(bsMix, e=True, t=(mshMix, id, mixTrgt, 1.0))
#connectMixCorr('shp_neutral_Mix', 'shp_corrective')


def blendMixTrgt(shp, bsTrgt, bsMix):
    shpSrc = mc.listConnections(shp+'.shpSource', d=True)[0]
    shpResult = mc.listConnections(shp+'.shpResult', d=True)[0]

    add = mc.createNode('plusMinusAverage', n='tete')
    mc.setAttr(add+'.operation', 1)
    ran = mc.createNode('setRange', n='smab')
    mc.setAttr(ran+'.maxX', 1)
    mc.setAttr(ran+'.maxY', 1)
    dicMultWght = {}
    for i in range(0, mc.getAttr(shp+'.trgtList', s=True)-1):
        nTrgt = mc.getAttr(shp+'.trgtList['+str(i)+']')
        dicMultWght[i+1] = mc.createNode('multDoubleLinear', n='suce')

    blendWght = mc.createNode('blendColors', n='bld_smab')
    mc.setAttr(blendWght+'.color2', 0, 0, 0, type='double3')
    for i in range(0, mc.getAttr(shp+'.trgtList', s=True)):
        nTrgt = mc.getAttr(shp+'.trgtList['+str(i)+']')
        valTrgt = mc.getAttr(shp+'.trgtValues['+str(i)+']')

        mltd = mc.createNode('multDoubleLinear', n='toto')
        div = mc.createNode('multiplyDivide', n='tata')
        if i < 2:
            mc.connectAttr(bsTrgt+'.'+nTrgt, dicMultWght[1]+'.input'+str(i+1))
        else:
            mc.connectAttr(dicMultWght[i-1]+'.output', dicMultWght[i]+'.input1')
            mc.connectAttr(bsTrgt+'.'+nTrgt, dicMultWght[i]+'.input2')


        mc.setAttr(div+'.operation', 2)
        mc.setAttr(div+'.input2X', 100)

        normVal = setRange(0.0, float(mc.getAttr(shp+'.trgtList', s=True)), 0.0, 1.0, valTrgt)
        ratioVal = (normVal*100)/1
        mc.setAttr(mltd+'.input2', ratioVal)


        mc.connectAttr(bsTrgt+'.'+nTrgt, mltd+'.input1')
        mc.connectAttr(mltd+'.output', div+'.input1X')
        mc.connectAttr(div+'.outputX', add+'.input1D['+str(i)+']')


    val = mc.getAttr(add+'.output1D')
    mc.setAttr(ran+'.oldMaxX', val)
    val = mc.getAttr(dicMultWght[len(dicMultWght)]+'.output')
    mc.setAttr(ran+'.oldMaxY',  val)
    mc.connectAttr(add+'.output1D', ran+'.valueX')
    mc.connectAttr(dicMultWght[len(dicMultWght)]+'.output', ran+'.valueY')
    mc.connectAttr(ran+'.outValueX', blendWght+'.color1R')
    mc.connectAttr(ran+'.outValueY', blendWght+'.blender')
    mc.connectAttr(blendWght+'.outputR', bsMix+'.'+shpResult.split(':')[-1])
#blendMixTrgt(mc.ls(sl=True)[0])


def connectMixShp(lMixSculpt):
    for mixSculpt in lMixSculpt:
        nspace = mixSculpt.split(':')[0]
        if not mc.attributeQuery('shpResult', n=mixSculpt, ex=True):
            mc.addAttr(mixSculpt, ln='shpResult', at='message')
        mshSrc  = mc.listConnections(mixSculpt+'.shpSource', s=True, p=False)[0]
        lBs = getBsDef(mshSrc, None)
        for bs in lBs:
            mc.setAttr(bs+'.envelope', 0)
        mixTrgt = mc.duplicate(mshSrc, n=mixSculpt+'_Mix')[0]
        if not mc.objExists(nspace+':mixTrgt'):
            crtNspace(mshSrc)
            grp = mc.createNode('transform', n='mixTrgt')
            mc.connectAttr(nspace+':geo_targets.v', grp+'.v')
        mc.parent(mixTrgt, nspace+':mixTrgt')
        mc.addAttr(mixTrgt, ln='mixResult', at='bool', dv=1)
        for bs in lBs:
            mc.setAttr(bs+'.envelope', 1)
        mc.connectAttr(mixTrgt+'.message', mixSculpt+'.shpResult', f=True)

        vtxs = mc.polyEvaluate(mshSrc, v=True)

        posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
        posTrgt = mc.xform(mixSculpt, q=True, ws=True, t=True)
        dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
        posDest = mc.xform(mixTrgt, q=True, ws=True, t=True)

        for i in range(0, vtxs):
            posSrcVtx = mc.xform(mshSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posTrgtVtx = mc.xform(mixSculpt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posDestVtx = mc.xform(mixTrgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)

            difSrc = [posSrcVtx[0]-posSrc[0], posSrcVtx[1]-posSrc[1], posSrcVtx[2]-posSrc[2]]
            difTrgt = [posTrgtVtx[0]-posTrgt[0], posTrgtVtx[1]-posTrgt[1], posTrgtVtx[2]-posTrgt[2]]
            difDest = [posDestVtx[0]-posDest[0], posDestVtx[1]-posDest[1], posDestVtx[2]-posDest[2]]

            val = [difSrc[0]-difTrgt[0], difSrc[1]-difTrgt[1], difSrc[2]-difTrgt[2]]
            valDif = [difDest[0]-val[0], difDest[1]-val[1], difDest[2]-val[2]]

            mc.move(valDif[0], valDif[1], valDif[2],  mixTrgt+'.vtx['+str(i)+']', co=True)

        mc.addAttr(mixTrgt, ln='trgtList', dt='string', multi=True)
        mc.addAttr(mixTrgt, ln='trgtValues', at='float', multi=True)

        for i in range(0, mc.getAttr(mixSculpt+'.trgtList', s=True)):
            val = mc.getAttr(mixSculpt+'.trgtList['+str(i)+']')
            mc.setAttr(mixTrgt+'.trgtList['+str(i)+']', val, type='string')
            val = mc.getAttr(mixSculpt+'.trgtValues['+str(i)+']')
            mc.setAttr(mixTrgt+'.trgtValues['+str(i)+']', val)
        bsMix = getBsDef(mshSrc, 2)[0]
        bsTrgt = getBsDef(mshSrc, 0)[0]
        mshMix = mc.blendShape(bsMix, q=True, g=True)[0]

        connectMixCorr(mixTrgt, mshMix, bsMix)
        blendMixTrgt(mixSculpt, bsTrgt, bsMix)
#connectMixShp(mc.ls(sl=True))


#GEN NEUTRAL#################################################################################################################################################################################
def generateNeutral(lObj):
    grp = 'geo_neutral'
    if not mc.objExists('geo_neutral'):
        grp = mc.createNode('transform', n=grp)
        mc.addAttr(grp, ln='neutralBox', at='bool', dv=1)
    for obj in lObj:
        nBase = obj
        if ':' in obj:
            nBase = obj.split(':')[-1]
        nDup  = 'neutral'+nBase[len(nBase.split('_')[0]) :]
        dup = mc.duplicate(obj, n=nDup)[0]
        mc.setAttr(dup+'.v', 1)
        for attr in ['translate', 'rotate', 'scale']:
            for chan in ['X', 'Y', 'Z']:
                mc.setAttr(dup+'.'+attr+chan, lock=False)
        mc.parent(dup, grp)

        shpSrc = mc.listRelatives(obj, s=True, ni=True)[0]
        shdSG = mc.listConnections(shpSrc,type='shadingEngine')[0]
        shd = mc.listConnections(shdSG+'.surfaceShader')[0]

        nDup = ''
        if ':' in shd:
            nDup = shd.split(':')[-1]
        newShd = nDup
        if not mc.objExists(nDup):
            newShd = dupShd(shdSG)
        else:
            newShd = mc.listConnections(nDup,type='shadingEngine')[0]
        #mc.sets(dup, forceElement=newShd)
#generateNeutral(mc.ls(sl=True))


#GEN TARGETS#################################################################################################################################################################################
def genAdd(neutral, bs, type):
    val = 0
    if type == 'cor':
        val = 1
    if type == 'mix':
        val = 2
    nspace = crtNspace(neutral)
    nBase = neutral
    if ':' in neutral:
        nBase = neutral.split(':')[-1]
    nDup  = type+nBase[len(nBase.split('_')[0]) :]
    dup = mc.duplicate(neutral, n=nDup)[0]
    bsAdd = getBsDef(dup, None) or []
    if not bsAdd:
        bsAdd = mc.blendShape(dup, n='bs_'+type)
        mc.addAttr(bsAdd, ln='bsType', at='enum', en='Trgt:Cor:Mix:', dv=val)
    lWght = mc.blendShape(bs, q=True, t=True) or []
    id = 0
    if lWght:
        id = len(lWght)
    chkTrgt = mc.blendShape(bsAdd, q=True, t=True) or []
    if not nDup in chkTrgt:
        mc.blendShape(bs, edit=True, t=(neutral, id, dup, 1.0))
    mc.setAttr(bs+'.'+nDup, 1)
    mc.setAttr(bs+'.'+nDup, l=True)
    return dup
#genAdd(mc.ls(sl=True)[0],['bs_head'], 'cor')

def ctrlAttr(ctrl, dicAttrs, neutral, bs, nspace):
    for attr in dicAttrs.keys():
        if not mc.attributeQuery(attr, n=ctrl, ex=True):
            mn = 0
            if len(dicAttrs[attr]) == 2:
                mn = -20
            mc.addAttr(ctrl, ln=attr, at='float', k=True, min=mn, max=20)
        valCtrl = 20
        for trgt in dicAttrs[attr]:
            if not mc.objExists(nspace+':'+trgt):
                mc.duplicate(neutral, n=trgt)
                mc.parent(nspace+':'+trgt, nspace+':geo_targets')
                presetTplFaceChan(nspace+':'+trgt, trgtToCtrlChan())
            lWght = mc.blendShape(bs, q=True, t=True) or []
            id = 0
            if lWght:
                id = len(lWght)
            chkTrgt = mc.blendShape(bs, q=True, t=True) or []
            if not trgt in chkTrgt:
                mc.blendShape(bs, edit=True, t=(neutral, id, nspace+':'+trgt, 1.0))
            mc.setDrivenKeyframe(bs+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=valCtrl, v=2)
            valCtrl = valCtrl*(-1)

#ctrlAttr(ctrl, dicAttrs, neutral, valCtrl = 20)

def linkTargets(ctrl, lNeutral):
    if not mc.objExists(ctrl):
        mc.createNode('transform', n=ctrl)
        mc.setAttr(ctrl+'.displayHandle', 1)
    for neutral in lNeutral:
        nspace = crtNspace(neutral)
        if not mc.objExists(nspace+':geo_targets'):
            gTrgt = mc.createNode('transform', n='geo_targets')
            mc.addAttr(gTrgt, ln='trgtBox', at='bool', dv=1)
        bs = getBsDef(neutral, None) or []
        if not bs:
            nBase = neutral
            if ':' in neutral:
                nBase = neutral.split(':')[-1]
            nBs  = 'bs_'+nBase[len(nBase.split('_')[0]) :]
            bs = mc.blendShape(neutral, n=nBs)
            mc.addAttr(bs, ln='bsType', at='enum', en='Trgt:Cor:Mix:', dv=0)
        trgtCor = genAdd(neutral, bs[0], 'cor')
        mc.parent(trgtCor, nspace+':geo_targets')
        trgtMix = genAdd(neutral, bs[0], 'mix')
        mc.parent(trgtMix, nspace+':geo_targets')

        dic = listOfShapes()
        lKeys = dic.keys()
        for key in sorted(lKeys):
            ctrlAttr(ctrl, dic[key], neutral, bs[0], nspace)
        mc.namespace(set=':')

#CORRECTIVES SHAPES (chara in pose)#GEN TARGETS###############################################################################################################################################
def exctractPose(lMsh):
    lCtrl = []
    dicCtrlPos = {}
    lObj = mc.ls('*.nodeType', r=True)
    for obj in lObj:
        if mc.getAttr(obj) == 'control':
            lCtrl.append(obj.split('.')[0])
        if lCtrl:
            for ctrl in lCtrl:
                if not ctrl in dicCtrlPos.keys():
                    dicCtrlPos[ctrl] = {}
                lAttrs = mc.listAttr(ctrl, k=True)
                for attr in lAttrs:
                    if not '.' in attr:
                        if  not mc.attributeQuery(attr, n=ctrl, ch=True):
                            val = mc.getAttr(ctrl+'.'+attr)
                            dicCtrlPos[ctrl][attr] = val
    for msh in lMsh:
        clearName = msh
        if ':' in msh:
            clearName = msh.split(':')[-1]
        dupName = 'shp'+clearName[len(clearName.split('_')[0]):]
        dupMsh = mc.duplicate(msh, n=dupName)[0]
        mc.parent(dupMsh, 'SHP')
        mc.addAttr(dupMsh, ln='notes', dt='string')
        mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string')
        mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string', lock=True)
# exctractPose(mc.ls(sl=True))


def presetTplFaceChan(trgt, dicChans):
    trgtKey = trgt
    if ':' in trgt:
        trgtKey = trgt.split(':')[-1]
    for sign in dicChans.keys():
        if trgtKey in dicChans[sign]:
            if not mc.attributeQuery('ctrlChan', n=trgt, ex=True):
                mc.addAttr(trgt, ln='ctrlChan', dt='string')
            if not mc.attributeQuery('negativeChan', n=trgt, ex=True):
                mc.addAttr(trgt, ln='negativeChan', at='bool')
            mc.setAttr(trgt+'.ctrlChan', dicChans[sign][trgtKey], type='string')
            if sign == 'negative':
                mc.setAttr(trgt+'.negativeChan', 1)
#presetTplFaceChan(trgt, trgtToCtrlChan())

def setTplFaceChan(lTrgt, val):
    for trgt in lTrgt:
        if not mc.attributeQuery('ctrlChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='ctrlChan', dt='string')
        if not mc.attributeQuery('negativeChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='negativeChan', dt='string')
        mc.setAttr(trgt+'.ctrlChan', val)
        mc.setAttr(trgt+'.negativeChan')


def setChannel(chan):
    lId = mc.textScrollList('targetsChan', q=True, sii=True)
    mc.textScrollList('targetsChan', e=True, da=True)
    for id in lId:
        mc.textScrollList('targetsList', e=True, sii=id)
        trgt = mc.textScrollList('targetsList', q=True, si=True)[0]

        mc.textScrollList('targetsChan', e=True, sii=id)
        oldVal = mc.textScrollList('targetsChan', q=True, si=True)[0]

        mc.textScrollList('targetsList', e=True, dii=id)
        if not mc.attributeQuery('ctrlChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='ctrlChan', dt='string')
            mc.setAttr(trgt+'.ctrlChan', '//' , type='string')

        sign = '+'
        if  mc.getAttr(trgt+'.negativeChan') == False:
            sign = '-'

        newVal = sign+chan[0]+chan[-1]
        if chan == 'None':
            newVal = '//'
        mc.setAttr(trgt+'.ctrlChan', chan, type='string')
        mc.textScrollList('targetsChan', e=True, rii=id)
        mc.textScrollList('targetsChan', e=True, ap=[id, newVal])


def invertSign():
    lId = mc.textScrollList('targetsChan', q=True, sii=True)
    mc.textScrollList('targetsChan', e=True, da=True)
    for id in lId:
        mc.textScrollList('targetsList', e=True, sii=id)
        trgt = mc.textScrollList('targetsList', q=True, si=True)[0]

        mc.textScrollList('targetsChan', e=True, sii=id)
        oldVal = mc.textScrollList('targetsChan', q=True, si=True)[0]

        mc.textScrollList('targetsList', e=True, dii=id)
        attrVal = mc.getAttr(trgt+'.negativeChan')

        if attrVal == 0:
            mc.setAttr(trgt+'.negativeChan', 1)
            newVal = oldVal.replace('+', '-')
            mc.textScrollList('targetsChan', e=True, rii=id)
            mc.textScrollList('targetsChan', e=True, ap=[id, newVal])
        elif attrVal == 1:
            newVal = oldVal.replace('-', '+')
            mc.setAttr(trgt+'.negativeChan', 0)
            mc.textScrollList('targetsChan', e=True, rii=id)
            mc.textScrollList('targetsChan', e=True, ap=[id, newVal])


########################################################################
def listOfShapes():
    #EYEBROWS##################################################
    dicEyebrows = {}
    dicEyebrows['ebSlide'] = ['eb_slide_up', 'eb_slide_dn']
    dicEyebrows['ebSqueeze'] = ['eb_squeeze']
    dicEyebrows['ebWrinkle'] = ['eb_wrinkle']
    #EYELIDS###################################################
    dicEyelids = {}
    dicEyelids['elBlinkUp'] = ['el_upSlide_up', 'el_upSlide_dn']
    dicEyelids['elBlinkDn'] = ['el_dnSlide_up', 'el_dnSlide_dn']
    dicEyelids['elOpen'] = ['el_open']
    #CHEEKS####################################################
    dicCheeks = {}
    dicCheeks['chPuff'] = ['ch_puffOut', 'ch_puffIn']
    dicCheeks['chCheeks'] = ['ch_cheeks']
    #NOSE######################################################
    dicNose = {}
    dicNose['nSnear'] = ['no_snear']
    #MOUTH#####################################################
    dicMouth = {}
    dicMouth['mEmote'] = ['mo_smile', 'mo_frown']
    dicMouth['mStrech'] = ['mo_wide', 'mo_narrow']
    dicMouth['mDepth'] = ['mo_depthOut', 'mo_depthIn']
    dicMouth['mPuffCorner'] = ['mo_puffCorner']
    dicMouth['mCornerPinch'] = ['mo_cornerPinch']
    dicMouth['mOpen'] = ['mo_open']
    dicMouth['mU'] = ['mo_uRaiser', 'mo_uLower']

    #LIPS######################################################
    dicLips = {}
    dicLips['lRoll'] = ['li_rollIn', 'li_rollOut']
    dicLips['lPush'] = ['li_push']
    dicLips['lPinch'] = ['li_pinch']
    dicLips['lSlide'] = ['li_raiser', 'li_lower']
    dicLips['lPuff'] = ['li_puff']

    ###########################################################
    dicShapes = {'dicMouth':dicMouth, 'dicEyebrows':dicEyebrows, 'dicLips':dicLips, 'dicCheeks':dicCheeks, 'dicNose':dicNose, 'dicEyelids':dicEyelids}

    return dicShapes

#listOfShapes()

def trgtToCtrlChan():
    dicChans = {}
    dicChansPositive = {}
    dicChansNegative = {}

    #EYEBROWS##################################################
    dicChansPositive['eb_slide_up'] = 'translateY'   #+
    dicChansNegative['eb_slide_dn'] = 'translateY'   #-
    dicChansPositive['eb_squeeze'] = 'translateX'    #+
    dicChansPositive['eb_wrinkle'] = 'scaleZ'        #+
    #EYELIDS###################################################
    dicChansPositive['el_upSlide_up'] = 'translateY' #+
    dicChansNegative['el_upSlide_dn'] = 'translateY' #-
    dicChansPositive['el_dnSlide_up'] = 'translateY' #+
    dicChansNegative['el_dnSlide_dn'] = 'translateY' #-
    dicChans['el_open'] = ''
    #CHEEKS####################################################
    dicChansPositive['ch_puffOut'] = 'scaleZ'      #+
    dicChansNegative['ch_puffIn'] = 'scaleZ'       #-
    dicChansPositive['ch_cheeks'] = 'translateY'   #+
    #NOSE######################################################
    dicChansPositive['no_snear'] = 'translateY'    #+
    #MOUTH#####################################################
    dicChansPositive['mo_smile'] = 'translateY'    #+
    dicChansNegative['mo_frown'] = 'translateY'    #-
    dicChansPositive['mo_wide'] = 'translateX'     #+
    dicChansNegative['mo_narrow'] = 'translateX'   #-
    dicChansPositive['mo_depthOut'] = 'translateZ' #+
    dicChansNegative['mo_depthIn'] = 'translateZ'  #-
    dicChansPositive['mo_puffCorner'] = 'scaleZ'   #+
    dicChansPositive['mo_cornerPinch'] = 'scaleY'  #+
    dicChans['mo_open'] = ''
    dicChansNegative['mo_uRaiser'] = 'rotateZ'     #-
    dicChansPositive['mo_uLower'] = 'rotateZ'      #+
    #LIPS######################################################
    dicChansPositive['li_rollIn'] = 'rotateX'     #+
    dicChansNegative['li_rollOut'] = 'rotateX'    #-
    dicChansPositive['li_push'] = 'translateZ'    #+
    dicChansNegative['li_pinch'] = 'scaleY'       #-
    dicChansPositive['li_raiser'] = 'translateY'  #+
    dicChansNegative['li_lower'] = 'translateY'   #-
    dicChansPositive['li_puff'] = 'scaleZ'        #+

    dicChans = {'positive':dicChansPositive, 'negative':dicChansNegative}
    return dicChans

def getTrgtFromNeutral(neutral):
    bs = getBsDef(neutral, 0)
    lTrgt = getTrgt(bs)
    return lTrgt

#neutral =  mc.ls(sl=True)[0]
#ctrlAttr('c_targets', dicMouth, neutral)
#ctrlAttr('c_targets', dicLips, neutral)
#ctrlAttr('c_targets', dicCheeks, neutral)
#ctrlAttr('c_targets', dicNose, neutral)
#ctrlAttr('c_targets', dicEyelids, neutral)
#ctrlAttr('c_targets', dicEyebrows, neutral)

#############################################################################################################################################################################################################################################
#RIGGING#####################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################
def loadTrgtRef(pathDir = r'T:\03_FAB\00_ASSETS\STP\CHR'):
    filePath = mc.file(q=True, sceneName=True)
    asset = lib_pipe.getAssetPath(filePath)
    assetPath = '\\' +asset+ r'\twip\MAYA'
    path = mc.fileDialog2(dir=pathDir, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.file(path, r=True, ns='TRGT')
    if not mc.objExists('TARGETS'):
        grpTrgt = mc.createNode('transform', n='TARGETS')
        boxTrgt = mc.ls('TRGT:*', assemblies=True)
        mc.parent(boxTrgt, grpTrgt)

        boxTrgt = mc.ls('TRGT:*:*', assemblies=True)
        mc.parent(boxTrgt, grpTrgt)

#loadMOD(pathDir = r'T:\90_TEAM_SHARE\03_FAB\00_ASSETS\01_MOD\01_CHARS')


def dispatchSep(space):
    lSep = mc.ls('*.sepZone', r=True, o=True)
    dicSep = {}
    for sep in lSep:
        zone = mc.getAttr(sep+'.sepZone', asString=True)
        dicSep[zone] = sep
    bBox = mc.exactWorldBoundingBox(lSep[0])
    sizeX = bBox[3]-bBox[0]
    sizeY = bBox[4]-bBox[1]
    sizeZ = bBox[5]-bBox[2]

    baseX = bBox[0]+bBox[3]
    baseY = bBox[1]+bBox[4]
    baseZ = bBox[2]+bBox[5]

    poseX = baseX + sizeX + space
    poseY = 0
    poseZ = 0
    for key in ['lips', 'mouth', 'nose', 'cheeks', 'eyelids', 'eyebrows']:
        mc.setAttr(dicSep[key]+'.translateY', poseY)
        baseY = poseY
        poseY = baseY + sizeY + space

#dispatchSep()

def buildSep(lNeutral, lFaceZone, lSepType):
    #sep types####################
    #mc.menuItem( label='Left')  #
    #mc.menuItem( label='Rigt')  #
    #mc.menuItem( label='Middle')#
    #mc.menuItem( label='Up')    #
    #mc.menuItem( label='Down')  #
    #mc.menuItem( label='Ext')   #
    #mc.menuItem( label='Int')   #
    #mc.menuItem( label='Corner' #
    ##############################
    #list les enum pour creer l attribut
    dicTrgt = lib_names.trgtNames()
    dicSlices = lib_names.sepSlices()
    for neutral in lNeutral:
        name = getObjNameFromNspace(neutral)
        baseName = name[len(name.split('_')[0])+1:]

        clearName = baseName
        if '_' in baseName:
            clearName = ''
            tok = baseName.split('_')
            for i in range(0, len(tok)):
                if i > 0:
                    clearName = clearName+tok[i].capitalize()
                elif i == 0:
                    clearName = clearName+tok[i]
                i += 1
        nSep = 'sep_'+clearName
        sepGrp = 'SEP_'+clearName.upper()
        lib_deformers.activeDef(neutral, False)

        if not mc.objExists(sepGrp):
            mc.createNode('transform', n=sepGrp)

        for faceZone in lFaceZone:
            for slice in lSepType:
                enAttr = ''
                enZone = faceZone
                for key in dicTrgt.keys():
                    enAttr = enAttr+key+':'

                if faceZone == 'None':
                    faceZone = ''
                    if mc.attributeQuery('sepZone', n=neutral, ex=True):
                        enZone = mc.getAttr(neutral+'.sepZone', asString=True)
                else:
                    faceZone = '_'+faceZone

                for sepType in lSepType:
                    if sepType == 'None':
                        sepType = ''
                    else:
                        sepType = '_'+sepType

                    nDup = nSep+faceZone+sepType
                    dupSep = mc.duplicate(neutral, n=nDup)[0]

                    if enZone in dicTrgt.keys():
                        if not mc.attributeQuery('sepZone', n=dupSep, ex=True):
                            mc.addAttr(dupSep, ln='sepZone', at='enum', en=enAttr)
                        lEnum = mc.attributeQuery('sepZone', n=dupSep, le=True)[0].split(':')
                        dv = lEnum.index(enZone)
                        mc.setAttr(dupSep+'.sepZone', dv)
                    if slice in dicSlices.keys():
                        if not mc.attributeQuery('sepSlice', n=dupSep, ex=True):
                            mc.addAttr(dupSep, ln='sepSlice', dt='string', multi=True)
                        id = mc.getAttr(dupSep+'.sepSlice', s=True)
                        mc.setAttr(dupSep+'.sepSlice['+str(id)+']', dicSlices[slice], type='string')
                    try:
                        mc.parent(dupSep, sepGrp)
                    except:
                        pass
                    nBs = 'bs_'+baseName+faceZone+sepType
                    if not mc.objExists(nBs):
                        mc.blendShape(neutral, dupSep, n=nBs)[0]
                    mc.setAttr(nBs+'.'+name, 1)
        lib_deformers.activeDef(neutral, True)
#buildSep(mc.ls(sl=True), ['_L', '_R', '_up', '_dn'])

def getWgtVtx(lMsh):
    dicWeighted = {}
    for msh in lMsh:
        if not msh in dicWeighted.keys():
            dicWeighted[msh] = []
        bs = getBsDef(msh, None)[0]
        rangeVtx = mc.polyEvaluate(msh, v=True)
        for vtx in range(0, rangeVtx):
            chkWght = mc.getAttr(bs+'.inputTarget[0].baseWeights['+str(vtx)+']')
            if chkWght != 0.0:
                dicWeighted[msh].append(vtx)
    return dicWeighted

#getWgtVtx(mc.ls(sl=True))

def autoWeightSepZones(neutral):
    bs = getBsDef(neutral, 0)[0]
    nspaceBs = bs[:len(bs)-len(bs.split(':')[-1])]
    dicZoneTrgt = getZonedTrgt(bs)
    dicZonedSep = getSepMsh()
    dicNeutral = {}

    mc.setAttr(bs+'.envelope', 0)
    vtxs = mc.polyEvaluate(neutral, v=True)
    posMsh = mc.xform(neutral, q=True, ws=True, t=True)

    for i in range(0, vtxs):
        posVtxW = mc.xform(neutral+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        dicNeutral[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]
    for key in dicZoneTrgt.keys():
        lVtxWeighted =  []

        for trgt in dicZoneTrgt[key]:
            tgrtMsh = nspaceBs+trgt
            posTrgt = mc.xform(tgrtMsh, q=True, ws=True, t=True)
            for i in range(0, vtxs):
                posVtxW = mc.xform(nspaceBs+trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]
                #if not posVtxL == dicNeutral[i]:
                    #if not i in lVtxWeighted:
                        #lVtxWeighted.append(i)
                for vec in [0, 1, 2]:
                    gap = compareFloats(dicNeutral[i][vec], posVtxL[vec], 0.0001)
                    if gap == False:
                        if not i in lVtxWeighted:
                            lVtxWeighted.append(i)
        #sorted(lVtxWeighted)
        for sep in dicZonedSep[key]:
            lWght = []
            sepShp = mc.listRelatives(sep, s=True, ni=True)[0]
            bsSepZone = mc.ls(mc.findDeformers(sepShp), type='blendShape')[0]
            if not mc.attributeQuery('weightedVtx', n=sep, ex=True):
                mc.addAttr(sep, ln='weightedVtx', dt='string', multi=True)
            for vtx in range(0, vtxs+1):
                val = 0.0
                if vtx in lVtxWeighted:
                    id = mc.getAttr(sep+'.weightedVtx', s=True)
                    mc.setAttr(sep+'.weightedVtx['+str(id)+']', str(vtx), type='string')
                    val = 1.0
                #lWght[vtx] = val
                lWght.append(val)
                vtx += 1
            mc.setAttr(bsSepZone+'.inputTarget[0].baseWeights[0:'+str(vtxs)+']', *lWght)
    mc.setAttr(bs+'.envelope', 1)
#autoWeightSepZones('TRGT:neutral_head')

def getWgtVtx(lMsh):
    dicWeighted = {}
    for msh in lMsh:
        if not msh in dicWeighted.keys():
            dicWeighted[msh] = []
        if not mc.attributeQuery('weightedVtx', n=msh, ex=True):
            mc.addAttr(msh, ln='weightedVtx', dt='string', multi=True)
        bs = getBsDef(msh, None)[0]
        rangeVtx = mc.polyEvaluate(msh, v=True)
        for vtx in range(0, rangeVtx):
            chkWght = mc.getAttr(bs+'.inputTarget[0].baseWeights['+str(vtx)+']')
            if chkWght != 0.0:
                dicWeighted[msh].append(vtx)
                id = mc.getAttr(msh+'.weightedVtx', s=True)
                mc.setAttr(msh+'.weightedVtx['+str(id)+']', str(vtx), type='string')
    return dicWeighted

#getWgtVtx(mc.ls(sl=True))



def getSepZoneMsh():
    lBaseSep = []
    dicSepZoned = {}
    bsNeut = getBsDef(None, 0)[0]
    neutralShp = mc.blendShape(bsNeut, q=True, g=True)[0]
    lBs = mc.listConnections (neutralShp+'.worldMesh[0]',  type='blendShape') or []
    for bs in lBs:
        sep = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
        zone = mc.getAttr(sep+'.sepZone', asString = True)
        if not zone in dicSepZoned.keys():
            dicSepZoned[zone] = []
        dicSepZoned[zone].append(sep)
    return dicSepZoned

#getSepZoneMsh()


def majSepBaseWght():
    bsNeut = getBsDef(None, 0)[0]
    nspaceBs = bsNeut[:len(bsNeut)-len(bsNeut.split(':')[-1])]
    dicZoneTrgt = getZonedTrgt(bsNeut)
    dicZonedSep = getSepZoneMsh()
    dicNeutral = {}
    neutral = mc.listRelatives(mc.blendShape(bsNeut, q=True, g=True)[0], p=True)[0]

    mc.setAttr(bsNeut+'.envelope', 0)
    lSep = getSepZoneMsh()
    vtxs = mc.polyEvaluate(neutral, v=True)
    posMsh = mc.xform(neutral, q=True, ws=True, t=True)

    for i in range(0, vtxs):
        posVtxW = mc.xform(neutral+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        dicNeutral[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]
    for key in dicZoneTrgt.keys():
        lVtxWeighted =  []
        for trgt in dicZoneTrgt[key]:
            tgrtMsh = nspaceBs+trgt
            posTrgt = mc.xform(tgrtMsh, q=True, ws=True, t=True)
            for i in range(0, vtxs):
                posVtxW = mc.xform(nspaceBs+trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]
                for vec in [0, 1, 2]:
                    gap = compareFloats(dicNeutral[i][vec], posVtxL[vec], 0.0001)
                    if gap == False:
                        if not i in lVtxWeighted:
                            lVtxWeighted.append(i)

        if key in dicZonedSep.keys():
            for sep in dicZonedSep[key]:
                if sep:
                    lWght = []
                    sepShp = mc.listRelatives(sep, s=True, ni=True)[0]
                    bsSepZone = mc.ls(mc.findDeformers(sepShp), type='blendShape')[0]
                    if mc.attributeQuery('weightedVtx', n=sep, ex=True):
                        mc.deleteAttr(sep+'.weightedVtx')
                    mc.addAttr(sep, ln='weightedVtx', dt='string', multi=True)
                    for vtx in range(0, vtxs+1):
                        val = 0.0
                        if vtx in lVtxWeighted:
                            id = mc.getAttr(sep+'.weightedVtx', s=True)
                            mc.setAttr(sep+'.weightedVtx['+str(id)+']', str(vtx), type='string')
                            val = 1.0
                        lWght.append(val)
                        vtx += 1
                    mc.setAttr(bsSepZone+'.inputTarget[0].baseWeights[0:'+str(vtxs)+']', *lWght)
    mc.setAttr(bsNeut+'.envelope', 1)
    print 'SMABED'
#majSepBaseWght()



def genSepZones(neutral):
    if neutral:
        bs = getBsDef(neutral, 0)[0]
        nspaceBs = bs[:len(bs)-len(bs.split(':')[-1])]
        dicZoneTrgt = getZonedTrgt(bs)
        for zone in dicZoneTrgt.keys():
            if len(dicZoneTrgt[zone]) > 0:
                buildSep([neutral], [zone], ['None'])
        autoWeightSepZones(neutral)
        dispatchSep(1.75)
#genSepZones('TRGT:neutral_head')

def symMap(obj):
    activeDef(obj, 0)
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
    activeDef(obj, 1)
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
        mc.addAttr(obj, ln='symTab', at='bool', dv=1, k=False)
        print 'symTab generated on :', obj

#crtSymAttr(mc.ls(sl=True))

def invertBsWghtTo(lObj):
    objSrc = lObj[0]
    objTrgt = lObj[1]
    bsSrc = getBsDef(objSrc, None)[0]
    bsTrgt = getBsDef(objTrgt, None)[0]
    iVtx = mc.polyEvaluate(objSrc, v=True)
    valSrc = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
    valTrgt = []
    for val in valSrc:
        valTrgt.append(1 - float(val))
    mc.setAttr(bsTrgt+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *valTrgt)
#invertBsWghtTo(mc.ls(sl=True))


def copyBsWghtTo(lObj):
    objSrc = lObj[0]
    objTrgt = lObj[1]
    bsSrc = getBsDef(objSrc, None)[0]
    bsTrgt = getBsDef(objTrgt, None)[0]
    iVtx = mc.polyEvaluate(objSrc, v=True)
    val = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
    mc.setAttr(bsTrgt+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *val)
#copyBsWghtTo(mc.ls(sl=True))

def flipBsWght(lObj):
    dicSym = {}
    for obj in lObj:
        dicSym['mid'] = []
        dicSym['sided'] = {}
        bsSrc = getBsDef(obj, None)[0]
        #bsTrgt = getBsDef(objTrgt, None)[0]
        if not mc.attributeQuery('symTab', n=obj, ex=True):
            crtSymAttr(lObj)
        for id in range(0, mc.getAttr(obj+'.symTabLeft', s=True)):
            vtxL = mc.getAttr(obj+'.symTabLeft['+str(id)+']')
            vtxR = mc.getAttr(obj+'.symTabRight['+str(id)+']')
            dicSym['sided'][vtxL] = vtxR
        for id in range(0, mc.getAttr(obj+'.symTabMid', s=True)):
            dicSym['mid'].append(mc.getAttr(obj+'.symTabMid['+str(id)+']'))
        dicVal = {}
        for id in dicSym['sided'].keys():
            dicVal[id] = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights['+str(id)+']')
        for id in dicSym['sided'].values():
            dicVal[id] = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights['+str(id)+']')
        #for id in symVtx['mid']:
            #dicVal[id] = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights['+id+']')
        for id in dicVal.keys():
            for key, value in dicSym['sided'].items():
                if id == key:
                    mc.setAttr(bsSrc+'.inputTarget[0].baseWeights['+str(id)+']', dicVal[value])
                if id == value:
                    mc.setAttr(bsSrc+'.inputTarget[0].baseWeights['+str(id)+']', dicVal[key])
#flipBsWght(mc.ls(sl=True))


def mirrorBsWght(lObj, side):
    dicSym = {}
    attrSrc = '.symTabLeft'
    attrTrgt = '.symTabRight'
    if side == 'R':
        attrSrc = '.symTabRight'
        attrTrgt = '.symTabLeft'
    for obj in lObj:
        dicSym['sided'] = {}
        bsSrc = getBsDef(obj, None)[0]
        if not mc.attributeQuery('symTab', n=obj, ex=True):
            crtSymAttr(lObj)
        for id in range(0, mc.getAttr(obj+attrSrc, s=True)):
            vtxSrc = mc.getAttr(obj+attrSrc+'['+str(id)+']')
            vtxTrgt = mc.getAttr(obj+attrTrgt+'['+str(id)+']')
            value = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights['+str(vtxSrc)+']')
            mc.setAttr(bsSrc+'.inputTarget[0].baseWeights['+str(vtxTrgt)+']', value)
#mirrorBsWght(mc.ls(sl=True))


def addBsWghtTo(lObj):
    objSrc = lObj[0]
    objTrgt = lObj[1]
    bsSrc = getBsDef(objSrc, None)[0]
    bsTrgt = getBsDef(objTrgt, None)[0]
    iVtx = mc.polyEvaluate(objSrc, v=True)
    val = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
    if val != 0.0:
        mc.setAttr(bsTrgt+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *val)

def crtSepChecker(lMsh):
    lCheckers = []
    lSep = []
    lBs = []
    for msh in lMsh:
        if mc.attributeQuery('sepChecker', n=msh, ex=True):
            lCheckers.append(msh)
        else:
            lSep.append(msh)
    if lCheckers:
        for checker in lCheckers:
            bs = getBsDef(checker, type=None)
            for sep in lSep:
                lWght = mc.blendShape(bs, q=True, t=True) or []
                id = 0
                if lWght:
                    id = len(lWght)
                chkTrgt = mc.blendShape(bs, q=True, t=True) or []
                if not sep in chkTrgt:
                    mc.blendShape(bs, edit=True, t=(checker, id, sep, 1.0))
                    mc.setAttr(bs+'.'+sep, 1)
    elif not lCheckers:
        shp = mc.listRelatives(lSep[0], ni=True)[0]
        activeDef(shp, 0)
        checker = mc.duplicate(lSep[0], n='smab')[0]

        activeDef(shp, 1)
        bs = mc.blendShape(checker, n='bs_smab')
        for sep in lSep:
            lWght = mc.blendShape(bs, q=True, t=True) or []
            id = 0
            if lWght:
                id = len(lWght)
            chkTrgt = mc.blendShape(bs, q=True, t=True) or []
            if not sep in chkTrgt:
                mc.blendShape(bs, edit=True, t=(checker, id, sep, 1.0))
                mc.setAttr(bs[0]+'.'+sep, 1)
#crtSepChecker(mc.ls(sl=True))


def connectNeutralWrap(lMsh):
    lSep = []
    lAdds = []
    for msh in lMsh:
        if mc.attributeQuery('sepZone', n=msh, ex=True):
            lSep.append(msh)
        else:
            lAdds.append(msh)
    for sep in lSep:
        activeDef(mc.listRelatives(sep, s=True)[0], 0)
        pos = mc.getAttr(sep+'.translate')[0]
        ort = mc.getAttr(sep+'.rotate')[0]
        father = mc.listRelatives(sep, p=True)[0]
        addsFather = father+'_ADDS'
        if not mc.objExists(father+'_ADDS'):
            addsFather = mc.createNode('transform', n=father+'_ADDS')
            mc.parent(addsFather, father)
        lToWrap = []
        if not mc.attributeQuery('adds', n=sep, ex=True):
            mc.addAttr(sep, ln='adds', at='message', multi=True)
        for add in lAdds:
            neutral = add.split('neutral_')[-1]
            neutName = neutral.capitalize().replace('_', '')+'t'
            nAdd = sep.replace(sep.split('_')[0], 'wrp'+neutName)
            dupAdd = nAdd
            if not mc.objExists(nAdd):
                dupAdd = mc.duplicate(add, n=nAdd)[0]
                mc.parent(dupAdd, addsFather)
                mc.setAttr(dupAdd+'.translate', *pos)
                mc.setAttr(dupAdd+'.rotate', *ort)
                id = mc.getAttr(sep+'.adds', s=True)
                mc.connectAttr(dupAdd+'.message', sep+'.adds['+str(id)+']')
                lToWrap.append(dupAdd)
            if not mc.attributeQuery('neutral', n=dupAdd, ex=True):
                mc.addAttr(dupAdd, ln='neutral', at='message')
                mc.connectAttr(add+'.message', dupAdd+'.neutral')
        mc.select(cl=True)
        if lToWrap:
            mc.select(dupAdd)
            mc.select(sep, add=True)
            mc.CreateWrap()
        activeDef(mc.listRelatives(sep, s=True)[0], 1)
#connectNeutralWrap(mc.ls(sl=True))

"""
def getSepMsh():
    lMsh = mc.ls(type='mesh', ni=True, rn=False)
    lRefMsh = mc.ls(type='mesh', ni=True, rn=True)
    lShp = list(set(lMsh)-set(lRefMsh))
    toExtract = []
    for shp in lShp:
        lBs = []
        lHist = mc.listHistory(shp, f=True, lv=1) or []
        if lHist:
            lBs = mc.ls(lHist, type='blendShape') or []
        if not lBs:
            toExtract.append(mc.listRelatives(shp, p=True)[0])
    return toExtract
#getSepMsh()
"""

def genTplName(comp, type):
    obj = comp.split('.')[0]
    zone = mc.getAttr(obj+'.sepZone', asString=True)
    side = ''
    lSlices = obj.split(zone.capitalize())[-1].split('_')
    if 'Left' in lSlices:
        side = '_L'
        lSlices.remove('Left')
    if 'Right' in lSlices:
        side = '_R'
        lSlices.remove('Right')
    nTpl = type+'_'+zone
    for slice in lSlices:
        nTpl+=slice
    return nTpl+side

def crtCrvPath(comp):
    obj = comp.split('.')[0]
    nCrvPath = genTplName(comp, 'crvPath')
    edgId = comp.split('[')[:-1]
    if not '.e[' in comp:
        fistule = ''
        if '.vtx[' in comp:
            fistule = mc.polyInfo(comp, vertexToEdge=True)[0].split(':')[-1]
        elif '.f[' in comp:
            fistule = mc.polyInfo(comp, faceToEdge=True)[0].split(':')[-1]
        lEdg = fistule.split(' ')
        for i in lEdg:
            if i != '':
                edgId = i
                break

    mc.select(cl=True)
    mc.select(obj+'.e['+str(edgId)+']')
    mel.eval("SelectEdgeLoopSp")
    crvPath = mc.polyToCurve(form=1, degree=3, conformToSmoothMeshPreview=0, n=nCrvPath)
    return crvPath
#crtCrvPath(mc.ls(sl=True))


def crtCrvPathCtrl(root, mshBase, vtx):
    mc.select(cl=True)
    mc.select(mshBase+'.vtx['+str(vtx)+']')
    lEdg = mc.polyListComponentConversion(fv=True, te=True)
    mc.select(cl=True)
    mc.select(lEdg)
    edg = mc.ls(sl=True, fl=True)[0]
    mc.select(cl=True)
    mc.select(edg)
    crvPath = mc.polyToCurve(form=1, degree=3, conformToSmoothMeshPreview=0)
    return crvPath
#crtCrvPath(mc.ls(sl=True))


def curveAttach(curve, node):
    """ attach nodes to curve """
    # init
    shape = mc.listRelatives(curve, ni=True, s=True)[-1]
    # attach each node to curve
    # init
    vp =  'vp'+node[len(node.split('_')[0]) :]
    if not mc.objExists(vp):
        vp = mc.createNode('vectorProduct', n=vp)
    poci = 'pOCI'+node[len(node.split('_')[0]) :]
    if not mc.objExists(poci):
        poci = mc.createNode('pointOnCurveInfo', n=poci)
    ca = 'ca'+node[len(node.split('_')[0]) :]
    if not mc.objExists(ca):
        ca = mc.createNode('transform', n=ca)
    # npoc
    npoc = 'nPOC'+node[len(node.split('_')[0]) :]
    if not mc.objExists(npoc):
        npoc = mc.createNode('nearestPointOnCurve', n=npoc)
    if not mc.isConnected(shape + '.worldSpace[0]', npoc + '.inputCurve'):
        mc.connectAttr(shape + '.worldSpace[0]', npoc + '.inputCurve', f=True)
    # connections
    mc.setAttr(vp + '.operation', 4)
    if not mc.isConnected(poci + '.position', vp + '.input1'):
        mc.connectAttr(poci + '.position', vp + '.input1', f=True)
    if not mc.isConnected(shape + '.worldSpace[0]', poci + '.inputCurve'):
        mc.connectAttr(shape + '.worldSpace[0]', poci + '.inputCurve', f=True)
    if not mc.isConnected(node + '.translate', npoc + '.inPosition'):
        mc.connectAttr(node + '.translate', npoc + '.inPosition', f=True)
    if not mc.isConnected(ca + '.parentInverseMatrix[0]', vp + '.matrix'):
        mc.connectAttr(ca + '.parentInverseMatrix[0]', vp + '.matrix', f=True)
    if not mc.isConnected(vp + '.output', ca + '.translate'):
        mc.connectAttr(vp + '.output', ca + '.translate', f=True)
    if not mc.isConnected(npoc + '.result.parameter', poci + '.parameter'):
        mc.connectAttr(npoc + '.result.parameter', poci + '.parameter', f=True)
    mc.disconnectAttr(npoc + '.result.parameter', poci + '.parameter')
    # parent
    print node
    mc.parent(node, ca)
    # delete nearestPointOnCurve
    mc.delete(npoc)
    # return
    return ca
#curveAttach('crv_hairs_R', mc.ls(sl=True))

def genTpl(lComp):
    if not mc.objExists('TPL'):
            mc.createNode('transform', n='TPL')
    if not mc.objExists('PATH'):
            mc.createNode('transform', n='PATH')
    for comp in lComp:
        obj = comp.split('.')[0]
        crvPath = crtCrvPath(comp)[0]
        pos = mc.xform(comp, q=True, ws=True, t=True)
        if len(pos) > 3:
            mc.warning('select only vertex please')
            return
            nbrVtx = len(pos)/3
            i, addX, addY, addZ = 0, 0, 0, 0
            for i in range(0, nbrVtx):
                addX += pos[i]
                addY += pos[i+1]
                addZ += pos[i+2]
                i += 3
            pos = [addX/nbrVtx, addY/nbrVtx, addZ/nbrVtx]

        mc.select(cl=True)
        nTpl = genTplName(comp, 'tpl')
        loc = mc.spaceLocator(n=nTpl)[0]
        mc.setAttr(loc+'.t', *pos)
        mc.setAttr(loc+'.localScaleX', .25)
        mc.setAttr(loc+'.localScaleY', .25)
        mc.setAttr(loc+'.localScaleZ', .25)
        mc.addAttr(loc, ln='vtxId', dt='string')
        mc.setAttr(loc+'.vtxId', comp.split('[')[-1][:-1], type='string')
        dicTrgt = lib_names.trgtNames()
        enAttr = ''
        for key in dicTrgt.keys():
            enAttr = enAttr+key+':'
        if not mc.attributeQuery('tplZone', n=loc, ex=True):
            mc.addAttr(loc, ln='tplZone', at='enum', en=enAttr)
        mc.connectAttr(obj+'.sepZone', loc+'.tplZone')

        ca = curveAttach(crvPath, loc)
        mc.parent(ca, 'TPL')
#genTpl(mc.ls(sl=True))

def connTplToNeutral():
    lNodes = mc.ls(type='polyEdgeToCurve')
    bsNeutral = getBsTrgt(0)[0]
    neutralShp =mc.blendShape(bsNeutral, q=True,  g=True)
    neutral = mc.listRelatives(neutralShp, p=True)[0]
    for node in lNodes:
        print node
        mc.connectAttr(neutral+'.outMesh', node+'.inputPolymesh', f=True)
        mc.connectAttr(neutral+'.outSmoothMesh', node+'.inputSmoothPolymesh', f=True)
        mc.connectAttr(neutral+'.worldMatrix[0]', node+'.inputMat', f=True)
        mc.connectAttr(neutral+'.displaySmoothMesh', node+'.displaySmoothMesh', f=True)
        mc.connectAttr(neutral+'.smoothLevel', node+'.smoothLevel', f=True)

#switchTplToNeutral()

def extractTpl(father):
    lTpl = mc.ls('*.tplZone', r=True, o=True) or []
    for tpl in lTpl:
        extTpl = mc.duplicate(tpl)[0]
        mc.parent(extTpl, father)
        mc.rename(extTpl, extTpl[:-1])


def getSepMsh():
    dicTrgt = lib_names.trgtNames()
    dicZonedSep = {}
    lMsh = mc.ls(type='mesh', ni=True, rn=False)
    lRefMsh = mc.ls(type='mesh', ni=True, rn=True)
    lShp = list(set(lMsh)-set(lRefMsh))
    toExtract = []
    for shp in lShp:
        lBs = []
        lHist = mc.listHistory(shp, f=True, lv=1) or []
        if lHist:
            lBs = mc.ls(lHist, type='blendShape') or []
        if not lBs:
            toExtract.append(mc.listRelatives(shp, p=True)[0])
    for key in dicTrgt.keys():
        dicZonedSep[key] = []
    for sep in toExtract:
        if mc.attributeQuery('sepZone', n=sep, ex=True):
            zone = mc.getAttr(sep+'.sepZone', asString=True)
            dicZonedSep[zone].append(sep)
    return dicZonedSep
#getSepMsh()

def getZonedTrgt(bs):
    lTrgt = []
    dicTrgt = lib_names.trgtNames()
    lWght = mc.aliasAttr(bs, q=True)
    for wght in lWght:
        if not wght.startswith('weight['):
            if not wght.startswith('cor_'):
                if not wght.startswith('mix_'):
                    lTrgt.append(wght)
    dicZones = {}
    for key in dicTrgt.keys():
        dicZones[key] = []

    for trgt in lTrgt:
        zone = trgt.split('_')[0]
        for key in dicTrgt.keys():
            if dicTrgt[key] == zone:
                dicZones[key].append(trgt)
    return dicZones
#getZonedTrgt()

def extractAdds(sep, extShp, normalize):
    if mc.attributeQuery('adds', n=sep, ex=True):
        lAdds = mc.listConnections(sep+'.adds', s=True) or []
        if lAdds:
            lExtAdds = []
            if not mc.attributeQuery('shpAdds', n=extShp, ex=True):
                mc.addAttr(sep, ln='shpAdds', at='message', multi=True)
            for add in lAdds:
                base = add.split('_')[0]
                base = base.replace('wrp', '')
                side =''
                if base.endswith('rt'):
                    base = base[: -2]
                    side = '_R'
                elif base.endswith('lt'):
                    base = base[: -2]
                    side = '_L'
                father = 'SHAPES'+'_'+base+side
                if not mc.objExists(father):
                    father = mc.createNode('transform', n='SHAPES'+'_'+base+side)
                nAdd = extShp+base
                extAdd = mc.duplicate(add, n=nAdd)[0]
                mc.parent(extAdd, father)
                id = mc.getAttr(extShp+'.adds', s=True)
                mc.connectAttr(extAdd+'.message', extShp+'.adds['+str(id)+']')
                lExtAdds.append(extAdd)

                if normalize:
                    roof = 0.0
                    lDef = mc.listHistory(add)
                    lWrp = mc.ls(lDef, type='wrap') or []
                    if lWrp:
                        wrp = lWrp[0]
                        mc.setAttr(wrp+'.envelope', 0)
                        neutAdd = mc.duplicate(add, n=add+'SUCE')[0]
                        mc.setAttr(wrp+'.envelope', 1)
                        posNeut = mc.xform(neutAdd, q=True, ws=True, t=True)
                        postrgtGeo = mc.xform(extAdd, q=True, ws=True, t=True)
                        dicTrgtGeoVtxDif = {}
                        dicTrgtGeoVtx = {}
                        lVtxs  =mc.polyEvaluate(extAdd, v=True)
                        for vtx in range(0, lVtxs):
                            posVtx = mc.xform(neutAdd+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                            posNeutGeoVtx= [posVtx[0]-posNeut[0], posVtx[1]-posNeut[1], posVtx[2]-posNeut[2]]
                            posVtxtrgtGeo = mc.xform(extAdd+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                            #remove transform pos from vtx pos trgt (set to world 0, 0, 0)
                            posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
                            #get dif betweeen sourc and trgtGeo vtx
                            dif = math.sqrt(((posVtxInneutralGeo[0]-posNeutGeoVtx[0])**2)+((posVtxInneutralGeo[1]-posNeutGeoVtx[1])**2)+((posVtxInneutralGeo[2]-posNeutGeoVtx[2])**2))
                            #get roof
                            if dif != 0.0:
                                if abs(dif) > roof:
                                    roof = dif
                            dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
                            dicTrgtGeoVtxDif[vtx] = dif
                        ratio = 1.0/roof
                        if roof < 1.0:
                            ratio = roof/1.0
                        for vtx in range(0, lVtxs):
                            norm = [0.0, 0.0, 0.0]
                            norm[0] = ratio*(posNeutGeoVtx[0] - dicTrgtGeoVtx[vtx][0])+dicTrgtGeoVtx[vtx][0]
                            norm[1] = ratio*(posNeutGeoVtx[1] - dicTrgtGeoVtx[vtx][1])+dicTrgtGeoVtx[vtx][1]
                            norm[2] = ratio*(posNeutGeoVtx[2] - dicTrgtGeoVtx[vtx][2])+dicTrgtGeoVtx[vtx][2]
                            mc.move(norm[0], norm[1], norm[2], extAdd+'.vtx['+str(vtx)+']', ls=True)
                        mc.delete(neutAdd)

            return lExtAdds

"""
OLD
def extractShapes():
    if not mc.objExists('SHAPES'):
        mc.createNode('transform', n='SHAPES')
    if not mc.objExists('FACE_TPL'):
        mc.createNode('transform', n='FACE_TPL')
    bs = getBsDef(None, 0)[0]
    nspaceBs = bs[:len(bs)-len(bs.split(':')[-1])]
    neutralGeo = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
    dicZone = lib_names.trgtNames()
    dicZoneTrgt = getZonedTrgt(bs)
    dicZonedSep = getSepMsh()
    nspace = lib_namespace.getNspaceFromObj(bs)
    lMovedVtx = []
    dicNeutGeoVtx = {}

    roof = 1.0
    #get neutralGeo transform position
    posSrc = mc.xform(neutralGeo, q=True, ws=True, t=True)
    vtxs = mc.polyEvaluate(neutralGeo, v=True)

    for key in dicZoneTrgt.keys():
        for trgt in dicZoneTrgt[key]:
            mc.setAttr(bs+'.'+trgt, 0)
    extractTpl('FACE_TPL')

    count = len(dicZoneTrgt.keys())
    for key in dicZoneTrgt.keys():
        ############################################
        count -= 1
        print '_____________________'
        print 'zone :', key, count, 'more'
        extraCount = len(dicZoneTrgt[key])
        ############################################
        lVtxs = []
        if dicZoneTrgt[key]:
            for id in range(0, mc.getAttr(dicZonedSep[key][0]+'.weightedVtx', s=True)):
                vtx = mc.getAttr(dicZonedSep[key][0]+'.weightedVtx['+str(id)+']')
                lVtxs.append(vtx)
                posVtx = mc.xform(neutralGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]
            for trgt in dicZoneTrgt[key]:
                ############################################
                extraCount -= 1
                print 'trgt :', trgt, extraCount, 'more'
                ############################################
                if mc.attributeQuery('ctrlChan', n=nspace+':'+trgt, ex=True):
                    chan = mc.getAttr(nspace+':'+trgt+'.ctrlChan')
                    normalise = False
                    if chan.startswith('translate'):
                        normalise = True
                    sign = mc.getAttr(nspace+':'+trgt+'.negativeChan')
                    mc.setAttr(bs+'.'+trgt, 1)
                    nTrgt = trgt[len(trgt.split('_')[0]):]
                    clearNTrgt = nTrgt
                    if '_' in trgt:
                        smab = nTrgt.split('_')
                        clearNTrgt = smab[1]
                        for i in range(2, len(smab)):
                            suce = smab[i].capitalize()
                            clearNTrgt += suce
                    for sep in dicZonedSep[key]:
                        lVtxMoved = []
                        posTrgt = mc.xform(sep, q=True, ws=True, t=True)
                        for i in lVtxs:
                            posVtxW = mc.xform(nspaceBs+trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                            posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]


                            for vec in [0, 1, 2]:
                                gap = compareFloats(dicNeutGeoVtx[i][vec], posVtxL[vec], 0.001)
                                if gap == False:
                                    if not i in lVtxMoved:
                                        lVtxMoved.append(i)
                        #if mc.polyCompare(neutralGeo, sep) == 1:
                        if lVtxMoved:
                            pole = ''
                            if mc.attributeQuery('sepSlice', n=sep, ex=True):
                                ids = mc.getAttr(sep+'.sepSlice', s=True)
                                for i in range(0, ids):
                                    pole += mc.getAttr(sep+'.sepSlice['+str(i)+']')
                            zone = dicZone[key]
                            side = ''
                            if 'Left' in sep:
                                side = '_L'
                            elif 'Right' in sep:
                                side = '_R'
                            nExShp = zone+'_'+clearNTrgt+pole+side

                            extShp = mc.duplicate(sep, n=nExShp)[0]
                            moveMax = 0.0
                            extAdds = extractAdds(sep, extShp, normalise) or []

                            if normalise == True:
                                dicTrgtGeoVtxDif = {}
                                dicTrgtGeoVtx = {}
                                postrgtGeo = mc.xform(sep, q=True, ws=True, t=True)
                                for vtx in lVtxs:
                                    axe = 0
                                    if chan.endswith('Y'):
                                        axe = 1
                                    elif chan.endswith('Z'):
                                        axe = 2
                                    #get position of vtx for trgt
                                    posVtxtrgtGeo = mc.xform(extShp+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                                    if abs(posVtxtrgtGeo[axe])-abs(postrgtGeo[axe]) > moveMax:
                                            moveMax = posVtxtrgtGeo[axe]-postrgtGeo[axe]
                                    #remove transform pos from vtx pos trgt (set to world 0, 0, 0)
                                    posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
                                    #get dif betweeen sourc and trgtGeo vtx
                                    dif = math.sqrt(((posVtxInneutralGeo[0]-dicNeutGeoVtx[vtx][0])**2)+((posVtxInneutralGeo[1]-dicNeutGeoVtx[vtx][1])**2)+((posVtxInneutralGeo[2]-dicNeutGeoVtx[vtx][2])**2))
                                    #get roof
                                    if dif != 0.0:
                                        if abs(dif) > roof:
                                            roof = dif
                                    dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
                                    dicTrgtGeoVtxDif[vtx] = dif
                                ratio = 1.0/roof
                                for vtx in lVtxs:
                                    norm = [0.0, 0.0, 0.0]
                                    norm[0] = ratio*(dicNeutGeoVtx[vtx][0] - dicTrgtGeoVtx[vtx][0])+dicTrgtGeoVtx[vtx][0]
                                    norm[1] = ratio*(dicNeutGeoVtx[vtx][1] - dicTrgtGeoVtx[vtx][1])+dicTrgtGeoVtx[vtx][1]
                                    norm[2] = ratio*(dicNeutGeoVtx[vtx][2] - dicTrgtGeoVtx[vtx][2])+dicTrgtGeoVtx[vtx][2]
                                    mc.move(norm[0], norm[1], norm[2], extShp+'.vtx['+str(vtx)+']', ls=True)
                            mc.addAttr(extShp, ln='ctrlChan', dt='string')
                            mc.setAttr(extShp+'.ctrlChan', chan, type='string')
                            mc.addAttr(extShp, ln='negativeChan', at='bool')
                            mc.setAttr(extShp+'.negativeChan', sign)
                            mc.addAttr(extShp, ln='maxMove', at='double')
                            mc.setAttr(extShp+'.maxMove', moveMax)
                            mc.parent(extShp, 'SHAPES')


                    mc.setAttr(bs+'.'+trgt, 0)
"""
def extractShapes():
    if not mc.objExists('SHAPES'):
        mc.createNode('transform', n='SHAPES')
    if not mc.objExists('FACE_TPL'):
        mc.createNode('transform', n='FACE_TPL')
    bs = getBsDef(None, 0)[0]
    neutralGeo = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
    dicZone = lib_names.trgtNames()
    dicZoneTrgt = getZonedTrgt(bs)
    dicZonedSep = getSepMsh()
    nspace = lib_namespace.getNspaceFromObj(bs)
    lMovedVtx = []
    dicNeutGeoVtx = {}

    roof = 0.0
    #get neutralGeo transform position
    posSrc = mc.xform(neutralGeo, q=True, ws=True, t=True)
    vtxs = mc.polyEvaluate(neutralGeo, v=True)

    for key in dicZoneTrgt.keys():
        for trgt in dicZoneTrgt[key]:
            mc.setAttr(bs+'.'+trgt, 0)
    extractTpl('FACE_TPL')

    count = len(dicZoneTrgt.keys())
    for key in dicZoneTrgt.keys():
        ############################################
        count -= 1
        print '_____________________'
        print 'zone :', key, count, 'more'
        extraCount = len(dicZoneTrgt[key])
        ############################################
        lVtxs = []
        if dicZoneTrgt[key]:
            for id in range(0, mc.getAttr(dicZonedSep[key][0]+'.weightedVtx', s=True)):
                vtx = mc.getAttr(dicZonedSep[key][0]+'.weightedVtx['+str(id)+']')
                lVtxs.append(vtx)
                posVtx = mc.xform(neutralGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]
            for trgt in dicZoneTrgt[key]:
                ############################################
                extraCount -= 1
                print 'trgt :', trgt, extraCount, 'more'
                ############################################
                if mc.attributeQuery('ctrlChan', n=nspace+':'+trgt, ex=True):
                    chan = mc.getAttr(nspace+':'+trgt+'.ctrlChan')
                    normalise = False
                    if chan.startswith('translate'):
                        normalise = True
                    sign = mc.getAttr(nspace+':'+trgt+'.negativeChan')
                    mc.setAttr(bs+'.'+trgt, 1)
                    nTrgt = trgt[len(trgt.split('_')[0]):]
                    clearNTrgt = nTrgt
                    if '_' in trgt:
                        smab = nTrgt.split('_')
                        clearNTrgt = smab[1]
                        for i in range(2, len(smab)):
                            suce = smab[i].capitalize()
                            clearNTrgt += suce
                    for sep in dicZonedSep[key]:
                        if mc.polyCompare(neutralGeo, sep) == 1:
                            pole = ''
                            if mc.attributeQuery('sepSlice', n=sep, ex=True):
                                ids = mc.getAttr(sep+'.sepSlice', s=True)
                                for i in range(0, ids):
                                    pole += mc.getAttr(sep+'.sepSlice['+str(i)+']')
                            zone = dicZone[key]
                            side = ''
                            if 'Left' in sep:
                                side = '_L'
                            elif 'Right' in sep:
                                side = '_R'
                            nExShp = zone+'_'+clearNTrgt+pole+side

                            extShp = mc.duplicate(sep, n=nExShp)[0]
                            moveMax = 0.0
                            if normalise == True:
                                dicTrgtGeoVtxDif = {}
                                dicTrgtGeoVtx = {}
                                postrgtGeo = mc.xform(sep, q=True, ws=True, t=True)
                                for vtx in lVtxs:
                                    axe = 0
                                    if chan.endswith('Y'):
                                        axe = 1
                                    elif chan.endswith('Z'):
                                        axe = 2
                                    #get position of vtx for trgt
                                    posVtxtrgtGeo = mc.xform(extShp+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)

                                    if abs(posVtxtrgtGeo[axe])-abs(postrgtGeo[axe]) > moveMax:
                                            moveMax = posVtxtrgtGeo[axe]-postrgtGeo[axe]
                                    #remove transform pos from vtx pos trgt (set to world 0, 0, 0)
                                    posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
                                    #get dif betweeen sourc and trgtGeo vtx
                                    dif = math.sqrt(((posVtxInneutralGeo[0]-dicNeutGeoVtx[vtx][0])**2)+((posVtxInneutralGeo[1]-dicNeutGeoVtx[vtx][1])**2)+((posVtxInneutralGeo[2]-dicNeutGeoVtx[vtx][2])**2))
                                    #get roof
                                    if dif != 0.0:
                                        if abs(dif) > roof:
                                            roof = dif
                                    dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
                                    dicTrgtGeoVtxDif[vtx] = dif
                                ratio = 1.0/roof
                                if roof < 1.0:
                                    ratio = roof/1.0
                                for vtx in lVtxs:
                                    norm = [0.0, 0.0, 0.0]
                                    norm[0] = ratio*(dicNeutGeoVtx[vtx][0] - dicTrgtGeoVtx[vtx][0])+dicTrgtGeoVtx[vtx][0]
                                    norm[1] = ratio*(dicNeutGeoVtx[vtx][1] - dicTrgtGeoVtx[vtx][1])+dicTrgtGeoVtx[vtx][1]
                                    norm[2] = ratio*(dicNeutGeoVtx[vtx][2] - dicTrgtGeoVtx[vtx][2])+dicTrgtGeoVtx[vtx][2]

                                    mc.move(norm[0], norm[1], norm[2], extShp+'.vtx['+str(vtx)+']', ls=True)

                            #extAdds = extractAdds(sep, extShp, normalise) or []

                            mc.addAttr(extShp, ln='ctrlChan', dt='string')
                            mc.setAttr(extShp+'.ctrlChan', chan, type='string')
                            mc.addAttr(extShp, ln='negativeChan', at='bool')
                            mc.setAttr(extShp+'.negativeChan', sign)
                            mc.addAttr(extShp, ln='maxMove', at='double')
                            mc.setAttr(extShp+'.maxMove', moveMax)
                            mc.parent(extShp, 'SHAPES')
                    mc.setAttr(bs+'.'+trgt, 0)

#extractShapes()



########################################################################################################################################################################
########################################################################################################################################################################
#BUILD##################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
def setFaceTpl():
    dicTpl = {}
    lFaceTpl = mc.ls('*.tplZone', r=True, o=True)
    print lFaceTpl
    for tpl in lFaceTpl:
        print tpl
        if not mc.objExists(tpl.split(':')[-1]):
            key = mc.getAttr(tpl+'.tplZone', asString=True)
            if not key in dicTpl.keys():
                dicTpl[key] = []
            dicTpl[key].append(mc.duplicate(tpl)[0])
    for key in dicTpl.keys():
        lib_controlGroup.addTplsToCg(dicTpl[key], 'cg_'+key)
        for tpl in dicTpl[key]:
            if mc.attributeQuery('buildPoseNode', n=tpl, ex=True):
                mc.setAttr(tpl+'.buildPoseNode', 1)
            print tpl, 'added to: cg_'+key

#setFaceTpl()

def buildFaceTpl():
    smab=[]
    #A CORRIGER!!!!
    lMsh = mc.ls(sl=True) or []
    if lMsh:
        msh = lMsh[0]
        #########################
        dicSym = {}
        iter = mc.getAttr(msh+'.symTabLeft', s=True)
        for i in range(0, iter):
            dicSym[mc.getAttr(msh+'.symTabLeft['+str(i)+']')] = mc.getAttr(msh+'.symTabRight['+str(i)+']')
        dicTrgt = lib_names.trgtNames()
        enAttr=''
        for key in dicTrgt.keys():
            enAttr = enAttr+key+':'

        lFaceTpl = mc.ls('*.tplZone', r=True, o=True)
        for tpl in lFaceTpl:
            zone = mc.getAttr(tpl+'.tplZone', asString=True)
            if not zone in smab:
                smab.append(zone)
        for zone in smab:
            lib_controlGroup.buildTplCg('cg_'+zone)
            lRoots = mc.listConnections('cg_'+zone+'.membersVisibility')
            for root in lRoots:
                pose = mc.listRelatives(root, c=True)[0]
                ctrl = mc.listRelatives(pose, c=True)[0]
                tpl = mc.listConnections(ctrl+'.nodes[0]', s=True)[0]
                side = mc.getAttr(ctrl+'.mirrorSide', asString=True)

                if not mc.attributeQuery('ctrlZone', n=ctrl, ex=True):
                    mc.addAttr(ctrl, ln='ctrlZone', at='enum', en=enAttr)
                mc.connectAttr(tpl+'.tplZone', ctrl+'.ctrlZone', f=True)

                mlt = mc.createNode('multiplyDivide')
                for i in ['X', 'Y', 'Z']:
                    mc.setAttr(mlt+'.input2'+i, -1)
                    mc.connectAttr(ctrl+'.translate'+i, mlt+'.input1'+i)
                    mc.connectAttr(mlt+'.output'+i, pose+'.translate'+i)

                mlt = mc.createNode('multiplyDivide')
                for i in ['X', 'Y', 'Z']:
                    mc.setAttr(mlt+'.input2'+i, -1)
                    mc.connectAttr(ctrl+'.rotate'+i, mlt+'.input1'+i)
                    mc.connectAttr(mlt+'.output'+i, pose+'.jointOrient'+i)

                vtx = int(mc.getAttr(tpl+'.vtxId'))
                if side == 'right':
                    if vtx in dicSym.keys():
                        suce = vtx
                        vtx = dicSym[suce]
                crvPath = crtCrvPathCtrl(root, msh, vtx)
                curveAttach(crvPath[0], root)
    else:
        mc.warning('select the mesh you want to attach the rig SAHEUP')


def connectFaceRig():
    dicShp = {}
    dicCtrl = {}
    dicSym = {}
    base = ''
    enAttr = ''
    lFaceTpl = mc.ls('*.tplZone', o=True)
    lShp = mc.ls('*.sepZone',r=True, o=True)
    lHist = mc.listHistory(lShp[0], f=True)
    bs = mc.ls(lHist, type='blendShape')[0]
    mshBase = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]

    posBase = mc.xform(mshBase, q=True, ws=True, t=True)

    dicTrgt = lib_names.trgtNames()

    for shp in lShp:
        zone = mc.getAttr(shp+'.sepZone', asString=True)
        if not zone in dicShp.keys():
            dicShp[zone] = []
            cg = 'cg_'+zone
            if mc.objExists(cg):
                dicCtrl[zone] = mc.listConnections(cg+'.members', s=True, d=False)
        dicShp[zone].append(shp)


    iter = mc.getAttr(mshBase+'.symTabLeft', s=True)
    for i in range(0, iter):
        dicSym[mc.getAttr(mshBase+'.symTabLeft['+str(i)+']')] = mc.getAttr(mshBase+'.symTabRight['+str(i)+']')


    for zone in dicCtrl.keys():
        dicSide = {}
        for ctrl in dicCtrl[zone]:
            side = mc.getAttr(ctrl+'.mirrorSide', asString=True)
            if not side in dicSide.keys():
                dicSide[side] = []
            dicSide[side].append(ctrl)

        for ctrl in dicCtrl[zone]:
            for shp in dicShp[zone]:
                side = 'middle'
                if shp.endswith('_L'):
                    side = 'left'
                elif shp.endswith('_R'):
                    side = 'right'

                posShp = mc.xform(shp, q=True, ws=True, t=True)
                chan = mc.getAttr(shp+'.ctrlChan')

                if chan != '//':
                    lDriver = dicSide[side]
                    driver = lDriver[0]
                    if len(lDriver)>1:
                        if mc.attributeQuery('sepSlice', n=shp, ex=True):
                            iter = mc.getAttr(shp+'.sepSlice', s=True)
                            toFind = ''
                            for i in range(0, iter):
                                slice = mc.getAttr(shp+'.sepSlice['+str(i)+']')
                                if slice == 'Dn':
                                    toFind+='Down'
                                elif slice == 'Mid':
                                    toFind+='Middle'
                                elif slice == 'Up':
                                    toFind+='Up'
                                elif slice == 'Int':
                                    toFind+='Int'
                                elif slice == 'Ext':
                                    toFind+='Ext'
                            for zizilol in lDriver:
                                if toFind in zizilol:
                                    driver = zizilol


                    dVal = 0
                    limChan = ''
                    val = 0
                    sign = 1
                    if mc.getAttr(shp+'.negativeChan') == 1:
                        sign = -1

                    if 'translate' in chan:
                        tpl = mc.listConnections(driver+'.ctrlZone', s=True)[0]
                        vtx = int(mc.getAttr(tpl+'.vtxId'))
                        if side == 'right':
                            if chan.endswith('X'):
                                sign = sign*-1
                            if vtx in dicSym.keys():
                                suce = vtx
                                vtx = dicSym[suce]


                        vtxSrc = mc.xform(mshBase+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                        vtxDest = mc.xform(shp+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)

                        difPos = [posShp[0]-posBase[0], posShp[1]-posBase[1], posShp[2]-posBase[2]]
                        difVtx = [vtxDest[0]- difPos[0], vtxDest[1]- difPos[1], vtxDest[2]- difPos[2]]
                        vtxPos = [abs(difVtx[0]- vtxSrc[0]), abs(difVtx[1]- vtxSrc[1]), abs(difVtx[2]- vtxSrc[2])]

                        val = vtxPos[0]
                        if chan.endswith('Y'):
                            val = vtxPos[1]
                        if chan.endswith('Z'):
                            val = vtxPos[2]
                        limChan = 'Trans'+chan[-1]+'Limit'

                    elif 'rotate' in chan:
                        limChan = 'Rot'+chan[-1]+'Limit'
                        if 'Down' in ctrl:
                            if chan.endswith('X'):
                                sign = sign*-1
                        val = 45

                    elif 'scale' in chan:
                        limChan = 'Scale'+chan[-1]+'Limit'
                        val = 3
                        dVal = 1


                    if mc.attributeQuery(shp.split(':')[-1], n=bs, ex=True):
                        mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=dVal, v=0)
                        mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=1*sign, v=1)
                    dKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True)[0]
                    if dKey:
                        if val>0 :
                            mc.setAttr(dKey+'.postInfinity', 4)
                            #mc.setAttr(ctrl+'.max'+limChan+'Enable', 1)
                            #mc.setAttr(ctrl+'.max'+limChan, val)
                        elif val<0:
                            mc.setAttr(dKey+'.preInfinity', 4)
                            #mc.setAttr(ctrl+'.min'+limChan+'Enable', 1)
                            #mc.setAttr(ctrl+'.min'+limChan, val)




#connectFaceRig_v2()



def connectFaceRig_v2():
    lMovedVtx = []
    dicNeutGeoVtx = {}
    dicTrgtGeoVtxDif = {}
    dicTrgtGeoVtx = {}
    roof = 0.0
    dicShp = {}
    dicCtrl = {}
    dicSym = {}
    base = ''
    enAttr = ''

    #list templates
    lFaceTpl = mc.ls('*.tplZone', o=True)

    #list shapes
    lShp = mc.ls('*.sepZone',r=True, o=True)

    #get blendShape
    lHist = mc.listHistory(lShp[0], f=True)
    bs = mc.ls(lHist, type='blendShape')[0]

    #get neutral
    mshBase = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
    posBase = mc.xform(mshBase, q=True, ws=True, t=True)
    vtxs = mc.polyEvaluate(mshBase, v=True)

    #get neutralGeo transform position
    posSrc = posBase
    for vtx in range(0, vtxs):
        posVtx = mc.xform(mshBase+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
        dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]
    dicTrgt = lib_names.trgtNames()

    #generate controlGroup basep on head separation
    for shp in lShp:
        zone = mc.getAttr(shp+'.sepZone', asString=True)
        if not zone in dicShp.keys():
            dicShp[zone] = []
            cg = 'cg_'+zone
            if mc.objExists(cg):
                dicCtrl[zone] = mc.listConnections(cg+'.members', s=True, d=False)
        dicShp[zone].append(shp)

    #init sym dic
    iter = mc.getAttr(mshBase+'.symTabLeft', s=True)
    for i in range(0, iter):
        dicSym[mc.getAttr(mshBase+'.symTabLeft['+str(i)+']')] = mc.getAttr(mshBase+'.symTabRight['+str(i)+']')

    for zone in dicCtrl.keys():
        dicSide = {}
        for ctrl in dicCtrl[zone]:
            side = mc.getAttr(ctrl+'.mirrorSide', asString=True)
            if not side in dicSide.keys():
                dicSide[side] = []
            dicSide[side].append(ctrl)
        for ctrl in dicCtrl[zone]:
            for shp in dicShp[zone]:
                side = 'middle'
                if shp.endswith('_L'):
                    side = 'left'
                elif shp.endswith('_R'):
                    side = 'right'
                posShp = mc.xform(shp, q=True, ws=True, t=True)
                chan = mc.getAttr(shp+'.ctrlChan')
                lDriver = dicSide[side]
                driver = lDriver[0]
                if len(lDriver)>1:
                    if mc.attributeQuery('sepSlice', n=shp, ex=True):
                        iter = mc.getAttr(shp+'.sepSlice', s=True)
                        toFind = ''
                        for i in range(0, iter):
                            slice = mc.getAttr(shp+'.sepSlice['+str(i)+']')
                            if slice == 'Dn':
                                toFind+='Down'
                            elif slice == 'Mid':
                                toFind+='Middle'
                            elif slice == 'Up':
                                toFind+='Up'
                            elif slice == 'Int':
                                toFind+='Int'
                            elif slice == 'Ext':
                                toFind+='Ext'
                        for zizilol in lDriver:
                            if toFind in zizilol:
                                driver = zizilol
                dVal = 0
                limChan = ''
                val = 0
                sign = 1
                if mc.getAttr(shp+'.negativeChan') == 1:
                    sign = -1
                if 'translate' in chan:
                    tpl = mc.listConnections(driver+'.ctrlZone', s=True)[0]
                    vtx = int(mc.getAttr(tpl+'.vtxId'))
                    if side == 'right':
                        if chan.endswith('X'):
                            sign = sign*-1
                        if vtx in dicSym.keys():
                            suce = vtx
                            vtx = dicSym[suce]
                    vtxSrc = mc.xform(mshBase+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                    vtxDest = mc.xform(shp+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                    difPos = [posShp[0]-posBase[0], posShp[1]-posBase[1], posShp[2]-posBase[2]]
                    difVtx = [vtxDest[0]- difPos[0], vtxDest[1]- difPos[1], vtxDest[2]- difPos[2]]
                    vtxPos = [abs(difVtx[0]- vtxSrc[0]), abs(difVtx[1]- vtxSrc[1]), abs(difVtx[2]- vtxSrc[2])]
                    val = vtxPos[0]
                    if chan.endswith('Y'):
                        val = vtxPos[1]
                    if chan.endswith('Z'):
                        val = vtxPos[2]
                    limChan = 'Trans'+chan[-1]+'Limit'
                elif 'rotate' in chan:
                    limChan = 'Rot'+chan[-1]+'Limit'
                    if 'Down' in ctrl:
                        if chan.endswith('X'):
                            sign = sign*-1
                    val = 45
                elif 'scale' in chan:
                    limChan = 'Scale'+chan[-1]+'Limit'
                    val = 3
                    dVal = 1
                if mc.attributeQuery(shp.split(':')[-1], n=bs, ex=True):
                    print shp, driver,  val, dVal, sign
                    mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=dVal, v=0)
                    mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=val*sign, v=2)
                dKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True)[0]

                if dKey:
                    if val>0 :
                        mc.setAttr(dKey+'.postInfinity', 4)
                        mc.setAttr(ctrl+'.max'+limChan+'Enable', 1)
                        mc.setAttr(ctrl+'.max'+limChan, val)
                    elif val<0:
                        mc.setAttr(dKey+'.preInfinity', 4)
                        mc.setAttr(ctrl+'.min'+limChan+'Enable', 1)
                        mc.setAttr(ctrl+'.min'+limChan, val)


    for shp in lShp:
        #get trgtGeo transform position
        postrgtGeo = mc.xform(shp, q=True, ws=True, t=True)
        #GET ROOf VAL FOR THE NORMALIZATION
        for vtx in range(0, vtxs):
            #get position of vtx
            posVtxtrgtGeo = mc.xform(shp+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
            #remove transform pos from vtx pos (set to world 0, 0, 0)
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
        ratio = 1/roof
        for vtx in lMovedVtx:
            norm = [0.0, 0.0, 0.0]

            norm[0] = ratio*(dicNeutGeoVtx[vtx][0] - dicTrgtGeoVtx[vtx][0])+dicTrgtGeoVtx[vtx][0]+posSrc[0]
            norm[1] = ratio*(dicNeutGeoVtx[vtx][1] - dicTrgtGeoVtx[vtx][1])+dicTrgtGeoVtx[vtx][1]+posSrc[1]
            norm[2] = ratio*(dicNeutGeoVtx[vtx][2] - dicTrgtGeoVtx[vtx][2])+dicTrgtGeoVtx[vtx][2]+posSrc[2]

            mc.move(norm[0], norm[1], norm[2], shp+'.vtx['+str(vtx)+']')

#connectFaceRig()


##UI#####################################################################################################################################################################
def smfaddTarget_ui(lNeutral):
    nWin = 'SMF_addTrgt'
    nPan = 'MASTER_panSmab'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_publishTool_UI = mc.window(nWin, t='facialShapes'+version, tlb=True)

    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout('GENERATE_SCENE', adj=True, w=225)

    mc.rowLayout(nc=2, adj=2)
    nTrgtType = mc.optionMenu('trgtTypes', label='Prefix         :')
    dicTrgt = lib_names.trgtNames()
    for key in sorted(dicTrgt.keys()):
        mc.menuItem( label=key+'   :  '+dicTrgt[key]+'_')

    mc.setParent('..')
    mc.rowLayout(nc=3, adj=3)
    mc.text('trgt name : ', al='left', font='boldLabelFont', h=12)
    mc.separator(h=2)
    mc.textField('newTrgtName', h=20)

    mc.setParent('..')
    mc.rowLayout(nc=3, adj=3)
    mc.text('attr name : ', al='left', font='boldLabelFont', h=12)
    mc.separator(h=2)
    mc.textField('newAttrName', h=20)
    mc.setParent('..')
    mc.button(label='add', c='tools_facialShapes.addTrgt(mc.ls(sl=True), "c_targets")')

    mc.showWindow(winSMF_publishTool_UI)
#smfaddTarget_ui()


def smfBlendShapesTool_ui():
    nWin = 'SMF_publishTool'
    nPan = 'MASTER_pan'
    version ='1.1'
    nNewCGName = 'getNewCGName'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_publishTool_UI = mc.window(nWin, t='facialShapes'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tool', c='')
    mc.separator(h=2)
    ######
    pan = mc.paneLayout(nPan, cn='vertical3', w=450)
    ######
    mc.tabLayout('MASTER_tab')
    mc.columnLayout('MODELING', adj=True, w=225)
    mc.separator(h=7.5, st='in')


    mc.frameLayout(l='Scene', cll=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='LOAD MOD    ', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.loadMOD()')
    mc.button(l='UNLOAD MOD', bgc=[1,.25,.5], h=28, w=230, c='tools_facialShapes.unloadMOD()')
    #
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='1. GEN NEUTRAL', h=28, w=230, c='tools_facialShapes.generateNeutral(mc.ls(sl=True))')
    mc.button(l='2. LINK BS', h=28, w=230, c='tools_facialShapes.linkTargets("c_targets", mc.ls(sl=True))')
    mc.setParent('..')
    mc.button( label='SAVE SCENE', w=100)
    mc.separator(h=10, st='in')
    #
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.columnLayout(adj=True, w=200)
    mc.button(l='LOAD TARGETS', h=28, w=230, c='tools_facialShapes.loadTrgt(mc.ls(sl=True))')
    mc.rowLayout(nc=2, adj=1)
    mc.textScrollList('targetsList', numberOfRows=8, ams=True, h=500, w=150, dcc='tools_facialShapes.isolateTrgt()')
    mc.popupMenu(b=3, mm=False, aob=True)
    mc.menuItem(l='Isolate trgts', c='tools_facialShapes.isolateTrgt()')
    mc.menuItem(l='Select trgts', c='tools_facialShapes.selTrgt()')
    mc.menuItem(l='Show all trgts', c='tools_facialShapes.showAllTrgt()')
    mc.menuItem(divider=True)
    mc.menuItem(l='Refresh', c='tools_facialShapes.refreshTrgt()')
    mc.menuItem(l='Clear', c='for i in ["targetsList", "targetsChan"]:mc.textScrollList(i, e=True, ra=True)')

    #mc.frameLayout(l='Chans', cll=True)
    mc.textScrollList('targetsChan', numberOfRows=8, ams=True, h=500, w=50)
    mc.popupMenu(b=3, mm=False, aob=True)

    mc.menuItem(l='set chan tX', c='tools_facialShapes.setChannel("translateX")')
    mc.menuItem(l='set chan tY', c='tools_facialShapes.setChannel("translateY")')
    mc.menuItem(l='set chan tZ', c='tools_facialShapes.setChannel("translateZ")')

    mc.menuItem(l='set chan rX', c='tools_facialShapes.setChannel("rotateX")')
    mc.menuItem(l='set chan rY', c='tools_facialShapes.setChannel("rotateY")')
    mc.menuItem(l='set chan rZ', c='tools_facialShapes.setChannel("rotateZ")')

    mc.menuItem(l='set chan sX', c='tools_facialShapes.setChannel("scaleX")')
    mc.menuItem(l='set chan sY', c='tools_facialShapes.setChannel("scaleY")')
    mc.menuItem(l='set chan sZ', c='tools_facialShapes.setChannel("scaleZ")')

    mc.menuItem(divider=True)
    mc.menuItem(l='Invert sign (+/-)', c='tools_facialShapes.invertSign()')
    mc.menuItem(l='set no chan', c='tools_facialShapes.setChannel("None")')
    ##
    #mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout('bsTools', adj=True, w=225)
    mc.button(l='SELECT CTRL', h=28, w=110, c='mc.select("c_targets")')
    mc.button(l='CHEKER ON/OFF', h=28, w=110, c='print "ziziLol"')



    mc.separator(h=10, st='in')
    mc.frameLayout(l='Trgt Tools', cll=True)
    mc.columnLayout('bsTools', adj=True, w=225)

    mc.rowLayout(nc=2)
    mc.button(l='ADD TRGT', h=28, w=110, c='tools_facialShapes.smfaddTarget_ui(mc.ls(sl=True))')
    mc.button(l='REMOVE TRGT', h=28, w=110, c='')

    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='DUPPLCATE SHP', h=28, w=110, c='tools_facialShapes.dupShp(mc.ls(sl=True))')
    mc.button('switch_neutralTrgt', l='NEUTRAL/TRGT', h=28, w=110, c='tools_facialShapes.showNeutral()')

    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='TRANSFER TO', h=28, w=110, c='tools_facialShapes.snapShp(mc.ls(sl=True))')
    mc.button(l='RESET', h=28, w=110, c='tools_facialShapes.resetShp(mc.ls(sl=True))')

    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='Cor Tools', cll=True)
    mc.rowLayout(nc=2)
    mc.button(l='bake corrective to all', h=28, w=110, c='')
    mc.button(l='extract msh pos', h=28, w=110, c='tools_facialShapes.exctractPose(mc.ls(sl=True))')

    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='Mix Tools', cll=True)
    mc.rowLayout(nc=2)
    mc.button(l='gen mix sculpt', h=28, w=110, bgc=[.05,.2,.5], c='tools_facialShapes.genMixSculpt(mc.ls(sl=True))')
    mc.button(l='connect mix shape', h=28, w=110, bgc=[.05,.05,.5], c='tools_facialShapes.connectMixShp(mc.ls(sl=True))')

    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='unactive mix', h=28, w=110, c='print "to do"')
    mc.button(l='update mix shape', h=28, w=110, c='print "to do"')
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='select mix sculpt', h=28, w=110, c='tools_facialShapes.genMixSculpt(mc.ls(sl=True))')
    mc.button(l='select mix trgt', h=28, w=110, c='tools_facialShapes.connectMixShp(mc.ls(sl=True))')
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='set mix pose', h=28, w=110, c='tools_facialShapes.genMixSculpt(mc.ls(sl=True))')
    mc.button(l='remove mix trgt', h=28, w=110, c='tools_facialShapes.connectMixShp(mc.ls(sl=True))')
    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='rig Tools', cll=True)
    mc.rowLayout(nc=2)
    mc.button(l='gen rig', h=28, w=110, c='')
    mc.button(l='update rig', h=28, w=110, c='')



    ###################################################################################################################
    ###################################################################################################################

    mc.columnLayout('SEPARATION', adj=True, w=225, p='MASTER_tab')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='References', cll=True)
    mc.button(l='load TRGT', h=28, w=110, c='tools_facialShapes.loadTrgtRef()')
    mc.button(l='init SEP', h=28, w=110, c='tools_facialShapes.genSepZones(mc.ls(sl=True)[0])')
    mc.button(l='maj Preweighting', h=28, w=110, c='tools_facialShapes.majSepBaseWght()')

    mc.setParent('..')
    mc.separator(h=7.5, st='in')


    mc.frameLayout(l='Sep Tools', cll=True)
    mc.rowLayout(nc=2, adj=1)
    nTrgtType = mc.optionMenu('sepZone', label='face zone  :')
    dicTrgt = lib_names.trgtNames()
    mc.menuItem( label='None')
    for key in sorted(dicTrgt.keys()):
        mc.menuItem(label=key)



    nTrgtType = mc.optionMenu('sepType', label='separation type  :')
    mc.menuItem( label='None')
    mc.menuItem( label='Left')
    mc.menuItem( label='Right')
    mc.menuItem( label='Middle')
    mc.menuItem( label='Up')
    mc.menuItem( label='Down')
    mc.menuItem( label='Ext')
    mc.menuItem( label='Int')
    mc.menuItem( label='Corner')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD SEP', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.buildSep(mc.ls(sl=True), [mc.optionMenu("sepZone", q=True, v=True)], [mc.optionMenu("sepType", q=True, v=True)])')
    mc.button(l='SEL CTRL', bgc=[.25,.2,.5], h=28, w=230, c='mc.select("TRGT:c_targets")')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Weights Tools', cll=True)
    mc.rowLayout(nc=2, adj=1)

    mc.button(l='COPY WGHT TO', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.copyBsWghtTo(mc.ls(sl=True))')
    mc.button(l='REVERSE WGHT', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.invertBsWghtTo(mc.ls(sl=True))')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='BUILD SYM MAP', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.crtSymAttr(mc.ls(sl=True))')
    mc.button(l='FLIP WGHT', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.flipBsWght(mc.ls(sl=True))')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD WGHT TO', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.addBsWghtTo(lObj)')
    mc.button(l='Smab', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.mirrorBsWght(mc.ls(sl=True), "R")')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='MIRROR WGHT R <-- L', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.mirrorBsWght(mc.ls(sl=True), "L")')
    mc.button(l='MIRROR WGHT R --> L', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.mirrorBsWght(mc.ls(sl=True), "R")')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='CHECK', cll=True)
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='create sepCheaker', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.crtSepChecker(mc.ls(sl=True))')
    mc.button(l='delete sepCheaker', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.crtSepChecker(mc.ls(sl=True))')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Adds', cll=True)
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='wrap to', h=28, w=110, c='tools_facialShapes.connectNeutralWrap(mc.ls(sl=True))')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Template', cll=True)
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='create Tpl', bgc=[.25,.2,.0], h=28, w=230, c='tools_facialShapes.genTpl(mc.ls(sl=True))')
    mc.button(l='update Tpl', bgc=[.25,.2,.5], h=28, w=230, c='')
    mc.button(l='report Tpl to neutral', bgc=[.25,.2,.5], h=28, w=230, c='tools_facialShapes.connTplToNeutral()')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Finish', cll=True)
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='EXTRACT SHAPES', bgc=[.2,.2,.5], h=28, w=230, c='tools_facialShapes.extractShapes()')

    ###################################################################################################################
    ###################################################################################################################

    mc.columnLayout('BUILD', adj=True, w=225, p='MASTER_tab')
    mc.separator(h=7.5, st='in')

    mc.frameLayout(l='Face Rig', cll=True)
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='template face', h=28, w=110, c='tools_facialShapes.setFaceTpl()')
    mc.button(l='build face', h=28, w=110, c='tools_facialShapes.buildFaceTpl()')
    mc.button(l='connect face', h=28, w=110, c='tools_facialShapes.connectFaceRig()')

    mc.setParent('..')
    mc.separator(h=7.5, st='in')


    mc.showWindow(winSMF_publishTool_UI)
#smfBlendShapesTool_ui()

