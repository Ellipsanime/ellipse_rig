import maya.cmds as mc
import glob, os
import namespace
reload(namespace)
from ellipse_rig.library import lib_controlGroup
reload(lib_controlGroup)


#___SHAPES___###########################################################################################################
def getGraphShp(obj):
    #return dic with shapes orig, inter def and not connected shapes
    #shapeOrig can be the same as shapeDef if their is nohistory on the mesh and then, we need to keep only the showed shape
    lShp = mc.listRelatives(obj, s=True) or []
    if lShp:
        dicShp = {}
        dicShp['shpOrig'] = []
        dicShp['shpDef'] = []
        dicShp['shpInter'] = []
        dicShp['shpResidual'] = []
        for shp in lShp:
            chkInter = mc.getAttr(shp+'.intermediateObject')
            chkInMsh = mc.listConnections(shp+'.inMesh') or []
            chkWrdMsh = mc.listConnections(shp+'.inMesh') or []
            chkOutMsh = mc.listConnections(shp+'.outMesh') or []
            if not chkWrdMsh and not chkInMsh:
                if not chkOutMsh :
                    if chkInter :
                        dicShp['shpResidual'].append(shp)
                    elif not chkInter:
                        dicShp['shpOrig'].append(shp)
                        dicShp['shpDef'].append(shp)
                elif chkOutMsh :
                    dicShp['shpOrig'].append(shp)

            elif chkWrdMsh or chkInMsh:
                if chkOutMsh :
                    dicShp['shpInter'].append(shp)
                elif not chkOutMsh :
                    if chkInter :
                        dicShp['shpResidual'].append(shp)
                    elif not chkInter:
                        dicShp['shpDef'].append(shp)
    return dicShp

#getGraphShp(mc.ls(sl=True))
#__REFERENCES__#########################################################################################################
def impRef():
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True)
    for ref in lRef:
        mc.file(ref, ir=True)



def cleanRefEdits(refNode):
    lEdits = mc.reference(referenceNode=refNode, query=True, editCommand=True) or []
    mc.file(ur=refNode)
    if lEdits:
        for edit in lEdits:
            action = edit.split('|')[0]
            mc.file(cr=refNode, editCommand=action)



def removeRef(ref):
    refNode = mc.referenceQuery(ref, rfn=True)
    nSpace = mc.referenceQuery(ref, ns=True)
    print ref, 'nspaces are :', nSpace
    cleanRefEdits(refNode)
    mc.file(ref, rr=True)
    if mc.namespace(ex=':'+nSpace):
        mc.namespace(rm=nSpace)



def refCleaner(scenePath, dicNspace):
    lRef = mc.file(scenePath, q=True, reference=True) or []
    if lRef:
        for ref in lRef:
            refNode = mc.referenceQuery(ref, rfn=True)
            nspace = mc.referenceQuery(ref, ns=True)
            clearNspace = nspace[1 :]
            inc = ''
            if '_' in nspace:
                clearNspace = clearNspace.split('_')[0]
                inc = clearNspace.split('_')[-1]
            if clearNspace in dicNspace['importe']:
                mc.file(ref, ir=True, mnr=False)
                #mc.namespace(rm=nspace, mnr=True)
            elif clearNspace in dicNspace['remove']:
                removeRef(ref)
#refCleaner( mc.file(q=True, sceneName=True), lib_names.refNspaceNames())

def refCleaner_v2(dicRef):
    for ref in dicRef['importe']:
        mc.file(ref, ir=True, mnr=False)
    for ref in dicRef['remove']:
        if ref:
            removeRef(ref)
#refCleaner( mc.file(q=True, sceneName=True), lib_names.refNspaceNames())


def nspaceCleanner(dicNspaces):
    lNspace = namespace.lsAllNspace(toExclude=['UI', 'shared'])
    for nspace in lNspace:
        clearNspace = nspace
        if '_' in nspace:
            clearNspace = clearNspace.split('_')[0]
        if nspace in dicNspaces['importe'] or clearNspace in dicNspaces['importe']:
            if mc.namespace(ex=':'+nspace):
                mc.namespace(rm=':'+nspace, mnr=True)

