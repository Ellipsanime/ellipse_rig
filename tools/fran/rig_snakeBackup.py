# coding: utf-8

import maya.cmds as mc
import math
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_rigPreset as libRgPreset
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world,rig_world
from ellipse_rig.assets.characters import guide_base

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
reload(guide_base)
reload(rig_world)
rig_world.RigWorld().createRig()  # instance class charGuide and run method createRig

class Snake(rig_world.RigWorld):

    def __init__(self, name='snake',side='', tplInfo='tplInfo', hook = '',*args):
        rig_world.RigWorld.__init__(self)
        self.hook =hook
        self.name = name
        self.info = tplInfo
        self.typeArrow = "arrowQuadro2"
        self.typeCircle = "circle"
        self.shpRotIk = (0,45,0)
        self.rigAdd = "rigAdd"
        self.typeShapeIkPath = "arrowSingle2"
        self.typeShapeIkPath2 = "square"
        self.typeShapeIk = "square"
        self.typeShapeCtr = "circle"
        self.CtrSlide = "sphere"
        color= lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.nbCtr = 8
        worldScl = mc.getAttr("tpl_WORLD"+".scaleX")
        self.shpSizeIk = (0.7*worldScl,0.7*worldScl,0.7*worldScl)
        self.shpSizeIkMid = (0.5*worldScl,0.5*worldScl,0.5*worldScl)
        self.valScl = float(mc.getAttr("tpl_WORLD" + ".scaleX"))

    def createSnake(self):
        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        # CREATE RIG TO LISTE INFO_________________________________
        dicBuf = {}
        dicSk = {}
        lCtrl = []
        for i, eachTpl in enumerate(lsInfo):
            # GET INFO TO CREATE RIG________________________________
            incPart = mc.getAttr(eachTpl+'.incInfo')
            side = (mc.attributeQuery("update",node=eachTpl, listEnum=1)[0]).split(":")[1]
            if side == 'empty': side =''
            master = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('masterTpl'))
            rigAddTpl = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('rigAddTpl'))
            lsTplIk =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]
            lsTplCtrPath =[mc.getAttr(eachTpl+'.ctrPath[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctrPath', mi=True,s=True))]
            lsTplMidIk =[mc.getAttr(eachTpl+'.ctrMidIk[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctrMidIk', mi=True,s=True))]
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            lsTplSk =[mc.getAttr(eachTpl+'.sk[%s]'%i) for i in range(mc.getAttr(eachTpl+'.sk', mi=True,s=True))]

            # CREATE RIG ADD____________________
            nRigAdd = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('add'), nSide=side,incP=incPart)
            rigAdd =libRig.createController(name=nRigAdd,shape=libRig.Shp([self.rigAdd],color='blue',size=(1,1,1),
            rotShp=(0,0,0)),match=rigAddTpl,father=self.nLocFly,attributs={"drawStyle": 2})
            lib_shapes.matchShpCv(shpRef=rigAddTpl, shpTarget=rigAdd['c'])
            # NAME________________________________________________________________
            nHook = gloss.name_format(prefix=gloss.lexicon('hook'),name=self.name, nSide=side,incP=incPart)
            nRig = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name,nSide=side,incP=incPart)
            nGlobalCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('cog'),nSide=side,incP=incPart)
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('SA'), name=self.name, nFunc=gloss.lexicon('loft') + 'Cv',nSide=side, incP=incPart)
            # HOOK________________________________________________________________
            hook =libRig.createObj(partial(mc.joint, **{'n':nHook}),match=None,father=self.nRig,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            lib_connectNodes.connectMatrixAxis(driver=self.nLocFly, slave=hook)
            # RIG________________________________________________________________
            rig = libRig.createObj(partial(mc.group, **{'n': nRig, 'em': True}), Match=self.nFly,father=hook)
            # COG___________________________________________________________________
            globalCtr = libRig.createController(name=nGlobalCtr,shape=libRig.Shp([self.typeCircle],color=self.valColorMasterCtr,size=(3,3,3)),match=master,father=rig)
            mc.setAttr(globalCtr["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            # MATCH CVS WITH TPL CV__________________________
            lib_shapes.matchShpCv(shpRef=master, shpTarget=globalCtr['c'])
            # CREATE GRP SA ______________________________________________________
            sAGrp = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), Match=None, father=self.nSa)

            ###################################### PATH SYSTEM #########################################################
            # CONTROLS IK PATH___________________________________________________________________
            lsSkIkPath = []
            lsIkPath = []
            lsRootIkPath = []
            for i, each in enumerate(lsTplIk):
                nIkPath = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name+'IkPath', nFunc=str(i + 1), nSide=side,incP=incPart)
                ikPath = libRig.createController(name=nIkPath, shape=libRig.Shp([self.typeShapeIkPath], color='red', size=self.shpSizeIkMid),match=each, father=globalCtr['c'])
                mc.setAttr(ikPath['root'] + '.segmentScaleCompensate', 0)
                lsSkIkPath.append(ikPath['sk'])
                lsIkPath.append(ikPath['c'])
                lsRootIkPath.append(ikPath['root'])
                # MATCH CVS WITH TPL CV__________________________
                lib_shapes.matchShpCv(shpRef=each, shpTarget=ikPath['c'])

            # CONTROLS PATH___________________________________________________________________
            lsSkCtrPath = []
            lsCtrPath = []
            lsRootCtrPath = []
            lsClusterPath = []
            for i, each in enumerate(lsTplCtrPath):
                nCtrPath = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name+'Path', nFunc=str(i + 1), nSide=side,incP=incPart)
                ctrPath = libRig.createController(name=nCtrPath, shape=libRig.Shp([self.typeShapeIkPath2], color='red', size=self.shpSizeIkMid),match=each, father=globalCtr['c'])
                mc.setAttr(ctrPath['root'] + '.segmentScaleCompensate', 0)
                lsSkCtrPath.append(ctrPath['sk'])
                lsCtrPath.append(ctrPath['c'])
                lsRootCtrPath.append(ctrPath['root'])
                # MATCH CVS WITH TPL CV__________________________
                lib_shapes.matchShpCv(shpRef=each, shpTarget=ctrPath['c'])
                # CREATE CLUSTERS_________________
                nClusterPath = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name,
                                                   nFunc='path' + str(i + 1), nSide=side, incP=incPart)
                clusterPath = mc.createNode("cluster", n=nClusterPath)
                nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'), name=self.name,
                                                   nFunc='path' + str(i + 1), nSide=side, incP=incPart)
                mltMatCluster = mc.createNode("multMatrix", n=nMltMatCluster)
                mc.connectAttr(ctrPath['c'] + '.worldMatrix[0]', mltMatCluster + '.matrixIn[0]')
                mc.connectAttr(ctrPath['root'] + '.worldInverseMatrix[0]', mltMatCluster + '.matrixIn[1]')
                mc.connectAttr(mltMatCluster + '.matrixSum', clusterPath + '.weightedMatrix')
                mc.connectAttr(ctrPath['c'] + '.worldMatrix[0]', clusterPath + '.matrix')
                mc.connectAttr(ctrPath['root'] + '.worldInverseMatrix[0]', clusterPath + '.bindPreMatrix')
                mc.connectAttr(ctrPath['root'] + '.worldMatrix[0]', clusterPath + '.preMatrix')
                lsClusterPath.append(clusterPath)

            # CREATE CURVE AND LOFT_______________________________________________
            # NAME _______________________________________________________________
            nLoftBase = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='ctrPath',nSide=side, incP=incPart)
            getCrvPath = lib_curves.createDoubleCrv(objLst=lsTplCtrPath, axis='X', offset=0.2 * self.valScl)
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            lsCv = []
            numbSubDv = 3
            for i, each in enumerate(getCrvPath['crv']):
                createCrv = lib_curves.crvSubdivide(crv=each, subDiv=numbSubDv, subDivKnot=0, degree=3)
                nCv = mc.rename(each, gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
                nFunc=gloss.lexicon('base') + str(i + 1), nSide=side,incP=incPart))
                mc.setAttr(nCv+ ".visibility", 0)
                lsCv.append(nCv)
            # skin crvs______________________________________
            lsSkCrv = []
            for i, each in enumerate(lsCv):
                skinCrv = mc.skinCluster(lsSkIkPath, each, tsb=1, mi=1)
                lsSkCrv.append(skinCrv)
            # dic to param points _______________________________
            listCv1 = mc.ls(lsCv[0] + '.cv[*]', fl=True)
            listCv2 = mc.ls(lsCv[1] + '.cv[*]', fl=True)
            adjNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(listCv1))/adjNumb))
            val = 0
            val2 = 0
            dictPartCv1= {}
            dictPartCv2= {}
            for each2 in range(selDiv2):
                lsPartCv1 =[]
                lsPartCv2 =[]
                for each in range(adjNumb):
                    lsPartCv1.append(listCv1[each+val+val2])
                    lsPartCv2.append(listCv2[each+val+val2])
                val += adjNumb
                val2 -=1
                dictPartCv1[each2] = lsPartCv1
                dictPartCv2[each2] = lsPartCv2
            # get values Skin___________________________
            #nbByPart = numbSubDv+2
            nbByPart = len(listCv1)
            count = 0
            getValCrv = []
            for each in range(nbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getValCrv.append(val)
            invertValCrv = getValCrv[::-1]
            # MODIFY SKIN VALUES CRVS_________________________________________________
            for i, eachPoint in enumerate(listCv1):
                mc.skinPercent(lsSkCrv[0][0], eachPoint, r=False, normalize=True,
                               transformValue=[(lsSkIkPath[0], invertValCrv[i]), (lsSkIkPath[1], getValCrv[i])])
            for i, eachPoint in enumerate(listCv2):
                mc.skinPercent(lsSkCrv[1][0], eachPoint, r=False, normalize=True,
                               transformValue=[(lsSkIkPath[0], invertValCrv[i]), (lsSkIkPath[1], getValCrv[i])])
            # create loftBase____________________________________________
            loftCtrPath = libRig.createObj(partial(mc.loft, lsCv[0], lsCv[1:], **{'n': nLoftBase, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
            'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,refObj=None, incPart=False, attributs={"visibility": 0})
            # CREATE SA CTR____________________________________________
            [lib_connectNodes.nurbs_attach(lsObj=[loftCtrPath,each[1]], parentInSA=True, delLoc=True,parentSA=sAGrp) for each in enumerate(lsRootCtrPath[1:-1])]
            mc.parent(lsRootCtrPath[0],lsIkPath[0])
            mc.parent(lsRootCtrPath[-1],lsIkPath[-1])

            # CREATE SYSTEM PATH SPLINE________________________________________________
            # CREATE CV PATH______________________________________________
            nSwitchsRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nCvPath = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nSide=side,incP=incPart)
            nNoTouch = gloss.name_format(prefix=gloss.lexicon('NoTouch'),name=self.name,nSide=side,incP=incPart)
            # CREATE SWITCH_______________________________________________________
            createSwitchs = mc.createNode("nurbsCurve", n=nSwitchsCtr)
            father = mc.listRelatives(createSwitchs, p=True)
            rootSwitchs = mc.rename(father, nSwitchsRoot)
            # parentage switch Attrib
            mc.parent(rootSwitchs, self.nSwitch)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="stretch_Option", at="enum", en="_________")
            mc.setAttr(nSwitchsCtr + ".stretch_Option", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="stretch", at="double", min=0, max=10, dv=10)
            mc.setAttr(nSwitchsCtr + ".stretch", e=True, k=True)
            # HIDE DEFAULT ATTRIBUTES ____________________________________________
            lib_attributes.hide_ctrl_hist(selObj=nSwitchsRoot)
            crvIkSpline = lib_curves.createDoubleCrv(objLst=lsTplCtrPath, axis='X', offset=0 * self.valScl)
            mc.delete(crvIkSpline['crv'][1])
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            numbSubDv = 3
            createCrvIkSpline = lib_curves.crvSubdivide(crv=crvIkSpline['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvIkSpline = mc.rename(crvIkSpline['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='IkPath' + str(1), nSide=side,incP=incPart))
            mc.setAttr(nCvIkSpline+ ".visibility", 1)
            mc.setAttr(nCvIkSpline+ ".template", 1)
            # skin crvs______________________________________
            #skinCrvIkSpline = mc.skinCluster(lsSkCtrPath,nCvIkSpline, tsb=1, mi=1)
            skinCrvIkSpline = mc.skinCluster(lsSkIkPath,nCvIkSpline, tsb=1, mi=1)
            # dic to param points _______________________________
            listCv1 = mc.ls(nCvIkSpline + '.cv[*]', fl=True)
            adjNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(listCv1))/adjNumb))
            val = 0
            val2 = 0
            dictPartCv1= {}
            dictPartCv1Invert= {}
            for each2 in range(selDiv2):
                lsPartCv1 =[]
                lsPartCvInv1 =[]
                for each in range(adjNumb):
                    lsPartCv1.append(listCv1[each+val+val2])
                    test =listCv1[::-1]
                    lsPartCvInv1.append(test[each+val+val2])
                val += adjNumb
                val2 -=1
                dictPartCv1[each2] = lsPartCv1
                dictPartCv1Invert[each2] = lsPartCvInv1
            # get values Skin___________________________
            numbByPart = numbSubDv+2
            nbByPart = numbSubDv+2
            count = 0
            getVal = []
            for each in range(numbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]
            # MODIFY SKIN VALUES CRVS_________________________________________________
            '''
            for i, each in enumerate(sorted(dictPartCv1.items())):
                for j, eachPart in enumerate(dictPartCv1.values()[i]):
                    mc.skinPercent(skinCrvIkSpline[0],eachPart, r=False,
                                   transformValue=[(lsSkCtrPath[i], invertVal[j]),(lsSkCtrPath[i+1], getVal[j])])
            '''
            for i, eachPoint in enumerate(listCv1):
                mc.skinPercent(skinCrvIkSpline[0], eachPoint, r=False, normalize=True,
                               transformValue=[(lsSkIkPath[0], invertValCrv[i]), (lsSkIkPath[1], getValCrv[i])])
            for i, each in enumerate(sorted(dictPartCv1.items())):
                for j, eachPoint in enumerate(dictPartCv1.values()[i]):
                    mc.deformer(lsClusterPath[i], e=True, g=eachPoint)
                    mc.percent(lsClusterPath[i], eachPoint, value=invertVal[j])
            lsClusterPathInv = lsClusterPath[::-1]
            for i, each in enumerate(sorted(dictPartCv1Invert.items())):
                for j, eachPoint in enumerate(dictPartCv1Invert.values()[i]):
                    mc.deformer(lsClusterPathInv[i], e=True, g=eachPoint)
                    mc.percent(lsClusterPathInv[i], eachPoint, value=invertVal[j])


            # CREATE BUF PATH AND SK PATH______________________________________________
            lsBufPath = []
            lsBufSkPath = []
            lsSkbend = []
            for i, each in enumerate(lsTplMidIk[1:-1]):
                # NAME_________________________________________________________
                nBufPath  = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name,nFunc='path'+str(i+1), nSide=side,incP=incPart)
                nSkPath = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name,nFunc='pathBuf'+str(i+1), nSide=side,incP=incPart)
                bufPath  = libRig.createObj(partial(mc.joint, **{'n': nBufPath}), match=[each],father=None,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                skPath  = libRig.createObj(partial(mc.joint, **{'n': nSkPath}), match=[each],father=bufPath,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                lsBufPath.append(bufPath)
                lsBufSkPath.append(skPath)
                # create system to skin shape bend
                if each == lsTplMidIk[1:-1][0] or each == lsTplMidIk[1:-1][-1]:
                    nBufBend  = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name,nFunc='bend'+str(i+1), nSide=side,incP=incPart)
                    nSkBend  = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name,nFunc='bend'+str(i+1), nSide=side,incP=incPart)
                    bufBend  = libRig.createObj(partial(mc.joint, **{'n': nBufBend}), match=[each],father=gloss.lexicon('world')+'Center',attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                    skBend  = libRig.createObj(partial(mc.joint, **{'n': nSkBend}), match=[each],father=bufBend,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                    lsSkbend.append(skBend)
            [mc.parent(each,lsBufPath[i])for i, each in enumerate(lsBufPath[1:])]
            # CREATE GRP NO TOUCH________________________________________________
            GrpNoTouch = libRig.createObj(partial(mc.group, **{'n': nNoTouch, 'em': True}),typeFunction={"group": {"visibility": 0}})
            # parentage group NoTouch avec HookSpine
            mc.parent(GrpNoTouch,self.nRig)
            # NAME_________________________________________________________
            nIkHandlePath = gloss.name_format(prefix=gloss.lexicon('ikHandle'),name=self.name,nFunc='path'+str(1), nSide=side,incP=incPart)
            nIkHandlePathRoot = gloss.name_format(prefix=gloss.lexicon('rootIkHandle'),name=self.name,nFunc='path'+str(1), nSide=side,incP=incPart)
            nGrpJts = gloss.name_format(prefix=gloss.lexicon('rootJt'),name=self.name,nFunc='path'+str(1), nSide=side,incP=incPart)
            # CREATE IK HANDLE_______________________________________________
            ikHandlePath = libRig.createObj(partial(mc.ikHandle, **{'n': nIkHandlePath, 'sj': lsBufPath[0],'ee': lsBufPath[-1],
                            'sol': 'ikSplineSolver','c': nCvIkSpline, 'fj': False, 'ccv': False,'scv': True}),
                            attributs={"poleVectorY": 1,"poleVectorZ": 0,"snapEnable": 0,"visibility": 0})
            grpIkHandlePath = libRig.createObj(partial(mc.group, **{'n': nIkHandlePathRoot, 'em': True}),match=[ikHandlePath],childLst=[ikHandlePath])
            # PARENT CURVE WITH HOOK SPINE___________________________________
            mc.select(cl=True)
            jntBufBase = libRig.createObj(partial(mc.joint, **{'n':nGrpJts}),match=lsTplIk[0], father=globalCtr['c'],
            attributs={"rotateOrder": 3,"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"segmentScaleCompensate": 0,
                       "inheritsTransform": 1,"drawStyle": 2,"visibility": 1})
            mc.parent(lsBufPath[0],jntBufBase)
            mc.setAttr(lsBufPath[0] + ".jointOrientX", 0)
            mc.setAttr(lsBufPath[0] + ".jointOrientY", 0)
            mc.setAttr(lsBufPath[0] + ".jointOrientZ", 0)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="path_Option", at="enum", en="_________")
            mc.setAttr(nSwitchsCtr + ".path_Option", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln='visPath', at="enum",en="off:on", k=True)
            mc.setAttr(nSwitchsCtr + '.visPath', e=True, cb=True)
            shpCvPath = mc.listRelatives(nCvIkSpline, shapes=True)[0]
            valmaxU = (mc.getAttr(shpCvPath + ".maxValue"))
            mc.addAttr(nSwitchsCtr, ln="path", at="double", min=0, max=valmaxU, dv=0)
            mc.setAttr(nSwitchsCtr + ".path", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="rollPath", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".rollPath", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="twistPath", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".twistPath", e=True, k=True)
            # CONNECT ATTRIBUTES SWITCH____________________________________________
            mc.connectAttr(nSwitchsCtr + '.path',ikHandlePath+ '.offset')
            mc.connectAttr(nSwitchsCtr + '.rollPath',ikHandlePath+ '.roll')
            mc.connectAttr(nSwitchsCtr + '.twistPath',ikHandlePath+ '.twist')
            # ADD SWITCH TO IK CTR_________________________________________________
            mc.parent(nSwitchsCtr,rigAdd['c'], s=True, add=True)

            # CREATE LOFT DRIVING BY BUF PATH ______________________________________________
            crvLoftBuf = lib_curves.createDoubleCrv(objLst=lsBufPath, axis='Z', offset=0.2 * self.valScl)
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            numbSubDv = 3
            createCrvSpline1 = lib_curves.crvSubdivide(crv=crvLoftBuf['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCrvLoftBuf1 = mc.rename(crvLoftBuf['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='SplineIK'+ str(1), nSide=side,incP=incPart))
            mc.setAttr(nCrvLoftBuf1+ ".visibility", 1)
            createCrvSpline2 = lib_curves.crvSubdivide(crv=crvLoftBuf['crv'][1], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCrvLoftBuf2 = mc.rename(crvLoftBuf['crv'][1], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='SplineIK'+ str(2), nSide=side,incP=incPart))
            mc.setAttr(nCrvLoftBuf2+ ".visibility", 1)
            # create loftBase____________________________________________
            nLoftBuf = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='buf',nSide=side, incP=incPart)
            loftBuf = libRig.createObj(partial(mc.loft,nCrvLoftBuf1,nCrvLoftBuf2, **{'n': nLoftBuf, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
            'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,refObj=None, incPart=False, attributs={"visibility":1})
            # delete Crvs_________________________________________________
            mc.delete(nCrvLoftBuf1)
            mc.delete(nCrvLoftBuf2)
            # Skin loft
            skinLoftBuf = mc.skinCluster(lsBufSkPath, nLoftBuf, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
           # concat points cv by 4 _______________________________
            recCv = mc.ls(nLoftBuf + '.cv[*]', fl=True)
            #recCvSk = mc.ls(nLoftBaseSk + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv)) / adjustNumb))
            val = 0
            lsPoint = []
            for each2 in range(selDiv2):
                part = []
                for each in range(adjustNumb):
                    part.append(recCv[each + val])
                val += adjustNumb
                lsPoint.append(part)
            # dic to param points _______________________________
            adjustNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(lsPoint))/adjustNumb))
            val = 0
            val2 = 0
            dictPart= {}
            for each2 in range(selDiv2):
                lsPart =[]
                for each in range(adjustNumb):
                    lsPart.append(lsPoint[each+val+val2])
                val += adjustNumb
                val2 -=1
                dictPart[each2] = lsPart
            # get values Skin___________________________
            numbByPart = numbSubDv+2
            nbByPart = numbSubDv+2
            count = 0
            getVal = []
            for each in range(numbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]
            # MODIFY SKIN VALUES LOFT CTR_________________________________________________
            for i, each in enumerate(sorted(dictPart.items())):
                for j, eachLigne in enumerate(dictPart.values()[i]):
                    for k, eachPoint in enumerate(eachLigne):
                        mc.skinPercent(skinLoftBuf[0], eachPoint, r=False, transformValue=[(lsBufSkPath[i], invertVal[j]),(lsBufSkPath[i+1], getVal[j])])


            ###################################### SNAKE SYSTEM #########################################################
            # CONTROLS IK SNAKE___________________________________________________________________
            lsSkIk = []
            lsIk= []
            lsRootIk = []
            for i, each in enumerate(lsTplMidIk):
                if each == lsTplMidIk[0] or each == lsTplMidIk[-1]:
                    # create sk
                    nSkIk = gloss.name_format(prefix=gloss.lexicon('sk'), name=self.name+'Ik', nFunc=str(i + 1), nSide=side,incP=incPart)
                    skIk = libRig.createObj(partial(mc.joint, **{'n': nSkIk}), match=[each],father=globalCtr['c'],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                    lsSkIk.append(skIk)
                else:
                    # create controls
                    nIk = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name+'Ik', nFunc=str(i + 1), nSide=side,incP=incPart)
                    ik = libRig.createController(name=nIk, shape=libRig.Shp([self.typeShapeIk], color=self.valColorCtrIK, size=self.shpSizeIkMid),match=each, father=globalCtr['c'])
                    mc.setAttr(ik['root'] + '.segmentScaleCompensate', 0)
                    lsSkIk.append(ik['sk'])
                    lsIk.append(ik['c'])
                    lsRootIk.append(ik['root'])
                    # MATCH CVS WITH TPL CV__________________________
                    lib_shapes.matchShpCv(shpRef=each, shpTarget=ik['c'])
            # parentage IK Controls to bufPaths______________________
            mc.parent(lsSkIk[0],lsIk[0])
            mc.parent(lsSkIk[-1],lsIk[-1])
            # CREATE SA BUF____________________________________________
            saBuf =[lib_connectNodes.nurbs_attach(lsObj=[loftBuf,each[1]], parentInSA=True, delLoc=True,parentSA=sAGrp) for each in enumerate(lsRootIk)]
            # CREATE LOFT TO BEND DEFORM_________________________________________________
            nLoftBend = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='bend',nSide=side, incP=incPart)
            nLoftBendShape = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='bendShape',nSide=side, incP=incPart)
            loftBendDupl = mc.duplicate(loftBuf)[0]
            loftBend =mc.rename(loftBendDupl,nLoftBend)
            mc.blendShape(loftBend,loftBuf,n=nLoftBendShape)
            mc.setAttr(nLoftBendShape+ ".loft_snakeBend_1_%s"%side, 1)
            mc.reorderDeformers(skinLoftBuf[0],nLoftBendShape,loftBuf)
            deformBend = mc.nonLinear(nLoftBend,type='bend')
            mc.setAttr(deformBend[1]+ ".rotateX", -90)
            mc.setAttr(deformBend[0]+ ".lowBound", -2)
            mc.setAttr(deformBend[0]+ ".highBound", 2)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="love_Option", at="enum", en="_________")
            mc.setAttr(nSwitchsCtr + ".love_Option", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="up", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".up", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="curlUp", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".curlUp", e=True, k=True)
            # CONNECT ATTRIBUTES____________________________________________
            mc.connectAttr(nSwitchsCtr + ".up", lsSkbend[-1]+ ".translateY")
            mc.connectAttr(nSwitchsCtr + ".curlUp", deformBend[0]+'.curvature')
            # SKIN LOFT BEND____________________________________________
            lib_attributes.lockAxis(loftBend, trans=True, rot=True, scl=True, axis=('x','y','z'))
            skinLoftBend = mc.skinCluster(lsSkbend,loftBend, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)



            # CREATE CV SPLINE______________________________________________
            crvSpline = lib_curves.createDoubleCrv(objLst=lsTplMidIk, axis='Z', offset=0.2 * self.valScl)
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            numbSubDv = 3
            createCrvSpline1 = lib_curves.crvSubdivide(crv=crvSpline['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvSpline1 = mc.rename(crvSpline['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='Spline'+ str(1), nSide=side,incP=incPart))
            mc.setAttr(nCvSpline1+ ".visibility", 1)
            createCrvSpline2 = lib_curves.crvSubdivide(crv=crvSpline['crv'][1], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvSpline2 = mc.rename(crvSpline['crv'][1], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='Spline'+ str(2), nSide=side,incP=incPart))
            mc.setAttr(nCvSpline2+ ".visibility", 1)
            # create loftBase____________________________________________
            nLoftCtr = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='ctr',nSide=side, incP=incPart)
            loftCtr = libRig.createObj(partial(mc.loft,nCvSpline1,nCvSpline2, **{'n': nLoftCtr, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
            'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,refObj=None, incPart=False, attributs={"visibility":1})
            # delete Crvs_________________________________________________
            mc.delete(nCvSpline1)
            mc.delete(nCvSpline2)
            # Skin loft
            skinLoft = mc.skinCluster(lsSkIk, nLoftCtr, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
           # concat points cv by 4 _______________________________
            recCv = mc.ls(nLoftCtr + '.cv[*]', fl=True)
            #recCvSk = mc.ls(nLoftBaseSk + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv)) / adjustNumb))
            val = 0
            lsPoint = []
            for each2 in range(selDiv2):
                part = []
                for each in range(adjustNumb):
                    part.append(recCv[each + val])
                val += adjustNumb
                lsPoint.append(part)
            # dic to param points _______________________________
            adjustNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(lsPoint))/adjustNumb))
            val = 0
            val2 = 0
            dictPart= {}
            for each2 in range(selDiv2):
                lsPart =[]
                for each in range(adjustNumb):
                    lsPart.append(lsPoint[each+val+val2])
                val += adjustNumb
                val2 -=1
                dictPart[each2] = lsPart
            # get values Skin___________________________
            numbByPart = numbSubDv+2
            nbByPart = numbSubDv+2
            count = 0
            getVal = []
            for each in range(numbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]

            # MODIFY SKIN VALUES LOFT CTR_________________________________________________
            for i, each in enumerate(sorted(dictPart.items())):
                for j, eachLigne in enumerate(dictPart.values()[i]):
                    for k, eachPoint in enumerate(eachLigne):
                        mc.skinPercent(skinLoft[0], eachPoint, r=False, transformValue=[(lsSkIk[i], invertVal[j]),(lsSkIk[i+1], getVal[j])])

            # CREATE LOFT TO SINE DEFORM_________________________________________________
            nLoftSine = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='sine',nSide=side, incP=incPart)
            nLoftShape = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='sineShape',nSide=side, incP=incPart)
            loftSineDupl = mc.duplicate(loftCtr)[0]
            loftSine =mc.rename(loftSineDupl,nLoftSine)
            mc.blendShape(loftSine,loftCtr,n=nLoftShape)
            mc.setAttr(nLoftShape+ ".loft_snakeSine_1_%s"%side, 1)
            mc.reorderDeformers(skinLoft[0],nLoftShape,loftCtr)
            deformSine = mc.nonLinear(nLoftSine,type='sine')
            mc.setAttr(deformSine[1]+ ".rotateX", -90)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="sine_Option", at="enum", en="_________")
            mc.setAttr(nSwitchsCtr + ".sine_Option", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="ampli", at="double", min=-1, max=1, dv=0)
            mc.setAttr(nSwitchsCtr + ".ampli", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="waves", at="double", min=-1, max=10, dv=0.6)
            mc.setAttr(nSwitchsCtr + ".waves", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="move", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".move", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="dropOff", at="double", min=-1, max=1, dv=-0.5)
            mc.setAttr(nSwitchsCtr + ".dropOff", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="frontBound", at="double", min=-1, max=0, dv=-0.75)
            mc.setAttr(nSwitchsCtr + ".frontBound", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="backBound", at="double", min=0, max=1, dv=1)
            mc.setAttr(nSwitchsCtr + ".backBound", e=True, k=True)
            # CONNECT ATTRIBUTES____________________________________________
            mc.connectAttr(nSwitchsCtr + ".ampli", deformSine[0]+'.amplitude')
            mc.connectAttr(nSwitchsCtr + ".waves", deformSine[0]+'.wavelength')
            mc.connectAttr(nSwitchsCtr + ".move", deformSine[0]+'.offset')
            mc.connectAttr(nSwitchsCtr + ".dropOff", deformSine[0]+'.dropoff')
            mc.connectAttr(nSwitchsCtr + ".frontBound", deformSine[0]+'.lowBound')
            mc.connectAttr(nSwitchsCtr + ".backBound", deformSine[0]+'.highBound')


            # CREATE FK CONTROL ______________________________________________
            lsSkCtr = []
            lsCtr = []
            lsRootCtr = []
            lsSkSplineIkH =[]
            lsCnsSplineIkH =[]
            for i, each in enumerate(lsTplCtr):
                nCtr = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name, nFunc='fk'+str(i + 1), nSide=side,incP=incPart)
                ctr = libRig.createController(name=nCtr, shape=libRig.Shp([self.typeShapeCtr], color='green', size=self.shpSizeIkMid),match=each, father=globalCtr['c'])
                mc.setAttr(ctr['root'] + '.segmentScaleCompensate', 0)
                lsSkCtr.append(ctr['sk'])
                lsCtr.append(ctr['c'])
                lsRootCtr.append(ctr['root'])
                # MATCH CVS WITH TPL CV__________________________
                lib_shapes.matchShpCv(shpRef=each, shpTarget=ctr['c'])
                # add sk to ikSplineHandle
                nBufSplineIkHSk = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nFunc='splineSk'+str(i+1), nSide=side,incP=incPart)
                nSkSplineIkHSk  = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name,nFunc='splineSk'+str(i+1), nSide=side,incP=incPart)
                bufSplineIkHSk  = libRig.createObj(partial(mc.joint, **{'n': nBufSplineIkHSk}), match=[each],father=ctr['root'],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                skSplineIkHSk  = libRig.createObj(partial(mc.joint, **{'n': nSkSplineIkHSk}), match=[each],father=bufSplineIkHSk,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                lsSkSplineIkH.append(skSplineIkHSk)
                lsCnsSplineIkH.append(bufSplineIkHSk)

            # CREATE SA CTR____________________________________________
            saCtr = [lib_connectNodes.nurbs_attach(lsObj=[loftCtr,each[1]], parentInSA=True, delLoc=True,parentSA=sAGrp) for each in enumerate(lsRootCtr)]
            for i,each in enumerate(saCtr):
                mc.parent(lsCnsSplineIkH[i],each[0])
            mc.orientConstraint(lsIk[-1], lsCnsSplineIkH[-1],mo=True)

            # CREATE LOFT SK_________________________________________________
            crvSk = lib_curves.createDoubleCrv(objLst=lsTplCtr, axis='Z', offset=0.2 * self.valScl)
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            numbSubDv = 1
            createCrvSpline1 = lib_curves.crvSubdivide(crv=crvSk['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvSk1 = mc.rename(crvSk['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='Sk'+ str(1), nSide=side,incP=incPart))
            mc.setAttr(nCvSk1+ ".visibility", 1)
            createCrvSpline2 = lib_curves.crvSubdivide(crv=crvSk['crv'][1], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvSk2 = mc.rename(crvSk['crv'][1], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='Sk'+ str(2), nSide=side,incP=incPart))
            mc.setAttr(nCvSk2+ ".visibility", 1)
            # create loftSk____________________________________________
            nLoftSk = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='sk',nSide=side, incP=incPart)
            loftSk = libRig.createObj(partial(mc.loft,nCvSk1,nCvSk2, **{'n': nLoftSk, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
            'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,refObj=None, incPart=False, attributs={"visibility":1})
            # delete Crvs_________________________________________________
            mc.delete(nCvSk1)
            mc.delete(nCvSk2)
            # Skin loft
            skinLoft = mc.skinCluster(lsSkCtr,nLoftSk, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
           # concat points cv by 4 _______________________________
            recCv = mc.ls(nLoftSk + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv)) / adjustNumb))
            val = 0
            lsPoint = []
            for each2 in range(selDiv2):
                part = []
                for each in range(adjustNumb):
                    part.append(recCv[each + val])
                val += adjustNumb
                lsPoint.append(part)
            # dic to param points _______________________________
            adjustNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(lsPoint))/adjustNumb))
            val = 0
            val2 = 0
            dictPart= {}
            for each2 in range(selDiv2):
                lsPart =[]
                for each in range(adjustNumb):
                    lsPart.append(lsPoint[each+val+val2])
                val += adjustNumb
                val2 -=1
                dictPart[each2] = lsPart
            # get values Skin___________________________
            numbByPart = numbSubDv+2
            nbByPart = numbSubDv+2
            count = 0
            getVal = []
            for each in range(numbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]

            # MODIFY SKIN VALUES LOFT CTR______________________________
            for i, each in enumerate(sorted(dictPart.items())):
                for j, eachLigne in enumerate(dictPart.values()[i]):
                    for k, eachPoint in enumerate(eachLigne):
                        mc.skinPercent(skinLoft[0], eachPoint, r=False, transformValue=[(lsSkCtr[i], invertVal[j]),(lsSkCtr[i+1], getVal[j])])

            # CREATE LOFT TO FLARE DEFORM_________________________________________________
            nLoftFlare = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='flare',nSide=side, incP=incPart)
            nLoftFlareShape = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='flareShape',nSide=side, incP=incPart)
            loftFlareDupl = mc.duplicate(loftSk)[0]
            loftFlare =mc.rename(loftFlareDupl,nLoftFlare)
            mc.blendShape(loftFlare,loftSk,n=nLoftFlareShape)
            mc.setAttr(nLoftFlareShape+ ".loft_snakeFlare_1_%s"%side, 1)
            mc.reorderDeformers(skinLoft[0],nLoftFlareShape,loftSk)
            deformFlare = mc.nonLinear(nLoftFlare,type='flare')
            mc.setAttr(deformFlare[1]+ ".rotateX", -90)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="puff_Option", at="enum", en="_________")
            mc.setAttr(nSwitchsCtr + ".puff_Option", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="puff", at="double", min=-1, max=10, dv=0)
            mc.setAttr(nSwitchsCtr + ".puff", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="slide", at="double", dv=0)
            mc.setAttr(nSwitchsCtr + ".slide", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="upDown", at="double", dv=0)
            mc.setAttr(nSwitchsCtr + ".upDown", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffFt", at="double", min=-10, max=0, dv=-0.2)
            mc.setAttr(nSwitchsCtr + ".fallOffFt", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffBk", at="double", min=0, max=10, dv=0.2)
            mc.setAttr(nSwitchsCtr + ".fallOffBk", e=True, k=True)
            # CONNECT ATTRIBUTES____________________________________________
            mc.connectAttr(nSwitchsCtr + ".puff", deformFlare[0]+'.curve')
            mc.connectAttr(nSwitchsCtr + ".slide", deformFlare[1]+'.translateZ')
            mc.connectAttr(nSwitchsCtr + ".upDown", deformFlare[1]+'.translateY')
            mc.connectAttr(nSwitchsCtr + ".fallOffFt", deformFlare[0]+'.lowBound')
            mc.connectAttr(nSwitchsCtr + ".fallOffBk", deformFlare[0]+'.highBound')


            # ADD SYSTEM ikHandle spline ______________________________________________
            # CREATE spline_________________________________________________
            crvSplineIkH = lib_curves.createDoubleCrv(objLst=lsTplCtr[::-1], axis='Z', offset=0 * self.valScl)
            mc.delete(crvSplineIkH['crv'][-1])
            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            numbSubDv = 1
            createCrvSplineIkH = lib_curves.crvSubdivide(crv=crvSplineIkH['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
            nCvSplineIkH = mc.rename(crvSplineIkH['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
            nFunc='SplineIkH'+ str(1), nSide=side,incP=incPart))
            mc.setAttr(nCvSplineIkH+ ".visibility", 1)
            # Skin cv
            skinLoftSplineIkH = mc.skinCluster(lsSkSplineIkH,nCvSplineIkH, tsb=1, mi=1)
            # dic to param points _______________________________
            listCv1 = mc.ls(nCvSplineIkH+ '.cv[*]', fl=True)
            adjNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(listCv1))/adjNumb))
            val = 0
            val2 = 0
            dictPartCv1= {}
            for each2 in range(selDiv2+2):
                lsPartCv1 =[]
                for each in range(adjNumb):
                    lsPartCv1.append(listCv1[each+val+val2])
                val += adjNumb
                val2 -=1
                dictPartCv1[each2] = lsPartCv1
            # get values Skin___________________________
            numbByPart = numbSubDv+2
            nbByPart = numbSubDv+2
            count = 0
            getVal = []
            for each in range(numbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]
            # MODIFY SKIN VALUES CRVS_________________________________________________
            for i, each in enumerate(sorted(dictPartCv1.items())):
                for j, eachPart in enumerate(dictPartCv1.values()[i]):
                    mc.skinPercent(skinLoftSplineIkH[0],eachPart, r=False,
                                   transformValue=[(lsSkSplineIkH[::-1][i], invertVal[j]),(lsSkSplineIkH[::-1][i+1], getVal[j])])

            # CREATE BUF SplineIkH AND CNS SplineIkH____________________________________________
            lsBufSplineIkH = []
            lsBufCnsSplineIkH= []
            for i, each in enumerate(lsSkCtr[::-1]):
                # NAME_________________________________________________________
                nBufSplineIkH  = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name,nFunc='splineIkH'+str(i+1), nSide=side,incP=incPart)
                nCnsSplineIkH = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nFunc='splineIkH'+str(i+1), nSide=side,incP=incPart)
                bufSplineIkH  = libRig.createObj(partial(mc.joint, **{'n': nBufSplineIkH}), match=[each],father=None,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":0})
                cnsSplineIkH  = libRig.createObj(partial(mc.joint, **{'n': nCnsSplineIkH}), match=[each],father=bufSplineIkH,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle":2})
                lsBufSplineIkH.append(bufSplineIkH)
                lsBufCnsSplineIkH.append(cnsSplineIkH)
            [mc.parent(each,lsBufSplineIkH[i])for i, each in enumerate(lsBufSplineIkH[1:])]
            # NAME_________________________________________________________
            nIkHandleSpline = gloss.name_format(prefix=gloss.lexicon('ikHandle'),name=self.name,nFunc='spline'+str(1), nSide=side,incP=incPart)
            nIkHandleSplineRoot = gloss.name_format(prefix=gloss.lexicon('rootIkHandle'),name=self.name,nFunc='spline'+str(1), nSide=side,incP=incPart)
            nGrpJtsSpline = gloss.name_format(prefix=gloss.lexicon('rootJt'),name=self.name,nFunc='spline'+str(1), nSide=side,incP=incPart)
            # CREATE IK HANDLE_______________________________________________
            ikHandleSpline = libRig.createObj(partial(mc.ikHandle, **{'n': nIkHandleSpline, 'sj': lsBufSplineIkH[0],'ee': lsBufSplineIkH[-1],
                            'sol': 'ikSplineSolver','c': nCvSplineIkH, 'fj': False, 'ccv': False,'scv': True}),
                            attributs={"poleVectorY": 1,"poleVectorZ": 0,"snapEnable": 0,"visibility": 0})
            grpIkHandleSpline = libRig.createObj(partial(mc.group, **{'n': nIkHandleSplineRoot, 'em': True}),match=[ikHandleSpline],childLst=[ikHandleSpline])
            # PARENT CURVE WITH HOOK SPINE___________________________________
            mc.select(cl=True)
            jntBufBaseSpline = libRig.createObj(partial(mc.joint, **{'n':nGrpJtsSpline}),match=lsTplIk[-1], father=globalCtr['c'],
            attributs={"rotateOrder": 3,"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"segmentScaleCompensate": 0,
                       "inheritsTransform": 1,"drawStyle": 2,"visibility": 1})
            mc.parent(lsBufSplineIkH[0],jntBufBaseSpline)
            mc.setAttr(lsBufSplineIkH[0] + ".jointOrientX", 0)
            mc.setAttr(lsBufSplineIkH[0] + ".jointOrientY", 0)
            mc.setAttr(lsBufSplineIkH[0] + ".jointOrientZ", 0)

            # CONNECT ATTRIBUT STRETCH TO SplineIkH____________________________________________
            nMltDivFollow = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc='followIkHld'+'Div',nSide=side,incP=incPart)
            nMltDblLinFollow = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nFunc='followIkHld'+'Neg',nSide=side,incP=incPart)
            nAddDblLScl = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.name,nFunc='followIkHld', nSide=side,incP=incPart)
            mltDivFollow = mc.createNode("multiplyDivide", n=nMltDivFollow)
            mc.setAttr(mltDivFollow+ ".operation", 2)
            mc.setAttr(mltDivFollow + ".input2X",10)
            mc.connectAttr(nSwitchsCtr + ".stretch", "%s.input1X" % (mltDivFollow), force=True)
            NodeMltDblLFollow = mc.createNode("multDoubleLinear", n=nMltDblLinFollow)
            mc.setAttr(NodeMltDblLFollow + ".input2", -1)
            mc.connectAttr(mltDivFollow + '.outputX', "%s.input1" % (NodeMltDblLFollow), force=True)
            nodeAddDLFollow = mc.shadingNode("addDoubleLinear",n=nAddDblLScl,asUtility=True)
            mc.setAttr("%s.input2" % (nodeAddDLFollow), 1)
            mc.connectAttr(NodeMltDblLFollow+ '.output', "%s.input1" % (nodeAddDLFollow), force=True)

            for i, each in enumerate(lsRootCtr):
                getParentWeight =[]
                parentCnsFollow = mc.parentConstraint(lsCnsSplineIkH[i],each,w=0)
                firstParentCnsFollow = mc.listConnections(mc.listRelatives(each, type="constraint")[0]+ ".target", p=True)[-1]
                getParentWeight.append(firstParentCnsFollow)
                parentCnsFollow2 = mc.parentConstraint(lsBufCnsSplineIkH[::-1][i],each,w=0)
                secondParentCnsFollow = mc.listConnections(mc.listRelatives(each, type="constraint")[0]+ ".target", p=True)[-1]
                getParentWeight.append(secondParentCnsFollow)
                mc.setAttr(parentCnsFollow[0]+ ".interpType", 2)
                mc.connectAttr(nodeAddDLFollow + '.output', getParentWeight[1], force=True)
                mc.connectAttr(mltDivFollow + '.outputX', getParentWeight[0], force=True)

            mc.orientConstraint(lsIk[-1],lsBufCnsSplineIkH[0],mo=True)

            # CONNECT ROLL AND TWIST IK HANDLE___________________________
            nMltDblLinRollEnd = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nFunc='RollIkHld'+'End',nSide=side,incP=incPart)
            nodeMltDblLRollEnd = mc.createNode("multDoubleLinear", n=nMltDblLinRollEnd)
            mc.setAttr(nodeMltDblLRollEnd + ".input2", -1)
            mc.connectAttr(lsIk[0]+'.rotateZ',"%s.input1" % (nodeMltDblLRollEnd), force=True)
            nMltDblLinRollStart = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nFunc='RollIkHld'+'Start',nSide=side,incP=incPart)
            nAddDblLRollStart  = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.name,nFunc='RollIkHld'+'Start', nSide=side,incP=incPart)
            nodeMltDblLRollStart = mc.createNode("multDoubleLinear", n=nMltDblLinRollStart)
            mc.setAttr(nodeMltDblLRollStart + ".input2", -1)
            mc.connectAttr(lsIk[-1]+'.rotateZ',"%s.input1" % (nodeMltDblLRollStart), force=True)
            nodeAddDLRollStart= mc.shadingNode("addDoubleLinear",n=nAddDblLRollStart,asUtility=True)
            #mc.setAttr("%s.input2" % (nodeAddDLRollStart), 1)
            mc.connectAttr(lsIk[-1]+'.rotateZ', "%s.input1" % (nodeAddDLRollStart), force=True)
            mc.connectAttr(nodeMltDblLRollEnd+ '.output', "%s.input2" % (nodeAddDLRollStart), force=True)

            mc.connectAttr(nodeMltDblLRollStart+ '.output',ikHandleSpline + '.roll', force=True)
            mc.connectAttr(nodeAddDLRollStart+ '.output',ikHandleSpline + '.twist', force=True)



            # CREATE SK_________________________________________________
            lsSk= []
            for i, each in enumerate(lsTplSk):
                nSk = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name,nFunc='sk',inc=str(i+1),nSide=side,incP=incPart)
                sk =libRig.createObj(partial(mc.joint, **{'n':nSk}),match=each,father=None,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                lsSk.append(sk)
            # CREATE SA SK____________________________________________
            lsSa =[lib_connectNodes.nurbs_attach(lsObj=[loftSk,each[1]], parentInSA=True, delLoc=False,parentSA=GrpNoTouch) for each in enumerate(lsSk)]
            lsSclLoc = [gloss.renameSplit(selObj=mc.pickWalk(each[0],d='down')[0], namePart=['loc'], newNamePart=['locSk'], reNme=True) for each in lsSa]
            lsSaScl =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['saSk'], reNme=True) for each in lsSa]
            # CREATE SA TO SCALE SYSTEM____________________
            mc.select(cl=True)
            lsSaSclUp=[lib_connectNodes.nurbs_attach(lsObj=[loftSk,each[1]], parentInSA=False, delLoc=False,parentSA=GrpNoTouch) for each in enumerate(lsSaScl)]

            locUp =[]
            for each in lsSaSclUp:
                mc.setAttr(mc.pickWalk(each[0],d='down')[0] + '.V', 0)
                locUp.append(mc.pickWalk(each[0],d='down')[0])

            lsDistDimUp =[]
            for j, eachSa in enumerate(lsSaScl):
                getPosUp = [mc.xform(each , q=True, ws=True, translation=True) for i, each in enumerate((eachSa,locUp[j]))]
                nNodeDstDimUp = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('info')+'Up'+str(j+1),nSide=side,incP=incPart)
                distDimUp = mc.distanceDimension( sp=(getPosUp[0][0],getPosUp[0][1],getPosUp[0][2]), ep=(getPosUp[-1][0],getPosUp[-1][1],getPosUp[-1][2]))
                rootDstDimUp = mc.pickWalk(distDimUp, d='up')
                mc.rename(rootDstDimUp,nNodeDstDimUp)
                mc.parent(nNodeDstDimUp,GrpNoTouch)
                lsDistDimUp.append(nNodeDstDimUp)

            for i, each in enumerate(lsDistDimUp):
                # create Node scale__________________________
                nMltDivDist = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name,nFunc='dst'+str(i+1), nSide=side, incP=incPart)
                nMltDivScl = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name,nFunc='scl'+str(i+1), nSide=side, incP=incPart)

                shpDistDim = mc.listRelatives(each, s=True)[0]
                mltDivDist = mc.createNode("multiplyDivide", n=nMltDivDist)
                mc.setAttr(mltDivDist + ".operation", 2)
                mc.setAttr(mltDivDist + ".input1X", 1)
                mc.setAttr(mltDivDist + ".input2X", mc.getAttr(shpDistDim+".distance"))

                mltDivScl = mc.createNode("multiplyDivide", n=nMltDivScl)
                mc.setAttr(mltDivScl + ".operation", 1)
                mc.connectAttr(shpDistDim  +".distance", "%s.input1X" % (mltDivScl), force=True)
                mc.connectAttr(mltDivDist +".outputX", "%s.input2X" % (mltDivScl), force=True)
                if each == lsDistDimUp[0] or each == lsDistDimUp[-1]:
                    pass
                else:
                    mc.connectAttr(mltDivScl+ '.outputX', "%s.scaleX" % (lsSk[i]), force=True)
                    mc.connectAttr(mltDivScl+ '.outputX', "%s.scaleY" % (lsSk[i]), force=True)
                mc.setAttr(lsSclLoc[i] + ".visibility", 0)
                mc.setAttr(locUp[i] + ".visibility", 0)
                mc.setAttr(each + ".visibility", 0)
            # parent knot Sk_________________________________________________
            #mc.parent(lsSk[0],lsCtr[0])
            #mc.parent(lsSk[-1],lsCtr[-1])

            '''
            # CREATE CURVE INFO___________________________________________________
            nArcLen = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nSide=side,incP=incPart)
            arclen = mc.arclen(nCvSpline, ch=True)
            nArclen = mc.rename(arclen, nArcLen)
            cvLen = mc.getAttr(nArclen + ".arcLength")
            '''

            ############################ Parentage et connection elements ###########################################
            lib_attributes.disconnectAll(lsSk[0]+'.scale', source=True, destination=True)
            lib_attributes.disconnectAll(lsSk[-1]+'.scale', source=True, destination=True)
            mc.parentConstraint(lsCtr[0], lsSk[0],w=1)
            mc.parentConstraint(lsCtr[-1], lsSk[-1],w=1)
            mc.scaleConstraint(lsCtr[0], lsSk[0],w=1)
            mc.scaleConstraint(lsCtr[-1], lsSk[-1],w=1)

            mc.parentConstraint(globalCtr['c'], jntBufBase,mo=True)
            mc.parentConstraint(lsCtrPath[-1], grpIkHandlePath, w=1)
            mc.parentConstraint(lsCtrPath[0], grpIkHandleSpline, w=1)
            # parentage IKHandle avec ctr Cog
            mc.parent(rigAdd['root'],lsIk[-1])
            mc.parent(grpIkHandlePath,globalCtr['c'])
            mc.parent(grpIkHandleSpline,globalCtr['c'])
            mc.parent(lsCv[0],gloss.lexicon('world')+'Center')
            mc.parent(lsCv[1],gloss.lexicon('world')+'Center')
            mc.parent(loftCtrPath,gloss.lexicon('world')+'Center')
            mc.parent(nCvIkSpline,gloss.lexicon('world')+'Center')
            mc.parent(loftCtr,gloss.lexicon('world')+'Center')
            mc.parent(loftBuf,gloss.lexicon('world')+'Center')
            mc.parent(loftBend,gloss.lexicon('world')+'Center')
            mc.parent(deformBend[1],gloss.lexicon('world')+'Center')
            mc.parent(loftSine,gloss.lexicon('world')+'Center')
            mc.parent(deformSine[1],gloss.lexicon('world')+'Center')
            mc.parent(loftSk,gloss.lexicon('world')+'Center')
            mc.parent(loftFlare,gloss.lexicon('world')+'Center')
            mc.parent(deformFlare[1],gloss.lexicon('world')+'Center')
            mc.parent(sAGrp,hook)
            mc.parent(nCvSplineIkH,gloss.lexicon('world')+'Center')
            # visibility
            mc.setAttr(loftBuf+ ".visibility",0)
            mc.setAttr(loftBend+ ".visibility",0)
            mc.setAttr(loftCtr+ ".visibility",0)
            mc.setAttr(loftSine+ ".visibility",0)
            mc.setAttr(loftSk+ ".visibility",0)
            mc.setAttr(loftFlare+ ".visibility",0)
            mc.setAttr(deformSine[1]+ ".visibility",0)
            mc.setAttr(deformBend[1]+ ".visibility",0)
            mc.setAttr(deformFlare[1]+ ".visibility",0)
            mc.setAttr(nCvSplineIkH+ ".visibility",0)
            mc.setAttr("root_WALK" + ".segmentScaleCompensate",0)
            mc.setAttr("root_FLY" + ".segmentScaleCompensate",0)

            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'), name=self.name,nFunc=gloss.lexicon('skin'), incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            [mc.sets(each, edit=True, forceElement=nSetPart)for i, each in enumerate(lsSk)]

