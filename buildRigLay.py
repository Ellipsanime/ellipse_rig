import maya.cmds as mc

from ellipse_rig.library import lib_controlGroup, lib_math, lib_dagMenu, lib_deformers, lib_shapes, lib_rigs
reload(lib_controlGroup)
reload(lib_math)
reload(lib_dagMenu)
reload(lib_deformers)
reload(lib_shapes)
reload(lib_rigs)
from ellipse_rig.core import references
reload(references)

def genSkLay(fDatas, lSkRig):
    lSkLay = []
    for sk in lSkRig:
        nDup = sk.split(':')[-1]
        skDup = nDup
        if not mc.objExists(nDup):
            skDup = mc.duplicate(sk, po=True, n=nDup)[0]
            mc.parent(skDup, world=True)
        if not mc.attributeQuery('skLay', n=sk, ex=True):
            mc.addAttr(sk, ln='skLay', at='message')
        if not mc.attributeQuery('skRig', n=skDup, ex=True):
            mc.addAttr(skDup, ln='skRig', at='message')
        mc.connectAttr(sk+'.skLay', skDup+'.skRig', f=True)
        mc.setAttr(skDup+'.drawStyle', 0)
        lSkLay.append(skDup)
    return lSkLay
        
def buildSkLayHi(axe, sign, cg, lCgChilds, lSkRig):
    dicSk = {}
    if lCgChilds:
        for cgChild in lCgChilds:
            lCtrlChild = lib_controlGroup.getCtrlFromCg(cgChild)
            for ctrl in lCtrlChild:
                lChilds = mc.listRelatives(ctrl, c=True, type='joint') or []
                if not lChilds:
                    chkConn = mc.listConnections(ctrl+'.translate', d=True, type='joint') or []
                    if chkConn:
                        lChilds.append(chkConn[0])
                if lChilds:
                    for child in lChilds:
                        if child in lSkRig:
                            pos = mc.xform(child, ws=True, q=True, t=True)
                            if axe == 'x' :
                                val = pos[0]
                            if axe == 'y' :
                                val = pos[1]
                            if axe == 'z' :
                                val = pos[2]
                            dicSk[val] = child
    lKeys = []

    if sign == '+':
        for i in reversed(sorted(dicSk.keys())):
            lKeys.append(i)
    elif sign == '-':
        for i in sorted(dicSk.keys()):
            lKeys.append(i)
    i = 0
    print lKeys
    for key in lKeys:
        if i < len(dicSk.keys())-1:
            skLay = mc.listConnections(dicSk[key]+'.skLay', d=True)
            fatherLay = mc.listConnections(dicSk[lKeys[i+1]]+'.skLay', d=True)
            try:
                mc.parent(skLay, fatherLay)
            except:
                pass
            i += 1




