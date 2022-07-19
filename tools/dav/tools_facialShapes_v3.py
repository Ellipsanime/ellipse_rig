import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OpenMaya

import math, os, glob, re
from functools import partial
from importlib import import_module
from ellipse_rig.icons import ic_datas
reload(ic_datas)

from ellipse_rig.prod_pressets import global_presets
reload(global_presets)
from ellipse_rig.library import lib_namespace as lNspace
reload(lNspace)
from ellipse_rig.library import lib_deformers, lib_pipe, lib_names,lib_namespace, lib_controlGroup, lib_blendShape, lib_checkers
reload(lib_deformers)
reload(lib_pipe)
reload(lib_names)
reload(lib_namespace)
reload(lib_controlGroup)
reload(lib_blendShape)
reload(lib_checkers)
from ellipse_rig.core import project_manager, scene_manager, debbug
reload(project_manager)
reload(debbug)

import tools_facialChanSliders
reload(tools_facialChanSliders)






def faceDescription():
    faceDatas = global_presets.faceDatas()
    prod = project_manager.getProject()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        faceDatas = module.faceDatas()
        print ('get face description for', prod)
    return faceDatas

#PRESSETS
###################################################
def trgtNames():
    dicTrgt = {}
    #dicTrgt['none'] = ''
    dicTrgt['cheeks'] = 'ch'
    dicTrgt['eyebrows'] = 'eb'
    dicTrgt['eyelids'] = 'el'
    dicTrgt['ears'] = 'er'
    dicTrgt['jaw'] = 'jw'
    dicTrgt['lips'] = 'li'
    dicTrgt['mouth'] = 'mo'
    dicTrgt['nose'] = 'no'
    return dicTrgt

def sepSlices():
    dicSlices = {}
    #dicSlices['none'] = ''
    #dicTrgt['Left'] = 'Lt'
    #dicTrgt['Right'] = 'Rt'
    dicSlices['Middle'] = 'Mid'
    dicSlices['Up'] = 'Up'
    dicSlices['Down'] = 'Dn'
    dicSlices['Ext'] = 'Ext'
    dicSlices['Int'] = 'Int'
    dicSlices['Corner'] = 'Corn'
    return dicSlices


def listOfShapes():
    #EYEBROWS##################################################
    dicEyebrows = {}
    dicEyebrows['ebSlide'] = ['eb_slide_up', 'eb_slide_dn']
    dicEyebrows['ebTwistInt'] = ['eb_intTwist_up', 'eb_intTwist_dn']
    dicEyebrows['ebTwistExt'] = ['eb_extTwist_up', 'eb_extTwist_dn']
    dicEyebrows['ebSqueeze'] = ['eb_squeeze']
    dicEyebrows['ebWrinkle'] = ['eb_wrinkle']
    #EYELIDS###################################################
    dicEyelids = {}
    dicEyelids['elSlide'] = ['el_slide_up', 'el_slide_dn']
    dicEyelids['elTwist'] = ['el_twist_in', 'el_twist_out']
    dicEyelids['elConcealar'] = ['el_Concealar']
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
    dicMouth['mOpen'] = ['mo_open']
    dicMouth['mCornerTwist'] = ['mo_cornerTwistDn', 'mo_cornerTwistUp']
    dicMouth['mCornerStrech'] = ['mo_cornerPinch', 'mo_cornerSpacing']


    #LIPS######################################################
    dicLips = {}
    dicLips['lRoll'] = ['li_rollIn', 'li_rollOut']
    dicLips['lPush'] = ['li_pushIn', 'li_pushOut']
    dicLips['lPinch'] = ['li_pinch']
    dicLips['lSlide'] = ['li_raiser', 'li_lower']
    dicLips['lPuff'] = ['li_puffIn', 'li_puffOut']
    dicLips['lU'] = ['li_uRaiser', 'li_uLower']
    dicLips['lSlipe'] = ['li_slipeLt', 'li_slipeRt']
    dicLips['lTwist'] = ['li_twistUp', 'li_twistDn']
    ###########################################################
    dicShapes = {'dicMouth':dicMouth, 'dicEyebrows':dicEyebrows, 'dicLips':dicLips, 'dicCheeks':dicCheeks, 'dicNose':dicNose, 'dicEyelids':dicEyelids}

    return dicShapes

#listOfShapes()
#neutral =  mc.ls(sl=True)[0]
#ctrlAttr('c_targets', dicMouth, neutral)
#ctrlAttr('c_targets', dicLips, neutral)
#ctrlAttr('c_targets', dicCheeks, neutral)
#ctrlAttr('c_targets', dicNose, neutral)
#ctrlAttr('c_targets', dicEyelids, neutral)
#ctrlAttr('c_targets', dicEyebrows, neutral)


def trgtToCtrlChan():
    dicChans = {}
    dicChansPositive = {}
    dicChansNegative = {}

    #EYEBROWS##################################################
    dicChansPositive['eb_slide_up'] = 'translateY'   #+
    dicChansNegative['eb_slide_dn'] = 'translateY'   #-
    dicChansNegative['eb_squeeze'] = 'translateX'    #-
    dicChansPositive['eb_wrinkle'] = 'scaleZ'        #+

    dicChansPositive['eb_intTwist_dn'] = 'rotateZ'   #+
    dicChansNegative['eb_intTwist_up'] = 'rotateZ'   #-
    dicChansNegative['eb_extTwist_dn'] = 'rotateZ'   #-
    dicChansPositive['eb_extTwist_up'] = 'rotateZ'   #+
    #EYELIDS###################################################
    dicChansPositive['el_slide_up'] = 'translateY' #+
    dicChansNegative['el_slide_dn'] = 'translateY' #-

    dicChansPositive['el_twist_in'] = 'rotateZ'    #+
    dicChansNegative['el_twist_out'] = 'rotateZ'   #-
    dicChansPositive['el_Concealar'] = 'scaleZ'    #+

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
    dicChansNegative['mo_cornerPinch'] = 'scaleY'  #+
    dicChansPositive['mo_cornerSpacing'] = 'scaleY'  #-

    dicChansPositive['mo_cornerTwistUp'] = 'rotateZ'#+
    dicChansNegative['mo_cornerTwistDn'] = 'rotateZ'#-
    dicChans['mo_open'] = ''
    #LIPS######################################################
    dicChansPositive['li_rollIn'] = 'rotateX'     #+
    dicChansNegative['li_rollOut'] = 'rotateX'    #-
    dicChansNegative['li_pushIn'] = 'translateZ'  #-
    dicChansPositive['li_pushOut'] = 'translateZ' #+
    dicChansNegative['li_pinch'] = 'scaleY'       #-
    dicChansPositive['li_raiser'] = ''  #
    dicChansNegative['li_lower'] = ''   #
    dicChansPositive['li_puffOut'] = 'scaleZ'     #+
    dicChansNegative['li_puffIn'] = 'scaleZ'      #-
    dicChansPositive['li_uRaiser'] = 'translateY'    #+
    dicChansNegative['li_uLower'] = 'translateY'     #-
    dicChansPositive['li_slipeLt'] = 'translateX' #+
    dicChansNegative['li_slipeRt'] = 'translateX' #-
    dicChansPositive['li_twistUp'] = 'rotateZ'        #+
    dicChansNegative['li_twistDn'] = 'rotateZ'      #-

    dicChans = {'positive':dicChansPositive, 'negative':dicChansNegative}
    return dicChans

def listSel():
    return mc.ls(sl=True, fl=True)

def launchDagHack(*args, **kwargs):
    import sys
    pathDir = os.path.dirname(__file__)
    pathCustom = pathDir.split('\\tools\\')[0]
    #pathCustom ='T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig'
    sys.path.append(pathCustom)
    import dagMenuHack
    reload(dagMenuHack)

def refreshScn(*args, **kwargs):
    mc.dgdirty(a=True)
    print 'scene flushed',


def displayHandles(getSel, *args, **kwargs):
    lNodes = getSel()
    lVal = []
    for node in lNodes:
        val = mc.getAttr(node+'.displayHandle')
        if not val in lVal:
            lVal.append(val)
    if len(lVal)!= 1:
        for node in lNodes:
            mc.setAttr(node+'.displayHandle', 1)

    else:
        val = mc.getAttr(lNodes[0]+'.displayHandle')
        for node in lNodes:
            if val == 0:
                mc.setAttr(node+'.displayHandle', 1)
            elif val == 1:
                mc.setAttr(node+'.displayHandle', 0)

def resetChans(lNodes):
    lTrgt = []
    if not lNodes:
        lNodes = mc.ls('*.resultMsh', r=True, o=True)
    for node in lNodes:
        if mc.getAttr(node+'.resultMsh') == 'TRGT':
            if not mc.attributeQuery('isInBet', n=node, ex=True):
                lTrgt.append(node)
    dicChans = trgtToCtrlChan()
    for trgt in lTrgt:
        presetTplFaceChan(trgt, dicChans)
#resetChans(mc.ls(sl=True) or [])

def crtPanel(*args, **kwargs):
    mc.window()
    mc.frameLayout(lv=0)
    mc.modelPanel()
    mc.showWindow()
#UTILES#################################################################################################################################################################################
def getBsDef(obj, type, *args):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mixTrgt     #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    #_________________#
    lBs = mc.ls(type='blendShape')
    #print 'HERE pecore :', obj, type, lBs
    lCon = lBs
    if obj:
        lBs = []
        lCon = []
        lHist = mc.listHistory(obj, ac=True)
        #print 'hist :', lHist
        lBs = mc.ls(lHist, type='blendShape')
        #print lBs
        #shp = mc.listRelatives(obj, s=True, ni=True)[-1]
        #print shp
        #lCon = mc.listConnections(shp, scn=True)

    if type == None:
        return lBs
    else:
        lToKeep = []
        #print type, lBs
        for bs in lBs:
            #print 'tutu :', bs
            if mc.attributeQuery('bsType', n=bs, ex=True):
                if mc.getAttr(bs+'.bsType') == type:
                    #print type, 'founded'
                    geo = ''
                    try:
                        geo = mc.blendShape(bs, q=True, g=True)[0]
                    except:
                        pass
                    if geo:
                        if obj and geo:
                            activeDef(geo, False)
                            activeDef(obj, False)
                            #print 'HAAAAA :', geo, obj
                            if mc.polyCompare(geo, obj, fd=True)  in [0, 8, 16, 24]:
                                #print "topo match"
                                lToKeep.append(bs)
                            activeDef(geo, True)
                            activeDef(obj, True)
                        else:
                            #print "no obj founded"
                            lToKeep.append(bs)
                    else:
                        mc.warning('bs '+bs+' is alone, plz clean him')
        if lToKeep:
            return lToKeep
        else:
            return mc.warning('no bs found or no mesh corresponding found')
#getBsDef(mc.ls(sl=True)[0])

def cleanBs(*args, **kwargs):
    lBs = []
    bsCor = getBsDef(None, 1) or []
    bsMix = getBsDef(None, 2) or []
    if bsCor:
        lBs.append(bsCor[0])
    if bsMix:
        lBs.append(bsMix[0])
    lCleaned = []
    for bs in lBs:
        lWght = mc.aliasAttr(bs, q=True) or []
        if not lWght:
            print 'cleaning', bs
            lCleaned.append(bs)
            shp = mc.blendShape(bs, q=True, g=True)[0]
            mshTrgt = mc.listRelatives(shp, p=True)[0]
            shpDatas = getTrgtMshDatas(mshTrgt)
            bsRes = shpDatas[mshTrgt]['bs']
            wght = shpDatas[mshTrgt]['weight']
            id = shpDatas[mshTrgt]['id']
            mshRes = mc.blendShape(bsRes, q=True, g=True)[0]

            nspace = lib_namespace.getNspaceFromObj(mshTrgt)

            mc.blendShape(bsRes, e=True, rm=True, t=(mshRes, id, mshTrgt, wght))
            mc.delete([bs, mshTrgt])
            lNodes = mc.ls(nspace + ':*', r=True) or []
            if lNodes:
                mc.delete(lNodes)
            lNspace = lib_namespace.lsAllNspaceOf(nspace)
            for nspaceChild in lNspace:
                lToDel = mc.ls(nspaceChild+':*', r=True) or []
                mc.delete(lToDel)
                lib_namespace.removeNspace(nspaceChild, keep=False)
            lib_namespace.removeNspace(nspace, keep=False)
    print 'empty blendShapes cleaned :', lCleaned





def getBsTrgt(type):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
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
    if mc.objectType(shp) == 'transform':
        shp = mc.listRelatives(shp, s=True, ni=True)[-1]
    lDef = mc.findDeformers(shp)
    if lDef:
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
    mc.connectAttr(dupShd+'.outColor', dupShdSG+'.surfaceShader')
    return dupShdSG
#dupShd(shdSG)

def crtNspace(obj, nsFather = ''):
    baseNspace = obj[len(obj.split('_')[0])+1:]
    nspace = baseNspace.upper()
    if not mc.namespace(ex=':'+nsFather):
        mc.namespace(add=nsFather, parent=':')
    if not mc.namespace(ex=':'+nsFather + ':'+ nspace):
        mc.namespace(add=nspace, parent=':'+nsFather + ':')
    nspace = mc.namespace(set=':'+nsFather + ':' + nspace)
    return nspace
#crtNspace('neutral_head', 'TRGT')

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
    # 3 = result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    #_________________#
    if not mc.attributeQuery('bsType', n=bs, ex=True):
        mc.addAttr(bs, ln='bsType', at='enum', en='Trgt:Cor:MixTrgt:Res:Shp:MixShp', dv=type)
#bsTypeAttrr(mc.ls(sl=True)[0], 1)

def getActivTrgt(bs):
    dicTrgt = {}
    lTrgt = mc.blendShape(bs, q=True, t=True) or []
    for trgt in lTrgt:
        if ':' in trgt:
            trgt = trgt.split(':')[-1]
        if mc.attributeQuery(trgt, n=bs, ex=True):
            if not mc.getAttr(bs+'.'+trgt, l=True):
                if mc.getAttr(bs+'.'+trgt, k=True):
                    if mc.listConnections(bs+'.'+trgt, s=True):
                        val = mc.getAttr(bs+'.'+trgt)
                        if val > 0.0001:
                            dicTrgt[trgt] = val
    #print 'HERE lTRGR :', dicTrgt
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

def genNspace(nspace):
    mc.namespace(set=':')
    if not mc.namespace(ex=nspace):
        mc.namespace(add=nspace, parent=':')
    mc.namespace(set=':' + nspace)

#genNspace('TRGT')

def geStorageGrp(type, msh, extra=''):
    nspace = crtNspace(msh, nsFather=type)
    nStorageGrp = 'geo_'+type.lower()+extra
    if not mc.objExists(nspace+':'+nStorageGrp):
        mc.createNode('transform', n=nStorageGrp)
    return nspace+':'+nStorageGrp

def unlockChans(node):
    for attr in ('translate', 'rotate', 'scale'):
        for chan in ['X', 'Y', 'Z']:
            mc.setAttr(node+'.'+attr+chan, lock=False)

def getLastInputId(bs):
    chkId = mc.getAttr(bs+'.inputTarget[0].inputTargetGroup', mi=True) or []
    lastId = -1
    if chkId:
        lastId = chkId[-1]
    return lastId
#getLastInputId('bsTrgtr_head')


def getTrgtFromNeutral(neutral):
    bs = getBsDef(neutral, 0)
    lTrgt = getTrgt(bs)
    return lTrgt

def removeCustomAttrs(lNodes):
    for node in lNodes:
        lAttrs = mc.listAttr(node, ud=True) or []
        if lAttrs:
            for attr in lAttrs:
                if mc.attributeQuery(attr, n=node, ex=True):
                    mc.setAttr(node+'.'+attr, l=False)
                    mc.deleteAttr(node+'.'+attr)
#removeCustomAttrs(mc.ls(sl=True))

def addExtractMeAttr(getSel, *args, **kwargs):
    lSep = getSel()
    for sep in lSep:
        if not mc.attributeQuery('extractMe', n=sep, ex=True):
            mc.addAttr(sep, ln='extractMe', at='bool', dv=True)
        else:
            mc.setAttr(sep+'.extractMe', True)
#addExtractMeAttr(mc.ls(sl=True))

def getAttrIds(node,attr):
    lIndexs = []
    lInputs = mc.getAttr(node+'.'+attr, mi=True) or []
    if lInputs:
        for i in lInputs:
            lIndexs.append(int(i))
    return lIndexs
#getAttrIds('bs_head', 'weight')

def getAvalableId(node, attr):
    lastId = 0
    lIds = mc.getAttr(node+'.'+attr, mi=True) or []
    if lIds:
        lastId = lIds[-1]+1
    return lastId

def genDicTrgtIds(bs):
    lWght = mc.aliasAttr(bs, q=True) or []
    if lWght:
        i = 0
        dicTrgtIds = {}
        for suce in range(0, len(lWght)/2):
            dicValues = {}
            dicValues['attr'] = lWght[i]
            dicValues['index'] = lWght[i+1][len(lWght[i+1].split('[')[0])+1:-1]
            chkInBet = mc.getAttr(bs+'.inputTarget[0].inputTargetGroup['+dicValues['index']+'].inputTargetItem', s=True)
            if chkInBet < 1:
                print 'theire is a inbeteween here'
                return
            #print 'HERE BS ADD :', bs
            shp = mc.listConnections(bs+'.inputTarget[0].inputTargetGroup['+dicValues['index']+'].inputTargetItem['+'6000'+'].inputGeomTarget', s=True) or []
            if shp:
                if not shp[0] in dicTrgtIds.keys():
                    dicTrgtIds[shp[0]] = {}
                dicTrgtIds[shp[0]] = dicValues
            i += 2
        return dicTrgtIds

#genDicTrgtIds('bs_headTeste')

#UI FONCTIONS#################################################################################################################################################################################
def getTrgt(bs):
    lTrgt = mc.blendShape(bs[0], q=True, t=True)
    return lTrgt
#getTrgt('bs_head')

def loadTrgt(getSel, *args, **kwargs):
    chkSel = getSel()
    obj = []
    if chkSel:
        obj = chkSel[0]
    mc.textScrollList("targetsList", e=True, ra=True)
    mc.textScrollList("targetsChan", e=True, ra=True)
    lTrgt = getTrgt(getBsDef(obj, 0))
    for trgt in lTrgt:
        if not mc.attributeQuery('isInBet', n=trgt, ex=True):
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

def loadSelItemInList(itemLister, *args, **kwargs):
    lTpl = mc.ls(sl=True)
    mc.textScrollList(itemLister, e=True, ra=True)
    mc.textScrollList(itemLister, e=True, a=lTpl)

def setchkBoxAllChans(chkBox, *args, **kwargs):
    val = mc.checkBoxGrp(chkBox, q=True, va4=True)[-1]
    mc.checkBoxGrp(chkBox, e=True, va3=[val, val, val])

def linkSlicesDrivers(*args, **kwargs):
    lDrivers = mc.textScrollList('tplDriversList', q=True, ai=True)
    lDrivens = mc.textScrollList('tplDrivensList', q=True, ai=True)
    dicChkBox = {'chkBoxTr':'translate', 'chkBoxRt':'rotate', 'chkBoxSc':'scale'}
    chans = ''
    for key in dicChkBox.keys():
        lValues = mc.checkBoxGrp(key, q=True, va3=True)
        for i in enumerate(['X', 'Y', 'Z']):
            if lValues[i[0]] == True:
                chans += dicChkBox[key]+i[1]+','
    for driver in lDrivers:
        for driven in lDrivens:
            if not mc.attributeQuery('zoneParentDriver', n=driven, ex=True):
                mc.addAttr(driven, ln='zoneParentDriver', dt='string', multi=True)

            idDriver = getAvalableId(driven, 'zoneParentDriver')
            lIdConn = getAttrIds(driven, 'zoneParentDriver') or []
            if lIdConn:
                for idConn in lIdConn:
                    if mc.getAttr(driven+'.zoneParentDriver['+str(idConn)+']', s=True) == driver:
                        idDriver = idConn
                    else:
                        mc.setAttr(driven+'.zoneParentDriver['+str(idDriver)+']', driver, type='string')
            else:
                mc.setAttr(driven+'.zoneParentDriver['+str(idDriver)+']', driver, type='string')

            #print driver, idDriver, chans
            if not mc.attributeQuery('zoneParentDriverChans', n=driven, ex=True):
                mc.addAttr(driven, ln='zoneParentDriverChans', dt='string', multi=True)
            mc.setAttr(driven+'.zoneParentDriverChans['+str(idDriver)+']', chans, type='string')





def isolateTrgt(*args, **kwargs):
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

def showAllTrgt(*args, **kwargs):
    lTrgt = mc.textScrollList('targetsList', q=True, ai=True)
    for trgt in lTrgt:
        mc.setAttr(trgt+'.v', 1)
#isolateTrgt()

def refreshTrgt(*args, **kwargs):
    nspace = mc.textScrollList('targetsList', q=True, ai=True)[0].split(':')[0]
    neutral = 'neutral_'+nspace.lower()
    loadTrgt(neutral)

def selTrgt(*args, **kwargs):
    lTrgt = mc.textScrollList('targetsList', q=True, si=True)
    mc.select(cl=True)
    mc.select(lTrgt)

def showNeutral(*args, **kwargs):
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



def showHideNeutral():
    val = 1
    currentVal = mc.getAttr('NTL:geo_neutral.hiddenInOutliner')
    if currentVal == val:
        val = 0
    mc.setAttr('NTL:geo_neutral.hiddenInOutliner',val)
    mel.eval("AEdagNodeCommonRefreshOutliners()")


def loadMOD(*args, **kwargs):
    pathDir = r'X:\04_FABRICATION\ASSETS\CHR'
    project = project_manager.getProject()
    if project:
        pathDir = project_manager.projectsPaths()[project]['FACE']
    path = mc.fileDialog2(dir=pathDir, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    if path:
        mc.file(path, r=True, ns='MOD')
#loadMOD(pathDir = r'T:\90_TEAM_SHARE\03_FAB\00_ASSETS\01_MOD\01_CHARS')

def unloadMOD(*args, **kwargs):
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

def addTrgt(getSel, ctrl, *args, **kwargs):
    lNeutral = getSel()
    if not lNeutral:
        mc.warning('select neutral(s) to add the new target')
        return
    prx = mc.optionMenu('trgtTypes', q=True, v=True).split(':')[0]
    trgt = mc.textField('newTrgtName', q=True, tx=True)
    if trgt == '':
        mc.warning('enter trgt name')
        return
    attr = mc.textField('newAttrName', q=True, tx=True)
    if attr == '':
        mc.warning('enter attr name')
        return

    nTrgt = trgt
    if not  trgt.startswith(prx+'_'):
        nTrgt = prx+'_'+trgt

    nAttr = attr
    print attr, prx
    if not attr.startswith(prx):
        nAttr = prx+attr.capitalize()
    print nAttr
    valCtrl = 20
    if not mc.attributeQuery(nAttr, n=ctrl, ex=True):
        mc.addAttr(ctrl, ln=nAttr, at='float', min=0, max=20, k=True)
    elif mc.attributeQuery(nAttr, n=ctrl, ex=True):
        min = mc.attributeQuery(nAttr, n=ctrl, min=True)[0]
        max = mc.attributeQuery(nAttr, n=ctrl, max=True)[0]
        if min == 0.0:
            mc.addAttr(ctrl+'.'+nAttr, e=True, min=-20)
            valCtrl = -20
        if min == -20.0:
            if max == 0.0:
                mc.addAttr(ctrl+'.'+nAttr, e=True, max=20)
                valCtrl = 20
            elif max == 20.0:
                mc.warning('attribute is already connected in two targets, you must create a new attribe with an other nameor remove the target')
                return
    for neutral in lNeutral:
        mshResult = neutral
        if not mc.getAttr(neutral+'.resultMsh') == 'TRGT':
            baseName = neutral
            if ':' in neutral:
                baseName = neutral.split(':')[-1]
            neutral = 'TRGT:'+baseName+'TRGT'

        nspace = crtNspace(baseName, nsFather='TRGT')
        if mc.objExists(nspace+':'+trgt):
            mc.warning(nspace+':'+trgt, 'skipped, it s already exist')
        else:
            activeDef(neutral, False)
            lNspace.setNspace(nspace)
            newTrgt = mc.duplicate(neutral, n=nTrgt)[0]
            storageGrp = geStorageGrp('TRGT', mshResult)
            mc.parent(newTrgt, storageGrp)
            lNspace.setNspace('')
            activeDef(neutral, True)

            #####################
            bs = getBsDef(neutral, 0)[0]
            lWght = mc.blendShape(bs, q=True, t=True) or []
            id = 0
            if lWght:
                id = getLastInputId(bs)+1
            chkTrgt = mc.blendShape(bs, q=True, t=True) or []
            if not trgt in chkTrgt:
                mc.blendShape(bs, edit=True, t=(neutral, id, newTrgt, 1.0))
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+nAttr, itt='linear', ott='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+nAttr, itt='linear', ott='linear', dv=valCtrl, v=2)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+nAttr, itt='linear', ott='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+newTrgt.split(':')[-1], cd=ctrl+'.'+nAttr, itt='linear', ott='linear', dv=valCtrl, v=2)


            print trgt, 'added to', neutral, 'and connected to', ctrl+'.'+nAttr

    if mc.window('SMF_addTrgt', ex=True, q=True):
        mc.deleteUI('SMF_addTrgt', window=True)
#addTrgt(mc.ls(sl=True), 'c_targets')

