import maya.cmds as mc

from ellipse_rig.library import lib_glossary, lib_dataNodes, lib_controlGroup, lib_math, lib_dagMenu, lib_clean, lib_namespace
reload(lib_glossary)
reload(lib_dataNodes)
reload(lib_controlGroup)
reload(lib_math)
reload(lib_dagMenu)
reload(lib_clean)
reload(lib_namespace)

from library.lib_glossary import lexiconAttr as attrName


def connectAutoHide():
    networkNodes = mc.ls(type='network')
    for node in networkNodes:
        if mc.attributeQuery('ik', n=node, ex=True):
            ctrlIk = mc.listConnections(node+'.ik', s=True, d=False)[0]
            mc.setAttr(ctrlIk+'.overrideEnabled', 1)

            lCtrlFk = mc.listConnections(node+'.fk', s=True, d=False)
            ctrlSwitch = mc.listConnections(node+'.switch', s=True, d=False)[0]

            cnd = mc.createNode('condition')
            rvs = mc.createNode('reverse')
            clmp = mc.createNode('clamp')

            mc.setAttr(cnd+'.firstTerm', 1)
            mc.setAttr(clmp+'.maxR', 1)
            mc.setAttr(clmp+'.maxG', 1)
            for ctrl in lCtrlFk:
                lShp = mc.listRelatives(ctrl, s=True)
                shp = ''
                for i in lShp:
                    if not mc.attributeQuery('nodeType', n=i, ex=True):
                        shp = i
                mc.setAttr(shp+'.overrideEnabled', 1)
                mc.connectAttr(cnd+'.outColorR', shp+'.drawOverride.overrideVisibility')

            mc.connectAttr(cnd+'.outColorG', ctrlIk+'.drawOverride.overrideVisibility')
            mc.connectAttr(ctrlSwitch+'.autoHideIKFK', cnd+'.secondTerm')
            mc.connectAttr(ctrlSwitch+'.ikBlend', clmp+'.inputR')
            mc.connectAttr(clmp+'.outputR', rvs+'.inputX')
            mc.connectAttr(clmp+'.outputR', cnd+'.colorIfTrueG')
            mc.connectAttr(rvs+'.outputX', cnd+'.colorIfTrueR')




def crtHook(driver, father):
    hook = 'hook'+driver[len(driver.split('_')[0]):]
    if not mc.objExists('hook'+driver[len(driver.split('_')[0]):]):
        hook = mc.createNode('transform', n='hook'+driver[len(driver.split('_')[0]):])
        dMat = mc.createNode('decomposeMatrix', n='dM'+driver[len(driver.split('_')[0]):])
        mMat = mc.createNode('multMatrix', n='mltM'+driver[len(driver.split('_')[0]):])
        mc.connectAttr(driver + '.worldMatrix[0]', mMat + '.matrixIn[0]')
        mc.connectAttr(hook + '.parentInverseMatrix[0]', mMat + '.matrixIn[1]')
        mc.connectAttr(mMat + '.matrixSum', dMat + '.inputMatrix')
        lAttr = ['translate', 'rotate', 'scale', 'shear']
        for i, attr in enumerate(['outputTranslate', 'outputRotate', 'outputScale', 'outputShear']):
            mc.connectAttr(dMat + '.' + attr, hook + '.' + lAttr[i])
        if father:
            mc.parent(hook, father)
    return hook




def remRef():
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    print 'removing REF :  ', lRef
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
            mc.file(ur=refNode)
            if lEdits:
                for edit in lEdits:
                    action = edit.split('|')[0]
                    mc.file(cr=refNode, editCommand=action)
            mc.file(ref, rr=True)
#remRef()


def cleanTpl(lTPLNodes):
    for node in lTPLNodes:
        if mc.objExists(node):
            chkLock = mc.lockNode(node, q=True)[0]
            if chkLock == False:
                try:
                    if not node == 'ikRPsolver':
                        mc.delete(node)
                except:
                    pass


def connHideGrp():
    dicCg = lib_controlGroup.getCgFatherToChild()
    dicMenuHideGrp = {}
    for cg in dicCg.keys():
        test = mc.listConnections(cg+'.members', s=True) or []
        if test:
            lCtrl = list(set(mc.listConnections(cg+'.members', s=True)))
            for child in dicCg[cg]:
                dicMenuHideGrp[child] = lCtrl
                lib_dagMenu.linkMenuHideGrp(dicMenuHideGrp)
