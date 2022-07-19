# coding: utf-8

import maya.cmds as mc
import math
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world
from ellipse_rig.assets.asset_base import guide_info
reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)
reload(guide_info)

guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig
guide_info.Info()  # instance class charGuide and run method createRig


class Book(guide_info.Info):

    def __init__(self,name='book',side='',selObj=None,obj=mc.ls(sl=True),numb=5,numbSk=16,sizeMast=(2,2,2),shpRotMaster=(0,0,0),
                 shpRotCtr=(90,90,0),sizeCtr=(1,1,1),typeShpMst="circle",**kwargs):
        guide_info.Info.__init__(self,name=name,side=side,selObj=selObj)
        self.selObj = selObj
        self.obj = obj
        self.typeShapeMast = typeShpMst
        self.typeShapeMastSheet = "crossLine"
        self.typeShapeMastBookCover = "cube"
        color= lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.valColorCtrMidIK = 'green'
        self.sheet ='sheet'
        self.numbSheet = 20
        self.numbIk = 2
        self.numbPath = 5
        self.numb = numb
        self.numbCtr = 10
        self.numbSk = 20
        self.offsetIk = (0,0,-5)
        self.typeShapeIkPath2 = "square"
        self.typeShapeIk = "cube"
        self.typeShapeCtr = "crossLine"
        self.offsetCtr =(0,0,-1)
        self.sizeMast = sizeMast
        self.sizeMastBookCover = (0.5,0.5,0.5)
        self.sizeMastSheet = (1,1,1)
        self.sizeIk = (0.3,0.3,0.3)
        self.sizeIkKnot = (0.4,0.4,0.4)
        self.sizeCtrPath = (0.3,0.3,0.3)
        self.sizeMidIk = (0.15,0.15,0.15)
        self.sizeCtr = (0.3,0.3,0.3)
        self.sizeSk = (0.1,0.1,0.1)
        self.typeSk = (0.3,0.3,0.3)
        self.sizeRigAdd = (0.5,0.5,0.5)
        self.shpRotMaster = shpRotMaster
        self.shpRotIk = (90,0,0)
        self.shpRotCtrPath = (0,0,0)
        self.shpRotCtr = shpRotCtr
        self.rigAdd = "rigAdd"
        self.Ctr = "square"



    def createBook(self):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = guide_info.Info.infoInc(self)
        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nRoot1 = gloss.name_format(prefix=gloss.lexicon('tplRoot'),name=self.name,nFunc='cv'+str(1), nSide=self.side,incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=dic['incVal'])
        nRigAdd = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=gloss.lexicon('add'), nSide=self.side,incP=dic['incVal'])
        nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=dic['incVal'])
        # GET PARENT HOOK ELEMENT__________________________________________________________
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly +".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0]+'.infPart')+".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)

        # CREATE IK___________________________________________________________
        if mc.objExists(nRIG) is True:
            mc.parent(dic['infoName'],nRIG)
        else:
            RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
            surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
            hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
            master = libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast], color=self.valColorMasterCtr,
            size=self.sizeMast, rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
            attributs={"drawStyle": 2}, worldScale=self.nWorld)
            root1 = libRig.createObj(partial(mc.group, **{'n': nRoot1, 'em': True}), father=master['root'],attrInfo=dic['infoName'])
            '''
            rigAdd = libRig.createController(name=nRigAdd, shape=libRig.Shp([self.rigAdd], color=self.valColorCtr,
            size=self.sizeRigAdd,rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
            attributs={"drawStyle": 2}, worldScale=self.nWorld)
            mc.setAttr(rigAdd['root'] + '.segmentScaleCompensate', 0)
            '''
            sclWorld = float(mc.getAttr(self.nWorld + '.scaleX'))

            # Create BookCover__________________________________________________________________
            lsDwnBook =[]
            lsDwnBookKnot =[]
            lsUpBook =[]
            lsBookCover =[]
            lsBookBack =[]
            for each in range(2):
                nMasterDwnBook = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name+'Up'+str(each+1), nFunc=gloss.lexicon('mtr'),
                                            nSide=self.side, incP=dic['incVal'])
                masterDwnBook = libRig.createController(name=nMasterDwnBook,shape=libRig.Shp([self.typeShapeMastBookCover], color=self.valColorCtrIK,
                size=self.sizeMastBookCover, rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,attributs={"drawStyle": 2}, worldScale=self.nWorld)
                nMasterUpBook= gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name+'Back'+str(each+1), nFunc=gloss.lexicon('mtr'),
                                            nSide=self.side, incP=dic['incVal'])
                masterUpBook = libRig.createController(name=nMasterUpBook,shape=libRig.Shp([self.typeShapeMastBookCover], color=self.valColorCtrIK,
                size=self.sizeMastBookCover, rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=masterDwnBook['c'],attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0,8.5,0, masterUpBook['root'], ls=True)

                nIkSheetKnot = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.sheet + 'knot' + str(each + 1), nSide=self.side,incP=dic['incVal'])
                IkSheetKnot = libRig.createController(name=nIkSheetKnot,shape=libRig.Shp([self.typeShapeIk], color=self.valColorCtrIK,size=self.sizeIkKnot, rotShp=self.shpRotIk),match=self.selObj, attrInfo=dic['infoName'],
                father=masterDwnBook['c'], attributs={"drawStyle": 2},worldScale=self.nWorld)

                if each == 0:
                    mc.move(-2,0,0, masterDwnBook['root'], ls=True)
                    lsBookCover.append(masterDwnBook['sk'])
                    lsBookCover.append(masterUpBook['sk'])
                else:
                    mc.move(2,0,0, masterDwnBook['root'], ls=True)
                    lsBookBack.append(masterDwnBook['sk'])
                    lsBookBack.append(masterUpBook['sk'])

                lsDwnBookKnot.append(IkSheetKnot['sk'])
                lsDwnBook.append(masterDwnBook['sk'])
                lsUpBook.append(masterUpBook['sk'])
            # CREATE CURVE AND LOFT BOOK COVER___________________________________________
            getCrv = lib_curves.createDoubleCrv(objLst=lsDwnBookKnot, axis='Z', offset=0.2)
            nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name+'Dwn', nSide=self.side,incP=dic['incVal'])
            loftDwn = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsDwnBookKnot,loftDwn,tsb=1,mi=1)

            getCrv = lib_curves.createDoubleCrv(objLst=lsUpBook, axis='Z', offset=0.2)
            nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name+'Up', nSide=self.side,incP=dic['incVal'])
            loftUp = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsUpBook,loftUp,tsb=1,mi=1)

            getCrv = lib_curves.createDoubleCrv(objLst=lsBookCover, axis='Z', offset=0.5)
            nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name+'Cover', nSide=self.side,incP=dic['incVal'])
            loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsBookCover,loft,tsb=1,mi=1)
            mc.setAttr(loft+'.visibility',1)
            mc.setAttr(loft+'.overrideEnabled',1)
            mc.setAttr(loft+'.overrideDisplayType',2)

            getCrv = lib_curves.createDoubleCrv(objLst=lsBookBack, axis='Z', offset=0.5)
            nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name+'Back', nSide=self.side,incP=dic['incVal'])
            loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsBookBack,loft,tsb=1,mi=1)
            mc.setAttr(loft+'.visibility',1)
            mc.setAttr(loft+'.overrideEnabled',1)
            mc.setAttr(loft+'.overrideDisplayType',2)

            getCrv = lib_curves.createDoubleCrv(objLst=lsDwnBook, axis='Z', offset=0.5)
            nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name+'Bot', nSide=self.side,incP=dic['incVal'])
            loftBottom = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsDwnBook,loftBottom,tsb=1,mi=1)
            mc.setAttr(loftBottom+'.visibility',1)
            mc.setAttr(loftBottom+'.overrideEnabled',1)
            mc.setAttr(loftBottom+'.overrideDisplayType',2)

            # CREATE GRP SA___________________________________________________
            nSAWorldGrp = gloss.name_format(prefix=gloss.lexicon('tplSA') + 'World', name=self.name, nSide=self.side,incP=dic['incVal'])
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nSide=self.side,incP=dic['incVal'])
            if mc.attributeQuery("tplSAWorld", node=master['c'], ex=True) is True:
                pass
            else:
                SAWorld = libRig.createObj(partial(mc.group, **{'n': nSAWorldGrp, 'em': True}), father=surfAttach,attrInfo=dic['infoName'], refObj=self.selObj)
                SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), father=SAWorld,refObj=self.selObj)
                mc.addAttr(master['c'], ln='tplSAWorld', dt="string")
                mc.setAttr(master['c'] + '.tplSAWorld', nSAWorldGrp, type="string")
                mc.addAttr(master['c'], ln='tplSA', dt="string")
                mc.setAttr(master['c'] + '.tplSA', nSAGrp, type="string")
            # CREATE ATTRIBUTES UPDATE TO SA WORLD____________________________
            lib_attributes.attrUpdateCtr(selObj=nSAWorldGrp, name=self.name, side=self.side)
            # PARENT INFO AND TPL RIG_________________________________________
            mc.parent(dic['infoName'],nRIG)
            mc.parent(nRIG,self.nWorldGrp)
            # CONNECT TO WORLD________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=self.nFly, slave=hookMaster)


            # Create Sheets__________________________________________________________________
            dicSheet ={}
            lsMasterSheet =[]
            for numbSheet in range(self.numbSheet):
                # Create master sheets__________________________________________________________________
                nMasterSheet = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.sheet+str(numbSheet+1), nFunc=gloss.lexicon('mtr'),
                                            nSide=self.side, incP=dic['incVal'])
                mastersheet = libRig.createController(name=nMasterSheet,shape=libRig.Shp([self.typeShapeMastSheet], color=self.valColorMasterCtr,
                size=self.sizeMastSheet, rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                lsMasterSheet.append(mastersheet['root'])
                # Create IkMid__________________________________________________________________
                lsRootCtr = []
                lsCtr = []
                lsCtrIk = []
                lsRootIkMid = []
                lsRootIk =[]
                lsSkIk = []
                lsIkKnotSk = []
                lsIkSkMid = []
                valMoveMidIk = [0,round((float(8) / float(self.numb - 1)), 3),0]
                for numb in range(self.numb):
                    incValMove = ((numb * valMoveMidIk[0]), (numb * valMoveMidIk[1]), (numb * valMoveMidIk[2]))
                    ''' names '''
                    nRopeMidIk = gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.sheet+str(numbSheet+1),nFunc='part',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                    ''' create '''
                    skPart = libRig.createObj(partial(mc.joint, **{'n': nRopeMidIk}), shape=libRig.Shp([self.typeShapeCtr],size=self.sizeSk),
                    father=None, refObj=self.selObj, attributs={"drawStyle": 2})
                    mc.move(0,incValMove[1],0, skPart, ls=True)
                    mc.parent(skPart, mastersheet['c'])
                    mc.setAttr(mc.listRelatives(skPart, s=True)[0] + '.overrideEnabled', 1)
                    mc.setAttr(mc.listRelatives(skPart, s=True)[0] + '.overrideDisplayType', 2)
                    # add ctr IK
                    if numb == 0 or numb == 1 or numb == (self.numb - 1):
                        ''' names '''
                        nIk = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name+str(numbSheet+1),nFunc='part',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                        ''' create '''
                        ik = libRig.createController(name=nIk,shape=libRig.Shp([self.typeShapeIk], color=self.valColorMasterCtr,
                        size=self.sizeIk, rotShp=self.shpRotIk),match=self.selObj, attrInfo=dic['infoName'], father=mastersheet['c'],
                        attributs={"drawStyle": 2}, worldScale=self.nWorld)
                        mc.move(0,incValMove[1],0, ik['root'], ls=True)
                        if numb == 0 or numb == (self.numb - 1):
                            lsIkKnotSk.append(ik['sk'])
                        elif numb == 1:
                            lsRootIkMid.append(ik['root'])
                            lsIkSkMid.append(ik['sk'])
                            # CREATE SK TO CURVE BASE________________________________
                            incVal = 1
                            lsAddSk =[]
                            for count in range(3):
                                nSkBase = gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.sheet+'add' + str(numbSheet + 1), nFunc='part',
                                                               inc=str(count + 1), nSide=self.side, incP=dic['incVal'])
                                skBase = libRig.createObj(partial(mc.joint, **{'n':nSkBase}),shape=libRig.Shp([self.typeShapeCtr],
                                size=self.sizeSk), father=None,refObj=self.selObj, attributs={"drawStyle": 2})
                                mc.move(0,0.5*incVal, 0, skBase, ls=True)
                                mc.parent(skBase,mastersheet['c'])
                                mc.setAttr(mc.listRelatives(skBase, s=True)[0] + '.overrideEnabled', 1)
                                mc.setAttr(mc.listRelatives(skBase, s=True)[0] + '.overrideDisplayType', 2)
                                incVal += 1
                        # ROOT SEGMENT SCALE COMPENSATE________________________________
                        mc.setAttr(ik['root']+'.segmentScaleCompensate',0)
                        # DISCONNECT ATTRIBUTES CONNECTION______________________________
                        connectPairs = []
                        connect = mc.listConnections(mc.getAttr(ik['c'] + ".sk"), plugs=True, connections=True, destination=False)
                        connectPairs.extend(zip(connect[1::2], connect[::2]))
                        [mc.disconnectAttr(srcAttr, desAttr) for srcAttr, desAttr in connectPairs]
                        mc.parent(ik['sk'],ik['c'])
                        mc.parent(skPart,ik['c'])
                        lsCtrIk.append(ik['c'])
                        lsSkIk.append(ik['sk'])
                    lsCtr.append(skPart)
                    lsRootCtr.append(skPart)

                # CREATE CURVE TO IK SHEET___________________________________________
                getCrv = lib_curves.createDoubleCrv(objLst=lsIkKnotSk, axis='Z', offset=0.2)
                nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.sheet,nFunc='part',inc=str(numbSheet+1), nSide=self.side,
                                          incP=dic['incVal'])
                loftSheet = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
                mc.skinCluster(lsIkKnotSk, loftSheet, tsb=1, mi=1)
                # SA TO IK MID___________________________________________
                lsSaIkMid = [lib_connectNodes.nurbs_attach(lsObj=[loftSheet, each], parentInSA=True, delLoc=True, parentSA=nSAGrp)for i, each in enumerate(lsRootIkMid)]
                lsSaIkMidRename = [gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True)for each in lsSaIkMid]


                # CREATE CURVE TO CTR SHEET___________________________________________
                getCrv = lib_curves.createDoubleCrv(objLst=lsSkIk, axis='Z', offset=0.2)
                nLoftSk = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.sheet+'Sk',nFunc='part',inc=str(numbSheet+1), nSide=self.side,
                                          incP=dic['incVal'])
                loftSheetSk = lib_curves.createLoft(name=nLoftSk, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
                mc.skinCluster(lsSkIk, loftSheetSk, tsb=1, mi=1)
                # SA TO CTR___________________________________________
                #lsSaSk = [lib_connectNodes.nurbs_attach(lsObj=[loftSheet, each], parentInSA=True, delLoc=True, parentSA=nSAGrp)for i, each in enumerate(lsRootIkMid)]
                #lsSaSkRename = [gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True)for each in lsSaSk]



                # DIC___________________________________________
                dicSheet['%s%s'%(self.name,int(numbSheet)+1)] = lsRootCtr
                # SHEET PLACEMENT___________________________________________
                number = int(self.numbSheet)
                if self.numbSheet %2 ==0:
                    mc.move(((round(((numbSheet+0.5)-(float(number/2)))/float(number+0.333),2))*sclWorld)*4,0,0,mastersheet['root'],ls=True)
                else:
                    mc.move(((round(((numbSheet)-(float(number/2)))/float(number-1),2))*sclWorld)*4,0,0,mastersheet['root'],ls=True)

            # CREATE SA___________________________________________________
            # CONNECT TO LOFT DOWN AND IK SHEET_________________________________________________
            lsSaCtr =[lib_connectNodes.nurbs_attach(lsObj=[loftDwn,each], parentInSA=True, delLoc=True, parentSA=nSAGrp) for i,each in enumerate(lsMasterSheet)]
            lsSaCtrRename =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True) for each in lsSaCtr]


            """

            # Import de la librairie sys
            import sys
            import maya.cmds as mc
            import maya.mel as mel
            # Définition du chemin des scripts
            pathCustom ='Z:\JOB\Maya_work\scripts_pycharm_work'
            
            # Si le chemin n'est pas déjà configuré
            if not pathCustom in sys.path:
                # On l'ajoute
                sys.path.append(pathCustom)
            # Import du module et définition d'un nom d'appel
            
            # Refresh du module
            
            
            #GUIDE
            from ellipse_rig.assets.props.book import guide_book
            reload(guide_book)
            guide = guide_book.Book(name='book',side='') # instance class charGuide
            guide.createBook()
            
            
            
            
            # Create Ctr Path__________________________________________________________________
            valMoveCtrPath= [0, 0,round((float(8 - 1) / float(self.numbPath - 1)), 3)]
            lsCtrPath = []
            lsRootPath = []
            for numb in range(self.numbPath):
                incValMovePath = (((numb) * valMoveCtrPath[0]), ((numb) * valMoveCtrPath[1]), ((numb) * valMoveCtrPath[2]))
                nCtrPath = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc='path',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                ctrPath = libRig.createController(name=nCtrPath,shape=libRig.Shp([self.typeShapeIkPath2], color=self.valColorMasterCtr,
                size=self.sizeCtrPath, rotShp=self.shpRotCtrPath),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0, 0,incValMovePath[2]-3.5, ctrPath ['root'], ls=True)
                lsCtrPath.append(ctrPath['c'])
                lsRootPath.append(ctrPath['root'])

            # CREATE CURVE AND LOFT___________________________________________
            getCrv = lib_curves.createDoubleCrv(objLst=lsIkSk, axis='Z', offset=0.2)
            loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsIkSk,loft,tsb=1,mi=1)
            # PARENT INFO AND TPL RIG_________________________________________
            mc.parent(dic['infoName'],nRIG)
            mc.parent(nRIG,self.nWorldGrp)
            # CONNECT TO WORLD________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=self.nFly, slave=hookMaster)
            # CREATE SA___________________________________________________
            # NAME _______________________________________________________________
            nSAWorldGrp = gloss.name_format(prefix=gloss.lexicon('tplSA') + 'World', name=self.name, nSide=self.side,incP=dic['incVal'])
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nSide=self.side, incP=dic['incVal'])
           # CREATE GRP SA___________________________________________________
            if mc.attributeQuery("tplSAWorld", node=master['c'], ex=True) is True:
                pass
            else:
                SAWorld = libRig.createObj(partial(mc.group, **{'n': nSAWorldGrp, 'em': True}), father=surfAttach,attrInfo=dic['infoName'], refObj=self.selObj)
                SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), father=SAWorld,refObj=self.selObj)
                mc.addAttr(master['c'], ln='tplSAWorld', dt="string")
                mc.setAttr(master['c'] + '.tplSAWorld', nSAWorldGrp, type="string")
                mc.addAttr(master['c'], ln='tplSA', dt="string")
                mc.setAttr(master['c'] + '.tplSA', nSAGrp, type="string")
            # CREATE ATTRIBUTES UPDATE TO SA WORLD____________________________
            lib_attributes.attrUpdateCtr(selObj=nSAWorldGrp, name=self.name, side=self.side)
            # CONNECT TO LOFT CTR PATH_________________________________________________
            lsSaCtr =[lib_connectNodes.nurbs_attach(lsObj=[loft,each], parentInSA=True, delLoc=True, parentSA=nSAGrp) for i,each in enumerate(lsRootPath)]
            lsSaCtrRename =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True) for each in lsSaCtr]
            mc.parent(lsRootPath[0],lsCtrIk[0])
            mc.parent(lsRootPath[-1],lsCtrIk[-1])
            # CONNECT TO LOFT_________________________________________________
            lSa = lib_connectNodes.surfAttach(selObj=[loft], lNumb=self.numb-2, parentInSA=True, parentSA=nSAGrp,delKnot=True)
            [mc.parent(lsRootMidIk[1:-1][i],each) for i,each in enumerate(lSa['sa'])]
            # CONNECT TO MASTER CONTROL_______________________________________
            lib_connectNodes.connectMatrixAxis(driver=master['c'], slave=SA)

            # Create Ctr__________________________________________________________________
            lsCtr = []
            lsRootCtr = []
            valMove = [0, 0,round((float(8 - 1) / float(self.numbCtr - 1)), 3)]
            for numb in range(self.numbCtr):
                incValMove = ((numb * valMove[0]), (numb * valMove[1]), (numb * valMove[2]))
                ''' names '''
                nRope = gloss.name_format(prefix=gloss.lexicon('tplCtr'),name=self.name,inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                skPart= libRig.createController(name=nRope,shape=libRig.Shp([self.typeShapeCtr], color=self.valColorCtrMidIK,
                size=self.sizeCtr, rotShp=self.shpRotCtr),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0, 0, incValMove[2]-3.5, skPart['root'], ls=True)
                lsCtr.append(skPart['c'])
                lsRootCtr.append(skPart['root'])

            # CREATE CURVE AND LOFT2_______________________________________________
            nLoft2 = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name, nFunc='ctr',nSide=self.side, incP=dic['incVal'])
            val = float(mc.getAttr(self.nWorld + '.scaleX'))
            concatSkMidIk = [mc.getAttr(each +'.sk') for each in lsCtr]
            concatSkMidIk.insert(0,mc.getAttr(lsKnot[0] +'.sk'))
            concatSkMidIk.append(mc.getAttr(lsKnot[-1] +'.sk'))
            getCrv = lib_curves.createDoubleCrv(objLst=concatSkMidIk, axis='Z', offset=0.1 * val,degree=1)
            loft2 = lib_curves.createLoft(name=nLoft2, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True
                                         , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
            mc.skinCluster(concatSkMidIk, loft2, tsb=1, mi=1)
            mc.setAttr(nLoft2+".overrideShading", 0)
            # CREATE ATTRIBUTES UPDATE TO LOFT _____________________________________
            mc.addAttr(nLoft2, ln='infPart', dt="string")
            mc.setAttr(nLoft2 + '.infPart', dic['infoName'], type="string")
            mc.addAttr(nLoft2, ln='updateSk', dt="string")
            mc.setAttr(nLoft2+ '.updateSk', 'partToDel', type="string")
            # CREATE SA___________________________________________________
            # CONNECT TO LOFT_________________________________________________
            for each in enumerate(lsRootCtr):
                if each[1] == lsRootCtr[0]:
                    mc.parent(each[1],lsCtr[0])
                elif each[1] == lsRootCtr[-1]:
                    mc.parent(each[1],lsCtr[-1])
                else:
                    saCtr =lib_connectNodes.nurbs_attach(lsObj=[loft2,each[1]], parentInSA=True, delLoc=True, parentSA=nSAGrp)
                    saCtrRename =gloss.renameSplit(selObj=saCtr[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True)
            # Create SK__________________________________________________________________
            lsSk = []
            valMove = [0, 0,round((float(8 - 1) / float(self.numbSk - 1)), 3)]
            for numb in range(self.numbSk):
                incValMove = ((numb * valMove[0]), (numb * valMove[1]), (numb * valMove[2]))
                ''' names '''
                nSk = gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.name,nFunc='sk',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                sk =libRig.createObj(partial(mc.joint, **{'n':nSk}),match=self.selObj,father=hookMaster,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                mc.move(0, 0, incValMove[2]-3.5, sk, ls=True)
                lsSk.append(sk)
            lSaSk =[lib_connectNodes.nurbs_attach(lsObj=[loft2,each[1]], parentInSA=True, delLoc=True, parentSA=nSAGrp)for each in enumerate(lsSk)]
            lsSaRename =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True) for each in lSaSk]

            #parent rigAdd
            mc.parent(rigAdd['root'],lsCtrIk[-1])


            # ADJUST POSITION RIGADD___________________________________________________
            getPos = mc.xform(lsCtrIk[-1], q=True, ws=True, translation=True)
            getRot = mc.xform(lsCtrIk[-1], q=True, ws=True, rotation=True)
            mc.xform(rigAdd['root'], worldSpace=True, t=getPos)
            mc.xform(rigAdd['root'], worldSpace=True, ro=getRot)
            mc.setAttr(rigAdd['root']+'.translateY',2.5)

            # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
            mc.addAttr(dic['infoName'], ln='delPart', dt='string', multi=True)  # add master control
            mc.setAttr(dic['infoName'] + '.delPart[0]', nRIG, type='string')
            mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
            mc.addAttr(dic['infoName'], ln='sizeSk', at="enum",
                       en="%s:%s:%s:%s:%s:%s" % (self.sizeCtr, self.sizeSk, self.typeSk,
                                                 self.offsetIk, self.numb, self.numbSk), k=True, p='infoSK')
            mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)
            mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')), dt='string',
                       multi=True)  # add master control
            mc.setAttr(dic['infoName'] + ".%s[0]" % gloss.lexiconAttr('masterTpl'), nMaster, type='string')
            mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('rigAddTpl')),dt='string',multi=True) # add master control
            mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('rigAddTpl'),rigAdd['c'],type='string')
            mc.addAttr(dic['infoName'], ln='ik', dt='string', multi=True)  # add IK control
            [mc.setAttr(dic['infoName'] + '.ik['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrIk)]
            mc.addAttr(dic['infoName'], shortName='ctrPath',dt='string',multi=True)
            [mc.setAttr(dic['infoName'] + '.ctrPath['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrPath)]
            mc.addAttr(dic['infoName'], shortName='ctrMidIk',dt='string',multi=True)
            concatCtrMidIk = lsCtr
            concatCtrMidIk.insert(0, lsKnot[0])
            concatCtrMidIk.append(lsKnot[-1])
            [mc.setAttr(dic['infoName']+'.ctrMidIk['+str(i)+']',each,type='string') for i, each in enumerate(concatCtrMidIk)]
            mc.addAttr(dic['infoName'], shortName='ctr',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.ctr['+str(i)+']',each,type='string') for i, each in enumerate(lsCtr)]
            mc.addAttr(dic['infoName'], shortName='sk',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.sk['+str(i)+']',each,type='string') for i, each in enumerate(lsSk)]
            # add ik in sym attributes
            if self.side is not '':
                # nSym = lib_attributes.attrSymetrie(selObj=nMaster, nameInfo=dic['infoName'])
                mc.setAttr(dic['infoName'] + '.sym[' + str(1) + ']', nMaster, type='string')
                lenSym = mc.getAttr(dic['infoName'] + '.sym', mi=True, s=True)
                [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrIk)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrPath)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(concatCtrMidIk)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsCtr)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',rigAdd['c'],type='string')

            dic['loft'] = loft
            dic['master'] = nMaster
            dic['lsCtrPath'] = lsCtrPath
            dic['lsCtr'] = concatCtrMidIk
            dic['lsCtr'] = lsCtr
            dic['lsSk'] = lsSk
            return dic
            
            """