def snapShp(getSel, *args, **kwargs):
    lMsh = []
    if isinstance(getSel, list):
        lMsh = getSel
    else:
        lMsh = getSel()
    mshSrc  = lMsh[0]
    mshTrgt = lMsh[1]
    ortSrc = mc.xform(mshSrc, ws=True, q=True, ro=True)
    ortTrgt = mc.xform(mshTrgt, ws=True, q=True, ro=True)
    mc.xform(mshSrc, ws=True, ro=(0.0, 0.0, 0.0))
    mc.xform(mshTrgt, ws=True, ro=(0.0, 0.0, 0.0))

    vtxs = mc.polyEvaluate(mshSrc, v=True)
    posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
    posTrgt = mc.xform(mshTrgt, q=True, ws=True, t=True)


    dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
    for i in range(0, vtxs):
        pos = mc.xform(mshSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        trgtPos = [pos[0]-dif[0], pos[1]-dif[1], pos[2]-dif[2]]
        mc.move(trgtPos[0], trgtPos[1], trgtPos[2], mshTrgt+'.vtx['+str(i)+']')
    mc.xform(mshSrc, ws=True, ro=(ortSrc[0],ortSrc[1],ortSrc[2]))
    mc.xform(mshTrgt, ws=True, ro=(ortTrgt[0],ortTrgt[1],ortTrgt[2]))
#snapShp(mc.ls(sl=True))


def snapShp_V2(getSel, *args, **kwargs):
    lMsh = []
    if isinstance(getSel, list):
        lSel = getSel
    else:
        lSel = getSel()
    if mc.objectType(lSel[0]) == 'transform':
        lMsh = lSel
        mshSrc  = lMsh[0]
        mshTrgt = lMsh[1]
        ortSrc = mc.xform(mshSrc, ws=True, q=True, ro=True)
        ortTrgt = mc.xform(mshTrgt, ws=True, q=True, ro=True)
        mc.xform(mshSrc, ws=True, ro=(0.0, 0.0, 0.0))
        mc.xform(mshTrgt, ws=True, ro=(0.0, 0.0, 0.0))

        vtxs = mc.polyEvaluate(mshSrc, v=True)
        posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
        posTrgt = mc.xform(mshTrgt, q=True, ws=True, t=True)


        dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
        for i in range(0, vtxs):
            pos = mc.xform(mshSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            trgtPos = [pos[0]-dif[0], pos[1]-dif[1], pos[2]-dif[2]]
            mc.move(trgtPos[0], trgtPos[1], trgtPos[2], mshTrgt+'.vtx['+str(i)+']')
        mc.xform(mshSrc, ws=True, ro=(ortSrc[0],ortSrc[1],ortSrc[2]))
        mc.xform(mshTrgt, ws=True, ro=(ortTrgt[0],ortTrgt[1],ortTrgt[2]))
    elif mc.objectType(lSel[0]) == 'mesh':
        mshTrgt = lSel[-1]
        mc.select(mshTrgt, d=True)
        mel.eval("ConvertSelectionToVertices")
        lVtx = mc.ls(sl=True, fl=True)
        mshSrc = lVtx[0].split('.')[0]
        #orient######################################################
        ortSrc = mc.xform(mshSrc, ws=True, q=True, ro=True)
        ortTrgt = mc.xform(mshTrgt, ws=True, q=True, ro=True)
        mc.xform(mshSrc, ws=True, ro=(0.0, 0.0, 0.0))
        mc.xform(mshTrgt, ws=True, ro=(0.0, 0.0, 0.0))
        ##############################################################
        posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
        posTrgt = mc.xform(mshTrgt, q=True, ws=True, t=True)
        dif = [posSrc[0] - posTrgt[0], posSrc[1] - posTrgt[1], posSrc[2] - posTrgt[2]]
        chkSoft = mc.softSelect(q=True, sse=True)
        if chkSoft:
            dicSoft = getSoftSelWght()
            for id in dicSoft.keys():
                sft = dicSoft[id]
                posVtxSrc = mc.xform(mshSrc + '.vtx[' + str(id) + ']', q=True, ws=True, t=True)
                posVtxTrgt = mc.xform(mshTrgt + '.vtx[' + str(id) + ']', q=True, ws=True, t=True)

                difSrc = [posVtxSrc[0] - posSrc[0], posVtxSrc[1] - posSrc[1], posVtxSrc[2] - posSrc[2]]
                difTrgt = [posVtxTrgt[0] - posTrgt[0], posVtxTrgt[1] - posTrgt[1], posVtxTrgt[2] - posTrgt[2]]

                difVtx = [difSrc[0] - difTrgt[0], difSrc[1] - difTrgt[1], difSrc[2] - difTrgt[2]]
                difSft = [difVtx[0]*sft, difVtx[1]*sft, difVtx[2]*sft]
                resPos = [posVtxTrgt[0]+difSft[0], posVtxTrgt[1]+difSft[1], posVtxTrgt[2]+difSft[2]]
                mc.move(resPos[0], resPos[1], resPos[2], mshTrgt + '.vtx[' + str(id) + ']')
        else:
            for vtxSrc in lVtx:
                id = vtxSrc.split('.vtx[')[-1][: -1]
                pos = mc.xform(vtxSrc, q=True, ws=True, t=True)
                resPos = [pos[0] - dif[0], pos[1] - dif[1], pos[2] - dif[2]]
                mc.move(resPos[0], resPos[1], resPos[2], mshTrgt + '.vtx[' + str(id) + ']')
        mc.xform(mshSrc, ws=True, ro=(ortSrc[0], ortSrc[1], ortSrc[2]))
        mc.xform(mshTrgt, ws=True, ro=(ortTrgt[0], ortTrgt[1], ortTrgt[2]))

#snapShp(mc.ls(sl=True))

def mirrorWire(getSel, side='L', *args, **kwargs):
    lObj = getSel()
    for obj in lObj:
        lCvs = mc.ls(obj+'.cv[*]', r=True, fl=True)

    for id in range(0, mc.getAttr(obj + attrSrc, s=True)):
        vtxSrc = mc.getAttr(obj + attrSrc + '[' + str(id) + ']')
        vtxTrgt = mc.getAttr(obj + attrTrgt + '[' + str(id) + ']')
        valueSrc = mc.xform(obj + '.vtx[' + str(vtxSrc) + ']', ws=True, q=True, t=True)
        valueTrgt = mc.xform(obj + '.vtx[' + str(vtxTrgt) + ']', ws=True, q=True, t=True)
        valDif = [valueSrc[0] - (valueTrgt[0] * -1), valueSrc[1] - valueTrgt[1], +valueSrc[2] - valueTrgt[2]]
        valSym = [valueTrgt[0] + (valDif[0] * -1), valueTrgt[1] + valDif[1], valueTrgt[2] + valDif[2]]
        mc.move(valSym[0], valSym[1], valSym[2], obj + '.vtx[' + str(vtxTrgt) + ']', co=True)


def mirrorSculpt(getSel, side='L', *args, **kwargs):
    lObj = getSel()
    dicSym = {}
    attrSrc = '.symTabLeft'
    attrTrgt = '.symTabRight'
    if side == 'R':
        attrSrc = '.symTabRight'
        attrTrgt = '.symTabLeft'
    for obj in lObj:
        dicSym['sided'] = {}
        posObj = mc.xform(obj, ws=True, q=True, t=True)
        ortObj = mc.xform(obj, ws=True, q=True, ro=True)
        mc.xform(obj, ws=True, ro=(0.0, 0.0, 0.0))
        if not mc.attributeQuery('symTab', n=obj, ex=True):
            mc.warning('no sym attr on the mesh, call DAVID')
            return
        for id in range(0, mc.getAttr(obj+attrSrc, s=True)):
            vtxSrc = mc.getAttr(obj+attrSrc+'['+str(id)+']')
            vtxTrgt = mc.getAttr(obj+attrTrgt+'['+str(id)+']')
            valueSrc = mc.xform(obj+'.vtx['+str(vtxSrc)+']', ws=True, q=True, t=True)
            valDif = [valueSrc[0] - posObj[0], valueSrc[1] - posObj[1], +valueSrc[2] - posObj[2]]
            mc.move(valDif[0]* -1, valDif[1], valDif[2], obj + '.vtx[' + str(vtxTrgt) + ']', co=True)
        mc.xform(obj, ws=True, ro=(ortObj[0], ortObj[1], ortObj[2]))

def flipSculpt(getSel, *args, **kwargs):
    lObj = getSel()
    dicSym = {}
    for obj in lObj:
        #mshOrig =
        dicSym['mid'] = []
        dicSym['sided'] = {}

        if not mc.attributeQuery('symTab', n=obj, ex=True):
            mc.warning('no sym attr found on the mesh!')
            return
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


def getSoftSelWght():
    dicWght = {}
    softSelection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(softSelection)
    selection = OpenMaya.MSelectionList()
    softSelection.getSelection(selection)
    pathDag = OpenMaya.MDagPath()
    oComp = OpenMaya.MObject()
    selection.getDagPath(0, pathDag, oComp)
    fnComp = OpenMaya.MFnSingleIndexedComponent(oComp)
    for i in range(fnComp.elementCount()):
        # print fnComp.element(i), fnComp.weight(i).influence()
        dicWght[fnComp.element(i)] = fnComp.weight(i).influence()
    return dicWght

def resetShp(getSel, *args, **kwargs):
    lSel = getSel()
    lMsh = mc.ls(lSel, type='transform')
    lComp = lSel
    for msh in lMsh:
        if msh in lComp:
            lComp.remove(msh)

    if not lComp:
        for msh in lMsh:
            vtxs = mc.polyEvaluate(msh, v=True)
            for i in range(0, vtxs):
                mc.setAttr(msh+'.pnts['+str(i)+']',0, 0, 0)
    else:
        mc.select(cl=True)
        mc.select(lComp)

        mel.eval("ConvertSelectionToVertices")
        lVtx = mc.ls(sl=True, fl=True)
        chkSoft = mc.softSelect(q=True, sse=True)
        if chkSoft:
            mshSrc = lVtx[0].split('.')[0]
            dicSfot = getSoftSelWght()
            for id in dicSfot.keys():
                posVtx = mc.getAttr(mshSrc+'.vtx['+str(id)+']')[0]
                posSoft = [posVtx[0]-(posVtx[0]*dicSfot[id]), posVtx[1]-(posVtx[1]*dicSfot[id]), posVtx[2]-(posVtx[2]*dicSfot[id])]
                mc.setAttr(mshSrc+'.vtx['+str(id)+']', posSoft[0], posSoft[1], posSoft[2])
                if lMsh:
                    for msh in lMsh:
                        posVtx = mc.getAttr(msh + '.vtx[' + str(id) + ']')[0]
                        posSoft = [posVtx[0] - (posVtx[0] * dicSfot[id]), posVtx[1] - (posVtx[1] * dicSfot[id]), posVtx[2] - (posVtx[2] * dicSfot[id])]
                        mc.setAttr(msh + '.vtx[' + str(id) + ']', posSoft[0], posSoft[1], posSoft[2])
        else:
            for vtx in lVtx:
                mc.setAttr(vtx, 0, 0, 0)
                if lMsh:
                    for msh in lMsh:
                        mc.setAttr(msh+'.'+vtx.split('.')[-1], 0, 0, 0)

#resetShp(mc.ls(sl=True))



def dupShp(getSel, *args, **kwargs):
    lMsh = getSel()
    for msh in lMsh:
        nspace = ':'
        if ':' in msh:
            nspace = msh[: len(msh)-len(msh.split(':')[-1])]
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
        removeCustomAttrs([dupShp])
        mc.parent(dupShp, dupGrp)
        mc.connectAttr(dupShp+'.message', msh+'.dupList['+str(id)+']')
        mc.namespace(set=':')

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

def snapTpl(cg, *args, **kwargs):
    lib_controlGroup.snapTplToCtrl(cg)

def majPosCtrl(getSel, *args, **kwargs):
    lCtrl = getSel()
    if not lCtrl:
        lNodes = mc.ls('*.nodeType', o=True, r=True)
        for node in lNodes:
            if mc.getAttr(node+'.nodeType') == 'control':
                lCtrl.append(node)
    lSk = []
    for ctrl in lCtrl:
        if mc.getAttr(ctrl+'.nodeType') == 'control':
            root = mc.listRelatives(ctrl, p=True)[0]
            lChilds = mc.listRelatives(root, c=True)

            lChilds.remove(ctrl)
            sk = lChilds[0]

            tmp = mc.createNode('transform')
            mc.delete(mc.parentConstraint(ctrl, tmp, mo=False))
            mc.delete(mc.parentConstraint(tmp, root, mo=False))
            mc.delete(tmp)

            mc.setAttr(ctrl+'.translateX', 0)
            mc.setAttr(ctrl+'.translateY', 0)
            mc.setAttr(ctrl+'.translateZ', 0)

            mc.setAttr(ctrl+'.rotateX', 0)
            mc.setAttr(ctrl+'.rotateY', 0)
            mc.setAttr(ctrl+'.rotateZ', 0)

            mc.setAttr(ctrl+'.scaleX', 1)
            mc.setAttr(ctrl+'.scaleY', 1)
            mc.setAttr(ctrl+'.scaleZ', 1)


            allChilds = mc.listRelatives(root, ad=True, type='joint')
            for child in allChilds:
                skinClusterPlugs = mc.listConnections(sk + ".worldMatrix[0]", type="skinCluster", p=1) or []
                if skinClusterPlugs:
                    if not child in lSk:
                        lSk.append(child)
        for sk in lSk:
            skinClusterPlugs = mc.listConnections(sk + ".worldMatrix[0]", type="skinCluster", p=1)
            if skinClusterPlugs:
                # for each skinCluster connection
                for skinClstPlug in skinClusterPlugs:
                    index = skinClstPlug[skinClstPlug.index("[")+1 : -1 ]
                    skinCluster = skinClstPlug[ : skinClstPlug.index(".") ]
                    curInvMat = mc.getAttr(sk + ".worldInverseMatrix")
                    mc.setAttr(skinCluster + ".bindPreMatrix[{0}]".format(index), type="matrix", *curInvMat )
#majPosCtrl(mc.ls(sl=True))




#EXTRACT SHAPE MIX#################################################################################################################################################################################
def getTrgrFromMix(mix):
    lBs = []
    dicMix = {}
    dicMix[mix] = {}
    dicMix[mix]['trgr'] = {}
    dicMix[mix]['trgt'] = {}
    for i in range(0, mc.getAttr(mix + '.trgrList', s=True)):
        dicMix[mix]['trgr'][mc.getAttr(mix + '.trgrList[' + str(i) + ']')] = mc.getAttr(mix + '.trgrValues[' + str(i) + ']')
        bs = mc.getAttr(mix + '.trgrList[' + str(i) + ']').split('.')[0]
        if not bs in lBs:
            lBs.append(bs)
    dataBs = {}
    for bs in lBs:
        dataBs.update(getDicBsTrgtDatasAsMsh(bs))
    for trgr in dicMix[mix]['trgr'].keys():
        for key in dataBs.keys():
            if dataBs[key]['data']['alias'] == trgr.split('.')[-1]:
                id = dataBs[key]['data']['index']
                if not trgr in dicMix[mix]['trgt'].keys():
                    dicMix[mix]['trgt'][trgr] = key
    return dicMix


def genMixSculpt(lMsh, *args, **kwargs):
    nCorr = 'mix'
    for msh in lMsh:
        lBs = getBsDef(msh, None)
        bsTrgt = ''
        for bs in lBs:
            if mc.getAttr(bs+'.bsType') == 0:
                bsTrgt = bs


        #dicTrgt = getActivTrgt(bsTrgt)
        dicTrgt = getMixTrigger(msh)
        for bs in dicTrgt.keys():
            #if ':' in bs:
                #bs = bs.split(':')[-1]
            nBs = bs.split('_')[-1].upper()
            nCorr = nCorr+'_'+nBs+'_'
            lTrgt = mc.blendShape(bs, q=True, t=True)
            for trgt in dicTrgt[bs].keys():
                nCorr = nCorr+trgt.split('_')[-1].capitalize()

        #pNspace = lTrgt[0].split(':')[0]
        #pNspace = msh[len(msh.split('_')[0])+1:].upper()
        pNspace = msh.split(':')[0]
        nspace = crtNspace(msh, pNspace)
        mixShp = mc.duplicate(msh, n=nCorr)[0]


        if not mc.objExists(nspace+':mixSculpt'):
            grp = mc.createNode('transform', n='mixSculpt')
            #mc.connectAttr(nspace+':geo_targets.v', grp+'.v')

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
            for toto in dicTrgt[key].keys():
                mc.setAttr(mixShp+'.trgtList['+str(i)+']', toto, type='string')
                mc.setAttr(mixShp+'.trgtValues['+str(i)+']', dicTrgt[key][toto])
                i=i+1
        mc.addAttr(mixShp, ln='shpSource', at='message')
        mc.connectAttr(msh+'.message', mixShp+'.shpSource', f=True)
        #mc.addAttr(mixShp, ln='shpResult', at='message')
        cleanShapes(mixShp)
        mc.namespace(set=':')
#genMixSculpt(mc.ls(sl=True))

def connectMixShp(getSel, *args, **kwargs):
    lMixSculpt = getSel()
    for mixSculpt in lMixSculpt:
        nspace = mixSculpt.split(':')[0]
        nspace = mixSculpt[: len(mixSculpt)-len(mixSculpt.split(':')[-1])]
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
            mc.connectAttr(nspace+'geo_targets.v', grp+'.v')
        #mc.parent(mixTrgt, nspace+'mixTrgt')
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
        #blendMixTrgt(mixSculpt, bsTrgt, bsMix)
        blendMixTrgt_v2(mixSculpt, bsTrgt, bsMix)
#connectMixShp(mc.ls(sl=True))

def connectMixShp_v2(lMixSculpt):
    for mixSculpt in lMixSculpt:
        #NAMMING
        nspace = mixSculpt[: len(mixSculpt)-len(mixSculpt.split(':')[-1])]
        nMix = mixSculpt+'_Mix__SMABtmp'
        mshSrc  = mc.listConnections(mixSculpt+'.shpSource', s=True, p=False)[0]
        chkResult = False
        #lBs = getBsDef(mshSrc, None)
        lBs = []

        bsTrgt = getBsDef(mshSrc, 0) or []
        bsCor = getBsDef(mshSrc, 1) or []
        bsMix = getBsDef(mshSrc, 2) or []
        bsResult = getBsDef(mshSrc, 3) or []
        if bsTrgt:
            lBs.append(bsTrgt[0])
        if bsCor:
            lBs.append(bsCor[0])
        if bsMix:
            lBs.append(bsMix[0])

        for bs in lBs:
            mc.setAttr(bs+'.envelope', 0)

        lSkin = mc.ls(mc.findDeformers(mshSrc), type='skinCluster')
        for skin in lSkin:
            mc.setAttr(skin+'.envelope', 0)

        mixTrgt = mc.duplicate(mshSrc, n=nMix)[0]
        for bs in lBs:
            mc.setAttr(bs+'.envelope', 1)
        for skin in lSkin:
            mc.setAttr(skin+'.envelope', 1)
        tmpActivator = ''
        if not mc.attributeQuery('shpResult', n=mixSculpt, ex=True):
            mc.addAttr(mixSculpt, ln='shpResult', at='message')
            mc.connectAttr(mixTrgt+'.message', mixSculpt+'.shpResult')
            mc.addAttr(mixTrgt, ln='mixResult', at='bool', dv=1)
            mixTrgt = mc.rename(mixTrgt, mixTrgt.replace('__SMABtmp', ''))
            mc.parent(mixTrgt, mixSculpt)
        else:
            chkMixResult = mc.listConnections(mixSculpt+'.shpResult', d=True) or []
            if chkMixResult:
                chkResult = True
                trgtMixWght = getTrgtAliasIndex(chkMixResult[0])[chkMixResult[0]]['alias']
                tmpActivator = mc.listConnections(bsMix[0]+'.'+trgtMixWght, s=True, d=False)[0]
                mc.setAttr(tmpActivator+'.input2', 0)
        ###########################################################

        vtxs = mc.polyEvaluate(mshSrc, v=True)
        posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
        posTrgt = mc.xform(mixSculpt, q=True, ws=True, t=True)
        dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
        posDest = mc.xform(mixTrgt, q=True, ws=True, t=True)

        #set bs pose#############################################################
        lActivedTrgt = mc.getAttr(mixSculpt+'.trgtList', s=True) or []
        for id in range(0, lActivedTrgt):
            activedTrgt = mc.getAttr(mixSculpt+'.trgtList['+str(id)+']')
            activatedValue = mc.getAttr(mixSculpt+'.trgtValues['+str(id)+']')
            try:
                mc.setAttr(activedTrgt, activatedValue)
            except:
                pass
        ########################################################################
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

        #repport mix trgt values
        if chkResult == False:
            unlockChans(mixTrgt)
            for i in range(0, mc.getAttr(mixSculpt+'.trgtList', s=True)):
                val = mc.getAttr(mixSculpt+'.trgtList['+str(i)+']')
                mc.setAttr(mixTrgt+'.trgtList['+str(i)+']', val, type='string')
                val = mc.getAttr(mixSculpt+'.trgtValues['+str(i)+']')
                mc.setAttr(mixTrgt+'.trgtValues['+str(i)+']', val)
            mshMix = mc.blendShape(bsMix[0], q=True, g=True)[0]

            connectMixCorr(mixTrgt, mshMix, bsMix[0])
            #blendMixTrgt(mixSculpt, bsTrgt[0], bsMix[0])
            blendMixTrgt_v2(mixSculpt, bsTrgt[0], bsMix[0])
        elif chkResult == True:
            mixResult = mc.listConnections(mixSculpt+'.shpResult', d=True)[0]
            snapShp([mixTrgt, mixResult])
            mc.delete(mixTrgt)
            mc.setAttr(tmpActivator+'.input2', 1)
        mc.setAttr(bsMix[0]+'.envelope', 1)
        for skin in lSkin:
            mc.setAttr(skin+'.envelope', 1)

#connectMixShp_v2(mc.ls(sl=True))

def genMixSculpt_v2(lMsh):
    nMix = 'mix'
    for mshResult in lMsh:
        storageGrp = geStorageGrp('MIX', mshResult)
        bsMix = getBsDef(mshResult, 2)
        if not bsMix:
            mixResult = genResult(mshResult, 'MIX')
            bsMix = mc.blendShape(mixResult, n='bsMix'+mshResult[len(mshResult.split('_')[0]):])[0]
            bsTypeAttrr(bsMix, 2)

        dicTrgt = getMixTrigger(mshResult)

        skinActived = False
        for bs in dicTrgt.keys():
            if mc.getAttr(bs+'.bsType') == 1:
                skinActived = True
            if ':' in bs:
                bs = bs.split(':')[-1]
            nBs = bs.split('_')[-1].upper()
            nMix = nMix+'_'+nBs+'_'
            lTrgt = mc.blendShape(bs, q=True, t=True)
            for trgt in dicTrgt[bs].keys():
                nMix = nMix+trgt.split('_')[-1].capitalize()

        #pNspace = lTrgt[0].split(':')[0]
        #pNspace = msh[len(msh.split('_')[0])+1:].upper()

        pNspace = mshResult.split(':')[0]
        nspace = crtNspace(mshResult, 'MIX')
        mixShp = mc.duplicate(mshResult, n=nMix)[0]


        if not mc.objExists(nspace+':mixSculpt'):
            grp = mc.createNode('transform', n='mixSculpt')
            #mc.connectAttr(nspace+':geo_targets.v', grp+'.v')

        for attr in ('translate', 'rotate', 'scale'):
            for chan in ['X', 'Y', 'Z']:
                mc.setAttr(mixShp+'.'+attr+chan, lock=False)
        father = mc.listRelatives(mixShp, p=True) or []
        if father:
            mc.parent(mixShp, nspace+':mixSculpt')
        mc.addAttr(mixShp, ln='trgtList', dt='string', multi=True)
        mc.addAttr(mixShp, ln='trgtValues', at='float', multi=True)
        mc.addAttr(mixShp, ln='hadSkinActived', at='bool', dv=skinActived)
        i = 0
        for bs in dicTrgt.keys():
            for trigger in dicTrgt[bs].keys():
                #print dicTrgt[bs], trigger
                mc.setAttr(mixShp+'.trgtList['+str(i)+']', bs+'.'+trigger, type='string')
                mc.setAttr(mixShp+'.trgtValues['+str(i)+']', dicTrgt[bs][trigger])
                i=i+1
        mc.addAttr(mixShp, ln='shpSource', at='message')
        mc.connectAttr(mshResult+'.message', mixShp+'.shpSource', f=True)
        #mc.addAttr(mixShp, ln='shpResult', at='message')
        cleanShapes(mixShp)
        mc.namespace(set=':')
#genMixSculpt(mc.ls(sl=True))

def getMixTrigger(msh):
    lBs = []
    bsTrgt = getBsDef(msh, 0) or []
    bsCor = getBsDef(msh, 1) or []
    bsMix = getBsDef(msh, 2) or []
    if bsTrgt:
        lBs.append(bsTrgt[0])
    if bsCor:
        lBs.append(bsCor[0])
    if bsMix:
        lBs.append(bsMix[0])

    dicActivedTrgt = {}
    for bs in lBs:
        if mc.getAttr(bs+'.bsType') != 3:
            lTrgt = getActivTrgt(bs) or []
            if lTrgt:
                for trgt in lTrgt:
                    val = mc.getAttr(bs+'.'+trgt)
                    if not bs in dicActivedTrgt.keys():
                        dicActivedTrgt[bs] = {}
                    if not trgt in dicActivedTrgt[bs].keys():
                        dicActivedTrgt[bs][trgt] = val
    return dicActivedTrgt
#getMixTrigger('result_head')

def getMixTrigger_v2(msh):
    lBs = []
    bsTrgt = getBsDef(msh, 0) or []
    bsCor = getBsDef(msh, 1) or []
    bsMix = getBsDef(msh, 2) or []
    if bsTrgt:
        lBs.append(bsTrgt[0])
    if bsCor:
        lBs.append(bsCor[0])
    if bsMix:
        lBs.append(bsMix[0])

    dicActivedTrgt = {}
    for bs in lBs:
        if mc.getAttr(bs+'.bsType') != 3:
            lTrgt = getActivTrgt(bs) or []
            if lTrgt:
                for trgt in lTrgt:
                    val = mc.getAttr(bs+'.'+trgt)
                    if not bs in dicActivedTrgt.keys():
                        dicActivedTrgt[bs] = {}
                    if not trgt in dicActivedTrgt[bs].keys():
                        dicActivedTrgt[bs][trgt] = val
    return dicActivedTrgt
#getMixTrigger('result_head')

def ctrMixCombination(lMshResult):
    for mshResult in lMshResult:
        initMixSculpt(mshResult)
        dicActivedTrgr = {}
        skinActived = False
        lBs = []
        dicCombinations = {}
        lTrgr = []
        #get bs for meshResult
        bsTrgt = getBsDef(mshResult, 0) or []
        bsCor = getBsDef(mshResult, 1) or []
        bsMix = getBsDef(mshResult, 2) or []

        if bsTrgt:
            lBs.append(bsTrgt[0])
            bsTrgt = bsTrgt[0]
        if bsCor:
            lBs.append(bsCor[0])
            bsCor = bsCor[0]
        if bsMix:
            lBs.append(bsMix[0])
            bsMix = bsMix[0]

        #dic {bs: {trigger: value, trigger: value}, bs: {trigger: value}} and list all triggers
        for bs in lBs:
            if mc.getAttr(bs+'.bsType') != 3:
                lTrgt = getActivTrgt(bs) or []
                if lTrgt:
                    for trgt in lTrgt:
                        fullName = bs+'.'+trgt
                        val = mc.getAttr(fullName)
                        if not bs in dicActivedTrgr.keys():
                            dicActivedTrgr[bs] = {}
                            if mc.getAttr(bs+'.bsType') == 1:
                                skinActived = True
                        if not trgt in dicActivedTrgr[bs].keys():
                            dicActivedTrgr[bs][trgt] = val

                        if not fullName in lTrgr:
                            lTrgr.append(fullName)

        combination = lTrgr[0]
        for i in range(1, len(lTrgr)):
            trgr = lTrgr[i]


            #generate combination result name
            nComb = combination.replace('Sculpt', '')
            nTrgr = trgr.replace('Sculpt', '')
            if ':' in nComb:
                nComb = nComb.split(':')[-1]
            if ':' in nTrgr:
                nTrgr = nTrgr.split(':')[-1]
            nComb = nComb.split('.')[-1][len(nComb.split('.')[-1].split('_')[0])+1 :].capitalize()
            nTrgr = nTrgr.split('.')[-1][len(nTrgr.split('.')[-1].split('_')[0])+1 :].capitalize()
            part = trgr.split('.')[0][len(trgr.split('.')[0].split('_')[0])+1 :].capitalize()
            nMix = 'mix'+part+'_'+nComb+nTrgr
            nMixSculpt = nMix+'Sculpt'

            lComb = []
            lCombId = mc.getAttr(bsMix+'.listMixCombinations', mi=True) or []
            if lCombId:
                for combId in lCombId:
                    lComb.append(mc.getAttr(bsMix+'.listMixCombinations['+str(combId)+']'))
            if not combination +', '+trgr in lComb:
                #print 'create here', nComb ,'->', nTrgr, '=', nMix
                lastId = getAvalableId(bsMix, 'listMixCombinations')
                mc.setAttr(bsMix+'.listMixCombinations['+str(lastId)+']', combination+', '+trgr, type='string')
                mc.setAttr(bsMix+'.listMixResults['+str(lastId)+']', nMix, type='string')
                nspace = crtNspace(mshResult, 'MIX')
                mixSculpt = mc.duplicate(mshResult, n=nMixSculpt)[0]
                for attr in ('translate', 'rotate', 'scale'):
                    for chan in ['X', 'Y', 'Z']:
                        mc.setAttr(mixSculpt+'.'+attr+chan, lock=False)
                cleanShapes(mixSculpt)
                mc.addAttr(mixSculpt, ln='shpSource', at='message')
                mc.connectAttr(mshResult+'.message', mixSculpt+'.shpSource', f=True)
                #mc.addAttr(mixSculpt, ln='shpResult', at='message')

                mc.namespace(set=':')
                if not mc.objExists(nspace+':geo_mixSculpt'):
                    mc.createNode('transform', n='geo_mixSculpt')
                mc.addAttr(mixSculpt, ln='trgrList', dt='string', multi=True)
                mc.addAttr(mixSculpt, ln='trgrValues', at='float', multi=True)
                mc.addAttr(mixSculpt, ln='hadSkinActived', at='bool', dv=skinActived)

                inc = 0
                for trigger in [combination, trgr]:
                    val = 1.0
                    if trigger.split('.')[0] in dicActivedTrgr.keys():
                        if trigger.split('.')[-1] in dicActivedTrgr[trigger.split('.')[0]].keys():
                            val = dicActivedTrgr[trigger.split('.')[0]][trigger.split('.')[-1]]

                    mc.setAttr(mixSculpt+'.trgrList['+str(inc)+']', trigger, type='string')
                    mc.setAttr(mixSculpt+'.trgrValues['+str(inc)+']', val)
                    inc += 1
                connectMixShp_v3([mixSculpt])


            combination = bsMix+'.'+nMix
            i += 1
        #print dicCombinations

#############################################
#NEW______________________________________

def recurceGetMixTrgr(mixSculpt, lTrgr):
    lId = mc.getAttr(mixSculpt + '.trgrList', mi=True) or []
    if lId:
        for id in lId:
            alias = mc.getAttr(mixSculpt + '.trgrList[' + str(id) + ']').split('.')[-1]
            bs = mc.getAttr(mixSculpt + '.trgrList[' + str(id) + ']').split('.')[0]
            dicBsDatas = getDicBsTrgtDatasAsAlias(bs)
            bsType = mc.getAttr(bs+'.bsType')
            if bsType == 0:
                trgr = dicBsDatas[alias]['sculpt'][1.0]['trgt']
                if not trgr in lTrgr:
                    lTrgr.append(trgr)
            if bsType == 2:
                mixTrgt = dicBsDatas[alias]['sculpt'][1.0]['trgt']
                recurceGetMixTrgr(mixTrgt, lTrgr)
    return lTrgr
#recurceGetMixTrgr(mixSculpt, lTrgr)

def getMixsZonesOLD():
    lMix = mc.ls('*.mixResult', r=True, o=True) or []
    dicMixZones = {}
    if lMix:
        for mix in lMix:
            sculpt = mc.listConnections(mix+'.message', d=True, s=False, type='transform')[0]
            mshSrc = mc.listConnections(sculpt+'.shpSource', s=True, d=False)[0]
            lId = mc.getAttr(mix + '.trgrList', mi=True) or []
            if lId:
                if not mshSrc in dicMixZones.keys():
                    dicMixZones[mshSrc] = {}
                dicMixZones[mshSrc][mix] = []
                for id in lId:
                    zone = mc.getAttr(mix + '.trgrList[' + str(id) + ']').split('.')[-1].split('_')[0]
                    print 'HERE :', mix, mc.getAttr(mix + '.trgrList[' + str(id) + ']'), zone
                    if not zone in dicMixZones[mshSrc][mix]:
                        dicMixZones[mshSrc][mix].append(zone)
    return dicMixZones

def getMixsZones():
    lMix = mc.ls('*.mixResult', r=True, o=True) or []
    dicMixZones = {}
    if lMix:
        for mix in lMix:
            mixSculpt = mc.listConnections(mix+'.message', d=True, s=False, type='transform')[0]
            mshSrc = mc.listConnections(mixSculpt+'.shpSource', s=True, d=False)[0]
            lId = mc.getAttr(mix + '.trgrList', mi=True) or []
            if lId:
                if not mshSrc in dicMixZones.keys():
                    dicMixZones[mshSrc] = {}
                dicMixZones[mshSrc][mix] = []
                for id in lId:
                    bs = mc.getAttr(mix + '.trgrList[' + str(id) + ']').split('.')[0]
                    bsType = mc.getAttr(bs+'.bsType')
                    if bsType == 2:
                        lTrgr = []
                        lTrgt  = recurceGetMixTrgr(mixSculpt, lTrgr)
                        for trgt in lTrgt:
                            zone = trgt.split(':')[-1].split('_')[0]
                            if not zone in dicMixZones[mshSrc][mix]:
                                dicMixZones[mshSrc][mix].append(zone)
                    if bsType == 0:
                        zone = mc.getAttr(mix + '.trgrList[' + str(id) + ']').split('.')[-1].split('_')[0]
                        if not zone in dicMixZones[mshSrc][mix]:
                            dicMixZones[mshSrc][mix].append(zone)
    return dicMixZones
def getMixExtractZone(getSel, *args, **kwargs):
    faceDatas = faceDescription()
    matZones = faceDatas.trgtNames()
    dicMixZones = getMixsZones()
    dicSep = getSepZone()
    dicMxiExtZones = {}
    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()
    for mshRes in lMshResult:
        if mshRes in dicSep.keys():
            if not mshRes in dicMxiExtZones.keys():
                dicMxiExtZones[mshRes] = {}
            for mix in dicMixZones[mshRes].keys():
                lMixZones = []
                for mixZone in dicMixZones[mshRes][mix]:
                    #print mshRes, mix, mixZone, matZones.items()
                    zoneKey = [k for (k, val) in matZones.items() if val == mixZone][0]
                    if not zoneKey in lMixZones:
                        lMixZones.append(zoneKey)
                extractZone = lMixZones[0]
                for zone in lMixZones:
                    if len(dicSep[mshRes][zone]) < len(dicSep[mshRes][extractZone]):
                        extractZone = zone
                sepZone = dicSep[mshRes][extractZone][0]
                if not sepZone in dicMxiExtZones[mshRes].keys():
                    dicMxiExtZones[mshRes][sepZone] = []
                if not mix in dicMxiExtZones[mshRes][sepZone]:
                    dicMxiExtZones[mshRes][sepZone].append(mix)
                    if not mc.attributeQuery('mixExtraction', n=mix, ex=True):
                        mc.addAttr(mix, ln='mixExtraction', dt='string')
                    mc.setAttr(mix+'.mixExtraction', sepZone, type='string')
    return dicMxiExtZones

def getMixVtxMoves(getSel, *args, **kwargs):
    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()
    dicMix = getMixExtractZone(lMshResult)

    dicMovedVtxByZone = {}
    for mshRes in lMshResult:
        if not mshRes in dicMovedVtxByZone.keys():
            dicMovedVtxByZone[mshRes] = {}
        lSepZones = dicMix[mshRes].keys()

        for sepZone in lSepZones:
            if not sepZone in dicMovedVtxByZone[mshRes].keys():
                dicMovedVtxByZone[mshRes][sepZone] = []
            lMix = dicMix[mshRes][sepZone]
            for mix in lMix:
                for i in mc.getAttr(mix+'.movedVtx', mi=True):
                    vtx = mc.getAttr(mix+'.movedVtx['+str(i)+']')
                    if not vtx in dicMovedVtxByZone[mshRes][sepZone]:
                        dicMovedVtxByZone[mshRes][sepZone].append(vtx)

    return dicMovedVtxByZone

def addMixToSlicewght(getSel, *args, **kwargs):
    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()
    dicVtxMoved = getMixVtxMoves(lMshResult)
    print dicVtxMoved
    for mshRes in lMshResult:
        for sepZone in dicVtxMoved[mshRes]:

            #if sepZone == 'SEP:sep_head_mouth':
                #print sepZone
            dicSlices = getSlices(sepZone)

            for vtx in dicVtxMoved[mshRes][sepZone]:
                #print vtx, sepZone
                valVtx = getSliceVtxWght([sepZone], vtx)
                if not valVtx == 1.0:
                    bs = getBsDef(sepZone, None)[0]
                    mc.setAttr(bs + '.inputTarget[0].baseWeights[' + str(vtx) + ']', 1.0)
                    lib_checkers.vtxColor([sepZone + '.vtx[' + str(vtx) + ']'], (0.256, 0.7957, 0.872)) #vtx wght on sep zone  BLUE

            for sep in dicSlices.keys():
                lSlices = dicSlices[sep]
                for vtx in dicVtxMoved[mshRes][sepZone]:
                    col = (0.6193, 0.163, 0.0) #vtx move ORANGE
                    for slice in lSlices:
                        lib_checkers.vtxColor([slice + '.vtx[' + str(vtx) + ']'], col) #vtx move
                    valVtx = getSliceVtxWght(lSlices, vtx)
                    # a revoir, si un makeNegative of a ete fait (lips up L, R Mid) le scrit ne peut pas detecter cr la somme des valeures est egale a 1.0
                    if not valVtx == 1.0:
                        col = (0.256, 0.7957, 0.872) #vtx wght on sep slices BLUE
                    for slice in lSlices:
                        bs = getBsDef(slice, None)[0]
                        mc.setAttr(bs + '.inputTarget[0].baseWeights[' + str(vtx) + ']', 1.0)
                        lib_checkers.vtxColor([slice+'.vtx['+str(vtx)+']'], col)
                print 'done for :', sep, '->', lSlices
    print 'DONE'


def getSliceVtxWght(lSlices, vtxId):
    val = 0.0
    for slice in lSlices:
        bs = getBsDef(slice, None)[0]
        val += mc.getAttr(bs + '.inputTarget[0].baseWeights[' + str(vtxId) + ']')
    return val

def clearVtxColor(getSel, *args, **kwargs):
    lObj = []
    if isinstance(getSel, list):
        lObj = getSel
    else:
        lObj = getSel()
    lib_checkers.vtxColor(lObj, None)

def initMixTrgtSculpt(mshResult):
    storageGrp = geStorageGrp('MIXTRGT', mshResult)
    bsMix = getBsDef(mshResult, 2)
    if not bsMix:
        mixResult = genResult(mshResult, 'MIXTRGT')
        mc.setAttr(mixResult+'.v', False)
        bsMix = mc.blendShape(mixResult, n='bsMixTrgt'+mshResult[len(mshResult.split('_')[0]):])[0]
        bsTypeAttrr(bsMix, 2)
        if not mc.attributeQuery('listMixCombinations', n=bsMix, ex=True):
            mc.addAttr(bsMix, ln='listMixCombinations', dt='string', multi=True)
        if not mc.attributeQuery('listMixResults', n=bsMix, ex=True):
            mc.addAttr(bsMix, ln='listMixResults', dt='string', multi=True)
    return bsMix

def initMixShpSculpt(mshResult):
    storageGrp = geStorageGrp('MIXSHP', mshResult)
    bsMix = getBsDef(mshResult, 5)
    if not bsMix:
        mixResult = genResult(mshResult, 'MIXSHP')
        mc.setAttr(mixResult+'.v', False)
        bsMix = mc.blendShape(mixResult, n='bsMixShp'+mshResult[len(mshResult.split('_')[0]):])[0]
        bsTypeAttrr(bsMix, 5)
        if not mc.attributeQuery('listMixCombinations', n=bsMix, ex=True):
            mc.addAttr(bsMix, ln='listMixCombinations', dt='string', multi=True)
        if not mc.attributeQuery('listMixResults', n=bsMix, ex=True):
            mc.addAttr(bsMix, ln='listMixResults', dt='string', multi=True)



def ctrMixCombination_v2(getSel, inBetVal='',*args, **kwargs):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mixTrgt     #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    #_________________#
    lMshResult = getSel()
    geteditShp = False

    chkeditShp = mc.ls('*.editShp', r=True) or []
    if chkeditShp:
        geteditShp = mc.getAttr(chkeditShp[0])
    """""
    #check if all trigger are from the same zone -> to remove
    if geteditShp == False:
        for mshResult in lMshResult:
            print "get bs trgt in crtMixComb"
            bsTrgt = getBsDef(mshResult, 0) or []
            if bsTrgt:
                print 'bs trgt =', bsTrgt
                lTrgr = getActivTrgt(bsTrgt[0]) or []
                print 'toto', lTrgr
                
                if lTrgr:
                    lZonesChk = []
                    for trgr in lTrgr.keys():
                        if not trgr.startswith(lTrgr.keys()[0].split('_')[0]):
                            lZonesChk.append(trgr)
                        if lZonesChk:
                            mc.warning('you can only generate mix on trgt from the same zone : ')
                            print lTrgr.keys()[0], ':', lZonesChk
                            return
                
            else:
                print 'no bs trgt founded'
                return
    """""



    for mshResult in lMshResult:
        print 'working on', mshResult
        toDebbug = ''
        shpEdit = False
        if mc.attributeQuery('editShp', n=mshResult, ex=True):
            shpEdit = True
        if shpEdit == True:
            print 'oups'
            initMixShpSculpt(mshResult)
        else:
            toDebbug = initMixTrgtSculpt(mshResult)
            print "trgt sculpt initiated"
        dicActivedTrgr = {}
        skinActived = False
        lBs = []
        lTrgr = []
        #get bs for meshResult
        bsTrgt = getBsDef(mshResult, 0) or []
        bsCor = getBsDef(mshResult, 1) or []
        #print "________________________________________"
        #print "________________________________________"
        bsMix = getBsDef(mshResult, 2) or []
        #print 'HERE suce', bsTrgt, bsMix
        if shpEdit == True:
            bsTrgt = getBsDef(mshResult, 4) or []
            bsMix = getBsDef(mshResult, 5) or []

        if bsTrgt:
            lBs.append(bsTrgt[0])
            bsTrgt = bsTrgt[0]
        if bsCor:
            lBs.append(bsCor[0])
            bsCor = bsCor[0]
        if bsMix:
            lBs.append(bsMix[0])
            bsMix = bsMix[0]
        #else:
            #bsMix = toDebbug

        if shpEdit == True:
            if bsTrgt and bsMix:
                lBs = [bsTrgt, bsMix]
        part = mshResult[len(mshResult.split('_')[0])+1 :].capitalize()
        #dic {bs: {trigger: value, trigger: value}, bs: {trigger: value}} and list all triggers
        for bs in lBs:
            if mc.getAttr(bs+'.bsType') != 3:
                lTrgt = getActivTrgt(bs) or []
                if lTrgt:
                    for trgt in lTrgt:
                        if trgt.startswith('cor'):
                            skinActived = True #a consolider pour checker si une corrective est avtivee!!
                        fullName = bs+'.'+trgt
                        val = mc.getAttr(fullName)
                        if not bs in dicActivedTrgr.keys():
                            dicActivedTrgr[bs] = {}
                            if mc.getAttr(bs+'.bsType') == 1:
                                skinActived = True
                        if not trgt in dicActivedTrgr[bs].keys():
                            dicActivedTrgr[bs][trgt] = val
                        if not fullName in lTrgr:
                            lTrgr.append(fullName)


        nMix = 'mix'+part
        lTrgr.sort()
        for trgr in lTrgr:
            #generate combination result name
            nTrgr = trgr.replace('Sculpt', '')
            if ':' in nTrgr:
                nTrgr = nTrgr.split(':')[-1]
            #print nTrgr
            nTrgr = nTrgr.replace('6000', '')
            nTrgr = nTrgr.split('.')[-1]
            if '_' in nTrgr.split('.')[-1]:
                nTrgr = nTrgr[len(nTrgr.split('.')[-1].split('_')[0]) + 1:].replace('_', '')
            nMix += '_'+nTrgr

        nMixSculpt = nMix+'Sculpt'

        lComb = []
        lCombId = mc.getAttr(bsMix+'.listMixCombinations', mi=True) or []
        if lCombId:
            for combId in lCombId:
                lComb.append(mc.getAttr(bsMix+'.listMixCombinations['+str(combId)+']'))
        if not nMix in lComb:
            lastId = getAvalableId(bsMix, 'listMixCombinations')
            mc.setAttr(bsMix+'.listMixCombinations['+str(lastId)+']', nMix, type='string')
            #mc.setAttr(bsMix+'.listMixResults['+str(lastId)+']', nMix, type='string')
            nspace = ''
            if shpEdit == True:
                storageGrpSculpt = geStorageGrp('MIXSHP', mshResult, extra='Sculpt')
                #nspace = crtNspace(mshResult, 'MIXSHP')
            else:
                storageGrpSculpt = geStorageGrp('MIXTRGT', mshResult, extra='Sculpt')
                #nspace = crtNspace(mshResult, 'MIXTRGT')

            mixSculpt = mc.duplicate(mshResult, n=nMixSculpt)[0]
            mc.parent(mixSculpt, storageGrpSculpt)
            for attr in ('translate', 'rotate', 'scale'):
                for chan in ['X', 'Y', 'Z']:
                    mc.setAttr(mixSculpt+'.'+attr+chan, lock=False)
            cleanShapes(mixSculpt)
            #mc.addAttr(mixSculpt, ln='shpSource', at='message')
            #mc.setAttr(mixSculpt+'.shpSource', mshResult, type='string')
            mc.addAttr(mixSculpt, ln='shpSource', at='message')
            mc.connectAttr(mshResult+'.message', mixSculpt+'.shpSource', f=True)
            #mc.addAttr(mixSculpt, ln='shpResult', at='message')
            mc.addAttr(mixSculpt, ln='trgrList', dt='string', multi=True)
            mc.addAttr(mixSculpt, ln='trgrValues', at='float', multi=True)
            mc.addAttr(mixSculpt, ln='hadSkinActived', at='bool', dv=skinActived)
            mc.namespace(set=':')

            inc = 0
            #print dicActivedTrgr
            for bs in dicActivedTrgr.keys():
                for trgr in dicActivedTrgr[bs]:
                    #print 'HERE', trgr
                    trigger = bs+'.'+trgr
                    val = dicActivedTrgr[bs][trgr]
                    mc.setAttr(mixSculpt+'.trgrList['+str(inc)+']', trigger, type='string')
                    mc.setAttr(mixSculpt+'.trgrValues['+str(inc)+']', val)
                    inc += 1
            #connectMixShp_v3([mixSculpt])
        else:
            mc.warning(nMix+' already exists')



def connectMixCorr(mixTrgt, mshMix, bsMix):
    lTrgt = mc.blendShape(bsMix, q=True, t=True) or []
    lastId = getLastInputId(bsMix)+1
    if not mixTrgt.split(':')[-1] in lTrgt:
        mc.blendShape(bsMix, e=True, t=(mshMix, lastId, mixTrgt, 1.0))
#connectMixCorr('shp_neutral_Mix', 'shp_corrective')


def blendMixTrgt(shp, bsTrgt, bsMix):
    shpSrc = mc.listConnections(shp+'.shpSource', d=True)[0]
    shpResult = mc.listConnections(shp+'.shpResult', s=True)[0]

    add = mc.createNode('plusMinusAverage', n='tete')
    mc.setAttr(add+'.operation', 1)
    ran = mc.createNode('setRange', n='smab')
    mc.setAttr(ran+'.maxX', 1)
    mc.setAttr(ran+'.maxY', 1)
    dicMultWght = {}
    for i in range(0, mc.getAttr(shp+'.trgrList', s=True)-1):
        nTrgt = mc.getAttr(shp+'.trgrList['+str(i)+']')
        dicMultWght[i+1] = mc.createNode('multDoubleLinear', n='suce')

    blendWght = mc.createNode('blendColors', n='bld_smab')
    mc.setAttr(blendWght+'.color2', 0, 0, 0, type='double3')

    tmpActivator = mc.createNode('multDoubleLinear', n='mDL_tempActivator')
    mc.addAttr(tmpActivator, ln='tmpActivator', at='bool', dv=True)
    mc.setAttr(tmpActivator+'.input2', 1.0)

    for i in range(0, mc.getAttr(shp+'.trgrList', s=True)):
        nTrgt = mc.getAttr(shp+'.trgrList['+str(i)+']')
        valTrgt = mc.getAttr(shp+'.trgrValues['+str(i)+']')

        mltd = mc.createNode('multDoubleLinear', n='toto')
        div = mc.createNode('multiplyDivide', n='tata')
        if i < 2:
            mc.connectAttr(nTrgt, dicMultWght[1]+'.input'+str(i+1))
        else:
            mc.connectAttr(dicMultWght[i-1]+'.output', dicMultWght[i]+'.input1')
            mc.connectAttr(nTrgt, dicMultWght[i]+'.input2')


        mc.setAttr(div+'.operation', 2)
        mc.setAttr(div+'.input2X', 100)

        normVal = setRange(0.0, float(mc.getAttr(shp+'.trgrList', s=True)), 0.0, 1.0, valTrgt)
        ratioVal = (normVal*100)/1
        mc.setAttr(mltd+'.input2', ratioVal)


        mc.connectAttr(nTrgt, mltd+'.input1')
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
    #mc.connectAttr(blendWght+'.outputR', bsMix+'.'+shpResult.split(':')[-1])
    mc.connectAttr(blendWght+'.outputR', tmpActivator+'.input1')
    mc.connectAttr(tmpActivator+'.output', bsMix+'.'+shpResult.split(':')[-1])

#blendMixTrgt(mc.ls(sl=True)[0])

def blendMixTrgt_v2(shp, bsTrgt, bsMix):
    lMult = []
    lRemap = []

    shpSrc = mc.listConnections(shp + '.shpSource', d=True)[0]
    shpResult = mc.listConnections(shp + '.shpResult', s=True)[0]
    lenTrgr = mc.getAttr(shp + '.trgrList', s=True)

    for i in range(0, lenTrgr):
        nTrgt = mc.getAttr(shp + '.trgrList[' + str(i) + ']')
        valTrgt = mc.getAttr(shp + '.trgrValues[' + str(i) + ']')
        nTrgt = mc.getAttr(shp + '.trgrList[' + str(i) + ']')

        remap = mc.createNode('remapValue', n='rm_trgr')
        mc.connectAttr(nTrgt, remap + '.inputValue')

        mc.setAttr(remap + '.value[0].value_Position', 0.0)  # horizontal
        mc.setAttr(remap + '.value[0].value_FloatValue', 0.0)  # vertical

        mc.setAttr(remap + '.value[1].value_Position', valTrgt)
        mc.setAttr(remap + '.value[1].value_FloatValue', 1.0)

        mc.setAttr(remap + '.value[2].value_Position', 1.0)
        mc.setAttr(remap + '.value[21].value_FloatValue', 0.0)

        if i >= 1:
            mlt = mc.createNode('multDoubleLinear', n='mDL_tempActivator')
            mc.addAttr(mlt, ln='trgrMult', at='bool', dv=True)
            if lMult:
                mc.connectAttr(lMult[-1] + '.output', mlt + '.input1')
            else:
                mc.connectAttr(lRemap[-1] + '.outValue', mlt + '.input1')
            mc.connectAttr(remap + '.outValue', mlt + '.input2')
            lMult.append(mlt)
        lRemap.append(remap)

    mc.connectAttr(lMult[-1] + '.output', bsMix + '.' + shpResult.split(':')[-1], f=True)


#blendMixTrgt_v2(mc.ls(sl=True)[0], 'bsTrgtr_head', 'bsMixTrgt_head')



def connectMixShp_v3(getSel, *args, **kwargs):
    lMixSculpt = getSel()
    for mixSculpt in lMixSculpt:
        loadMixValues([mixSculpt])
        mc.dgdirty(a=True)
        shpEdit = False
        if mc.attributeQuery('editShp', n=mixSculpt, ex=True):
            shpEdit = True
        if mc.attributeQuery('shpSource', n=mixSculpt, ex=True):
            mshResult = mc.listConnections(mixSculpt+'.shpSource', s=True)[0]
            #NAMMING
            nspace = mixSculpt[: len(mixSculpt)-len(mixSculpt.split(':')[-1])]
            nMix = mixSculpt.replace('Sculpt', '')+'__mix__Tmp'
            mshSrc  = mc.listConnections(mixSculpt+'.shpSource', s=True, p=False)[0]
            hadSkin = False
            chkMixRes = False
            getMixRes = []
            mixResult = ''
            lBs = []

            if mc.attributeQuery('hadSkinActived', n=mixSculpt, ex=True):
                if mc.getAttr(mixSculpt+'.hadSkinActived') == 1:
                    hadSkin = True

            #0= target  #1 = corrective  #2 = mixTrgt  #3 = Result  #4 = Shapes  #5 = mixShp
            bsTrgt = getBsDef(mshSrc, 0) or []
            bsCor = getBsDef(mshSrc, 1) or []
            bsMix = getBsDef(mshSrc, 2) or []
            bsResult = getBsDef(mshSrc, 3) or []
            if shpEdit == True:
                bsTrgt = getBsDef(mshSrc, 4) or []
                bsMix = getBsDef(mshSrc, 5) or []
                bsResult = []

            if bsTrgt:
                lBs.append(bsTrgt[0])
            if bsCor:
                lBs.append(bsCor[0])
            if bsMix:
                lBs.append(bsMix[0])
            if bsResult:
                lBs.append(bsResult[0])

            for bs in lBs:
                mc.setAttr(bs+'.envelope', 0)

            lSkin = mc.ls(mc.findDeformers(mshSrc), type='skinCluster')
            for skin in lSkin:
                mc.setAttr(skin+'.envelope', 0)

            mixTrgt = mc.duplicate(mshSrc, n=nMix)[0]
            mc.setAttr(mixTrgt+'.v', False)

            remap = ''

            if mc.attributeQuery('shpResult', n=mixSculpt, ex=True):
                getMixRes = mc.listConnections(mixSculpt+'.shpResult', d=True) or []
                if getMixRes:
                    chkMixRes = True
            else:
                mc.addAttr(mixSculpt, ln='shpResult', at='message')

            storageGrp = ''
            if chkMixRes == False:
                mc.connectAttr(mixTrgt+'.message', mixSculpt+'.shpResult')
                mc.addAttr(mixTrgt, ln='mixResult', at='bool', dv=1)
                mixTrgt = mc.rename(mixTrgt, mixTrgt.replace('__mix__Tmp', ''))
                if shpEdit == True:
                    storageGrp = geStorageGrp('MIXSHP', mshResult)
                else:
                    storageGrp = geStorageGrp('MIXTRGT', mshResult)

                mc.parent(mixTrgt, storageGrp)
            elif chkMixRes == True:
                chkMixResult = mc.listConnections(mixSculpt+'.shpResult', d=True) or []
                if chkMixResult:
                    trgtMixWght = getTrgtAliasIndex(getMixRes[0])[getMixRes[0]]['alias']
                    tmpActivator = mc.listConnections(bsMix[0]+'.'+trgtMixWght, s=True, d=False)[0]

                    mixResult = mc.listConnections(mixSculpt+'.shpResult', d=True)[0]
                    remap = mc.listConnections(tmpActivator+'.input2', s=True, d=False)[0]
                    mc.setAttr(remap+'.outputMax', 0)
            ###########################################################

            #set bs pose#############################################################
            lActivedTrgt = mc.getAttr(mixSculpt+'.trgrList', s=True) or []
            for id in range(0, lActivedTrgt):
                activedTrgt = mc.getAttr(mixSculpt+'.trgrList['+str(id)+']')
                activatedValue = mc.getAttr(mixSculpt+'.trgrValues['+str(id)+']')
                try:
                    mc.setAttr(activedTrgt, activatedValue)
                except:
                    pass


            mixSculptSrc = mixSculpt
            lMovedVtx = []

            vtxs = mc.polyEvaluate(mshSrc, v=True)
            posSrc = mc.xform(mshSrc, q=True, ws=True, t=True)
            posTrgt = mc.xform(mixSculpt, q=True, ws=True, t=True)
            posDest = mc.xform(mixTrgt, q=True, ws=True, t=True)

            for skin in lSkin:
                mc.setAttr(skin+'.envelope', 1)

            if hadSkin == False:
                for bs in lBs:
                    mc.setAttr(bs + '.envelope', 1)


            elif hadSkin == True:
                try:
                    mc.parent(mixResult, world=True)
                except:
                    pass
                difSkinShp = mc.invertShape(mshSrc, mixSculpt)
                posTrgt = mc.xform(difSkinShp, q=True, ws=True, t=True)
                mixSculptSrc = difSkinShp
                try:
                    mc.parent(mixResult, mixSculpt)
                except:
                    pass
                for bs in lBs:
                    mc.setAttr(bs+'.envelope', 1)

                for skin in lSkin:
                    mc.setAttr(skin+'.envelope', 0)


            ########################################################################
            for i in range(0, vtxs):
                posSrcVtx = mc.xform(mshSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                posTrgtVtx = mc.xform(mixSculptSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                posDestVtx = mc.xform(mixTrgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)

                difSrc = [posSrcVtx[0]-posSrc[0], posSrcVtx[1]-posSrc[1], posSrcVtx[2]-posSrc[2]]
                difTrgt = [posTrgtVtx[0]-posTrgt[0], posTrgtVtx[1]-posTrgt[1], posTrgtVtx[2]-posTrgt[2]]
                difDest = [posDestVtx[0]-posDest[0], posDestVtx[1]-posDest[1], posDestVtx[2]-posDest[2]]


                if not difSrc == difTrgt:
                    val = [difSrc[0] - difTrgt[0], difSrc[1] - difTrgt[1], difSrc[2] - difTrgt[2]]
                    valDif = [difDest[0] - val[0], difDest[1] - val[1], difDest[2] - val[2]]
                    mc.move(valDif[0], valDif[1], valDif[2],  mixTrgt+'.vtx['+str(i)+']', co=True)
                    lMovedVtx.append(i)

            mc.addAttr(mixTrgt, ln='trgrList', dt='string', multi=True)
            mc.addAttr(mixTrgt, ln='trgrValues', at='float', multi=True)

            if hadSkin == True:
                mc.delete(mixSculptSrc)

            #repport mix trgt values
            if chkMixRes == False:
                unlockChans(mixTrgt)
                for i in range(0, mc.getAttr(mixSculpt+'.trgrList', s=True)):
                    val = mc.getAttr(mixSculpt+'.trgrList['+str(i)+']')
                    mc.setAttr(mixTrgt+'.trgrList['+str(i)+']', val, type='string')
                    val = mc.getAttr(mixSculpt+'.trgrValues['+str(i)+']')
                    mc.setAttr(mixTrgt+'.trgrValues['+str(i)+']', val)
                mshMix = mc.blendShape(bsMix[0], q=True, g=True)[0]
                connectMixCorr(mixTrgt, mshMix, bsMix[0])
                #blendMixTrgt(mixSculpt, bsTrgt[0], bsMix[0])
                blendMixTrgt_v2(mixSculpt, bsTrgt[0], bsMix[0])

            elif chkMixRes == True:
                snapShp([mixTrgt, mixResult])
                mc.delete(mixTrgt)
                mc.setAttr(remap+'.outputMax', 1)

            if mc.attributeQuery('movedVtx', n=mixResult, ex=True):
                mc.deleteAttr(mixResult+'.movedVtx')
            mc.addAttr(mixResult, ln='movedVtx', dt='string', multi=True)
            id = 0
            for movedVtx in lMovedVtx:
                mc.setAttr(mixResult+'.movedVtx['+str(id)+']', movedVtx, type='string')
                id += 1

            for skin in lSkin:
                mc.setAttr(skin+'.envelope', 1)
        mc.dgdirty(a=True)

#connectMixShp_v2(mc.ls(sl=True))


def ctrMixCombinationInbet(getSel, inBetVal='', *args, **kwargs):
    # TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mixTrgt     #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    # _________________#
    lMshResult = getSel()
    geteditShp = False

    chkeditShp = mc.ls('*.editShp', r=True) or []
    if chkeditShp:
        geteditShp = mc.getAttr(chkeditShp[0])
    """""
    #check if all trigger are from the same zone -> to remove
    if geteditShp == False:
        for mshResult in lMshResult:
            print "get bs trgt in crtMixComb"
            bsTrgt = getBsDef(mshResult, 0) or []
            if bsTrgt:
                print 'bs trgt =', bsTrgt
                lTrgr = getActivTrgt(bsTrgt[0]) or []
                print 'toto', lTrgr

                if lTrgr:
                    lZonesChk = []
                    for trgr in lTrgr.keys():
                        if not trgr.startswith(lTrgr.keys()[0].split('_')[0]):
                            lZonesChk.append(trgr)
                        if lZonesChk:
                            mc.warning('you can only generate mix on trgt from the same zone : ')
                            print lTrgr.keys()[0], ':', lZonesChk
                            return

            else:
                print 'no bs trgt founded'
                return
    """""

    for mshResult in lMshResult:
        print
        'working on', mshResult
        toDebbug = ''
        shpEdit = False
        if mc.attributeQuery('editShp', n=mshResult, ex=True):
            shpEdit = True
        if shpEdit == True:
            print
            'oups'
            initMixShpSculpt(mshResult)
        else:
            toDebbug = initMixTrgtSculpt(mshResult)
            print
            "trgt sculpt initiated"
        dicActivedTrgr = {}
        skinActived = False
        lBs = []
        lTrgr = []
        # get bs for meshResult
        bsTrgt = getBsDef(mshResult, 0) or []
        bsCor = getBsDef(mshResult, 1) or []
        # print "________________________________________"
        # print "________________________________________"
        bsMix = getBsDef(mshResult, 2) or []
        # print 'HERE suce', bsTrgt, bsMix
        if shpEdit == True:
            bsTrgt = getBsDef(mshResult, 4) or []
            bsMix = getBsDef(mshResult, 5) or []

        if bsTrgt:
            lBs.append(bsTrgt[0])
            bsTrgt = bsTrgt[0]
        if bsCor:
            lBs.append(bsCor[0])
            bsCor = bsCor[0]
        if bsMix:
            lBs.append(bsMix[0])
            bsMix = bsMix[0]
        # else:
        # bsMix = toDebbug

        if shpEdit == True:
            if bsTrgt and bsMix:
                lBs = [bsTrgt, bsMix]
        part = mshResult[len(mshResult.split('_')[0]) + 1:].capitalize()
        # dic {bs: {trigger: value, trigger: value}, bs: {trigger: value}} and list all triggers
        for bs in lBs:
            if mc.getAttr(bs + '.bsType') != 3:
                lTrgt = getActivTrgt(bs) or []
                if lTrgt:
                    for trgt in lTrgt:
                        if trgt.startswith('cor'):
                            skinActived = True  # a consolider pour checker si une corrective est avtivee!!
                        fullName = bs + '.' + trgt
                        val = mc.getAttr(fullName)
                        if not bs in dicActivedTrgr.keys():
                            dicActivedTrgr[bs] = {}
                            if mc.getAttr(bs + '.bsType') == 1:
                                skinActived = True
                        if not trgt in dicActivedTrgr[bs].keys():
                            dicActivedTrgr[bs][trgt] = val
                        if not fullName in lTrgr:
                            lTrgr.append(fullName)

        nMix = 'mix' + part
        lTrgr.sort()
        for trgr in lTrgr:
            # generate combination result name
            nTrgr = trgr.replace('Sculpt', '')
            if ':' in nTrgr:
                nTrgr = nTrgr.split(':')[-1]
            # print nTrgr
            nTrgr = nTrgr.replace('6000', '')
            nTrgr = nTrgr.split('.')[-1]
            if '_' in nTrgr.split('.')[-1]:
                nTrgr = nTrgr[len(nTrgr.split('.')[-1].split('_')[0]) + 1:].replace('_', '')
            nMix += '_' + nTrgr

        nMixSculpt = nMix + 'Sculpt'

        lComb = []
        lCombId = mc.getAttr(bsMix + '.listMixCombinations', mi=True) or []
        if lCombId:
            for combId in lCombId:
                lComb.append(mc.getAttr(bsMix + '.listMixCombinations[' + str(combId) + ']'))
        if not nMix in lComb:
            lastId = getAvalableId(bsMix, 'listMixCombinations')
            mc.setAttr(bsMix + '.listMixCombinations[' + str(lastId) + ']', nMix, type='string')
            # mc.setAttr(bsMix+'.listMixResults['+str(lastId)+']', nMix, type='string')
            nspace = ''
            if shpEdit == True:
                storageGrpSculpt = geStorageGrp('MIXSHP', mshResult, extra='Sculpt')
                # nspace = crtNspace(mshResult, 'MIXSHP')
            else:
                storageGrpSculpt = geStorageGrp('MIXTRGT', mshResult, extra='Sculpt')
                # nspace = crtNspace(mshResult, 'MIXTRGT')

            mixSculpt = mc.duplicate(mshResult, n=nMixSculpt)[0]
            mc.parent(mixSculpt, storageGrpSculpt)
            for attr in ('translate', 'rotate', 'scale'):
                for chan in ['X', 'Y', 'Z']:
                    mc.setAttr(mixSculpt + '.' + attr + chan, lock=False)
            cleanShapes(mixSculpt)
            # mc.addAttr(mixSculpt, ln='shpSource', at='message')
            # mc.setAttr(mixSculpt+'.shpSource', mshResult, type='string')
            mc.addAttr(mixSculpt, ln='shpSource', at='message')
            mc.connectAttr(mshResult + '.message', mixSculpt + '.shpSource', f=True)
            # mc.addAttr(mixSculpt, ln='shpResult', at='message')
            mc.addAttr(mixSculpt, ln='trgrList', dt='string', multi=True)
            mc.addAttr(mixSculpt, ln='trgrValues', at='float', multi=True)
            mc.addAttr(mixSculpt, ln='hadSkinActived', at='bool', dv=skinActived)
            mc.namespace(set=':')

            inc = 0
            # print dicActivedTrgr
            for bs in dicActivedTrgr.keys():
                for trgr in dicActivedTrgr[bs]:
                    # print 'HERE', trgr
                    trigger = bs + '.' + trgr
                    val = dicActivedTrgr[bs][trgr]
                    mc.setAttr(mixSculpt + '.trgrList[' + str(inc) + ']', trigger, type='string')
                    mc.setAttr(mixSculpt + '.trgrValues[' + str(inc) + ']', val)
                    inc += 1
            # connectMixShp_v3([mixSculpt])
        else:
            mc.warning(nMix + ' already exists')


def mirrorMix(getSel, srcSide, *args, **kwargs):
    lMixSculpt = getSel()
    mSide = 'R'
    if srcSide == mSide:
        mSide = 'L'
    for mixSculpt in lMixSculpt:
        lIds = mc.getAttr(mixSculpt+'.trgrList', mi=True) or []
        if lIds:
            for id in lIds:
                trgrAttr = mc.getAttr(mixSculpt+'.trgrList['+str(id)+']')
                trgr = trgrAttr.split('.')[-1]
                trgrType = mc.getAttr(trgr+'.extactedAs')
                if trgrType == 'TRGT':
                    bs = trgrAttr.split('.')[0]
                    mTrgr = trgr.replace(side+'_', mSide+'_')[-1]
                    if mc.objExists(mTrgr):
                        val = mc.getAttr(mixSculpt+'.trgrValues['+str(id)+']')
                        mc.setAttr(bs+'.'+trgr, 0)
                        mc.setAttr(bs+'.'+trgr, val)
                elif trgrType == 'COR':
                    print 'to do'

            #ctrMixCombination_v2([mixSculpt])
            #mirrorSculpt(msh)
            #connectMixShp_v3([mixSculpt])


def flipMix(lMixSculpt, SrcSide):
    for mixSculpt in lMixSculpt:
        print 'to DO'


def propagateMix(getSel, *args, **kwargs):
    lMixSculpt = getSel()
    mixSrc = lMixSculpt[0]
    mshReferal = mc.listConnections(mixSrc+'.shpSource', s=True)[0]
    activeDef(mshReferal, False)
    vtxs = mc.polyEvaluate(mixSrc, v=True)
    posSrc = mc.xform(mixSrc, q=True, ws=True, t=True)
    posReferal = mc.xform(mshReferal, q=True, ws=True, t=True)

    for sculpt in lMixSculpt[1 :]:
        mixDest = mc.listConnections(sculpt+'.shpResult', s=True)[0]
        tmpDest = mc.duplicate(mshReferal, n=mixDest+'_tmp')[0]

        posSculpt = mc.xform(sculpt, q=True, ws=True, t=True)
        posDest = mc.xform(tmpDest, q=True, ws=True, t=True)

        for i in range(0, vtxs):
            posRefVtx = mc.xform(mshReferal+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posSrcVtx = mc.xform(mixSrc+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posSculptVtx = mc.xform(sculpt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
            posDestVtx = mc.xform(tmpDest+'.vtx['+str(i)+']', q=True, ws=True, t=True)


            localRef = [posRefVtx[0]-posReferal[0], posRefVtx[1]-posReferal[1], posRefVtx[2]-posReferal[2]]
            localSrc = [posSrcVtx[0]-posSrc[0], posSrcVtx[1]-posSrc[1], posSrcVtx[2]-posSrc[2]]
            localSculpt = [posSculptVtx[0]-posSculpt[0], posSculptVtx[1]-posSculpt[1], posSculptVtx[2]-posSculpt[2]]
            localDest = [posDestVtx[0]-posDest[0], posDestVtx[1]-posDest[1], posDestVtx[2]-posDest[2]]

            difSrc = [localSrc[0]-localRef[0], localSrc[1]-localRef[1], localSrc[2]-localRef[2]]
            difSculpt = [localSculpt[0]-localRef[0], localSculpt[1]-localRef[1], localSculpt[2]-localRef[2]]

            dif = [difSculpt[0]-difSrc[0], difSculpt[1]-difSrc[1], difSculpt[2]-difSrc[2]]
            val = [dif[0]*-1, dif[1]*-1, dif[2]*-1]

            localDest = [localDest[0]-val[0], localDest[1]-val[1], localDest[2]-val[2]]

            mc.move(localDest[0], localDest[1], localDest[2],  tmpDest+'.vtx['+str(i)+']', co=True)

        print 'toto'
        snapShp([tmpDest, mixDest])
        print 'tutu'


    activeDef(mshReferal, True)
    mc.delete(tmpDest)


def reorderMix(getSel, *args, **kwargs):
    lMixSculpt = []
    if isinstance(getSel, list):
        lMixSculpt = getSel
    else:
        lMixSculpt = getSel()
    for mixSculpt in lMixSculpt:
        print mixSculpt

def removeMix(getSel, *args, **kwargs):
    lMix = []
    if isinstance(getSel, list):
        lMix = getSel
    else:
        lMix = getSel()
    for mix in lMix:
        if mc.attributeQuery('trgrList', n=mix, ex=True):
            mixSculpt = mix
            mixRes = mix
            if not mc.attributeQuery('mixResult', n=mix, ex=True):
                mixRes = mc.listConnections(mix+'.shpResult', s=True)[0]
            else:
                mixSculpt = mc.listConnections(mix+'.message', d=True)[0]
            mixDatas = getTrgtMshDatas(mixRes)
            bsMix = mixDatas[mixRes]['bs']
            lCombId = mc.getAttr(bsMix + '.listMixCombinations', mi=True) or []
            if lCombId:
                for combId in lCombId:
                    if mc.getAttr(bsMix+'.listMixCombinations['+str(combId)+']') == mixRes.split(':')[-1]:
                        mc.removeMultiInstance(bsMix+'.listMixCombinations['+str(combId)+']', b=True)
                        #mc.removeMultiInstance(bsMix+'.listMixResults['+str(combId)+']', b=True)

            alias = mixDatas[mixRes]['alias']
            wght = mixDatas[mixRes]['weight']
            id = mixDatas[mixRes]['id']
            mlt = mc.listConnections(bsMix+'.'+alias, s=True)[0]
            mshMix = mc.blendShape(bsMix, q=True, g=True)[0]
            mc.blendShape(bsMix, e=True, rm=True, t=(mshMix, id, mixRes, wght))
            mc.delete([mlt, mixSculpt,mixRes])






def loadMixValues(getSel, *args, **kwargs):
    lMixSculpt = []
    if isinstance(getSel, list):
        lMixSculpt = getSel
    else:
        lMixSculpt = getSel()
    mixSculpt = lMixSculpt[0]
    lId = mc.getAttr(mixSculpt+'.trgrList', mi=True) or []
    if lId:
        dicTrgr = {}
        driver = ''
        for id in lId:
            trgr = mc.getAttr(mixSculpt+'.trgrList['+str(id)+']')
            chkDk = mc.listConnections(trgr, s=True, scn=True, type='animCurve') or []
            if chkDk:
                dKey = mc.listConnections(trgr, s=True, scn=True, type='animCurve')[0]
                attrDriver = mc.listConnections(dKey, s=True, scn=True, type='transform', p=True)[0]

                value = mc.getAttr(mixSculpt+'.trgrValues['+str(id)+']') * 10
                if not mc.keyframe(dKey, q=True, vc=True)[0] == 0:
                    value = value * -1

                if not attrDriver in dicTrgr.keys():
                    dicTrgr[attrDriver] = value
        driver = dicTrgr.keys()[0].split('.')[0]
        lChans = mc.listAttr(driver, ud=True, k=True, v=True, m=False)
        if lChans:
            for chan in lChans:
                mc.setAttr(driver+'.'+chan, 0.0)
            for chan in dicTrgr.keys():
                mc.setAttr(chan, dicTrgr[chan])
#loadMixValues(mc.ls(sl=True)[0])

def loadMixValuesRig(mix, bs):
    lTrgt = mc.blendShape(bs, q=True, t=True) or []
    if lTrgt:
        for trgt in lTrgt:
            if trgt.endswith('6000'):
                try:
                    mc.setAttr(bs+'.'+trgt.split(':')[-1], 0.0)
                except:
                    pass
    lId = mc.getAttr(mix+'.trgrList', mi=True) or []
    if lId:
        dicTrgr = {}
        for id in lId:
            trgr = mc.getAttr(mix+'.trgrList['+str(id)+']')
            value = mc.getAttr(mix + '.trgrValues[' + str(id) + ']')
            driverChan = bs + '.' + trgr.split(':')[-1]
            try:
                mc.setAttr(driverChan, value)
            except:
                pass


#GEN NEUTRAL#################################################################################################################################################################################
def generateNeutral(getSel, *args, **kwargs):
    lObj = getSel()
    genNspace('NTL')
    grp = 'NTL:geo_neutral'
    lNeutral = []
    if not mc.objExists(grp):
        grp = mc.createNode('transform', n='geo_neutral')
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
        chkSg = mc.listConnections(shpSrc,type='shadingEngine') or []
        shdSG = ''
        shd = ''
        if chkSg:
            shdSG = chkSg[0]
            shd = mc.listConnections(shdSG+'.surfaceShader')[0]
            nDup = shd
            if ':' in shd:
                nDup = shd.split(':')[-1]
            newShd = nDup
            if not mc.objExists(nDup):
                newShd = dupShd(shdSG)
            else:
                newShd = mc.listConnections(nDup, type='shadingEngine')[0]
            mc.sets(dup, forceElement=newShd)
        lNeutral.append(dup)

    mc.namespace(set=':')

    for neutral in lNeutral:
        if not mc.attributeQuery('resultMeshs', n=neutral, ex=True):
            mc.addAttr(neutral, ln='resultMeshs', multi=True)
        result = genResult(neutral, '')
        mc.connectAttr(result+'.message', neutral+'.resultMeshs['+str(mc.getAttr(neutral+'.resultMeshs', s=True))+']')
    #mc.setAttr(grp+'.hiddenInOutliner', 1)
    #mel.eval("AEdagNodeCommonRefreshOutliners()")

#generateNeutral(mc.ls(sl=True))

def genResult(neut, type):
    activeDef(neut, False)
    if type:
        genNspace(type)
    nBase = neut
    if ':' in neut:
        nBase = neut.split(':')[-1]
    mshResult = 'result'+nBase[len(nBase.split('_')[0]):]+type
    if not mc.objExists(type+':'+mshResult):
        mshResult = mc.duplicate(neut, n=mshResult)[0]
        unlockChans(mshResult)
        #crtSymAttr([mshResult])
    if not mc.attributeQuery('resultMsh', n=mshResult, ex=True):
        mc.addAttr(mshResult, ln='resultMsh', dt='string')
    mc.setAttr(mshResult+'.resultMsh', type, type='string')
    grpResult = 'geo_result'
    if not mc.objExists(grpResult):
        mc.namespace(set=':')
        grpResult = mc.createNode('transform', n=grpResult)
    try:
        mc.parent(mshResult, grpResult)
    except:
        pass
    conTrgt = True
    if type == '':
        conTrgt = False

    if mc.attributeQuery('editShp', n=neut, ex=True):
        connectShpMix(mshResult, neut, conTrgt)
    else:
        connectResult(mshResult, type, conTrgt)
    activeDef(neut, True)
    return mshResult

def connectResult(msh, type, conTrgt=True):
    mc.namespace(set=':')
    result = msh.split(':')[-1].replace(type, '')
    if not mc.objExists(result):
        result = mc.duplicate(msh, n=msh.split(':')[-1])[0]
    bsRes = getBsDef(result, 3) or []
    if not bsRes:
        bsRes = mc.blendShape(result, n='bsRes'+result[len(result.split('_')[0]):])
        mc.addAttr(bsRes, ln='bsType', at='enum', en='Trgt:Cor:Mix:Res', dv=3)
        skin = mc.ls(mc.listHistory(result, ac=True, f=True), type='skinCluster') or []
        print 'skin check :', skin
        if skin:
            skin = skin[0]
            mc.reorderDeformers(skin, bsRes[0], result)

    if conTrgt == True:
        lWght = mc.blendShape(bsRes[0], q=True, t=True) or []
        id = 0
        if lWght:
            #id = len(lWght)
            id = getLastInputId(bsRes[0]) + 1
        if not msh in lWght:
            mc.blendShape(bsRes[0], edit=True, t=(result, id, msh, 1.0))
            alias = getTrgtMshDatas(msh)[msh]['alias']
            mc.setAttr(bsRes[0]+'.'+alias, 1.0)

def connectShpMix(msh, neut, conTrgt=True):
    #TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mixTrgt     #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    #_________________#
    mc.namespace(set=':')
    bsRes = getBsDef(neut, 4) or []
    #print 'Here again bsRes :', bsRes, neut
    if bsRes:
        if conTrgt == True:
            lWght = mc.blendShape(bsRes[0], q=True, t=True) or []
            id = 0
            if lWght:
                #id = len(lWght)
                id = getLastInputId(bsRes[0])+1
            if not msh in lWght:
                mc.blendShape(bsRes[0], edit=True, t=(neut, id, msh, 1.0))
                alias = getTrgtMshDatas(msh)[msh]['alias']
                mc.setAttr(bsRes[0]+'.'+alias, 1.0)
#GEN TARGETS#################################################################################################################################################################################
def genAdd(neutral, bs, type):
    val = 0
    if type == 'cor':
        val = 1
    if type == 'mix':
        val = 2
    #nspace = crtNspace(neutral, ':TRGT')
    #print nspace
    nBase = neutral
    if ':' in neutral:
        nBase = neutral.split(':')[-1]
    nDup  = type+nBase[len(nBase.split('_')[0]) :]
    dup = mc.duplicate(neutral, n=nDup)[0]
    bsAdd = getBsDef(dup, None) or []
    if not bsAdd:
        bsAdd = mc.blendShape(dup, n='bs_'+type)
        mc.addAttr(bsAdd, ln='bsType', at='enum', en='Trgt:Cor:Mix:Res', dv=val)
    lWght = mc.blendShape(bs, q=True, t=True) or []
    id = 0
    if lWght:
        #id = len(lWght)
        id = getLastInputId(bs)+1
    chkTrgt = mc.blendShape(bsAdd, q=True, t=True) or []
    if not nDup in chkTrgt:
        mc.blendShape(bs, edit=True, t=(neutral, id, dup, 1.0))
    mc.setAttr(bs+'.'+nDup, 1)
    mc.setAttr(bs+'.'+nDup, l=True)
    return dup
#genAdd(mc.ls(sl=True)[0],['bs_head'], 'cor')

def ctrlAttr(ctrl, dicAttrs, mshResult, bs, nspace, storageGrp):
    for attr in dicAttrs.keys():
        if not mc.attributeQuery(attr, n=ctrl, ex=True):
            mn = 0
            if len(dicAttrs[attr]) == 2:
                mn = -20
            mc.addAttr(ctrl, ln=attr, at='float', k=True, min=mn, max=20)
        valCtrl = 20
        for trgt in dicAttrs[attr]:
            if not mc.objExists(nspace+':'+trgt):
                trgtSculpt = mc.duplicate(mshResult, n=trgt)[0]
                mc.parent(trgtSculpt, storageGrp)
                presetTplFaceChan(trgtSculpt, trgtToCtrlChan())
            lWght = mc.blendShape(bs, q=True, t=True) or []
            id = 0
            if lWght:
                #id = len(lWght)
                id = getLastInputId(bs) + 1
            chkTrgt = mc.blendShape(bs, q=True, t=True) or []
            if not trgt in chkTrgt:
                mc.blendShape(bs, edit=True, t=(mshResult, id, trgtSculpt, 1.0))
            mc.setDrivenKeyframe(bs+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=0, v=0)
            mc.setDrivenKeyframe(bs+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=valCtrl, v=2)
            valCtrl = valCtrl*(-1)

#ctrlAttr(ctrl, dicAttrs, neutral, valCtrl = 20)

def linkTargets(nCtrl, lNeutral):
    nspaceTrgt = 'TRGT'
    genNspace(nspaceTrgt)
    ctrl = nspaceTrgt+':'+nCtrl
    if not mc.objExists(nspaceTrgt+':'+nCtrl):
        ctrl = mc.createNode('transform', n=nCtrl)
        mc.setAttr(ctrl+'.displayHandle', 1)
    for neutral in lNeutral:
        mshResultTrgt = genResult(neutral, nspaceTrgt)
        nspace = crtNspace(neutral, ':TRGT')
        if not mc.objExists(nspace+':geo_targets'):
            gTrgt = mc.createNode('transform', n='geo_targets')
            mc.addAttr(gTrgt, ln='trgtBox', at='bool', dv=1)
        bs = getBsDef(mshResultTrgt, None) or []
        if not bs:
            nBase = neutral
            if ':' in neutral:
                nBase = neutral.split(':')[-1]
            nBs  = 'bs'+nBase[len(nBase.split('_')[0]) :]
            bs = mc.blendShape(mshResultTrgt, n=nBs)
            mc.addAttr(bs, ln='bsType', at='enum', en='Trgt:Cor:Mix:', dv=0)


        #trgtMix = genAdd(mshResultTrgt, bs[0], 'mix')
        #mc.parent(trgtMix, nspace+':geo_targets')

        dic = listOfShapes()
        lKeys = dic.keys()
        for key in sorted(lKeys):
            ctrlAttr(ctrl, dic[key], mshResultTrgt, bs[0], nspace)
        mc.namespace(set=':')

def linkTargets_v2(ctrl, listSel, *args, **kwargs):
    lNeutral = listSel()
    faceDatas = global_presets.faceDatas()
    prod = project_manager.getProject()
    if prod:
        #print 'get face description for', prod
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        faceDatas = module.faceDatas()
    if not mc.objExists(ctrl):
        ctrl = mc.createNode('transform', n=ctrl)
        mc.setAttr(ctrl+'.displayHandle', 1)
    for mshResult in lNeutral:
        mshResultTrgt = genResult(mshResult, 'TRGT')
        mc.setAttr(mshResultTrgt+'.v', 0)
        bsTrgt = getBsDef(mshResultTrgt, 0) or []
        if not bsTrgt:
            bsTrgt = mc.blendShape(mshResultTrgt, n='bsTrgtr'+mshResult[len(mshResult.split('_')[0]):])[0]
            bsTypeAttrr(bsTrgt, 0)
        dic = faceDatas.listOfShapes()
        lKeys = dic.keys()
        nspace = crtNspace(mshResult, nsFather='TRGT')
        storageGrp = geStorageGrp('TRGT', mshResult)
        for key in sorted(lKeys):
            ctrlAttr(ctrl, dic[key], mshResultTrgt, bsTrgt, nspace, storageGrp)
        mc.namespace(set=':')

def cleanAllBsTrgt(listSel, *args, **kwargs):
    lBs = getBsDef()
    for bs in lBs:
        print bs


def getTrgtAliasIndex(msh):
    #print msh
    dicMsh = {}
    lHist = mc.listHistory(msh, f=True)
    bs = mc.ls(lHist, type='blendShape')[0]
    lWght = mc.aliasAttr(bs, q=True)
    i = 0
    for id in range(0, len(lWght)/2):
        alias = lWght[i]
        index = lWght[i+1][len(lWght[i+1].split('[')[0])+1:-1]
        trgtAttr = 'inputTarget[0].inputTargetGroup['+index+'].inputTargetItem'
        linputs = mc.getAttr(bs+'.'+trgtAttr, mi=True)
        for input in linputs:
            shpTrgt = mc.listConnections(bs+'.'+trgtAttr+'['+str(input)+'].inputGeomTarget', s=True)[0]
            if shpTrgt == msh:
                dicMsh[msh] = {}
                dicMsh[msh]['alias'] = alias
                dicMsh[msh]['index'] = index
                return dicMsh
        i += 2

#getTrgtAliasIndex('pSphere3')

def getDicBsTrgtDatasAsMsh(bs):
    lWght = mc.aliasAttr(bs, q=True) or []
    if lWght:
        i = 0
        dicTrgtIds = {}
        for id in range(0, len(lWght)/2):
            dicDatas = {}
            dicDatas['alias'] = lWght[i]
            dicDatas['index'] = lWght[i+1][len(lWght[i+1].split('[')[0])+1:-1]
            dicInbet = {}
            trgtAttr = 'inputTarget[0].inputTargetGroup['+dicDatas['index']+'].inputTargetItem'
            linputs = mc.getAttr(bs+'.'+trgtAttr, mi=True)
            for input in linputs:
                mshTrgt = mc.listConnections(bs+'.'+trgtAttr+'['+str(input)+'].inputGeomTarget', s=True)[0]
                if input == 6000:
                    if not mshTrgt in dicTrgtIds.keys():
                        dicTrgtIds[mshTrgt] = {}
                        dicTrgtIds[mshTrgt]['data'] = {}
                    dicTrgtIds[mshTrgt]['data'] = dicDatas
                else:
                    if not mshTrgt in dicInbet.keys():
                        dicInbet[mshTrgt] = {}
                        dicInbet[mshTrgt]['id'] = str(input)
                        dicInbet[mshTrgt]['value'] = str(input*0.001)[1:]

            if dicInbet.keys():
                dicTrgtIds[mshTrgt]['inbet'] = dicInbet

            i += 2
        return dicTrgtIds
    else:
        return None


#getDicBsTrgtDatasAsMsh('bs_teste')

def getDicBsTrgtDatasAsAlias(bs):
    lWght = mc.aliasAttr(bs, q=True)
    i = 0
    dicTrgtIds = {}
    for id in range(0, len(lWght)/2):
        alias = lWght[i]
        index = lWght[i+1][len(lWght[i+1].split('[')[0])+1:-1]
        if not lWght[i] in dicTrgtIds.keys():
            dicTrgtIds[alias] = {}
        dicTrgtIds[alias]['index'] = index
        dicSculpt = {}
        trgtAttr = 'inputTarget[0].inputTargetGroup['+index+'].inputTargetItem'
        lInputs = mc.getAttr(bs+'.'+trgtAttr, mi=True)
        for input in lInputs:
            mshTrgt = mc.listConnections(bs+'.'+trgtAttr+'['+str(input)+'].inputGeomTarget', s=True)[0]
            val = (input-5000.0)/1000
            if not val in dicSculpt.keys():
                dicSculpt[val] = {}
            dicSculpt[val]['trgt'] = mshTrgt
            dicSculpt[val]['id'] = str(input)
        if dicSculpt.keys():
            dicTrgtIds[alias]['sculpt'] = dicSculpt
        i += 2
    return dicTrgtIds
#getDicBsTrgtDatasAsAlias('bs_teste')

def getTrgtMshDatas(trgtMsh):
    dicDatas = {}
    dicDatas[trgtMsh] = {}
    shp = mc.listRelatives(trgtMsh, s=True, ni=True)[0]
    datas = mc.listConnections(shp, type='blendShape', d=True, plugs=True)[0]
    bs = datas.split('.')[0]
    id = int(datas.split('[')[2].split(']')[0])
    input = int(datas.split('[')[-1].split(']')[0])
    wght = (input-5000.0)/1000
    alias = mc.aliasAttr(bs+'.weight['+str(id)+']', q=True)

    dicDatas[trgtMsh]['bs'] = bs
    dicDatas[trgtMsh]['id'] = id
    dicDatas[trgtMsh]['weight'] = wght
    dicDatas[trgtMsh]['alias'] = alias

    return dicDatas
#getTrgtMshDatas('TRGT:HEAD:mo_smile_025')


def addInbet(mshReult, bsType):
    if bsType == 'TRGT':
        type = 0
    if bsType == 'COR':
        type = 1
    if bsType == 'MIX':
        type = 2
    bsTrgt = getBsDef(mc.ls(sl=True)[0], type)[0]
    lActivedTrgt = getActivTrgt(bsTrgt) or []
    if lActivedTrgt:
        if not len(lActivedTrgt) == 1 :
            return 'wait for update with mix'
        elif len(lActivedTrgt) == 1 :
            mshTrgt = mc.listRelatives(mc.blendShape(bsTrgt, q=True, g=True), p=True)[0]
            trgt = lActivedTrgt.keys()[0]
            val = round(lActivedTrgt[trgt], 3)
            dicBsData = getDicBsTrgtDatasAsAlias(bsTrgt)
            if val in dicBsData[trgt]['sculpt'].keys():
                print trgt, 'at val', val, 'already exist so modify it or enter a new value'
                return
            else:
                id = dicBsData[trgt]['index']
                nspace = crtNspace(mshReult, nsFather=bsType)
                storageGrp = mc.ls(nspace+':*', assemblies=True)[0]
                nInbet = trgt+'_'+str(val).replace('.', '')
                trgtInBet = mc.duplicate(mshReult, n=nInbet)[0]
                mc.parent(trgtInBet, storageGrp)
                if bsType == 'TRGT':
                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), trgtInBet, val))
                elif bsType == 'COR':
                    trgtInBetSculpt = mc.rename(trgtInBet, trgtInBet+'Sculpt')
                    if not mc.attributeQuery('result', n=trgtInBetSculpt, ex=True):
                        mc.addAttr(trgtInBetSculpt, ln='result', at='message')
                    difCor = mc.invertShape(mshReult, trgtInBetSculpt)
                    activeDef(mshReult, 0)
                    shpCore = mc.duplicate(mshReult, n=nInbet)[0]
                    unlockChans(shpCore)
                    mc.parent(shpCore, trgtInBetSculpt)
                    activeDef(mshReult, 1)
                    #TMP for get attrs notes and trgt#########
                    if not mc.attributeQuery('shpSource', n=shpCore, ex=True):
                        mc.addAttr(shpCore, ln='shpSource', at='message')
                    mc.connectAttr(trgtInBetSculpt+'.result', shpCore+'.shpSource')
                    #######################################################
                    #bs = getBsTrgt(1)[0]
                    #bs = getBsDef(mshSrc, None)[0]
                    lTrgt = mc.blendShape(bsTrgt, q=True, t=True) or []
                    msh = mc.blendShape(bsTrgt, q=True, g=True)[0]
                    if not shpCore.split(':')[-1] in lTrgt:
                        #id = len(lTrgt)
                        id = getLastInputId(bsTrgt) + 1
                        mc.blendShape(bsTrgt, edit=True, t=(msh, id, shpCore, 1.0))
                    snapShp([difCor, shpCore])
                    mc.delete(difCor)

                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), shpCore, val))

                mc.addAttr(trgtInBet, ln='isInBet', at='bool', dv=True)
#addInbet(mc.ls(sl=True)[0], 'TRGT')

def addInbet_v2(getSel, bsType, *args, **kwargs):
    lMshReult = getSel()
    mshReult = lMshReult[0]
    if bsType == 'TRGT':
        type = 0
    if bsType == 'COR':
        type = 1
    if bsType == 'MIX':
        type = 2
    bsTrgt = ''
    getBsTrgt = getBsDef(mshReult, type) or []
    #print 'SUCE', getBsTrgt

    if getBsTrgt:
        bsTrgt = getBsTrgt[0]
    else:
        print 'toto'

    #print 'HRE toto:', bsTrgt
    lActivedTrgt = getActivTrgt(bsTrgt) or []
    if lActivedTrgt:
        if not len(lActivedTrgt) == 1:
            return 'wait for update with mix'
        elif len(lActivedTrgt) == 1:
            mshTrgt = mc.listRelatives(mc.blendShape(bsTrgt, q=True, g=True), p=True)[0]
            trgt = lActivedTrgt.keys()[0]
            val = round(lActivedTrgt[trgt], 3)
            dicBsData = getDicBsTrgtDatasAsAlias(bsTrgt)
            if val in dicBsData[trgt]['sculpt'].keys():
                print trgt, 'at val', val, 'already exist so modify it or enter a new value'
                return
            else:
                id = dicBsData[trgt]['index']
                nspace = crtNspace(mshReult, nsFather = bsType)
                storageGrp = mc.ls(nspace+':*', assemblies=True)[0]
                trgtInBet = ''
                nInbet = trgt+'_'+str(val).replace('.', '')
                if bsType == 'TRGT':
                    trgtInBet = mc.duplicate(mshReult, n=nInbet)[0]
                    mc.addAttr(trgtInBet, ln='isInBet', at='bool', dv=True)
                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), trgtInBet, val))
                elif bsType == 'COR':
                    trgtInBet = genCorSculpt([mshReult], inBetVal=str(val).replace('.', ''), trgtWght = mshTrgt)[0]
                    mc.addAttr(trgtInBet, ln='isInBet', at='bool', dv=True)
                    shpCore = connectCorrective([trgtInBet])
                    mc.addAttr(shpCore, ln='isInBet', at='bool', dv=True)
                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), shpCore, val))
                    mc.namespace(set=':')
                    return
                elif bsType == 'MIX':
                    print 'MIXOUILLE', nInbet
                    return
                    trgtInBet = ctrMixCombinationInbet([mshReult], inBetVal=str(val).replace('.', ''))[0]
                    mc.addAttr(trgtInBet, ln='isInBet', at='bool', dv=True)
                    shpMix = connectCorrective([trgtInBet])
                    mc.addAttr(shpMix, ln='isInBet', at='bool', dv=True)
                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), shpCore, val))
                    return

                    """
                    if not mc.attributeQuery('result', n=trgtInBetSculpt, ex=True):
                        mc.addAttr(trgtInBetSculpt, ln='result', at='message')
                    difCor = mc.invertShape(mshReult, trgtInBetSculpt)
                    activeDef(mshReult, 0)
                    shpCore = mc.duplicate(mshReult, n=nInbet)[0]
                    unlockChans(shpCore)
                    mc.parent(shpCore, trgtInBetSculpt)
                    activeDef(mshReult, 1)
                    #TMP for get attrs notes and trgt#########
                    if not mc.attributeQuery('shpSource', n=shpCore, ex=True):
                        mc.addAttr(shpCore, ln='shpSource', at='message')
                    mc.connectAttr(trgtInBetSculpt+'.result', shpCore+'.shpSource')
                    #######################################################
                    #bs = getBsTrgt(1)[0]
                    #bs = getBsDef(mshSrc, None)[0]
                    lTrgt = mc.blendShape(bsTrgt, q=True, t=True) or []
                    msh = mc.blendShape(bsTrgt, q=True, g=True)[0]
                    if not shpCore.split(':')[-1] in lTrgt:
                        id = len(lTrgt)
                        mc.blendShape(bsTrgt, edit=True, t=(msh, id, shpCore, 1.0))
                    snapShp([difCor, shpCore])
                    mc.delete(difCor)
                    """

                    mc.blendShape(bsTrgt, e=True, ib=True, t=(mshTrgt, int(id), shpCore, val))
                mc.namespace(set=':')
                mc.parent(trgtInBet, storageGrp)

