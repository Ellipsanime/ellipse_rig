import maya.cmds as mc
from ellipse_rig.library.lib_glossary import lexiconAttr as attrName

def getTplDataNodes(attr):
    lDataNodes = []
    lNodes = mc.ls('*.'+attr, r=True)
    for node in lNodes:
        if mc.getAttr(node) == 1:
            lDataNodes.append(node.split('.')[0])

    return lDataNodes
#getTplDataNodes(attrName('moduleDataTpl'))

def getTplDataNodeFromTpl(tpl):
    dataNode = mc.getAttr(tpl+'.infPart')
    return dataNode
#getTplDataNodes(attrName('moduleDataTpl'))


def getBuildTplHi(lDataNodes):
    master = ''
    dicHi = {}
    if lDataNodes:
        for node in lDataNodes:
            if not mc.connectionInfo(node+'.'+attrName('attrParent'), id=True):
                master = node
                dicHi[0] = [master]
        lDataNodes.remove(master)
        i = 0
        for inc in range(0, len(lDataNodes)):
            lFathers = dicHi[i] or []
            i += 1
            dicHi[i] = []
            for father in lFathers:
                lChilds = mc.listConnections(father+'.'+attrName('attrChild'), d=True, s=False, plugs=False)
                if lChilds:
                    for child in lChilds:
                        if not child in dicHi[i]:
                            dicHi[i].append(child)
                        if child in lDataNodes:
                            lDataNodes.remove(child)
                    inc += len(lChilds)
        for key in dicHi.keys():
            if not dicHi[key]:
                try:
                    del dicHi[key]
                except:
                    pass
    return dicHi

#getBuildTplHi(getTplDataNodes(attrName('moduleDataTpl')))

def getDataNodeInc(dataNode):
    inc = ''
    if mc.attributeQuery('incInfo', n=dataNode, ex=True):
        inc = '_'+mc.getAttr(dataNode+'.incInfo')
    return inc

def getDataNodeModuleType(dataNode):
    moduleType = mc.getAttr(dataNode+'.'+attrName('moduleType'))
    if moduleType == 'FLY':
        moduleType = 'all'
    return moduleType

def getDataNodeSide(dataNode):
    side = ''
    if len(dataNode.split('_')) > 3:
        side = '_' + dataNode.split('_')[-1]
    return side


def getMatchIkFkCtrl(dataNode):
    dicCtrl = {}
    inc = getDataNodeInc(dataNode)
    side = getDataNodeSide(dataNode)
    end = ''
    if inc:
        end = end+inc
    if side:
        end = end+side
    dicCtrl['Switch'] = mc.getAttr(dataNode+'.cg_switch'+end+'[0]')
    dicCtrl['IK'] = mc.getAttr(dataNode+'.cg_ik'+end+'[0]')
    s = mc.getAttr(dataNode+'.cg_fkMb'+end, s=True)
    dicCtrl['FK'] = []
    for i in range(0, s):
        dicCtrl['FK'].append(mc.getAttr(dataNode+'.cg_fkMb'+end+'['+str(i)+']'))

    return dicCtrl
#getMatchIkFkCtrl('tplInfo_leg_1_L')