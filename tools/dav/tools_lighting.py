import maya.cmds as mc
import maya.mel as mel
from ellipse_rig.library import lib_math
reload(lib_math)
from ellipse_rig.tools.dav import tools_smab_v2
reload(tools_smab_v2)


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
                comp = lib_math.getNearestTrans(averageRoot, adjFaces)
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
                id = tools_smab_v2.getAvalableId(node, 'deformersList')
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