#addInbet_v2(mc.ls(sl=True)[0], 'TRGT')

def removeTrgt(getSel, *args, **kwargs):
    lTrgt = getSel()
    for trgt in lTrgt:
        if mc.attributeQuery('mixDriver', n=trgt, ex=True):
            if mc.getAttr(trgt+'.mixDriver') == True:
                mc.warning('this trgt is driving a mix, you can t remove it until he s deconnected from the mix')
                return
        trgtDatas = getTrgtMshDatas(trgt)
        bs = trgtDatas[trgt]['bs']
        alias = trgtDatas[trgt]['alias']
        wght = trgtDatas[trgt]['weight']
        id = trgtDatas[trgt]['id']


        aniCrv = mc.listConnections(bs+'.'+alias, s=True, scn=True)[0]
        ctrlChan = mc.listConnections(aniCrv, s=True, scn=True, type='transform', plugs=True)[0]
        rangeChan = mc.attributeQuery(ctrlChan.split('.')[-1], n=ctrlChan.split('.')[0], r=True)
        if 0.0 in rangeChan:
            if mc.objExists(aniCrv):
                mc.delete(aniCrv)
            if mc.attributeQuery(ctrlChan.split('.')[-1], n=ctrlChan.split('.')[0], ex=True):
                mc.deleteAttr(ctrlChan)
        else:
            val = mc.getAttr(aniCrv+'.keyTimeValue[1].keyTime')
            if val == 0:
                mc.addAttr(ctrlChan, e=True, min=0.0)
                if mc.objExists(aniCrv):
                    mc.delete(aniCrv)
            elif val > 0:
                mc.addAttr(ctrlChan, e=True, max=0.0)
                if mc.objExists(aniCrv):
                    mc.delete(aniCrv)
        mshRes = mc.blendShape(bs, q=True, g=True)[0]
        mc.blendShape(bs, e=True, rm=True, t=(mshRes, id, trgt, wght))
        mc.delete(trgt)
        print trgt, 'removed from ', ctrlChan

