# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(libRig)
reload(guide_base)

rigInfo = guide_base.Info()
rigGuide = guide_base.CharGuide()  # instance class charGuide and run method createRig

class Head(guide_base.CharGuide,guide_base.Info):

    def __init__(self, name='head', side='', selObj=None, numbNeck=None, numbSk=3, offsetIk=(0,1,0), offsetT=(0,11,0), offsetR=(0,0,0), incVal=None, **kwargs):
        guide_base.CharGuide.__init__(self, name=name, side=side, selObj=selObj, numb=numbNeck, numbSk=numbSk, incVal=incVal)
        self.selObj = selObj
        self.obj = mc.ls(sl=True)
        self.name = name
        self.numbHead = 1
        self.numbSkHead = 1
        self.typeSk = "sphere"
        self.offsetIk = (0,2,0)
        self.sizeMast = (1.8,1.8,1.8)
        self.sizeIk = (1.2,1.2,1.2)
        self.sizeCtr = (1,1,1)
        self.sizeSk = (1.5,1.5,1.5)
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR

        self.nameNeck ='neck'
        self.numbNeck = numbNeck
        self.numbSkNeck = numbSk
        self.offsetIkNeck = offsetIk
        self.sizeMastNeck = (0.6,0.6,0.6)
        self.sizeIkNeck = (0.4,0.4,0.4)
        self.sizeCtrNeck = (0.3,0.3,0.3)
        self.sizeSkNeck = (0.5,0.5,0.5)
        self.offsetMasterTrNeck = offsetT
        self.offsetMasterRoNeck = offsetR
        self.incVal = incVal


    def createNeck(self):
        # TEMPLATE NECK________________________________________________________
        rigGuide = guide_base.CharGuide(name=self.nameNeck, side=self.side, selObj=self.selObj, numb=self.numbNeck, numbSk=self.numbSkNeck,
                                        offsetIk=self.offsetIkNeck, shpRotIk=self.shpRotIk, sizeMast=self.sizeMastNeck, sizeIk=self.sizeIkNeck, shpRotCTR=self.shpRotCtr,
                                        sizeCtr=self.sizeCtrNeck,sizeSk=self.sizeSkNeck, typeBox=self.typeSk, typeShp=self.typeShape, incVal=self.incVal)  # instance class CharGuide
        dic = rigGuide.templateSk()  # run method createRig
        # CREATE NECK________________________________________________________
        if self.selObj != []: # check if objRef is empty
            pass
        else:
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(self.offsetMasterTrNeck[0]*val,self.offsetMasterTrNeck[1]*val,self.offsetMasterTrNeck[2]*val,mc.getAttr(dic['master']+'.root'))
            mc.rotate(self.offsetMasterRoNeck[0],self.offsetMasterRoNeck[1],self.offsetMasterRoNeck[2],mc.getAttr(dic['master']+'.root'))
        # DICTIONARY RETURN_________________________________________________________
        mc.select(cl=True)
        return dic


    def createHead(self):
        # TEMPLATE HEAD_______________________________________________________
        rigInfo = guide_base.Info(name=self.name, side='', incVal=self.incVal)
        dic = rigInfo.infoInc()

        # GET PARENT HOOK ELEMENT__________________________________________________________
        #print 'createHead', self.obj[0], dic
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('attrChild'), dic['infoName'] + ".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0] + '.infPart') + ".%s"%gloss.lexiconAttr('attrChild'), dic['infoName'] + ".%s"%gloss.lexiconAttr('attrParent'), f=True)

        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=dic['incVal'])
        nIkHead = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nSide=self.side,incP=dic['incVal'])
        nIkSkull = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=gloss.lexicon('skull'),nSide=self.side,incP=dic['incVal'])
        # CREATE HEAD_________________________________________________________
        RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
        hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)

        master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast],color=self.valColorMasterCtr,
                size=self.sizeMast),match=self.selObj,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
        mc.setAttr(master['c']+'.segmentScaleCompensate',0)

        # PARENT INFO AND TPL RIG_________________________________________
        mc.parent(dic['infoName'],nRIG)
        mc.parent(nRIG,self.nWorldGrp)
        mc.parent(master['root'],nHookMaster)
        # CREATE IK________________________________________________________
        lsIk =[]
        headCtr = libRig.createController(name=nIkHead, shape=libRig.Shp([self.typeShapeIk],color=self.valColorCtrIK,size=self.sizeIk,rotShp=self.shpRotIk),
                match=self.selObj,father=master['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)
        skullCtr = libRig.createController(name=nIkSkull, shape=libRig.Shp([self.typeShape],color=self.valColorCtrIK,size=self.sizeIk,rotShp=self.shpRotIk),
                match=self.selObj,father=headCtr['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)
        lsIk.append(headCtr['c'])
        lsIk.append(skullCtr['c'])
        # OFFSET IK____________________________________________________
        val = mc.getAttr(self.nWorld+ '.scale')[0][0]*1
        mc.move(self.offsetIk[0]*val,self.offsetIk[1]*val,self.offsetIk[2]*val,skullCtr['root'],os=True)
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='delPart',dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+'.delPart[0]',nRIG,type='string')
        mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
        mc.addAttr(dic['infoName'], ln='sizeSk', at="enum", en="%s:%s:%s:%s:%s:%s"%(self.sizeCtr,self.sizeSk,self.typeSk,
                                    self.offsetIk,self.numb,self.numbSk), k=True, p='infoSK')
        mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)
        mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')),dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('masterTpl'),nMaster,type='string')
        mc.addAttr(dic['infoName'], ln='ik',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.ik['+str(i)+']',each,type='string') for i, each in enumerate(lsIk)]

        if self.numbNeck == None or self.numbNeck == 0:
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(0,12*val,0,master['root'])
            pass
        else:
            dicNeck = Head.createNeck(self)  # run method createRig
            # CREATE HEAD________________________________________________________
            mc.parentConstraint(dicNeck['lsIk'][-1],master['root'])
            mc.scaleConstraint(dicNeck['lsIk'][-1],master['root'])
            [mc.setAttr(each+".visibility",0)for each in (mc.listRelatives(master['c'], s=True))]
            [mc.setAttr(each+".visibility",0)for each in (mc.listRelatives(headCtr['c'], s=True))]
            # ADJUST SIZE LAST IK NECK_________________________________________________
            selShape = mc.listRelatives(dicNeck['lsIk'][-1], s=True)[0]
            recCv = mc.ls(selShape + '.cv[*]', fl=True)
            scaleWX= mc.getAttr(self.nWorld+".scaleX")
            mc.scale(scaleWX*2,scaleWX*2,scaleWX*2, recCv, os=True)
            # ADD ATTRIBUTES NECK ON TEMPLATE INFO _____________________________________
            mc.setAttr(dic['infoName'] + ".%s[1]"%gloss.lexiconAttr('masterTpl'),dicNeck['master'], type="string")
            mc.addAttr(dic['infoName'], ln='infoNeck',dt='string',multi=True) # add master control
            mc.setAttr(dic['infoName']+'.infoNeck[0]',dicNeck['infoName'],type='string')
            mc.connectAttr(dicNeck['infoName'] + ".%s" % gloss.lexiconAttr('attrChild'), dic['infoName'] + ".%s" % gloss.lexiconAttr('attrParent'), f=True)

        '''
        rigGuide = guide_base.CharGuide(name=self.name, side=self.side, selObj=self.selObj, numb=self.numbHead, numbSk=self.numbSkHead,
                                        offsetIk=self.offsetIk, shpRotIk=self.shpRotIk, sizeMast=self.sizeMast, sizeIk=self.sizeIk,shpRotCTR=self.shpRotCtr,
                                        sizeCtr=self.sizeCtr,sizeSk=self.sizeSk, typeBox=self.typeSk, typeShp=self.typeShape)  # instance class CharGuide
        dicHead = rigGuide.templateSk()  # run method createRig
        if self.numbNeck == None or self.numbNeck == 0:
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(0,12*val,0,mc.getAttr(dicHead['master']+'.root'))
            pass
        else:
            dicNeck = Head.createNeck(self)  # run method createRig
            # CREATE HEAD________________________________________________________
            mc.parentConstraint(dicNeck['lsIk'][-1],mc.getAttr(dicHead['master']+".root"))
            mc.scaleConstraint(dicNeck['lsIk'][-1],mc.getAttr(dicHead['master']+".root"))
            [mc.setAttr(each+".visibility",0)for each in (mc.listRelatives(dicHead['master'], s=True))]
            [mc.setAttr(each+".visibility",0)for each in (mc.listRelatives(dicHead['lsIk'][0], s=True))]
            # ADJUST SIZE LAST IK NECK_________________________________________________
            selShape = mc.listRelatives(dicNeck['lsIk'][-1], s=True)[0]
            recCv = mc.ls(selShape + '.cv[*]', fl=True)
            scaleWX= mc.getAttr(self.nWorld+".scaleX")
            mc.scale(scaleWX*2,scaleWX*2,scaleWX*2, recCv, os=True)
            # ADD ATTRIBUTES NECK ON TEMPLATE INFO _____________________________________
            mc.addAttr(dicHead['infoName'], ln='infoNeck',dt='string',multi=True) # add master control
            mc.setAttr(dicHead['infoName']+'.infoNeck[0]',dicNeck['infoName'],type='string')
        '''


        '''
        mc.addAttr(dicHead['infoName'], ln='masterNeck',dt='string',multi=True) # add master control
        mc.setAttr(dicHead['infoName']+'.masterNeck[0]',dicNeck['master'],type='string')
        mc.addAttr(dicHead['infoName'], ln='ikNeck',dt='string',multi=True) # add IK control
        [mc.setAttr(dicHead['infoName']+'.ikNeck['+str(i)+']',each,type='string') for i, each in enumerate(dicNeck['lsIk'])]
        mc.addAttr(dicHead['infoName'], ln='ctrNeck',dt='string',multi=True) # add IK control
        [mc.setAttr(dicHead['infoName']+'.ctrNeck['+str(i)+']',each,type='string') for i, each in enumerate(dicNeck['lsCtr'])]
        '''