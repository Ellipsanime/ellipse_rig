# coding: utf-8

import maya.cmds as mc
import math
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world
from ellipse_rig.assets.asset_base import guide_info
reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)
reload(guide_info)

guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig
guide_info.Info()  # instance class charGuide and run method createRig


class Wheel(guide_info.Info):

    def __init__(self,name='wheel',side='',selObj=None,obj=mc.ls(sl=True),nbSbdv=16,numbSk=16,sizeMast=(2,2,2),shpRotMaster=(0,0,0),
                 shpRotCtr=(90,0,0),sizeCtr=(1,1,1),typeShpMst="circle",**kwargs):
        guide_info.Info.__init__(self,name=name,side=side,selObj=selObj)
        self.selObj = selObj
        self.nbSbdv = nbSbdv
        self.numbSk = numbSk
        self.typeShapeMast = typeShpMst
        color= lib_shapes.side_color(side=side)
        self.valColorMasterCtr = color["colorMaster"]
        self.sizeMast = sizeMast
        self.shpRotMaster = shpRotMaster
        self.shpRotCtr = shpRotCtr
        self.valColorCtr = color["colorCtr"]
        self.sizeCtr = (0.3,0.3,0.3)
        self.rigAdd = "rigAdd"
        self.sizeRigAdd = (0.5,0.5,0.5)
        self.Ctr = "square"
        self.nbCtr = 8
        self.sizeSk =(1,1,1)
        self.typeSk ='joint'
        self.offsetIk = (0,0,0)
        self.numb = nbSbdv

    def createWheel(self):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = guide_info.Info.infoInc(self)
        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHook1 = gloss.name_format(prefix=gloss.lexicon('tplHook'),name=self.name,nFunc='cv'+str(1), nSide=self.side,incP=dic['incVal'])
        nRoot1 = gloss.name_format(prefix=gloss.lexicon('tplRoot'),name=self.name,nFunc='cv'+str(1), nSide=self.side,incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=dic['incVal'])
        nCrv1 = gloss.name_format(prefix=gloss.lexicon('tplCv'),name=self.name,nFunc=str(1), nSide=self.side,incP=dic['incVal'])
        nCrv2 = gloss.name_format(prefix=gloss.lexicon('tplCv'),name=self.name,nFunc=str(2), nSide=self.side,incP=dic['incVal'])
        nLoft = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc=str(1), nSide=self.side,incP=dic['incVal'])
        nCrvPath = gloss.name_format(prefix=gloss.lexicon('tplCv'),name=self.name,nFunc="path"+str(1), nSide=self.side,incP=dic['incVal'])
        nRigAdd = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=gloss.lexicon('add'), nSide=self.side,incP=dic['incVal'])


        RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
        hookMaster = libRig.createObj(partial(mc.group, **{'n': nHook1, 'em': True}),father=RIG,attrInfo=dic['infoName'])
        master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast],color=self.valColorMasterCtr,
                size=self.sizeMast,rotShp=self.shpRotMaster),match=self.selObj,attrInfo=dic['infoName'],father=hookMaster,attributs={"drawStyle": 2},worldScale=self.nWorld)
        root1 = libRig.createObj(partial(mc.group, **{'n': nRoot1, 'em': True}),father=master['root'],attrInfo=dic['infoName'])

        rigAdd =libRig.createController(name=nRigAdd,shape=libRig.Shp([self.rigAdd],color=self.valColorCtr,
                size=self.sizeRigAdd,rotShp=self.shpRotMaster),match=self.selObj,attrInfo=dic['infoName'],father=master['c'],attributs={"drawStyle": 2},worldScale=self.nWorld)
        mc.move(0,2.5,0, rigAdd['root'], ls=True)

        # Crvs___________________________________________
        crv1 =libRig.createObj(partial(mc.circle, **{'n': nCrv1, 's':self.nbSbdv,'sw':360,'nr':(1,0,0)}),father=root1,attributs={"visibility": 0})
        mc.setAttr(crv1 + '.rotateX',22.5)
        mc.move(0.2,0,0, crv1, ls=True)
        crv2 =libRig.createObj(partial(mc.circle, **{'n': nCrv2, 's':self.nbSbdv,'sw':360,'nr':(1,0,0)}),father=root1,attributs={"visibility": 0})
        mc.setAttr(crv2 + '.rotateX',22.5)
        mc.move(-0.2,0,0, crv2, ls=True)
        # CrvPath___________________________________________
        crvPath =libRig.createObj(partial(mc.circle, **{'n': nCrvPath, 's':self.nbSbdv,'sw':360,'nr':(1,0,0)}),father=root1,attributs={"visibility": 0})
        mc.setAttr(crvPath + '.rotateX',22.5)

        # create controleurs tpl to adjust wheel
        crvTmp =libRig.createObj(partial(mc.circle, **{'n': 'cvTmp', 's':8,'sw':360,'nr':(1,0,0)}),father=None)
        lsShpTmp = mc.ls(crvTmp+ '.cv[*]', fl=True)
        mc.setAttr(crvTmp + '.rotateX',45)
        getPosition = [mc.pointPosition(each) for each in lsShpTmp]
        mc.delete(crvTmp)

        lsSkCtr = []
        lsCtr = []
        count =1
        for each in range(self.nbCtr):
            nCtr = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name,nFunc=str(count), nSide=self.side,
                                     incP=dic['incVal'])
            ctr = libRig.createController(name=nCtr, shape=libRig.Shp([self.Ctr], color=self.valColorCtr,size=self.sizeCtr,
                  rotShp=self.shpRotCtr),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
                  attributs={"drawStyle": 2}, worldScale=self.nWorld)
            mc.setAttr(ctr['root']+ '.segmentScaleCompensate', 0)
            mc.xform(ctr['root'], worldSpace=True, t=getPosition[count-1])
            count += 1
            lsSkCtr.append(ctr['sk'])
            lsCtr.append(ctr['c'])
        # CREATE LOFT SK____________________________________________
        loft = libRig.createObj(
            partial(mc.loft, crv1, crv2, **{'n': nLoft, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
                                                   'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=root1,
            refObj=None, incPart=False, attributs={"visibility": 1})

        # ADJUST SKINNING CV___________________________
        splitPart =3
        listCv1 = mc.ls(crv1 + '.cv[*]', fl=True)
        listCv1.append(listCv1[0])
        listCv2 = mc.ls(crv2 + '.cv[*]', fl=True)
        listCv2.append(listCv2[0])
        listCvPath = mc.ls(crvPath + '.cv[*]', fl=True)
        listCvPath.append(listCvPath[0])


        val = 0
        dictPartCv1 = {}
        dictPartCv2 = {}
        dictPartPath = {}
        for each2 in range(self.nbCtr):
            lsPartCv1 =[]
            lsPartCv2 =[]
            lsPartPath =[]
            for each in range(splitPart):
                lsPartCv1.append(listCv1[each+val])
                lsPartCv2.append(listCv2[each+val])
                lsPartPath.append(listCvPath[each+val])
            val += 2
            dictPartCv1[each2] = lsPartCv1
            dictPartCv2[each2] = lsPartCv2
            dictPartPath[each2] = lsPartPath
        # get values Skin___________________________
        count = 0
        getValCrv = []
        for each in range(splitPart):
            val = round(abs(float(count) / float(splitPart - 1)), 4)
            count += 1
            getValCrv.append(val)
        invertValCrv = getValCrv[::-1]

        # skin crvs______________________________________
        skinCrv = mc.skinCluster(lsSkCtr, crv1, tsb=1, mi=1)
        skinCrv2 = mc.skinCluster(lsSkCtr, crv2, tsb=1, mi=1)
        skinCrvPath = mc.skinCluster(lsSkCtr, crvPath, tsb=1, mi=1)
        addfirstskToLast = lsSkCtr
        addfirstskToLast.append(lsSkCtr[0])
        # MODIFY SKIN VALUES CRVS_________________________________________________
        for i, each in enumerate(sorted(dictPartCv1.items())):
            for j, eachPoint in enumerate(dictPartCv1.values()[i]):
                mc.skinPercent(skinCrv[0], eachPoint, r=False, transformValue=[(lsSkCtr[i],
                               invertValCrv[j]),(addfirstskToLast[i+1], getValCrv[j])])

        for i, each in enumerate(sorted(dictPartCv2.items())):
            for j, eachPoint in enumerate(dictPartCv2.values()[i]):
                mc.skinPercent(skinCrv2[0], eachPoint, r=False, transformValue=[(lsSkCtr[i],
                               invertValCrv[j]),(addfirstskToLast[i+1], getValCrv[j])])

        for i, each in enumerate(sorted(dictPartPath.items())):
            for j, eachPoint in enumerate(dictPartPath.values()[i]):
                mc.skinPercent(skinCrvPath[0], eachPoint, r=False, transformValue=[(lsSkCtr[i],
                               invertValCrv[j]),(addfirstskToLast[i+1], getValCrv[j])])


        # PARENT INFO AND TPL RIG_________________________________________
        mc.parent(dic['infoName'],nRIG)
        mc.parent(nRIG,self.nWorldGrp)
        # CONNECT TO WORLD________________________________________________
        lib_connectNodes.connectMatrixAxis(driver=self.nFly, slave=hookMaster)
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='delPart',dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+'.delPart[0]',nRIG,type='string')
        mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
        mc.addAttr(dic['infoName'], ln='sizeSk', at="enum", en="%s:%s:%s:%s:%s:%s"%(self.sizeCtr,self.sizeSk,self.typeSk,
                                    self.offsetIk,self.numb,self.numbSk), k=True, p='infoSK')
        mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)


        mc.addAttr(dic['infoName'], longName='infoCRV', numberOfChildren=1, attributeType='compound')
        mc.addAttr(dic['infoName'], ln='crvInfo', at="enum", en="%s:%s"%(self.nbSbdv,self.numbSk), k=True, p='infoCRV')
        mc.setAttr(dic['infoName'] + '.crvInfo', e=True, cb=True)

        mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')),dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('masterTpl'),nMaster,type='string')
        mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('rigAddTpl')),dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('rigAddTpl'),nRigAdd,type='string')
        mc.addAttr(dic['infoName'], ln='ctr',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.ctr['+str(i)+']',each,type='string') for i, each in enumerate(lsCtr)]

        mc.addAttr(dic['infoName'], ln='cvs',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.cvs['+str(i)+']',each,type='string') for i, each in enumerate([crv1,crv2])]
        mc.addAttr(dic['infoName'], ln='cvPath',dt='string',multi=True) # add IK control
        mc.setAttr(dic['infoName']+".cvPath[0]",crvPath,type='string')

        # add ik in sym attributes
        if self.side is not'':
            #nSym = lib_attributes.attrSymetrie(selObj=nMaster, nameInfo=dic['infoName'])
            mc.setAttr(dic['infoName']+'.sym['+str(1)+']',nMaster,type='string')
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsCtr)]


        dic['loft'] = nLoft
        dic['master'] = nMaster
        dic['lsCtr'] = lsCtr

        return dic


'''
# Import de la librairie sys
import sys
import maya.cmds as mc
import maya.mel as mel
# Définition du chemin des scripts
pathCustom ='T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip'

# Si le chemin n'est pas déjà configuré
if not pathCustom in sys.path:
    # On l'ajoute
    sys.path.append(pathCustom)
# Import du module et définition d'un nom d'appel
# Refresh du module



from ellipse_rig.assets.props.wheel import guide_wheel
reload(guide_wheel)
guide = guide_wheel.Wheel(name='wheel',side='') # instance class charGuide
guide.createWheel()


from ellipse_rig.assets.props.wheel import rig_wheel
reload(rig_wheel)
rig = rig_wheel.Wheel() # instance class charGuide
rig.createWheel()
'''