def removeInbet(getSel, *args, **kwargs):
    lInBetTrgt = []
    if isinstance(getSel, list):
        lInBetTrgt = getSel
    else:
        lInBetTrgt = getSel()
    for inBetTrgt in lInBetTrgt:
        if mc.attributeQuery('isInBet', n=inBetTrgt, ex=True):
            if mc.getAttr(inBetTrgt+'.isInBet') == True:
                trgtDatas = getTrgtMshDatas(inBetTrgt)
                id = trgtDatas[inBetTrgt]['id']
                bs = trgtDatas[inBetTrgt]['bs']
                wght = trgtDatas[inBetTrgt]['weight']
                mshRes = mc.blendShape(bs, q=True, g=True)[0]
                mc.blendShape(bs, e=True, rm=True, t=(mshRes, id, inBetTrgt, wght))
                mc.delete(inBetTrgt)
                print inBetTrgt, 'succesfuly removed from ', trgtDatas[inBetTrgt]['alias'], 'at value :', wght
            else:
                mc.warning(inBetTrgt, 'is not an inBetween')
        else:
            mc.warning(inBetTrgt, 'is not an inBetween')
def removeCor(getSel, *args, **kwargs):
    lTrgt = getSel()
    for trgt in lTrgt:
        cor = mc.listConnections(trgt+'.result', d=True, s=False) or []
        if cor:
            if mc.attributeQuery('mixDriver', n=cor[0], ex=True):
                if mc.getAttr(cor[0]+'.mixDriver') == True:
                    mc.warning('this trgt is driving a mix, you can t remove it until he s deconnected from the mix')
                    return

            trgtDatas = getTrgtMshDatas(cor[0])
            bs = trgtDatas[cor[0]]['bs']
            alias = trgtDatas[cor[0]]['alias']
            wght = trgtDatas[cor[0]]['weight']
            id = trgtDatas[cor[0]]['id']


            aniCrv = mc.listConnections(bs+'.'+alias, s=True, scn=True)[0]
            if mc.objExists(aniCrv):
                mc.delete(aniCrv)
            mshRes = mc.blendShape(bs, q=True, g=True)[0]
            mc.blendShape(bs, e=True, rm=True, t=(mshRes, id, cor[0], wght))
            mc.delete(cor[0])
        mc.delete(trgt)
        print trgt, 'removed'



def removeCorInbet(getSel, *args, **kwargs):
    lInBetTrgt = []
    if isinstance(getSel, list):
        lInBetTrgt = getSel
    else:
        lInBetTrgt = getSel()
    for inBetTrgt in lInBetTrgt:
        cor = mc.listConnections(inBetTrgt + '.result', d=True, s=False) or []
        if cor:
            if mc.attributeQuery('isInBet', n=cor[0], ex=True):
                if mc.getAttr(cor[0]+'.isInBet') == True:
                    trgtDatas = getTrgtMshDatas(cor[0])
                    id = trgtDatas[cor[0]]['id']
                    bs = trgtDatas[cor[0]]['bs']
                    wght = trgtDatas[cor[0]]['weight']
                    mshRes = mc.blendShape(bs, q=True, g=True)[0]
                    mc.blendShape(bs, e=True, rm=True, t=(mshRes, id, cor[0], wght))
                    mc.delete(cor[0])
                    mc.delete(inBetTrgt)
                    print inBetTrgt, 'succesfuly removed from ', trgtDatas[cor[0]]['alias'], 'at value :', wght
                else:
                    mc.warning(inBetTrgt, 'is not an inBetween')
            else:
                mc.warning(inBetTrgt, 'is not an inBetween')
#GEN SKIN MESH###############################################################################################################################################################################
def genSkinMsh(lNeutral):
    tplPath = r'T:/03_FAB/00_ASSETS/STP/BNK/facialTpl/wip/MAYA/SMF_STP_LibFacial_tpl_v001_003.ma'
    scenePath = mc.file(q=True, sceneName=True)

    #list les refs dans la scene
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        if not tplPath in lRef:
            print 'loading face template'
            mc.file(tplPath, reference=True, type='mayaAscii', namespace='TPL')
    else:
        print 'loading face template'
        mc.file(tplPath, reference=True, type='mayaAscii', namespace='TPL')
    #genNspace('RIG')
    mc.namespace(set=':')

def convertToTemplate(getSel, *args, **kwargs):
    lNodes = getSel()
    for node in lNodes:
        if not node.startswith('tpl_'):
            mc.warning(node, 'need to start with  "tpl_"')
            return
    cg = lib_controlGroup.getAllCg()[0]
    lib_controlGroup.addTplsToCg(lNodes, cg)
    for node in lNodes:
        if mc.attributeQuery('isMirrored', n=node, ex=True):
            mc.setAttr(node+'.isMirrored', cb=True)

def buildTpl(*args, **kwargs):
    cg = lib_controlGroup.getAllCg()[0]
    lib_controlGroup.buildTplCg(cg)

def import_face_template(*args, **kwargs):
    path = r'T:\03_FAB\00_ASSETS\STP\BNK\facialTpl\wip\MAYA'
    lFiles = glob.glob(path+'\*.ma')
    lastRev = max(lFiles, key=os.path.getmtime)
    mc.file(lastRev, i=True)

#CORRECTIVES SHAPES (chara in pose)#GEN TARGETS###############################################################################################################################################


def genCorSculpt(getSel, inBetVal='', trgtWght='', *args, **kwargs):
    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()

    lCtrl = []
    dicCtrlPos = {}
    lObj = mc.ls('*.nodeType', r=True)
    for obj in lObj:
        if mc.getAttr(obj) == 'control':
            lCtrl.append(obj.split('.')[0])
        if lCtrl:
            for ctrl in lCtrl:
                if mc.attributeQuery('bindPoseAttrs', n=ctrl, ex=True):
                    end = mc.getAttr(ctrl+'.bindPoseAttrs', s=True)
                    for id in range(0, end):
                        attr = mc.getAttr(ctrl+'.bindPoseAttrs['+str(id)+']')
                        if not mc.getAttr(ctrl+'.'+attr) == mc.getAttr(ctrl+'.bindPoseValues['+str(id)+']'):
                            if not ctrl in dicCtrlPos.keys():
                                        dicCtrlPos[ctrl] = {}
                            dicCtrlPos[ctrl][attr] = mc.getAttr(ctrl+'.'+attr)
                else:
                    lAttrs = mc.listAttr(ctrl, k=True)
                    for attr in lAttrs:
                        if not '.' in attr:
                            if not mc.attributeQuery(attr, n=ctrl, ch=True):
                                if not ctrl in dicCtrlPos.keys():
                                    dicCtrlPos[ctrl] = {}
                                val = mc.getAttr(ctrl+'.'+attr)
                                dicCtrlPos[ctrl][attr] = val

    if len(dicCtrlPos.keys()) > 1:
        print dicCtrlPos.keys()
        mc.warning('you can add correctives targets only on ONE CONTROLER at a time (one corrective for one controler channel), line 3049')
        return
    elif len(dicCtrlPos[dicCtrlPos.keys()[0]]) > 1:
        print dicCtrlPos[dicCtrlPos.keys()[0]]
        mc.warning('you can add correctives targets only on ONE CHANNEL at a time (one corrective for one controler channel), suce')
        return
    lCorSculpt = []
    for mshResult in lMshResult:
        storageGrp = geStorageGrp('COR', mshResult)
        #return
        bsCor = getBsDef(mshResult, 1)
        if not bsCor:
            corResult = genResult(mshResult, 'COR')
            mc.setAttr(corResult+'.v', False)
            bsCor = mc.blendShape(corResult, n='bsCor'+mshResult[len(mshResult.split('_')[0]):])[0]
            bsTypeAttrr(bsCor, 1)

        corResult = mc.blendShape(bsCor, q=True, g=True)[0]
        #dicTrgt = getActivTrgt(bsCor)
        clearName = mshResult
        #nspace = bsCor[:len(bsCor)-len(bsCor.split(':')[-1])]
        #mc.namespace(set=':'+nspace)
        nCtrl = ''
        for key in dicCtrlPos.keys():
            base = key.replace(key.split('_')[0], '')
            nCtrl += base[1 :]
            for chan in dicCtrlPos[key].keys():
                nCtrl += chan[0].upper()+chan[1:]

        if ':' in mshResult:
            clearName = mshResult.split(':')[-1]

        clearName = clearName[len(clearName.split('_')[0]):]
        dupName = nCtrl+'Sculpt'+inBetVal
        nspace = crtNspace(mshResult, 'COR')
        dupMsh = nspace+':'+dupName
        if trgtWght:
            dupMsh = nspace + ':' + trgtWght

        if not mc.objExists(dupMsh):
            dupMsh = mc.duplicate(mshResult, n=dupName)[0]
            mc.parent(dupMsh, storageGrp)
            if not mc.attributeQuery('shpSource', n=dupMsh, ex=True):
                mc.addAttr(dupMsh, ln='shpSource', at='message')
            mc.connectAttr(corResult+'.message', dupMsh+'.shpSource', f=True)
            if not mc.attributeQuery('notes', n=dupMsh, ex=True):
                mc.addAttr(dupMsh, ln='notes', dt='string')
        #mc.addAttr(dupMsh, ln='trgtActived', dt='string', multi=True)
        #mc.addAttr(dupMsh, ln='trgtValues', at='double', multi=True)
            mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string')
            mc.setAttr(dupMsh+'.notes',  lock=True)

        elif mc.objExists(dupMsh):
            #get notes value: {u'c_jawDn1': {u'rx': u'20.0'}}
            dicChkCtrl = getDicCtrlPose(dupMsh)
            chkCtrl = dicChkCtrl.keys()[0]
            chkAttr = dicChkCtrl[chkCtrl].keys()[0]
            chkVal = dicChkCtrl[chkCtrl][chkAttr]
            val = dicCtrlPos[chkCtrl][chkAttr]
            #print 'HEERE :', val, ' ->',  chkVal
            # if notes value and cor value are opposite (positive and negative) create opposite cor
            if val < 0.0 and chkVal > 0.0 or  val > 0.0 and chkVal < 0.0:
                dupName = nCtrl + 'OppSculpt' + inBetVal
                nspace = crtNspace(mshResult, 'COR')
                dupMsh = nspace + ':' + dupName
                if trgtWght:
                    dupMsh = nspace + ':' + trgtWght+inBetVal
                dupMsh = mc.duplicate(mshResult, n=dupName)[0]
                mc.parent(dupMsh, storageGrp)
                if not mc.attributeQuery('shpSource', n=dupMsh, ex=True):
                    mc.addAttr(dupMsh, ln='shpSource', at='message')
                mc.connectAttr(corResult + '.message', dupMsh + '.shpSource', f=True)
                if not mc.attributeQuery('notes', n=dupMsh, ex=True):
                    mc.addAttr(dupMsh, ln='notes', dt='string')
                # mc.addAttr(dupMsh, ln='trgtActived', dt='string', multi=True)
                # mc.addAttr(dupMsh, ln='trgtValues', at='double', multi=True)
                mc.setAttr(dupMsh + '.notes', dicCtrlPos, type='string')
                mc.setAttr(dupMsh + '.notes', lock=True)

            else:
                mc.setAttr(dupMsh+'.notes',  lock=False)
                mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string')
                mc.setAttr(dupMsh+'.notes',  lock=True)
                snapShp([mshResult, dupMsh])
        lCorSculpt.append(dupMsh)

        #id = 0
        #for trgt in dicTrgt.keys():
            #mc.setAttr(dupMsh+'.trgtActived['+str(id)+']', trgt, type='string')
            #mc.setAttr(dupMsh+'.trgtValues['+str(id)+']', dicTrgt[trgt])
            #id += 1

        for attr in ['translate', 'rotate', 'scale']:
            for i in ['X', 'Y', 'Z']:
                mc.setAttr(dupMsh+'.'+attr+i, l=False)

    mc.namespace(set=':')
    return lCorSculpt
#gencorrSculpt(mc.ls(sl=True))



def getDicCtrlPose(msh):
    dicCtrl = {}
    val = mc.getAttr(msh+'.notes')[2:-1]
    lKeys = val.split('}')
    for dic in lKeys:
        ctrl = dic.split(': {')[0].replace(", u'", "").replace("'", '').replace(' ', '')
        if ctrl:
            if ctrl != '\n':
                if not ctrl in dicCtrl.keys():
                    dicCtrl[ctrl] = {}
                lAttrs = dic.split(': {')[-1]
                for data in lAttrs.split(','):
                    attr = data.split(':')[0][2:].replace("'", '')
                    value = data.split(':')[-1][1:]
                    if attr:
                        if not attr in dicCtrl[ctrl].keys():
                            dicCtrl[ctrl][attr] = value
    return dicCtrl
#getDicCtrlPose('TRGT:HEAD:cor_head__jawRxRyRz__jawDn2TzTxTySculpt.notes')



def connectCorrective(getSel, *args, **kwargs):
    lCor = []
    if isinstance(getSel, list):
        lCor = getSel
    else:
        lCor = getSel()
    lShpCorResult = []
    for cor in lCor:
        print 'connecting ', cor
        if not mc.attributeQuery('result', n=cor, ex=True):
            mc.addAttr(cor, ln='result', at='message')
        lShpCor = mc.listConnections(cor+'.result', d=True) or []
        mshSrc = mc.listConnections(cor+'.shpSource', s=True)[0]
        #toto = mc.listHistory(mshSrc, ac=True, af=True)
        #lHist = mc.listHistory(mshSrc, ac=True, af=True)
        #kin = mc.ls(lHist, type='skinCluster') or []
        lDeformers = mc.findDeformers('result_head')
        skin = mc.ls(lDeformers, type='skinCluster') or []

        #print 'HERE :', skin
        mshSkin = mc.listRelatives(mc.skinCluster(skin[0], q=True, g=True)[0], p=True)[0]

        dicCtrl = getDicCtrlPose(cor)
        for msh in [mshSrc, mshSkin]:
            lDef = mc.findDeformers(msh) or []
            for node in lDef:
                if mc.nodeType(node) == 'blendShape':
                    mc.setAttr(node+'.envelope', 0)

        lCtrl = mc.ls('*.nodeType', o=True, r=True)
        for ctrl in lCtrl:
            if mc.getAttr(ctrl+'.nodeType') == 'control':
                for attr in ['translate', 'rotate', 'scale']:
                    val = 0
                    if attr == 'scale':
                        val = 1
                    for axe in ['X', 'Y', 'Z']:
                        mc.setAttr(ctrl+'.'+attr+axe, val)

        for ctrl in dicCtrl.keys():
            for attr in dicCtrl[ctrl].keys():
                val = float(dicCtrl[ctrl][attr])
                mc.setAttr(ctrl+'.'+attr, val)

        difCor = mc.invertShape(mshSkin, cor)

        for msh in [mshSrc, mshSkin]:
            lDef = mc.findDeformers(msh) or []
            for node in lDef:
                if mc.nodeType(node) == 'blendShape':
                    mc.setAttr(node+'.envelope', 1)

        nShpCor = cor.replace('Sculpt', '')
        shpCore = nShpCor
        lShpCorResult.append(shpCore)
        bs = getBsDef(mshSrc, None)[0]
        if lShpCor:
            if nShpCor in lShpCor:
                snapShp([difCor, nShpCor])
                mc.delete(difCor)
                if mc.attributeQuery('isInBet', n=cor, ex=True):
                    if mc.getAttr(cor+'.isInBet') == True:
                        return
                dKey = mc.listConnections(bs+'.'+shpCore.split(':')[-1], s=True, scn=True) or []
                if dKey:
                    mc.delete(dKey[0])
        else:
            nspace = cor[:len(cor)-len(cor.split(':')[-1])]
            activeDef(mshSkin, 0)
            shpCore = mc.duplicate(mshSkin, n=nShpCor)[0]
            mc.setAttr(shpCore+'.v', False)
            unlockChans(shpCore)
            mc.parent(shpCore, cor)
            activeDef(mshSkin, 1)

            #TMP for get attrs notes and trgt#########
            if not mc.attributeQuery('shpSource', n=shpCore, ex=True):
                mc.addAttr(shpCore, ln='shpSource', at='message')
            mc.connectAttr(cor+'.result', shpCore+'.shpSource')
            #######################################################
            #bs = getBsTrgt(1)[0]
            #bs = getBsDef(mshSrc, None)[0]
            lTrgt = mc.blendShape(bs, q=True, t=True) or []
            msh = mc.blendShape(bs, q=True, g=True)[0]
            snapShp([difCor, shpCore])
            mc.delete(difCor)
            if not shpCore.split(':')[-1] in lTrgt:
                if mc.attributeQuery('isInBet', n=cor, ex=True):
                    if mc.getAttr(cor+'.isInBet') == True:
                        return lShpCorResult[0]
                else:
                    #id = len(lTrgt)
                    id = getLastInputId(bs) + 1
                    mc.blendShape(bs, edit=True, t=(msh, id, shpCore, 1.0))

        for ctrl in dicCtrl.keys():
            for attr in dicCtrl[ctrl].keys():
                val = float(dicCtrl[ctrl][attr])
                mc.setDrivenKeyframe(bs+'.'+shpCore.split(':')[-1], cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=0, v=0)
                mc.setDrivenKeyframe(bs+'.'+shpCore.split(':')[-1], cd=ctrl+'.'+attr, itt='linear', ott='linear', dv=val, v=1)
                dKey = mc.listConnections(bs+'.'+shpCore.split(':')[-1], s=True, scn=True)[0]
                if dKey:
                    if val > 0 :
                        mc.setAttr(dKey+'.postInfinity', 4)
                    elif val < 0 :
                        mc.setAttr(dKey+'.preInfinity', 4)





def genFlipCor(getSel, side, *args, **kwargs):
    lSculptCor = []
    if isinstance(getSel, list):
        lSculptCor = getSel
    else:
        lSculptCor = getSel()
    for sculptCor in lSculptCor:
        print 'generating', sculptCor, ' mirror'
        mshSrc = mc.listConnections(sculptCor+'.shpSource', s=True)[0]
        sculptRes = mc.listConnections(sculptCor+'.result', d=True, s=False)[0]
        mshMiror = ''
        mSide = 'R'
        if mSide == side:
            mSide = 'L'
        if mc.attributeQuery('mshMirror', n=sculptCor, ex=True) and mc.listConnections(sculptCor+'.mshMirror', s=True):
            mshMiror = mc.listConnections(sculptCor+'.mshMirror', s=True)[0]
        else:
            if not mc.attributeQuery('mshMirror', n=sculptCor, ex=True):
                mc.addAttr(sculptCor, ln='mshMirror', at='message')
                sculptCor = mc.rename(sculptCor, sculptCor+'_'+side)
                sculotResSided = mc.rename(sculptRes, sculptRes+'_'+side)
                lHist = mc.listHistory(sculotResSided, f=True)
                bs = mc.ls(lHist, type='blendShape')[0]
                dicTrgtData = getTrgtAliasIndex(sculotResSided)
                alias = dicTrgtData[sculotResSided]['alias']
                wghtId = 'weight['+dicTrgtData[sculotResSided]['index']+']'
                mc.aliasAttr(alias+'_'+side, bs+'.'+wghtId)
                #print 'alias :', alias, 'renamed to :', alias+'_'+side
            mshMiror = mc.duplicate(sculptCor, n=sculptCor.replace('_'+side, '_'+mSide), rc=True)[0]
            mc.connectAttr(mshMiror+'.message', sculptCor+'.mshMirror')
            mc.connectAttr(sculptCor+'.message', mshMiror+'.mshMirror')
            dicCtrlPos = getDicCtrlPose(sculptCor)
            for ctrl in dicCtrlPos.keys():
                for attr in dicCtrlPos[ctrl].keys():
                    if attr in ['tx', 'ry', 'rz']:
                        dicCtrlPos[ctrl][attr] = float(dicCtrlPos[ctrl][attr])*-1
            mc.connectAttr(mshSrc+'.message', mshMiror+'.shpSource')
            mc.setAttr(mshMiror+'.notes', lock=False)
            mc.setAttr(mshMiror+'.notes', dicCtrlPos, type='string')
            mc.setAttr(mshMiror+'.notes', lock=True)
            toDel = mc.listRelatives(mshMiror, c=True, type='transform')
            mc.delete(toDel)

        posSculptCor = mc.xform(sculptCor, q=True, ws=True, t=True)
        posMshMiror = mc.xform(mshMiror, q=True, ws=True, t=True)
        if not mc.attributeQuery('symTabLeft', n=mshSrc, ex=True):
            crtSymAttr([mshSrc])
        for id in range(0, mc.getAttr(mshSrc+'.symTabLeft', s=True)):
            vtxL = mc.getAttr(mshSrc+'.symTabLeft['+str(id)+']')
            vtxR = mc.getAttr(mshSrc+'.symTabRight['+str(id)+']')
            posVtxL = mc.xform(sculptCor+'.vtx['+str(vtxL)+']', q=True, ws=True, t=True)
            posVtxR = mc.xform(sculptCor+'.vtx['+str(vtxR)+']', q=True, ws=True, t=True)
            difL = [posMshMiror[0]+(posVtxL[0]-posSculptCor[0])*-1, posMshMiror[1]+(posVtxL[1]-posSculptCor[1]), posMshMiror[2]+(posVtxL[2]-posSculptCor[2])]
            difR = [posMshMiror[0]+(posVtxR[0]-posSculptCor[0])*-1, posMshMiror[1]+(posVtxR[1]-posSculptCor[1]), posMshMiror[2]+(posVtxR[2]-posSculptCor[2])]

            mc.move(difL[0], difL[1], difL[2], mshMiror+'.vtx['+str(vtxR)+']')
            mc.move(difR[0], difR[1], difR[2], mshMiror+'.vtx['+str(vtxL)+']')

        for id in range(0, mc.getAttr(mshSrc+'.symTabMid', s=True)):
            vtxM = mc.getAttr(mshSrc+'.symTabMid['+str(id)+']')
            posVtxM = mc.xform(sculptCor+'.vtx['+str(vtxM)+']', q=True, ws=True, t=True)
            difM = [posMshMiror[0]+(posVtxM[0]-posSculptCor[0])*-1, posMshMiror[1]+(posVtxM[1]-posSculptCor[1]), posMshMiror[2]+(posVtxM[2]-posSculptCor[2])]

            mc.move(difM[0], difM[1], difM[2], mshMiror+'.vtx['+str(vtxM)+']')
        connectCorrective([mshMiror])
        print sculptCor, 'mirror generated'


#genFlipCor(mc.ls(sl=True), "L")



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
            elif sign == 'positive':
                mc.setAttr(trgt+'.negativeChan', 0)
#presetTplFaceChan(trgt, trgtToCtrlChan())

