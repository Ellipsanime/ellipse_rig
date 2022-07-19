import maya.cmds as mc
from ellipse_rig.library import lib_pipe
import os
import glob


nTplList = 'templates'
nCtrlList = 'controlers'
nitemTree = 'SMAB_itemTree'
class tree_view():

    def __init__(self, name='', treeParent='', popUpName='', *args):
        self.name = name
        self.parent = treeParent
        self.itemSelId = 'id'
        self.popUp = popUpName
        self.itemSel = ''
        self.renamerClbkInc = 0


    def buildTreeView(self):
        if not mc.objExists(self.name):
            mc.treeView(self.name, p=self.parent)
            mc.treeView(self.name, e=True, enk=True, ams=True)

            mc.treeView(self.name, e=True, dad=self.dADropClbk)

            mc.treeView(self.name, e=True, irc=self.rnItemClbk)
            mc.treeView(self.name, e=True, sc=self.selItemClbk)
            self.treePopUp()
        return self.name

    def getSelectedItem(self, *args):
        itemSel = mc.treeView(self.name, q=True, si=True)
        if itemSel:
            return itemSel[0]

    def selItemClbk(self, *args):
        self.itemSel = args[0]
        return True

    def rnItemClbk(self, *args):
        self.renamerClbkInc += 1
        if self.renamerClbkInc == 1:
            lItems = lib_controlGroup.getAllItems()
            lExistingNames = []
            for item in lItems:
                treeName = mc.getAttr(item+'.treeName')
                if not treeName in lExistingNames:
                    lExistingNames.append(treeName)
            item = self.itemSel
            newitem = item
            newName = mc.treeView(self.name, q=True, si=True) or []
            if newName:
                newName = newName[0]
                if len(newName) > 3:
                    if not newName == newitem:
                        if not newName.startswith('item_') and not ':' in item:
                            newName = 'item_'+newName
                        #if not mc.treeView(self.name, q=True, iex=newName):
                        if not newName in lExistingNames:
                            if mc.objExists(item):
                                if not mc.referenceQuery(item, inr=True):
                                    newitem = lib_controlGroup.renameitem(item, newName)
                            else:
                                lItems = listitem()
                                for existitem in lItems:
                                    if mc.getAttr(existitem+'.treeName') == newitem:
                                        newitem = existitem
                                        if not mc.referenceQuery(item, inr=True):
                                            newitem = lib_controlGroup.renameitem(item, newName)
                            if mc.objExists(newitem):
                                mc.lockNode(newitem, lock=False)
                                mc.setAttr(newitem+'.treeName', newName, type='string')
                                mc.lockNode(newitem, lock=True)
                        else:
                            mc.warning(newName, 'already exists')
                            self.loaditemInTree(self.name)
                else:
                    mc.warning('the name is empty or have less than 3 caraters ("item_" included in the caracters count)')
                    self.loaditemInTree(self.name)


    def dADropClbk(self, *args):
        #item = self.itemSel
        #newFather = mc.treeView(self.name, q=True, ip=self.itemSel)
        newFather = args[3]
        lItems = args[0]
        for item in lItems:
            if item != newFather:
                parentitemTo(self.itemSel, newFather)
                print item, 'parented to', newFather
            elif item == newFather:
                self.loaditemInTree(self.name)


    def loaditemInTree(self, itemTree):
        mc.treeView(self.name, e=True, ra=True)
        dicitem = lib_controlGroup.getitemHi(lib_controlGroup.getAllItems())
        for i in range(0, len(dicitem.keys())):
            for item in dicitem[i]:
                father = ''
                chkFather = mc.listConnections(item+'.parent', s=True, d=False) or []
                if chkFather:
                    father = chkFather[0]
                mc.treeView(self.name, e=True, addItem=(item, father))
                if not mc.attributeQuery('treeName', n=item, ex=True):
                    mc.lockNode(item, lock=False)
                    mc.addAttr(item, ln='treeName', dt='string')
                    mc.setAttr(item+'.treeName', item, type='string')
                    mc.lockNode(item, lock=True)
                itemLabel = mc.getAttr(item+'.treeName')
                if not itemLabel == item:
                    if ':' in item:
                        if item.split(':')[-1] == itemLabel:
                            itemLabel = item
                            mc.lockNode(item, lock=False)
                            mc.setAttr(item+'.treeName', item, type='string')
                            mc.lockNode(item, lock=True)
                mc.treeView(self.name, e=True, dl=(item, itemLabel))




    def treePopUp(self):
        mc.popupMenu(self.popUp, p=self.name)
        mc.menuItem(l='add sel as TPL', p=self.popUp, c='tools_smab_v2.addTplToitem(mc.ls(sl=True))')
        mc.menuItem(l='add sel as CTRL', p=self.popUp, c='tools_smab_v2.addCtrlToitem(mc.ls(sl=True))')
        mc.menuItem(divider=True)
        mc.menuItem(l='build item', p=self.popUp, c='tools_smab_v2.builditem()')
        mc.menuItem(divider=True)

        mc.menuItem(l='delete item', p=self.popUp, c='tools_smab_v2.deleteSelItem(tools_smab_v2.nitemTree)')
        mc.menuItem(divider=True)
        mc.menuItem(l='parent orphans to item_all', p=self.popUp, c='tools_smab_v2.parentOrphanitem(tools_smab_v2.nitemTree)')
        mc.menuItem(l='Select in viewport', p=self.popUp, c='tools_smab_v2.selectItemInViewport(tools_smab_v2.finditemFromTree())')
        #mc.menuItem(l='show item from sel', p=self.popUp)
        #mc.menuItem(l='select ctrl', p=self.popUp)
        #mc.menuItem(l='select tpl', p=self.popUp)

