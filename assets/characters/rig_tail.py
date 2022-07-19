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



class Tail(rig_world.RigWorld):

    def __init__(self, name='tail', tplInfo='tplInfo', hook = '',*args):
        rig_world.RigWorld.__init__(self)
        self.hook =hook
        self.name = name
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.typePin = "pinSimple"
        self.shpRotIk = (0,45,0)

    def createTail(self):
        # FILTER BY TPL INFO_______________________________________
        #lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        # CREATE RIG TO LISTE INFO_________________________________
        dicBuf = {}
        dicSk = {}
        lCtrl = []
        for i, eachTpl in enumerate([self.info]):
            # GET INFO TO CREATE RIG________________________________
            incPart = mc.getAttr(eachTpl+'.incInfo')
            side = (mc.attributeQuery("update",node=eachTpl, listEnum=1)[0]).split(":")[1]
            if side == 'empty': side =''
            color = lib_shapes.side_color(side=side)
            valColorCtr = color["colorCtr"]
            valColorCtrIK = color["colorIk"]
            valColorMstCtr = color["colorMaster"]
            sizeIk = (mc.attributeQuery("sizeSk",node=eachTpl, listEnum=1)[0]).split(":")[0]
            numbSk = (mc.attributeQuery("sizeSk",node=eachTpl, listEnum=1)[0]).split(":")[5]
            master = mc.getAttr(eachTpl+".%s[0]"%gloss.lexiconAttr('masterTpl'))
            lsTplIk =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            # NAME________________________________________________________________
            nSwitchsRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nCvSpine = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nSide=side,incP=incPart)
            nArcLen = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nSide=side,incP=incPart)
            nArcLenStretch = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nFunc=gloss.lexicon('stretch'),nSide=side,incP=incPart)
            nNoTouch = gloss.name_format(prefix=gloss.lexicon('NoTouch'),name=self.name,nSide=side,incP=incPart)
            nHook = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name,nSide=side,incP=incPart)
            nCog = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('cog'),nFunc=self.name,nSide=side,incP=incPart)
            nDownIk = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('pelvis'),nFunc=self.name+'Ik',nSide=side,incP=incPart)
            nTopIk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=self.name+'Ik',nSide=side,incP=incPart)
            # CREATE SWITCH_______________________________________________________
            createSwitchs = mc.createNode("nurbsCurve", n=nSwitchsCtr)
            father = mc.listRelatives(createSwitchs, p=True)
            rootSwitchs = mc.rename(father, nSwitchsRoot)
            # parentage switch Attrib
            mc.parent(rootSwitchs, self.nSwitch)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtr, ln="stretch", at="double", min=0, max=10, dv=0)
            mc.setAttr(nSwitchsCtr + ".stretch", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="squash", at="double", min=-10, max=10, dv=0)
            mc.setAttr(nSwitchsCtr + ".squash", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="slide", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".slide", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="frequency", at="double", min=0.1,dv=3)
            mc.setAttr(nSwitchsCtr + ".frequency", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="averageValue", at="double", min=1,dv=1)
            mc.setAttr(nSwitchsCtr + ".averageValue", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffA", at="double",dv=-int(numbSk))
            mc.setAttr(nSwitchsCtr + ".fallOffA", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffB", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".fallOffB", e=True, k=True)

            mc.addAttr(nSwitchsCtr, ln="sinSystem", nn="Sin System", at="enum", en=".:")
            mc.setAttr(nSwitchsCtr + ".sinSystem", e=True, cb=True)
            mc.addAttr(nSwitchsCtr, ln="amplitudeSide", at="double", min=-10, max=10, dv=0)
            mc.setAttr(nSwitchsCtr + ".amplitudeSide", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="distanceSide", at="double", dv=0)
            mc.setAttr(nSwitchsCtr + ".distanceSide", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="frequencySide", at="double", min=0.1,dv=3)
            mc.setAttr(nSwitchsCtr + ".frequencySide", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffSideA", at="double",dv=-int(numbSk))
            mc.setAttr(nSwitchsCtr + ".fallOffSideA", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffSideB", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".fallOffSideB", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="amplitudeFtBk", at="double", min=-10, max=10, dv=0)
            mc.setAttr(nSwitchsCtr + ".amplitudeFtBk", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="distanceFtBk", at="double", dv=0)
            mc.setAttr(nSwitchsCtr + ".distanceFtBk", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="frequencyFtBk", at="double", min=0.1,dv=0.5)
            mc.setAttr(nSwitchsCtr + ".frequencyFtBk", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffFtBkA", at="double",dv=-int(numbSk))
            mc.setAttr(nSwitchsCtr + ".fallOffFtBkA", e=True, k=True)
            mc.addAttr(nSwitchsCtr, ln="fallOffFtBkB", at="double",dv=0)
            mc.setAttr(nSwitchsCtr + ".fallOffFtBkB", e=True, k=True)

            # HIDE DEFAULT ATTRIBUTES ____________________________________________
            lib_attributes.hide_ctrl_hist(selObj=nSwitchsRoot)
            # FUSION TPL IK and CTR_______________________________________________
            concatIkFk = lsTplCtr
            concatIkFk.insert(0, lsTplIk[0])
            concatIkFk.insert(len(lsTplCtr) + 1, lsTplIk[-1])
            # ADJUST DEGRE WITH SUBDIVISE_________________________________________
            if len(concatIkFk) <= 2:
                degres = 1
                numbJtLen = len(concatIkFk) + 1
            elif len(concatIkFk) == 3:
                degres = 2
                numbJtLen = len(concatIkFk)
            else:
                degres = 3
                numbJtLen = len(concatIkFk) - 1
            # CREATE RIG CURVE____________________________________________________
            pos =[mc.xform(each2, q=True, ws=True, t=True) for each2 in concatIkFk]
            cvSpine = libRig.createObj(partial(mc.curve, **{'n': nCvSpine,'p':pos,'d':degres}))
            shp = mc.listRelatives(cvSpine, s=True)[0]
            mc.rename(shp,nCvSpine+'Shape')
            # ADD 2 POINTS ON CURVE______________________________________________
            lib_curves.crvSubdivide(crv=cvSpine, subDiv=0, subDivKnot=1, degree=degres)
            recCv = mc.ls(nCvSpine + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(nCvSpine + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(nCvSpine + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            recCv = mc.ls(nCvSpine + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            # CREATE CURVE INFO___________________________________________________
            arclen = mc.arclen(cvSpine, ch=True)
            nArclen = mc.rename(arclen, nArcLen)
            cvLen = mc.getAttr(nArclen + ".arcLength")
            # DIFF BETWEEN NUMBER TREADS AND CURVE LENGTH_________________________
            numbSk = int(numbSk)
            tread = (float(cvLen)/numbSk)
            # CREATE TRANSFORM TO CURVE___________________________________________
            numb = numbSk + 1
            count = 0
            getTrf = []
            getPtOnCv = []
            getParamAlongCv = []
            for each in range(numb):
                createSystCv = lib_connectNodes.ConnectCurve(cvLen,tread,numb,count,self.name,incPart,cvSpine,side)
                count += 1
                getTrf.append(createSystCv[0])
                getPtOnCv.append(createSystCv[1])
                getParamAlongCv.append(createSystCv[2])
            # DUPLICATE CURVE TO STRETCH___________________________________________
            nCvStretch = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('stretch'),nSide=side,incP=incPart)
            cvStretch = mc.duplicate(nCvSpine)
            mc.rename(cvStretch,nCvStretch)
            # CREATE CURVE INFO TO CV STRETCH______________________________________
            arclenStretch = mc.arclen(nCvStretch, ch=True)
            nArclenStretch = mc.rename(arclenStretch,nArcLenStretch)
            # HOOK________________________________________________________________
            hookTail = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), Match=self.nFly,father=self.nRig)
            # CREATE GRP NO TOUCH________________________________________________
            GrpNoTouch = libRig.createObj(partial(mc.group, **{'n': nNoTouch, 'em': True}),typeFunction={"group": {"visibility": 0}})
            # parentage group NoTouch avec HookSpine
            mc.parent(GrpNoTouch, hookTail)
            # COG___________________________________________________________________
            ctrCog = libRig.createController(name=nCog,shape=libRig.Shp([self.typeCircle],color=valColorMstCtr,size=(1.5,1.5,1.5)),match=master,father=hookTail)
            mc.setAttr(ctrCog["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            ################################# IK_###################################
            # CREATE ______________________________________________________________
            downIK = libRig.createController(name=nDownIk,shape=libRig.Shp([self.typeSquare],color=valColorCtrIK,size=(1,1,1),rotShp=self.shpRotIk),match=lsTplIk[0],father=None)
            mc.setAttr(downIK ["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            mc.setAttr(downIK ["root"] + ".segmentScaleCompensate",0)
            # CREATE CLUSTER_________________
            nCluster = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name, nFunc=gloss.lexicon('ik')+'Dwn',nSide=side,incP=incPart)
            clusterIkDwn = mc.createNode("cluster", n=nCluster)
            nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'),name=self.name, nFunc=gloss.lexicon('ik')+'Dwn',nSide=side,incP=incPart)
            mltMatCluster = mc.createNode("multMatrix", n=nMltMatCluster)
            mc.connectAttr(downIK['c'] + '.worldMatrix[0]', mltMatCluster + '.matrixIn[0]')
            mc.connectAttr(downIK['root'] + '.worldInverseMatrix[0]', mltMatCluster + '.matrixIn[1]')
            mc.connectAttr(mltMatCluster + '.matrixSum', nCluster+ '.weightedMatrix')
            mc.connectAttr(downIK['c'] + '.worldMatrix[0]', nCluster + '.matrix')
            mc.connectAttr(downIK['root'] + '.worldInverseMatrix[0]', nCluster + '.bindPreMatrix')
            mc.connectAttr(downIK['root'] + '.worldMatrix[0]', nCluster + '.preMatrix')

            topIK = libRig.createController(name=nTopIk,shape=libRig.Shp([self.typeSquare],color=valColorCtrIK,size=(1,1,1),rotShp=self.shpRotIk),match=lsTplIk[-1],father=None)
            mc.setAttr(topIK["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            # CREATE CLUSTER_________________
            nCluster = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name, nFunc=gloss.lexicon('ik')+'Top',nSide=side,incP=incPart)
            clusterIkTop = mc.createNode("cluster", n=nCluster)
            nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'),name=self.name, nFunc=gloss.lexicon('ik')+'Top',nSide=side,incP=incPart)
            mltMatCluster = mc.createNode("multMatrix", n=nMltMatCluster)
            mc.connectAttr(topIK['c'] + '.worldMatrix[0]', mltMatCluster + '.matrixIn[0]')
            mc.connectAttr(topIK['root'] + '.worldInverseMatrix[0]', mltMatCluster + '.matrixIn[1]')
            mc.connectAttr(mltMatCluster + '.matrixSum', nCluster + '.weightedMatrix')
            mc.connectAttr(topIK['c'] + '.worldMatrix[0]', nCluster+ '.matrix')
            mc.connectAttr(topIK['root'] + '.worldInverseMatrix[0]', nCluster + '.bindPreMatrix')
            mc.connectAttr(topIK['root'] + '.worldMatrix[0]', nCluster + '.preMatrix')

            # ADD SWITCH TO IK CTR_________________________________________________
            mc.parent(nSwitchsCtr, downIK["c"], s=True, add=True)
            mc.parent(nSwitchsCtr, topIK["c"], s=True, add=True)
            # Get Rot world Ik for start and end spine_____________________________
            getRotDownIk = mc.xform(downIK["c"], q=True, ws=True, ro=True)
            getRotTopIk = mc.xform(topIK["c"], q=True, ws=True, ro=True)

            # CHAIN JOINTS_________________________________________________________
            # CREATE DISTANCE DIMENSION____________________________________________
            if len(getPtOnCv) < 2:
                mc.warning("Select Minimun Two Elements :)")
            else:
                getDistDim = [mc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0)) for i, eachE in enumerate(getPtOnCv[:-1])]
                [mc.setAttr(eachE + ".visibility", 0) for i, eachE in enumerate(getDistDim)]
                # parentage DistanceDim avec group NoTouch
                [mc.parent(mc.pickWalk(each, d="up"), GrpNoTouch) for each in getDistDim]
                # CONNECTION_______________________________________________________
                delLoc = []
                for i, eachE in enumerate(getPtOnCv[:-1]):
                    delLoc= mc.listConnections("%s.startPoint" % (getDistDim[i]), s=True, d=False)
                    mc.connectAttr("%s.position" % (getPtOnCv[i]), "%s.startPoint" % (getDistDim[i]),
                                   force=True)
                    mc.connectAttr("%s.position" % (getPtOnCv[i + 1]), "%s.endPoint" % (getDistDim[i]),
                                   force=True)
                mc.delete(delLoc)
                valDist = [mc.getAttr(eachDist + ".distance") for i, eachDist in enumerate(getDistDim)]
                # CREATE BUF SK AND SK______________________________________________
                mc.select(cl=True)
                lsBufSk = []
                lsSk = []
                lsAnchor = []
                for i, eachTrf in enumerate(getTrf):
                    # NAME_________________________________________________________
                    nBufSk = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name+str(i+1), nSide=side,incP=incPart)
                    nSk = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name,nFunc=gloss.lexicon('buf')+str(i+1), nSide=side,incP=incPart)
                    nAnchor = gloss.name_format(prefix=gloss.lexicon('anchor'),name=self.name+str(i+1), nSide=side,incP=incPart)
                    positions2 = mc.xform(eachTrf, q=True, ws=True, translation=True)
                    rotations2 = mc.xform(eachTrf, q=True, ws=True, ro=True)
                    getJts = mc.joint(n=nBufSk, p=positions2, o=(rotations2[0], rotations2[1], rotations2[2]))
                    mc.setAttr(getJts +".drawStyle",2)
                    mc.select(cl=True)
                    getJtsSk = mc.joint(n=nSk, p=positions2, o=(rotations2[0], rotations2[1], rotations2[2]))
                    mc.setAttr(getJtsSk +".drawStyle",0)
                    mc.setAttr(getJtsSk +".radius",0.5*mc.getAttr("tpl_WORLD"+".scaleX"))
                    mc.select(cl=True)
                    getAnchor= mc.joint(n=nAnchor, p=positions2, o=(rotations2[0], rotations2[1], rotations2[2]))
                    mc.setAttr(getAnchor +".drawStyle",2)
                    mc.select(cl=True)
                    lsBufSk.append(getJts)
                    lsSk.append(getJtsSk)
                    lsAnchor.append(getAnchor)
                dicBuf["bufJts"] = lsBufSk
                dicSk["sk"] = lsSk
                [mc.parent(each,lsBufSk[i])for i, each in enumerate(lsBufSk[1:])]
                [mc.parent(each,lsSk[i])for i, each in enumerate(lsSk[1:])]
                [mc.parent(each,lsAnchor[i])for i, each in enumerate(lsAnchor[1:])]
                # ADJUST ORIENTATION JNTS__________________________________________
                for each in lsBufSk[:-1]: mc.joint(each, e=True, oj="yxz", sao="xup")
                for each in lsSk[:-1]: mc.joint(each, e=True, oj="yxz", sao="xup")
                for each in lsAnchor[:-1]: mc.joint(each, e=True, oj="yxz", sao="xup")
                mc.setAttr(lsBufSk[-1] + ".jointOrientX", 0)
                mc.setAttr(lsBufSk[-1] + ".jointOrientY", 0)
                mc.setAttr(lsBufSk[-1] + ".jointOrientZ", 0)
                mc.setAttr(lsSk[-1] + ".jointOrientX", 0)
                mc.setAttr(lsSk[-1] + ".jointOrientY", 0)
                mc.setAttr(lsSk[-1] + ".jointOrientZ", 0)
                mc.setAttr(lsAnchor[-1] + ".jointOrientX", 0)
                mc.setAttr(lsAnchor[-1] + ".jointOrientY", 0)
                mc.setAttr(lsAnchor[-1] + ".jointOrientZ", 0)
                # ADJUST SCALE LIMITS______________________________________________
                for each in lsSk:
                    mc.transformLimits(each, sx=(0.1, 1), esx=(1, 0))
                    mc.transformLimits(each, sy=(0.1, 1), esy=(1, 0))
                    mc.transformLimits(each, sz=(0.1, 1), esz=(1, 0))
                # DELETE TRF_______________________________________________________
                [mc.delete(each) for each in getTrf]
                # PARENT SK TO BUF_________________________________________________
                [mc.parent(eachJtSk, lsBufSk[i]) for i, eachJtSk in enumerate(lsSk)]
                [mc.parent(jtAnchor, lsBufSk[i]) for i, jtAnchor in enumerate(lsAnchor)]
                # O_JT TOP FOR ORIENTATION WITH STRETCH OR NOT_____________________
                # NAME_____________________________________________________________
                nOJt = gloss.name_format(prefix=gloss.lexicon('o'),name=self.name, nSide=side,incP=incPart)
                nTampOJt = gloss.name_format(prefix=gloss.lexicon('cnsO'),name=self.name, nSide=side,incP=incPart)
                # CREATE O_JT______________________________________________________
                ojt = libRig.createObj(partial(mc.joint, **{'n': nOJt}),match=[topIK["c"]],father=lsBufSk[-1],attributs={"drawStyle": 2})
                tampOjt = libRig.createObj(partial(mc.joint, **{'n': nTampOJt}),match=[topIK["c"]],father=lsBufSk[-1],attributs={"drawStyle": 2})
                # PARENT LAST SK IN O_JT___________________________________________
                mc.parent(lsSk[-1],ojt)
                mc.parent(lsAnchor[-1],ojt)
                #mc.connectAttr(hookTail + '.scale', lsSk[-1] + '.scale')
                '''
                # SYSTEM CREATE IK HANDLE__________________________________________
                lib_connectNodes.switchConstraints(partial(mc.orientConstraint,topIK["c"],ojt,**{'w':0}),partial(mc.orientConstraint,tampOjt,ojt,**{'w':1}),
                                                   attrib=nSwitchsCtr,attribType="stretch",nameObj=ojt,name=self.name,side=side,inc=incPart)
                '''
                # NAME_________________________________________________________
                nIkHandleSpine = gloss.name_format(prefix=gloss.lexicon('ikHandle'),name=self.name+str(1), nSide=side,incP=incPart)
                nIkHandleSpineRoot = gloss.name_format(prefix=gloss.lexicon('rootIkHandle'),name=self.name+str(1), nSide=side,incP=incPart)
                nGrpJts = gloss.name_format(prefix=gloss.lexicon('rootJt'),name=self.name+str(1), nSide=side,incP=incPart)
                nExpTwistIk = gloss.name_format(prefix=gloss.lexicon('exp'),name=self.name,nFunc=gloss.lexicon('twist'), nSide=side,incP=incPart)
                # CREATE IK HANDLE_______________________________________________
                ikHandleSpine = libRig.createObj(partial(mc.ikHandle, **{'n': nIkHandleSpine, 'sj': lsBufSk[0],'ee': lsBufSk[-1],
                                'sol': 'ikSplineSolver','c': cvSpine, 'fj': False, 'ccv': False,'scv': True}))
                grpIkHandleSpine = libRig.createObj(partial(mc.group, **{'n': nIkHandleSpineRoot, 'em': True}),match=[ikHandleSpine],childLst=[ikHandleSpine])
                # PARENT CURVE WITH HOOK SPINE___________________________________
                mc.select(cl=True)
                getJtGrp = libRig.createObj(partial(mc.joint, **{'n':nGrpJts}),match=lsTplIk[0], father=ctrCog["c"],attributs={"drawStyle": 2,"visibility": 0})
                mc.parent(lsBufSk[0],getJtGrp)
                mc.setAttr(getJtGrp + ".rotateOrder", 3, l=False, k=True)
                mc.setAttr(getJtGrp + ".segmentScaleCompensate", 0)
                mc.setAttr(getJtGrp + ".inheritsTransform", 0)
                mc.setAttr(getJtGrp + ".jointOrientX", 0)
                mc.setAttr(getJtGrp + ".jointOrientY",0)
                mc.setAttr(getJtGrp + ".jointOrientZ", 0)
                mc.setAttr(lsBufSk[0] + ".jointOrientX", 0)
                mc.setAttr(lsBufSk[0] + ".jointOrientY", 0)
                mc.setAttr(lsBufSk[0] + ".jointOrientZ", 0)
                # DUPLICATION JOINT TO SKIN CURVE____________________________________
                mc.parent(cvSpine, gloss.lexicon('world')+'Center')
                mc.parent(nCvStretch, gloss.lexicon('world')+'Center')
                mc.select(cl=True)
                rotationsDownIK = mc.xform(lsTplIk[0], q=True, ws=True, ro=True)

                # CREATE FK__________________________________________________________
                lsFkControl = []
                lsFkRoot = []
                lsFkControlAll = []
                if len(concatIkFk) > 2:
                    for i, elemFK in enumerate(concatIkFk[1:-1]):
                        # NAME_______________________________________________________
                        nFk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name+str(i+1), nSide=side,incP=incPart)
                        # CREATE_____________________________________________________
                        createFk = libRig.createController(name=nFk,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)),match=[elemFK])
                        mc.setAttr(createFk["root"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
                        mc.setAttr(createFk["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
                        mc.parent(nSwitchsCtr,createFk["c"], s=True, add=True)
                        skCtr= gloss.renameSplit(selObj=createFk["sk"], namePart=['sk'], newNamePart=['jnt'], reNme=True)
                        lCtrl.append(createFk)
                        lsFkControl.append(createFk["c"])
                        lsFkRoot.append(createFk["root"])
                        lsFkControlAll.append(createFk["c"])
                    # PARENT FK BETWEEN THEM_________________________________________
                    [mc.parent(lsFkRoot[i + 1], lsFkControl[i]) for i, each in enumerate(lsFkRoot[1:])]
                    mc.setAttr(lsFkRoot[0] + ".segmentScaleCompensate", 0)
                else:
                    pass
                lsFkControlAll.insert(0,ctrCog['c'])

                # CREATE ADD IK CONTROL MIDDLE_______________________________________
                # CREATE Loft To Parent ctr middle____________________________________
                getCrv = lib_curves.createDoubleCrv(objLst=concatIkFk, axis='X', offset=0.2)
                # ADD 2 POINTS ON CURVE______________________________________________
                lib_curves.crvSubdivide(crv=getCrv['crv'][0], subDiv=0, subDivKnot=1, degree=degres)
                lib_curves.crvSubdivide(crv=getCrv['crv'][1], subDiv=0, subDivKnot=1, degree=degres)
                cv1 = mc.rename(getCrv['crv'][0],gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name+'Cls1',nSide=side,incP=incPart))
                cv2 = mc.rename(getCrv['crv'][1],gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name+'Cls2',nSide=side,incP=incPart))
                recCv = mc.ls(cv1 + '.cv[*]', fl=True)
                mc.delete(recCv[2],s=True)
                recCv = mc.ls(cv1 + '.cv[*]', fl=True)
                mc.delete(recCv[2],s=True)
                recCv = mc.ls(cv1 + '.cv[*]', fl=True)
                mc.delete(recCv[-3],s=True)
                recCv = mc.ls(cv1 + '.cv[*]', fl=True)
                mc.delete(recCv[-3],s=True)
                recCv = mc.ls(cv2 + '.cv[*]', fl=True)
                mc.delete(recCv[2],s=True)
                recCv = mc.ls(cv2 + '.cv[*]', fl=True)
                mc.delete(recCv[2],s=True)
                recCv = mc.ls(cv2 + '.cv[*]', fl=True)
                mc.delete(recCv[-3],s=True)
                recCv = mc.ls(cv2 + '.cv[*]', fl=True)
                mc.delete(recCv[-3],s=True)
                nLoftBase = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name+'Cls',nSide=side,incP=incPart)
                loftBase = libRig.createObj(partial(mc.loft, cv1, cv2,**{'n':nLoftBase, 'ch':True, 'u':True,'c':0,'ar':1,'d':3,'ss':0,'rn':0,'po':0,'rsn':True})
                                          , father=self.nWorldCenter, refObj=None, incPart=False, attributs={"visibility":0})

                mc.parent(cv1,self.nWorldCenter)
                mc.parent(cv2,self.nWorldCenter)

                # SKIN CVS____________________________________________________________
                skinCurveJoints = mc.skinCluster(lsFkControlAll, cvSpine, tsb=True, mi=1)
                skinCurveJoints = mc.skinCluster(lsFkControlAll, cv1, tsb=True, mi=1)
                skinCurveJoints = mc.skinCluster(lsFkControlAll, cv2, tsb=True, mi=1)
                skinCurveJoints = mc.skinCluster(lsFkControlAll, nCvStretch, tsb=True, mi=1)

                # RETURN SKIN CLUSTER________________________________________________
                ListHist = mc.listHistory(cvSpine, pdo=True)
                SkinCluster = mc.ls(ListHist, type="skinCluster")
                recCv = mc.ls(cvSpine + '.cv[*]', fl=True)

                ListHist = mc.listHistory(cv1, pdo=True)
                SkinCluster1 = mc.ls(ListHist, type="skinCluster")
                recCv1 = mc.ls(cv1 + '.cv[*]', fl=True)

                ListHist = mc.listHistory(cv2, pdo=True)
                SkinCluster2 = mc.ls(ListHist, type="skinCluster")
                recCv2 = mc.ls(cv2 + '.cv[*]', fl=True)

                ListHist = mc.listHistory(nCvStretch, pdo=True)
                SkinCluster3 = mc.ls(ListHist, type="skinCluster")
                recCvStretch = mc.ls(nCvStretch + '.cv[*]', fl=True)


                for i, each in enumerate(recCv[1:-2]):
                    mc.skinPercent(SkinCluster[0], each, r=False,transformValue=(lsFkControlAll[i], 1))
                for i, each in enumerate(recCv1[1:-2]):
                    mc.skinPercent(SkinCluster1[0], each, r=False,transformValue=(lsFkControlAll[i], 1))
                for i, each in enumerate(recCv2[1:-2]):
                    mc.skinPercent(SkinCluster2[0], each, r=False,transformValue=(lsFkControlAll[i], 1))
                for i, each in enumerate(recCvStretch[1:-2]):
                    mc.skinPercent(SkinCluster3[0], each, r=False,transformValue=(lsFkControlAll[i], 1))
                # ADJUST SKIN 2 LAST CV______________________________________________
                mc.skinPercent(SkinCluster[0], recCv[-1], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster[0], recCv[-2], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster1[0], recCv1[-1], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster1[0], recCv1[-2], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster2[0], recCv2[-1], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster2[0], recCv2[-2], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster3[0], recCvStretch[-1], r=False,transformValue=(lsFkControlAll[-1], 1))
                mc.skinPercent(SkinCluster3[0], recCvStretch[-2], r=False,transformValue=(lsFkControlAll[-1], 1))

                #lsClusters = [clusterIkDwn,clusterIkMid,clusterIkTop]
                lsClusters = [clusterIkDwn,clusterIkTop]
                ########
                # get point loftSk_______________________________
                recCv = mc.ls(cvSpine + '.cv[*]', fl=True)
                recCv1 = mc.ls(cv1 + '.cv[*]', fl=True)
                recCv2 = mc.ls(cv2 + '.cv[*]', fl=True)
                recCvStretch = mc.ls(nCvStretch + '.cv[*]', fl=True)

                adjustNumb = 1
                selDiv2 = int(math.ceil(float(len(recCv))/adjustNumb))
                val = 0
                dictPointSk ={}
                for each2 in range(selDiv2):
                    part = []
                    for each in range(adjustNumb):
                        part.append(recCv[each+val])
                    val += adjustNumb
                    dictPointSk[each2]= part
                val = [round(abs(-i/float(dictPointSk.keys()[-3])), 4) for i, each in enumerate(recCv[1:-1])]

                # adjust value cluster Down loft
                mc.deformer(lsClusters[0], e=True, g=recCv[0])
                mc.deformer(lsClusters[0], e=True, g=recCv[-1])
                mc.percent(lsClusters[0], recCv[-1], value=0)

                mc.deformer(lsClusters[0], e=True, g=recCv1[0])
                mc.deformer(lsClusters[0], e=True, g=recCv1[-1])
                mc.percent(lsClusters[0], recCv1[-1], value=0)

                mc.deformer(lsClusters[0], e=True, g=recCv2[0])
                mc.deformer(lsClusters[0], e=True, g=recCv2[-1])
                mc.percent(lsClusters[0], recCv2[-1], value=0)

                mc.deformer(lsClusters[0], e=True, g=recCvStretch[0])
                mc.deformer(lsClusters[0], e=True, g=recCvStretch[-1])
                mc.percent(lsClusters[0], recCvStretch[-1], value=0)

                for i, each in enumerate(recCv[1:-1]):
                    mc.deformer(lsClusters[0], e=True, g=each)
                    mc.percent(lsClusters[0], each, value=val[::-1][i])
                for i, each in enumerate(recCv1[1:-1]):
                    mc.deformer(lsClusters[0], e=True, g=each)
                    mc.percent(lsClusters[0], each, value=val[::-1][i])
                for i, each in enumerate(recCv2[1:-1]):
                    mc.deformer(lsClusters[0], e=True, g=each)
                    mc.percent(lsClusters[0], each, value=val[::-1][i])
                for i, each in enumerate(recCvStretch[1:-1]):
                    mc.deformer(lsClusters[0], e=True, g=each)
                    mc.percent(lsClusters[0], each, value=val[::-1][i])

                # adjust value cluster Top loft
                mc.deformer(lsClusters[1], e=True, g=recCv[0])
                mc.deformer(lsClusters[1], e=True, g=recCv[-1])
                mc.percent(lsClusters[1], recCv[0], value=0)

                mc.deformer(lsClusters[1], e=True, g=recCv1[0])
                mc.deformer(lsClusters[1], e=True, g=recCv1[-1])
                mc.percent(lsClusters[1], recCv1[0], value=0)

                mc.deformer(lsClusters[1], e=True, g=recCv2[0])
                mc.deformer(lsClusters[1], e=True, g=recCv2[-1])
                mc.percent(lsClusters[1], recCv2[0], value=0)

                mc.deformer(lsClusters[1], e=True, g=recCvStretch[0])
                mc.deformer(lsClusters[1], e=True, g=recCvStretch[-1])
                mc.percent(lsClusters[1], recCvStretch[0], value=0)

                for i, each in enumerate(recCv[1:-1]):
                    mc.deformer(lsClusters[1], e=True, g=each)
                    mc.percent(lsClusters[1], each, value=val[i])
                for i, each in enumerate(recCv1[1:-1]):
                    mc.deformer(lsClusters[1], e=True, g=each)
                    mc.percent(lsClusters[1], each, value=val[i])
                for i, each in enumerate(recCv2[1:-1]):
                    mc.deformer(lsClusters[1], e=True, g=each)
                    mc.percent(lsClusters[1], each, value=val[i])
                for i, each in enumerate(recCvStretch[1:-1]):
                    mc.deformer(lsClusters[1], e=True, g=each)
                    mc.percent(lsClusters[1], each, value=val[i])

                # CREATE ADD IK CONTROL_______________________
                lsAddIk = []
                lsAddIk.extend(lsFkControlAll)
                lsAddIk.append(topIK["c"])
                lsRootIkAdd =[]
                lsClstIkAdd =[]
                sclWorld = mc.getAttr("tpl_WORLD"+".scaleX")
                for k, each in enumerate(lsAddIk):
                    # NAME_______________________________________________________
                    nIkAdd = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('add')+'Ik'+str(k+1),nSide=side,incP=incPart)
                    # CREATE_____________________________________________________
                    createIkAdd = libRig.createController(name=nIkAdd,shape=libRig.Shp([self.typePin],color=valColorCtrIK,size=(1*sclWorld,1*sclWorld,1*sclWorld),rotShp=(0,90,0)),match=[each])
                    mc.setAttr(createIkAdd["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)

                    # CREATE CLUSTER_________________
                    nCluster = gloss.name_format(prefix=gloss.lexicon('cls'), name=self.name, nFunc=gloss.lexicon('mid')+str(k+1),nSide=side,incP=incPart)
                    clusterIkMid = mc.createNode("cluster", n=nCluster)
                    nMltMatCluster = gloss.name_format(prefix=gloss.lexicon('mltM'),name=self.name, nFunc=gloss.lexicon('mid')+str(k+1),nSide=side,incP=incPart)
                    mltMatCluster = mc.createNode("multMatrix", n=nMltMatCluster)
                    mc.connectAttr(createIkAdd['c'] + '.worldMatrix[0]', mltMatCluster + '.matrixIn[0]')
                    mc.connectAttr(createIkAdd['root'] + '.worldInverseMatrix[0]', mltMatCluster + '.matrixIn[1]')
                    mc.connectAttr(mltMatCluster + '.matrixSum', clusterIkMid + '.weightedMatrix')
                    mc.connectAttr(createIkAdd['c'] + '.worldMatrix[0]', clusterIkMid + '.matrix')
                    mc.connectAttr(createIkAdd['root'] + '.worldInverseMatrix[0]', clusterIkMid + '.bindPreMatrix')
                    mc.connectAttr(createIkAdd['root'] + '.worldMatrix[0]', clusterIkMid + '.preMatrix')
                    # ADD SWITCH TO ADD IK CONTROL MIDDLE_________________________________
                    mc.parent(nSwitchsCtr, createIkAdd["c"], s=True, add=True)
                    lsRootIkAdd.append(createIkAdd["root"])
                    lsClstIkAdd.append(nCluster)


                lsRootIkAdd.append(loftBase)

                # CREATE SA_______________________
                lSa = lib_connectNodes.nurbs_attach(lsObj =lsRootIkAdd,parentInSA=True,delLoc=True)
                [mc.parent(each,self.nSa) for each in lSa]
                # ADD CONTROLS CLUSTER VALUE________________________
                for j, each in enumerate(lsClstIkAdd):
                    mc.deformer(each, e=True, g=recCv[j+1])
                    mc.percent(each, recCv[j+1], value=1)

                mc.deformer(lsClstIkAdd[0], e=True, g=recCv[0])
                mc.deformer(lsClstIkAdd[-1], e=True, g=recCv[-1])
                mc.percent(lsClstIkAdd[0], recCv[0], value=1)
                mc.percent(lsClstIkAdd[-1], recCv[1], value=1)

                # HIDE IK HANDLE AND CURVE___________________________
                mc.setAttr(ikHandleSpine +".visibility",0)
                mc.setAttr(cvSpine +".visibility",0)
                mc.setAttr(cv1 +".visibility",0)
                mc.setAttr(cv2 +".visibility",0)
                mc.setAttr(nCvStretch +".visibility",0)

                #____________________________________ STRETCH___________________________
                valAttr = 10
                expStretch = lib_connectNodes.expStretchSpine(self.name,incPart, ctrCog['c'], nArclen, cvLen, lsSk,valAttr, numbSk, nSwitchsCtr,lsBufSk, getDistDim,valDist,side,allSk=True)

                expSin = lib_connectNodes.expSin(self.name,incPart, ctrCog['c'], nArclen, cvLen, lsSk,valAttr, numbSk, nSwitchsCtr,lsBufSk, getDistDim,valDist,side)
                #CONNECT SCALE TO FIRST AND LAST SK
                #mc.connectAttr((expStretch + ".outputScale"), (lsSk[0] + ".scale"))
                #mc.connectAttr((expStretch + ".outputScale"), (lsSk[-1] + ".scale"))
                for each in lsAnchor:
                    mc.connectAttr((expStretch + ".outputScale"), (each + ".scale"))
                # TWIST SYSTEM_______________________________________
                valNumbRoot = 1 + (1 / numbSk)
                valNumbEnd = (1 * numbSk)
                lib_connectNodes.expTwist(lsBufSk, valNumbRoot, valNumbEnd, downIK['c'], topIK['c'], self.name,side,incPart)
                # TWIST SYSTEM WITH FK_______________________________
                val = "(0"
                for each in lsFkControl:
                    val += "+%s.rotateY" % (each)
                exprTwist = "%s.twist" % (ikHandleSpine) + "=" + "%s)" % (val)
                mc.expression(s="%s.twist" % (ikHandleSpine) + "=" + "%s-%s.rotateY)" % (val,downIK ["c"]), n=nExpTwistIk)


                #adjust distanceValue_______________________________________________________
                # get init parameter value
                stepTread = 0
                countParam = 0
                mc.setAttr(getPtOnCv[1] + '.parameter', 0)
                for each in range(100000):
                    if mc.getAttr(getDistDim[0] + '.distance') < tread:
                        countParam += 0.00001
                        mc.setAttr(getPtOnCv[1] + '.parameter', countParam)
                    else:
                        stepTread += mc.getAttr(getPtOnCv[1] + '.parameter')
                        break

                concat = stepTread
                roundTread = round(tread,6)
                for j, eachPtcv in enumerate(getPtOnCv[1:-1]):
                    mc.setAttr(eachPtcv + '.parameter', concat)
                    countParam = 0
                    for each in range(100000):
                        if mc.getAttr(getDistDim[j] + '.distance') < roundTread or mc.getAttr(eachPtcv + '.parameter')==0:
                            countParam += 0.00001
                            mc.setAttr(eachPtcv + '.parameter',countParam+concat)
                        else:
                            concat = mc.getAttr(eachPtcv + '.parameter')
                            break

                ############################ Parentage et connection elements ###########################################
                mc.parentConstraint(ctrCog['c'], getJtGrp)
                mc.parentConstraint(topIK['c'], grpIkHandleSpine, w=1)
                 # parentage IKHandle avec ctr Cog
                mc.parent(grpIkHandleSpine, ctrCog['c'])
                # contraindre premier fk avec ctr Cog
                mc.parent(downIK['root'], ctrCog['c'])
                # parent les ik avec les fk ###
                if len(concatIkFk[0:-1]) > 2:
                    mc.parent(topIK["root"], lsFkControl[-1])
                    mc.parent(lsFkRoot[0], ctrCog["c"])
                else:
                    mc.parent(topIK["c"], ctrCog)
                # SNAP CVS____________________________________________
                # MASTER______________________________________________
                lib_shapes.snapShpCv(shpRef=master, shpTarget=nCog)
                # IK______________________________________________
                [lib_shapes.snapShpCv(shpRef=each, shpTarget=[downIK['c'],topIK['c']][i]) for i, each in enumerate(lsTplIk)]
                # FK______________________________________________
                [lib_shapes.snapShpCv(shpRef=concatIkFk[1:-1][i], shpTarget=each) for i, each in enumerate(lsFkControl)]
                '''
                # ADD IK MIDDLE_______________________________________
                lib_shapes.snapShpCv(shpRef=lsFkControl[len(lsFkControl)/2], shpTarget=nIkMiddle)
                selShape = mc.listRelatives(nIkMiddle, s=True)[0]
                recCv = mc.ls(selShape + '.cv[*]', fl=True)
                mc.scale(0.8,0.8,0.8, recCv)
                getPos = mc.xform(lSa['sa'][0], q=True, ws=True, translation=True)
                getRot = mc.xform(lSa['sa'][0], q=True, ws=True, rotation=True)
                mc.xform(ikMiddle['root'], worldSpace=True, t=getPos)
                mc.xform(ikMiddle['root'], worldSpace=True, ro=getRot)
                mc.parent(ikMiddle['root'],lSa['sa'][0])
                mc.setAttr(ikMiddle['root'] + '.rotateX',0)
                mc.setAttr(ikMiddle['root'] + '.rotateY',0)
                mc.setAttr(ikMiddle['root'] + '.rotateZ',0)
                mc.parent(lSa['sa'][0],ctrCog["c"])
                '''
                # SET SKIN_________________________________________
                mc.select(cl=True)
                nSetPart = gloss.name_format(prefix=gloss.lexicon('set'), name=gloss.lexicon('skin'), incP=incPart)
                if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
                for i, each in enumerate(lsSk):
                    mc.sets(each, edit=True, forceElement=nSetPart)
                # RENAME SK_________________________________________
                lsSkRename= [gloss.renameSplit(selObj=each, namePart=['spineBuf'], newNamePart=['spine'], reNme=True) for each in lsSk]

                # LIST HOOK IN TPL INFO_________________________________________
                lsHooks = lsAnchor[1:]
                if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                    pass
                else:
                    mc.addAttr(eachTpl, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
                [mc.setAttr(eachTpl+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]

                # ATTRIBUTES TO CONTROL GRP________________________________________________
                cogCtr = ctrCog["c"]
                #lsIkCtr = [downIK['c'],ikMiddle['c'],topIK['c']]
                lsIkCtr = [downIK['c'],topIK['c']]
                lsFkCtr = lsFkControl
                # NAME CG_____________________________________________
                cgMaster = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgMaster'),nSide=side,incP=incPart)
                cgSwitch = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgSwitch'),nSide=side,incP=incPart)
                cgIk = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgIk'),nSide=side,incP=incPart)
                cgFk = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)

                if mc.objExists(eachTpl+'.%s'%cgMaster):
                    pass
                else:
                    mc.addAttr(eachTpl, ln=cgMaster,dt='string',multi=True) # add Cg Master
                    mc.addAttr(eachTpl, ln=cgSwitch,dt='string',multi=True) # add Cg switch
                    mc.addAttr(eachTpl, ln=cgIk,dt='string',multi=True) # add Cg ik
                    mc.addAttr(eachTpl, ln=cgFk,dt='string',multi=True) # add Cg fk
                mc.setAttr(eachTpl+'.%s['%(cgMaster) +str(0)+']',cogCtr,type='string')
                mc.setAttr(eachTpl+'.%s['%(cgSwitch) +str(0)+']',createSwitchs,type='string')
                [mc.setAttr(eachTpl+'.%s['%(cgIk) +str(i)+']',each,type='string') for i, each in enumerate(lsIkCtr)]
                [mc.setAttr(eachTpl+'.%s['%(cgFk) +str(i)+']',each,type='string') for i, each in enumerate(lsFkCtr)]

                # PARENT HOOK WITH RIG MEMBER________________________________________________
                mc.parent(hookTail,self.hook)

        return dicBuf, dicSk, lCtrl