def doBuildRigLay_OLD(fDatas):
    lMsh = []
    lSkRig = []
    lMshShp = mc.ls(fDatas.nSpaces[fDatas.mod] + ':msh_*', r=True, type='mesh') or []
    if lMshShp:
        for msh in lMshShp:
            father = mc.listRelatives(msh, p=True)[0]
            if not father.replace(fDatas.nSpaces[fDatas.mod], fDatas.nSpaces[fDatas.stp]) in lMsh:
                lMsh.append(father.replace(fDatas.nSpaces[fDatas.mod], fDatas.nSpaces[fDatas.stp]))
    for msh in lMsh:
        skin = lib_deformers.getSkin(msh)
        if skin:
            lSk = mc.skinCluster(skin, query=True, inf=True)
            for sk in lSk:
                if not sk in lSkRig:
                    lSkRig.append(sk)
    lSkLay = genSkLay(fDatas, lSkRig)
    lCgs = lib_controlGroup.getAllCg()
    dicCgFamily = lib_controlGroup.getCgFatherToChild()
    lCgModules = []
    lKeepedCg = ['spine', 'arm', 'leg', 'foot', 'hand', 'head', 'tail','face']
    for cg in lCgs:
        if cg.split('_')[1] in lKeepedCg:
            lCgModules.append(cg)

    dicCgHi = lib_controlGroup.getCgHi(lCgs)
    dicCg = {}
    for key in dicCgFamily.keys():
        if not key in dicCg.keys():
            dicCg[key] = []
        for cg in dicCgFamily[key]:
            if not cg in lCgModules and not cg in dicCg[key]:
                dicCg[key].append(cg)

    for i in sorted(dicCgHi.keys()):
        for cg in dicCgHi[i]:
            if cg in lCgModules:
                module = cg.split('_')[1]
                getCgChilds = lib_controlGroup.getCgChilds(cg) or []
                lCgChilds = []
                if getCgChilds:
                    for cgChild in getCgChilds:
                        if not cgChild in lCgModules:
                            lCgChilds.append(cgChild)
                #print cg, getCgChilds, lCgChilds
                if module == 'spine':
                    print 'spine'
                    buildSkLayHi('y', '+', cg, lCgChilds, lSkRig)
                    lFkCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    if lCgChilds:
                        for cgChild in lCgChilds:
                            lCtrlChild = lib_controlGroup.getCtrlFromCg(cgChild)

                elif module == 'arm':
                    print 'arm'
                    sign = '+'
                    if cg.endswith('_R'):
                        sign = '-'
                    buildSkLayHi('x', sign, cg, lCgChilds, lSkRig)
                    #lFkCrl = lib_controlGroup.getCtrlFromCg(cg)
                    #if lCgChilds:
                        #for cgChild in lCgChilds:
                            #lCtrlChild = lib_controlGroup.getCtrlFromCg(cgChild)
                    #print cg, lCgChilds, lFkCrl
                elif module == 'leg':
                    print 'leg'
                    sign = '-'
                    buildSkLayHi('y', sign, cg, lCgChilds, lSkRig)
                elif module == 'head':
                    print 'head'
                    sign = '+'
                    buildSkLayHi('y', sign, cg, lCgChilds, lSkRig)
                elif module == 'face':
                    print 'face'
                    sign = '+'
                    buildSkLayHi('y', sign, cg, lCgChilds, lSkRig)
                elif module == 'tail':
                    print 'tail'
                    sign = '-'
                    buildSkLayHi('z', sign, cg, lCgChilds, lSkRig)


def buildWWF(fDatas, geoBox):
    scPath = fDatas.filePath

    if not scPath:
        mc.warning('name your current scene by saving it correctly')
        #return
    if not mc.objExists('WIP'):
        tmpNode = mc.createNode('transform', n='WIP')
        mc.addAttr(tmpNode, ln='deleteMe', at='bool', dv=1)

    box = 'ALL'
    if not mc.objExists(box):
        box = mc.createNode('transform', n='ALL')
        mc.parent(geoBox, box)
    rig = 'RIG'
    if not mc.objExists(rig):
        rig = mc.createNode('transform', n='RIG')

    world = 'WORLD'
    cWalk = 'c_WALK'
    cFly = 'c_FLY'
    ctrShp = {world:'square', cWalk:'crossArrow', cFly:'fly'}
    for ctr in [world, cWalk, cFly]:
        if not mc.objExists(ctr):
            bld = lib_shapes.shp_form(ctrShp[ctr], "Index", "brown24", name=ctr)
            if bld.endswith('Shape'):
                mc.rename(bld, ctr)

    rootWalk = mc.createNode('transform', n='root_WALK')
    rootFly = mc.createNode('transform', n='root_FLY')

    mc.parent(cFly, rootFly)
    mc.parent(rootFly, cWalk)
    mc.parent(cWalk, rootWalk)
    mc.parent(rootWalk, world)
    mc.parent(world, box)
    mc.parent(rig, box)

    if geoBox:
        bBoxBox = mc.exactWorldBoundingBox(box, calculateExactly=True)
        bBoxWorld = mc.exactWorldBoundingBox(world, calculateExactly=True)
        dif = [bBoxBox[3] - bBoxWorld[3], 0, bBoxBox[5] - bBoxWorld[5]]
        center = mc.objectCenter(geoBox, gl=True)
        mc.setAttr(world + '.scale', 2 + dif[0], 2 + dif[1], 2 + dif[2])
        mc.makeIdentity(world, a=True)
        mc.setAttr(rootFly + '.t', *center)
        shpFly = mc.listRelatives(cFly, s=True)[0]
        lCvs = mc.ls(shpFly + '.cv[*]', fl=True)
        for cv in lCvs:
            pos = mc.xform(cv, q=True, ws=True, t=True)
            mc.move(pos[0], 0, pos[2] - dif[2], cv, ls=True)
        print 'shapes ajusted'
    lib_controlGroup.addCtrlToCg([world, cWalk, cFly], 'cg_all')
    hook = lib_rigs.crtHook(cFly, rig)
    mc.delete(mc.parentConstraint('RIG:c_FLY', 'root_FLY', mo=False))
    return hook



