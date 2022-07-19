import maya.cmds as mc


def getCnstGraph(node):
    ## DKATZ
    dicLCnst = {}
    lCnst = node
    if not mc.nodeType(node, i='constraint'):
        lCnst = list(set(mc.listConnections(node, type='constraint')))
    for cnst in lCnst:
        dicCnst = {}
        dicDrivers = {}
        dicCnst['type'] = mc.objectType(cnst)
        dicCnst['driven'] = list(set(mc.listConnections(cnst, d=True, s=False, type='transform')))
        if cnst in dicCnst['driven']:
            dicCnst['driven'].remove(cnst)
        incTrgt = mc.getAttr(cnst + '.target', size=True)
        for i in range(0, incTrgt):
            attr = mc.connectionInfo(cnst + '.target[' + str(i) + '].targetWeight', sfd=True).split('.')[-1]
            driver = mc.connectionInfo(cnst + '.target[' + str(i) + '].targetParentMatrix', sfd=True).split('.')[0]
            dicDrivers[driver] = attr
        dicCnst['drivers'] = dicDrivers.keys()
        dicCnst['driverAttr'] = dicDrivers
        dicLCnst[cnst] = dicCnst
    return dicLCnst

#getCnstGraph(mc.ls(sl=True)[0])


def crtHook(lDriver, names=list()):
    lHooks = []
    for index, driver in enumerate(lDriver):
        hook = str()
        hook_suffix = driver[len(driver.split('_')[0])
                                 :] if not names else names[index]
        if not mc.objExists('hook_{}'.format(hook_suffix)):
            hook = mc.createNode('transform', n='hook_{}'.format(hook_suffix))
            dMat = mc.createNode('decomposeMatrix', n='dM' + hook_suffix)
            mMat = mc.createNode('multMatrix', n='mltM' + hook_suffix)
            mc.connectAttr(driver + '.worldMatrix[0]', mMat + '.matrixIn[0]')
            mc.connectAttr(
                hook + '.parentInverseMatrix[0]', mMat + '.matrixIn[1]')
            mc.connectAttr(mMat + '.matrixSum', dMat + '.inputMatrix')
            lAttr = ['translate', 'rotate', 'scale', 'shear']
            for i, attr in enumerate(['outputTranslate', 'outputRotate', 'outputScale', 'outputShear']):
                mc.connectAttr(dMat + '.' + attr, hook + '.' + lAttr[i])
        if hook and hook not in lHooks:
            lHooks.append(hook)
    return lHooks
