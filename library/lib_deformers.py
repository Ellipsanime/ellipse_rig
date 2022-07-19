# coding: utf-8

from ellipse_rig.library import lib_names, lib_attributes
reload(lib_names)
reload(lib_attributes)
import maya.cmds as mc

def setRange(oldMin, oldMax, min, max, val):
    # DKatz
    ##be sure to give FLOAT in the arguments values -> 1.0, 3.5, 2.5, 7.0, 6.23)
    newVal = min + ((max - min) * (((val / (oldMax - oldMin)) * 100.0) / 100.0))
    return newVal
# setRange(2.0, 4.0, 3.0, 6.0, 1.0)


def createSquash(selObj,shpAttr,squash,skObjLst=None,instanceShpLst=None):
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
    # get meshs to drive
    if mc.objExists(selObj[0] + ".Link") is True or mc.listRelatives(selObj[0], type="mesh") is not None:
        selMeshs = ''
        if mc.objExists(selObj[0] + ".Link") is True:
            getAttr = mc.getAttr(selObj[0] + ".Link")
            selMeshs = mc.sets(getAttr, q=True)
        if mc.listRelatives(selObj[0], type="mesh") != None:
            selMeshs = selObj
        # skin Geo ###
        if skObjLst is not None:
            for each in selMeshs:
                lstHis = mc.listHistory(each, pdo=True)
                if mc.ls(lstHis, type="skinCluster")==[]:
                    if mc.getAttr(each+'.translateX',lock=True)==True:
                        lib_attributes.lockAxis(each)
                        mc.skinCluster(skObjLst, each, tsb=True)
                    else:
                        mc.skinCluster(skObjLst, each, tsb=True)
                else:
                    pass
                mc.select(cl=True)
        for inc, each in enumerate(selMeshs):
            mc.select(each, add=True)
        # create Squash Deformer ###
        createSquash = mc.nonLinear(typ="squash", lowBound=-2, highBound=2, startSmoothness=0, endSmoothness=0,
                                    maxExpandPos=0.5, expand=1, factor=0)
        mc.select(cl=True)
        mc.parent(createSquash[1], squash)
        mc.setAttr(createSquash[1] + ".visibility", 0)
        mc.setAttr(createSquash[1] + ".translate", 0, 0, 0)
        mc.setAttr(createSquash[1] + ".rotate", 0, 0, 0)
        mc.setAttr(createSquash[1] + ".scale", 1, 1, 1)
        # connect Attributs ###
        mc.connectAttr((instanceShpLst[1] + "|" + shpAttr + ".Ubi_Squash"), (createSquash[0] + ".factor"))
        # link connection
        # low_Bound ###
        mc.select(instanceShpLst[2], r=True)
        mc.setAttr(instanceShpLst[1] + "|" + shpAttr + ".Ubi_Low_Bound", 10)
        mc.setDrivenKeyframe(createSquash[0] + ".lowBound", cd=shpAttr + ".Ubi_Low_Bound")
        mc.setAttr((instanceShpLst[1] + "|" + shpAttr + ".Ubi_Low_Bound"), 0)
        mc.setAttr((createSquash[0] + ".lowBound"), 0)
        mc.setDrivenKeyframe(createSquash[0] + ".lowBound", cd=shpAttr + ".Ubi_Low_Bound")
        mc.setAttr((instanceShpLst[1] + "|" + shpAttr + ".Ubi_Low_Bound"), 5)
        mc.setAttr((createSquash[0] + ".lowBound"), -2)
        mc.setDrivenKeyframe(createSquash[0] + ".lowBound", cd=shpAttr + ".Ubi_Low_Bound")
        # high_Bound ###
        mc.select(instanceShpLst[2], r=True)
        mc.setAttr(instanceShpLst[1] + "|" + shpAttr + ".Ubi_High_Bound", 10)
        mc.setDrivenKeyframe(createSquash[0] + ".highBound", cd=shpAttr + ".Ubi_High_Bound")
        mc.setAttr((instanceShpLst[1] + "|" + shpAttr + ".Ubi_High_Bound"), 0)
        mc.setAttr((createSquash[0] + ".highBound"), 0)
        mc.setDrivenKeyframe(createSquash[0] + ".highBound", cd=shpAttr + ".Ubi_High_Bound")
        mc.setAttr((instanceShpLst[1] + "|" + shpAttr + ".Ubi_High_Bound"), 5)
        mc.setAttr((createSquash[0] + ".highBound"), 2)
        mc.setDrivenKeyframe(createSquash[0] + ".highBound", cd=shpAttr + ".Ubi_High_Bound")



