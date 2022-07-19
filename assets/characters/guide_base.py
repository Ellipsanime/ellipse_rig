# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves, lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.assets.asset_base import guide_world

reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(guide_world)

guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig


class Info(guide_world.GuideWorld):

    def __init__(self, name='default', side='', selObj=None, incVal=None, **kwargs):
        guide_world.GuideWorld.__init__(self, selObj=selObj)
        self.selObj = selObj
        self.name = name
        self.side = side
        self.rotShape = [0,0,0]
        ## Juline : add incVal info
        self.incVal = incVal
        if self.incVal:
            self.incInfo = None
        else:
            self.incInfo = True
        ##

    def infoInc(self, incVal=None):
        # TEMPLATE INFO INCREMENTATION________________________________________
        dic = {}
        # NAME________________________________________________________________
        nInfo = gloss.name_format(prefix=gloss.lexicon('tplInfo'),name=self.name, nSide=self.side, incInfo=True, forceInc=self.incVal)
        # CREATE INFO_________________________________________________________
        libRig.createObj(partial(mc.group, **{'n': nInfo, 'em': True}), father=self.nWorld, refObj=self.selObj)
        ## Juline : add incVal info
        if not incVal:
            if self.incVal:
                incVal = self.incVal
            else:
                incVal = gloss.get_inc(selObj=nInfo, slideSplit=2)
        ##
        # CREATE ATTRIBUTES INFO INCREMENTATION AND UPDATE OR DEL ____________
        #mc.addAttr(nInfo, longName='infoBase', numberOfChildren=4, attributeType='compound')
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleDataTpl'), at="bool", dv=1)
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleDataTpl'), e=True, k=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleType'), dt="string")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleType'), self.name, type="string")
        ## Juline : Add attr info side
        mc.addAttr(nInfo, longName='side', dataType="string")
        if self.side:
            mc.setAttr(nInfo + '.side', self.side, type="string")
        else:
            mc.setAttr(nInfo + '.side', 'None', type="string")
        ##
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('attrParent'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('attrParent'), e=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('attrChild'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('attrChild'), e=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleMirror'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleMirror'), e=True)

        mc.addAttr(nInfo, ln=gloss.lexiconAttr('buildCg'), at="bool", dv=1)
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('buildCg'), e=True, k=True)

        mc.addAttr(nInfo, ln='incInfo', dt="string")
        mc.addAttr(nInfo, ln='infPart', dt="string")
        mc.addAttr(nInfo, ln='updateSk', dt="string")
        val = str(self.side)
        if self.side == '': val = 'empty'
        mc.addAttr(nInfo, ln='update', at="enum", en="%s:%s" % (self.name, val), k=True)
        mc.setAttr(nInfo + '.incInfo', incVal, type="string")
        mc.setAttr(nInfo + '.infPart', nInfo, type="string")
        mc.setAttr(nInfo + '.updateSk', 'partToDel', type="string")
        mc.setAttr(nInfo + '.update', e=True, cb=True)
        if self.side is not'':
            mc.addAttr(nInfo, ln='sym',dt='string',multi=True) # add master control
            mc.setAttr(nInfo+'.sym[0]',nInfo,type='string')
        dic['infoName'] = nInfo
        dic['incVal'] = incVal
        return dic


