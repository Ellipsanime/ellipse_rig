import maya.cmds as mc
from ellipse_rig.library import lib_math
reload(lib_math)


def getShp(msh):
	shp = mc.listRelatives(msh, ni=True, s=True, c=True)
	return shp

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
    nSa = i.replace(i.split('_')[0], 'sa')
    nPOSI = i.replace(i.split('_')[0], 'pOSI')
    nFBFMat = i.replace(i.split('_')[0], 'fBfM')
    nMltMat = i.replace(i.split('_')[0], 'mltM')
    nDMat =  i.replace(i.split('_')[0], 'dM')
    nCPOS = i.replace(i.split('_')[0], 'cPOS')
    nLoc =i.replace(i.split('_')[0], 'tmp')
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
    return sa



def crtSurfAttach(lSel, nNbsGrp, nSaGrp):
    lRoot = []
    path = {}
    if not mc.objExists(nNbsGrp):
		mc.createNode('transform', n=nNbsGrp)
    if not mc.objExists(nSaGrp):
        mc.createNode('transform', n=nSaGrp)
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
        if path[path.keys()[0]] == 'transform':
            for root in lRoot:
            	print 'attaching :', root
                #GET THE FACE INDEX
                indFace = lib_math.getNearestCompId_fromMesh(path.keys()[0], root, 'face')
                facet = path.keys()[0]+'.f['+str(indFace)+']'
                lEdg = getEdges(facet)
                #CREATE THE NURBS FROM THE EDGES
                nNbs = path.keys()[0].replace(path.keys()[0].split('_')[0], 'nbs')+'F'+str(indFace)
                nbs = nNbs
                if not mc.objExists(nNbs):
                    nbs = mc.loft(lEdg[0], lEdg[1], n=nNbs, ch=True, u=True, c=False, d=3, ss=1, rn=False, po=0, rsn=True)[0]
                    mc.parent(nNbs, nNbsGrp)
                sa = attachOnNbs(nbs, root, None, False)
                mc.parent(sa, nSaGrp)
        ##########################################
        elif path[path.keys()[0]] == 'mesh':
            comp = path.keys()[0]
            if not comp.split('.')[-1].startswith('f['):
                adjFaces = []
                if comp.split('.')[-1].startswith('e['):
                    adjFaces = mc.ls(mc.polyListComponentConversion(comp, fe=True, tf=True), fl=True)
                elif comp.split('.')[-1].startswith('vtx['):
                    adjFaces = mc.ls(mc.polyListComponentConversion(comp, fv=True, tf=True), fl=True)

                averageRoot = mc.createNode('transform')
                mc.delete(mc.pointConstraint(lRoot, averageRoot, mo=False))
                print averageRoot, adjFaces
                comp = lib_math.getNearestTrans(averageRoot, adjFaces)
                mc.delete(averageRoot)

            indFace = comp.split('[')[-1][: -1]
            lEdg = getEdges(comp)
            clearName = path.keys()[0].split('.')[0]
            #CREATE THE NURBS FROM THE EDGES
            nNbs = clearName.replace(clearName.split('_')[0], 'nbs')+'F'+indFace
            nbs = nNbs
            if not mc.objExists(nNbs):
                nbs = mc.loft(lEdg[0], lEdg[1], n=nNbs, ch=True, u=True, c=False, d=3, ss=1, rn=False, po=0, rsn=True)[0]
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


def slideOnNbs(lNodes, nbrSa, dir):
    lSa = []
    nbsPath = {}
    for node in lNodes:
        shp = mc.listRelatives(node, s=True, ni=True) or []
        if shp:
            if mc.objectType(shp[0]) == 'nurbsSurface':
                nbsPath[node] = shp[0]
        else:
            lSa.append(node)
        if nbsPath:
            lenPath = mc.getAttr(nbsPath[nbsPath.keys()[0]] + '.minMaxRange'+dir)[-1][-1]
            if not lSa:
                print('need to be done: crt surfAttch with ne nbrSa parametter')
                return
            if lSa:
                baseNameDriver = nbsPath.keys()[0][len(nbsPath.keys()[0].split('_')[0]):]
                driver = mc.spaceLocator(n='loc' + baseNameDriver)[0]
                mc.addAttr(driver, ln='pathSlide', at='float', min=0.0, max=10.0, dv=10.0, k=True)
                #space = lenPath / (len(lSa)-1)
                spread = 0.0
                for sa in lSa:
                    spread = mc.getAttr(sa + '.'+dir)
                    mc.setDrivenKeyframe(sa + '.'+dir, cd=driver + '.pathSlide', itt='linear', ott='linear', dv=0.0, v=0.0)
                    mc.setDrivenKeyframe(sa + '.'+dir, cd=driver + '.pathSlide', itt='linear', ott='linear', dv=10.0, v=spread)
                    #spread += space
#slideOnNbs(mc.ls(sl=True), 0, 'V')

###############################################################
#CURVE ATTAHC
###############################################################

"""
def crtCrvPath(lVtx):
    dicSym = {}
    obj = lVtx[0].split('.')[0]
    for id in range(0, mc.getAttr(obj+'.symTabLeft', s=True)):
        vtxL = mc.getAttr(obj+'.symTabLeft['+str(id)+']')
        vtxR = mc.getAttr(obj+'.symTabRight['+str(id)+']')
        dicSym[vtxL] = vtxR
    lSuce = []
    for vtx in lVtx:
        vtxId = int(vtx.split('[')[-1][:-1])
        if vtxId in dicSym.keys():
            lSuce.append(vtxId)

    idStart = lSuce[0]
    idEnd = lSuce[1]
    edg = mc.polySelect(obj, sep=(idStart, idEnd))
    mc.select(cl=True)
    mc.select(obj+'.e['+str(edg[0])+']')
    mc.select(obj+'.e['+str(edg[1])+']')
    mel.eval("SelectEdgeLoopSp")
    crvPath = mc.polyToCurve(form=1, degree=3, conformToSmoothMeshPreview=0)
    return crvPath
#crtCrvPath(mc.ls(sl=True))
"""

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