def setTplFaceChan(lTrgt, val):
    for trgt in lTrgt:
        if not mc.attributeQuery('ctrlChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='ctrlChan', dt='string')
        if not mc.attributeQuery('negativeChan', n=trgt, ex=True):
            mc.addAttr(trgt, ln='negativeChan', dt='string')
        mc.setAttr(trgt+'.ctrlChan', val)
        mc.setAttr(trgt+'.negativeChan')


def setChannel(chan, *args, **kwargs):
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
        if  mc.getAttr(trgt+'.negativeChan') == True:
            sign = '-'

        newVal = sign+chan[0]+chan[-1]
        if chan == 'None':
            newVal = '//'
        mc.setAttr(trgt+'.ctrlChan', chan, type='string')
        mc.textScrollList('targetsChan', e=True, rii=id)
        mc.textScrollList('targetsChan', e=True, ap=[id, newVal])


def invertSign(*args, **kwargs):
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
    faceDatas = faceDescription()
    lSep = mc.ls('*.sepZone', r=True, o=True)
    dicSep = {}
    for sep in lSep:
        #print sep
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
    for key in faceDatas.lZones:
        mc.setAttr(dicSep[key]+'.translateY', poseY)
        baseY = poseY
        poseY = baseY + sizeY + space

#dispatchSep()

def buildSep(getSel, lFaceZone, lSepType, *args, **kwargs):
    #buildSep(, )listSel, ["None"], [mc.optionMenu("sepType", q=True, v=True)])
    faceDatas = faceDescription()
    lNeutral = []
    if isinstance(getSel, list):
        lNeutral = getSel
    else:
        lNeutral = getSel()
    #sep types####################
    #mc.menuItem( label='Left')  #
    #mc.menuItem( label='Rigt')  #
    #mc.menuItem( label='Middle')#
    #mc.menuItem( label='Up')    #
    #mc.menuItem( label='Down')  #
    #mc.menuItem( label='Ext')   #
    #mc.menuItem( label='Int')   #
    #mc.menuItem( label='Corner')#
    ##############################
    #list les enum pour creer l attribut
    dicTrgt = faceDatas.trgtNames()
    dicSlices = faceDatas.sepSlices()
    if lSepType == ['getType']:
        lSepType = getSepType("sepType")
    genNspace('SEP')
    for neutral in lNeutral:

        nspace = mc.namespaceInfo(cur=True)+':'
        name = getObjNameFromNspace(neutral)
        baseName = name[len(name.split('_')[0])+1:]

        clearName = baseName
        if not mc.attributeQuery('slices', n=neutral, ex=True):
            mc.addAttr(neutral, ln='slices', at='message', multi=True)
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
        if not mc.objExists(nspace + ':' + sepGrp):
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
                    if not mc.attributeQuery('sepOrig', n=dupSep, ex=True):
                        mc.addAttr(dupSep, ln='sepOrig', at='message')
                    mc.connectAttr(dupSep+'.sepOrig', neutral+'.slices['+str(mc.getAttr(neutral+'.slices', s=True))+']')
                    if not mc.attributeQuery('extractMe', n=dupSep, ex=True):
                        mc.addAttr(dupSep, ln='extractMe', at='bool', dv=True)
                    mc.setAttr(dupSep+'.extractMe', True)

                    if mc.attributeQuery('extractMe', n=neutral, ex=True):
                        mc.setAttr(neutral+'.extractMe', False)
                    #else:
                        #mc.addAttr(neutral, ln='extractMe', at='bool', dv=False)
                    for attr in ['translate', 'rotate', 'scale']:
                        for axe in ['X', 'Y', 'Z']:
                            mc.setAttr(dupSep+'.'+attr+axe, l=False)

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
                        mc.parent(dupSep, nspace + ':' + sepGrp)
                    except:
                        pass
                    nBs = 'bs_'+baseName+faceZone+sepType
                    bs = nspace + ':' + nBs
                    if not mc.objExists(nBs):
                        bs = mc.blendShape(neutral, dupSep, n=nBs)[0]
                    mc.setAttr(bs+'.'+name, 1)
        lib_deformers.activeDef(neutral, True)
    mc.namespace(set=':')
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
    dicZoneTrgt = getZonedTrgt(bs)
    aliasDatas = getDicBsTrgtDatasAsAlias(bs)
    dicZonedSep = getSepMsh()
    dicNeutral = {}

    mc.setAttr(bs+'.envelope', 0)
    vtxs = mc.polyEvaluate(neutral, v=True)
    posMsh = mc.xform(neutral, q=True, ws=True, t=True)

    for i in range(0, vtxs):
        posVtxW = mc.xform(neutral+'.vtx['+str(i)+']', q=True, ws=True, t=True)
        dicNeutral[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]
    for key in dicZoneTrgt.keys():
        lVtxWeighted = []

        for alias in dicZoneTrgt[key]:
            trgt = aliasDatas[alias]['sculpt'][1.0]['trgt']
            posTrgt = mc.xform(trgt, q=True, ws=True, t=True)
            for i in range(0, vtxs):
                posVtxW = mc.xform(trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
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


def getSepZone():
    # TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mixTrgt     #
    # 3 = Result      #
    # 4 = Shapes      #
    # 5 = mixShp      #
    # _________________#
    dicSepZoned = {}
    lBsRes = getBsDef(None, 3)
    for bsRes in lBsRes:
        mshRes = mc.blendShape(bsRes, q=True, g=True)[0]
        father = mc.listRelatives(mshRes, p=True)[0]
        bsTrgt = getBsDef(father, 0) or []

        if bsTrgt:
            print bsRes, mshRes, father, bsTrgt
            if not father in dicSepZoned.keys():
                dicSepZoned[father] = {}
            lCon = mc.listConnections(mshRes, scn=True, d=True)
            lBs = mc.ls(lCon, type='blendShape')
            for bs in lBs:
                if bs in lCon:
                    sep = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
                    zone = mc.getAttr(sep+'.sepZone', asString=True)
                    if not zone in dicSepZoned[father].keys():
                        dicSepZoned[father][zone] = []
                    dicSepZoned[father][zone].append(sep)
    return dicSepZoned
#getSepZone()

def getSepZoneMsh():
    dicSepZoned = {}
    lBsRes = getBsDef(None, 3)
    for bsRes in lBsRes:
        mshRes = mc.blendShape(bsRes, q=True, g=True)[0]
        father = mc.listRelatives(mshRes, p=True)[0]
        bsTrgt = getBsDef(father, 0) or []
        if bsTrgt:
            #print mshRes, bsTrgt
            if not mshRes in dicSepZoned.keys():
                dicSepZoned[mshRes] = {}
            lBs = mc.ls(mc.listHistory(mshRes, f=True), type='blendShape')
            lCon = mc.listConnections(mshRes, scn=True)
            #print 'lBs :', lBs
            for bs in lBs:
                if bs in lCon:
                    sep = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
                    zone = mc.getAttr(sep+'.sepZone', asString=True)
                    if not zone in dicSepZoned[mshRes].keys():
                        dicSepZoned[mshRes][zone] = []
                    dicSepZoned[mshRes][zone].append(sep)
    return dicSepZoned
#getSepZoneMsh()

def connectSep():
    print 'to do'


def majSepBaseWght(*args, **kwargs):
    dicZonedSep = getSepZoneMsh()
    for mshRes in dicZonedSep.keys():
        print mshRes
        print dicZonedSep[mshRes]
        if dicZonedSep[mshRes]:
            father = mc.listRelatives(mshRes, p=True)[0]
            nspaceBs = 'TRGT:'+father[len(father.split('_')[0])+1:].upper()+':'
            bsRes = getBsDef(father, 3)
            bsTrgt = getBsDef(father, 0)[0]

            dicZoneTrgt = getZonedTrgt(bsTrgt)

            activeDef(mshRes, False)
            dicResVtx = {}
            vtxs = mc.polyEvaluate(mshRes, v=True)

            posMsh = mc.xform(father, q=True, ws=True, t=True)
            for i in range(0, vtxs):
                posVtxW = mc.xform(mshRes+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                dicResVtx[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]

            for key in dicZoneTrgt.keys():
                lVtxWeighted = []
                for trgt in dicZoneTrgt[key]:
                    trgtMsh = nspaceBs+trgt
                    posTrgt = mc.xform(trgtMsh, q=True, ws=True, t=True)
                    for i in range(0, vtxs):
                        posVtxW = mc.xform(nspaceBs+trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                        posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]
                        for vec in [0, 1, 2]:
                            gap = compareFloats(dicResVtx[i][vec], posVtxL[vec], 0.0001)
                            if gap == False:
                                if not i in lVtxWeighted:
                                    lVtxWeighted.append(i)

                if key in dicZonedSep[mshRes].keys():
                    for sep in dicZonedSep[mshRes][key]:
                        print 'updating weights for :', sep
                        if sep:
                            dicSLices = getSlices(sep)
                            lSlices = []
                            for src in dicSLices.keys():
                                for slice in dicSLices[src]:
                                    lSlices.append(slice)
                            lWght = []
                            sepShp = mc.listRelatives(sep, s=True, ni=True)[0]
                            bsSepZone = mc.ls(mc.findDeformers(sepShp), type='blendShape')[0]
                            lOldVtx = []
                            lSlicesVtx = []
                            if mc.attributeQuery('weightedVtx', n=sep, ex=True):
                                lIds = mc.getAttr(sep + '.weightedVtx', mi=True)
                                for id in lIds:
                                    lOldVtx.append(mc.getAttr(sep + '.weightedVtx[' + str(id) + ']'))
                                mc.deleteAttr(sep+'.weightedVtx')
                            mc.addAttr(sep, ln='weightedVtx', dt='string', multi=True)
                            for vtx in range(0, vtxs+1):
                                val = 0.0
                                if vtx in lVtxWeighted:
                                    if not vtx in lOldVtx:
                                        lSlicesVtx.append(vtx)
                                    id = mc.getAttr(sep+'.weightedVtx', s=True)
                                    mc.setAttr(sep+'.weightedVtx['+str(id)+']', str(vtx), type='string')
                                    val = 1.0
                                lWght.append(val)
                                vtx += 1
                            mc.setAttr(bsSepZone+'.inputTarget[0].baseWeights[0:'+str(vtxs)+']', *lWght)
                            updateSlicesWght(dicSLices, lSlicesVtx, vtxs)
        activeDef(mshRes, True)
    print 'weights updated'
#majSepBaseWght()

def updateSlicesWght(dicSLices, lSlicesVtx, vtxs):
    for sep in dicSLices.keys():
        lSlices = dicSLices[sep]
        lBs = []
        for slice in lSlices:
            lBs.append(mc.ls(mc.findDeformers(slice), type='blendShape')[0])
        for vtx in lSlicesVtx:
            chkWgth = 0.0
            for bs  in lBs:
                chkWgth += mc.getAttr(bs+ '.inputTarget[0].baseWeights[' + str(vtx) + ']')
            if chkWgth == 0.0:
                for bs in lBs:
                    mc.setAttr(bs + '.inputTarget[0].baseWeights[' + str(vtx) + ']', 1.0)


def getSlices(sepZone):
    dicZoneSlices = {}
    dicSlices = {}
    sliced = len(mc.ls(mc.listHistory(sepZone, f=True), type='blendShape'))
    lSlices = [sepZone]
    lParsed = []
    iter = 0
    i = 1
    if sliced == 2:
        sliced += 1
    while iter < sliced:
        if lSlices != lParsed:
            lParsed = lSlices
            dicZoneSlices[i] = lSlices
            i += 1
            iter += len(lParsed)
        else:
            lSlices = []
            for parsed in lParsed:
                chkSlice = mc.listConnections(parsed+'.slices', s=True) or []
                if chkSlice:
                    lSlices.extend(chkSlice)
            iter += 1
    hiSLices = dicZoneSlices.keys()
    hiSLices.sort()
    for zone in dicZoneSlices.keys():
        for slice in dicZoneSlices[zone]:
            if  slice != sepZone:
                father = mc.listConnections(slice+'.sepOrig') or []
                if father:
                    if not father[0] in dicSlices.keys():
                        dicSlices[father[0]] = []
                    dicSlices[father[0]].append(slice)
    return dicSlices
    #print dicZoneSlices
#getSlices(mc.ls(sl=True)[0])


def majSlicesBaseWght():
    dicZonedSep = getSepZoneMsh()
    for mshRes in dicZonedSep.keys():
        if dicZonedSep[mshRes]:
            father = mc.listRelatives(mshRes, p=True)[0]
            nspaceBs = 'TRGT:'+father[len(father.split('_')[0])+1:].upper()+':'
            bsRes = getBsDef(father, 3)
            bsTrgt = getBsDef(father, 0)[0]

            dicZoneTrgt = getZonedTrgt(bsTrgt)

            activeDef(mshRes, False)
            dicResVtx = {}
            vtxs = mc.polyEvaluate(mshRes, v=True)

            posMsh = mc.xform(father, q=True, ws=True, t=True)
            for i in range(0, vtxs):
                posVtxW = mc.xform(mshRes+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                dicResVtx[i] = [posVtxW[0]-posMsh[0], posVtxW[1]-posMsh[1], posVtxW[2]-posMsh[2]]

            for key in dicZoneTrgt.keys():
                lVtxWeighted = []
                for trgt in dicZoneTrgt[key]:
                    trgtMsh = nspaceBs+trgt
                    posTrgt = mc.xform(trgtMsh, q=True, ws=True, t=True)
                    for i in range(0, vtxs):
                        posVtxW = mc.xform(nspaceBs+trgt+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                        posVtxL = [posVtxW[0]-posTrgt[0], posVtxW[1]-posTrgt[1], posVtxW[2]-posTrgt[2]]
                        for vec in [0, 1, 2]:
                            gap = compareFloats(dicResVtx[i][vec], posVtxL[vec], 0.0001)
                            if gap == False:
                                if not i in lVtxWeighted:
                                    lVtxWeighted.append(i)

                if key in dicZonedSep[mshRes].keys():
                    for sep in dicZonedSep[mshRes][key]:
                        print 'updating weights for :', sep
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
        activeDef(mshRes, True)
    print 'weights updated'

def lZonedVtx(mshZone):
    lZonedVtx = []
    rng = mc.getAttr(mshZone+'.weightedVtx', mi=True) or []
    if rng:
        for id in rng:
            lZonedVtx.append(mc.getAttr(mshZone+'.weightedVtx['+str(id)+']'))
    return lZonedVtx
#lZonedVtx(mc.ls(sl=True)[0])

def removeUnweightedVtx():
    zone = 'SEP:sep_head_eyelids'
    dicSlices = getSlices(zone)
    lWghtVtx = lZonedVtx(zone)
    lVtx = mc.polyEvaluate(zone, v=True)
    dicVtx = {}
    for slice in dicSlices[zone]:
        shp = mc.listRelatives(slice, s=True, ni=True)[0]
        bsS = mc.ls(mc.findDeformers(shp), type='blendShape')[0]
        if mc.attributeQuery('weightedVtx', n=slice, ex=True):
            mc.deleteAttr(sep+'.weightedVtx')
        mc.addAttr(sep, ln='weightedVtx', dt='string', multi=True)

        lWght = []


        for vtx in range(0, vtxs+1):
            val = 0.0
            if vtx in lVtxWeighted:
                id = mc.getAttr(sep+'.weightedVtx', s=True)
                mc.setAttr(sep+'.weightedVtx['+str(id)+']', str(vtx), type='string')
                val = 1.0
            lWght.append(val)
            vtx += 1
        mc.setAttr(bsSepZone+'.inputTarget[0].baseWeights[0:'+str(vtxs)+']', *lWght)





def genSepZones(getSel, *args, **kwargs):
    lNeutral = getSel()
    neutral = lNeutral[0]
    if neutral:
        """
        if not mc.getAttr(neutral+'.resultMsh') == 'TRGT':
            baseName = neutral
            if ':' in neutral:
                baseName = neutral.split(':')[-1]
            neutral = 'TRGT:'+baseName

        """
        bs = getBsDef(neutral, 0)[0]
        nspaceBs = bs[:len(bs)-len(bs.split(':')[-1])]
        dicZoneTrgt = getZonedTrgt(bs)
        for zone in dicZoneTrgt.keys():
            if len(dicZoneTrgt[zone]) > 0:
                buildSep([neutral], [zone], ['None'])
        autoWeightSepZones(neutral)
        mc.setAttr(mc.listRelatives(neutral, p=True)[0]+'.v', False)
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

def crtSymAttr(getSel, *args, **kwargs):
    lObj = ''
    if isinstance(getSel, list):
        lObj = getSel
    else:
        lObj = getSel()

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

def chkSym(getSel, *args, **kwargs):
    lMsh = ''
    if isinstance(getSel, list):
        lMsh = getSel
    else:
        lMsh = getSel()
    for msh in lMsh:
        if not mc.attributeQuery('symTab', n=msh, ex=True):
            return mc.warning(msh, 'doesn t have sym tabulation')
    lAsymetric = []
    for msh in lMsh:
        posMsh = mc.xform(msh, ws=True, q=True, t=True)
        for id in range(0, mc.getAttr(msh + '.symTabLeft', s=True)):
            vtxL = mc.getAttr(msh + '.symTabLeft[' + str(id) + ']')
            vtxR = mc.getAttr(msh + '.symTabRight[' + str(id) + ']')
            valVtxL = mc.xform(msh+'.vtx['+str(vtxL)+']', ws=True, q=True, t=True)
            valVtxR = mc.xform(msh + '.vtx[' + str(vtxR) + ']', ws=True, q=True, t=True)
            valL = [posMsh[0]-valVtxL[0], posMsh[1]-valVtxL[1], posMsh[2]-valVtxL[2]]
            valR = [posMsh[0] - valVtxR[0], posMsh[1] - valVtxR[1], posMsh[2] - valVtxR[2]]
            if not valR == [valL[0]*-1, valL[1], valL[2]]:
                for asym in [msh+'.vtx['+str(vtxL)+']', msh+'.vtx['+str(vtxR)+']']:
                    lAsymetric.append(asym)
        for id in range(0, mc.getAttr(msh + '.symTabMid', s=True)):
            vtxMid = mc.getAttr(msh+'.symTabMid[' + str(id) + ']')
            valVtxMid = mc.xform(msh+'.vtx[' + str(vtxMid) + ']', ws=True, q=True, t=True)
            if not posMsh[0] - valVtxMid[0] == 0:
                lAsymetric.append(msh+'.vtx['+str(vtxMid)+']')
        if lAsymetric:
            mc.select(cl=True)
            mc.select(lAsymetric)
            mc.sets(n=msh+'Assym')
    print 'sym checkd on ', lMsh,

def copySymTabTo(getSel, *args, **kwargs):
    lMsh = ''
    if isinstance(getSel, list):
        lMsh = getSel
    else:
        lMsh = getSel()
    if lMsh:
        mshSrc = lMsh[0]
        lDest = lMsh[1 :]
        if not mc.attributeQuery('symTab', n=mshSrc, ex=True):
            return mc.warning('no sym tabulation found on the source', mshSrc)
        else:
            dicSym = {}
            dicSym['mid'] = []
            dicSym['sided'] = {}
            for id in range(0, mc.getAttr(mshSrc+'.symTabLeft', s=True)):
                vtxL = mc.getAttr(mshSrc+'.symTabLeft['+str(id)+']')
                vtxR = mc.getAttr(mshSrc+'.symTabRight['+str(id)+']')
                dicSym['sided'][vtxL] = vtxR
            for id in range(0, mc.getAttr(mshSrc+'.symTabMid', s=True)):
                dicSym['mid'].append(mc.getAttr(mshSrc+'.symTabMid['+str(id)+']'))
        for mshDest in lDest:
            if not mc.attributeQuery('symTab', n=mshDest, ex=True):
                mc.addAttr(mshDest, ln='symTab', at='bool', dv=1, k=False)
                mc.addAttr(mshDest, ln='symTabLeft', at='long', multi=True)
                mc.addAttr(mshDest, ln='symTabRight', at='long', multi=True)
                mc.addAttr(mshDest, ln='symTabMid', at='long', multi=True)
            inc = 0
            for key in dicSym['sided'].keys():
                vtxL = int(key)
                vtxR = int(dicSym['sided'][key])
                mc.setAttr(mshDest + '.symTabLeft[' + str(inc) + ']', vtxL)
                mc.setAttr(mshDest + '.symTabRight[' + str(inc) + ']', vtxR)
                inc += 1
            inc = 0
            for vtx in dicSym['mid']:
                vtxMid = int(vtx)
                mc.setAttr(mshDest + '.symTabMid[' + str(inc) + ']', vtxMid)
                inc += 1



def invertBsWghtTo(lObj, *args, **kwargs):
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

def invertBsWghtTo_v2(getSel, *args, **kwargs):
    lSep = getSel()
    dicSeps = {}
    mshDest = lSep[-1]
    bsDest = mc.ls(mc.findDeformers(mshDest), type='blendShape')[0]
    lSep.remove(mshDest)
    ratio = len(lSep)
    for vtx in range(0, mc.polyEvaluate(lSep[0], v=True)):
        wght = 0.0
        for sep in lSep:
            bs = mc.ls(mc.findDeformers(sep), type='blendShape')[0]
            wght += mc.getAttr(bs+'.inputTarget[0].baseWeights['+str(vtx)+']')
        wghtRes = 1-(wght/ratio)
        mc.setAttr(bsDest+'.inputTarget[0].baseWeights['+str(vtx)+']', wghtRes)

#invertBsWghtTo_v2i(mc.ls(sl=True))


def copyBsWghtTo(getSel, *args, **kwargs):
    lObj = getSel()
    objSrc = lObj[0]
    objTrgt = lObj[1]
    bsSrc = getBsDef(objSrc, None)[0]
    bsTrgt = getBsDef(objTrgt, None)[0]
    iVtx = mc.polyEvaluate(objSrc, v=True)
    val = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
    mc.setAttr(bsTrgt+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *val)
#copyBsWghtTo(mc.ls(sl=True))

def flipBsWght(getSel, *args, **kwargs):
    lObj = getSel()
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


def mirrorBsWght(getSel, side, *args, **kwargs):
    lObj = getSel()
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

def genDifWght(getSel, *args, **kwargs):
    lMsh = getSel()
    lMshSrc = lMsh[:-1]
    mshDest = lMsh[-1]
    lToNorm = []
    bsDest = getBsDef(mshDest, None)[0]
    iVtx = mc.polyEvaluate(mshDest, v=True)
    lVal = [0.0 for i in range(iVtx+1)]
    lNormVal = []
    for msh in lMshSrc:
        bsSrc = getBsDef(msh, None)[0]
        lWght = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
        i = 0
        for i in range(0, len(lWght)):
            lVal[i]+=lWght[i]
            if lVal[i] > 1:
                lVal[i] =1
            elif lVal[i] < 1:
                lToNorm.append(i)
            else:
                lVal[i] = lVal[i]

    i = 0
    for i in range(0, len(lVal)):
        lVal[i] = 1-lVal[i]
    mc.setAttr(bsDest+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *lVal)
    if lToNorm:
        mc.warning('some weight need to be normalized :'+ str(lToNorm))
#genDifWght(mc.ls(sl=True))

def addBsWghtTo(getSel):
    lObj = getSel()
    objSrc = lObj[0]
    objTrgt = lObj[1]
    bsSrc = getBsDef(objSrc, None)[0]
    bsTrgt = getBsDef(objTrgt, None)[0]
    iVtx = mc.polyEvaluate(objSrc, v=True)
    val = mc.getAttr(bsSrc+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']')
    if val != 0.0:
        mc.setAttr(bsTrgt+'.inputTarget[0].baseWeights[0:'+str(iVtx)+']', *val)

def crtSepChecker(getSel, *args, **kwargs):
    lMsh = getSel()
    #print lMsh, 'toto'
    lCheckers = []
    lSep = []
    lBs = []
    for msh in lMsh:
        if mc.attributeQuery('sepChecker', n=msh, ex=True):
            #print msh
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
        removeCustomAttrs([checker])

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
                sepAttr = sep
                if ':' in sep:
                    sepAttr = sep.split(':')[-1]
                mc.setAttr(bs[0]+'.'+sepAttr, 1)
#crtSepChecker(mc.ls(sl=True))

def normalizeSelSep(getSel, *args, **kwargs):
    lSep = getSel()
    dicSeps = {}
    for vtx in range(0, mc.polyEvaluate(lSep[0], v=True)):
        wght = 0.0
        if not vtx in dicSeps.keys():
            dicSeps[vtx] = {}
        dicSeps[vtx]['sep'] = {}
        for sep in lSep:
            if not sep in dicSeps[vtx]['sep'].keys():
                dicSeps[vtx]['sep'][sep] = {}
            bs = mc.ls(mc.findDeformers(sep), type='blendShape')[0]
            dicSeps[vtx]['sep'][sep]['bs'] = bs
            dicSeps[vtx]['sep'][sep]['wght'] = mc.getAttr(bs+'.inputTarget[0].baseWeights['+str(vtx)+']')
            wght += dicSeps[vtx]['sep'][sep]['wght']
        if wght > 0.0:
            for sep in dicSeps[vtx]['sep'].keys():
                normVal = setRange(0.0, wght, 0.0, 1.0, dicSeps[vtx]['sep'][sep]['wght'])
                mc.setAttr(dicSeps[vtx]['sep'][sep]['bs']+'.inputTarget[0].baseWeights['+str(vtx)+']', normVal)








def connectNeutralWrap(getSel, *args, **kwargs):
    lMsh = getSel()
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
                removeCustomAttrs([dupAdd])

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
        shpAdd= mc.listRelatives(dupAdd, s=True, ni=True)[-1]
        lWrp = mc.ls(mc.findDeformers(shpAdd), type='wrap') or []
        if lWrp:
            for wrp in lWrp:
                wrpIds = mc.getAttr(wrp+'.basePoints', mi=True) or []
                if wrpIds:
                    for wrpId in wrpIds:
                        baseBuff = mc.listConnections(wrp+'.basePoints['+str(wrpId)+']', s=True) or []
                        if baseBuff:
                            removeCustomAttrs(baseBuff)
        #id = 0
        #lIds = mc.getAttr(buffTrgt+'.bases', mi=True) or []
        #if lIds:
            #id = lIds[-1]+1
        #mc.connectAttr(baseBuff+'.message', buffTrgt+'.bases['+str(id)+']')
#connectNeutralWrap(mc.ls(sl=True))

def wrapOn(getSel, *args, **kwargs):
    lMsh = getSel()
    trgt = lMsh[-1]
    lAdds = lMsh[: -1]

    buffTrgt = ''
    activeDef(mc.listRelatives(trgt, s=True)[0], 0)
    if mc.attributeQuery('hasBuff', n=trgt, ex=True):
        buffTrgt = mc.listConnections(trgt+'.hasBuff', s=True)[0]
    else:
        mc.addAttr(trgt, ln='hasBuff', at='message')
        buffTrgt = mc.duplicate(trgt, n=trgt+'_buff')[0]
        removeCustomAttrs([buffTrgt])
        unlockChans(buffTrgt)

        mc.connectAttr(buffTrgt+'.message', trgt+'.hasBuff', f=True)
        mc.addAttr(buffTrgt, ln='checkers', at='message', multi=True)
        mc.addAttr(buffTrgt, ln='bases', at='message', multi=True)
        shpTrgt = mc.listRelatives(trgt, s=True, ni=True)[-1]
        shpBuff = mc.listRelatives(buffTrgt, s=True, ni=True)[-1]
        mc.connectAttr(shpTrgt+'.worldMesh[0]', shpBuff+'.inMesh', f=True)
        mc.setAttr(shpBuff+'.v', False)
        buffFather = trgt+'BUFFERS'
        if not mc.objExists(buffFather):
            buffFather = mc.createNode('transform', n=buffFather)
            mc.addAttr(buffFather, ln='deleteMe', at='bool', dv=True)
        mc.parent(buffTrgt, buffFather)

    pos = mc.getAttr(buffTrgt+'.translate')[0]
    ort = mc.getAttr(buffTrgt+'.rotate')[0]

    nBuff = trgt[len(trgt.split(':')[-1].split('_')[0])+1 :]
    for add in lAdds:
        nDupAdd = add+'_'+nBuff+'Wrapped'
        dupAdd = nDupAdd
        if not mc.objExists(dupAdd):
            dupAdd = mc.duplicate(add, n=nDupAdd)[0]
            if mc.attributeQuery('sepZone', n=dupAdd, ex=True):
                mc.deleteAttr(dupAdd, at='sepZone')

            mc.setAttr(dupAdd+'.translate', *pos)
            mc.setAttr(dupAdd+'.rotate', *ort)
            id = mc.getAttr(buffTrgt+'.checkers', s=True)
            mc.connectAttr(dupAdd+'.message', buffTrgt+'.checkers['+str(id)+']')
            if not mc.attributeQuery('neutral', n=dupAdd, ex=True):
                mc.addAttr(dupAdd, ln='neutral', at='message')
                mc.connectAttr(add+'.message', dupAdd+'.neutral')

            lChilds = mc.listRelatives(buffTrgt, c=True, type='transform') or []
            if lChilds:
                mc.parent(lChilds, world=True)
            mc.select(cl=True)
            mc.select(dupAdd)
            mc.select(buffTrgt, add=True)
            mc.CreateWrap()
            if lChilds:
                for child in lChilds:
                    mc.parent(child, buffTrgt)

            mc.parent(dupAdd, buffTrgt)
            wrp = mc.ls(mc.listHistory(dupAdd), type='wrap')[0]
            baseBuff = mc.listConnections(wrp+'.basePoints[0]', s=True)[0]
            removeCustomAttrs([baseBuff])
            id = 0
            lIds = mc.getAttr(buffTrgt+'.bases', mi=True) or []
            if lIds:
                id = lIds[-1]+1
            mc.connectAttr(baseBuff+'.message', buffTrgt+'.bases['+str(id)+']')
            mc.parent(baseBuff, buffTrgt)
        mc.setAttr(add+'.v', False)
        activeDef(mc.listRelatives(trgt, s=True)[0], 1)
#wrapOn(mc.ls(sl=True))

def removeWraps(getSel, *args, **kwargs):
    lMsh = getSel()
    for msh in lMsh:
        if mc.attributeQuery('hasBuff', n=msh, ex=True):
            buff = mc.listConnections(msh+'.hasBuff', s=True)[0]
            lIds = mc.getAttr(buff+'.bases', mi=True)
            for id in lIds:
                base = mc.listConnections(buff+'.bases['+str(id)+']', s=True) or []
                if base:
                    if mc.objExists(base[0]):
                        mc.delete(base)
            mc.delete(buff)
            mc.deleteAttr(msh+'.hasBuff')
            print msh, 'was cleaned from his wrap buffers'
        else:
            print msh, 'have no wrap buffer'



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

def genTplName(comp, type, *args, **kwargs):
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






def genTplName_v2(comp, type):
    obj = comp.split('.')[0]
    zone = mc.getAttr(obj+'.sepZone', asString=True)
    side = ''
    slices = obj.split(zone.capitalize())[-1].replace('_','')
    lSlices = re.findall('[A-Z][^A-Z]*', slices)
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

#genTplName('SEP:sep_headEyelidsLeftUp_Middle.vtx[61]', 'tpl')


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
    if not mc.objExists(nCrvPath):
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
    if not mc.objExists('PATHS'):
        mc.createNode('transform', n='PATHS')
    mc.parent(crvPath, 'PATHS')
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
    try:
        mc.parent(node, ca)
    except:
        pass
    # delete nearestPointOnCurve
    mc.delete(npoc)
    # return
    return ca
#curveAttach('crv_hairs_R', mc.ls(sl=True))

def genTpl(getSel, *args, **kwargs):
    lComp = getSel()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
    if not mc.objExists('TPL'):
            mc.createNode('transform', n='TPL')
    if not mc.objExists('PATH'):
            mc.createNode('transform', n='PATH')
    for comp in lComp:
        obj = comp.split('.')[0]
        crvPath = crtCrvPath(comp)[0]
        pos = mc.xform(comp, q=True, ws=True, t=True)
        if len(pos) > 3:
            mc.warning('select only one vertex please')
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
        nTpl = genTplName_v2(comp, 'tpl')
        loc = mc.spaceLocator(n=nTpl)[0]
        mc.setAttr(loc+'.translateX', pos[0])
        mc.setAttr(loc+'.translateY', pos[1])
        mc.setAttr(loc+'.translateZ', pos[2])

        mc.setAttr(loc+'.t', *pos)
        mc.setAttr(loc+'.localScaleX', .25)
        mc.setAttr(loc+'.localScaleY', .25)
        mc.setAttr(loc+'.localScaleZ', .25)
        mc.addAttr(loc, ln='vtxId', dt='string')
        mc.setAttr(loc+'.vtxId', comp.split('[')[-1][:-1], type='string')
        #dicTrgt = trgtNames()

        enAttr = ''
        for key in dicTrgt.keys():
            enAttr = enAttr+key+':'
        if not mc.attributeQuery('tplZone', n=loc, ex=True):
            mc.addAttr(loc, ln='tplZone', at='enum', en=enAttr)
        mc.connectAttr(obj+'.sepZone', loc+'.tplZone')

        ca = curveAttach(crvPath, loc)
        mc.parent(ca, 'TPL')
#genTpl(mc.ls(sl=True))



def updateTpl(getSel, *args, **kwargs):
    lSel = []
    if isinstance(getSel, list):
        lSel = getSel
    else:
        lSel = getSel()
    tpl = ''
    comp = ''
    if not len(lSel) == 2:
        mc.warning('you must select a locator and a vertex on the corresponding slice')
        return
    for sel in lSel:
        if mc.objectType(sel) == 'transform':
            tpl = sel
        elif mc.objectType(sel) == 'mesh':
            comp = sel
    if tpl and comp:
        ca = mc.listRelatives(tpl, p=True)[0]
        msh = comp.split('.')[0]
        pETOC = mc.ls(mc.listHistory(ca), type='polyEdgeToCurve')[0]
        crvPath = mc.listConnections(pETOC+'.outputcurve', d=True)[0]
        lEdgId = mc.polyInfo(comp, vertexToEdge=True)[0].split(':')[-1]
        edgId = ''
        for i in lEdgId.split(' '):
            if i != '':
                edgId = i
                break
        mc.select(cl=True)
        mc.select(msh+'.e['+str(edgId)+']')
        mel.eval("SelectEdgeLoopSp")
        mel.eval("ConvertSelectionToVertices")
        lVtx = mc.ls(sl=True, fl=True)
        lIds = []
        for vtx in lVtx:
            lIds.append(vtx.split('.')[-1])
        mc.setAttr(pETOC+'.inputComponents', len(lIds), *lIds, type='componentList')

        pos = mc.xform(comp, q=True, ws=True, t=True)
        nbrVtx = len(pos)/3
        i, addX, addY, addZ = 0, 0, 0, 0
        for i in range(0, nbrVtx):
            addX += pos[i]
            addY += pos[i+1]
            addZ += pos[i+2]
            i += 3
        pos = [addX/nbrVtx, addY/nbrVtx, addZ/nbrVtx]

        mc.select(cl=True)
        mc.setAttr(tpl+'.translateX', pos[0])
        mc.setAttr(tpl+'.translateY', pos[1])
        mc.setAttr(tpl+'.translateZ', pos[2])

        mc.setAttr(tpl+'.t', *pos)
        mc.setAttr(tpl+'.vtxId', comp.split('[')[-1][:-1], type='string')
        curveAttach(crvPath, tpl)
        mc.setAttr(tpl+'.t', 0.0,0.0,0.0)




def connTplToNeutral(*args, **kwargs):
    lNodes = mc.ls(type='polyEdgeToCurve')
    bsNeutral = getBsTrgt(0)[0]
    neutralShp =mc.blendShape(bsNeutral, q=True,  g=True)
    neutral = mc.listRelatives(neutralShp, p=True)[0]
    for node in lNodes:
        mc.connectAttr(neutral+'.outMesh', node+'.inputPolymesh', f=True)
        mc.connectAttr(neutral+'.outSmoothMesh', node+'.inputSmoothPolymesh', f=True)
        mc.connectAttr(neutral+'.worldMatrix[0]', node+'.inputMat', f=True)
        mc.connectAttr(neutral+'.displaySmoothMesh', node+'.displaySmoothMesh', f=True)
        mc.connectAttr(neutral+'.smoothLevel', node+'.smoothLevel', f=True)
    return neutral

#switchTplToNeutral()
"""
def extractTpl(father):
    dicTpl = {}
    lTpl = mc.ls('*.tplZone', r=True, o=True) or []
    for tpl in lTpl:
        extTpl = mc.duplicate(tpl)[0]

        try:
            mc.parent(extTpl, father)
        except:
            pass
        val = mc.getAttr(tpl+'.tplZone')
        mc.setAttr(extTpl+'.tplZone', val)
        mc.rename(extTpl, extTpl[:-1])
        if mc.attributQuery('zoneParentDriver', n=tpl, ex=True):
            if not dicTpl[tpl] in dicTpl.keys:
                dicTpl[tpl] = extTpl
    for keu in dicTpl.keys():
        oldDriver = mc.listConnections(tpl+'.zoneParentDriver')
        print 'zoneParentDriver, zoneParentDriverChans'
"""
def extractTpl(father):
    mshResult = connTplToNeutral()
    activeDef(mshResult, False)
    lToKeep = []
    lTpl = mc.ls('*.tplZone', r=True, o=True) or []
    for tpl in lTpl:
        lToKeep.append(tpl)
        try:
            mc.parent(tpl, father)
        except:
            try:
                mc.parent(tpl, world=True)
            except:
                pass
    activeDef(mshResult, True)
    return lToKeep





def getSepMsh():
    #dicTrgt = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
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
        #print sep
        if mc.attributeQuery('sepZone', n=sep, ex=True):
            zone = mc.getAttr(sep+'.sepZone', asString=True)
            #print 'HERE', sep, zone
            dicZonedSep[zone].append(sep)
    return dicZonedSep
#getSepMsh()


def getSepMsh_v2():
    dicZonedSep = {}
    lSep = mc.ls('*.sepZone', r=True, o=True)
    toExtract = []
    for sep in lSep:
        lBs = []
        lHist = mc.listHistory(sep, f=True, lv=1) or []
        if lHist:
            lBs = mc.ls(lHist, type='blendShape') or []
        if not lBs:
            toExtract.append(sep)
    for sep in toExtract:
        if mc.attributeQuery('sepZone', n=sep, ex=True):
            zone = mc.getAttr(sep+'.sepZone', asString=True)
            if not zone in dicZonedSep.keys():

                dicZonedSep[zone] = []
            dicZonedSep[zone].append(sep)
    return dicZonedSep
#getSepMsh_v2()


def getSepExtractor(bs):
    dicZonedSep = {}
    resMsh = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
    lHist = mc.listHistory(resMsh, f=True)
    #print lHist
    chkPETOC = mc.ls(lHist, type='polyEdgeToCurve') or []
    if chkPETOC:
        lHist = mc.listHistory(resMsh, ac=True)
    lMsh = mc.ls(lHist, type='mesh')
    toExtract = []
    for msh in lMsh:
        sep = mc.listRelatives(msh,p=True)[0]
        if not sep in toExtract:
            if mc.attributeQuery('extractMe', n=sep, ex=True):
                if mc.getAttr(sep+'.extractMe') == True:
                    toExtract.append(sep)
    for sep in toExtract:
        if mc.attributeQuery('sepZone', n=sep, ex=True):
            zone = mc.getAttr(sep+'.sepZone', asString=True)
            if not zone in dicZonedSep.keys():
                dicZonedSep[zone] = []
            dicZonedSep[zone].append(sep)
    return dicZonedSep
#getSepExtractor('bsTrgtr_head')


def getZonedTrgt(bs):
    lTrgt = []
    #dicTrgt = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
    lWght = mc.aliasAttr(bs, q=True)
    for wght in lWght:
        if not wght.startswith('weight['):
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

def extractAdds(sep, extShp, normalize, id):
    if mc.attributeQuery('adds', n=sep, ex=True):
        lAdds = mc.listConnections(sep+'.adds', s=True) or []
        if lAdds:
            lExtAdds = []

            if not mc.attributeQuery('shpAdds', n=extShp, ex=True):
                mc.addAttr(sep, ln='shpAdds', at='message', multi=True)
            print 'extarcting add on :', sep
            for add in lAdds:
                if mc.attributeQuery('extractMe', n=add, ex=True):
                    if mc.getAttr(add+'.extractMe') == True:
                        base = add.split('_')[0]
                        base = base.replace('wrp', '')
                        side = ''
                        if base.endswith('rt'):
                            base = base[: -2]
                            side = '_R'
                        elif base.endswith('lt'):
                            base = base[: -2]
                            side = '_L'
                        #father = 'SHAPES'+'_'+base+side
                        #if not mc.objExists(father):
                            #father = mc.createNode('transform', n='SHAPES'+'_'+base+side)
                        nAdd = extShp+base
                        if mc.objExists(nAdd):
                            mc.delete(nAdd)


                        extAdd = mc.duplicate(add, n=nAdd)[0]
                        neutral = mc.listConnections(add+'.neutral', s=True)[0]
                        if mc.attributeQuery('neutral', n=extAdd, ex=True):
                            mc.deleteAttr(extAdd+'.neutral')
                        #mc.addAttr(extAdd, ln='neutral', dt='string')
                        #mc.setAttr(extAdd+'.neutral', neutral, type='string')
                        linkMshSrc([neutral, extAdd])


                        #mc.parent(extAdd, father)
                        idAdd = mc.getAttr(extShp+'.adds', s=True)
                        mc.connectAttr(extAdd+'.message', extShp+'.adds['+str(idAdd)+']')
                        mc.addAttr(extAdd, ln='weightId', dt='string')
                        mc.setAttr(extAdd+'.weightId', id, type='string')
                        mc.addAttr(extAdd, ln='extractedFrom', dt='string')
                        mc.setAttr(extAdd+'.extractedFrom', add, type='string')
                        lExtAdds.append(extAdd)

                        if normalize:
                            lDef = mc.listHistory(add)
                            lWrp = mc.ls(lDef, type='wrap') or []
                            if lWrp:
                                wrp = lWrp[0]
                                mc.setAttr(wrp+'.envelope', 0)
                                neutAdd = mc.duplicate(add, n=add+'SUCE')[0]
                                mc.setAttr(wrp+'.envelope', 1)
                                addNormRatioAttr(neutAdd, [extAdd], 1.0)
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
    #dicZone = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
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
                            #add shpType attr
                            mc.addAttr(extShp, ln='shpResultType', dt='string')
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


def addNormRatioAttr(neutralGeo, lTrgt, roof):
    smab = len(lTrgt)
    posSrc = mc.xform(neutralGeo, q=True, ws=True, t=True)
    vtxs = mc.polyEvaluate(neutralGeo, v=True)
    for trgt in lTrgt:
        roof = 0.0
        moveMax = 0.0
        vtxRoofId = ''
        dicTrgtGeoVtxDif = {}
        dicTrgtGeoVtx = {}
        postrgtGeo = mc.xform(trgt, q=True, ws=True, t=True)

        if not mc.attributeQuery('vtxRoof', n=trgt, ex=True):
            mc.addAttr(trgt, ln='vtxRoof', at='float', )
        if not mc.attributeQuery('vtxRoofId', n=trgt, ex=True):
            mc.addAttr(trgt, ln='vtxRoofId', dt='string')
        if not mc.attributeQuery('ratio', n=trgt, ex=True):
            mc.addAttr(trgt, ln='ratio', at='float')

        for vtx in range(0, vtxs):
            #get position of vtx for trgt
            posVtxtrgtGeo = mc.xform(trgt+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
            posVtx = mc.xform(neutralGeo+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)


            #remove transform pos from vtx pos trgt (set to world 0, 0, 0)
            posVtxInneutralGeo = [posVtxtrgtGeo[0]-postrgtGeo[0], posVtxtrgtGeo[1]-postrgtGeo[1], posVtxtrgtGeo[2]-postrgtGeo[2]]
            #get dif betweeen sourc and trgtGeo vtx
            dif = math.sqrt(((posVtxInneutralGeo[0]-posVtx[0])**2)+((posVtxInneutralGeo[1]-posVtx[1])**2)+((posVtxInneutralGeo[2]-posVtx[2])**2))
            #get roof
            if dif != 0.0:
                if abs(dif) > roof:
                    roof = dif
                    vtxRoofId = trgt+'.vtx['+str(vtx)+']'
            dicTrgtGeoVtx[vtx] = posVtxInneutralGeo
            dicTrgtGeoVtxDif[vtx] = dif
        ratio = 1.0/roof
        if roof < 1.0:
            ratio = roof/1.0
        mc.setAttr(trgt+'.ratio', ratio)
        mc.setAttr(trgt+'.vtxRoof', roof)
        mc.setAttr(trgt+'.vtxRoofId', vtxRoofId, type='string')
        smab -= 1

#addNormRatioAttr('MOD:msh_head', mc.ls(sl=True), 1.0)

#dk = 1/ (( (0.842 + 0.418) /2)  *10)


def extractShapes_v2():
    if not mc.objExists('SHAPES'):
        mc.createNode('transform', n='SHAPES')
    if not mc.objExists('FACE_TPL'):
        mc.createNode('transform', n='FACE_TPL')
    bs = getBsDef(None, 0)[0]
    neutralGeo = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]
    #dicZone = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
    dicZoneTrgt = getZonedTrgt(bs)
    dicZonedSep = getSepMsh_v2()
    resultTypeMesh = mc.blendShape(bs, q=True, g=True)[0]
    nspace = lib_namespace.getNspaceFromObj(resultTypeMesh)
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
                            #add shpType attr
                            mc.addAttr(extShp, ln='shpResultType', dt='string')
                            moveMax = 0.0
                            if normalise == True:
                                addNormRatioAttr(neutralGeo, [extShp], 1.0)
                            mc.addAttr(extShp, ln='ctrlChan', dt='string')
                            mc.setAttr(extShp+'.ctrlChan', chan, type='string')
                            mc.addAttr(extShp, ln='negativeChan', at='bool')
                            mc.setAttr(extShp+'.negativeChan', sign)
                            mc.addAttr(extShp, ln='maxMove', at='double')
                            mc.setAttr(extShp+'.maxMove', moveMax)
                            mc.parent(extShp, 'SHAPES')

                            extAdds = extractAdds(sep, extShp, normalise) or []
                            for add in extAdds:
                                mc.addAttr(add, ln='ctrlChan', dt='string')
                                mc.setAttr(add+'.ctrlChan', chan, type='string')
                                mc.addAttr(add, ln='negativeChan', at='bool')
                                mc.setAttr(add+'.negativeChan', sign)
                                mc.addAttr(add, ln='maxMove', at='double')
                                mc.setAttr(add+'.maxMove', moveMax)
                    mc.setAttr(bs+'.'+trgt, 0)

#extractShapes_v2()


def extractShapes_trgt(lMshResults, *args, **kwargs):
    faceDatas = faceDescription()
    dicZone = faceDatas.trgtNames()
    lExpShp = []
    lExpShpAdds = []
    #if not mc.objExists('SHAPES_TRGT'):
        #mc.createNode('transform', n='SHAPES_TRGT')
    if not lMshResults:
        lMshResults = [None]
    #lCtrl = mc.ls('*.nodeType', o=True, r=True)
    #for ctrl in lCtrl:
        #if mc.getAttr(ctrl+'.nodeType') == 'control':
            #for attr in ['translate', 'rotate', 'scale']:
                #val = 0
                #if attr == 'scale':
                    #val = 1
                #for axe in ['X', 'Y', 'Z']:
                    #mc.setAttr(ctrl+'.'+attr+axe, val)

    lib_checkers.vtxColor(lMshResults, None)
    for mshRes in lMshResults:
        #print 'HERE:', mshRes
        bsTrgt = getBsDef(mshRes, 0)[0]
        bsRes = getBsDef(mshRes, 3)[0]
        dataBsRes = getDicBsTrgtDatasAsMsh(bsRes)
        mshTrgt = mc.listRelatives(mc.blendShape(bsTrgt, q=True, g=True)[0], p=True)[0]
        if not dataBsRes == None:
            for wght in dataBsRes.keys():
                alias = dataBsRes[wght]['data']['alias']
                if wght == mshTrgt:
                     mc.setAttr(bsRes+'.'+alias, True)
                else:
                    mc.setAttr(bsRes+'.'+alias, False)
            #{u'COR:result_headCOR': {'data': {'alias': u'result_headCOR', 'index': u'1'}}
            lHist = mc.listHistory(mshRes, ac=True)
            skin = mc.ls(lHist, type='skinCluster')or []
            if skin:
                mc.setAttr(skin[0]+'.envelope', 0)
                geoRes = mc.skinCluster(skin[0], q=True, g=True)[0]

            aliasData = getDicBsTrgtDatasAsAlias(bsTrgt)
            #neutralGeo = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]

            #dicZone = trgtNames()
            dicZoneTrgt = getZonedTrgt(bsTrgt)
            dicZonedSep = getSepExtractor(bsTrgt)
            resultTypeMesh = mc.blendShape(bsTrgt, q=True, g=True)[0]
            nspace = lib_namespace.getNspaceFromObj(resultTypeMesh)
            lMovedVtx = []
            dicNeutGeoVtx = {}

            roof = 0.0
            #get neutralGeo transform position
            posSrc = mc.xform(mshRes, q=True, ws=True, t=True)
            vtxs = mc.polyEvaluate(mshRes, v=True)

            for key in dicZoneTrgt.keys():
                for trgt in dicZoneTrgt[key]:
                    mc.setAttr(bsTrgt+'.'+trgt, 0)

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
                    print dicZoneTrgt[key], dicZonedSep
                    if key in dicZonedSep.keys():
                        for id in range(0, mc.getAttr(dicZonedSep[key][0]+'.weightedVtx', s=True)):
                            vtx = mc.getAttr(dicZonedSep[key][0]+'.weightedVtx['+str(id)+']')
                            lVtxs.append(vtx)
                            posVtx = mc.xform(mshRes+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
                            dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]
                        for trgt in dicZoneTrgt[key]:
                            ############################################
                            extraCount -= 1
                            print 'trgt :', trgt, extraCount, 'more'
                            ############################################
                            trgtSculpt = aliasData[trgt]['sculpt'][1.0]['trgt']
                            if mc.attributeQuery('ctrlChan', n=trgtSculpt, ex=True):
                                chan = mc.getAttr(trgtSculpt+'.ctrlChan')
                                normalise = False
                                if chan.startswith('translate'):
                                    normalise = True
                                sign = mc.getAttr(trgtSculpt+'.negativeChan')
                                mc.setAttr(bsTrgt+'.'+trgt, 1)
                                nTrgt = trgt[len(trgt.split('_')[0]):]
                                clearNTrgt = nTrgt
                                if '_' in trgt:
                                    smab = nTrgt.split('_')
                                    clearNTrgt = smab[1]
                                    for i in range(2, len(smab)):
                                        suce = smab[i].capitalize()
                                        clearNTrgt += suce
                                dicShp = {}
                                for sep in dicZonedSep[key]:
                                    lWrp = mc.ls(mc.listHistory(sep, f=True), type='wrap') or []
                                    if lWrp:
                                        for wrp in [lWrp[0]]:
                                            wrpIds = mc.getAttr(wrp+'.basePoints', mi=True) or []
                                            if wrpIds:
                                                for wrpId in wrpIds:
                                                    wrpBaseMsh = mc.listConnections(wrp+'.basePoints['+str(wrpId)+']', s=True)or []
                                                    if wrpBaseMsh:
                                                        mc.delete(mc.parentConstraint(wrpBaseMsh[0], sep, mo=False))
                                    lib_checkers.vtxColor([sep], None)
                                    if mc.polyCompare(mshRes, sep, fd=True, v=False) in [0, 8, 16, 24]:
                                        pole = ''
                                        #print 'goodMesh'

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

                                        dicShp[zone+'_'+clearNTrgt+pole+side+'6000'] = []
                                        for wght in aliasData[trgt]['sculpt'].keys():
                                            id = aliasData[trgt]['sculpt'][wght]['id']

                                            nExShp = zone+'_'+clearNTrgt+pole+side+id
                                            #print nExShp
                                            mc.setAttr(bsTrgt+'.'+trgt, wght)

                                            if mc.objExists(nExShp):
                                                mc.delete(nExShp)
                                                #print nExShp, 'DELETED'

                                            extShp = mc.duplicate(sep, n=nExShp)[0]
                                            #print nExShp, 'GENERATED'
                                            lExpShp.append(extShp)
                                            if mc.attributeQuery('extractMe', n=extShp, ex=True):
                                                mc.deleteAttr(extShp+'.extractMe')
                                            #add shpType attr
                                            mc.addAttr(extShp, ln='shpResultType', dt='string')
                                            moveMax = 0.0
                                            if normalise == True and id == '6000':
                                                addNormRatioAttr(mshRes, [extShp], 1.0)

                                            mc.addAttr(extShp, ln='ctrlChan', dt='string')
                                            mc.setAttr(extShp+'.ctrlChan', chan, type='string')
                                            mc.addAttr(extShp, ln='negativeChan', at='bool')
                                            mc.setAttr(extShp+'.negativeChan', sign)
                                            mc.addAttr(extShp, ln='maxMove', at='double')
                                            mc.setAttr(extShp+'.maxMove', moveMax)
                                            mc.addAttr(extShp, ln='weightId', dt='string')
                                            mc.setAttr(extShp+'.weightId', id, type='string')
                                            if id != '6000':
                                                dicShp[zone+'_'+clearNTrgt+pole+side+'6000'].append(extShp)
                                            #mc.parent(extShp, 'SHAPES_TRGT')
                                            linkMshSrc([mshRes,extShp])
                                            extAdds = extractAdds(sep, extShp, normalise, id) or []
                                            if extAdds:
                                                lExpShp.extend(extAdds)
                                            trgtAdd = ''
                                            for add in extAdds:
                                                if mc.getAttr(add+'.weightId') == '6000':
                                                    trgtAdd = add
                                                    mc.addAttr(trgtAdd, ln='inBets', at='message', multi=True)
                                            for add in extAdds:
                                                mc.addAttr(add, ln='ctrlChan', dt='string')
                                                mc.setAttr(add+'.ctrlChan', chan, type='string')
                                                mc.addAttr(add, ln='negativeChan', at='bool')
                                                mc.setAttr(add+'.negativeChan', sign)
                                                mc.addAttr(add, ln='maxMove', at='double')
                                                mc.setAttr(add+'.maxMove', moveMax)
                                                if mc.getAttr(add+'.weightId') != '6000':
                                                    mc.addAttr(add, ln='isInBet', at='bool', dv=True)
                                    else:
                                        print 'no good mesh',mc.polyCompare(mshRes, sep)
                                mc.setAttr(bsTrgt+'.'+trgt, 0)
                                for shp in dicShp.keys():
                                    mc.addAttr(shp, ln='inBets', at='message', multi=True)
                                    mc.addAttr(shp, ln='extractedAs', dt='string')
                                    mc.setAttr(shp+'.extractedAs', 'TRGT', type='string')
                                    dicAdds = {}
                                    trgtAdd = ''
                                    if mc.attributeQuery('adds', n=shp, ex=True):
                                        lMshAdd = mc.getAttr(shp+'.adds', mi=True) or []

                                        if lMshAdd:
                                            if not shp in dicAdds.keys():
                                                dicAdds[shp] = {}
                                            for mshAdd in lMshAdd:
                                                trgtAdd = mc.listConnections(shp+'.adds['+str(mshAdd)+']', s=True) or []
                                                if trgtAdd:
                                                    dicAdds[shp][mc.getAttr(trgtAdd[0]+'.extractedFrom')] = trgtAdd[0]
                                                    if not mc.attributeQuery('inBets', n=trgtAdd[0], ex=True):
                                                        mc.addAttr(trgtAdd[0], ln='inBets', at='message', multi=True)
                                    if dicShp[shp]:
                                        for inBet in dicShp[shp]:

                                            mc.addAttr(inBet, ln='isInBet', at='bool', dv=True)
                                            lastId = mc.getAttr(shp+'.inBets',s=True)
                                            mc.connectAttr(inBet+'.message', shp+'.inBets['+str(lastId)+']')


                                            if mc.attributeQuery('adds', n=inBet, ex=True):
                                                lMshAdd = mc.getAttr(inBet+'.adds', mi=True) or []
                                                if lMshAdd:
                                                    for mshAdd in lMshAdd:
                                                        inBetAdd = mc.listConnections(inBet+'.adds['+str(mshAdd)+']', s=True) or []
                                                        if inBetAdd:
                                                                srcAdd = mc.getAttr(inBetAdd[0]+'.extractedFrom')
                                                                trgtAdd = dicAdds[shp][srcAdd]

                                                                lastId = mc.getAttr(trgtAdd+'.inBets', s=True)
                                                                mc.connectAttr(inBetAdd[0]+'.message', trgtAdd+'.inBets['+str(lastId)+']')

            if skin:
                mc.setAttr(skin[0]+'.envelope', 1)
    return lExpShp




def extractShapes_cor(lMshResults):
    lExCor = []
    #if not mc.objExists('SHAPES_COR'):
        #mc.createNode('transform', n='SHAPES_COR')
    for mshRes in lMshResults:

        bsCor = getBsDef(mshRes, 1)[0]

        nResMsh = bsCor.split('_')[-1].capitalize()
        mshCor = mc.listRelatives(mc.blendShape(bsCor, q=True, g=True)[0], p=True)[0]
        aliasData = getDicBsTrgtDatasAsAlias(bsCor)
        #u'jawRz_L': {'index': u'4', 'sculpt': {1.0: {'id': '6000', 'trgt': u'COR:HEAD:jawRz_L'}}},
        resultTypeMesh = mc.blendShape(bsCor, q=True, g=True)[0]
        nspace = lib_namespace.getNspaceFromObj(resultTypeMesh)
        dicShp = {}
        for trgt in aliasData.keys():
            for wght in aliasData[trgt]['sculpt'].keys():
                id = aliasData[trgt]['sculpt'][wght]['id']
                cor = aliasData[trgt]['sculpt'][wght]['trgt']

                nBase = cor.split(':')[-1]
                if id != '6000':
                    nBase = cor.split(':')[-1][: -4]
                nExShp = 'cor' + nResMsh + '_' + nBase+ id
                #print nExShp
                if not mc.attributeQuery('isInBet', n=cor, ex=True):
                    dicShp['cor'+nResMsh+'_'+nBase+'6000'] = {}
                    dicShp['cor' + nResMsh + '_' + nBase + '6000']['objName'] = nExShp
                    dicShp['cor' + nResMsh + '_' + nBase + '6000']['inBets'] = []

                mc.setAttr(bsCor+'.'+trgt, wght)
                if mc.objExists(nExShp):
                    mc.delete(nExShp)
                extShp = mc.duplicate(cor, n=nExShp)[0]
                lExCor.append(extShp)
                #lCorShp.append(extShp)

                father = mc.listRelatives(cor, p=True)[0]
                noteAttr = mc.getAttr(father+'.notes')
                mc.addAttr(extShp, ln='notes', dt='string')
                mc.setAttr(extShp+'.notes', noteAttr, type='string')


                mc.addAttr(extShp, ln='shpResultType', dt='string')
                mc.addAttr(extShp, ln='weightId', dt='string')
                mc.setAttr(extShp+'.weightId', id, type='string')

                if id != '6000':
                    dicShp['cor'+nResMsh+'_'+nBase+'6000']['inBets'].append(extShp)
                #mc.parent(extShp, 'SHAPES_COR')
                #extAdds = extractAdds(sep, extShp, normalise) or []
                #for add in extAdds:
                    #mc.addAttr(add, ln='weightId', dt='string')
                    #mc.setAttr(add+'.weightId', id, type='string')
            mc.setAttr(bsCor+'.'+trgt, 0)
        #print 'CHECK HEAR:', dicShp.keys()
        for cor in dicShp.keys():
            shp = dicShp[cor]['objName']
            mc.addAttr(shp, ln='inBets', at='message', multi=True)
            mc.addAttr(shp, ln='extractedAs', dt='string')
            mc.setAttr(shp+'.extractedAs', 'COR', type='string')
            if dicShp[cor]['inBets']:
                for inBet in dicShp[cor]['inBets']:
                    lastId = mc.getAttr(shp+'.inBets',s=True)
                    mc.connectAttr(inBet+'.message', shp+'.inBets['+str(lastId)+']')
    return lExCor
#extractShapes_cor()


def extractNameParser(trgt, zone, slice, matZones):
    nTrgt = trgt[len(trgt.split('_')[0]):]
    clearNTrgt = nTrgt
    if '_' in trgt:
        trunk = nTrgt.split('_')
        clearNTrgt = trunk[1]
        for i in range(2, len(trunk)):
            add = trunk[i].capitalize()
            clearNTrgt += add
    pole = ''
    if mc.attributeQuery('sepSlice', n=slice, ex=True):
        ids = mc.getAttr(slice + '.sepSlice', s=True)
        for i in range(0, ids):
            pole += mc.getAttr(slice + '.sepSlice[' + str(i) + ']')
    prefixZone = matZones[zone]
    side = ''
    if 'Left' in slice:
        side = '_L'
    elif 'Right' in slice:
        side = '_R'
    nExShp = prefixZone + '_' + clearNTrgt + pole + side + '6000'
    return nExShp


def genMatSlices():
    dicMatEsp = {}
    dicExtSlices = getSepMsh_v2()
    for zone in dicExtSlices.keys():
        if not zone in dicMatEsp.keys():
            dicMatEsp[zone] = {}
            dicMatEsp[zone]['slices'] = {}
            dicMatEsp[zone]['side'] = []
            dicMatEsp[zone]['length'] = 0
        for slice in dicExtSlices[zone]:
            side = 'Midd'
            if 'Left' in slice:
                side = 'Left'
            elif 'Right' in slice:
                side = 'Right'
            if not side in dicMatEsp[zone]['slices'].keys():
                dicMatEsp[zone]['slices'][side] = []
            if not side in dicMatEsp[zone]['side']:
                dicMatEsp[zone]['side'].append(side)
                dicMatEsp[zone]['length'] += 1
            if mc.attributeQuery('sepSlice', n=slice, ex=True):
                ids = mc.getAttr(slice + '.sepSlice', s=True)
                for i in range(0, ids):
                    pole = mc.getAttr(slice + '.sepSlice[' + str(i) + ']')
                    if not pole in dicMatEsp[zone]['slices'][side]:
                        dicMatEsp[zone]['slices'][side].append(pole)
                        dicMatEsp[zone]['length'] += 1
    return dicMatEsp


def getZoneFromTrgt(trgt, matZones):
    prefix = trgt.split(':')[-1].split('_')[0]
    for zone in matZones.keys():
        if matZones[zone] == prefix:
            return zone

def getCorrespondingSlice(extZone, zone, slice, lextSlices):
    poles = []
    if mc.attributeQuery('sepSlice', n=slice, ex=True):
        ids = mc.getAttr(slice + '.sepSlice', s=True)
        for i in range(0, ids):
            poles.append(mc.getAttr(slice + '.sepSlice[' + str(i) + ']'))
    side = ''
    toto = ''
    if 'Left' in slice:
        side = 'Left'
    elif 'Right' in slice:
        side = 'Right'
    for extSlice in lextSlices:
        #print lextSlices
        if side:
            if side in extSlice:
                toto = extSlice
                if mc.attributeQuery('sepSlice', n=slice, ex=True):
                    ids = mc.getAttr(slice + '.sepSlice', s=True)
                    for i in range(0, ids):
                        if mc.getAttr(slice + '.sepSlice[' + str(i) + ']') in poles:
                            toto = extSlice

    return toto

    #lips mouth SEP:sep_headLipsUp_Middle





def extractShapes_mixTrgt_OLD(getSel, *args, **kwargs):
    # getBsDef(obj, type)
    # TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    # 3 = Result      #
    # _________________#

    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()
    dicMatSep = genMatSlices()
    dicMixZones = getMixsZones()
    lExpShp = []
    lExpShpAdds = []
    faceDatas = faceDescription()
    matZones = faceDatas.trgtNames()
    dicSep = getSepZone()
    print 'TOTO:', dicSep
    dicMixExtTrgr = {}
    dicExtSlices = getSepMsh_v2()
    for mshRes in lMshResult:
        if not mshRes in dicMixExtTrgr.keys():
            dicMixExtTrgr[mshRes] = {}
        bsRes = getBsDef(mshRes, 3)[0]
        #getZonedTrgt(bsRes)
        dataBsRes = getDicBsTrgtDatasAsMsh(bsRes)
        bsMix = getBsDef(mshRes, 2)[0]
        mc.setAttr(bsMix+'.envelope', 1.0)
        dataBsMix = getDicBsTrgtDatasAsMsh(bsMix)
        mixRes = mc.listRelatives(mc.blendShape(bsMix, q=True, g=True)[0], p=True)[0]
        for resTrgt in dataBsRes.keys():
            if not resTrgt == mixRes:
                mc.setAttr(bsRes+'.'+dataBsRes[resTrgt]['data']['alias'], 0.0)
                #print bsRes+'.'+dataBsRes[resTrgt]['data']['alias'], 'turned off'
            if resTrgt == mixRes:
                mc.setAttr(bsRes + '.' + dataBsRes[resTrgt]['data']['alias'], 1.0)
        skin = mc.ls(mc.listHistory(mshRes, ac=True), type='skinCluster') or []
        if skin:
            mc.setAttr(skin[0] + '.envelope', 0)

        for mix in dicMixZones[mshRes].keys():
            dicMixTrgr = getTrgrFromMix(mix)
            if not mix in dicMixExtTrgr[mshRes].keys():
                dicMixExtTrgr[mshRes][mix] = {}
                dicMixExtTrgr[mshRes][mix]['zones'] = []
                dicMixExtTrgr[mshRes][mix]['values'] = {}
                dicMixExtTrgr[mshRes][mix]['trgr'] = {}
                for trgr in dicMixTrgr[mix]['trgt'].keys():
                    dicMixExtTrgr[mshRes][mix]['trgr'][trgr] = dicMixTrgr[mix]['trgt'][trgr]
                    dicMixExtTrgr[mshRes][mix]['values'][trgr] = dicMixTrgr[mix]['trgr'][trgr]

            for mixZone in dicMixZones[mshRes][mix]:
                zoneKey = [k for (k, val) in matZones.items() if val == mixZone][0]
                #print 'HERE :', zoneKey
                if not zoneKey in dicMixExtTrgr[mshRes][mix]['zones']:
                    dicMixExtTrgr[mshRes][mix]['zones'].append(zoneKey)
                if not zoneKey in dicMixExtTrgr[mshRes][mix].keys():
                    dicMixExtTrgr[mshRes][mix][zoneKey] = ''
                dicMixExtTrgr[mshRes][mix][zoneKey] = dicSep[mshRes][zoneKey][0]

        dicextractTrgt = {}
        dicextractTrgt['left'] = []
        dicextractTrgt['right'] = []
        dicextractTrgt['middle'] = []
        for mix in dicMixExtTrgr[mshRes].keys():
            #print 'working on ', mix
            lZones = dicMixExtTrgr[mshRes][mix]['zones']
            for trgr in dicMixExtTrgr[mshRes][mix]['trgr'].keys():
                trgt = dicMixExtTrgr[mshRes][mix]['trgr'][trgr]
                for zone in lZones:
                    lSlices = dicExtSlices[zone]
                    for slice in lSlices:
                        extTrgrName = extractNameParser(trgt, zone, slice, matZones)
                        if extTrgrName.endswith('_L6000'):
                            if not extTrgrName in dicextractTrgt['left']:
                                dicextractTrgt['left'].append(extTrgrName)
                        elif extTrgrName.endswith('_R6000'):
                            if not extTrgrName in dicextractTrgt['right']:
                                dicextractTrgt['right'].append(extTrgrName)
                        else :
                            if not extTrgrName in dicextractTrgt['middle']:
                                dicextractTrgt['middle'].append(extTrgrName)

            len = 0
            extZone = ''
            for zone in dicMixExtTrgr[mshRes][mix]['zones']:
                if dicMatSep[zone]['length'] > len:
                    len = dicMatSep[zone]['length']
                    extZone = zone

            loadMixValues([mix])
            mc.refresh()
            for slice in dicExtSlices[extZone]:
                mixName = mix.split(':')[-1]
                side = ''
                if 'Left' in slice:
                    side = '_L'
                elif 'Right' in slice:
                    side = '_R'
                if mc.attributeQuery('sepSlice', n=slice, ex=True):
                    ids = mc.getAttr(slice + '.sepSlice', s=True)
                    for i in range(0, ids):
                        pole = mc.getAttr(slice + '.sepSlice[' + str(i) + ']')
                        mixName += pole
                mixName = mixName+side
                if mc.objExists(mixName):
                    mc.delete(mixName)
                new = mc.duplicate(slice, n=mixName)[0]
                lExpShp.append(new)
                mc.parent(new, world=True)
                lAttrs = mc.listAttr(new, ud=True)
                for attr in lAttrs:
                    if mc.attributeQuery(attr, n=new, ex=True):
                        mc.setAttr(new+'.' + attr, l=False)
                        mc.deleteAttr(new+'.' + attr)
                mc.addAttr(new, ln='trgrList', dt='string', multi=True)
                mc.addAttr(new, ln='trgrValues', at='float', multi=True)
                mc.addAttr(new, ln='extractedAs', dt='string')
                mc.setAttr(new+'.extractedAs', 'MIX', type='string')

                lTrgr = dicMixExtTrgr[mshRes][mix]['trgr']
                print mix, lTrgr, 'cul'
                id = 0
                for trgr in lTrgr.keys():
                    zone  = getZoneFromTrgt(lTrgr[trgr], matZones)
                    print mix, ':'
                    print trgr, zone, extZone, '5907'
                    extSlice = slice
                    val = dicMixExtTrgr[mshRes][mix]['values'][trgr]
                    #recurceGetMixTrgr
                    if zone:
                        if not zone == extZone:
                            lExtSlices = dicExtSlices[zone]
                            extSlice = getCorrespondingSlice(extZone, zone, slice, lExtSlices)

                        trgrExt = extractNameParser(dicMixExtTrgr[mshRes][mix]['trgr'][trgr], zone, extSlice, matZones)
                        #print trgrExt
                        mc.setAttr(new+'.trgrList['+str(id)+']', trgrExt, type='string')
                        mc.setAttr(new + '.trgrValues[' + str(id) + ']', val)
                        id += 1



    return lExpShp
            #.mixExtraction


def dicTmpActivator(bs):
    dicTmpAct = {}
    dicTmpAct[bs] = {}
    lNodes = mc.listConnections(bs, s=True, t='multDoubleLinear') or []
    if lNodes:
        for node in lNodes:
            if mc.attributeQuery('tmpActivator', n=node, ex=True):
                if not node in dicTmpAct[bs].keys():
                    dicTmpAct[bs][node] = []
                dicTmpAct[bs][node] = mc.listConnections(node + '.output', d=True, c=True, p=True)
    return dicTmpAct

def unplugActivators(dicActivator):
    for bs in dicActivator.keys():
        for activ in dicActivator[bs]:
            plugs = dicActivator[bs][activ]
            mc.disconnectAttr(plugs[0], plugs[-1])
#unplugActivators(dicActivator)

def replugActivators(dicActivator):
    for bs in dicActivator.keys():
        for activ in dicActivator[bs]:
            plugs = dicActivator[bs][activ]
            mc.connectAttr(plugs[0], plugs[-1], f=True)
#replugActivators(dicActivator)
# dicTmpActivator('bsMixTrgt_head')
def extractShapes_mixTrgt(getSel, *args, **kwargs):
    # getBsDef(obj, type)
    # TYPES :__________#
    # 0 = target      #
    # 1 = corrective  #
    # 2 = mix         #
    # 3 = Result      #
    # _________________#
    lMshResult = []
    if isinstance(getSel, list):
        lMshResult = getSel
    else:
        lMshResult = getSel()
    dicMatSep = genMatSlices()
    dicMixZones = getMixsZones()
    lExpShp = []
    lExpShpAdds = []
    #matZones = trgtNames()
    faceDatas = faceDescription()
    matZones = faceDatas.trgtNames()
    dicSep = getSepZone()
    dicMixExtTrgr = {}
    dicExtSlices = getSepMsh_v2()
    for mshRes in lMshResult:
        if not mshRes in dicMixExtTrgr.keys():
            dicMixExtTrgr[mshRes] = {}
        bsRes = getBsDef(mshRes, 3)[0]
        dataBsRes = getDicBsTrgtDatasAsMsh(bsRes)
        bsMix = getBsDef(mshRes, 2)[0]
        mc.setAttr(bsMix + '.envelope', 1.0)
        dataBsMix = getDicBsTrgtDatasAsMsh(bsMix)
        mixRes = mc.listRelatives(mc.blendShape(bsMix, q=True, g=True)[0], p=True)[0]
        for resTrgt in dataBsRes.keys():
            if not resTrgt == mixRes:
                mc.setAttr(bsRes + '.' + dataBsRes[resTrgt]['data']['alias'], 0.0)
            if resTrgt == mixRes:
                mc.setAttr(bsRes + '.' + dataBsRes[resTrgt]['data']['alias'], 1.0)
        skin = mc.ls(mc.listHistory(mshRes, ac=True), type='skinCluster') or []
        if skin:
            mc.setAttr(skin[0] + '.envelope', 0)
        for mix in dicMixZones[mshRes].keys():
            dicMixTrgr = getTrgrFromMix(mix)
            if not mix in dicMixExtTrgr[mshRes].keys():
                dicMixExtTrgr[mshRes][mix] = {}
                dicMixExtTrgr[mshRes][mix]['zones'] = []
                dicMixExtTrgr[mshRes][mix]['values'] = {}
                dicMixExtTrgr[mshRes][mix]['trgr'] = {}
                for trgr in dicMixTrgr[mix]['trgt'].keys():
                    dicMixExtTrgr[mshRes][mix]['trgr'][trgr] = dicMixTrgr[mix]['trgt'][trgr]
                    dicMixExtTrgr[mshRes][mix]['values'][trgr] = dicMixTrgr[mix]['trgr'][trgr]
            for mixZone in dicMixZones[mshRes][mix]:
                zoneKey = [k for (k, val) in matZones.items() if val == mixZone][0]
                if not zoneKey in dicMixExtTrgr[mshRes][mix]['zones']:
                    dicMixExtTrgr[mshRes][mix]['zones'].append(zoneKey)
                if not zoneKey in dicMixExtTrgr[mshRes][mix].keys():
                    dicMixExtTrgr[mshRes][mix][zoneKey] = ''
                dicMixExtTrgr[mshRes][mix][zoneKey] = dicSep[mshRes][zoneKey][0]
        dicextractTrgt = {}
        dicextractTrgt['left'] = []
        dicextractTrgt['right'] = []
        dicextractTrgt['middle'] = []
        dicActivator = dicTmpActivator(bsMix)
        unplugActivators(dicActivator)
        for mix in dicMixExtTrgr[mshRes].keys():
            for trgr in dicMixExtTrgr[mshRes][mix]['trgr'].keys():
                trgt = dicMixExtTrgr[mshRes][mix]['trgr'][trgr]
                len = 0
                extZone = ''
                for zone in dicMixExtTrgr[mshRes][mix]['zones']:
                    if dicMatSep[zone]['length'] > len:
                        len = dicMatSep[zone]['length']
                        extZone = zone

            #loadMixValues([mix])
            wghtPlug = bsMix+'.'+dataBsMix[mix]['data']['alias']
            mc.setAttr(wghtPlug, 1.0)
            mc.refresh()
            for slice in dicExtSlices[extZone]:
                side = ''
                if 'Left' in slice:
                    side = '_L'
                elif 'Right' in slice:
                    side = '_R'
                mixName = extractNameParser(mix, extZone, slice, matZones)
                if mc.objExists(mixName):
                    mc.delete(mixName)
                new = mc.duplicate(slice, n=mixName)[0]
                lExpShp.append(new)
                mc.parent(new, world=True)
                lAttrs = mc.listAttr(new, ud=True)
                for attr in lAttrs:
                    if mc.attributeQuery(attr, n=new, ex=True):
                        mc.setAttr(new + '.' + attr, l=False)
                        mc.deleteAttr(new + '.' + attr)
                mc.addAttr(new, ln='trgrList', dt='string', multi=True)
                mc.addAttr(new, ln='trgrValues', at='float', multi=True)
                mc.addAttr(new, ln='extractedAs', dt='string')
                mc.setAttr(new + '.extractedAs', 'MIX', type='string')
                lTrgr = dicMixExtTrgr[mshRes][mix]['trgr']
                id = 0
                for trgr in lTrgr.keys():
                    zone = getZoneFromTrgt(lTrgr[trgr], matZones)
                    extSlice = slice
                    val = dicMixExtTrgr[mshRes][mix]['values'][trgr]
                    if not zone:
                        trgtMix = dicMixExtTrgr[mshRes][mix]['trgr'][trgr]
                        if mc.attributeQuery('trgrList', n=trgtMix, ex=True):
                            # a revoir pour le cote recurcif si il y a des mix de mix de mix de mix.....
                            zone = [k for (k, itm) in matZones.items() if itm == dicMixZones[mshRes][trgtMix][0]][0]
                            trgrMixExt = extractNameParser(trgtMix, zone, extSlice, matZones)
                    if zone:
                        if not zone == extZone:
                            lExtSlices = dicExtSlices[zone]
                            extSlice = getCorrespondingSlice(extZone, zone, slice, lExtSlices)
                        trgrExt = extractNameParser(dicMixExtTrgr[mshRes][mix]['trgr'][trgr], zone, extSlice, matZones)
                        mc.setAttr(new + '.trgrList[' + str(id) + ']', trgrExt, type='string')
                        mc.setAttr(new + '.trgrValues[' + str(id) + ']', val)
                        id += 1
            mc.setAttr(wghtPlug, 0.0)
        replugActivators(dicActivator)
    return lExpShp
    # .mixExtraction

def extractBones():
    lNodes = mc.ls('*.nodeType', r=True, o=True)
    lTpl = []
    lCtrl = []
    lCnst = []
    for node in lNodes:
        if mc.getAttr(node+'.nodeType') == 'controlTemplate':
            lTpl.append(node)
    for tpl in lTpl:
        ctrl = tpl.replace('tpl_', 'c_')
        if mc.objExists(ctrl):
            if mc.attributeQuery('nodeType', n=ctrl, ex=True):
                if mc.getAttr(ctrl+'.nodeType') == 'control':
                    lCnst.append(mc.parentConstraint(ctrl, tpl, mo=False)[0])
                    lCnst.append(mc.scaleConstraint(ctrl, tpl, mo=False)[0])
                else:
                    return 'bad ctrl', ctrl
            else:
                return 'bad ctrl', ctrl
        else:
            return 'bad ctrl', ctrl
    mc.delete(lCnst)
    return lTpl



def extractShapes_v3(getSel, *args, **kwargs):
    lMshResults = getSel()
    if not lMshResults:
        mc.warning('please, select the msh_results you want to extract')
        return
    #lib_pipe.saveNewRev()
    lExtracted = mc.ls('*.extractedAs', o=True) or []
    lTplBones = extractBones()
    print 'bones extracted'
    lTplFace = extractTpl('world')
    print 'tplFace extracted'
    lTrgt = extractShapes_trgt(lMshResults)
    print 'trgt extracted'
    chkCor = getBsDef(None, 1) or []
    lCor = []
    if chkCor:
        lCor = extractShapes_cor(lMshResults)
    chkMixTrgt = getBsDef(None, 2) or []
    lMixTrgt = []
    if chkMixTrgt:
        lMixTrgt = extractShapes_mixTrgt(lMshResults)
    dicSkin = {}
    lToExport = []
    if not mc.objExists('toExport'):
        mc.createNode('transform', n='toExport')
    if lTplBones:
        lToExport.extend(lTplBones)
        #for bone in lTplBones:
            #chkParent = mc.listRelatives(bone, p=True) or []
            #if chkParent:
                #if not chkParent[0] in lTplBones:
                    #mc.parent(bone, 'toExport')
    if lTplFace:
        #try:
            #mc.parent(lTplFace, 'toExport')
        #except:
            #pass
        lToExport.extend(lTplFace)
    if lTrgt:
        mc.parent(lTrgt, 'toExport')
        lToExport.extend(lTrgt)
    if lCor:
        mc.parent(lCor, 'toExport')
        lToExport.extend(lCor)
    if lMixTrgt:
        mc.parent(lMixTrgt, 'toExport')
        lToExport.extend(lMixTrgt)
    if dicSkin:
        lToExport.extend(dicSkin)
    if lExtracted:
        for extracted in lExtracted:
            if not extracted in lToExport:
                if mc.objExists(extracted):
                    mc.delete(extracted)
    #print lToExport
    #trgtScene = mc.file(q=True, sceneName=True)
    #shpScene = mc.file(q=True, sceneName=True).replace('_trgt_', '_shp_')
    #mc.select(cl=True)
    #mc.select(lToExport)
    #mc.file(shpScene, force=True, exportSelected=True, type="mayaAscii")
    #mc.file(shpScene, o=True, f=True)
    print 'extracted'
#extractShapes_v3(mc.ls(sl=True))



def recursGetResultSlices(msh):
    lSlice = mc.listConnections(msh+'.slices') or []
    if lSlice:
        for slice in lSlice:
            lSlice.extend(recursGetResultSlices(slice))
    return lSlice
#recursGetResultSlices('result_head')

def getResultSlices(msh):
    lSlices = recursGetResultSlices(msh)
    return lSlices
#getResultSlices('result_head')



def linkMshSrc(lNodes):
    mshSrc = lNodes[0]
    lMshDest = lNodes[1:]
    for mshDest in lMshDest:
        if not mc.attributeQuery('mshOrig', n=mshDest, ex=True):
            mc.addAttr(mshDest, ln='mshOrig', dt='string')
        mc.setAttr(mshDest+'.mshOrig', lock=False)
        mc.setAttr(mshDest+'.mshOrig', mshSrc, type='string')
        mc.setAttr(mshDest+'.mshOrig', lock=True)


def linkSlicesMshOrig(lMsh):
    for msh in lMsh:
        lSlices = getResultSlices(msh)
        for slice in lSlices:
            linkMshSrc([msh, slice])



def initShpBuild(mshResult):
    storageGrp = geStorageGrp('SHP', mshResult)
    bsShp = getBsDef(mshResult, 4)

    if not bsShp:
        shpResult = genResult(mshResult, 'SHP')
        mc.setAttr(shpResult+'.v', False)
        bsShp = mc.blendShape(shpResult, n='bsShp'+mshResult[len(mshResult.split('_')[0]):])[0]
        bsTypeAttrr(bsShp, 4)

    return shpResult

def get_skin(msh):
    dicSkin = {}
    shp = mc.listRelatives(msh, s=True, ni=True)[-1]
    lHist = mc.listHistory(shp)
    skin = mc.ls(lHist, type='skinCluster') or []
    if skin:
        dicSkin[skin[0]] = mc.skinCluster(skin[0],query=True,inf=True)
    return dicSkin
#get_skin(mc.ls(sl=True)[0])

def getSkinWght(msh):
    dicWght = {}
    lVtx = mc.ls(msh+'.vtx[*]', r=True, fl=True)
    skin = get_skin(msh).keys()[0]
    for vtx in lVtx:
        if not vtx in dicWght.keys():
            dicWght[vtx] = {}
        lWght = mc.skinPercent(skin, vtx, q=True, v=True, ib=False)
        lSk = mc.skinPercent(skin, vtx, q=True, t=None, ib=False) or []
        for i in range(0, len(lSk)):
            dicWght[vtx][lSk[i]] = lWght[i]
    return dicWght
#getSkinWght(mc.ls(sl=True)[0])
def tansfert_skin_by_joint(mshSrc, mshDest):
    dicSkinDest = get_skin(mshDest)
    skinSrc = get_skin(mshSrc).keys()[0]
    dicSkinSrc = get_weighted_vtx_by_joint(mshSrc, byType='sk')
    lSk = dicSkinSrc[skinSrc]
    skinDest = ''
    if dicSkinDest:
        skinDest = dicSkinDest.keys()[0]
    else:
        lSkDest = []
        mc.select(cl=True)
        mc.select(lSk, mshDest)
        skinDest = mc.skinCluster(tsb=True)[0]
        mc.select(cl=True)
    for sk in lSk:
        for vtx in dicSkinSrc[sk]:
            vtxDest = vtx.replace(mshSrc, mshDest)
            wght = mc.skinPercent( skinSrc, vtx, transform=sk, query=True )
            val = (sk, wght)
            print vtx, 'to :', vtxDest, val
            mc.skinPercent(skinDest, vtxDest, transformValue=val)
    print 'done'
#tansfert_skin_by_joint(mc.ls(sl=True)[0])
#tansfert_skin_by_joint('tmp_head', 'MOD:msh_body')


def tansfert_skin_by_vtx(mshSrc, mshDest, nspaceSrc, nspaceDest, lVtxToTransfert, dicToReplace):
    if not lVtxToTransfert:
        lVtxToTransfert = mc.ls(mshSrc+'.vtx[*]', fl=True)
    dicSkinSrc = get_skin(mshSrc)
    skinSrc = dicSkinSrc.keys()[0]
    lSkSrc = dicSkinSrc[skinSrc]

    dicSkinDest = get_skin(mshDest)
    skinDest = ''
    lMissedSkDest = []

    if dicSkinDest:
        skinDest = dicSkinDest.keys()[0]
        for sk in lSkSrc:
            skDest = sk.replace(nspaceSrc, nspaceDest)
            if not skDest in dicSkinDest[skinDest]:
                if mc.objExists(skDest):
                    print skDest, 'need to be added'
                    mc.skinCluster(skinDest, edit=True, ai=skDest, lw=True, wt=0)
                    mc.skinCluster(skinDest, edit=True, inf=skDest, lw=False)
                else:
                    lMissedSkDest.append(skDest)

        if lMissedSkDest:
            mc.warning('followed sk doesn t exists :', lMissedSkDest)
            return
    elif not dicSkinDest:
        lSkDest = []
        mc.select(cl=True)
        for sk in lSkSrc:
            skDest = sk.replace(nspaceSrc, nspaceDest)
            if mc.objExists(skDest):
                lSkDest.append(skDest)
            else:
                lMissedSkDest.append(skDest)

        if lMissedSkDest:
            mc.warning('followed sk doesn t exists :', lMissedSkDest)
            return
        mc.select(lSkDest, mshDest)
        skinDest = mc.skinCluster(tsb=True)[0]
        mc.select(cl=True)
    dicWghtDest = getSkinWght(mshDest)
    dicWghtSrc = getSkinWght(mshSrc)
    for vtxSrc in dicWghtSrc.keys():
        if vtxSrc in lVtxToTransfert:
            lWght = []
            id = vtxSrc.split('[')[-1].replace(']', '')
            vtxDest = mshDest+'.vtx['+str(id)+']'
            chkWght = 0.0
            for sk in dicWghtSrc[vtxSrc].keys():
                wght = (sk.replace(nspaceSrc, nspaceDest), dicWghtSrc[vtxSrc][sk])
                #if skSrc have replace sk value (name) it will take the weight value of the sk name
                #if skSrc have not replace sk value (name) it will take the weight value of all the sk of skinDest
                if sk in dicToReplace.keys():
                    if dicToReplace[sk]:
                        wght =  (dicToReplace[sk], dicWghtDest[vtxSrc][sk])
                    else:
                        wght = (sk.replace(nspaceSrc, nspaceDest), 0.0)
                        for skDest in dicWghtDest[vtxDest].keys():
                            wghtDest = (skDest, dicWghtDest[vtxDest][skDest])
                            lWght.append(wghtDest)
                            chkWght+=wghtDest[-1]
                lWght.append(wght)
                chkWght+=wght[-1]
            if chkWght > 1.0:
                #print vtxDest, chkWght
                lNormWght = []
                for wght in lWght:
                    normWght = wght
                    if wght[-1] > 0.0:
                        #print wght
                        normWght = (wght[0], setRange(0.0, chkWght, 0.0, 1.0, wght[-1]))
                    lNormWght.append(normWght)
                lWght = lNormWght
            if mc.objExists(vtxDest):
                mc.skinPercent(skinDest, vtxDest, transformValue=lWght, zri=True)
    print 'done'
#tansfert_skin_by_vtx(mc.ls(sl=True)[0], mc.ls(sl=True)[-1])
#tansfert_skin_by_vtx('tmp_head', 'MOD:msh_body', '', '',  mc.ls(sl=True, fl=True), {'': ''})#SHP:sk_headSocket

def buildShapesTRGTRig(getSel, *args, **kwargs):
    lMshResults = getSel()
    #extractShapes_v3(lMshResults)
    setFaceTpl()
    lMshOrig = []
    for mshRes in lMshResults:
        mshOrig = mshRes.replace(mshRes.split('_')[0], 'msh')
        if not mc.objExists(mshOrig):
            activeDef(mshRes, 0)
            mshOrig = mc.duplicate(mshRes, n=mshRes.replace(mshRes.split('_')[0], 'msh'))[0]
            activeDef(mshRes, 1)
            mc.addAttr(mshOrig, ln='editShp', at='bool', dv=True, k=True)
            mc.parent(mshOrig, world=True)
        lMshOrig.append(mshOrig)
        dicSkin = get_skin(mshRes)
        if dicSkin:
            tansfert_skin_by_vtx(mshRes, mshOrig, '', '', [], {'': ''})#SHP:sk_headSocket
    buildFaceTpl_v2(lMshOrig, doPath=False)
    lAdds = []
    lAddsOrig = []

    for msh in mc.ls('*.adds', r=True):
        chkMult = mc.getAttr(msh, mi=True)
        if chkMult:
            for i in chkMult:
                if mc.listConnections(msh+'['+str(i)+']', s=True):
                    add = mc.listConnections(msh+'['+str(i)+']', s=True)[0]
                    if mc.attributeQuery('mshOrig', n=add, ex=True):
                        if not mc.getAttr(add+'.mshOrig') in lAdds:
                            lAdds.append(mc.getAttr(add+'.mshOrig'))
    if lAdds:
        for add in lAdds:
            if not mc.objExists(add.replace(add.split('_')[0], 'msh')):
                addOrig = mc.duplicate(add, n=add.replace(add.split('_')[0], 'msh'))[0]

                mc.addAttr(addOrig, ln='driverOrig', dt='string')
                mc.setAttr(addOrig+'.driverOrig', mshOrig, type='string')
                mc.setAttr(addOrig+'.driverOrig', lock=True)

                lAddsOrig.append(addOrig)
                mc.parent(addOrig, world=True)



    for mshOrig in lMshOrig:
        #print 'Heeeere :', mshOrig
        connectFaceRig_v3([mshOrig], True, True, True, True)
        dicSkin = get_skin(mshOrig)
        if dicSkin:
            bs = getBsDef(mshOrig, None)
        mc.reorderDeformers(dicSkin.keys()[0], bs[0], mshOrig)

    #for addOrig in lAddsOrig:
        #driver = mc.getAttr(addOrig+'.driverOrig')
        #mc.select(cl=True)
        #mc.select(addOrig)
        #mc.select(driver, add=True)
        #mc.CreateWrap()


########################################################################################################################################################################
########################################################################################################################################################################
#BUILD##################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
def setFaceTpl(*args, **kwargs):
    dicTpl = {}
    lFaceTpl = mc.ls('*.tplZone', r=True, o=True)
    for tpl in lFaceTpl:
        key = mc.getAttr(tpl+'.tplZone', asString=True)
        if not key in dicTpl.keys():
            dicTpl[key] = []
        dicTpl[key].append(tpl)
    for key in dicTpl.keys():
        lib_controlGroup.addTplsToCg(dicTpl[key], 'cg_'+key)
        for tpl in dicTpl[key]:
            if mc.attributeQuery('buildPoseNode', n=tpl, ex=True):
                mc.setAttr(tpl+'.buildPoseNode', 1)
            if tpl.endswith('_L'):
                mc.setAttr(tpl+'.isMirrored', 1)
                mc.setAttr(tpl+'.mirrorType', 4)
                if key == 'lips':
                    mc.setAttr(tpl+'.mirrorType', 0)
            print tpl, 'added to: cg_'+key

#setFaceTpl()

def buildFaceTpl():
    lZones = []
    #A CORRIGER!!!!
    lMsh = mc.ls(sl=True) or []
    if lMsh:
        mshPath = lMsh[0].replace(lMsh[0].split('_')[0], 'path')
        msh = mshPath
        if not mc.objExists(mshPath):
            msh = mc.duplicate(lMsh[0], n=lMsh[0].replace(lMsh[0].split('_')[0], 'path'))[0]
            mc.parent(msh, world=True)
        #########################
        dicSym = {}
        if not mc.attributeQuery('symTabLeft', n=msh, ex=True):
            crtSymAttr([msh])
        iter = mc.getAttr(msh+'.symTabLeft', s=True)
        for i in range(0, iter):
            dicSym[mc.getAttr(msh+'.symTabLeft['+str(i)+']')] = mc.getAttr(msh+'.symTabRight['+str(i)+']')
        #dicTrgt = trgtNames()
        faceDatas = faceDescription()
        dicTrgt = faceDatas.trgtNames()
        enAttr=''
        for key in dicTrgt.keys():
            enAttr = enAttr+key+':'

        lFaceTpl = mc.ls('*.tplZone', r=True, o=True)
        for tpl in lFaceTpl:
            zone = mc.getAttr(tpl+'.tplZone', asString=True)
            if not zone in lZones:
                lZones.append(zone)
        for zone in lZones:
            lib_controlGroup.buildTplCg('cg_'+zone)
            lRoots = mc.listConnections('cg_'+zone+'.membersVisibility')
            for root in lRoots:
                #if not mc.listRelatives(root, p=True)[0] == root.split(':')[-1].replace('root_', 'ca_'):
                pose = mc.listRelatives(root, c=True)[0]
                ctrl = mc.listRelatives(pose, c=True)[0]
                tpl = mc.listConnections(ctrl+'.nodes[0]', s=True)[0]
                side = mc.getAttr(ctrl+'.mirrorSide', asString=True)

                if not mc.attributeQuery('ctrlZone', n=ctrl, ex=True):
                    mc.addAttr(ctrl, ln='ctrlZone', at='enum', en=enAttr)
                mc.connectAttr(tpl+'.tplZone', ctrl+'.ctrlZone', f=True)

                if not mc.ls(mc.listConnections(pose), type='multiplyDivide'):
                    mlt = mc.createNode('multiplyDivide')
                    for i in ['X', 'Y', 'Z']:
                        mc.setAttr(mlt+'.input2'+i, -1)
                        mc.connectAttr(ctrl+'.translate'+i, mlt+'.input1'+i, f=True)
                        mc.connectAttr(mlt+'.output'+i, pose+'.translate'+i, f=True)

                #mlt = mc.createNode('multiplyDivide')
                #for i in ['X', 'Y', 'Z']:
                    #mc.setAttr(mlt+'.input2'+i, -1)
                    #mc.connectAttr(ctrl+'.rotate'+i, mlt+'.input1'+i)
                    #mc.connectAttr(mlt+'.output'+i, pose+'.jointOrient'+i)

                vtx = int(mc.getAttr(tpl+'.vtxId'))
                if side == 'right':
                    if vtx in dicSym.keys():
                        suce = vtx
                        vtx = dicSym[suce]

                rootFather = mc.listRelatives(root, p=True)[0]
                crvShp = mc.ls(mc.listHistory(rootFather), type='nurbsCurve') or []
                if crvShp:
                    mc.parent(root, world=True)
                    mc.delete(rootFather)
                    mc.delete(mc.listRelatives(crvShp, p=True)[0])

                crvPath = crtCrvPathCtrl(root, msh, vtx)
                ca = curveAttach(crvPath[0], root)

    else:
        mc.warning('select the mesh you want to attach the rig')


def buildFaceTpl_v2(getSel, doPath=True, *args, **kwargs):
    lMshDest = []
    if isinstance(getSel, list):
        lMshDest = getSel
    else:
        lMshDest = getSel()

    lZones = []
    if lMshDest:
        mshPath = lMshDest[0]
        if doPath == True:
            mshPath = lMshDest[0].replace(lMshDest[0].split('_')[0], 'path')
            if not mc.objExists(mshPath):
                mshPath = mc.duplicate(lMshDest[0], n=lMshDest[0].replace(lMshDest[0].split('_')[0], 'path'))[0]
                mc.parent(mshPath, world=True)
        activeDef(mshPath, False)

            #########################
        dicSym = {}
        if not mc.attributeQuery('symTabLeft', n=mshPath, ex=True):
            crtSymAttr([mshPath])
        iter = mc.getAttr(mshPath+'.symTabLeft', s=True)
        for i in range(0, iter):
            dicSym[mc.getAttr(mshPath+'.symTabLeft['+str(i)+']')] = mc.getAttr(mshPath+'.symTabRight['+str(i)+']')
        #dicTrgt = trgtNames()
        faceDatas = faceDescription()
        dicTrgt = faceDatas.trgtNames()
        enAttr=''
        for key in dicTrgt.keys():
            enAttr = enAttr+key+':'

        lFaceTpl = mc.ls('*.tplZone', r=True, o=True)
        for tpl in lFaceTpl:
            zone = mc.getAttr(tpl+'.tplZone', asString=True)
            if not zone in lZones:
                lZones.append(zone)
        for zone in lZones:
            lib_controlGroup.buildTplCg('cg_'+zone)
            getRoots = mc.listConnections('cg_'+zone+'.membersVisibility')
            lRoots = []
            for root in getRoots:
                if mc.attributeQuery('nodeType', n=root, ex=True):
                    if mc.getAttr(root+'.nodeType') == 'root':
                        lRoots.append(root)
            for root in lRoots:
                #if not mc.listRelatives(root, p=True)[0] == root.split(':')[-1].replace('root_', 'ca_'):
                pose = mc.listRelatives(root, c=True)[0]
                ctrl = mc.listRelatives(pose, c=True)[0]
                tpl = mc.listConnections(ctrl+'.nodes[0]', s=True)[0]
                side = mc.getAttr(ctrl+'.mirrorSide', asString=True)

                if not mc.attributeQuery('ctrlZone', n=ctrl, ex=True):
                    mc.addAttr(ctrl, ln='ctrlZone', at='enum', en=enAttr)
                mc.connectAttr(tpl+'.tplZone', ctrl+'.ctrlZone', f=True)
                if not mc.ls(mc.listConnections(pose, s=True, d=False), type='multiplyDivide'):
                    mlt = mc.createNode('multiplyDivide')
                    for i in ['X', 'Y', 'Z']:
                        mc.setAttr(mlt+'.input2'+i, -1)
                        mc.connectAttr(ctrl+'.translate'+i, mlt+'.input1'+i, f=True)
                        mc.connectAttr(mlt+'.output'+i, pose+'.translate'+i, f=True)

                #mlt = mc.createNode('multiplyDivide')
                #for i in ['X', 'Y', 'Z']:
                    #mc.setAttr(mlt+'.input2'+i, -1)
                    #mc.connectAttr(ctrl+'.rotate'+i, mlt+'.input1'+i)
                    #mc.connectAttr(mlt+'.output'+i, pose+'.jointOrient'+i)

                vtx = int(mc.getAttr(tpl+'.vtxId'))
                if side == 'right':
                    if vtx in dicSym.keys():
                        suce = vtx
                        vtx = dicSym[suce]

                rootFather = mc.listRelatives(root, p=True)[0]
                rigGrp = [rootFather]
                crvShp = mc.ls(mc.listHistory(rootFather), type='nurbsCurve') or []
                if crvShp:
                    rigGrp = mc.listRelatives(rootFather, p=True) or []
                    mc.parent(root, world=True)
                    mc.delete(rootFather)
                    mc.delete(mc.listRelatives(crvShp, p=True)[0])

                crvPath = crtCrvPathCtrl(root, mshPath, vtx)
                ca = curveAttach(crvPath[0], root)
                if rigGrp:
                    if mc.objExists(rigGrp[0]):
                        mc.parent(ca, rigGrp[0])
        activeDef(mshPath, True)

    else:
        mc.warning('select the mesh you want to attach the rig')


def getCtrlMirror(ctrl):
    lIds = getAttrIds(ctrl,'nodesId')
    ctrlMirror = ''
    for id in lIds:
        if mc.getAttr(ctrl+'.nodesId['+str(id)+']') == 'mirror':
            ctrlMirror = mc.listConnections(ctrl+'.nodes['+str(id)+']', s=True)[0]
    return ctrlMirror
#getCtrlMirror(mc.ls(sl=True)[0])





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

    #bs= 'bsRes_head'
    mshBase = mc.listRelatives(mc.blendShape(bs, q=True, g=True)[0], p=True)[0]

    posBase = mc.xform(mshBase, q=True, ws=True, t=True)

    #dicTrgt = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()

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
                                elif slice == 'Corn':
                                    toFind+='Corner'
                            for sidedCtrl in lDriver:
                                ctrlPole = sidedCtrl.split(zone)[-1].split('_')[0]
                                if toFind == ctrlPole:
                                    driver = sidedCtrl
                                    print shp, ' ->', driver, '.', chan,


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
                        val = 90

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







def connectShapesRig(type, bs):
    lTrgt = []
    lShp = mc.ls('*.extractedAs', o=True, r=True)
    for shp in lShp:
        if mc.getAttr(shp+'.extractedAs') == type:
            lTrgt.append(shp)
    if type == 'COR':
        connectCorRig(lTrgt, bs)
    elif type == 'MIX':
        connectMixRig(lTrgt, bs)

#connectShapesRig('COR', 'bs_head')


def connectCorRig(lCor, bs):
    lTrgt = mc.blendShape(bs, q=True, t=True) or []
    msh = mc.blendShape(bs, q=True, g=True)[0]
    for cor in lCor:
        if not mc.attributeQuery('isInBet', n=cor, ex=True):

            dicCtrl = getDicCtrlPose(cor)
            #print 'HERE : ', cor, dicCtrl
            if not cor in lTrgt:
                #if not mc.attributeQuery('isInBet', n=cor, ex=True):
                #print bs
                #print getAttrIds(bs, 'weight')
                id = getAttrIds(bs, 'weight')[-1]+1
                #print id
                mc.blendShape(bs, edit=True, t=(msh, id, cor, 1.0))
                print cor, 'added'

            elif cor in lTrgt:
                dKey = mc.listConnections(bs+'.'+cor.split(':')[-1], s=True, scn=True) or []
                if dKey:
                    mc.delete(dKey)

            for ctrl in dicCtrl.keys():
                print 'working on', ctrl
                clearCtrl = ''
                if mc.objExists(ctrl):
                    clearCtrl = ctrl
                if not mc.objExists(ctrl):
                    chkCtrl = mc.ls('*'+ctrl, r=True) or []
                    if chkCtrl:
                        if len(chkCtrl) == 1:
                            clearCtrl = chkCtrl[0]
                        elif len(chkCtrl) > 1:
                            mc.warning('found more than one ctrl for :', ctrl)


                if clearCtrl:
                    for attr in dicCtrl[ctrl].keys():
                        val = float(dicCtrl[ctrl][attr])
                        mc.setDrivenKeyframe(bs+'.'+cor.split(':')[-1], cd=clearCtrl+'.'+attr, itt='linear', ott='linear', dv=0, v=0)
                        mc.setDrivenKeyframe(bs+'.'+cor.split(':')[-1], cd=clearCtrl+'.'+attr, itt='linear', ott='linear', dv=val, v=1)
                        dKey = mc.listConnections(bs+'.'+cor.split(':')[-1], s=True, scn=True)[0]
                        if dKey:
                            if val > 0:
                                mc.setAttr(dKey+'.postInfinity', 4)
                            elif val < 0:
                                mc.setAttr(dKey+'.preInfinity', 4)
                            print 'key adde for', clearCtrl, attr, 'at val', val


def connectMixRig(getSel, bs, *args, **kwargs):
    lMix = []
    if isinstance(getSel, list):
        lMix = getSel
    else:
        lMix = getSel()
    lTrgt = mc.blendShape(bs, q=True, t=True) or []
    msh = mc.blendShape(bs, q=True, g=True)[0]
    for mix in lMix:
        baseName = mix.replace(mix.split('_')[0], '')
        if not mix in lTrgt:
            id = getAttrIds(bs, 'weight')[-1] + 1
            mc.blendShape(bs, edit=True, t=(msh, id, mix, 1.0))
    for mix in lMix:
        baseName = mix.replace(mix.split('_')[0], '')
        loadMixValuesRig(mix, bs)
        #if not mix in lTrgt:
            #id = getAttrIds(bs, 'weight')[-1] + 1
            #mc.blendShape(bs, edit=True, t=(msh, id, mix, 1.0))
        add = mc.createNode('plusMinusAverage', n='pMA_'+baseName)
        mc.setAttr(add+'.operation', 1)
        for node in ['ran_'+baseName, 'bld_' + baseName]:
            if mc.objExists(node):
                mc.delete(node)
        ran = mc.createNode('setRange', n='ran_'+baseName)
        blendWght = mc.createNode('blendColors', n='bld_' + baseName)
        mc.setAttr(blendWght + '.color2', 0, 0, 0, type='double3')
        mc.setAttr(ran+'.maxX', 1)
        mc.setAttr(ran+'.maxY', 1)
        dicMultWght = {}
        for i in range(0, mc.getAttr(mix+'.trgrList', s=True)-1):
            if mc.objExists('mDL_'+baseName+str(i+1)):
                mc.delete('mDL_'+baseName+str(i+1))
            dicMultWght[i+1] = mc.createNode('multDoubleLinear', n='mDL_'+baseName+str(i+1))

        for i in range(0, mc.getAttr(mix+'.trgrList', s=True)):
            nTrgt = bs+'.'+mc.getAttr(mix+'.trgrList['+str(i)+']')
            valTrgt = mc.getAttr(mix+'.trgrValues['+str(i)+']')
            for node in ['mltd'+baseName+str(i+1), 'div'+baseName+str(i+1)]:
                if mc.objExists(node):
                    mc.delete(node)
            mltd = mc.createNode('multDoubleLinear', n='mltd'+baseName+str(i+1))
            div = mc.createNode('multiplyDivide', n='div'+baseName+str(i+1))
            if i < 2:
                mc.connectAttr(nTrgt, dicMultWght[1]+'.input'+str(i+1))
            else:
                mc.connectAttr(dicMultWght[i-1]+'.output', dicMultWght[i]+'.input1')
                mc.connectAttr(nTrgt, dicMultWght[i]+'.input2')


            mc.setAttr(div+'.operation', 2)
            mc.setAttr(div+'.input2X', 100)

            normVal = setRange(0.0, float(mc.getAttr(mix+'.trgrList', s=True)), 0.0, 1.0, valTrgt)
            ratioVal = (normVal*100)/1
            mc.setAttr(mltd+'.input2', ratioVal)


            mc.connectAttr(nTrgt, mltd+'.input1')
            mc.connectAttr(mltd+'.output', div+'.input1X')
            mc.connectAttr(div+'.outputX', add+'.input1D['+str(i)+']')

        val = mc.getAttr(add+'.output1D')
        mc.setAttr(ran+'.oldMaxX', val)
        print 'HERE:',  dicMultWght
        val = mc.getAttr(dicMultWght[len(dicMultWght)]+'.output')
        mc.setAttr(ran+'.oldMaxY',  val)
        mc.connectAttr(add+'.output1D', ran+'.valueX')
        mc.connectAttr(dicMultWght[len(dicMultWght)]+'.output', ran+'.valueY')
        mc.connectAttr(ran+'.outValueX', blendWght+'.color1R')
        mc.connectAttr(ran+'.outValueY', blendWght+'.blender')
        #mc.connectAttr(blendWght+'.outputR', bsMix+'.'+mixResult.split(':')[-1])
        mc.connectAttr(blendWght+'.outputR', bs+'.'+mix.split(':')[-1])
    for trgt in lTrgt:
        if trgt.endswith('6000'):
            mc.setAttr(bs+'.'+trgt.split(':')[-1], 0.0)


#blendMixTrgt(mc.ls(sl=True)[0])

def connectFatherSlicesCtrl():
    lTpl = mc.ls('*.zoneParentDriver', r=True, o=True)
    lDkeys = mc.ls('*.driverChan', r=True, o=True)
    dicDKeys = {}
    for dKey in lDkeys:
        ctrl = mc.getAttr(dKey+'.driverChan').split('.')[0]
        if not ctrl in dicDKeys.keys():
            dicDKeys[ctrl] = {}
        chan = mc.getAttr(dKey+'.driverChan').split('.')[-1]
        if not chan in dicDKeys[ctrl].keys():
            dicDKeys[ctrl][chan] = []
        if not dKey in dicDKeys[ctrl][chan]:
            dicDKeys[ctrl][chan].append(dKey)

    if lTpl:
        dicParentSlice = {}
        for tpl in lTpl:
            nspace = ''
            if ':' in tpl:
                nspace = tpl.split(':')[0]+':'

            driven = ''
            chkDriven = mc.listConnections(tpl+'.message', d=True) or []
            if chkDriven:
                for node in chkDriven:
                    if mc.attributeQuery('nodeType', n=node, ex=True):
                        if mc.getAttr(node+'.nodeType') == 'control':
                            if mc.getAttr(node+'.mirrorSide', asString=True) in ['none', 'left', 'middle']:
                                driven = node
                drivenM = getCtrlMirror(driven)
                if not drivenM:
                    drivenM = driven
            lIds = getAttrIds(tpl, 'zoneParentDriver')
            for id in lIds:
                tplDriver = mc.getAttr(tpl+'.zoneParentDriver['+str(id)+']')
                driver = ''
                chkDriver = mc.listConnections(nspace+tplDriver+'.message', d=True) or []
                if chkDriver:
                    for node in chkDriver:
                        if mc.attributeQuery('nodeType', n=node, ex=True):
                            if mc.getAttr(node+'.nodeType') == 'control':
                                if mc.getAttr(node+'.mirrorSide', asString=True) in ['none', 'left', 'middle']:
                                    driver = node
                                    driverM = getCtrlMirror(driver)
                                    if not driverM:
                                        driverM = driver
                                    if not driver in dicParentSlice.keys():
                                        dicParentSlice[driver] = {}
                                    if not driverM in dicParentSlice.keys():
                                        dicParentSlice[driverM] = {}
                                    if not driven in dicParentSlice[driver].keys():
                                        dicParentSlice[driver][driven] = []
                                    if not drivenM in dicParentSlice[driverM].keys():
                                        dicParentSlice[driverM][drivenM] = []
                                    for chan in mc.getAttr(tpl+'.zoneParentDriverChans['+str(id)+']').split(','):
                                        if chan:
                                            if not chan in dicParentSlice[driver][driven]:
                                                dicParentSlice[driver][driven].append(chan)
                                            if not chan in dicParentSlice[driverM][drivenM]:
                                                dicParentSlice[driverM][drivenM].append(chan)

        for driver in dicParentSlice.keys():
            for driven in dicParentSlice[driver].keys():
                for chan in dicParentSlice[driver][driven]:
                    #print driver, driven, chan#, dicDKeys.keys()
                    if driven in dicDKeys.keys():
                        if chan in dicDKeys[driven].keys():
                            lDkeys = dicDKeys[driven][chan]
                            attrFollow = driver[len(driver.split('_')[0])+1 :]+'Follow'
                            if not mc.attributeQuery(attrFollow, n=driven, ex=True):
                                mc.addAttr(driven, ln=attrFollow, at='float', min=0.0, max=10.0, k=True, dv=10.0)
                            #else:
                                #lToDel = mc.listConnections(driven+'.'+attrFollow) or []
                                #if lToDel:
                                    #mc.delete(lToDel)

                            nADL = 'aDL_'+driven[len(driven.split('_')[0])+1 :]+'_'+attrFollow+chan
                            nMDL = 'mDL_'+driven[len(driven.split('_')[0])+1 :]+'_'+attrFollow+chan
                            nDiv = 'div_'+driven[len(driven.split('_')[0])+1 :]+'_'+attrFollow+chan

                            aDL = nADL
                            mDL = nMDL
                            div = nDiv
                            if not mc.objExists(nADL):
                                aDL = mc.createNode('addDoubleLinear', n=nADL)
                            if not mc.objExists(nMDL):
                                mDL = mc.createNode('multDoubleLinear', n=nMDL)
                            if not mc.objExists(nDiv):
                                div = mc.createNode('multDoubleLinear', n=nDiv)

                            mc.setAttr(div+'.input2', .1)
                            if not mc.isConnected(driven+'.'+chan, aDL+'.input1', iuc=True):
                                mc.connectAttr(driven+'.'+chan, aDL+'.input1', f=True)
                            if not mc.isConnected(driven+'.'+attrFollow, div+'.input1', iuc=True):
                                mc.connectAttr(driven+'.'+attrFollow, div+'.input1', f=True)
                            if not mc.isConnected(div+'.output', mDL+'.input1', iuc=True):
                                mc.connectAttr(div+'.output', mDL+'.input1', f=True)
                            if not mc.isConnected(driver+'.'+chan, mDL+'.input2', iuc=True):
                                mc.connectAttr(driver+'.'+chan, mDL+'.input2', f=True)
                            if not mc.isConnected(mDL+'.output', aDL+'.input2', iuc=True):
                                mc.connectAttr(mDL+'.output', aDL+'.input2', f=True)


                            for dKey in lDkeys:
                                if chan.startswith('scale'):
                                    #print dKey, driver, driven, chan
                                    nSub = 'sub_'+driven[len(driven.split('_')[0])+1 :]+'_'+attrFollow+chan
                                    nMltSub = 'nrm_'+driven[len(driven.split('_')[0])+1 :]+'_'+attrFollow+chan
                                    sub = nSub
                                    mltSub = nMltSub
                                    if not mc.objExists(nSub):
                                        sub = mc.createNode('addDoubleLinear', n=nSub)
                                    if not mc.objExists(nMltSub):
                                        mltSub = mc.createNode('multDoubleLinear', n=nMltSub)
                                    mc.setAttr(mltSub+'.input2', -1)
                                    if not mc.isConnected(aDL+'.output', sub+'.input1', iuc=True):
                                        mc.connectAttr(aDL+'.output', sub+'.input1', f=True)
                                    if not mc.isConnected(div+'.output', mltSub+'.input1', iuc=True):
                                        mc.connectAttr(div+'.output', mltSub+'.input1', f=True)
                                    if not mc.isConnected(mltSub+'.output', sub+'.input2', iuc=True):
                                        mc.connectAttr(mltSub+'.output', sub+'.input2', f=True)
                                    if not mc.isConnected(sub+'.output', dKey+'.input', iuc=True):
                                        mc.connectAttr(sub+'.output', dKey+'.input', f=True)


                                else:
                                    nodeConn = mc.listConnections(dKey+'.input', s=True)[0]
                                    if mc.attributeQuery('nodeType', n=nodeConn, ex=True):
                                        if mc.getAttr(nodeConn+'.nodeType') == 'control':
                                            if not mc.isConnected(aDL+'.output', dKey+'.input', iuc=True):
                                                mc.connectAttr(aDL+'.output', dKey+'.input', f=True)

                                    else:
                                        if not mc.isConnected(aDL+'.output', dKey+'.input', iuc=True):
                                            mc.connectAttr(aDL+'.output', dKey+'.input', f=True)
                                        if not mc.isConnected(nodeConn+'.output', aDL+'.input1', iuc=True):
                                            mc.connectAttr(nodeConn+'.output', aDL+'.input1', f=True)

                    else:
                        print 'HERRE  to slice divere that have no targ (eyebrows_L/ eyelidsYp_L) 7040'
#connectFatherSlicesCtrl()


def connectAdds():
    lTrgt = mc.ls('*.adds', o=True, r=True)
    if lTrgt:
        for trgt in lTrgt:
            if mc.attributeQuery('extractedAs', n=trgt, ex=True):
                if not mc.attributeQuery('isInBet', n=trgt, ex=True):
                    lAdds = mc.getAttr(trgt + '.adds', mi=True) or []
                    if lAdds:
                        for id in lAdds:
                            chkConn = mc.listConnections(trgt + '.adds[' + str(id) + ']', s=True) or []
                            if chkConn:
                                add = chkConn[0]
                                #print 'ADD :', add
                                lConn = mc.listConnections(mc.listRelatives(add, s=True, ni=True)[-1], d=True) or []
                                if lConn:
                                    #print 'CONN ADD FOUNDED', lConn
                                    bsToKill = mc.ls(lConn, type='blendShape') or []
                                    #print bsToKill
                                    if bsToKill:
                                        #print 'bsToKill :', bsToKill
                                        mc.delete(bsToKill)

        for trgt in lTrgt:
            if mc.attributeQuery('extractedAs', n=trgt, ex=True):
                if not mc.attributeQuery('isInBet', n=trgt, ex=True):
                    #shp = mc.listRelatives(trgt, s=True, ni=True)[0]
                    hist = mc.listHistory(trgt, f=True, lv=1)
                    #print 'CHK ADDS :', trgt, mc.ls(mc.listHistory(trgt, f=True, lv=1), type='blendShape')
                    bsTrgt = mc.ls(mc.listHistory(trgt, f=True, lv=1), type='blendShape')[0]
                    dicTrgtIdsSrc = genDicTrgtIds(bsTrgt)
                    trgtId = int(dicTrgtIdsSrc[trgt]['index'])
                    lAdds = mc.getAttr(trgt+'.adds', mi=True) or []
                    if lAdds:
                        for id in lAdds:
                            chkConn = mc.listConnections(trgt+'.adds['+str(id)+']', s=True) or []
                            if chkConn:
                                add = chkConn[0]
                                mshAdd = ''
                                if mc.attributeQuery('neutrale', n=add, ex=True):
                                    mshAdd = mc.getAttr(add+'.neutral').replace('result_', 'MOD:msh_')#a blinder pour des updates de shapes dans des derive (papaSmurf)
                                    if not mc.objExists(mshAdd):
                                        mshAdd = mc.getAttr(add + '.neutral').replace('result_', 'msh_')  # a blinder pour des updates de shapes dans des derive (papaSmurf)
                                        if not mc.objExists(mshAdd):
                                            mc.duplicate('NTL:'+mc.getAttr(add + '.neutral'), n=mshAdd)
                                        try:
                                            mc.parent(mshAdd, world=True)
                                        except:
                                            pass
                                elif mc.attributeQuery('mshOrig', n=add, ex=True):
                                    mshAdd = mc.getAttr(add+'.mshOrig').replace('result_', 'MOD:msh_')#a blinder pour des updates de shapes dans des derive (papaSmurf)
                                    if not mc.objExists(mshAdd):
                                        mshAdd = mc.getAttr(add + '.mshOrig').replace('result_', 'msh_')  # a blinder pour des updates de shapes dans des derive (papaSmurf)
                                        if not mc.objExists(mshAdd):
                                            mc.duplicate('NTL:'+mc.getAttr(add + '.mshOrig'), n=mshAdd)
                                        try:
                                            mc.parent(mshAdd, world=True)
                                        except:
                                            pass
                                #print mshAdd
                                shp = mc.listRelatives(mshAdd, s=True, ni=True)[-1]
                                suce = mc.findDeformers(shp)
                                bsAdd = mc.ls(suce, type='blendShape') or []
                                if not bsAdd:
                                    bsAdd = mc.blendShape(mshAdd, n='bs'+mshAdd[len(mshAdd.split('_')[0]):])[0]
                                    #print 'bsAdd generated :', bsAdd
                                else:
                                    bsAdd = bsAdd[0]
                                    #print 'bsAdd founded :', bsAdd
                                #bsAdd = mc.blendShape(mshAdd, n='bs'+mshAdd[len(mshAdd.split('_')[0]):])[0]
                                chkTrgt = mc.blendShape(bsAdd, q=True, t=True) or []
                                if not add.split(':')[-1] in chkTrgt:
                                    mc.blendShape(bsAdd, edit=True, t=(mshAdd, trgtId, add, 1.0))

                                #print 'ICI?, 6673)'
                                dicTrgtIdsDest = genDicTrgtIds(bsAdd)
                                mc.connectAttr(bsTrgt+'.'+dicTrgtIdsSrc[trgt]['attr'], bsAdd+'.'+dicTrgtIdsDest[add]['attr'], f=True)
                                if mc.attributeQuery('inBets', n=add, ex=True):
                                    dicDatas = getTrgtMshDatas(add)
                                    lInBets = mc.getAttr(add+'.inBets', mi=True) or []
                                    if lInBets:
                                        for i in lInBets:
                                            inBet = mc.listConnections(add+'.inBets['+str(i)+']', s=True)[0]
                                            input = int(dicDatas[add]['id'])
                                            weight = int(mc.getAttr(inBet+'.weightId'))
                                            value = (weight-5000.0)/1000
                                            mc.blendShape(bsAdd, e=True, ib=True, t=(mshAdd, input, inBet, value))

#connectAdds()


def connectAdds_v2():
    lTrgt = mc.ls('*.adds', o=True, r=True)
    if lTrgt:
        for trgt in lTrgt:
            print 'trgtAdd :', trgt
            add = mc.listConnections(trgt + '.adds[' + str(id) + ']', s=True)[0]
            mshAdd = ''
            if mc.attributeQuery('neutrale', n=add, ex=True):
                mshAdd = mc.getAttr(add + '.neutral').replace('result_', 'MOD:msh_')  # a blinder pour des updates de shapes dans des derive (papaSmurf)
            elif mc.attributeQuery('mshOrig', n=add, ex=True):
                mshAdd = mc.getAttr(add + '.mshOrig').replace('result_', 'MOD:msh_')  # a blinder pour des updates de shapes dans des derive (papaSmurf)
            shp = mc.listRelatives(mshAdd, s=True, ni=True)[-1]
            suce = mc.findDeformers(shp)
            bsAdd = mc.ls(suce, type='blendShape') or []
            if bsAdd:
                mc.delete(bsAdd)
        for trgt in lTrgt:
            if not mc.attributeQuery('isInBet', n=trgt, ex=True):
                #shp = mc.listRelatives(trgt, s=True, ni=True)[0]
                bsTrgt = mc.ls(mc.listHistory(trgt, f=True, lv=1), type='blendShape')[0]
                dicTrgtIdsSrc = genDicTrgtIds(bsTrgt)
                trgtId = int(dicTrgtIdsSrc[trgt]['index'])
                lAdds = mc.getAttr(trgt+'.adds', mi=True) or []
                if lAdds:
                    for id in lAdds:
                        add = mc.listConnections(trgt+'.adds['+str(id)+']', s=True)[0]
                        mshAdd = ''
                        if mc.attributeQuery('neutrale', n=add, ex=True):
                            mshAdd = mc.getAttr(add+'.neutral').replace('result_', 'MOD:msh_')#a blinder pour des updates de shapes dans des derive (papaSmurf)
                        elif  mc.attributeQuery('mshOrig', n=add, ex=True):
                            mshAdd = mc.getAttr(add+'.mshOrig').replace('result_', 'MOD:msh_')#a blinder pour des updates de shapes dans des derive (papaSmurf)
                        shp = mc.listRelatives(mshAdd, s=True, ni=True)[-1]
                        suce = mc.findDeformers(shp)
                        bsAdd = mc.ls(suce, type='blendShape') or []
                        #if not bsAdd:
                            #bsAdd = mc.blendShape(mshAdd, n='bs'+mshAdd[len(mshAdd.split('_')[0]):])[0]
                        #else:
                            #bsAdd = bsAdd[0]
                        #if bsAdd:
                            #mc.delete(bsAdd)
                        bsAdd = mc.blendShape(mshAdd, n='bs'+mshAdd[len(mshAdd.split('_')[0]):])[0]

                        chkTrgt = mc.blendShape(bsAdd, q=True, t=True) or []
                        if not add.split(':')[-1] in chkTrgt:
                            mc.blendShape(bsAdd, edit=True, t=(mshAdd, trgtId, add, 1.0))

                        dicTrgtIdsDest = genDicTrgtIds(bsAdd)
                        mc.connectAttr(bsTrgt+'.'+dicTrgtIdsSrc[trgt]['attr'], bsAdd+'.'+dicTrgtIdsDest[add]['attr'], f=True)
                        if mc.attributeQuery('inBets', n=add, ex=True):
                            dicDatas = getTrgtMshDatas(add)
                            lInBets = mc.getAttr(add+'.inBets', mi=True) or []
                            if lInBets:
                                for i in lInBets:
                                    inBet = mc.listConnections(add+'.inBets['+str(i)+']', s=True)[0]
                                    input = int(dicDatas[add]['id'])
                                    weight = int(mc.getAttr(inBet+'.weightId'))
                                    value = (weight-5000.0)/1000
                                    mc.blendShape(bsAdd, e=True, ib=True, t=(mshAdd, input, inBet, value))

#connectAdds_v2()

def connectFaceRig_v2(mshDest):
    dicNeutGeoVtx = {}
    roof = 0.0
    dicZones = {}
    dicSym = {}
    verbose = None
    lShp = mc.ls('*.extractedAs',r=True, o=True) or []
    if lShp:
        #get blendShape
        shpDest = mc.listRelatives(mshDest, s=True, ni=True)[0]
        lDef = mc.findDeformers(shpDest) or []
        bs = ''
        nBs = 'bs'+mshDest[len(mshDest.split('_')[0]):]
        if lDef:
            chkBs = mc.ls(lDef, type='blendShape') or []
            if chkBs:
                bs = chkBs[0]
            else:
                bs = mc.blendShape(mshDest, n=nBs)[0]
        else:
             bs = mc.blendShape(mshDest, n=nBs)[0]
        activeDef(mc.listRelatives(mshDest, s=True, ni=True)[0], False)
        for sculpt in lShp:
            if mc.getAttr(sculpt+'.extractedAs') == 'TRGT':
                if not mc.attributeQuery('isInBet', n=sculpt, ex=True):
                    if mc.attributeQuery('ctrlChan', n=sculpt, ex=True) and mc.getAttr(sculpt+'.ctrlChan') != '//':
                        activeDef(mc.listRelatives(sculpt, s=True, ni=True)[0], False)
                        sculptOrig = mc.listRelatives(sculpt, s=True, ni=False)[-1]
                        if mc.polyCompare(sculptOrig, mshDest, fd=True, v=False) in [0, 8, 16, 24]:
                            if mc.attributeQuery('sepZone', n=sculpt, ex=True):
                                zone = mc.getAttr(sculpt+'.sepZone', asString=True)
                                if not zone in dicZones.keys():
                                    dicZones[zone] = {}
                                    cg = 'cg_'+zone
                                    if mc.objExists(cg):
                                        lCtrl = mc.listConnections(cg+'.members', s=True, d=False)
                                        for ctrl in lCtrl:
                                            if mc.attributeQuery('ctrlZone', n=ctrl, ex=True):
                                                side = mc.getAttr(ctrl+'.mirrorSide', asString=True)
                                                if not side in dicZones[zone].keys():
                                                    dicZones[zone][side] = {}
                                                if not ctrl in dicZones[zone][side].keys():
                                                    dicZones[zone][side][ctrl] = []
                                endName = sculpt.split('_')[-1][: 1]
                                side = 'middle'
                                if endName == ('L'):
                                    side = 'left'
                                elif endName == ('R'):
                                    side = 'right'
                                toFind = ''
                                if mc.attributeQuery('sepSlice', n=sculpt, ex=True):
                                    iter = mc.getAttr(sculpt+'.sepSlice', s=True)
                                    for i in range(0, iter):
                                        slice = mc.getAttr(sculpt+'.sepSlice['+str(i)+']')
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
                                        elif slice == 'Corn':
                                            toFind+='Corner'
                                for driver in dicZones[zone][side].keys():
                                    ctrlPole = driver.split(zone)[-1].split('_')[0]
                                    if toFind == ctrlPole:
                                        if not sculpt in dicZones[zone][side][driver]:
                                            dicZones[zone][side][driver].append(sculpt)
                            chkConnTrgt = mc.blendShape(bs, q=True, t=True) or []
                            if not chkConnTrgt:
                                mc.blendShape(bs, edit=True, t=(mshDest, 0, sculpt, 1.0))
                            else:
                                if not sculpt in mc.blendShape(bs, q=True, t=True):
                                    id = getAttrIds(bs, 'weight')[-1]+1
                                    mc.blendShape(bs, edit=True, t=(mshDest, id, sculpt, 1.0))
                    activeDef(mc.listRelatives(sculpt, s=True, ni=True)[0], True)
        activeDef(mc.listRelatives(mshDest, s=True, ni=True)[0], True)
        posBase = mc.xform(mshDest, q=True, ws=True, t=True)
        vtxs = mc.polyEvaluate(mshDest, v=True)

        #get neutralGeo transform position
        posSrc = posBase
        for vtx in range(0, vtxs):
            posVtx = mc.xform(mshDest+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
            dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]

        #init sym dic
        if not mc.attributeQuery('symTabLeft', n=mshDest, ex=True):
            crtSymAttr([mshDest])
        iter = mc.getAttr(mshDest+'.symTabLeft', s=True)
        for i in range(0, iter):
            dicSym[mc.getAttr(mshDest+'.symTabLeft['+str(i)+']')] = mc.getAttr(mshDest+'.symTabRight['+str(i)+']')
        for zone in dicZones.keys():
            for side in dicZones[zone].keys():
                for driver in dicZones[zone][side].keys():
                    for shp in dicZones[zone][side][driver]:
                        chan = mc.getAttr(shp+'.ctrlChan')
                        if chan != '//':
                            driverDefaultVal = 0
                            limChan = ''
                            driverVal = 1
                            drivenVal = 2
                            sign = 1
                            maxCtrlVal = 45
                            if mc.getAttr(shp+'.negativeChan') == 1:
                                sign = -1
                            if 'translate' in chan:
                                tpl = mc.listConnections(driver+'.ctrlZone', s=True)[0]
                                #vtx = int(mc.getAttr(tpl+'.vtxId'))
                                drivenVal = mc.getAttr(shp+'.ratio')
                                limChan = 'Trans'+chan[-1]+'Limit'
                                maxCtrlVal = mc.getAttr(shp+'.vtxRoof') * 1.5
                                if mc.getAttr(tpl+'.mirrorType') == 4:
                                    if side == 'right':
                                        if chan.endswith('Z'):
                                            sign = sign*-1
                                #for lips
                                elif mc.getAttr(tpl+'.mirrorType') == 0:
                                    if side == 'right':
                                        if chan.endswith('X'):
                                            sign = sign*-1

                            elif 'rotate' in chan:
                                limChan = 'Rot'+chan[-1]+'Limit'
                                if 'Down' in driver:
                                    if chan.endswith('X'):
                                        sign = sign*-1
                                driverVal = 45

                            elif 'scale' in chan:
                                limChan = 'Scale'+chan[-1]+'Limit'
                                driverVal = 3
                                maxCtrlVal = driverVal
                                driverDefaultVal = 1

                            if mc.attributeQuery(shp.split(':')[-1], n=bs, ex=True):
                                chkDKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True, d=False) or []
                                mc.delete(chkDKey)

                            mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=driverDefaultVal, v=0)
                            mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=driverVal*sign, v=drivenVal)
                            dKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True, d=False)[0]

                            if dKey:
                                if not mc.attributeQuery('driverChan', n=dKey, ex=True):
                                    mc.addAttr(dKey, ln='driverChan', dt='string')
                                mc.setAttr(dKey+'.driverChan', driver+'.'+chan, type='string')
                                if sign>0 :
                                    mc.setAttr(dKey+'.postInfinity', 4)
                                    #mc.setAttr(ctrl+'.max'+limChan+'Enable', 1)
                                    mc.setAttr(ctrl+'.max'+limChan, maxCtrlVal)
                                elif sign<0:
                                    mc.setAttr(dKey+'.preInfinity', 4)
                                    #mc.setAttr(ctrl+'.min'+limChan+'Enable', 1)
                                    mc.setAttr(ctrl+'.min'+limChan, maxCtrlVal*-1)
                            if mc.attributeQuery('inBets', n=shp, ex=True):
                                dicDatas = getTrgtMshDatas(shp)
                                lIds = mc.getAttr(shp+'.inBets', mi=True) or []
                                if lIds:
                                    for i in lIds:
                                        inBet = mc.listConnections(shp+'.inBets['+str(i)+']', s=True)[0]
                                        input = int(dicDatas[shp]['id'])
                                        weight = int(mc.getAttr(inBet+'.weightId'))
                                        value = (weight-5000.0)/1000
                                        #print 'HERE :', geoDef, input, inBet, value
                                        if inBet in mc.blendShape(bs, q=True, t=True):
                                            mc.blendShape(bs, e=True, rm=True, t=(mshDest, input, inBet, value))
                                        mc.blendShape(bs, e=True, ib=True, t=(mshDest, input, inBet, value))

        connectShapesRig('COR', bs)
        connectAdds()
        #connectFatherSlicesCtrl()
    #print 'ZIZILOL'

"""
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
"""
#connectFaceRig_v2()


def connectFaceRig_v3(getSel, conCor, conAdds, conSliceFather, conMix, *args, **kwargs):
    mshDest = ''
    if isinstance(getSel, list):
        mshDest = getSel[0]
    else:
        mshDest = getSel()[0]
    dicNeutGeoVtx = {}
    roof = 0.0
    dicZones = {}
    dicSym = {}
    verbose = None
    lShp = mc.ls('*.extractedAs',r=True, o=True) or []
    if lShp:
        #get blendShape
        shpDest = mc.listRelatives(mshDest, s=True, ni=True)[0]
        lDef = mc.findDeformers(shpDest) or []
        bs = ''
        nBs = 'bs'+mshDest[len(mshDest.split('_')[0]):]
        if lDef:
            chkBs = mc.ls(lDef, type='blendShape') or []
            if chkBs:
                #bs = chkBs[0]
                mc.delete(chkBs[0])
            #else:
            #bs = mc.blendShape(mshDest, n=nBs)[0]
        #else:
        bs = mc.blendShape(mshDest, n=nBs)[0]

        #try:
        bsTypeAttrr(bs, 4)
        #except:
            #pass
        activeDef(mc.listRelatives(mshDest, s=True, ni=True)[0], False)
        for sculpt in lShp:
            if mc.getAttr(sculpt+'.extractedAs') == 'TRGT':
                if not mc.attributeQuery('isInBet', n=sculpt, ex=True):
                    if mc.attributeQuery('ctrlChan', n=sculpt, ex=True) and mc.getAttr(sculpt+'.ctrlChan') != '//':
                        activeDef(mc.listRelatives(sculpt, s=True, ni=True)[0], False)
                        sculptOrig = mc.listRelatives(sculpt, s=True, ni=False)[-1]
                        if mc.polyCompare(sculptOrig, mshDest, fd=True, v=False) in [0, 8, 16, 24]:
                            if mc.attributeQuery('sepZone', n=sculpt, ex=True):
                                zone = mc.getAttr(sculpt+'.sepZone', asString=True)
                                if not zone in dicZones.keys():
                                    dicZones[zone] = {}
                                    cg = 'cg_'+zone
                                    if mc.objExists(cg):
                                        lCtrl = mc.listConnections(cg+'.members', s=True, d=False)
                                        for ctrl in lCtrl:
                                            if mc.attributeQuery('ctrlZone', n=ctrl, ex=True):
                                                side = mc.getAttr(ctrl+'.mirrorSide', asString=True)
                                                if not side in dicZones[zone].keys():
                                                    dicZones[zone][side] = {}
                                                if not ctrl in dicZones[zone][side].keys():
                                                    dicZones[zone][side][ctrl] = []
                                endName = sculpt.split('_')[-1][: 1]
                                side = 'middle'
                                if endName == ('L'):
                                    side = 'left'
                                elif endName == ('R'):
                                    side = 'right'
                                toFind = ''
                                if mc.attributeQuery('sepSlice', n=sculpt, ex=True):
                                    iter = mc.getAttr(sculpt+'.sepSlice', s=True)
                                    for i in range(0, iter):
                                        slice = mc.getAttr(sculpt+'.sepSlice['+str(i)+']')
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
                                        elif slice == 'Corn':
                                            toFind+='Corner'
                                #print sculpt, zone, endName, side
                                for driver in dicZones[zone][side].keys():
                                    ctrlPole = driver.split(zone)[-1].split('_')[0]
                                    if toFind == ctrlPole:
                                        if not sculpt in dicZones[zone][side][driver]:
                                            dicZones[zone][side][driver].append(sculpt)
                            chkConnTrgt = mc.blendShape(bs, q=True, t=True) or []
                            if not chkConnTrgt:
                                mc.blendShape(bs, edit=True, t=(mshDest, 0, sculpt, 1.0))
                            else:
                                #if not sculpt.split(':')[-1] in mc.blendShape(bs, q=True, t=True):  OLD smurf
                                if not sculpt in mc.blendShape(bs, q=True, t=True):
                                    id = getAttrIds(bs, 'weight')[-1]+1
                                    mc.blendShape(bs, edit=True, t=(mshDest, id, sculpt, 1.0))
                        else:
                            print '#####################################'
                            mc.warning(sculpt+' does not correspond to '+mshDest)
                            print '#####################################'
                    activeDef(mc.listRelatives(sculpt, s=True, ni=True)[0], True)
        activeDef(mc.listRelatives(mshDest, s=True, ni=True)[0], True)
        posBase = mc.xform(mshDest, q=True, ws=True, t=True)
        vtxs = mc.polyEvaluate(mshDest, v=True)

        #get neutralGeo transform position
        posSrc = posBase
        for vtx in range(0, vtxs):
            posVtx = mc.xform(mshDest+'.vtx['+str(vtx)+']', q=True, ws=True, t=True)
            dicNeutGeoVtx[vtx] = [posVtx[0]-posSrc[0], posVtx[1]-posSrc[1], posVtx[2]-posSrc[2]]

        #init sym dic
        if not mc.attributeQuery('symTabLeft', n=mshDest, ex=True):
            crtSymAttr([mshDest])
        iter = mc.getAttr(mshDest+'.symTabLeft', s=True)
        for i in range(0, iter):
            dicSym[mc.getAttr(mshDest+'.symTabLeft['+str(i)+']')] = mc.getAttr(mshDest+'.symTabRight['+str(i)+']')
        for zone in dicZones.keys():
            for side in dicZones[zone].keys():
                for driver in dicZones[zone][side].keys():
                    for shp in dicZones[zone][side][driver]:
                        if mc.attributeQuery(shp.split(':')[-1], n=bs, ex=True):
                            chkDKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True, d=False) or []
                            if chkDKey:
                                mc.delete(chkDKey)
                        chan = mc.getAttr(shp+'.ctrlChan')
                        #if chan != '//' or chan != '':
                        if chan in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                            driverDefaultVal = 0
                            limChan = ''
                            driverVal = 1
                            drivenVal = 2
                            sign = 1
                            maxCtrlVal = 45
                            if mc.getAttr(shp+'.negativeChan') == 1:
                                sign = -1
                            if 'translate' in chan:
                                tpl = mc.listConnections(driver+'.ctrlZone', s=True)[0]
                                #vtx = int(mc.getAttr(tpl+'.vtxId'))
                                drivenVal = mc.getAttr(shp+'.ratio')
                                limChan = 'Trans'+chan[-1]+'Limit'
                                maxCtrlVal = mc.getAttr(shp+'.vtxRoof') * 1.5
                                if mc.getAttr(tpl+'.mirrorType') == 4:
                                    if side == 'right':
                                        if chan.endswith('Z'):
                                            sign = sign*-1
                                #for lips
                                #elif mc.getAttr(tpl+'.mirrorType') == 0:
                                    #if side == 'right':
                                        #if chan.endswith('X'):
                                            #sign = sign*-1

                            elif 'rotate' in chan:
                                limChan = 'Rot'+chan[-1]+'Limit'
                                if 'Down' in driver:
                                    if chan.endswith('X'):
                                        sign = sign*-1
                                #for lips
                                if mc.getAttr(tpl+'.mirrorType') == 0:
                                    if chan.endswith('Z'):
                                        if side in ['left', 'right']:
                                            sign = sign*-1
                                driverVal = 45

                            elif 'scale' in chan:
                                limChan = 'Scale'+chan[-1]+'Limit'
                                driverVal = 3
                                maxCtrlVal = driverVal
                                driverDefaultVal = 1

                            #print bs+'.'+shp.split(':')[-1], driver, chan, driverDefaultVal
                            mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=driverDefaultVal, v=0)
                            mc.setDrivenKeyframe(bs+'.'+shp.split(':')[-1], cd=driver+'.'+chan, itt='linear', ott='linear', dv=driverVal*sign, v=drivenVal)
                            dKey = mc.listConnections(bs+'.'+shp.split(':')[-1], s=True, d=False) or []

                            if dKey:
                                if not mc.attributeQuery('driverChan', n=dKey[0], ex=True):
                                    mc.addAttr(dKey[0], ln='driverChan', dt='string')
                                mc.setAttr(dKey[0]+'.driverChan', driver+'.'+chan, type='string')
                                if sign > 0:
                                    mc.setAttr(dKey[0]+'.postInfinity', 4)
                                    #mc.setAttr(ctrl+'.max'+limChan+'Enable', 1)
                                    mc.setAttr(ctrl+'.max'+limChan, maxCtrlVal)
                                elif sign<0:
                                    mc.setAttr(dKey[0]+'.preInfinity', 4)
                                    #mc.setAttr(ctrl+'.min'+limChan+'Enable', 1)
                                    mc.setAttr(ctrl+'.min'+limChan, maxCtrlVal*-1)
                            if mc.attributeQuery('inBets', n=shp, ex=True):
                                dicDatas = getTrgtMshDatas(shp)
                                lIds = mc.getAttr(shp+'.inBets', mi=True) or []
                                if lIds:
                                    for i in lIds:
                                        inBet = mc.listConnections(shp+'.inBets['+str(i)+']', s=True)[0]
                                        input = int(dicDatas[shp]['id'])
                                        weight = int(mc.getAttr(inBet+'.weightId'))
                                        value = (weight-5000.0)/1000
                                        #print 'HERE :', geoDef, input, inBet, value
                                        if inBet in mc.blendShape(bs, q=True, t=True):
                                            mc.blendShape(bs, e=True, rm=True, t=(mshDest, input, inBet, value))
                                        mc.blendShape(bs, e=True, ib=True, t=(mshDest, input, inBet, value))

        if conCor == True:
            print 'connecting COR'
            connectShapesRig('COR', bs)
        if conAdds == True:
            print 'connecting ADDS'
            connectAdds()
        if conSliceFather == True:
            print 'connecting SLICE FATHER'
            connectFatherSlicesCtrl()
        if conMix == True:
            print 'connecting MIX'
            connectShapesRig('MIX', bs)



