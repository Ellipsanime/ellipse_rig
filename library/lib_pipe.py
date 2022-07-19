
import maya.mel as mel
import sys
import maya.cmds as mc
import os
from ellipse_rig.library import lib_clean as clean
from ellipse_rig.library import lib_names, lib_shapes, lib_controlGroup, lib_rigs
reload(clean)
reload(lib_names)
reload(lib_shapes)
reload(lib_controlGroup)
reload(lib_rigs)
from ellipse_rig import buildRig
reload(buildRig)
import glob



def quickPushInSG(path, type, step, task, asset ):

    """
    path = r"t:/test/SmurfBaby.ma"
    type = "PRP" or "BG" or "CHR"
    step = "STP"
    task = "vanimFull" or "vlay"
    asset = "SmurfBaby"

    """
    import core_lib.core_db.shotgun_db
    sg = core_lib.core_db.shotgun_db.Shotgun_DB()
    sg.quick_push(path, project_shortname="SMF", entity_type="Asset", entity_code=asset, step_shortname=step, task_name=task)



def pushInSG():
    pathPush = r'T:\00_PROGRAMMATION\PRIMARY'
    if not pathPush in sys.path:
        sys.path.append(pathPush)
    from ellipsanime import bank
    bank.quickpushcurrent()


#TOOLS############################################################
def addDelMe():
    #ajoute un attribut de deleteMe sur les nodes selectionnes
    lNodes = mc.ls(sl=True)
    for node in lNodes:
        if not mc.attributeQuery('deleteMe', n=node, ex=True):
            mc.addAttr(node, ln='deleteMe', at='bool', dv=1, k=False)
        mc.setAttr(node+'.deleteMe', 1)


def addFlagAttr(nAttr, val):
    lNodes = mc.ls(sl=True)
    #dicColor = {}
    #dicColor['deleteMe'] = [1, 0, 0]
    #dicColor['cleanMe'] = [1, .225, 0]
    #dicColor['rigMe'] = [1, 1, 0]
    #dicColor['skipMe'] = [0, 1, 0]
    for node in lNodes:
        if not mc.attributeQuery(nAttr, n=node, ex=True):
            lock = False
            if mc.lockNode(node, q=True, lock=True)[0] == True:
                mc.lockNode(node, lock=False)
                lock = True
            mc.addAttr(node, ln=nAttr, at='bool', dv=1, k=False)
            if lock == True:
                mc.lockNode(node, lock=True)
        mc.setAttr(node+'.'+nAttr, val)
        #mc.setAttr(node+'.useOutlinerColor',val)
        #mc.setAttr(node+'.outlinerColor', *dicColor[nAttr])


def removeDelMe():
    #ajoute un attribut de deleteMe sur les nodes selectionnes
    lNodes = mc.ls(sl=True)
    for node in lNodes:
        if mc.attributeQuery('deleteMe', n=node, ex=True):
            mc.setAttr(node+'.deleteMe', 0)

def reactiveUndo():
    mc.undoInfo(state=True)

def recursChkShp(obj, lGetMsh):
    chkShp = mc.listRelatives(obj, s=True) or []
    if chkShp:
        lGetMsh.append(obj)
    elif not chkShp:
        lChild = mc.listRelatives(obj, c=True) or []
        for child in lChild:
            recursChkShp(child, lGetMsh)
    return lGetMsh
#recursChkShp(mc.ls(sl=True)[0])

def genModDummy():
    lObj = mc.ls(sl=True)
    if not mc.objExists('DUMMY'):
        mc.createNode('transform', n='DUMMY')
        mc.parent('DUMMY', 'ALL')
    asset = getAssetPath(scenePath())
    grp = mc.createNode('transform', n='dum_'+asset.lower())
    mc.parent(grp, 'DUMMY')
    for obj in lObj:
        lGetMsh = []
        lMsh = recursChkShp(obj, lGetMsh)
        for msh in lMsh:
            clearName = msh
            if ':' in msh:
                clearName = msh.split(':')[-1]
            nDummy = 'dum'+clearName[len(clearName.split('_')[0]):]
            if not mc.objExists(nDummy):
                dummy = mc.duplicate(msh, n=nDummy)[0]
                for attr in ['translate', 'rotate', 'scale']:
                    for axe in ['X', 'Y', 'Z']:
                        mc.setAttr(dummy+'.'+attr+axe, lock=False)
                mc.delete(dummy, ch=True)
                mc.parent(dummy, grp)

#genModDummy()

#FOLDERS PATH UTILS################################################
def projectPath():
    path = r'T:\03_FAB\00_ASSETS\MOD\CHR\Smurf\wip\MAYA'
    return path

def scenePath():
    scPath = mc.file(q=True, sceneName=True)
    return scPath

def getSceneName(path):
    scName = path.split(r'/')[-1]
    return scName

def getDirPaf():
    scPath = mc.file(q=True, sceneName=True)
    nScene = scPath.split(r'/')[-1]
    rootDir = scPath.replace(nScene, '')
    return rootDir

def getStepPath(path):
    nPathStep = path.split(r'/')[3]
    return nPathStep

def getTaskPath(path):
    scPath = mc.file(q=True, sceneName=True)
    nPathTask = scPath.split(r'/')[-1]
    return nPathTask

def getAssetPath(path):
    nPathAsset = path.split(r'/')[5]
    return nPathAsset

def getTaskScene(path):
    scName = getSceneName(path)
    nSceneTask = scName.split('_')[-3]
    return nSceneTask

def getTypePath(path):
    scPath = mc.file(q=True, sceneName=True)
    nPathType = scPath.split(r'/')[4]
    return nPathType

def getSousDes(path):
    scName = getSceneName(path)
    sDes = scName.split('_')[3]
    return sDes


def getNewScenePath(step, task, type):
    scPath = mc.file(q=True, sceneName=True)

    nScene = scPath.split(r'/')[-1]
    nPathStep = scPath.split(r'/')[3]
    nPathType = scPath.split(r'/')[4]
    nPathAsset = scPath.split(r'/')[5]
    nPathTask = scPath.split(r'/')[6]

    scStep = nScene.split('_')[1]
    scAsset = nScene.split('_')[2]
    scTask = nScene.split('_')[-3]

    rootDir = scPath.replace(nScene, '')

    newScene = nScene.replace('_'+scStep+'_', '_'+step+'_')
    newDir = rootDir.replace(r'/'+nPathStep+r'/', r'/'+step+r'/')

    if task == 'EXP' or task == 'ani':
        newScene = nScene.replace('_'+scStep+'_', '_'+step+'_').replace('_'+scTask+'_', '_'+task+'_')
        newDir = rootDir.replace(r'/'+nPathStep+r'/', r'/'+step+r'/').replace(r'/'+nPathTask+r'/', r'/tmpPub/')
        if ('_art_') in newScene:
            newScene = newScene.replace('_art_', '_')

    #newFile = updateRev(newDir+newScene)

    return newDir+newScene
#getNewScenePath('STP', 'TPL', 'CHR')



def getNewDirPath(step):
    scPath = mc.file(q=True, sceneName=True)
    nScene = scPath.split(r'/')[-1]
    nPathStep = scPath.split(r'/')[3]
    nPathTask = scPath.split(r'/')[6]
    rootDir = scPath.replace(nScene, '')
    newDir = rootDir.replace(r'/'+nPathStep+r'/', r'/'+step+r'/').replace(r'/'+nPathTask+r'/', r'/tmpPub/')
    return newDir
#getNewDirPath('STP')

def getPubPath(task):
    scPath = mc.file(q=True, sceneName=True)
    rootDir = scPath.replace(scPath.split(r'/')[-1], '')
    pubDir = rootDir.split(r'/'+task)[0]
    return pubDir
#getPubPath('wip')


def updateRev(scenePath):
    sceneName = scenePath.split('.')[0]
    inc = sceneName.split('_')[-1]
    updateInc = str(int(inc)+1)
    newInc = inc[: len(inc)-len(updateInc)]+updateInc
    newScenPath = scenePath.replace('_'+inc, '_'+newInc)
    return newScenPath