def doTpl(lCtrl, nCg, ctrlType='loc'):
    lTpl = []
    for ctrl in lCtrl:
        nTpl = ctrl.replace(ctrl.split('_')[0], 'tpl')
        lTpl.append(nTpl)
        tpl = nTpl
        if not mc.objExists(nTpl):
            #tpl = mc.spaceLocator(n=nTpl)[0]
            tpl = mc.circle(n=nTpl)[0]
            mc.delete(tpl, ch=True)
            mc.delete(mc.parentConstraint(ctrl, tpl, mo=False))
            lCtrlShp = mc.listRelatives(ctrl, s=True, ni=True) or []
            if lCtrlShp:
                for shp in lCtrlShp:
                    if not mc.attributeQuery('nodeType', n=shp, ex=True):
                        if mc.getAttr(shp+'.v'):
                            if mc.attributeQuery('worldSpace', n=shp, ex=True):
                                mc.connectAttr(shp+'.worldSpace[0]', mc.listRelatives(tpl, s=True)[0]+'.create')


    for i in range(0, len(lTpl)-1):
        try:
            mc.parent(lTpl[i+1], lTpl[i])
        except:
            pass

    cg = lib_controlGroup.crtCg(nCg)
    lib_controlGroup.addTplsToCg(lTpl, cg)
    if ctrlType == 'joint':
        for tpl in lTpl:
            mc.setAttr(tpl+'.builtType', 0)
            mc.setAttr(tpl+'.iconType', 0)
    lib_controlGroup.buildTplCg(cg)
    return lTpl


