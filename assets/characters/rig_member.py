# coding: utf-8



import maya.cmds as mc
import math
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_rigPreset as libRgPreset
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes, lib_constraints
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
reload(lib_constraints)

rig_world.RigWorld().createRig()  # instance class charGuide and run method createRig

class Member(rig_world.RigWorld):

    def __init__(self, name='leg', tplInfo='tplInfo', hook='', *args):
        rig_world.RigWorld.__init__(self)
        self.hook = hook
        self.hookIk = 'hook_FLY'
        self.name = name
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.shpRotIk = (0,45,0)
        self.IkType = 'ikRPsolver'
        self.valAttrAdjust = 10
        self.nameStart = 'hip'
        self.nameMid = 'knee'
        self.nameEnd = 'foot'
        self.nameKnot = 'toes'
        self.nameKnot2 = 'wrist'
        self.nameClav = 'femur'
        if self.name == 'arm':
            self.nameStart = 'shoulder'
            self.nameMid = 'elbow'
            self.nameEnd = 'hand'
            self.nameKnot = 'fingers'
            self.nameClav = 'clav'


    def createMember(self):
        # FILTER BY TPL INFO_______________________________________
        #lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        # CREATE RIG TO LIST INFO_________________________________
        dicMember = {}
        dicBuf = {}
        dicSk = {}
        lCtrl = []
        getShpAttr = []
        for i, eachTpl in enumerate([self.info]):
            dic = {}
            # GET INFO TO CREATE RIG____________________________________________________________________________________
            incPart = mc.getAttr(eachTpl+'.incInfo')
            side = (mc.attributeQuery("update",node=eachTpl, listEnum=1)[0]).split(":")[1]
            if side == 'empty': side =''
            color = lib_shapes.side_color(side=side)
            valColorAdd = color["colorCtr"]
            valColorCtr = color["colorIk"]
            valColorCtrIK = color["colorMaster"]
            sizeIk = (mc.attributeQuery("sizeSk",node=eachTpl, listEnum=1)[0]).split(":")[0]
            numbPart = (mc.attributeQuery("sizeSk",node=eachTpl, listEnum=1)[0]).split(":")[4]
            numbSk = (mc.attributeQuery("sizeSk",node=eachTpl, listEnum=1)[0]).split(":")[5]
            master = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('masterTpl'))
            masterStart = mc.getAttr(eachTpl+".%s[0]"%'masterStart')
            lsTplIk =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            lsTplCtrOnly =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            lsTplClavIk =[mc.getAttr(eachTpl+'.ikStart[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ikStart', mi=True,s=True))]
            lsTplClavCtr =[mc.getAttr(eachTpl+'.ctrStart[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctrStart', mi=True,s=True))]
            lsTplPlV =[mc.getAttr(eachTpl+'.masterPlV[%s]'%i) for i in range(mc.getAttr(eachTpl+'.masterPlV', mi=True,s=True))]
            concatPlV = [mc.getAttr(eachTpl+'.masterPlV[%s]'%i) for i in range(mc.getAttr(eachTpl+'.masterPlV', mi=True,s=True))]
            if int(numbPart) > 1:
                lsTplAddPlV =[mc.getAttr(eachTpl+'.masterAddPlV[%s]'%i) for i in range(mc.getAttr(eachTpl+'.masterAddPlV', mi=True,s=True))]
                lenLsPlV = len(concatPlV)
                [concatPlV.insert(lenLsPlV + (i), each) for i, each in enumerate(lsTplAddPlV)]
            # NAME___________________________________________________
            nSwitchsRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('switch'),
                                             nSide=side,incP=incPart)
            nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'),
                                            nSide=side,incP=incPart)
            ## creation shape pour Attribut
            shapeAttrib = mc.createNode("nurbsCurve", n=nSwitchsCtr)
            transformShape = mc.listRelatives(shapeAttrib, p=True)
            rootSwitchs = mc.rename(transformShape,nSwitchsRoot)
            ## ajouter un attribut au dernier element de la selection
            mc.addAttr(shapeAttrib, ln="ikBlend", nn="Ik Blend", at="double", min=0, max=10, dv=10)
            mc.setAttr(shapeAttrib + ".ikBlend", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="twistFix", nn="Twist Fix", at="double", dv=0)
            mc.setAttr(shapeAttrib + ".twistFix", e=True, k=True)
            #mc.addAttr(shapeAttrib, ln="smooth", nn="Smooth", at="double", min=0, max=10, dv=0)
            #mc.setAttr(shapeAttrib + ".smooth", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="arc", nn="Arc", at="double", min=0, max=10, dv=0)
            mc.setAttr(shapeAttrib + ".arc", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="autoHideIKFK", nn="Auto Hide IKFK", at="bool", dv=1)
            mc.setAttr(shapeAttrib + ".autoHideIKFK", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="orientIK", at="float", min=0, max=10, dv=0)
            mc.setAttr(shapeAttrib + ".orientIK", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="autoOrient", nn="Auto Orient", at="double", min=0, max=10, dv=0)
            mc.setAttr(shapeAttrib + ".autoOrient", e=True, k=True)


            # parentage switch Attrib
            mc.parent(rootSwitchs, self.nSwitch)
            # HIDE DEFAULT ATTRIBUTES ________________________________
            lib_attributes.hide_ctrl_hist(selObj=nSwitchsRoot)
            # FUSION TPL IK and CTR___________________________________
            concatIkFk = lsTplCtr
            concatIkFk.insert(0, lsTplIk[0])
            concatIkFk.insert(len(lsTplCtr) + 1, lsTplIk[-1])
            # FUSION CONCAT AND MID_MB________________________________
            if mc.objExists(eachTpl+'.midMb') is True:
                lsTplMidMb =[mc.getAttr(eachTpl+'.midMb[%s]'%i) for i in range(mc.getAttr(eachTpl+'.midMb', mi=True,s=True))]
                lenLsTplMidMb  = len(lsTplMidMb)+1
                # add MIDDLE MEMBER TO LIST FK/IK_____________________
                lenLs = len(concatIkFk)
                [concatIkFk.insert(lenLs + (i), each) for i, each in enumerate(lsTplMidMb)]
            else:
                lenLsTplMidMb  = 1

            ############################################  FK  ##########################################################
            nLsFk = []
            lsRotOrder = []
            # NAME______________________________________________________________________________________________________
            count = 1
            for i, each in enumerate(concatIkFk):
                rotOrdFk = libRgPreset.configAxis(mb="rOrdLeg")["rOrdFk"]
                if self.name == "arm":
                    rotOrdFk = libRgPreset.configAxis(mb="rOrdArm")["rOrdFk"]
                if i == 0:
                    nFk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameStart,nSide=side,incP=incPart)
                elif i < (len(concatIkFk)-lenLsTplMidMb):
                    nFk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameMid+str(i),nSide=side,incP=incPart)
                else:
                    nFk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameEnd+str(count),nSide=side,incP=incPart)
                    count += 1

                    rotOrdFk = libRgPreset.configAxis(mb="rOrdFoot")["rOrdFk"]
                    if self.name == "arm":
                        rotOrdFk = libRgPreset.configAxis(mb="rOrdHand")["rOrdFk"]
                nLsFk.append(nFk)
                lsRotOrder.append(rotOrdFk)
            # CREATE CHAIN FK___________________________________________________________________________________________
            aimFk = libRgPreset.configAxis(mb="aimJtLeg%s"%side,side=side)["aimOri"]
            upVFk = libRgPreset.configAxis(mb="aimJtLeg%s"%side,side=side)["aimUpV"]
            if self.name == "arm":
                aimFk = libRgPreset.configAxis(mb="aimJtArm%s"%side,side=side)["aimOri"]
                upVFk = libRgPreset.configAxis(mb="aimJtArm%s"%side,side=side)["aimUpV"]
            fk = libRig.chainJoint(lstChain=concatIkFk,lstNameChain=nLsFk, lsRotOrder=lsRotOrder,aim=aimFk, upV=upVFk,
                                   convertChain=True,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)))

            # adjust radius joints__________________________________________________________
            [mc.setAttr(each + ".radius",0.7*mc.getAttr("tpl_WORLD"+".scaleX")) for each in fk]
            [mc.setAttr(each + ".drawStyle",2) for each in fk]
            # duplicate MidMb to create a second hierarchy__________________________________
            lsJntMidMb = []
            for i, each in enumerate(fk[len(concatIkFk)-lenLsTplMidMb:]):
                nJnt = gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameEnd+str(i+1),nSide=side, incP=incPart)
                libRig.createObj(partial(mc.joint, **{'n': nJnt}), match=[each], father=each,
                                 attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                if i ==0:
                    mc.parent(nJnt, fk[len(concatIkFk) - (lenLsTplMidMb + 1)])
                else:
                    mc.parent(nJnt, gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameEnd+str(i),nSide=side, incP=incPart))
                lsJntMidMb.append(nJnt)
                #mc.setAttr(nJnt+ '.rotateOrder',lsRotOrder[0])


            # add jnt to chain for ik handle foot/hand_____________________________________
            if mc.objExists(eachTpl+'.midMb') is False:
                mc.parent(lsJntMidMb, fk[-1])
                mc.setAttr(lsJntMidMb[0]+".translateY",1*mc.getAttr("tpl_WORLD"+".scaleX"))
            # duplicate first MidMb _________________________________
            nJntFirst = gloss.name_format(prefix=gloss.lexicon('root'), name=self.nameEnd+"Twist1",nSide=side, incP=incPart)
            mc.rename(mc.duplicate(fk[len(concatIkFk)-lenLsTplMidMb],po=True),nJntFirst)
            # Create UpV End Chain _________________________________
            nUpVRootBase = gloss.name_format(prefix=gloss.lexicon('root'), name=self.nameEnd,nFunc=gloss.lexicon('upV'),nSide=side, incP=incPart)
            nUpV = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.nameEnd,nFunc=gloss.lexicon('upV'),nSide=side, incP=incPart)
            UpVRoot = libRig.createObj(partial(mc.group, **{'n':nUpVRootBase, 'em': True}),match=[mc.getAttr(eachTpl+'.ik[1]')],father=nJntFirst)
            UpV = libRig.createObj(partial(mc.group, **{'n':nUpV, 'em': True}),match=[UpVRoot],father=UpVRoot,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            mc.move(1*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,UpV, ls=True)

            # Create CONTROL TWIST HAND/FOOT Chain Rig_________________________________
            nFkWrist = gloss.lexicon('wrist')
            if self.name == 'leg':
                nFkWrist = gloss.lexicon('ankle')
            nJntRig1 = gloss.name_format(prefix=gloss.lexicon('c'), name=nFkWrist,nSide=side, incP=incPart)
            mc.rename(mc.duplicate(fk[len(concatIkFk)-lenLsTplMidMb],po=True),nJntRig1)
            mc.parent(nJntRig1,nJntFirst)
            mc.setAttr(nJntRig1+".drawStyle",2)
            mc.setAttr(nJntRig1+".segmentScaleCompensate",0)
            lib_shapes.parent_shp(lsObj=nJntRig1, lsShp=[self.typeCircle], delBaseShp=None, colorType='Index', color=valColorCtr, bound={'sizeX':1, 'sizeY':1, 'sizeZ':1})
            nJntRig2 = gloss.name_format(prefix=gloss.lexicon('jnt'), name=nFkWrist,nSide=side, incP=incPart)
            mc.rename(mc.duplicate(fk[len(concatIkFk)-lenLsTplMidMb+1],po=True),nJntRig2)
            mc.parent(nJntRig2,nJntRig1)
            mc.setAttr(nJntRig2+".drawStyle",2)
            # Create Ik Handle End Chain Rig_______________________
            nIkHdlFirst = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameEnd,nFunc=gloss.lexicon('jnt')+"First",nSide=side,incP=incPart)
            ikHandleFirst = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlFirst ,'sj':nJntRig1,'ee':nJntRig2,'sol':self.IkType}),
                                        match=[fk[len(concatIkFk)-lenLsTplMidMb+1]],father=None,attributs={"snapEnable": 0,"visibility":0})
            mc.poleVectorConstraint(nUpV, ikHandleFirst)
            mc.setAttr(ikHandleFirst+".twist",abs(mc.getAttr(nJntRig1+".rotateY")))
            # FUSION MEMBER CHAIN AND JOINTS END MEMBER________________________________
            lsChainFk = fk[:len(concatIkFk)-lenLsTplMidMb]
            lsChainFk.extend([nJntFirst])
            # SNAP SHAPE TPL FK________________________________________________________
            [lib_shapes.snapShpCv(shpRef=concatIkFk[i], shpTarget=each) for i, each in enumerate(fk)]
            # ADJUST SIZE SHAPE LAST FK AND FK TWIST___________________________________
            lib_shapes.parent_shp(lsObj=nLsFk[len(concatIkFk)-lenLsTplMidMb], lsShp=["circle"], delBaseShp=True, colorType='Index',
                                  color=valColorCtr, bound={'sizeX':0.5*mc.getAttr("tpl_WORLD"+".scaleX"),
                                  'sizeY':0.5*mc.getAttr("tpl_WORLD"+".scaleX"),'sizeZ':0.5*mc.getAttr("tpl_WORLD"+".scaleX")})
            lib_shapes.snapShpCv(shpRef=fk[len(concatIkFk)-lenLsTplMidMb], shpTarget=nJntRig1)
            selShape = mc.listRelatives(nJntRig1, s=True)[0]
            recCv = mc.ls(selShape + '.cv[*]', fl=True)
            mc.scale(1.2,1.2,1.2, recCv)
            # CREATE CONSTRAINT TO MIDDLE MEMBER_______________________________________
            lastJtMb = lsChainFk[len(concatIkFk)-lenLsTplMidMb]
            nCnsPart = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nFunc=gloss.lexicon('cns')+ gloss.lexicon('jt'),
                                         nSide=side,incP=incPart)
            # CREATE GRP CONSTRAINT__________________________________
            libRig.createObj(partial(mc.group, **{'n': nCnsPart, 'em': True}),match=[lastJtMb], father=nJntRig1,
                             attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            # add Attributes ___________________________________________________________________________________________
            for i, each in enumerate(nLsFk[:len(concatIkFk)-lenLsTplMidMb]):
                mc.addAttr(each ,ln="followRoot",nn="Follow Root", at="double", min=0, max=10, dv=0)
                mc.setAttr(each  +".followRoot", e=True, k=True)
                mc.addAttr(each ,ln="stretch",nn="Stretch", at="double")
                mc.setAttr(each  +".stretch", e=True, cb=True)
                mc.addAttr(each ,ln="squash",nn="Squash", at="double")
                mc.setAttr(each  +".squash", e=True, cb=True)
                mc.addAttr(each ,ln="parentScale",nn="Parent Scale",at="bool",dv=0)
                mc.setAttr(each  +".parentScale", e=True, k=True)
            # CREATE CONSTRAINT TO MEMBER_______________________________________________________________________________
            # NAME___________________________________________________
            hookMb = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name, nSide=side,incP=incPart)
            #nHookSpine = gloss.name_format(prefix=gloss.lexicon('hook'),name=self.name,nFunc=gloss.lexicon('spine'),nSide=side,incP=incPart)
            nConsSpine = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name, nSide=side,incP=incPart)
            nRootO = gloss.name_format(prefix=gloss.lexicon('o'),name=self.name, nSide=side,incP=incPart)
            nRootshoulder = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameStart, nSide=side,incP=incPart)

            # CREATE____________________________________________________________________________________________________
            # INSPECT IF SPINE EXIST_________________________________
            """ names """
            nInspect = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('spine'),nSide=side,incP=incPart)
            # create ###
            if mc.objExists(nInspect) == True:
                "!!!!!!!!!!!!WARNING A DEBUG !!!!!!!!!!!!!!!!!"
                objMatch = nInspect
            else:
                objMatch = self.nFly
            # creer root ###
            hookMb =libRig.createObj(partial(mc.joint, **{'n':hookMb}),match=[objMatch],father=self.nRig,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            #hookSpine = libRig.createObj(partial(mc.joint, **{'n':nHookSpine}),match=[objMatch],father=hook,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            consSpine = libRig.createObj(partial(mc.group, **{'n':nConsSpine, 'em': True}),match=[nLsFk[0]],father=hookMb,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            RootO =libRig.createObj(partial(mc.joint, **{'n':nRootO}),match=[nLsFk[0]],father=nLsFk[0],attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2,"rotateOrder":lsRotOrder[0]})
            RootShoulder =libRig.createObj(partial(mc.joint, **{'n':nRootshoulder}),match=[nLsFk[0]],father=RootO,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2,"rotateOrder":lsRotOrder[0]})

            mc.parent(RootO, w=True)
            mc.parent(nLsFk[0],RootShoulder)
            mc.parent(RootO,consSpine)

            # CREATE IK CONTROL_________________________________________________________________________________________
            # NAME___________________________________________________
            nIkRoot = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nIkBuf = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nIk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nDstDimCns= gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nDstDim = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nOrientIk = gloss.name_format(prefix=gloss.lexicon('o'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            # ADJUST ROTATE ORDER____________________________________
            rotOrdIk = libRgPreset.configAxis(mb="rOrdLeg")["rOrdIk"]
            if self.name == "arm":
                rotOrdIk = libRgPreset.configAxis(mb="rOrdArm")["rOrdIk"]
            # create buf Ik for retract system ###
            hookIk =libRig.createObj(partial(mc.group, **{'n':nIkRoot,'em': True}),match=[mc.getAttr(eachTpl+'.ik[1]')],father=self.nRig)
            if self.name == "arm":
                if side != 'R':
                    mc.rotate(0,0,-90,hookIk, r=True,os=True,fo=True)
                else:
                    mc.rotate(0,0,90,hookIk, r=True,os=True,fo=True)
            ikBuf =libRig.createObj(partial(mc.group, **{'n':nIkBuf,'em': True}),match=[hookIk],father=hookIk,attributs={"rotateOrder":rotOrdIk})
            ikCtr = libRig.createController(name=nIk,shape=libRig.Shp([self.typeCircle],color=valColorCtrIK,size=(1,1,1)),match=[hookIk], father=ikBuf,attributs={"rotateOrder":rotOrdIk,"drawStyle": 2})
            dstDimCns =libRig.createObj(partial(mc.group, **{'n':nDstDimCns,'em': True}),match=[hookIk],father=ikCtr['c'])
            dstDimMbEnd =libRig.createObj(partial(mc.group, **{'n':nDstDim,'em': True}),match=[hookIk],father=RootO)
            #mc.addAttr(dstDim, ln=naming.autoClavReparent, at='bool', dv=True)
            # CREATE LOC TO CONNECT DISTANCE DIM______________________
            mc.pointConstraint(dstDimCns, dstDimMbEnd)
            # CREATE ORIENT IK________________________________________
            OrientIk =libRig.createObj(partial(mc.group, **{'n':nOrientIk, 'em': True}),match=[hookIk],father=ikBuf,attributs={"rotateOrder":rotOrdIk})
            getRot = mc.xform(self.nWorld, q=True, ws=True, rotation=True)
            mc.xform(OrientIk, worldSpace=True, ro=getRot)
            # SNAP SHAPE TPL FK______________________________________
            lib_shapes.snapShpCv(shpRef=mc.getAttr(eachTpl+'.ik[1]'), shpTarget=ikCtr['c'])
            mc.parent(ikCtr['root'],OrientIk)
            # CONNECT SCALE ROOT FK TWIST WITH IK CONTROL__________
            if self.name == "arm":
                mc.connectAttr(ikCtr['c'] + ".scaleX", nJntFirst+'.scaleY')
                mc.connectAttr(ikCtr['c'] + ".scaleY", nJntFirst+'.scaleZ')
                mc.connectAttr(ikCtr['c'] + ".scaleZ", nJntFirst+'.scaleX')
            else:
                mc.connectAttr(ikCtr['c'] + ".scaleX", nJntFirst+'.scaleZ')
                mc.connectAttr(ikCtr['c'] + ".scaleY", nJntFirst+'.scaleX')
                mc.connectAttr(ikCtr['c'] + ".scaleZ", nJntFirst+'.scaleY')
            # CREATE LOCATOR OPTION TO DRIVE IK________________________________________
            nLocRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameEnd,nFunc='locIk', nSide=side,incP=incPart)
            rootLocCtr =libRig.createObj(partial(mc.group, **{'n':nLocRoot, 'em': True}),match=[hookIk],father=OrientIk,attributs={"rotateOrder":rotOrdIk})
            nCtrLoc = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameEnd,nFunc='locIk', nSide=side,incP=incPart)
            ctrLoc = libRig.createObj(partial(mc.spaceLocator, **{'n':nCtrLoc}),match=[rootLocCtr],father=rootLocCtr,attributs={"visibility":0,"rotateOrder":rotOrdIk})

            # CONNECT ORIENT IK_________________________________________________________________________________________
            # name
            nMDLOrtIk = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nMDLInvert = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('ik')+'Invert', nSide=side,incP=incPart)
            nPBld = gloss.name_format(prefix=gloss.lexicon('pBlend'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            nAddDblLinIk = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('ik'), nSide=side,incP=incPart)
            # create
            mDLOrtIk = mc.createNode('multDoubleLinear', n=nMDLOrtIk)
            mDLInvert = mc.createNode('multDoubleLinear', n=nMDLInvert)
            pBld = mc.createNode('pairBlend', n=nPBld)
            addDblLinIk = mc.createNode('addDoubleLinear', n=nAddDblLinIk)
            for attr in ('X', 'Y', 'Z'):
                valOrt = mc.getAttr(OrientIk+'.rotate'+attr)
                mc.setAttr(pBld+'.inRotate'+attr+'1', valOrt)
            mc.connectAttr(shapeAttrib + ".orientIK", mDLOrtIk+'.input1')
            mc.setAttr(mDLOrtIk+'.input2', 0.1)
            mc.setAttr(addDblLinIk+'.input2', -1)
            mc.connectAttr(mDLOrtIk+'.output',addDblLinIk+'.input1')
            mc.setAttr(mDLInvert+'.input2', -1)
            mc.connectAttr(addDblLinIk+'.output',mDLInvert+'.input1')
            mc.connectAttr(mDLInvert+'.output',pBld+'.weight')
            mc.setAttr(pBld+'.rotateMode', 0)
            mc.setAttr(pBld+'.rotInterpolation', 1)
            mc.connectAttr(pBld+'.outRotate', ikCtr['root']+'.r')

            # ADD ATTRIBUTES TO CTR IK__________________________________________________________________________________
            mc.addAttr(ikCtr['c'], ln="twist", nn="Twist", at="double", dv=0)
            mc.setAttr(ikCtr['c'] + ".twist", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="soft", nn="Soft", at="double", min=0, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".soft", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="stretch", nn="Stretch", at="double", min=0, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".stretch", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="retract", nn="Retract", at="double", min=0, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".retract", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="squash", nn="Squash", at="double", min=0, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".squash", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="squashRate", nn="Squash Rate", at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".squashRate", e=True, cb=True)
            mc.addAttr(ikCtr['c'], ln="softDistance", nn="Soft Distance", at="double", min=0, max=1, dv=0.1)
            mc.setAttr(ikCtr['c'] + ".softDistance", e=True, cb=True)
            mc.addAttr(ikCtr['c'], ln="stomp", nn="Stomp", at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".stomp", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="roll" , nn="Roll", at="double",min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".roll" , e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="rollBreak" , nn="RollBreak", at="double",min=0, max=10, dv=10)
            mc.setAttr(ikCtr['c'] + ".rollBreak" , e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="rollOffset" , nn="RollOffset", at="double",min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".rollOffset" , e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="ballRoll", nn="Ball Roll", at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".ballRoll", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="ballPivot", nn="Ball Pivot", at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".ballPivot", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="knotRoll" , nn="Knot Roll" , at="double",min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".knotRoll", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="knotPivot", nn="Knot Pivot" , at="double",min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".knotPivot", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="%sRoll" % (self.nameKnot2), nn="%s Roll" % (self.nameKnot2), at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".%sRoll" % (self.nameKnot2), e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="bank", nn="Bank", at="double", min=-10, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".bank", e=True, k=True)
            mc.addAttr(ikCtr['c'], ln="poleVector", nn="Pole Vector", at="enum", en=".:")
            mc.setAttr(ikCtr['c'] + ".poleVector", e=True, cb=True)
            mc.addAttr(ikCtr['c'], ln="follow%s" % (self.nameEnd), nn="Follow %s" % (self.nameEnd),at="double", min=0, max=10, dv=0)
            mc.setAttr(ikCtr['c'] + ".follow%s" % (self.nameEnd), e=True, k=True)
            for each in range(int(numbPart)+1):
                mc.addAttr(ikCtr['c'], ln="stretchPart%s"%(int(each)+1), nn="StretchPart%s"%(int(each)+1), at="double", dv=0)
                mc.setAttr(ikCtr['c'] + ".stretchPart%s"%(int(each)+1), e=True, k=True)

            # IK HANDLE POLE VECTOR_____________________________________________________________________________________
            # name_____________________________________________
            nTampDistDim = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nJntPlV1 = gloss.name_format(prefix=gloss.lexicon('jt'),name=self.name,nFunc=gloss.lexicon('plV')+"1", nSide=side,incP=incPart)
            nJntPlV2 = gloss.name_format(prefix=gloss.lexicon('jt'),name=self.name,nFunc=gloss.lexicon('plV')+"2", nSide=side,incP=incPart)
            nIkHdlPlV = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nTampPlVRoot = gloss.name_format(prefix=gloss.lexicon('plV'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nUpVRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('upV'), nSide=side,incP=incPart)
            nTampPlV = gloss.name_format(prefix=gloss.lexicon('upV'),name=self.name,nFunc=gloss.lexicon('upV'), nSide=side,incP=incPart)
            nPlV = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nIkHdlMb = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nSide=side,incP=incPart)
            nExpTwistFollow = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="twistFollow", nSide=side,incP=incPart)
            nExpIkBlend = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="iKBlend", nSide=side,incP=incPart)
            nExpStretch = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="stretch", nSide=side,incP=incPart)
            # creer un group tamp pour connecter la distance dim et le syst de poleVector ###
            dstDimMb = libRig.createObj(partial(mc.group, **{'n':nTampDistDim , 'em': True}),match=[lsTplIk[0]],father=consSpine,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            #mc.addAttr( dstDimMb, ln=naming.autoClavReparent, at='bool', dv=True)
            mc.pointConstraint(fk[0],dstDimMb)
            # create chain joints to poleVector_______________________________
            chainPlV = libRig.chainJoint(lstChain=[lsTplIk[0],lsTplIk[-1]],lstNameChain=[nJntPlV1,nJntPlV2], lsRotOrder=None,aim=aimFk, upV=upVFk,convertChain=True,shape=None)
            mc.parent(chainPlV[0],dstDimMb)
            [mc.setAttr(each+'.drawStyle',2) for each in chainPlV]
            # create ik handle to poleVector__________________________________
            ikHdlPlV = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlPlV ,'sj':chainPlV[0],'ee':chainPlV[1],'sol':self.IkType}),
                       match=[lsTplIk[-1]],father=dstDimMbEnd,attributs={"snapEnable": 0,"poleVectorX":0,"poleVectorY":0,"poleVectorZ":0,"visibility":0})
            # root tampPoleVector ###
            rootTampPoleV = libRig.createObj(partial(mc.spaceLocator, **{'n':nTampPlVRoot}),match=[chainPlV[0]],father=chainPlV[1],attributs={"visibility":0})
            mc.pointConstraint(ikCtr['c'], rootTampPoleV)
            mc.pointConstraint(dstDimMb, rootTampPoleV)

            # creer SystemConnect poleVector___________________________________
            rootUpV = libRig.createObj(partial(mc.spaceLocator, **{'n':nUpVRoot}),match=[rootTampPoleV],father=rootTampPoleV,attributs={"visibility":0})
            lsPlVCtr =[]
            lsPlVRoot = []
            lsCrvTmp =[]

            # PAIR___________________________________
            countCtr = 1
            if int(numbPart) %2 ==0:
                if int(numbPart) == 2:
                    countCtr = 1
            for k, each in enumerate(concatPlV):
                if k == 0:
                    pass
                else:
                    nTampPlV = gloss.name_format(prefix=gloss.lexicon('upV'),name=self.name,nFunc=gloss.lexicon('upV')+str(k+1), nSide=side,incP=incPart)
                    nPlV = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('plV')+str(k+1), nSide=side,incP=incPart)

                TampPoleV = libRig.createObj(partial(mc.spaceLocator, **{'n': nTampPlV}),match=[concatPlV[k]],father=rootUpV)

                # CREATE POLE VECTOR_________________________________
                plV = libRig.createController(name=nPlV,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)),
                                                match=[concatPlV[k]], father=RootO,attributs={"drawStyle":2})

                # SNAP SHAPE TPL PLV__________________________________
                lib_shapes.snapShpCv(shpRef=concatPlV[k], shpTarget=plV['c'])
                # create Attribute pinch_________________________________
                mc.addAttr(plV['c'], ln="pinch", nn="Pinch", at="double", min=0, max=10, dv=0)
                mc.setAttr(plV['c'] + ".pinch", e=True, k=True)
                # connection rootPoleVector with tampPoleVector ###
                mc.parentConstraint(TampPoleV,plV['root'])

                # CREATE CRV SHAPE BETWEEN ELBOW POLE VECTOR________________________________________________________________
                lsToCrv =[fk[countCtr],plV['sk']]
                positions = [mc.xform(each, q=True, ws=True, translation=True) for each in lsToCrv]
                nCrvPoleV = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('plV'),nSide=side,incP=incPart)
                createCrvTmp = mc.curve(n=nCrvPoleV, p=positions, d=1)
                mc.skinCluster(lsToCrv, createCrvTmp, tsb=1, mi=1)
                mc.setAttr(createCrvTmp +".template",1)
                mc.setAttr(createCrvTmp +".inheritsTransform",0)
                lsPlVCtr.append(plV['c'])
                lsPlVRoot.append(plV['root'])
                lsCrvTmp.append(createCrvTmp)

                if int(numbPart) %2 ==0:
                    if k+2 < int(len(concatPlV)):
                        countCtr += 2
                    else:
                        countCtr += 1
                else:
                    countCtr += 2

            # CREATE IK HANDLE__________________________________________________________________________________________
            recuppointConsWeight =[]
            if(self.IkType != 'ikSplineSolver'):
                #print nIkHdlMb
                ikHandle = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlMb ,'sj':fk[0],'ee':lsChainFk[len(concatIkFk)-lenLsTplMidMb],'sol':self.IkType}),match=[lsTplIk[-1]],father=RootO,attributs={"snapEnable": 0,"visibility":0})
                pointCnsdstDimMb = mc.pointConstraint(dstDimMb,ikHandle,w=0)
                firstAimCons = mc.listConnections(mc.listRelatives(ikHandle, type="constraint")[0]+ ".target", p=True)[-1]
                recuppointConsWeight.append(firstAimCons)
                pointCnscreateTpDistDim = mc.pointConstraint(dstDimMbEnd,ikHandle,w=1)
                secondAimCons = mc.listConnections(mc.listRelatives(ikHandle, type="constraint")[0]+ ".target", p=True)[-1]
                recuppointConsWeight.append(secondAimCons)
                plCns = mc.poleVectorConstraint(lsPlVCtr[0], ikHandle)
                #recupIntIkHandle.append(ikHandle)
            else:
                pass

            # CONNECTION FOLLOW HAND_____________________________________________________________________________________
            nMltDivFollowH1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='followH'+'Div',nSide=side,incP=incPart)
            nMltDivFollowH2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='followH'+'Mlt',nSide=side,incP=incPart)
            mltDivFollowH1 = mc.createNode("multiplyDivide", n=nMltDivFollowH1)
            mc.setAttr(mltDivFollowH1+ ".operation", 2)
            mc.setAttr(mltDivFollowH1 + ".input2X",10)
            mc.connectAttr(ikCtr['c'] + ".follow%s"%(self.nameEnd), "%s.input1X" % (mltDivFollowH1), force=True)
            mltDivFollowH2 = mc.createNode("multiplyDivide", n=nMltDivFollowH2)
            mc.setAttr(mltDivFollowH2 + ".operation", 1)
            val ="X"
            if self.name == 'leg':
                val ="Y"
                if side == "L":
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='followH'+'Neg',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(ikCtr['c'] + ".follow%s"%(self.nameEnd), "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivFollowH1), force=True)
            mc.connectAttr(ikCtr['c']+ ".rotate%s"%(val), "%s.input1X" % (mltDivFollowH2), force=True)
            mc.connectAttr(mltDivFollowH1 + '.outputX', "%s.input2X" % (mltDivFollowH2), force=True)

            # CONNECTION FOLLOW HAND2
            nMltDivFollow = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='followIk'+'Div',nSide=side,incP=incPart)
            nMltDblLinFollow = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='followIk'+'Neg',nSide=side,incP=incPart)
            nAddDblLScl = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.nameEnd,nFunc='followIk', nSide=side,incP=incPart)
            nFollowTamp = gloss.name_format(prefix=gloss.lexicon('rot'),name=self.nameEnd,nFunc='followIk',nSide=side,incP=incPart)

            followTamp = libRig.createObj(partial(mc.group, **{'n':nFollowTamp,'em': True}),match=[rootUpV],father=ikCtr['c'])
            getRotateWeight =[]
            rotateCnsFollow = mc.orientConstraint(rootTampPoleV,rootUpV,w=0)
            firstrotateCnsFollow = mc.listConnections(mc.listRelatives(rootUpV, type="constraint")[0]+ ".target", p=True)[-1]
            getRotateWeight.append(firstrotateCnsFollow)
            rotaterotateCnsFollow2 = mc.orientConstraint(followTamp,rootUpV,w=1)
            secondrotateCnsFollow2 = mc.listConnections(mc.listRelatives(rootUpV, type="constraint")[0]+ ".target", p=True)[-1]
            getRotateWeight.append(secondrotateCnsFollow2)
            mc.setAttr(rotateCnsFollow[0]+ ".interpType", 2)

            mltDivFollow = mc.createNode("multiplyDivide", n=nMltDivFollow)
            mc.setAttr(mltDivFollow+ ".operation", 2)
            mc.setAttr(mltDivFollow + ".input2X",10)
            mc.connectAttr(ikCtr['c'] + ".follow%s"%(self.nameEnd), "%s.input1X" % (mltDivFollow), force=True)
            NodeMltDblLFollow = mc.createNode("multDoubleLinear", n=nMltDblLinFollow)
            mc.setAttr(NodeMltDblLFollow + ".input2", -1)
            mc.connectAttr(mltDivFollow + '.outputX', "%s.input1" % (NodeMltDblLFollow), force=True)
            nodeAddDLFollow = mc.shadingNode("addDoubleLinear",n=nAddDblLScl,asUtility=True)
            mc.setAttr("%s.input2" % (nodeAddDLFollow), 1)
            mc.connectAttr(NodeMltDblLFollow+ '.output', "%s.input1" % (nodeAddDLFollow), force=True)

            mc.connectAttr(nodeAddDLFollow + '.output', getRotateWeight[0], force=True)
            mc.connectAttr(mltDivFollow + '.outputX', getRotateWeight[1], force=True)



            #mc.connectAttr(mltDivFollowH2 + '.outputX', "%s.rotateY" %(rootUpV), force=True)

            # CONNECTION TWIST_____________________________________________________________________________________
            nMltDivTwist1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='twist'+'FollowDiv',nSide=side,incP=incPart)
            nMltDivTwist2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='twist'+'FollowMlt',nSide=side,incP=incPart)

            if side == "R" :
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='twist'+'FollowNeg',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(ikCtr['c']+".twist", "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.twist" %(ikHandle), force=True)
            else:
                mc.connectAttr(ikCtr['c']+".twist", "%s.twist" %(ikHandle), force=True)

            # check if lsTplCtrOnly is > 1 and add position value < 0 to create a add node between twist
            valuesTrsZ = [mc.getAttr(each+'.translateZ') for each in lsTplCtrOnly]
            if mc.getAttr(concatPlV[0]+'.translateZ') > 0 and len(lsTplCtrOnly)%2 ==0:
                if sum(valuesTrsZ)<0:
                    nAddDblLTwist = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.nameEnd, nFunc='twist',nSide=side, incP=incPart)
                    nodeAddDLTwist = mc.shadingNode("addDoubleLinear", n=nAddDblLTwist, asUtility=True)
                    mc.setAttr("%s.input2" % (nodeAddDLTwist), 180)
                    mc.connectAttr(ikCtr['c']+".twist", "%s.input1" % (nodeAddDLTwist), force=True)
                    mc.connectAttr(nodeAddDLTwist + '.output', "%s.twist" % (ikHandle), force=True)



            # CONNECTION IK BLEND WITH CTR IK___________________________________________________________________________
            nIkBlend= gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('ikBlend'), nSide=side,incP=incPart)
            mDLIkBlend = mc.createNode('multDoubleLinear', n=nIkBlend)
            mc.setAttr(mDLIkBlend+'.input2', .1)
            mc.connectAttr(shapeAttrib + '.ikBlend', mDLIkBlend+'.input1')
            mc.connectAttr(mDLIkBlend + '.output', ikHandle+'.ikBlend')
            mc.connectAttr(mDLIkBlend  + '.output', ikHandleFirst+'.ikBlend')
            cndBlend = mc.createNode('condition', n='cnd_ikBlend')
            mc.setAttr(cndBlend + '.secondTerm', 1)
            mc.setAttr(cndBlend + '.operation', 0)
            mc.setAttr(cndBlend + '.colorIfTrueR', 1)
            mc.setAttr(cndBlend + '.colorIfFalseR', 0)
            mc.connectAttr(mDLIkBlend + '.output', cndBlend + '.firstTerm')
            #mc.connectAttr(cndBlend + '.outColorR', ikWrist[0] + '.ikBlend')

            # CONNECTION SYSTEM SQUASH RATE_____________________________________________________________________________
            nMltDLinSquash= gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nSide=side,incP=incPart)
            nodeMltDLinSquash = mc.shadingNode("multDoubleLinear",n=nMltDLinSquash,asUtility=True)
            mc.setAttr("%s.input2" % (nodeMltDLinSquash), -0.15)
            mc.connectAttr("%s.squashRate" % (ikCtr['c']), "%s.input1" % (nodeMltDLinSquash), force=True)
            nAddDLinSquash= gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.name,nSide=side,incP=incPart)
            nodeAddDLinSquash = mc.shadingNode("addDoubleLinear",n=nAddDLinSquash,asUtility=True)
            mc.setAttr("%s.input2" % (nodeAddDLinSquash), -0.5)
            mc.connectAttr("%s.output" % (nodeMltDLinSquash), "%s.input1" % (nodeAddDLinSquash), force=True)

            # STRETCH MEMBER____________________________________________________________________________________________
            # get aim axis chain jnts
            getAxis = {}
            for each in aimFk:
                if aimFk[0] != 0:
                    getAxis ='X'
                elif aimFk[1] != 0:
                    getAxis ='Y'
                elif aimFk[2] != 0:
                    getAxis ='Z'
            # get totale value aim axis chain jnts
            concatValChainJnt = 0
            for i, each in enumerate(lsChainFk[1:len(concatIkFk)-(lenLsTplMidMb-1)]):
                concatValChainJnt += float(mc.getAttr(each+".translate%s"%(getAxis)))

            # CREATE DISTANCE DIMENSION_________________________________________________________________________________
            # create group No Touch
            nNoTouch = gloss.name_format(prefix=gloss.lexicon('NoTouch'),name=self.name,nSide=side,incP=incPart)
            GrpNoTouch = libRig.createObj(partial(mc.group, **{'n':nNoTouch , 'em': True}),father=hookMb)
            ## Distance Dimension
            getPos = [mc.xform(each , q=True, ws=True, translation=True) for i, each in enumerate((RootO,ikCtr['c']))]
            nNodeDstDim = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('info'),nSide=side,incP=incPart)
            distDim = mc.distanceDimension( sp=(getPos[0][0],getPos[0][1],getPos[0][2]), ep=(getPos[-1][0],getPos[-1][1],getPos[-1][2]))
            rootDstDim = mc.pickWalk(distDim, d='up')
            mc.rename(rootDstDim,nNodeDstDim)
            mc.parent(nNodeDstDim,GrpNoTouch)
            [mc.parent(each,GrpNoTouch)for each in lsCrvTmp]
            mc.setAttr (nNodeDstDim+".visibility", 0)
            getLoc =  mc.listConnections(nNodeDstDim)
            NodeDecompMatrix = mc.shadingNode( "decomposeMatrix",n="decMatDistDim_%s_%s_%s"%(self.name,side,incPart), asUtility=True)
            NodeDecompMatrix2 = mc.shadingNode( "decomposeMatrix",n="decMatDistDim2_%s_%s_%s"%(self.name,side,incPart), asUtility=True)
            mc.connectAttr("%s.worldMatrix[0]" %(dstDimMb), "%s.inputMatrix" %(NodeDecompMatrix),force=True)
            mc.connectAttr( "%s.outputTranslate" %(NodeDecompMatrix), "%s.startPoint" %(nNodeDstDim),force=True)
            mc.connectAttr("%s.worldMatrix[0]" %(dstDimMbEnd), "%s.inputMatrix" %(NodeDecompMatrix2),force=True)
            mc.connectAttr( "%s.outputTranslate" %(NodeDecompMatrix2), "%s.endPoint" %(nNodeDstDim),force=True)

            # create NodeMultDoubleLinear to drive scale of sk ###
            ############## WARNING PART TO CONNECT SK ############################
            recupMultDbleLinScale1 =[]; recupMultDbleLinScale2 =[]
            count = ""
            for u, each in enumerate(lsChainFk[:len(concatIkFk)-(lenLsTplMidMb)]):
                if u == 0:
                    nameExp = self.nameStart
                elif u == 0:
                    nameExp = self.nameMid
                else:
                    nameExp = self.nameMid
                    count=str(u-1)
                """ names """
                nameExpr = gloss.name_format(prefix=gloss.lexicon('mltDblLin')+"%s"%1,name=nameExp+count,nFunc=gloss.lexicon('scl')+count,nSide=side,incP=incPart)
                nameExpr2 = gloss.name_format(prefix=gloss.lexicon('mltDblLin')+"%s"%2,name=nameExp+count,nFunc=gloss.lexicon('scl')+count,nSide=side,incP=incPart)
                # create ###
                MltDblLinScale1 = mc.shadingNode( "multDoubleLinear",n=nameExpr, asUtility=True)
                mc.setAttr( "%s.input1"%(MltDblLinScale1), 1)
                mc.connectAttr("%s.squash" %(each), "%s.input2" %(MltDblLinScale1),force=True)
                MltDblLinScale2 = mc.shadingNode( "multDoubleLinear",n=nameExpr2, asUtility=True)
                mc.setAttr( "%s.input1"%(MltDblLinScale2), 1)
                mc.connectAttr("%s.squash" %(each), "%s.input2" %(MltDblLinScale2),force=True)
                recupMultDbleLinScale1.append(MltDblLinScale1)
                recupMultDbleLinScale2.append(MltDblLinScale2)




            # STRETCH - SOFTIK - SQUASH_________________________________________________________________________________
            valRetract = "*(1-(%s/%s))"%(ikCtr['c']+".retract",10.1)
            nDcpMat = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=self.name,nFunc=gloss.lexicon('squash'),nSide=side,incP=incPart)
            dcpMat= mc.shadingNode("decomposeMatrix", n=nDcpMat, asUtility=True)
            mc.connectAttr((RootO + ".worldMatrix[0]"), (dcpMat+ ".inputMatrix"))
            valStretch= ""
            varStringStretch = "// STRETCH"
            varStretch = "float $cstretch = %s/%s;" %(ikCtr['c']+".stretch" ,self.valAttrAdjust)
            varSoft = "float $csoft = %s/%s;" %(ikCtr['c']+".soft" ,self.valAttrAdjust)
            varSquash = "float $csquash = %s/%s;" %(ikCtr['c']+".squash" ,self.valAttrAdjust)
            varDistance = "float $d = float(%s.distance);" %(nNodeDstDim)
            concatScale = ""
            concatChain = "float $dchain = (0"
            varF = "float $f = 1;"
            varW = "float $w = 1;"
            varCondition1 = "if ($d>$dchain%s) $w=$dchain/$d;" %(valRetract)
            varSoftF = "float $fsoft = 1;"
            varSoftW = "float $wsoft = 1;"
            expSoft = "if($csoft>0) {\n float $dsoft=%s;\n float $ds=$dsoft*$dchain;\n float $da=$dchain-$ds;\n float $deff=$d;\n if($d>=$da) $deff=$ds*(1-exp(-1*($d-$da)/$ds))+$da;\n " %(ikCtr['c'] +".softDistance")
            expSoft2 = expSoft + "$wsoft=$deff/$d;\n $w=(1-$csoft)*$w+$csoft*$wsoft;\n $fsoft=1/$w;\n $w=$cstretch+(1-$cstretch)*$w;\n"
            expSoft3 = expSoft2 + " %s=1-$w;\n %s=$w;\n}" %(recuppointConsWeight[0],recuppointConsWeight[1]) + " else {\n %s=0;\n %s=1;\n}\n" %(recuppointConsWeight[0],recuppointConsWeight[1])
            ######################################################################
            expStretch ="if($cstretch>0) {\n if($d>$dchain)"+" $f=(1-$cstretch + $cstretch*$d/$dchain);\n $fsoft=((1-$cstretch)+$fsoft*$cstretch);\n"+" $f=$f*(1-$csoft)+$fsoft*($csoft);\n} "
            expSquash = "float $sAim=1;\nfloat $sUp=1;"
            getSquash = ""
            countExp =1

            normalizer = 10
            for z, each in enumerate(lsChainFk[1:len(concatIkFk)-(lenLsTplMidMb-1)]):
                if side == "L":
                    varScale = "float $cscale%s = %s;\n" %(z+1,fk[z]+(".scale%s"%(getAxis)))
                    concatScale += varScale
                    varScale2 = "%s" %(fk[z]+(".scale%s"%(getAxis)))
                    varLength ="%s" %(float(mc.getAttr(each+ ".translate%s"%(getAxis))))
                    concatChain += " + %s" %(varLength) +"*$cscale%s" %(z+1)
                elif side == "R":
                    normalizer = -10
                    varScale = "float $cscale%s = %s;\n" %(z+1,fk[z]+(".scale%s"%(getAxis)))
                    concatScale += varScale
                    varScale2 = "%s" %(fk[z]+(".scale%s"%(getAxis)))
                    varLength ="%s" %(abs(float(mc.getAttr(each+ ".translate%s"%(getAxis)))))
                    concatChain += " + %s" %(varLength) +"*$cscale%s" %(z+1)

                squatch ="\n$sAim=$f*$cscale%s;\n$sUp=1;\n" %(z+1)
                squash2 = squatch + "if($csquash>0) $sUp=1-$csquash+$csquash*pow($sAim,%s.output);\n" %(nodeAddDLinSquash)

                ValT =float(mc.getAttr(each+ ".translate%s"%(getAxis)))
                stretchPart = "+(%s/%s)"%(ikCtr['c'] + ".stretchPart%s"%countExp,normalizer)
                part = "%s.translate%s ="%(each,getAxis) + str(ValT)+"*$f%s" %(valRetract)+ stretchPart +" ;\n"
                getSquash += squash2 + part +"%s.stretch=$sAim;\n%s.squash=$sUp;\n" %(fk[z],fk[z])
                countExp +=1
            concatChain += ")*%s.outputScaleY%s"%(dcpMat,valRetract)
            concatExprPart1 = "%s\n%s\n%s\n%s\n%s%s\n%s;\n%s\n%s\n%s\n%s\n%s\n"%(varStringStretch,varStretch,varSoft,varSquash,concatScale,varDistance,concatChain,varF,varW,varCondition1,varSoftF,varSoftW)
            concatExprPart2 = concatExprPart1 + "%s\n%s\n%s\n%s\n"%(expSoft3,expStretch,expSquash,getSquash)

            expSysStretch = mc.expression(s= concatExprPart2 ,n=nExpStretch)

            # CREATE DISTANCE DIMENSION TO PINCH SYSTEM_________________________________________________________________
            valScl= mc.getAttr("tpl_WORLD"+".scaleX")
            lsPlVBuf = []
            lsMltDivPinch = []
            for i, each in enumerate(concatPlV):
                # create buf to ctr pinch
                nPinchBuf = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name,nFunc=gloss.lexicon('pinch')+str(i+1),nSide=side,incP=incPart)
                pinchBuf = libRig.createObj(partial(mc.group, **{'n': nPinchBuf, 'em': True}), match=[fk[1]], father=lsPlVCtr[i],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                lsPlVBuf.append(pinchBuf)
                # create mltDiv
                nMltDivPinch = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('pinch')+str(i+1),nSide=side,incP=incPart)
                mltDivPinch = mc.createNode("multiplyDivide", n=nMltDivPinch)
                mc.setAttr(mltDivPinch + ".operation", 2)
                mc.setAttr(mltDivPinch + ".input2X",10)
                mc.connectAttr(lsPlVCtr[i]+".pinch", "%s.input1X" % (mltDivPinch), force=True)
                lsMltDivPinch.append(mltDivPinch)

            # create ctr pinch
            lsCnsSk = [dstDimMb]
            for j, each in enumerate(concatPlV):
                nPinch = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name,nFunc=gloss.lexicon('pinch')+str(j+1),nSide=side,incP=incPart)
                pinch = libRig.createController(name=nPinch,shape=libRig.Shp(['sphere'],color=valColorAdd ,size=(0.2*valScl,0.2*valScl,0.2*valScl)),
                match=[lsPlVBuf[j]], father=lsPlVBuf[j],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder":lsRotOrder[0],"drawStyle": 2})
                mc.setAttr(pinch['c'] + ".visibility",0)
                lsCnsSk.append(pinch['sk'])
            lsCnsSk.append(dstDimMbEnd)

            ## create Distances Dimensions
            lsDistDim = []
            lsBlendColor =[]
            for k, each in enumerate(lsCnsSk[:-1]):
                getPos = [mc.xform(each2 , q=True, ws=True, translation=True) for j, each2 in enumerate((each,lsCnsSk[k+1]))]
                nDstDimPart = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name+str(i+1),nFunc=gloss.lexicon('info')+str(k+1),nSide=side,incP=incPart)
                distDimPart = mc.distanceDimension( sp=(getPos[0][0],getPos[0][1],getPos[0][2]), ep=(getPos[-1][0],getPos[-1][1],getPos[-1][2]))
                rootDstDimPart = mc.pickWalk(distDimPart, d='up')
                mc.rename(rootDstDimPart,nDstDimPart)
                mc.setAttr(nDstDimPart + ".visibility",0)
                getLoc =  mc.listConnections(nDstDimPart)
                NodDecompMatrix = mc.shadingNode( "decomposeMatrix",n="decMatDistDim_%s%s_%s_%s"%(self.name,(k+1),side,incPart), asUtility=True)
                NodDecompMatrix2 = mc.shadingNode( "decomposeMatrix",n="decMatDistDim2_%s%s_%s_%s"%(self.name,(k+1),side,incPart), asUtility=True)
                mc.connectAttr("%s.worldMatrix[0]" %(each), "%s.inputMatrix" %(NodDecompMatrix),force=True)
                mc.connectAttr( "%s.outputTranslate" %(NodDecompMatrix), "%s.startPoint" %(nDstDimPart),force=True)
                mc.connectAttr("%s.worldMatrix[0]" %(lsCnsSk[k+1]), "%s.inputMatrix" %(NodDecompMatrix2),force=True)
                mc.connectAttr( "%s.outputTranslate" %(NodDecompMatrix2), "%s.endPoint" %(nDstDimPart),force=True)
                lsDistDim.append(nDstDimPart)
                # create blend color
                nBlendColorPinch = gloss.name_format(prefix=gloss.lexicon('blendCol'),name=self.name,nFunc=gloss.lexicon('pinch')+str(k+1),nSide=side,incP=incPart)
                blendColorPinch = mc.createNode("blendColors", n=nBlendColorPinch)
                mc.connectAttr(lsMltDivPinch[0] +".outputX", "%s.blender" % (blendColorPinch), force=True)
                shpDistDim = mc.listRelatives(nDstDimPart, s=True)[0]
                if side == 'R':
                    nDblinPinch = gloss.name_format(prefix=gloss.lexicon('dblLin'),name=self.name,nFunc=gloss.lexicon('pinch')+str(i+1),nSide=side,incP=incPart)
                    dblinPinch = mc.createNode("multDoubleLinear", n=nDblinPinch)
                    mc.setAttr(dblinPinch + ".input2", -1)
                    mc.connectAttr(shpDistDim  +".distance", "%s.input1" % (dblinPinch), force=True)
                    mc.connectAttr(dblinPinch +".output", "%s.color1R" % (blendColorPinch), force=True)
                else:
                    mc.connectAttr(shpDistDim  +".distance", "%s.color1R" % (blendColorPinch), force=True)
                attrCon = lsChainFk[1:len(concatIkFk)-(lenLsTplMidMb-1)][k]+'.translateY'
                if mc.connectionInfo(attrCon, isDestination=True):
                    getOutPutExp = mc.connectionInfo(attrCon,sourceFromDestination=True)
                    mc.connectAttr(getOutPutExp, "%s.color2R" % (blendColorPinch), force=True)
                mc.connectAttr(blendColorPinch +".outputR", "%s.translateY" % (lsChainFk[1:len(concatIkFk)-(lenLsTplMidMb-1)][k]), force=True)
                lsBlendColor.append(blendColorPinch)



            for each in lsDistDim :
                mc.parent(each,GrpNoTouch)

            for i, each in enumerate(lsPlVBuf):
                pos = mc.xform(concatPlV[i], q=True, ws=True, translation=True)
                rot = mc.xform(concatPlV[i], q=True, ws=True, rotation=True)
                mc.xform(each, worldSpace=True, t=pos)
                mc.xform(each, worldSpace=True, ro=rot)

            if mc.objExists('locator*'):
                mc.delete('locator*')
            else:
                pass

            # LOCK AND HIDE FK CONTROL__________________________________________________________________________________
            lib_attributes.lockAndHideAxis(fk[1:len(concatIkFk)-(lenLsTplMidMb)],transVis=True)

            # LOCK STRETCH TO FK__________________________________________________________________________________
            nCondLock = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('stretch'),nSide=side,incP=incPart)
            condLock = mc.createNode("condition", n=nCondLock)
            mc.setAttr(condLock + ".colorIfTrueG",1)
            mc.setAttr(condLock + ".colorIfFalseG",0)
            mc.setAttr(condLock + ".operation",2)
            mc.setAttr(condLock + ".secondTerm",0)

            mc.connectAttr(shapeAttrib + ".ikBlend","%s.firstTerm" % (condLock), force=True)

            getConstraintPos = mc.listRelatives(dstDimMbEnd, type="constraint")[0]
            cnsPointLock = mc.listConnections(mc.listRelatives(dstDimMbEnd, type="constraint")[0]+ ".target", p=True)[-1]
            mc.connectAttr(condLock + ".outColorG",cnsPointLock, force=True)
            #mc.connectAttr(condLock + ".outColorR","%s.nodeState" % (getConstraintPos), force=True)


            ####################################  NURBS SYSTEM #######################################################
            valScl= mc.getAttr("tpl_WORLD"+".scaleX")
            lsArcRoot = []
            lsArcCtr = []
            lsArcSk = []
            lsArcBindP = []
            lsArcCluster = []
            # CREATE CONTROL ADD IN FIRST PART LEG/ARM_______________________________________
            nCtrArc= gloss.name_format(prefix=gloss.lexicon('c'), name=self.nameStart, nFunc=gloss.lexicon('arc'),nSide=side,incP=incPart)
            ctrArc = libRig.createController(name=nCtrArc,shape=libRig.Shp(['square'],color=valColorAdd ,size=(0.4*valScl,0.4*valScl,0.4*valScl)),
            match=[lsChainFk[0]], father=lsChainFk[0],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder":lsRotOrder[0],"drawStyle": 2})
            nbindPAdd= gloss.name_format(prefix=gloss.lexicon('bindP'), name=self.nameStart, nFunc=gloss.lexicon('add'),nSide=side,incP=incPart)
            bindAdd = libRig.createObj(partial(mc.joint, **{'n': nbindPAdd}), match=[ctrArc['root']], father=ctrArc['root'],
                        attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})

            lsArcRoot.append(ctrArc['root'])
            lsArcCtr.append(ctrArc['c'])
            lsArcSk.append(ctrArc['sk'])
            lsArcBindP.append(bindAdd)
            # JOINT TO ADDITIVE CTR IN ELBOW/KNEE_______________________________________________
            for i, each in enumerate(lsChainFk[1:-1]):
                nJntOri = gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameMid, nFunc=gloss.lexicon('orient')+str(i+1),nSide=side,incP=incPart)
                jntOri = libRig.createObj(partial(mc.joint, **{'n': nJntOri}), match=[each], father=each,
                            attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                # CONNECT JNT ORIENT WITH YOUR FATHER
                getJntOriZ=mc.getAttr(each + '.jointOrientZ')
                divOriZ = -(float(getJntOriZ/2))

                nMltDivJntOr1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameMid,nFunc='JntOr'+str(i+1),nSide=side,incP=incPart)
                mltDivJntOr1 = mc.createNode("multiplyDivide", n=nMltDivJntOr1)
                mc.setAttr(mltDivJntOr1+ ".operation", 2)
                mc.setAttr(mltDivJntOr1 + ".input2X",2)
                mc.connectAttr(each+".rotateZ", "%s.input1X" % (mltDivJntOr1), force=True)
                nMltDblLinJntOr = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameMid,nFunc='JntOr'+str(i+1),nSide=side,incP=incPart)
                NodeMltDblLinearJntOr = mc.createNode("multDoubleLinear", n=nMltDblLinJntOr)
                mc.setAttr(NodeMltDblLinearJntOr + ".input2", -1)
                mc.connectAttr(mltDivJntOr1+".outputX", "%s.input1" % (NodeMltDblLinearJntOr), force=True)

                nAddDblLinJntOr = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameMid,nFunc='JntOr'+str(i+1),nSide=side,incP=incPart)
                addDblLinJntOr = mc.createNode("addDoubleLinear", n=nAddDblLinJntOr)
                mc.setAttr(addDblLinJntOr + ".input1",divOriZ)
                mc.connectAttr(NodeMltDblLinearJntOr+".output", "%s.input2" % (addDblLinJntOr), force=True)
                mc.connectAttr(addDblLinJntOr+'.output',jntOri+".rotateZ", force=True)
                # CREATE CONTROLS ADD LEG/ARM_______________________________________________
                nCtrArc= gloss.name_format(prefix=gloss.lexicon('c'), name=self.nameMid, nFunc=gloss.lexicon('arc')+str(i+1),nSide=side,incP=incPart)
                ctrArc = libRig.createController(name=nCtrArc,shape=libRig.Shp(['square'],color=valColorAdd ,size=(0.4*valScl,0.4*valScl,0.4*valScl)),
                                                                match=[nJntOri], father=nJntOri,attributs={"rotateOrder":lsRotOrder[0],"drawStyle": 2})
                nbindPAdd= gloss.name_format(prefix=gloss.lexicon('bindP'), name=self.nameMid, nFunc=gloss.lexicon('add')+str(i+1),nSide=side,incP=incPart)
                bindAdd = libRig.createObj(partial(mc.joint, **{'n': nbindPAdd}), match=[ctrArc['root']], father=ctrArc['root'],
                            attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsArcRoot.append(ctrArc['root'])
                lsArcCtr.append(ctrArc['c'])
                lsArcSk.append(ctrArc['sk'])
                lsArcBindP.append(bindAdd)

            # CREATE CONTROL ADD IN LAST PART LEG/ARM_______________________________________
            nCtrArc= gloss.name_format(prefix=gloss.lexicon('c'), name=self.nameEnd, nFunc=gloss.lexicon('arc'),nSide=side,incP=incPart)
            ctrArc = libRig.createController(name=nCtrArc,shape=libRig.Shp(['square'],color=valColorAdd ,size=(0.4*valScl,0.4*valScl,0.4*valScl)),
            match=[nJntRig1], father=nJntRig1,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder":lsRotOrder[0],"drawStyle": 2})
            nbindPAdd= gloss.name_format(prefix=gloss.lexicon('bindP'), name=self.nameEnd, nFunc=gloss.lexicon('add'),nSide=side,incP=incPart)
            bindAdd = libRig.createObj(partial(mc.joint, **{'n': nbindPAdd}), match=[ctrArc['root']], father=ctrArc['root'],
                        attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            lsArcRoot.append(ctrArc['root'])
            lsArcCtr.append(ctrArc['c'])
            lsArcSk.append(ctrArc['sk'])
            lsArcBindP.append(bindAdd)

            # CONNECTION WITH ATTRIBUTE ARC______________________________________
            for i, each in enumerate(lsArcCtr[1:-1]):
                nMltDivSkArc = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameMid,nFunc=gloss.lexicon('arc')+'Sk'+str(i+1),nSide=side,incP=incPart)
                mltDivSkArc = mc.createNode("multiplyDivide", n=nMltDivSkArc)
                mc.setAttr(mltDivSkArc + ".operation", 2)
                mc.setAttr(mltDivSkArc + ".input2X",10)
                mc.connectAttr(shapeAttrib + '.arc', "%s.input1X" % (mltDivSkArc), force=True)
                nMltDblLinSkArc = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameMid,nFunc=gloss.lexicon('arc')+'Sk'+str(i+1),nSide=side,incP=incPart)
                NodeMltDblLinearSkArc = mc.createNode("multDoubleLinear", n=nMltDblLinSkArc)
                mc.setAttr(NodeMltDblLinearSkArc + ".input2", -1)
                mc.connectAttr(mltDivSkArc+".outputX", "%s.input1" % (NodeMltDblLinearSkArc), force=True)
                nAddDblLinSkArcX = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameMid,nFunc=gloss.lexicon('arc')+'Sk'+str(i+1)+'X',nSide=side,incP=incPart)
                addDblLinSkArcX = mc.createNode("addDoubleLinear", n=nAddDblLinSkArcX)
                mc.connectAttr(each+".scaleX", "%s.input1" % (addDblLinSkArcX), force=True)
                mc.connectAttr(NodeMltDblLinearSkArc+".output", "%s.input2" % (addDblLinSkArcX), force=True)
                nMltDivSkArc2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameMid,nFunc=gloss.lexicon('arc')+'2'+'Sk'+str(i+1),nSide=side,incP=incPart)
                mltDivSkArc2 = mc.createNode("multiplyDivide", n=nMltDivSkArc2)
                mc.connectAttr(each+".scaleX", "%s.input2X" % (mltDivSkArc2), force=True)
                mc.connectAttr(addDblLinSkArcX+'.output', "%s.input1X" % (mltDivSkArc2), force=True)
                mc.connectAttr(each+".scaleY", "%s.input1Y" % (mltDivSkArc2), force=True)
                mc.connectAttr(each+".scaleZ", "%s.input1Z" % (mltDivSkArc2), force=True)
                mc.connectAttr(mltDivSkArc2+".outputX",lsArcSk[i+1]+".scaleX", force=True)
                mc.connectAttr(mltDivSkArc2+".outputY",lsArcSk[i+1]+".scaleY", force=True)
                mc.connectAttr(mltDivSkArc2+".outputZ",lsArcSk[i+1]+".scaleZ", force=True)

            # CREATE CURVE AND LOFT_______________________________________________
            # NAME _______________________________________________________________
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('SA'), name=self.name, nFunc=gloss.lexicon('loft') + 'Cv',nSide=side, incP=incPart)
            nloftGrp = gloss.name_format(prefix=gloss.lexicon('GRP'), name=self.name,nFunc=gloss.lexicon('loft') + 'Cv', nSide=side, incP=incPart)
            nLoftBase = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc=gloss.lexicon('base'),nSide=side, incP=incPart)
            nLoftCtr = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='Ctr', nSide=side,incP=incPart)
            nLoftBaseSk = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name,nFunc=gloss.lexicon('base') + 'Sk', nSide=side, incP=incPart)
            val = float(mc.getAttr("tpl_WORLD" + ".scaleX"))
            # CREATE GRP SA ______________________________________________________
            sAGrp = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), Match=None, father=self.nSa)
            loftGrp = libRig.createObj(partial(mc.group, **{'n': nloftGrp, 'em': True}), Match=None, father=self.nSa)
            # create Jnt to skin LoftBase
            lsJntLoftBase = []
            for each in lsChainFk:
                nJntCrvSk = gloss.renameSplit(selObj=each, namePart=['c', 'root'], newNamePart=['loftSk', 'loftSk'],reNme=False)
                jntCrvSk = libRig.createObj(partial(mc.joint, **{'n': nJntCrvSk}), match=[each], father=each,
                                 attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsJntLoftBase.append(jntCrvSk)
            # Adjust Parentage to create a good orientation curve
            [mc.parent(each, w=True) for each in lsJntLoftBase]
            [mc.parent(each, lsJntLoftBase[i]) for i, each in enumerate(lsJntLoftBase[1:])]
            getCrv = lib_curves.createDoubleCrv(objLst=lsJntLoftBase, axis='Z', offset=0.2 * val)
            [mc.parent(each, lsChainFk[i]) for i, each in enumerate(lsJntLoftBase)]

            # create loftBase____________________________________________
            loftBase = lib_curves.createLoft(name=nLoftBase, objLst=getCrv['crv'], father=GrpNoTouch, deleteCrv=False)
            mc.setAttr(loftBase + ".visibility", 0)
            mc.skinCluster(lsJntLoftBase, loftBase, tsb=1, mi=1)

            # adjust Subdivision Crv
            #### WARNING numbSubDv must to be a impair number and >3_________________________________
            lsCv = []
            numbSubDv = 7
            for i, each in enumerate(getCrv['crv']):
                createCrv = lib_curves.crvSubdivide(crv=each, subDiv=numbSubDv, subDivKnot=0, degree=3)
                nCv = mc.rename(each, gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
                nFunc=gloss.lexicon('base') + str(i + 1), nSide=side,incP=incPart))
                mc.setAttr(nCv+ ".visibility", 0)
                lsCv.append(nCv)

            # CREATE SA Base and Sk to Crv_______________________
            numbSkCrv = (int(numbPart) +1)*2
            lSaBase = lib_connectNodes.surfAttach(selObj=[nLoftBase], lNumb=numbSkCrv, parentInSA=True, parentSA=nSAGrp,
                                                  delKnot=True)
            for each in lSaBase['loc']:
                mc.setAttr(each + '.rotateX', 180)
                if side == "R" and self.name == 'leg':
                    mc.setAttr(each + '.rotateZ', -90)
                elif side == "L" and self.name == 'arm':
                    mc.setAttr(each + '.rotateZ', -90)
                else:
                    mc.setAttr(each + '.rotateZ', 90)
            [mc.setAttr(each + ".visibility", 1) for each in lSaBase['loc']]
            numbMb = (int(numbPart) +1)
            countNumbNb = 0
            countVal = 0.01
            countVal2 = 0.99
            count =0
            for each in range(numbMb):
                mc.setAttr(lSaBase['loc'][countNumbNb] + '.U', count +countVal)
                countNumbNb += 1
                mc.setAttr(lSaBase['loc'][countNumbNb] + '.U', count +countVal2)
                countNumbNb += 1
                count += 1

            # create Sk to skin Crv_____________________________________
            lsSkToCrv = []
            for i, each in enumerate(lSaBase['loc']):
                nSkCrv = gloss.renameSplit(selObj=each, namePart=['UV'], newNamePart=['sk'], reNme=False)
                libRig.createObj(partial(mc.joint, **{'n': nSkCrv}), match=[each], father=lSaBase['sa'][i],
                                 attributs={"drawStyle": 2})
                lsSkToCrv.append(nSkCrv)
            # create chain Jnt To twist shoulder_____________________________________
            nJntTwistChain1 = gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameStart, nFunc='TwistSys1', nSide=side,incP=incPart)
            nJntTwistChain2 = gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameStart, nFunc='TwistSys2', nSide=side,incP=incPart)
            nIkHdlTwist = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameStart,nFunc=gloss.lexicon('twist'),nSide=side,incP=incPart)
            jntTwistChain1 = libRig.createObj(partial(mc.joint, **{'n': nJntTwistChain1}), match=[lsChainFk[0]], father=lsChainFk[0],
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            jntTwistChain2 = libRig.createObj(partial(mc.joint, **{'n': nJntTwistChain2}), match=[lsChainFk[1]], father=jntTwistChain1,
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            mc.setAttr(jntTwistChain1+'.rotateOrder',lsRotOrder[0])
            mc.setAttr(jntTwistChain2+'.rotateOrder',lsRotOrder[0])
            mc.parent(jntTwistChain1,RootO)
            ikHdlTwist =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlTwist ,'sj':jntTwistChain1,'ee':jntTwistChain2,'sol':self.IkType}),
                        match=[lsChainFk[1]],father=lsChainFk[0],attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})
            mc.setAttr(ikHdlTwist+'.poleVector',0,0,0)
            mc.pointConstraint(lsChainFk[0],jntTwistChain1)
            # skin crvs______________________________________
            lsSkCrv = []
            for i, each in enumerate(lsCv):
                skinCrv = mc.skinCluster(lsSkToCrv, each, tsb=1, mi=1)
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
            nbByPart = numbSubDv+2
            count = 0
            getValCrv = []
            for each in range(nbByPart):
                val = round(abs(float(count)/float(nbByPart -1)), 4)
                count += 1
                getValCrv.append(val)
            invertValCrv = getValCrv[::-1]
            # MODIFY SKIN VALUES CRVS_________________________________________________
            for i, each in enumerate(sorted(dictPartCv1.items())):
                for j, eachPoint in enumerate(dictPartCv1.values()[i]):
                    mc.skinPercent(lsSkCrv[0][0], eachPoint, r=False, transformValue=[(lsSkToCrv[i+i], invertValCrv[j]),(lsSkToCrv[i+1+i],getValCrv[j])])
            for i, each in enumerate(sorted(dictPartCv2.items())):
                for j, eachPoint in enumerate(dictPartCv2.values()[i]):
                    mc.skinPercent(lsSkCrv[1][0], eachPoint, r=False, transformValue=[(lsSkToCrv[i+i], invertValCrv[j]),(lsSkToCrv[i+1+i],getValCrv[j])])


            # CREATE LOFT CTR____________________________________________
            loftCtr = libRig.createObj(
                partial(mc.loft, lsCv[0], lsCv[1:], **{'n': nLoftCtr, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
                                                       'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,
                refObj=None, incPart=False, attributs={"visibility": 0})
            # Skin loft
            skinLoft = mc.skinCluster(lsArcSk, nLoftCtr, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
            # get bind pre matrix_______________________________
            for i, each in enumerate(lsArcBindP):
                mc.connectAttr(each + ".worldInverseMatrix[0]", "%s.bindPreMatrix[%s]" % (skinLoft[0], i), force=True)

            # CREATE LOFT SK____________________________________________
            loftBaseSk = libRig.createObj(
                partial(mc.loft, lsCv[0], lsCv[1:], **{'n': nLoftBaseSk, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
                                                       'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,
                refObj=None, incPart=False, attributs={"visibility": 1})
            # Skin loft
            skinLoftSk = mc.skinCluster(lsArcSk, nLoftBaseSk, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
            # get bind pre matrix_______________________________
            for i, each in enumerate(lsArcBindP):
                mc.connectAttr(each + ".worldInverseMatrix[0]", "%s.bindPreMatrix[%s]" % (skinLoftSk[0], i), force=True)

            # concat points cv by 4 _______________________________
            recCv = mc.ls(nLoftCtr + '.cv[*]', fl=True)
            recCvSk = mc.ls(nLoftBaseSk + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv)) / adjustNumb))
            val = 0
            lsPoint = []
            lsPointSk = []
            for each2 in range(selDiv2):
                part = []
                partSk = []
                for each in range(adjustNumb):
                    part.append(recCv[each + val])
                    partSk.append(recCvSk[each + val])
                val += adjustNumb
                lsPoint.append(part)
                lsPointSk.append(partSk)

            # dic to param points _______________________________
            adjustNumb = numbSubDv+2
            selDiv2 = int(math.ceil(float(len(lsPoint))/adjustNumb))
            val = 0
            val2 = 0
            dictPart= {}
            dictPartSk= {}
            for each2 in range(selDiv2):
                lsPart =[]
                lsPartSk =[]
                for each in range(adjustNumb):
                    lsPart.append(lsPoint[each+val+val2])
                    lsPartSk.append(lsPointSk[each+val+val2])
                val += adjustNumb
                val2 -=1
                dictPart[each2] = lsPart
                dictPartSk[each2] = lsPartSk

            # get values Skin___________________________
            numbByPart = numbSubDv+2
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
                        mc.skinPercent(skinLoft[0], eachPoint, r=False, transformValue=[(lsArcSk[i], invertVal[j]),(lsArcSk[i+1], getVal[j])])

            # MODIFY SKIN VALUES LOFT Sk_________________________________________________
            for i, each in enumerate(sorted(dictPartSk.items())):
                for j, eachLigneSk in enumerate(dictPartSk.values()[i]):
                    for k, eachPoint in enumerate(eachLigneSk):
                        mc.skinPercent(skinLoftSk[0], eachPoint, r=False, transformValue=[(lsArcSk[i], invertVal[j]),(lsArcSk[i+1], getVal[j])])


            # CREATE INTERMEDIATE ARC CONTROLS_______________________________________
            # CREATE SA_______________________
            lSa = lib_connectNodes.surfAttach(selObj=[nLoftCtr], lNumb=len(lsChainFk) -1, parentInSA=True,
                                              parentSA=nSAGrp, delKnot=True)
            subdivPartLoft = numbSubDv
            if numbSubDv ==3:
                valSlide = 1
            else:
                valSlide = 1 + (float(numbSubDv-3)/2)

            for i, each in enumerate(lSa['loc']):
                mc.setAttr(each + '.U', valSlide)

                valSlide += subdivPartLoft + 1

            # CREATE CONTROLS_________________
            lsCtrArcBisRoot = []
            lsCtrArcBisCtr = []
            lsClusterArcBis = []
            for i, each in enumerate(lSa['loc']):
                nCtrArcBis = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name,
                                               nFunc=gloss.lexicon('arc') + str(i + 1), nSide=side, incP=incPart)
                ctrArcBis = libRig.createController(name=nCtrArcBis, shape=libRig.Shp(['square'], color=valColorAdd,
                size=(0.3 * valScl, 0.3 * valScl,0.3 * valScl)),match=[each], father=lSa['sa'][i],
                attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder": lsRotOrder[0], "drawStyle": 2})
                mc.setAttr(ctrArcBis['root'] + '.rotateX', 180)
                if side == "R" and self.name == 'leg':
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ', -90)
                elif side == "L" and self.name == 'arm':
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ', -90)
                else:
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ', 90)
                lsCtrArcBisRoot.append(ctrArcBis['root'])
                lsCtrArcBisCtr.append(ctrArcBis['c'])
                # CREATE CLUSTERS_________________
                nClusterArcBis = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name,
                                                   nFunc=gloss.lexicon('arc') + str(i + 1), nSide=side, incP=incPart)
                clusterArcBis = mc.createNode("cluster", n=nClusterArcBis)
                nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'), name=self.name,
                                                   nFunc=gloss.lexicon('arc') + str(i + 1), nSide=side, incP=incPart)
                mltMatCluster = mc.createNode("multMatrix", n=nMltMatCluster)
                mc.connectAttr(ctrArcBis['c'] + '.worldMatrix[0]', mltMatCluster + '.matrixIn[0]')
                mc.connectAttr(ctrArcBis['root'] + '.worldInverseMatrix[0]', mltMatCluster + '.matrixIn[1]')
                mc.connectAttr(mltMatCluster + '.matrixSum', clusterArcBis + '.weightedMatrix')
                mc.connectAttr(ctrArcBis['c'] + '.worldMatrix[0]', clusterArcBis + '.matrix')
                mc.connectAttr(ctrArcBis['root'] + '.worldInverseMatrix[0]', clusterArcBis + '.bindPreMatrix')
                mc.connectAttr(ctrArcBis['root'] + '.worldMatrix[0]', clusterArcBis + '.preMatrix')
                lsClusterArcBis.append(clusterArcBis)
            # concat Arc_________________
            lsConcatArc = lsArcCtr
            lenLs = 1
            for i, each in enumerate(lsCtrArcBisCtr):
                lsConcatArc.insert(lenLs + (i), each)
                lenLs += 1

            # ADD AND MODIFY CLUSTER VALUES_________________________________________________
            # get values Skin___________________________
            numbByPart = numbSubDv
            if numbByPart == 3:
                numbByPart = numbSubDv
            else:
                numbByPart = numbSubDv -(float(numbSubDv-3)/2)
            count = 0
            getVal = []
            for each in range(int(numbByPart)):
                val = round(abs(float(count)/float(numbByPart -1)), 4)
                count += 1
                getVal.append(val)
            invertVal = getVal[::-1]
            for each in invertVal[1:]:
                getVal.append(each)
            for i, each in enumerate(lsClusterArcBis):
                for j, eachLigne in enumerate(dictPartSk.values()[i]):
                    for k, eachPoint in enumerate(eachLigne):
                        mc.deformer(each, e=True, g=eachPoint)
                        mc.percent(each, eachPoint, value=getVal[j])

            # example [lib_curves.crvSubdivide(crv=each, name=None, subDiv=3,subDivKnot=None, degree=1) for each in getCrv2['crv']]
            # parent__________________________________________________________
            mc.parent(nLoftBase, loftGrp)
            mc.parent(nLoftCtr, loftGrp)
            mc.parent(nLoftBaseSk, loftGrp)
            [mc.parent(each, loftGrp) for each in lsCv]
            mc.parent(loftGrp,hookMb)
            mc.parent(nSAGrp,hookMb)
            # inherits Transform______________________________________________
            mc.setAttr(nLoftBase + '.inheritsTransform', 0)
            mc.setAttr(nLoftCtr + '.inheritsTransform', 0)
            mc.setAttr(nLoftBaseSk + '.inheritsTransform', 0)
            [mc.setAttr(each + '.inheritsTransform', 0) for each in lsCv]

            # SK ARM/LEG_________________________________________________
            # CREATE SA_______________________
            nbPart = 3
            subdv = int(numbPart)
            adjust = subdv + 1
            nbsk = (nbPart * adjust) + subdv
            lSaSk = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=nbsk, parentInSA=True, parentSA=nSAGrp,delKnot=True)
            # CREATE CONTROLS_________________
            lsCtrSkRoot = []
            lsCtrSk = []
            lsSk = []
            valmaxU = (mc.getAttr(nLoftBaseSk + ".minMaxRangeU"))[0][1]

            valSlide = (float(numbSubDv)/10)
            if numbSubDv == 3:
                valSlide = 0

            for i, each in enumerate(lSaSk['loc']):
                nCtrhdldSk = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name,
                                               nFunc=gloss.lexicon('shp') + str(i + 1), nSide=side, incP=incPart)
                ctrhdldSk = libRig.createController(name=nCtrhdldSk, shape=libRig.Shp(['crossLine'], color=valColorAdd,
                size=(0.2 * valScl, 0.2 * valScl,0.2 * valScl)),match=[each], father=lSaSk['sa'][i],
                attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder": lsRotOrder[0], "drawStyle": 2})
                mc.setAttr(ctrhdldSk['root'] + '.rotateX', 180)
                if side == "R" and self.name == 'leg':
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ', -90)
                elif side == "L" and self.name == 'arm':
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ', -90)
                else:
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ', 90)
                mc.setAttr(each + '.U', valSlide)
                if numbSubDv == 3:
                    valSlide += 1
                else:
                    valSlide += (float(numbSubDv)/10)*3

                for subdvN in range(subdv):
                    if ((nbPart+1)*(subdvN+1)) == (i + 1):
                        nBufhdldSkAdd = gloss.name_format(prefix=gloss.lexicon('buf'), name=self.name,
                                                       nFunc=gloss.lexicon('shp')+'AddSk'+ str(i + 1), nSide=side, incP=incPart)
                        bufhdldSkAdd =libRig.createObj(partial(mc.group, **{'n':nBufhdldSkAdd,'em': True}),match=[ctrhdldSk['c']],
                                         father=ctrhdldSk['c'],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})

                        nSkhdldSkAdd = gloss.name_format(prefix=gloss.lexicon('sk'), name=self.name,
                                                       nFunc=gloss.lexicon('shp')+'AddSk'+ str(i + 1), nSide=side, incP=incPart)
                        skHdldSkAdd =libRig.createObj(partial(mc.joint, **{'n':nSkhdldSkAdd}),match=[bufhdldSkAdd],father=bufhdldSkAdd,
                                                  attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

                        # CONNECT SCALE BUF SK ADD________________________________________________________
                        nMltDivSc= gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.nameMid,
                                                       nFunc=gloss.lexicon('scl')+ str(subdvN + 1), nSide=side, incP=incPart)
                        mltDivSc = mc.createNode("multiplyDivide", n=nMltDivSc)
                        mc.setAttr(mltDivSc + ".operation", 2)
                        mc.setAttr(mltDivSc + ".input2X", 180)

                        if self.name == 'arm':
                            nMltDblLinSc = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=self.nameMid,
                                                       nFunc=gloss.lexicon('scl')+ str(subdvN + 1), nSide=side, incP=incPart)
                            NodeMltDblLinSc = mc.createNode("multDoubleLinear", n=nMltDblLinSc)
                            mc.setAttr(NodeMltDblLinSc + ".input2", -1)
                            mc.connectAttr(lsChainFk[1:-1][subdvN] + '.rotateZ', "%s.input1" % (NodeMltDblLinSc), force=True)
                            mc.connectAttr(NodeMltDblLinSc + '.output', "%s.input1X" % (mltDivSc), force=True)

                        else:
                            mc.connectAttr(lsChainFk[1:-1][subdvN] + '.rotateZ', "%s.input1X" % (mltDivSc), force=True)

                        nAddDblLSc = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=self.nameMid,
                                                       nFunc=gloss.lexicon('scl')+ str(subdvN + 1), nSide=side, incP=incPart)
                        addDblLSc = mc.createNode("addDoubleLinear", n=nAddDblLSc)
                        mc.setAttr(addDblLSc + ".input2", 1)
                        mc.connectAttr(mltDivSc + ".outputX", "%s.input1" % (addDblLSc), force=True)

                        nCondSc = gloss.name_format(prefix=gloss.lexicon('cnd'), name=self.nameMid,
                                                       nFunc=gloss.lexicon('scl')+ str(subdvN + 1), nSide=side, incP=incPart)
                        cndSc = mc.createNode('condition', n=nCondSc)
                        mc.setAttr(cndSc + '.secondTerm', 0)
                        mc.setAttr(cndSc + '.operation', 5)
                        if self.name == 'leg':
                            mc.setAttr(cndSc + '.operation', 3)
                        mc.setAttr(cndSc + '.colorIfFalseR', 1)
                        mc.connectAttr(lsChainFk[1:-1][subdvN] + '.rotateZ', cndSc + '.firstTerm')
                        mc.connectAttr(addDblLSc + '.output', cndSc + '.colorIfTrueR')
                        mc.connectAttr(cndSc + ".outColorR", "%s.scaleX" % (bufhdldSkAdd), force=True)
                    else:
                        pass
                # visibility handle and delete shape______________________
                mc.setAttr(ctrhdldSk['c'] + '.displayHandle', 1)
                mc.setAttr(ctrhdldSk['c'] + '.overrideEnabled ', 1)
                lib_shapes.set_color(ctrhdldSk['c'], colorType='Index', color=valColorAdd)
                shpCtr = mc.listRelatives(ctrhdldSk['c'], s=True)[0]
                mc.select(cl=True)
                mc.delete(shpCtr)
                lsCtrSkRoot.append(ctrhdldSk['root'])
                lsCtrSk.append(ctrhdldSk['c'])
                lsSk.append(ctrhdldSk['sk'])

            # adjust first and last sa_________________
            mc.setAttr(lSaSk['loc'][0] + '.U', ((float(numbSubDv)/10)))
            mc.setAttr(lSaSk['loc'][-1] + '.U', (valmaxU - ((float(numbSubDv)/10))))

            # SK KNOT IN ARM/LEG_________________________________________________
            nSkShoulder = gloss.lexicon('shoulder')
            if self.name == 'leg':
                nSkShoulder = gloss.lexicon('hip')
            lSaShoulder = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=1,parentInSA=True, parentSA=nSAGrp,delKnot=True,nameRef='c_%s_%s_%s'%(nSkShoulder,side,incPart))
            mc.setAttr(lSaShoulder['loc'][0] + ".U",0.01)
            nRootTwistUp = gloss.name_format(prefix=gloss.lexicon('root'),name=nSkShoulder, nFunc=gloss.lexicon('shp'),nSide=side,incP=incPart)
            nCtrTwistUp = gloss.name_format(prefix=gloss.lexicon('c'),name=nSkShoulder, nFunc=gloss.lexicon('shp'),nSide=side,incP=incPart)
            nSkTwistUp = gloss.name_format(prefix=gloss.lexicon('sk'),name=nSkShoulder,nSide=side,incP=incPart)
            nOffTwistUp = gloss.name_format(prefix=gloss.lexicon('off'),name=nSkShoulder,nSide=side,incP=incPart)
            rootTwistUp =libRig.createObj(partial(mc.joint, **{'n':nRootTwistUp}),match=[lSaShoulder['loc'][0]],father=lSaShoulder['sa'][0],
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            ctrTwistUp = libRig.createObj(partial(mc.joint, **{'n':nCtrTwistUp}), shape= libRig.Shp(['crossLine'],color=valColorAdd,
            size=(0.2*valScl,0.2*valScl,0.2*valScl)),match=[rootTwistUp], father=rootTwistUp, attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            skTwistUp =libRig.createObj(partial(mc.joint, **{'n':nSkTwistUp}),match=[rootTwistUp],father=rootTwistUp,
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            lib_connectNodes.connectAxis(ctrTwistUp,skTwistUp,pos=True,rot=True,scl=True)

            offTwistUp = libRig.createObj(partial(mc.group, **{'n':nOffTwistUp,'em': True}),match=[rootTwistUp],
                                         father=rootTwistUp,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})

            # Create SK TO CONTROL TWIST HAND/FOOT_________________________________

            lSaTwist = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=1,parentInSA=True, parentSA=nSAGrp,delKnot=True,nameRef='c_%s_%s_%s'%(nFkWrist,side,incPart))
            mc.setAttr(lSaTwist['loc'][0] + ".U",(mc.getAttr(nLoftBaseSk+'.minMaxRangeU')[0][1]-0.05))

            nRootTwist = gloss.name_format(prefix=gloss.lexicon('root'),name=nFkWrist,nSide=side,incP=incPart)
            nCtrTwist = gloss.name_format(prefix=gloss.lexicon('c'), name=nFkWrist,nFunc=gloss.lexicon('shp'),nSide=side, incP=incPart)
            nSkTwist = gloss.name_format(prefix=gloss.lexicon('sk'), name=nFkWrist,nSide=side, incP=incPart)

            rootTwist =libRig.createObj(partial(mc.joint, **{'n':nRootTwist}),match=[lSaTwist['loc'][0]],father=lSaTwist['sa'][0],
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            ctrTwist = libRig.createObj(partial(mc.joint, **{'n':nCtrTwist}), shape= libRig.Shp(['crossLine'],color=valColorAdd,
            size=(0.2*valScl,0.2*valScl,0.2*valScl)),match=[rootTwist], father=rootTwist, attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            skTwist =libRig.createObj(partial(mc.joint, **{'n':nSkTwist}),match=[rootTwist],father=rootTwist,
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            lib_connectNodes.connectAxis(ctrTwist,skTwist,pos=True,rot=True,scl=True)

            mc.setAttr(rootTwistUp + '.rotateY',180)
            mc.setAttr(rootTwist + '.rotateY',180)
            if side == "R" and self.name == 'leg':
                mc.setAttr(rootTwistUp + '.rotateZ',90)
                mc.setAttr(rootTwist + '.rotateZ',90)
            elif side == "L" and self.name == 'leg':
                mc.setAttr(rootTwistUp + '.rotateZ',-90)
                mc.setAttr(rootTwist + '.rotateZ',-90)
            elif side == "L" and self.name == 'arm':
                mc.setAttr(rootTwistUp + '.rotateZ',-90)
                mc.setAttr(rootTwist + '.rotateZ',-90)
            else:
                mc.setAttr(rootTwistUp + '.rotateZ',90)
                mc.setAttr(rootTwist + '.rotateZ',90)

            # visibility handle and delete shape______________________
            mc.setAttr(ctrTwistUp + '.displayHandle', 1)
            mc.setAttr(ctrTwistUp + '.overrideEnabled ', 1)
            lib_shapes.set_color(ctrTwistUp, colorType='Index', color=valColorAdd)
            shpCtr = mc.listRelatives(ctrTwistUp, s=True)[0]
            mc.select(cl=True)
            mc.delete(shpCtr)
            mc.setAttr(ctrTwist + '.displayHandle', 1)
            mc.setAttr(ctrTwist + '.overrideEnabled ', 1)
            lib_shapes.set_color(ctrTwist, colorType='Index', color=valColorAdd)
            shpCtr = mc.listRelatives(ctrTwist, s=True)[0]
            mc.select(cl=True)
            mc.delete(shpCtr)

            nPlVTwistTop = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.name, nFunc=gloss.lexicon('twist')+'Top',nSide=side,incP=incPart)
            nAimTwistTop = gloss.name_format(prefix=gloss.lexicon('aim'), name=self.name, nFunc=gloss.lexicon('twist')+'Top',nSide=side,incP=incPart)
            plVTwistTop = libRig.createObj(partial(mc.group, **{'n': nPlVTwistTop, 'em': True}), match=[lsChainFk[0]],father=lsChainFk[0],
                                attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0,"rotateOrder":lsRotOrder[0]})
            aimTwistTop = libRig.createObj(partial(mc.group, **{'n': nAimTwistTop, 'em': True}), match=[nRootO],father=nRootO,
                                attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0,"rotateOrder":lsRotOrder[0]})
            if self.nameEnd == 'hand':
                mc.move(0,0,-1*mc.getAttr("tpl_WORLD"+".scaleX"),plVTwistTop, ls=True)
                aim= (0.0,1.0,0.0)
                upV= (0.0,0.0,-1.0)
                if side =='R': aim= (0.0,-1.0,0.0)
            else:
                mc.move(-1*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,plVTwistTop, ls=True)
                aim= (0.0,1,0.0)
                upV= (-1.0,0.0,0.0)
                if side =='R': aim= (0.0,-1.0,0.0)
            mc.aimConstraint(lsChainFk[1], nAimTwistTop, aim=aim, u=upV, wut='object', wuo=plVTwistTop)
            mc.pointConstraint(lsChainFk[0],aimTwistTop)
            mc.parent(lsJntLoftBase[0],jntTwistChain1)
            mc.parent(plVTwistTop,jntTwistChain1)
            mc.setAttr(lsJntLoftBase[0]+'.rotateOrder',lsRotOrder[0])


            # SYSTEM TWIST HANDLE_________________________________________________
            if self.name == 'arm':
                rotOrder = 0
            else:
                rotOrder = 5
            nTwistHdl1 = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.name, nFunc=gloss.lexicon('twist')+'1',nSide=side,incP=incPart)
            nTwistHdl2 = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.name, nFunc=gloss.lexicon('twist')+'2',nSide=side,incP=incPart)
            nTwistIkHdl = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nFunc=gloss.lexicon('twist')+'1',nSide=side,incP=incPart)
            twistHdl1 = libRig.createObj(partial(mc.joint, **{'n': nTwistHdl1}), match=[nJntFirst], father=nJntRig1,
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2,"rotateOrder":rotOrder})
            twistHdl2 = libRig.createObj(partial(mc.joint, **{'n': nTwistHdl2}), match=[nJntFirst], father=twistHdl1,
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2,"rotateOrder":rotOrder})
            mc.setAttr(twistHdl1+'.rotateOrder',rotOrder)
            mc.setAttr(twistHdl2+'.rotateOrder',rotOrder)


            nPlVTwistHdl = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.name, nFunc=gloss.lexicon('twist')+'Hdl',nSide=side,incP=incPart)
            nAimTwistHdl = gloss.name_format(prefix=gloss.lexicon('aim'), name=self.name, nFunc=gloss.lexicon('twist')+'Hdl',nSide=side,incP=incPart)
            plVTwistHdl = libRig.createObj(partial(mc.group, **{'n': nPlVTwistHdl, 'em': True}), match=[nJntFirst],father=twistHdl1,
                                attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0,"rotateOrder":lsRotOrder[0]})
            aimTwistHdl = libRig.createObj(partial(mc.group, **{'n': nAimTwistHdl, 'em': True}), match=[nJntFirst],father=nJntFirst,
                                attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0,"rotateOrder":lsRotOrder[0]})
            mc.setAttr(aimTwistHdl+'.rotateOrder',lsRotOrder[0])

            if self.nameEnd == 'hand':
                mc.move(-1*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,plVTwistHdl, ls=True)
                mc.move(0,1*mc.getAttr("tpl_WORLD"+".scaleX"),0,twistHdl2, ls=True)
                aim= (0.0,1.0,0.0)
                upV= (-1.0,0.0,0.0)
                if side =='R':
                    aim= (0.0,-1.0,0.0)
                    mc.move(0,-1*mc.getAttr("tpl_WORLD"+".scaleX"),0,twistHdl2, ls=True)
            else:
                mc.move(0,0,1*mc.getAttr("tpl_WORLD"+".scaleX"),plVTwistHdl, ls=True)
                mc.move(1*mc.getAttr("tpl_WORLD"+".scaleX"),-1*mc.getAttr("tpl_WORLD"+".scaleX"),0,twistHdl2, ls=True)
                aim= (1,0.0,0.0)
                upV= (0.0,0.0,1.0)
                if side =='R':
                    aim= (1.0,0.0,0.0)
                    mc.move(-1*mc.getAttr("tpl_WORLD"+".scaleX"),1*mc.getAttr("tpl_WORLD"+".scaleX"),0,twistHdl2, ls=True)

            ikHdlTwistHdl =libRig.createObj(partial(mc.ikHandle, **{'n':nTwistIkHdl ,'sj':twistHdl1,'ee':twistHdl2,'sol':self.IkType}),
                        match=[twistHdl2],father=nJntFirst,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0,"rotateOrder":rotOrder})
            mc.setAttr(ikHdlTwistHdl+'.poleVector',0,0,0)
            mc.aimConstraint(twistHdl2, nAimTwistHdl, aim=aim, u=upV, wut='object', wuo=plVTwistHdl)
            mc.parent(lsJntLoftBase[-1], aimTwistHdl)


            '''
            if self.nameEnd == 'foot':
                #mc.parent(ikHdlTwistHdl, nJntRig1)
                masterFoot = mc.getAttr(eachTpl+".%s[0]"%('master%s'%(self.nameEnd)))
                getP = mc.xform(masterFoot, q=True, ws=True, translation=True)
                #mc.xform(ikHdlTwistHdl, worldSpace=True, t=getP)
                nRotSkAnkle = gloss.name_format(prefix=gloss.lexicon('root'), name=self.name, nFunc=gloss.lexicon('twist')+'Sk',nSide=side,incP=incPart)

                rotSkAnkle = libRig.createObj(partial(mc.group, **{'n': nRotSkAnkle, 'em': True}), match=[aimTwistHdl],father=nJntFirst,
                                    attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0,"rotateOrder":lsRotOrder[0]})
                mc.connectAttr(aimTwistHdl + ".rotateX", rotSkAnkle + ".rotateX", force=True)
                mc.parent(lsJntLoftBase[-1], rotSkAnkle)
            '''


            # Create SYSTEM 360 WRIST___________________________________________________________________________
            #if self.name == 'arm':
            nRig360 = gloss.name_format(prefix=gloss.lexicon('rig'), name=nFkWrist,nFunc='360',nSide=side, incP=incPart)
            rig360 = libRig.createObj(partial(mc.spaceLocator, **{'n':nRig360}),match=[nJntRig1],father=nJntRig1,attributs={"visibility":0,"rotateOrder":rotOrder})
            const360 = mc.orientConstraint(twistHdl1,rig360,w=1)
            constWrist360 = mc.orientConstraint(nJntRig1,rig360,w=1)
            oriCns = mc.listConnections(mc.listRelatives(rig360, type="orientConstraint")[0]+".target")[-1]
            mc.setAttr(oriCns+'.interpType',0)
            nTrs360 = gloss.name_format(prefix=gloss.lexicon('trans'), name=nFkWrist,nFunc='360',nSide=side, incP=incPart)
            nBuf360 = gloss.name_format(prefix=gloss.lexicon('buf'), name=nFkWrist,nFunc='360',nSide=side, incP=incPart)
            nRot360 = gloss.name_format(prefix=gloss.lexicon('rot'), name=nFkWrist,nFunc='360',nSide=side, incP=incPart)
            trs360 = libRig.createObj(partial(mc.group, **{'n':nTrs360,'em': True}),match=[nJntFirst],
                                                     father=nJntFirst,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"rotateOrder":rotOrder})
            buf360 = libRig.createObj(partial(mc.group, **{'n':nBuf360,'em': True}),match=[trs360],
                                                     father=trs360,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"rotateOrder":rotOrder})
            rot360 = libRig.createObj(partial(mc.group, **{'n':nRot360,'em': True}),match=[buf360],
                                                     father=buf360,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"rotateOrder":rotOrder})

            constBuf360 = mc.orientConstraint(ikCtr['c'],buf360,w=1)
            oriCnsBuf360 = mc.listConnections(mc.listRelatives(buf360, type="orientConstraint")[0]+".target")[-1]
            mc.delete(oriCnsBuf360)

            mc.pointConstraint(nJntRig1,trs360)
            mc.parent(ikHdlTwistHdl, nJntRig1)
            mc.parent(twistHdl1, nJntFirst)
            mc.pointConstraint(nJntRig1,twistHdl1)

            mc.addAttr(nJntFirst, ln="ori360", at="float",dv=0)
            mc.setAttr(nJntFirst + ".ori360", e=True, k=True)

            nMltDblL360 = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=nFkWrist,nFunc='360',nSide=side, incP=incPart)
            NodeMltDblL360 = mc.createNode("multDoubleLinear", n=nMltDblL360)

            mc.setAttr(NodeMltDblL360 + ".input2",-2)
            if self.name == 'leg' and side =='L':
                mc.setAttr(NodeMltDblL360 + ".input2",2)

            mc.connectAttr(rig360 + '.rotateY', "%s.input1" % (NodeMltDblL360), force=True)
            mc.connectAttr(NodeMltDblL360 + '.output', "%s.ori360" % (nJntFirst), force=True)

            nMltDiv360 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nFkWrist,nFunc='rot360',nSide=side, incP=incPart)
            mltDiv360 = mc.createNode("multiplyDivide", n=nMltDiv360)
            mc.setAttr(mltDiv360 + ".operation", 1)
            mc.setAttr(mltDiv360 + ".input2X", 0.6)
            if self.name == 'leg':
                mc.setAttr(mltDiv360 + ".input2X", 1)
            mc.connectAttr(nJntFirst + '.ori360', "%s.input1X" % (mltDiv360), force=True)

            if self.name == 'arm':
                mc.connectAttr(mltDiv360 + ".outputX", "%s.rotateX" % (rot360), force=True)
            else:
                mc.connectAttr(mltDiv360 + ".outputX", "%s.rotateY" % (rot360), force=True)

            mc.parent(lsJntLoftBase[-1], rot360)

            nMltDiv360Sk = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nFkWrist,nFunc='sk360',nSide=side, incP=incPart)
            mltDiv360Sk = mc.createNode("multiplyDivide", n=nMltDiv360Sk)
            mc.setAttr(mltDiv360Sk + ".operation", 2)
            mc.setAttr(mltDiv360Sk + ".input2X", 6)
            mc.connectAttr(nJntFirst + '.ori360', "%s.input1X" % (mltDiv360Sk), force=True)

            nMltDblL360Sk = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=nFkWrist,nFunc='sk360',nSide=side, incP=incPart)
            NodeMltDblL360Sk = mc.createNode("multDoubleLinear", n=nMltDblL360Sk)
            mc.setAttr(NodeMltDblL360Sk + ".input2", -1)
            mc.connectAttr(mltDiv360Sk + '.outputX', "%s.input1" % (NodeMltDblL360Sk), force=True)


            # TWIST FIX ATTRIBUTE_________________________________________________
            concatLsRoot = [each for each in lsCtrSkRoot]
            concatLsRoot.insert(0, rootTwistUp)
            concatLsRoot.append(skTwist)

            sel = concatLsRoot
            selInvert = concatLsRoot[::-1]
            lenSel = len(sel)
            val = [round(abs(float(i)/float(lenSel-1)), 4) for i, each in enumerate(sel)]
            valInvert = [round(abs(float(i)/float(lenSel-1)), 4) for i, each in enumerate(sel)][::-1]
            concatZip = zip(sel,selInvert)
            if lenSel <= 2:
                mc.warning('trop court')
            else:
                if lenSel %2 ==0 and lenSel>2:
                    valDiv2 = [round(abs(float(i)/float((lenSel/2)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)])]
                    countLen = (lenSel/2)
                elif lenSel %2 !=0 and lenSel>1:
                    valDiv2 = [round(abs(float(i)/float(((lenSel/2)+1)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)+1])]
                    countLen = (lenSel/2)+1

                for i, each in enumerate(concatZip[:countLen]):
                    nMltDblLinSkArc = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nFunc=gloss.lexicon('twist')+'Fixe'+str(i+1),nSide=side,incP=incPart)
                    nMltDivSkArc = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('twist')+'Fixe'+str(i+1),nSide=side,incP=incPart)
                    NodeMltDblLinearSkArc = mc.createNode("multDoubleLinear", n=nMltDblLinSkArc)
                    mc.setAttr(NodeMltDblLinearSkArc + ".input2", -1)
                    mc.connectAttr(shapeAttrib + ".twistFix", "%s.input1" % (NodeMltDblLinearSkArc), force=True)
                    mltDivSkArc = mc.createNode("multiplyDivide", n=nMltDivSkArc)
                    mc.setAttr(mltDivSkArc + ".input2X",valDiv2[i])
                    mc.connectAttr(NodeMltDblLinearSkArc+".output", "%s.input1X" % (mltDivSkArc), force=True)
                    mc.connectAttr(mltDivSkArc+".outputX", "%s.rotateAxisY" % (each[0]), force=True)
                    if each[0] != each[1]:
                        mc.connectAttr(mltDivSkArc+".outputX", "%s.rotateAxisY" % (each[1]), force=True)

            # SQUASH ATTRIBUTE_________________________________________________
            concatLsSk = [each for each in lsSk]
            concatLsSk.insert(0, skTwistUp)
            concatLsSk.append(nSkTwist)
            sel = concatLsSk
            selInvert = concatLsSk[::-1]
            lenSel = len(sel)
            val = [round(abs(float(i)/float(lenSel-1)), 4) for i, each in enumerate(sel)]
            valInvert = [round(abs(float(i)/float(lenSel-1)), 4) for i, each in enumerate(sel)][::-1]
            concatZip = zip(sel,selInvert)
            if lenSel <= 2:
                mc.warning('trop court')
            else:
                if lenSel %2 ==0 and lenSel>2:
                    valDiv2 = [round(abs(float(i)/float((lenSel/2)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)])]
                    valDiv2Invert = [round(abs(float(i)/float(((lenSel/2)+1)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)])][::-1]
                    countLen = (lenSel/2)
                elif lenSel %2 !=0 and lenSel>1:
                    valDiv2 = [round(abs(float(i)/float(((lenSel/2)+1)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)+1])]
                    valDiv2Invert = [round(abs(float(i)/float(((lenSel/2)+1)-1)), 4) for i, each in enumerate(sel[:(lenSel/2)+1])][::-1]
                    countLen = (lenSel/2)+1
                for i, each in enumerate(concatZip[:countLen]):
                    ctrEach0 = mc.listConnections(each[0]+'.scale')
                    ctrEach1 = mc.listConnections(each[1]+'.scale')
                    if ctrEach1 is None:
                        pass
                    else:
                        nMltDivSkArc = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('squash')+'Sk'+str(i+1),nSide=side,incP=incPart)
                        mltDivSkArc = mc.createNode("multiplyDivide", n=nMltDivSkArc)
                        mc.setAttr(mltDivSkArc + ".input2X",valDiv2[i])
                        mc.connectAttr(fk[0]+'.squash', "%s.input1X" % (mltDivSkArc), force=True)

                        nNodeAddDblLinear = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.name,nFunc=gloss.lexicon('squash')+'Sk'+str(i+1),nSide=side,incP=incPart)
                        nodeAddDblLinear = mc.createNode("addDoubleLinear", n=nNodeAddDblLinear)
                        mc.setAttr(nodeAddDblLinear + ".input2", valDiv2Invert[i])
                        mc.connectAttr(mltDivSkArc+'.outputX', "%s.input1" % (nodeAddDblLinear), force=True)

                        nMltDivSkArc0 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('squash')+'0Sk'+str(i+1),nSide=side,incP=incPart)
                        mltDivSkArc0 = mc.createNode("multiplyDivide", n=nMltDivSkArc0)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2X" % (mltDivSkArc0), force=True)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2Y" % (mltDivSkArc0), force=True)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2Z" % (mltDivSkArc0), force=True)
                        mc.connectAttr(ctrEach0[0]+'.scale', "%s.input1" % (mltDivSkArc0), force=True)

                        nMltDivSkArc1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc=gloss.lexicon('squash')+'1Sk'+str(i+1),nSide=side,incP=incPart)
                        mltDivSkArc1 = mc.createNode("multiplyDivide", n=nMltDivSkArc1)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2X" % (mltDivSkArc1), force=True)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2Y" % (mltDivSkArc1), force=True)
                        mc.connectAttr(nodeAddDblLinear+'.output', "%s.input2Z" % (mltDivSkArc1), force=True)
                        mc.connectAttr(ctrEach1[0]+'.scale', "%s.input1" % (mltDivSkArc1), force=True)

                        mc.connectAttr(mltDivSkArc0+'.output', "%s.scale" % (each[0]), force=True)
                        if each[0] != each[1]:
                            mc.connectAttr(mltDivSkArc1+'.output', "%s.scale" % (each[1]), force=True)

            #PURGE SA____________________________________
            [mc.delete(each)for each in lSaBase['loc']]
            [mc.delete(each)for each in lSaSk['loc']]
            [mc.delete(each)for each in lSa['loc']]


            ####################################  CLAVICULE #######################################################
            # CREATE BASE___________________________
            # NAME__________________________________
            nHookClv = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.nameClav,nSide=side,incP=incPart)
            nRootScl = gloss.name_format(prefix=gloss.lexicon('scl'),name=self.nameClav,nSide=side,incP=incPart)
            nRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameClav,nSide=side,incP=incPart)
            nJnt = gloss.name_format(prefix=gloss.lexicon('jnt'),name=self.nameClav+'1',nSide=side,incP=incPart)
            nCns = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.nameClav,nSide=side,incP=incPart)
            nEnd = gloss.name_format(prefix=gloss.lexicon('end'),name=self.nameClav,nSide=side,incP=incPart)
            nAo = gloss.name_format(prefix=gloss.lexicon('ao'),name=self.nameClav,nSide=side,incP=incPart)
            nEff = gloss.name_format(prefix=gloss.lexicon('eff'),name=self.nameClav,nSide=side,incP=incPart)
            nAoSwitch = gloss.name_format(prefix='orig',name=self.nameClav,nFunc=gloss.lexicon('ao')+'Switch',nSide=side,incP=incPart)
            nCnsMb = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.nameClav,nFunc=self.name,nSide=side,incP=incPart)

            hookClv =libRig.createObj(partial(mc.group, **{'n':nHookClv,'em': True}),match=[lsTplClavIk[0]],father=self.nRig,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            rootScl =libRig.createObj(partial(mc.joint, **{'n':nRootScl}),match=[hookClv],father=hookClv,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            # FUSION TPL TO CREATE CHAIN___________________________________
            lsChainJnt = list(lsTplClavIk)
            [lsChainJnt.insert(i + 1, lsTplClavCtr[i]) for i in range(len(lsTplClavCtr))]

            nLsFkClav = [gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameClav,nFunc='%s'%(i+1),nSide=side,incP=incPart) for i in range(len(lsChainJnt))]
            # CREATE CHAIN FK___________________________________________________________________________________________
            aimFk = libRgPreset.configAxis(mb="aimJtLeg%s"%side,side=side)["aimOri"]
            upVFk = libRgPreset.configAxis(mb="aimJtLeg%s"%side,side=side)["aimUpV"]
            if side =='R':
                upVFk = (-1,0,0)
            else:
                upVFk = (1,0,0)

            if self.name == "arm":
                aimFk = libRgPreset.configAxis(mb="aimJtArm%s"%side,side=side)["aimOri"]

            fkClav = libRig.chainJoint(lstChain=lsChainJnt,lstNameChain=nLsFkClav, lsRotOrder=lsRotOrder,aim=aimFk, upV=upVFk, posUpV =(0,0,1),
                                   convertChain=True,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)))

            # ADJUST ORIENTATION FK____________________________________________________
            [mc.setAttr(each+".jointOrientY",0) for i, each in enumerate(nLsFkClav[1:])]

            # SNAP SHAPE TPL FK________________________________________________________
            [lib_shapes.snapShpCv(shpRef=lsChainJnt[i], shpTarget=each) for i, each in enumerate(nLsFkClav)]
            lib_shapes.snapShpCv(masterStart, shpTarget=nLsFkClav[0])
            # adjust radius joints__________________________________________________________
            [mc.setAttr(each + ".radius",0.7*mc.getAttr("tpl_WORLD"+".scaleX")) for each in fkClav]
            [mc.setAttr(each + ".drawStyle",2) for each in fkClav]

            # CREATE SK CLAV__________________________________________
            lsSkClav =[]
            for i, each in enumerate(fkClav[:-1]):
                nSkClav = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.nameClav,nFunc='%s'%(i+1),nSide=side,incP=incPart)
                libRig.createObj(partial(mc.joint, **{'n':nSkClav}),match=[each],father=each ,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                lsSkClav.append(nSkClav)

            # duplicate ClavFk to create a second hierarchy__________________________________
            lsJntClav = []
            for i, each in enumerate(fkClav):
                if i ==0:
                    libRig.createObj(partial(mc.joint, **{'n': nRoot}), match=[each], father=each,
                                attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    libRig.createObj(partial(mc.joint, **{'n': nJnt}), match=[each], father=nRoot,
                                     attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    libRig.createObj(partial(mc.joint, **{'n': nAo}), match=[each], father=nRoot,
                                     attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    aoSwitch =libRig.createObj(partial(mc.group, **{'n':nAoSwitch,'em': True}),match=[fk[1]],
                                          father=fk[1],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                    mc.parent(aoSwitch,nRoot)
                    mc.parent(nRoot,nRootScl)
                else:
                    nJnt = gloss.name_format(prefix=gloss.lexicon('jnt'), name=self.nameClav+str(i+1),nSide=side, incP=incPart)
                    libRig.createObj(partial(mc.joint, **{'n': nJnt}), match=[each], father=each,
                                     attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    mc.parent(nJnt,gloss.name_format(prefix=gloss.lexicon('jnt'),name=self.nameClav+str(i),nSide=side, incP=incPart))

                if i == int(len(fkClav)-1):
                    libRig.createObj(partial(mc.joint, **{'n': nCns}), match=[each],father=nJnt,
                                     attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                    libRig.createObj(partial(mc.joint, **{'n': nEff}), match=[each], father=nAo,
                                     attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsJntClav.append(nJnt)

            ## Create IK Handle Control To Fk #################

            for i,each in enumerate(fkClav[:-1]):
                nIkHdlAo = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameClav+str(i+1),nSide=side,incP=incPart)
                nUpVRootBase = gloss.name_format(prefix=gloss.lexicon('root'), name=self.nameClav,nFunc=gloss.lexicon('upV')+str(i+1),nSide=side, incP=incPart)
                nUpVClav = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.nameClav,nFunc=gloss.lexicon('upV')+str(i+1),nSide=side, incP=incPart)
                UpVRootBase = libRig.createObj(partial(mc.group, **{'n':nUpVRootBase, 'em': True}),match=[each],father=each,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                UpVClav = libRig.createObj(partial(mc.group, **{'n':nUpVClav, 'em': True}),match=[UpVRootBase],father=UpVRootBase,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})


                mc.move(0,0,1*mc.getAttr("tpl_WORLD"+".scaleX"),UpVClav, ls=True)
                mc.select(cl=True)

                ikHdlAo =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlAo ,'sj':lsJntClav[i],'ee':lsJntClav[i+1],'sol':self.IkType}),
                                                        match=[fkClav[i+1]],father=each,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})
                mc.poleVectorConstraint(nUpVClav, ikHdlAo)
                mc.setAttr(ikHdlAo+".twist",abs(mc.getAttr(lsJntClav[i]+".rotateY")))

            mc.pointConstraint(fkClav[0],lsJntClav[0])

            # Create IK Handle Drive Fk________________________________________
            nIkHdlAoFk = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameClav,nFunc=gloss.lexicon('fk'),nSide=side,incP=incPart)
            ikHdlAoFk =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlAoFk ,'sj':nAo,'ee':nEff,'sol':self.IkType}),
                                                    match=[aoSwitch],father=nRoot,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})

            # Create Shoulder System__________________________________________
            lsJntAo = []
            for i, each in enumerate(fk[:len(concatIkFk)-lenLsTplMidMb+1]):

                nJntAo = gloss.name_format(prefix=gloss.lexicon('ao'), name=self.name+str(i+1),nSide=side, incP=incPart)
                libRig.createObj(partial(mc.joint, **{'n': nJntAo}), match=[each], father=each,
                                 attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                if i ==0:
                    mc.parent(nJntAo,nRoot)
                else:
                    mc.parent(nJntAo, gloss.name_format(prefix=gloss.lexicon('ao'), name=self.name+str(i),nSide=side, incP=incPart))
                lsJntAo.append(nJntAo)
            # constraint IkHandle_______________________________________________
            getPointWeight =[]
            pointCnsgrpTampDistDim = mc.pointConstraint(nAoSwitch,nIkHdlAoFk,w=0)
            firstAimCons = mc.listConnections(mc.listRelatives(nIkHdlAoFk, type="constraint")[0]+ ".target", p=True)[-1]
            getPointWeight.append(firstAimCons)
            pointCnscreateTpDistDim = mc.pointConstraint(lsJntAo[1],nIkHdlAoFk,w=1)
            secondAimCons = mc.listConnections(mc.listRelatives(nIkHdlAoFk, type="constraint")[0]+ ".target", p=True)[-1]
            getPointWeight.append(secondAimCons)

            # SYSTEM POLE VECTOR CLAV__________________________________
            nDistDimPlVClav = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.nameClav,nSide=side,incP=incPart)
            nTampPoleVClav = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.nameClav,nSide=side,incP=incPart)
            nRootPlVClav = gloss.name_format(prefix=gloss.lexicon('root')+'UpV',name=self.nameClav,nSide=side,incP=incPart)
            nPlVClav = gloss.name_format(prefix=gloss.lexicon('upV'),name=self.nameClav,nSide=side,incP=incPart)
            nJtClav = gloss.name_format(prefix=gloss.lexicon('jnt'),name=self.nameClav,nSide=side,incP=incPart)
            nJtIkClav = gloss.name_format(prefix=gloss.lexicon('jnt')+'Ik',name=self.nameClav,nSide=side,incP=incPart)
            nIkHdlClav = gloss.name_format(prefix=gloss.lexicon('ik'),name=self.nameClav,nSide=side,incP=incPart)
            nIkHdlClav2 = gloss.name_format(prefix=gloss.lexicon('ik')+'jnt',name=self.nameClav,nSide=side,incP=incPart)

            # CREATE____________________________________________________
            distDimPlVClav = libRig.createObj(partial(mc.group, **{'n':nDistDimPlVClav, 'em': True}),match=[nJntPlV1],father=hookClv,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            tampPoleVClav = libRig.createObj(partial(mc.spaceLocator, **{'n':nTampPoleVClav}),match=[nJntPlV1],father=distDimPlVClav,attributs={"visibility":0})
            mc.pointConstraint(ikCtr['c'],tampPoleVClav)
            mc.pointConstraint(distDimPlVClav,tampPoleVClav)
            rootPlVClav = libRig.createObj(partial(mc.spaceLocator, **{'n':nRootPlVClav}),match=[tampPoleVClav],father=tampPoleVClav,attributs={"visibility":0})
            plVClav = libRig.createObj(partial(mc.spaceLocator, **{'n':nPlVClav}),match=[plV['c']],father=rootPlVClav,attributs={"visibility":0})
            jtClav = libRig.createObj(partial(mc.joint, **{'n':nJtClav}), match=[nJntPlV1], father=distDimPlVClav,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            jtIkClav = libRig.createObj(partial(mc.joint, **{'n':nJtIkClav}), match=[nJntPlV1], father=jtClav,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            # create ik ###
            ikHdlClav2 =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlClav2 ,'sj':nJtClav,'ee':nJtIkClav,'sol':self.IkType}),
                       match=None,father=distDimPlVClav,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})
            mc.setAttr(ikHdlClav2 + ".poleVectorX", 0)
            mc.setAttr(ikHdlClav2 + ".poleVectorY", 0)
            mc.setAttr(ikHdlClav2 + ".poleVectorZ", 0)
            # constraint ###
            mc.parent(tampPoleVClav,nJtIkClav)
            mc.select(cl=True)
            mc.pointConstraint(dstDimCns,ikHdlClav2)

            # connect Node nRootPlVClav
            mc.connectAttr(mltDivFollowH2 + '.outputX', "%s.rotateY" %(rootPlVClav), force=True)
            ## Create IK Handle ###
            ikHdlClav =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlClav ,'sj':lsJntAo[0],'ee':lsJntAo[-1],'sol':self.IkType}),
                       match=None,father=nRoot,attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})
            print 'HERE pour polvecotr autoOrient : 1792 in rig_member'
            mc.poleVectorConstraint(plVClav, ikHdlClav)
            mc.pointConstraint(ikCtr['c'],ikHdlClav)

            # connect ikHdlClav to twist/blend/autoOrient
            if side == "R" :
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.twist" %(ikHdlClav), force=True)
            else:
                mc.connectAttr(ikCtr['c']+".twist", "%s.twist" %(ikHdlClav), force=True)
            #mc.connectAttr(mltDivTwist2 + '.outputX', "%s.twist" %(ikHdlClav), force=True)
            mc.connectAttr(mDLIkBlend + '.output',"%s.ikBlend" %(ikHdlClav), force=True)
            # autoOrient
            nMltDivAutoOr1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameClav,nFunc='AutoOr1'+'Div',nSide=side,incP=incPart)
            mltDivAutoOr1 = mc.createNode("multiplyDivide", n=nMltDivAutoOr1)
            mc.setAttr(mltDivAutoOr1+ ".operation", 2)
            mc.setAttr(mltDivAutoOr1 + ".input2X",10)
            mc.connectAttr(shapeAttrib+".autoOrient", "%s.input1X" % (mltDivAutoOr1), force=True)
            mc.connectAttr(mltDivAutoOr1 + '.outputX',getPointWeight[1], force=True)

            nMltDivAutoOr2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameClav,nFunc='AutoOr2'+'Div',nSide=side,incP=incPart)
            mltDivAutoOr2 = mc.createNode("multiplyDivide", n=nMltDivAutoOr2)
            mc.setAttr(mltDivAutoOr2+ ".operation", 2)
            mc.setAttr(mltDivAutoOr2 + ".input2X",10)
            mc.connectAttr(shapeAttrib+".autoOrient", "%s.input1X" % (mltDivAutoOr2), force=True)
            nMltDblLinAutoOr = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameClav,nFunc='AutoOr',nSide=side,incP=incPart)
            NodeMltDblLinearAutoOr = mc.createNode("multDoubleLinear", n=nMltDblLinAutoOr)
            mc.setAttr(NodeMltDblLinearAutoOr + ".input2", -1)
            mc.connectAttr(mltDivAutoOr2+".outputX", "%s.input1" % (NodeMltDblLinearAutoOr), force=True)
            nAddDblLinAutoOr = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameClav,nFunc='AutoOr',nSide=side,incP=incPart)
            addDblLinAutoOr = mc.createNode("addDoubleLinear", n=nAddDblLinAutoOr)
            mc.setAttr(addDblLinAutoOr + ".input1",1)
            mc.connectAttr(NodeMltDblLinearAutoOr+".output", "%s.input2" % (addDblLinAutoOr), force=True)
            mc.connectAttr(addDblLinAutoOr+'.output',getPointWeight[0], force=True)

            # ParentConstaint Arm ###
            cnsMb =libRig.createObj(partial(mc.group, **{'n':nCnsMb,'em': True}),match=[nRootO],father=nRootO,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            mc.parent(cnsMb, nIkHdlAo)
            mc.parentConstraint(nCnsMb,nRootO)
            # pointConstaint Arm ###
            mc.pointConstraint(fkClav[0],lsJntClav[0])

            # CLEAN fkClav__________________________________
            mc.delete(fkClav[-1])
            del fkClav[-1]
            # parent Ctr ###
            lsRootFk = []


            for i, each in enumerate(fkClav):
                nRootFk = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameClav+str(i+1),nSide=side,incP=incPart)
                rootFk =libRig.createObj(partial(mc.group, **{'n':nRootFk, 'em': True}),match=[each],father=nAo)
                # mc.delete(mc.parentConstraint(each, rootFk, mo=False))
                mc.parent(each, nRootFk)
                lsRootFk.append(nRootFk)
            [mc.parent(lsRootFk[i+1],each) for i, each in enumerate(fkClav[:-1])]

            # CREATE SCAPULA_____________________________________
            if self.name == "arm":
                tplScapula = mc.getAttr(eachTpl+".scapulaStart[0]")
                nBufScapula = gloss.name_format(prefix=gloss.lexicon('buf'), name='scapula', nSide=side,incP=incPart)
                nScapula = gloss.name_format(prefix=gloss.lexicon('c'), name='scapula', nSide=side,incP=incPart)
                nScapulaRot = gloss.name_format(prefix=gloss.lexicon('rot'), name='scapula',nSide=side,incP=incPart)
                bufScapula = libRig.createObj(partial(mc.group, **{'n':nBufScapula, 'em': True}),match=[fkClav[0]],
                father=fkClav[0],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                scapulaRot = libRig.createObj(partial(mc.group, **{'n':nScapulaRot, 'em': True}),match=[fkClav[0]],
                father=bufScapula,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                mc.parent(bufScapula ,lsRootFk[0])
                scapula = libRig.createController(name=nScapula, shape=libRig.Shp([self.typeCircle], color=valColorCtr,
                size=(0.2, 0.2, 0.2)),match=[tplScapula], father=scapulaRot,addInf=True,attributs={"drawStyle": 2})
                mc.setAttr(scapula['root']+".jointOrientX",0)
                mc.setAttr(scapula['root']+".jointOrientY",0)
                mc.setAttr(scapula['root']+".jointOrientZ",0)

                # SNAP SHAPE TPL SCAPULA________________________________________________________
                lib_shapes.snapShpCv(shpRef=tplScapula, shpTarget=scapula['c'])
                # CONNECT SCAPULA________________________________________________________
                nMltDivScapula = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name='scapula',nSide=side,incP=incPart)
                mltDivScapula = mc.createNode("multiplyDivide", n=nMltDivScapula)
                mc.setAttr(mltDivScapula + ".operation", 2)
                mc.setAttr(mltDivScapula + ".input2X",1.5)
                mc.connectAttr(fkClav[0]+".rotateX", "%s.rotateX" % (scapulaRot), force=True)
                mc.connectAttr(fkClav[0]+".rotateZ", "%s.input1X" % (mltDivScapula), force=True)
                nCndScapula = gloss.name_format(prefix=gloss.lexicon('cnd'),name='scapula',nSide=side, incP=incPart)
                NodeCndScapula = mc.createNode("condition", n=nCndScapula)
                mc.setAttr(NodeCndScapula + ".secondTerm", -10)
                mc.setAttr(NodeCndScapula + ".operation", 3)
                mc.setAttr(NodeCndScapula + ".colorIfFalseR",-10)
                mc.connectAttr(mltDivScapula+'.outputX', "%s.firstTerm" % (NodeCndScapula), force=True)
                mc.connectAttr(mltDivScapula+'.outputX', "%s.colorIfTrueR" % (NodeCndScapula), force=True)
                mc.connectAttr(NodeCndScapula+".outColorR", "%s.rotateZ" % (scapulaRot), force=True)

            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            # SK CLAV ______________
            for each in lsSkClav:
                mc.sets(each, edit=True, forceElement=nSetPart)
            if self.name == "arm":
                mc.sets(scapula['sk'], edit=True, forceElement=nSetPart)
            # SK MB_________________
            mc.sets(nSkTwistUp, edit=True, forceElement=nSetPart)
            for each in lsSk:
                mc.sets(each, edit=True, forceElement=nSetPart)
            mc.sets(nSkTwist, edit=True, forceElement=nSetPart)

            # LIST HOOK IN TPL INFO_________________________________________
            lsHooks = lsSkClav
            for i, each in enumerate(lsSk):
                lsHooks.insert(len(lsHooks)+1, each)
            if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                pass
            else:
                mc.addAttr(eachTpl, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
            [mc.setAttr(eachTpl+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]


            # ATTRIBUTES TO CONTROL GRP________________________________________________
            lsFkClav = fkClav
            lsIkMb = [ikCtr['c'],plV['c']]
            lsFkMb = fk[:len(concatIkFk)-(lenLsTplMidMb)]
            lsFkMb.insert(len(concatIkFk)-(lenLsTplMidMb), nJntRig1)
            lsFkMidMb = fk[len(concatIkFk)-(lenLsTplMidMb):-1]
            lsFkArc =lsConcatArc
            lsFkShp = lsCtrSk
            #if ctrTwistUp not in lsFkShp:
                #lsFkShp.append(ctrTwistUp)
            #if ctrTwist not in lsFkShp:
                #lsFkShp.append(ctrTwist)
            #print lsFkShp, 'titi'
            # NAME CG_____________________________________________
            cgClav = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgClav'),nSide=side,incP=incPart)
            cgIk = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgIk'),nSide=side,incP=incPart)
            cgFkMb = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)
            cgFkMidMb = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=self.nameEnd,nSide=side,incP=incPart)
            cgFkArc = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=self.name+'Arc',nSide=side,incP=incPart)
            cgFkShp = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=self.name+'Shp',nSide=side,incP=incPart)
            cgSwitch = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgSwitch'),nSide=side,incP=incPart)
            if mc.objExists(eachTpl+'.%s'%(cgFkMb)):
                pass
            else:
                mc.addAttr(eachTpl, ln=cgSwitch,dt='string',multi=True) # add Cg switch
                mc.addAttr(eachTpl, ln=cgClav,dt='string',multi=True) # add Clav Ctr
                mc.addAttr(eachTpl, ln=cgIk,dt='string',multi=True) # add ik Ctr
                mc.addAttr(eachTpl, ln=cgFkMb,dt='string',multi=True) # add Mb Fk
                mc.addAttr(eachTpl, ln=cgFkMidMb,dt='string',multi=True) # add MidMb Fk
                mc.addAttr(eachTpl, ln=cgFkArc,dt='string',multi=True) # add Arc Fk
                mc.addAttr(eachTpl, ln=cgFkShp,dt='string',multi=True) # add Shp Fk
            mc.setAttr(eachTpl+'.%s['%(cgSwitch) +str(0)+']',shapeAttrib,type='string')
            [mc.setAttr(eachTpl+'.%s['%(cgClav) +str(i)+']',each,type='string') for i, each in enumerate(lsFkClav)]
            [mc.setAttr(eachTpl+'.%s['%(cgIk) +str(i)+']',each,type='string') for i, each in enumerate(lsIkMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkMidMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkMidMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkArc)+str(i)+']',each,type='string') for i, each in enumerate(lsFkArc)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkShp)+str(i)+']',each,type='string') for i, each in enumerate(lsFkShp)]

            # PARENT CONTROLS WITH SHAPE SWITCH________________________________________________
            mc.parent(shapeAttrib, ikCtr['c'], s=True, add=True)
            mc.parent(shapeAttrib, nJntRig1, s=True, add=True)
            [mc.parent(shapeAttrib, each, s=True, add=True) for each in fk[:-1]]
            [mc.parent(shapeAttrib, each, s=True, add=True) for each in lsCtrSk]
            [mc.parent(shapeAttrib, each, s=True, add=True) for each in lsArcCtr]
            mc.parent(shapeAttrib, ctrTwistUp, s=True, add=True)
            mc.parent(shapeAttrib, ctrTwist, s=True, add=True)
            [mc.parent(shapeAttrib, each, s=True, add=True) for i, each in enumerate(nLsFkClav[:-1])]

            # PARENT HOOK WITH RIG MEMBER________________________________________________
            mc.parent(hookClv,self.hook)
            mc.parent(hookMb,self.hook)
            mc.parent(hookIk,self.hookIk)

            # ADD DICTIONARY RETURN________________________________________________
            dic["lsFk"] = fk
            dic["tplFk"] = lsTplCtr
            dic["lsFkMidMb"] = fk[len(concatIkFk)-(lenLsTplMidMb):]
            dic["lsFkMidMbJts"] = lsJntMidMb
            dic["ik"] = ikCtr['c']
            dic["FkTwist"] = nJntRig1
            dic["ikFkBlend"] = nIkBlend
            dic["cnsIkHdlMb"] = dstDimCns
            dic["upVRootEndMb"] = UpVRoot
            dic["upVEndMb"] = UpV
            dic["ikHdlFirst"] = ikHandleFirst
            dic["lsJntRig"] = [nJntRig1,nJntRig2]
            dic["grpNoTouch"] = GrpNoTouch
            dic["cnsPart"] = nCnsPart
            # to leg Patch
            dic["numbPart"] = numbPart
            dic["consSpine"] = consSpine
            dic["lsChainFk"] = lsChainFk
            dic["lsPlVRoot"] = lsPlVRoot
            dic["nNodeDstDim"] = nNodeDstDim
            dic["ikHandle"] = ikHandle
            dic["RootO"] = RootO
            dic["lsPlVCtr"] = lsPlVCtr
            dic["dstDimMb"] = dstDimMb
            dic["dstDimMbEnd"] = dstDimMbEnd
            dic["nIkHdlMb"] = nIkHdlMb
            dic["expMb"] = mc.expression(expSysStretch, s=True, q=True)
            dic["blendColor"] = lsBlendColor
            dic["shpAttrib"] = shapeAttrib
            dicMember["%s"%eachTpl] = dic
            if self.name == 'arm':
                dic["360"] = NodeMltDblL360Sk
            #mc.delete('locator1')

        return dicMember




    def createMidMember(self):
        # RIG MEMBER__________________________________________________________________
        dic = Member.createMember(self)
        #dicMidMember = {}
        for i, eachEl in enumerate(sorted(dic)):
            dicMidMember = {}
            incPart = mc.getAttr(eachEl+'.incInfo')
            side = (mc.attributeQuery("update",node=eachEl, listEnum=1)[0]).split(":")[1]
            if side == 'empty': side =''
            color = lib_shapes.side_color(side=side)
            valColorAdd = color["colorCtr"]
            valColorCtr = color["colorIk"]
            valColorCtrIK = color["colorMaster"]
            numbMdMb = mc.getAttr(eachEl+'.infoNumbMb[1]')
            lsBank =[mc.getAttr(eachEl+'.bank[%s]'%i) for i in range(mc.getAttr(eachEl+'.bank', mi=True,s=True))]
            lsTplMidMb =[mc.getAttr(eachEl+'.midMb[%s]'%i) for i in range(mc.getAttr(eachEl+'.midMb', mi=True,s=True))]
            if self.name == 'leg': tplHeel = mc.getAttr(eachEl+'.%sHeel[0]'%(self.nameEnd))

            # BANK SCALE__________________________________________________________________
            nBankScl = gloss.renameSplit(selObj=lsBank[0], namePart=['tplBank'], newNamePart=['sclBank'], reNme=False)
            bankScl = libRig.createObj(partial(mc.group, **{'n':nBankScl,'em':True}),match=[lsBank[0]],father=dic[eachEl]['ik'],attributs={"visibility":0})
            # CREATE BANK__________________________________________________________________
            lsBankRoot = []
            lsBankCtr = []
            for each in lsBank:
                nBankRoot = gloss.renameSplit(selObj=each, namePart=['tplBank'], newNamePart=['rootBank'], reNme=False)
                nBank = gloss.renameSplit(selObj=each, namePart=['tplBank'], newNamePart=['bank'], reNme=False)
                bankRoot = libRig.createObj(partial(mc.group, **{'n':nBankRoot,'em':True}),match=[each],father=None,attributs={"visibility":1})
                bank = libRig.createObj(partial(mc.spaceLocator, **{'n':nBank}),match=[each],father=bankRoot,attributs={"visibility":1})
                lsBankRoot.append(bankRoot)
                lsBankCtr.append(bank)
            # PARENT_______________________________________________________________________
            mc.parent(lsBankRoot[0],bankScl)
            [mc.parent(each,lsBankCtr[i]) for i, each in enumerate(lsBankRoot[1:])]
            # connect Attributes roll pivot ________________________________
            nMltDivHeel2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('heel')+'Mlt',nSide=side,incP=incPart)
            nMltDivRoll2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Mlt',nSide=side,incP=incPart)
            nMltDivPiv2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('piv')+'Mlt',nSide=side,incP=incPart)

            mltDivHeel2 = mc.createNode("multiplyDivide", n=nMltDivHeel2)
            mc.setAttr(mltDivHeel2 + ".operation", 1)
            mc.setAttr(mltDivHeel2 + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik'] + '.%s Roll' % (self.nameKnot2), "%s.input1X" % (mltDivHeel2), force=True)
            if side == "R" and self.name == 'leg':
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='knotPivot',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(dic[eachEl]['ik'] + '.%s Roll' % (self.nameKnot2), "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivHeel2), force=True)

            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivHeel2 + '.outputX', "%s.rotate%s" % (lsBankCtr[0],val), force=True)

            multDivRoll2 = mc.createNode("multiplyDivide", n=nMltDivRoll2)
            mc.setAttr(multDivRoll2  + ".operation", 1)
            mc.setAttr(multDivRoll2  + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik'] + '.knotRoll', "%s.input1X" % (multDivRoll2), force=True)
            val = 'X'
            if self.name == 'arm':
                val = 'Z'
                if side =='R':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='r',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.knotRoll', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (multDivRoll2), force=True)
            mc.connectAttr(multDivRoll2 + '.outputX', "%s.rotate%s" % (lsBankCtr[1],val), force=True)

            mltDivPiv2 = mc.createNode("multiplyDivide", n=nMltDivPiv2)
            mc.setAttr(mltDivPiv2  + ".operation", 1)
            mc.setAttr(mltDivPiv2  + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik'] + '.knot Pivot', "%s.input1X" % (mltDivPiv2), force=True)
            if side == "R" and self.name == 'leg':
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='knotPivot',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(dic[eachEl]['ik'] + '.knot Pivot', "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivPiv2), force=True)

            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivPiv2 + '.outputX', "%s.rotate%s" % (lsBankCtr[1],val), force=True)


            # connect Attributes bank ________________________________
            nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('bank'),nSide=side,incP=incPart)
            nMltDivBank2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('bank')+'Mlt',nSide=side,incP=incPart)
            nCondition1 = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('bank')+'R',nSide=side,incP=incPart)
            NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
            if side == "L" and self.name == 'leg':
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
            elif side == "R" and self.name == 'arm':
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
            else:
                mc.setAttr(NodeMltDblLinear + ".input2", 1)
            mc.connectAttr(dic[eachEl]['ik']+'.bank', "%s.input1" % (NodeMltDblLinear), force=True)
            mltDivBank2 = mc.createNode("multiplyDivide", n=nMltDivBank2)
            mc.setAttr(mltDivBank2 + ".operation", 1)
            mc.setAttr(mltDivBank2 + ".input2X",9)
            mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivBank2), force=True)
            NodeCondition = mc.createNode("condition", n=nCondition1)
            if side == "L":
                if self.name == 'leg':
                    mc.setAttr(NodeCondition + ".operation", 3)
                else:
                    mc.setAttr(NodeCondition + ".operation", 4)
            else:
                if self.name == 'leg':
                    mc.setAttr(NodeCondition + ".operation", 4)
                else:
                    mc.setAttr(NodeCondition + ".operation", 3)
            mc.setAttr(NodeCondition + ".colorIfTrueG",0)
            mc.setAttr(NodeCondition + ".colorIfFalseR",0)
            mc.connectAttr(NodeMltDblLinear+'.output', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(mltDivBank2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition), force=True)
            mc.connectAttr(mltDivBank2 + '.outputX', "%s.colorIfFalseG" % (NodeCondition), force=True)
            val = 'Z'
            if self.name == 'arm': val = 'Y'
            mc.connectAttr(NodeCondition + '.outColorR', "%s.rotate%s" % (lsBankCtr[3],val), force=True)
            mc.connectAttr(NodeCondition + '.outColorG', "%s.rotate%s" % (lsBankCtr[2],val), force=True)

            # connect bank first to Attributes roll ________________________________
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Mlt',nSide=side,incP=incPart)
            nCondition = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll'),nSide=side,incP=incPart)

            NodeMultDiv2 = mc.createNode("multiplyDivide", n=nMultMat2)
            mc.setAttr(NodeMultDiv2 + ".operation", 1)
            mc.setAttr(NodeMultDiv2 + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.input1X" % (NodeMultDiv2), force=True)

            NodeCondition = mc.createNode("condition", n=nCondition)
            mc.setAttr(NodeCondition + ".operation", 5)
            mc.setAttr(NodeCondition + ".colorIfFalseR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition), force=True)

            val = 'X'
            if self.name == 'arm':
                val = 'Z'
                if side =='L':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='l',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.roll', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (NodeMultDiv2), force=True)

            mc.connectAttr(NodeCondition + '.outColorR',"%s.rotate%s" % (lsBankCtr[0],val), force=True)
            # CREATE FOOT/HAND ROLL_____________________________________________________________
            lsRollRoot = []
            lsRollCtr = []
            for i, each in enumerate(lsTplMidMb[:-1]):
                nBallRollRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameEnd,nFunc=gloss.lexicon('ballRoll')+"%s"%(i+1),nSide=side,incP=incPart)
                nBallRoll = gloss.name_format(prefix=gloss.lexicon('ballRoll'),name=self.nameEnd+"%s"%(i+1),nSide=side,incP=incPart)
                rollRoot = libRig.createObj(partial(mc.group, **{'n':nBallRollRoot,'em':True}),match=[each],father=None,attributs={"visibility":1})
                roll = libRig.createObj(partial(mc.spaceLocator, **{'n':nBallRoll}),match=[each],father=rollRoot,attributs={"visibility":1})
                lsRollRoot.append(rollRoot)
                lsRollCtr.append(roll)
            # PARENT_______________________________________________________________________
            if len(lsRollRoot) ==1:
                mc.parent(lsRollRoot[0],lsBankCtr[-1])
                mc.parent(dic[eachEl]["cnsIkHdlMb"],lsRollCtr[0])
            else:
                count = len(lsRollRoot)
                for each in reversed(lsRollRoot):
                    if each == lsRollRoot[-1]:
                        mc.parent(lsRollRoot[-1],lsBankCtr[-1])
                    else:
                        mc.parent(each,lsRollCtr[count])
                    count -=1
                mc.parent(dic[eachEl]["cnsIkHdlMb"],lsRollCtr[0])
            # connect Attributes piv for roll ________________________________
            nMltDivBallPiv2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('ballPiv')+'Mlt',nSide=side,incP=incPart)

            mltDivBallPiv2 = mc.createNode("multiplyDivide", n=nMltDivBallPiv2)
            mc.setAttr(mltDivBallPiv2 + ".operation", 1)
            mc.setAttr(mltDivBallPiv2 + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik'] + '.ballPivot', "%s.input1X" % (mltDivBallPiv2), force=True)
            if self.name == 'leg' and side =='R':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('ballPiv')+'Inv',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.ballPivot', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivBallPiv2), force=True)

            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivBallPiv2 + '.outputX', "%s.rotate%s" % (lsRollCtr[-1],val), force=True)
            # connect roll ________________________________
            nMultMat1 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys'+'Div',nSide=side,incP=incPart)
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys'+'Mlt',nSide=side,incP=incPart)
            nCondition = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys',nSide=side,incP=incPart)
            NodeMultDiv1 = mc.createNode("multiplyDivide", n=nMultMat1)
            mc.setAttr(NodeMultDiv1 + ".operation",2)
            mc.setAttr(NodeMultDiv1 + ".input2X",10)
            if self.nameEnd == 'hand':
                mc.setAttr(NodeMultDiv1 + ".input2X",10.1)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.input1X" % (NodeMultDiv1), force=True)
            NodeMultDiv2 = mc.createNode("multiplyDivide", n=nMultMat2)
            mc.setAttr(NodeMultDiv2 + ".operation", 1)
            mc.setAttr(NodeMultDiv2 + ".input2X",90)
            mc.connectAttr(NodeMultDiv1 + '.outputX', "%s.input1X" % (NodeMultDiv2), force=True)

            NodeCondition = mc.createNode("condition", n=nCondition)
            mc.setAttr(NodeCondition + ".operation", 3)
            mc.setAttr(NodeCondition + ".colorIfFalseR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition), force=True)

            val = 'X'
            if self.name == 'arm':
                val = 'Z'
            [mc.connectAttr(NodeCondition + '.outColorR',"%s.rotate%s" % (each,val), force=True) for each in lsRollCtr]


            # connect Attributes rollBreak ________________________________
            nMltDivRollBreak2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'BreakMlt',nSide=side,incP=incPart)
            nClampMinBreak = gloss.name_format(prefix=gloss.lexicon('clmp'),name=self.nameEnd,nFunc=gloss.lexicon('min')+'Break',nSide=side,incP=incPart)
            nClampMinBreakKnot = gloss.name_format(prefix=gloss.lexicon('clmp'),name=self.nameEnd,nFunc=gloss.lexicon('min')+'BreakKnot',nSide=side,incP=incPart)
            nClampMaxBreak = gloss.name_format(prefix=gloss.lexicon('clmp'),name=self.nameEnd,nFunc=gloss.lexicon('max')+'Break',nSide=side,incP=incPart)
            nInverBreak = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='break',nSide=side,incP=incPart)
            nPlusMinBreak = gloss.name_format(prefix=gloss.lexicon('plMA'),name=self.nameEnd,nFunc='sub'+'Break',nSide=side,incP=incPart)
            nPlusMinBreakKnotSub = gloss.name_format(prefix=gloss.lexicon('plMA'),name=self.nameEnd,nFunc='sub' +'KnotBreak',nSide=side,incP=incPart)
            nPlusMinBreakKnotSum = gloss.name_format(prefix=gloss.lexicon('plMA'),name=self.nameEnd,nFunc='sum' +'KnotBreak',nSide=side,incP=incPart)
            nInverSubBreak = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='sub' +'Break',nSide=side,incP=incPart)


            nMltDivRollOffset = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Offset',nSide=side,incP=incPart)
            nPlusMinRollOffset = gloss.name_format(prefix=gloss.lexicon('plMA'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Offset',nSide=side,incP=incPart)


            multDivRollBreak2 = mc.createNode("multiplyDivide", n=nMltDivRollBreak2)
            mc.setAttr(multDivRollBreak2  + ".operation", 1)
            mc.setAttr(multDivRollBreak2  + ".input2X",9)
            mc.connectAttr(dic[eachEl]['ik'] + '.rollBreak', "%s.input1X" % (multDivRollBreak2), force=True)

            clampMinBreak = mc.createNode("clamp", n=nClampMinBreak)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.inputR" % (clampMinBreak), force=True)
            mc.connectAttr(multDivRollBreak2 + '.outputX', "%s.minR" % (clampMinBreak), force=True)

            clampMaxBreak = mc.createNode("clamp", n=nClampMaxBreak)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.inputR" % (clampMaxBreak), force=True)
            mc.connectAttr(multDivRollBreak2 + '.outputX', "%s.maxR" % (clampMaxBreak), force=True)

            plusMinBreak = mc.createNode("plusMinusAverage", n=nPlusMinBreak)
            mc.setAttr(plusMinBreak + ".operation", 2)
            mc.connectAttr(clampMinBreak + '.outputR', "%s.input1D[1]" % (plusMinBreak), force=True)
            mc.connectAttr(clampMaxBreak + '.outputR', "%s.input1D[0]" % (plusMinBreak), force=True)

            if self.name == 'arm' and side =='L':
                NodeMltDblLinearBreak = mc.createNode("multDoubleLinear", n=nInverBreak)
                mc.setAttr(NodeMltDblLinearBreak + ".input2", -1)
                mc.connectAttr(plusMinBreak + '.output1D', "%s.input1" % (NodeMltDblLinearBreak), force=True)
                mc.connectAttr(NodeMltDblLinearBreak + '.output', "%s.colorIfTrueR" % (NodeCondition), force=True)
            else:
                mc.connectAttr(plusMinBreak + '.output1D', "%s.colorIfTrueR" % (NodeCondition), force=True)
            clampMinBreakKnot = mc.createNode("clamp", n=nClampMinBreakKnot)
            mc.setAttr(clampMinBreakKnot  + ".maxR",999)
            mc.connectAttr(NodeMultDiv2  + '.outputX', "%s.inputR" % (clampMinBreakKnot), force=True)
            mc.connectAttr(multDivRollBreak2   + '.outputX', "%s.minR" % (clampMinBreakKnot), force=True)
            plusMinBreakKnotSub = mc.createNode("plusMinusAverage", n=nPlusMinBreakKnotSub)
            mc.setAttr(plusMinBreakKnotSub + ".operation", 2)
            mc.connectAttr(multDivRollBreak2 + '.outputX', "%s.input1D[1]" % (plusMinBreakKnotSub), force=True)
            mc.connectAttr(clampMinBreakKnot + '.outputR', "%s.input1D[0]" % (plusMinBreakKnotSub), force=True)
            plusMinBreakKnotSum = mc.createNode("plusMinusAverage", n=nPlusMinBreakKnotSum)
            mc.setAttr(plusMinBreakKnotSum + ".operation", 1)
            mc.connectAttr(multDivRoll2 + '.outputX', "%s.input1D[1]" % (plusMinBreakKnotSum), force=True)
            mc.connectAttr(plusMinBreakKnotSub + '.output1D', "%s.input1D[0]" % (plusMinBreakKnotSum), force=True)

            valBreak = 'X'
            if self.name == 'arm':
                valBreak = 'Z'

            if self.name == 'arm' and side =='L':
                NodeMltDblLinearSubBreak = mc.createNode("multDoubleLinear", n=nInverSubBreak)
                mc.setAttr(NodeMltDblLinearSubBreak + ".input2", -1)
                mc.connectAttr(plusMinBreakKnotSum + '.output1D', "%s.input1" % (NodeMltDblLinearSubBreak), force=True)
                mc.connectAttr(NodeMltDblLinearSubBreak + '.output', "%s.rotate%s" % (lsBankCtr[1],valBreak), force=True)

            else:
                mc.connectAttr(plusMinBreakKnotSum + '.output1D', "%s.rotate%s" % (lsBankCtr[1],valBreak), force=True)


            # rollOffset________________________________________________________________________________________________
            multDivRollOffset = mc.createNode("multiplyDivide", n=nMltDivRollOffset)
            mc.setAttr(multDivRollOffset + ".operation", 1)
            mc.setAttr(multDivRollOffset + ".input2X",8.9)
            mc.connectAttr(dic[eachEl]['ik'] + '.rollOffset', "%s.input1X" % (multDivRollOffset), force=True)
            plusMinRollOffset = mc.createNode("plusMinusAverage", n=nPlusMinRollOffset)
            mc.setAttr(plusMinRollOffset + ".operation", 2)
            mc.connectAttr(NodeCondition + '.outColorR', "%s.input1D[0]" % (plusMinRollOffset), force=True)
            mc.connectAttr(multDivRollOffset + '.outputX', "%s.input1D[1]" % (plusMinRollOffset), force=True)
            val = 'X'
            if self.name == 'arm':
                val = 'Z'
            [mc.connectAttr(plusMinRollOffset + '.output1D',"%s.rotate%s" % (each,val), force=True) for each in lsRollCtr]


            # END ROLL____________________________________________________________________
            nBallRollEnd = gloss.name_format(prefix=gloss.lexicon('ballRoll'),name=self.nameEnd,nFunc=gloss.lexicon('end'),nSide=side,incP=incPart)
            nCnsIkHdlEnd = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.nameEnd,nFunc=gloss.lexicon('ikHdl'),nSide=side,incP=incPart)
            ballRollEnd = libRig.createObj(partial(mc.group, **{'n':nBallRollEnd,'em':True}),match=lsRollRoot[-1],father=lsBankCtr[-1])
            cnsIkHdlEnd = libRig.createObj(partial(mc.group, **{'n':nCnsIkHdlEnd,'em':True}),match=dic[eachEl]["lsFkMidMb"][-1],father=ballRollEnd,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})

            # CREATE STOMP SYSTEM___________________________________________________________
            nhookMidMb = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.nameEnd,nSide=side,incP=incPart)
            nCnsStomp = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.nameEnd,nFunc=gloss.lexicon('stomp'),nSide=side,incP=incPart)
            nLsJtsStomp = [gloss.name_format(prefix=gloss.lexicon('cns'),name=self.nameEnd,nFunc=gloss.lexicon('stomp')+"%s"%each,nSide=side,incP=incPart) for each in range(2)]
            nSclStomp = gloss.name_format(prefix=gloss.lexicon('scl'),name=self.nameEnd,nFunc=gloss.lexicon('stomp'),nSide=side,incP=incPart)
            nStompRootIkHdl = gloss.name_format(prefix=gloss.lexicon('root'),name=self.nameEnd,nFunc=gloss.lexicon('stomp')+'ikHdl',nSide=side,incP=incPart)
            hookMidMb = libRig.createObj(partial(mc.group, **{'n':nhookMidMb,'em':True}),father=self.nRig)
            cnsStomp  = libRig.createObj(partial(mc.group, **{'n':nCnsStomp,'em':True}),match=[dic[eachEl]["lsFkMidMbJts"][0]],father=hookMidMb)
            jtsStomp1 = libRig.createObj(partial(mc.joint, **{'n':nLsJtsStomp[0]}),match=[dic[eachEl]["cnsIkHdlMb"]],father=cnsStomp,attributs={"drawStyle": 2})
            jtsStomp2 = libRig.createObj(partial(mc.joint, **{'n':nLsJtsStomp[1]}),match=[dic[eachEl]["cnsIkHdlMb"]],father=jtsStomp1,attributs={"drawStyle": 2})

            mc.move(0,-0.5*mc.getAttr("tpl_WORLD"+".scaleX"),0,jtsStomp2, ls=True)
            sclStomp  = libRig.createObj(partial(mc.group, **{'n':nSclStomp,'em':True}),match=[dic[eachEl]["cnsIkHdlMb"]],father=jtsStomp1)
            getRot = mc.xform(bankScl, q=True, ws=True, rotation=True)
            mc.xform(sclStomp, worldSpace=True, ro=getRot)
            stompRootIkHdl  = libRig.createObj(partial(mc.group, **{'n':nStompRootIkHdl,'em':True}),match=[jtsStomp2],father=dic[eachEl]['ik'])
            # create ik handle stomp_________________________________
            nStompIkHdl = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameEnd,nFunc=gloss.lexicon('stomp'),nSide=side,incP=incPart)
            ikHdlStomp = libRig.createObj(partial(mc.ikHandle, **{'n':nStompIkHdl,'sj':jtsStomp1,'ee':jtsStomp2,'sol':"ikSCsolver"}),match=[stompRootIkHdl],father=stompRootIkHdl,attributs={"snapEnable": 0,"visibility":0})
            mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHdlStomp+'.ikBlend')
            # connect Attribute stomp with scale groups_________________________________
            nMultMat1 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('stomp')+'XZ',nSide=side,incP=incPart)
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('stomp')+'Y',nSide=side,incP=incPart)
            nAddDblLin = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('stomp'),nSide=side,incP=incPart)
            nAddDblLin2 = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('stomp')+'Min',nSide=side,incP=incPart)
            nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('stomp'),nSide=side,incP=incPart)
            NodeMultDiv1 = mc.createNode("multiplyDivide", n=nMultMat1)
            mc.setAttr(NodeMultDiv1 + ".operation", 2)
            mc.setAttr(NodeMultDiv1 + ".input2X",25)
            mc.connectAttr(dic[eachEl]['ik'] + '.stomp', "%s.input1X" % (NodeMultDiv1), force=True)
            NodeMultDiv2 = mc.createNode("multiplyDivide", n=nMultMat2)
            mc.setAttr(NodeMultDiv2 + ".operation", 2)
            mc.setAttr(NodeMultDiv2 + ".input2X",12.5)
            mc.connectAttr(dic[eachEl]['ik'] + '.stomp', "%s.input1X" % (NodeMultDiv2), force=True)
            NodeAddDblLinear = mc.createNode("addDoubleLinear", n=nAddDblLin)
            mc.setAttr(NodeAddDblLinear + ".input1", 1)
            mc.connectAttr("%s.outputX" % (NodeMultDiv1), "%s.input2" % (NodeAddDblLinear), force=True)
            NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
            mc.setAttr(NodeMltDblLinear + ".input2", -1)
            mc.connectAttr("%s.outputX" % (NodeMultDiv2), "%s.input1" % (NodeMltDblLinear), force=True)
            NodeAddDblLinearMin = mc.createNode("addDoubleLinear", n=nAddDblLin2)
            mc.setAttr(NodeAddDblLinearMin + ".input1", 1)
            mc.connectAttr("%s.output" % (NodeMltDblLinear), "%s.input2" % (NodeAddDblLinearMin), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinear), "%s.scaleX" % (bankScl), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinearMin), "%s.scaleY" % (bankScl), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinear), "%s.scaleZ" % (bankScl), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinear), "%s.scaleX" % (sclStomp), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinearMin), "%s.scaleY" % (sclStomp), force=True)
            mc.connectAttr("%s.output" % (NodeAddDblLinear), "%s.scaleZ" % (sclStomp), force=True)
            if self.name == 'arm':
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='divStomp1',nSide=side,incP=incPart)
                mltDblLinStomp = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(mltDblLinStomp + ".input2", -1)
                mc.connectAttr(dic[eachEl]['ik'] + '.stomp', "%s.input1" % (mltDblLinStomp), force=True)
                mc.connectAttr(mltDblLinStomp+'.output', "%s.input1X" % (NodeMultDiv1), force=True)
                mc.connectAttr(mltDblLinStomp+'.output', "%s.input1X" % (NodeMultDiv2), force=True)
            # connect Attribute stomp with ik handle stomp_________________________________
            nMultMat1 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('ikHdl')+'1'+'Stomp',nSide=side,incP=incPart)
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('ikHdl')+'2'+'Stomp',nSide=side,incP=incPart)
            nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('ikHdl')+'Stomp',nSide=side,incP=incPart)
            nCondition = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('ikHdl')+'Stomp',nSide=side,incP=incPart)
            NodeMultDiv1 = mc.createNode("multiplyDivide", n=nMultMat1)
            mc.setAttr(NodeMultDiv1 + ".operation",1)
            mc.setAttr(NodeMultDiv1 + ".input2X",90)
            mc.connectAttr(dic[eachEl]['ik'] + '.stomp', "%s.input1X" % (NodeMultDiv1), force=True)
            NodeMultDiv2 = mc.createNode("multiplyDivide", n=nMultMat2)
            mc.setAttr(NodeMultDiv2 + ".operation", 1)
            mc.setAttr(NodeMultDiv2 + ".input2X",90)
            NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
            mc.setAttr(NodeMltDblLinear + ".input2", -1)
            mc.connectAttr(dic[eachEl]['ik']+'.stomp', "%s.input1" % (NodeMltDblLinear), force=True)
            mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (NodeMultDiv2), force=True)
            NodeCondition = mc.createNode("condition", n=nCondition)
            mc.setAttr(NodeCondition + ".operation", 3)
            mc.connectAttr(dic[eachEl]['ik'] + '.stomp', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition), force=True)
            mc.connectAttr(NodeMultDiv1 + '.outputX', "%s.colorIfFalseR" % (NodeCondition), force=True)
            mc.connectAttr(NodeCondition + '.outColorR', "%s.translateY" % (ikHdlStomp), force=True)

            # PARENT CONSTRAINT CNS FOOT STOMP TO JNT RIG1 ___________________
            mc.parentConstraint(dic[eachEl]["cnsPart"],nCnsStomp)
            nMltDivStomp = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc='stompScl',nSide=side,incP=incPart)
            NodeMultDivStomp = mc.createNode("multiplyDivide", n=nMltDivStomp)
            mc.setAttr(NodeMultDiv1 + ".operation", 1)
            mc.connectAttr(dic[eachEl]['ik'] + '.scale', "%s.input1" % (NodeMultDivStomp), force=True)
            mc.connectAttr(dic[eachEl]['FkTwist'] + '.scale', "%s.input2" % (NodeMultDivStomp), force=True)
            mc.connectAttr(NodeMultDivStomp + '.output', "%s.scale" % (nCnsStomp), force=True)

            # CONSTRAINT ROOT UP VECTOR TO LAST ROLL CTR _____________________
            mc.orientConstraint(lsRollCtr[0],dic[eachEl]["upVRootEndMb"])

            # PARENT IK HANDLE FIRST TO LAST ROLL CTR_________________________
            mc.parent(dic[eachEl]["ikHdlFirst"],lsRollCtr[0])

            # ADJUST HIERARCHY FOOT __________________________________________
            mc.parent(dic[eachEl]['lsFkMidMbJts'][0],nSclStomp)
            # CREATE IK HANDLE FOOT/HAND______________________________________
            lsParentRollCtr = lsRollCtr
            lsParentRollCtr.insert(len(lsRollCtr), cnsIkHdlEnd)

            # CREATE IK HANDLE FOOT1/HAND1______________________________________
            nIkHdlMb = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameEnd,nFunc=gloss.lexicon('jnt')+"1",nSide=side,incP=incPart)
            ikHandle = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlMb ,'sj':dic[eachEl]['lsFkMidMbJts'][0],'ee':dic[eachEl]['lsFkMidMbJts'][1],'sol':self.IkType}),
                                        match=[lsParentRollCtr[0]],father=lsParentRollCtr[0],attributs={"snapEnable": 0,"visibility":0})
            poleV1 = mc.poleVectorConstraint(dic[eachEl]["upVEndMb"], ikHandle)
            mc.setAttr(ikHandle+".twist",abs(mc.getAttr(dic[eachEl]['lsFkMidMbJts'][0]+".rotateY")))
            mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHandle+'.ikBlend')
            if abs(mc.getAttr(dic[eachEl]['lsFkMidMbJts'][0]+'.rotateX')) > 1 :
                mc.setAttr(ikHandle+'.twist',180)
            else:
                pass


            # CREATE UPV TO CHAIN FOOT _______________________________________
            lsUpJnt= []

            for i, each in enumerate(dic[eachEl]['lsFkMidMb'][1:-1]):
                nUpV = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.nameEnd,nFunc=gloss.lexicon('jnt')+"%s"%(i+2),nSide=side, incP=incPart)
                if i ==0:
                    UpV = libRig.createObj(partial(mc.group, **{'n':nUpV, 'em': True}),match=[each],father=dic[eachEl]['lsFkMidMbJts'][0],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                else:
                    UpV = libRig.createObj(partial(mc.group, **{'n':nUpV, 'em': True}),match=[each],father=dic[eachEl]['lsFkMidMb'][i],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                mc.move(0,0,1*mc.getAttr("tpl_WORLD"+".scaleX"),UpV, ls=True, r=True)
                lsUpJnt.append(nUpV)

            lsIkHandleMidMbJnt = []
            for i, each in enumerate(dic[eachEl]['lsFkMidMbJts'][1:-1]):
                nIkHdlMb = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameEnd,nFunc=gloss.lexicon('jnt')+"%s"%(i+2),nSide=side,incP=incPart)

                ikHandle2 = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlMb ,'sj':each,'ee':dic[eachEl]['lsFkMidMbJts'][i+2],'sol':self.IkType}),
                                            match=[lsParentRollCtr[i+1]],father=lsParentRollCtr[i+1],attributs={"snapEnable": 0,"visibility":0})
                poleV2= mc.poleVectorConstraint(lsUpJnt[i], ikHandle2)
                mc.setAttr(ikHandle2+".twist",abs(mc.getAttr(each+".rotateY")))
                mc.disconnectAttr(poleV2[0]+'.constraintTranslateY',ikHandle2+'.poleVectorY')
                mc.disconnectAttr(poleV2[0]+'.constraintTranslateZ',ikHandle2+'.poleVectorZ')
                mc.setAttr(ikHandle2+'.poleVectorY', 0)
                mc.setAttr(ikHandle2+'.poleVectorZ', 0)
                mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHandle2+'.ikBlend')
                lsIkHandleMidMbJnt.append(ikHandle2)
                if abs(mc.getAttr(each+'.rotateX')) > 1 :
                    mc.setAttr(ikHandle2+'.twist',180)
                else:
                    pass





            # parent UPV TO JNTS _______________________________________
            for i, each in enumerate(dic[eachEl]['lsFkMidMbJts'][1:-2]):
                mc.parent(lsUpJnt[1:][i],each)

            # ADD ROOT TO CTR FOOT/HAND ________________________________
            mc.parent(dic[eachEl]['lsFkMidMb'][0],dic[eachEl]['lsFkMidMbJts'][0])
            # mc.setAttr(dic[eachEl]['lsFkMidMb'][0]+'.jointOrientY', 0)


            # DELETE LAST CTR___________________________________________
            mc.delete(dic[eachEl]['lsFkMidMb'][-1])
            newFkMidMB = dic[eachEl]['lsFkMidMb'][1:]
            del newFkMidMB[-1]
            lsSkMidMb = []
            for i, each in enumerate(newFkMidMB):
                nBufCtr= gloss.renameSplit(selObj=each, namePart=['c'], newNamePart=['buf'], reNme=False)
                nRootCtr= gloss.renameSplit(selObj=each, namePart=['c'], newNamePart=['root'], reNme=False)
                nSkCtr= gloss.renameSplit(selObj=each, namePart=['c'], newNamePart=['sk'], reNme=False)
                bufCtr= libRig.createObj(partial(mc.joint, **{'n':nBufCtr}),match=[each],father=each,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                rootCtr= libRig.createObj(partial(mc.joint, **{'n':nRootCtr}),match=[bufCtr],father=bufCtr,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                skCtr= libRig.createObj(partial(mc.joint, **{'n':nSkCtr}),match=[rootCtr],father=rootCtr,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                mc.parent(bufCtr, w=True)
                mc.parent(each,rootCtr)
                if i == 0:
                    mc.parent(bufCtr,dic[eachEl]['lsFkMidMb'][0])
                    nSkCtrBase= gloss.renameSplit(selObj=dic[eachEl]['lsFkMidMb'][0], namePart=['c'], newNamePart=['sk'], reNme=False)
                    skCtrBase= libRig.createObj(partial(mc.joint, **{'n':nSkCtrBase}),match=[dic[eachEl]['lsFkMidMb'][0]],father=dic[eachEl]['lsFkMidMb'][0],
                                            attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                    if self.name == 'arm':
                        mc.connectAttr(dic[eachEl]['360'] + ".output", "%s.rotateY" % (skCtrBase), force=True)
                else:
                    mc.parent(bufCtr,newFkMidMB[i-1])
                mc.setAttr(bufCtr + ".segmentScaleCompensate", 0)
                lib_connectNodes.connectAxis(each,skCtr)
                lib_connectNodes.connectAxis(dic[eachEl]['lsFkMidMbJts'][1:][i],bufCtr,pos=False,rot=True,scl=False)
                lsSkMidMb.append(nSkCtr)
                # NODES BALL ROLL ________________________________
                nMltDivRoll1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'BallDiv',nSide=side,incP=incPart)
                nMltDivRoll2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'BallMlt',nSide=side,incP=incPart)

                multDivRoll1 = mc.createNode("multiplyDivide", n=nMltDivRoll1)
                mc.setAttr(multDivRoll1 + ".operation", 2)
                mc.setAttr(multDivRoll1 + ".input2X",10)
                mc.connectAttr(dic[eachEl]['ik'] + '.ballRoll', "%s.input1X" % (multDivRoll1), force=True)
                multDivRoll2 = mc.createNode("multiplyDivide", n=nMltDivRoll2)
                mc.setAttr(multDivRoll2  + ".operation", 1)
                mc.setAttr(multDivRoll2  + ".input2X",90)
                mc.connectAttr(multDivRoll1 + '.outputX', "%s.input1X" % (multDivRoll2), force=True)
            if self.name == 'arm':
                mc.connectAttr(multDivRoll2 + '.outputX', "%s.rotateX" % (rootCtr), force=True)
            else:
                mc.connectAttr(multDivRoll2 + '.outputX', "%s.rotateZ" % (rootCtr), force=True)

            # CREATE MATCH IK_________________________________________________
            nMatchIk = gloss.name_format(prefix='MatchIk', name=self.nameEnd,nSide=side, incP=incPart)
            matchIk = libRig.createObj(partial(mc.group, **{'n':nMatchIk, 'em': True}),match=[dic[eachEl]['ik']],father=dic[eachEl]['FkTwist'])

            # CREATE HEEL CONTROL_________________________________________________
            if self.name == 'leg':
                tplHeel = mc.getAttr(eachEl+'.%sHeel[0]'%(self.nameEnd))
                rotOrdFk = libRgPreset.configAxis(mb="rOrdFoot")["rOrdFk"]
                nHeelCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('heel'),nSide=side,incP=incPart)
                heelCtr = libRig.createController(name=nHeelCtr,shape=libRig.Shp([self.typeCircle],color=valColorCtrIK,size=(0.2,0.2,0.2)),
                                            match=[tplHeel], father=dic[eachEl]['lsFkMidMb'][0],attributs={"rotateOrder":rotOrdFk,"drawStyle": 2})
                getRot = mc.xform(dic[eachEl]['lsFkMidMb'][1], q=True, ws=True, rotation=True)
                mc.xform(heelCtr['root'], worldSpace=True, ro=getRot)
                lib_shapes.snapShpCv(shpRef=tplHeel, shpTarget=heelCtr['c'])



            #CONNECT NODE TO INIT AXIS WITH SWITCH IK/FK____________________________________
            nMltDInitAxis = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='init'+'Axis',nSide=side,incP=incPart)

            multDInitAxis = mc.createNode("multiplyDivide", n=nMltDInitAxis)
            mc.setAttr(multDInitAxis + ".operation", 1)
            mc.connectAttr(multDInitAxis + '.output', "%s.rotate" % (jtsStomp1), force=True)
            mc.connectAttr(multDInitAxis + '.output', "%s.rotate" % (jtsStomp2), force=True)
            for each in dic[eachEl]["lsFkMidMbJts"]:
                mc.connectAttr(multDInitAxis + '.output', "%s.rotate" % (each), force=True)


            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            mc.sets(nSkCtrBase, edit=True, forceElement=nSetPart)
            for each in lsSkMidMb:
                mc.sets(each, edit=True, forceElement=nSetPart)
            # ADD DICTIONARY RETURN________________________________________________
            dic["%s"%eachEl].update(dicMidMember=newFkMidMB)
            dic["%s"%eachEl].update(dicMidMbCtr=dic[eachEl]['lsFkMidMb'][:-1])

            # DICTIONARY TO CONTROL GRP________________________________________________
            dicCtrGrp ={}
            ctrMidMb = dic[eachEl]['lsFkMidMb'][:-1]

            # PARENT HOOK WITH RIG MEMBER________________________________________________
            mc.parent(hookMidMb,self.hook)

            # IK BLEND DEFAULT VALUE 0________________________________________________
            if self.nameEnd == 'hand':
                mc.setAttr(dic[eachEl]["shpAttrib"] + ".ikBlend",0)



        return dic


    def createEndMember(self):
        # RIG MEMBER__________________________________________________________________
        dic = Member.createMidMember(self)
        for i, eachEl in enumerate(sorted(dic)):
            incPart = mc.getAttr(eachEl+'.incInfo')
            side = (mc.attributeQuery("update",node=eachEl, listEnum=1)[0]).split(":")[1]
            if side == 'empty': side =''
            color = lib_shapes.side_color(side=side)
            valColorAdd = color["colorCtr"]
            valColorCtr = color["colorIk"]
            valColorCtrIK = color["colorMaster"]
            dicTplEndMb ={}
            lSkHook = []
            if mc.getAttr(eachEl+'.endMb[0]') != "0":
                for i in range(mc.getAttr(eachEl+'.endMb', mi=True,s=True)):
                    endMb = mc.getAttr(eachEl+'.endMb[%s]'%i).replace(" ", "")
                    splitNlsTplEndMb = endMb[1:-1].split(",")
                    lsTplEndMb =[each[1:-1] for each in splitNlsTplEndMb]
                    dicTplEndMb["%s"%(i+1)]= lsTplEndMb
                ############################################  FK  ##########################################################
                # CREATE GROUP END MEMBER_______________________________
                #print dic[eachEl]['dicMidMember'][-1]
                nHookEndMb = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.nameKnot,nSide=side, incP=incPart)
                hookEndMb = libRig.createObj(partial(mc.group, **{'n':nHookEndMb, 'em': True}),match=[dic[eachEl]['dicMidMember'][-1]],
                                            father=dic[eachEl]['dicMidMember'][-1],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                # ADD ATTRIBUTE SCALE PHALANGES_______________________________
                mc.addAttr(hookEndMb, ln="scalePhalanges" , nn="ScalePhalanges", at="double",min=1, max=9999, dv=360)
                mc.setAttr(hookEndMb + ".scalePhalanges" , e=True, k=True)
                # CREATE FK______________________________________________
                # ADJUST ROTATE ORDER____________________________________
                rotOrdFk = libRgPreset.configAxis(mb="rOrdToe")["rOrdFk"]
                dicEndMbCtr ={}
                dicEndMbRoot ={}
                dicEndMbSk ={}
                knot = 'T'
                if self.nameKnot == 'fingers': knot = 'F'
                for key,values in sorted(dicTplEndMb.items()):
                    lsEndMbCtr =[]
                    lsEndMbRoot =[]
                    lsEndMbSk = []
                    lsaddDblLRot = []
                    part = 'part'
                    if key =='1':
                        part = 'thumb'
                    elif key =='2':
                        part = 'point'
                    elif key =='3':
                        part = 'middle'
                    elif key =='4':
                        part = 'ring'
                    elif key =='5':
                        part = 'pinky'
                    else:
                        pass
                    for i, each in enumerate(values):
                        nEndCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=part+"%s"%(knot),nFunc="%s"%(i+1),nSide=side,incP=incPart)
                        endCtr = libRig.createController(name=nEndCtr,shape=libRig.Shp([self.typeCircle],color=valColorCtrIK,size=(0.2,0.2,0.2)),
                                                    match=[each], father=None,attributs={"rotateOrder":rotOrdFk,"drawStyle": 2})
                        if side == 'R':
                            mc.rotate(0,180,180,endCtr['root'],os=True)
                            selShape = mc.listRelatives(endCtr['c'], s=True)[0]
                            recCv = mc.ls(selShape + '.cv[*]', fl=True)
                            mc.rotate(180,0,0, recCv)
                        # SNAP SHAPE TPL FK______________________________________
                        shp = mc.listRelatives(endCtr['c'], s=True)[0]
                        recCv = mc.ls(shp + '.cv[*]', fl=True)
                        sclW = mc.getAttr('tpl_WORLD' +'.scale')[0]
                        mc.scale(1*sclW[0],1*sclW[0],1*sclW[0],recCv)
                        if self.name == 'leg':
                            mc.rotate(90,0,0, recCv)
                        lib_shapes.snapShpCv(shpRef=each, shpTarget=endCtr['c'])
                        lsEndMbCtr.append(endCtr['c'])
                        lsEndMbRoot.append(endCtr['root'])
                        lsEndMbSk.append(endCtr['sk'])
                        lSkHook.append(endCtr['sk'])
                        # CREATE SK ADD TO ROT PHALANGES_________________________
                        nBufSkAdd = gloss.name_format(prefix=gloss.lexicon('buf'),name=part+"%s"%(knot),nFunc="addSk%s"%(i+1),nSide=side,incP=incPart)
                        nSkAdd = gloss.name_format(prefix=gloss.lexicon('sk'),name=part+"%s"%(knot),nFunc="add%s"%(i+1),nSide=side,incP=incPart)
                        bufSkAdd = libRig.createObj(partial(mc.group, **{'n': nBufSkAdd, 'em': True}),
                        match=[endCtr['c']],father=endCtr['c'],attributs={"rotateX": 0, "rotateY": 0, "rotateZ": 0})
                        libRig.createObj(partial(mc.joint, **{'n': nSkAdd}), match=[bufSkAdd], father=bufSkAdd,
                        attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"drawStyle": 2})

                        rotAxis = 'Z'
                        scaleAxis = 'X'
                        if self.name == 'leg':
                            rotAxis = 'X'
                            scaleAxis = 'Y'
                        # CONNECT ROTATE BUF SK ADD________________________________________________________
                        nAddDblLRot = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=part+"%s"%(knot),
                                                         nFunc="rot%s" % (i + 1), nSide=side,incP=incPart)
                        addDblLRot = mc.createNode("addDoubleLinear", n=nAddDblLRot)
                        mc.setAttr(addDblLRot + ".input2", 1)
                        mc.connectAttr(endCtr['c'] + '.rotate%s'%(rotAxis), "%s.input1" % (addDblLRot), force=True)
                        lsaddDblLRot.append(addDblLRot)

                        nMltDblLinSkAdd = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=part+"%s"%(knot),
                                                       nFunc="addSk%s"%(i+1), nSide=side, incP=incPart)
                        NodeMltDblLinSkAdd = mc.createNode("multDoubleLinear", n=nMltDblLinSkAdd)
                        mc.setAttr(NodeMltDblLinSkAdd + ".input2", -1)
                        mc.connectAttr(addDblLRot + '.output', "%s.input1" % (NodeMltDblLinSkAdd), force=True)
                        nMltDivSkAdd = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=part+"%s"%(knot),
                                                         nFunc="addSk%s" % (i + 1), nSide=side,incP=incPart)
                        mltDivSkAdd = mc.createNode("multiplyDivide", n=nMltDivSkAdd)
                        mc.setAttr(mltDivSkAdd + ".operation", 2)
                        mc.setAttr(mltDivSkAdd + ".input2X", 2)
                        mc.connectAttr(NodeMltDblLinSkAdd + ".output", "%s.input1X" % (mltDivSkAdd), force=True)
                        mc.connectAttr(mltDivSkAdd + ".outputX", "%s.rotate%s" % (bufSkAdd,rotAxis), force=True)
                        # CONNECT SCALE BUF SK ADD________________________________________________________
                        nMltDblLinScl = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=part+"%s"%(knot),
                                                       nFunc="scl%s"%(i+1), nSide=side, incP=incPart)
                        NodeMltDblLinScl = mc.createNode("multDoubleLinear", n=nMltDblLinScl)
                        mc.setAttr(NodeMltDblLinScl + ".input2", -1)
                        if self.name == 'leg':
                            mc.setAttr(NodeMltDblLinScl + ".input2", 1)
                        mc.connectAttr(addDblLRot + '.output', "%s.input1" % (NodeMltDblLinScl), force=True)
                        nMltDivScl= gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=part+"%s"%(knot),
                                                         nFunc="scl%s" % (i + 1), nSide=side,incP=incPart)
                        mltDivScl = mc.createNode("multiplyDivide", n=nMltDivScl)
                        mc.setAttr(mltDivScl + ".operation", 2)
                        mc.connectAttr(NodeMltDblLinScl + ".output", "%s.input1X" % (mltDivScl), force=True)
                        mc.connectAttr(hookEndMb + ".scalePhalanges", "%s.input2X" % (mltDivScl), force=True)
                        nAddDblLScl = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=part+"%s"%(knot),
                                                         nFunc="scl%s" % (i + 1), nSide=side,incP=incPart)
                        addDblLScl = mc.createNode("addDoubleLinear", n=nAddDblLScl)
                        mc.setAttr(addDblLScl + ".input2", 1)
                        mc.connectAttr(mltDivScl + ".outputX", "%s.input1" % (addDblLScl), force=True)

                        nCondScl = gloss.name_format(prefix=gloss.lexicon('cnd'), name=part+"%s"%(knot),nFunc="scl%s" % (i + 1), nSide=side,incP=incPart)
                        cndScl = mc.createNode('condition', n=nCondScl)
                        mc.setAttr(cndScl + '.secondTerm', 0)
                        mc.setAttr(cndScl + '.operation', 5)
                        if self.name == 'leg':
                            mc.setAttr(cndScl + '.operation', 3)
                        mc.setAttr(cndScl + '.colorIfFalseR', 1)
                        mc.connectAttr(endCtr['c'] + '.rotate%s'%(rotAxis), cndScl + '.firstTerm')
                        mc.connectAttr(addDblLScl + '.output', cndScl + '.colorIfTrueR')
                        mc.connectAttr(cndScl + ".outColorR", "%s.scale%s" % (bufSkAdd,scaleAxis), force=True)


                    # ADD ATTRIBUTES ROTATION___________________________________
                    for i, each in enumerate(lsEndMbCtr):
                        mc.addAttr(dic[eachEl]['dicMidMbCtr'][-1], ln="%sRoll%s"%(part,i+1), nn="%sRoll%s"%(part,i+1), at="double", dv=0)
                        mc.setAttr(dic[eachEl]['dicMidMbCtr'][-1] + ".%sRoll%s"%(part,i+1), e=True, k=True)
                        # CONNECT ROTATE AXIS END MEMBER_________________________
                        valAxis = 'Z'
                        if self.name == 'leg':
                            valAxis = 'X'
                        mc.connectAttr(dic[eachEl]['dicMidMbCtr'][-1] + ".%sRoll%s"%(part,i+1), "%s.rotateAxis%s" % (each,valAxis), force=True)
                        mc.connectAttr(dic[eachEl]['dicMidMbCtr'][-1] + ".%sRoll%s"%(part,i+1), "%s.input2" % (lsaddDblLRot[i]), force=True)
                        # ADD NODE TO DRIVE SK ROT TO ATTRIBUTES ROTATION________
                        nDblLScl = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=part+"%s"%(knot),
                                                         nFunc="sk%s" % (i + 1), nSide=side,incP=incPart)
                        dblLScl = mc.createNode("addDoubleLinear", n=nDblLScl)

                        if self.name == 'arm':
                            mc.connectAttr(each + ".rotateZ", "%s.input1" % (dblLScl), force=True)
                            mc.connectAttr(dic[eachEl]['dicMidMbCtr'][-1] + ".%sRoll%s"%(part,i+1), "%s.input2" % (dblLScl), force=True)
                            mc.connectAttr(each + ".rotateX", lsEndMbSk[i] + ".rotateX", force=True)
                            mc.connectAttr(each + ".rotateY", lsEndMbSk[i] + ".rotateY", force=True)
                            mc.connectAttr(dblLScl + ".output", lsEndMbSk[i] + ".rotateZ", force=True)
                        elif self.name == 'leg':
                            mc.connectAttr(each + ".rotateX", "%s.input1" % (dblLScl), force=True)
                            mc.connectAttr(dic[eachEl]['dicMidMbCtr'][-1] + ".%sRoll%s"%(part,i+1), "%s.input2" % (dblLScl), force=True)
                            mc.connectAttr(dblLScl + ".output", lsEndMbSk[i] + ".rotateX", force=True)
                            mc.connectAttr(each + ".rotateY", lsEndMbSk[i] + ".rotateY", force=True)
                            mc.connectAttr(each + ".rotateZ", lsEndMbSk[i] + ".rotateZ", force=True)



                    '''
                    for i, each in enumerate(lsEndMbCtr):
                        mc.addAttr(lsEndMbCtr[0], ln="%sRoll%s"%(part,i+1), nn="%sRoll%s"%(part,i+1), at="double", dv=0)
                        mc.setAttr(lsEndMbCtr[0] + ".%sRoll%s"%(part,i+1), e=True, k=True)
                        # CONNECT ROTATE AXIS END MEMBER_________________________
                        valAxis = 'Z'
                        if self.name == 'leg':
                            valAxis = 'X'
                        mc.connectAttr(lsEndMbCtr[0] + ".%sRoll%s"%(part,i+1), "%s.rotateAxis%s" % (each,valAxis), force=True)
                        mc.connectAttr(lsEndMbCtr[0] + ".%sRoll%s"%(part,i+1), "%s.input2" % (lsaddDblLRot[i]), force=True)
                        # ADD NODE TO DRIVE SK ROT TO ATTRIBUTES ROTATION________
                        nDblLScl = gloss.name_format(prefix=gloss.lexicon('dblLin'), name=part+"%s"%(knot),
                                                         nFunc="sk%s" % (i + 1), nSide=side,incP=incPart)
                        dblLScl = mc.createNode("addDoubleLinear", n=nDblLScl)

                        if self.name == 'arm':
                            mc.connectAttr(each + ".rotateZ", "%s.input1" % (dblLScl), force=True)
                            mc.connectAttr(lsEndMbCtr[0] + ".%sRoll%s"%(part,i+1), "%s.input2" % (dblLScl), force=True)
                            mc.connectAttr(each + ".rotateX", lsEndMbSk[i] + ".rotateX", force=True)
                            mc.connectAttr(each + ".rotateY", lsEndMbSk[i] + ".rotateY", force=True)
                            mc.connectAttr(dblLScl + ".output", lsEndMbSk[i] + ".rotateZ", force=True)
                        elif self.name == 'leg':
                            mc.connectAttr(each + ".rotateX", "%s.input1" % (dblLScl), force=True)
                            mc.connectAttr(lsEndMbCtr[0] + ".%sRoll%s"%(part,i+1), "%s.input2" % (dblLScl), force=True)
                            mc.connectAttr(dblLScl + ".output", lsEndMbSk[i] + ".rotateX", force=True)
                            mc.connectAttr(each + ".rotateY", lsEndMbSk[i] + ".rotateY", force=True)
                            mc.connectAttr(each + ".rotateZ", lsEndMbSk[i] + ".rotateZ", force=True)
                    '''

                    dicEndMbCtr['%s'%key] = lsEndMbCtr
                    dicEndMbRoot['%s'%key] = lsEndMbRoot
                    dicEndMbSk['%s'%key] = lsEndMbSk
                # PARENT FK______________________________________________
                for key,values in sorted(dicEndMbCtr.items()):
                    for i, each in enumerate(values[:-1]):
                        mc.parent(dicEndMbRoot[key][i+1], each)
                for key,values in sorted(dicEndMbRoot.items()):
                    if key =='1' and self.nameEnd == 'hand':
                        mc.parent(values[0],dic[eachEl]['dicMidMbCtr'][-2])
                        mc.setAttr(values[0] + ".segmentScaleCompensate",0)
                    else:
                        mc.parent(dicEndMbRoot[key][0],hookEndMb)

                # CREATE JOINTS SK TO HAND_________________________________
                # Get FIRST TOE/FINGER CTR_________________________________
                lsGrpSkHand = []
                lsSkHand = []
                lsTrfHand = []
                lsEndMbCtrFirst = []

                nMeta = gloss.lexicon('metatarse')
                if self.nameEnd == 'hand': nMeta = gloss.lexicon('metacarpe')
                for key,values in sorted(dicEndMbCtr.items()):
                    nGrpSkHand = gloss.name_format(prefix=gloss.lexicon('root'),name=nMeta,nFunc="sk%s"%(key),nSide=side,incP=incPart)
                    nAimHand = gloss.name_format(prefix=gloss.lexicon('aim'),name=nMeta,nFunc="sk%s"%(key),nSide=side,incP=incPart)
                    nUpVHand = gloss.name_format(prefix=gloss.lexicon('upV'),name=nMeta,nFunc="sk%s"%(key),nSide=side,incP=incPart)
                    nSkHand = gloss.name_format(prefix=gloss.lexicon('sk'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)
                    nTrfHand = gloss.name_format(prefix=gloss.lexicon('sk'),name=nMeta,nFunc="Trs%s"%(key),nSide=side,incP=incPart)
                    libRig.createObj(partial(mc.group, **{'n':nGrpSkHand, 'em': True}),match=[dic[eachEl]['dicMidMbCtr'][-2]],
                                                            father=dic[eachEl]['dicMidMbCtr'][-2],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                    libRig.createObj(partial(mc.group, **{'n':nAimHand, 'em': True}),match=[dic[eachEl]['dicMidMbCtr'][-2]],
                                                            father=nGrpSkHand,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                    libRig.createObj(partial(mc.group, **{'n':nUpVHand, 'em': True}),match=[values[0]],
                                                            father=nGrpSkHand,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                    lsGrpSkHand.append(nGrpSkHand)

                    if self.nameEnd == 'hand':
                        mc.move(0,0,-0.5*mc.getAttr("tpl_WORLD"+".scaleX"),nUpVHand, ls=True)
                        aim= (0.0,-1.0,0.0)
                        upV= (0.0,0.0,-1.0)
                        if side =='R': aim= (0.0,1.0,0.0)
                    else:
                        mc.move(-0.5*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,nUpVHand, ls=True)
                        aim= (0.0,0.0,1.0)
                        upV= (-1.0,0.0,0.0)
                        if side =='R': aim= (0.0,0.0,-1.0)

                    aimCnst = mc.aimConstraint(values[0], nAimHand, aim=aim, u=upV, wut='object', wuo=nUpVHand)[0]
                    # create sk
                    skHand = libRig.createObj(partial(mc.joint, **{'n':nSkHand}),match=[nAimHand],father=nAimHand,
                                     attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2,"radius":0.2})

                    #infHand = libRig.createObj(partial(mc.group, **{'n':nTrfHand, 'em': True}),match=[values[0]],father=nAimHand,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                    #pCnst = mc.pointConstraint(values[0], nTrfHand)[0]

                    ####################################################################################################################
                    #add metacerp twist
                    ctrlDriver = values[0]
                    rootDriver = mc.listRelatives(ctrlDriver, p=True)[0]
                    dicCnst = lib_constraints.getCnstGraph(aimCnst)
                    #attrWght = dicCnst[pCnst]['driverAttr'][ctrlDriver]

                    nMultMtx = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)
                    nDecompMtx = gloss.name_format(prefix=gloss.lexicon('mtxDcp'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)
                    nMltDL = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)
                    nQuatToEuler = gloss.name_format(prefix=gloss.lexicon('quatToEuler'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)
                    nBlend = gloss.name_format(prefix=gloss.lexicon('blendColors'),name=nMeta,nFunc="%s"%(key),nSide=side,incP=incPart)

                    mltMtx = mc.createNode('multMatrix', n=nMultMtx)
                    dcmpMat = mc.createNode('decomposeMatrix', n=nDecompMtx)
                    mltDLNAim = mc.createNode('multDoubleLinear', n=nMltDL+'NormAimSwitch')
                    mltDLNTwist = mc.createNode('multDoubleLinear', n=nMltDL+'NormTwist')
                    mltDLSwitch = mc.createNode('multDoubleLinear', n=nMltDL+'twistSwitch')
                    qTE = mc.createNode('quatToEuler', n=nQuatToEuler)
                    bld = mc.createNode('blendColors', n=nBlend)



                    mc.connectAttr(aimCnst+'.constraintRotate', bld+'.color1')
                    mc.connectAttr(mltDLNAim+'.output', bld+'.blender')


                    mc.addAttr(ctrlDriver, ln=gloss.lexiconAttr('metacarpAim'), at='float', hnv=True, hxv=True, min=0, max=10, dv=10, k=True)
                    mc.addAttr(ctrlDriver, ln=gloss.lexiconAttr('metacarpTwist'), at='float', hnv=True, hxv=True, min=0, max=10, dv=10, k=True)

                    mc.setAttr(mltDLNAim+'.input2', 0.1)
                    mc.setAttr(mltDLNTwist+'.input2', -0.1)
                    mc.setAttr(mltDLSwitch+'.input2', 1.0)

                    mc.connectAttr(ctrlDriver+'.metacarpAim', mltDLNAim+'.input1')


                    mc.connectAttr(ctrlDriver+'.metacarpTwist', mltDLNTwist+'.input1')

                    mc.connectAttr(rootDriver+'.worldMatrix[0]', mltMtx+'.matrixIn[0]')
                    mc.connectAttr(ctrlDriver+'.worldInverseMatrix[0]', mltMtx+'.matrixIn[1]')
                    mc.connectAttr(mltMtx+'.matrixSum', dcmpMat+'.inputMatrix')
                    mc.connectAttr(dcmpMat+'.outputQuatY', qTE+'.inputQuatY')
                    mc.connectAttr(dcmpMat+'.outputQuatW', qTE+'.inputQuatW')
                    mc.connectAttr(qTE+'.outputRotateY', mltDLSwitch+'.input1')
                    mc.connectAttr(mltDLNTwist+'.output', mltDLSwitch+'.input2')
                    mc.connectAttr(mltDLSwitch+'.output', skHand+'.rotateY')


                    bindRot = mc.getAttr(bld+'.color1')
                    mc.setAttr(bld+'.color2', *bindRot[0])
                    #w8 debug for activ/unactive aim metacarp
                    #mc.connectAttr(bld+'.outputR', aimMetacarp+'.rotateX', f=True)
                    #mc.connectAttr(bld+'.outputG', aimMetacarp+'.rotateY', f=True)
                    #mc.connectAttr(bld+'.outputB', aimMetacarp+'.rotateZ', f=True)





                    lsEndMbCtrFirst.append(values[0])
                    lsSkHand.append(nSkHand)
                    lSkHook.append(nSkHand)
                    #lsTrfHand.append(nTrfHand)
                # OFFSET END MEMBER CTR_________________________________________________
                number = len(lsGrpSkHand)
                for i, each in enumerate(lsGrpSkHand):
                    val = i*0.5
                    if self.name == 'leg':
                        mc.move(0,0,(round(((val)-(float(number/4)))/float(number-0.5),1))*mc.getAttr("tpl_WORLD"+".scaleX"),each,ls=True)
                        if side == 'R':
                            mc.move(0,0,-(round(((val)-(float(number/4)))/float(number-0.5),1))*mc.getAttr("tpl_WORLD"+".scaleX"),each,ls=True)
                    else:
                        if side == 'R':
                            mc.move((round(((val)-(float(number/4)))/float(number-0.5),1))*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,each,ls=True)
                        else:
                            mc.move(-(round(((val)-(float(number/4)))/float(number-0.5),1))*mc.getAttr("tpl_WORLD"+".scaleX"),0,0,each,ls=True)
                '''
                ## ADJUST SCALE SK_______________________________________________________
                for i, each in enumerate(lsEndMbCtrFirst):
                    nMltDivScl = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('scl')+'%s'%(i+1)+'Sk',nSide=side,incP=incPart)
                    mltDivScl = mc.createNode("multiplyDivide", n=nMltDivScl)
                    mc.setAttr(mltDivScl + ".operation", 2)
                    if self.name == 'leg':
                        getInitVal = mc.getAttr(lsTrfHand[i]+ '.translateZ')
                        mc.setAttr(mltDivScl + ".input2X",getInitVal)
                        mc.connectAttr("%s.translateZ" %(lsTrfHand[i]), "%s.input1X" %(mltDivScl),force=True)
                        mc.connectAttr("%s.outputX" %(mltDivScl), "%s.scaleZ" %(lsSkHand[i]),force=True)
                    else:
                        getInitVal = mc.getAttr(lsTrfHand[i]+ '.translateY')
                        mc.setAttr(mltDivScl + ".input2X",getInitVal)
                        mc.connectAttr("%s.translateY" %(lsTrfHand[i]), "%s.input1X" %(mltDivScl),force=True)
                        mc.connectAttr("%s.outputX" %(mltDivScl), "%s.scaleY" %(lsSkHand[i]),force=True)
                '''
                # SET SKIN_________________________________________
                mc.select(cl=True)
                nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
                if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)

                [mc.sets(each, edit=True, forceElement=nSetPart) for each in lsSkHand]
                for key,values in sorted(dicEndMbSk.items()):
                    for i, each in enumerate(values):
                        mc.sets(each, edit=True, forceElement=nSetPart)


                #print dicEndMbCtr
                # DICTIONARY TO CONTROL GRP________________________________________________
                cgFkMidMb = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=self.nameEnd,nSide=side,incP=incPart)
                if mc.objExists(eachEl + '.%s'%(cgFkMidMb)):
                    pass
                else:
                    mc.addAttr(eachEl, ln=cgFkMidMb,dt='string',multi=True) # add MidMb Fk
                lenMidMb = mc.getAttr(eachEl + '.%s'%(cgFkMidMb), mi=True,s=True)
                lsEndMbFk = []
                for key,values in sorted(dicEndMbCtr.items()):
                    #nKey = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=self.nameKnot,nFunc=str(key),nSide=side,incP=incPart)
                    #mc.addAttr(eachEl, ln=nKey,dt='string',multi=True) # add MidMb Fk
                    for j, each in enumerate(values):
                        lsEndMbFk.append(each)
                        #mc.setAttr(eachEl+'.%s[%s]'%(nKey,j),each,type='string')
                [mc.setAttr(eachEl+'.%s[%s]'%(cgFkMidMb,lenMidMb+i),each,type='string') for i, each in enumerate(lsEndMbFk)]
                if mc.attributeQuery(gloss.lexiconAttr('listHooks'), n=eachEl, ex=True):
                    lIds = mc.getAttr(eachEl+'.'+gloss.lexiconAttr('listHooks'), mi=True)
                    storedHooks = []
                    for id in lIds:
                        storedHooks.append(mc.getAttr(eachEl+'.'+gloss.lexiconAttr('listHooks')+'['+str(id)+']'))
                    for skHook in lSkHook:
                        if not skHook in storedHooks:
                            lastId = mc.getAttr(eachEl+'.'+gloss.lexiconAttr('listHooks'), mi=True)[-1]+1
                            mc.setAttr(eachEl+'.'+gloss.lexiconAttr('listHooks')+'['+str(lastId)+']', skHook, type='string')
            else:
                print 'no end member'






            # PATCH LEG ###############################
            numbPart= dic[eachEl]["numbPart"]
            # DEV SYSTEM IK HANDLE MULTI________________________________________________________________________________
            if int(numbPart) > 1:
                # PAIR___________________________________
                if int(numbPart) % 2 == 0:
                    # ADD CTR IN IK CONTROL____________________________
                    sclWorld = mc.getAttr("tpl_WORLD" + ".scaleX")
                    nWrist = gloss.lexicon('wrist')
                    mvUpV = (0, 0, 1 * mc.getAttr("tpl_WORLD" + ".scaleX"))
                    if self.name == 'leg':
                        nWrist = gloss.lexicon('ankle')
                        mvUpV = (1 * mc.getAttr("tpl_WORLD" + ".scaleX"), 0, 0)
                    nRigAnkleRot = gloss.name_format(prefix=gloss.lexicon('rig'), name=nWrist,
                                                     nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    nCnsAnkleRot = gloss.name_format(prefix=gloss.lexicon('cns'), name=nWrist,
                                                     nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    nAimAnkleRot = gloss.name_format(prefix=gloss.lexicon('aim'), name=nWrist,
                                                     nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    nUpVAnkleRot = gloss.name_format(prefix=gloss.lexicon('upV'), name=nWrist,
                                                     nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    nAnkleRot = gloss.name_format(prefix=gloss.lexicon('c'), name=nWrist, nFunc=gloss.lexicon('rot'),
                                                  nSide=side, incP=incPart)
                    nAnkleRotDistD = gloss.name_format(prefix=gloss.lexicon('rot'), name=nWrist, nFunc='dstD',
                                                       nSide=side, incP=incPart)

                    rigAnkleRot = libRig.createObj(partial(mc.group, **{'n': nRigAnkleRot, 'em': True}),
                                                   match=[dic[eachEl]["ik"]], father=dic[eachEl]["consSpine"])
                    cnsAnkleRot = libRig.createObj(partial(mc.group, **{'n': nCnsAnkleRot, 'em': True}),
                                                   match=[dic[eachEl]["ik"]], father=rigAnkleRot)
                    aimAnkleRot = libRig.createObj(partial(mc.group, **{'n': nAimAnkleRot, 'em': True}),
                                                   match=[dic[eachEl]["ik"]], father=cnsAnkleRot)
                    upVAnkleRot = libRig.createObj(partial(mc.group, **{'n': nUpVAnkleRot, 'em': True}),
                                                   match=[dic[eachEl]["ik"]], father=cnsAnkleRot)

                    mc.move(mvUpV[0], mvUpV[1], mvUpV[2], upVAnkleRot, ls=True)
                    mc.pointConstraint(dic[eachEl]["ik"], cnsAnkleRot)
                    aimRot = (0.0, 1.0, 0.0)
                    upVRot = (1.0, 0.0, 0.0)
                    mc.aimConstraint(dic[eachEl]["lsChainFk"][0], aimAnkleRot, aim=aimRot, u=upVRot, wut='object', wuo=upVAnkleRot)
                    ankleRot = libRig.createController(name=nAnkleRot,
                                                       shape=libRig.Shp([self.typeCircle], color=valColorCtrIK,
                                                                        size=(
                                                                            0.5 * sclWorld, 0.5 * sclWorld,
                                                                            0.5 * sclWorld),
                                                                        rotShp=(0, 0, 90)), match=[cnsAnkleRot],
                                                       father=aimAnkleRot, attributs={"drawStyle": 2})
                    ankleRotDistD = libRig.createObj(partial(mc.group, **{'n': nAnkleRotDistD, 'em': True}),
                                                     match=[dic[eachEl]["ik"]], father=ankleRot['c'])
                    mc.delete(mc.listRelatives(dic[eachEl]["lsPlVRoot"][-1], type="parentConstraint"))
                    mc.parent(dic[eachEl]["lsPlVRoot"][-1], ankleRotDistD)

                    # CREATE ATTRIBUTE QUADLOCK________________________
                    mc.addAttr(dic[eachEl]["ik"], ln="quadLock", nn="QuadLock", at="double", min=-10, max=10, dv=0)
                    mc.setAttr(dic[eachEl]["ik"] + ".quadLock", e=True, k=True)

                    # node to drive ankleRotDistD_____________
                    nAddDLinAnkleRot = gloss.name_format(prefix=gloss.lexicon('addDblLin'), name=nWrist,
                                                         nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    nodeAddDLinAnkleRot = mc.shadingNode("addDoubleLinear", n=nAddDLinAnkleRot, asUtility=True)
                    mc.setAttr("%s.input2" % (nodeAddDLinAnkleRot), -(mc.getAttr(dic[eachEl]["nNodeDstDim"] + '.distance')))
                    mc.connectAttr("%s.distance" % (dic[eachEl]["nNodeDstDim"]), "%s.input1" % (nodeAddDLinAnkleRot), force=True)
                    nMltDivAnkleRot2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nWrist,
                                                         nFunc=gloss.lexicon('rot') + 'Multi', nSide=side, incP=incPart)
                    mltDivAnkle2 = mc.createNode("multiplyDivide", n=nMltDivAnkleRot2)
                    mc.setAttr(mltDivAnkle2 + ".operation", 2)
                    mc.setAttr(mltDivAnkle2 + ".input2X", mc.getAttr(dic[eachEl]["nNodeDstDim"] + '.distance'))
                    mc.connectAttr("%s.output" % (nodeAddDLinAnkleRot), "%s.input1X" % (mltDivAnkle2), force=True)

                    nMltDivAnkleRot = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nWrist,
                                                        nFunc=gloss.lexicon('rot') + 'Div', nSide=side, incP=incPart)
                    mltDivAnkle = mc.createNode("multiplyDivide", n=nMltDivAnkleRot)
                    mc.setAttr(mltDivAnkle + ".operation", 2)
                    mc.setAttr(mltDivAnkle + ".input2X", 10)
                    mc.connectAttr("%s.quadLock" % (dic[eachEl]["ik"]), "%s.input1X" % (mltDivAnkle), force=True)
                    nMltDivAnkleRot3 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nWrist,
                                                         nFunc=gloss.lexicon('rot') + 'Div2', nSide=side, incP=incPart)
                    mltDivAnkle3 = mc.createNode("multiplyDivide", n=nMltDivAnkleRot3)
                    mc.setAttr(mltDivAnkle3 + ".operation", 1)
                    mc.setAttr(mltDivAnkle3 + ".input2X", 45)
                    mc.connectAttr("%s.outputX" % (mltDivAnkle), "%s.input1X" % (mltDivAnkle3), force=True)

                    nMltDivAnkleRot4 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=nWrist,
                                                         nFunc=gloss.lexicon('rot'), nSide=side, incP=incPart)
                    mltDivAnkle4 = mc.createNode("multiplyDivide", n=nMltDivAnkleRot4)
                    mc.setAttr(mltDivAnkle3 + ".operation", 1)
                    mc.connectAttr("%s.outputX" % (mltDivAnkle2), "%s.input1X" % (mltDivAnkle4), force=True)
                    mc.connectAttr("%s.outputX" % (mltDivAnkle3), "%s.input2X" % (mltDivAnkle4), force=True)
                    mc.connectAttr("%s.outputX" % (mltDivAnkle4), "%s.rotateX" % (ankleRotDistD), force=True)




                    # DELETE AND CREATE NEW IK HANDLE
                    lsFkImpair = [each for i, each in enumerate(dic[eachEl]["lsChainFk"]) if (i % 2) == 0]
                    mc.delete(dic[eachEl]["ikHandle"])
                    # create ik handle along chainFk
                    lsFkImpair = [each for i, each in enumerate(dic[eachEl]["lsChainFk"]) if (i % 2) == 0]
                    #for i, each in enumerate(lsFkImpair[:-1]):

                    nIkHdlQuad = gloss.name_format(prefix=gloss.lexicon('ikHdl'), name=self.name,
                                                      nFunc='quad' + str(i + 1), nSide=side, incP=incPart)
                    #nIkHdlQuad = dic[eachEl]["ikHandle"]
                    ikHdlQuad = mc.ikHandle(n=nIkHdlQuad, sj=lsFkImpair[0], ee=lsFkImpair[1], sol='ikRPsolver')
                    mc.setAttr(nIkHdlQuad+".snapEnable", 0)
                    mc.setAttr(nIkHdlQuad+".visibility", 0)
                    mc.parent(nIkHdlQuad, nAnkleRotDistD)
                    mc.poleVectorConstraint(dic[eachEl]["lsPlVCtr"][0], nIkHdlQuad)
                    mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHdlQuad[0] + '.ikBlend', f=True)
                    mc.connectAttr(dic[eachEl]["ik"] + '.twist', ikHdlQuad[0] + '.twist', f=True)
                    connect1 = mc.listConnections(ikHdlQuad[-1], plugs=False, connections=True, destination=False)[1]

                    # create ik handle on endChain
                    nIkHdlQuadEnd = dic[eachEl]["ikHandle"]
                    ikHandleQuadEnd = mc.ikHandle(n=nIkHdlQuadEnd, sj=lsFkImpair[-1], ee=dic[eachEl]["lsChainFk"][-1], sol='ikRPsolver')
                    mc.setAttr(ikHandleQuadEnd[0] + ".snapEnable", 0)
                    mc.setAttr(ikHandleQuadEnd[0] + ".visibility", 0)
                    mc.parent(ikHandleQuadEnd[0], dic[eachEl]["RootO"])
                    mc.poleVectorConstraint(dic[eachEl]["lsPlVCtr"][-1], ikHandleQuadEnd[0])
                    mc.pointConstraint(dic[eachEl]["dstDimMb"], ikHandleQuadEnd[0])
                    mc.pointConstraint(dic[eachEl]["dstDimMbEnd"], ikHandleQuadEnd[0])
                    mc.pointConstraint(dic[eachEl]["dstDimMbEnd"], ankleRot['root'])
                    connect2 = mc.listConnections(ikHandleQuadEnd[-1], plugs=False, connections=True, destination=False)[1]

                    # reconnect Expression
                    nExpStretch = gloss.name_format(prefix=gloss.lexicon('exp'), name=self.name, nFunc="stretch",nSide=side, incP=incPart)
                    expMb = dic[eachEl]["expMb"]
                    # unlock and disconnect translate y fk chain
                    [mc.setAttr(each + '.ty', lock=False) for each in dic[eachEl]["lsChainFk"][1:-1]]
                    [lib_attributes.disconnectAll(each + '.ty', source=True, destination=True) for each in dic[eachEl]["lsChainFk"][1:-1]]
                    mc.setAttr(dic[eachEl]["lsChainFk"][-1] + '.ty', lock=False)
                    lib_attributes.disconnectAll(dic[eachEl]["lsChainFk"][-1] + '.ty', source=True, destination=True)
                    #
                    mc.expression(nExpStretch, e=True, s="", o="", ae=1, uc="none")
                    mc.expression(nExpStretch, e=True, s="", o="", ae=1, uc="all")
                    mc.expression(nExpStretch, e=True, s=expMb)

                    mc.connectAttr(connect1+'.ty',ikHdlQuad[-1]+'.ty')
                    mc.connectAttr(connect2+'.ty',ikHandleQuadEnd[-1]+'.ty')
                    # adjust twist
                    nAddDLinQuad = gloss.name_format(prefix=gloss.lexicon('addDblLin'), name=self.name, nFunc='quadEnd',
                                                      nSide=side, incP=incPart)
                    nodeAddDLinQuad = mc.shadingNode("addDoubleLinear", n=nAddDLinQuad, asUtility=True)
                    mc.connectAttr(dic[eachEl]["ik"] + '.twist', "%s.input1" % (nodeAddDLinQuad), f=True)
                    if side == "R":
                        mc.setAttr("%s.input2" % (nodeAddDLinQuad), abs(mc.getAttr(lsFkImpair[-1] + ".rotateY")))
                    else:
                        mc.setAttr("%s.input2" % (nodeAddDLinQuad), -abs(mc.getAttr(lsFkImpair[-1] + ".rotateY")))
                    mc.connectAttr(nodeAddDLinQuad + '.output', ikHandleQuadEnd[0] + '.twist', f=True)
                    mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHandleQuadEnd[0] + '.ikBlend', force=True)
                    # check rotateY to lsFkImpair[-1] is 0:
                    if side == "R":
                        if int(mc.getAttr(lsFkImpair[-1] + '.rotateY')) == 0:
                            pass
                        else:
                            mc.setAttr("%s.input2" % (nodeAddDLinQuad), -90)

                    # connect blendColor to fk controls
                    for i, each in enumerate(dic[eachEl]["blendColor"]):
                        mc.connectAttr(each + '.color2R', dic[eachEl]["lsChainFk"][1:][i] + '.ty',
                                       force=True)
                    # lock translate y fk chain
                    [mc.setAttr(each + '.ty', lock=True) for each in dic[eachEl]["lsChainFk"][1:-1]]


                else:
                    # IMPAIR_____________________________
                    print ('horse system')
            else:
                print("numbpart is 1, don't create add control")






###########################################################################################################################
"""
# Import de la librairie sys
import sys
import maya.cmds as mc
import maya.mel as mel
# Définition du chemin des scripts
pathCustom ='X:\SETUP\maya'

# Si le chemin n'est pas déjà configuré
if not pathCustom in sys.path:
    # On l'ajoute
    sys.path.append(pathCustom)
# Import du module et définition d'un nom d'appel
# Refresh du module

from ellipse_rig.assets.characters import rig_member
reload(rig_member)
memb = rig_member.Member() # instance class charGuide
memb.createMember()




from ellipse_rig.assets.characters import rig_spine
reload(rig_spine)
rig = rig_spine.Spine() # instance class charGuide
rig.createSpine()
"""