import maya.cmds as mc
from functools import partial
import maya.mel as mel
from prod_presets.badgers import bdg_pipe
reload(bdg_pipe)





def getBuildPoseNode():
    lUdNodes = []
    lNodes = mc.ls('*.udAttr', r=True, o=True)
    for node in lNodes:
        if mc.objectType(node) == 'dagPose':
            lUdNodes.append(node)
    return lUdNodes
#getBuildPoseNode()

def getADVCtrl():
    lCtrl = []
    lUdNodes = getBuildPoseNode()
    for udNode in lUdNodes:
        udPoseAttr = mc.getAttr(udNode+'.udAttr')
        trunkAttr = udPoseAttr.split(';')
        for i in trunkAttr:
            if not i.startswith('setAttr'):
                if not '.' in i:
                    ctrl = i.split(' ')[-1]
                    lCtrl.append(ctrl)
    return lCtrl
#getADVCtrl()

#__DISPLAY__############################################################################################################
def set_joint_draw(state=2):
    lSk = mc.ls(type='joint', allPaths=True) or []
    for sk in lSk:
        if not mc.listConnections(sk + '.drawStyle', connections=True, destination=True, source=False):
            if not mc.getAttr(sk + '.drawStyle', lock=True):
                mc.setAttr(sk + '.drawStyle', state)

def hide_ctrl_hist():
    lNodes = mc.ls()
    for node in lNodes:
        try:
            if not mc.attributeQuery('nodeType', n=node, ex=True):
                mc.setAttr(node + '.isHistoricallyInteresting', 0)
            elif not mc.getAttr(node + '.nodeType') == 'control':
                mc.setAttr(node + '.isHistoricallyInteresting', 0)
        except:
            print node + '.isHistoricallyInteresting is lock'

def hideCurvesAttr():
    lCrv = mc.ls(type='nurbsCurve', r=True)
    for crv in lCrv:
        lAttrs = mc.listAttr(crv) or []
        lUserAttrs = mc.listAttr(crv, ud=True) or []
        lDefaultAttrs = lAttrs
        if lUserAttrs:
            lDefaultAttrs = list(set(lAttrs)-set(lUserAttrs))
        for attr in lDefaultAttrs:
            if '.' in attr:
                pass
            else:
                #mc.setAttr(obj+'.'+attr, l=True, k=False, cb=False)
                mc.setAttr(crv + '.' + attr, k=False, cb=False)
#HiddeAttributShape('WORLD:curveShape2')

def lock_shapes_and_smooth():
    topNode = mc.ls(type='transform')[0]
    lMsh = mc.ls(type = 'mesh')
    if not mc.attributeQuery('lockMesh', n=topNode, ex=True):
        mc.addAttr(topNode, ln='lockMesh', at='enum', en='Unlock:Lock', dv=1)
    lOldTopNode = mc.ls('*.lockMesh', type='transform') or []
    for oldTopNode in lOldTopNode:
        mc.connectAttr(topNode+'.lockMesh', oldTopNode, f=True)
    for msh in lMsh:
        if not mc.isConnected(topNode+'.lockMesh', msh +'.overrideEnabled'):
            mc.connectAttr(topNode+'.lockMesh', msh +'.overrideEnabled')
        mc.setAttr(msh + '.overrideDisplayType', 2)
        for attr in ['.displaySubdComps', '.smoothLevel', '.useSmoothPreviewForRender']:
            mc.setAttr(msh+attr, lock=True)

def hiddeNurbs():
    lNurbs = mc.ls(type='nurbsSurface', long=True)
    for node in lNurbs:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])

def hiddeCurves():
    lCrv = mc.ls(type='nurbsCurve', long=True)
    for node in lCrv:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])

def remove_unkowPlugNodes():
    lUnknowPlugs = mc.unknownPlugin(q=True, l=True) or []
    if lUnknowPlugs:
        for plug in lUnknowPlugs:
            mc.unknownPlugin(plug, r=True)

