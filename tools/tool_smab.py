import maya.cmds as mc
import maya.mel as mel
import sys
import os
from functools import partial
#pathCustom ='T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig'
#pathCustom ='C:\\STUFF'
#sys.path.append(pathCustom)
from ellipse_rig import prod_presets
reload(prod_presets)
from ellipse_rig.library import lib_controlGroup, lib_rigs, lib_namespace, lib_constraints, lib_pipe, lib_math, lib_deformers, lib_clean, lib_dagMenu, lib_modules
reload(lib_controlGroup)
reload(lib_rigs)
reload(lib_namespace)
reload(lib_constraints)
reload(lib_pipe)
reload(lib_math)
reload(lib_deformers)
reload(lib_clean)
reload(lib_dagMenu)
reload(lib_modules)
#from ellipse_rig.assets.characters import character_guide_ui
#from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import get_maya_main_window
#reload(character_guide_ui)


from ellipse_rig.tools.dav import tools_attach
reload(tools_attach)
mc.namespace(set=':')



def launchDagHack():
    fullPath = os.path.realpath(__file__)
    print 'fullPath :', fullPath
    targetPath = fullPath.replace(fullPath.split('ellipse_rig')[-1], '')
    print 'targetPath :', targetPath

    sys.path.append(targetPath)
    import dagMenuHack
    reload(dagMenuHack)


def addExpertMod(lNodes = ['MOD:ALL', 'RIG:ALL']):
    for node in lNodes:
        if mc.objExists(node):
            if not mc.attributeQuery('expertMode', n=node, ex=True):
                mc.addAttr(node, ln='expertMode', at='bool', dv=1)
#####################################
#def GuguTplTool():
    #im = character_guide_ui.CharacterGuide(parent=get_maya_main_window())
    #im.show()
########################################
#SPACE SWITCH
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


def linkMirrorCtrl(lNodes):
    if len(lNodes) == 2:
        for node in lNodes:
            if not mc.attributeQuery('control', node=node, ex=True):
                mc.addAttr(node, ln='control', at='message')
            if not mc.attributeQuery('nodesId', n=node, ex=True):
                mc.addAttr(node, ln='nodesId', dt='string', multi=True)
            if not mc.attributeQuery('nodes', n=node, ex=True):
                mc.addAttr(node, ln='nodes', at='message', multi=True)

        id = 0
        ids = mc.getAttr(lNodes[0] + '.nodesId', mi=True) or []
        if not ids:
            mc.setAttr(lNodes[0]+'.nodesId['+str(id)+']', 'mirror', type='string')
            mc.connectAttr(lNodes[1]+'.control', lNodes[0]+'.nodes['+str(id)+']')
        elif ids:
            for i in ids:
                if mc.getAttr(lNodes[0]+'.nodesId['+str(i)+']') == 'mirror':
                    mc.connectAttr(lNodes[1]+'.control', lNodes[0]+'.nodes['+str(i)+']')
                else:
                    id = i+1
            if id != 0:
                mc.setAttr(lNodes[0]+'.nodesId['+str(id)+']', 'mirror', type='string')
                mc.connectAttr(lNodes[1]+'.control', lNodes[0]+'.nodes['+str(id)+']')


        id = 0
        ids = mc.getAttr(lNodes[1] + '.nodesId', mi=True) or []
        if not ids:
            mc.setAttr(lNodes[1]+'.nodesId['+str(id)+']', 'mirror', type='string')
            mc.connectAttr(lNodes[0]+'.control', lNodes[1]+'.nodes['+str(id)+']')
        else:
            for i in ids:
                if mc.getAttr(lNodes[1]+'.nodesId['+str(i)+']') == 'mirror':
                    mc.connectAttr(lNodes[0]+'.control', lNodes[1]+'.nodes['+str(i)+']')
                else:
                    id = i+1
            if id != 0:
                mc.setAttr(lNodes[1]+'.nodesId['+str(id)+']', 'mirror', type='string')
                mc.connectAttr(lNodes[0]+'.control', lNodes[1]+'.nodes['+str(id)+']')
    else:
        mc.warning('you need to select two ctrl')
#linkMirrorCtrl(mc.ls(sl=True))


def parentShpToCtrl(lNodes):
    lCtrl = []
    lShp = lNodes
    for node in lNodes:
        if mc.attributeQuery('nodeType', n=node, ex=True):
            if mc.getAttr(node+'.nodeType') == 'control':
                lCtrl.append(node)
    for ctrl in lCtrl:
        lShp.remove(ctrl)

    if not lCtrl:
        mc.warning('you need to select at least one ctrl : does your selected ctrl is/are in a CG?')
    else:
        if not lShp:
            mc.warning('no shape to copy xas found in your selection')
        else:
            for ctrl in lCtrl:
                chkShp = mc.listRelatives(ctrl, s=True) or []
                if chkShp:
                    for oldShp in chkShp:
                        if not mc.attributeQuery('nodeType', n=oldShp, ex=True):
                            try:
                                mc.delete(oldShp)
                            except:
                                mc.setAttr(oldShp+'.v', False)
                                mc.select(oldShp)
                                lib_pipe.addFlagAttr("deleteMe", 1)
                i = 1
                for shp in lShp:
                    lCrv = mc.listRelatives(shp, s=True) or []
                    if lCrv:
                        if mc.attributeQuery('nodeType', n=lCrv[0], ex=True):
                            if mc.getAttr(node+'.nodeType') == 'control':
                                mc.parent(lCrv[0], ctrl, add=True, s=True)

                        else:
                            tmp = mc.duplicate(shp, n=shp+'Tmp')[0]
                            mc.parent(tmp, ctrl)
                            mc.makeIdentity(tmp, a=True)
                            mc.delete(mc.parentConstraint(ctrl, tmp, mo=False))
                            mc.makeIdentity(tmp, a=True)
                            mc.parent(tmp, world=True)
                            lCrv = mc.listRelatives(tmp, s=True)
                            for crv in lCrv:
                                mc.parent(crv, ctrl, r=True, s=True)
                                mc.rename(crv, ctrl+'Shape'+str(i))
                                i += 1
                            mc.delete(tmp)
                            i += 1

#parentShpToCtrl(mc.ls(sl=True))



def getAvalableId(node, attr):
    lastId = 0
    lIds = mc.getAttr(node+'.'+attr, mi=True) or []
    if lIds:
        lastId = lIds[-1]+1
    return lastId


def ubiOverideTools():
    print 'overideTools'


def crtHook(lDriver):
    lHooks = []
    for driver in lDriver:
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
        if not hook in lHooks:
            lHooks.append(hook)
    return lHooks

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

def crtInterpolationDrivers(lNodes, lDeformersType, nbrPoints=2):
    for node in lNodes:
        if mc.attributeQuery('deformersList', n=node, ex=True):
            lIds = mc.getAttr(node+'.deformersList', mi=True)
            lDeformerNodes = []
            for id in lIds:
                lPoints = []
                deformedNode = mc.listConnections(node+'.deformersList['+str(id)+']', s=True, d=False)[0]
                if mc.nodeType(deformedNode) in lDeformersType:
                    if mc.attributeQuery('falloffCurve', n=node, ex=True):
                        lPointsIds = mc.getAttr(deformedNode+'.falloffCurve', mi=True)
                        for pId in lPointsIds:
                            driver = "toto"#to do
                            smfCtrlOrt= "tutu"#to do
                            baseName = deformedNode[len(driver.split(':')[-1].split('_')[0]):]+'Interp'

                            root = mc.createNode('transform', n='root'+baseName, p=smfCtrlOrt)
                            ctrl = mc.createNode('transform', n='c'+baseName, p=root)

                            #mc.setAttr(deformedNode+'.falloffCurve['str(pId)+'].falloffCurve_Position', valX)#horizontale
                            #mc.setAttr(deformedNode+'.falloffCurve['str(pId)+'].falloffCurve_FloatValue', valY)#verticale

                            mc.addAttr(ctrl, ln='interpolation', at='enum', en='None:Linear:Smooth:Spline:')
                            mc.connectAttr(ctrl+'.interpolation', deformedNode+'.falloffCurve['+str(pId)+'].falloffCurve_Interp')
                            mc.connectAttr(ctrl+'.translateX', deformedNode+'.falloffCurve['+str(pId)+'].falloffCurve_Position')#horizontale
                            mc.connectAttr(ctrl+'.translateX', deformedNode+'.falloffCurve['+str(pId)+'].falloffCurve_FloatValue')#verticale



#crtInterpolationDrivers(mc.ls(sl=True), ['softMod', cluster'])



