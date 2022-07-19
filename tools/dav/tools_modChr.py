import maya.cmds as mc
from ellipse_rig.library import lib_pipe
import os
import glob



def saveNewRev():
    scenePath = mc.file(q=True, sceneName=True)
    incPath = lib_pipe.updateRev(scenePath)
    lib_pipe.nSaveScene(incPath, lib_pipe.getStepPath(incPath), lib_pipe.getTaskPath(incPath), lib_pipe.getTypePath(incPath))



def loadStpChrPose():
    scenePath = mc.file(q=True, sceneName=True)
    step = 'STP'
    task = 'exp'
    nspace = 'TMP'
    asset = scenePath.split(r'/')[5]
    rigPath = scenePath[: len(scenePath)-len(scenePath.split(r'/')[-1])].replace('/wip/', '/exp/')
    assetType = scenePath.split(r'/')[4]
    expPath = rigPath.replace(r'/MOD/', '/STP/')+'SMF_STP_'+asset+'_'+task+'_v'
    print expPath
    lFiles = glob.glob(expPath+'*.ma')
    if lFiles:
        lastRev = max(lFiles, key=os.path.getmtime)
        if os.path.exists(lastRev):
            mc.file(lastRev, r=True, ns=nspace)
            print lastRev, 'loaded'
    else:
        mc.warning('no exp founded for : '+asset)
#loadStpChrPose()

def removeStpChrPose():
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nspace = mc.referenceQuery(ref, ns=True)
            if nspace == ':TMP':
                lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
                mc.file(ur=refNode)
                if lEdits:
                    for edit in lEdits:
                        action = edit.split('|')[0]
                        mc.file(cr=refNode, editCommand=action)
                print ref
                mc.file(ref, rr=True)
    if mc.namespace(ex=nspace):
        mc.namespace(rm=nspace)

def copyMshPose(lMsh):
    if lMsh:
        storageGrp = 'SHP_POSE'
        if not mc.objExists(storageGrp):
            #mc.rename(storageGrp, 'OLDSHP_POSE')
            storageGrp = mc.createNode('transform', n='SHP_POSE')
        #lSkin = mc.ls(r=True, type='skinCluster') or []
        #if lSkin:
            #lMsh = []
            #for skin in lSkin:
                #deformed = mc.skinCluster(skin, q=True, g=True) or []
                #if deformed:
                    #if mc.objectType(deformed[0]) == 'mesh':
                        #msh = mc.listRelatives(deformed[0], p=True) [0]
                        #if not msh in lMsh:
                            #lMsh.append(msh)
        for msh in lMsh:
            clearName = msh
            if ':' in msh:
                clearName = msh.split(':')[-1]
            shp = mc.listRelatives(msh, s=True, ni=True)[-1]
            lDef = mc.findDeformers(shp)
            if lDef:
                for node in lDef:
                    if mc.objectType(node) == 'blendShape':
                        mc.setAttr(node+'.envelope', 0)
            dupName = clearName.replace(clearName.split('_')[0], 'shpPose')
            if mc.objExists(dupName):
                mc.setAttr(dupName+'.v', False)
                mc.rename(dupName, dupName+'_OLD1')
            dup = mc.duplicate(msh, n=dupName)[0]
            for attr in ['translate', 'rotate', 'scale']:
                for chan in ['X','Y', 'Z']:
                    mc.setAttr(dup+'.'+attr+chan, lock=False)
            mc.parent(dup, storageGrp)
            mc.setAttr(dup+'.v', True)

#getCharPose(mc.ls(sl=True))



def smfModChrTool_ui():
    nWin = 'SMF_modChrTool'
    nPan = 'MASTER_panModChr'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_facialSepTool_UI = mc.window(nWin, t='mod chr tools'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tool', c='')
    mc.separator(h=2)
    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout('zizilol', adj=True, w=225)
    mc.separator(h=7.5, st='in')

    mc.frameLayout(l='Charaters in pose', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=3, adj=2)
    mc.button(l='LOAD rig pose', bgc=[.2,.3,.5], h=28, w=100, c='tools_modChr.loadStpChrPose()')
    mc.button(l='COPY msh pose', bgc=[.2,.5,.5], h=28, w=100, c='tools_modChr.copyMshPose(mc.ls(sl=True))')
    mc.button(l='UNLOAD rig pose', bgc=[.5,.2,.4], h=28, w=100, c='tools_modChr.removeStpChrPose()')
    #mc.setParent('..')
    #mc.rowLayout(nc=2, adj=1)
    #mc.button(l='connect BS', h=28, w=130, bgc=[.2,.5,.5], c='')
    #mc.button(l='connect OUTMESH', h=28, w=130, bgc=[.5,.2,.2], c='')
    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='Finalize attributes', cll=True)
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD DELETE ME', bgc=[.2,.5,.5], h=28, w=130, c='tools_modChr.lib_pipe.addDelMe()')
    mc.button(l='REMOVE DELETE ME', bgc=[.5,.2,.2], h=28, w=130, c='tools_modChr.lib_pipe.removeDelMe()')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD SKIP ME', h=28, w=130, bgc=[.2,.5,.5], c='tools_modChr.lib_pipe.addFlagAttr("skipMe", 1)')
    mc.button(l='REMOVE SKIP ME', h=28, w=130, bgc=[.5,.2,.2], c='tools_modChr.lib_pipe.addFlagAttr("skipMe", 0)')



    mc.showWindow(winSMF_facialSepTool_UI)
#smfFurTool_ui()

