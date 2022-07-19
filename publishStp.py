import sys
pathPush = r'T:\00_PROGRAMMATION\PRIMARY'
if not pathPush in sys.path:
    sys.path.append(pathPush)

# from ellipsanime.maya import bank
# bank.quickpushcurrent()
from smurf.sgutils import sg_operation as sgop


#scene_path = mc.file(location=True, q=True)
#sgop.CleanEdit_pusher(scene_path)


import maya.cmds as mc
from random import *


from ellipse_rig import buildRig
reload(buildRig)

from ellipse_rig.library import lib_pipe, lib_names
reload(lib_pipe)
reload(lib_names)
from ellipse_rig.tools.dav import tools_fur, tools_facialShapes, tools_characters, tools_anim, tools_rig, tools_smab
reload(tools_fur)
reload(tools_facialShapes)
reload(tools_characters)
reload(tools_anim)
reload(tools_rig)
reload(tools_smab)

def getStep():
    step = mc.optionMenu("stepSet", q=True, v=True)
    return step

def getRef():
    step = getStep()
    nspace = step
    newDirPath = lib_pipe.getPubPath(step)
    if step == 'STP':
        nspace = 'RIG'
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
    if step == 'STP':
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
            if taskChk == 'wip':
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


def rigAssetManager_ui():
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
    mc.button(l='PUBLISH', bgc=[.25,.2,.5], h=28, w=130, c='tools_publish.tmpPublish()')


    mc.showWindow(winSMF_facialSepTool_UI)
#rigAssetManager_ui()