def activeDef(shp, val):
    lDef = mc.findDeformers(shp)
    if lDef:
        for node in lDef:
            mc.setAttr(node+'.envelope', val)
#activeDef(mc.ls(sl=True), False)

def getSkin(node):
    skin = ''
    if mc.nodeType(node) == 'transform' or mc.nodeType(node) == 'mesh':
        lDef = mc.listHistory(node)
        if lDef:
            chkSkin = mc.ls(lDef, et='skinCluster') or []
            if chkSkin:
                skin = chkSkin[0]
    elif mc.nodeType(node) =='skinCluster':
        skin = node
    return skin

#getSkin(mc.ls(sl=True)[0])



def getSkindata(msh):
    dicSkin = {}
    shp = mc.listRelatives(msh, s=True, ni=True)[-1]
    lHist = mc.listHistory(shp)
    skin = mc.ls(lHist, type='skinCluster') or []
    if skin:
        dicSkin[skin[0]] = mc.skinCluster(skin[0],query=True,inf=True)
    return dicSkin
#get_skin(mc.ls(sl=True)[0])



def resetSkin(lMsh):
    for msh in lMsh:
        skin = getSkin(msh)
        lIds = mc.getAttr(skin+'.matrix', mi=True)
        for id in lIds:
            chkSk = mc.listConnections(skin+'.matrix['+str(id)+']', s=True) or []
            if chkSk:
                sk = chkSk[0]
                chkHackSkin = mc.listConnections(skin+'.bindPreMatrix['+str(id)+']', s=True) or []
                if not chkHackSkin:
                    val = mc.getAttr(sk +'.worldInverseMatrix')
                    mc.setAttr(skin+'.bindPreMatrix['+str(id)+']', type='matrix', *val)
#resetSkin(mc.ls(sl=True))

def localSkin(skin):
    for id in range(0, mc.getAttr(skin+'.matrix', s=True)):
        father = mc.listRelatives(mc.listConnections(skin+'.matrix['+str(id)+']', s=True)[0], p=True)[0]
        mc.connectAttr(father+'.worldInverseMatrix[0]', skin+'.bindPreMatrix['+str(id)+']', f=True)
#localSkin('FACIALE:skinCluster1')


def ctrlSkinLocal(lCtrl):
    for ctrl in lCtrl:
        if ('c_') in ctrl:
            sk = ctrl.replace('c_', 'sk_')
            if mc.objExists(sk):
                root = ctrl.replace('c_', 'root_')
                if mc.objExists(root):
                    lSkinPlugs = mc.listConnections(sk+".worldMatrix[0]", type="skinCluster", p=1)
                    if lSkinPlugs:
                        for skinPlug in lSkinPlugs:
                            id = skinPlug.split('[')[-1][: -1]
                            skin = skinPlug.split('.')[0]
                            mc.connectAttr(root+'.worldInverseMatrix[0]', skin+'.bindPreMatrix['+id+']', f=True)
                            print skin, 'hacked for ', ctrl
                    else:
                        mc.warning('no SKINCLUSTER found for : '+ctrl)
                else:
                    mc.warning('no ROOT found for : '+ctrl)
            else:
                mc.warning('no SK found for : '+ctrl)
        else:
            mc.warning(ctrl+' is not a controler')