"""
def nspaceCleanner_props(dicNspaces):
    lNspace = namespace.lsAllNspace(toExclude=['UI', 'shared'])
    for nspace in lNspace:
        clearNspace = nspace
        if '_' in nspace:
            clearNspace = clearNspace.split('_')[0]
        if nspace in dicNspaces['importe'] or clearNspace in dicNspaces['importe']:
            if mc.namespace(ex=':'+nspace):
                mc.namespace(rm=':'+nspace, mnr=True)

"""
def listExpNspaces():
    lExpNspace = []
    lExpLoc = mc.ls('*.exp_data', r=True, o=True) or []
    if lExpLoc:
        for loc in lExpLoc:
            if mc.attributeQuery('name_space', n=loc, ex=True):
                lExpNspace.append(mc.getAttr(loc+'.name_space'))
    return lExpNspace



def nspaceCleanner_props(fDatas, lExpNspaces):
    lNspace = namespace.lsAllNspace(toExclude=['UI', 'shared'])
    print 'namespaces found :',  lNspace
    for nspace in reversed(lNspace):
        print 'working on NSPACE :', nspace
        if mc.namespace(ex=':'+nspace):
            if nspace in fDatas.nSpaces.values():
                #print nspace, 'removed'
                mc.namespace(rm=':'+nspace, mnr=True)
            else:
                if not nspace in lExpNspaces and not nspace.startswith('RIG:'):
                    #print nspace, 'removed because not lExpNSpaces'
                    mc.namespace(rm=':'+nspace, mnr=True)
            """



            elif '_' in nspace:
                inc = nspace.split('_')[-1]
                lNodes = mc.ls(nspace+':*', r=True)
                for node in lNodes:
                    if mc.objExists(node):
                        mc.rename(node, node+'_'+inc)
                if mc.namespace(ex=':'+nspace):
                    mc.namespace(rm=':'+nspace, mnr=True)
            """

#nspaceCleanner_props()

#nspaceCleanner_props()

def remRef(scenePath):
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
            # si le namespace est UV, on clean la ref et on remove
            elif nSpace == ':UV':
                print 'UV'
            # si la ref doit etre importee en dure dans la scene
            else:
                mc.file(ref, ir=True)
                mc.namespace(rm=nSpace)
                print ref, 'imported and cleaned'

#remRef()
#__PARENTS__############################################################################################################
def getAssetBox():
    lCam = mc.listCameras()
    lTopNodes = mc.ls(assemblies=True)
    box = ''
    for node in lTopNodes:
        remove = 0
        if mc.referenceQuery( node, isNodeReferenced=True ):
            remove = 1
        if mc.attributeQuery('deleteMe', n=node, ex=True):
            if mc.getAttr(node+'.deleteMe') == 1:
                remove = 1
        if node in lCam :
            remove = 1

        if remove == 0:
            box = node
            break
    return box
#getAssetBox()

def getAllBoxs():
    lCam = mc.listCameras()
    lTopNodes = mc.ls(assemblies=True)
    lBox = []
    for node in lTopNodes:
        remove = 0
        if node in lCam:
            remove = 1
        if not ':' in node:
            if mc.attributeQuery('deleteMe', n=node, ex=True):
                if mc.getAttr(node+'.deleteMe') == 1:
                    remove = 1
        if remove == 0:
            lBox.append(node)
    return lBox


def getRefBoxs():
    lNspace = []
    lBoxs = []
    scenePath = mc.file(q=True, sceneName=True)
    lRef = mc.file(scenePath, q=True, reference=True)
    for ref in lRef:
        refNode = mc.referenceQuery(ref, rfn=True)
        nSpace = mc.referenceQuery(ref, ns=True)
        lNspace.append(nSpace)
    lTopNodes = mc.ls(assemblies=True)
    for node in lTopNodes:
        if ':' in node:
            lBoxs.append(node)
    return lBoxs

def removeTmpHi():
    lNodes = mc.ls('*.tmpHi', o=True)
    for node in lNodes:
        if mc.getAttr(node+'.tmpHi') == 1:
            father = mc.listRelatives(node, p=True)[0]
            lChilds = mc.listRelatives(node, c=True, type='transform')
            for child in lChilds:
                mc.parent(child, father)
            mc.delete(node)

####OLD#####################################################################################
def comparObj(objSrc, objDest):
    if objSrc.split(':')[-1] == objDest.split(':')[-1]:
        return 1
    else:
        return 0