def remove_plugNodes(lPlugs=['Turtle', 'mtoa', 'stereoCamera']):
    lActivePlugs = mc.pluginInfo(query=True, listPlugins=True)
    for plug in lPlugs:
        if plug in lActivePlugs:
            lTypesNode = mc.pluginInfo(plug, query=True, dn=True) or []
            if lTypesNode:
                remove_nodes(lTypesNode)
                for type in lTypesNode:
                    lNodes = mc.ls(type=type) or []
                    if lNodes:
                        for node in lNodes:
                            mc.lockNode(node, lock=False)
                            mc.delete(node)
            mc.flushUndo()
            mc.unloadPlugin(plug)
    remove_unkowPlugNodes()
#remove_plugNodes(['Turtle', 'mtoa'])

def remove_nodes(lTypesNode=['displayLayer', 'nodeGraphEditorInfo', 'animLayer', 'unknown'], lToKeep=['defaultLayer']):
    for typeNode in lTypesNode:
        lNodes = mc.ls(type=typeNode)
        for toKeep in lToKeep:
            if toKeep in lNodes:
                lNodes.remove(toKeep)
        for node in lNodes:
            if mc.objExists(node):
                mc.lockNode(node, lock=False)
                lConn = mc.listConnections(node, c=True, p=True, s=True, d=True) or []
                if lConn:
                    for i in range(1, len(lConn)):
                        if mc.isConnected(lConn[i], lConn[i-1]):
                            mc.disconnectAttr(lConn[i], lConn[i-1])
                        elif mc.isConnected(lConn[i-1], lConn[i]):
                            mc.disconnectAttr(lConn[i-1], lConn[i])
                        i += 2
                #print 'deleting :', node
                mc.delete(node)
#remove_nodes(['displayLayer', 'nodeGraphEditorInfo'], ['defaultLayer'])

def remTrash():
    #list tout les nodes (et leur enfants) a suprimer
    lNodes = mc.ls('*.deleteMe', o=True, r=True)
    if lNodes:
        print 'here are the nodes with a DELETEME :', lNodes
        for node in lNodes:
            if mc.objExists(node):
                if mc.getAttr(node+'.deleteMe') == 1:
                    mc.lockNode(node, lock=False)
                    mc.delete(node)

def comparObj(objSrc, objDest):
    if objSrc.split(':')[-1] == objDest.split(':')[-1]:
        return 1
    else:
        return 0

def recurseHi(objSrc, objDest, do, dicHi):
    lChildSrc = mc.listRelatives(objSrc, c=True, s=False) or []
    lChildDest = mc.listRelatives(objDest, c=True, s=False) or []
    if lChildDest :
        if lChildSrc :
            for childDest in lChildDest:
                for childSrc in lChildSrc:
                    do = comparObj(childSrc, childDest)
                    if do == 1:
                        recurseHi(childSrc, childDest, do, dicHi)
                    else:
                        if not  objSrc in dicHi.keys():
                            dicHi[objSrc] = []
                        if not childDest in dicHi[objSrc]:
                            dicHi[objSrc].append(childDest)
    return dicHi

def makeHi(father, lChildren):
    for child in lChildren:
        mc.parent(child, father)

def addFlagAttr(nAttr, val):
    lNodes = mc.ls(sl=True)
    dicColor = {}
    dicColor['deleteMe'] = [1, 0, 0]
    dicColor['cleanMe'] = [1, .225, 0]
    dicColor['rigMe'] = [1, 1, 0]
    dicColor['skipMe'] = [0, 1, 0]
    for node in lNodes:
        if not mc.attributeQuery(nAttr, n=node, ex=True):
            lock = False
            if mc.lockNode(node, q=True, lock=True)[0] == True:
                mc.lockNode(node, lock=False)
                lock = True
            mc.addAttr(node, ln=nAttr, at='bool', dv=1, k=False)
            if lock == True:
                mc.lockNode(node, lock=True)
        mc.setAttr(node+'.'+nAttr, val)
        mc.setAttr(node+'.useOutlinerColor',val)
        mc.setAttr(node+'.outlinerColor', *dicColor[nAttr])

