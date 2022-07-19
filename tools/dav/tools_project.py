import maya.cmds as mc
from functools import partial
import sys, os, json

from ellipse_rig.library import lib_UI
reload(lib_UI)



class tree_assetManager_UI(lib_UI.UI_treeView):
    def __init__(self, name='', treeParent='', popUpName='',*args):
        super(tree_assetManager_UI, self).__init__(*args)
        # globals
        self.name = name
        self.parent = treeParent
        self.itemSelId = 'id'
        self.popUp = popUpName
        self.itemSel = ''
        self.rnCgClbkInc = 0

    def treePopUp(self):
        mc.popupMenu(self.popUp, p=self.name)
        mc.menuItem(l='Add sel', p=self.popUp, c='')
        mc.menuItem(l='Add Txt', p=self.popUp, c='')
        mc.menuItem(divider=True)


def setDirPath(nProjectDir, *args):
    dirPath = mc.fileDialog2(dir=newDirPath, dialogStyle=1, cap='SUCE', fm=1, okc='SMABIT')
    mc.textField(nProjectDir, e=True, fileName=dirPath)
    return dirPath


def initSceneUI():
    dicDatas = {}
    dicDatas['type'] = ['ALL', 'Charaters', 'Props', 'BG']
    dicDatas['steps'] = ['ALL', 'FUR', 'MOD', 'STP', 'SHD']
    nWin = 'init_project'
    nPan = 'INIT_masterPan'
    nProjectDir = 'toto'
    version = '0.1'

    nTypeTrig = 'optMenu_type'
    nStepTrig = 'optMenu_step'
    nListTrig = 'txScrList_assets'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_initRig_UI = mc.window(nWin, t=nWin + version, tlb=True)
    fLay = mc.formLayout(nd=100)
    rowA = mc.columnLayout(adj=True)
    mc.rowLayout(nc=2, adj=2)
    typeTrig = mc.optionMenu(nTypeTrig, label='Type', cc='')
    for type in dicDatas['type']:
        mc.menuItem(label=type)
    #stepTrig = mc.optionMenu(nStepTrig, label='Step', cc='')
    #for step in dicDatas['steps']:
        #mc.menuItem(label=step)


    searchTrig = mc.textFieldGrp(nListTrig, l='search :', adj=2, cc='')
    mc.popupMenu()
    mc.menuItem('chkBox_search', l='start with', cb=False)
    mc.setParent('..')

    mc.separator(h=5, st="in")
    mc.setParent('..')
    #mc.columnLayout('AM_treePan', adj=True)
    fistul = mc.paneLayout(cn='right3')
    assetsTree = tree_assetManager_UI(name='AM_assetsList_tree', treeParent=fistul, popUpName='AM_assetsList_popup')
    assetsTree.buildTreeView()
    mc.textScrollList()
    mc.textScrollList()

    mc.setParent('..')
    colA = mc.columnLayout(adj=True)
    mc.separator(h=5, st="in")
    suce = mc.button(l='reload')

    mc.formLayout(fLay, e=True,
                  af=[(rowA, 'top', 5), (rowA, 'left', 5), (rowA, 'right', 5),
                      (fistul, 'left', 5), (fistul, 'right', 5),
                      (colA, 'left', 5), (colA, 'right', 5), (colA, 'bottom', 5), ],
                  ac=[(fistul, 'top', 5, rowA), (fistul, 'bottom', 5, colA)])

    #assetsTree.loadItemsInTree({0:{'Master':['Char', 'Prp', 'BG']}, 1:{'Char':['Smurf', 'Azrael'], 'Prp':['Plate', 'Knife']}})



    mc.showWindow(win_initRig_UI)





