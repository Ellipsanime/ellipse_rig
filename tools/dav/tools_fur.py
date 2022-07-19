import maya.cmds as mc
from ellipse_rig.library import lib_pipe
import pymel.core as pm


def loadMOD(pathDir = r'T:\03_FAB\00_ASSETS\MOD\CHR'):
    path = mc.fileDialog2(dir=pathDir, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.file(path, r=True, ns='MOD')
#loadMOD(pathDir = r'T:\90_TEAM_SHARE\03_FAB\00_ASSETS\01_MOD\01_CHARS')

def unloadMOD():
    scenePath = mc.file(q=True, sceneName=True)
    #list les refs dans la scene
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nSpace = mc.referenceQuery(ref, ns=True)
            # si le namespace est MOD, on clean la ref et on remove
            if nSpace == ':MOD':
                lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
                mc.file(ur=refNode)
                if lEdits:
                    for edit in lEdits:
                        action = edit.split('|')[0]
                        mc.file(cr=refNode, editCommand=action)
                mc.file(ref, rr=True)
                print ref, 'removed'
#unloadMOD()

def setFurMesh(lObj, val):
    type = 'emitter'
    if val == 1:
        type = 'txt ref'
    elif val == 2:
        type == 'gab'
    for obj in lObj:
        if not mc.attributeQuery('fur', n=obj, ex=True):
            mc.addAttr(obj, ln='fur', at='enum', en=':emitter:txtRef:gab')
            mc.setAttr(obj+'.fur', val)
            mc.setAttr(obj+'.fur', lock=True)
        else:
            mc.setAttr(obj+'.fur', lock=False)
            mc.addAttr(obj+'.fur', e=True, at='enum', en=':emitter:txtRef:gab')
            mc.setAttr(obj+'.fur', val)
            mc.setAttr(obj+'.fur', lock=True)
    print lObj, 'was seted as', type

def tmpPublish():
    scenePath = mc.file(q=True, sceneName=True)
    type = lib_pipe.getTypePath(scenePath)
    task = 'EXP'
    step = lib_pipe.getStepPath(scenePath)
    incPath = lib_pipe.updateRev(scenePath)
    lib_pipe.nSaveScene(incPath, lib_pipe.getStepPath(incPath), lib_pipe.getTaskPath(incPath), lib_pipe.getTypePath(incPath))

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
        taskChk = lib_pipe.getTaskScene(scenePath)
        if taskChk == 'tpl':
            buildRig.doBuildRig(cleanScene=True, doCg=True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)
        elif taskChk == 'wip':
            lib_pipe.nPubBuild(scenePath, step, task, type, lib_names.refNspaceRIG())
            print 'EXP GENERATED'
            scenePath = mc.file(q=True, sceneName=True)
            lib_pipe.nPubAni(scenePath, step, 'ani', type, {})
    #nSaveScene(step, 'EXP', type)


def smfFurTool_ui():
    nWin = 'SMF_furTool'
    nPan = 'MASTER_panFur'
    version ='1.1'
    nNewCGName = 'getNewCGName'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_facialSepTool_UI = mc.window(nWin, t='fur moi tout ca'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tool', c='')
    mc.separator(h=2)
    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout('zizilol', adj=True, w=225)
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='References tools', cll=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='LOAD MOD    ', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.loadMOD()')
    mc.button(l='UNLOAD MOD', bgc=[1,.25,.5], h=28, w=100, c='tools_fur.unloadMOD()')

    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='Settings tools', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='SET EMITTER', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.setFurMesh(mc.ls(sl=True), 0)')
    mc.button(l='SET TXT REF', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.setFurMesh(mc.ls(sl=True), 1)')
    mc.button(l='SET GAB', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.setFurMesh(mc.ls(sl=True), 2)')

    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='Finalize', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='ADD DELETEME', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.lib_pipe.addDelMe()')
    mc.button(l='REMOVE DELETEME', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.lib_pipe.removeDelMe()')

    mc.setParent('..')
    mc.button(l='UNe BONNE FOIS POUR TOUTE!', bgc=[.25,.2,.5], h=28, w=100, c='tools_fur.tmpPublish()')


    mc.showWindow(winSMF_facialSepTool_UI)
#smfFurTool_ui()