def hiFusion(nspaceKeeped):
    lBoxs = getAllBoxs()
    masterBox = getAssetBox()
    for box in lBoxs:
        if box.split(':')[0] == nspaceKeeped:
            masterBox = box
    if masterBox in lBoxs:
        lBoxs.remove(masterBox)
    for box in lBoxs:
        addFlagAttr('deleteMe', True)(box)
        nspaceBox = ':'
        if ':' in box:
            nspaceBox = box.split(':')[0]
        dicHi = compareHi(masterBox, box, nspaceKeeped+':', nspaceBox+':')
        for key in dicHi.keys():
            for father in dicHi[key].keys():
                for child in dicHi[key][father]:
                    if mc.objExists(father):
                        if mc.objExists(child):
                            #print 'try fathering', child, 'to',  father
                            try:
                                mc.parent(child, father)
                            except:
                                #print 'TA MERE', child, father
                                pass
    remTrash()
#hiFusion('MOD')

def convertName(name, toReplace, new):
    trunc = name.split('|')
    newName = ''
    for stick in trunc:
        if stick != '':
            if not toReplace in stick:
                newName = newName+'|'+new+stick
            elif toReplace in stick:
                newStick = stick.replace(toReplace, new)
                newName = newName+'|'+newStick
    return newName
#convertName('|ALL|GEO|geo_head|geo_lashes_R|msh_lash2_R', ':', 'MOD:')

def compareHi(hiSrc, hiToCHk, nspaceSrc, nspaceToSwitch):
    lChild = mc.listRelatives(hiToCHk, ad=True, f = True, type = 'transform') or []
    dicHi = {}
    if lChild:
        for child in lChild:
            childDest = convertName(child, nspaceToSwitch, nspaceSrc)
            if not mc.objExists(childDest):
                father = mc.listRelatives(child, p=True)[0]
                fatherDest = convertName(father, nspaceToSwitch, nspaceSrc).split('|')[-1]
                if not mc.objExists(fatherDest):
                    fatherDest = father
                deep = len(child.split('|'))
                if not deep in dicHi.keys():
                    dicHi[deep] = {}
                if not fatherDest in dicHi[deep].keys():
                    dicHi[deep][fatherDest] = []
                dicHi[deep][fatherDest].append(child)
    return dicHi
#compareHi('MOD:ALL', 'ALL', 'MOD:', ':')

def cleanRefEdits(refNode):
    lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
    mc.file(ur=refNode)
    if lEdits:
        for edit in lEdits:
            action = edit.split('|')[0]
            mc.file(cr=refNode, editCommand=action)

def removeRef(ref):
    refNode = mc.referenceQuery(ref, rfn=True)
    nSpace = mc.referenceQuery(ref, ns=True)
    print ref, 'nspaces are :', nSpace
    cleanRefEdits(refNode)
    mc.file(ref, rr=True)
    if mc.namespace(ex=':'+nSpace):
        mc.namespace(rm=nSpace)

def refCleaner_v2(dicRef):
    for ref in dicRef['importe']:
        mc.file(ref, ir=True, mnr=False)
    for ref in dicRef['remove']:
        if ref:
            removeRef(ref)
#refCleaner( mc.file(q=True, sceneName=True), lib_names.refNspaceNames())

def getAssetBox():
    lCam = mc.listCameras()
    lTopNodes = mc.ls(assemblies=True)
    box = ''
    for node in lTopNodes:
        remove = 0
        if mc.referenceQuery( node, isNodeReferenced=True ):
            remove = 1
        if mc.attributeQuery('deleteMe', n=node, ex=True):
            if mc.getAttr(node+'.deleteMe') == 1:
                remove = 1
        if node in lCam :
            remove = 1

        if remove == 0:
            box = node
            break
    return box
#getAssetBox()