class CharGuide(Info):

    def __init__(self,name='default',side='',selObj=None,obj=mc.ls(sl=True),numb=1,numbSk=1,offsetIk=(0,4,0),shpRotIk=(0,0,0)
                 ,sizeMast=(2,2,2),sizeIk=(1.2,1.2,1.2),shpRotMaster=(0,0,0),shpRotCtr=(0,0,0),sizeCtr=(1,1,1),sizeSk=(0.7,0.7,0.7),
                 typeBox="cube",typeShpMst="circle",typeShpIk="square",typeShp="circle", incVal=None,degree=None, **kwargs):
        Info.__init__(self,name=name,side=side,selObj=selObj, incVal=incVal)
        self.selObj = selObj
        self.obj = obj
        self.numb = numb
        self.numbSk = numbSk
        self.offsetIk = offsetIk
        self.typeShapeMast = typeShpMst
        self.typeShapeIk = typeShpIk
        self.typeShape = typeShp
        color = lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.sizeMast = sizeMast
        self.sizeIk = sizeIk
        self.sizeCtr = sizeCtr
        self.sizeSk = sizeSk
        self.typeSk = typeBox
        self.shpRotMaster = shpRotMaster
        self.shpRotIk = shpRotIk
        self.shpRotCtr = shpRotCtr
        self.numbIk = 2
        self.incVal = incVal ## Juline
        self.degree = degree

    def templateIk(self):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = Info.infoInc(self, self.incVal)
        print dic
        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=dic['incVal'])
        nLsIk = [gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nFunc='Ik',inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]
        nLsIkSk = [gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.name,nFunc='Ik',inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]

        # GET PARENT HOOK ELEMENT__________________________________________________________
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly +".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0]+'.infPart')+".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)

        # CREATE IK___________________________________________________________
        if mc.objExists(nRIG) is True:
            mc.parent(dic['infoName'], nRIG)
        else:
            RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
            surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
            hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
            master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast],color=self.valColorMasterCtr,
                    size=self.sizeMast,rotShp=self.shpRotMaster),match=self.selObj,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
            # CREATE IK________________________________________________________
            for knot in range(self.numbIk):
                if knot == 0  and self.name =='arm':
                    shpForm = 'circle'
                elif knot == 0  and self.name =='leg':
                    shpForm = 'circle'
                else:
                    shpForm = self.typeShapeIk
                ikCtr = libRig.createController(name=nLsIk[knot], shape=libRig.Shp([shpForm],color=self.valColorCtrIK,size=self.sizeIk,rotShp=self.shpRotIk),
                        match=self.selObj,father=master['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)
                # OFFSET IK____________________________________________________
                val = mc.getAttr(self.nWorld+ '.scale')[0][0]*knot
                mc.move(self.offsetIk[0]*val,self.offsetIk[1]*val,self.offsetIk[2]*val,ikCtr['root'],os=True)
                # ROOT SEGMENT SCALE COMPENSATE________________________________
                mc.setAttr(ikCtr['root']+'.segmentScaleCompensate',0)
                # DISCONNECT ATTRIBUTES CONNECTION______________________________
                connectPairs = []
                connect = mc.listConnections(mc.getAttr(ikCtr['c'] + ".sk"), plugs=True, connections=True, destination=False)
                connectPairs.extend(zip(connect[1::2], connect[::2]))
                [mc.disconnectAttr(srcAttr, desAttr) for srcAttr, desAttr in connectPairs]
                mc.parent(ikCtr['sk'],ikCtr['c'])
            # CREATE CURVE AND LOFT___________________________________________
            getCrv = lib_curves.createDoubleCrv(objLst=nLsIkSk, axis='Z', offset=0.2)
            loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True,degree=None)
            mc.skinCluster(nLsIkSk,loft,tsb=1,mi=1)
            # PARENT INFO AND TPL RIG_________________________________________
            mc.parent(dic['infoName'],nRIG)
            mc.parent(nRIG,self.nWorldGrp)
            # CONNECT TO WORLD________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=self.nWorld, slave=hookMaster)
            # PARENT__________________________________________________________
            mc.parent(master['root'],nHookMaster)
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='delPart',dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+'.delPart[0]',nRIG,type='string')
        mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
        mc.addAttr(dic['infoName'], ln='sizeSk', at="enum", en="%s:%s:%s:%s:%s:%s"%(self.sizeCtr,self.sizeSk,self.typeSk,
                                    self.offsetIk,self.numb,self.numbSk), k=True, p='infoSK')
        mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)

        #for i, each in enumerate(nLsCtrSk):
        #    mc.addAttr(dic['infoName'], ln='sk['+str(i)+']', type='string')
        #    mc.setAttr(dic['infoName'] + '.sk[' + str(i) + ']', each, type='string')
        #    mc.connectAttr(each + '.message', dic['infoName'] + '.sk[' + str(i) + ']')

        mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')),dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('masterTpl'),nMaster,type='string')
        mc.addAttr(dic['infoName'], ln='ik',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.ik['+str(i)+']',each,type='string') for i, each in enumerate(nLsIk)]
        # add ik in sym attributes
        if self.side is not'':
            #nSym = lib_attributes.attrSymetrie(selObj=nMaster, nameInfo=dic['infoName'])
            mc.setAttr(dic['infoName']+'.sym['+str(1)+']',nMaster,type='string')
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(nLsIk)]
        # ADD DICTIONARY ______________________________________________________
        dic['loft'] = nLoft
        dic['srfAttach'] = nSurfAttach
        dic['master'] = nMaster
        dic['lsIk'] = nLsIk
        dic['lsIkSk'] = nLsIkSk
        mc.select(cl=True)
        return dic


    def templateCtr(self):
        '''
        :return:
        '''
        # TEMPLATE IK_________________________________________________________
        dic = CharGuide.templateIk(self)
        # NAME _______________________________________________________________
        nSAWorldGrp = gloss.name_format(prefix=gloss.lexicon('tplSA') + 'World', name=self.name, nSide=self.side,incP=dic['incVal'])
        nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nSide=self.side, incP=dic['incVal'])
        nLsCtr = [gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numb)]
        nLsCtrSk = [gloss.name_format(prefix=gloss.lexicon('tplSk'), name=self.name, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numb)]
        # CREATE CTR__________________________________________________________
        if mc.objExists(nSAWorldGrp) is True:
            pass
        else:
            # CREATE GRP SA___________________________________________________
            SAWorld = libRig.createObj(partial(mc.group, **{'n': nSAWorldGrp, 'em': True}), father=dic['srfAttach'], attrInfo=dic['infoName'],refObj=self.selObj)
            SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), father=SAWorld, refObj=self.selObj)
            if mc.attributeQuery("tplSAWorld", node=dic['master'], ex=True) is True:
                pass
            else:
                mc.addAttr(dic['master'], ln='tplSAWorld', dt="string")
                mc.setAttr(dic['master'] + '.tplSAWorld', nSAWorldGrp, type="string")
                mc.addAttr(dic['master'], ln='tplSA', dt="string")
                mc.setAttr(dic['master'] + '.tplSA', nSAGrp, type="string")
            # CREATE ATTRIBUTES UPDATE TO SA WORLD____________________________
            lib_attributes.attrUpdateCtr(selObj=nSAWorldGrp, name=self.name, side=self.side)
            # CONNECT TO LOFT_________________________________________________
            lSa = lib_connectNodes.surfAttach(selObj=[dic['loft']], lNumb=self.numb, parentInSA=True, parentSA=nSAGrp,delKnot=True)
            # CREATE CTR______________________________________________________
            for val in range(self.numb):
                ctr = libRig.createController(name=nLsCtr[val],shape=libRig.Shp([self.typeShape], color=self.valColorCtr,
                     size=self.sizeCtr,rotShp=self.shpRotCtr),match=lSa['sa'][val], attrInfo=dic['infoName'], father=lSa['sa'][val],worldScale=self.nWorld)
                mc.setAttr(ctr['root'] + '.rotateZ', -90)  # adjust orientation
                mc.setAttr(ctr['root'] + '.rotateY', 180)  # adjust orientation
                if self.name == 'arm':
                    mc.setAttr(ctr['root'] + '.rotateY', 0)  # adjust orientation

            # CONNECT TO MASTER CONTROL_______________________________________
            lib_connectNodes.connectMatrixAxis(driver=dic['master'], slave=SA)
        # FUSION SK: IK and CTR_______________________________________________
        nConcatSk = nLsCtrSk
        nConcatSk.insert(0, dic['lsIkSk'][0])
        nConcatSk.insert(len(nLsCtrSk) + 1, dic['lsIkSk'][-1])
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], shortName='ctr',dt='string',multi=True)

        for i, each in enumerate(nLsCtr):
            mc.setAttr(dic['infoName']+'.ctr['+str(i)+']', each, type='string')
            #mc.connectAttr(each + '.message', dic['infoName']+'.ctr['+str(i)+']')

        #mc.addAttr(dic['infoName'], shortName='sk', dt='string', multi=True)
        #for i, each in enumerate(nLsCtrSk):
        #    mc.setAttr(dic['infoName'] + '.sk[' + str(i) + ']', each, type='string')

        #getnLsCtr =[mc.getAttr(dic['infoName']+'.ctr[%s]'%i) for i in range(mc.getAttr(dic['infoName']+'.ctr', mi=True,s=True))]
        # add ik in sym attributes
        if self.side is not'':
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(nLsCtr)]
        # ADD DICTIONARY ______________________________________________________
        dic['lsCtr'] = nLsCtr
        dic['concatSk'] = nConcatSk
        dic['grpSA'] = nSAGrp
        dic['grpWorldSA'] = nSAWorldGrp
        mc.select(cl=True)
        return dic

    def templateSk(self,active=False):
        '''
        :return:
        '''
        # TEMPLATE CTR________________________________________________________
        dic = CharGuide.templateCtr(self)
        # NAME _______________________________________________________________
        nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nFunc=gloss.lexicon('sk'),nSide=self.side,incP=dic['incVal'])
        nLoft2 = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name, nFunc=gloss.lexicon('sk'),nSide=self.side,incP=dic['incVal'])
        nLsBox = [gloss.name_format(prefix='box', name=self.name, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numbSk)]
        # CREATE GRP SA_______________________________________________________
        SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}),father=None,attrInfo=dic['infoName'],refObj=self.selObj)
        # CREATE ATTRIBUTES UPDATE TO SA _____________________________________
        mc.addAttr(nSAGrp, ln='updateSk', dt="string")
        mc.setAttr(nSAGrp + '.updateSk', 'partToDel', type="string")
        # CREATE CURVE AND LOFT_______________________________________________
        val = float(mc.getAttr(self.nWorld + '.scaleX'))
        getCrv = lib_curves.createDoubleCrv(objLst=dic['concatSk'], axis='Z', offset=0.2 * val)
        loft = lib_curves.createLoft(name=nLoft2, objLst=getCrv['crv'], father=None, deleteCrv=True,degree=self.degree
                                     , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
        mc.skinCluster(dic['concatSk'], loft, tsb=1, mi=1)
        mc.setAttr(nLoft2+".overrideShading", 0)
        # CREATE ATTRIBUTES UPDATE TO LOFT _____________________________________
        mc.addAttr(nLoft2, ln='infPart', dt="string")
        mc.setAttr(nLoft2 + '.infPart', dic['infoName'], type="string")
        mc.addAttr(nLoft2, ln='updateSk', dt="string")
        mc.setAttr(nLoft2+ '.updateSk', 'partToDel', type="string")
        # CONNECT TO LOFT_____________________________________________________
        lSa = lib_connectNodes.surfAttach(selObj=[nLoft2], lNumb=self.numbSk,parentInSA=True, parentSA=nSAGrp,delKnot=True)
        if self.degree == 1:
            for i, each in enumerate(lSa['loc']):
                mc.setAttr(each +'.U',(0.5+i))
        # CREATE SK___________________________________________________________
        lsSk = []
        for val in range(self.numbSk):
            scaleWX= float(mc.getAttr(self.nWorld+".scaleX"))
            scaleSk = (float(abs(self.offsetIk[1]))/self.numbSk)*1
            # ADJUST TYPE BOX_________________________________________________
            if self.typeSk == "cube":
                ctr =libRig.createObj(partial(mc.joint, **{'n': nLsBox[val]}),shape= libRig.Shp([self.typeSk],
                    size= (scaleWX*0.4,scaleWX*self.sizeSk[1]*0.4,scaleWX*self.sizeSk[2]*0.4)),match=lSa['sa'][val],
                                      father=lSa['sa'][val],refObj=self.selObj,attributs={"drawStyle": 2,"overrideEnabled": 1})
            elif self.typeSk == "sphere":
                ctr =libRig.createObj(partial(mc.joint, **{'n': nLsBox[val]}),shape= libRig.Shp([self.typeSk],
                    size= (scaleWX*scaleSk*0.4,scaleWX*self.sizeSk[1]*0.4,scaleWX*self.sizeSk[2]*0.4)),match=lSa['sa'][val],
                                      father=lSa['sa'][val],refObj=None,attributs={"drawStyle": 2,"overrideEnabled": 1})

            shp = mc.listRelatives(ctr, s=True)[0]
            mc.setAttr(shp+".overrideDisplayType", 2)
            lsSk.append(ctr)
        # CREATE ATTRIBUTES VIS TO LOCATOR Sk_________________________________
        mc.addAttr(dic['master'], ln='visSK', at="enum", en="%s:%s" % ('Off', 'On'), k=True)
        mc.setAttr(dic['master'] + '.visSK', e=True, cb=True)
        [mc.connectAttr(dic['master'] + '.visSK',each+ '.visibility',f=True) for each in lSa['loc']]
        lib_attributes.lockAndHideAxis(lSa['loc'], transVis=True, rotVis=True, sclVis=True)
        [mc.setAttr(each+ '.V',l=True, k=False,cb=False) for each in lSa['loc']]
        # PARENT______________________________________________________________
        mc.parent(nSAGrp, dic['grpSA'])
        mc.parent(nLoft2,dic['grpWorldSA'])
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='sk',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.sk['+str(i)+']',each,type='string') for i, each in enumerate(lsSk)]
        # DICTIONARY RETURN___________________________________________________
        mc.select(cl=True)
        return dic

# exemple d'appel
'''
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

from ellipse_rig.assets.characters import guide_spine
reload(guide_spine)
guide = guide_spine.Spine(name='spine',side='',selObj=mc.ls(sl=True),numb=3,numbSk=9) # instance class charGuide
guide.createSpine()

from ellipse_rig.assets.characters import guide_head
reload(guide_head)
guide = guide_head.Head(name='head',side='',selObj=mc.ls(sl=True)) # instance class charGuide
guide.createHead()

from ellipse_rig.assets.characters import guide_eyes
reload(guide_eyes)
guide = guide_eyes.Eyes(name='eye',side='',selObj=mc.ls(sl=True),numb=2,numbSk=5) # instance class charGuide
guide.createEyes()


from ellipse_rig.assets.characters import guide_member
reload(guide_member)
guide = guide_member.Member(name='member',side='R',selObj=mc.ls(sl=True),numb=1,numbSk=7,offsetT=(0,7,0),offsetR=(0,0,0)) # instance class charGuide
guide.createEndMember()



from ellipse_rig.assets.characters import guide_leg
reload(guide_leg)
guide = guide_leg.Leg(name='leg',side='L',selObj=mc.ls(sl=True),numb=2,numbSk=7,numbMidMb=2) # instance class charGuide
guide.createLeg()


from ellipse_rig.assets.characters import guide_arm
reload(guide_arm)
guide = guide_arm.Arm(name='arm',side='L',selObj=mc.ls(sl=True),numb=1,numbSk=7,numbMidMb=2) # instance class charGuide
guide.createArm()

#lib_attributes.lockAxis(lsIk, rot=True, axis=('y', 'z'))
#lib_attributes.lockAndHideAxis(lsIk, rotVis=True, axis=('y', 'z'))
'''
