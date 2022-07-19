import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import os, glob, re, math
from functools import partial
from importlib import import_module

from ellipse_rig.library import lib_namespace as lNspace
reload(lNspace)

from ellipse_rig.core import project_manager, scene_manager
reload(project_manager)

from ellipse_rig.library import lib_deformers, lib_pipe, lib_names,lib_namespace, lib_controlGroup, lib_blendShape, lib_checkers
reload(lib_deformers)
reload(lib_pipe)
reload(lib_names)
reload(lib_namespace)
reload(lib_controlGroup)
reload(lib_blendShape)
reload(lib_checkers)

from ellipse_rig.prod_pressets import global_presets
reload(global_presets)
from ellipse_rig.core import debbug
reload(debbug)
import tools_facialChanSliders
reload(tools_facialChanSliders)

def faceDescription():
    faceDatas = global_presets.faceDatas()
    prod = project_manager.getProject()
    if prod:
        module = import_module('ellipse_rig.prod_pressets.{}_pressets'.format(prod))
        faceDatas = module.faceDatas()
        print ('get face description for', prod)
    return faceDatas

def listSel():
    return mc.ls(sl=True, fl=True)



###########################################################################################
#"SEPARATIONS"
def buildSep(getSel, lFaceZone, lSepType, *args, **kwargs):
    #buildSep(, )listSel, ["None"], [mc.optionMenu("sepType", q=True, v=True)])
    faceDatas = faceDescription()
    lNeutral = []
    if isinstance(getSel, list):
        lNeutral = getSel
    else:
        lNeutral = getSel()
    #sep types####################
    #mc.menuItem( label='Left')  #
    #mc.menuItem( label='Rigt')  #
    #mc.menuItem( label='Middle')#
    #mc.menuItem( label='Up')    #
    #mc.menuItem( label='Down')  #
    #mc.menuItem( label='Ext')   #
    #mc.menuItem( label='Int')   #
    #mc.menuItem( label='Corner')#
    ##############################
    #list les enum pour creer l attribut
    dicTrgt = faceDatas.trgtNames()
    dicSlices = faceDatas.sepSlices()
    if lSepType == ['getType']:
        lSepType = getSepType("sepType")
    genNspace('SEP')
    for neutral in lNeutral:

        nspace = mc.namespaceInfo(cur=True)+':'
        name = getObjNameFromNspace(neutral)
        baseName = name[len(name.split('_')[0])+1:]

        clearName = baseName
        if not mc.attributeQuery('slices', n=neutral, ex=True):
            mc.addAttr(neutral, ln='slices', at='message', multi=True)
        if '_' in baseName:
            clearName = ''
            tok = baseName.split('_')
            for i in range(0, len(tok)):
                if i > 0:
                    clearName = clearName+tok[i].capitalize()
                elif i == 0:
                    clearName = clearName+tok[i]
                i += 1
        nSep = 'sep_'+clearName
        sepGrp = 'SEP_'+clearName.upper()
        lib_deformers.activeDef(neutral, False)
        if not mc.objExists(nspace + ':' + sepGrp):
            mc.createNode('transform', n=sepGrp)
        for faceZone in lFaceZone:
            for slice in lSepType:
                enAttr = ''
                enZone = faceZone
                for key in dicTrgt.keys():
                    enAttr = enAttr+key+':'

                if faceZone == 'None':
                    faceZone = ''
                    if mc.attributeQuery('sepZone', n=neutral, ex=True):
                        enZone = mc.getAttr(neutral+'.sepZone', asString=True)
                else:
                    faceZone = '_'+faceZone

                for sepType in lSepType:
                    if sepType == 'None':
                        sepType = ''
                    else:
                        sepType = '_'+sepType

                    nDup = nSep+faceZone+sepType
                    dupSep = mc.duplicate(neutral, n=nDup)[0]
                    if not mc.attributeQuery('sepOrig', n=dupSep, ex=True):
                        mc.addAttr(dupSep, ln='sepOrig', at='message')
                    mc.connectAttr(dupSep+'.sepOrig', neutral+'.slices['+str(mc.getAttr(neutral+'.slices', s=True))+']')
                    if not mc.attributeQuery('extractMe', n=dupSep, ex=True):
                        mc.addAttr(dupSep, ln='extractMe', at='bool', dv=True)
                    mc.setAttr(dupSep+'.extractMe', True)

                    if mc.attributeQuery('extractMe', n=neutral, ex=True):
                        mc.setAttr(neutral+'.extractMe', False)
                    #else:
                        #mc.addAttr(neutral, ln='extractMe', at='bool', dv=False)
                    for attr in ['translate', 'rotate', 'scale']:
                        for axe in ['X', 'Y', 'Z']:
                            mc.setAttr(dupSep+'.'+attr+axe, l=False)

                    if enZone in dicTrgt.keys():
                        if not mc.attributeQuery('sepZone', n=dupSep, ex=True):
                            mc.addAttr(dupSep, ln='sepZone', at='enum', en=enAttr)
                        lEnum = mc.attributeQuery('sepZone', n=dupSep, le=True)[0].split(':')
                        dv = lEnum.index(enZone)
                        mc.setAttr(dupSep+'.sepZone', dv)
                    if slice in dicSlices.keys():
                        if not mc.attributeQuery('sepSlice', n=dupSep, ex=True):
                            mc.addAttr(dupSep, ln='sepSlice', dt='string', multi=True)
                        id = mc.getAttr(dupSep+'.sepSlice', s=True)
                        mc.setAttr(dupSep+'.sepSlice['+str(id)+']', dicSlices[slice], type='string')
                    try:
                        mc.parent(dupSep, nspace + ':' + sepGrp)
                    except:
                        pass
                    nBs = 'bs_'+baseName+faceZone+sepType
                    bs = nspace + ':' + nBs
                    if not mc.objExists(nBs):
                        bs = mc.blendShape(neutral, dupSep, n=nBs)[0]
                    mc.setAttr(bs+'.'+name, 1)
        lib_deformers.activeDef(neutral, True)
    mc.namespace(set=':')