#########################################################################
#SAVE UTILES###################################################################
def createFolder(folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
    except OSError:
        print ('Error: Creating directory. '+folder)
#createFolder(folder)

def nSaveScene(newPath, step, task, type):
    #sauvegarde de la scene PUBLIEE
    dirPath = getPubPath(task)
    cleanDirPath = dirPath.replace('/', '\\')
    cleanNewPAth = newPath.replace('/', '\\')
    createFolder(cleanDirPath)
    mc.file(scenePath, rn=cleanNewPAth)
    mc.file(save=True)
    return newPath
#nSaveScene(step, task, type)

def saveNewRev(*args):
    scenePath = mc.file(q=True, sceneName=True)
    incPath = updateRev(scenePath)
    nSaveScene(incPath, getStepPath(incPath), getTaskPath(incPath), getTypePath(incPath))
################################################################################
#REFERENCES UTILS###############################################################
def loadRef(pathDir, *args):
    path = mc.fileDialog2(dir=pathDir, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.file(path, r=True, ns='MOD')


def unloadRef(ref, *args):
    refNode = mc.referenceQuery(ref, rfn=True)
    lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
    mc.file(ur=refNode)
    if lEdits:
        for edit in lEdits:
            action = edit.split('|')[0]
            mc.file(cr=refNode, editCommand=action)
    mc.file(ref, rr=True)
    print ref, 'removed'

################################################################################
#PUBLISH UTILS##################################################################

def nPubMod(scenePath, step, task, type, dicNspaces, *args):
    print 'removing ref :'
    clean.refCleaner(mc.file(q=True, sceneName=True), dicNspaces)
    clean.hiFusion('MOD')
    print 'removing nodes :'
    clean.remTrash()
    clean.nspaceCleanner(dicNspaces)
    print 'saving scene'
    #sauvegarde de la scene PUBLIEE
    newFile = getNewScenePath(step, task, type)
    nSaveScene(newFile, step, task, type)
    print 'publish succesfuly done'


def nPubUv(scenePath, step, task, type, dicNspaces):
    print 'to do'
def nPubTpl(scenePath, step, task, type, dicNspaces):
    print 'to do'
def nPubFur(scenePath, step, task, type, dicNspaces,*args):
    print 'removing ref :'
    clean.refCleaner(mc.file(q=True, sceneName=True), dicNspaces)
    clean.nspaceCleanner(dicNspaces)
    print 'removing nodes :'
    clean.remTrash()
    print 'saving scene'
    #sauvegarde de la scene PUBLIEE
    newFile = getNewScenePath(step, task, type)
    nSaveScene(newFile, step, task, type)
    print 'publish succesfuly done'
def nPubShd(scenePath, step, task, type, dicNspaces):
    print 'to do'

def nPubBuild(scenePath, step, task, type, dicNspaces):
    print 'removing ref'
    clean.refCleaner(mc.file(q=True, sceneName=True), dicNspaces)
    clean.hiFusion('RIG')
    print 'removing nodes'
    clean.remTrash()
    clean.remove_nodes(['displayLayer', 'nodeGraphEditorInfo'], ['defaultLayer'])
    clean.deleteAniCrv()
    print 'removing namespaces'
    clean.nspaceCleanner(dicNspaces)


    print 'saving scene'
    #sauvegarde de la scene PUBLIEE
    newFile = getNewScenePath(step, task, type)
    nSaveScene(newFile, step, task, type)

    #clean.nspaceCleanner(dicNspaces)

def nPubAni(scenePath, step, task, type, dicNspaces):
    clean.lock_shapes_and_smooth()
    clean.set_joint_draw()
    clean.hide_ctrl_hist()
    newFile = getNewScenePath(step, task, type)
    nSaveScene(newFile, step, task, type)
    print 'ANI generated'

def flagNodes(ref):
    nspace = mc.referenceQuery(ref, ns=True)
    lNodes = mc.ls(nspace+':*', r=True)
    for node in lNodes:
        if not mc.attributeQuery('stepSource', n=node, ex=True):
            mc.addAttr(node, ln='stepSource', dt='string')
        mc.setAttr(node+'.stepSource', nspace.split(':')[-1], type='string')
        if nspace.split(':')[-1] == 'FUR':
            lCrvShp = mc.ls('FUR:*', r=True, type='nurbsCurve') or []
            if lCrvShp:
                for crvShp in lCrvShp:
                    crv = mc.listRelatives(crvShp, p=True)[0]
                    if not mc.attributeQuery('needRestPos', n=crv, ex=True):
                        mc.addAttr(crv, ln='needRestPos', at='bool', dv=True)

#flagNodes('${PROD_ROOT}/03_FAB/00_ASSETS/FUR/CHR/Azrael/SMF_FUR_Azrael_art_v006_001.ma')

def crvGuidesRestPosition():
    lCrv = mc.ls('*.needRestPos', r=True, o=True) or []
    if lCrv:
        mc.select(cl=True)
        mc.select(lCrv)
        mel.eval("pgYetiCommand -saveGuidesRestPosition")
        print 'rest position for guides updated on:', lCrv
    else:
        print 'no fur guides in this scene'

#crvGuidesRestPosition()

def removeGroom():
    lFurNodes = []
    lToKeep = []
    lToDel = []
    furBox = ''
    lNodes = mc.ls('*.stepSource', r=True, o=True)
    for node in lNodes:
        if mc.getAttr(node+'.stepSource') == 'FUR':
            lFurNodes.append(node)
            if mc.objectType(node) == 'transform':
                if not mc.attributeQuery('stepSource', n=mc.listRelatives(node, p=True)[0], ex=True):
                    furBox = node
                if mc.attributeQuery('fur', n=node, ex=True):
                    if mc.getAttr(node+'.fur') > 1:
                        lToKeep.append(node)
                else:
                    lToDel.append(node)
            elif mc.objectType(node) != 'mesh':
                lToDel.append(node)

    if lFurNodes:
        for node in lToKeep:
            mc.parent(node, furBox)
        if furBox in lToDel:
            lToDel.remove(furBox)
        mc.delete(lToDel)
    if furBox:
        if not mc.listRelatives(furBox, c=True):
            mc.delete(furBox)
#removeGroom()


################################################################################
#INIT STP WIP###################################################################

def addVisAttr(driver, driven):
    clearDriven = driven
    if ':' in driven:
        clearDriven = driven.split(':')[-1]
    nCnd = 'cnd'+clearDriven[len(driven.split('_')[0]) :]
    if not mc.attributeQuery('switch_vis', n=driver, ex=True):
        mc.addAttr(driver, ln='switch_vis', at='enum', en=':Hide:PrimaryOff:Show', k=True, dv=2)
    mc.connectAttr(driver+'.switch_vis', driven+'.visibility', f=True)
    if not mc.attributeQuery('primaryVisibility', n=driven, ex=True):
        mc.addAttr(driven, ln='primaryVisibility', at='bool')
    cnd = mc.createNode('condition', n=nCnd)
    mc.connectAttr(driver+'.switch_vis', cnd+'.firstTerm', f=True)
    mc.setAttr(cnd+'.secondTerm', 1)
    mc.setAttr(cnd+'.operation', 1)
    mc.connectAttr(cnd+'.outColorR', driven+'.primaryVisibility', f=True)
    mc.connectAttr(driven+'.primaryVisibility', driven+'.template', f=True)
    mc.connectAttr(driven+'.primaryVisibility', driven+'.hideOnPlayback', f=True)

def addVisAttr_v2(lNodes):
    lDriven = []
    driver = ''
    lMsh = []
    for node in lNodes:
        lShp = mc.listRelatives(node, ad=True, type='mesh') or []
        if lShp:
            lDriven.append(node)
        else:
            driver = node
    clearDriver = driver
    if not mc.attributeQuery('switch_vis', n=driver, ex=True):
        mc.addAttr(driver, ln='switch_vis', at='enum', en=':Hide:PrimaryOff:Show', k=True, dv=2)
    if ':' in driver:
        clearDriver = driver.split(':')[-1]

    nCnd = 'cnd'+clearDriver[len(driver.split('_')[0]) :]
    cnd = nCnd
    if not mc.objExists(nCnd):
        cnd = mc.createNode('condition', n=nCnd)
        mc.connectAttr(driver+'.switch_vis', cnd+'.firstTerm', f=True)
        mc.setAttr(cnd+'.secondTerm', 1)
        mc.setAttr(cnd+'.operation', 1)

    for driven in lDriven:
        mc.connectAttr(driver+'.switch_vis', driven+'.visibility', f=True)
        if not mc.attributeQuery('primaryVisibility', n=driven, ex=True):
            mc.addAttr(driven, ln='primaryVisibility', at='bool')
        mc.connectAttr(cnd+'.outColorR', driven+'.primaryVisibility', f=True)
        lShp = mc.listRelatives(driven, ad=True, type='mesh', ni=True)

        for shp in lShp:
            if not mc.getAttr(shp+'.intermediateObject') == True:
                lMsh.append(shp)
                mc.connectAttr(driven+'.primaryVisibility', shp+'.template', f=True)
                mc.connectAttr(driven+'.primaryVisibility', shp+'.hideOnPlayback', f=True)
    print 'visAttr added from', driven, 'to', lShp
#addVisAttr_v2(mc.ls(sl=True))


def updateRef_old(lStep):
    scenePath = mc.file(q=True, sceneName=True)
    asset = scenePath.split(r'/')[5]
    basePath = scenePath.split(asset)[0]
    assetType = scenePath.split(r'/')[4]
    dicLoadedRef = {}
    lRef = mc.file(scenePath, q=True, reference=True) or []
    for step in lStep:
        nspace = step
        if step == 'MOD':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            task = 'high'
            dicLoadedRef[step]['task'] = 'high'
            dicLoadedRef[step]['nspace'] = step
        elif step == 'STP':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            task = 'rig'
            dicLoadedRef[step]['task'] = 'rig'
            dicLoadedRef[step]['nspace'] = 'RIG'
            nspace = 'RIG'
        elif step == 'SHD':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            task = 'base'
            dicLoadedRef[step]['task'] = 'high'
            if assetType == 'PRP' or assetType == 'BG':
                task = 'high'
                dicLoadedRef[step]['task'] = 'high'
            dicLoadedRef[step]['nspace'] = step
        elif step == 'UVS':
            if assetType == 'PRP':
                return mc.warning('no step UVS for props')
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            step = 'SHD'
            task = 'uvs'
            nspace = 'UVS'
            dicLoadedRef[step]['task'] = 'art'
            dicLoadedRef[step]['nspace'] = 'UVS'
        elif step == 'FUR':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            task = 'art'
            dicLoadedRef[step]['task'] = 'art'
            dicLoadedRef[step]['nspace'] = step

        stepPath = basePath.replace(r'/STP/', '/'+step+'/')+asset+r'/SMF_'+step+'_'+asset+'_'+task+'_v'
        if lRef:
            for ref in lRef:
                refNode = mc.referenceQuery(ref, rfn=True)
                nSpace = mc.referenceQuery(ref, ns=True)
                if nSpace in dicLoadedRef.keys():
                    stepPath = basePath.replace(r'/STP/', '/'+step+'/')+asset+r'/SMF_'+step+'_'+asset+'_'+task+'_v'

        if step == 'STP':
            stepPath = scenePath.split('_STP_'+asset)[0]+'_STP_'+asset+'_'+task+'_v'

        lFiles = glob.glob(stepPath+'*.ma')

        if lFiles:
            lastRev = max(lFiles, key=os.path.getmtime)
            if os.path.exists(lastRev):
                if lRef:
                    if not lastRev in lRef:
                        for ref in lRef:
                            if ref.startswith(stepPath):
                                if ref != lastRev:
                                    refNode = mc.referenceQuery(ref, rfn=True)
                                    mc.file(lastRev, lr=refNode)
                                    print lastRev, 'uploaded'

                else:
                    mc.file(lastRev, r=True, ns=nspace)
                    print lastRev, 'loaded' ,
            else:
                mc.warning('their is no mdo publish for', asset)
        else:
            mc.warning('step : '+step+' for the asset : '+asset+' does not exist')

#updateRef(['SHD'])


def updateRef(lStep):
    scenePath = mc.file(q=True, sceneName=True)

    asset = scenePath.split(r'/')[5]
    basePath = scenePath.split(asset)[0]
    assetType = scenePath.split(r'/')[4]
    assetStep = scenePath.split(r'/')[3]
    dicLoadedRef = {}
    lRef = mc.file(scenePath, q=True, reference=True) or []
    for step in lStep:
        if step == 'MOD':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = 'high'
            dicLoadedRef[step]['nspace'] = step
            dicLoadedRef[step]['file'] = ''

        elif step == 'STP':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = 'rig'
            dicLoadedRef[step]['nspace'] = 'RIG'
            dicLoadedRef[step]['file'] = ''

        elif step == 'SHD':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = 'base'
            dicLoadedRef[step]['file'] = ''
            if assetType == 'PRP' or assetType == 'BG':
                dicLoadedRef[step]['task'] = 'high'
            dicLoadedRef[step]['nspace'] = step
            dicLoadedRef[step]['file'] = ''

        elif step == 'FUR':
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = 'art'
            dicLoadedRef[step]['nspace'] = step
            dicLoadedRef[step]['file'] = ''

    if lRef:
        for ref in lRef:
            nSpace = mc.referenceQuery(ref, ns=True)
            if nSpace in dicLoadedRef.keys():
                dicLoadedRef[step]['file'] = ref
            elif nSpace == 'RIG':
                dicLoadedRef['STP']['file'] = ref

    print dicLoadedRef
    for step in lStep:
        print step
        task = dicLoadedRef[step]['task']
        nspace = dicLoadedRef[step]['nspace']
        stepPath = ""
        refPath = dicLoadedRef[step]['file']
        if refPath:
            stepPath = refPath.split('.')[0]
        else:
            stepPath = basePath.replace(r'/'+assetStep+r'/', r'/'+step+r'/')+asset+r'/SMF_'+step+'_'+asset+'_'+task+'_v'

        lFiles = glob.glob(stepPath+'*.ma')
        if lFiles:
            lastRev = max(lFiles, key=os.path.getmtime)
            if os.path.exists(lastRev):
                if refPath:
                    if not lastRev == refPath:
                        refNode = mc.referenceQuery(refPath, rfn=True)
                        mc.file(lastRev, lr=refNode)
                        print lastRev, 'uploaded',
                    else:
                        refNode = mc.referenceQuery(refPath, rfn=True)
                        mc.file(lastRev, lr=refNode)
                        print lastRev, 'reloaded',
                else:
                    mc.file(lastRev, r=True, ns=nspace)
                    print lastRev, 'loaded',
            else:
                mc.warning('step : '+step+' for the asset : '+asset+' does not exist')
        else:
            mc.warning('step : '+step+' for the asset : '+asset+' does not exist')

#updateRef(['SHD'])

"""

def updateRef(lStep):
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for path in lRef:
            step = getStepPath(path)
            if step in lStep:
                lFiles = glob.glob(path.split('_v')[0]+'*.ma')
                if not lFiles:
                    mc.warning('their is no mdo publish for')
                lastRev = max(lFiles, key=os.path.getmtime).replace('\\', '/')
                if lastRev != path:
                    if os.path.exists(lastRev):
                        refNode = mc.referenceQuery(path, rfn=True)
                        mc.file(lastRev, lr=refNode)
                elif lastRev == path:
                    mc.warning('no update needed for ref : '+path)
    else:
        for step in lStep:
            loadStep(step)
    print 'references updating finish'
#updateRef(['T:/03_FAB/00_ASSETS/STP/CHR/Smurf/exp/MAYA/SMF_STP_Smurf_exp_vanim_v011_100.ma'])
"""

def refLastMod():
    scPath = mc.file(q=True, sceneName=True)
    asset = scPath.split(r'/')[5]
    basePath = scPath.split(asset)[0]
    modPath = basePath.replace(r'/STP/', r'/MOD/')+asset+r'/SMF_MOD_'+asset+'_high_v'
    lFiles = glob.glob(modPath+'*.ma')
    if not lFiles:
        mc.warning('their is no mdo publish for', asset)
        return

    lastRev = max(lFiles, key=os.path.getmtime)
    if os.path.exists(lastRev):
        mc.file(lastRev, r=True, ns='MOD')
    else:
        mc.warning('their is no mdo publish for', asset)
#refLastMod()


def switchStepRef(oldStep, oldTask, newStep, newTask):
    scPath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scPath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            step = getStepPath(ref)
            if step == oldStep:
                asset = ref.split(r'/')[5]
                scName = ref.split(r'/')[6]
                newScName = scName.replace('_'+oldStep+'_', '_'+newStep+'_').replace('_'+oldTask+'_', '_'+newTask+'_')
                task = scName.split('_')[-3]
                if task == oldTask:
                    basePath = ref.split(asset)[0]
                    newPath = basePath.replace(r'/'+oldStep+r'/', r'/'+newStep+r'/')+asset+r'/'+newScName
                    lFiles = glob.glob(newPath[: len(newPath)-len(newPath.split('_')[-1])]+'*.ma')
                    if not lFiles:
                        mc.warning('their is no mdo publish for', asset)
                        return False
                    lastRev = max(lFiles, key=os.path.getmtime)
                    if os.path.exists(lastRev):
                        refNode = mc.referenceQuery(ref, rfn=True)
                        mc.file(lastRev, lr=refNode)
                        return True
                    else:
                        mc.warning('their is no mdo publish for', asset)
                        return False
    else:
        mc.warning('their is no ref in this scene')
        return False

#switchStepRef('MOD', 'high', 'SHD', 'base')


def initWipVAni():
    scPath = mc.file(q=True, sceneName=True)
    assetType = getTypePath(scPath)
    if not scPath:
        mc.warning('name your current scene by saving it correctly')
        return
    tmpNode = mc.createNode('transform', n='WIP')
    mc.addAttr(tmpNode, ln='deleteMe', at='bool', dv=1)
    refLastMod()
    #chkRigFile = scPath.replace('MOD', 'STP').replace('_High_', '_rig_vanim_')# to do for props with tpl and rig files
    if assetType in ['PRP', 'BG']:
        box = clean.getAllBoxs() or []
        if box:
            box = box[0]
        else:
            box = mc.createNode('transform', n='ALL')
        if not mc.attributeQuery('expertMode', n=box, ex=True):
            mc.addAttr(box, ln='expertMode', at='bool', dv=0)
        geo = 'GEO'
        if ':' in box:
            geo = box.replace(box.split(':')[-1], 'GEO')
        if not mc.objExists(geo):
            #geo = mc.createNode('transform', n='GEO')
            geo = ''
        world = lib_shapes.shp_form('square',"Index","yellow",name='WORLD')
        print 'WORLD generated'
        if world.endswith('Shape'):
            world = mc.rename(world, 'WORLD')
        cWalk  = lib_shapes.shp_form('crossArrow',"Index","brown24",name='c_WALK')
        print 'WALK generated'
        if cWalk.endswith('Shape'):
            cWalk = mc.rename(cWalk, 'c_WALK')
        cFly  = lib_shapes.shp_form('fly',"Index","brown24",name='c_FLY')
        print 'FLY generated'
        if cFly.endswith('Shape'):
            cFly = mc.rename(cFly, 'c_FLY')
        rootWalk = mc.createNode('transform', n='root_WALK')
        rootFly = mc.createNode('transform', n='root_FLY')
        rig = mc.createNode('transform', n='RIG')
        mc.parent(cFly, rootFly)
        mc.parent(rootFly, cWalk)
        mc.parent(cWalk, rootWalk)
        mc.parent(rootWalk, world)
        mc.parent(world, box)
        mc.parent(rig, box)

        if geo:
            bBoxBox = mc.exactWorldBoundingBox(box, calculateExactly=True)
            bBoxWorld = mc.exactWorldBoundingBox(world, calculateExactly=True)
            dif = [bBoxBox[3] - bBoxWorld[3], 0, bBoxBox[5] - bBoxWorld[5]]
            center = mc.objectCenter(geo, gl=True)
            mc.setAttr(world+'.scale', 2+dif[0], 2+dif[1], 2+dif[2])
            mc.makeIdentity(world, a=True)
            mc.setAttr(rootFly+'.t', *center)
            shpFly = mc.listRelatives(cFly, s=True)[0]
            lCvs = mc.ls(shpFly+'.cv[*]', fl=True)
            for cv in lCvs:
                pos = mc.xform(cv, q=True, ws=True, t=True)
                mc.move(pos[0], 0, pos[2]-dif[2], cv, ls=True)
            addVisAttr(cFly, geo)
            print 'shapes ajusted'
        lib_controlGroup.addCtrlToCg([world, cWalk, cFly], 'cg_all')
        print 'cg_all generated'



#initWipVAni()
################################################################################
#EXP########################################################################

def doExpMod():
    scenePath = mc.file(sn=True, q=True)
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nSpace = mc.referenceQuery(ref, ns=True)
            mc.file(ref, ir=True, mnr=True)
    lBoxs = mc.ls(assemblies=True)
    box = ''
    for node in lBoxs:
        if not mc.listRelatives(node, s=True):
            box = node
    asset = scenePath.split('_')[-4]
    newName = asset[0].lower()+asset[1:]
    geo = 'GEO'
    for child in mc.listRelatives(box, c=True):
        mc.parent(child, world=True)
        mc.addAttr(child, ln='dtType', dt='string')
        mc.setAttr(child+'.dtType', child, type='string')
        mc.setAttr(child+'.dtType', l=True)
        if child == geo:
            mc.setAttr(child+'.displayHandle', 1)
            mc.setAttr(geo+'.overrideEnabled', 1)
            mc.setAttr(geo+'.overrideColor', 17)
            geo = mc.rename(child, child.lower()+'_'+newName)
        else:
            driven = mc.rename(child, child.lower()+'_'+newName)
            mc.parentConstraint(geo, driven, mo=True)
            mc.scaleConstraint(geo, driven, mo=True)

    mc.delete(box)
#doExpMod()


def doExpRig():
    scenePath = mc.file(sn=True, q=True)
    """
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nSpace = mc.referenceQuery(ref, ns=True)
            mc.file(ref, ir=True, mnr=True)
    """
    lBoxs = mc.ls(assemblies=True)
    box = ''
    for node in lBoxs:
        if not mc.listRelatives(node, s=True):
            box = node
    asset = scenePath.split('_')[-5]
    newName = asset[0].lower()+asset[1:]
    geo = 'GEO'
    fly = 'c_FLY'
    mc.parent(fly, box)
    lAttrs = mc.listAttr(fly, ud=True)
    for attr in lAttrs:
        if mc.attributeQuery(attr, n=fly, ex=True):
            mc.setAttr(fly+'.'+attr, l=False)
            mc.deleteAttr(fly+'.'+attr)
    mc.delete('WORLD')
    mc.delete(mc.listRelatives(fly, s=True)[0])
    fly = mc.rename(fly, 'ANCHOR')
    lChilds = mc.listRelatives(fly, c=True, type='transform') or []
    if lChilds:
        for child in lChilds:
            mc.rename(child, child+asset)
    for child in mc.listRelatives(box, c=True):
        mc.parent(child, world=True)
        mc.addAttr(child, ln='dtType', dt='string')
        mc.setAttr(child+'.dtType', child, type='string')
        mc.setAttr(child+'.dtType', l=True)
        mc.rename(child, child.lower()+'_'+newName)
    mc.delete(box)
    lToDelete = mc.ls('*.deleteMe', o=True)
    mc.select(cl=True)
    for node in lToDelete:
        if mc.objExists(node):
            if mc.getAttr(node+'.deleteMe'):
                mc.delete(node)
#doExpRig()




################################################################################

#OLD SCRIPT#####################################################################
def saveScene(scenePath, old, new):
    #sauvegarde de la scene PUBLIEE
    newPath = scenePath.replace(old, new)
    mc.file(scenePath, rn=newPath)
    mc.file(save=True)
    return newPath
#saveScene(scenePath, '', '')

def saveStep(pathRig):
    cleanPathRig = pathRig.replace('/', '\\')
    pathRoot = cleanPathRig.split('02_RIG')[0]
    assetType = cleanPathRig.split('02_RIG')[-1][1:]
    sceneRig = cleanPathRig.split('\\')[-1]
    sceneAni = sceneRig.replace('_STP_EXP_', '_ANI_')
    folder = pathRoot+'\\05_ANI\\'+assetType[: len(assetType)-len(sceneRig)-1]
    createFolder(folder)
    mc.file(pathRig, rn=folder+'\\'+sceneAni)
    mc.file(save=True)
#saveStep('T:\\90_TEAM_SHARE\\03_FAB\\00_ASSETS\\02_RIG\\01_CHARS\\Smurf\\SMF_STP_EXP_Smurf_v004_001.ma')


#__MOD__################################################################################################################
def pubMod():
    scenePath = mc.file(q=True, sceneName=True)
    print 'removing ref :'
    clean.remRef(scenePath)
    print 'removing nodes :'
    clean.remTrash()
    print 'saving scene'
    #sauvegarde de la scene PUBLIEE
    newPath = scenePath.replace('_WIP_', '_EXP_')
    mc.file(scenePath, rn=newPath)
    mc.file(save=True)
    print 'publish succesfuly done'


#__RIG__################################################################################################################

def saveTpl():
    scenePath = mc.file(q=True, sceneName=True)
    newPath = updateRev(scenePath)
    mc.file(scenePath, rn=newPath)
    mc.file(save=True)
    print 'template incremented and saved'
    return newPath



def saveRig():
    scenePath = mc.file(q=True, sceneName=True)
    newPath = saveScene(scenePath, '_tpl_', '_rig_')
    print 'RIG saved'
    return newPath

def saveBuild():
    scenePath = mc.file(q=True, sceneName=True)
    newPath = updateRev(scenePath)
    mc.file(scenePath, rn=newPath)
    mc.file(save=True)
    print 'build incremented and saved'
    return newPath


def genExp(nToKeep=[':RIG', ':MOD', ':FUR'], nToDel=['']):

    scenePath = saveBuild()
    lRef = mc.file(scenePath, q=True, reference=True)
    for ref in lRef:
        if mc.referenceQuery(ref, ns=True) in nToKeep:
            mc.file(ref, ir=True)
        else:
            mc.file(ref, rr=True)
    clean.hiFusion()
    if mc.objExists('MOD:ALL'):
        mc.delete('MOD:ALL')
    clean.deleteNspace()
    clean.remove_nodes(['displayLayer'], ['defaultLayer'])
    newPath = saveScene(scenePath, '_BUILD_', '_EXP_')
    print ' exp genered '
    return newPath
#genExp([':RIG', ':MOD', ':FUR'], [''])

def genVanim(nToKeep=[':RIG', ':MOD', ':FUR'], nToDel=['']):
    path = genExp(nToKeep, nToDel)
    clean.lock_shapes_and_smooth()
    clean.set_joint_draw()
    clean.hide_ctrl_hist()
    clean.rootUnkeyable()
    saveStep(path)
    print ' ani generated'
#genVanim([':RIG', ':MOD', ':FUR'], [''])

def genVAnimFull(oldPath, newPath, assetType, step, task, asset, push=False):
    crvGuidesRestPosition()
    mc.file(oldPath, rn=newPath)
    mc.file(save=True)
    print 'vanimFull generated for', asset
    if push == True:
        quickPushInSG(newPath, assetType, step, task, asset)
    print 'vanimFull pushed for', asset

def genVAnimLow():
    removeGroom()
    clean.rootUnkeyable()

def genVlay(assetType, asset, push=False):
    '''
    :param assetType: CHR or PRP or BG
    :return: nothing, just generate a lowLOWcost scene from vanim
    '''
    lMsh = mc.ls(type='mesh')
    rigAdd = 'get rig add for don t loose him'
    if assetType == 'PRP':
        if mc.objExists('RIG'):
            chkChilds = mc.listRelatives('RIG', c=True) or []
            if not chkChilds:
                mc.delete('RIG')
                mc.parentConstraint('c_FLY', 'GEO', mo=True)
                mc.scaleConstraint('c_FLY', 'GEO', mo=True)
    #elif assetType == 'CHR':
        #if mc.objExists('RIG'):
            #mc.delete('RIG')
            #mc.parentConstraint('c_FLY', 'GEO', mo=True)
            #mc.scaleConstraint('c_FLY', 'GEO', mo=True)
    elif assetType == 'BG':
        if mc.objExists('RIG'):
            chkChilds = mc.listRelatives('RIG', c=True) or []
            if not chkChilds:
                mc.delete('RIG')
                mc.parentConstraint('WORLD', 'GEO', mo=True)
                mc.scaleConstraint('WORLD', 'GEO', mo=True)
            if mc.objExists('root_WALK'):
                mc.delete('root_WALK')

    print 'vlay generated for', asset
    path = mc.file(q=True, sceneName=True)
    asset = getAssetPath(path)
    newFile = path.replace('_vanim_', '_vlay_')
    mc.file(path, rn=newFile)
    mc.file(save=True)
    if push == True:
        quickPushInSG(newFile, assetType, 'STP', 'vlay', asset)
    print 'vlay pushed for', asset

def genVMarketing():
    getshd = switchStepRef("MOD", "high", "SHD", "base")
    return getshd

def genRootWip(tplRoot, newRig):
    asset = getAssetPath(newRig)
    assetRoot = getAssetPath(tplRoot)
    task = getTaskScene(tplRoot)
    wip = tplRoot.replace(task, 'wip_vanim_')
    lFiles = glob.glob(wip.split('_wip_vanim_')[0]+'_wip_vanim_*')
    lastRootWip = max(lFiles, key=os.path.getmtime)
    print tplRoot    #T:/03_FAB/00_ASSETS/STP/CHR/Smurf/wip/MAYA/SMF_STP_Smurf_tpl_v009_032.ma
    print newRig     #T:/03_FAB/00_ASSETS/STP/CHR/SmurfyGrooveBlossom/wip/MAYA/SMF_STP_SmurfyGrooveBlossom_rig_v001_003.ma
    print assetRoot  #Smurf
    print asset      #SmurfyGrooveBlossom
    print task       #tpl
    print wip        #T:/03_FAB/00_ASSETS/STP/CHR/Smurf/wip/MAYA/SMF_STP_Smurf_wip_v009_032.ma
    print lastRootWip #T:/03_FAB/00_ASSETS/STP/CHR/Smurf/wip/MAYA\SMF_STP_Smurf_wip_vanim_v020_075.ma
    mc.file(lastRootWip, open=True)

    lRef = mc.file(lastRootWip, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refStep = getStepPath(ref)
            if refStep in ['MOD', 'STP', 'SHP']:
                ext = getTaskScene(ref)
                newRef = ref.replace(assetRoot, asset)
                print newRef
                lFiles = glob.glob(newRef.split('_'+ext+'_')[0]+'_'+ext+'_*')
                if lFiles:
                    print lFiles
                    lastNewRef = max(lFiles, key=os.path.getmtime)
                    refNode = mc.referenceQuery(ref, rfn=True)
                    print lastNewRef, refNode
                    mc.file(lastNewRef, lr=refNode)
                    print ref, 'switched with', lastNewRef
                else:
                    mc.warning('no file found for '+ref)
    getRootWip = ''
    getNewRig = ''
    getNewMod = ''


def publishRig(path, doExp, doLay, doMarket, incNewRev, onlyVanimFull=False, push=False):

    if doMarket == False:
        newRev = path
        if incNewRev == True:
            newRev = updateRev(path)
        print 'new revison saved'
        path = nSaveScene(newRev, getStepPath(newRev), getTaskPath(newRev), getTypePath(newRev))
    elif doMarket == True:
        chkShd = genVMarketing()
        if chkShd == False:
            return
    assetType = getTypePath(path)
    asset = getAssetPath(path)
    task = getTaskScene(path)
    dicRef = {}
    lRef = mc.file(path, q=True, reference=True) or []
    dicRef['importe'] = []
    dicRef['remove'] = []
    lExpNspaces = clean.listExpNspaces() or []
    clean.clearExpertMode()
    if assetType == 'PRP':
        print 'PROP publishing'
        sd = getSousDes(path)
        if sd == 'tpl':
            assetRoot = buildRig.doBuildRig(cleanScene=True, doCg=True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)
            scName = getSceneName(path)
            pubScene = scName.replace('_'+sd+'_', '_rig_')
            newFile = path.replace(scName, pubScene)
            mc.file(path, rn=newFile)
            mc.file(save=True)
            print 'rig :', newFile, 'generated'
            return
        if task == 'vanim' or task == 'vanimFull' or task == 'vlay':
            if lRef:
                for ref in lRef:
                    step = getStepPath(ref)
                    lKeepedStep = ['MOD', 'STP']
                    if doMarket == True:
                        lKeepedStep = ['MOD', 'STP', 'SHD']
                    if step in lKeepedStep:
                        dicRef['importe'].append(ref)
                    else:
                        dicRef['remove'].append(ref)
                clean.refCleaner_v2(dicRef)
                print 'references cleaned'
            clean.removeTmpFather()
            print 'delteMe tmpFathers'
            clean.remTrash()
            print 'delteMe deleted'
            clean.hiFusion('')
            print 'hierachi fusion done'
            clean.remove_nodes()
            print 'reidualsNodes cleaned'

            clean.remove_plugNodes()
            print 'plugins removed'

            clean.deleteAniCrv()
            print 'residuals key deleted'
            lib_controlGroup.parentOrphanCg()
            clean.setObjectSets('RIG')
            clean.cleanCgSets()
            print 'rig sets cleaned'
            clean.nspaceCleanner_props(lExpNspaces)
            print 'namespaces cleaned'
            clean.removeTmpHi()
            clean.hiddeNurbs()
            clean.hiddeCurves()
            clean.hiddeLoc()
            clean.unfreezeVtxNormals()
            clean.rootUnkeyable()
            if doExp == True:
                print 'creating EXP'
                doExpRig()
                newDir = getDirPaf().replace('/wip', '/exp')
                createFolder(newDir)
                scName = getSceneName(path)
                expName = scName.replace('_'+sd+'_', '_exp_')
                newFile = newDir.replace('/', '\\')+'\\'+expName
                mc.file(path, rn=newFile)
                mc.file(save=True)
                return
            newDir = getDirPaf().replace('/wip', '/toCheck')
            if doMarket == True:
                newDir = getDirPaf().replace('/wip', '/vMarket')
            if not '/wip' in getDirPaf() :
                newDir = getDirPaf().replace('/exp', '/toCheck')
            createFolder(newDir)
            scName = getSceneName(path)
            pubScene = scName.replace('_'+sd+'_', '_')
            if doMarket == True:
                pubScene = scName.replace('_'+sd+'_'+task+'_', '_vMarket_')
            newFile = newDir.replace('/', '\\')+'\\'+pubScene
            clean.lock_shapes_and_smooth()
            clean.set_joint_draw()
            clean.hide_ctrl_hist()
            mc.file(path, rn=newFile)
            mc.file(save=True)
            if doLay == True:
                if task != 'vlay':
                    vanimPath = newFile
                    print 'print generating vlay'
                    genVlay(assetType, asset)
                    mc.file(vanimPath, o=True)


    if assetType == 'CHR':
        print 'CHARACTER PUBLISHING'
        sd = getSousDes(path)
        if sd == 'tpl':
            assetRoot = buildRig.doBuildRig(cleanScene=True, doCg=True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)
            lib_controlGroup.parentOrphanCg()
            clean.setObjectSets('RIG')
            clean.cleanCgSets()
            print 'rig sets cleaned'
            scName = getSceneName(path)
            pubScene = scName.replace('_'+sd+'_', '_rig_')
            newFile = path.replace(scName, pubScene)
            mc.file(path, rn=newFile)
            mc.file(save=True)
            if assetRoot:
                genRootWip(assetRoot, newFile)
            return
        elif sd == 'wip' or sd.startswith('wip'):
            step = getStepPath(path)
            #nPubBuild(scenePath, step, sd, type, lib_names.refNspaceRIG())
            if task == 'vanim' or task == 'vanimFull' or task == 'vlay':
                if lRef:
                    for ref in lRef:
                        step = getStepPath(ref)
                        lKeepedStep = ['MOD', 'STP', 'FUR', 'SHD']
                        if doMarket == True:
                            lKeepedStep = ['MOD', 'STP', 'FUR', 'SHD']
                        if step in lKeepedStep:
                            dicRef['importe'].append(ref)

                        if doMarket == False:
                            if step == 'FUR' or step == 'SHD':
                                flagNodes(ref)
                        else:
                            dicRef['remove'].append(ref)
                    clean.refCleaner_v2(dicRef)
                    print 'references cleaned'
            clean.removeTmpFather()
            print 'delteMe tmpFathers'
            clean.remTrash()
            print 'delteMe deleted'
            clean.hiFusion('RIG')
            print 'hierachi fusion done'
            clean.remove_nodes()
            print 'residualsNodes cleaned'
            clean.remove_plugNodes()
            print 'plugins removed'
            clean.deleteAniCrv()
            print 'residuals key deleted'
            if doMarket == False:
                clean.removeShdDags()
                print 'residuals SHD dag cleanned'
            lib_controlGroup.parentOrphanCg()
            clean.setObjectSets('RIG')
            clean.cleanCgSets()
            print 'rig sets cleaned'
            clean.nspaceCleanner_props(lExpNspaces)
            print 'namespaces cleaned'
            clean.hiddeNurbs()
            print 'nurbsPlanes hidded'
            clean.hiddeCurves()
            print 'nurbsCurves hidded'
            clean.hiddeLoc()
            print 'locators hidded'
            clean.unfreezeVtxNormals()
            print 'vtxNormals cleaned'
            scName = getSceneName(path)

            newDir = getDirPaf().replace('/wip', '/exp')
            expName = scName.replace('_'+sd+'_', '_exp_')

            if doMarket == True:
                newDir = getDirPaf().replace('/wip', '/vMarket')
                expName = scName.replace('_'+sd+'_'+task+'_', '_vMarket_')

            createFolder(newDir)
            newFile = newDir.replace('/', '\\')+'\\'+expName
            mc.file(path, rn=newFile)
            mc.file(save=True)
            if doMarket == True:
                return
            #if doExp == True:
                #return
            newDir = getDirPaf().replace('/exp', '/toCheck')
            pubScene = scName.replace('_'+sd+'_'+task, '_vanimFull')
            createFolder(newDir)

            newFile = newDir.replace('/', '\\')+'\\'+pubScene
            clean.lock_shapes_and_smooth()
            clean.set_joint_draw()
            clean.hide_ctrl_hist()
            if task in ['vanim', 'vanimFull']:
                genVAnimFull(path, newFile, assetType, 'STP', 'vanimFull', asset)
            if onlyVanimFull == True:
                return
            genVAnimLow()
            newFile = newFile.replace('_vanimFull_', '_vanim_')
            mc.file(path, rn=newFile)
            mc.file(save=True)
            if doLay == True:
                if task != 'vlay':
                    vanimPath = newFile
                    print 'print generating vlay'
                    genVlay(assetType, asset)
                    mc.file(vanimPath, o=True)

        elif sd == 'sep':
            print 'to do, zizilol'
        elif sd == 'root':
            step = getStepPath(path)
            if task == 'wip':
                if lRef:
                    for ref in lRef:
                        step = getStepPath(ref)
                        if step in ['MOD', 'STP', 'FUR']:
                            dicRef['importe'].append(ref)
                        else:
                            dicRef['remove'].append(ref)
                        if step == 'FUR' or step == 'SHD':
                                flagNodes(ref)
                    clean.refCleaner_v2(dicRef)
                    print 'references cleaned'
            #mc.delete('MOD:geo_eyes')
            #print 'eyes removed'
            clean.removeTmpFather()
            print 'delteMe tmpFathers'
            clean.hiFusion('RIG')
            print 'hierachi fusion done'
            clean.remTrash()
            print 'delteMe deleted'
            clean.remove_nodes()
            print 'residualsNodes cleaned'
            clean.remove_plugNodes()
            print 'plugins removed'

            clean.deleteAniCrv()
            print 'residuals key deleted'
            lib_controlGroup.parentOrphanCg()
            clean.setObjectSets('RIG')
            clean.cleanCgSets()
            print 'rig sets cleaned'
            clean.nspaceCleanner_props(lExpNspaces)
            print 'namespaces cleaned'
            clean.unfreezeVtxNormals()
            print 'vtxNormals cleaned'
            expName = path.replace('_'+task+'_', '_rig_')
            mc.file(path, rn=expName)
            mc.file(save=True)
            return

    if assetType == 'BG':
        sd = getSousDes(path)
        if task == 'vanim' or task == 'vlay':
            if lRef:
                for ref in lRef:
                    step = getStepPath(ref)
                    if step == 'MOD' or step == 'STP':
                        dicRef['importe'].append(ref)
                    else:
                        dicRef['remove'].append(ref)
                clean.refCleaner_v2(dicRef)
                print 'references cleaned'
            clean.hiFusion('')
            print 'hierachi fusion done'
            clean.removeTmpFather()
            print 'delteMe tmpFathers'
            clean.remTrash()
            print 'delteMe deleted'


            clean.remove_nodes(['displayLayer', 'nodeGraphEditorInfo'], ['defaultLayer'])
            print 'reidualsNodes cleaned'
            clean.deleteAniCrv()
            print 'residuals key deleted'
            lib_controlGroup.parentOrphanCg()
            clean.setObjectSets('RIG')
            clean.cleanCgSets()
            print 'rig sets cleaned'
            clean.nspaceCleanner_props(lExpNspaces)
            print 'namespaces cleaned'
            #newDir = path.split(r'/wip')[0]
            #newDir = getDirPaf()+'/toCheck'
            newDir = getDirPaf().replace('/wip', '/toCheck')
            createFolder(newDir)
            scName = getSceneName(path)
            #pubScene = scName.replace('_'+sd+'_vanim', '_vanimFull')
            pubScene = scName.replace('_'+sd+'_', '_')
            newFile = newDir.replace('/', '\\')+'\\'+pubScene
            clean.lock_shapes_and_smooth()
            clean.set_joint_draw()
            clean.hide_ctrl_hist()
            clean.rootUnkeyable()
            mc.file(path, rn=newFile)
            mc.file(save=True)
            if doLay == True:
                if task != 'vlay':
                    vanimPath = newFile
                    print 'print generating vlay'
                    genVlay(assetType, asset)
                    mc.file(vanimPath, o=True)
    if push == True:
        pushInSG()

"""
print 'removing ref'
    clean.refCleaner(mc.file(q=True, sceneName=True), dicNspaces)
    clean.hiFusion('RIG')
    print 'removing nodes'
    clean.remTrash()
    clean.remove_nodes(['displayLayer', 'nodeGraphEditorInfo'], ['defaultLayer'])
    clean.deleteAniCrv()
    print 'removing namespaces'
    clean.nspaceCleanner(dicNspaces)
"""


#SWITCH REF TO LOC
def getDicRef():
    dicRef = {}
    scenePath = mc.file(sn=True, q=True)
    lRef = [x for x in mc.file(scenePath, q=True, reference=True) if "exp" in x.split("/")] or []
    for ref in lRef:
        assetStep = ref.split('/')[3]
        assetType = ref.split('/')[4]
        assetName = ref.split('/')[5]
        nSpace = mc.referenceQuery(ref, ns=True)
        geo = nSpace+':geo_'+assetName[0].lower()+assetName[1:]
        if not mc.objExists(geo):
            geo = nSpace+':geo_'+assetName
        father = mc.listRelatives(geo, p=True)[0]
        if not assetType in dicRef.keys():
            dicRef[assetType] = {}
        if not assetStep in dicRef[assetType].keys():
            dicRef[assetType][assetStep] = {}
        if not ref in dicRef[assetType][assetStep].keys():
            dicRef[assetType][assetStep][ref] = {}
        if assetType == 'PRP':
            dicRef[assetType][assetStep][ref]['assetName'] = assetName
            dicRef[assetType][assetStep][ref]['geo'] = geo
            dicRef[assetType][assetStep][ref]['nspace'] = nSpace
            dicRef[assetType][assetStep][ref]['father'] = father
            if assetType == 'STP':
                print 'STP'
    return dicRef
#getDicRef()

def genDataShd(nspace, loc):
    lSg = []
    if nspace:
        lSg = mc.ls(nspace+'*', type='shadingEngine', r=True)
    else:
        lTmpSg = mc.ls(type='shadingEngine', r=True)
        for sg in lTmpSg:
            if not mc.referenceQuery(sg, inr=True):
                lSg.append(sg)
    dicShd = {}
    for sg in lSg:
        lHist = mc.listHistory(sg)
        lShp = mc.ls(lHist, type='shape') or []
        if lShp:
            shd = mc.ls(lHist, type='RedshiftMaterial') or []
            if not shd:
                shd = mc.ls(lHist, type='blinn') or []
            if not shd:
                shd = mc.ls(lHist, type='lambert') or []
            if shd:
                if not shd[0] in dicShd.keys():
                    dicShd[shd[0]] = {}
                dicShd[shd[0]]['msh'] = []
                dicShd[shd[0]]['txt'] = []
                dicShd[shd[0]]['keeper'] = []
                for shp in lShp:
                        msh = mc.listRelatives(shp, p=True)[0]
                        dicShd[shd[0]]['msh'].append(msh)
                if not mc.referenceQuery(shd, inr=True):
                    lKeepers = ''
                    lRefMsh = mc.ls(lShp, rn=True)
                    lKeepers = list(set(lShp)-set(lRefMsh)) or []
                    if not lKeepers:
                        keeper = mc.polyPlane(n='mtlK_'+shd[0], h=1, w=1, sh=1, sw=1)[0]
                        mc.addAttr(keeper, ln='skipMe', at='bool', dv=True)
                        mc.delete(keeper, ch=True)
                        dicShd[shd[0]]['keeper'].append(keeper)
                        mc.sets(mc.listRelatives(keeper, s=True, ni=True)[0], fe=sg)
                        mc.parent(keeper, 'REFDATA')
                    else:
                        dicShd[shd[0]]['keeper'] = lKeepers
                lHist = mc.listHistory(shd) or []
                if lHist:
                    lTxt = mc.ls(lHist, type='file') or []
                    if lTxt:
                        for txt in lTxt:
                            dicShd[shd[0]]['txt'].append(mc.getAttr(txt+'.fileTextureName'))
    for shd in dicShd.keys():
        nDataNode = shd.replace(':', '__')+'Data'
        dataNode = nDataNode
        if not mc.objExists(nDataNode):
            dataNode = mc.createNode('network', n=nDataNode)
        for attr in ['shd', 'sg']:
            if not mc.attributeQuery(attr, n=dataNode, ex=True):
                mc.addAttr(dataNode, ln=attr, dt='string')
        mc.setAttr(dataNode+'.shd', shd, type='string')
        mc.setAttr(dataNode+'.sg', sg, type='string')
        if loc:
            mc.connectAttr(dataNode+'.message', loc+'.assetShd['+str(mc.getAttr(loc+'.assetShd', s=True))+']')
            mc.parent(keeper, loc)
        for attr in dicShd[shd].keys():
            if not mc.attributeQuery(attr, n=dataNode, ex=True):
                mc.addAttr(dataNode, ln=attr, dt='string', multi=True)
            for i in range(0, len(dicShd[shd][attr])):
                mc.setAttr(dataNode+'.'+attr+'['+str(i)+']', dicShd[shd][attr][i], type='string')


#genDataShd('', '')

def getStateSwitchData(locSwitch):
    dicAttr = {}
    lAttr = mc.listAttr(locSwitch, ud=True, k=True)
    for attr in lAttr:
        if not mc.listConnections(locSwitch+'.'+attr, s=True, d=False):
            if not attr in dicAttr:
                dicAttr[attr] = {}
            type = mc.attributeQuery(attr, n=locSwitch, at=True)
            val = mc.getAttr(locSwitch+'.'+attr)
            asMin = mc.attributeQuery(attr, n=locSwitch, mne=True)
            if asMin:
                dicAttr[attr]['min'] = mc.attributeQuery(attr, n=locSwitch, min=True)[0]
            asMax = mc.attributeQuery(attr, n=locSwitch, mxe=True)
            if asMax:
                dicAttr[attr]['max'] = mc.attributeQuery(attr, n=locSwitch, max=True)[0]

            if type == 'enum':
                alias = mc.attributeQuery(attr, n=locSwitch, le=True)
                dicAttr[attr]['alias'] = alias
            dicAttr[attr]['type'] = type
            dicAttr[attr]['value'] = val

    return dicAttr
#genStateSwitchData('PageA_1')


def connStatesSwitch():
    lLocSwitchs = mc.ls('*.stateSwitch', r=True, o=True) or []
    if lLocSwitchs:
        for locSwitch in lLocSwitchs:
            print 'working on :', locSwitch
            dicAttr = getStateSwitchData(locSwitch)
            if dicAttr:
                rigAdd = 'c_rigAdd'
                if not mc.objExists(rigAdd):
                    rigAdd = 'RIG:c_rigAdd'
                if not mc.objExists(rigAdd):
                    rigAdd = lib_rigs.crtRigAdd()
                    print 'rigAdd created'
                for attr in dicAttr.keys():
                    print 'checking for :', attr
                    if not mc.attributeQuery(attr, n=rigAdd, ex=True):
                        print 'trying to connect :', attr
                        if dicAttr[attr]['type'] == 'enum':
                            mc.addAttr(rigAdd, ln=attr, at=dicAttr[attr]['type'], k=True, en=dicAttr[attr]['alias'][0])
                        elif dicAttr[attr]['type'] == 'double':
                            mc.addAttr(rigAdd, ln=attr, at=dicAttr[attr]['type'], k=True, dv=dicAttr[attr]['value'])
                            if 'min' in dicAttr[attr].keys():
                                mc.addAttr(rigAdd+'.'+attr, e=True, min=dicAttr[attr]['min'])
                            if 'max' in dicAttr[attr].keys():
                                mc.addAttr(rigAdd+'.'+attr, e=True, max=dicAttr[attr]['max'])
                        elif dicAttr[attr]['type'] == 'float':
                            mc.addAttr(rigAdd, ln=attr, at=dicAttr[attr]['type'], k=True, dv=dicAttr[attr]['value'])
                            if 'min' in dicAttr[attr].keys():
                                mc.addAttr(rigAdd+'.'+attr, e=True, min=dicAttr[attr]['min'])
                            if 'max' in dicAttr[attr].keys():
                                mc.addAttr(rigAdd+'.'+attr, e=True, max=dicAttr[attr]['max'])
                        elif dicAttr[attr]['type'] == 'bool':
                            mc.addAttr(rigAdd, ln=attr, at=dicAttr[attr]['type'], k=True, dv=dicAttr[attr]['value'])
                        mc.connectAttr(rigAdd+'.'+attr, locSwitch+'.'+attr, f=True)
                        print attr, 'succesful connected'





def getDeleteMehData(nspace, locData):
    lDeleteMe = mc.ls(nspace+'*.deleteMe', o=True)
    if not mc.attributeQuery('toDelete', n=locData, ex=True):
        mc.addAttr(locData, ln='toDelete', dt='string', multi=True)
    for node in lDeleteMe:
        if mc.getAttr(node+'.deleteMe') == True:
            id = mc.getAttr(locData+'.toDelete', s=True)
            mc.setAttr(locData+'.toDelete['+str(id)+']', node, type='string')



#getDeleteMehData('REF_SCALE:', 'null1')



def doModExpDataLoc():
    dicRef = getDicRef()
    if dicRef:
        scenePath = mc.file(sn=True, q=True)
        lBoxs = mc.ls(assemblies=True)
        box = ''
        for node in lBoxs:
            if not mc.listRelatives(node, s=True):
                box = node

        dtNode = 'REFDATA'
        if not mc.objExists('REFDATA'):
            dtNode = mc.createNode('transform', n='REFDATA')
            loc_grp = 'ALL'

            if not mc.objExists(loc_grp):
                loc_grp = mc.createNode('transform', n='LOC')
                mc.parent(loc_grp, 'ALL')
            mc.parent(dtNode, loc_grp)
        if 'PRP' in dicRef.keys():
            for step in dicRef['PRP'].keys():
                for ref in dicRef['PRP'][step].keys():
                    assetName = dicRef['PRP'][step][ref]['assetName']
                    nspace = dicRef['PRP'][step][ref]['nspace']
                    father = dicRef['PRP'][step][ref]['father']
                    geo = dicRef['PRP'][step][ref]['geo']

                    nLoc = 'rd_'+nspace[1].lower()+nspace[2:]

                    loc = nLoc
                    if not mc.objExists(nLoc):
                        loc = mc.spaceLocator(n=nLoc)[0]
                        mc.parent(loc, dtNode)
                    else:
                        for attr in ['path', 'nSpace', 'father', 'assetName', 't', 'r', 's']:
                            mc.setAttr(loc+'.'+attr, l=False)

                    mc.setAttr(loc+'.overrideEnabled', 1)
                    mc.setAttr(loc+'.overrideColor', 20)

                    for attr in ['path', 'nSpace', 'father', 'assetName']:
                        if not mc.attributeQuery(attr, n=loc, ex=True):
                            mc.addAttr(loc, ln=attr, dt='string')

                    for attr in ['assetShd', 'assetCtrl']:
                        if not mc.attributeQuery(attr, n=loc, ex=True):
                            mc.addAttr(loc, ln=attr, at='message', multi=True)


                    mc.setAttr(loc+'.path', ref, type='string')
                    mc.setAttr(loc+'.nSpace', nspace[1:], type='string')
                    mc.setAttr(loc+'.father', father, type='string')
                    mc.setAttr(loc+'.assetName', assetName, type='string')

                    locSwitch = mc.ls(nspace+':*.stateSwitch', o=True) or []
                    if locSwitch:
                        dicSwitch = getStateSwitchData(locSwitch[0])
                        for attr in dicSwitch.keys():
                            type = dicSwitch[attr]['type']
                            val = dicSwitch[attr]['value']
                            if type == 'enum':
                                lAlias = ''
                                for i in dicSwitch[attr]['alias']:
                                    lAlias += ':'+i
                                mc.addAttr(loc, ln= attr, at=type,en=lAlias, dv=val)

                    for attr in ['path', 'nSpace', 'father', 'assetName']:
                        mc.setAttr(loc+'.'+attr, l=True)

                    mc.delete(mc.parentConstraint(geo, loc, mo=False))
                    mc.delete(mc.scaleConstraint(geo, loc, mo=False))
                    for attr in ('t', 'r', 's'):
                        mc.setAttr(loc+'.'+attr, l=True)
                    genDataShd(nspace+':', loc)

                    getDeleteMehData(nspace+':', loc)

            genDataShd('','')



        lRef = mc.file(scenePath, q=True, reference=True) or []
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
            mc.file(ur=refNode)
            if lEdits:
                for edit in lEdits:
                    action = edit.split('|')[0]
                    mc.file(cr=refNode, editCommand=action)
            mc.file(ref, rr=True)


#doModExpDataLoc()


def getLatestFile(ext):
    dir = 'T:/03_FAB/00_ASSETS/STP/PRP/ScrewdriverA'
    if not os.path.exists(dir):
        mc.warning(dir, 'exp does not exist')
    else:
        list_of_files = glob.glob(dir+'/SMF_STP_ScrewdriverA_vanim_v*')
        latest_file = max(list_of_files, key=os.path.getmtime)
        print latest_file
        lFiles = os.listdir(dir) or []
        if lFiles:
            lScenes = []
            for i in lFiles:
                if i.endswith(ext):
                    lScenes.append(i)
        print lScenes
        #print max(lScenes, key=os.path.getmtime)
#getLatestFile('.ma')


def convertRefPath(path, step, task):

    nScene = path.split(r'/')[-1]
    nPathStep = path.split(r'/')[3]
    nPathType = path.split(r'/')[4]
    nPathAsset = path.split(r'/')[5]
    nPathTask = path.split(r'/')[6]

    scStep = nScene.split('_')[1]
    scAsset = nScene.split('_')[2]
    scTask = nScene.split('_')[-3]

    rootDir = path.replace(nScene, '')

    newScene = nScene.replace('_'+scStep+'_', '_'+step+'_')
    newDir = rootDir.replace(r'/'+nPathStep+r'/', r'/'+step+r'/')

    newScene = nScene.replace('_'+scStep+'_', '_'+step+'_').replace('_'+scTask+'_', '_'+task+'_')

    return newDir+newScene
#getRefPath('T:/03_FAB/00_ASSETS/MOD/PRP/HorseToyA/exp/MAYA/SMF_MOD_HorseToyA_exp_high_v001_005.ma', 'STP', 'vanim')

def reassingShd():
    lShdData = []
    lNodes = mc.ls('*.keeper', o=True, r=True)
    for node in lNodes:
        if mc.attributeQuery('shd', n=node, ex=True):
            if mc.attributeQuery('sg', n=node, ex=True):
                lShdData.append(node)
    for node in lShdData:

        shd = mc.getAttr(node+'.shd')
        sg = mc.getAttr(node+'.sg')
        print node, shd
        for id in range(0, mc.getAttr(node+'.msh', s=True)):
            msh = mc.getAttr(node+'.msh['+str(id)+']')
            print msh
            mc.sets(msh, e=True, fe='MOD:'+sg)
        print

#reassingShd()

def rebuildRefInStp(step):
    lLoc = mc.ls(sl=True)
    boxDatas = mc.listRelatives(lLoc[0], p=True)[0]
    if not mc.attributeQuery('deleteMe', n=boxDatas, ex=True):
        mc.addAttr(boxDatas, ln='deleteMe', at='bool', dv=True)
    for loc in lLoc:
        nspace = mc.getAttr(loc+'.nSpace')
        refPath = mc.getAttr(loc+'.path')
        lastRev = refPath
        refStep = refPath.split('/')[3]
        refTask = refPath.split('_')[-3]
        toRef = refPath.replace('/'+refStep+'/', '/'+step+'/')
        dir = toRef.replace(toRef.split('/')[-1], '')
        if not os.path.exists(dir):
            mc.warning(dir, 'exp does not exist')
        else:
            ext = ''
            if step == 'MOD':
                ext = 'high'
            elif step == 'STP':
                ext = 'vanim'
            elif step == 'SHD':
                ext = 'shd'
            elif step == 'SHD':
                ext = 'shd'

            toRef = convertRefPath(refPath, step, ext)
            lFiles = glob.glob(toRef.split('_'+ext+'_')[0]+'_'+ext+'_*')
            lastRev = max(lFiles, key=os.path.getmtime)
            print 'finding :', lastRev
        mc.file(lastRev, r=True, ns=nspace)
        lNodes = mc.ls(nspace+':*.dtType', o=True)
        anchor = ''
        geo = ''
        rig = ''
        for node in lNodes:
            chk = mc.getAttr(node+'.dtType')
            if chk == 'ANCHOR':
                anchor = node
            elif chk == 'GEO':
                geo = node
            elif chk == 'RIG':
                rig = node


        if mc.objExists(rig):
            if not mc.objExists('RIG'):
                mc.createNode('transform', n='RIG')
                mc.parent('RIG', 'MOD:ALL')
            mc.parent(rig, 'RIG')

        if mc.objExists(anchor):
            buf = mc.createNode('transform', n='buffer')
            mc.parent(anchor, buf)
            mc.delete(mc.parentConstraint(loc, buf, mo=False))
            mc.delete(mc.scaleConstraint(loc, buf, mo=False))
            mc.parent(anchor, world=True)
            mc.delete(buf)

        if mc.objExists(geo):
            geoFather = mc.getAttr(loc+'.father')
            father = geoFather
            if mc.referenceQuery('MOD:'+geoFather, inr=True):
                nTmpFather = 'MOD:'+geoFather+'TMP'
                father = nTmpFather
                if not mc.objExists(nTmpFather):
                    father = mc.createNode('transform', n=nTmpFather)
                    mc.addAttr(father, ln='tmpHi', at='bool', dv=1)
                    mc.addAttr(father, ln='hiFather', dt='string')
                    mc.setAttr(father+'.hiFather', geoFather, type='string')
                    mc.parent(father, 'MOD:'+geoFather)
                mc.parent(geo, father)
    reassingShd()


#rebuildRefInStp('MOD')
#rebuildRefInStp('STP')
#rebuildRefInStp('SHD')