def getAllBoxs():
    lCam = mc.listCameras()
    lTopNodes = mc.ls(assemblies=True)
    lBox = []
    for node in lTopNodes:
        remove = 0
        if node in lCam:
            remove = 1
        if not ':' in node:
            if mc.attributeQuery('deleteMe', n=node, ex=True):
                if mc.getAttr(node+'.deleteMe') == 1:
                    remove = 1
        if remove == 0:
            lBox.append(node)
    return lBox


def getRefBoxs():
    lNspace = []
    lBoxs = []
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True)
    for ref in lRef:
        refNode = mc.referenceQuery(ref, rfn=True)
        nSpace = mc.referenceQuery(ref, ns=True)
        lNspace.append(nSpace)
    lTopNodes = mc.ls(assemblies=True)
    for node in lTopNodes:
        if ':' in node:
            lBoxs.append(node)
    return lBoxs


def cleanForSnap(*args):
    fDatas = bdg_pipe.fileDatas()
    scnTask = fDatas.getSncTask()
    if scnTask == fDatas.build:
        print scnTask
    else:
        assetType = fDatas.getScnType()
        if assetType == fDatas.chr:
            print 'et merde'
            remTrash()
            #hiFusion(nspaceKeeped)
            set_joint_draw()
            lock_shapes_and_smooth()
            #hiddeNurbs()
            remove_plugNodes(lPlugs=['Turtle','stereoCamera'])
            remove_nodes(lTypesNode=['displayLayer', 'nodeGraphEditorInfo', 'animLayer', 'unknown'], lToKeep=['defaultLayer'])
            saveNewRev()




def saveNewRev(*args):
    fDatas = bdg_pipe.fileDatas()
    fileName = fDatas.fileName
    inc = fDatas.getInc()
    updateInc = str(int(inc)+1)
    newInc = inc[: len(inc)-len(updateInc)]+updateInc
    newName = fileName.replace('__v'+str(inc), '__v'+str(newInc))
    mc.file(fileName, rn=newName)
    mc.file(save=True)
    print fileName.split('/')[-1], 'incremented to :', newName.split('/')[-1],



def initRigScene(lJnt, *args):
    mel.eval('source "R:/__REZ_REPOSITORIES__/PLUGIN/advanced_skeleton/5.795/AdvancedSkeleton5.mel";')
    mel.eval('AdvancedSkeleton5;')
    for jnt in lJnt:
        mc.joint(n=jnt)
    mc.select(lJnt[0])
    mel.eval('asReBuildAdvancedSkeleton;')
#initRigScene(['Root', 'RootEnd'])
"""
mel.eval('loadAdvancedSkeleton()')
"""




