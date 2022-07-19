# coding: utf-8
import maya.cmds as mc

def nurbs_attach(parentInSA=False):
    lObj = mc.ls(sl=True)
    # Select the NURBS and the OBJECTS to attached
    # Find nurbs surface
    for obj in lObj:
        lShp = mc.listRelatives(obj, shapes=True) or []
        for shp in lShp:
            if mc.nodeType(shp) == 'nurbsSurface':
                nbs = obj

    lRoot = []
    for i in lObj:
        if not nbs in i:
            lRoot.append(i)

    for i in lRoot:
        # NAMES
        ## Split NameSpace
        iNoNS = i.split(':')[-1]
        print iNoNS
        nSa = iNoNS.replace(iNoNS.split('_')[0], 'sa')
        nPOSI = iNoNS.replace(iNoNS.split('_')[0], 'pOSI')
        nFBFMat = iNoNS.replace(iNoNS.split('_')[0], 'fBfM')
        nMltMat = iNoNS.replace(iNoNS.split('_')[0], 'mltM')
        nDMat = iNoNS.replace(iNoNS.split('_')[0], 'dM')
        nCPOS = iNoNS.replace(iNoNS.split('_')[0], 'cPOS')
        nLoc = iNoNS.replace(iNoNS.split('_')[0], 'loc')
        # CREATE NODE
        sa = mc.createNode('transform', n=nSa)
        pOSI = mc.createNode('pointOnSurfaceInfo', n=nPOSI)
        fBFMat = mc.createNode('fourByFourMatrix', n=nFBFMat)
        mltMat = mc.createNode('multMatrix', n=nMltMat)
        dMat = mc.createNode('decomposeMatrix', n=nDMat)
        cPOS = mc.createNode('closestPointOnSurface', n=nCPOS)

        # CONNECTIONS
        # connect le nurbs to the pOSI
        shp = mc.listRelatives(nbs, s=True)[0]
        mc.connectAttr(shp + '.worldSpace[0]', pOSI + '.inputSurface', f=True)
        # connect le pointOnSurfaceInfo au fourByfourMatrix
        mc.connectAttr(pOSI + '.normalizedNormalX', fBFMat + '.in10', f=True)
        mc.connectAttr(pOSI + '.normalizedNormalY', fBFMat + '.in11', f=True)
        mc.connectAttr(pOSI + '.normalizedNormalZ', fBFMat + '.in12', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUX', fBFMat + '.in00', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUY', fBFMat + '.in01', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentUZ', fBFMat + '.in02', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVX', fBFMat + '.in20', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVY', fBFMat + '.in21', f=True)
        mc.connectAttr(pOSI + '.normalizedTangentVZ', fBFMat + '.in22', f=True)
        mc.connectAttr(pOSI + '.positionX', fBFMat + '.in30', f=True)
        mc.connectAttr(pOSI + '.positionY', fBFMat + '.in31', f=True)
        mc.connectAttr(pOSI + '.positionZ', fBFMat + '.in32', f=True)
        # connect le fourByfourMatrix au multMatrix
        mc.connectAttr(fBFMat + '.output', mltMat + '.matrixIn[0]', f=True)
        # connect le multMatrix au decomposeMatrix
        mc.connectAttr(mltMat + '.matrixSum', dMat + '.inputMatrix', f=True)
        # connect le null au multMatrix
        mc.connectAttr(sa + '.parentInverseMatrix', mltMat + '.matrixIn[1]', f=True)
        # connect le decomposeMatrix au null
        mc.connectAttr(dMat + '.outputRotate', sa + '.r', f=True)
        mc.connectAttr(dMat + '.outputTranslate', sa + '.t', f=True)

        # LOCATOR
        mc.spaceLocator(n=nLoc)
        mc.parent(nLoc, sa)
        mc.setAttr(nLoc + '.t', 0, 0, 0)
        mc.setAttr(nLoc + '.r', 0, 0, 0)
        mc.addAttr(nLoc, ln='U', at='double', dv=0.5)
        mc.setAttr(nLoc + '.U', e=True, keyable=True)

        mc.addAttr(nLoc, ln='V', at='double', dv=0.5)
        mc.setAttr(nLoc + '.V', e=True, keyable=True)

        mc.connectAttr(nLoc + '.U', pOSI + '.parameterU', f=True)
        mc.connectAttr(nLoc + '.V', pOSI + '.parameterV', f=True)

        # CLOSETS POINT ON SURFACE
        mc.createNode('closestPointOnSurface', n=cPOS)
        mc.connectAttr(shp + '.worldSpace[0]', cPOS + '.inputSurface', f=True)
        mc.connectAttr(i + '.t', cPOS + '.inPosition', f=True)
        mc.connectAttr(cPOS + '.parameterU', nLoc + '.U', f=True)
        mc.connectAttr(cPOS + '.parameterV', nLoc + '.V', f=True)
        mc.disconnectAttr(cPOS + '.parameterU', nLoc + '.U')
        mc.disconnectAttr(cPOS + '.parameterV', nLoc + '.V')
        mc.delete(cPOS)

        if parentInSA:
            try:
                mc.parent(i, sa)
            except:
                print i, " can't be parented in ", sa
