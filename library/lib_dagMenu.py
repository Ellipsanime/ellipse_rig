import maya.cmds as mc
from ellipse_rig.library import lib_glossary as gloss
reload(gloss)
from ellipse_rig.library.lib_glossary import lexiconAttr as attrName
from ellipse_rig.library import lib_dataNodes, lib_constraints
from ellipse_rig.library import lib_namespace as namespace
reload(lib_dataNodes)


def chkcgChild(dataNode):
    lAttr = mc.listAttr(dataNode, ud=True)
    lChildCg = []
    for attr in lAttr:
        if attr.startswith('childCg_'):
            lChildCg.append('cg'+attr[len(attr.split('_')[0]):])
    return lChildCg

#chkcgChild('tplInfo_arm_1_L')


def getMirrorLinks(lDataNodes):
    dicMirror = {}
    for dataNode in lDataNodes:
        moduleType = mc.getAttr(dataNode+'.'+attrName('moduleType'))
        if moduleType in ['leg', 'arm']:
            dicCtrl = lib_dataNodes.getMatchIkFkCtrl(dataNode)
            mc.setAttr(dicCtrl['IK']+'.mirrorType', lock=False)
            mc.setAttr(dicCtrl['IK']+'.mirrorType', 0)
        if moduleType in ['face']:
            pass
        if mc.attributeQuery(attrName('moduleMirror'), n=dataNode, ex=True):
            if mc.listConnections(dataNode+'.'+attrName('moduleMirror')):
                moduleMirror = mc.listConnections(dataNode+'.'+attrName('moduleMirror'), s=False, d=True)
                if moduleMirror:
                    dicMirror[dataNode] = moduleMirror[0]
                    chkChilds = chkcgChild(dataNode) or []
                    if chkChilds:
                        for cgChild in chkChilds:
                            side = cgChild.split('_')[-1]
                            cgMirror = ''
                            if side == 'L':
                                cgMirror = cgChild[: -1]+'R'
                            elif side == 'R':
                                cgMirror = cgChild[: -1]+'L'
                            if mc.objExists(cgChild) and mc.objExists(cgMirror):
                                dicMirror[cgChild] = cgMirror
    return dicMirror


#getMirrorLinks(lib_dataNodes.getTplDataNodes(attrName('moduleDataTpl')))


def getCgFromDataNode(dataNode):
    cg = mc.listConnections(dataNode+'.'+attrName('builtCg'), s=True, d=False)
    return cg

def connectMirorCtrl(dicMirror):
    for key in dicMirror.keys():
        cgSrc = key
        cgDest = dicMirror[key]
        if mc.attributeQuery('nodeType', n=cgSrc, ex=True):
            if not mc.getAttr(cgSrc+'.nodeType') == 'controlGroup':
                cgSrc = getCgFromDataNode(key)[0]
        elif not mc.attributeQuery('nodeType', n=cgSrc, ex=True):
            cgSrc = getCgFromDataNode(key)[0]
        if mc.attributeQuery('nodeType', n=cgDest, ex=True):
            if not mc.getAttr(cgDest+'.nodeType') == 'controlGroup':
                cgDest = getCgFromDataNode(dicMirror[key])[0]
        elif not mc.attributeQuery('nodeType', n=cgDest, ex=True):
            cgDest = getCgFromDataNode(dicMirror[key])[0]
        for i in range(0, mc.getAttr(cgSrc+'.members', s=True)):
            ctrlSrc = mc.listConnections(cgSrc+'.members['+str(i)+']', s=True, d=False)[0]
            ctrlTrgt = mc.listConnections(cgDest+'.members['+str(i)+']', s=True, d=False)[0]

            if not mc.attributeQuery('control', node=ctrlSrc, ex=True):
                mc.addAttr(ctrlSrc, ln='control', at='message')
            if not mc.attributeQuery('control', node=ctrlTrgt, ex=True):
                mc.addAttr(ctrlTrgt, ln='control', at='message')

            if mc.attributeQuery('mirrorType', n=ctrlSrc, ex=True):
                mc.setAttr(ctrlSrc + '.mirrorType', lock=False)
                mc.setAttr(ctrlSrc + '.mirrorType', 1)
                id = mc.getAttr(ctrlTrgt + '.nodesId', s=True)
                mc.setAttr(ctrlTrgt + '.nodesId[' + str(id) + ']', 'mirror', type='string')
                mc.connectAttr(ctrlSrc + '.control', ctrlTrgt + '.nodes[' + str(id) + ']')


            if mc.attributeQuery('mirrorType', n=ctrlTrgt, ex=True):
                mc.setAttr(ctrlTrgt + '.mirrorType', lock=False)
                mc.setAttr(ctrlTrgt + '.mirrorType', 1)
                id = mc.getAttr(ctrlSrc + '.nodesId', s=True)
                mc.setAttr(ctrlSrc + '.nodesId[' + str(id) + ']', 'mirror', type='string')
                mc.connectAttr(ctrlTrgt + '.control', ctrlSrc + '.nodes[' + str(id) + ']')
    networkNodes = mc.ls(type = 'network')
    for node in networkNodes:
        if mc.attributeQuery('ik', n=node, ex=True):
            ctrl = mc.listConnections(node+'.ik', s=True, d=False)[0]
            mc.setAttr(ctrl+'.mirrorType', 0)

#connectMirorCtrl(getMirrorLinks(lib_dataNodes.getTplDataNodes(attrName('moduleDataTpl'))))