def recurseHi(objSrc, objDest, do, dicHi):
    lChildSrc = mc.listRelatives(objSrc, c=True, s=False) or []
    lChildDest = mc.listRelatives(objDest, c=True, s=False) or []
    if lChildDest :
        if lChildSrc :
            for childDest in lChildDest:
                for childSrc in lChildSrc:
                    do = comparObj(childSrc, childDest)
                    if do == 1:
                        recurseHi(childSrc, childDest, do, dicHi)
                    else:
                        if not  objSrc in dicHi.keys():
                            dicHi[objSrc] = []
                        if not childDest in dicHi[objSrc]:
                            dicHi[objSrc].append(childDest)
    return dicHi

def makeHi(father, lChildren):
    for child in lChildren:
        mc.parent(child, father)

def hiFusion(nspaceKeeped):
    lBoxs = getAllBoxs()
    masterBox = getAssetBox()
    for box in lBoxs:
        if box.split(':')[0] == nspaceKeeped:
            masterBox = box
    if masterBox in lBoxs:
        lBoxs.remove(masterBox)
    for box in lBoxs:
        addDelMe(box)
        nspaceBox = ':'
        if ':' in box:
            nspaceBox = box.split(':')[0]
        dicHi = compareHi(masterBox, box, nspaceKeeped+':', nspaceBox+':')
        for key in dicHi.keys():
            for father in dicHi[key].keys():
                for child in dicHi[key][father]:
                    if mc.objExists(father):
                        if mc.objExists(child):
                            #print 'try fathering', child, 'to',  father
                            try:
                                mc.parent(child, father)
                            except:
                                #print 'TA MERE', child, father
                                pass
    remTrash()
#hiFusion('MOD')


def convertName(name, toReplace, new):
    trunc = name.split('|')
    newName = ''
    for stick in trunc:
        if stick != '':
            if not toReplace in stick:
                newName = newName+'|'+new+stick
            elif toReplace in stick:
                newStick = stick.replace(toReplace, new)
                newName = newName+'|'+newStick
    return newName
#convertName('|ALL|GEO|geo_head|geo_lashes_R|msh_lash2_R', ':', 'MOD:')

def compareHi(hiSrc, hiToCHk, nspaceSrc, nspaceToSwitch):
    lChild = mc.listRelatives(hiToCHk, ad=True, f = True, type = 'transform') or []
    dicHi = {}
    if lChild:
        for child in lChild:
            childDest = convertName(child, nspaceToSwitch, nspaceSrc)
            if not mc.objExists(childDest):
                father = mc.listRelatives(child, p=True)[0]
                fatherDest = convertName(father, nspaceToSwitch, nspaceSrc).split('|')[-1]
                if not mc.objExists(fatherDest):
                    fatherDest = father
                deep = len(child.split('|'))
                if not deep in dicHi.keys():
                    dicHi[deep] = {}
                if not fatherDest in dicHi[deep].keys():
                    dicHi[deep][fatherDest] = []
                dicHi[deep][fatherDest].append(child)
    return dicHi
#compareHi('MOD:ALL', 'ALL', 'MOD:', ':')

#__DELETES__############################################################################################################
def addDelMe(node):
    if not mc.attributeQuery('deleteMe', n=node, ex=True):
        mc.addAttr(node, ln='deleteMe', at='bool', dv=1, k=False)
    mc.setAttr(node+'.deleteMe', 1)



def remTrash():
    #list tout les nodes (et leur enfants) a suprimer
    lNodes = mc.ls('*.deleteMe', o=True, r=True)
    if lNodes:
        print 'here are the nodes with a DELETEME :', lNodes
        for node in lNodes:
            if mc.objExists(node):
                if mc.getAttr(node+'.deleteMe') == 1:
                    mc.lockNode(node, lock=False)
                    mc.delete(node)

def removeTmpFather():
    lNodes = mc.ls('*.tmpFather', o=True, r=True)
    if lNodes:
        for node in lNodes:
            if mc.getAttr(node+'.tmpFather') == 1:
                father = mc.listRelatives(node, p=True)[0]
                lChilds = mc.listRelatives(node, c=True) or []
                if lChilds:
                    for child in lChilds:
                        mc.parent(child, father)
                mc.delete(node)