def crtEyelidsTpl():
    elUp = 'tpl_eyelidsUp_L'
    elUpSlpt = 'tpl_eyelidsUpSculpt_L'
    elDn = 'tpl_eyelidsDn_L'
    elDnSlpt = 'tpl_eyelidsDnSculpt_L'
    elCornExt = 'tpl_eyelidsCornExt_L'
    elCornInt = 'tpl_eyelidsCornInt_L'


    if not mc.objExists('tpl_eyelidsUp_L'):
        elUp = mc.spaceLocator(n='tpl_eyelidsUp_L')[0]
    mc.delete(mc.parentConstraint('MOD:adj_eyeLid_Up_L', elUp, mo=False))

    if not mc.objExists('tpl_eyelidsUpSculpt_L'):
        elUpSlpt = mc.spaceLocator(n='tpl_eyelidsUpSculpt_L')[0]
        mc.parent(elUpSlpt, elUp)
    mc.delete(mc.parentConstraint('MOD:adj_eyeLidSculpt_Up_L', elUpSlpt, mo=False))


    if not mc.objExists('tpl_eyelidsDn_L'):
        elDn = mc.spaceLocator(n='tpl_eyelidsDn_L')[0]
    mc.delete(mc.parentConstraint('MOD:adj_eyeLid_Dn_L', elDn, mo=False))

    if not mc.objExists('tpl_eyelidsDnSculpt_L'):
        elDnSlpt = mc.spaceLocator(n='tpl_eyelidsDnSculpt_L')[0]
        mc.parent(elDnSlpt, elDn)
    mc.delete(mc.parentConstraint('MOD:adj_eyeLidSculpt_Dn_L', elDnSlpt, mo=False))


    if not mc.objExists('tpl_eyelidsCornExt_L'):
        elCornExt = mc.spaceLocator(n='tpl_eyelidsCornExt_L')[0]
    mc.delete(mc.parentConstraint('MOD:adj_eyeLidsCornerExt_L', elCornExt, mo=False))

    if not mc.objExists('tpl_eyelidsCornInt_L'):
        elCornInt = mc.spaceLocator(n='tpl_eyelidsCornInt_L')[0]
    mc.delete(mc.parentConstraint('MOD:adj_eyeLidsCornerInt_L', elCornInt, mo=False))

    for tpl in [elUp, elDn, elCornExt, elCornInt]:
        try:
            mc.parent(tpl, 'SHP:tpl_eyeLids_L')
        except:
            print tpl, 'is already a child of SHP:tpl_eyeLids_L'
    lib_controlGroup.addTplsToCg([elUp, elUpSlpt, elDn, elDnSlpt, elCornExt, elCornInt], 'cg_face')
    for tpl in [elUp, elUpSlpt, elDn, elDnSlpt, elCornExt, elCornInt]:
        mc.setAttr(tpl+'.isMirrored', True)
        mc.setAttr(tpl+'.mirrorType', 0)
    lib_controlGroup.buildTplCg('cg_face')
    connectEyelidsPAckman()
#crtEyelidsTpl()







