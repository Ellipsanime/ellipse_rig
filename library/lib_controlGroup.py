import maya.cmds as mc
import maya.mel as mel
from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_dataNodes
from ellipse_rig.library.lib_glossary import lexiconAttr as attrName
from ellipse_rig.library.lib_glossary import lexicon as nName
#from OLD.prod.setup.base.rigFacial.core import control
#from OLD.prod.setup.base.rigFacial.foundations import typeLib, attributeLib

from ellipse_rig.library import lib_tmp



reload(gloss)
reload(lib_dataNodes)
reload(lib_tmp)




def crtCg(nCg):
    cg = lib_tmp.ControlGroup(nCg)
    return cg
#crtCg('fur')

def setCg(nCg):
    cg = nCg
    controlGroups = lib_tmp.ControlGroup(nCg)
    if controlGroups:
        cg = controlGroups
    return cg
#setCg('cg_fur')


def parentCg(nCg, nCgFather):
    cg = setCg(nCg)
    if nCgFather:
        cgFather = lib_tmp.ControlGroup(nCgFather)
        cg.parentCgTo(cgFather)
    elif nCgFather == '':
        unparentCg(cg)

def parentOrphanCg():
    lCg = getAllCg()
    cgBox = 'cg_all'
    if not cgBox in lCg:
        if 'RIG:cg_all' in lCg:
            cgBox = 'RIG:cg_all'
    dicCgHi = getCgHi(lCg)
    for cg in dicCgHi[0]:
        if not cg == cgBox:
            parentCg(cg, cgBox)

def unparentCg(cg):
    toKill = mc.listConnections(str(cg)+'.parent', s=True, plugs=True, d=False) or []
    if toKill:
        mc.disconnectAttr(toKill[0], str(cg)+'.parent')


def addTplToCg(node, nCg):
    templated = []
    cg = setCg(nCg)
    if lib_tmp.ObjectType(node).isOfType('controlTemplate'):
        templated.append(node)
    else:
        lib_tmp.ControlTemplate(node)
    templated.append(node)
    addedNodes = cg.addTemplates(templated)
#addTplToCg(mc.ls(sl=True)[0], setCg('cg_fur'))

def addTplsToCg(lNodes, nCg):
    templated = []
    cg = setCg(nCg)
    for node in lNodes:
        if lib_tmp.ObjectType(node).isOfType('controlTemplate'):
            templated.append(node)
        else:
            lib_tmp.ControlTemplate(node)
        templated.append(node)
    cg.addTemplates(templated)
#addTplToCg(mc.ls(sl=True), setCg('cg_face'))

def buildTplCg(nCg):
    cg = setCg(nCg)
    cg.buildControls(verbose=False, progressBar=None)
#buildTplCg(setCg('cg_fur'))


def addCtrlToCg(lCtrl, nCg):
    crtCg = lib_tmp.ControlGroup(nCg)
    for ctrl in lCtrl:
        crtCg.addControl(ctrl)
    return crtCg

