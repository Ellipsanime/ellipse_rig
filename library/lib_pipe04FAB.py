
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

#FOLDERS PATH UTILS################################################


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



################################################################################
#PUBLISH UTILS##################################################################
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
################################################################################
#INIT STP WIP###################################################################


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





#__RIG__################################################################################################################

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


def genVAnimLow():
    removeGroom()
    clean.rootUnkeyable()

def genVlay(assetType, asset, push=True):
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



def publishRig(path, doExp, doLay, doMarket, incNewRev, onlyVanimFull=False, push=True):
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