########################################################################################################################
#####################################


nTplList = 'locList'
nCtrlList = 'controlers'
nCgTree = 'SMAB_cgTree'

def smfSwitchTool_ui():
    nWin = 'SMF_modSwirchTool'
    nPan = 'MASTER_panModSwitch'
    version ='1.1'
    nFormLay = 'SWITCH_formLayout'
    nFramLay = 'SMAB_framLAyout'
    nColumnLay = 'SMAB_treeColLay'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_facialSepTool_UI = mc.window(nWin, t='switch tools'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tool', c='')
    mc.separator(h=2)
    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout('cL_SwitchLoc', adj=True, w=225)
    mc.button(l='LOAD LOC', bgc=[.2,.3,.5], h=28, w=100, c='tools_modChr.loadSwitchLocs()')
    mc.textScrollList(nTplList, numberOfRows=8, ams=True, h=300, w=200)
    mc.popupMenu('SMAB_tplListPopup', b=3, mm=False, aob=True)
    mc.menuItem(l='Load cg TPL', c='tools_smab_v2.updateTplList(tools_smab_v2.nTplList)')
    mc.menuItem(l='Remove from cg', c='tools_smab_v2.removeFromCg(tools_smab_v2.nTplList)')
    mc.menuItem(divider=True)
    mc.menuItem(l='Select in viewport', c='tools_smab_v2.selectItemInViewport(tools_smab_v2.getSelItemS(tools_smab_v2.nTplList))')




    mc.setParent('..')



    colLay = mc.columnLayout('cL_SwitchAttributes', adj=True, w=225)
    treeLoad = mc.button(l='reload_btn', bgc=[.5,.2,.2], h=28, w=130, c='tools_modChr.lib_pipe.removeDelMe()')
    #formLay = mc.formLayout(nFormLay, nd=100)



    #mc.separator(h=7.5, st='in')
    cgTree = tree_view(name=nCgTree, treeParent=colLay, popUpName='attributesTreePopUp')
    cgTree.buildTreeView()
    #mc.formLayout(formLay, e=True, af=[(colLay, 'top', 5), (colLay, 'left', 5), (colLay, 'right', 5), (colLay, 'bottom', 5)])

    mc.setParent('..')
    mc.setParent('..')

    mc.separator(h=2)
    mc.tabLayout('TAB_SWITCH')

    mc.rowLayout('textures_switchs', nc=2, adj=1)
    mc.button(l='COPY msh pose', bgc=[.2,.5,.5], h=28, w=100, c='tools_modChr.copyMshPose(mc.ls(sl=True))')
    mc.button(l='UNLOAD rig pose', bgc=[.5,.2,.4], h=28, w=100, c='tools_modChr.removeStpChrPose()')
    mc.setParent('..')


    mc.rowLayout('visibility_switchs', nc=2, adj=1)
    mc.button(l='ADD DELETE ME', bgc=[.2,.5,.5], h=28, w=130, c='tools_modChr.lib_pipe.addDelMe()')
    mc.button(l='REMOVE DELETE ME', bgc=[.5,.2,.2], h=28, w=130, c='tools_modChr.lib_pipe.removeDelMe()')
    mc.setParent('..')

    mc.rowLayout('speciale_edits', nc=2, adj=1)
    mc.button(l='ADD SKIP ME', h=28, w=130, bgc=[.2,.5,.5], c='tools_modChr.lib_pipe.addFlagAttr("skipMe", 1)')
    mc.button(l='REMOVE SKIP ME', h=28, w=130, bgc=[.5,.2,.2], c='tools_modChr.lib_pipe.addFlagAttr("skipMe", 0)')





    mc.showWindow(winSMF_facialSepTool_UI)
#smfSwitchTool_ui()