def buildCG():
    attrData = attrName('moduleDataTpl')
    attrBuildCg = attrName('buildCg')
    dicDataNodes = lib_dataNodes.getBuildTplHi(lib_dataNodes.getTplDataNodes(attrData))
    lCg = []
    for key in dicDataNodes.keys():
        for dataNode in dicDataNodes[key]:
            if mc.attributeQuery(attrBuildCg, n=dataNode, ex=True):
                if mc.getAttr(dataNode+'.'+attrBuildCg) == 1:
                    moduleType = mc.getAttr(dataNode+'.'+attrName('moduleType'))
                    if moduleType == 'FLY':
                        moduleType = 'all'
                    inc = ''
                    if mc.attributeQuery('incInfo', n=dataNode, ex=True):
                        inc = '_'+mc.getAttr(dataNode+'.incInfo')
                    side = ''
                    if len(dataNode.split('_')) > 3:
                        side = '_' + dataNode.split('_')[-1]
                    nCg = nName('cg')+'_'+moduleType+inc+side
                    lCtrlAttr = mc.listAttr(dataNode, ud=True, multi=True, st='cg_*') or []
                    lCtrl = []
                    for ctrlAttr in lCtrlAttr:
                        lCtrl.append(mc.getAttr(dataNode+'.'+ctrlAttr))
                    crtCg = addCtrlToCg(lCtrl, nCg)
                    cg = crtCg.getControlGroup()
                    lCg.append(cg)
                    if not mc.attributeQuery(attrName('builtCg'), n=dataNode, ex=True):
                        mc.addAttr(dataNode, ln=attrName('builtCg'), at='message')
                    mc.connectAttr(cg+'.message', dataNode+'.'+attrName('builtCg'), f=True)
                    fatherDataNode = mc.listConnections(dataNode+'.'+attrName('attrParent'), s=True, d=False, plugs=False)
                    if fatherDataNode:
                        cgFather = mc.listConnections(fatherDataNode[0]+'.'+attrName('builtCg'), s=True, d=False, plugs=False)[0]
                        id = mc.getAttr(cgFather+'.children', s=True)
                        mc.connectAttr(cgFather+'.children['+str(id)+']', cg+'.parent')

                    lExtraCtrlAttr = mc.listAttr(dataNode, ud=True, st='childCg_*') or []
                    for cgAttr in lExtraCtrlAttr:
                        inc = mc.getAttr(dataNode+'.'+cgAttr, s=True)
                        lCtrl = []
                        for i in range(0, inc):
                            lCtrl.append(mc.getAttr(dataNode+'.'+cgAttr+'['+str(i)+']'))

                        nExtraCg = nName('cg')+cgAttr[len(cgAttr.split('_')[0]):]
                        crtExtraCg = addCtrlToCg(lCtrl, nExtraCg)
                        extraCg = crtExtraCg.getControlGroup()
                        id = mc.getAttr(cg+'.children', s=True)
                        mc.connectAttr(cg+'.children['+str(id)+']', extraCg+'.parent')
    return lCg

def getTplFromCg(cg):
    lTpl = mc.listConnections(cg+'.templates', s=True)
    return lTpl

def getCtrlFromCg(cg):
    lCtrl = mc.listConnections(cg+'.members', s=True)
    return lCtrl


def getAllCg():
    lNet = mc.ls(type='network', r=True)
    lCg = []
    for net in lNet:
        if mc.attributeQuery('nodeType', n=net, ex=True):
            if mc.getAttr(net+'.nodeType') == 'controlGroup':
                lCg.append(net)
    return lCg
#getAllCg()

def getCgChilds(cg):
    lChild = mc.listConnections(cg+'.children', d=True) or []
    return lChild

def getCgFather(cg):
    father = mc.listConnections(cg+'.parent', d=True) or []
    return father

def getCgFatherToChild():
    lCg = getAllCg()
    dicCg = {}
    for cg in lCg:
        lChild = mc.listConnections(cg+'.children', d=True) or []
        if lChild:
            dicCg[cg] = lChild
    return dicCg
#getCgFatherToChild()


def renameCg(cg, newName):
    if not mc.referenceQuery(cg, inr=True):
        nspace = ''
        nNewCg = newName
        clearName = newName
        if ':' in cg:
            nOldCg = cg.split(':')[-1]
            nspace = cg[: len(cg)-len(nOldCg)]
            if not newName.startswith('cg_'):
                clearName = nspace+'cg_'+nNewCg
            else:
                clearName = nspace+nNewCg
        else:
            if not newName.startswith('cg_'):
                clearName = 'cg_'+newName
        mc.lockNode(cg, l=False)
        mc.rename(cg, clearName)
        print 'RENAMED', cg, clearName
        mc.lockNode(clearName, l=True)
        return clearName
    else:
        print 'this cg (', cg, ') is from a reference'


def getCgHi(lCg):
    lMaster = []
    dicHi = {}
    dicHi[0] = []
    if lCg:
        for cg in lCg:
            if not mc.connectionInfo(cg+'.parent', id=True):
                lMaster.append(cg)
                dicHi[0].append(cg)
        for master in lMaster:
            lCg.remove(master)
        i = 0
        for inc in range(0, len(lCg)):
            lFathers = dicHi[i] or []
            i += 1
            dicHi[i] = []
            for father in lFathers:
                lChilds = mc.listConnections(father+'.children', d=True, s=False, plugs=False)
                if lChilds:
                    for child in lChilds:
                        if not child in dicHi[i]:
                            dicHi[i].append(child)
                        if child in lCg:
                            lCg.remove(child)
                    inc += len(lChilds)
        for key in dicHi.keys():
            if not dicHi[key]:
                try:
                    del dicHi[key]
                except:
                    pass
    return dicHi