def remove_unkowPlugNodes():
    lUnknowPlugs = mc.unknownPlugin(q=True, l=True) or []
    if lUnknowPlugs:
        for plug in lUnknowPlugs:
            try:
                mc.unknownPlugin(plug, r=True)
            except:
                print 'can t remove', plug
                pass



def remove_plugNodes(lPlugs):
    lActivePlugs = mc.pluginInfo(query=True, listPlugins=True)
    for plug in lPlugs:
        if plug in lActivePlugs:
            lTypesNode = mc.pluginInfo(plug, query=True, dn=True) or []
            if lTypesNode:
                remove_nodes(lTypesNode)
                for type in lTypesNode:
                    lNodes = mc.ls(type=type) or []
                    if lNodes:
                        for node in lNodes:
                            print node
                            mc.lockNode(node, lock=False)
                            mc.delete(node)
            mc.flushUndo()
            mc.unloadPlugin(plug, f=True)
    remove_unkowPlugNodes()

#remove_plugNodes(['Turtle', 'mtoa'])


def remove_nodes(lTypesNode=['displayLayer', 'nodeGraphEditorInfo', 'animLayer', 'unknown'], lToKeep=['defaultLayer']):
    for typeNode in lTypesNode:
        lNodes = mc.ls(type=typeNode)
        for toKeep in lToKeep:
            if toKeep in lNodes:
                lNodes.remove(toKeep)
        for node in lNodes:
            if mc.objExists(node):
                mc.lockNode(node, lock=False)
                lConn = mc.listConnections(node, c=True, p=True, s=True, d=True) or []
                if lConn:
                    for i in range(1, len(lConn)):
                        if mc.isConnected(lConn[i], lConn[i-1]):
                            mc.disconnectAttr(lConn[i], lConn[i-1])
                        elif mc.isConnected(lConn[i-1], lConn[i]):
                            mc.disconnectAttr(lConn[i-1], lConn[i])
                        i += 2
                #print 'deleting :', node
                mc.delete(node)
#remove_nodes(['displayLayer', 'nodeGraphEditorInfo'], ['defaultLayer'])

def removeStep(lStep):
    dicToKeep = {}
    lToDel = []
    lNodes = mc.ls('*.stepSource', r=True, o=True)
    lBox = []
    for node in lNodes:
        step = mc.getAttr(node+'.stepSource')
        if step in lStep:
            if not step in dicToKeep.keys():
                dicToKeep[step] = {}
                dicToKeep[step]['nodes'] = []
                dicToKeep[step]['box'] = ''
            if mc.attributeQuery('keepMe', n=node, ex=True):
                if mc.getAttr(node + '.keepMe') == True:
                    dicToKeep[step].appendNode(node)
            if not mc.attributeQuery('stepSource', n=mc.listRelatives(node, p=True)[0], ex=True):
                dicToKeep[step]['box'] = node
                lBox.append(node)
            else:
                if not mc.getAttr(mc.listRelatives(node, p=True)[0]+'.stepSource') == step:
                    dicToKeep[step]['box'] = node
            if not node in dicToKeep[step]['nodes'] or not node in dicToKeep[step]['box']:
                lToDel.append(node)

    if dicToKeep:
        for step in dicToKeep.keys():
            for node in dicToKeep[step]['nodes']:
                mc.parent(node, dicToKeep[step]['box'])

    mc.delete(lToDel)
    for box in lBox:
        if not mc.listRelatives(furBox, c=True):
            mc.delete(furBox)
#removeStep()


def removeShdDags():
    lNodes = mc.ls('*.stepSource', r=True, o=True) or []
    lToKeep = []
    lDrivers = mc.ls('*.stateSwitch', r=True, o=True) or []
    if lDrivers:
        for loc in lDrivers:
            if not loc in lToKeep:
                lToKeep.append(loc)
            father = mc.listRelatives(loc, p=True)[0]
            if not father in lToKeep:
                lToKeep.append(father)
            #mc.parent(father, world=True)
    lDags = mc.ls(lNodes, dag=True)
    if lDags:
        for node in lDags:
            if mc.objExists(node):
                if mc.attributeQuery('stepSource', n=node, ex=True):
                    if mc.getAttr(node+'.stepSource') == 'SHD':
                        if not node in lToKeep:
                            mc.delete(node)
