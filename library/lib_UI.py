import maya.cmds as mc



class UI_treeView(object):
    #cgTree = cg_tree_view(name=nCgTree, treeParent=framLay, popUpName='SMAB_cgTreePopUp')
    #cgTree.buildTreeView()
    #cgTree.loadCgInTree(cgTree)

    def __init__(self, name='', treeParent='', popUpName='', *args):
        self.name = name
        self.parent = treeParent
        self.itemSelId = 'id'
        self.popUp = popUpName
        self.itemSel = ''
        self.rnCgClbkInc = 0


    def buildTreeView(self):
        if not mc.objExists(self.name):
            mc.treeView(self.name, p=self.parent)
            mc.treeView(self.name, e=True, enk=True, ams=True)

            mc.treeView(self.name, e=True, dad=self.dADropClbk)

            mc.treeView(self.name, e=True, irc=self.rnCgClbk)
            mc.treeView(self.name, e=True, sc=self.selItemClbk)
            self.treePopUp()
        return self.name

    def getSelectedItem(self, *args):
        itemSel = mc.treeView(self.name, q=True, si=True)
        if itemSel:
            return itemSel[0]

    def selItemClbk(self, *args):
        self.itemSel = args[0]
        self.rnCgClbkInc = 0
        return True

    def rnCgClbk(self, *args):
        self.rnCgClbkInc += 1
        if self.rnCgClbkInc -1 == 0:
            lCg = lib_controlGroup.getAllCg()
            lExistingNames = []
            for cg in lCg:
                treeName = mc.getAttr(cg+'.treeName')
                if not treeName in lExistingNames:
                    lExistingNames.append(treeName)
            cg = self.itemSel
            newCg = cg
            newName = mc.treeView(self.name, q=True, si=True) or []
            if newName:
                print 'HERRE', newName
                newName = newName[0]
                if len(newName) > 3:
                    if not newName == newCg:
                        if not newName.startswith('cg_') and not ':' in cg:
                            newName = 'cg_'+newName
                        #if not mc.treeView(self.name, q=True, iex=newName):
                        if not newName in lExistingNames:
                            if mc.objExists(cg):
                                if not mc.referenceQuery(cg, inr=True):
                                    newCg = lib_controlGroup.renameCg(cg, newName)
                                    #self.rnCgClbkInc = 0
                            else:
                                lCg = listCG()
                                for existCg in lCg:
                                    if mc.getAttr(existCg+'.treeName') == newCg:
                                        newCg = existCg
                                        if not mc.referenceQuery(cg, inr=True):
                                            newCg = lib_controlGroup.renameCg(cg, newName)
                                            #self.rnCgClbkInc = 0
                            if mc.objExists(newCg):
                                mc.lockNode(newCg, lock=False)
                                mc.setAttr(newCg+'.treeName', newName, type='string')
                                mc.lockNode(newCg, lock=True)
                        else:
                            mc.warning(newName, 'already exists')
                            self.loadCgInTree(self.name)
                else:
                    mc.warning('the name is empty or have less than 3 caraters ("cg_" included in the caracters count)')
                    self.loadCgInTree(self.name)


    def dADropClbk(self, *args):
        #item = self.itemSel
        #newFather = mc.treeView(self.name, q=True, ip=self.itemSel)
        newFather = args[3]
        lItems = args[0]
        for item in lItems:
            if item != newFather:
                parentCgTo(self.itemSel, newFather)
                print item, 'parented to', newFather
            elif item == newFather:
                self.loadCgInTree(self.name)


    def loadItemsInTree(self, dicItems):
        mc.treeView(self.name, e=True, ra=True)
        for i in range(0, len(dicItems.keys())):
            for father in dicItems[i].keys():
                if father == 'Master':
                    for item in dicItems[i][father]:
                        mc.treeView(self.name, e=True, ai=(item, ''))
                else:
                    for item in dicItems[i][father]:
                        mc.treeView(self.name, e=True, ai=(item, father))
    #loadItemsInTree({0:{'Master':['toto', 'tutu']}, 1:{'toto':['kiki', 'kuku'], 'tutu':['papa', 'mama']}})



    def treePopUp(self):
        mc.popupMenu(self.popUp, p=self.name)
        mc.menuItem(l='add sel as TPL', p=self.popUp, c='tools_smab_v3.addTplToCg(mc.ls(sl=True))')
        mc.menuItem(l='add sel as CTRL', p=self.popUp, c='tools_smab_v3.addCtrlToCg(mc.ls(sl=True))')
        mc.menuItem(divider=True)
  