def getMixRigTmp(getSel, *args, **kwargs):
    msh = ''
    if isinstance(getSel, list):
        msh = getSel[0]
    else:
        msh = getSel()[0]
    bs = mc.listHistory



##UI#####################################################################################################################################################################
def compEditor_ui(*args, **kwargs):
    import maya.mel
    maya.mel.eval('componentEditorWindow()')



def smfaddTarget_ui(lNeutral, *args, **kwargs):
    version = os.getenv('REZ_ELLIPSE_RIG_VERSION')
    if version == None:
        version = '__HP__'
    nWin = 'SMF_addTrgtS'
    nPan = 'MASTER_panFaceAddTrgt'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_publishTool_UI = mc.window(nWin, t='facialShapes'+version)

    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout('GENERATE_SCENE', adj=True, w=225)

    mc.rowLayout(nc=2, adj=2)
    nTrgtType = mc.optionMenu('trgtTypes', label='Prefix         :')
    #dicTrgt = trgtNames()
    faceDatas = faceDescription()
    dicTrgt = faceDatas.trgtNames()
    for key in sorted(dicTrgt.keys()):
        #mc.menuItem( label=key+'   :  '+dicTrgt[key]+'_')
        mc.menuItem(label=dicTrgt[key] +':  (' + key+')')

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
    mc.button(label='add', c=partial(addTrgt, listSel, "c_targets"))

    mc.showWindow(winSMF_publishTool_UI)