def buildStrech(shoulder, elbow, wrist, ik, scl):
    posSh = mc.xform(shoulder, ws=True, q=True, t=True)
    posEl = mc.xform(elbow, ws=True, q=True, t=True)
    posWr = mc.xform(wrist, ws=True, q=True, t=True)
    dstToolUp = mc.distanceDimension(sp=posSh, ep=posEl)
    dstToolDn = mc.distanceDimension(sp=posEl, ep=posWr)
    dstToolIk = mc.distanceDimension(sp=posSh, ep=posWr)


    chkLoc = mc.listConnections(dstToolIk+'.startPoint', s=True)[0]
    if mc.referenceQuery(chkLoc, inr=True):
        loc = mc.spaceLocator(n=shoulder.replace('c_', 'dstLoc_'))[0]
        mc.delete(mc.parentConstraint(shoulder, loc, mo=False))
        mc.connectAttr(mc.listRelatives(loc, s=True)[0]+'.worldPosition[0]', dstToolIk+'.startPoint', f=True)
    chkLoc = mc.listConnections(dstToolIk + '.endPoint', s=True)[0]
    if mc.referenceQuery(chkLoc, inr=True):
        loc = mc.spaceLocator(n=ik.replace('c_', 'dstLoc_'))[0]
        mc.delete(mc.parentConstraint(ik, loc, mo=False))
        mc.connectAttr(mc.listRelatives(loc, s=True)[0] + '.worldPosition[0]', dstToolIk + '.endPoint', f=True)

    dstUp = mc.getAttr(dstToolUp + '.distance')
    dstDn = mc.getAttr(dstToolDn + '.distance')
    dstIk = mc.getAttr(dstToolIk + '.distance')
    dstLimb = dstUp + dstDn
    print 'HERE :'
    print 'dstUp', dstUp
    print 'dstDn', dstDn
    print 'dstIk', dstIk
    print 'dstLimb', dstLimb
    locStr = mc.listConnections(dstToolIk+'.startPoint', s=True)[0]
    mc.parent(locStr, mc.listRelatives(shoulder, p=True)[0])
    mc.setAttr(locStr+'.v', False)
    locEnd = mc.listConnections(dstToolIk+'.endPoint', s=True)[0]
    mc.parent(locEnd, ik)
    mc.setAttr(locEnd + '.v', False)
    toDel = []
    for dstTool in [dstToolUp, dstToolDn]:
        locA = mc.listConnections(dstTool+'.startPoint', s=True)[0]
        locB = mc.listConnections(dstTool+'.endPoint', s=True)[0]
        toDel.append(locA)
        toDel.append(locB)
    mc.delete(toDel)
    """
    
    sub = mc.createNode('floatMath')
    mc.setAttr(sub+'.operation', 1)
    mc.connectAttr(dstToolIk+'.distance', sub+'.floatA')
    mc.setAttr(sub+'.floatB', dstLimb)
    cnd = mc.createNode('condition')
    mc.setAttr(cnd+'.operation', 2)
    mc.setAttr( cnd+'.colorIfFalseR', dstLimb)
    mc.connectAttr(dstToolIk+'.distance', cnd+'.colorIfTrueR')
    mc.connectAttr(sub+'.outFloat' , cnd + '.firstTerm')
    div = mc.createNode('floatMath')
    mc.setAttr(div+'.operation', 3)
    mc.connectAttr(cnd+'.outColorR', div+'.floatA')
    mc.setAttr(div+'.floatB', dstLimb)
    #mlt = mc.createNode('multDoubleLinear')
    #mc.connectAttr(div+'.outFloat', mlt+'.input1')
    #mc.connectAttr(fly + '.scaleX', mlt + '.input1')
    sclMlt = mc.createNode('multDoubleLinear')
    mc.connectAttr(scl+'.scaleX',  sclMlt+ '.input1')
    mc.setAttr(sclMlt+ '.input2', dstLimb)
    mc.connectAttr(sclMlt+ '.output', sub+'.floatB')
    mc.connectAttr(sclMlt + '.output', div+'.floatB')
    mc.connectAttr(sclMlt + '.output', cnd+'.colorIfFalseR')
    """
    sclMltSrc = mc.createNode('multDoubleLinear')
    sclMltTrgt = mc.createNode('multDoubleLinear')
    mc.setAttr(sclMltSrc+'.input1', 1)
    mc.setAttr(sclMltSrc + '.input2', dstLimb)
    mc.setAttr(sclMltTrgt + '.input1', 1)
    mc.connectAttr(dstToolIk+'.distance', sclMltTrgt + '.input2')

    sub = mc.createNode('floatMath')
    div = mc.createNode('multDoubleLinear')
    cnd = mc.createNode('condition')
    addUp = mc.createNode('addDoubleLinear')
    addDn = mc.createNode('addDoubleLinear')

    mc.setAttr(sub + '.operation', 1)
    mc.setAttr(div+'.input2', 0.5)
    mc.setAttr(cnd + '.operation', 2)
    mc.setAttr(cnd+'.secondTerm', 0)
    mc.setAttr(cnd + '.colorIfFalseR', 0)
    mc.setAttr(addUp+'.input1', dstUp)
    mc.setAttr(addDn + '.input1', dstDn)

    mc.connectAttr(sclMltSrc+'.output', sub+'.floatA')
    mc.connectAttr(sclMltTrgt + '.output', sub + '.floatB')

    mc.connectAttr(sub+'.outFloat', cnd+'.firstTerm')
    mc.connectAttr(sub + '.outFloat', div + '.input1')
    mc.connectAttr(div+'.output', cnd+'.colorIfTrueR')

    mc.connectAttr(cnd+'.outColorR', addUp+'.input2')
    mc.connectAttr(cnd + '.outColorR', addDn + '.input2')

    mc.connectAttr(addUp+'.output', elbow+'.translateY')
    mc.connectAttr(addDn + '.output', wrist + '.translateY')