def deleteCg(cg):
    if not mc.referenceQuery(cg, inr=True):
        mc.lockNode(cg, l=False)
        mc.delete(cg)




def snapTplToCtrl(cg):
    lCnst = []
    lCtrl = getCtrlFromCg(cg)
    for ctrl in lCtrl:
        id = ''
        lIds = mc.getAttr(ctrl+'.nodesId', mi=True)
        for i in lIds:
            if mc.getAttr(ctrl+'.nodesId['+str(i)+']') == 'nsTpl':
                id = str(i)
        tpl = mc.listConnections(ctrl+'.nodes['+id+']', s=True, d=False)[0]
        lCnst.append(mc.parentConstraint(ctrl, tpl, mo=False)[0])
    mc.delete(lCnst)
    print 'templates are snapped on their controler for cg :', cg
#snapTplToCtrl('cg_face')
###################################
#BIND POSES
###################################
def getControlGroupMembers(cg, recursive=True):
    members = mc.listConnections(cg + '.members', sh=1) or []
    if recursive:
        childs = mc.listConnections(cg + '.children') or []
        for c in childs:
            members.extend(getControlGroupMembers(c))
    return members




def restoreBindPose(nodes, *args):
    if isinstance(nodes, basestring):
        nodes = [nodes]
    # init
    ctrls = []
    # get controllers
    for node in nodes:
        if mc.objectType(node) == 'network':
            ctrls = getControlGroupMembers(node)
        else:
            ctrls.append(node)
    # reset controllers
    for ctrl in ctrls:
        if mc.attributeQuery('bindPoseAttrs', node=ctrl, exists=True) and mc.attributeQuery('bindPoseValues', node=ctrl, exists=True):
            attrs = mc.getAttr(ctrl + '.bindPoseAttrs', mi=True) or []
            for x in attrs:
                attr = mc.getAttr('{0}.bindPoseAttrs[{1}]'.format(ctrl, x))
                if not mc.getAttr('{0}.{1}'.format(ctrl, attr), settable=True):
                    continue
                value = mc.getAttr('{0}.bindPoseValues[{1}]'.format(ctrl, x))
                if not attr == 'ikBlend':
                    mc.setAttr('{0}.{1}'.format(ctrl, attr), value)


def setBindPose(nodes, *args):
    if isinstance(nodes, basestring):
        nodes = [nodes]
    # init
    ctrls = []
    # get controllers
    for node in nodes:
        if mc.objectType(node) == 'network':
            ctrls = getControlGroupMembers(node)
        else:
            ctrls.append(node)
    # set bindPose on controllers
    for ctrl in ctrls:
        # create attributes
        if mc.attributeQuery('bindPoseAttrs', n=ctrl, ex=True):
            indices = mc.getAttr(ctrl + '.bindPoseAttrs', multiIndices=True) or []
            if indices:
                for x in indices:
                    mc.removeMultiInstance('{0}.bindPoseAttrs[{1}]'.format(ctrl, x))
        else:
            mc.addAttr(ctrl, ln='bindPoseAttrs', multi=True, dt='string')
        if mc.attributeQuery('bindPoseValues', n=ctrl, ex=True):
            indices = mc.getAttr(ctrl + '.bindPoseValues', multiIndices=True) or []
            if indices:
                for x in indices:
                    mc.removeMultiInstance('{0}.bindPoseValues[{1}]'.format(ctrl, x))
        else:
            mc.addAttr(ctrl, ln='bindPoseValues', multi=True, at='float')
        # set bindPose
        keyableAttrs = mc.listAttr(ctrl, visible=True, keyable=True, scalar=True, leaf=True, shortNames=True) or []
        if keyableAttrs:
            bindPoseAttrs = []
            bindPoseValues = []
            idx = 0
            for x in xrange(len(keyableAttrs)):
                plug = '{0}.{1}'.format(ctrl, keyableAttrs[x])
                if mc.objExists(plug):
                    bpAttrsPlug = ctrl + '.bindPoseAttrs[{}]'.format(idx)
                    mc.setAttr(bpAttrsPlug, keyableAttrs[x], type='string')
                    bindPoseAttrs.append(keyableAttrs[x])
                    value = mc.getAttr(plug)
                    bpValuesPlug = ctrl + '.bindPoseValues[{}]'.format(idx)
                    mc.setAttr(bpValuesPlug, value)
                    bindPoseValues.append(value)
                    idx += 1