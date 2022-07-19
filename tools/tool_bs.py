import maya.cmds as mc


#def getShp(obj):


def getShdFromShp(shp):
    shdSG=mc.listConnections(shp,type='shadingEngine')[0]
    shd = mc.listConnections(shdSG+'.surfaceShader')[0]
    return shd

#getShdFromShp('neutral_iris_RShape')

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



def generateNeutral(lObj):
    grp = 'geo_neutral'
    if not mc.objExists('geo_neutral'):
        grp = mc.createNode('transform', n=grp)
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
        mc.sets(dup, forceElement=newShd)


#generateNeutral(mc.ls(sl=True))

#RIG BLENDSHAPES
###########################################################
dicMouth = {}
dicMouth['mEmote'] = ['m_smile', 'm_frown']
dicMouth['mStrech'] = ['m_wide', 'm_narrow']
dicMouth['mU'] = ['m_u_up', 'm_u_dn']
dicMouth['mSlide'] = ['m_raiser', 'm_lower']
dicMouth['mPuff'] = ['m_puff']
dicMouth['mPuffCorner'] = ['m_puffCorner']
dicMouth['mOpen'] = ['m_open']
###########################################################
dicEyebrows = {}
dicEyebrows['ebSlide'] = ['eb_slide_up', 'eb_slide_dn']
dicEyebrows['ebSqueeze'] = ['eb_squeeze']
dicEyebrows['ebWrinkle'] = ['eb_wrinkle']
###########################################################
dicLips = {}
dicLips['lRoll'] = ['l_rollIn', 'l_rollOut']
dicLips['lPush'] = ['l_push']
dicLips['lPinch'] = ['l_pinch']
dicLips['lCornerPinch'] = ['l_cornerPinch']
###########################################################
dicCheeks = {}
dicCheeks['chPuff'] = ['ch_puffOut', 'ch_puffIn']
dicCheeks['chCheeks'] = ['ch_cheeks']
###########################################################
dicNose = {}
dicNose['nSnear'] = ['n_snear']
###########################################################
dicEyelids = {}
dicEyelids['elBlink'] = ['el_slide_up', 'el_slide_dn']
###########################################################

def getBsDef(obj):
    lHist = mc.listHistory(obj)
    lBs = []
    for node in lHist:
        if mc.nodeType(node) == 'blendShape':
            if not node in lBs:
                lBs.append(node)
    return lBs
#getBsDef(mc.ls(sl=True)[0])

def ctrlAttr(ctrl, dicAttrs, neutral):
    if not mc.objExists(ctrl):
        mc.createNode('transform', n=ctrl)
        mc.setAttr(ctrl+'.displayHandle', 1)
    if not mc.objExists('geo_targets'):
        mc.createNode('transform', n='geo_targets')
    bs = getBsDef(neutral) or []
    if not bs:
        bs = mc.blendShape(neutral, n='bs_head')
        mc.addAttr(bs, ln='bsType', at='enum', en='Trgt:Mix:', dv=0)
    for attr in dicAttrs.keys():
        if not mc.attributeQuery(attr, n=ctrl, ex=True):
            mn = 0
            if len(dicAttrs[attr]) == 2:
                mn = -20
            mc.addAttr(ctrl, ln=attr, at='float', k=True, min=mn, max=20)
            valCtrl = 20
            for trgt in dicAttrs[attr]:
                if not mc.objExists(trgt):
                    mc.duplicate(neutral, n=trgt)[0]
                    lWght = mc.blendShape(bs, q=True, t=True) or []
                    id = 0
                    if lWght:
                        id = len(lWght)
                    chkTrgt = mc.blendShape(bs, q=True, t=True) or []
                    if not trgt in chkTrgt:
                        mc.blendShape(bs[0], edit=True, t=(neutral, id, trgt, 1.0))
                mc.setDrivenKeyframe(bs[0]+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', dv=0, v=0)
                mc.setDrivenKeyframe(bs[0]+'.'+trgt, cd=ctrl+'.'+attr, itt='linear', dv=valCtrl, v=2)
                mc.parent(trgt, 'geo_targets')
                valCtrl = valCtrl*(-1)

neutral =  mc.ls(sl=True)[0]
ctrlAttr('c_targets', dicMouth, neutral)
ctrlAttr('c_targets', dicLips, neutral)
ctrlAttr('c_targets', dicCheeks, neutral)
ctrlAttr('c_targets', dicNose, neutral)
ctrlAttr('c_targets', dicEyelids, neutral)
ctrlAttr('c_targets', dicEyebrows, neutral)





###########################################################

def switchDk(lNodes):
    lAttrD = []
    lAttrT = mc.aliasAttr(lNodes[1],q=True)
    for attr in mc.listAttr(lNodes[0], ud=True):
        if mc.getAttr(lNodes[0]+'.'+attr, type=True) == 'double':
            lAttrD.append(attr)
    for attr in lAttrD:
        valMin = mc.getAttr(lNodes[0]+'.'+attr, min=True)
        valMax = mc.getAttr(lNodes[0]+'.'+attr, max=True)
        mc.setAttr(lNodes[0]+'.'+attr, valMax)
        trgt = ''
        for bsAttr in lAttrT:
            if not mc.getAttr(lNodes[1]+'.'+bsAttr) == 0:
               trgt = bsAttr
        #mc.setAttr()


    print mc.getAttr(lNodes[1]+'.'+bsAttrs[0])
#switchDk(mc.ls(sl=True))

"""
bsChan = 'chan_face'
lAttr = mc.listAttr(bsChan, ud=True, o=True)
lMsh = mc.ls('*.extractHead', o=True)
bs = mc.connectionInfo(bsChan+'.bsTarget', sfd=True).split('.')[0]
bsAttrs = mc.aliasAttr(bs,q=True)
baseN = ''
for attr in lAttr:
mc.setAttr(bsChan+'.'+attr, 0)

setDrivenKeyframe
"""

def connectTrgt(trgtNegative, trgtPositive, ctrl):
    bs = mc.findDeformers(trgtNegative)
    bsSrc = getBsDef(trgtNegative)
    bsTrgt = getBsDef(trgtPositive)
    if not bsSrc == bsTrgt:
        return 'this two targets are not connected to the same blendshape node'
    else:
        shpP = mc.listRelatives(trgtPositive, s=True, ni=True)[0]
        conn = mc.listConnections(shpP, plugs=True, type='blendShape')[0]
        idP = conn.split('.')[2].replace('inputTargetGroup[', '')[: -1]

        shpN = mc.listRelatives(trgtNegative, s=True, ni=True)[0]
        conn = mc.listConnections(shpN, plugs=True, type='blendShape')[0]
        idN = conn.split('.')[2].replace('inputTargetGroup[', '')[: -1]
        print idP, idN
        toto = mc.getAttr(bsSrc[0]+'.weight['+str(idP)+']')
        print toto

#connectTrgt('shp_L', 'shp_R', '')

