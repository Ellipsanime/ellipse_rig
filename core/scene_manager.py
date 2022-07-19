import maya.cmds as mc
import os, sys, glob, json
from importlib import import_module
import references, clean_rig, clean_mod
reload(references)
reload(clean_rig)
reload(clean_mod)
import imp

from ellipse_rig.library import lib_controlGroup, lib_shapes
reload(lib_controlGroup)
reload(lib_shapes)
from ellipse_rig.prod_pressets import global_presets
reload(global_presets)
import references
reload(references)


def getDataNodes():
    print('toDo')
    return

def crtDatasNode():
    dataNode = getDataNodes()
    if not chkDatasNodes:
        dataNode = mc.createNode('netWork', n=nDatasNode)



def getProject():
    pathDir = os.path.dirname(__file__)
    pathJson = os.path.join(pathDir, 'projectName.json')
    jsonFile = glob.glob(pathJson)
    if jsonFile:
        jsonDatas = {}
        with open(jsonFile[0], "r") as file:
             jsonDatas = json.load(file)
        return jsonDatas['projectName']



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
#########INIT######################################################
def setDirPath(nProjectDir, *args):
    dirPath = mc.fileDialog2(dir=newDirPath, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.textField(nProjectDir, e=True, fileName=dirPath)
    return dirPath


def initWipVAni(prod=''):
    fDatas = global_presets.fileDatas()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        fDatas = module.fileDatas()
        print fDatas.test

    scPath = fDatas.filePath

    assetType = fDatas.getScnType()

    if not scPath:
        mc.warning('name your current scene by saving it correctly')
        return
    if not mc.objExists('WIP'):
        tmpNode = mc.createNode('transform', n='WIP')
        mc.addAttr(tmpNode, ln='deleteMe', at='bool', dv=1)
    #print fDatas.dirSteps[fDatas.mod]
    references.updateRef([fDatas.dirSteps[fDatas.mod]], prod=prod)
    #chkRigFile = scPath.replace('MOD', 'STP').replace('_High_', '_rig_vanim_')# to do for props with tpl and rig files
    if assetType in ['prp', 'toto']:
        box = clean_rig.getAllBoxs() or []
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


def initSceneUI():
    nWin = 'init_project'
    nPan = 'INIT_masterPan'
    nProjectDir = 'toto'
    version = '0.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_initRig_UI = mc.window(nWin, t=nWin + version, tlb=True)
    masterPan = mc.paneLayout(cn='single')


    mc.columnLayout(adj=True)
    mc.rowLayout(nc=3, adj=2)
    mc.text('set project directory :', al='left', font='boldLabelFont', h=12)
    mc.textField(nProjectDir, fileName='set assets path', h=20)
    mc.button(l='. . .', c=partial(setDirPath, nProjectDir))
    mc.setParent('..')

    mc.showWindow(win_initRig_UI)
###################################################################

def saveNewRev(prod='', *args):
    clean_rig.killVaccs(['breed_gene', 'vaccine_gene'], ['vaccine.py', 'userSetup.py'])
    fDatas = global_presets.fileDatas()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        fDatas = module.fileDatas()
    print fDatas.test, 'in saved proc'
    newScnName = fDatas.updateFileInc()
    newScnPath = fDatas.filePath.replace(fDatas.fileName, newScnName)
    fDatas.saveScene(fDatas.filePath, newScnPath)
    fDatas.filePath = newScnPath
    fDatas.fileName = fDatas.getFileName()
    fDatas.filePath = newScnPath
    print newScnPath, 'generated'
    return newScnPath




def buildTpl(fDatas):
    from ellipse_rig import buildRig
    reload(buildRig)
    assetRoot = buildRig.doBuildRig(cleanScene=True, doCg=True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)
    lib_controlGroup.parentOrphanCg()
    clean_rig.setObjectSets('RIG')
    clean_rig.cleanCgSets()
    print 'rig sets cleaned'
    #rigPath = fDatas.switchScnTask(fDatas.tpl, fDatas.rig)
    #fDatas.saveScene(fDatas.filePath, rigPath)
    fDatas.genRig()
    if assetRoot:
        genRootWip(assetRoot, fDatas.filePath)


def buildLay():
    prod = getProject()
    from ellipse_rig import buildRigLay
    reload(buildRigLay)
    fDatas = global_presets.fileDatas()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        fDatas = module.fileDatas()
    buildRigLay.doBuildRigLay(fDatas)


def pubScene(prod='', doExp=True, doLay=False, doChk=True, doAni=True, doRnd=False):
    fDatas = global_presets.fileDatas()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        fDatas = module.fileDatas()

    if doLay == False:
        doExp = fDatas.doExp
        doChk = fDatas.doChk
        doAni = fDatas.doAni
        doRnd = fDatas.doRnd
    fDatas.filePath = saveNewRev(prod=prod)
    fDatas.fileName = fDatas.getFileName()
    task = fDatas.getScnTask()
    step = fDatas.getDirStep()
    refDatas = fDatas.getRefDatas()
    if step == fDatas.stepMod:
        clean_rig.remTrash()
        print 'delteMe deleted'
        clean_mod.freezeTrs([])
        clean_rig.remove_nodes()
        print 'reidualsNodes cleaned'
        clean_rig.remove_plugNodes(fDatas.plugins)
        print 'plugins removed'
        clean_rig.deleteAniCrv()
        print 'residuals key deleted'
        references.manageRefs(refDatas['steps'], ['EYES'])
        clean_rig.nspaceCleanner_props(fDatas, [])
        fDatas.genMod()

    elif step == fDatas.stepStp:
        ###################################
        if task == fDatas.tpl:
            buildTpl(fDatas)
            return
        ###################################
        elif task == fDatas.lay:
            doLay=True
            doChk=False
            doAni=False
            doRnd=False
        nspaceToKepp = references.manageRefs(refDatas['steps'], fDatas.refToKeep)
        clean_rig.clearExpertMode()
        clean_rig.removeTmpFather()
        print 'delteMe tmpFathers'
        clean_rig.remTrash()
        print 'delteMe deleted'
        clean_rig.hiFusion(fDatas.nSpaces[fDatas.stp])
        print 'hierachi fusion done'
        clean_rig.remove_nodes()
        print 'reidualsNodes cleaned'
        clean_rig.remove_plugNodes(fDatas.plugins)
        print 'plugins removed'
        clean_rig.deleteAniCrv()
        print 'residuals key deleted'
        lib_controlGroup.parentOrphanCg()
        clean_rig.setObjectSets(fDatas.nSpaces[fDatas.stp])
        clean_rig.cleanCgSets()
        print 'rig sets cleaned'
        clean_rig.nspaceCleanner_props(fDatas, nspaceToKepp)
        print 'namespaces cleaned'
        clean_rig.removeTmpHi()
        print 'tmpHi removed'
        clean_rig.hiddeNurbs()
        print 'nurbs hidded'
        clean_rig.hiddeCurves()
        print 'curves hidded'
        clean_rig.hiddeLoc()
        print 'loc hidded'
        clean_rig.hiddeIkHdl()
        print 'ik handles hidded'
        clean_rig.unfreezeVtxNormals()
        print 'vtx normals unfreezed'
        clean_rig.rootUnkeyable()
        ###########################to do for props
        if doLay == False:
            fDatas.genExp()
        ################################

        clean_rig.lock_shapes_and_smooth()
        clean_rig.set_joint_draw()
        clean_rig.hide_ctrl_hist()
        if doRnd == True:
            fDatas.genVRnd()
        if doChk == True:
            clean_rig.removeStep(fDatas.vAniStepToDel)
            fDatas.genVChk()
        if doAni == True:
            if doChk == False:
                clean_rig.removeStep(fDatas.vAniStepToDel)
            fDatas.genVAni()
        if doLay == True:
            fDatas.genVLay()

#initWipVAni()