#smfaddTarget_ui()

def getSepType(trigger, *args, **kwargs):
    val = mc.optionMenu(trigger, q=True, v=True)
    return [val]

def smfBlendShapesTool_ui():
    nWin = 'UI_facialTool'
    nPan = 'MASTER_panFaceTool'
    version ='1.3'
    nProjectMenu = 'FACIALSCULPT_projectMenuName'
    nLoadModBtn = 'mod_loadBtn'
    nGenTrgtBtn = 'trgt_genBtn'
    nLoadTplBtn = 'trgt_loadTplBtn'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_facialTool_UI = mc.window(nWin, t='facial tools'+version)

    mBar = mc.menuBarLayout('facialTool_mBar')
    mc.menu(l='File', to=True)
    mc.menuItem(divider=True, dividerLabel='File')
    mc.menuItem(l='save new rev', c=partial(scene_manager.saveNewRev, project_manager.getProject()))
    mc.menuItem(l='reload current', c=partial(debbug.reopenCurrentScene))
    mc.menuItem(divider=True, dividerLabel='Scene')
    mc.menuItem(l='refesh scene', c=partial(refreshScn))
    mc.menuItem(l='clean BS', c=partial(cleanBs))
    mc.menuItem(l='dag menu', c=partial(launchDagHack))


    mc.setParent('..')
    mc.menu(l='Inits', to=True)
    mc.menuItem(divider=True, dividerLabel='Sculpt')
    mc.menuItem(l='gen neutral', c=partial(generateNeutral, listSel))
    mc.menuItem(l='gen zone sculpt', c=partial(linkTargets_v2, "c_targets", listSel))
    mc.menuItem(divider=True, dividerLabel='Sym')
    mc.menuItem(l='crt symTab', c=partial(crtSymAttr, listSel))
    mc.menuItem(l='copy symTab to', c=partial(copySymTabTo, listSel))
    mc.menuItem(l='Check Sym', c=partial(chkSym, listSel))
    mc.menuItem(divider=True, dividerLabel='Rig')
    mc.menuItem(l='import face tpl', c=partial(import_face_template))
    mc.menuItem(l='build face tpl', c=partial(buildTpl))


    mc.setParent('..')
    mc.menu(l='Tools', to=True)
    mc.menuItem(divider=True, dividerLabel='Utils')
    mc.menuItem(l='comp editor', c=partial(compEditor_ui))
    mc.menuItem(l='display handles', c=partial(displayHandles, listSel))



    mc.setParent('..')
    mc.menu(l='Dev', to=True)
    mc.menuItem(l='normalize sep sel', c='tools_facialShapes_v3.normalizeSelSep(listSel)')
    mc.menuItem(l='connect mshSrc', c='tools_facialShapes_v3.linkMshSrc(listSel)')
    mc.menuItem(l='ad extractMe', c=partial(addExtractMeAttr, listSel))
    mc.menuItem(l='presset chan drivers', c='tools_facialShapes_v3.resetChans(listSel or [])')
    mc.menuItem(l='connect parent ctrl', c='tools_facialShapes_v3.connectFatherSlicesCtrl()')
    mc.menuItem(l='link resMsh to slices', c='tools_facialShapes_v3.linkSlicesMshOrig(listSel)')
    mc.menuItem(divider=True, dividerLabel='Testes MIX')
    mc.menuItem(l='mix to sep', c=partial(addMixToSlicewght, listSel))
    mc.menuItem(l='remove vtx color', c=partial(clearVtxColor, listSel))
    mc.menuItem(l='extrace mix', c=partial(extractShapes_mixTrgt, listSel))
    mc.menuItem(divider=True, dividerLabel='Testes COMB')
    mc.menuItem(l='gen comb sculpt', c=partial(addMixToSlicewght, listSel))
    mc.menuItem(l='gen comb trgt', c=partial(clearVtxColor, listSel))



    mc.menu(nProjectMenu, label='Project')
    mc.radioMenuItemCollection()
    # setProject(nChecker, nProjectMenu, nProject, prodColor, initBtn, saveBtn, pubBtn, doJsn=True,  *args, **kwargs)
    mc.menuItem('projSet_Smurf04', label='Smurf04', radioButton=False, c=partial(project_manager.setProject, nWin, nProjectMenu, 'Smurf04', [0.6, 0.75, 0.9], nGenTrgtBtn,
                          nGenTrgtBtn, nLoadTplBtn, 'FACE'))
    mc.menuItem('projSet_Belfort', label='Belfort', radioButton=False, c=partial(project_manager.setProject, nWin, nProjectMenu, 'Belfort', [0.6, 0.75, 0.9], nGenTrgtBtn,
                          nGenTrgtBtn, nLoadTplBtn, 'FACE'))
    mc.menuItem('projSet_Marsu', label='Marsu', radioButton=False, c=partial(project_manager.setProject, nWin, nProjectMenu, 'Marsu', [0.6, 0.75, 0.9], nGenTrgtBtn,
                          nGenTrgtBtn, nLoadTplBtn, 'FACE'))


    ######
    pan = mc.paneLayout(nPan, cn='single', w=520)
    ######
    mc.tabLayout('MASTER_tab')
    mc.columnLayout('MODELING', adj=True, w=225)
    mc.separator(h=7.5, st='in')


    mc.frameLayout(l='References', cll=True)
    mc.rowLayout(nc=2, adj=2)
    loadModBtn = mc.button(nLoadModBtn, l='LOAD MOD', h=28, w=230, c=partial(loadMOD))
    #loadModBtn = mc.button(nLoadModBtn, l='LOAD MOD    ', bgc=[.25, .2, .5], h=28, w=230, c='tools_facialShapes_v3.loadMOD(r"T:\03_FAB\00_ASSETS\MOD\CHR")')
    #mc.button(l='LOAD FACE TPL', h=28, w=230, c='tools_facialShapes_v3.genSkinMsh(listSel)')
    mc.button(l='UNLOAD MOD', h=28, w=230, c=partial(unloadMOD))

    mc.setParent('..')
    mc.separator(h=10, st='in')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='chan sliders', h=28, w=230, c=partial(tools_facialChanSliders.SMAB_facialSlidersTool_ui))
    mc.button(label='Create new pan', h=28, w=230, c=partial(crtPanel))

    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.paneLayout(nPan, cn='vertical2')
    mc.columnLayout(adj=True, w=300)
    mc.frameLayout(l='Utils', cll=False, bv=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='TRANSFER TO', h=28, w=110, c=partial(snapShp_V2, listSel))
    mc.button(l='RESET', h=28, w=110, c=partial(resetShp, listSel))

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='mirror L to R', h=28, w=110, c=partial(mirrorSculpt, listSel))
    mc.button(l='flip L to R', h=28, w=110, c=partial(flipSculpt, listSel))

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='WRAP ALL TO', h=28, w=110, c=partial(wrapOn, listSel))
    mc.button(l='REMOVE WRAP FROM', h=28, w=110, c=partial(removeWraps, listSel))

    mc.setParent('..')
    mc.button(l='DUPPLCATE SHP', h=28, w=110, c=partial(dupShp, listSel))
    # mc.button('switch_neutralTrgt', l='NEUTRAL/TRGT', h=28, w=110, c=partial(showNeutral()')





    mc.setParent('..')
    mc.button(l='LOAD TARGETS', h=28, w=230, c=partial(loadTrgt, listSel))
    mc.rowLayout(nc=2, adj=1)
    mc.textScrollList('targetsList', numberOfRows=8, ams=True, h=500, w=150, dcc=partial(isolateTrgt))
    mc.popupMenu(b=3, mm=False, aob=True)
    mc.menuItem(l='Isolate trgts', c=partial(isolateTrgt))
    mc.menuItem(l='Select trgts', c=partial(selTrgt))
    mc.menuItem(l='Show all trgts', c=partial(showAllTrgt))
    mc.menuItem(divider=True)
    #mc.menuItem(l='Refresh', c=partial(refreshTrgt))
    mc.menuItem(l='Clear', c='for i in ["targetsList", "targetsChan"]:mc.textScrollList(i, e=True, ra=True)')

    #mc.frameLayout(l='Chans', cll=True)
    mc.textScrollList('targetsChan', numberOfRows=8, ams=True, h=500, w=50)
    mc.popupMenu(b=3, mm=False, aob=True)

    mc.menuItem(l='set chan tX', c=partial(setChannel, "translateX"))
    mc.menuItem(l='set chan tY', c=partial(setChannel, "translateY"))
    mc.menuItem(l='set chan tZ', c=partial(setChannel, "translateZ"))

    mc.menuItem(l='set chan rX', c=partial(setChannel, "rotateX"))
    mc.menuItem(l='set chan rY', c=partial(setChannel, "rotateY"))
    mc.menuItem(l='set chan rZ', c=partial(setChannel, "rotateZ"))

    mc.menuItem(l='set chan sX', c=partial(setChannel, "scaleX"))
    mc.menuItem(l='set chan sY', c=partial(setChannel, "scaleY"))
    mc.menuItem(l='set chan sZ', c=partial(setChannel, "scaleZ"))

    mc.menuItem(divider=True)
    mc.menuItem(l='Invert sign (+/-)', c=partial(invertSign))
    mc.menuItem(l='set no chan', c=partial(setChannel, "None"))
    ##
    #mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout('bsTools', adj=True)
    #mc.button(l='SELECT CTRL', h=28, w=110, c='mc.select("TRGT:c_targets")')

    mc.frameLayout(l='Sculpt Zone Tools', cll=True, bgc=[.2, .5, .5], bv=True)
    mc.columnLayout('bsTools', adj=True, w=225)

    mc.rowLayout(nc=2)
    mc.button(l='ADD TRGT', h=28, w=110, c=partial(smfaddTarget_ui, listSel))
    mc.button(l='ADD INBET', h=28, w=110, c=partial(addInbet_v2, listSel, "TRGT"))


    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='REMOVE TRGT', h=28, w=110, c=partial(removeTrgt, listSel))
    mc.button(l='REMOVE INBET', h=28, w=110, c=partial(removeInbet, listSel))




    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='Skin Corrective Tools', cll=True, bgc=[.2, .4, .3], bv=True)
    mc.rowLayout(nc=2)
    mc.button(l='SET COR POSE', h=28, w=110, c=partial(genCorSculpt, listSel, ''))
    mc.button(l='SET INBET POSE', h=28, w=110, c=partial(addInbet_v2, listSel, "COR"))
    mc.setParent('..')
    mc.button(l='CONNECT COR SCULPT', h=28, w=110, c=partial(connectCorrective, listSel))
    mc.rowLayout(nc=2)
    mc.button(l='REMOVE COR', h=28, w=110, c=partial(removeCor, listSel))
    mc.button(l='REMOVE INBET', h=28, w=110, c=partial(removeCorInbet, listSel))
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='miror cor L to R', h=28, w=110, c=partial(genFlipCor, listSel, "L"))
    mc.button(l='miror cor R to L', h=28, w=110, c=partial(genFlipCor, listSel, "R"))
    #mc.button(l='bake corrective to all', h=28, w=110, c='')


    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='Zones Mix Tools', cll=True, bgc=[.2, .2, .5], bv=True)
    mc.rowLayout(nc=2)
    mc.button(l='gen mix sculpt', h=28, w=110, c=partial(ctrMixCombination_v2, listSel, ''))
    mc.button(l='connect mix shape', h=28, w=110, c=partial(connectMixShp_v3, listSel))
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='mirror mix L-->R', h=28, w=110, c=partial(mirrorMix, listSel, "L"))
    mc.button(l='mirror mix R-->L', h=28, w=110, c=partial(mirrorMix, listSel, "R"))

    #mc.setParent('..')
    #mc.rowLayout(nc=2)
    #mc.button(l='create mix inbet', h=28, w=110, c=partial(addInbet_v2, listSel, "MIX"))
    #mc.button(l='remove mix inbet', h=28, w=110, c='print "to do"')

    #mc.setParent('..')
    #mc.rowLayout(nc=2)
    #mc.button(l='unactive mix', h=28, w=110, c='print "to do"')
    #mc.button(l='active mix', h=28, w=110, c='print "to do"')
    #mc.setParent('..')
    #mc.rowLayout(nc=2)
    #mc.button(l='select mix sculpt', h=28, w=110, c='print "to do"')
    #mc.button(l='select mix trgt', h=28, w=110, c='print "to do"')
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='load mix', h=28, w=110, c=partial(loadMixValues, listSel))
    mc.button(l='remove mix', h=28, w=110, c=partial(removeMix, listSel))
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l='propagate mix to', h=28, w=110, c=partial(propagateMix, listSel))
    ###
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=10, st='in')
    mc.frameLayout(l='rig Tools', cll=True, bgc=[.1, .3, .4], bv=True)
    mc.rowLayout(nc=2)
    mc.button(l='template node', h=28, w=110, c=partial(convertToTemplate, listSel))
    mc.button(l='build rig', h=28, w=110, c=partial(buildTpl))
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='update ctrl', h=28, w=110, c=partial(majPosCtrl, listSel))
    mc.button(l='update tpl', h=28, w=110, c=partial(snapTpl, "cg_face"))




    ###################################################################################################################
    ###################################################################################################################

    mc.columnLayout('SEPARATION', adj=True, w=225, p='MASTER_tab')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='References', cll=True)

    mc.button(l='INIT SEP', h=28, w=110, c=partial(genSepZones, listSel))
    #mc.button(l='connect SEP', h=28, w=110, c=partial(connectSep()')
    mc.button(l='UPDATE AUTO-WEIGHTS', h=28, w=110, c=partial(majSepBaseWght))

    mc.setParent('..')
    mc.separator(h=7.5, st='in')


    mc.frameLayout(l='Sep Tools', cll=True)
    mc.rowLayout(nc=2, adj=1)
    #nTrgtType = mc.optionMenu('sepZone', label='face zone  :')
    #dicTrgt = lib_names.trgtNames()
    #mc.menuItem( label='None')
    #for key in sorted(dicTrgt.keys()):
    #    mc.menuItem(label=key)



    nTrgtType = mc.optionMenu('sepType', label='SLICE TYPE  :')
    mc.menuItem( label='None')
    mc.menuItem( label='Left')
    mc.menuItem( label='Right')
    mc.menuItem( label='Middle')
    mc.menuItem( label='Up')
    mc.menuItem( label='Down')
    mc.menuItem( label='Ext')
    mc.menuItem( label='Int')
    mc.menuItem( label='Corner')

    #mc.button(l='ADD SEP', bgc=[.25,.2,.5], h=28, w=230, c=partial(buildSep, listSel, [mc.optionMenu("sepZone", q=True, v=True)], [mc.optionMenu("sepType", q=True, v=True)])')
    mc.button(l='ADD SLICE', bgc=[.25,.2,.5], h=28, w=230, c=partial(buildSep, listSel, ["None"], ['getType']))
    #mc.button(l='SEL CTRL', bgc=[.25,.2,.5], h=28, w=230, c='mc.select("TRGT:c_targets")')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Weights Tools', cll=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='copy wght to', bgc=[.25,.2,.5], h=28, w=230, c=partial(copyBsWghtTo, listSel))
    mc.button(l='inverse wght to (make negative of)', bgc=[.25,.2,.5], h=28, w=230, c=partial(invertBsWghtTo_v2, listSel))

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    #mc.button(l='BUILD SYM MAP', bgc=[.25,.2,.5], h=28, w=230, c=partial(crtSymAttr(listSel)')
    mc.button(l='self flip wght', bgc=[.25,.2,.5], h=28, w=230, c=partial(flipBsWght, listSel))
    mc.button(l='Normalize wght', bgc=[.25,.2,.5], h=28, w=230, c=partial(normalizeSelSep, listSel))

    #mc.setParent('..')
    #mc.rowLayout(nc=2, adj=1)
    #mc.button(l='ADD WGHT TO', bgc=[.25,.2,.5], h=28, w=230, c=partial(addBsWghtTo(lObj)')
    #mc.button(l='Smab', bgc=[.25,.2,.5], h=28, w=230, c=partial(mirrorBsWght(listSel, "R")')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='self mirror wght L-->R', bgc=[.25,.2,.5], h=28, w=230, c=partial(mirrorBsWght, listSel, "L"))
    mc.button(l='self mirror wght R-->L', bgc=[.25,.2,.5], h=28, w=230, c=partial(mirrorBsWght, listSel, "R"))

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='CHECK', cll=True)
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='create sepCheaker', bgc=[.25,.2,.5], h=28, w=230, c=partial(crtSepChecker, listSel))
    #mc.button(l='delete sepCheaker', bgc=[.25,.2,.5], h=28, w=230, c=partial(crtSepChecker(listSel)')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Adds', cll=True)
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='wrap to all', h=28, w=110, c=partial(connectNeutralWrap, listSel))

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Template', cll=True)
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='create Tpl', bgc=[.25,.2,.0], h=28, w=230, c=partial(genTpl, listSel))
    mc.button(l='update Tpl', bgc=[.25,.2,.5], h=28, w=230, c=partial(updateTpl, listSel))
    mc.button(l='report Tpl to neutral', bgc=[.25,.2,.5], h=28, w=230, c=partial(connTplToNeutral))
    mc.setParent('..')
    mc.rowLayout(nc=3, adj=2)
    mc.columnLayout()
    mc.button(l='load as driver', c=partial(loadSelItemInList, "tplDriversList"))
    mc.textScrollList('tplDriversList')
    mc.popupMenu(b=3, mm=False, aob=True)
    mc.menuItem(l='select in viewport', c='print "to do"')
    mc.menuItem(l='reset', c='print "to do"')
    mc.menuItem(l='remove', c='print "to do"')

    mc.setParent('..')
    mc.columnLayout()
    mc.checkBoxGrp('chkBoxTr', ncb=4, l='Translate : ', la4=['X', 'Y', 'Z', 'All'], ct5=('left', 'left', 'left', 'left', 'left'), co5=(0, -75, -150, -225, -290), cc4=partial(setchkBoxAllChans, "chkBoxTr"))
    mc.checkBoxGrp('chkBoxRt', ncb=4, l='Rotate : ', la4=['X', 'Y', 'Z', 'All'], ct5=('left', 'left', 'left', 'left', 'left'), co5=(0, -75, -150, -225, -290), cc4=partial(setchkBoxAllChans, "chkBoxRt"))
    mc.checkBoxGrp('chkBoxSc', ncb=4, l='Scale : ', la4=['X', 'Y', 'Z', 'All'], ct5=('left', 'left', 'left', 'left', 'left'), co5=(0, -75, -150, -225, -290), cc4=partial(setchkBoxAllChans, "chkBoxSc"))
    mc.setParent('..')
    mc.columnLayout()
    mc.button(l='load as driven', c=partial(loadSelItemInList, "tplDrivensList"))
    mc.textScrollList('tplDrivensList')


    mc.menuItem(l='select in viewport', c='print "to do"')
    mc.menuItem(l='reset', c='print "to do"')
    mc.menuItem(l='remove', c='print "to do"')

    mc.setParent('..')
    mc.setParent('..')
    mc.button(l='APPLY', bgc=[.25,.2,.5], c=partial(linkSlicesDrivers))

    #mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Finish', cl=True, cll=True)
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='EXTRACT SHAPES', bgc=[.2,.2,.5], h=28, w=230, c=partial(extractShapes_v3, listSel))


    mc.setParent('..')
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='CONNECT SHAPES', bgc=[.2,.2,.5], h=28, w=230, c=partial(buildShapesTRGTRig, listSel))

    ###################################################################################################################
    ###################################################################################################################

    mc.columnLayout('BUILD', adj=True, w=225, p='MASTER_tab')
    mc.separator(h=7.5, st='in')

    mc.frameLayout(l='Face Rig', cll=True)
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='template face', h=28, w=110, c=partial(setFaceTpl))
    mc.button(l='build face', h=28, w=110, c=partial(buildFaceTpl_v2, listSel, True))
    mc.button(l='connect face', h=28, w=110, c=partial(connectFaceRig_v3, listSel, True, True, True, True))

    mc.setParent('..')
    mc.separator(h=7.5, st='in')

    ###################################
    ###################################

    mc.showWindow(win_facialTool_UI)
    project_manager.checkProject(nWin, nProjectMenu, nLoadModBtn, nGenTrgtBtn, nLoadTplBtn, 'FACE')
#smfBlendShapesTool_ui()