#####MENU_HIDE_CTRL#####________________________________________________________________________________________________
def linkMenuHideGrp(dicMenuHideGrp):
    #need a dctionary with cg to hide as key and ctrl(s) will show the menu for hide the cg in a array as the value of the dic key
    #ex : dicMenuHideGrp['cg_armShape_L'] = ['c_shoulder_L', 'c_elbow_L', 'c_hand_L', 'c_handIK_L']
    for cg in dicMenuHideGrp.keys():
        if mc.objExists(cg):
            for driver in dicMenuHideGrp[cg]:
                if not mc.attributeQuery('menuHideGroups', n=driver, ex=True):
                    mc.addAttr(driver, ln='menuHideGroups', at='message', multi=True)
                doConn = True
                s = mc.getAttr(driver+'.menuHideGroups', s=True)
                if s == 0:
                    s = 1
                for id in range(0, s):
                    if mc.isConnected(cg+'.message', driver+'.menuHideGroups['+str(id)+']'):
                        doConn = False
                if doConn == True:
                    if not mc.attributeQuery('menuHideGroups', n=driver, im=True):
                        mc.connectAttr(cg+'.message', driver+'.menuHideGroups', na=True, f=True)
                    else:
                        mc.connectAttr(cg+'.message', driver+'.menuHideGroups['+str(mc.getAttr(driver+'.menuHideGroups', s=True))+']', f=True)

#linkMenuHideGrp(dicMenuHideGrp)



def recoCgVis(lCg):
    for cg in lCg:
        lMemb = mc.listConnections(cg+'.members', s=True, d=False, plugs=False)
        for memb in lMemb:
            old = mc.listConnections(memb+'.v', s=True, d=False, plugs=True)
            if old:
                #mc.setAttr(memb+'.v', lock=False)
                mc.disconnectAttr(old[0], memb+'.v')
            mc.connectAttr(cg+'.membersVisibility', memb+'.v')


#recoCgVis(mc.ls(sl=True))

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


#####MATCH_IK_FK#####________________________________________________________________________________________________

def getMatchMenu(ctrlIK):
    matchNode = ''
    node = ctrlIK
    if ':' in ctrlIK:
        node = namespace.getNodeName(ctrlIK)
    nMatchNode = 'menu_matchIKFK' + node[len(node.split('_')[0]):][1].capitalize() + node[len(node.split('_')[0]) + 2:].replace('_', '')
    if not mc.attributeQuery('menuMatchIKFK', node=ctrlIK, ex=True):
        mc.addAttr(ctrlIK, ln='menuMatchIKFK', at='message')
    if not mc.attributeQuery('orientOffset', node=ctrlIK, ex=True):
        mc.addAttr(ctrlIK, ln='orientOffset', at='double3')
        mc.addAttr(ctrlIK, ln='orientOffsetX', at='double', p='orientOffset')
        mc.addAttr(ctrlIK, ln='orientOffsetY', at='double', p='orientOffset')
        mc.addAttr(ctrlIK, ln='orientOffsetZ', at='double', p='orientOffset')
    if mc.connectionInfo(ctrlIK + '.menuMatchIKFK', id=True):
        matchNode = mc.listConnections(ctrlIK + '.menuMatchIKFK')[0]
    if not matchNode:
        matchNode = mc.createNode('network', n=nMatchNode)
        mc.connectAttr(matchNode + '.message', ctrlIK + '.menuMatchIKFK', f=True)
        if not mc.attributeQuery('ik', node=matchNode, ex=True):
            mc.addAttr(matchNode, ln='ik', at='message')
            mc.connectAttr(ctrlIK + '.message', matchNode + '.ik', f=True)
        if not mc.attributeQuery('fk', node=matchNode, ex=True):
            mc.addAttr(matchNode, ln='fk', at='message', multi=True)
        if not mc.attributeQuery('switch', node=matchNode, ex=True):
            mc.addAttr(matchNode, ln='switch', at='message')
        if not mc.attributeQuery('reverseTwist', node=matchNode, ex=True):
            mc.addAttr(matchNode, ln='reverseTwist', at='bool')
    return matchNode


# getMatchMenu('c_hand')


def crtMatchIKFK(ctrlIK, lCtrlFK, ctrlSwitch):
    matchNode = getMatchMenu(ctrlIK)
    mc.connectAttr(ctrlSwitch + '.message', matchNode + '.switch', f=True)
    i = 0
    for ctrl in lCtrlFK:
        mc.addAttr(ctrl, ln='menuMatchIKFK', at='message')
        mc.connectAttr(ctrl + '.message', matchNode + '.fk[' + str(i) + ']', f=True)
        mc.connectAttr(matchNode + '.message', ctrl + '.menuMatchIKFK', f=True)
        i += 1
    dummy = mc.createNode('transform')
    mc.setAttr(dummy + '.rotateOrder', mc.getAttr(ctrlIK + '.rotateOrder'))
    mc.delete(mc.parentConstraint(ctrlIK, dummy, mo=False))
    mc.parent(dummy, lCtrlFK[-1])
    for val in ['X', 'Y', 'Z']:
        mc.setAttr(ctrlIK + '.orientOffset' + val, mc.getAttr(dummy + '.rotate' + val))
    mc.delete(dummy)



#crtMatchIKFK('WORLD:ARM_L_1:c_handIK_L', [], 'WORLD:ARM_L_1:c_armSwitch_L')