def connectEyelidsPAckman():
    dicEyelids = {
        'c_eyelidsUp_L' : {'clst':'MOD:adj_eyeLid_Up_L', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY'}}},
        'c_eyelidsUpSculpt_L' : {'clst':'MOD:adj_eyeLidSculpt_Up_L', 'chans':{'positive':{'translateX':'translateX', 'translateZ':'translateY', 'rotateX':'rotateX', 'rotateZ':'rotateY', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateY':'translateZ', 'rotateY':'rotateZ', }}},
        'c_eyelidsDn_L' : {'clst':'MOD:adj_eyeLid_Dn_L', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY', }}},
        'c_eyelidsDnSculpt_L' : {'clst':'MOD:adj_eyeLidSculpt_Dn_L', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY', }}},
        'c_eyelidsCornInt_L' : {'clst':'MOD:adj_eyeLidsCornerInt_L', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateY', 'translateZ':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateY', 'rotateZ':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{}}},
        'c_eyelidsCornExt_L' : {'clst':'MOD:adj_eyeLidsCornerExt_L', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateY', 'translateZ':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateY', 'rotateZ':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{}}},
        'c_eyelidsUp_R' : {'clst':'MOD:adj_eyeLid_Up_R', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY', }}},
        'c_eyelidsUpSculpt_R' : {'clst':'MOD:adj_eyeLidSculpt_Up_R', 'chans':{'positive':{'translateX':'translateX', 'translateZ':'translateY', 'rotateX':'rotateX', 'rotateZ':'rotateY', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateY':'translateZ', 'rotateY':'rotateZ', }}},
        'c_eyelidsDn_R' : {'clst':'MOD:adj_eyeLid_Dn_R', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY', }}},
        'c_eyelidsDnSculpt_R' : {'clst':'MOD:adj_eyeLidSculpt_Dn_R', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{'translateZ':'translateY', 'rotateZ':'rotateY', }}},
        'c_eyelidsCornInt_R' : {'clst':'MOD:adj_eyeLidsCornerInt_R', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateY', 'translateZ':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateY', 'rotateZ':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{}}},
        'c_eyelidsCornExt_R' : {'clst':'MOD:adj_eyeLidsCornerExt_R', 'chans':{'positive':{'translateX':'translateX', 'translateY':'translateY', 'translateZ':'translateZ', 'rotateX':'rotateX', 'rotateY':'rotateY', 'rotateZ':'rotateZ', 'scaleX':'scaleX', 'scaleY':'scaleY', 'scaleZ':'scaleZ'},
                                                                  'negative':{}}}
                                                                   }

    for ctrl in dicEyelids.keys():
        clst = dicEyelids[ctrl]['clst']
        for chan in dicEyelids[ctrl]['chans']['positive'].keys():
            dif = mc.getAttr(clst+'.'+dicEyelids[ctrl]['chans']['positive'][chan])
            if dif != mc.getAttr(ctrl+'.'+chan):
                nADL = 'aDL'+ctrl[len(ctrl.split('_')[0]) :]+'Off'+chan[0]+chan[-1]
                aDL = nADL
                if not mc.objExists(nADL):
                    aDL = mc.createNode('addDoubleLinear', n=nADL)
                mc.connectAttr(ctrl+'.'+chan, aDL+'.input1', f=True)
                mc.connectAttr(aDL+'.output', clst+'.'+dicEyelids[ctrl]['chans']['positive'][chan], f=True)
                mc.setAttr(aDL+'.input2', dif)
            else:
                mc.connectAttr(ctrl+'.'+chan, clst+'.'+dicEyelids[ctrl]['chans']['positive'][chan], f=True)



        for chan in dicEyelids[ctrl]['chans']['negative'].keys():
            nMDL = 'mDl'+ctrl[len(ctrl.split('_')[0]) :]+'Rvs'+chan[0]+chan[-1]
            mDL = nMDL
            if not mc.objExists(nMDL):
                mDL = mc.createNode('multDoubleLinear', n=nMDL)
            mc.setAttr(mDL+'.input2', -1)
            mc.connectAttr(ctrl+'.'+chan, mDL+'.input1', f=True)

            dif = mc.getAttr(clst+'.'+dicEyelids[ctrl]['chans']['negative'][chan])
            if dif != mc.getAttr(ctrl+'.'+chan):
                nADL = 'aDL'+ctrl[len(ctrl.split('_')[0]) :]+'Off'+chan[0]+chan[-1]
                aDL = nADL
                if not mc.objExists(nADL):
                    aDL = mc.createNode('addDoubleLinear', n=nADL)
                mc.connectAttr(mDL+'.output', aDL+'.input1', f=True)
                mc.connectAttr(aDL+'.output', clst+'.'+dicEyelids[ctrl]['chans']['negative'][chan], f=True)
                mc.setAttr(aDL+'.input2', dif)
            else:
                mc.connectAttr(mDL+'.output', clst+'.'+dicEyelids[ctrl]['chans']['negative'][chan], f=True)

#connectEyelidsPAckman()



def conIris():
    hookEyes = crtHook(['SHP:sk_eyes'])[0]

    dML = 'dM_eyeBall_L'
    if not mc.objExists(dML):
        dML = mc.createNode('decomposeMatrix', n='dM_eyeBall_L')
    mc.connectAttr('SHP:sk_eyeBall_L.worldMatrix[0]', dML+'.inputMatrix', f=True)

    divXL = 'div_irisX_L'
    if not mc.objExists(divXL):
        divXL = mc.createNode('floatMath', n='div_irisX_L')
        mc.setAttr(divXL+'.operation', 3)
    mc.connectAttr(dML+'.outputScaleX', divXL+'.floatB', f=True)
    mc.setAttr(divXL+'.floatA', mc.getAttr(dML+'.outputScaleX'))


    divYL = 'div_irisY_L'
    if not mc.objExists(divYL):
        divYL = mc.createNode('floatMath', n='div_irisY_L')
        mc.setAttr(divYL+'.operation', 3)
    mc.connectAttr(dML+'.outputScaleY', divYL+'.floatB', f=True)
    mc.setAttr(divYL+'.floatA', mc.getAttr(dML+'.outputScaleY'))

    mDLIrisXL = 'mDl_irisX_L'
    if not mc.objExists(mDLIrisXL):
        mc.createNode('multDoubleLinear', n='mDl_irisX_L')
    mc.connectAttr('MOD:geo_eye_L.adjIrisX', mDLIrisXL+'.input1', f=True)
    mc.connectAttr(divXL+'.outFloat', mDLIrisXL+'.input2', f=True)

    globSclIrisXL = 'mDl_globSclIrisX_L'
    if not mc.objExists(globSclIrisXL):
        mc.createNode('multDoubleLinear', n='mDl_globSclIrisX_L')
    mc.connectAttr(hookEyes+'.scaleX', globSclIrisXL+'.input1', f=True)
    mc.connectAttr(mDLIrisXL+'.output', globSclIrisXL+'.input2', f=True)
    mc.connectAttr(globSclIrisXL+'.output', 'MOD:polyMoveVertex9.scaleX', f=True)
    mc.connectAttr(globSclIrisXL+'.output', 'MOD:polyMoveVertex11.scaleX', f=True)

    mDLIrisYL = 'mDl_irisY_L'
    if not mc.objExists(mDLIrisYL):
        mc.createNode('multDoubleLinear', n='mDl_irisY_L')
    mc.connectAttr('MOD:geo_eye_L.adjIrisY', mDLIrisYL+'.input1', f=True)
    mc.connectAttr(divYL+'.outFloat', mDLIrisYL+'.input2', f=True)

    globSclIrisYL = 'mDl_globSclIrisY_L'
    if not mc.objExists(globSclIrisYL):
        mc.createNode('multDoubleLinear', n='mDl_globSclIrisY_L')
    mc.connectAttr(hookEyes+'.scaleY', globSclIrisYL+'.input1', f=True)
    mc.connectAttr(mDLIrisYL+'.output', globSclIrisYL+'.input2', f=True)
    mc.connectAttr(globSclIrisYL+'.output', 'MOD:polyMoveVertex9.scaleY', f=True)
    mc.connectAttr(globSclIrisYL+'.output', 'MOD:polyMoveVertex11.scaleY', f=True)


    mDLPupilXL = 'mDl_pupilX_L'
    if not mc.objExists(mDLPupilXL):
        mc.createNode('multDoubleLinear', n='mDl_pupilX_L')
    mc.connectAttr('MOD:geo_eye_L.adjPupilX', mDLPupilXL+'.input1', f=True)
    mc.connectAttr(divXL+'.outFloat', mDLPupilXL+'.input2', f=True)


    globSclPupilXL = 'mDl_globSclPupilX_L'
    if not mc.objExists(globSclPupilXL):
        mc.createNode('multDoubleLinear', n='mDl_globSclPupilX_L')
    mc.connectAttr(hookEyes+'.scaleX', globSclPupilXL+'.input1', f=True)
    mc.connectAttr(mDLPupilXL+'.output', globSclPupilXL+'.input2', f=True)
    mc.connectAttr(globSclPupilXL+'.output', 'MOD:polyMoveVertex4.scaleX', f=True)


    mDLPupilYL = 'mDl_pupilY_L'
    if not mc.objExists(mDLPupilYL):
        mc.createNode('multDoubleLinear', n='mDl_pupilY_L')
    mc.connectAttr('MOD:geo_eye_L.adjPupilY', mDLPupilYL+'.input1', f=True)
    mc.connectAttr(divYL+'.outFloat', mDLPupilYL+'.input2', f=True)

    globSclPupilYL = 'mDl_globSclPupilY_L'
    if not mc.objExists(globSclPupilYL):
        mc.createNode('multDoubleLinear', n='mDl_globSclPupilY_L')
    mc.connectAttr(hookEyes+'.scaleY', globSclPupilYL+'.input1', f=True)
    mc.connectAttr(mDLPupilYL+'.output', globSclPupilYL+'.input2', f=True)
    mc.connectAttr(globSclPupilYL+'.output', 'MOD:polyMoveVertex4.scaleY', f=True)

    ##################################################################################################
    dMR = 'dM_eyeBall_R'
    if not mc.objExists(dMR):
        dMR = mc.createNode('decomposeMatrix', n='dM_eyeBall_R')
    mc.connectAttr('SHP:sk_eyeBall_R.worldMatrix[0]', dMR+'.inputMatrix', f=True)

    divXR = 'div_irisX_R'
    if not mc.objExists(divXR):
        divXR = mc.createNode('floatMath', n='div_irisX_L')
        mc.setAttr(divXR+'.operation', 3)
    mc.connectAttr(dMR+'.outputScaleX', divXR+'.floatB', f=True)
    mc.setAttr(divXR+'.floatA', mc.getAttr(dMR+'.outputScaleX'))

    divYR = 'div_irisY_R'
    if not mc.objExists(divYR):
        divYR = mc.createNode('floatMath', n='div_irisY_R')
        mc.setAttr(divYR+'.operation', 3)
    mc.connectAttr(dMR+'.outputScaleY', divYR+'.floatB', f=True)
    mc.setAttr(divYR+'.floatA', mc.getAttr(dMR+'.outputScaleY'))

    mDLIrisXR = 'mDl_irisX_R'
    if not mc.objExists(mDLIrisXR):
        mc.createNode('multDoubleLinear', n='mDl_irisX_R')
    mc.connectAttr('MOD:geo_eye_R.adjIrisX', mDLIrisXR+'.input1', f=True)
    mc.connectAttr(divXR+'.outFloat', mDLIrisXR+'.input2', f=True)


    globSclIrisXR = 'mDl_globSclIrisX_R'
    if not mc.objExists(globSclIrisXR):
        mc.createNode('multDoubleLinear', n='mDl_globSclIrisX_R')
    mc.connectAttr(hookEyes+'.scaleX', globSclIrisXR+'.input1', f=True)
    mc.connectAttr(mDLIrisXR+'.output', globSclIrisXR+'.input2', f=True)
    mc.connectAttr(globSclIrisXR+'.output', 'MOD:polyMoveVertex12.scaleX', f=True)
    mc.connectAttr(globSclIrisXR+'.output', 'MOD:polyMoveVertex10.scaleX', f=True)

    mDLIrisYR = 'mDl_irisY_R'
    if not mc.objExists(mDLIrisYR):
        mc.createNode('multDoubleLinear', n='mDl_irisY_R')
    mc.connectAttr('MOD:geo_eye_R.adjIrisY', mDLIrisYR+'.input1', f=True)
    mc.connectAttr(divYR+'.outFloat', mDLIrisYR+'.input2', f=True)


    globSclIrisYR = 'mDl_globSclIrisY_R'
    if not mc.objExists(globSclIrisYR):
        mc.createNode('multDoubleLinear', n='mDl_globSclIrisY_R')
    mc.connectAttr(hookEyes+'.scaleY', globSclIrisYR+'.input1', f=True)
    mc.connectAttr(mDLIrisYR+'.output', globSclIrisYR+'.input2', f=True)
    mc.connectAttr(globSclIrisYR+'.output', 'MOD:polyMoveVertex12.scaleY', f=True)
    mc.connectAttr(globSclIrisYR+'.output', 'MOD:polyMoveVertex10.scaleY', f=True)


    mDLPupilXR = 'mDl_pupilX_R'
    if not mc.objExists(mDLPupilXR):
        mc.createNode('multDoubleLinear', n='mDl_pupilX_R')
    mc.connectAttr('MOD:geo_eye_R.adjPupilX', mDLPupilXR+'.input1', f=True)
    mc.connectAttr(divXR+'.outFloat', mDLPupilXR+'.input2', f=True)


    globSclPupilXR = 'mDl_globSclPupilX_R'
    if not mc.objExists(globSclPupilXR):
        mc.createNode('multDoubleLinear', n='mDl_globSclPupilX_R')
    mc.connectAttr(hookEyes+'.scaleX', globSclPupilXR+'.input1', f=True)
    mc.connectAttr(mDLPupilXR+'.output', globSclPupilXR+'.input2', f=True)
    mc.connectAttr(globSclPupilXR+'.output', 'MOD:polyMoveVertex7.scaleX', f=True)


    mDLPupilYR = 'mDl_pupilY_R'
    if not mc.objExists(mDLPupilYR):
        mc.createNode('multDoubleLinear', n='mDl_pupilY_R')
    mc.connectAttr('MOD:geo_eye_R.adjPupilY', mDLPupilYR+'.input1', f=True)
    mc.connectAttr(divYR+'.outFloat', mDLPupilYR+'.input2', f=True)


    globSclPupilYR = 'mDl_globSclPupilY_R'
    if not mc.objExists(globSclPupilYR):
        mc.createNode('multDoubleLinear', n='mDl_globSclPupilY_R')
    mc.connectAttr(hookEyes+'.scaleY', globSclPupilYR+'.input1', f=True)
    mc.connectAttr(mDLPupilYR+'.output', globSclPupilYR+'.input2', f=True)
    mc.connectAttr(globSclPupilYR+'.output', 'MOD:polyMoveVertex7.scaleY', f=True)


    print 'iris and pupils tweaked'

#conIris()

def connectEyes(lCtrl):
    #lCtrl = ['c_eyeRoot_L', 'c_eyeRoot_R']
    if not lCtrl:
        mc.warning('you must select the c_eyeRot_[...] ctrl')
        return
    lGeoEyes = mc.ls('*.irisScale', r=True, o=True)
    for ctrl in lCtrl:
        #SquashEye#################################################
        father = mc.listRelatives(ctrl, p=True)[0]
        if not mc.attributeQuery('squash', n=ctrl, ex=True):
            mc.addAttr(ctrl, ln='squash', at='double', k=True, dv=0)

        mc.setDrivenKeyframe(father+'.scaleX.', cd=ctrl+'.squash', itt='linear', ott='linear', dv=0, v=1)
        mc.setDrivenKeyframe(father+'.scaleX', cd=ctrl+'.squash', itt='linear', ott='linear', dv=10, v=0.816497)


        mc.setDrivenKeyframe(father+'.scaleY', cd=ctrl+'.squash', itt='linear', ott='linear', dv=0, v=1)
        mc.setDrivenKeyframe(father+'.scaleY', cd=ctrl+'.squash', itt='linear', ott='linear', dv=10, v=1.5)

        mc.setDrivenKeyframe(father+'.scaleZ', cd=ctrl+'.squash', itt='linear', ott='linear', dv=0, v=1)
        mc.setDrivenKeyframe(father+'.scaleZ', cd=ctrl+'.squash', itt='linear', ott='linear', dv=10, v=0.816497)

        lDKeys = []
        lDKeys.append(mc.listConnections(father+'.scaleX', s=True, scn=True)[0])
        lDKeys.append(mc.listConnections(father+'.scaleY', s=True, scn=True)[0])
        lDKeys.append(mc.listConnections(father+'.scaleZ', s=True, scn=True)[0])
        for dKey in lDKeys:
            mc.setAttr(dKey+'.postInfinity', 4)
            mc.setAttr(dKey+'.preInfinity', 4)

        #ConnectEye#################################################
        geoEye = ''
        for node in lGeoEyes:
            if not mc.attributeQuery('nodeType', n=node, ex=True):
                endGeoEye = node.split('_')[-1]
                if endGeoEye == ctrl.split('_')[-1]:
                    geoEye = node

        lAttrs = mc.listAttr(geoEye, ud=True, k=True)
        toSkeep = []
        for id in range(0, len(lAttrs)):
            if not lAttrs[id] in toSkeep:
                type = mc.getAttr(geoEye+'.'+lAttrs[id], type=True)
                if type == 'double':
                    val = mc.getAttr(geoEye+'.'+lAttrs[id])
                    if not mc.attributeQuery(lAttrs[id], n=ctrl, ex=True):
                        mc.addAttr(ctrl, ln=lAttrs[id], at=type, dv=val, k=True)
                    try:
                        mc.connectAttr(ctrl+'.'+lAttrs[id], geoEye+'.'+lAttrs[id])
                    except:
                        pass

                elif type == 'double3':
                    lChilds = mc.attributeQuery(lAttrs[id], n=geoEye, lc=True)
                    if not mc.attributeQuery(lAttrs[id], n=ctrl, ex=True):
                        mc.addAttr(ctrl, ln=lAttrs[id], at=type)
                    inc = 0
                    for child in lChilds:
                        type = mc.getAttr(geoEye+'.'+child, type=True)
                        val = mc.getAttr(geoEye+'.'+child)
                        if not mc.attributeQuery(child, n=ctrl, ex=True):
                            mc.addAttr(ctrl, ln=child, at=type, p=lAttrs[id], dv=val, k=True)
                        #mc.connectAttr(ctrl+'.'+child, eye+'.'+child)
                        toSkeep.append(child)
                    for child in lChilds:
                        try:
                            mc.connectAttr(ctrl+'.'+child, geoEye+'.'+child)
                        except:
                            pass
        print ctrl, 'connected to ', geoEye
        conIris()



#connectEyes(mc.ls(sl=True)[0], mc.ls(sl=True)[1])


def setCtrlTransformToZero():
    lNodes = mc.ls('*.nodeType', o=True, r=True)
    for node in lNodes:
        if mc.getAttr(node+'.nodeType') == 'control':
            val = 0
            for attr in ['translate', 'rotate', 'scale']:
                if mc.attributeQuery(attr, n=node, ex=True):
                    if attr == 'scale':
                        val = 1
                    for chan in ['X', 'Y', 'Z']:
                        if not mc.getAttr(node+'.'+attr+chan, lock=True):
                            mc.setAttr(node+'.'+attr+chan, val)
#setCtrlTransformToZero()

###############################################################################################################
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


def replaceSkByMsh(lNodes):
    lSk = []
    mshSk = ''
    shpBase = ''
    for node in lNodes:
        if mc.nodeType(node) == 'joint':
            lSk.append(node)
        else:
            mshSk = node
    lShp = mc.listRelatives(mshSk, s=True) or []
    if lShp:
        if len(lShp)>1:
            for shp in lShp:
                if not mc.listConnections(shp+'.inMesh', s=True, d=False) and not mc.listConnections(shp+'.worldMesh[0]', s=True, d=False):
                    shpBase = shp
        elif len(lShp) == 1:
            tmpDup = mc.duplicate(mshSk)[0]
            shpBase = mc.listRelatives(tmpDup, s=True)[-1]

    for sk in lSk:
        lSkinPlugs = mc.listConnections(sk+".worldMatrix[0]", type="skinCluster", p=1)
        if lSkinPlugs:
            for skinPlug in lSkinPlugs:
                skin = skinPlug.split('.')[0]
                crvShp = mc.skinCluster(skin, q=True, g=True)[0]
                crv = mc.listRelatives(crvShp, p=True)[0]
                if not mshSk in mc.skinCluster(skin,query=True,inf=True):
                    mc.setAttr(skin+'.useComponents', 1)
                    mc.skinCluster(skin, e=True, ug=True, ps=0, ns=10, lw=True, ai=mshSk, bsh=shpBase, wt=1.0)
                    mc.skinCluster(skin, e=True, inf=sk, wt=0.0)
                lCvs = mc.ls(crv+'.cv[*]', fl=True)
                for cv in lCvs:
                    mc.skinPercent(skin, cv, transformValue=[(sk, 0.0), (mshSk, 1.0)])
                mc.select(crv)
                mel.eval('removeUnusedInfluences')
#replaceSkByMsh(mc.ls(sl=True))

"""
def genDifShpFromSkin(lMsh):
    if lMsh:
        if len(lMsh) == 2:
            mshDef = ''
            shp = ''
            for msh in lMsh:
                chkDef = mc.findDeformers(mc.listRelatives(msh, s=True, ni=True)[-1]) or []
                if chkDef:
                    for node in chkDef:
                        if mc.nodeType(node) == 'skinCluster':
                            mshDef = msh
                            break
            if mshDef:
                if shp:
                    lMsh.remove(mshDef)
                    shp = lMsh[0]
                    shpDif = mc.invertShape(shp, mshDef)
                    shpDif = mc.rename(shpDif, mshDef.split(':')[-1].replace(mshDef.split('_')[0], 'shp')+'Dif')
                    mc.parent(shpDif, world=True)
                else:
                    mc.warning('the two mesh in the selection are deformed by skinCluster)')
            else:
                mc.warning('no mesh in the selection is deformed by skinCluster)')
        else:
            mc.warning('you need to select two mesh')
    else:
        mc.warning('you need to select two mesh')

#genDifShpFromSkin(mc.ls(sl=True))
"""

def genDifShpFromSkin(lMsh):
    if lMsh:
        lFailed = []
        for msh in lMsh:
            if msh.startswith('MOD:'):
                mshDef = 'RIG:msh'+msh[len(msh.split('_')[0]) :]
                if mc.objExists(mshDef):
                    chkDef = mc.findDeformers(mc.listRelatives(mshDef, s=True, ni=True)[-1]) or []
                    chkSkin = mc.ls(chkDef, type='skinCluster') or []
                    if chkSkin:
                        activeDef(mshDef, False)
                        shpDif = mc.invertShape(mshDef, msh)
                        activeDef(mshDef, True)
                        shpDif = mc.rename(shpDif, mshDef.split(':')[-1].replace(mshDef.split('_')[0], 'shp')+'Dif')
                        try:
                            mc.parent(shpDif, world=True)
                        except:
                            pass
                        bs = mc.ls(chkDef, type='blendShape') or []
                        lastId = 0
                        if not bs:
                            bs = mc.blendShape(mshDef, n=mshDef.replace(mshDef.split('_')[0], 'bs'))
                            mc.reorderDeformers(chkSkin[0], bs[0], mshDef)
                        if len(bs) == 1:
                            lWght = mc.blendShape(bs[0], q=True, t=True) or []
                            if lWght:
                                lastId = mc.getAttr(bs[0]+'.inputTarget[0].inputTargetGroup', mi=True)[-1]+1
                            chkTrgt = mc.blendShape(bs[0], q=True, t=True) or []
                            if not shpDif in chkTrgt:
                                mc.blendShape(bs[0], edit=True, t=(mshDef, lastId, shpDif, 1.0))
                                mc.setAttr(bs[0]+'.'+shpDif, 1)
                        else:
                            mc.warning(mshDef+' have '+str(len(bs))+', please clean it')
                        #resetSkin([mshDef])

                    else:
                        mc.warning('the rig mesh is not deformed by skinCluster')
                else:
                    mc.warning('select mesh from MOD please')
            else:
                if not msh in lFailed:
                    lFailed.append(msh)
    else:
        mc.warning('you need to select the mesh from the MOD')
    if lFailed:
        print ('shp cennection failed on :', lFailed)
#genDifShpFromSkin(mc.ls(sl=True))

def genDifShpFromSkin_v2(lMsh):
    if lMsh:
        lFailed = []
        for msh in lMsh:
            if msh.startswith('MOD:'):
                mshDef = 'RIG:msh'+msh[len(msh.split('_')[0]) :]
                if mc.objExists(mshDef):
                    chkDef = mc.findDeformers(mc.listRelatives(mshDef, s=True, ni=True)[-1]) or []
                    chkSkin = mc.ls(chkDef, type='skinCluster') or []
                    if chkSkin:
                        mc.setAttr(chkSkin[0]+'.envelope', False)
                        dupName = mshDef.split(':')[-1].replace(mshDef.split(':')[-1].split('_')[0], 'shp')
                        dupNoSkin = mc.duplicate(mshDef)[0]
                        dupNoSkin = mc.rename(dupNoSkin,dupName+'NoSkin')
                        activeDef(mshDef, False)
                        mc.setAttr(chkSkin[0]+'.envelope', True)
                        shpDif = mc.invertShape(mshDef, msh)
                        shpDif = mc.rename(shpDif, dupName+'Dif')
                        activeDef(mshDef, False)
                        try:
                            for node in [dupNoSkin, shpDif]:
                                for attr in ['translate', 'rotate', 'scale']:
                                    for chan in ['X', 'Y', 'Z']:
                                        mc.setAttr(node+'.'+attr+chan, lock=False)
                                        mc.parent(node, world=True)

                        except:
                            pass
                        ######################################
                        #shpDif
                        vtxs = mc.polyEvaluate(mshDef, v=True)
                        posSrc = mc.xform(mshDef, q=True, ws=True, t=True)
                        posTrgt = mc.xform(dupNoSkin, q=True, ws=True, t=True)
                        dif = [posSrc[0]-posTrgt[0], posSrc[1]-posTrgt[1], posSrc[2]-posTrgt[2]]
                        posDest = mc.xform(shpDif, q=True, ws=True, t=True)

                        for i in range(0, vtxs):
                            posDefVtx = mc.xform(mshDef+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                            posNoSkinVtx = mc.xform(dupNoSkin+'.vtx['+str(i)+']', q=True, ws=True, t=True)
                            posDestVtx = mc.xform(shpDif+'.vtx['+str(i)+']', q=True, ws=True, t=True)

                            difSrc = [posDefVtx[0]-posSrc[0], posDefVtx[1]-posSrc[1], posDefVtx[2]-posSrc[2]]
                            difTrgt = [posNoSkinVtx[0]-posTrgt[0], posNoSkinVtx[1]-posTrgt[1], posNoSkinVtx[2]-posTrgt[2]]
                            difDest = [posDestVtx[0]-posDest[0], posDestVtx[1]-posDest[1], posDestVtx[2]-posDest[2]]

                            val = [difTrgt[0]-difSrc[0], difTrgt[1]-difSrc[1], difTrgt[2]-difSrc[2]]
                            valDif = [difDest[0]-val[0], difDest[1]-val[1], difDest[2]-val[2]]

                            mc.move(valDif[0], valDif[1], valDif[2], shpDif+'.vtx['+str(i)+']', co=True)
                        ########################################
                        activeDef(mshDef, True)
                        try:
                            mc.parent(shpDif, world=True)
                        except:
                            pass
                        bs = mc.ls(chkDef, type='blendShape') or []
                        lastId = 0
                        if not bs:
                            bs = mc.blendShape(mshDef, n=mshDef.replace(mshDef.split('_')[0], 'bs'))
                            mc.reorderDeformers(chkSkin[0], bs[0], mshDef)
                        if len(bs) == 1:
                            lWght = mc.blendShape(bs[0], q=True, t=True) or []
                            if lWght:
                                lastId = mc.getAttr(bs[0]+'.inputTarget[0].inputTargetGroup', mi=True)[-1]+1
                            chkTrgt = mc.blendShape(bs[0], q=True, t=True) or []
                            if not shpDif in chkTrgt:
                                mc.blendShape(bs[0], edit=True, t=(mshDef, lastId, shpDif, 1.0))
                                mc.setAttr(bs[0]+'.'+shpDif, 1)
                        else:
                            mc.warning(mshDef+' have '+str(len(bs))+', please clean it')
                        #lib_deformers.resetSkin([mshDef])

                    else:
                        mc.warning('the rig mesh is not deformed by skinCluster')
                else:
                    mc.warning('select mesh from MOD please')
            else:
                if not msh in lFailed:
                    lFailed.append(msh)
    else:
        mc.warning('you need to select the mesh from the MOD')
    if lFailed:
        print ('shp cennection failed on :', lFailed)
#genDifShpFromSkin_v2(mc.ls(sl=True))


def crtFreeRot():
    ctrl = lib_rigs.crtFreeRotCtrl()
    lib_controlGroup.addCtrlToCg([ctrl], 'cg_all')

def activeDef(shp, val):
    if mc.objectType(shp) == 'transform':
        shp = mc.listRelatives(shp, s=True, ni=True)[-1]
    lDef = mc.findDeformers(shp)
    if lDef:
        for node in lDef:
            mc.setAttr(node+'.envelope', val)
#activeDef(mc.ls(sl=True), False)


def crtMshSkinExtra(lMsh):
    lExtraMsh = []
    for msh in lMsh:
        activeDef(msh, 0)
        if not mc.attributeQuery('skinExtra', n=msh, ex=True):
            mc.addAttr(msh, ln='skinExtra', at='message')
            extraMsh = mc.duplicate(msh, n=msh+'SkinExtra')[0]
            lExtraMsh.append(extraMsh)
            mc.delete(extraMsh, ch=True)
            mc.connectAttr(extraMsh+'.message', msh+'.skinExtra')
            mc.addAttr(extraMsh, ln='meshDriver', dt='string')
            mc.setAttr(extraMsh+'.meshDriver', msh, type='string')
            bs = mc.blendShape(msh, extraMsh, n=extraMsh.replace('msh_', 'bs_'))[0]
            mc.setAttr(bs+'.'+msh.split(':')[-1], 1)
        else:
            extraMsh = mc.listConnections(msh+'.skinExtra', s=True, d=False)[0]
            lExtraMsh.append(extraMsh)
        activeDef(msh, 1)
    freezeJnt = ''
    chkSkFreeze = mc.ls('*sk_FREEZE', r=True) or []
    if not chkSkFreeze:
        freezeJnt = mc.createNode('joint', n='sk_FREEZE')
    else:
        freezeJnt = chkSkFreeze[0]
    #for extraMsh in lExtraMsh:
        #mc.skinCluster()
    return lExtraMsh
#crtMshSkinExtra(mc.ls(sl=True))

def crtLocFaceExtraTpl(lVtx):
    obj = lVtx[0].split('.')[0]
    lLoc = []
    lCa = []
    if not mc.attributeQuery('symTabLeft', n=obj, ex=True):
        lib_math.crtSymAttr([obj])
    for vtx in lVtx:
        vtxId = vtx.split('.vtx[')[-1][: -1]
        pos = mc.xform(vtx, q=True, ws=True, t=True)
        #locZone = mc.ls('*.sepZone', r=True, o=True)[0]
        #lZones = mc.attributeQuery('sepZone', n=locZone, le=True)[0].split(':')
        lZones = ['cheeks', 'cheekBones', 'eyebrows', 'eyelids', 'eyes', 'lips']
        zoneVal = ''
        for zone in lZones:
            zoneVal += zone+':'
        loc = mc.spaceLocator(n='loc_faceExtra_vtx'+str(vtxId))[0]
        lLoc.append(loc)
        mc.setAttr(loc+'.t', *pos)
        mc.addAttr(loc, ln='isExtraLoc', at='bool', dv=True)
        mc.addAttr(loc, ln='attachType', at='enum', en='nurbs:curves:', k=True)
        mc.addAttr(loc, ln='extraZone', at='enum', en=zoneVal, k=True)
        mc.addAttr(loc, ln='extraPole', at='enum', en='None:Up:Dn:Ft:Bk:Int:Mid:Ext:Corn:Tip', k=True)
        mc.addAttr(loc, ln='extraSlice', at='enum', en='None:Up:Dn:Ft:Bk:Int:Mid:Ext:Corn:Tip', k=True)
        mc.addAttr(loc, ln='extraInc', at='long', dv=1, min=1, k=True)
        mc.addAttr(loc, ln='extraVtx', dt='string')
        mc.addAttr(loc, ln='compHandle', dt='string')
        mc.setAttr(loc+'.extraVtx', vtx, type='string', lock=True)
        mc.setAttr(loc+'.compHandle', vtx, type='string', lock=True)
        lCa.append(tools_attach.crtCurveAttach([vtx, loc], 'TMP_PATH', 'TMP_LOC')[0])
        mc.addAttr(loc, ln='extraSide', at='enum', en='None:Left:Right:', k=True)
        if int(vtxId) in mc.getAttr(obj+'.symTabLeft')[0]:
            mc.setAttr(loc+'.extraSide', 1)
        if int(vtxId) in mc.getAttr(obj+'.symTabRight')[0]:
            mc.setAttr(loc+'.extraSide', 2)
    return lLoc
#crtLocFaceExtraTpl(mc.ls(sl=True, fl=True))


def editLocToComponent(lSel):
    tpl = ''
    comp = ''
    if not len(lSel) == 2:
        mc.warning('select only one locator and one component to attach it')
        return
    for sel in lSel:
        if mc.objectType(sel) == 'transform':
            tpl = sel
        elif mc.objectType(sel) == 'mesh':
            comp = sel
    mc.setAttr(tpl+'.compHandle', comp, type='string')


def buildFaceRigAdd():
    lLoc = mc.ls('*.isExtraLoc', r=True, o=True)
    lCg = []
    for loc in lLoc:
        if mc.getAttr(loc+'.isExtraLoc'):
            zone = mc.getAttr(loc+'.extraZone', asString=True)
            if zone == 'None':
                zone = ''
            pole = mc.getAttr(loc+'.extraPole', asString=True)
            if pole == 'None':
                pole = ''
            slice = mc.getAttr(loc+'.extraSlice', asString=True)
            if slice == 'None':
                slice = ''
            inc = str(mc.getAttr(loc+'.extraInc'))
            side = ''
            if mc.getAttr(loc+'.extraSide', asString=True) == 'Left':
                side = '_L'
            elif mc.getAttr(loc+'.extraSide', asString=True) == 'Right':
                side = '_R'
            name = 'tpl_'+zone+pole+slice+'Shp'+inc+side
            tpl = mc.rename(loc, name)
            mc.parent(tpl, world=True)
            for attr in ['attachType', 'extraZone', 'extraPole', 'extraSlice', 'extraInc', 'extraSide']:
                mc.setAttr(tpl+'.'+attr, k=False, cb=False)
            mc.setAttr(tpl+'.isExtraLoc', False)
            nCg = 'cg_'+zone.lower()+'Shp'
            if not nCg in lCg:
                lCg.append(nCg)
                lib_controlGroup.crtCg(nCg)
            lib_controlGroup.addTplsToCg([tpl], nCg)
            if side in ['_L', '_R']:
                mc.setAttr(tpl+'.isMirrored', True)

    mc.delete('TMP_PATH')
    mc.delete('TMP_LOC')
    for cg in lCg:
        lib_controlGroup.buildTplCg(cg)
        lTpl = lib_controlGroup.getTplFromCg(cg)
        lCtrl = lib_controlGroup.getCtrlFromCg(cg)
        for tpl in lTpl:
            attachTyp = mc.getAttr(tpl+'.attachType', asString=True)
            for ctrl in lCtrl:
                if ctrl in mc.listConnections(tpl+'.message', d=True):
                    root = ctrl.replace('c_', 'root_')
                    vtx = ''
                    if mc.attributeQuery('extraVtx', n=tpl, ex=True):
                        vtx = mc.getAttr(tpl+'.extraVtx')
                    elif mc.attributeQuery('compHandle', n=tpl, ex=True):
                        vtx =compHdl = mc.getAttr(tpl+'.compHandle')
                    if mc.getAttr(ctrl+'.mirrorSide') == 2:
                        msh = vtx.split('.')[0]
                        vtxId = float(vtx.split('[')[-1][: -1])
                        lenAttr = mc.getAttr(msh+'.symTabLeft', s=True)
                        for i in range(0, lenAttr):
                            if vtxId == mc.getAttr(msh+'.symTabLeft['+str(i)+']'):
                                vtx = msh+'.vtx['+str(mc.getAttr(msh+'.symTabRight['+str(i)+']'))+']'
                                break

                    if attachTyp == 'nurbs':
                        tools_attach.crtSurfAttach([vtx, root], 'PATH', cg.replace('cg_', 'rig_'))
                    elif attachTyp == 'curves':
                        tools_attach.crtCurveAttach([vtx, root], 'PATH', cg.replace('cg_', 'rig_'))







###########################################################################
###########################################################################
###########################################################################
#GET TAB
def getTab(tabSide, tabNames):
    getTab=mc.tabLayout(tabSide, q=True, sti=True)
    tab = ['']
    if getTab == 1:
        tab = tabNames[1]#'MASTERS_CG'
    elif getTab == 2:
        tab = tabNames[2]#'CONTROLE_GROUP'
    return tab[0]
###########################################################################
###########################################################################

###########################################################################
###########################################################################
#GET NAME FOR NEW CONTROL GROUP
def newCgName():
    getName=mc.textField('SMAB_getNewCGName', q=True, tx=True)
    return getName
###########################################################################
###########################################################################
#CG UTILS
def listCG():
    lCg = lib_controlGroup.getAllCg()
    return lCg

def crtCg():
    nCg = newCgName()
    lib_controlGroup.crtCg(nCg)
    cgTree = cg_tree_view(name='SMAB_cgTree', treeParent='SMAB_framLAyout', popUpName='SMAB_cgTreePopUp')
    cgTree.loadCgInTree(cgTree)

def parentCgTo(cg, cgFather):
    lib_controlGroup.parentCg(cg, cgFather)
    print cg, 'parented to : ', cgFather


def findCgFromTree():
    cgTree = cg_tree_view(name='SMAB_cgTree', treeParent='SMAB_framLAyout', popUpName='SMAB_cgTreePopUp')
    cgSel = cgTree.getSelectedItem()
    lCg = lib_controlGroup.getAllCg()
    for cg in lCg:
        if mc.attributeQuery('treeName', n=cg, ex=True):
            if mc.getAttr(cg+'.treeName') == cgSel:
                return cg

#ADD TEMPLATE TO CG*/
def addTplToCg(lTpl):
    cg = findCgFromTree()
    lib_controlGroup.addTplsToCg(lTpl, cg)

def addCtrlToCg(lCtrl):
    cg = findCgFromTree()
    lib_controlGroup.addCtrlToCg(lCtrl, cg)

def buildCg():
    cg = findCgFromTree()
    lib_controlGroup.buildTplCg(cg)

def listTplFromCg(cg):
    lTpl = mc.listConnections(cg+'.templates', s=True) or []
    return lTpl

def listCtrlFromCg(cg):
    lCtrl = []
    lMembers = mc.listConnections(cg+'.members', s=True, sh=True) or []
    for member in lMembers:
        lCtrl.append(member.split('|')[-1])
    return lCtrl

def removeFromCg(itemsList):
    #cg = findCgFromTree()
    lObj = getSelItemS(itemsList) or []
    if lObj:
        for obj in lObj:
            cg = mc.listConnections(obj+'.message', type='network', p=True) or []
            if cg:
                for i in cg:
                    mc.disconnectAttr(obj+'.message', i)
                print obj, 'disconnected from', cg[0].split('.')[0]

#removeFromCg(mc.ls(sl=True))


def pubAndVLay():
    pubVLay = mc.confirmDialog(t='Confirm', m='you want to publish with a VLAY?', b=['bha ouais!','oups, i miss-click'], db='bha ouais!', cb='oups, i miss-click')
    if pubVLay == 'bha ouais!':
        lib_pipe.publishRig(mc.file(q=True, sceneName=True), False, True, False, True)


## DEBBUG TOOLS#####################################

def buildModulesHp(doCleanCtr, doCgCtr, doMirrorCtr, doVisCtr, doMatchIKFKCtr, doSaveCtr, *args):

    doClean = mc.menuItem(doCleanCtr, q=True, cb=True)
    doCg =  mc.menuItem(doCgCtr, q=True, cb=True)
    doMirror = mc.menuItem(doMirrorCtr, q=True, cb=True)
    doVis = mc.menuItem(doVisCtr, q=True, cb=True)
    doMatchIKFK = mc.menuItem(doMatchIKFKCtr, q=True, cb=True)
    saveCtr = mc.menuItem(doSaveCtr, q=True, cb=True)
    print 'building module : clean=', doClean, 'cg=', doCg, 'mirrorCtrl=', doMirror, 'linkVis=', doVis, 'IKFKMatch=', doMatchIKFK, 'savScene=', saveCtr,

    from ellipse_rig import buildRig
    reload(buildRig)
    buildRig.doBuildRig(cleanScene=doClean, doCg=doCg, linkMirror=doMirror, connMenuHideGrp=doVis, mathcIkFk=doMatchIKFK, pipe=saveCtr)
    print 'build',

##########################################################################
#####################################
#UI UTILS#############################################################################################################
def getSelItemS (itemsList):
    getItem=mc.textScrollList(itemsList, q=True, si=True)
    return getItem

def selectItemInViewport(lItems):
    mc.select(cl=True)
    mc.select(lItems)
    print lItems, 'selected'

def updateTplList(itemsList):
    mc.textScrollList(itemsList, e=True, ra=True)
    cg = findCgFromTree()
    if cg:
        lTpl = listTplFromCg(cg)
        if not lTpl:
            lTpl = 'no tpl found for this cg'
        mc.textScrollList(itemsList, e=True, a=lTpl)
    else:
        mc.warning('no cg selected in the tree')

def updateCtrlList(itemsList):
    mc.textScrollList(itemsList, e=True, ra=True)
    cg = findCgFromTree()
    if cg:
        lCtrl = listCtrlFromCg(cg)
        if not lCtrl:
            lCtrl = 'no ctrl found for this cg'
        mc.textScrollList(itemsList, e=True, a=lCtrl)
    else:
        mc.warning('no cg selected in the tree')

def deleteSelItem(nTree):
    cgTree = cg_tree_view(name=nTree)
    item = findCgFromTree()
    if not mc.referenceQuery(item, inr=True):
        lib_controlGroup.deleteCg(item)
        cgTree.loadCgInTree(cgTree.name)
    else:
        mc.lockNode(item, lock=False)
        mc.addAttr(item, ln='deleteMe', at='bool', dv=True)
        mc.lockNode(item, lock=True)
        mc.warning(item+' is from a reference and can t be deleted directly: a "deleteMe" attr was added on this node and he will be removed at publish')

def reloadTree(nTree):
    tree = cg_tree_view(name=nTree)
    tree.loadCgInTree(nTree)

def parentOrphanCg(nTree):
    lib_controlGroup.parentOrphanCg()
    reloadTree(nTree)


class cg_tree_view():

    def __init__(self, name='', treeParent='', popUpName='', *args):
        self.name = name
        self.parent = treeParent
        self.itemSelId = 'id'
        self.popUp = popUpName
        self.itemSel = ''
        self.rnCgClbkInc = 0


    def buildTreeView(self):
        if not mc.objExists(self.name):
            mc.treeView(self.name, p=self.parent)
            mc.treeView(self.name, e=True, enk=True, ams=True)

            mc.treeView(self.name, e=True, dad=self.dADropClbk)

            mc.treeView(self.name, e=True, irc=self.rnCgClbk)
            mc.treeView(self.name, e=True, sc=self.selItemClbk)
            self.treePopUp()
        return self.name

    def getSelectedItem(self, *args):
        itemSel = mc.treeView(self.name, q=True, si=True)
        if itemSel:
            return itemSel[0]

    def selItemClbk(self, *args):
        self.itemSel = args[0]
        self.rnCgClbkInc = 0
        return True

    def rnCgClbk(self, *args):
        self.rnCgClbkInc += 1
        if self.rnCgClbkInc -1 == 0:
            lCg = lib_controlGroup.getAllCg()
            lExistingNames = []
            for cg in lCg:
                treeName = mc.getAttr(cg+'.treeName')
                if not treeName in lExistingNames:
                    lExistingNames.append(treeName)
            cg = self.itemSel
            newCg = cg
            newName = mc.treeView(self.name, q=True, si=True) or []
            if newName:
                print 'HERRE', newName
                newName = newName[0]
                if len(newName) > 3:
                    if not newName == newCg:
                        if not newName.startswith('cg_') and not ':' in cg:
                            newName = 'cg_'+newName
                        #if not mc.treeView(self.name, q=True, iex=newName):
                        if not newName in lExistingNames:
                            if mc.objExists(cg):
                                if not mc.referenceQuery(cg, inr=True):
                                    newCg = lib_controlGroup.renameCg(cg, newName)
                                    #self.rnCgClbkInc = 0
                            else:
                                lCg = listCG()
                                for existCg in lCg:
                                    if mc.getAttr(existCg+'.treeName') == newCg:
                                        newCg = existCg
                                        if not mc.referenceQuery(cg, inr=True):
                                            newCg = lib_controlGroup.renameCg(cg, newName)
                                            #self.rnCgClbkInc = 0
                            if mc.objExists(newCg):
                                mc.lockNode(newCg, lock=False)
                                mc.setAttr(newCg+'.treeName', newName, type='string')
                                mc.lockNode(newCg, lock=True)
                        else:
                            mc.warning(newName, 'already exists')
                            self.loadCgInTree(self.name)
                else:
                    mc.warning('the name is empty or have less than 3 caraters ("cg_" included in the caracters count)')
                    self.loadCgInTree(self.name)


    def dADropClbk(self, *args):
        #item = self.itemSel
        #newFather = mc.treeView(self.name, q=True, ip=self.itemSel)
        newFather = args[3]
        lItems = args[0]
        for item in lItems:
            if item != newFather:
                parentCgTo(self.itemSel, newFather)
                print item, 'parented to', newFather
            elif item == newFather:
                self.loadCgInTree(self.name)


    def loadCgInTree(self, cgTree):
        mc.treeView(self.name, e=True, ra=True)
        dicCg = lib_controlGroup.getCgHi(lib_controlGroup.getAllCg())
        for i in range(0, len(dicCg.keys())):
            for cg in dicCg[i]:
                father = ''
                chkFather = mc.listConnections(cg+'.parent', s=True, d=False) or []
                if chkFather:
                    father = chkFather[0]
                mc.treeView(self.name, e=True, addItem=(cg, father))
                if not mc.attributeQuery('treeName', n=cg, ex=True):
                    mc.lockNode(cg, lock=False)
                    mc.addAttr(cg, ln='treeName', dt='string')
                    mc.setAttr(cg+'.treeName', cg, type='string')
                    mc.lockNode(cg, lock=True)
                cgLabel = mc.getAttr(cg+'.treeName')
                if not cgLabel == cg:
                    if ':' in cg:
                        if cg.split(':')[-1] == cgLabel:
                            cgLabel = cg
                            mc.lockNode(cg, lock=False)
                            mc.setAttr(cg+'.treeName', cg, type='string')
                            mc.lockNode(cg, lock=True)


                mc.treeView(self.name, e=True, dl=(cg, cgLabel))




    def treePopUp(self):
        mc.popupMenu(self.popUp, p=self.name)
        mc.menuItem(l='add sel as TPL', p=self.popUp, c='tools_smab_v3.addTplToCg(mc.ls(sl=True))')
        mc.menuItem(l='add sel as CTRL', p=self.popUp, c='tools_smab_v3.addCtrlToCg(mc.ls(sl=True))')
        mc.menuItem(divider=True)
        mc.menuItem(l='build CG', p=self.popUp, c='tools_smab_v3.buildCg()')
        mc.menuItem(divider=True)

        mc.menuItem(l='delete CG', p=self.popUp, c='tools_smab_v3.deleteSelItem(tools_smab_v3.nCgTree)')
        mc.menuItem(divider=True)
        mc.menuItem(l='parent cgs to ', p=self.popUp, c='tools_smab_v3.parentOrphanCg(tools_smab_v3.nCgTree)')
        mc.menuItem(l='parent orphans to cg_all', p=self.popUp, c='tools_smab_v3.parentOrphanCg(tools_smab_v3.nCgTree)')
        mc.menuItem(l='Select in viewport', p=self.popUp, c='tools_smab_v3.selectItemInViewport(tools_smab_v3.findCgFromTree())')
        #mc.menuItem(l='show CG from sel', p=self.popUp)
        #mc.menuItem(l='select ctrl', p=self.popUp)
        #mc.menuItem(l='select tpl', p=self.popUp)

########################################################################################################################
#####################################
nTplList = 'templates'
nCtrlList = 'controlers'
nCgTree = 'SMAB_cgTree'


def SMAB_rigCharacterAdd_UI():
    nWin = 'SMAB_rigTool'
    nPan = 'SMAB_masterPan'
    #nFomLay = 'SMAB_formLayout'
    nFomLay = 'Control Groups'
    nFramLay = 'SMAB_framLAyout'
    nColumnLay = 'SMAB_treeColLay'
    version ='2.1'
    nNewCGName = 'SMAB_getNewCGName'
    #nTplList = 'templates'
    #nCtrlList = 'controlers'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_rigCharacterAdd_UI = mc.window(nWin, t='Setup Multy Asset Builder'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')


    mc.menu(l='File', to=True)
    mc.menuItem(l='Init wip_vanim', c='tools_smab_v3.lib_pipe.initWipVAni()')
    mc.menuItem(l='Maj refs', sm=True, to=True)
    mc.menuItem(l='ALL', c='tools_smab_v3.lib_pipe.updateRef(["MOD", "STP", "SHD", "FUR"])')
    mc.menuItem(l='MOD', c='tools_smab_v3.lib_pipe.updateRef(["MOD"])')
    mc.menuItem(l='STP', c='tools_smab_v3.lib_pipe.updateRef(["STP"])')
    mc.menuItem(l='SHD', c='tools_smab_v3.lib_pipe.updateRef(["SHD"])')
    mc.menuItem(l='FUR', c='tools_smab_v3.lib_pipe.updateRef(["FUR"])')
    mc.menuItem(l='MOD to SHD', c='tools_smab_v3.lib_pipe.switchStepRef("MOD", "high", "SHD", "base")')
    mc.menuItem(l='dVmarcket', c='tools_smab_v3.lib_pipe.publishRig(mc.file(q=True, sceneName=True), False, False, True)')
    mc.setParent('..', m=True)
    mc.menuItem(divider=True, dividerLabel='Saves')
    mc.menuItem(l='Save new revision', c='tools_smab_v3.lib_pipe.saveNewRev()')
    mc.menuItem(l='Publish', c='tools_smab_v3.lib_pipe.publishRig(mc.file(q=True, sceneName=True), False, False, False, True)')
    mc.menuItem(optionBox=True, c='tools_smab_v3.pubAndVLay()')
    mc.menuItem(divider=True, dividerLabel='Dag Menu')
    mc.menuItem(l='add expertMode', c='tools_smab_v3.addExpertMod()')
    mc.menuItem(l='hack dagMenu', c='tools_smab_v3.launchDagHack()')

    mc.setParent('..')
    mc.menu(l='Tools', to=True)
    mc.menuItem(l='connect char in pose sculpt', c='tools_smab_v3.genDifShpFromSkin_v2(mc.ls(sl=True))')
    mc.menuItem(l='remove anime curves', c='tools_smab_v3.lib_clean.deleteAniCrv()')
    mc.menuItem(l='add vis attr', c='tools_smab_v3.lib_pipe.addVisAttr_v2(mc.ls(sl=True))')
    mc.menuItem(l='connect stateSwitchs', c='tools_smab_v3.lib_pipe.connStatesSwitch()')
    mc.menuItem(l='set all ctrl trans to 0', c='tools_smab_v3.setCtrlTransformToZero()')




    mc.setParent('..')
    mc.menu(l='Tools FACE', to=True)
    mc.menuItem(l='convert VTX sel to LOC', c='tools_smab_v3.crtLocFaceExtraTpl(mc.ls(sl=True, r=True, fl=True))')
    mc.menuItem(l='convert LOCFACE to TPL', c='tools_smab_v3.buildFaceRigAdd()')
    mc.menuItem(l='generate skinExtra mesh', c='tools_smab_v3.crtMshSkinExtra(mc.ls(sl=True))')
    mc.menuItem(divider=True, dividerLabel='Eyes tools')
    mc.menuItem(l='connect eyes', c='tools_smab_v3.connectEyes(mc.ls(sl=True))')
    mc.menuItem(l='build eyelids cock', c='tools_smab_v3.crtEyelidsTpl()')
    mc.menuItem(divider=True, dividerLabel='Eyes patch')
    mc.menuItem(l='tweak iris', c='tools_smab_v3.conIris()')


    mc.setParent('..')
    mc.menu(l='Debbug', to=False)
    mc.menuItem(divider=True, dividerLabel='Options')
    mc.menuItem(l='build module options', sm=True, to=True)
    mc.menuItem(divider=True, dividerLabel='Debbug')
    mc.menuItem('chkBox_doClean', l='clean', cb=False)
    mc.menuItem('chkBox_doCg', l='build cg', cb=True)
    mc.menuItem('chkBox_doMirror', l='link mirror', cb=True)
    mc.menuItem('chkBox_doVis', l='connect vis', cb=True)
    mc.menuItem('chkBox_doMatchIKFK', l='IK FK match', cb=True)
    mc.menuItem('chkBox_doSave', l='do save', cb=False)
    mc.menuItem(divider=True, dividerLabel='Local Build')
    mc.menuItem(l='build', c=partial(buildModulesHp, 'chkBox_doClean', 'chkBox_doCg', 'chkBox_doMirror', 'chkBox_doVis', 'chkBox_doMatchIKFK', 'chkBox_doSave'))

    #mc.menuItem(l='switch loc to STP', c='tools_smab_v3.lib_pipe.rebuildRefInStp("STP")')
    #mc.menuItem(l='switch loc to MOD', c='tools_smab_v3.lib_pipe.rebuildRefInStp("MOD")')

    #mc.menuItem(l='CHAR tpl', c='tools_smab_v3.GuguTplTool()')

    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    mc.tabLayout('TAB_SMAB')
    formLay = mc.formLayout(nFomLay, p='TAB_SMAB', nd=100)
    ######
    colLayTree = mc.columnLayout(nColumnLay, adj=True, w=225)
    mc.text('enter name : ', al='left', font='boldLabelFont', h=12)
    mc.separator(h=2)
    mc.textField(nNewCGName, h=20)
    mc.separator(h=1, st='none')
    mc.button(l='create cg', h=25, bgc=[0.6, 0.75, 0.9], c='tools_smab_v3.crtCg()')
    mc.separator(h=5, st='in')
    #mc.button(l='update controlGroup', h=20, c='updateCgList("CONTROLE_GROUP")')
    #mc.separator(h=2, st='out')
    ######
    #mc.tabLayout('TAB_LEFT')
    ##############################################################################################################
    ##############################################################################################################
    #CONTROL GRP PANEL
    framLay = mc.frameLayout(nFramLay, p=formLay, l='Controls Groups')
    cgTree = cg_tree_view(name=nCgTree, treeParent=framLay, popUpName='SMAB_cgTreePopUp')
    cgTree.buildTreeView()
    #cgTree.editTree()
    mc.button('reload_btn', p=formLay,  l='reload', h=20, c='tools_smab_v3.reloadTree(tools_smab_v3.nCgTree)')

    ###########################################################################################################
    ##############################################################################################################
    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout('Modules', adj=True)
    mc.rowLayout(nc=2, adj=2)
    mc.columnLayout(adj=True)
    mc.button('btnSpineModule', l='Spine', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnSpineModule")')
    mc.button('btnArmModule', l='Arm', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnArmModule")')
    mc.button('btnLegModule', l='Leg', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnLegModule")')
    mc.button('btnNeckModule', l='Neck', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnNeckModule")')
    mc.button('btnEyeModule', l='Eye', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnEyeModule")')
    mc.button('btnTailModule', l='Tail', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnTailModule")')
    mc.button('btnWingModule', l='Wing', h=28, w=80, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnWingModule")')
    mc.button('btnSnakeModule', l='Snake', h=28, en=False, c='tools_smab_v3.lib_modules.modulesBtnSwitcher_UI("btnSnakeModule")')

    mc.setParent('..')
    mc.columnLayout('module_options', adj=True)
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.rowLayout(nc=2, adj=2)
    mc.button('symetryze module', h=28, w=120, c='tools_smab_v3.lib_modules.tplSym("L")')
    mc.button('reparent module to', h=28, w=120, c='tools_smab_v3.lib_modules.tplReparent()')
    mc.setParent('..')
    mc.button('Generate', h=28, bgc=[.2, .5, .5], c='tools_smab_v3.lib_modules.buildModuleTpl()')



    ##################
    mc.columnLayout(adj=True, w=175, p=pan)

    mc.frameLayout(l='attach tools', cll=True, bv=True, bgc=[.2, .5, .5], bgs=True)
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='create hook', h=28, w=130, c='tools_smab_v3.crtHook(mc.ls(sl=True))')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='surf attach', h=28, w=130, c='tools_smab_v3.tools_attach.crtSurfAttach(mc.ls(sl=True), "PATH", "SURFATTACH")')
    mc.button(l='curve attach', h=28, w=130, c='tools_smab_v3.tools_attach.crtCurveAttach(mc.ls(sl=True), "PATH", "CURVEATTACH")')
    mc.setParent('..')
    mc.setParent('..')

    mc.frameLayout(l='Space switch', cll=True, bv=True, bgc=[.5, .2, .4], bgs=True)
    mc.text('select driver(s) then the driven')
    mc.radioButtonGrp('rButtonSpSw', nrb=4, l='type : ', la4=['parent', 'point', 'orient', 'scale'], ct5=('left', 'left', 'left', 'left', 'left'), co5=(5, -100, -150, -205, -255))
    mc.radioButtonGrp('rButtonSpSw', e=True, select=1)
    mc.button(l='add spaceSwitch', h=28, w=130, c='tools_smab_v3.addSpaceSwitch("rButtonSpSw", mc.ls(sl=True))')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='remove spaceSwitch', h=28, w=130, bgc=[.5, .2, .2], c='tools_smab_v3.lib_dagMenu.removeSpaceSwitch(mc.ls(sl=True))')
    mc.button(l='remove from spaceSwitch', h=28, w=130, bgc=[.5, .2, .2], c='tools_smab_v3.lib_dagMenu.removeFromSpaceSwitch(mc.ls(sl=True))')
    mc.setParent('..')
    mc.setParent('..')

    mc.frameLayout(l='Ctrl', cll=True, bv=True, bgc=[.5, .3, .0], bgs=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='shape to ctrls', h=28, w=130, c='tools_smab_v3.parentShpToCtrl(mc.ls(sl=True))')
    mc.button(l='create freeRot', h=28, w=130, c='tools_smab_v3.crtFreeRot()')
    mc.setParent('..')
    mc.button(l='link ctrl as mirror', h=28, w=130, c='tools_smab_v3.linkMirrorCtrl(mc.ls(sl=True))')
    mc.setParent('..')

    mc.frameLayout(l='Deformers', cll=True, bv=True, bgc=[.2, .3, .5], bgs=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='add cluster', h=28, w=130, c='tools_smab_v3.addClst(mc.ls(sl=True))')
    mc.button(l='add softMod', h=28, w=130, c='tools_smab_v3.crtSoftMod(mc.ls(sl=True))')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='reset skin', h=28, w=130, c='tools_smab_v3.lib_deformers.resetSkin(mc.ls(sl=True))')
    mc.button(l='hack ctrl skin', h=28, w=130, c='tools_smab_v3.lib_deformers.ctrlSkinLocal(mc.ls(sl=True))')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='sk to msh skin', h=28, w=130, c='tools_smab_v3.replaceSkByMsh(mc.ls(sl=True))')
    mc.button(l='combine msh', h=28, w=130, c='tools_smab_v3.lib_deformers.combDeformedMesh(mc.ls(sl=True))')
    mc.setParent('..')
    mc.setParent('..')




    mc.frameLayout(l='Utils', cll=True, bv=True, bgc=[.5, .5, .2], bgs=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='add deleteMe', h=28, w=130, c='tools_smab_v3.lib_pipe.addFlagAttr("deleteMe", 1)')
    mc.button(l='remove deleteMe', h=28, w=130, c='tools_smab_v3.lib_pipe.addFlagAttr("deleteMe", 0)')



    ##################

    mc.columnLayout(adj=True, w=225, p=nPan)
    mc.frameLayout(l='List Attrs', cll=True, bv=True, bgc=[.5, .5, .5], bgs=True)


    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.button(l='update tab', h=20, c='tab=getTab(getNetWorkMember(tab))')
    mc.separator(height=2, style='out')
    ######
    mc.tabLayout('TAB_RIGHT')

    #nFramLayR = 'SMAB_framLAyoutR'
    nColumnLayR = 'SMAB_treeColLayR'
    #framLayR = mc.frameLayout(nFramLayR, p='TAB_RIGHT', l='Templates Liste')
    ################################################################################

    #tplTree = cg_tree_view(name='SMAB_tplTree', treeParent='TAB_RIGHT', popUpName='SMAB_tplTreePopUp')
    #tplTree.buildTreeView()

    #tplTree = cg_tree_view(name='SMAB_ctrlTree', treeParent='TAB_RIGHT', popUpName='SMAB_ctrlTreePopUp')
    #tplTree.buildTreeView()


    mc.textScrollList(nTplList, numberOfRows=8, ams=True, h=300, w=200)
    mc.popupMenu('SMAB_tplListPopup', b=3, mm=False, aob=True)
    mc.menuItem(l='Load cg TPL', c='tools_smab_v3.updateTplList(tools_smab_v3.nTplList)')
    mc.menuItem(l='Remove from cg', c='tools_smab_v3.removeFromCg(tools_smab_v3.nTplList)')
    mc.menuItem(divider=True)
    mc.menuItem(l='Select in viewport', c='tools_smab_v3.selectItemInViewport(tools_smab_v3.getSelItemS(tools_smab_v3.nTplList))')


    #mc.menuItem(l='remove template', p='editPopMen', c='removeFromCg (\'NEW_CG\')')

    mc.textScrollList(nCtrlList, numberOfRows=8, ams=True, h=300, w=200)
    mc.popupMenu('SMAB_ctrlListPopup', b=3, mm=False, aob=True)
    mc.menuItem(l='Load cg CTRL', c='tools_smab_v3.updateCtrlList(tools_smab_v3.nCtrlList)')
    mc.menuItem(l='Remove from cg', c='tools_smab_v3.removeFromCg(tools_smab_v3.nCtrlList)')
    mc.menuItem(divider=True)
    mc.menuItem(l='Select in viewport', c='tools_smab_v3.selectItemInViewport(tools_smab_v3.getSelItemS(tools_smab_v3.nCtrlList))')

    cgTree.loadCgInTree(cgTree)

    mc.formLayout(formLay, e=True,

                af=[(colLayTree, 'top', 5), (colLayTree, 'left', 5), (colLayTree, 'right', 5),
                    (framLay, 'left', 5), (framLay, 'right', 5),
                    ('reload_btn', 'left', 5), ('reload_btn', 'right', 5), ('reload_btn', 'bottom', 5)],
                ac=[(framLay, 'bottom', 5, 'reload_btn'), (framLay, 'top', 5, colLayTree)]
                )
    mc.showWindow(win_rigCharacterAdd_UI)
#SMAB_rigCharacterAdd_UI()