def eyesLay():
    toDel =  ['msh_eyeball_L', 'msh_cornea_L', 'msh_iris_L', 'msh_specu_L', 'msh_pupil_L', 'msh_eyeball_R', 'msh_cornea_R', 'msh_iris_R', 'msh_specu_R', 'msh_pupil_R']
    for msh in toDel:
        if mc.objExists(msh):
            mc.delete(msh)
    geoEyes = mc.duplicate('MOD:geo_eyes')[0]
    mc.parent(geoEyes, 'GEO')
    lNodes = mc.listRelatives(geoEyes, ad=True, type='transform')

    for node in lNodes:
        if mc.getAttr(node+'.v') == False:
            if mc.objExists(node):
                mc.delete(node)
    lTpl = ['RIG:c_lookAt_1', 'RIG:c_lookAt_1_R', 'RIG:c_lookAt_1_L']
    lBuildTpl = doTpl(lTpl, 'cg_eyes')


    for node in ['loc_corneBase_L', 'loc_corneBase_R']:
        for attr in ['translate', 'rotate']:
            for chan in ['X', 'Y', 'Z']:
                mc.setAttr(node+'.'+attr+chan, 0)
        mc.setAttr(node+'.translateY', 1.0)
    for tpl in lBuildTpl:
        if tpl.split('_')[-1] in ['L', 'R']:
            side = '_L'
            if tpl.endswith('_R'):
                side = '_R'
            mc.select(cl=True)
            root = mc.joint(n='root_eye'+side)
            off = mc.joint(n='off_eye'+side)
            sk = mc.joint(n='sk_eye'+side)
            mc.setAttr(off + '.segmentScaleCompensate', 0)
            mc.setAttr(sk+'.segmentScaleCompensate', 0)
            mc.parent(root, 'c_head_1')
            mc.delete(mc.parentConstraint('geo_eye'+side, root, mo=False))
            mc.delete(mc.scaleConstraint('geo_eye'+side, root, mo=False))
            mc.delete(mc.parentConstraint('geo_eyeball'+side, off, mo=False))
            mc.delete(mc.parentConstraint('msh_eyeball'+side, sk, mo=False))
            mc.parent('loc_corneBase'+side, root)
            ctrl = mc.listConnections(tpl+'.message', d=True, type='transform')[0]
            mc.aimConstraint(ctrl, sk, mo=True, aim=[0,0,1], u=[0, 1, 0], wut='object', wuo='loc_corneBase'+side)


    lib_controlGroup.parentCg('cg_eyes', 'cg_head')
    rigGrp = mc.listConnections('cg_eyes.rigGroup', s=True, type='transform')
    mc.parent(rigGrp, 'c_head_1')
    tplGrp = mc.listConnections('cg_eyes.tplGroup', s=True, type='transform')
    mc.parent(tplGrp, 'WIP')


def clearRigAdds(nspace):
    if not mc.namespace(ex=nspace):
        mc.namespace(add=nspace)
    lNodes = mc.ls('*.nodeType', r=False, o=True)
    for node in lNodes:
        if not ':' in node:
            if not '|' in node:
                if mc.objExists(node):
                    mc.lockNode(node, lock=False)
                    lFathers = mc.listRelatives(node, p=True) or []
                    lChild = mc.listRelatives(node, c=True) or []
                    for father in lFathers:
                        if not ':' in father:
                            mc.rename(father, nspace + father)
                    for child in lChild:
                        if not ':' in child:
                            if mc.objExists(child):
                                mc.rename(child, nspace + child)
                    if mc.objExists(node):
                        mc.rename(node, nspace + node)


