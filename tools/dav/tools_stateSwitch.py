import maya.cmds as mc
import maya.mel as mel
import sys, os, json

from ellipse_rig.library import lib_UI
reload(lib_UI)


class tree_stateSwitchDrivers_UI(lib_UI.UI_treeView):
    def __init__(self, name='STSW_drivers_tree', treeParent='STSW_masterPan', popUpName='STSW_drivers_popup', *args):
        super(tree_stateSwitchDrivers_UI, self).__init__(*args)
        # globals
        self.name = name
        self.parent = treeParent
        self.itemSelId = 'id'
        self.popUp = popUpName
        self.itemSel = ''
        self.rnCgClbkInc = 0


    def treePopUp(self):
        mc.popupMenu(self.popUp, p=self.name)
        mc.menuItem(l='Load Sel', p=self.popUp, c='')
        mc.menuItem(l='Load all drivers', p=self.popUp, c='')
        mc.menuItem(divider=True)


class tree_stateSwitchDriven_UI(lib_UI.UI_treeView):
    def __init__(self, name='STSW_driven_tree', treeParent='STSW_masterPan', popUpName='STSW_driven_popup', *args):
        super(tree_stateSwitchDriven_UI, self).__init__(*args)
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

def crtTxtLay():
    print 'toto'

def getTxtLay():
    print 'toto'



def stateSwitch_UI():
    version = os.getenv('REZ_ELLIPSE_RIG_VERSION')
    if version == None:
        version = '__HP__'
    nWin = 'STSW_tool'
    nPan = 'STSW_masterPan'
    nFormLay = 'STSW_formLay'
    nFramLay = 'STSW_framLayout'
    nColumnLay = 'STSW_treeColLay'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)

    win_stateSwitch_UI = mc.window(nWin, t='State switchs '+version)
    mBar = mc.menuBarLayout('SMAB_mBarName')
    mc.menu(l='File', to=True)
    mc.menuItem(divider=True, dividerLabel='INIT')
    pan = mc.paneLayout(nPan, cn='quad')


    ##############################################################################################################
    ##############################################################################################################
    #CONTROL GRP PANEL




    drivenTree = tree_stateSwitchDriven_UI()
    drivenTree.buildTreeView()
    driversTree = tree_stateSwitchDrivers_UI()
    driversTree.buildTreeView()

    #mc.setParent('..')




    formLay = mc.formLayout(nFormLay)
    framLay = mc.frameLayout(nFramLay, l='Debbug', cll=True, bv=True, bgc=[.2, .5, .5], bgs=True)
    zizilol = mc.textScrollList()

    mc.setParent('..')
    mc.setParent('..')
    mc.columnLayout()

    toto = mc.button()
    tutu = mc.button()
    titi = mc.button()

    mc.formLayout(formLay, e=True, af=[(framLay, 'left', 5), (framLay, 'bottom', 5), (framLay, 'top', 5), (framLay, 'right', 5)])


    mc.showWindow(win_stateSwitch_UI)


#stateSwitch_UI()