#removeShdDags()

def deleteNspace():
    lNspace = namespace.lsAllNspace(['UI', 'shared'])
    for nspace in lNspace:
        namespace.removeNspace(nspace, keep=True)

def deleteAniCrv():
    lAniCrv = mc.ls(type='animCurve')
    lDKey = []
    lAniKey = []
    for crv in lAniCrv:
        lConn = mc.listConnections(crv, s=True, d=False) or []
        if lConn:
            lDKey.append(crv)
        elif not lConn:
            lAniKey.append(crv)
    if lAniKey:
        mc.delete(lAniKey)
#deleteAniCrv()

#__LOCKS__##############################################################################################################
def lock_shapes_and_smooth():
    topNode = mc.ls(type='transform')[0]
    lMsh = mc.ls(type = 'mesh')
    if not mc.attributeQuery('lockMesh', n=topNode, ex=True):
        mc.addAttr(topNode, ln='lockMesh', at='enum', en='Unlock:Lock', dv=1)
    lOldTopNode = mc.ls('*.lockMesh', type='transform') or []
    for oldTopNode in lOldTopNode:
        mc.connectAttr(topNode+'.lockMesh', oldTopNode, f=True)
    for msh in lMsh:
        if not mc.isConnected(topNode+'.lockMesh', msh +'.overrideEnabled'):
            mc.connectAttr(topNode+'.lockMesh', msh +'.overrideEnabled')
        mc.setAttr(msh + '.overrideDisplayType', 2)
        for attr in ['.displaySubdComps', '.smoothLevel', '.useSmoothPreviewForRender']:
            mc.setAttr(msh+attr, lock=True)

#__DISPLAY__############################################################################################################
def set_joint_draw(state=2):
    lSk = mc.ls(type='joint', allPaths=True) or []
    for sk in lSk:
        if not mc.listConnections(sk + '.drawStyle', connections=True, destination=True, source=False):
            if not mc.getAttr(sk + '.drawStyle', lock=True):
                mc.setAttr(sk + '.drawStyle', state)

def hide_ctrl_hist():
    lNodes = mc.ls()
    for node in lNodes:
        try:
            if not mc.attributeQuery('nodeType', n=node, ex=True):
                mc.setAttr(node + '.isHistoricallyInteresting', 0)
            elif not mc.getAttr(node + '.nodeType') == 'control':
                mc.setAttr(node + '.isHistoricallyInteresting', 0)
        except:
            print node + '.isHistoricallyInteresting is lock'

def hideCurvesAttr():
    lCrv = mc.ls(type='nurbsCurve', r=True)
    for crv in lCrv:
        lAttrs = mc.listAttr(crv) or []
        lUserAttrs = mc.listAttr(crv, ud=True) or []
        lDefaultAttrs = lAttrs
        if lUserAttrs:
            lDefaultAttrs = list(set(lAttrs)-set(lUserAttrs))
        for attr in lDefaultAttrs:
            if '.' in attr:
                pass
            else:
                #mc.setAttr(obj+'.'+attr, l=True, k=False, cb=False)
                mc.setAttr(crv + '.' + attr, k=False, cb=False)
#HiddeAttributShape('WORLD:curveShape2')


def hiddeNurbs():
    lNurbs = mc.ls(type='nurbsSurface', long=True)
    for node in lNurbs:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])
def hiddeCurves():
    lCrv = mc.ls(type='nurbsCurve', long=True)
    for node in lCrv:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])
def hiddeLoc():
    lLoc = mc.ls(type='locator', long=True)
    for node in lLoc:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])

def hiddeIkHdl():
    lIks = mc.ls(type='ikHandle', long=True)
    for node in lIks:
        try:
            mc.setAttr(node+'.v', False)
        except:
            mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])

def hiddeAnchor():
    lNodes = mc.ls('*.data-type')
    for node in lNodes:
        if not mc.attributeQuery('nodeType', n=mc.listRelatives(node, p=True, f=True)[0], ex=True):
            try:
                mc.setAttr(mc.listRelatives(node, p=True, f=True)[0]+'.v', False)
            except:
                mc.warning('can t hide : '+mc.listRelatives(node, p=True, f=True)[0])

