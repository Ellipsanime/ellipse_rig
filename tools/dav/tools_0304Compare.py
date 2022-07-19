import maya.cmds as mc
from functools import partial
import sys, os, json


def dicAsset():
    assets = {'ALL': ['SmurfJokey', 'BoxJokeA'], 'Charaters': ['SmurfJokey'], 'Props': ['BoxJokeA'], 'BG': []}
    return assets


def loadAsset(typeTrig, litTrig, *args):
    assets = dicAsset()
    mc.textScrollList(litTrig, e=True, ra=True)
    type = mc.optionMenu(typeTrig, q=True, v=True)
    lAssets = sorted(assets[type])
    for item in lAssets:
        mc.textScrollList(litTrig, e=True, a=item)
    print
    lAssets


def activeDef(shp, val):
    lDef = mc.findDeformers(shp)
    if lDef:
        for node in lDef:
            mc.setAttr(node + '.envelope', val)


# activeDef(mc.ls(sl=True), False)
def buildSceneChk(litTrig, *args):
    asset = mc.textScrollList(litTrig, q=True, si=True)[0]
    print
    asset


def compareSteps(srcStep, lDestSteps, onlyMsh):
    lMshShp = mc.listRelatives(srcStep + ':*', f=True, type='mesh') or []
    if lMshShp:
        lMsh = []
        lDup = []
        lCnst = []
        dicCompare = {}
        dicCompare['unfound'] = {}
        dicCompare['unmatch'] = {}
        for shp in lMshShp:
            msh = mc.listRelatives(shp, p=True, f=True)[0]
            if onlyMsh == True:
                if msh.split('|')[-1].split(':')[-1].startswith('msh_'):
                    if not msh in lMsh:
                        lMsh.append(msh)
            else:
                if not msh in lMsh:
                    lMsh.append(msh)
        for msh in lMsh:
            for destStep in lDestSteps:
                chk = False
                mshDest = msh.replace(srcStep, destStep)
                if not mc.objExists(mshDest):
                    if not msh in dicCompare['unfound'].keys():
                        dicCompare['unfound'][msh] = []
                    dicCompare['unfound'][msh].append(destStep)
                else:
                    activeDef(mc.listRelatives(msh, s=True, ni=True)[-1], False)
                    activeDef(mc.listRelatives(mshDest, s=True, ni=True)[-1], False)
                    dupMsh = mshDest

                    if len(msh.split('|')[-1].split(':')) > 2:
                        dupMsh = mc.duplicate(mshDest)[0]
                        mc.parent(dupMsh, world=True)
                        lDup.append(dupMsh)
                        for attr in ['translate', 'rotate', 'scale']:
                            for chan in ['X', 'Y', 'Z']:
                                mc.setAttr(dupMsh + '.' + attr + chan, lock=False, k=True, cb=True)
                        lCnst.append(mc.parentConstraint(msh, dupMsh, mo=False))
                        lCnst.append(mc.scaleConstraint(msh, dupMsh, mo=False))

                    if not mc.polyCompare(msh, dupMsh) in [0, 8, 16, 32, 64]:
                        print mc.polyCompare(msh, dupMsh)
                        if not msh in dicCompare['unmatch'].keys():
                            dicCompare['unmatch'][msh] = []
                        dicCompare['unmatch'][msh].append(destStep)
                    activeDef(mc.listRelatives(msh, s=True, ni=True)[-1], True)
                    activeDef(mc.listRelatives(mshDest, s=True, ni=True)[-1], True)

    mc.delete(lDup)
    # print dicCompare
    return dicCompare


# compareSteps('SHD:', ['RIG:'], True)

def toto():
    tutu = mc.textFieldGrp('txScrList_assets', q=True, bgc=True)
    print
    tutu


def setSearchType(trigger, driven, father):
    chk = mc.menuItem(trigger, q=True, cb=True)
    if chk:
        mc.textFieldGrp(driven, e=True, l='search * :', ebg=False, bgc=[1, 1, 1])
        mc.columnLayout(father, e=True, cat=['left', -92])
    else:
        mc.textFieldGrp(driven, e=True, l='search :', ebg=False, bgc=[.25, .25, .25])
        mc.columnLayout(father, e=True, cat=['left', -100])
    return chk


def compareSteps_UI():
    assetDir = r'C:\Users\feine\Desktop\04_FAB\ASSETS'
    lTypes = ['ALL', 'Charaters', 'Props', 'BG']
    nWin = 'concordinationCheck'
    nPan = 'conc_masterPan'
    version = '0.1'

    nTypeTrig = 'optMenu_type'
    nListTrig = 'txScrList_assets'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_initRig_UI = mc.window(nWin, t=nWin + version, tlb=True)
    fLay = mc.formLayout(nd=100)
    rowA = mc.columnLayout(adj=True)
    mc.rowLayout(nc=3, adj=3)
    typeTrig = mc.optionMenu(nTypeTrig, label='Type', cc=partial(loadAsset, nTypeTrig, nListTrig))
    for type in lTypes:
        mc.menuItem(label=type)
    mc.separator(hr=False, h=20, st="in")
    mc.columnLayout('colLay_concoedinationChecker', adj=True, cat=['left', -100])
    searchTrig = mc.textFieldGrp('txScrList_assets', l='search :', adj=2, pht='assent name', cc='')
    mc.popupMenu()
    toto = mc.menuItem('chkBox_search', l='start with', cb=False,
                       c='setSearchType("chkBox_search", "txScrList_assets", "colLay_concoedinationChecker")')
    mc.setParent('..')
    mc.setParent('..')

    mc.separator(h=5, st="in")
    mc.setParent('..')

    pan = mc.paneLayout(cn='vertical2')
    mc.frameLayout(l='assets list')
    listTrig = mc.textScrollList(nListTrig)
    mc.popupMenu()
    mc.menuItem(l='reload', c='')
    mc.setParent('..')
    mc.frameLayout(l='Result')
    debbug = mc.textScrollList('concordinationResult')
    mc.popupMenu()
    mc.menuItem(l='clear', c='')
    mc.setParent('..')
    mc.setParent('..')

    colA = mc.columnLayout(adj=True)

    mc.separator(h=5, st="in")
    mc.button(l='check', c=partial(buildSceneChk, nListTrig))

    mc.formLayout(fLay, e=True,
                  af=[(rowA, 'top', 5), (rowA, 'left', 5), (rowA, 'right', 5),
                      (pan, 'left', 5), (pan, 'right', 5),
                      (colA, 'left', 5), (colA, 'right', 5), (colA, 'bottom', 5), ],
                  ac=[(pan, 'top', 5, rowA), (pan, 'bottom', 5, colA)])

    mc.showWindow(win_initRig_UI)


compareSteps_UI()