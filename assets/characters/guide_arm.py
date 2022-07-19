
import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_attributes
from ellipse_rig.assets.characters import guide_member

reload(lib_attributes)
reload(guide_member)

class Arm(guide_member.Member):
    def __init__(self,name='arm',side='',selObj=None,numb=1,numbSk=1,numbMidMb=2,numbEndMb=5,subDvEndMb=3,numbPlV=1,
                 offsetIk=(0,-3,0),shpRotIk=(0,-90,90),offsetStartT=(0,8,0),offsetT=(0,6.5,0),offsetR=(0,0,0),sizeCtr=(1,1,1),sizeSk=(0.7,0.7,0.7),typeBox="sphere", incVal=None, **kwargs):
        guide_member.Member.__init__(self, name=name, side=side, selObj=selObj, numb=numb, numbSk=numbSk,
                                     numbMidMb=numbMidMb,numbEndMb=numbEndMb,subDvEndMb=subDvEndMb,
                                     sizeCtr=sizeCtr,sizeSk=sizeSk,typeBox=typeBox, incVal=incVal)
        self.incVal = incVal
        # start member________________________
        self.nStartMb = 'clav'
        self.sizeMastStartMb = (0.4,0.4,0.4)
        self.sizeStartMbIk = (0.3,0.3,0.3)
        self.sizeCtrStartMb = (0.3,0.3,0.3)
        #  member_____________________________
        self.name = name
        self.offsetIk = offsetIk
        self.posPlV = (0,0,-3)
        self.numbPlV = numbPlV
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR
        self.shpRotIk = shpRotIk
        self.shpRotCtr = (0,90,0)
        self.nMidMb = 'hand'
        self.sizeMastMidMb = (0.75,0.75,0.75)
        self.sizeCtrMidMb = (0.6,0.6,0.3)
        # mid member________________________
        self.numbMidMb = numbMidMb+1
        self.sizeBank = (0.1,0.1,0.1)
        self.offsetMidMbCtr = (0,-0.8,0)
        # end member________________________
        self.nEndMb = 'fingers'
        self.numbEndMb = numbEndMb
        self.numbSubDvEndMb = subDvEndMb
        self.sizeMastToes = (0.3,1,0.2)
        self.sizeCtrToes = (0.1,1,0.15)
        self.offsetEndMbTr = (0,-0.3,0)

        # partie a inserer pour module jambe
        '''
        if side is '':
            self.offsetMasterTr = offsetT
            self.offsetMasterRo = offsetR
        elif side is 'L':
            self.offsetMasterTr = (offsetT[0]+1,offsetT[1],offsetT[2])
            self.offsetMasterRo = offsetR
        elif side is 'R':
            self.offsetMasterTr = (offsetT[0]-1,offsetT[1],offsetT[2])
            self.offsetMasterRo = offsetR
        '''

    def createArm(self):
        rigGuide = guide_member.Member(nStartMb=self.nStartMb,name=self.name,nMidMb=self.nMidMb,nEndMb=self.nEndMb, side=self.side,
                   selObj=self.selObj,numb=self.numb,numbMidMb=self.numbMidMb,numbEndMb=self.numbEndMb,subDvEndMb=self.numbSubDvEndMb,numbPlV=self.numbPlV,
                   numbSk=self.numbSk,shpRotIk=self.shpRotIk,shpRotCtr=self.shpRotCtr,offsetT=self.offsetMasterTr,offsetR=self.offsetMasterRo,
                   offsetMidMbCtr = self.offsetMidMbCtr,offsetEndMbTr=self.offsetEndMbTr,posPlV =self.posPlV,sizeMast=self.sizeMast,sizeIk=self.sizeIk,
                   sizeCtr=self.sizeCtr,sizeSk=self.sizeSk,typeBox=self.typeSk,typeShp=self.typeShape, incVal=self.incVal)  # instance class CharGuide

        dic = rigGuide.createEndMember()  # run method createRig
        # ADJUST CONSTRAINT HOOK MASTER MID MEMBER_______________________
        getHook = mc.pickWalk(mc.getAttr(dic['%sMaster'%self.nMidMb] + '.root'), direction='up')
        lib_attributes.disconnectAll(getHook, source=True, destination=True)
        mc.parentConstraint(dic['lsIk'][-1],getHook)
        mc.scaleConstraint(dic['lsIk'][-1],getHook)
        mc.setAttr(mc.getAttr(dic['%sMaster'%self.nMidMb]+'.root')+".translateY", 0)
        mc.setAttr(mc.listRelatives(dic['%sMaster'%self.nMidMb], s=True)[0] + ".visibility", 0)
        #mc.setAttr(mc.listRelatives(dic['%sMaster'%self.nMidMb], s=True)[1] + ".visibility", 0)
        # DICTIONARY RETURN_________________________________________________________
        mc.select(cl=True)
        return dic