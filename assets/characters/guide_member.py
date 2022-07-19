# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)
reload(guide_base)


rigGuide = guide_base.CharGuide()  # instance class charGuide and run method createRig

class Member(guide_base.CharGuide):
    def __init__(self,nStartMb='startMb',name='member',nMidMb='midMb',nEndMb='endMb',side='',selObj=None,numb=1,numbSk=1,
                 numbStartSk=1,numbStartMb=1,numbMidMb=1,numbEndMb=None,subDvEndMb=3,numbPlV=1,
                 offsetStartIk=(2,0,0),offsetIk=(0,-5.5,0),shpRotIk=(0,45,0),offsetStartT=(0,0,0),offsetStartR=(0,0,0),
                 offsetT=(0,6.5,0),offsetR=(0,0,0),shpRotCtr=(0,0,0),sizeMastStartMb=(0.7,0.7,0.7),
                 offsetStartMbCtr = (0,0,0),offsetMidMbCtr = (0,0,0),offsetEndMbTr=(0,0,0.3),posPlV =(0,0,0), incVal=None, **kwargs):

        guide_base.CharGuide.__init__(self, name=name, side=side, selObj=selObj, numb=numb, numbSk=numbSk, incVal=incVal)
        self.incVal = incVal
        # start member________________________
        self.nStartMb = nStartMb
        #if side is 'L':
        self.offsetStartIk = (offsetStartIk[0],offsetStartIk[1],offsetStartIk[2])
        if side is 'R':
            self.offsetStartIk = (-offsetStartIk[0],offsetStartIk[1],offsetStartIk[2])
        self.sizeMastStartMb = (0.7,0.7,0.7)
        self.sizeStartMbIk = (0.35,0.35,0.35)
        self.sizeCtrStartMb = (0.5,0.5,0.5)
        self.sizeScapularStartMb = (0.2,0.2,0.2)
        self.numbStartMb = numbStartMb
        self.numbStartSk = numbStartSk
        self.typeShapeMastStartMb ="boomrang"
        self.typeShapeStartMb = "sphere"
        self.offsetMastStartTr = offsetStartT
        self.offsetMastStartRo = offsetStartR
        self.offsetStartMbCtr = offsetStartMbCtr
        self.shpRotStartCtr = (-90,0,90)
        self.shpRotStartMaster = (-90,90,0)
        self.posScapular = (0,0,-2)
        #  member______________________________
        self.name = name
        self.offsetIk = offsetIk
        self.sizeMast = (1,1,1)
        self.sizeIk = (0.6,0.6,0.6)
        self.sizeCtr = (0.6,0.6,0.6)
        self.sizePlV = (0.3,0.3,0.3)
        self.sizeSk = (0.7,0.7,0.7)
        self.numbPlV = numbPlV
        self.typeSk = "sphere"
        self.typeShapeMast = "circle"
        self.typeShape = "circle"
        self.typeShapePlV = "sphere"
        self.typeShapePlVAdd = "arrowQuadro2"
        self.posPlV = posPlV
        self.posPlVAdd = (0,0,-1)
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR
        self.shpRotCtr = shpRotCtr
        self.typeMbIk ="cube"
        # mid member____________________________
        self.nMidMbGeneric = "midMb"
        self.nMidMb = nMidMb
        self.sizeMastMidMb = (0.7,0.7,0.7)
        self.sizeCtrMidMb = (0.6,0.6,0.3)
        self.numbMidMb = numbMidMb
        self.typeShapeMidMember = "square"
        self.typeShapeBank = "sphere"
        self.sizeBank = (0.1,0.1,0.1)
        self.offsetMidMbCtr = offsetMidMbCtr
        # end member____________________________
        self.nEndMbGeneric = "endMb"
        self.nEndMb = nEndMb
        self.numbEndMb = numbEndMb
        self.numbSubDvEndMb = subDvEndMb
        self.typeShapeEndMb = "pyramide2"
        self.sizeMastEndMb = (0.3,1,0.2)
        self.sizeCtrEndMb = (0.1,0.35,0.15)
        self.offsetEndMbTr = offsetEndMbTr

    def createStartMember(self):
        rigGuide = guide_base.CharGuide(name=self.nStartMb, side=self.side, selObj=self.selObj,
                    numb=self.numbStartMb, numbSk=self.numbStartSk,offsetIk=self.offsetStartIk,shpRotMaster=self.shpRotStartMaster,
                    shpRotIk=self.shpRotIk,sizeMast=self.sizeMastStartMb, sizeIk=self.sizeStartMbIk,sizeCtr=self.sizeCtrStartMb,
                    shpRotCTR=self.shpRotStartCtr,sizeSk=self.sizeSk,typeBox=self.typeSk,typeShpIk=self.typeMbIk,typeShpMst=self.typeShapeMastStartMb,
                    typeShp=self.typeShapeMastStartMb, incVal=self.incVal)  # instance class CharGuide
        dic = rigGuide.templateSk()  # run method createRig
        # OFFSET ROOT MASTER STARTMEMBER_____________________________________
        val = float(mc.getAttr(self.nWorld + '.scaleX'))
        if self.selObj != []: # check if objRef is empty
            pass
        else:
            mc.move(float(self.offsetMastStartTr[0])*val,float(self.offsetMastStartTr[1])*val,float(self.offsetMastStartTr[2])*val,dic['master'])
            mc.rotate(float(self.offsetMastStartRo [0]),float(self.offsetMastStartRo [1]),float(self.offsetMastStartRo [2]),dic['master'])
        if self.side is 'L':
            [mc.setAttr((mc.getAttr(each+'.root')) + '.rotateZ',180) for each in dic['lsCtr']]  # adjust orientation
        elif self.side is 'R':
            [mc.setAttr((mc.getAttr(each+'.root')) + '.rotateZ',0) for each in dic['lsCtr']]  # adjust orientation

        # OFFSET SHAPE CTR STARTMEMBER_____________________________________
        for each in dic['lsCtr']:
            selShape = mc.listRelatives(each, s=True)[0]
            recCv = mc.ls(selShape + '.cv[*]', fl=True)
            mc.rotate(0,90,90, recCv)

        #mc.move(0,0.01,0,mc.getAttr(dic['lsIk'][0] +'.root'))
        if self.nStartMb == 'clav':
            # CREATE SCAPULA_____________________________________
            nScapula = gloss.name_format(prefix=gloss.lexicon('tpl'),name='scapula',nSide=self.side,incP=dic['incVal'])
            scapula = libRig.createController(name=nScapula, shape=libRig.Shp([self.typeShapeStartMb],
            color=self.valColorCtr,size=self.sizeScapularStartMb), match=dic['master'],attrInfo=dic['infoName'], father=dic['master'], worldScale=self.nWorld)
            val = float(mc.getAttr(self.nWorld + '.scaleX'))
            mc.move(self.posScapular[0], self.posScapular[1], self.posScapular[2] * val, scapula['root'], os=True)
            # CREATE CRV SHAPE BETWEEN CLAVICULE AND SCAPULAR____
            lsToCrv = [mc.getAttr(dic['master'] + '.sk'), scapula['sk']]
            positions = [mc.xform(each2, q=True, ws=True, translation=True) for each2 in lsToCrv]
            nCrvScapula = gloss.name_format(prefix=gloss.lexicon('tplCv'), name='scapula',nSide=self.side,incP=dic['incVal'])
            createCrvScapula = mc.curve(n=nCrvScapula, p=positions, d=1)
            mc.skinCluster(lsToCrv, createCrvScapula, tsb=1, mi=1)
            mc.setAttr(createCrvScapula + ".template", 1)
            mc.setAttr(createCrvScapula + ".inheritsTransform", 0)
            mc.parent(createCrvScapula, dic['srfAttach'])
            # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
            mc.addAttr(dic['infoName'], shortName='scapulaStart', dt='string', multi=True)
            mc.setAttr(dic['infoName'] + '.scapulaStart[0]',scapula['c'], type='string')
            dic['scapula']= scapula['c']
        # DISCONNECT BUILD CG_____________________________________
        mc.setAttr(dic['infoName']+'.buildCg',0)

        #".%s"%gloss.lexiconAttr('masterTpl')
        # DICTIONARY RETURN_________________________________________________________
        mc.select(cl=True)
        return dic


    def createMember(self):
        # TEMPLATE LEG_________________________________________________________
        dicStart =  Member.createStartMember(self)
        rigGuide = guide_base.CharGuide(name=self.name, side=self.side, selObj=self.selObj, numb=self.numb, numbSk=self.numbSk,
                   offsetIk=self.offsetIk, shpRotIk=self.shpRotIk, sizeMast=self.sizeMast, sizeIk=self.sizeIk,shpRotCTR=self.shpRotCtr,
                   sizeCtr=self.sizeCtr,sizeSk=self.sizeSk, typeBox=self.typeSk,typeShpMst=self.typeShapeMast,typeShpIk=self.typeMbIk,typeShp=self.typeShape, incVal=self.incVal)  # instance class CharGuide
        dic = rigGuide.templateSk()  # run method createRig
        # OFFSET ROOT MASTER MEMBER__________________________________________
        val = float(mc.getAttr(self.nWorld + '.scaleX'))
        if self.selObj != []: # check if objRef is empty
            pass
        else:
            mc.move(float(self.offsetMasterTr[0])*val,float(self.offsetMasterTr[1])*val,float(self.offsetMasterTr[2])*val,dic['master'])
            mc.rotate(float(self.offsetMasterRo[0]),float(self.offsetMasterRo[1]),float(self.offsetMasterRo[2]),dic['master'])
        # CREATE SYSTEM TO POLE VECTOR_______________________________________
        # NAME ______________________________________________________________
        nGrpPlV = gloss.name_format(prefix=gloss.lexicon('tplPlV'),name=self.name,nFunc=gloss.lexicon('plV'),nSide=self.side,incP=dic['incVal'])
        nLsSkIkPlV = [gloss.name_format(prefix=gloss.lexicon('tplSk'), name=self.name, inc=str(i+1),nFunc=gloss.lexicon('plV'),
                                        nSide=self.side, incP=dic['incVal']) for i, each in enumerate(dic["lsIk"])]
        nLsLookAt = [gloss.name_format(prefix=gloss.lexicon('tplLookAt'), name=self.name, inc=str(i+1),nFunc=gloss.lexicon('plV'),
                                        nSide=self.side, incP=dic['incVal']) for i, each in enumerate(dic["lsIk"])]
        nLoftPlV = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name,nFunc=gloss.lexicon('plV'),nSide=self.side,incP=dic['incVal'])
        nPoleVector = gloss.name_format(prefix=gloss.lexicon('tplPlV'), name=self.name, nSide=self.side,incP=dic['incVal'])
        if mc.objExists(nGrpPlV) is True:
            pass
        else:
            # CREATE ____________________________________________________________
            getSAWorld = mc.getAttr(dic['master'] + ".tplSAWorld")
            grpPlV = libRig.createObj(partial(mc.group, **{'n': nGrpPlV, 'em': True}),match=[dic['master']], father=getSAWorld)
            mc.parentConstraint(dic['master'],nGrpPlV)
            lsSkPlv =[]; lsLookAt =[]; lsupV =[]
            for i, each in enumerate(dic["lsIk"]):
                skIkPlV = mc.duplicate(mc.getAttr(each + ".sk"),n=nLsSkIkPlV[i])
                lookAt = libRig.createObj(partial(mc.spaceLocator, **{'n':nLsLookAt[i]}),match=[each], father=nGrpPlV, attributs={"visibility":0})
                mc.parent(nLsSkIkPlV[i],nGrpPlV)
                mc.pointConstraint(each,nLsSkIkPlV[i],offset=(0,0,0),w=1)
                mc.pointConstraint(each,nLsLookAt[i],offset=(0,0,0),w=1)
                mc.parentConstraint(nLsLookAt[i],mc.getAttr(each + ".sk"))
                # LIST PARENT___________________________________________________
                lsSkPlv.append(nLsSkIkPlV[i])
                lsLookAt.append(nLsLookAt[i])
            # CREATE CURVE AND LOFT_____________________________________________
            val = float(mc.getAttr(self.nWorld + '.scaleX'))
            getCrv = lib_curves.createDoubleCrv(objLst=lsSkPlv, axis='Z', offset=0.2 * val)
            loft = lib_curves.createLoft(name=nLoftPlV, objLst=getCrv['crv'], father=None, deleteCrv=True)
            mc.skinCluster(lsSkPlv, loft, tsb=1, mi=1)
            # CONNECT TO LOFT___________________________________________________
            lSa = lib_connectNodes.surfAttach(selObj=[nLoftPlV], lNumb=1, parentInSA=True, parentSA=None,delKnot=True)

            # CREATE POLE VECTOR________________________________________________
            poleV = libRig.createController(name=nPoleVector, shape=libRig.Shp([self.typeShapePlV],
                    color=self.valColorCtr,size=self.sizePlV,rotShp=(90, 0, 0)), match=lSa['sa'],attrInfo=dic['infoName'], father=lSa['sa'], worldScale=self.nWorld)
            mc.setAttr(poleV['root'] + '.rotateY', 180)  # adjust orientation
            mc.setAttr(poleV['root'] + '.rotateZ', 90)  # adjust orientation
            mc.move(self.posPlV[0],self.posPlV[1],self.posPlV[2]*val,poleV['c'],os=True)
            # CREATE AIM CONSTRAINT_____________________________________________
            aimCns = [mc.aimConstraint(dic["lsIk"][j-1], each, aim=(0,-1,0), u=(0,0,1), wut='object', wuo=nPoleVector) for j, each in enumerate(lsLookAt)]
            # CREATE AIM CONSTRAINT ON POLE VECTOR______________________________
            #mc.aimConstraint(lSa['sa'], nPoleVector, aim=(0, 0, -1), u=(0, 1, 0), wut='object', wuo=dic['lsIk'][0])
            # CREATE CRV SHAPE BETWEEN ELBOW POLE VECTOR________________________________________________________________
            lsToCrv =[dic['lsCtr'][0],poleV['sk']]
            positions = [mc.xform(each, q=True, ws=True, translation=True) for each in lsToCrv]
            nCrvPoleV = gloss.name_format(prefix=gloss.lexicon('tplCv'),name=self.name,nFunc=gloss.lexicon('plV'),nSide=self.side,incP=dic['incVal'])
            createCrvTmp = mc.curve(n=nCrvPoleV, p=positions, d=1)
            mc.skinCluster(lsToCrv, createCrvTmp, tsb=1, mi=1)
            mc.setAttr(createCrvTmp +".template",1)
            mc.setAttr(createCrvTmp +".inheritsTransform",0)
            mc.parent(createCrvTmp,dic['srfAttach'])
            # SYSTEM NO FLIP TO INVERT POLE VECTOR________________________________________________
            nCndFlipPlV = gloss.name_format(prefix=gloss.lexicon('cnd'),name=self.name,nFunc='plv',nSide=self.side,incP=dic['incVal'])
            cndFlipPlV = mc.createNode('condition', n=nCndFlipPlV)
            mc.setAttr(cndFlipPlV + '.secondTerm', 0)
            if self.name =='leg':
                mc.setAttr(cndFlipPlV+ '.operation', 3)
            elif self.name =='arm':
                mc.setAttr(cndFlipPlV+ '.operation', 4)
            mc.setAttr(cndFlipPlV + '.colorIfTrueR', 1)
            mc.setAttr(cndFlipPlV + '.colorIfFalseR', -1)

            mc.connectAttr(poleV['c'] + '.translateZ', cndFlipPlV + '.firstTerm')
            mc.connectAttr(cndFlipPlV + '.outColorR', aimCns[0][0] + '.upVectorZ')
            mc.connectAttr(cndFlipPlV + '.outColorR', aimCns[1][0] + '.upVectorZ')

            # CREATE ADD POLE VECTOR________________________________________________
            lsAddPlV =[]
            if self.numb >1:
                numbPlVAdd = self.numb
                countCtr = 2
                count = 1
                # PAIR___________________________________
                if self.numb %2 ==0:
                    numbPlVAdd -= (float(self.numb/2))
                    if self.numb == 2:
                        countCtr = 1
                else:
                    # IMPAIR__________________________________
                    numbPlVAdd -= (float(self.numb/2)+1)

                for each in range(int(numbPlVAdd)):
                    nPlVectorAdd = gloss.name_format(prefix=gloss.lexicon('tplPlV'), name=self.name,nFunc=gloss.lexicon('add')+str(count), nSide=self.side,incP=dic['incVal'])
                    poleVAdd = libRig.createController(name=nPlVectorAdd, shape=libRig.Shp([self.typeShapePlVAdd],
                    color=self.valColorCtr,size=self.sizeCtr,rotShp=(90, 0, 0)), match=[dic['lsCtr'][countCtr]],attrInfo=dic['infoName'], father=dic['lsCtr'][countCtr], worldScale=self.nWorld)
                    mc.move(self.posPlVAdd[0],self.posPlVAdd[1],self.posPlVAdd[2]*val,poleVAdd['root'],os=True)
                    # CREATE CRV SHAPE BETWEEN ELBOW POLE VECTOR________________________________________________________________
                    lsToCrv =[mc.getAttr(dic['lsCtr'][countCtr]+'.sk'),poleVAdd['sk']]
                    positions = [mc.xform(each2, q=True, ws=True, translation=True) for each2 in lsToCrv]
                    nCrvPoleV = gloss.name_format(prefix=gloss.lexicon('tplCv'),name=self.name,nFunc=gloss.lexicon('plV')+'Add'+str(count),nSide=self.side,incP=dic['incVal'])
                    createCrvTmp2 = mc.curve(n=nCrvPoleV, p=positions, d=1)
                    mc.skinCluster(lsToCrv, createCrvTmp2, tsb=1, mi=1)
                    mc.setAttr(createCrvTmp2 +".template",1)
                    mc.setAttr(createCrvTmp2 +".inheritsTransform",0)
                    mc.parent(createCrvTmp2,dic['srfAttach'])
                    lsAddPlV.append(poleVAdd['c'])
                    count += 1
                    if self.numb %2 ==0:
                        if each+2 < int(numbPlVAdd):
                            countCtr += 2
                        else:
                            countCtr += 1
                    else:
                        countCtr += 2
            else:
                pass

            # PARENT LOFT_______________________________________________________
            getSA = mc.getAttr(dic['master'] + ".tplSA")
            mc.parent(nLoftPlV,getSAWorld)
            mc.parent(lSa['sa'],getSA)
            # LOCK TRANSLATE X AXIS_______________________________________________
            lib_attributes.lockAndHideAxis(dic["lsCtr"], transVis=True, axisT='x')
            [lib_attributes.lockAndHideAxis(each, transVis=True, axisT='x') for each in lsAddPlV]
            [mc.setAttr(mc.getAttr(each+'.root') + '.rotateZ', 90) for each in dic["lsCtr"]]
        # ADJUST VIS SHAPE IF START MEMBER EXIST _____________________________
        if mc.objExists(dicStart['infoName']) is True:
            mc.parent(mc.getAttr(dicStart['infoName']+'.delPart[0]'),mc.getAttr(dic['infoName']+'.delPart[0]'))
            mc.pointConstraint(dic['master'],mc.getAttr(dicStart['master']+'.root'))
            mc.pointConstraint(dic['lsIk'][0], dicStart['lsIk'][-1])
            [mc.setAttr(mc.listRelatives(dicStart['lsIk'][i], s=True)[0] + ".visibility", 0) for i,each in enumerate(dicStart['lsIk'])]
            #[mc.setAttr(mc.listRelatives(dicStart['lsIk'][i], s=True)[1] + ".visibility", 0) for i,each in enumerate(dicStart['lsIk'])]
        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        if mc.objExists(dicStart['infoName']) is False:
            pass
        else:
            mc.setAttr(dic['infoName']+".%s[1]"%gloss.lexiconAttr('masterTpl'),dicStart['master'],type='string')
            mc.addAttr(dic['infoName'], shortName='infoNumbMb', dt='string', multi=True)
            mc.setAttr(dic['infoName'] + '.infoNumbMb[0]', self.numb, type='string')
            mc.addAttr(dic['infoName'], shortName='masterStart',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.masterStart['+str(i)+']',each,type='string') for i, each in enumerate([dicStart['master']])]
            mc.addAttr(dic['infoName'], shortName='ikStart',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.ikStart['+str(i)+']',each,type='string') for i, each in enumerate(dicStart['lsIk'])]
            mc.addAttr(dic['infoName'], shortName='ctrStart',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.ctrStart['+str(i)+']',each,type='string') for i, each in enumerate(dicStart['lsCtr'])]
            if self.nStartMb == 'clav':
                mc.addAttr(dic['infoName'], shortName='scapulaStart',dt='string',multi=True)
                mc.setAttr(dic['infoName']+'.scapulaStart[0]',dicStart['scapula'],type='string')
                mc.setAttr(dicStart['scapula']+'.infPart', dic['infoName'], e=True, type="string")
            # REPLACE DIC INFO NAME TO LSIK AND LSCTR__________________________
            mc.setAttr(dicStart['master']+'.infPart', dic['infoName'], e=True, type="string")
            [mc.setAttr(each+'.infPart',dic['infoName'],e=True,type="string") for i, each in enumerate(dicStart['lsIk'])]
            [mc.setAttr(each+'.infPart',dic['infoName'],e=True,type="string") for i, each in enumerate(dicStart['lsCtr'])]
        mc.addAttr(dic['infoName'], shortName='masterPlV',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.masterPlV['+str(i)+']',each,type='string') for i, each in enumerate([nPoleVector])]
        if self.numb >1:
            mc.addAttr(dic['infoName'], shortName='masterAddPlV',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.masterAddPlV['+str(i)+']',each,type='string') for i, each in enumerate(lsAddPlV)]

        # add ik in sym attributes
        if self.side is not'':
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate([dicStart['master']])]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(dicStart['lsIk'])]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(dicStart['lsCtr'])]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate([nPoleVector])]
            if self.numb >1:
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsAddPlV)]
            if self.nStartMb == 'clav':
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']', each, type='string') for i, each in enumerate([dicStart['scapula']])]
        # DICTIONARY RETURN_________________________________________________________
        mc.select(cl=True)
        return dic


    def createMidMember(self):
        # TEMPLATE LEG_________________________________________________________
        dic =  Member.createMember(self)
        # NAME_________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.nMidMb, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.nMidMb,nSide=self.side, incP=dic['incVal'])
        nHookMasterLeg = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.nMidMb,nFunc=gloss.lexicon('leg'),nSide=self.side, incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.nMidMb,nFunc=gloss.lexicon('tplMtr'),nSide=self.side,incP=dic['incVal'])
        nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.nMidMb, nSide=self.side,incP=dic['incVal'])
        nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.nMidMb, nSide=self.side,incP=dic['incVal'])
        nLsCtr = [gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.nMidMb, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numbMidMb)]
        nBankFt = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('front'),nSide=self.side,incP=dic['incVal'])
        nBankBk = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('back'),nSide=self.side,incP=dic['incVal'])
        nBankGrp = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('lnk'),nSide=self.side,incP=dic['incVal'])
        nBankLt = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('left'),nSide=self.side,incP=dic['incVal'])
        nBankRt = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('right'),nSide=self.side,incP=dic['incVal'])
        nLsBank =(nBankBk,nBankFt,nBankLt,nBankRt)
        nBankCrv = gloss.name_format(prefix=gloss.lexicon('tplBank'), name=self.nMidMb, nFunc=gloss.lexicon('cv'),nSide=self.side,incP=dic['incVal'])
        # CREATE FOOT_________________________________________________________
        RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
        hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
        hookMasterLeg = libRig.createObj(partial(mc.group, **{'n': nHookMasterLeg, 'em': True}),father=hookMaster)

        master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeCircle],color=self.valColorMasterCtr,
                size=self.sizeMastMidMb),match=(0,0,0),attrInfo=dic['infoName'],attributs={"drawStyle": 2},worldScale=self.nWorld)
        surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
        # CONNECT HOOK________________________________________________________
        lib_connectNodes.connectMatrixAxis(driver=mc.getAttr(dic['lsIk'][-1]+'.root'), slave=hookMaster)
        mc.connectAttr(dic['lsIk'][-1] + ".translateX", (hookMasterLeg + ".translateX"))
        mc.connectAttr(dic['lsIk'][-1] + ".translateZ", (hookMasterLeg + ".translateZ"))
        mc.connectAttr(dic['lsIk'][-1] + ".rotateY", (hookMasterLeg + ".rotateY"))
        # PARENT INFO AND TPL RIG_____________________________________________
        mc.parent(nRIG,mc.listRelatives(dic['infoName'],p=True))
        mc.parent(master['root'],nHookMasterLeg)
        mc.move(0,-1*float(mc.getAttr(self.nWorld + '.scaleX')),0,master["root"],ls=True)
        # CREATE CTR__________________________________________________________
        lsCtr =[]; lsSk =[]
        for knot in range(self.numbMidMb):
            if knot ==0:
                parent = master['c']
            else:
                parent = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.nMidMb,inc=str(knot),nSide=self.side,incP=dic['incVal'])
            ctr = libRig.createController(name=nLsCtr[knot], shape=libRig.Shp([self.typeShapeMidMember],color=self.valColorCtrIK,size=self.sizeCtrMidMb,rotShp=self.shpRotCtr),
                    match=self.selObj,father=parent,attrInfo=dic['infoName'],worldScale=self.nWorld)
            # OFFSET IK_______________________________________________________
            val = mc.getAttr(self.nWorld+ '.scale')[0][0]
            mc.move(self.offsetMidMbCtr[0]*val,self.offsetMidMbCtr[1]*val,self.offsetMidMbCtr[2]*val,ctr['root'],ls=True)
            # ROOT SEGMENT SCALE COMPENSATE___________________________________
            mc.setAttr(ctr['root']+'.segmentScaleCompensate',0)
            # SET TO LIST_____________________________________________________
            lsCtr.append(ctr['c'])
            lsSk.append(ctr['sk'])

        # CREATE CURVE AND LOFT_______________________________________________
        lsSk.insert(0, dic['lsIk'][-1])
        val = float(mc.getAttr(self.nWorld + '.scaleX'))
        getCrv =''
        if self.name == 'leg':
            getCrv = lib_curves.createDoubleCrv(objLst=lsSk, axis='X', offset=0.2*val)
        elif self.name == 'arm':
            getCrv = lib_curves.createDoubleCrv(objLst=lsSk, axis='Z', offset=-0.2*val)
        loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True,
                                     attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
        mc.skinCluster(lsSk,loft,tsb=1,mi=1)
        mc.setAttr(nLoft+".overrideShading", 0)
        # CREATE BANK CTR_____________________________________________________
        bankGrp = libRig.createObj(partial(mc.group, **{'n': nBankGrp, 'em': True}),match=[lsSk[-2]],father=master['c'])
        bankFt = libRig.createController(name=nBankFt,shape=libRig.Shp([self.typeShapeBank],color=self.valColorMasterCtr,
                size=self.sizeBank),match=[lsSk[-1]],father=master['c'],attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
        bankBk = libRig.createController(name=nBankBk,shape=libRig.Shp([self.typeShapeBank],color=self.valColorMasterCtr,
                size=self.sizeBank),match=[master['c']],father=master['c'],attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
        bankLt= libRig.createController(name=nBankLt,shape=libRig.Shp([self.typeShapeBank],color=self.valColorMasterCtr,
                size=self.sizeBank),match=[lsSk[-2]],father=nBankGrp,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
        bankRt= libRig.createController(name=nBankRt,shape=libRig.Shp([self.typeShapeBank],color=self.valColorMasterCtr,
                size=self.sizeBank),match=[lsSk[-2]],father=nBankGrp,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
        # ADJUST POSITION BANK_______________________________________________
        val = mc.getAttr(self.nWorld+ '.scale')[0][0]
        if self.name == 'leg':
            # CONSTRAINT POSITION BANK___________________________________________
            mc.pointConstraint(lsSk[-1],bankFt['root'],mo=True,skip="y",weight=True)
            mc.pointConstraint(lsSk[-2],nBankGrp,skip="y",weight=True)
            if self.side == 'L':
                mc.move(0.7*val,0,0,bankLt['c'],ls=True)
                mc.move(-0.7*val,0,0,bankRt['c'],ls=True)
            else:
                mc.move(-0.7*val,0,0,bankLt['c'],ls=True)
                mc.move(0.7*val,0,0,bankRt['c'],ls=True)
        elif self.name == 'arm':
            # CONSTRAINT POSITION BANK___________________________________________
            mc.pointConstraint(lsSk[-1],bankFt['root'],mo=True,skip="x",weight=True)
            mc.pointConstraint(lsSk[-2],nBankGrp,skip="x",weight=True)
            if self.side == 'L':
                mc.move(0,0,-0.7*val,bankLt['c'],ls=True)
                mc.move(0,0,0.7*val,bankRt['c'],ls=True)
            else:
                mc.move(0,0,0.7*val,bankLt['c'],ls=True)
                mc.move(0,0,-0.7*val,bankRt['c'],ls=True)
        # ADD CURVE___________________________________________________________
        lsCrvBank = (bankBk['sk'],bankLt['sk'],bankFt['sk'],bankRt['sk'],bankBk['sk'])
        positions = [mc.xform(each, q=True, ws=True, translation=True) for each in lsCrvBank]
        curve1 = mc.curve(n=nBankCrv, p=positions,d=1)
        mc.skinCluster(lsCrvBank,curve1,tsb=1,mi=1)
        mc.setAttr(nBankCrv+".overrideEnabled",1)
        mc.setAttr(nBankCrv+".overrideDisplayType",1)
        mc.parent(nBankCrv,nRIG)

        # CREATE HEEL FOOT___________________________________________________________
        if self.name == 'leg':
            nHeel = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=gloss.lexicon('heel'), nSide=self.side,incP=dic['incVal'])
            heel = libRig.createController(name=nHeel, shape=libRig.Shp(["triangle"],color=self.valColorCtrIK,
                  size=(1,1,1),rotShp=(0,-90,0)),match=[bankBk['c']],father=master['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)
            mc.pointConstraint(lsCtr[0],heel['root'],skip=("x","z"),weight=True)
        else:
            pass

        # ADD ATTRIBUTES ON TEMPLATE INFO_____________________________________
        mc.addAttr(dic['infoName'], shortName='master%s'%(self.nMidMb),dt='string',multi=True)
        mc.setAttr(dic['infoName']+'.master%s[0]'%(self.nMidMb),master['c'],type='string')
        mc.addAttr(dic['infoName'], shortName='%s'%self.nMidMbGeneric,dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.%s['%self.nMidMbGeneric +str(i)+']',each,type='string') for i, each in enumerate(lsCtr)]
        mc.setAttr(dic['infoName']+'.infoNumbMb[1]',self.numbMidMb-1,type='string')
        mc.addAttr(dic['infoName'], shortName='bank',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.bank['+str(i)+']',each,type='string') for i, each in enumerate(nLsBank)]
        # add ik in sym attributes
        if self.side != '':
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate([nMaster])]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsCtr)]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(nLsBank)]


        # ADD ATTRIBUTES HEEL ON TEMPLATE INFO _____________________________________
        if self.name == 'leg':
            mc.addAttr(dic['infoName'], shortName='%s'%self.nMidMb+ 'Heel',dt='string',multi=True)
            mc.setAttr(dic['infoName']+'.%s'%self.nMidMb + 'Heel[0]',heel['c'],type='string')

            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            mc.setAttr(dic['infoName']+'.sym['+str(lenSym)+']',heel['c'],type='string')

        # LOCK AXIS HAND/FOOT________________________________________________
        for i, each in enumerate(lsCtr):
            if self.name == 'arm':
                mc.setAttr(each + '.tz',l=True)
            elif self.name == 'leg':
                mc.setAttr(each + '.tx',l=True)
            else:
                pass

        # ADD DICTIONARY______________________________________________________
        dic['%s'%self.nMidMb] = nLsCtr
        dic['%sMaster'%self.nMidMb] = nMaster
        dic['ctrBank'] = nLsBank
        dic['rigPart'] = nRIG
        mc.select(cl=True)
        return dic




    def createEndMember(self):
        # TEMPLATE FOOT_________________________________________________________
        dic = Member.createMidMember(self)
        if self.numbEndMb == None or self.numbEndMb ==0:
            print 'no end member'
            dicEndMb ={}
            dicEndMb['%s%s'%(self.nEndMb,0)] = 0
            # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
            mc.addAttr(dic['infoName'], shortName='%s'%self.nEndMbGeneric,dt='string',multi=True)
            count = 0
            countInvert = 0
            for key,value in sorted(dicEndMb.items()):
                mc.setAttr(dic['infoName'] + '.infoNumbMb[2]', 0, type='string')
                mc.setAttr(dic['infoName'] + '.infoNumbMb[3]', 0, type='string')
                mc.setAttr(dic['infoName']+'.%s['%self.nEndMbGeneric + str(count)+']',value,type='string')
            # ADD DICTIONARY RETURN________________________________________________
            mc.select(cl=True)
            return dic
        else:
            # NAME__________________________________________________________________
            nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.nEndMb, nSide=self.side,incP=dic['incVal'])
            nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.nEndMb,nSide=self.side, incP=dic['incVal'])
            nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.nEndMb,nFunc=gloss.lexicon('tplMtr'),nSide=self.side,incP=dic['incVal'])
            nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.nEndMb, nSide=self.side,incP=dic['incVal'])
            nLoft = [gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.nEndMb,inc=str(knot+1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbEndMb)]
            # CREATE TOES___________________________________________________________
            RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
            hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
            master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeEndMb],color=self.valColorMasterCtr,
                    size=self.sizeMastEndMb,rotShp=self.shpRotCtr),match=self.selObj,father=nHookMaster,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
            mc.setAttr(mc.listRelatives(master['c'], s=True)[0] + ".visibility", 0)
            mc.move(0,0,0,master["root"],ls=True)
            surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
            # CONNECT HOOK________________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=dic['%s'%self.nMidMb][-2], slave=hookMaster)
            # PARENT INFO AND TPL RIG_____________________________________________
            mc.parent(nRIG,dic['rigPart'])
            # CREATE CTR__________________________________________________________
            sclWorld = float(mc.getAttr(self.nWorld + '.scaleX'))
            dicEndMb ={}
            for knot in range(self.numbEndMb):
                lsCtr =[]
                lsFirstRoot =[]
                for val in range(self.numbSubDvEndMb):
                    # NAME_________________________________________________________
                    nCtr = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.nEndMb, nFunc=str(val+1)+'Part',inc=str(knot + 1),nSide=self.side,incP=dic['incVal'])
                    parent = master['c']
                    if val !=0:
                        parent = gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.nEndMb, nFunc=str(val)+'Part',inc=str(knot+ 1),
                                    nSide=self.side,incP=dic['incVal'])
                    # CREATE ______________________________________________________
                    adjR = (0,0,0)
                    if self.name == 'leg':
                        adjR = (90,0,0)
                    elif self.name == 'arm':
                        adjR = (180,90,0)
                    ctr = libRig.createController(name=nCtr, shape=libRig.Shp(["circle",self.typeShapeEndMb],color=self.valColorCtrIK,
                          size=self.sizeCtrEndMb,rotShp=adjR),match=[nMaster],father=parent ,attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)

                    if val == 0:
                        lsFirstRoot.append(ctr['root'])
                    else:
                        mc.move(self.offsetEndMbTr[0]*sclWorld,self.offsetEndMbTr[1]*sclWorld,self.offsetEndMbTr[2]*sclWorld,ctr['root'],ls=True)

                    lsCtr.append(ctr['c'])
                dicEndMb['%s%s'%(self.nEndMb,int(knot)+1)] = lsCtr
                # OFFSET END MEMBER CTR_________________________________________________
                number = int(self.numbEndMb)
                if self.name == 'leg':
                    mc.move((round(((knot)-(float(number/2)))/float(number-0.5),2))*sclWorld,0,0,lsFirstRoot[0],ls=True)
                    if self.side == 'R':
                        mc.move(-(round(((knot)-(float(number/2)))/float(number-0.5),2))*sclWorld,0,0,lsFirstRoot[0],ls=True)
                elif self.name == 'arm':
                    mc.move(0,0,-(round(((knot)-(float(number/2)))/float(number-0.5),2))*sclWorld,lsFirstRoot[0],ls=True)



            # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
            mc.addAttr(dic['infoName'], shortName='%s'%self.nEndMbGeneric,dt='string',multi=True)
            count = 0
            countInvert = 0
            for key,value in sorted(dicEndMb.items()):
                mc.setAttr(dic['infoName'] + '.infoNumbMb[2]', self.numbEndMb, type='string')
                mc.setAttr(dic['infoName'] + '.infoNumbMb[3]', self.numbSubDvEndMb, type='string')
                mc.setAttr(dic['infoName']+'.%s['%self.nEndMbGeneric + str(count)+']',value,type='string')
                # add ik in sym attributes
                if self.side is not'':
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    [mc.setAttr(dic['infoName']+'.sym['+str(lenSym+i)+']',each,type='string') for i,each in enumerate(value)]
                count += 1
                countInvert += 1
            # ADD DICTIONARY RETURN________________________________________________
            mc.select(cl=True)
            return dic


