import sys
import os
#customPath = 'C:\\STUFF'
#pathCustom ='T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig'
srcDgMenuToolsPath = os.path.realpath(__file__)
dgMenuToolsPath = srcDgMenuToolsPath.replace(srcDgMenuToolsPath.split('ellipse_rig')[-1], '')
sys.path.append(dgMenuToolsPath)

import tools_dagMenu
reload(tools_dagMenu)

import maya.cmds as mc
import maya.mel as mel
from functools import partial
import math

########################################
#NURBS ATTACH
def getNearestTrans(trs, lObj):
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


def getAvalableId(node, attr):
    lastId = 0
    lIds = mc.getAttr(node+'.'+attr, mi=True) or []
    if lIds:
        lastId = lIds[-1]+1
    return lastId


def crtPOMI(shp, cPOM, i):
    nPOMI=i.replace(i.split('_')[0], "pOMI")
    if not mc.objExists(nPOMI):
        mc.createNode('pointOnMeshInfo', name=nPOMI)
    if not mc.isConnected (shp+'.outMesh', nPOMI+'.inMesh'):
        mc.connectAttr(shp+'.outMesh', nPOMI+'.inMesh', f=True)
    mc.setAttr(nPOMI+'.relative', 0)
    mc.connectAttr(cPOM+'.parameterU', nPOMI+'.parameterU', f=True)
    mc.disconnectAttr(cPOM+'.parameterU', nPOMI+'.parameterU')
    mc.connectAttr(cPOM+'.parameterV', nPOMI+'.parameterV', f=True)
    mc.disconnectAttr(cPOM+'.parameterV', nPOMI+'.parameterV')
    mc.connectAttr(cPOM+'.closestFaceIndex', nPOMI+'.faceIndex', f=True)
    mc.disconnectAttr(cPOM+'.closestFaceIndex', nPOMI+'.faceIndex')
    return nPOMI

def getNearestCompId(cPOM, root, type):
    pos = mc.xform(root, q=True, ws=True, t=True)
    mc.setAttr(cPOM+'.inPosition', *pos)
    id = mc.getAttr(cPOM+'.closestFaceIndex')
    if type == 'vtx':
        id = mc.getAttr(cPOM+'.closestVertexIndex')
    if type == 'edg':
        id = mc.getAttr(cPOM+'.closestVertexIndex')
    return id

def getEdges(facet):
    lEdg=['', '']
    getEdg = mc.ls(mc.polyListComponentConversion(facet, ff=True, te=True), fl=True)
    lVtx=mc.ls(mc.polyListComponentConversion(facet, ff=True, tv=True), fl=True)
    if len(getEdg) == 4:
        lEdg[0] = getEdg[0]
        lVtxBase = mc.ls(mc.polyListComponentConversion(lEdg[0], fe=True, tv=True), fl=True)
        lVtxEnd = list(set(lVtx)-set(lVtxBase))
        lEdg[1] = mc.polyListComponentConversion(lVtxEnd[0], lVtxEnd[1], fv=True, te=True, internal=True)
    elif len(getEdg) == 3:
        mc.warning('the face '+facet+' have LESS than 4 sides')
    elif len(getEdg) > 4:
        mc.warning('the face '+facet+' have MORE than 4 sides')
    return lEdg