#buildSep(mc.ls(sl=True), ['_L', '_R', '_up', '_dn'])
###########################################################################################

# UI TOOLS
###########################################################################################
def crtButton_UI(name='', label='empty', colors=[0.35, 0.35, 0.35], cmmd='print "to do"', h=25, w=200, tip=''):
    if name:
        btn = mc.button(name, l=label, h=h, w=w, bgc=colors, c=cmmd, ann=tip)
        return btn
    else:
        btn = mc.button(l=label, h=h, w=w, bgc=colors, c=cmmd, ann=tip)
        return btn

###########################################################################################################
# UIS
def sculptFace_UI(father):
    panSculptCommons = mc.paneLayout('SCULPT', cn='vertical2', p=father)
    fLayTrgtList = mc.formLayout(nd=100)
    treeTrgt = mc.treeView(adr=False, p=fLayTrgtList)
    popTrgtList = mc.popupMenu()
    mc.menuItem(d=True, dl='Load Targets')
    mc.menuItem(l='Load Trgts')
    mc.menuItem(l='load zone trgt', sm=True)
    mc.menuItem(l='eyebrows')
    mc.menuItem(l='eyelids')
    mc.menuItem(l='mouth')
    mc.menuItem(l='lips')

    mc.menuItem(l='add zone', p=popTrgtList, sm=True)
    mc.menuItem(l='eyebrows')
    mc.menuItem(l='eyelids')
    mc.menuItem(l='mouth')
    mc.menuItem(l='lips')

    mc.menuItem(l='Unload Selected', p=popTrgtList)
    mc.menuItem(d=True, dl='Sort By', p=popTrgtList)
    mc.menuItem(l='Sculpt', p=popTrgtList)
    mc.menuItem(l='Zone', p=popTrgtList)
    mc.menuItem(l='Inbet', cb=True, p=popTrgtList)

    mc.menuItem(d=True, dl='Viewport', p=popTrgtList)
    mc.menuItem(l='select in viewport', p=popTrgtList)
    mc.menuItem(l='Isolate in viewport', p=popTrgtList)

    mc.treeView(treeTrgt, e=True, addItem=("mo_smile", ""))
    mc.treeView(treeTrgt, e=True, addItem=("mo_smile_050", "mo_smile"))
    mc.treeView(treeTrgt, e=True, addItem=("mo_frown", ""))
    mc.treeView(treeTrgt, e=True, addItem=("mo_wide", ""))
    mc.treeView(treeTrgt, e=True, addItem=("mo_narrow", "mo_narrow"))
    mc.treeView(treeTrgt, e=True, addItem=("mo_narrow_025", "mo_narrow"))
    mc.treeView(treeTrgt, e=True, addItem=("mo_narrow_050", "mo_narrow"))
    mc.treeView(treeTrgt, e=True, addItem=("mo_narrow_075", "mo_narrow"))

    mc.formLayout(fLayTrgtList, e=True,
                  af=[(treeTrgt, 'top', 1), (treeTrgt, 'left', 1), (treeTrgt, 'right', 1), (treeTrgt, 'bottom', 1)])

    mc.setParent('..')
    mc.columnLayout(adj=True)
    # panSculptCommons = mc.paneLayout('zizilal', cn='horizontal2')

    mc.frameLayout('SCULPT TOOLS', cll=True)
    tabTasks = mc.tabLayout('SCULPT_tab')
    mc.columnLayout('ZONES', adj=True)
    mc.rowLayout(nc=2, adj=1)
    btnAddInBet = crtButton_UI('addInbet_btn', 'add inbet')
    btnRemInBet = crtButton_UI('removeInbet_btn', 'remove inbet')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='add Trgt')
    mc.button(l='remove Trgt')

    # mc.formLayout(fLayTrgtTask, e=True, af=[(treeTrgt, 'top', 1), (treeTrgt, 'left', 1), (treeTrgt, 'right', 1), (treeTrgt, 'bottom', 1)])

    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout('SKIN COR', adj=True)
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='Init Sculpt Pose')
    mc.button(l='Connect Sculpt Pose')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='Add Inbet')
    mc.button(l='Remove Inbet')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='Mirror L To R')
    mc.button(l='Mirror R To L')
    mc.setParent('..')

    mc.setParent('..')
    mc.columnLayout('MIX ZONES', adj=True)
    mc.button()
    mc.button()

    mc.setParent('..')
    mc.columnLayout('MIX SLICES', adj=True)
    mc.button()
    mc.button()

    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='Commons Tools', cll=True)
    mc.columnLayout(adj=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Transfert Sculpt To',
              ann='transfert first selected vtx position to others select can select mesh or vtx')
    mc.button(l='Reset', ann='reset first selected vtx position to others select can select mesh or vtx')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Self Mirror Sculpt L -> R', ann='mirror vtx position on the selected mesh from left to right')
    mc.button(l='Self Mirror Sculpt R -> L', ann='mirror vtx position on the selected mesh from right to left')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Self Flip Sculpt L -> R',
              ann='transfert first selected vtx position to others select can select mesh or vtx')
    mc.button(l='Self Flip Sculpt R -> L')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Wrap To All', ann='transfert first selected vtx position to others select can select mesh or vtx')
    mc.button(l='Kill Wrap')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Check Vtx Move', ann='transfert first selected vtx position to others select can select mesh or vtx')
    mc.button(l='Kill Checkers')


