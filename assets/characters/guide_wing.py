import maya.cmds as mc
import math
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_rigPreset as libRgPreset
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes, lib_constraints
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world,rig_world
from ellipse_rig.assets.asset_base import guide_info


reload(gloss)
reload(libRig)
reload(libRgPreset)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)
reload(lib_constraints)
reload(guide_info)


guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig
guide_info.Info()  # instance class charGuide and run method createRig



class Wing(guide_info.Info):

    def __init__(self,name='wing',side='',selObj=None,numb=1,numbSk=1,nbFeathersbyLine=[10,5,8],offsetIk=(0,4,0),offsetT=(0,6.5,0),offsetR=(0,0,0), incVal=None, **kwargs):

        if len(mc.ls(sl=True)) == 0:
            pass
        else:
            # INSPECT IF INFO PART EXIST________________________________________
            if mc.objExists(mc.ls(sl=True)[0] + ".infPart") is False:
                mc.warning('please select object with info part and module arm only !!!!!')
            else:
                # INSPECT SCENE________________________________________
                objScene = mc.ls(tr=True)
                # GET TPL INFO_________________________________________
                getInfo = mc.getAttr(mc.ls(sl=True)[0] + ".infPart")
                #side = (mc.attributeQuery("update",node=getInfo, listEnum=1)[0]).split(":")[1]
                #side = mc.getAttr(getInfo+'.side')
                self.dataNode = guide_info.Info.__init__(self,name=name,side=side,selObj=selObj)
                self.getInfo = getInfo
                self.arm = 'arm'
                self.name = name
                self.feather = 'feather'
                self.side = side
                self.offsetIk = offsetIk
                self.offsetFatherIk = (0,3,0)
                self.sizeMast = (1.7,0.3,1.7)
                self.sizeMastFeather = (0.3,0.1,0.3)
                self.sizeIkFeather = (0.3,0.3,0.3)
                self.sizeIk = (1.2,1.2,1.2)
                self.sizeCtr = (1,1,1)
                self.sizeSk = (1.2,1.2,1.2)
                self.typeSk = (0.3,0.3,0.3)
                self.offsetMasterTr = offsetT
                self.offsetMasterRo = offsetR
                self.typeShapeMast = 'cube'
                self.incVal = incVal
                self.selObj = mc.ls(sl=True)
                self.selTypeFkArm = 'triangle'
                self.selTypeFk = 'roll'
                self.selTypeFkAdd = 'cube'
                self.nbFeathersbyLine = nbFeathersbyLine
                self.numb = 1
                self.numbSk = 1
                color = lib_shapes.side_color(side=side)
                self.valColorCtr = color["colorCtr"]
                self.valColorCtrIK = color["colorIk"]
                self.valColorMasterCtr = color["colorMaster"]
                self.typeShapeMast = 'circle'
                self.shpRotMaster = (0,0,0)

    def createWing(self):
        if len(mc.ls(sl=True)) != 0: # check if objRef is empty
            # TEMPLATE INFO INCREMENTATION_________________________________________
            dic = guide_info.Info.infoInc(self)
            # GET TPL INFO_________________________________________
            getType = mc.getAttr(self.getInfo + ".moduleType")
            # INSPECT IF INFO PART IS ARM__________________________
            if getType != 'arm':
                mc.warning('please select arm member to generate guide wing!!!!!')
            else:
                tplArm = self.getInfo
                mc.connectAttr(tplArm+'.children', dic['infoName']+'.parent')
                #dic = {}
                # GET INFO TO CREATE RIG____________________________________________________________________________________
                incPart = mc.getAttr(tplArm+'.incInfo')
                #side = (mc.attributeQuery("update",node=tplArm, listEnum=1)[0]).split(":")[1]
                if self.side == 'empty': self.side =''
                color = lib_shapes.side_color(side=self.side)
                sizeIk = (mc.attributeQuery("sizeSk",node=tplArm, listEnum=1)[0]).split(":")[0]
                numbPart = (mc.attributeQuery("sizeSk",node=tplArm, listEnum=1)[0]).split(":")[4]
                lsTplIk =[mc.getAttr(tplArm+'.ik[%s]'%i) for i in range(mc.getAttr(tplArm+'.ik', mi=True,s=True))]
                lsTplCtr =[mc.getAttr(tplArm+'.ctr[%s]'%i) for i in range(mc.getAttr(tplArm+'.ctr', mi=True,s=True))]
                nbSudvArm =[mc.getAttr(tplArm+'.infoNumbMb[0]') for i in range(mc.getAttr(tplArm+'.infoNumbMb[0]', mi=True,s=True))][0]
                lsTplFinger =[mc.getAttr(tplArm+'.endMb[%s]'%i) for i in range(mc.getAttr(tplArm+'.endMb[0]', mi=True,s=True))]
                lsToWing = lsTplCtr
                lsToWing.insert(0,lsTplIk[0])
                lsToWing.append(lsTplIk[-1])
                dicTplEndMb ={}
                if mc.getAttr(tplArm+'.endMb[0]') != "0":
                    for i in range(mc.getAttr(tplArm+'.endMb', mi=True,s=True)):
                        endMb = mc.getAttr(tplArm+'.endMb[%s]'%i).replace(" ", "")
                        splitNlsTplEndMb = endMb[1:-1].split(",")
                        lsTplEndMb =[each[1:-1] for each in splitNlsTplEndMb]
                        dicTplEndMb["%s"%(i+1)]= lsTplEndMb

                    lsToWing.append(dicTplEndMb['1'][0])
                    lsToWing.append(dicTplEndMb['1'][-1])
                # GET SCALE WORLD__________________________
                valInfo = mc.getAttr(self.nWorld+ '.scale')[0][0]
                val = 1
                # GET TEMPORARY SCALE WORLD BY 1__________________________
                mc.setAttr(self.nWorld+ '.scaleX',1)
                mc.setAttr(self.nWorld+ '.scaleY',1)
                mc.setAttr(self.nWorld+ '.scaleZ',1)

                ############################################  SYST WING  ##########################################################
                # NAME________________________________________________________________
                nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=incPart)
                if mc.objExists(nRIG) is True:
                    mc.parent(dic['infoName'],nRIG)
                else:
                    RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
                # CREATE GROUP TO BASE SYSTEM_______________________________
                lsGrpWing =[]
                lsBufWing =[]
                for i, each in enumerate(lsToWing):
                    nGrpsWing = gloss.name_format(prefix=gloss.lexicon('tplRig'), name=self.name,nFunc="base"+"%s"%(i+1),nSide=self.side, incP=incPart)
                    grpsWing = libRig.createObj(partial(mc.group, **{'n':nGrpsWing, 'em': True}),match=[each],father=None)
                    nBufWing = gloss.name_format(prefix=gloss.lexicon('tplBuf'), name=self.name,nFunc="base"+"%s"%(i+1),nSide=self.side, incP=incPart)
                    bufWing = libRig.createObj(partial(mc.group, **{'n':nBufWing, 'em': True}),match=[grpsWing],father=grpsWing)
                    mc.parentConstraint(each,grpsWing)
                    mc.scaleConstraint(each,grpsWing)
                    mc.parent(grpsWing,nRIG)
                    lsGrpWing.append(grpsWing)
                    lsBufWing.append(bufWing)

                # CREATE MASTER_______________________________
                nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=incPart)
                hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG,attributs={"visibility": 0})
                nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=incPart)
                master = libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast], color=self.valColorMasterCtr,
                size=self.sizeMast, rotShp=self.shpRotMaster),match=None, attrInfo=dic['infoName'], father=hookMaster,
                attributs={"drawStyle": 2}, worldScale=None)

                # CREATE CTR_______________________________
                rotOrdFk = libRgPreset.configAxis(mb="rOrdArm")["rOrdFk"]
                lsCtrIkArm = []
                lsRootIkArm = []
                lsCtrIk = []
                lsIkSk = []
                lsbaseSk = []
                for i, each in enumerate(lsBufWing):
                    nCtrBase = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc="baseArm"+"%s"%(i+1),nSide=self.side,incP=incPart)
                    ctrBase = libRig.createController(name=nCtrBase,shape=libRig.Shp([self.selTypeFkArm],color=self.valColorCtrIK,size=(4*val,1*val,3*val),rotShp=(0,-90,0)),
                                                match=[each],attrInfo=dic['infoName'], father=each,attributs={"drawStyle": 2})

                    nCtr = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc="back"+"%s"%(i+1),nSide=self.side,incP=incPart)
                    ctr = libRig.createController(name=nCtr,shape=libRig.Shp([self.selTypeFk],color=self.valColorCtrIK,size=(0.5*val,0.5*val,0.5*val)),
                                                match=[each],attrInfo=dic['infoName'], father=ctrBase['c'],attributs={"drawStyle": 2})
                    mc.move(0,0,-4*val,ctr['root'],ls=True)
                    mc.select(cl=True)
                    nSkBase = gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.name,nFunc="base"+"%s"%(i+1),nSide=self.side,incP=incPart)
                    skBase = libRig.createObj(partial(mc.joint, **{'n': nSkBase}), match=[each], father=each,
                                attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    lsCtrIkArm.append(ctrBase['c'])
                    lsRootIkArm.append(ctrBase['root'])
                    lsCtrIk.append(ctr['c'])
                    lsIkSk.append(ctr['sk'])
                    lsbaseSk.append(skBase)

                # GRP TO LOFT___________________________________________
                nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.name, nSide=self.side,incP=incPart)
                surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=self.getInfo)

                # CREATE NUMBER LINE FEATHER_______________________________
                nbLine = int(len(self.nbFeathersbyLine))
                dicCtrAddBase ={}
                dicCtrAddBack ={}
                dicFeatherLinesBase ={}
                dicFeatherLinesBack ={}
                dicFeatherLinesAim ={}
                dicFeatherLinesCtrArm ={}
                dicFeatherLinesCtrBack ={}
                ##########################################################################
                for i,eachLine in enumerate(self.nbFeathersbyLine):
                    # CTR ADD ARM BY LINE____________
                    lsSkAddArm = []
                    lsCtrAddArm = []
                    for j, each in enumerate(lsBufWing):
                        nCtrAddArm = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc="Arm"+"%s"%(j+1)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        ctrAddArm = libRig.createController(name=nCtrAddArm,shape=libRig.Shp([self.selTypeFkAdd],color=self.valColorCtr,size=(0.1*val,0.1*val,0.1*val)),
                                                    match=[each],attrInfo=dic['infoName'], father=lsRootIkArm[j],attributs={"drawStyle": 2})
                        shape = mc.listRelatives(ctrAddArm['c'], s=True)[0]
                        mc.setAttr(shape + ".overrideEnabled", True)
                        mc.setAttr(shape + '.overrideRGBColors', 1)
                        if self.side == 'L':
                            mc.setAttr(shape + '.overrideColorRGB', 1, (float(i)/5), (float(i)/5))
                            mc.move(-(round(((i)-(float(nbLine/2)))/float(nbLine-0.5),2))*val,0,0,ctrAddArm['root'],ls=True)
                        else:
                            mc.setAttr(shape + '.overrideColorRGB', (float(i)/5), (float(i)/5),1)
                            mc.move((round(((i)-(float(nbLine/2)))/float(nbLine-0.5),2))*val,0,0,ctrAddArm['root'],ls=True)
                        lsSkAddArm.append(ctrAddArm['sk'])
                        lsCtrAddArm.append(ctrAddArm['c'])
                    # CTR ADD BACK BY LINE____________
                    lsSkAdd = []
                    lsCtrAddback = []
                    for j, each in enumerate(lsCtrIk):
                        nCtrAdd = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc="back"+"%s"%(j+1)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        ctrAdd = libRig.createController(name=nCtrAdd,shape=libRig.Shp([self.selTypeFkAdd],color=self.valColorCtr,size=(0.1*val,0.1*val,0.1*val)),
                                                    match=[each],attrInfo=dic['infoName'], father=each,attributs={"drawStyle": 2})
                        shape = mc.listRelatives(ctrAdd['c'], s=True)[0]
                        mc.setAttr(shape + ".overrideEnabled", True)
                        mc.setAttr(shape + '.overrideRGBColors', 1)
                        if self.side == 'L':
                            mc.setAttr(shape + '.overrideColorRGB', 1, (float(i)/5), (float(i)/5))
                            mc.move(-(round(((i)-(float(nbLine/2)))/float(nbLine-0.5),2))*val,0,0,ctrAdd['root'],ls=True)
                        else:
                            mc.setAttr(shape + '.overrideColorRGB', (float(i)/5), (float(i)/5),1)
                            mc.move((round(((i)-(float(nbLine/2)))/float(nbLine-0.5),2))*val,0,0,ctrAdd['root'],ls=True)
                        lsSkAdd.append(ctrAdd['sk'])
                        lsCtrAddback.append(ctrAdd['c'])
                    # LOFT ARM___________________________________________
                    getCrv = lib_curves.createDoubleCrv(objLst=lsSkAddArm, axis='X', offset=0.2)
                    nLoftArm = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name,nFunc='arm'+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                    loftArm = lib_curves.createLoft(name=nLoftArm, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True,degree=None)
                    skinLoftBase = mc.skinCluster(lsSkAddArm,loftArm,tsb=1,mi=1)
                    # Adjust loft weight
                    lib_curves.weightLoft(nLoft=nLoftArm,lsSk=lsSkAddArm,nbSubDv=0,skinLoft=skinLoftBase)

                    # LOFTS BACK___________________________________________
                    getCrv = lib_curves.createDoubleCrv(objLst=lsSkAdd, axis='X', offset=0.2)
                    nLoftBack = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name,nFunc='back'+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                    loftBack = lib_curves.createLoft(name=nLoftBack, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True,degree=None)
                    skinLoftBack = mc.skinCluster(lsSkAdd,loftBack,tsb=1,mi=1)
                    # Adjust loft weight
                    lib_curves.weightLoft(nLoft=nLoftBack,lsSk=lsSkAdd,nbSubDv=0,skinLoft=skinLoftBack)

                    dicCtrAddBase['tplAddCtr%s'%(int(i)+1)] = lsCtrAddArm
                    dicCtrAddBack['tplAddCtr%s'%(int(i)+1)] = lsCtrAddback

                    # CREATE SA LINES_______________________
                    lSaArm = lib_connectNodes.surfAttach(selObj=[loftArm], lNumb=eachLine, parentInSA=True, parentSA=surfAttach,delKnot=True)
                    lSaBack = lib_connectNodes.surfAttach(selObj=[loftBack], lNumb=eachLine, parentInSA=True, parentSA=surfAttach,delKnot=True)
                    count = 1

                    lsBaseLine = []
                    lsBackLine = []
                    lsAimLine = []
                    for eachFeather in range(int(eachLine)):
                        # ADJ LOC BASE FEATHER_______________________
                        newNLocBase =  gloss.name_format(prefix=gloss.lexicon('tplUv'),name=self.name,nFunc="base"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        locBase = mc.rename(lSaArm['loc'][eachFeather],newNLocBase)
                        newNSaBase =  gloss.name_format(prefix=gloss.lexicon('tplSa'),name=self.name,nFunc="base"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        saBase = mc.rename(lSaArm['sa'][eachFeather],newNSaBase)
                        # ADJ LOC BACK FEATHER_______________________
                        newNLocBack =  gloss.name_format(prefix=gloss.lexicon('tplUv'),name=self.name,nFunc="back"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        locBack = mc.rename(lSaBack['loc'][eachFeather],newNLocBack)
                        newNSaBack =  gloss.name_format(prefix=gloss.lexicon('tplSa'),name=self.name,nFunc="back"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side,incP=incPart)
                        saBack = mc.rename(lSaBack['sa'][eachFeather],newNSaBack)
                        # ADJ LOC COLOR_______________________
                        shape = mc.listRelatives(locBase, s=True)[0]
                        shape2 = mc.listRelatives(locBack, s=True)[0]
                        lsLoc = [locBase,locBack]
                        for k, each in enumerate([shape,shape2]):
                            mc.setAttr(each + ".overrideEnabled", True)
                            mc.setAttr(each + '.overrideRGBColors', 1)
                            if self.side == 'L':
                                mc.setAttr(each + '.overrideColorRGB', 1, (float(i)/5), (float(i)/5))
                            else:
                                mc.setAttr(each + '.overrideColorRGB', (float(i)/5), (float(i)/5), 1)
                            mc.setAttr(lsLoc[k]+'.visibility',1)
                            mc.setAttr(lsLoc[k]+'.localScaleX',0.2*valInfo)
                            mc.setAttr(lsLoc[k]+'.localScaleY',0.2*valInfo)
                            mc.setAttr(lsLoc[k]+'.localScaleZ',0.2*valInfo)
                        # CONNECT U LOCBASE TO LOCBACK_______________________
                        mc.connectAttr(locBase + '.U',locBack + '.U')
                        # SET INFO NAME TO LOC_______________________
                        update = mc.attributeQuery("update",node=dic['infoName'], listEnum=1)[0]
                        mc.addAttr(newNLocBase, ln='infPart', dt="string")
                        mc.setAttr(newNLocBase + '.infPart',dic['infoName'], type="string")
                        mc.addAttr(newNLocBack, ln='infPart', dt="string")
                        mc.setAttr(newNLocBack + '.infPart',dic['infoName'], type="string")
                        # add attributs symetrie
                        update = mc.attributeQuery("update",node=dic['infoName'], listEnum=1)[0]
                        nSym = "empty"
                        test = newNLocBase.split("_")
                        if update.split(":")[1] == 'L':
                            test[-1]='R'
                            nSym = "_".join(test)
                        elif update.split(":")[1] == 'R':
                            test[-1]='L'
                            nSym = "_".join(test)
                        mc.addAttr(newNLocBase, ln='symPart', dt="string")
                        mc.setAttr(newNLocBase + '.symPart', nSym, type="string")
                        mc.addAttr(newNLocBack, ln='symPart', dt="string")
                        mc.setAttr(newNLocBack + '.symPart', nSym, type="string")
                        # AIM CONSTRAINT TO FEATHER_______________________
                        nAimFeather = gloss.name_format(prefix=gloss.lexicon('tplBuf'), name=self.name,nFunc="feather"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side, incP=incPart)
                        aimFeather = libRig.createObj(partial(mc.group, **{'n':nAimFeather, 'em': True}),match=[locBase],father=locBase)
                        nUpVFeather = gloss.name_format(prefix=gloss.lexicon('tplUpV'), name=self.name,nFunc="feather"+"%s"%(count)+"Part%s"%(i+1),nSide=self.side, incP=incPart)
                        upVFeather = libRig.createObj(partial(mc.group, **{'n':nUpVFeather, 'em': True}),match=[locBase],father=locBase)
                        if self.side == 'L':
                            mc.move(0,0,-(1*valInfo),upVFeather,ls=True)
                            aim= (0.0,1.0,0.0)
                            upV= (0.0,0.0,1.0)
                        else:
                            mc.move(0,0,(1*valInfo),upVFeather,ls=True)
                            aim= (0.0,1.0,0.0)
                            upV= (0.0,0.0,-1.0)
                        aimCns = mc.aimConstraint(locBack,aimFeather, aim=aim, u=upV, wut='object', wuo=upVFeather)
                        if self.side == 'R':
                            mc.setAttr(aimCns[0]+'.offsetY',180)
                        else:
                            pass
                        count += 1
                        lsBaseLine.append(str(locBase))
                        lsBackLine.append(str(locBack))
                        lsAimLine.append(str(aimFeather))
                    dicFeatherLinesBase['tplFeatherLinesBase%s'%(int(i)+1)] = lsBaseLine
                    dicFeatherLinesBack['tplFeatherLinesBack%s'%(int(i)+1)] = lsBackLine
                    dicFeatherLinesAim['tplFeatherLinesAim%s'%(int(i)+1)] = lsAimLine
                    dicFeatherLinesCtrArm['tplLineCtrArm%s'%(int(i)+1)] = lsCtrAddArm
                    dicFeatherLinesCtrBack['tplLinesCtrBack%s'%(int(i)+1)] = lsCtrAddback

                # PARENT INFO AND TPL RIG_________________________________________
                mc.parent(dic['infoName'],nRIG)
                mc.parent(nRIG,self.nWorldGrp)

                # GET SCALE WORLD SET __________________________
                mc.setAttr(self.nWorld+ '.scaleX',valInfo)
                mc.setAttr(self.nWorld+ '.scaleY',valInfo)
                mc.setAttr(self.nWorld+ '.scaleZ',valInfo)

                # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
                mc.addAttr(dic['infoName'], ln='delPart', dt='string', multi=True)  # add master control
                mc.setAttr(dic['infoName'] + '.delPart[0]', nRIG, type='string')
                mc.addAttr(dic['infoName'], ln='subDvArm', dt='string', multi=True)  # add master control
                mc.setAttr(dic['infoName'] + '.subDvArm[0]',nbSudvArm, type='string')
                mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
                mc.addAttr(dic['infoName'], ln='sizeSk', at="enum",
                           en="%s:%s:%s:%s:%s:%s" % (self.sizeCtr, self.sizeSk, self.typeSk,
                                                     self.offsetIk, self.numb, self.numbSk), k=True, p='infoSK')
                mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)
                mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')), dt='string',
                           multi=True)  # add master control
                mc.setAttr(dic['infoName'] + ".%s[0]" % gloss.lexiconAttr('masterTpl'), nMaster, type='string')
                mc.addAttr(dic['infoName'], ln='ik', dt='string', multi=True)  # add IK control
                [mc.setAttr(dic['infoName'] + '.ik['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrIk)]
                mc.addAttr(dic['infoName'], ln='ikBase', dt='string', multi=True)  # add IK control
                [mc.setAttr(dic['infoName'] + '.ikBase['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrIkArm)]

                mc.addAttr(dic['infoName'], shortName='ctrBase',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicCtrAddBase.items()):
                    mc.setAttr(dic['infoName']+'.ctrBase[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='ctr',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicCtrAddBack.items()):
                    mc.setAttr(dic['infoName']+'.ctr[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='featherLinesBase',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicFeatherLinesBase.items()):
                    mc.setAttr(dic['infoName']+'.featherLinesBase[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='featherLinesBack',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicFeatherLinesBack.items()):
                    mc.setAttr(dic['infoName']+'.featherLinesBack[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='featherLinesAim',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicFeatherLinesAim.items()):
                    mc.setAttr(dic['infoName']+'.featherLinesAim[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='lineCtrArm',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicFeatherLinesCtrArm.items()):
                    mc.setAttr(dic['infoName']+'.lineCtrArm[%s'%str(count)+']',value,type='string')
                    count += 1

                mc.addAttr(dic['infoName'], shortName='lineCtrBack',dt='string',multi=True)
                count = 0
                for key,value in sorted(dicFeatherLinesCtrBack.items()):
                    mc.setAttr(dic['infoName']+'.lineCtrBack[%s'%str(count)+']',value,type='string')
                    count += 1


                # add ik in sym attributes
                if self.side is not '':
                    mc.setAttr(dic['infoName'] + '.sym[' + str(1) + ']', nMaster, type='string')
                    lenSym = mc.getAttr(dic['infoName'] + '.sym', mi=True, s=True)
                    [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrIk)]
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrIkArm)]
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    for key,value in sorted(dicCtrAddBase.items()):
                        lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                        [mc.setAttr(dic['infoName']+'.sym['+str(lenSym+i)+']',each,type='string') for i,each in enumerate(value)]

                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    for key,value in sorted(dicCtrAddBack.items()):
                        lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                        [mc.setAttr(dic['infoName']+'.sym['+str(lenSym+i)+']',each,type='string') for i,each in enumerate(value)]


                    '''
                    [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrPath)]
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(concatCtrMidIk)]
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsCtr)]
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',rigAdd['c'],type='string')

                    '''

                #dic['loft'] = loft
                dic['master'] = nMaster
                dic['lsIk'] = lsCtrIk
                #dic['lsCtr'] = lsCtr
                #dic['lsSk'] = lsSk
            return dic

        else:
            mc.warning('please select object of part member !!!!!')