def attachOnCrv(curve, node):
    """ attach nodes to curve """
    # init
    shape = mc.listRelatives(curve, ni=True, s=True)[-1]
    # attach each node to curve
    # init
    vp = 'vp'+node[len(node.split('_')[0]) :]
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
    # store construction nodes
    mc.addAttr(ca, ln='constructNodes', dt='string', multi=True)
    for i, cNodes in enumerate([vp, poci, node, curve]):
        mc.setAttr(ca+'.constructNodes['+str(i)+']', cNodes, type='string')
    # parent
    mc.parent(node, ca)
    # delete nearestPointOnCurve
    mc.delete(npoc)
    # return
    return ca
#attachOnCrv('crv_hairs_R', mc.ls(sl=True))


def crtCurveAttach(lSel, nCrvsGrp, nCaGrp):
    lRoot = []
    lCa = []
    path = {}
    if not mc.objExists(nCaGrp):
		mc.createNode('transform', n=nCaGrp)
    if not mc.objExists(nCrvsGrp):
        mc.createNode('transform', n=nCrvsGrp)
    for sel in lSel:
        selType = mc.nodeType(sel)
        if selType == 'transform':
            chkShp = mc.listRelatives(sel, s=True, ni=True) or []
            if chkShp:
                if mc.nodeType(chkShp[0]) == 'mesh':
                    path[sel] = 'transform'
                elif mc.nodeType(chkShp[0]) == 'nurbsCurve':
                    path[sel] = 'nurbsCurve'
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
        if path[path.keys()[0]] == 'transform':
            for root in lRoot:
            	print 'attaching :', root
                #GET THE EDGE INDEX
                indEdg = lib_math.getNearestCompId_fromMesh(path.keys()[0], root, 'edg')
                edge = path.keys()[0]+'.e['+str(indEdg)+']'
                clearName = edge.split('.')[0]
                #CREATE THE CURVE FROM THE MESH
                nCrv = clearName.replace(clearName.split('_')[0], 'crv')+'E'+indEdg
                print 'heere' , nCrv
            #CREATE THE NURBS FROM THE EDGES
                crv = nCrv
                if not mc.objExists(nCrv):
                    crv = mc.polyToCurve(edge, n=nCrv, form=1, degree=3, conformToSmoothMeshPreview=0)
                    mc.parent(crv, nCrvsGrp)
                ca = attachOnCrv(crv, root)
                lCa.append(ca)
                mc.parent(ca, nCaGrp)
        ##########################################
        elif path[path.keys()[0]] == 'mesh':
            comp = path.keys()[0]
            edg = comp
            if not comp.split('.')[-1].startswith('e['):

                if comp.split('.')[-1].startswith('f['):
                    adjVtx = mc.ls(mc.polyListComponentConversion(comp, ff=True, tv=True), fl=True)

                elif comp.split('.')[-1].startswith('vtx['):
                    adjEdg = mc.ls(mc.polyListComponentConversion(comp, fv=True, te=True), fl=True)
                    adjVtx = mc.ls(mc.polyListComponentConversion(adjEdg, fe=True, tv=True), fl=True)

                clearName = comp.split('.')[0]
                #CREATE THE CURVE FROM THE MESH
                averageRoot = mc.createNode('transform')
                mc.delete(mc.pointConstraint(lRoot, averageRoot, mo=False))
                lOrderVtx = lib_math.orderVTxList_nearstToFarrest(adjVtx, averageRoot)
                mc.delete(averageRoot)

                vtxRef = lOrderVtx[0]
                vtxTrgt = lOrderVtx[1]
                if len(lOrderVtx) > 2:
                    if comp in lOrderVtx:
                        lOrderVtx.remove(comp)
                        vtxRef = comp
                        vtxTrgt = lOrderVtx[0]
                vtxData = lib_math.getVtxData([vtxRef, vtxTrgt])
                for id in vtxData[vtxRef]['edges']:
                    if id in vtxData[vtxTrgt]['edges']:
                        edg = comp.split('.')[0]+'.e['+str(id)+']'


            #CREATE THE CURVE FROM THE EDGES
            indEdg = edg.split('.e[')[-1][: -1]
            nCrv =  clearName.replace(clearName.split('_')[0], 'crv')+'E'+indEdg
            crv = nCrv
            mc.select(cl=True)
            mc.select(edg)
            if not mc.objExists(nCrv):
                crv = mc.polyToCurve(n=nCrv, form=1, degree=3, conformToSmoothMeshPreview=0)
                #curveFromMeshEdge1
                mc.parent(crv, nCrvsGrp)
            for root in lRoot:
                ca = attachOnCrv(crv, root)
                lCa.append(ca)
                mc.parent(ca, nCaGrp)


        ############################################
        elif path[path.keys()[0]] == 'nurbsCurve':
            for root in lRoot:
            	print 'attaching :', root
                ca = attachOnCrv(path.keys()[0], root)
                lCa.append(ca)
                mc.parent(ca, nCaGrp)
        print 'roots succecsfuly attahced'
        return lCa
    else:
        mc.warning('check your selection')
#crtCurveAttach(mc.ls(sl=True), 'TOTO', 'TUTU')