def attachOnNbs (nbs, i, nodeToConnect, doLoc=False):
    #NAMES
    nSa = i.replace(':root_', ':sa_')
    nPOSI = i.replace(':root_', ':pOSI_')
    nFBFMat = i.replace(':root_', ':fBfM_')
    nMltMat = i.replace(':root_', ':mltM_')
    nDMat = i.replace(':root_', ':dM_')
    nCPOS = i.replace(':root_', ':cPOS_')
    nLoc = i.replace(':root_', ':tmp_')
    #CREATE NODE
    sa = mc.createNode('transform', n=nSa)
    pOSI = mc.createNode('pointOnSurfaceInfo', n=nPOSI)
    fBFMat = mc.createNode('fourByFourMatrix', n=nFBFMat)
    mltMat = mc.createNode('multMatrix', n=nMltMat)
    dMat = mc.createNode('decomposeMatrix', n=nDMat)
    cPOS =  mc.createNode('closestPointOnSurface', n=nCPOS)
    #CONNECTIONS
    #connect le nurbs to the pOSI
    shp= mc.listRelatives(nbs, s=True)[0]
    if nodeToConnect == None:
        mc.connectAttr(shp + '.worldSpace', pOSI + '.inputSurface', f=True)
    else:
        mc.connectAttr(nodeToConnect, pOSI + '.inputSurface', f=True)
    #connect le pointOnSurfaceInfo au fourByfourMatrix
    mc.connectAttr(pOSI+'.normalizedNormalX', fBFMat+'.in10', f=True)
    mc.connectAttr(pOSI+'.normalizedNormalY', fBFMat+'.in11', f=True)
    mc.connectAttr(pOSI+'.normalizedNormalZ', fBFMat+'.in12', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentUX', fBFMat+'.in00', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentUY', fBFMat+'.in01', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentUZ', fBFMat+'.in02', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentVX', fBFMat+'.in20', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentVY', fBFMat+'.in21', f=True)
    mc.connectAttr(pOSI+'.normalizedTangentVZ', fBFMat+'.in22', f=True)
    mc.connectAttr(pOSI+'.positionX', fBFMat+'.in30', f=True)
    mc.connectAttr(pOSI+'.positionY', fBFMat+'.in31', f=True)
    mc.connectAttr(pOSI+'.positionZ', fBFMat+'.in32', f=True)
    #connect le fourByfourMatrix au multMatrix
    mc.connectAttr(fBFMat+'.output', mltMat+'.matrixIn[0]', f=True)
    #connect le multMatrix au decomposeMatrix
    mc.connectAttr(mltMat+'.matrixSum', dMat+'.inputMatrix', f=True)
    #connect le null au multMatrix
    mc.connectAttr(sa+'.parentInverseMatrix', mltMat+'.matrixIn[1]', f=True)
    #connect le decomposeMatrix au null
    mc.connectAttr(dMat+'.outputRotate', sa+'.r', f=True)
    mc.connectAttr(dMat+'.outputTranslate', sa+'.t', f=True)
    #LOCATOR

    loc = mc.spaceLocator(n=nLoc)[0]
    shpLoc = mc.listRelatives(loc, s=True)[0]
    mc.parent(shpLoc, sa, s=True, r=True)
    mc.delete(loc)


    mc.addAttr(sa, ln='U', at='double', dv= 0.5)
    mc.setAttr(sa+'.U', e=True, keyable=True)
    mc.addAttr(sa, ln='V', at='double', dv=0.5)
    mc.setAttr(sa+'.V', e=True, keyable=True )
    mc.connectAttr(sa+'.U', pOSI+'.parameterU', f=True)
    mc.connectAttr(sa+'.V', pOSI+'.parameterV', f=True)
    #CLOSETS POINT ON SURFACE
    mc.createNode('closestPointOnSurface', n=cPOS)
    mc.connectAttr(shp+'.worldSpace[0]', cPOS+'.inputSurface', f=True)
    mc.connectAttr(i+'.t', cPOS+'.inPosition', f=True)
    mc.connectAttr(cPOS+'.parameterU', sa+'.U', f=True)
    mc.connectAttr(cPOS+'.parameterV', sa+'.V', f=True)
    mc.disconnectAttr(cPOS+'.parameterU', sa+'.U')
    mc.disconnectAttr(cPOS+'.parameterV', sa+'.V')
    mc.delete(cPOS)
    if doLoc == False:
        mc.delete(shpLoc)
    mc.parent(i, sa)
    for attr in ['translate', 'rotate', 'scale']:
        val = 0
        if attr == 'scale' :
            val = 1
        for chan in ['X', 'Y', 'Z']:
            mc.setAttr(i+'.'+attr+chan, val)
    return sa



def crtSurfAttach(lSel, nNbsGrp, nSaGrp, sfMod):
    lRoot = []
    path = {}
    if not mc.objExists(nSaGrp):
        mc.createNode('transform', n=nSaGrp)
    if not mc.objExists(nNbsGrp):
        mc.createNode('transform', n=nNbsGrp)
        mc.setAttr(nNbsGrp+'.v', False)
        mc.parent(nNbsGrp, nSaGrp)


    for sel in lSel:
        selType = mc.nodeType(sel)
        if selType == 'transform':
            chkShp = mc.listRelatives(sel, s=True, ni=True) or []
            if chkShp:
                if mc.nodeType(chkShp[0]) == 'mesh':
                    path[sel] = 'transform'
                elif mc.nodeType(chkShp[0]) == 'nurbsSurface':
                    path[sel] = 'nurbsSurface'
                else:
                    lRoot.append(sel)
            else:
                lRoot.append(sel)
        elif selType == 'mesh':
            path[sel] = 'mesh'

        elif selType == 'joint':
            lRoot.append(sel)
    if lRoot and path.keys():
        ###########################################################
        if path[path.keys()[0]] == 'mesh':
            comp = path.keys()[0]
            if not comp.split('.')[-1].startswith('f['):
                adjFaces = []
                if comp.split('.')[-1].startswith('e['):
                    adjFaces = mc.ls(mc.polyListComponentConversion(comp, fe=True, tf=True), fl=True)
                elif comp.split('.')[-1].startswith('vtx['):
                    adjFaces = mc.ls(mc.polyListComponentConversion(comp, fv=True, tf=True), fl=True)

                averageRoot = mc.createNode('transform')
                mc.delete(mc.pointConstraint(lRoot, averageRoot, mo=False))
                comp = getNearestTrans(averageRoot, adjFaces)
                mc.delete(averageRoot)

            indFace = comp.split('[')[-1][: -1]
            lEdg = getEdges(comp)
            clearName = path.keys()[0].split('.')[0]
            #CREATE THE NURBS FROM THE EDGES
            nspace = clearName.split(':')[0]
            nNbs = nspace+':'+clearName.split(':')[-1].replace(clearName.split(':')[-1].split('_')[0], 'nbs')+'_F'+indFace
            nbs = nNbs
            if not mc.objExists(nNbs):
                nbs = mc.loft(lEdg[0], lEdg[1], n=nNbs, ch=True, u=True, c=False, d=3, ss=1, rn=False, po=0, rsn=True)[0]
                shpNbs = mc.listRelatives(nbs, s=True)[0]
                lft = mc.listConnections(shpNbs+'.create', s=True, d=True)[0]
                lPETOC = mc.listConnections(lft+'.inputCurve')
                shpMsh = mc.listConnections(lPETOC[0]+'.inputMesh', s=True, d=False)[0]
                mc.deformer(sfMod, e=True, rm=True, g=shpMsh)
                lastDef = mc.listConnections(shpMsh+'.inMesh', s=True, d=False, plugs=True) or []
                if not lastDef:
                    mc.listConnections(shpMsh+'.worldMesh[0]', s=True, d=False, plugs=True)
                for pETOC in lPETOC:
                    mc.connectAttr(lastDef[0], pETOC+'.inputMesh', f=True)
                mc.deformer(sfMod, e=True, g=shpMsh)
                mc.parent(nbs, nNbsGrp)
            for root in lRoot:
            	print 'attaching :', root
                sa = attachOnNbs(nbs, root, None, False)
                mc.parent(sa, nSaGrp)

        ############################################
        elif path[path.keys()[0]] == 'nurbsSurface':
            for root in lRoot:
            	print 'attaching :', root
                sa = attachOnNbs(path.keys()[0], root, None, False)
                mc.parent(sa, nSaGrp)
        print 'roots succecsfuly attahced'
    else:
        mc.warning('check your selection')

#crtSurfAttach(mc.ls(sl=True), 'PATH', 'SURFATTACH')
#NURBS ATTACH
########################################
def crtSoftMod(comp):
    dicSft = {}
    type = mc.objectType(comp)
    tmpShd = 'shd_sftTmp'
    smpShdSG = 'shd_sftTmpSG'
    if not mc.objExists(tmpShd):
        tmpShd = 'shd_sftTmp'
        if not mc.objExists(tmpShd):
            tmpShd = mel.eval("shadingNode -as lambert -n shd_sftTmp")
            mc.setAttr(tmpShd+'.transparency', .8, .8, .8)
            smpShdSG = mc.sets(renderable=True, em=True, n=smpShdSG)
            mc.connectAttr(tmpShd+'.outColor', smpShdSG+'.surfaceShader', f=True)
            mc.setAttr(tmpShd+'.color', 0.513, 1, 0.887617)


    if type == 'mesh':

        msh = comp.split('.')[0]

        baseName = comp.replace('.', '_').replace('[', '_').replace(']', '')

        nSmfRootSlide = baseName.replace('msh_', 'root_')+'SftSlide'
        if not mc.objExists(nSmfRootSlide):
            smfRootSlide = mc.createNode('transform', n=nSmfRootSlide)
            smfCtrlSlide = mc.createNode('transform', n=nSmfRootSlide.replace('root_', 'c_'), p=smfRootSlide)
            mc.setAttr(smfCtrlSlide+'.displayHandle', 1)
            mc.setAttr(smfCtrlSlide+'.overrideEnabled', 1)
            mc.setAttr(smfCtrlSlide+'.overrideColor', 17)

            smfRoot = mc.createNode('transform', n=nSmfRootSlide.replace('SftSlide', 'SftHdl'), p=smfCtrlSlide)
            smfCtrl = mc.sphere(n=smfRoot.replace('root_', 'c_'))
            sphereNbs = smfCtrl[-1]
            smfCtrl = smfCtrl[0]
            dicSft['ctrl'] = smfCtrl
            mc.sets(smfCtrl, e=True, fe=smpShdSG)
            mc.parent(smfCtrl, smfRoot)



            sfMod = mc.deformer(msh, n=baseName.replace('msh_', 'sFM_'), type='softMod')[0]
            dicSft['sft'] = sfMod
            dM = mc.createNode('decomposeMatrix', n=baseName.replace('msh_', 'dM_'))

            mc.addAttr(smfCtrl, ln='sftRadius', k=True, at='double', dv=1)
            mc.connectAttr(smfCtrl+'.sftRadius', sphereNbs+'.radius', f=True)
            mc.addAttr(smfCtrl, ln='sftMode', k=True, at='enum', en='volume:surface:', dv=1)

            mc.connectAttr(smfCtrl+'.parentMatrix', dM+'.inputMatrix')
            mc.connectAttr(smfCtrl+'.worldMatrix[0]', sfMod+'.matrix')
            mc.connectAttr(smfCtrl+'.parentInverseMatrix', sfMod+'.bindPreMatrix')
            mc.connectAttr(smfCtrl+'.matrix', sfMod+'.weightedMatrix')
            mc.connectAttr(smfCtrl+'.parentMatrix', sfMod+'.preMatrix')
            mc.connectAttr(dM+'.outputTranslate', sfMod+'.falloffCenter')
            mc.connectAttr(smfCtrl+'.sftRadius', sfMod+'.falloffRadius')
            mc.connectAttr(smfCtrl+'.sftMode', sfMod+'.falloffMode')

            for node in [smfCtrlSlide, smfCtrl]:
                if not mc.attributeQuery('deformersList', n=node, ex=True):
                    mc.addAttr(node, ln='deformersList', at='message', multi=True)
                id = getAvalableId(node, 'deformersList')
                mc.connectAttr(sfMod+'.message', node+'.deformersList['+str(id)+']')

            if not comp in dicSft.keys():
                dicSft[comp] = smfRootSlide
    mc.select(cl=True)
    return dicSft
    #crtSoftMod(mc.ls(sl=True))


def stickySMod(lComp):
    if lComp:
        for comp in lComp:
            dicSft = crtSoftMod(comp)
            root = dicSft[comp]
            crtSurfAttach([comp, root], "TWEAKS_PATH", "TWEAKS_SA", dicSft['sft'])
            mc.select(dicSft['ctrl'])

#stickySMod(mc.ls(sl=True))




########################################
#SPACE SWITCH
def getSwitchNode(ctrl):
    '''
    get networkNode for spaceSwitch options or create it
    '''
    node = ctrl
    nspace = ''
    if ':' in ctrl:
        node = namespace.getNodeName(ctrl)
        nspace = namespace.getNspaceFromObj(ctrl) + ':'
    switchNode = ''
    nSwitchNode = 'menu_spaceSwitch' + node[len(node.split('_')[0]):][1].capitalize() + node[len(node.split('_')[0]) + 2:].replace('_', '')
    if not mc.attributeQuery('menuSpaceSwitch', node=ctrl, ex=True):
        mc.addAttr(ctrl, ln='menuSpaceSwitch', at='message')
    if mc.connectionInfo(ctrl + '.menuSpaceSwitch', id=True):
        switchNode = mc.listConnections(ctrl + '.menuSpaceSwitch')[0]
    if not switchNode:
        switchNode = mc.createNode('network', n=nSwitchNode)
        mc.connectAttr(switchNode + '.message', ctrl + '.menuSpaceSwitch', f=True)
        if not mc.attributeQuery('targets', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='targets', dt='string', multi=True)
            mc.setAttr(switchNode + '.targets[0]', 'Root', type='string')
        if not mc.attributeQuery('attrs', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='attrs', dt='string', multi=True)
            mc.setAttr(switchNode + '.attrs[0]', '', type='string')
        if not mc.attributeQuery('constraint', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='constraint', at='message')
    return switchNode

def crtSpaceSwitch(lTargets, ctrl, cnstType):
    '''
    create constraint,  add and connect followsAttr ofrom ctrl to constraint attr weight
    '''
    if len(lTargets) > 4:
        print 'you can not give more than 4 targets'
    else:
        node = ctrl
        nspace = ''
        if ':' in ctrl:
            node = namespace.getNodeName(ctrl)
            nspace = namespace.getNspaceFromObj(ctrl) + ':'
        root = nspace + 'root' + node[len(node.split('_')[0]):]
        # root = mc.listRelatives(ctrl, p=True)[0]
        switchNode = getSwitchNode(ctrl)
        for target in lTargets:
            if cnstType == 'parent':
                cnst = mc.parentConstraint(target, root, mo=True)[0]
            elif cnstType == 'orient':
                cnst = mc.orientConstraint(target, root, mo=True)[0]
            elif cnstType == 'point':
                cnst = mc.pointConstraint(target, root, mo=True)[0]
            if not mc.isConnected(cnst + '.message', switchNode + '.constraint'):
                mc.connectAttr(cnst + '.message', switchNode + '.constraint')
            nAttr = target
            if ':' in target:
                nAttr = namespace.getNodeName(target)
            if '_' in nAttr:
                nAttr = nAttr[len(nAttr.split('_')[0]):][1].capitalize() + nAttr[len(nAttr.split('_')[0]) + 2:].replace('_', '')
            if not mc.attributeQuery('follow' + nAttr, node=ctrl, ex=True):
                mc.addAttr(ctrl, ln='follow' + nAttr, at='float', min=0, max=10, k=True)
            mDL = mc.createNode('multDoubleLinear', n='mDL_follow' + nAttr)
            mc.connectAttr(ctrl + '.follow' + nAttr, mDL + '.input1', f=True)
            mc.setAttr(mDL + '.input2', 0.1)
            cnstGraph = lib_constraints.getCnstGraph(root)
            weghtAtttr = cnstGraph[cnst]['driverAttr'][target]
            if not mc.isConnected(mDL + '.output', cnst + '.' + weghtAtttr):
                mc.connectAttr(mDL + '.output', cnst + '.' + weghtAtttr, f=True)
            id = mc.getAttr(switchNode + '.targets', size=True)
            mc.setAttr(switchNode + '.targets[' + str(id) + ']', nAttr, type='string')
            mc.setAttr(switchNode + '.attrs[' + str(id) + ']', 'follow' + nAttr, type='string')
#crtSpaceSwitch(mc.ls(sl=True), 'RIG:WORLD:SPINE_1:HEAD_1:c_head', 'orient')

def removeSpaceSwitch(lCtrl):
    for ctrl in lCtrl:
        switchNode = getSwitchNode(ctrl)
        if switchNode:
            cnst = mc.listConnections(switchNode+'.constraint', s=True, d=False) or []
            if cnst :
                cnstGraph = lib_constraints.getCnstGraph(cnst[0])
                for key in cnstGraph[cnst[0]]['driverAttr'].keys():
                    wghtAttr = cnstGraph[cnst[0]]['driverAttr'][key]
                    mDL = mc.listConnections(cnst[0]+'.'+wghtAttr, s=True, d=False)[0]
                    driverAttr = mc.listConnections(mDL+'.input1', s=True, d=False, plugs=True) or []
                    if driverAttr:
                        mc.deleteAttr(driverAttr[0])
                    mc.delete(mDL)
                mc.delete(switchNode)
                mc.delete(cnst[0])
                print 'spaceSwitch removed from', ctrl
            else:
                mc.warning('no constraint found for : '+ctrl)
        else:
            mc.warning('no switchNode found for : '+ctrl)



def removeFromSpaceSwitch(lCtrl):
    driver = lCtrl[0]
    lDriven = lCtrl[1:]
    for ctrl in lDriven:
        switchNode = getSwitchNode(ctrl)
        cnst = mc.listConnections(switchNode+'.constraint', s=True, d=False)[0]
        cnstGraph = lib_constraints.getCnstGraph(cnst)
        wghtAttr = cnstGraph[cnst]['driverAttr'][driver]
        driven = cnstGraph[cnst]['driven']
        mDL = mc.listConnections(cnst+'.'+wghtAttr, s=True, d=False)[0]
        driverAttr = mc.listConnections(mDL+'.input1', s=True, d=False, plugs=True)[0]
        lIds = mc.getAttr(switchNode+'.attrs', mi=True) or []
        dicAttrSwitchNode = {}
        if lIds:
            for i in lIds:
                if not mc.getAttr(switchNode+'.attrs['+str(i)+']') == driverAttr.split('.')[-1]:
                    dicAttrSwitchNode[mc.getAttr(switchNode+'.attrs['+str(i)+']')] = mc.getAttr(switchNode+'.targets['+str(i)+']')
        mc.deleteAttr(switchNode+'.attrs')
        mc.deleteAttr(switchNode+'.targets')
        mc.addAttr(switchNode, ln='attrs', dt='string', multi=True)
        mc.addAttr(switchNode, ln='targets', dt='string', multi=True)
        for i in range(0, len(dicAttrSwitchNode.keys())):
            mc.setAttr(switchNode+'.attrs['+str(i)+']', dicAttrSwitchNode.keys()[i], type='string')
            mc.setAttr(switchNode+'.targets['+str(i)+']', dicAttrSwitchNode[dicAttrSwitchNode.keys()[i]], type='string')

        mc.delete(mDL)
        type = cnstGraph[cnst]['type']
        if type == 'parentConstraint':
            mc.parentConstraint(driver, driven, e=True, rm=True)
        if type == 'pointConstraint':
            mc.pointConstraint(driver, driven, e=True, rm=True)
        if type == 'orientConstraint':
            mc.orientConstraint(driver, driven, e=True, rm=True)
        if type == 'scaleConstraint':
            mc.scaleConstraint(driver, driven, e=True, rm=True)
        mc.deleteAttr(driverAttr)
        print driver, 'removed for spaceSwitch of', ctrl

########################################

def checkAssetType(dicAssets):
    for nspace in dicAssets.keys():
        print nspace

def getNodesFromNspace(assetType, type):
    lNodes = mc.ls(sl=True)
    dicNspace = {}
    for node in lNodes:
        nspace = node.replace(node.split(':')[-1], '')
        if type == 'mesh':
            if mc.referenceQuery(node, inr=True):
                ref = mc.referenceQuery(node, f=True)
                if ref.split('/')[-3] == assetType:
                    if not nspace in dicNspace.keys():
                        dicNspace[nspace] = []
                    lMsh = mc.ls(nspace+'*', r=True, type='mesh', ni=True)
                    for msh in lMsh:
                        father = mc.listRelatives(msh, p=True, type='transform')[0]
                        if mc.getAttr(msh+'.v') == True:
                            if mc.getAttr(father+'.v') == True:
                                if not father in dicNspace[nspace]:
                                    dicNspace[nspace].append(father)
        elif type == 'ctrl':
            if not nspace in dicNspace.keys():
                dicNspace[nspace] = []
            print 'to do'
    return dicNspace
#getNodesFromNspace('PRP', 'mesh')

def addSpaceSwitch(chkBox, lNodes):
    if len(lNodes) < 2:
        mc.warning('you nee to select one or more driver AND one driven')
        return
    for node in lNodes:
        if not mc.attributeQuery('nodeType', n=node, ex=True):
            mc.warning(node+' is not a ctrl or is not in a controlGroup')
            return
        else:
            if not mc.getAttr(node+'.nodeType') == 'control':
                mc.warning(node+' is not a ctrl or is not in a controlGroup')
                return

    lTargets = lNodes[: -1]
    driven = lNodes[-1]
    dicType = {1:'parent', 2:'point', 3:'orient', 4:'scale'}
    cnstType = mc.radioButtonGrp(chkBox, q=True, sl=True)
    lib_dagMenu.crtSpaceSwitch(lTargets, driven, dicType[cnstType])
#crtSpaceSwitch(mc.ls(sl=True), 'RIG:WORLD:SPINE_1:HEAD_1:c_head', 'orient')
#SPACE SWITCH
########################################

#UI_TOOLS###############################################################################################################
def getAssets():
    dicAssets = {}
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            assetType = ref.split('/')[4]
            nSpace = mc.referenceQuery(ref, ns=True)
            if not assetType in dicAssets.keys():
                dicAssets[assetType] = {}
            if not nSpace in dicAssets[assetType].keys():
                dicAssets[assetType][nSpace] = {}
            dicAssets[assetType][nSpace]['file'] = ref
            dicAssets[assetType][nSpace]['mesh'] = {}
            lMsh = mc.ls(nSpace+':*', type='mesh', r=True, ni=True)
            for msh in lMsh:
                trans = mc.listRelatives(msh, p=True)[0]
                if mc.getAttr(trans+'.v') and mc.getAttr(msh+'.v'):
                    if  not trans in dicAssets[assetType][nSpace]['mesh'].keys():
                        dicAssets[assetType][nSpace]['mesh'][trans] = msh
    return dicAssets

#getAssets()

def loadAssetsInTree():
    treeAsset = 'treeAssets_'
    dicAssets = getAssets()
    for type in dicAssets.keys():
        if type in ['PRP', 'CHR', 'BG']:
            mc.treeView(treeAsset+type, e=True, ra=True)
            for asset in sorted(dicAssets[type].keys()):
                mc.treeView(treeAsset+type, e=True, addItem = (asset, ''))
                for msh in sorted(dicAssets[type][asset]['mesh'].keys()):
                    #niceName = msh.split(':')[-1]+r'/_____/'+asset[1 :]
                    #print niceName
                    mc.treeView(treeAsset+type, e=True, addItem = (msh, asset))
#loadAssetsInTree()





def loadItemsInTree(tree, assetType, type, load=False, *args):
    if load == True:
        mc.treeView(tree, e=True, ra=True)
    dicNodes = getNodesFromNspace(assetType, type)
    lNspace = dicNodes.keys()
    sorted(lNspace)
    for nspace in sorted(lNspace):
        mc.treeView(tree, e=True, addItem=(nspace, ''))
        for node in sorted(dicNodes[nspace]):
            mc.treeView(tree, e=True, addItem=(node, nspace))


def getTreeSelectedItem(tree):
        itemSel = mc.treeView(tree, q=True, si=True)
        if itemSel:
            return itemSel[0]

########################################################################################################################




def SMAB_animTools_UI():
    nWin = 'SMAB_animTools'
    nPan = 'SMAB_masterPanAn'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_rigCharacterAdd_UI = mc.window(nWin, t=nWin+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools', to=True)
    mc.menuItem(l='comming soon', c='print "be patient  ;)",')

    masterPan = mc.paneLayout('SMAB_formLayAnimTree', cn='single')


    mc.paneLayout('SMAB_formLayAnimTree', cn='top3')


    mc.frameLayout('framAssets', l='Assets', bv=True, bgc=[.3, .4, .5], bgs=True)
    mc.tabLayout('TAB_ASSETS')
    formLayPrp = mc.formLayout('PROPS', nd=100, bgc=[.3, .4, .5])
    treeAssetPrp = mc.treeView('treeAssets_PRP', adr=False, p=formLayPrp, ams=True)

    mc.popupMenu('SMAB_propsListPopup', b=3, mm=False, aob=True)
    mc.menuItem(divider=True, dividerLabel='Loading')
    mc.menuItem(l='Add from selection', c=partial(loadItemsInTree, treeAssetPrp, 'PRP', 'mesh', False))
    mc.menuItem(l='Load from selection', c=partial(loadItemsInTree, treeAssetPrp, 'PRP', 'mesh', True))
    mc.menuItem(l='Load all')
    mc.menuItem(l='Unload')
    mc.menuItem(l='Clear')
    mc.menuItem(divider=True, dividerLabel='Editing')
    mc.menuItem(l='Unlock mesh')
    mc.menuItem(l='Relock mesh')

    mc.formLayout(formLayPrp, e=True, af= [
                                        (treeAssetPrp, 'top', 5), (treeAssetPrp, 'left', 5), (treeAssetPrp, 'right', 5), (treeAssetPrp, 'bottom', 5),
                                        ])

    mc.setParent('..')
    formLayChr = mc.formLayout('CHARACTERS', nd=100, bgc=[.2, .5, .5])
    treeAssetChr = mc.treeView('treeAssets_CHR', adr=False, p=formLayChr)
    mc.popupMenu('SMAB_charactersListPopup', b=3, mm=False, aob=True)
    mc.menuItem(divider=True, dividerLabel='Loading')
    mc.menuItem(l='Add from selection', c=partial(loadItemsInTree, treeAssetPrp, 'CHR', 'mesh', False))
    mc.menuItem(l='Load from selection', c=partial(loadItemsInTree, treeAssetPrp, 'CHR', 'mesh', True))
    mc.menuItem(l='Load all')
    mc.menuItem(l='Unload')
    mc.menuItem(l='Clear')
    mc.menuItem(divider=True, dividerLabel='Editing')
    mc.menuItem(l='Unlock mesh')
    mc.menuItem(l='Relock mesh')
    mc.formLayout(formLayChr, e=True, af= [
                                        (treeAssetChr, 'top', 5), (treeAssetChr, 'left', 5), (treeAssetChr, 'right', 5), (treeAssetChr, 'bottom', 5),
                                        ])

    mc.setParent('..')
    formLayBg = mc.formLayout('BACK_GROUNDS', nd=100, bgc=[.1, .4, .6])
    treeAssetBg = mc.treeView('treeAssets_BG', adr=False, p=formLayBg)
    mc.popupMenu('SMAB_backGroundsListPopup', b=3, mm=False, aob=True)
    mc.menuItem(divider=True, dividerLabel='Loading')
    mc.menuItem(l='Add from selection', c=partial(loadItemsInTree, treeAssetPrp, 'BG', 'mesh', False))
    mc.menuItem(l='Load from selection', c=partial(loadItemsInTree, treeAssetPrp, 'BG', 'mesh', True))
    mc.menuItem(l='Load all')
    mc.menuItem(l='Unload')
    mc.menuItem(l='Clear')
    mc.menuItem(divider=True, dividerLabel='Editing')
    mc.menuItem(l='Unlock mesh')
    mc.menuItem(l='Relock mesh')
    mc.formLayout(formLayBg, e=True, af= [
                                        (treeAssetBg, 'top', 5), (treeAssetBg, 'left', 5), (treeAssetBg, 'right', 5), (treeAssetBg, 'bottom', 5),
                                        ])


    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    #.5, .2, .4 / .5, .3, .0
    mc.frameLayout('framCtrl', l='Controlers', bv=True, bgc=[.5, .2, .4], bgs=True)
    mc.tabLayout('TAB_DEFORMERS')
    formLaySft = mc.formLayout('SOFT_MOD_CTRL', nd=100, bgc=[.5, .2, .4])
    treeCtrlSft = mc.treeView(adr=False, p=formLaySft)
    mc.popupMenu('SMAB_softModListPopup', b=3, mm=False, aob=True)
    mc.menuItem(divider=True, dividerLabel='Loading')
    mc.menuItem(l='Add from selection')
    mc.menuItem(l='Load from selection')
    mc.menuItem(l='Load all')
    mc.menuItem(l='Isolate')
    mc.menuItem(l='Unload')
    mc.menuItem(l='Clear')
    mc.menuItem(divider=True, dividerLabel='Editing')
    mc.menuItem(l='Add mesh')
    mc.menuItem(l='Remove mesh')
    mc.menuItem(l='Delete ctrl')
    mc.formLayout(formLaySft, e=True, af= [
                                        (treeCtrlSft, 'top', 5), (treeCtrlSft, 'left', 5), (treeCtrlSft, 'right', 5), (treeCtrlSft, 'bottom', 5),
                                        ])


    mc.setParent('..')
    formLayFRot = mc.formLayout('FREE_ROT_CTRL', nd=100)
    treeCtrlFRot = mc.treeView(adr=False, p=formLayFRot)
    mc.popupMenu('SMAB_freeRotListPopup', b=3, mm=False, aob=True)
    mc.menuItem(divider=True, dividerLabel='Loading')
    mc.menuItem(l='Add from selection')
    mc.menuItem(l='Load from selection')
    mc.menuItem(l='Load all')
    mc.menuItem(l='Isolate')
    mc.menuItem(l='Unload')
    mc.menuItem(l='Clear')
    mc.menuItem(divider=True, dividerLabel='Editing')
    mc.menuItem(l='Add mesh')
    mc.menuItem(l='Remove mesh')
    mc.menuItem(l='Delete ctrl')
    mc.formLayout(formLayFRot, e=True, af= [
                                        (treeCtrlFRot, 'top', 5), (treeCtrlFRot, 'left', 5), (treeCtrlFRot, 'right', 5), (treeCtrlFRot, 'bottom', 5),
                                        ])







    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout(adj=True)


    mc.columnLayout(co=['left', -60], adj=True)
    mc.rowLayout(nc=3, adj=3)
    enumTypeDef = mc.attrEnumOptionMenuGrp('SMAB_typeDefo', l='Controler type:',ei=[(0, 'SoftMod'),(1, 'Lattice'), (2, 'FreeRot')])
    bntAttach = mc.button('SMAB_btnAttach', label='attach to :')
    vtxName = mc.textField('SMAB_nameVtx')

    mc.setParent('..')
    mc.setParent('..')

    mc.separator(h=10)
    mc.button(l='Generate')
    mc.separator(h=10)

    mc.frameLayout(l='Space switch', cll=True, bv=True, bgc=[.5, .2, .4], bgs=True)
    mc.text('select driver(s) then the driven')
    mc.radioButtonGrp('rButtonSpSwAnim', nrb=4, l='type : ', la4=['parent', 'point', 'orient', 'scale'], ct5=('left', 'left', 'left', 'left', 'left'), co5=(5, -100, -150, -205, -255))
    mc.radioButtonGrp('rButtonSpSwAnim', e=True, select=1)
    mc.button(l='add spaceSwitch', h=28, w=130, c='tools_dagMenu.addSpaceSwitch("rButtonSpSwAnim", mc.ls(sl=True))')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='remove spaceSwitch', h=28, w=130, bgc=[.5, .2, .2], c='tools_dagMenu.removeSpaceSwitch(mc.ls(sl=True))')
    mc.button(l='remove from spaceSwitch', h=28, w=130, bgc=[.5, .2, .2], c='tools_dagMenu.removeFromSpaceSwitch(mc.ls(sl=True))')





    ###########################################################################
    mc.treeView(treeAssetPrp, e=True, addItem = ("Apple_01", ""))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_apple_01", "Apple_01"))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_sting_01", "Apple_01"))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_leaf_01", "Apple_01"))

    mc.treeView(treeAssetPrp, e=True, addItem = ("Apple_02", ""))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_apple_02", "Apple_02"))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_sting_02", "Apple_02"))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_leaf_02", "Apple_02"))

    mc.treeView(treeAssetPrp, e=True, addItem = ("Knife_01", ""))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_handle", "Knife_01"))
    mc.treeView(treeAssetPrp, e=True, addItem = ("msh_slice", "Knife_01"))
    ###

    mc.treeView(treeAssetChr, e=True, addItem = ("SmurfBrainy_01", ""))
    mc.treeView(treeAssetChr, e=True, addItem = ("msh_body", "SmurfBrainy_01"))
    mc.treeView(treeAssetChr, e=True, addItem = ("msh_hat", "SmurfBrainy_01"))
    mc.treeView(treeAssetChr, e=True, addItem = ("msh_glasses", "SmurfBrainy_01"))
    mc.treeView(treeAssetChr, e=True, addItem = ("msh_pant", "SmurfBrainy_01"))
    ###
    mc.treeView(treeAssetBg, e=True, addItem = ("GargInt_01", ""))
    mc.treeView(treeAssetBg, e=True, addItem = ("msh_chair", "GargInt_01"))
    mc.treeView(treeAssetBg, e=True, addItem = ("msh_steps", "GargInt_01"))
    mc.treeView(treeAssetBg, e=True, addItem = ("msh_door", "GargInt_01"))
    mc.treeView(treeAssetBg, e=True, addItem = ("msh_doorHandle", "GargInt_01"))
    mc.treeView(treeAssetBg, e=True, addItem = ("msh_book", "GargInt_01"))



    mc.treeView(treeCtrlSft, e=True, addItem = ("SmurfBrainy_01_SFT", ""))
    mc.treeView(treeCtrlSft, e=True, addItem = ("msh_body", "SmurfBrainy_01_SFT"))
    mc.treeView(treeCtrlSft, e=True, addItem = ("msh_pant", "SmurfBrainy_01_SFT"))

    mc.treeView(treeCtrlFRot, e=True, addItem = ("gargInt_01_FROT", ""))
    mc.treeView(treeCtrlFRot, e=True, addItem = ("msh_door", "gargInt_01_FROT"))
    mc.treeView(treeCtrlFRot, e=True, addItem = ("msh_doorHandle", "gargInt_01_FROT"))
    ###########################################################################
    mc.showWindow(win_rigCharacterAdd_UI)
#SMAB_animTools_UI()