#ctrlSkinLocal(mc.ls(sl=True))


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

def get_weighted_vtx_by_joint(msh, byType='sk'):
    dicSk = {}
    dicVtx = {}
    dicSkin = get_skin(msh)
    skin = dicSkin.keys()[0]
    for sk in dicSkin[skin]:
        if not sk in dicSk.keys():
            dicSk[sk] = []
        mc.select(cl=True)
        mc.skinCluster(skin, e=True, siv=sk)
        if mc.polyEvaluate(vc=True) > 0:
            lVtx = mc.ls(sl=True, fl=True)
            for vtx in lVtx:
                dicSk[sk].append(vtx)
                if not vtx in dicVtx.keys():
                    dicVtx[vtx] = []
                if not sk in dicVtx[vtx]:
                    dicVtx[vtx].append(sk)
    mc.select(cl=True)
    mc.select(msh)
    if byType == 'sk':
        return dicSk
    if byType == 'vtx':
        return dicVtx
#get_weighted_vtx_by_joint(mc.ls(sl=True)[0], byType='sk')


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


import maya.cmds as mc

def setRange(oldMin, oldMax, min, max, val):
    # DKatz
    ##be sure to give FLOAT in the arguments values -> 1.0, 3.5, 2.5, 7.0, 6.23)
    newVal = min + ((max - min) * (((val / (oldMax - oldMin)) * 100.0) / 100.0))
    return newVal
#setRange(0.0, 4.0, 0.0, 0.0799999908, 1.0)

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

def get_skin(msh):
    dicSkin = {}
    shp = mc.listRelatives(msh, s=True, ni=True)[-1]
    lHist = mc.listHistory(shp)
    skin = mc.ls(lHist, type='skinCluster') or []
    if skin:
        dicSkin[skin[0]] = mc.skinCluster(skin[0],query=True,inf=True)
    return dicSkin
#get_skin(mc.ls(sl=True)[0])

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
            lReplaceWght = 0.0
            for sk in dicWghtSrc[vtxSrc].keys():
                wght = (sk.replace(nspaceSrc, nspaceDest), dicWghtSrc[vtxSrc][sk])
                #if skSrc have replace sk value (name) it will take the weight value of the sk name
                #if skSrc have not replace sk value (name) it will take the weight value of all the sk of skinDest
                if sk in dicToReplace.keys():
                    if dicToReplace[sk]:
                        wght =  (dicToReplace[sk], dicWghtDest[vtxDest][dicToReplace[sk]])
                        if wght[-1] != 0.0:
                            lReplaceWght += wght[-1]
                    else:
                        wght = (sk.replace(nspaceSrc, nspaceDest), 0.0)
                        for skDest in dicWghtDest[vtxDest].keys():
                            wghtDest = (skDest, dicWghtDest[vtxDest][skDest])
                            lWght.append(wghtDest)
                            chkWght+=wghtDest[-1]
                lWght.append(wght)
                chkWght+=wght[-1]
            if lReplaceWght > 1.0:
                lReplaceWght = 1.0
            if not chkWght == 1.0:
                lNormWght = []
                roof = 1.0-lReplaceWght
                for wght in lWght:
                    normWght = wght
                    if wght[-1] > 0.0:
                        if not wght[0] in dicToReplace.values():
                            normWght = (wght[0], setRange(0.0, chkWght-lReplaceWght, 0.0, roof, wght[-1]))
                    lNormWght.append(normWght)
                lWght = lNormWght
            if mc.objExists(vtxDest):
                mc.skinPercent(skinDest, vtxDest, transformValue=lWght, zri=True)
    print 'done'
