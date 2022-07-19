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

class Neck(rig_world.RigWorld):


    def __init__(self, name='neck', tplInfo='tplInfo', hook ='',*args):
        rig_world.RigWorld.__init__(self)
        self.hook = hook
        self.nameHead = name
        self.nameNeck = 'neck'
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.shpRotIk = (0,45,0)
        self.typeScale = "pinSimple"


    def createNeck(self):
        # FILTER BY TPL INFO_______________________________________
        #lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.nameHead])
        # CREATE RIG TO LISTE INFO_________________________________
        print 'BEGINS NECK'
        for i, eachTpl in enumerate([self.info]):
            print 'HERE :', eachTpl
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
            lsTplCtrNeck =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]

            # GET INFO TO CREATE NECK________________________________
            getInfoNeck= gloss.renameSplit(selObj=eachTpl, namePart=['head'], newNamePart=['neck'], reNme=False)

            # FUSION TPL IK and CTR___________________________________
            concatIkFk = lsTplCtrNeck
            concatIkFk.insert(0, lsTplIkHead[0])
            concatIkFk.insert(len(lsTplCtrNeck) + 1, lsTplIkHead[-1])
            print 'ici'
            # HOOK NECK___________________________________
            nHook = gloss.name_format(prefix=gloss.lexicon('rig'), name=self.nameNeck, nSide=side, incP=incPart)
            nBuf = gloss.name_format(prefix=gloss.lexicon('buf'), name=self.nameNeck, nSide=side, incP=incPart)
            hookNeck = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), match=concatIkFk[0],father=self.nRig)
            bufNeck = libRig.createObj(partial(mc.group, **{'n': nBuf, 'em': True}), match=concatIkFk[0],father=hookNeck)
            ############################################  FK NECK ######################################################
            lsFkNeck = []
            lsRootFkNeck = []
            lsSkFkNeck = []
            # CREATE__________________________________________________
            for i, each in enumerate(concatIkFk[:-1]):
                valColor =valColorCtrIK
                nFkNeck = gloss.name_format(prefix=gloss.lexicon('c'),name=self.nameNeck,nFunc=gloss.lexicon('base'),nSide=side,incP=incPart)
                if i < (len(concatIkFk)-1):
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