def sepFace_UI(father):
    mc.columnLayout('SEPARATION', adj=True, p=father)
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Separations Tools', cll=True)
    mc.columnLayout(adj=True)
    mc.rowLayout(nc=2, adj=2)
    btnInit = crtButton_UI('initSep_btn', 'init separations')
    btnUpdate = crtButton_UI('updateWght_btn', 'update weights')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    #mc.frameLayout(l='Sep Tools', cll=True)
    mc.rowLayout(nc=2, adj=1)
    # dicTrgt = lib_names.trgtNames()
    # mc.menuItem( label='None')
    # for key in sorted(dicTrgt.keys()):
    #    mc.menuItem(label=key)

    nTrgtType = mc.optionMenu('sepType', label='SLICE POLE  :')
    mc.menuItem(label='None')
    mc.menuItem(label='Left')
    mc.menuItem(label='Right')
    mc.menuItem(label='Middle')
    mc.menuItem(label='Up')
    mc.menuItem(label='Down')
    mc.menuItem(label='Ext')
    mc.menuItem(label='Int')
    mc.menuItem(label='Corner')
    # mc.button(l='ADD SEP', bgc=[.25,.2,.5], h=28, w=230, c=partial(buildSep, listSel, [mc.optionMenu("sepZone", q=True, v=True)], [mc.optionMenu("sepType", q=True, v=True)])')
    btnInit = crtButton_UI('addSlice_btn', 'Gen slice', cmmd=partial(buildSep, listSel, ["None"], ['getType']))

    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='Weight Tools', cll=True)
    mc.columnLayout(adj=True)

    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=6, adj=3)
    mc.text(label='wght : ', align='left')
    mc.floatField(minValue=0.0, maxValue=1.0)
    mc.floatScrollBar(min=0.0, max=1.0, step=0.01, largeStep=0.01)
    mc.separator(h=15, st='in', hr=False)
    mc.text(label=' step : ', align='right')
    mc.floatField(minValue=0.0, maxValue=1.0, v=0.05, pre=2)
    #btnStepWght = crtButton_UI('wghtStep_btn', 'set step', w=50)



    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    btnWghtCopy = crtButton_UI('copyWght_btn', 'copy weight to')
    btnWghtFlip = crtButton_UI('flipWght_btn', 'self flip weight')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    btnWghtMirrorL = crtButton_UI('mirrorWghtL_btn', 'mirror weight L to R')
    btnWghtMirrorR = crtButton_UI('mirrorWghtR_btn', 'mirror weight R to L')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    btnWghtNegative = crtButton_UI('negativeWght_btn', 'inverse weight to')
    btnWghtNormalize = crtButton_UI('normalizeWght_btn', 'normalize slices weight')