#tansfert_skin_by_vtx(mc.ls(sl=True)[0], mc.ls(sl=True)[-1])
#lVtxToTransfert = mc.ls(sl=True, fl=True)
#tansfert_skin_by_vtx('TMP:tmp_head', 'tmp_head', '', '',  lVtxToTransfert, {'TMP:sk_jaw': 'sk_jaw', 'TMP:sk_jawDn1':'sk_jawDn1', 'TMP:sk_jawDn2':'sk_jawDn2', 'TMP:sk_jawUp':'sk_jawUp'})#SHP:sk_headSocket
#tansfert_skin_by_vtx('TMP:tmp_head', 'tmp_head', 'TMP:', '',  mc.ls(sl=True, fl=True), {'TMP:sk_jaw': '', 'TMP:sk_jawDn1':'', 'TMP:sk_jawDn2':'', 'TMP:sk_jawUp':''})#SHP:sk_headSocket
#tansfert_skin_by_vtx(mc.ls(sl=True)[0], mc.ls(sl=True)[-1])
#tansfert_skin_by_vtx('TMP:tmp_head', 'tmp_head', '', '',  mc.ls(sl=True, fl=True), {'TMP:sk_jaw': 'sk_jaw', 'TMP:sk_jawDn1':'sk_jawDn1', 'TMP:sk_jawDn2':'sk_jawDn2', 'TMP:sk_jawUp':'sk_jawUp'})#SHP:sk_headSocket
#tansfert_skin_by_vtx('TMP:tmp_head', 'tmp_head', 'TMP:', '',  mc.ls(sl=True, fl=True), {'TMP:sk_jaw': '', 'TMP:sk_jawDn1':'', 'TMP:sk_jawDn2':'', 'TMP:sk_jawUp':''})#SHP:sk_headSocket
#tansfert_skin_by_vtx('tmp_headConvertedWght', 'MOD:msh_body', '', '',  lVtxToTransfert, {'':''})#SHP:sk_headSocket
"""

def tansfert_skin_by_vtxOld(mshSrc, mshDest, nspaceSrc, nspaceDest, lVtxToTransfert, dicToReplace):
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
"""

def combDeformedMesh(lMsh):
    dicMsh = {}
    lToComb = []
    lSk = []
    lMsh.sort()
    i = 1
    for msh in lMsh:
        if not i in dicMsh.keys():
            dicMsh[i] = {}
        vtxs = mc.polyEvaluate(msh, v=True)
        dicMsh[i]['vtxs'] = vtxs
        dicMsh[i]['skin'] = getSkindata(msh)
        dicMsh[i]['wght'] = getSkinWght(msh)
        lToComb.append(mc.duplicate(msh)[0])
        tmpLSk = dicMsh[i]['skin'][dicMsh[i]['skin'].keys()[0]]
        for sk in tmpLSk:
            if not sk in lSk:
                if mc.nodeType(sk) == 'joint':
                    lSk.append(sk)
        i += 1
    tmpGrp = mc.group(lToComb)
    mshRes = mc.polyUnite(lToComb)[0]
    mc.delete(mshRes, ch=True)
    mc.delete(tmpGrp)
    mc.select(cl=True)
    mc.select(lSk)
    mc.select(mshRes, add=True)
    skinRes = mc.skinCluster(tsb=True)[0]
    inc = 0
    for i in range(1, len(dicMsh.keys())+1):
        for vtx in dicMsh[i]['wght'].keys():
            lWght = []
            vtxId = vtx.split('[')[-1][: -1]
            newId = int(vtxId) + inc
            vtxRes = mshRes+'.vtx['+str(newId)+']'
            for sk in lSk:
                wght = (sk, 0.0)
                if sk in dicMsh[i]['wght'][vtx].keys():
                    wght = (sk, dicMsh[i]['wght'][vtx][sk])
                lWght.append(wght)
            mc.skinPercent(skinRes, vtxRes, transformValue=lWght, zri=True)
        inc += dicMsh[i]['vtxs']
    print lMsh, 'combined succesfuly',

#combDeformedMesh(mc.ls(sl=True))