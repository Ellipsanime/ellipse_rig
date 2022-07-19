import maya.cmds as mc
from random import *

from ellipse_rig.assets.backGrounds import bg_build
reload(bg_build)

from ellipse_rig.assets.props import vlay_build
reload(vlay_build)

from ellipse_rig import buildRig
reload(buildRig)

from ellipse_rig.library import lib_pipe, lib_names
reload(lib_pipe)
reload(lib_names)
from ellipse_rig.tools.dav import tools_fur, tools_facialShapes, tools_characters, tools_anim, tools_rig, tools_smab, tools_ctrlShape
reload(tools_fur)
reload(tools_facialShapes)
reload(tools_characters)
reload(tools_anim)
reload(tools_rig)
reload(tools_smab)
reload(tools_ctrlShape)


def loadFurTools():
    import tools_fur
    reload(tools_fur)
    tools_fur.smfFurTool_ui()

def getStep():
    step = mc.optionMenu("stepSet", q=True, v=True)
    return step

def getRef():
    step = getStep()
    nspace = step
    newDirPath = lib_pipe.getNewDirPath(step)
    if step == 'STP':
        nspace = 'RIG'
    if step == 'Eyes':
        newDirPath = r'T:\03_FAB\00_ASSETS\MOD\BNK\HumanEyes\tmpPub\MAYA'
        nspace = step.upper()+'_1'
    elif step == 'IntMouth':
        newDirPath = r'T:\03_FAB\00_ASSETS\MOD\BNK\BuccalKit\tmpPub\MAYA'
        nspace = step.upper()+'_1'
    elif step == 'LightSet':
        bullShit = ['not today!', 'j ai la flemme la', 'ptit flipper?']
        i = randint(0, len(bullShit)-1)
        mc.warning(bullShit[i])
        return
    newPath = mc.fileDialog2(dir=newDirPath, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.file(newPath, r=True, ns=nspace)

def removeRef():
    step = getStep()
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            nSpace = mc.referenceQuery(ref, ns=True)
            if nSpace == ':'+step:
                lib_pipe.unloadRef(ref)

def saveNewRev():
    scenePath = mc.file(q=True, sceneName=True)
    incPath = lib_pipe.updateRev(scenePath)
    lib_pipe.nSaveScene(incPath, lib_pipe.getStepPath(incPath), lib_pipe.getTaskPath(incPath), lib_pipe.getTypePath(incPath))

def tmpPublish():
    scenePath = mc.file(q=True, sceneName=True)
    type = lib_pipe.getTypePath(scenePath)
    task = 'exp'
    step = lib_pipe.getStepPath(scenePath)
    incPath = lib_pipe.updateRev(scenePath)
    lib_pipe.nSaveScene(incPath, lib_pipe.getStepPath(incPath), lib_pipe.getTaskPath(incPath), lib_pipe.getTypePath(incPath))
    sceneName = lib_pipe.getSceneName(scenePath)
    sousDes = False
    if len(sceneName.split('_')) == 7:
        sousDes = True

    if step == 'MOD':
        lib_pipe.nPubMod(scenePath, step, task, type, lib_names.refNspaceMOD())
    elif step == 'UV':
        lib_pipe.nPubMod(scenePath, step, task, type, lib_names.refNspaceUV())
    elif step == 'TPL':
        lib_pipe.nPubTpl(scenePath, step, task, type, lib_names.refNspaceTPL())
    elif step == 'FUR':
       lib_pipe.nPubFur(scenePath, step, task, type, lib_names.refNspaceFUR())
    elif step == 'SHD':
        lib_pipe.nPubShd(scenePath, step, task, type, lib_names.refNspaceSHD())
    elif step == 'STP':
        typeChk = lib_pipe.getTypePath(scenePath)
        if typeChk == 'CHR':
            taskChk = lib_pipe.getTaskScene(scenePath)
            if taskChk == 'tpl':
                buildRig.doBuildRig(cleanScene=True, doCg=True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)
            if taskChk == 'sep':
                print 'to do'
            elif taskChk == 'wip':
                lib_pipe.nPubBuild(scenePath, step, task, type, lib_names.refNspaceRIG())
                print 'EXP GENERATED'

        elif typeChk == 'PRP':
            taskChk = lib_pipe.getTaskScene(scenePath)
            sd = lib_pipe.getSousDes(scenePath)
            if taskChk == 'vanim':
                lib_pipe.nPubBuild(scenePath, step, sd, type, lib_names.refNspaceRIG())
            if taskChk == 'vlay':
                lib_pipe.nPubBuild(scenePath, step, sd, type, lib_names.refNspaceRIG())



                lib_pipe.nPubBuild(scenePath, step, task, type, lib_names.refNspaceRIG())
                print 'EXP GENERATED'

        scenePath = mc.file(q=True, sceneName=True)
        lib_pipe.nPubAni(scenePath, step, 'ani', type, {})

    #nSaveScene(step, 'EXP', type)

def transAttrTo(nodeSrc, nodeDest):
    lAttr = mc.listAttr(nodeSrc, k=True, cb=False)
    for attr in lAttr:
        val = mc.getAttr(nodeSrc+'.'+attr)
        try:
            mc.setAttr(nodeDest+'.'+attr, val)
        except:
            print 'smab', attr

#transAttrTo(mc.ls(sl=True)[0], mc.ls(sl=True)[1])


def smfPublishTool_ui():
    nWin = 'SMF_pubTool'
    nPan = 'MASTER_panPub'
    version ='  1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_facialSepTool_UI = mc.window(nWin, t='passes moi donc le sel   '+version, tlb=True)


    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tools_Smab', c='tools_publish.tools_smab.SMAB_rigCharacterAdd_UI()')
    mc.menuItem(l='tools_Facial', c='tools_publish.tools_facialShapes.smfBlendShapesTool_ui()')
    mc.menuItem(l='tools_Ctrl', c='tools_publish.tools_ctrlShape.crtShapes_UI()')
    mc.menuItem(divider=True)
    mc.menuItem(l='build BG', c='tools_publish.bg_build.build()')
    mc.menuItem(divider=True)
    mc.menuItem(l='build vlay', c='tools_publish.vlay_build.buildPropsVlay()')


    mc.menuItem(divider=True)
    #mc.menuItem(l='tools_Fur', c='tools_publish.loadFurTools()')

    #mc.menuItem(divider=True)
    #mc.menuItem(l='tools_RigOld', c='tools_publish.tools_characters.smfCharactersTool_ui()')
    #mc.menuItem(l='tools_Rig WIP', c='tools_publish.tools_rig.smfRigTool_ui()')
    #mc.menuItem(divider=True)
    #mc.menuItem(l='tools_Uv', c='print "to do"')
    #mc.menuItem(divider=True)
    #mc.menuItem(l='tools_Ani', c='tools_publish.tools_anim.smfAnimTool_ui()')
    #mc.separator(h=2)

    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout(adj=True, w=225)
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='References tools', cll=True)
    mc.rowLayout(nc=3, adj=1)
    nTrgtType = mc.optionMenu('stepSet', label='STEP :')
    mc.menuItem( label='MOD')
    mc.menuItem( label='STP')
    mc.menuItem( label='UV')
    mc.menuItem( label='FUR')
    mc.menuItem( label='SHD')
    #mc.menuItem( label='ANI')
    mc.menuItem(divider=True)
    mc.menuItem( label='TURN')
    mc.menuItem( label='HumanEyes')
    mc.menuItem( label='BuccalKit')

    mc.button(l='LOAD REF', bgc=[.25,.2,.5], h=28, w=100, c='tools_publish.getRef()')
    mc.button(l='UNLOAD REF', bgc=[1,.25,.5], h=28, w=130, c='tools_publish.removeRef()')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='CLEANS', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD DELETE ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("deleteMe", 1)')
    mc.button(l='REMOVE DELETE ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("deleteMe", 0)')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD CLEAN ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("cleanMe", 1)')
    mc.button(l='REMOVE CLEAN ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("cleanMe", 0)')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD SKIP ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("skipMe", 1)')
    mc.button(l='REMOVE SKIP ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("skipMe", 0)')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD RIG ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("rigMe", 1)')
    mc.button(l='REMOVE RIG ME', h=28, w=130, c='tools_publish.lib_pipe.addFlagAttr("rigMe", 0)')



    #mc.setParent('..')
    #mc.rowLayout(nc=3, adj=1)
    #mc.button(l='CRT DUMMY', h=28, w=130, c='tools_publish.lib_pipe.genModDummy()')
    #mc.button(l='copy attr values to', h=28, w=130, c='tools_publish.lib_pipe.transAttrTo(mc.ls(sl=True)[0], mc.ls(sl=True)[1])')
    #mc.button(l='ACTIVE UNDO', bgc=[1, 1,.5], h=28, w=130, c='tools_publish.lib_pipe.reactiveUndo()')

    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Finalize', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='SAVE NEW REVISION', h=28, w=130, c='tools_publish.saveNewRev()')
    mc.button(l='GENERATE EXP', h=28, w=130, c='tools_publish.lib_pipe.publishRig(mc.file(q=True, sceneName=True), True)')

    mc.setParent('..')
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='PUBLISH', bgc=[.25,.2,.5], h=28, w=130, c='tools_publish.lib_pipe.publishRig(mc.file(q=True, sceneName=True), False)')



    mc.showWindow(winSMF_facialSepTool_UI)
#smfPublishTool_ui()
