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

class Eyes(rig_world.RigWorld):


    def __init__(self, name='eye', tplInfo='tplInfo', hook ='',*args):
        rig_world.RigWorld.__init__(self)
        self.hook = hook
        self.name = name
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeTriangle = "triangle"
        self.typeSquare = "square"
        self.shpRotIk = (90,0,0)
        self.shpRotEyeCtr = (0,90,0)

    def createEyes(self):
        # FILTER BY TPL INFO____________________________________________
        #lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.nameHead])
        #[self.info]
        # CREATE RIG TO LISTE INFO_______________________________________
        for i, eachTpl in enumerate([self.info]):
            # GET INFO TO CREATE HEAD____________________________________
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
            getModuleMirror = mc.listConnections(eachTpl+'.moduleMirror')

            # CREATE________________________________________________________
            # NAME__________________________________________________________
            nHook = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.name, nSide=side, incP=incPart)
            nBuf = gloss.name_format(prefix=gloss.lexicon('buf'), name=self.name, nSide=side, incP=incPart)
            # HOOK ______________________________________________________
            hookEyes = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), match=lsTplIk[0],father=self.nRig)
            bufEyes = libRig.createObj(partial(mc.group, **{'n': nBuf, 'em': True}), match=lsTplIk[0],father=hookEyes)

            valScl= mc.getAttr("tpl_WORLD"+".scaleX")
            # CREATE CTR LOOK AT GLOBAL______________________________________
            lsTplLookAt = [lsTplIk[-1]]
            lsTplDirection = [lsTplIk[0]]
            if getModuleMirror == None:
                pass
            else:
                getTplLast = [mc.getAttr(getModuleMirror[0]+'.ik[%s]'%i) for i in range(mc.getAttr(getModuleMirror[0]+'.ik', mi=True,s=True))][-1]
                lsTplLookAt.append(getTplLast)
                getTplDirection = [mc.getAttr(getModuleMirror[0]+'.ik[%s]'%i) for i in range(mc.getAttr(getModuleMirror[0]+'.ik', mi=True,s=True))][0]
                lsTplDirection.append(getTplDirection)

            nFkLookAt = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('lookAt'),incP=incPart)
            nFkDir = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,incP=incPart)
            if mc.objExists(nFkLookAt):
                nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'))
            else:
                # CREATE SWITCH_______________________________________________________
                nSwitchsRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('switch'))
                nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'))
                createSwitchs = mc.createNode("nurbsCurve", n=nSwitchsCtr)
                father = mc.listRelatives(createSwitchs, p=True)
                rootSwitchs = mc.rename(father, nSwitchsRoot)
                # parentage switch Attrib
                mc.parent(rootSwitchs, self.nSwitch)
                # ADD ATTRIBUTES TO SWITCH____________________________________________
                mc.addAttr(nSwitchsCtr, ln="lookAt", at="double", min=0, max=10, dv=0)
                mc.setAttr(nSwitchsCtr + ".lookAt", e=True, k=True)
                # HIDE DEFAULT ATTRIBUTES ____________________________________________
                lib_attributes.hide_ctrl_hist(selObj=nSwitchsRoot)

                fkLookAt= libRig.createController(name=nFkLookAt,shape=libRig.Shp([self.typeCircle],color="yellow",size=(1*valScl,1*valScl,1*valScl),rotShp=self.shpRotIk),
                                                  match=lsTplIk[1],father=bufEyes)
                fkDir= libRig.createController(name=nFkDir,shape=libRig.Shp([self.typeTriangle],color="yellow",size=(1.5*valScl,1.5*valScl,1.5*valScl),rotShp=self.shpRotEyeCtr),
                                                  match=lsTplIk[0],father=bufEyes)
                # adjust position CTR LOOK AT GLOBAL_____________________________
                pointCns = mc.pointConstraint(lsTplLookAt,fkLookAt['root'])
                orientCns = mc.orientConstraint(lsTplLookAt,fkLookAt['root'])
                mc.select(cl=True)
                pointCnsDir = mc.pointConstraint(lsTplDirection,fkDir['root'])
                orientCnsDir = mc.orientConstraint(lsTplDirection,fkDir['root'])
                mc.select(cl=True)
                # purge Constraint ###
                mc.delete(pointCns)
                mc.delete(orientCns)
                mc.delete(pointCnsDir)
                mc.delete(orientCnsDir)
                # ADD SWITCH TO IK CTR_________________________________________________
                mc.parent(nSwitchsCtr, nFkLookAt, s=True, add=True)
                mc.parent(nSwitchsCtr, nFkDir, s=True, add=True)


            # CREATE CTR LOOK AT_____________________________________________
            nFkLookAtSide = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('lookAt'),nSide=side,incP=incPart)
            fkLookAtSide= libRig.createController(name=nFkLookAtSide,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(0.3*valScl,0.3*valScl,0.3*valScl),rotShp=self.shpRotIk),
                                                  match=lsTplIk[1],father=nFkLookAt)

            # CREATE AIM AND UPV_____________________________________________
            nBufAim = gloss.name_format(prefix=gloss.lexicon('buf'), name=gloss.lexicon('lookAt'),nFunc=gloss.lexicon('aim'), nSide=side, incP=incPart)
            nUpVAim = gloss.name_format(prefix=gloss.lexicon('upV'), name=gloss.lexicon('lookAt'),nFunc=gloss.lexicon('aim'), nSide=side, incP=incPart)
            nAim = gloss.name_format(prefix=gloss.lexicon('aim'),name=gloss.lexicon('lookAt'),nSide=side,incP=incPart)
            nAimTarget = gloss.name_format(prefix=gloss.lexicon('aim'),name=self.name,nFunc=gloss.lexicon('lookAt'),nSide=side,incP=incPart)


            bufAim = libRig.createObj(partial(mc.group, **{'n':nBufAim, 'em': True}), match=lsTplIk[0],father=bufEyes)
            upVAim = libRig.createObj(partial(mc.group, **{'n':nUpVAim, 'em': True}), match=lsTplIk[0],father=bufAim)
            aim = libRig.createObj(partial(mc.joint, **{'n':nAim}), match=[lsTplIk[0]], father=bufAim,
            attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
            aimTarget = libRig.createObj(partial(mc.group, **{'n':nAimTarget, 'em': True}), match=lsTplIk[1],father=nFkDir)
            mc.move(0,2,0,upVAim,r=True)


            mc.aimConstraint(fkLookAtSide['c'],aim,aim=(0,0,1),u=(0,1,0), wut="object", wuo=upVAim)
            mc.select(cl=True)
            firstAimCons = mc.listConnections(mc.listRelatives(aim, type="constraint")[0]+ ".target", p=True)[-1]
            mc.aimConstraint(aimTarget,aim,aim=(0,0,1),u=(0,1,0), wut="object", wuo=upVAim)
            secondAimCons = mc.listConnections(mc.listRelatives(aim, type="constraint")[0]+ ".target", p=True)[-1]
            mc.select(cl=True)

            # create nodes for switch constraint aim ###
            nExprMlDv = gloss.name_format(prefix=gloss.lexicon('mltDiv'),name=self.name,nFunc='Div',nSide=side,incP=incPart)
            nExprMlDblLin = gloss.name_format(prefix=gloss.lexicon('mltDblLin'),name=self.name,nSide=side,incP=incPart)
            nExprAddDblLin = gloss.name_format(prefix=gloss.lexicon('addDblLin'),name=self.name,nSide=side,incP=incPart)
            # create ###
            NodeMultDiv = mc.createNode( "multiplyDivide",n= nExprMlDv)
            mc.setAttr(NodeMultDiv+ ".operation",2); mc.setAttr(NodeMultDiv+ ".input2X",10)
            NodeMultDblLinear = mc.createNode( "multDoubleLinear",n= nExprMlDblLin)
            mc.setAttr(NodeMultDblLinear+ ".input2",-1)
            NodeAddDblLinear = mc.createNode( "addDoubleLinear",n= nExprAddDblLin)
            mc.setAttr(NodeAddDblLinear+ ".input2",1)
            # connect ###
            mc.connectAttr("%s.lookAt" %(nSwitchsCtr), "%s.input1X" %(NodeMultDiv),force=True)
            mc.connectAttr("%s.outputX" %(NodeMultDiv), "%s" %(firstAimCons),force=True)
            mc.connectAttr("%s" %(firstAimCons), "%s.input1" %(NodeMultDblLinear),force=True)
            mc.connectAttr( "%s.output" %(NodeMultDblLinear), "%s.input1" %(NodeAddDblLinear),force=True)
            mc.connectAttr("%s.output" %(NodeAddDblLinear), "%s" %(secondAimCons),force=True)

            # ADD SWITCH TO IK CTR_________________________________________________
            mc.parent(nSwitchsCtr, fkLookAtSide['c'], s=True, add=True)

            # LIST HOOK IN TPL INFO_________________________________________
            lsHooks = [aim]
            if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                pass
            else:
                mc.addAttr(eachTpl, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
            [mc.setAttr(eachTpl+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]

            # ATTRIBUTES TO CONTROL GRP________________________________________________
            lsFkCtr = [nFkLookAt,nFkDir,fkLookAtSide['c']]
            # NAME CG_____________________________________________
            cgFkMb = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)
            cgSwitch = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgSwitch'),nSide=side,incP=incPart)
            if mc.objExists(eachTpl+'.%s'%cgFkMb):
                pass
            else:
                mc.addAttr(eachTpl, ln=cgFkMb,dt='string',multi=True) # add head fk
                mc.addAttr(eachTpl, ln=cgSwitch,dt='string',multi=True) # add Cg switch
            mc.setAttr(eachTpl+'.%s['%(cgSwitch) +str(0)+']',nSwitchsCtr,type='string')
            [mc.setAttr(eachTpl+'.%s['%(cgFkMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkCtr)]
            # PARENT HOOK WITH RIG MEMBER________________________________________________
            mc.parent(hookEyes, world=True)