#TWEAK LEGS###############################################################
def crtRigAdd(lBones, ikCtrl, rollToes, lPv, nAttr):
    print lBones, ikCtrl, rollToes, nAttr
    if not mc.attributeQuery(nAttr, n=ikCtrl, ex=True):
        mc.addAttr(ikCtrl, ln=nAttr, min=0.0, max=10.0, at='float', k=True, dv=5)
    lJnt = []
    father = mc.listRelatives(lBones[0], p=True)
    side = lBones[0].split('_')[-1]
    for node in lBones:
        nPart = node.split('_')[0].replace('IKX', '')
        mc.select(cl=True)
        if not mc.objExists('jnt_add'+nPart+'_'+side):
            jnt = mc.joint(n='jnt_add'+nPart+'_'+side)
            mc.setAttr(jnt+'.drawStyle', 2)
            lJnt.append(jnt)
            mc.parent(jnt, node)
            for attr in ['translate', 'rotate', 'jointOrient']:
                for chan in ['X', 'Y', 'Z']:
                    mc.setAttr(jnt+'.'+attr+chan, 0.0)
        else:
            lJnt.append('jnt_add'+nPart+'_'+side)
    if not mc.objExists('ikAdd_ankle_'+side):
        mc.parent(lJnt[1], lJnt[0])
        mc.parent(lJnt[2], lJnt[1])
        mc.parent(lJnt[0], father)
        ikAdd = mc.ikHandle(n='ikAdd_ankle_'+side, sj=lJnt[0], ee=lJnt[-1], sol='ikRPsolver')[0]
        mc.parent(ikAdd, ikCtrl)
        mc.setAttr(ikAdd+'.v', False)
        mc.poleVectorConstraint(lPv, ikAdd)
    nMDL = 'mDL_addAnkle_'+side
    mDL = nMDL
    nMDLNorm = 'mDLNorm_addAnkle_'+side
    mDLNorm = nMDLNorm
    nClmp = 'clmp_addAnkle_'+side
    clmp = nClmp
    if not mc.objExists(nMDL):
        mDL = mc.createNode('multDoubleLinear', n=nMDL)
        mc.addAttr(mDL, ln='fixeMeIfYouCan', at='bool')
    mc.connectAttr(lJnt[1]+'.rotateX', mDL+'.input1', f=True)
    if not mc.objExists(nMDLNorm):
        mDLNorm = mc.createNode('multDoubleLinear', n=nMDLNorm)
    mc.setAttr(mDLNorm+'.input2', 0.1)
    mc.connectAttr(ikCtrl+'.'+nAttr, mDLNorm+'.input1', f=True)
    mc.connectAttr(mDLNorm+'.output', mDL+'.input2', f=True)
    if not mc.objExists(nClmp):
        clmp = mc.createNode('clamp', n=nClmp)
    mc.connectAttr(mDL+'.output', clmp+'.inputR', f=True)
    mc.connectAttr(mDL+'.output', clmp+'.minR', f=True)
    mc.connectAttr(clmp+'.outputR', rollToes+'.rotateX', f=True)

#crtRigAdd(mc.ls(sl=True))



def tweakIt(ikField, bonesField, destField):
    ikCtrl = mc.textField(ikField, q=True, tx=True)
    rollToesCtrl = mc.textField(destField, q=True, tx=True)
    lPv = []
    if ikCtrl:
        if rollToesCtrl:
            dest = mc.listRelatives(rollToesCtrl, p=True)[0]
            lIk = mc.listRelatives(rollToesCtrl, ad=True, type='ikHandle') or []
            if lIk:
                ikHdl = lIk[0]
                for ik in lIk:
                    pos = mc.xform(ik, ws=True, q=True, t=True)
                    if mc.xform(ik, ws=True, q=True, t=True)[1] > mc.xform(ikHdl, ws=True, q=True, t=True)[1]:
                        ikHdl = ik

                stJnt = mc.ikHandle(ikHdl, q=True, sj=True)
                eff = mc.ikHandle(ikHdl, q=True, ee=True)
                lBones = mc.ikHandle(ikHdl, q=True, jl=True)
                endJnt = mc.listRelatives(lBones[-1], c=True, type='joint')[0]
                lBones.append(endJnt)
                pvCnst = mc.poleVectorConstraint(ikHdl, q=True)
                if pvCnst:
                    lPv = mc.poleVectorConstraint(pvCnst, q=True, tl=True)
                crtRigAdd(lBones, ikCtrl, dest, lPv, 'ankleAimSDK')
    print 'leg', ikCtrl, 'fixed',




def loadSel(type):
    lNodes = mc.ls(sl=True)
    if type == 'IK':
        if mc.nodeType(lNodes[0]) == 'transform':
            if mc.listRelatives(lNodes[0], s=True):
                mc.textField('BDG_ctrlIK', e=True, tx=str(lNodes[0]))
            else:
                mc.warning('wrong selection :', lNodes)
        else:
            mc.warning('wrong selection :', lNodes)

    elif type == 'DEST':
        if mc.nodeType(lNodes[0]) == 'transform':
            if mc.listRelatives(lNodes[0], s=True):
                mc.textField('BDG_nodeToTweak', e=True, tx=lNodes[0])
            else:
               mc.warning('wrong selection :', lNodes)
        else:
            mc.warning('wrong selection :', lNodes)