def doBuildRigLay(fDatas):
    clearRigAdds('SOURCERIG')
    lMsh = []
    geoBox = 'GEO'
    if not mc.objExists(geoBox):
        mc.createNode('transform', n=geoBox)

    lMshShp = mc.ls(fDatas.nSpaces[fDatas.mod] + ':msh_*', r=True, type='mesh', ni=True) or []
    if lMshShp:
        for msh in lMshShp:
            father = mc.listRelatives(msh, p=True)[0]
            fatherRig = father.replace(fDatas.nSpaces[fDatas.mod], fDatas.nSpaces[fDatas.stp])
            if mc.objExists(fatherRig):
                lDef = mc.findDeformers(mc.listRelatives(fatherRig, s=True, ni=True)[0]) or []
                if lDef:
                    for node in lDef:
                        if not mc.nodeType(node) in ['skinCluster', 'blendShape']:
                            mc.setAttr(node + '.envelope', 0)
                        nDupMsh = fatherRig.split(':')[-1]
                        dupMsh = nDupMsh
                        if not mc.objExists(nDupMsh):
                            dupMsh = mc.duplicate(fatherRig, n=nDupMsh)[0]
                            mc.setAttr(dupMsh+'.v', True)
                            for attr in ['translate', 'rotate', 'scale']:
                                for chan in ['X', 'Y', 'Z']:
                                    mc.setAttr(dupMsh+'.'+attr+chan, lock=False, k=True)
                            mc.parent(dupMsh, geoBox)
                        lMsh.append(dupMsh)

    lCgModules = []
    lCgs = lib_controlGroup.getAllCg()
    dicCgFamily = lib_controlGroup.getCgFatherToChild()



    lKeepedCg = ['spine', 'arm', 'leg', 'neck', 'head', 'hand', 'foot']
    for cg in lCgs:
        if cg.startswith('RIG:'):
            if cg.split('_')[1] in lKeepedCg:
                lCgModules.append(cg)

    dicCgHi = lib_controlGroup.getCgHi(lCgs)
    dicCg = {}
    for key in dicCgFamily.keys():
        if not key in dicCg.keys():
            dicCg[key] = []
        for cg in dicCgFamily[key]:
            if not cg in lCgModules and not cg in dicCg[key]:
                dicCg[key].append(cg)

    scl = buildWWF(fDatas, geoBox)
    for i in sorted(dicCgHi.keys()):
        for cg in dicCgHi[i]:
            if cg in lCgModules:
                module = cg.split('_')[1]
                getCgChilds = lib_controlGroup.getCgChilds(cg) or []
                lCgChilds = []
                if getCgChilds:
                    for cgChild in getCgChilds:
                        if not cgChild in lCgModules:
                            lCgChilds.append(cgChild)
                print module
                if module == 'spine':
                    lTpl = []
                    lCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    for ctrl in lCtrl:
                        chkSkin = mc.listConnections(ctrl, s=True, type='skinCluster') or []
                        if chkSkin:
                            for skin in chkSkin:
                                geo = mc.skinCluster(skin, q=True, g=True)[0]
                                chkcrvInfo = mc.listConnections(geo, d=True, type='curveInfo') or []
                                if chkcrvInfo:
                                    if not ctrl in lTpl:
                                        lTpl.append(ctrl)
                    doTpl(lTpl, cg.split(':')[-1])

                elif module in ['arm', 'leg']:
                    lSwitchNode = mc.ls('*.reverseTwist', r=True, o=True)
                    lCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    for sNode in lSwitchNode:
                        lFk = mc.listConnections(sNode+'.fk', s=True) or []
                        if lFk:
                            if lFk[0] in lCtrl:
                                ik = mc.listConnections(sNode+'.ik', s=True)[0]
                                tplFk = doTpl(lFk, cg.split(':')[-1], ctrlType='joint')
                                tplIk = doTpl([ik], cg.split(':')[-1])
                                cg = mc.listConnections(tplFk[0]+'.message', d=True, type='network')[0]
                                #tplEndId = mc.listConnections(tplFk[-1] + '.message', d=True, plugs=True, type='network')[0].split('[')[-1][: -1]
                                startIk = mc.listRelatives(mc.listConnections(tplFk[0]+'.message', d=True, type='transform')[0], p=True)[0]
                                endIk = mc.listRelatives(mc.listConnections(tplFk[-1]+'.message', d=True, type='transform')[0], p=True)[0]

                                ikCtrl = mc.listConnections(tplIk[0]+'.message', d=True, type='transform')[0]
                                #mc.parent(ikHdl, ikCtrl)
                                mc.addAttr(ikCtrl, ln='ikBlend', at='float', min=0, max=10, dv=10, k=True)
                                mdl = mc.createNode('multDoubleLinear', n=cg.replace('cg_', 'mdl_'))
                                mc.setAttr(mdl+'.input1', .1)
                                mc.connectAttr(ikCtrl+'.ikBlend', mdl+'.input2')

                                pv = ''
                                for ctrl in lCtrl:
                                    chkConn = mc.listConnections(ctrl, d=True, type='poleVectorConstraint') or []
                                    if chkConn:
                                        tplPv = doTpl([ctrl], cg.split(':')[-1])
                                        pv = mc.listConnections(tplPv[0] + '.message', d=True, type='transform')[0]
                                        break
                                #notHere
                                ctrlSh = mc.listConnections(tplFk[0]+'.message', d=True, type='transform')[0]
                                ctrlEl = mc.listConnections(tplFk[1]+'.message', d=True, type='transform')[0]
                                fatherEl = mc.listRelatives(ctrlEl, p=True)[0]
                                ctrlWr = mc.listConnections(tplFk[2] + '.message', d=True, type='transform')[0]
                                fatherWr = mc.listRelatives(ctrlWr, p=True)[0]
                                mc.parent(fatherWr, world=True)
                                for node in mc.listRelatives(fatherEl, c=True):
                                    mc.parent(node, ctrlSh)
                                mc.delete(fatherEl)
                                mc.parent(fatherWr, ctrlEl)
                                ikHdl = mc.ikHandle(n=cg.replace('cg_', 'ik_'), sj=mc.listRelatives(ctrlSh, p=True)[0], ee=ctrlWr, sol='ikRPsolver', s=False)[0]
                                mc.connectAttr(mdl + '.output', ikHdl + '.ikBlend')
                                mc.poleVectorConstraint(pv, ikHdl)
                                ort = mc.createNode('transform', n=pv.replace('c_', 'ort_'))
                                mc.delete(mc.parentConstraint(ctrlSh, ort, mo=False))
                                mc.aimConstraint(ikCtrl, ort, mo=True, aim=[00,1,0], u=[0, 0, -1], wut='object', wuo='c_cog_1')
                                mc.parent(mc.listRelatives(pv, p=True)[0], 'hook_FLY')
                                mc.pointConstraint(ikCtrl, ort, mc.listRelatives(pv, p=True)[0], mo=True)
                                mc.parent(mc.listRelatives(pv, p=True)[0], mc.listRelatives(ikCtrl, p=True)[0])
                                mc.parent(ort, mc.listRelatives(mc.listRelatives(ctrlSh, p=True)[0])[0])

                                mc.parent(ikHdl, ikCtrl)
                                mc.parent(mc.listRelatives(ikCtrl, p=True)[0], 'hook_FLY')
                                #mc.setAttr(ctrlEl+'.translate', k=False, lock=True, cb=False)
                                mc.connectAttr(ikCtrl+'.v', pv+'.v', f=True)
                                #buildStrech(ctrlSh, ctrlEl, ctrlWr, ikCtrl, scl)



                elif module in ['hand', 'foot']:
                    lCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    remove = []
                    for ctrl in lCtrl:
                        shp = mc.listRelatives(ctrl, s=True, ni=True)[0]
                        if mc.nodeType(shp) == 'locator':
                            remove.append(ctrl)
                    if remove:
                        for rem in remove:
                            if rem in lCtrl:
                                lCtrl.remove(rem)
                    lTplFk = doTpl(lCtrl, cg.split(':')[-1])
                    dicCtrlModule  = {}
                    for tpl in lTplFk:
                        if module in tpl:
                            dicCtrlModule[tpl] = mc.listRelatives(mc.listConnections(tpl+'.message', d=True, type='transform')[0], p=True)[0]
                    for tplFk in dicCtrlModule.keys():
                        if tplFk in lTplFk:
                            lTplFk.remove(tplFk)
                    for tpl in lTplFk:
                        if tpl.split('_')[1].endswith('1'):
                            root = mc.listRelatives(mc.listConnections(tpl+'.message', d=True, type='transform')[0], p=True)[0]
                            father = lib_math.getNearestTrans(root, dicCtrlModule.values())
                            mc.parent(root, father)
                    if module == 'foot':
                        lCtrl = lib_controlGroup.getCtrlFromCg(cg.split(':')[-1])
                        remove = []
                        for ctrl in lCtrl:
                            shp = mc.listRelatives(ctrl, s=True, ni=True)[0]
                            if mc.nodeType(shp) == 'locator':
                                remove.append(ctrl)
                        if remove:
                            for rem in remove:
                                if rem in lCtrl:
                                    lCtrl.remove(rem)
                        father = lCtrl[0]
                        for ctrl in lCtrl:
                            posSrc = mc.xform(father, ws=True, q=True, t=True)[1]
                            posY =  mc.xform(ctrl, ws=True, q=True, t=True)[1]
                            if posY > posSrc:
                                father = ctrl
                        for ctrl in lCtrl:
                            if not ctrl == father:
                                root = mc.listRelatives(ctrl, p=True)[0]
                                if not mc.listRelatives(root, p=True)[0] == father:
                                    mc.parent(root, father)



                elif module == 'neck':
                    lTpl = []
                    dicHi = {}
                    lCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    for ctrl in lCtrl:
                        if not mc.attributeQuery('squash', n=ctrl, ex=True):
                            lTpl.append(doTpl([ctrl], cg.split(':')[-1]))

                    for tpl in lTpl:
                        dicHi[mc.xform(tpl, ws=True, q=True, t=True)[1]] = tpl
                    lHi = []
                    hiVal = sorted(dicHi.keys())
                    for val in reversed(hiVal):
                        lHi.append(dicHi[val][0])
                    for i in range(0, len(lHi)-1):
                        ctrl = mc.listConnections(lHi[i]+'.message', d=True, type='transform')[0]
                        root = mc.listRelatives(ctrl, p=True)[0]
                        father = mc.listConnections(lHi[i+1]+'.message', d=True, type='transform')[0]
                        mc.parent(root, father)
                        i += 1



                elif module == 'head':
                    lCtrl = lib_controlGroup.getCtrlFromCg(cg)
                    for ctrl in lCtrl:
                        if not mc.attributeQuery('squash', n=ctrl, ex=True):
                            doTpl([ctrl], cg.split(':')[-1])
                    eyesLay()

    lLayCg = []
    for cg in lib_controlGroup.getAllCg():
            if cg.startswith('RIG:'):
                if mc.objExists(cg.split(':')[-1]):
                    lLayCg.append(cg.split(':')[-1])
                    cgFather = lib_controlGroup.getCgFather(cg)
                    if cgFather:
                        lib_controlGroup.parentCg(cg.split(':')[-1], cgFather[0].split(':')[-1])
    for cg in lLayCg:
        cgParent = lib_controlGroup.getCgFather(cg)
        tplGrp = mc.listConnections(cg+'.tplGroup', s=True, type='transform') or []
        if tplGrp:
            mc.parent(tplGrp, 'WIP')
        if cgParent:
            lDrivers = mc.listConnections(cgParent[0]+'.members', d=True) or []
            rigGrp = mc.listConnections(cg + '.rigGroup', s=True) or []
            ctrlMaster = mc.listConnections(cg + '.members[0]', d=True) or []
            if lDrivers and  ctrlMaster and rigGrp:
                driver = lib_math.getNearestTrans(ctrlMaster[0], lDrivers)
                hook = lib_rigs.crtHook(driver, 'RIG1')
                mc.parent(rigGrp[0], hook)
        if cg.split('_')[1] in ['hand', 'foot']:
            rigGrp = mc.listConnections(cg+'.rigGroup', s=True, type='transform')
            root = mc.listRelatives(rigGrp, c=True)[0]
            cgParent = lib_controlGroup.getCgFather(cg)
            lDrivers = mc.listConnections(cgParent[0] + '.members', d=True) or []
            driver = lib_math.getNearestTrans(root, lDrivers)
            eff = mc.listRelatives(mc.listRelatives(driver, p=True)[0], c=True, type='ikEffector') or []
            ikHdl = ''
            ikCtrl = ''
            rootShld = ''
            if eff:
                ikHdl = mc.listConnections(eff, d=True)[0]
                ikCtrl = mc.listRelatives(ikHdl, p=True)[0]
                rootShld = mc.listConnections(ikHdl + '.startJoint')[0]
            else:
                ikHdl = mc.listRelatives(driver, c=True, type='ikHandle') or []
                rootShld = mc.listConnections(ikHdl[0]+ '.startJoint')[0]
                if ikHdl:
                    ikCtrl = driver

            cnst = mc.orientConstraint(ikCtrl, root, mo=True)[0]
            mlt = mc.listConnections(ikCtrl + '.ikBlend', d=True)[0]
            mc.connectAttr(mlt + '.output', cnst + '.' + ikCtrl + 'W0', f=True)
            ctrlHand = mc.listRelatives(root, c=True, type='transform')[0]
            mc.addAttr(ctrlHand, ln='ikBlend', at='float', min=0, max=10, dv=10, k=True)
            mc.connectAttr(ctrlHand+'.ikBlend', ikCtrl+'.ikBlend')
            cnd = mc.createNode('condition')
            mc.setAttr(cnd + '.operation', 1)
            mc.setAttr(cnd+'.secondTerm', 10.0)
            mc.connectAttr(ctrlHand + '.ikBlend', cnd+'.firstTerm', f=True)
            rvs = mc.createNode('reverse')
            mc.connectAttr(cnd+'.outColorR', rvs+'.inputX')
            mc.connectAttr(cnd+'.outColorR', ikCtrl+'.v', f=True)
            #mc.connectAttr(rvs + '.outputX', rootShld+'.v', f=True)
            if cg.split('_')[1] == 'hand':
                mc.setAttr(ctrlHand + '.ikBlend', 0)

    print 'RIG LAY BUILDED'
    lIkHdl = mc.ls(type='ikHandle') or []
    if lIkHdl:
        solver = mc.createNode('ikRPsolver')
        mc.connectAttr(solver+'.message', mc.ls(type='ikSystem')[0]+'.ikSolver[0]', f=True)
        for hdl in lIkHdl:
            if not mc.referenceQuery(hdl, inr=True):
                mc.connectAttr(solver+'.message', hdl+'.ikSolver', f=True)


    chkSwitch = mc.ls('*.ctrlSwitcher', r=True, o=True) or []
    if chkSwitch:
        for node in chkSwitch:
            root = mc.listRelatives(node, p=True)[0]
            rigAdd = mc.duplicate(root)[0]
            mc.parent(rigAdd, 'hook_FLY')

    lRefs = fDatas.getScnRefs()
    for ref in lRefs:
        references.removeRef(ref)
    print 'REFS REMOVED'
    mc.rename('RIG1', 'RIG')








