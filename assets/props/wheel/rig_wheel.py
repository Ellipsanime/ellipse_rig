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

class Wheel(rig_world.RigWorld):

    def __init__(self, name='wheel',side='', tplInfo='tplInfo', hook = '',*args):
        rig_world.RigWorld.__init__(self)
        self.hook =hook
        self.name = name
        self.info = tplInfo
        self.typeArrow = "arrowQuadro2"
        self.typeCross = "cross"
        self.shpRotIk = (0,45,0)
        self.rigAdd = "rigAdd"
        self.Ctr = "square"
        self.CtrSlide = "sphere"
        color = lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.nbCtr = 8

    def createWheel(self):
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
            color = lib_shapes.side_color(side=side)
            valColorCtr = color["colorCtr"]
            valColorIk = color["colorIk"]
            valColorMstCtr = color["colorMaster"]

            master = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('masterTpl'))
            rigAddTpl = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('rigAddTpl'))
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            tplCv1 =mc.getAttr(eachTpl+'.cvs[0]')
            tplCv2 =mc.getAttr(eachTpl+'.cvs[1]')
            tplPath =mc.getAttr(eachTpl+'.cvPath[0]')
            subdCv = (mc.attributeQuery("crvInfo",node=eachTpl, listEnum=1)[0]).split(":")[0]
            skNumb = (mc.attributeQuery("crvInfo",node=eachTpl, listEnum=1)[0]).split(":")[1]

            # NAME________________________________________________________________
            nHook = gloss.name_format(prefix=gloss.lexicon('hook'),name=self.name, nSide=side,incP=incPart)
            nRig = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name,nSide=side,incP=incPart)
            nGlobalCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('cog'),nSide=side,incP=incPart)
            nCtrTr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nSide=side,incP=incPart)
            nCtrCns = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nSide=side,incP=incPart)
            # HOOK________________________________________________________________
            hook =libRig.createObj(partial(mc.joint, **{'n':nHook}),match=None,father=self.nRig,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            lib_connectNodes.connectMatrixAxis(driver=self.nLocFly, slave=hook)
            # RIG________________________________________________________________
            rig = libRig.createObj(partial(mc.group, **{'n': nRig, 'em': True}), Match=self.nFly,father=hook)
            # COG___________________________________________________________________
            globalCtr = libRig.createController(name=nGlobalCtr,shape=libRig.Shp([self.typeArrow],color=valColorMstCtr,size=(3,3,3)),match=master,father=rig)
            mc.setAttr(globalCtr["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            ctrCns = libRig.createObj(partial(mc.group, **{'n':nCtrCns, 'em': True}), Match=globalCtr["c"],father=rig)
            # CTR TRANSLATE___________________________________________________________________
            ctrTr = libRig.createController(name=nCtrTr,shape=libRig.Shp([self.typeCross],color=valColorIk,size=(1.5,1.5,1.5)),match=master,father=globalCtr["c"])
            mc.setAttr(ctrTr["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            mc.setAttr(ctrTr['root'] + '.segmentScaleCompensate', 0)
            # CONSTRAINT_____________________________________________
            mc.parentConstraint(globalCtr["c"],ctrCns)
            mc.scaleConstraint(globalCtr["c"],ctrCns)
            # CTR___________________________________________________________________
            lsSkCtr = []
            lsCtr = []
            lsSkCtrUp = []
            for i,each in enumerate(lsTplCtr):
                nCtr = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name, nFunc=str(i+1), nSide=side,incP=incPart)
                ctr = libRig.createController(name=nCtr,shape=libRig.Shp([self.Ctr], color=valColorIk, size=(1,1,1)),match=each,father=ctrTr['c'])
                mc.setAttr(ctr['root'] + '.segmentScaleCompensate', 0)
                lsSkCtr.append(ctr['sk'])
                lsCtr.append(ctr['c'])

                lib_attributes.disconnectAll(ctr['sk']+'.scale', source=True, destination=True)
                mc.connectAttr(ctr['c']+'.scaleX', ctr['sk']+'.scaleX', force=True)
                mc.connectAttr(ctr['c']+'.scaleZ', ctr['sk']+'.scaleZ', force=True)

                nSkUp = gloss.name_format(prefix=gloss.lexicon('sk'), name=self.name, nFunc='up'+str(i+1), nSide=side,incP=incPart)
                skUp =libRig.createObj(partial(mc.joint, **{'n':nSkUp}),match=[ctr['c']],father=ctr['root'],attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                lib_connectNodes.connectAxis(ctr['c'],skUp,pos=True,rot=True,scl=False,rotOrder=True)
                mc.connectAttr(ctr['c']+'.scaleY',skUp+'.scaleY', force=True)
                mc.connectAttr(ctr['c']+'.scaleZ',skUp+'.scaleZ', force=True)
                lsSkCtrUp.append(skUp)


                # MATCH CVS WITH TPL CV__________________________
                lib_shapes.matchShpCv(shpRef=each, shpTarget=ctr['c'])

            # CREATE CRV______________________________________________
            nRootCrvs = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('loft'), nSide=side,incP=incPart)
            nCrv1 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=str(1), nSide=side,incP=incPart)
            nCrv2 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=str(2), nSide=side,incP=incPart)
            nCrvUp1 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc='up'+str(1), nSide=side,incP=incPart)
            nCrvUp2 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc='up'+str(2), nSide=side,incP=incPart)
            nloft = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nSide=side,incP=incPart)
            nloftup = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc='up',nSide=side,incP=incPart)

            rootLoft = libRig.createObj(partial(mc.group, **{'n': nRootCrvs, 'em': True}),match=[ctrTr["c"]],father=self.nRig,attributs={"visibility": 0})
            crv1 =libRig.createObj(partial(mc.circle, **{'n': nCrv1, 's':int(subdCv),'sw':360,'nr':(1,0,0)}),match=[tplCv1],father=rootLoft)
            crv2 =libRig.createObj(partial(mc.circle, **{'n': nCrv2, 's':int(subdCv),'sw':360,'nr':(1,0,0)}),match=[tplCv2],father=rootLoft)

            crvUp1 =libRig.createObj(partial(mc.circle, **{'n': nCrvUp1, 's':int(subdCv),'sw':360,'nr':(1,0,0)}),match=[tplCv1],father=rootLoft)
            crvUp2 =libRig.createObj(partial(mc.circle, **{'n': nCrvUp2, 's':int(subdCv),'sw':360,'nr':(1,0,0)}),match=[tplCv2],father=rootLoft)

            # CrvPath___________________________________________
            nRotCrvPath = gloss.name_format(prefix=gloss.lexicon('rot'),name=self.name,nFunc="cvPath"+str(1),nSide=side,incP=incPart)
            nCrvPath = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc="path"+str(1),nSide=side,incP=incPart)
            nCrvInfo = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('info')+'path',nSide=side,incP=incPart)
            rotCrvPath = libRig.createObj(partial(mc.group, **{'n': nRotCrvPath, 'em': True}),match=[ctrTr["c"]],father=rootLoft)
            crvPath =libRig.createObj(partial(mc.circle, **{'n': nCrvPath, 's':int(subdCv),'sw':360,'nr':(1,0,0)}),match=[tplPath],father=rotCrvPath)
            mc.select(crvPath)
            nArclen = mc.arclen(ch=True)
            mc.rename(nArclen,nCrvInfo)
            mc.select(cl=True)
            mc.orientConstraint(ctrTr["c"],rotCrvPath)
            mc.pointConstraint(ctrTr["c"],crvPath)

            # MATCH CVS WITH TPL CV__________________________
            lib_shapes.matchShpCv(shpRef=tplCv1, shpTarget=crv1)
            lib_shapes.matchShpCv(shpRef=tplCv2, shpTarget=crv2)
            lib_shapes.matchShpCv(shpRef=tplPath, shpTarget=crvPath)
            lib_shapes.matchShpCv(shpRef=tplCv1, shpTarget=crvUp1)
            lib_shapes.matchShpCv(shpRef=tplCv2, shpTarget=crvUp2)
            """
            selShape = mc.listRelatives(crvUp2,s=True)[0]
            recCv = mc.ls(selShape + '.cv[*]', fl=True)
            mc.scale(0.8,0.8,0.8,recCv,cs=True)
            """
            # CREATE LOFT____________________________________
            loftCv = libRig.createObj(
            partial(mc.loft, crv1, crv2, **{'n': nloft, 'ch': True, 'u': True, 'c': 0, 'ar': 1,'d': 3, 'ss': 0, 'rn': 0,
             'po': 0, 'rsn': True}), father=rootLoft,refObj=None, incPart=False, attributs={"visibility": 1})

            loftCvUp = libRig.createObj(
            partial(mc.loft, crvUp1, crvUp2, **{'n': nloftup, 'ch': True, 'u': True, 'c': 0, 'ar': 1,'d': 3, 'ss': 0, 'rn': 0,
             'po': 0, 'rsn': True}), father=rootLoft,refObj=None, incPart=False, attributs={"visibility": 1})


            # ADJUST SKINNING CV___________________________
            splitPart = 3
            listCv1 = mc.ls(crv1 + '.cv[*]', fl=True)
            listCv1.append(listCv1[0])
            listCv2 = mc.ls(crv2 + '.cv[*]', fl=True)
            listCv2.append(listCv2[0])
            listCvUp1 = mc.ls(crvUp1 + '.cv[*]', fl=True)
            listCvUp1.append(listCvUp1[0])
            listCvUp2 = mc.ls(crvUp2 + '.cv[*]', fl=True)
            listCvUp2.append(listCvUp2[0])

            val = 0
            dictPartCv1 = {}
            dictPartCv2 = {}
            dictPartCvUp1 = {}
            dictPartCvUp2 = {}
            for each2 in range(self.nbCtr):
                lsPartCv1 = []
                lsPartCv2 = []
                lsPartCvUp1 = []
                lsPartCvUp2 = []
                for each in range(splitPart):
                    lsPartCv1.append(listCv1[each + val])
                    lsPartCv2.append(listCv2[each + val])
                    lsPartCvUp1.append(listCvUp1[each + val])
                    lsPartCvUp2.append(listCvUp2[each + val])
                val += 2
                dictPartCv1[each2] = lsPartCv1
                dictPartCv2[each2] = lsPartCv2
                dictPartCvUp1[each2] = lsPartCvUp1
                dictPartCvUp2[each2] = lsPartCvUp2
            # get values Skin___________________________
            count = 0
            getValCrv = []
            for each in range(splitPart):
                val = round(abs(float(count) / float(splitPart - 1)), 4)
                count += 1
                getValCrv.append(val)
            invertValCrv = getValCrv[::-1]

            # skin crvs______________________________________
            skinCrv = mc.skinCluster(lsSkCtr, crv1, tsb=1, mi=1)
            skinCrv2 = mc.skinCluster(lsSkCtr, crv2, tsb=1, mi=1)
            skinCrvUp1 = mc.skinCluster(lsSkCtrUp, crvUp1, tsb=1, mi=1)
            skinCrvUp2 = mc.skinCluster(lsSkCtrUp, crvUp2, tsb=1, mi=1)
            addfirstskToLast = lsSkCtr
            addfirstskToLast.append(lsSkCtr[0])
            addfirstskToLastUp = lsSkCtrUp
            addfirstskToLastUp.append(lsSkCtrUp[0])

            # MODIFY SKIN VALUES CRVS_________________________________________________
            for i, each in enumerate(sorted(dictPartCv1.items())):
                for j, eachPoint in enumerate(dictPartCv1.values()[i]):
                    mc.skinPercent(skinCrv[0], eachPoint, r=False,
                                   transformValue=[(lsSkCtr[i],invertValCrv[j]),(addfirstskToLast[i + 1],getValCrv[j])])
            for i, each in enumerate(sorted(dictPartCv2.items())):
                for j, eachPoint in enumerate(dictPartCv2.values()[i]):
                    mc.skinPercent(skinCrv2[0], eachPoint, r=False,
                                   transformValue=[(lsSkCtr[i],invertValCrv[j]),(addfirstskToLast[i + 1],getValCrv[j])])

            for i, each in enumerate(sorted(dictPartCvUp1.items())):
                for j, eachPoint in enumerate(dictPartCvUp1.values()[i]):
                    mc.skinPercent(skinCrvUp1[0], eachPoint, r=False,
                                   transformValue=[(lsSkCtrUp[i],invertValCrv[j]),(addfirstskToLastUp[i + 1],getValCrv[j])])
            for i, each in enumerate(sorted(dictPartCvUp2.items())):
                for j, eachPoint in enumerate(dictPartCvUp2.values()[i]):
                    mc.skinPercent(skinCrvUp2[0], eachPoint, r=False,
                                   transformValue=[(lsSkCtrUp[i],invertValCrv[j]),(addfirstskToLastUp[i + 1],getValCrv[j])])

            # CREATE SA____________________________________
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('SA'), name=self.name, nFunc=gloss.lexicon('loft')+'Cv',nSide=side,incP=incPart)
            sAGrp = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), Match=None, father=self.nSa)
            mc.connectAttr(self.nLocFly + '.scale', "%s.scale" % (sAGrp), force=True)

            lSaCtr = lib_connectNodes.surfAttach(selObj=[loftCv], lNumb=int(skNumb), parentInSA=True, parentSA=nSAGrp, delKnot=True)
            # ADJUST POSITION______________________________
            ratio = mc.getAttr(loftCv+'.minMaxRangeU')[0][1]/int(skNumb)
            [mc.setAttr(lSaCtr['loc'][each] + '.U', each*ratio) for each in range(int(skNumb))]
            # RENAME SA____________________________________
            lsSa =[gloss.renameSplit(selObj=each, namePart=['wheel'], newNamePart=['wheelCtr'], reNme=True) for each in lSaCtr['sa']]
            lsSaCtr=[gloss.renameSplit(selObj=each, namePart=['wheel'], newNamePart=['wheelCtr'], reNme=True) for each in lSaCtr['loc']]
            # CREATE SA TO SCALE SYSTEM____________________
            lSaScl = lib_connectNodes.surfAttach(selObj=[loftCv], lNumb=int(skNumb), parentInSA=True, parentSA=nSAGrp, delKnot=True)
            lsSaScl =[gloss.renameSplit(selObj=each, namePart=['wheel'], newNamePart=['wheelSkH'], reNme=True) for each in lSaScl['sa']]
            lsSaLocScl=[gloss.renameSplit(selObj=each, namePart=['wheel'], newNamePart=['wheelSkH'], reNme=True) for each in lSaScl['loc']]
            [mc.setAttr(lsSaLocScl[each] + '.U', each*ratio) for each in range(int(skNumb))]
            [mc.setAttr(lsSaLocScl[each] + '.V', 0) for each in range(int(skNumb))]

            lSaSclUp = lib_connectNodes.surfAttach(selObj=[loftCvUp], lNumb=int(skNumb), parentInSA=True, parentSA=nSAGrp, delKnot=True)
            [mc.setAttr(lSaSclUp['loc'][each] + '.U', each*ratio) for each in range(int(skNumb))]
            [mc.setAttr(lSaSclUp['loc'][each] + '.V', 1) for each in range(int(skNumb))]

            ## Distance Dimension___________________________
            # create group No Touch_________________________
            nNoTouch = gloss.name_format(prefix=gloss.lexicon('NoTouch'),name=self.name,nSide=side,incP=incPart)
            GrpNoTouch = libRig.createObj(partial(mc.group, **{'n':nNoTouch , 'em': True}),father=rig,attributs={"visibility": 0})

            lsDistDim =[]
            for j, eachSa in enumerate(lsSaCtr):
                getPos = [mc.xform(each , q=True, ws=True, translation=True) for i, each in enumerate((eachSa,lsSaLocScl[j]))]
                nNodeDstDim = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('info')+str(j+1),nSide=side,incP=incPart)
                distDim = mc.distanceDimension( sp=(getPos[0][0],getPos[0][1],getPos[0][2]), ep=(getPos[-1][0],getPos[-1][1],getPos[-1][2]))
                rootDstDim = mc.pickWalk(distDim, d='up')
                mc.rename(rootDstDim,nNodeDstDim)
                mc.parent(nNodeDstDim,GrpNoTouch)
                lsDistDim.append(nNodeDstDim)

            lsDistDimUp =[]
            for j, eachSa in enumerate(lsSaCtr):
                getPosUp = [mc.xform(each , q=True, ws=True, translation=True) for i, each in enumerate((eachSa,lSaSclUp['loc'][j]))]
                nNodeDstDimUp = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('info')+'Up'+str(j+1),nSide=side,incP=incPart)
                distDimUp = mc.distanceDimension( sp=(getPosUp[0][0],getPosUp[0][1],getPosUp[0][2]), ep=(getPosUp[-1][0],getPosUp[-1][1],getPosUp[-1][2]))
                rootDstDimUp = mc.pickWalk(distDimUp, d='up')
                mc.rename(rootDstDimUp,nNodeDstDimUp)
                mc.parent(nNodeDstDimUp,GrpNoTouch)
                lsDistDimUp.append(nNodeDstDimUp)


            # create ctrS slidde alone loft__________________
            lsSkSlide =[]
            for i, each in enumerate(lsSa):
                nCtrSlide = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc='slide'+str(i+1),nSide=side,incP=incPart)
                ctrSlide = libRig.createController(name=nCtrSlide,shape=libRig.Shp([self.CtrSlide], color=valColorCtr, size=(0.1,0.1,0.1)),match=each,father=each)
                mc.setAttr(ctrSlide['c'] + '.segmentScaleCompensate', 0)
                mc.setAttr(ctrSlide['sk'] + '.segmentScaleCompensate', 0)
                # create Node scale__________________________
                nMltDivDist = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name,nFunc='dst'+str(i+1), nSide=side, incP=incPart)
                nMltDivScl = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name,nFunc='scl'+str(i+1), nSide=side, incP=incPart)
                nMltDivSclUp = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name,nFunc='sclUp'+str(i+1), nSide=side, incP=incPart)

                shpDistDim = mc.listRelatives(lsDistDim[i], s=True)[0]
                mltDivDist = mc.createNode("multiplyDivide", n=nMltDivDist)
                mc.setAttr(mltDivDist + ".operation", 2)
                mc.setAttr(mltDivDist + ".input1X", 1)
                mc.setAttr(mltDivDist + ".input2X", mc.getAttr(shpDistDim+".distance"))

                mltDivScl = mc.createNode("multiplyDivide", n=nMltDivScl)
                mc.setAttr(mltDivScl + ".operation", 1)
                mc.connectAttr(shpDistDim  +".distance", "%s.input1X" % (mltDivScl), force=True)
                mc.connectAttr(mltDivDist +".outputX", "%s.input2X" % (mltDivScl), force=True)

                shpDistDimUp = mc.listRelatives(lsDistDimUp[i], s=True)[0]
                mltDivSclUp = mc.createNode("multiplyDivide", n=nMltDivSclUp)
                mc.setAttr(mltDivSclUp + ".operation", 1)
                mc.connectAttr(shpDistDimUp  +".distance", "%s.input1X" % (mltDivSclUp), force=True)
                mc.connectAttr(mltDivDist +".outputX", "%s.input2X" % (mltDivSclUp), force=True)

                mc.connectAttr(mltDivScl+ '.outputX', "%s.scaleZ" % (ctrSlide['root']), force=True)
                mc.connectAttr(mltDivSclUp+ '.outputX', "%s.scaleY" % (ctrSlide['root']), force=True)
                lsSkSlide.append(ctrSlide['sk'])


            # CREATE RIG ADD____________________
            nRigAdd = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('add'), nSide=side,incP=incPart)
            rigAdd =libRig.createController(name=nRigAdd,shape=libRig.Shp([self.rigAdd],color=valColorMstCtr,size=(1,1,1),
            rotShp=(0,0,0)),match=rigAddTpl,father=ctrTr["c"],attributs={"drawStyle": 2})
            lib_shapes.matchShpCv(shpRef=rigAddTpl, shpTarget=rigAdd['c'])


            # ADD ATTRIBUTES TO RIG ADD__________________________________________________________________________________
            mc.addAttr(rigAdd['c'], ln="offSet", nn="OffSet", at="double", dv=0)
            mc.setAttr(rigAdd['c'] + ".offSet", e=True, k=True)
            mc.addAttr(rigAdd['c'], ln='auto', at="enum",en="off:on", k=True)
            mc.setAttr(rigAdd['c'] + '.auto', e=True, cb=True)

            # CREATE PATH SYSTEM____________________
            nMotionPath = gloss.name_format(prefix=gloss.lexicon('mPath'), name=self.name,nSide=side, incP=incPart)
            motionPath = mc.createNode("motionPath", n=nMotionPath)
            AxeVal = 'Z'
            factor = 25
            # expression of Locator on the curve
            exp1 = (str(motionPath) + ".uValue" + " = (((" + crvPath + ".translate%s *" %(AxeVal) + rigAdd['c'] +".auto + " + rigAdd['c'] + ".offSet) *" + globalCtr["c"] +".scaleY)/%s" %(nCrvInfo) + ".arcLength)"+"*%s"%(str(factor)) + "\n")
            # creer l'expression qui reçoit le code pour les treads
            nExp = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc='path', nSide=side,incP=incPart)
            codeExp = mc.expression (s=exp1, n=nExp)


            for i,each in enumerate(lsSaLocScl):
                nAddDblLSa = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.name, nFunc='sa'+str(i+1),nSide=side, incP=incPart)
                addDblLSa = mc.shadingNode("addDoubleLinear",n=nAddDblLSa,asUtility=True)
                mc.setAttr("%s.input2" % (addDblLSa), mc.getAttr(each+ '.U'))
                mc.connectAttr(codeExp+ '.output[0]', "%s.input1" % (addDblLSa), force=True)
                mc.connectAttr(addDblLSa + '.output', "%s.U" % (each), force=True)
                mc.connectAttr(addDblLSa + '.output', "%s.U" % (lsSaCtr[i]), force=True)
                mc.connectAttr(addDblLSa + '.output', "%s.U" % (lSaSclUp['loc'][i]), force=True)
            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'), name=self.name,nFunc=gloss.lexicon('skin'), incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            [mc.sets(each, edit=True, forceElement=nSetPart)for i, each in enumerate(lsSkSlide)]