def fixAxes():
    axe = mc.optionMenu('orienTwekFixe', q=True, v=True)
    lNodes = mc.ls('*.fixeMeIfYouCan', o=True) or []
    if lNodes:
        for node in lNodes:
            src = mc.listConnections(node+'.input1', s=True, d=False, scn=True) or []
            if src:
                print src
                mc.connectAttr(src[0]+'.rotate'+axe, node+'.input1', f=True)
                print src[0], 'tweaked to', axe



def smoothSDK(*arg):
    val = mc.floatSliderGrp('SDKSmoothSlider', q=True, value=True)*.01
    lNodes = mc.ls('*.fixeMeIfYouCan', o=True) or []
    if lNodes:
        for node in lNodes:
            nomrNode = mc.listConnections(node+'.input2', s=True) or []
            if nomrNode:
                mc.setAttr(nomrNode[0]+'.input2', val)
#TOOLS#############################################################
def addClst(lCtrl):
    mc.select(cl=True)
    for ctrl in lCtrl:
        clearName = ctrl
        if ':' in ctrl:
            clearName = ctrl.split(':')[-1]
        nClst = 'clst'+clearName[len(clearName.split('_')[0]):]
        clts = mc.deformer(n=nClst, type='cluster')[0]
        mc.connectAttr(ctrl+'.worldMatrix[0]', clts+'.matrix')
        mc.connectAttr(ctrl+'.parentInverseMatrix', clts+'.bindPreMatrix')
        mc.connectAttr(ctrl+'.matrix', clts+'.weightedMatrix')
        mc.connectAttr(ctrl+'.parentMatrix', clts+'.preMatrix')
    mc.select(lCtrl)

#addClst(mc.ls(sl=True))



def getSkin(node):
    skin = ''
    if mc.nodeType(node) == 'transform' or mc.nodeType(node) == 'mesh':
        lDef = mc.listHistory(node)
        if lDef:
            skin = mc.ls(lDef, et='skinCluster')[0]
    elif mc.nodeType(node) =='skinCluster':
        skin = node
    return skin

#getSkin(mc.ls(sl=True)[0])


def getAvalableId(node, attr):
    lastId = 0
    lIds = mc.getAttr(node+'.'+attr, mi=True) or []
    if lIds:
        lastId = lIds[-1]+1
    return lastId


