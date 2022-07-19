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
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        # CREATE RIG TO LIST INFO_________________________________
        dicMember = {}
        dicBuf = {}
        dicSk = {}
        lCtrl = []

        getShpAttr = []
        for i, eachTpl in enumerate(lsInfo):
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
            lsTplIk =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            lsTplClavIk =[mc.getAttr(eachTpl+'.ikStart[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ikStart', mi=True,s=True))]
            lsTplClavCtr =[mc.getAttr(eachTpl+'.ctrStart[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctrStart', mi=True,s=True))]
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
            mc.addAttr(shapeAttrib, ln="smooth", nn="Smooth", at="double", min=0, max=10, dv=0)
            mc.setAttr(shapeAttrib + ".smooth", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="arc", nn="Arc", at="double", min=0, max=10, dv=0)
            mc.setAttr(shapeAttrib + ".arc", e=True, k=True)
            mc.addAttr(shapeAttrib, ln="autoHideIKFK", nn="Auto Hide IKFK", at="bool", dv=0)
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

            # Create SK TO CONTROL TWIST HAND/FOOT_________________________________
            nRigTwist = gloss.name_format(prefix=gloss.lexicon('rig'), name=nFkWrist,nFunc=gloss.lexicon('sk'),nSide=side, incP=incPart)
            nSkTwist = gloss.name_format(prefix=gloss.lexicon('sk'), name=nFkWrist,nSide=side, incP=incPart)
            skTwist =libRig.createObj(partial(mc.joint, **{'n': nRigTwist}), match=[nJntRig1], father=nJntRig1,
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})

            libRig.createObj(partial(mc.joint, **{'n': nSkTwist}), match=[nJntRig1], father=nRigTwist,
                             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})

            nMltDblLinTwist= gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='twist',nSide=side,incP=incPart)
            NodeMltDblLinTwist = mc.createNode("multDoubleLinear", n=nMltDblLinTwist)
            mc.setAttr(NodeMltDblLinTwist + ".input2", -1)
            mc.connectAttr(nJntRig1+".rotateY", "%s.input1" % (NodeMltDblLinTwist), force=True)
            nMltDivTwist = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='twist',nSide=side,incP=incPart)
            mltDivTwist = mc.createNode("multiplyDivide", n=nMltDivTwist)
            mc.setAttr(mltDivTwist+ ".operation", 2)
            mc.setAttr(mltDivTwist + ".input2X",2)
            mc.connectAttr(NodeMltDblLinTwist+'.output', "%s.input1X" % (mltDivTwist), force=True)
            mc.connectAttr(mltDivTwist+'.outputX', "%s.rotateY" % (nRigTwist), force=True)

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
            mc.parent(RootO, w=True)
            mc.parent(nLsFk[0],RootO)
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
            # CONNECT LOC_FLY WITH HOOK IK_____________________________________
            '''
            mc.parent(ikBuf, w=True)
            dMatrixCog = mc.shadingNode("decomposeMatrix", n="dMtxLocFly_%s_%s"%(self.name,incPart), asUtility=True)
            mc.connectAttr((self.nLocFly + ".worldMatrix[0]"), (dMatrixCog+ ".inputMatrix"))
            mc.connectAttr((dMatrixCog + ".outputRotate"), (hookIk + ".rotate"))
            mc.connectAttr((dMatrixCog + ".outputScale"), (hookIk + ".scale"))
            mc.connectAttr((dMatrixCog + ".outputShear"), (hookIk + ".shear"))
            mc.connectAttr((dMatrixCog + ".outputTranslate"), (hookIk + ".translate"))
            mc.select(cl=True)
            mc.parent(ikBuf,hookIk)
            '''
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
            mc.addAttr(ikCtr['c'], ln="rollFull" , nn="RollFull", at="enum", en="Off:On:")
            mc.setAttr(ikCtr['c'] + ".rollFull" , e=True, k=True)
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

            ## Ajouter shapeAttribut avec Ctrs IK ###
            mc.parent(shapeAttrib, ikCtr['c'], s=True, add=True)

            # IK HANDLE POLE VECTOR_____________________________________________________________________________________
            # name_____________________________________________
            nPlV = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nTampDistDim = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nJntPlV1 = gloss.name_format(prefix=gloss.lexicon('jt'),name=self.name,nFunc=gloss.lexicon('plV')+"1", nSide=side,incP=incPart)
            nJntPlV2 = gloss.name_format(prefix=gloss.lexicon('jt'),name=self.name,nFunc=gloss.lexicon('plV')+"2", nSide=side,incP=incPart)
            nIkHdlPlV = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nTampPlVRoot = gloss.name_format(prefix=gloss.lexicon('plV'),name=self.name,nFunc=gloss.lexicon('plV'), nSide=side,incP=incPart)
            nUpVRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('upV'), nSide=side,incP=incPart)
            nTampPlV = gloss.name_format(prefix=gloss.lexicon('upV'),name=self.name,nFunc=gloss.lexicon('upV'), nSide=side,incP=incPart)
            nIkHdlMb = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nSide=side,incP=incPart)
            nExpTwistFollow = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="twistFollow", nSide=side,incP=incPart)
            nExpIkBlend = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="iKBlend", nSide=side,incP=incPart)
            nExpStretch = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc="stretch", nSide=side,incP=incPart)

            # create pole vector_________________________________
            plV = libRig.createController(name=nPlV,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)),
                                            match=[mc.getAttr(eachTpl+'.masterPlV[0]')], father=RootO,attributs={"drawStyle":2})
            # SNAP SHAPE TPL PLV__________________________________
            lib_shapes.snapShpCv(shpRef=mc.getAttr(eachTpl+'.masterPlV[0]'), shpTarget=plV['c'])
            # creer un group tamp pour connecter la distance dim et le syst de poleVector ###
            dstDimMb = libRig.createObj(partial(mc.group, **{'n':nTampDistDim , 'em': True}),match=[lsTplIk[0]],father=consSpine,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
            #mc.addAttr( dstDimMb, ln=naming.autoClavReparent, at='bool', dv=True)
            mc.pointConstraint(fk[0],dstDimMb)
            # create chain joints to poleVector ###
            chainPlV = libRig.chainJoint(lstChain=[lsTplIk[0],lsTplIk[-1]],lstNameChain=[nJntPlV1,nJntPlV2], lsRotOrder=None,aim=aimFk, upV=upVFk,convertChain=True,shape=None)
            mc.parent(chainPlV[0],dstDimMb)
            [mc.setAttr(each+'.drawStyle',2) for each in chainPlV]
            # create ik handle to poleVector ###
            ikHdlPlV = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlPlV ,'sj':chainPlV[0],'ee':chainPlV[1],'sol':self.IkType}),
                       match=[lsTplIk[-1]],father=dstDimMbEnd,attributs={"snapEnable": 0,"poleVectorX":0,"poleVectorY":0,"poleVectorZ":0,"visibility":0})
            # root tampPoleVector ###
            rootTampPoleV = libRig.createObj(partial(mc.spaceLocator, **{'n':nTampPlVRoot}),match=[chainPlV[0]],father=chainPlV[1],attributs={"visibility":0})
            mc.pointConstraint(ikCtr['c'], rootTampPoleV)
            mc.pointConstraint(dstDimMb, rootTampPoleV)
            # creer SystemConnect poleVector ###
            rootUpV = libRig.createObj(partial(mc.spaceLocator, **{'n':nUpVRoot}),match=[rootTampPoleV],father=rootTampPoleV,attributs={"visibility":0})
            TampPoleV = libRig.createObj(partial(mc.spaceLocator, **{'n': nTampPlV}),match=[mc.getAttr(eachTpl+'.masterPlV[0]')],father=rootUpV)
            # connection rootPoleVector with tampPoleVector ###
            mc.parentConstraint(TampPoleV,plV['root'])

            # CREATE IK HANDLE__________________________________________________________________________________________
            recuppointConsWeight =[]
            if(self.IkType != 'ikSplineSolver'):
                ikHandle = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlMb ,'sj':fk[0],'ee':lsChainFk[len(concatIkFk)-lenLsTplMidMb],'sol':self.IkType}),match=[lsTplIk[-1]],father=RootO,attributs={"snapEnable": 0,"visibility":0})
                pointCnsdstDimMb = mc.pointConstraint(dstDimMb,ikHandle,w=0)
                firstAimCons = mc.listConnections(mc.listRelatives(ikHandle, type="constraint")[0]+ ".target", p=True)[-1]
                recuppointConsWeight.append(firstAimCons)
                pointCnscreateTpDistDim = mc.pointConstraint(dstDimMbEnd,ikHandle,w=1)
                secondAimCons = mc.listConnections(mc.listRelatives(ikHandle, type="constraint")[0]+ ".target", p=True)[-1]
                recuppointConsWeight.append(secondAimCons)
                mc.poleVectorConstraint(plV['c'], ikHandle)
                #recupIntIkHandle.append(ikHandle)
            else:
                pass
            # CREATE CRV SHAPE BETWEEN ELBOW POLE VECTOR________________________________________________________________
            lsToCrv =[fk[int(numbPart)],plV['sk']]
            positions = [mc.xform(each, q=True, ws=True, translation=True) for each in lsToCrv]
            nCrvPoleV = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('plV'),nSide=side,incP=incPart)
            createCrvTmp = mc.curve(n=nCrvPoleV, p=positions, d=1)
            mc.skinCluster(lsToCrv, createCrvTmp, tsb=1, mi=1)
            mc.setAttr(createCrvTmp +".template",1)
            mc.setAttr(createCrvTmp +".inheritsTransform",0)

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
            mc.connectAttr(mltDivFollowH2 + '.outputX', "%s.rotateY" %(rootUpV), force=True)

            # CONNECTION TWIST_____________________________________________________________________________________
            nMltDivTwist1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='twist'+'FollowDiv',nSide=side,incP=incPart)
            nMltDivTwist2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc='twist'+'FollowMlt',nSide=side,incP=incPart)
            mltDivTwist1 = mc.createNode("multiplyDivide", n=nMltDivTwist1)
            mc.setAttr(mltDivTwist1+ ".operation", 2)
            mc.setAttr(mltDivTwist1 + ".input2X",10)
            mc.connectAttr(ikCtr['c']+".twist", "%s.input1X" % (mltDivTwist1), force=True)
            if side == "R" :
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='twist'+'FollowNeg',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(ikCtr['c']+".twist", "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivTwist1), force=True)
            mltDivTwist2 = mc.createNode("multiplyDivide", n=nMltDivTwist2)
            mc.setAttr(mltDivTwist2 + ".operation", 1)
            mc.setAttr(mltDivTwist2 + ".input2X",90)
            mc.connectAttr(mltDivTwist1 + '.outputX', "%s.input1X" % (mltDivTwist2), force=True)
            mc.connectAttr(mltDivTwist2 + '.outputX',"%s.twist" %(ikHandle), force=True)

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
            mc.parent(createCrvTmp,GrpNoTouch)
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
            for z, each in enumerate(lsChainFk[1:len(concatIkFk)-(lenLsTplMidMb-1)]):
                if side == "L":
                    varScale = "float $cscale%s = %s;\n" %(z+1,fk[z]+(".scale%s"%(getAxis)))
                    concatScale += varScale
                    varScale2 = "%s" %(fk[z]+(".scale%s"%(getAxis)))
                    varLength ="%s" %(float(mc.getAttr(each+ ".translate%s"%(getAxis))))
                    concatChain += " + %s" %(varLength) +"*$cscale%s" %(z+1)
                elif side == "R":
                    varScale = "float $cscale%s = %s;\n" %(z+1,fk[z]+(".scale%s"%(getAxis)))
                    concatScale += varScale
                    varScale2 = "%s" %(fk[z]+(".scale%s"%(getAxis)))
                    varLength ="%s" %(abs(float(mc.getAttr(each+ ".translate%s"%(getAxis)))))
                    concatChain += " + %s" %(varLength) +"*$cscale%s" %(z+1)

                squatch ="\n$sAim=$f*$cscale%s;\n$sUp=1;\n" %(z+1)
                squash2 = squatch + "if($csquash>0) $sUp=1-$csquash+$csquash*pow($sAim,%s.output);\n" %(nodeAddDLinSquash)

                ValT =float(mc.getAttr(each+ ".translate%s"%(getAxis)))
                part = "%s.translate%s ="%(each,getAxis) + str(ValT)+"*$f%s" %(valRetract)+ " ;\n"
                getSquash += squash2 + part +"%s.stretch=$sAim;\n%s.squash=$sUp;\n" %(fk[z],fk[z])

            concatChain += ")*%s.outputScaleY%s"%(dcpMat,valRetract)
            concatExprPart1 = "%s\n%s\n%s\n%s\n%s%s\n%s;\n%s\n%s\n%s\n%s\n%s\n"%(varStringStretch,varStretch,varSoft,varSquash,concatScale,varDistance,concatChain,varF,varW,varCondition1,varSoftF,varSoftW)
            concatExprPart2 = concatExprPart1 + "%s\n%s\n%s\n%s\n"%(expSoft3,expStretch,expSquash,getSquash)
            mc.expression(s= concatExprPart2 ,n=nExpStretch)

            # LOCK AND HIDE FK CONTROL__________________________________________________________________________________
            lib_attributes.lockAndHideAxis(fk[1:len(concatIkFk)-(lenLsTplMidMb)],transVis=True)



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
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('SA'), name=self.name, nFunc=gloss.lexicon('loft')+'Cv',nSide=side,incP=incPart)
            nloftGrp = gloss.name_format(prefix=gloss.lexicon('GRP'), name=self.name, nFunc=gloss.lexicon('loft')+'Cv',nSide=side,incP=incPart)
            nLoftBase = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc=gloss.lexicon('base'),nSide=side,incP=incPart)
            nLoftBaseSk = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc=gloss.lexicon('base')+'Sk',nSide=side,incP=incPart)
            val = float(mc.getAttr("tpl_WORLD"+".scaleX"))
            # CREATE GRP SA ______________________________________________________
            sAGrp = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), Match=None,father=self.nSa)
            loftGrp = libRig.createObj(partial(mc.group, **{'n': nloftGrp, 'em': True}), Match=None,father=self.nSa)
            # create Jnt to skin Loft
            lsJntLoft =[]
            for each in lsChainFk:
                nJntLoft= gloss.renameSplit(selObj=each, namePart=['c','root'], newNamePart=['loftSk','loftSk'], reNme=False)
                libRig.createObj(partial(mc.joint, **{'n': nJntLoft}), match=[each], father=each,
                            attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsJntLoft.append(nJntLoft)
            # Adjust Parentage to create a good orientation curve
            [mc.parent(each,w=True) for each in lsJntLoft]
            [mc.parent(each,lsJntLoft[i]) for i, each in enumerate(lsJntLoft[1:])]
            getCrv = lib_curves.createDoubleCrv(objLst=lsJntLoft, axis='Z', offset=0.2 * val)
            [mc.parent(each,lsChainFk[i]) for i, each in enumerate(lsJntLoft)]
            # parent to Twist Sys______________________________________________
            mc.parent(lsJntLoft[-1],nJntRig1)

            # variante1 parent to Twist Sys______________________________________________
            '''
            mc.parent(lsJntLoft[0],nRootO)
            mc.setAttr(lsJntLoft[0]+'.rotateOrder',lsRotOrder[0])
            mc.orientConstraint(lsChainFk[0],lsJntLoft[0], skip="y" )
            lib_connectNodes.connectAxis(lsChainFk[0],lsJntLoft[0],pos=True,rot=False,scl=False)
            '''
            # variante2 parent to Twist Sys______________________________________________
            '''
            mc.setAttr(lsJntLoft[0]+'.rotateOrder',lsRotOrder[0])
            nDblLin = gloss.name_format(prefix=gloss.lexicon('dblLin'),name=self.name,nFunc=gloss.lexicon('twist'), nSide=side,incP=incPart)
            NodeMultDblLinear = mc.createNode("multDoubleLinear", n=nDblLin)
            mc.setAttr(NodeMultDblLinear + ".input2", -1)
            mc.connectAttr("%s.rotateY" % (lsChainFk[0]), "%s.input1" % (NodeMultDblLinear), force=True)
            mc.connectAttr("%s.output" % (NodeMultDblLinear), "%s.rotateY" % (lsJntLoft[0]), force=True)
            '''
            # variante3 parent to Twist Sys______________________________________________
            '''
            mc.parent(lsJntLoft[0],nRootO)
            mc.setAttr(lsJntLoft[0]+'.rotateOrder',lsRotOrder[0])
            '''
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
            mc.parent(lsJntLoft[0],aimTwistTop)
            mc.setAttr(lsJntLoft[0]+'.rotateOrder',lsRotOrder[0])
            nDblLin = gloss.name_format(prefix=gloss.lexicon('dblLin'),name=self.name,nFunc=gloss.lexicon('twist'), nSide=side,incP=incPart)
            NodeMultDblLinear = mc.createNode("multDoubleLinear", n=nDblLin)
            mc.setAttr(NodeMultDblLinear + ".input2", -1)
            mc.connectAttr("%s.rotateY" % (aimTwistTop), "%s.input1" % (NodeMultDblLinear), force=True)
            mc.connectAttr("%s.output" % (NodeMultDblLinear), "%s.rotateY" % (lsJntLoft[0]), force=True)

            lsCv = []
            for i, each in enumerate(getCrv['crv']):
                nCv = mc.rename(each,gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('base')+str(i+1),nSide=side,incP=incPart))
                mc.skinCluster(lsJntLoft, nCv, tsb=1, mi=1)
                mc.setAttr(nCv+".visibility",0)
                lsCv.append(nCv)

            degree =len(lsChainFk)
            loftBase = libRig.createObj(partial(mc.loft, lsCv[0], lsCv[1:],**{'n':nLoftBase, 'ch':True, 'u':True,'c':0,'ar':1,'d':3,'ss':0,'rn':0,'po':0,'rsn':True})
                                      , father=None, refObj=None, incPart=False, attributs={"visibility":0})
            sbDvLoft = (degree*(len(lsChainFk)))-1
            mc.rebuildSurface(nLoftBase,ch=True,rpo=True,rt=0,end=True, dir=2, su=sbDvLoft, sv=1, du=3,dv=3,tol=0.01)

            # Skin loft
            skinLoft = mc.skinCluster(lsArcSk, nLoftBase, tsb=1, bm=1, nw=1,mi=3, omi=True,dr=4, rui=True)
            # get bind pre matrix_______________________________
            for i, each in enumerate(lsArcBindP):
                mc.connectAttr(each+".worldInverseMatrix[0]", "%s.bindPreMatrix[%s]" % (skinLoft[0],i), force=True)

            # get point loft_______________________________
            recCv = mc.ls(nLoftBase + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv))/adjustNumb))
            val = 0
            dictPoint ={}
            for each2 in range(selDiv2):
                part= []
                for each in range(adjustNumb):
                    part.append(recCv[each+val])
                val += adjustNumb
                dictPoint[each2]= part
            print dictPoint
            # MODIFY SKIN VALUES_________________________________________________
            print lsChainFk[1:-1]
            count = len(lsChainFk[1:-1])+1
            if len(lsChainFk[1:-1]) == 1:
                count = 2
            count2 = 1
            count3 = dictPoint.keys()[-2] -(dictPoint.keys()[-2]/count)
            print dictPoint.keys()[-2]
            for valcount in range(count):
                for i, each in enumerate(sorted(dictPoint.items()[count2:-count3])):
                    val = round(abs(-i/float(dictPoint.keys()[-2]/count)), 4)
                    for j, point in enumerate(each[1]):
                        mc.skinPercent(skinLoft[0], point, r=False,transformValue=(lsArcSk[valcount], 1))
                        mc.skinPercent(skinLoft[0], point, r=False,transformValue=(lsArcSk[valcount+1], val))  # apply influence Jt 1
                count2 += dictPoint.keys()[-2]/count
                count3 -= dictPoint.keys()[-2]/count
            # adjust skin top loft
            valInfluencJt = mc.skinPercent(skinLoft[0], dictPoint.items()[2][1][0], transform=lsArcSk[1],query=True)  # return influence Jt 0
            [mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[0], 1)) for each in dictPoint.items()[0][1]]
            for each in dictPoint.items()[1][1]:
                mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[0], 1))
                mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[1], float(valInfluencJt/3)))

            # adjust skin Down loft
            valInfluencJt2 = mc.skinPercent(skinLoft[0], dictPoint.items()[-3][1][0], transform=lsArcSk[-2],query=True)  # return influence Jt 0
            [mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[-1], 1))for each in dictPoint.items()[-1][1]]
            for each in dictPoint.items()[-2][1]:
                    mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[-1], 1))
                    mc.skinPercent(skinLoft[0], each, r=False,transformValue=(lsArcSk[-2], valInfluencJt2/3))

            # CREATE INTERMEDIATE ARC CONTROLS_______________________________________
            # CREATE SA_______________________
            lSa = lib_connectNodes.surfAttach(selObj=[nLoftBase], lNumb=len(lsChainFk)-1,parentInSA=True, parentSA=nSAGrp,delKnot=True)
            valSlide = 0.5
            for i, each in enumerate(lSa['loc']):
                mc.setAttr(each + '.U',valSlide)
                valSlide += 1
            # CREATE CONTROLS_________________
            lsCtrArcBisRoot= []
            lsCtrArcBisCtr = []
            lsClusterArcBis = []
            for i, each in enumerate(lSa['loc']):
                nCtrArcBis = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name, nFunc=gloss.lexicon('arc')+str(i+1),nSide=side,incP=incPart)
                ctrArcBis = libRig.createController(name=nCtrArcBis,shape=libRig.Shp(['square'],color=valColorAdd ,size=(0.3*valScl,0.3*valScl,0.3*valScl)),
                match=[each], father=lSa['sa'][i],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder":lsRotOrder[0],"drawStyle": 2})
                mc.setAttr(ctrArcBis['root'] + '.rotateX',180)
                if side == "R" and self.name == 'leg':
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ',-90)
                elif side == "L" and self.name == 'arm':
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ',-90)
                else:
                    mc.setAttr(ctrArcBis['root'] + '.rotateZ',90)
                lsCtrArcBisRoot.append(ctrArcBis['root'])
                lsCtrArcBisCtr.append(ctrArcBis['c'])
                # CREATE CLUSTERS_________________
                nClusterArcBis = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name, nFunc=gloss.lexicon('arc')+str(i+1),nSide=side,incP=incPart)
                clusterArcBis = mc.createNode("cluster", n=nClusterArcBis)
                nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'),name=self.name, nFunc=gloss.lexicon('arc')+str(i+1),nSide=side,incP=incPart)
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

            # CREATE LOFT SK_________________
            degree =len(lsConcatArc)
            #degree =len(lsChainFk)
            loftBaseSk = libRig.createObj(partial(mc.loft, lsCv[0], lsCv[1:],**{'n':nLoftBaseSk, 'ch':True, 'u':True,'c':0,'ar':1,'d':3,'ss':0,'rn':0,'po':0,'rsn':True})
                                      , father=None, refObj=None, incPart=False, attributs={"visibility": 1})
            sbDvLoft = (degree*(len(lsConcatArc)))-1
            #sbDvLoft = (degree*(len(lsChainFk)))-1
            mc.rebuildSurface(nLoftBaseSk,ch=True,rpo=True,rt=0,end=True, dir=2, su=sbDvLoft, sv=1, du=3,dv=3,tol=0.01)
            # Skin loft
            skinLoftSk = mc.skinCluster(lsArcSk, nLoftBaseSk, tsb=1, bm=1, nw=1,mi=3, omi=True,dr=4, rui=True)
            # get bind pre matrix_______________________________
            for i, each in enumerate(lsArcBindP):
                mc.connectAttr(each+".worldInverseMatrix[0]", "%s.bindPreMatrix[%s]" % (skinLoftSk[0],i), force=True)

            # get point loftSk_______________________________
            recCv = mc.ls(nLoftBaseSk + '.cv[*]', fl=True)
            adjustNumb = 4
            selDiv2 = int(math.ceil(float(len(recCv))/adjustNumb))
            val = 0
            dictPointSk ={}
            for each2 in range(selDiv2):
                part= []
                for each in range(adjustNumb):
                    part.append(recCv[each+val])
                val += adjustNumb
                dictPointSk[each2]= part

            # MODIFY SKIN VALUES_________________________________________________
            count = len(lsChainFk[1:-1])+1
            if len(lsChainFk[1:-1]) == 1:
                count = 2
            count2 = 1
            count3 = dictPointSk.keys()[-2] -(dictPointSk.keys()[-2]/count)
            for valcount in range(count):
                for i, each in enumerate(sorted(dictPointSk.items()[count2:-count3])):
                    val = round(abs(-i/float(dictPointSk.keys()[-2]/count)), 4)
                    for j, point in enumerate(each[1]):
                        mc.skinPercent(skinLoftSk[0], point, r=False,transformValue=(lsArcSk[valcount], 1))
                        mc.skinPercent(skinLoftSk[0], point, r=False,transformValue=(lsArcSk[valcount+1], val))  # apply influence Jt 1
                count2 += dictPointSk.keys()[-2]/count
                count3 -= dictPointSk.keys()[-2]/count

            # adjust skin top loft
            valInfluencJt = mc.skinPercent(skinLoftSk[0], dictPointSk.items()[2][1][0], transform=lsArcSk[1],query=True)  # return influence Jt 0
            [mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[0], 1)) for each in dictPointSk.items()[0][1]]
            for each in dictPointSk.items()[1][1]:
                mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[0], 1))
                mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[1], float(valInfluencJt/3)))

            # adjust skin Down loft
            valInfluencJt2 = mc.skinPercent(skinLoftSk[0], dictPointSk.items()[-3][1][0], transform=lsArcSk[-2],query=True)  # return influence Jt 0
            [mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[-1], 1))for each in dictPointSk.items()[-1][1]]
            for each in dictPointSk.items()[-2][1]:
                    mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[-1], 1))
                    mc.skinPercent(skinLoftSk[0], each, r=False,transformValue=(lsArcSk[-2], valInfluencJt2/3))

            # ADD AND MODIFY CLUSTER VALUES_________________________________________________
            count = len(lsConcatArc[1:-1])+1
            if len(lsConcatArc[1:-1]) == 1:
                count = 2
            count2 = 1
            count3 = dictPointSk.keys()[-2] -(dictPointSk.keys()[-2]/count)
            dicPartPts = {}
            dicValPts = {}
            for valcount in range(count):
                lsPts =[]
                lsValPts =[]
                for i, each in enumerate(sorted(dictPointSk.items()[count2:-count3])):
                    lsPts.append(each[1])
                    val = round(abs(-i/float(dictPointSk.keys()[-2]/count)), 4)
                    lsValPts.append(val)
                dicPartPts[valcount] = lsPts
                dicValPts[valcount] = lsValPts
                count2 += dictPointSk.keys()[-2]/count
                count3 -= dictPointSk.keys()[-2]/count

            countPart = 0
            for i, each in enumerate(lsClusterArcBis):
                # part 1
                for j, part1 in enumerate(dicPartPts[0+i+countPart]):
                    for k, cvloft in enumerate(part1):
                        mc.deformer(each, e=True, g=cvloft)
                        mc.percent(each, cvloft, value=dicValPts[i][j])
                # part 2
                for j, part2 in enumerate(dicPartPts[1+i+countPart]):
                    for k, cvloft in enumerate(part2):
                        mc.deformer(each, e=True, g=cvloft)
                        mc.percent(each, cvloft, value=dicValPts[i][::-1][j])
                countPart += 1

            # adjust value cluster top loft
            valStart = mc.percent(lsClusterArcBis[0], dictPointSk.items()[2][1][0], value=True,q=True)
            [mc.percent(lsClusterArcBis[0], each, value=valStart[0]/3) for each in dictPointSk.items()[1][1]]
            # adjust value cluster Down loft
            [mc.percent(lsClusterArcBis[-1], each, value=valStart[0]/3) for each in dictPointSk.items()[-2][1]]

            # example [lib_curves.crvSubdivide(crv=each, name=None, subDiv=3,subDivKnot=None, degree=1) for each in getCrv2['crv']]
            # parent__________________________________________________________
            mc.parent(nLoftBase,loftGrp)
            mc.parent(nLoftBaseSk,loftGrp)
            [mc.parent(each,loftGrp)for each in lsCv]
            mc.parent(loftGrp,hookMb)
            mc.parent(nSAGrp,hookMb)
            # inherits Transform______________________________________________
            mc.setAttr(nLoftBase + '.inheritsTransform',0)
            mc.setAttr(nLoftBaseSk + '.inheritsTransform',0)
            [mc.setAttr(each + '.inheritsTransform',0) for each in lsCv]
            '''
            shp = mc.listRelatives(nLoftBase, s=True)[0]
            mc.parent(shp, loftGrp, r=True, s=True)
            shp = mc.listRelatives(nLoftBaseSk, s=True)[0]
            mc.parent(shp, loftGrp, r=True, s=True, add=True)
            for each in lsCv:
                shp = mc.listRelatives(each, s=True)[0]
                mc.parent(shp, loftGrp, r=True, s=True, add=True)
            #mc.parent(nLoftBase,loftGrp)
            #mc.parent(nLoftBaseSk,loftGrp)
            #[mc.parent(each,loftGrp)for each in lsCv]
            mc.parent(loftGrp,nHook)
            mc.parent(nSAGrp,nHook)
            # inherits Transform______________________________________________
            mc.setAttr(loftGrp + '.inheritsTransform',0)
            #mc.setAttr(nLoftBaseSk + '.inheritsTransform',0)
            #[mc.setAttr(each + '.inheritsTransform',0) for each in lsCv]
            #mc.delete(nLoftBase)
            #mc.delete(nLoftBaseSk)
            #[mc.delete(each)for each in lsCv]
            '''


            # SK ARM/LEG_________________________________________________
            # CREATE SA_______________________
            lSa = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=int(numbSk),parentInSA=True, parentSA=nSAGrp,delKnot=True)
            # CREATE CONTROLS_________________
            lsCtrSkRoot= []
            lsCtrSk= []
            lsSk= []
            for i, each in enumerate(lSa['loc']):
                nCtrhdldSk = gloss.name_format(prefix=gloss.lexicon('c'), name=self.name, nFunc=gloss.lexicon('shp')+str(i+1),nSide=side,incP=incPart)
                nOffHdldSk = gloss.name_format(prefix=gloss.lexicon('off'), name=self.name, nFunc=gloss.lexicon('shp')+str(i+1),nSide=side,incP=incPart)
                ctrhdldSk = libRig.createController(name=nCtrhdldSk,shape=libRig.Shp(['crossLine'],color=valColorAdd ,size=(0.2*valScl,0.2*valScl,0.2*valScl)),
                match=[each], father=lSa['sa'][i],attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0,"rotateOrder":lsRotOrder[0],"drawStyle": 2})
                mc.setAttr(ctrhdldSk['root'] + '.rotateX',180)
                if side == "R" and self.name == 'leg':
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ',-90)
                elif side == "L" and self.name == 'arm':
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ',-90)
                else:
                    mc.setAttr(ctrhdldSk['root'] + '.rotateZ',90)

                offhdldSk = libRig.createObj(partial(mc.group, **{'n':nOffHdldSk,'em': True}),match=[ctrhdldSk['root']],
                                             father=ctrhdldSk['root'],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                mc.parent(ctrhdldSk['c'],offhdldSk)
                mc.parent(ctrhdldSk['sk'],offhdldSk)

                lsCtrSkRoot.append(ctrhdldSk['root'])
                lsCtrSk.append(ctrhdldSk['c'])
                lsSk.append(ctrhdldSk['sk'])

            # SK KNOT IN ARM/LEG_________________________________________________

            nSkShoulder = gloss.lexicon('shoulder')
            if self.name == 'leg':
                nSkShoulder = gloss.lexicon('hip')
            lSaTwist = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=1,parentInSA=True, parentSA=nSAGrp,delKnot=True,nameRef='c_%s_%s_%s'%(nSkShoulder,side,incPart))
            mc.setAttr(lSaTwist['loc'][0] + ".U",0.01)
            nRootTwistUp = gloss.name_format(prefix=gloss.lexicon('root'),name=nSkShoulder,nSide=side,incP=incPart)
            nCtrTwistUp = gloss.name_format(prefix=gloss.lexicon('c'),name=nSkShoulder, nFunc=gloss.lexicon('shp'),nSide=side,incP=incPart)
            nSkTwistUp = gloss.name_format(prefix=gloss.lexicon('sk'),name=nSkShoulder,nSide=side,incP=incPart)
            nOffTwistUp = gloss.name_format(prefix=gloss.lexicon('off'),name=nSkShoulder,nSide=side,incP=incPart)

            rootTwistUp =libRig.createObj(partial(mc.joint, **{'n':nRootTwistUp}),match=[lSaTwist['loc'][0]],father=lSaTwist['sa'][0],
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            ctrTwistUp = libRig.createObj(partial(mc.joint, **{'n':nCtrTwistUp}), shape= libRig.Shp(['crossLine'],color=valColorAdd,
            size=(0.2*valScl,0.2*valScl,0.2*valScl)),match=[rootTwistUp], father=rootTwistUp, attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})

            skTwistUp =libRig.createObj(partial(mc.joint, **{'n':nSkTwistUp}),match=[rootTwistUp],father=rootTwistUp,
                                      attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
            lib_connectNodes.connectAxis(ctrTwistUp,skTwistUp,pos=True,rot=True,scl=True)

            mc.setAttr(rootTwistUp + '.rotateY',180)
            if side == "R" and self.name == 'leg':
                mc.setAttr(rootTwistUp + '.rotateZ',90)
            elif side == "L" and self.name == 'leg':
                mc.setAttr(rootTwistUp + '.rotateZ',-90)
            elif side == "L" and self.name == 'arm':
                mc.setAttr(rootTwistUp + '.rotateZ',-90)
            else:
                mc.setAttr(rootTwistUp + '.rotateZ',90)

            offTwistUp = libRig.createObj(partial(mc.group, **{'n':nOffTwistUp,'em': True}),match=[rootTwistUp],
                                         father=rootTwistUp,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})






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
            if self.name == "arm":
                aimFk = libRgPreset.configAxis(mb="aimJtArm%s"%side,side=side)["aimOri"]
                upVFk = libRgPreset.configAxis(mb="aimJtArm%s"%side,side=side)["aimUpV"]
            fkClav = libRig.chainJoint(lstChain=lsChainJnt,lstNameChain=nLsFkClav, lsRotOrder=lsRotOrder,aim=aimFk, upV=upVFk,
                                   convertChain=True,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)))
            # ADJUST ORIENTATION FK____________________________________________________
            [mc.setAttr(each+".jointOrientY",0) for i, each in enumerate(nLsFkClav[1:])]
            ## ADD SHP ATTR TO FK CLAV ###
            [mc.parent(shapeAttrib, each, s=True, add=True) for i, each in enumerate(nLsFkClav)]
            # SNAP SHAPE TPL FK________________________________________________________
            [lib_shapes.snapShpCv(shpRef=lsChainJnt[i], shpTarget=each) for i, each in enumerate(nLsFkClav)]

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
            mc.poleVectorConstraint(plVClav, ikHdlClav)
            mc.pointConstraint(ikCtr['c'],ikHdlClav)

            # connect ikHdlClav to twist/blend/autoOrient
            mc.connectAttr(mltDivTwist2 + '.outputX', "%s.twist" %(ikHdlClav), force=True)
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
            for each in fkClav:
                nRootFk = gloss.renameSplit(selObj=each, namePart=['c'], newNamePart=['root'], reNme=False)
                rootFk =libRig.createObj(partial(mc.group, **{'n':nRootFk, 'em': True}),match=[each],father=nAo)
                mc.parent(each,nRootFk)
                lsRootFk.append(nRootFk)
            [mc.parent(lsRootFk[i+1],each) for i, each in enumerate(fkClav[:-1])]


            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            # SK CLAV ______________
            for each in lsSkClav:
                mc.sets(each, edit=True, forceElement=nSetPart)
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
            # NAME CG_____________________________________________
            cgClav = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgClav'),nSide=side,incP=incPart)
            cgIk = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgIk'),nSide=side,incP=incPart)
            cgFkMb = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)
            cgFkMidMb = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=gloss.lexiconAttr('cgFkMidMb'),nSide=side,incP=incPart)
            cgFkArc = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=gloss.lexiconAttr('cgFkArc'),nSide=side,incP=incPart)
            cgFkShp = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=gloss.lexiconAttr('cgFkShp'),nSide=side,incP=incPart)

            if mc.objExists(eachTpl+'.%s'%(cgFkMb)):
                pass
            else:
                mc.addAttr(eachTpl, ln=cgClav,dt='string',multi=True) # add Clav Ctr
                mc.addAttr(eachTpl, ln=cgIk,dt='string',multi=True) # add ik Ctr
                mc.addAttr(eachTpl, ln=cgFkMb,dt='string',multi=True) # add Mb Fk
                mc.addAttr(eachTpl, ln=cgFkMidMb,dt='string',multi=True) # add MidMb Fk
                mc.addAttr(eachTpl, ln=cgFkArc,dt='string',multi=True) # add Arc Fk
                mc.addAttr(eachTpl, ln=cgFkShp,dt='string',multi=True) # add Shp Fk

            [mc.setAttr(eachTpl+'.%s['%(cgClav) +str(i)+']',each,type='string') for i, each in enumerate(lsFkClav)]
            [mc.setAttr(eachTpl+'.%s['%(cgIk) +str(i)+']',each,type='string') for i, each in enumerate(lsIkMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkMidMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkMidMb)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkArc)+str(i)+']',each,type='string') for i, each in enumerate(lsFkArc)]
            [mc.setAttr(eachTpl+'.%s['%(cgFkShp)+str(i)+']',each,type='string') for i, each in enumerate(lsFkShp)]

            # PARENT HOOK WITH RIG MEMBER________________________________________________
            #mc.parent(hookClv,self.hook)
            #mc.parent(hookMb,self.hook)
            #mc.parent(hookIk,self.hookIk)

            # ADD DICTIONARY RETURN________________________________________________
            dic["lsFk"] = fk
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
            dicMember["%s"%eachTpl] = dic

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
            nMltDivHeel1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('heel')+'Div',nSide=side,incP=incPart)
            nMltDivHeel2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('heel')+'Mlt',nSide=side,incP=incPart)
            nMltDivRoll1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Div',nSide=side,incP=incPart)
            nMltDivRoll2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Mlt',nSide=side,incP=incPart)
            nMltDivPiv1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('piv')+'Div',nSide=side,incP=incPart)
            nMltDivPiv2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('piv')+'Mlt',nSide=side,incP=incPart)

            mltDivHeel1 = mc.createNode("multiplyDivide", n=nMltDivHeel1)
            mc.setAttr(mltDivHeel1+ ".operation", 2)
            mc.setAttr(mltDivHeel1 + ".input2X",10)
            mc.connectAttr(dic[eachEl]['ik'] + '.%s Roll' % (self.nameKnot2), "%s.input1X" % (mltDivHeel1), force=True)
            mltDivHeel2 = mc.createNode("multiplyDivide", n=nMltDivHeel2)
            mc.setAttr(mltDivHeel2 + ".operation", 1)
            mc.setAttr(mltDivHeel2 + ".input2X",90)
            mc.connectAttr(mltDivHeel1 + '.outputX', "%s.input1X" % (mltDivHeel2), force=True)
            if side == "R" and self.name == 'leg':
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='knotPivot',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(dic[eachEl]['ik'] + '.%s Roll' % (self.nameKnot2), "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivHeel1), force=True)

            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivHeel2 + '.outputX', "%s.rotate%s" % (lsBankCtr[0],val), force=True)

            multDivRoll1 = mc.createNode("multiplyDivide", n=nMltDivRoll1)
            mc.setAttr(multDivRoll1 + ".operation", 2)
            mc.setAttr(multDivRoll1 + ".input2X",10)
            mc.connectAttr(dic[eachEl]['ik'] + '.knotRoll', "%s.input1X" % (multDivRoll1), force=True)
            multDivRoll2 = mc.createNode("multiplyDivide", n=nMltDivRoll2)
            mc.setAttr(multDivRoll2  + ".operation", 1)
            mc.setAttr(multDivRoll2  + ".input2X",90)
            mc.connectAttr(multDivRoll1 + '.outputX', "%s.input1X" % (multDivRoll2), force=True)
            val = 'X'
            if self.name == 'arm':
                val = 'Z'
                if side =='R':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='r',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.knotRoll', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (multDivRoll1), force=True)

            mc.connectAttr(multDivRoll2 + '.outputX', "%s.rotate%s" % (lsBankCtr[1],val), force=True)

            mltDivPiv1 = mc.createNode("multiplyDivide", n=nMltDivPiv1)
            mc.setAttr(mltDivPiv1 + ".operation", 2)
            mc.setAttr(mltDivPiv1 + ".input2X",10)
            mc.connectAttr(dic[eachEl]['ik'] + '.knot Pivot', "%s.input1X" % (mltDivPiv1), force=True)
            if side == "R" and self.name == 'leg':
                nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='knotPivot',nSide=side,incP=incPart)
                NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                mc.setAttr(NodeMltDblLinear + ".input2", -1)
                mc.connectAttr(dic[eachEl]['ik'] + '.knot Pivot', "%s.input1" % (NodeMltDblLinear), force=True)
                mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivPiv1), force=True)

            mltDivPiv2 = mc.createNode("multiplyDivide", n=nMltDivPiv2)
            mc.setAttr(mltDivPiv2  + ".operation", 1)
            mc.setAttr(mltDivPiv2  + ".input2X",90)
            mc.connectAttr(mltDivPiv1 + '.outputX', "%s.input1X" % (mltDivPiv2), force=True)
            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivPiv2 + '.outputX', "%s.rotate%s" % (lsBankCtr[1],val), force=True)

            # connect Attributes bank ________________________________
            nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('bank'),nSide=side,incP=incPart)
            nMltDivBank1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('bank')+'Div',nSide=side,incP=incPart)
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
            mltDivBank1 = mc.createNode("multiplyDivide", n=nMltDivBank1)
            mc.setAttr(mltDivBank1 + ".operation", 2)
            mc.setAttr(mltDivBank1 + ".input2X",10)
            mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivBank1), force=True)
            mltDivBank2 = mc.createNode("multiplyDivide", n=nMltDivBank2)
            mc.setAttr(mltDivBank2 + ".operation", 1)
            mc.setAttr(mltDivBank2 + ".input2X",90)
            mc.connectAttr("%s.outputX" % (mltDivBank1), "%s.input1X" % (mltDivBank2), force=True)
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
            nMultMat1 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Div',nSide=side,incP=incPart)
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Mlt',nSide=side,incP=incPart)
            nCondition = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll'),nSide=side,incP=incPart)
            nCondition2 = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Full',nSide=side,incP=incPart)
            NodeMultDiv1 = mc.createNode("multiplyDivide", n=nMultMat1)
            mc.setAttr(NodeMultDiv1 + ".operation",2)
            mc.setAttr(NodeMultDiv1 + ".input2X",10)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.input1X" % (NodeMultDiv1), force=True)
            NodeMultDiv2 = mc.createNode("multiplyDivide", n=nMultMat2)
            mc.setAttr(NodeMultDiv2 + ".operation", 1)
            mc.setAttr(NodeMultDiv2 + ".input2X",90)
            mc.connectAttr(NodeMultDiv1 + '.outputX', "%s.input1X" % (NodeMultDiv2), force=True)
            NodeCondition2 = mc.createNode("condition", n=nCondition2)
            mc.setAttr(NodeCondition2 + ".operation", 0)
            mc.setAttr(NodeCondition2 + ".colorIfFalseR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.rollFull', "%s.firstTerm" % (NodeCondition2), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition2), force=True)
            NodeCondition = mc.createNode("condition", n=nCondition)
            mc.setAttr(NodeCondition + ".operation", 5)
            mc.setAttr(NodeCondition + ".colorIfFalseR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(NodeCondition2 + '.outColorR', "%s.colorIfTrueR" % (NodeCondition), force=True)

            val = 'X'
            if self.name == 'arm':
                val = 'Z'
                if side =='L':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameKnot,nFunc='l',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.roll', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (NodeMultDiv1), force=True)
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
            nMltDivBallPiv1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('ballPiv')+'Div',nSide=side,incP=incPart)
            nMltDivBallPiv2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.nameEnd,nFunc=gloss.lexicon('ballPiv')+'Mlt',nSide=side,incP=incPart)
            mltDivBallPiv1 = mc.createNode("multiplyDivide", n=nMltDivBallPiv1)
            mc.setAttr(mltDivBallPiv1+ ".operation", 2)
            mc.setAttr(mltDivBallPiv1 + ".input2X",10)
            mc.connectAttr(dic[eachEl]['ik'] + '.ballPivot', "%s.input1X" % (mltDivBallPiv1), force=True)
            mltDivBallPiv2 = mc.createNode("multiplyDivide", n=nMltDivBallPiv2)
            mc.setAttr(mltDivBallPiv2 + ".operation", 1)
            mc.setAttr(mltDivBallPiv2 + ".input2X",90)
            mc.connectAttr(mltDivBallPiv1 + '.outputX', "%s.input1X" % (mltDivBallPiv2), force=True)
            if self.name == 'leg' and side =='R':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc=gloss.lexicon('ballPiv')+'Inv',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.ballPivot', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (mltDivBallPiv1), force=True)

            val = 'Y'
            if self.name == 'arm': val = 'X'
            mc.connectAttr(mltDivBallPiv2 + '.outputX', "%s.rotate%s" % (lsRollCtr[-1],val), force=True)
            # connect roll ________________________________
            nMultMat1 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys'+'Div',nSide=side,incP=incPart)
            nMultMat2 = gloss.name_format(prefix=gloss.lexicon('mtxMlt'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys'+'Mlt',nSide=side,incP=incPart)
            nCondition = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'Sys',nSide=side,incP=incPart)
            nCondition2 = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.nameEnd,nFunc=gloss.lexicon('roll')+'SysFull',nSide=side,incP=incPart)
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
            NodeCondition2 = mc.createNode("condition", n=nCondition2)
            mc.setAttr(NodeCondition2 + ".operation", 0)
            mc.setAttr(NodeCondition2 + ".colorIfTrueR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.rollFull', "%s.firstTerm" % (NodeCondition2), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfFalseR" % (NodeCondition2), force=True)
            NodeCondition = mc.createNode("condition", n=nCondition)
            mc.setAttr(NodeCondition + ".operation", 3)
            mc.setAttr(NodeCondition + ".colorIfFalseR",0)
            mc.connectAttr(dic[eachEl]['ik']+'.roll', "%s.firstTerm" % (NodeCondition), force=True)
            mc.connectAttr(NodeMultDiv2 + '.outputX', "%s.colorIfTrueR" % (NodeCondition), force=True)
            mc.connectAttr(NodeCondition2 + '.outColorR', "%s.colorIfFalseR" % (NodeCondition), force=True)

            val = 'X'
            if self.name == 'arm':
                val = 'Z'
                if side =='L':
                    nMltDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.nameEnd,nFunc='l',nSide=side,incP=incPart)
                    NodeMltDblLinear = mc.createNode("multDoubleLinear", n=nMltDblLin)
                    mc.setAttr(NodeMltDblLinear + ".input2", -1)
                    mc.connectAttr(dic[eachEl]['ik'] + '.roll', "%s.input1" % (NodeMltDblLinear), force=True)
                    mc.connectAttr(NodeMltDblLinear+'.output', "%s.input1X" % (NodeMultDiv1), force=True)

            [mc.connectAttr(NodeCondition + '.outColorR',"%s.rotate%s" % (each,val), force=True) for each in lsRollCtr]
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
            mc.scaleConstraint(dic[eachEl]["cnsPart"],nCnsStomp)
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
            mc.poleVectorConstraint(dic[eachEl]["upVEndMb"], ikHandle)
            mc.setAttr(ikHandle+".twist",abs(mc.getAttr(dic[eachEl]['lsFkMidMbJts'][0]+".rotateY")))
            mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHandle+'.ikBlend')
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

            for i, each in enumerate(dic[eachEl]['lsFkMidMbJts'][1:-1]):
                nIkHdlMb = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.nameEnd,nFunc=gloss.lexicon('jnt')+"%s"%(i+2),nSide=side,incP=incPart)

                ikHandle2 = libRig.createObj(partial(mc.ikHandle, **{'n':nIkHdlMb ,'sj':each,'ee':dic[eachEl]['lsFkMidMbJts'][i+2],'sol':self.IkType}),
                                            match=[lsParentRollCtr[i+1]],father=lsParentRollCtr[i+1],attributs={"snapEnable": 0,"visibility":0})
                mc.poleVectorConstraint(lsUpJnt[i], ikHandle2)
                mc.setAttr(ikHandle2+".twist",abs(mc.getAttr(each+".rotateY")))
                mc.connectAttr(dic[eachEl]["ikFkBlend"] + '.output', ikHandle2+'.ikBlend')
            # parent UPV TO JNTS _______________________________________
            for i, each in enumerate(dic[eachEl]['lsFkMidMbJts'][1:-2]):
                mc.parent(lsUpJnt[1:][i],each)


            # ADD ROOT TO CTR FOOT/HAND ________________________________
            mc.parent(dic[eachEl]['lsFkMidMb'][0],dic[eachEl]['lsFkMidMbJts'][0])

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
            #mc.parent(hookMidMb,self.hook)

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
                    endCtr = libRig.createController(name=nEndCtr,shape=libRig.Shp([self.typeCircle],color=valColorCtrIK,size=(1,1,1)),
                                                match=[each], father=None,attributs={"rotateOrder":rotOrdFk,"drawStyle": 2})
                    if side == 'R':
                        mc.rotate(0,180,180,endCtr['root'],os=True)
                        selShape = mc.listRelatives(endCtr['c'], s=True)[0]
                        recCv = mc.ls(selShape + '.cv[*]', fl=True)
                        mc.rotate(180,0,0, recCv)
                    # SNAP SHAPE TPL FK______________________________________
                    lib_shapes.snapShpCv(shpRef=each, shpTarget=endCtr['c'])
                    lsEndMbCtr.append(endCtr['c'])
                    lsEndMbRoot.append(endCtr['root'])
                    lsEndMbSk.append(endCtr['sk'])
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
                #print values[0]
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

                mc.aimConstraint(values[0], nAimHand, aim=aim, u=upV, wut='object', wuo=nUpVHand)
                # create sk
                libRig.createObj(partial(mc.joint, **{'n':nSkHand}),match=[nAimHand],father=nAimHand,
                                 attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":0,"radius":0.2})

                libRig.createObj(partial(mc.group, **{'n':nTrfHand, 'em': True}),match=[values[0]],
                                                        father=nAimHand,attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
                mc.pointConstraint(values[0],nTrfHand)
                lsEndMbCtrFirst.append(values[0])
                lsSkHand.append(nSkHand)
                lsTrfHand.append(nTrfHand)
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

            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)

            [mc.sets(each, edit=True, forceElement=nSetPart) for each in lsSkHand]
            for key,values in sorted(dicEndMbSk.items()):
                for i, each in enumerate(values):
                    mc.sets(each, edit=True, forceElement=nSetPart)
            # DICTIONARY TO CONTROL GRP________________________________________________
            cgFkMidMb = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name=gloss.lexiconAttr('cgFkMidMb'),nSide=side,incP=incPart)
            if mc.objExists(eachEl + '.%s'%(cgFkMidMb)):
                pass
            else:
                mc.addAttr(eachEl, ln=cgFkMidMb,dt='string',multi=True) # add MidMb Fk
            lenMidMb = mc.getAttr(eachEl + '.%s'%(cgFkMidMb), mi=True,s=True)
            lsEndMbFk = []
            for key,values in sorted(dicEndMbCtr.items()):
                for j, each in enumerate(values):
                    lsEndMbFk.append(each)
            [mc.setAttr(eachEl+'.%s[%s]'%(cgFkMidMb,lenMidMb+i),each,type='string') for i, each in enumerate(lsEndMbFk)]


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