# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.assets.characters import guide_base
reload(guide_base)


rigGuide = guide_base.CharGuide()  # instance class charGuide and run method createRig

class Spine(guide_base.CharGuide):

    def __init__(self,name='spine',side='',selObj=None,numb=1,numbSk=1,offsetIk=(0,4,0),offsetT=(0,6.5,0),offsetR=(0,0,0), incVal=None, **kwargs):
        guide_base.CharGuide.__init__(self, name=name, side=side, selObj=selObj, numb=numb, numbSk=numbSk, incVal=incVal)
        self.name = name
        self.offsetIk = offsetIk
        self.sizeMast = (1.7,0.3,1.7)
        self.sizeIk = (1.2,1.2,1.2)
        self.sizeCtr = (1,1,1)
        self.sizeSk = (1.2,1.2,1.2)
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR
        self.typeShapeMast = 'cube'
        self.incVal = incVal

    def createSpine(self):
        rigGuide = guide_base.CharGuide(name=self.name, side=self.side, selObj=self.selObj, numb=self.numb, numbSk=self.numbSk,
                                        offsetIk=self.offsetIk, shpRotIk=self.shpRotIk,
                                        sizeMast=self.sizeMast, sizeIk=self.sizeIk,shpRotCTR=self.shpRotCtr,
                                        sizeCtr=self.sizeCtr,sizeSk=self.sizeSk, typeBox=self.typeSk,
                                        typeShp=self.typeShape, typeShpMst=self.typeShapeMast, incVal=self.incVal)  # instance class CharGuide
        dic = rigGuide.templateSk()  # run method createRig

        # OFFSET ROOT MASTER SPINE__________________________________________
        if self.selObj != []: # check if objRef is empty
            pass
        else:
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(self.offsetMasterTr[0]*val,self.offsetMasterTr[1]*val,self.offsetMasterTr[2]*val,mc.getAttr(dic['master']+'.root'))
            mc.rotate(self.offsetMasterRo[0],self.offsetMasterRo[1],self.offsetMasterRo[2],mc.getAttr(dic['master']+'.root'))
            # OFFSET FLY____________________________________________________
            #to debbug, offest all the tpl when no father are selected
            #mc.move(self.offsetMasterTr[0]*val, self.offsetMasterTr[1]*val, self.offsetMasterTr[2]*val,self.nFlyGrp)

        return dic