#connHideGrp()

def importRootTplRef():
    rootRef = ''
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            if mc.referenceQuery(ref, ns=True) == ':ROOT':
                rootRef = ref
                mc.file(ref, ir=True)
                mc.namespace(rm=':ROOT', mnr=True)
                mc.namespace(set=':')
    return rootRef


def fistNspace():
    currentNspace = mc.namespaceInfo(cur=True)
    if not currentNspace == '':
        mc.namespace(set=':')
#fistNspace()

def doBuildRig(cleanScene = True, doCg = True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True):
    #if pipe == True:
        #lib_pipe.saveTpl()
    assetRootPath = ''
    if 'ROOT' in lib_namespace.lsAllNspace(toExclude=['UI', 'shared']):
        assetRootPath = importRootTplRef()
    fistNspace()

    lTPLNodes = mc.ls()
    hook = ''
    toto = lib_dataNodes.getTplDataNodes(attrName('moduleDataTpl'))
    dicLModules = lib_dataNodes.getBuildTplHi(lib_dataNodes.getTplDataNodes(attrName('moduleDataTpl')))
    lDataNodes = []
    for key in dicLModules.keys():
        for dataNode in dicLModules[key]:
            fistNspace()
            print 'working on :', dataNode
            #lDataNodes.append(dataNode)
            moduleType = mc.getAttr(dataNode+'.'+attrName('moduleType'))
            chkModuleFather = mc.listConnections(dataNode+'.'+attrName('attrParent'), s=True, d=False, plugs=False)
            if chkModuleFather:
                lAnchors = ['loc_FLY']
                moduleFather = chkModuleFather[0]
                moduleFatherType = mc.getAttr(moduleFather+'.'+attrName('moduleType'))
                id = mc.getAttr(dataNode+'.'+attrName('masterTpl'), s=True)
                masterTpl = mc.getAttr(dataNode+'.'+attrName('masterTpl')+'['+str(id-1)+']')

                mastTplFather = mc.listRelatives(masterTpl, p=True)[0]
                cnst = mc.listConnections(mastTplFather, type='parentConstraint', d=True) or []
                if cnst:
                    if mc.attributeQuery('driver', n=cnst[0], ex=True):
                        masterTpl = mc.listConnections(cnst[0]+'.driver', s=True)

                if mc.attributeQuery(attrName('listHooks'), n=moduleFather, ex=True):
                    lAnchors = []
                    for suce in range(0, mc.getAttr(moduleFather+'.'+attrName('listHooks'), s=True)):
                        lAnchors.append(mc.getAttr(moduleFather+'.'+attrName('listHooks')+'['+str(suce)+']'))

                if lAnchors:
                    father = lib_math.getNearestTrans(masterTpl, lAnchors)

                hook = crtHook(father, 'RIG')
                if not mc.attributeQuery('rigHook', n=dataNode, ex=True):
                    mc.addAttr(dataNode, ln='rigHook', dt='string')
                mc.setAttr(dataNode+'.rigHook', hook, type='string')
                try:
                    mc.setAttr(dataNode+'.rigHook', lock=True)
                except:
                    pass



            #__FLY__#############################################################
            if moduleType == 'FLY':
                from ellipse_rig.assets.asset_base import rig_world
                reload(rig_world)
                rig = rig_world.RigWorld()
                buildModule = rig.createRig()

            #__SPINE__###########################################################
            elif moduleType == 'spine':
                from ellipse_rig.assets.characters import rig_spine
                reload(rig_spine)
                rig = rig_spine.Spine(moduleType, dataNode, hook)
                buildModule = rig.createSpine()


            #__ARM__#############################################################
            elif moduleType == 'arm':
                from ellipse_rig.assets.characters import rig_member
                reload(rig_member)
                rig = rig_member.Member(moduleType, dataNode, hook)
                buildModule = rig.createEndMember()
                if mathcIkFk == True:
                    dicCtrl = lib_dataNodes.getMatchIkFkCtrl(dataNode)
                    lib_dagMenu.crtMatchIKFK(dicCtrl['IK'], dicCtrl['FK'], dicCtrl['Switch'])


            #__LEG__#############################################################
            elif moduleType == 'leg':
                from ellipse_rig.assets.characters import rig_member
                reload(rig_member)
                rig = rig_member.Member(moduleType, dataNode, hook)
                buildModule = rig.createEndMember()
                if mathcIkFk == True:
                    dicCtrl = lib_dataNodes.getMatchIkFkCtrl(dataNode)
                    lib_dagMenu.crtMatchIKFK(dicCtrl['IK'], dicCtrl['FK'], dicCtrl['Switch'])

            #__HEAD__############################################################
            elif moduleType == 'head':
                if moduleFatherType == 'neck':
                    hook = mc.getAttr(chkModuleFather[0]+'.rigHook')
                from ellipse_rig.assets.characters import rig_head
                reload(rig_head)
                rig = rig_head.Head(moduleType, dataNode, hook)
                buildModule = rig.createHead()

            #__HEAD__############################################################
            #elif moduleType == 'neck':
                #from ellipse_rig.assets.characters import rig_head
                #reload(rig_head)
                #rig = rig_head.Head(moduleType, dataNode, hook)
                #buildModule = rig.createHead()

            #__EYES__############################################################
            elif moduleType == 'eye':
                from ellipse_rig.assets.characters import rig_eyes
                reload(rig_eyes)
                rig = rig_eyes.Eyes(moduleType, dataNode, hook)
                buildModule = rig.createEyes()

            #__TAIL__############################################################
            elif moduleType in ['tail', 'antenna']:
                from ellipse_rig.assets.characters import rig_tail
                reload(rig_tail)
                rig = rig_tail.Tail(moduleType, dataNode, hook)
                buildModule = rig.createTail()




            #__FEATHER__#############################################################
            elif moduleType == 'featherPart':
                from ellipse_rig.assets.characters import rig_feather
                reload(rig_feather)
                print 'FEATHER :', moduleType, dataNode, hook
                rig = rig_feather.Feather(moduleType, dataNode, hook)
                buildModule = rig.createFeather()

            #__WING__################################################################
            elif moduleType == 'wing':
                from ellipse_rig.assets.characters import rig_wing
                reload(rig_wing)
                rig = rig_wing.Wing(moduleType, dataNode, hook)
                buildModule = rig.createWing()

            #__FACE__############################################################
            """
            elif moduleType == 'face':
                lRef = mc.file(mc.file(q=True, sceneName=True), q=True, reference=True)
                for ref in lRef:
                    if mc.referenceQuery(ref, ns=True) == ':FACE':
                        mc.file(ref, ir=True)
                mc.namespace(rm='FACE', mnr=True)
                if ':' in dataNode:
                    dataNode = dataNode.split(':')[-1]
            """


            lDataNodes.append(dataNode)


    if doCg == True:
        lCg = lib_controlGroup.getAllCg() or []
        lib_controlGroup.buildCG()
        if lCg:
            for node in lCg:
                cg = lib_controlGroup.setCg(node)
                lib_controlGroup.buildTplCg(cg)
        if mc.objExists('cg_face'):
            lib_controlGroup.buildTplCg(lib_controlGroup.setCg('cg_face'))
        if mc.objExists('FACE:cg_face'):
            lib_controlGroup.buildTplCg(lib_controlGroup.setCg('FACE:cg_face'))
        print 'CG built'

    if linkMirror == True:
        dicMirror = lib_dagMenu.getMirrorLinks(lDataNodes)
        lib_dagMenu.connectMirorCtrl(dicMirror)
        print 'mirror connected'

    if connMenuHideGrp == True:
        connHideGrp()
        connectAutoHide()
        print 'menuHiddeGroup connected'


    if cleanScene == True:
        cleanTpl(lTPLNodes)
        lib_clean.remTrash()
        remRef()
        lNspaces = lib_namespace.lsAllNspace(toExclude = ['UI', 'shared', 'FACE']) or []
        if lNspaces:
            for nspace in lNspaces:
                mc.namespace(rm=':'+nspace, dnc=True)
        print 'rig cleaned'
    print 'RIG SUCCESFULY BUILT    motehrFucker'
    return assetRootPath

#doBuildRig(cleanScene = True, doCg = True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)



