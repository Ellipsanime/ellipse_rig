
import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_baseRig)
reload(guide_world)
reload(guide_base)


rigGuide = guide_base.CharGuide()  # instance class charGuide and run method createRig

class Tail(guide_base.CharGuide):

    def __init__(self,name='tail',side='',selObj=None,numb=1,numbSk=1,offsetIk=(0,8,0),offsetT=(0,6.5,0),offsetR=(-90,0,0),**kwargs):
        guide_base.CharGuide.__init__(self, name=name, side=side, selObj=selObj, numb=numb, numbSk=numbSk)
        self.name = name
        self.offsetIk = offsetIk
        self.sizeMast = (0.7,0.1,0.7)
        self.sizeIk = (0.5,0.5,0.5)
        self.sizeCtr = (0.5,0.5,0.5)
        self.sizeSk = (0.3,0.3,0.3)
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR
        self.typeShapeMast = 'cube'

    def createTail(self):
        rigGuide = guide_base.CharGuide(name=self.name, side=self.side, selObj=self.selObj, numb=self.numb, numbSk=self.numbSk,
                                        offsetIk=self.offsetIk, shpRotIk=self.shpRotIk,
                                        sizeMast=self.sizeMast, sizeIk=self.sizeIk,shpRotCTR=self.shpRotCtr,
                                        sizeCtr=self.sizeCtr,sizeSk=self.sizeSk, typeBox=self.typeSk,
                                        typeShp=self.typeShape, typeShpMst=self.typeShapeMast)  # instance class CharGuide
        dic = rigGuide.templateSk()  # run method createRig
        # OFFSET ROOT MASTER SPINE__________________________________________
        if self.selObj != []: # check if objRef is empty
            pass
        else:
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(self.offsetMasterTr[0]*val,self.offsetMasterTr[1]*val,self.offsetMasterTr[2]*val,mc.getAttr(dic['master']+'.root'))
            mc.rotate(self.offsetMasterRo[0],self.offsetMasterRo[1],self.offsetMasterRo[2],mc.getAttr(dic['master']+'.root'))
            # OFFSET FLY____________________________________________________
            mc.move(self.offsetMasterTr[0]*val, self.offsetMasterTr[1]*val, self.offsetMasterTr[2]*val,self.nFlyGrp)
        return dic