def crtSoftMod(lNodes):
    deformedNode = ''
    lDrivers = []
    if lNodes:
        for node in lNodes:
            type = mc.objectType(node)
            if type in ['transform', 'joint']:
                shp = mc.listRelatives(node, s=True, ni=True) or []
                if shp:
                    if mc.objectType(shp[0]) in ['mesh', 'nurbsSurface']:
                        deformedNode = node
                    else:
                        lDrivers.append(node)
                else:
                    lDrivers.append(node)
            elif type in ['mesh', 'nurbsSurface']:
                deformedNode = node
    elif not lNodes:
        lDrivers.append('na_softMod')

    if not deformedNode:
        nDefNode = 'tmp_deformersMesh'
        lChk = mc.ls('*'+nDefNode, r=True) or []
        if not lChk:
            deformedNode = mc.polyPlane(n=nDefNode, sw=1, sh=1, sx=1, sy=1)[0]
        else:
            deformedNode = lChk[0]

    for driver in lDrivers:
        baseName = driver
        if ':' in driver:
            baseName = driver.split(':')[-1]
        side = ''
        if baseName.endswith('_L') or baseName.endswith('_R'):
            side = '_'+baseName.split('_')[-1]
            baseName = baseName[len(baseName.split('_')[0]):(len(baseName)-len(baseName.split('_')[-1])-1)]

        baseName = baseName[len(baseName.split('_')[0]):]+'Sft'
        smfRootOrt = mc.createNode('transform', n='root'+baseName+'Ort'+side)
        dMOrt = mc.createNode('decomposeMatrix', n='dM'+baseName+'Ort'+side)
        avgSclOrt = mc.createNode('plusMinusAverage', n='avg'+baseName+'Ort'+side)
        mDLOrt = mc.createNode('multDoubleLinear', n='mDL'+baseName+'Ort'+side)
        mc.connectAttr(smfRootOrt+'.worldMatrix[0]', dMOrt+'.inputMatrix')
        mc.connectAttr(dMOrt+'.outputScaleX', avgSclOrt+'.input1D[0]', f=True)
        mc.connectAttr(dMOrt+'.outputScaleY', avgSclOrt+'.input1D[1]', f=True)
        mc.connectAttr(dMOrt+'.outputScaleZ', avgSclOrt+'.input1D[2]', f=True)
        mc.connectAttr(avgSclOrt+'.output1D', mDLOrt+'.input1', f=True)
        mc.setAttr(avgSclOrt+'.operation', 3)
        if mc.objExists(driver):
            mc.parent(smfRootOrt, driver)
        smfCtrlOrt = mc.createNode('transform', n='c'+baseName+'Ort'+side, p=smfRootOrt)

        smfRootSlide = mc.createNode('transform', n='root'+baseName+'Slide'+side, p=smfCtrlOrt)
        smfCtrlSlide = mc.createNode('transform', n='c'+baseName+'Slide'+side, p=smfRootSlide)

        smfRoot = mc.createNode('transform', n='root'+baseName+side, p=smfCtrlSlide)
        smfCtrl = mc.createNode('transform', n='c'+baseName+side, p=smfRoot)


        sfMod = mc.deformer(deformedNode, n='sfM'+baseName+side, type='softMod')[0]
        dM = mc.createNode('decomposeMatrix', n='dM'+baseName+side)


        mc.addAttr(smfCtrl, ln='sftRadius', k=True, at='double', dv=5)
        mc.addAttr(smfCtrl, ln='sftMode', k=True, at='enum', en='volume:surface:', dv=1)

        mc.connectAttr(smfCtrl+'.parentMatrix', dM+'.inputMatrix')
        mc.connectAttr(smfCtrl+'.worldMatrix[0]', sfMod+'.matrix')
        mc.connectAttr(smfCtrl+'.parentInverseMatrix', sfMod+'.bindPreMatrix')
        mc.connectAttr(smfCtrl+'.matrix', sfMod+'.weightedMatrix')
        mc.connectAttr(smfCtrl+'.parentMatrix', sfMod+'.preMatrix')
        mc.connectAttr(dM+'.outputTranslate', sfMod+'.falloffCenter')
        mc.connectAttr(smfCtrl+'.sftRadius', mDLOrt+'.input2')
        mc.connectAttr(mDLOrt+'.output', sfMod+'.falloffRadius')
        mc.connectAttr(smfCtrl+'.sftMode', sfMod+'.falloffMode')

        for node in [smfCtrlOrt, smfCtrlSlide, smfCtrl]:
            if not mc.attributeQuery('deformersList', n=node, ex=True):
                mc.addAttr(node, ln='deformersList', at='message', multi=True)
            id = getAvalableId(node, 'deformersList')
            mc.connectAttr(sfMod+'.message', node+'.deformersList['+str(id)+']')

        val = 0
        for attr in ['translate', 'rotate', 'scale']:
            if attr == 'scale':
                val = 1
            for chan in [attr+'X', attr+'Y', attr+'Z']:
                mc.setAttr(smfRootOrt+'.'+chan, val)

#crtSoftMod(mc.ls(sl=True))


def resetSkin(lMsh):
    for msh in lMsh:
        skin = getSkin(msh)
        lIds = mc.getAttr(skin+'.matrix', mi=True)
        for id in lIds:
            sk = mc.listConnections(skin+'.matrix['+str(id)+']', s=True)[0]
            chkHackSkin = mc.listConnections(skin+'.bindPreMatrix['+str(id)+']', s=True) or []
            if not chkHackSkin:
                val = mc.getAttr(sk +'.worldInverseMatrix')
                mc.setAttr(skin+'.bindPreMatrix['+str(id)+']', type='matrix', *val)
