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

class Head(rig_world.RigWorld):


    def __init__(self, name='head', tplInfo='tplInfo', hook ='',*args):
        rig_world.RigWorld.__init__(self)
        self.hook = hook
        self.nameHead = name
        self.nameNeck = 'neck'
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.shpRotIk = (0,45,0)
        self.typeScale = "pinSimple"


    def createHead(self):
        # FILTER BY TPL INFO_______________________________________
        #lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.nameHead])
        # CREATE RIG TO LISTE INFO_________________________________
        for i, eachTpl in enumerate([self.info]):
            # GET INFO TO CREATE HEAD________________________________
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
            lsTplIkHead =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]

            # CREATE__________________________________________________
            # NAME__________________________________________________
            nHook = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.nameHead, nSide=side, incP=incPart)
            nBuf = gloss.name_format(prefix=gloss.lexicon('buf'), name=self.nameHead, nSide=side, incP=incPart)
            # HOOK NECK_____________________________________________
            hookHead = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), match=lsTplIkHead[0],father=self.nRig)
            bufHead = libRig.createObj(partial(mc.group, **{'n': nBuf, 'em': True}), match=lsTplIkHead[0],father=hookHead)
            # NAME__________________________________________________
            nFkHead = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameHead,nSide=side,incP=incPart)
            nFkSkull = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('skull'),nSide=side,incP=incPart)
            # HOOK HEAD_____________________________________________
            ctrFkHead = libRig.createController(name=nFkHead,shape=libRig.Shp([self.typeSquare],color=valColorCtrIK,size=(1,1,1)),match=lsTplIkHead[0],father=bufHead)
            mc.setAttr(ctrFkHead["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdNeck",side=side)["rOrdFk"], l=False, k=True)
            ctrFkSkull = libRig.createController(name=nFkSkull,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)),match=lsTplIkHead[1],father=ctrFkHead["c"])
            mc.setAttr(ctrFkSkull["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdNeck",side=side)["rOrdFk"], l=False, k=True)
            # SNAP SHAPE TPL FK______________________________________
            lib_shapes.snapShpCv(shpRef=lsTplIkHead[0], shpTarget=ctrFkHead['c'])
            lib_shapes.snapShpCv(shpRef=lsTplIkHead[1], shpTarget=ctrFkSkull['c'])
            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            mc.sets(ctrFkSkull['sk'], edit=True, forceElement=nSetPart)
            mc.sets(ctrFkHead['sk'], edit=True, forceElement=nSetPart)

            # CREATE SCALE HEAD SYSTEM______________________________
            sclHead = libRig.connectScale(name=self.nameHead,shp=[self.typeScale,"sphere"],rotShp=(0,0,-90),sizeShp=(1,1,1),matchObj=ctrFkHead["c"],father=hookHead,child=bufHead)
            shp = mc.listRelatives(sclHead['c'], s=True)[1]
            recCv = mc.ls(shp + '.cv[*]', fl=True)
            sclW = mc.getAttr('tpl_WORLD' +'.scale')[0]
            mc.scale(0.2,0.2,0.2,recCv,os=True)

            # GET INFO TO CREATE NECK________________________________
            getInfoNeck= gloss.renameSplit(selObj=eachTpl, namePart=['head'], newNamePart=['neck'], reNme=False)
            if mc.objExists(getInfoNeck):
                incPartNeck = mc.getAttr(getInfoNeck+'.incInfo')
                lsTplIkNeck =[mc.getAttr(getInfoNeck+'.ik[%s]'%i) for i in range(mc.getAttr(getInfoNeck+'.ik', mi=True,s=True))]
                lsTplCtrNeck =[mc.getAttr(getInfoNeck+'.ctr[%s]'%i) for i in range(mc.getAttr(getInfoNeck+'.ctr', mi=True,s=True))]
                # FUSION TPL IK and CTR___________________________________
                concatIkFk = lsTplCtrNeck
                concatIkFk.insert(0, lsTplIkNeck[0])
                concatIkFk.insert(len(lsTplCtrNeck) + 1, lsTplIkNeck[-1])

                # HOOK NECK___________________________________

                nHook = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.nameNeck, nSide=side, incP=incPart)
                nBuf = gloss.name_format(prefix=gloss.lexicon('buf'), name=self.nameNeck, nSide=side, incP=incPart)
                hookNeck = nHook
                bufNeck = nBuf
                if not mc.objExists(nHook):
                    hookNeck = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), match=concatIkFk[0],father=self.nRig)
                if not mc.objExists(nBuf):
                    bufNeck = libRig.createObj(partial(mc.group, **{'n': nBuf, 'em': True}), match=concatIkFk[0],father=hookNeck)

                ############################################  FK NECK ######################################################
                lsFkNeck = []
                lsRootFkNeck = []
                lsSkFkNeck = []
                # CREATE__________________________________________________
                for i, each in enumerate(concatIkFk[:-1]):
                    valColor =valColorCtrIK
                    if i == 0:
                        nFkNeck = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameNeck,nFunc=gloss.lexicon('base'),nSide=side,incP=incPart)
                    elif i < (len(concatIkFk)-1):
                        nFkNeck = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameNeck+str(i),nSide=side,incP=incPart)
                        valColor =valColorCtr
                    ctrFkNeck = libRig.createController(name=nFkNeck,shape=libRig.Shp([self.typeCircle],color=valColor,size=(1,1,1)),match=each)
                    mc.setAttr(ctrFkNeck["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdNeck",side=side)["rOrdFk"], l=False, k=True)
                    # SNAP SHAPE TPL FK______________________________________
                    lib_shapes.snapShpCv(shpRef=each, shpTarget=ctrFkNeck['c'])
                    # ADD TO LIST____________________________________________
                    lsFkNeck.append(ctrFkNeck["c"])
                    lsRootFkNeck.append(ctrFkNeck["root"])
                    lsSkFkNeck.append(ctrFkNeck["sk"])
                mc.setAttr(lsRootFkNeck[1]+'.segmentScaleCompensate',0)
                # PARENT________________________________________________
                [mc.parent(lsRootFkNeck[i + 1], lsFkNeck[i]) for i, each in enumerate(lsRootFkNeck[1:])]
                mc.setAttr(lsRootFkNeck[0] + ".segmentScaleCompensate", 0)
                mc.parent(lsRootFkNeck[0],bufNeck)
                # CREATE JNT TO CONNECT HOOK HEAD_______________________
                nJntConnectHead = gloss.name_format(prefix=gloss.lexicon('jnt'),name=self.nameNeck+'End',nSide=side,incP=incPart)
                jntConnectHead = libRig.createObj(partial(mc.joint, **{'n': nJntConnectHead}), match=[concatIkFk[-1]], father=lsFkNeck[-1],
                attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})

                constTmp = mc.parentConstraint(hookHead,jntConnectHead)
                mc.delete(constTmp)
                mc.parentConstraint(jntConnectHead,hookHead)

                # SET SKIN_________________________________________
                mc.select(cl=True)
                nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),incP=incPart)
                if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
                for i, each in enumerate(lsSkFkNeck[::-1]):
                    mc.sets(each, edit=True, forceElement=nSetPart)

                # LIST HOOK IN TPL INFO_________________________________________
                lsHooks = lsSkFkNeck
                if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                    pass
                else:
                    mc.addAttr(getInfoNeck, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
                [mc.setAttr(getInfoNeck+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]
                # ATTRIBUTES TO CONTROL GRP________________________________________________
                lsFkCtr = lsFkNeck
                cgFkMb = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)
                if mc.objExists(eachTpl+'.%s'%cgFkMb):
                    pass
                else:
                    mc.addAttr(getInfoNeck, ln=cgFkMb,dt='string',multi=True) # add head fk
                [mc.setAttr(getInfoNeck+'.%s['%(cgFkMb) +str(i)+']',each,type='string') for i, each in enumerate(lsFkCtr)]

                # PARENT HOOK WITH RIG MEMBER________________________________________________
                mc.parent(hookNeck,self.hook)
                #print
                mc.parent(hookHead,lsFkNeck[-1])
            #else:
            #    print 'No Neck'

            # LIST HOOK IN TPL INFO_________________________________________
            lsHooks = [ctrFkHead["sk"],ctrFkSkull["sk"]]
            if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                pass
            else:
                mc.addAttr(eachTpl, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
            [mc.setAttr(eachTpl+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]

            # ATTRIBUTES TO CONTROL GRP________________________________________________
            lsFkCtr = [ctrFkHead["c"],ctrFkSkull["c"]]
            # NAME CG_____________________________________________
            cgFkMb = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)
            #cgSwitch = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgSwitch'),nSide=side,incP=incPart)
            if mc.objExists(eachTpl+'.%s'%cgFkMb):
                pass
            else:
                mc.addAttr(eachTpl, ln=cgFkMb,dt='string',multi=True) # add head fk
                #mc.addAttr(eachTpl, ln=cgSwitch,dt='string',multi=True) # add Cg switch
            #mc.setAttr(eachTpl+'.%s['%(cgSwitch) +str(i)+']',createSwitchs,type='string')
            [mc.setAttr(eachTpl+'.%s['%(cgFkMb)+str(i)+']',each,type='string') for i, each in enumerate(lsFkCtr)]
            # PARENT HOOK WITH RIG MEMBER________________________________________________
            mc.parent(hookHead,self.hook)





            '''
            # CREATE CURVE AND LOFT_______________________________________________
            # NAME _______________________________________________________________
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('SA'), name=self.nameNeck, nFunc=gloss.lexicon('sk'),nSide=side,incP=incPart)
            nDontTouchGrp = gloss.name_format('DontTouch', name=self.nameNeck, nFunc=gloss.lexicon('sk'),nSide=side,incP=incPart)
            nLoftNeckBase = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.nameNeck,nFunc=gloss.lexicon('base'),nSide=side,incP=incPart)
            nLoftNeckSk = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.nameNeck,nFunc=gloss.lexicon('sk'),nSide=side,incP=incPart)
            grpSANeck = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), Match=None,father=self.nSa)
            dontTouchGrp = libRig.createObj(partial(mc.group, **{'n': nDontTouchGrp, 'em': True}), Match=None,father=self.nSa)

            val = float(mc.getAttr(self.nWorld + '.scaleX'))
            getCrv = lib_curves.createDoubleCrv(objLst=lsFkNeck, axis='X', offset=0.2 * val)
            loftBase = lib_curves.createLoft(name=nLoftNeckBase, objLst=getCrv['crv'], father=None, deleteCrv=True
                                         , attributs={"visibility":0,"overrideEnabled":1,"overrideDisplayType":2})
            mc.skinCluster(lsSkFkNeck, loftBase, tsb=1, mi=1)

            # CONNECT TO LOFT_____________________________________________________
            adjustNumb = 1
            lSa = lib_connectNodes.surfAttach(selObj=[nLoftNeckBase], lNumb=((len(lsFkNeck)-1)*adjustNumb),parentInSA=True, parentSA=None,delKnot=True)
            # ADJUST SA POSITION__________________________________________________
            selDiv2 = int(math.ceil(float(len(lSa['loc']))/adjustNumb))
            val = 0
            dictPart ={}
            for each2 in range(selDiv2):
                part= []
                for each in range(adjustNumb):
                    part.append(lSa['loc'][each+val])
                val += adjustNumb
                dictPart[each2]= part

            for key, value in dictPart.items():
                for i, each in enumerate(value):
                    valDiv= 1/float((adjustNumb+1))
                    mc.setAttr(each+".U", key+(valDiv*(i+1)))
            # PARENT__________________________________________
            for i, each in enumerate(lSa['sa']):
                mc.parent(each,nSAGrp)
            # CONNECT SCALE___________________________________
            nodeMatrix = gloss.name_format(prefix=gloss.lexicon('dM'), name=self.nameNeck,nSide=side,incP=incPart)
            Matrix = mc.createNode("decomposeMatrix", n=nodeMatrix)
            mc.connectAttr(lsFkNeck[0] + ".worldMatrix[0]", (Matrix + ".inputMatrix"))
            mc.connectAttr(Matrix + ".outputScale", (nSAGrp + ".scale"))
            mc.connectAttr(Matrix + ".outputShear", (nSAGrp + ".shear"))
            # PARENT__________________________________________
            mc.parent(nLoftNeckBase,dontTouchGrp)
            # CREATE SK NECK__________________________________
            for i, each in enumerate(lSa['sa']):
                nSk = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.nameNeck, nFunc=gloss.lexicon('sk')+str(i),nSide=side,incP=incPart)
            '''




            '''
            [lib_curves.crvSubdivide(crv=each, name=None, subDiv=3,subDivKnot=None, degree=3) for each in getCrv['crv']]
            loft = lib_curves.createLoft(name=nLoftNeck, objLst=getCrv['crv'], father=None, deleteCrv=True
                                         , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
            #mc.skinCluster(lsFkNeck, loft, tsb=1, mi=1)
            selShape = mc.listRelatives(nLoftNeck, s=True)[0]
            mc.setAttr(selShape+".overrideEnabled", 1)

            loft = lib_curves.createLoft(name=nLoftNeck, objLst=getCrv['crv'], father=None, deleteCrv=True
                                         , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
            mc.skinCluster(lsFkNeck, loft, tsb=1, mi=1)
            mc.setAttr(nLoftNeck+".overrideShading", 0)
            '''