"""
def hiddeNode(dicTypes):
    for type in dicTypes.keys():
        lNodes = mc.ls(type=type)
        for node in lNodes:
            if type == 'nurbsSurface':
                mc.setAttr(node+'.v', False)
            elif type == 'locator':
                for flag in lFlags:
                    if mc.attributeQuery
            father = mc.listRelatives(node, p=True) or []
        print lNurbs
hiddeNode({'nurbsSurface':[''], 'locator':['exp_data']})
"""

def renameCg():
    lCg = lib_controlGroup.getAllCg()
    for cg in lCg:
        name = mc.getAttr(cg+'.treeName')
        if name.startswith('RIG:'):
            name = name.split(':')[-1]
        mc.rename(cg, name)


def setObjectSets(nspace):
    lSets = mc.ls(type='objectSet')
    for set in lSets:
        if set.split(':')[-1].startswith('ctrl_') or set.split(':')[-1].startswith('skin_'):
            mc.addAttr(set, ln=nspace.lower()+'Set', at='bool', dv=True)
#setObjectSets('MOD')


def cleanCgSets():
    lCg = lib_controlGroup.getAllCg()
    lRigSets = mc.ls('*.rigSet', r=True, o=True) or []
    for cg in lCg:
        lRigSets.append(cg.replace('cg_', 'ctrl_'))
        lRigSets.append(cg.replace('cg_', 'skin_'))
    for set in lRigSets:
        if mc.objExists(set):
            mc.delete(set)
    dicHiCg = lib_controlGroup.getCgHi(lCg)
    for key in reversed(dicHiCg.keys()):
        for cg in dicHiCg[key]:
            nSet = cg.replace('cg_', 'ctrl_')
            lCtrl = lib_controlGroup.getCtrlFromCg(cg) or []
            lChilds = lib_controlGroup.getCgChilds(cg) or []
            if lChilds:
                for child in lChilds:
                    if mc.attributeQuery('ctrlSet', n=child, ex=True):
                        childSet = mc.listConnections(child+'.ctrlSet', s=True)[0]
                    lCtrl.append(childSet)
            ctrlSet = mc.sets(lCtrl, n=nSet)
            mc.connectAttr(ctrlSet+'.message', cg+'.ctrlSet', f=True)




def clearExpertMode():
    lNodes = mc.ls('*.expertMode', r=True)
    if lNodes:
        for node in lNodes:
            mc.setAttr(node, False)

def unfreezeVtxNormals():
    lMsh = mc.ls(type='mesh')
    for msh in lMsh:
        if not mc.listConnections(msh+'.inMesh', s=True):
            mc.polySetToFaceNormal(msh)
            mc.polySoftEdge(msh,  a=180, ch=1)
            val = mc.getAttr(msh+'.intermediateObject')
            mc.setAttr(msh+'.intermediateObject', False)
            mc.delete(msh, ch=True)
            mc.setAttr(msh+'.intermediateObject', val)
            mc.select(cl=True)



def rootUnkeyable():
    lNodes = mc.ls(dag=True)
    lCtrl = []
    for node in mc.ls('*.nodeType', r=True, o=True):
        if mc.getAttr(node+'.nodeType') == 'control':
            lCtrl.append(node)
    for node in lNodes:
        if not node in lCtrl:
            for attr in ['translate', 'rotate', 'scale']:
                for chan in ['X', 'Y', 'Z']:
                    if mc.attributeQuery(attr+chan, n=node, ex=True):
                        mc.setAttr(node+'.'+attr+chan, k=False)
###################################################################
#VIRUS



def killVaccs(nodesToFlag, filesToKill):
    lNodes = mc.ls(type='script')
    infected = False
    for node in lNodes:
        if node in nodesToFlag:
            infected = True
            if mc.objExists(node):
                mc.delete(node)
                print (node, 'deleted')

    if infected:
        dir = mc.internalVar(userAppDir=True) + r'scripts/'
        lFiles = glob.glob(dir + '*.py')
        for found in lFiles:
            fName = os.path.basename(found)
            if fName in filesToKill:
                if os.path.isfile(found):
                    os.remove(found)
                    print (fName, 'removed from', found.replace(fName, ''))


#killVaccs(['breed_gene', 'vaccine_gene'], ['vaccine.py', 'userSetup.py'])