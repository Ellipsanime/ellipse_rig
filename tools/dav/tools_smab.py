import maya.cmds as mc
from ellipse_rig.tools.dav import tools_smab_v2
reload(tools_smab_v2)
mc.namespace(set=":")
#tools_smab_v2.SMAB_rigCharacterAdd_UI()




"""
import maya.cmds as mc
import maya.mel as mel

from ellipse_rig.library import lib_controlGroup, lib_rigs, lib_namespace, lib_constraints, lib_pipe
reload(lib_controlGroup)
reload(lib_rigs)
reload(lib_namespace)
reload(lib_constraints)
reload(lib_pipe)

#from ellipse_rig.assets.characters import character_guide_ui
#from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import get_maya_main_window
#reload(character_guide_ui)

from ellipse_rig.tools.dav import tools_attach, tools_ctrlShape
reload(tools_attach)
reload(tools_ctrlShape)
mc.namespace(set=':')

import maya.cmds as mc
from ellipse_rig.library import lib_shapes
reload(lib_shapes)

from ellipse_rig.assets.backGrounds import bg_build
reload(bg_build)


def genShp(type):
    crv = lib_shapes.shp_form(type,"Index","red",name=None)
    return crv

def posShp(lObj, type):
    shp = genShp(type)

    #bBox = lib_shapes.bounding_box_utils(lObj,size=None,delete=True)
    #lib_shapes.parent_shp(lsObj=lObj, lsShp=[type], delBaseShp=None, colorType="Index", color="red",rotShp=(0, 0, 0),bound=bBox)
    #lib_shapes.shape_size(shp,rotShp=(0, 0, 0),bound=bBox)


def launchDagHack():
    import sys
    pathCustom ='T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig'
    sys.path.append(pathCustom)
    import dagMenuHack
    reload(dagMenuHack)


#####################################
#def GuguTplTool():
    #im = character_guide_ui.CharacterGuide(parent=get_maya_main_window())
    #im.show()
########################################
#SPACE SWITCH
def getSwitchNode(ctrl):
    '''
    get networkNode for spaceSwitch options or create it
    '''
    node = ctrl
    nspace = ''
    if ':' in ctrl:
        node = lib_namespace.getNodeName(ctrl)
        nspace = lib_namespace.getNspaceFromObj(ctrl) + ':'
    switchNode = ''
    nSwitchNode = 'menu_spaceSwitch' + node[len(node.split('_')[0]):][1].capitalize() + node[len(
        node.split('_')[0]) + 2:].replace('_', '')
    if not mc.attributeQuery('menuSpaceSwitch', node=ctrl, ex=True):
        mc.addAttr(ctrl, ln='menuSpaceSwitch', at='message')
    if mc.connectionInfo(ctrl + '.menuSpaceSwitch', id=True):
        switchNode = mc.listConnections(ctrl + '.menuSpaceSwitch')[0]
    if not switchNode:
        switchNode = mc.createNode('network', n=nSwitchNode)
        mc.connectAttr(switchNode + '.message', ctrl + '.menuSpaceSwitch', f=True)
        if not mc.attributeQuery('targets', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='targets', dt='string', multi=True)
            mc.setAttr(switchNode + '.targets[0]', 'Root', type='string')
        if not mc.attributeQuery('attrs', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='attrs', dt='string', multi=True)
            mc.setAttr(switchNode + '.attrs[0]', '', type='string')
        if not mc.attributeQuery('constraint', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='constraint', at='message')

    return switchNode

def crtSpaceSwitch(lTargets, ctrl, cnstType):
    '''
    create constraint,  add and connect followsAttr ofrom ctrl to constraint attr weight
    '''
    if len(lTargets) > 4:
        print 'you can not give more than 4 targets'
    else:
        node = ctrl
        nspace = ''
        if ':' in ctrl:
            node = lib_namespace.getNodeName(ctrl)
            nspace = lib_namespace.getNspaceFromObj(ctrl) + ':'
        root = nspace + 'root' + node[len(node.split('_')[0]):]
        # root = mc.listRelatives(ctrl, p=True)[0]
        switchNode = getSwitchNode(ctrl)
        for target in lTargets:
            if cnstType == 'parent':
                cnst = mc.parentConstraint(target, root, mo=True)[0]
            elif cnstType == 'orient':
                cnst = mc.orientConstraint(target, root, mo=True)[0]
            elif cnstType == 'point':
                cnst = mc.pointConstraint(target, root, mo=True)[0]
            if not mc.isConnected(cnst + '.message', switchNode + '.constraint'):
                mc.connectAttr(cnst + '.message', switchNode + '.constraint')
            nAttr = target
            if ':' in target:
                nAttr = lib_namespace.getNodeName(target)
            if '_' in nAttr:
                nAttr = nAttr[len(nAttr.split('_')[0]):][1].capitalize() + nAttr[len(nAttr.split('_')[0]) + 2:].replace('_', '')
            if not mc.attributeQuery('follow' + nAttr, node=ctrl, ex=True):
                mc.addAttr(ctrl, ln='follow' + nAttr, at='float', min=0, max=10)
            mc.setAttr(ctrl + '.follow' + nAttr, k=True, cb=True)
            mDL = mc.createNode('multDoubleLinear', n='mDL_follow' + nAttr)
            mc.connectAttr(ctrl + '.follow' + nAttr, mDL + '.input1', f=True)
            mc.setAttr(mDL + '.input2', 0.1)
            cnstGraph = lib_constraints.getCnstGraph(root)
            weghtAtttr = cnstGraph[cnst]['driverAttr'][target]
            if not mc.isConnected(mDL + '.output', cnst + '.' + weghtAtttr):
                mc.connectAttr(mDL + '.output', cnst + '.' + weghtAtttr, f=True)
            id = mc.getAttr(switchNode + '.targets', size=True)
            mc.setAttr(switchNode + '.targets[' + str(id) + ']', nAttr, type='string')
            mc.setAttr(switchNode + '.attrs[' + str(id) + ']', 'follow' + nAttr, type='string')


#crtSpaceSwitch(mc.ls(sl=True), 'RIG:WORLD:SPINE_1:HEAD_1:c_head', 'orient')

def ubiNbsAttach():
    print 'nbsAttch'

def ubiCrvAttach():
    print 'crvAttch'

def ubiOverideTools():
    print 'overideTools'

def ubiTanConst():
    print 'tangConstraintWindow'

def crtHook(lDriver):
    for driver in lDriver:
        hook = 'hook'+driver[len(driver.split('_')[0]):]
        if not mc.objExists('hook'+driver[len(driver.split('_')[0]):]):
            hook = mc.createNode('transform', n='hook'+driver[len(driver.split('_')[0]):])
            dMat = mc.createNode('decomposeMatrix', n='dM'+driver[len(driver.split('_')[0]):])
            mMat = mc.createNode('multMatrix', n='mltM'+driver[len(driver.split('_')[0]):])
            mc.connectAttr(driver + '.worldMatrix[0]', mMat + '.matrixIn[0]')
            mc.connectAttr(hook + '.parentInverseMatrix[0]', mMat + '.matrixIn[1]')
            mc.connectAttr(mMat + '.matrixSum', dMat + '.inputMatrix')
            lAttr = ['translate', 'rotate', 'scale', 'shear']
            for i, attr in enumerate(['outputTranslate', 'outputRotate', 'outputScale', 'outputShear']):
                mc.connectAttr(dMat + '.' + attr, hook + '.' + lAttr[i])

def addClst(lCtrl):
    mc.select(cl=True)
    for ctrl in lCtrl:
        clearName = ctrl
        if ':' in ctrl:
            clearName = ctrl.split(':')[-1]
        nClst = 'clst'+clearName[len(clearName.split('_')[0]):]
        clts = mc.deformer(n=nClst, type='cluster')[0]
        mc.connectAttr(ctrl+'.worldMatrix[0]', clts+'.matrix')
        mc.connectAttr(ctrl+'.parentInverseMatrix', clts+'.bindPreMatrix')
        mc.connectAttr(ctrl+'.matrix', clts+'.weightedMatrix')
        mc.connectAttr(ctrl+'.parentMatrix', clts+'.preMatrix')
    mc.select(lCtrl)

#addClst(mc.ls(sl=True))
###########################################################################
###########################################################################
#GET CONTROL GROUP LIST
def listCG():
    getRefCg=mc.ls('cg_*', r=True, et='network')
    getNewCg=mc.ls('cg_*', et='network')
    getCg=mc.ls('cg_*', r=True, et='network')
    return getCg

def listTplFromCg(cg):
    lTpl = mc.listConnections(cg+'.templates', s=True) or []
    return lTpl

def listCtrlFromCg(cg):
    lCtrl = mc.listConnections(cg+'.members', s=True) or []
    return lCtrl


def updateCgList(itemsList):
    mc.textScrollList(itemsList, e=True, ra=True)
    mc.textScrollList(itemsList, e=True, a=listCG())

def updateTplList(itemsList):
    mc.textScrollList(itemsList, e=True, ra=True)
    if getSelItem('CONTROLE_GROUP'):
        mc.textScrollList(itemsList, e=True, a=listTplFromCg(getSelItem('CONTROLE_GROUP')))
    else:
        mc.warning('select a fuck*** cg on the left list tocard!')

def updateCtrlList(itemsList):
    mc.textScrollList(itemsList, e=True, ra=True)
    if getSelItem('CONTROLE_GROUP'):
        mc.textScrollList(itemsList, e=True, a=listCtrlFromCg(getSelItem('CONTROLE_GROUP')))
    else:
        mc.warning('select a fuck*** cg on the left list tocard!')

def renameItem(itemList):
    cg = getSelItem(itemList)
    print 'renaming', cg
    newName = mc.textField('newName', q=True, tx=True)
    lib_controlGroup.renameCg(cg, newName)
    print cg, 'renamed to ', newName
    updateCgList(itemList)
    nWin = 'cg_rename'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)


def deleteItem(itemList):
    item = getSelItem('CONTROLE_GROUP')
    if not mc.referenceQuery(item, inr=True):
        cg = getSelItem(itemList)
        lib_controlGroup.deleteCg(cg)
        updateCgList(itemList)
    else:
        mc.warning('this cg (', item, ') is from a reference and can t be renamed')

def selectItem(itemsList):
    lItems = getSelItemS(itemsList)
    mc.select(cl=True)
    mc.select(lItems)

###########################################################################
###########################################################################
#GET TAB
def getTab(tabSide, tabNames):
    getTab=mc.tabLayout(tabSide, q=True, sti=True)
    tab=['']
    if  getTab == 1:
        tab = tabNames[1]#'MASTERS_CG'
    elif getTab == 2:
        tab = tabNames[2]#'CONTROLE_GROUP'
    return tab[0]
###########################################################################
###########################################################################
#GET SELECTED ITEM
def getSelItem (itemsList):
    getItem=mc.textScrollList(itemsList, q=True, si=True) or []
    if getItem:
        return getItem[0]
    else:
        return None
###########################################################################
###########################################################################
#GET SELECTED ITEMS
def getSelItemS (itemsList):
    getItem=mc.textScrollList(itemsList, q=True, si=True)
    return getItem
###########################################################################
###########################################################################
#GET NAME FOR NEW CONTROL GROUP
def newCgName():
    getName=mc.textField('getNewCGName', q=True, tx=True)
    return getName
###########################################################################
###########################################################################
#CREATE NEW CONTROL GROUP
def crtCg():
    nCg = newCgName()
    lib_controlGroup.crtCg(nCg)
    updateCgList('CONTROLE_GROUP')

def parentCgTo():
    lCgChild = getSelItemS('EDITS')
    cgFather = getSelItem('CONTROLE_GROUP')
    for cg in lCgChild:
        lib_controlGroup.parentCg(cg, cgFather)
    print lCgChild, 'parented to : ', cgFather

#ADD TEMPLATE TO CG*/
def addTplToCg (itemsList, lTpl):
    cg = getSelItem(itemsList)
    lib_controlGroup.addTplsToCg(lTpl, cg)

#CREATE JOINTS*/
def buildCg(itemsList):
    cg = getSelItem(itemsList)
    lib_controlGroup.buildTplCg(cg)

def addCtrlToCg(itemsList, lCtrl):
    cg = getSelItem(itemsList)
    lib_controlGroup.addCtrlToCg(lCtrl, cg)

def removeFromCg(itemsList):
    lObj = getSelItemS(itemsList) or []
    if lObj:
        for obj in lObj:
            cg = mc.listConnections(obj+'.message', type='network', p=True) or []
            if cg:
                for i in cg:
                    mc.disconnectAttr(obj+'.message', i)
                print obj, 'disconnected from', cg[0].split('.')[0]

#removeFromCg(mc.ls(sl=True))


###########################################
#TMP TOOLS
def addExpertMod(lNodes = ['MOD:ALL', 'RIG:ALL']):
    for node in lNodes:
        if mc.objExists(node):
            if not mc.attributeQuery('expertMode', n=node, ex=True):
                mc.addAttr(node, ln='expertMode', at='bool', dv=1)

#####################################
#####################################
#UI

def renameCg_ui(itemList):
    item = getSelItem('CONTROLE_GROUP')
    if not mc.referenceQuery(item, inr=True):
        nWin = 'cg_rename'
        nPan = 'cg_renamePan'
        if mc.window(nWin, ex=True, q=True):
            mc.deleteUI(nWin, window=True)
        winSMF_renmaCg_UI = mc.window(nWin, t='cg_rename', tlb=True)
        pan = mc.paneLayout(nPan, cn='vertical3')
        mc.rowLayout(nc=2, adj=1)
        mc.textField('newName', h=20)
        mc.button(label='rename', c='tools_smab.renameItem("CONTROLE_GROUP")')

        mc.showWindow(winSMF_renmaCg_UI)
    else:
        mc.warning('this cg (', item, ') is from a reference and can t be renamed')

#renameCg_ui()




def majEditCgMenu(toShow):
    mc.popupMenu('editPopMen', e=True, dai=True)

    if toShow == 'tpl':
        mc.menuItem(l='LOAD TPL', p='editPopMen', c='tools_smab.majEditCgMenu("tpl")')
        mc.menuItem(l='add template', p='editPopMen', c='addTplToCg (\'NEW_CG\')')
        mc.menuItem(l='remove template', p='editPopMen', c='addTplToCg (\'NEW_CG\')')
        mc.menuItem(l='LOAD CTRL', p='editPopMen', c='tools_smab.majEditCgMenu("ctrl")')
        mc.menuItem(l='LOAD CG', p='editPopMen', c='tools_smab.majEditCgMenu("cg")')

    elif toShow == 'ctrl':
        mc.menuItem(l='LOAD TPL', p='editPopMen', c='tools_smab.majEditCgMenu("tpl")')
        mc.menuItem(l='LOAD CTRL', p='editPopMen', c='tools_smab.majEditCgMenu("ctrl")')
        mc.menuItem(l='add ctrl', p='editPopMen', c='addTplToCg (\'NEW_CG\')')
        mc.menuItem(l='remove ctrl', p='editPopMen', c='addTplToCg (\'NEW_CG\')')
        mc.menuItem(l='LOAD CG', p='editPopMen', c='addTplToCg (\'NEW_CG\')')

    elif toShow == 'cg':
        mc.menuItem(l='LOAD TPL', p='editPopMen', c='tools_smab.majEditCgMenu("tpl")')
        mc.menuItem(l='LOAD CTRL', p='editPopMen', c='tools_smab.majEditCgMenu("ctrl")')
        mc.menuItem(l='LOAD CG', p='editPopMen', c='tools_smab.majEditCgMenu("cg")')
        mc.menuItem(l='parent cg to', p='editPopMen', c='addTplToCg (\'NEW_CG\')')
        mc.menuItem(l='remove cg', p='editPopMen', c='addTplToCg (\'NEW_CG\')')


def crtShapes_UI():
    nWin = 'SMF_crtShapesTools'
    nPan = 'CTRLSHAPES_MASTER_pan'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_publishTool_UI = mc.window(nWin, t='shapes tool'+version, tlb=True)

    ######
    pan = mc.paneLayout(nPan, cn='vertical3', w=450)
    ######
    mc.columnLayout(adj=True, w=225)
    mc.rowLayout(nc=5)
    mc.button(l='arrowSingleCrv', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowSingleCrv")')
    mc.button(l='square', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "square")')
    mc.button(l='arrowDouble2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowDouble2")')
    mc.button(l='arrowDouble3', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowDouble3")')
    mc.button(l='circleArrow4', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "circleArrow4")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='pinQuadro', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "pinQuadro")')
    mc.button(l='sphere', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "sphere")')
    mc.button(l='arrowQuadro2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowQuadro2")')
    mc.button(l='arrowSingle', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowSingle")')
    mc.button(l='arrowOctogone', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowOctogone")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='boomrang', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "boomrang")')
    mc.button(l='star', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "star")')
    mc.button(l='pinDouble', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "pinDouble")')
    mc.button(l='arrowQuadroBump', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowQuadroBump")')
    mc.button(l='arrowSingle2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowSingle2")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='squareRounded', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "squareRounded")')
    mc.button(l='arrowLine', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowLine")')
    mc.button(l='circleArrow', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "circleArrow")')
    mc.button(l='cross', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "cross")')
    mc.button(l='crossArrow', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "crossArrow")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='arrowDouble', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowDouble")')
    mc.button(l='rigAdd', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "rigAdd")')
    mc.button(l='circle', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "circle")')
    mc.button(l='arrowDoubleCrv', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowDoubleCrv")')
    mc.button(l='empty', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "empty")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='pyramide2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "pyramide2")')
    mc.button(l='cube', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "cube")')
    mc.button(l='triangle', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "triangle")')
    mc.button(l='arrowSingleCrv2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowSingleCrv2")')
    mc.button(l='line', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "line")')
    mc.setParent ('..')
    mc.rowLayout(nc=5)
    mc.button(l='fly', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "fly")')
    mc.button(l='pyramide', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "pyramide")')
    mc.button(l='arrowDoubleCrv2', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowDoubleCrv2")')
    mc.button(l='pinSimple', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "pinSimple")')
    mc.button(l='roll', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "roll")')
    mc.setParent ('..')
    mc.rowLayout(nc=3)
    mc.button(l='arrowQuadro', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "arrowQuadro")')
    mc.button(l='circleDemi', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "circleDemi")')
    mc.button(l='crossLine', h=75, w=75, c='tools_smab.posShp(mc.ls(sl=True), "crossLine")')
    mc.showWindow(winSMF_publishTool_UI)
#crtShapes_UI()



def SMAB_rigCharacterAdd_UI():
    nWin = 'smab_rigTool'
    nPan = 'MASTER_pan'
    version ='1.1'
    nNewCGName = 'getNewCGName'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winUBI_rigCharacterAdd_UI = mc.window(nWin, t='Setup Multy Asset Builder'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='create spaceSwitch', c='')
    mc.menuItem(l='tangConstraint', c='')
    mc.menuItem(d=True)
    mc.menuItem(l='override tool', c='tools_smab.ubiOverideTools()')

    mc.menuItem(l='TMP TOOLS', c='print "do nothings"')

    mc.menuItem(l='shapes', c='tools_smab.crtShapes_UI()')
    mc.menuItem(l='add expertMode', c='tools_smab.addExpertMod()')
    mc.menuItem(l='add vis attr', c='tools_smab.lib_pipe.addVisAttr("c_FLY", "MOD:GEO")')
    mc.menuItem(l='init wipAni', c='tools_smab.lib_pipe.initWipVAni()')
    mc.menuItem(l='hack dagMenu', c='tools_smab.launchDagHack()')

    mc.menu(l='Tools BG')
    mc.menuItem(l='add rigMe', c='tools_smab.lib_pipe.addFlagAttr("rigMe", 1)')
    mc.menuItem(l='remove rigMe', c='tools_smab.lib_pipe.addFlagAttr("rigMe", 0)')
    mc.menuItem(d=True)
    mc.menuItem(l='add onlyVis', c='tools_smab.lib_pipe.addFlagAttr("onlyVis", 1)')
    mc.menuItem(l='remove onlyVis', c='tools_smab.lib_pipe.addFlagAttr("onlyVis", 0)')
    mc.menuItem(d=True)
    mc.menuItem(d=True)
    mc.menuItem(l='build BG', c='tools_smab.bg_build.build()')
    mc.separator(h=2)
    #mc.menuItem(l='switch loc to STP', c='tools_smab.lib_pipe.rebuildRefInStp("STP")')
    #mc.menuItem(l='switch loc to MOD', c='tools_smab.lib_pipe.rebuildRefInStp("MOD")')

    #mc.menuItem(l='CHAR tpl', c='tools_smab.GuguTplTool()')


    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout(adj=True, w=225)
    mc.text('enter name : ', al='left', font='boldLabelFont', h=12)
    mc.separator(h=2)
    mc.textField(nNewCGName, h=20)
    mc.separator(h=1, st='none')
    mc.button(l='create cg', h=25, bgc=[0.6, 0.75, 0.9], c='tools_smab.crtCg()')
    mc.separator(h=5, st='in')
    mc.button(l='update controlGroup', h=20, c='tools_smab.updateCgList("CONTROLE_GROUP")')
    mc.separator(h=2, st='out')
    ######
    mc.tabLayout('TAB_LEFT')
    mc.textScrollList('CONTROLE_GROUP', numberOfRows=8, ams=False, h=300, w=200)
    mc.popupMenu(b=3, mm=False, aob=True)
    mc.menuItem(l='add template', c='tools_smab.addTplToCg("CONTROLE_GROUP", mc.ls(sl=True))')
    mc.menuItem(l='add controler', c='tools_smab.addCtrlToCg("CONTROLE_GROUP", mc.ls(sl=True))')
    mc.menuItem(divider=True)
    mc.menuItem(l='build cg', c='tools_smab.buildCg("CONTROLE_GROUP")')
    mc.menuItem(l='rename cg', c='tools_smab.renameCg_ui("CONTROLE_GROUP")')
    mc.menuItem(l='add show/hide', c='tools_smab.showHide("CONTROLE_GROUP")')
    mc.menuItem(l='add to Masters', c='addToMaster (\'CONTROLE_GROUP\')')
    mc.menuItem(divider=True)
    mc.menuItem(l='< parent cg to', c='tools_smab.parentCgTo()')
    mc.menuItem(l='show children', c='tools_smab.updateCgList("EDITS")')
    mc.menuItem(divider=True)
    mc.menuItem(divider=True)
    mc.menuItem(l='delete cg', c='tools_smab.deleteItem("CONTROLE_GROUP")')
    mc.setParent('..')
    ######
    mc.separator(h=2, st='out')
    mc.button(l='show all', h=20, c='')
    ##################
    mc.columnLayout(adj=True, w=175, p=pan)
    mc.button(l='add cluster', h=28, w=175, c='tools_smab.addClst(mc.ls(sl=True))')
    mc.button(l='surf attach', h=28, w=175, c='tools_smab.tools_attach.crtSurfAttach(mc.ls(sl=True), "PATH", "SURFATTACH")')
    ##################
    mc.columnLayout(adj=True, w=225, p=pan)
    mc.rowLayout(nc=1, adj=True)
    mc.button(l='create hook', h=28, w=100, c='tools_smab.crtHook(mc.ls(sl=True))')
    mc.setParent('..')
    ######
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='add deleteMe', h=28, w=130, c='tools_smab.lib_pipe.addFlagAttr("deleteMe", 1)')
    mc.button(l='remove deleteMe', h=28, w=130, c='tools_smab.lib_pipe.addFlagAttr("deleteMe", 0)')
    mc.setParent('..')
    mc.separator(h=5, st="in")
    mc.button(l='update controlers', h=20, c='tab=getTab(getNetWorkMember(tab))')
    mc.separator(height=2, style='out')
    ######
    mc.tabLayout('TAB_RIGHT')
    mc.textScrollList('EDITS', numberOfRows=8, ams=True, h=300, w=200)
    mc.popupMenu('editPopMen', b=3, mm=False, aob=True)
    mc.menuItem(l='LOAD TPL', c='tools_smab.updateTplList("EDITS")')
    mc.menuItem(l='remove template', p='editPopMen', c='tools_smab.removeFromCg (\'NEW_CG\')')


    mc.menuItem(divider=True)
    mc.menuItem(l='LOAD CTRL', c='tools_smab.updateCtrlList("EDITS")')
    mc.menuItem(l='remove ctrl', p='editPopMen', c='addTplToCg (\'NEW_CG\')')


    mc.menuItem(divider=True)
    mc.menuItem(l='LOAD CG', c='tools_smab.updateCgList("EDITS")')
    mc.menuItem(l='< parent cg to', p='editPopMen', c='tools_smab.parentCgTo()')
    mc.menuItem(l='remove cg', p='editPopMen', c='tools_smab.updateCgList("EDITS")')
    mc.menuItem(l='showParent', p='editPopMen', c='tools_smab.updateCgList("EDITS")')




    mc.setParent('..')
    ######
    mc.separator(h=2, st='out')
    mc.button(l='select in viewPort', h=20, c='tools_smab.selectItem("EDITS")')
    updateCgList('CONTROLE_GROUP')

    mc.setParent('..')
    mc.setParent('..')

    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Finalize', cll=True)

    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='SAVE NEW REVISION', h=28, w=130, c='tools_smab.lib_pipe.saveNewRev()')
    mc.button(l='PUBLISH', bgc=[.25,.2,.5], h=28, w=130, c='tools_smab.lib_pipe.publishRig(mc.file(q=True, sceneName=True), False)')


    mc.showWindow(winUBI_rigCharacterAdd_UI)

#SMAB_rigCharacterAdd_UI()

"""