#resetSkin(mc.ls(sl=True))


def BDG_rigCharacterAdd_UI():
    nWin = 'BDG_rigTool'
    nPan = 'BDG_masterPan'
    #nFomLay = 'SMAB_formLayout'

    version ='1.1.1'

    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winBDG_rigCharacterAdd_UI = mc.window(nWin, t='BDG Tools'+version, tlb=True)

    mBar = mc.menuBarLayout('BDG_mBar')
    mc.menu(l='File', to=True)
    mc.menuItem(divider=True, l='Init')
    mc.menuItem(l='Init build', c=partial(initRigScene, ["Root", "RootEnd"]))
    mc.menuItem(divider=True, l='Saves')
    mc.menuItem(l='Save new revision', c=partial(saveNewRev))
    mc.menuItem(divider=True, l='Clean')
    mc.menuItem(l='Clean for snap', c=partial(cleanForSnap))
    pan = mc.paneLayout(nPan, cn='single')


    mc.tabLayout()
    mc.columnLayout('Tools', adj=True)
    mc.frameLayout(l='Utils', cll=True, bv=True, bgc=[.5, .5, .2], bgs=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='add deleteMe', h=28, w=130, c=partial(addFlagAttr, "deleteMe", 1))
    mc.button(l='remove deleteMe', h=28, w=130, c=partial(addFlagAttr, "deleteMe", 0))


    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='Deformers', cll=True, bv=True, bgc=[.2, .3, .5], bgs=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='add cluster', h=28, w=130, c=partial(addClst, mc.ls(sl=True)))
    mc.button(l='add softMod', h=28, w=130, c=partial(crtSoftMod, mc.ls(sl=True)))
    mc.setParent('..')
    #mc.rowLayout(nc=2, adj=2)
    mc.button(l='reset skin sss', h=28, w=130, c=partial(resetSkin, mc.ls(sl=True)))
    #mc.button(l='hack ctrl skin', h=28, w=130, c='tools_smab_v3.lib_deformers.ctrlSkinLocal(mc.ls(sl=True))')

    mc.button(l='teste', h=28, w=130, c='')




    #mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout('Tweak Legs', adj=True)
    mc.separator(h=5, st="in")
    mc.frameLayout(label='ctrl IK', fn='fixedWidthFont', bgc=[.4, .4, .4])
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='load ctrlIK', c='loadSel("IK")')
    mc.textField('BDG_ctrlIK', en=False)


    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.frameLayout(label='node to update', fn='fixedWidthFont', bgc=[.4, .4, .4])
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='load toesRool ctrl', c='loadSel("DEST")')
    mc.textField('BDG_nodeToTweak', en=False)

    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.button(l='build', c='tweakIt("BDG_ctrlIK", "BDG_jntlIK", "BDG_nodeToTweak")')
    mc.showWindow(winBDG_rigCharacterAdd_UI)

    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.frameLayout(label='fixe orient axe', fn='fixedWidthFont', bgc=[.4, .4, .4])
    mc.rowLayout(nc=2, adj=2)
    mc.optionMenu('orienTwekFixe', label='Switch axe to:')
    mc.menuItem( label='X')
    mc.menuItem( label='Y')
    mc.menuItem( label='Z')
    mc.button(l='Fixe it', c='fixAxes()')

    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.frameLayout(label='fixe orient axe', fn='fixedWidthFont', bgc=[.4, .4, .4])
    mc.floatSliderGrp('SDKSmoothSlider', label='rerange SDK', min=0, max=10, value=5, step=1, field=True, cc=partial(smoothSDK), cl3=['left', 'left', 'left'])
    mc.separator(h=5, st="in")

#BDG_rigCharacterAdd_UI()
