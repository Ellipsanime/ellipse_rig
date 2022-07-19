import maya.cmds as mc
import glob, os
from importlib import import_module
from ellipse_rig.prod_pressets import global_presets
reload(global_presets)





def cleanRefEdits(refNode):
    lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
    mc.file(ur=refNode)
    if lEdits:
        print 'EDITS FOUND FOR :', refNode
        for edit in lEdits:
            action = edit.split('|')[0]
            mc.file(cr=refNode, editCommand=action)


def removeRef(ref):
    refNode = mc.referenceQuery(ref, rfn=True)
    if mc.attributeQuery('keepMe', n=refNode, ex=True):
        if mc.getAttr(refNode+ '.keepMe') == True:
            nSpace = mc.referenceQuery(ref, ns=True)
            mc.file(ref, ir=True, mnr=False)
            return nSpace.split(':')[-1]
    else:
        nSpace = mc.referenceQuery(ref, ns=True)
        print 'nspaces are :', nSpace
        cleanRefEdits(refNode)
        mc.file(ref, rr=True)
        if mc.namespace(ex=':'+nSpace):
            lResiduals = mc.ls(nSpace+':*', r=True) or []
            print 'residuals :', lResiduals
            if lResiduals:
                mc.delete(lResiduals)
            mc.namespace(rm=nSpace)


def updateRef(lStep, prod=''):
    fDatas = global_presets.fileDatas()
    if prod:
        print prod, 'updateRef proc'
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        fDatas = module.fileDatas()
    scenePath = fDatas.filePath

    asset = fDatas.getDirAsset()
    basePath = fDatas.getDir()
    assetType = fDatas.getDirType()
    assetStep = fDatas.getDirStep()
    print basePath, asset
    dicLoadedRef = {}
    lRef = mc.file(scenePath, q=True, reference=True) or []
    for step in lStep:
        if step == fDatas.dirSteps[fDatas.mod] :
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = fDatas.tasks[fDatas.mod]
            dicLoadedRef[step]['nspace'] = fDatas.nSpaces[fDatas.mod]
            dicLoadedRef[step]['file'] = ''

        elif step == fDatas.dirSteps[fDatas.stp] :
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = fDatas.rig
            dicLoadedRef[step]['nspace'] = fDatas.nSpaces[fDatas.stp]
            dicLoadedRef[step]['file'] = ''

        elif step == fDatas.dirSteps[fDatas.shd] :
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = fDatas.tasks[fDatas.shd]
            dicLoadedRef[step]['file'] = ''
            if assetType == 'PRP' or assetType == 'BG':
                dicLoadedRef[step]['task'] = 'high'
            dicLoadedRef[step]['nspace'] = fDatas.nSpaces[fDatas.shd]
            dicLoadedRef[step]['file'] = ''

        elif step == fDatas.dirSteps[fDatas.fur] :
            if not step in dicLoadedRef.keys():
                dicLoadedRef[step] = {}
            dicLoadedRef[step]['task'] = 'art'
            dicLoadedRef[step]['nspace'] = step
            dicLoadedRef[step]['file'] = ''

    if lRef:
        for ref in lRef:
            nSpace = mc.referenceQuery(ref, ns=True)
            refStep = fDatas.getRefDirStep(ref)
            if refStep in dicLoadedRef.keys():
                dicLoadedRef[step]['file'] = ref

    for step in lStep:
        task = dicLoadedRef[step]['task']
        nspace = dicLoadedRef[step]['nspace']
        stepPath = ""
        refPath = dicLoadedRef[step]['file']
        lFiles = []
        if refPath:
            stepPath = refPath.split('.')[0]
            lFiles = glob.glob(stepPath+ '*.ma')
        else:
            stepPath = fDatas.getOtherStepDir(assetStep, step)
            lFiles = glob.glob(stepPath+fDatas.dirTrunk+'*.ma')
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

def flagNodes(step):
    nspace = step
    lNodes = mc.ls(nspace+':*', r=True)
    for node in lNodes:
        locked = False
        if mc.lockNode(node, q=True)[0] == True:
            #print 'locked', node
            locked = True
            mc.lockNode(node, l=False)
        if not mc.attributeQuery('stepSource', n=node, ex=True):
            mc.addAttr(node, ln='stepSource', dt='string')
        mc.setAttr(node+'.stepSource', nspace.split(':')[-1], type='string')
        if locked == True:
            #print 'relock', node
            mc.lockNode(node)
        if nspace.split(':')[-1] == 'FUR':
            lCrvShp = mc.ls('FUR:*', r=True, type='nurbsCurve') or []
            if lCrvShp:
                for crvShp in lCrvShp:
                    crv = mc.listRelatives(crvShp, p=True)[0]
                    if not mc.attributeQuery('needRestPos', n=crv, ex=True):
                        mc.addAttr(crv, ln='needRestPos', at='bool', dv=True)


def manageRefs(refDatas, refToKeep):
    lNspaceToKeep = []
    for step in refDatas.keys():
        if step in refToKeep:
            for ref in refDatas[step]:
                print 'trying for', step
                mc.file(ref, ir=True, mnr=False)
                print 'imported :', step
                flagNodes(step)
                print step, 'flagged'
        else:
            for ref in refDatas[step]:
                lNspaceToKeep.append(removeRef(ref))
    return lNspaceToKeep