###########################################################################################
def SMAB_facialSculptTool_ui():
    nWin = 'UI_facialSculptTool'
    nPan = 'MASTER_facialSculptTool'
    version = '2.0'
    nProjectMenu = 'FACIALSCULPT_projectMenuName'


    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_facialSculptTool_UI = mc.window(nWin, t='facial tools' + version)

    mBar = mc.menuBarLayout('facialTool_mBar')
    mc.menu(l='File')
    mc.menuItem(l='Init')
    mc.menuItem(d=True, dl='Scene Gestion')
    mc.menuItem(l='Save New Inc')
    mc.menuItem(l='Reload Current')
    mc.menu(l='Tools')

    mc.menu(nProjectMenu, label='Project')
    panMaster = mc.paneLayout(nWin + 'MasterPan', cn='vertical2')
    tools_facialChanSliders.chanSliders_UI(panMaster)
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.tabLayout('MASTER_tab')

    ###################################################################################################################
    ###################################################################################################################

    sculptFace_UI('MASTER_tab')

    sepFace_UI('MASTER_tab')

    ###################################################################################################################
    ###################################################################################################################

    mc.columnLayout('BUILD', adj=True, w=225, p='MASTER_tab')
    mc.separator(h=7.5, st='in')

    mc.frameLayout(l='Face Rig', cll=True)
    mc.rowLayout(nc=3, adj=2)

    mc.setParent('..')
    mc.separator(h=7.5, st='in')

    ###################################
    ###################################
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    toto = mc.helpLine()

    mc.showWindow(win_facialSculptTool_UI)


#SMAB_facialSculptTool_ui()
