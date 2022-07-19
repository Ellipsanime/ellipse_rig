# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_connectNodes, lib_shapes
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(libRig)
reload(lib_connectNodes)
reload(lib_shapes)
reload(guide_base)

rigGuide = guide_base.Info()  # instance class charGuide and run method createRig

class Eyes(guide_base.Info):

    def __init__(self,name='default',side='',selObj=None,obj=mc.ls(sl=True),numb=1,numbSk=1,offsetIk=(0,14,0),shpRot=(0,0,0)
                 ,sizeMast=(0.5,0.5,0.5),sizeIk=(0.4,0.4,0.4),sizeCtr=(1,1,1),sizeSk=(0.7,0.7,0.7),typeBox="cube",typeShp="circle",**kwargs):
        guide_base.Info.__init__(self, name=name, side=side, selObj=selObj)
        self.numb = numb
        self.obj = obj
        self.numbSk = numbSk
        self.offsetIk = offsetIk
        self.typeShape = typeShp
        self.typeShape2 = "sphere"
        color= lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.sizeMast = sizeMast
        self.sizeIk = sizeIk
        self.sizeCtr = sizeCtr
        self.sizeSk = sizeSk
        self.typeSk = typeBox
        self.shpRot = shpRot
        self.numbIk = 2

    def createEyes(self):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = guide_base.Info.infoInc(self)
        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('tplMtr'),nSide=self.side,incP=dic['incVal'])
        nLsIk = [gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]
        nLsJntEye = [gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('jnt'),inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]
        nUpV = gloss.name_format(prefix=gloss.lexicon('tplUv'),name=self.name,nSide=self.side,incP=dic['incVal'])
        nIkHandle = gloss.name_format(prefix=gloss.lexicon('ikHdl'),name=self.name,nSide=self.side,incP=dic['incVal'])

        # GET PARENT HOOK ELEMENT__________________________________________________________
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly +".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0]+'.infPart')+".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)


        # CREATE IK___________________________________________________________
        if mc.objExists(nRIG) is True:
            mc.parent(dic['info'],nRIG)
        else:
            RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
            hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
            master= libRig.createController(name=nMaster,shape=libRig.Shp([self.typeCircle],color=self.valColorMasterCtr,
                    size=self.sizeMast),match=self.selObj,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)
            count = 1
            scaleWX= float(mc.getAttr(self.nWorld+".scaleX"))
            lsIkCtr =[]
            lsJnt =[]
            for knot in range(self.numbIk):
                ikCtr = libRig.createController(name=nLsIk[knot], shape=libRig.Shp([self.typeShape2],color=self.valColorCtrIK,
                        size=(self.sizeIk[0]*scaleWX*count,self.sizeIk[1]*scaleWX*count,self.sizeIk[2]*scaleWX*count),rotShp=self.shpRot),
                        match=self.selObj,father=master['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)

                jntEye = libRig.createObj(partial(mc.joint, **{'n': nLsJntEye[knot]}), match=[master['c']], father=master['c'],
                                 attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 0})
                # ROOT SEGMENT SCALE COMPENSATE________________________________
                mc.setAttr(ikCtr['root']+'.segmentScaleCompensate',0)
                mc.setAttr(jntEye+'.radius',0.2)
                mc.setAttr(jntEye+'.template',1)
                lsIkCtr.append(ikCtr)
                lsJnt.append(jntEye)
                count -= 0.5
            # adjust position and size look at_________________________________
            mc.move(0,0,5,lsIkCtr[-1]['root'],r=True)
            # CREATE JNT Chain_________________________________________________
            for i, each in enumerate(lsJnt):
                if i ==0:
                    mc.parent(each,lsIkCtr[0]['c'])
                    upV = libRig.createObj(partial(mc.group, **{'n': nUpV, 'em': True}),father=lsIkCtr[0]['c'])
                    mc.move(0,2,0,upV,r=True)
                else:
                    mc.parent(each,lsJnt[0])
                    mc.parent(lsIkCtr[1]['root'],lsIkCtr[0]['c'])
                    mc.move(0,0,2,each,r=True)
            # CREATE IK HANDLE________________________________________________
            ikHdl =libRig.createObj(partial(mc.ikHandle, **{'n':nIkHandle ,'sj':lsJnt[0],'ee':lsJnt[1],'sol':'ikRPsolver'}),
            match=[lsIkCtr[-1]['c']],father=lsIkCtr[-1]['c'],attributs={"rotateX":0,"rotateY":0,"rotateZ":0,"snapEnable": 0,"visibility":0})
            mc.poleVectorConstraint(nUpV, ikHdl)
            mc.setAttr(ikHdl+".twist",abs(mc.getAttr(lsJnt[0]+".rotateZ")))
            # CREATE ATTRIB LOOK AT________________________________________________
            attribLookAt = mc.addAttr(lsIkCtr[-1]['c'],ln="lookAtMv",nn="LookAt Move", at="double",min=0.1,dv=1)
            mc.setAttr(lsIkCtr[-1]['c'] + ".lookAtMv", e=True, k=True)
            mc.connectAttr("%s.lookAtMv" %(lsIkCtr[-1]['c']), "%s.scaleZ" %(lsJnt[0]),force=True)


            # PARENT INFO AND TPL RIG_________________________________________
            mc.parent(dic['infoName'],nRIG)
            mc.parent(nRIG,self.nWorldGrp)
            # CONNECT TO WORLD________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=self.nWorld, slave=hookMaster)
            # PARENT__________________________________________________________
            mc.parent(master['root'],nHookMaster)
            # OFFSET MASTER____________________________________________________
            val = mc.getAttr(self.nWorld + '.scale')[0][0]
            mc.move(0,14*val,0,master['root'],os=True)


        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='sizeSk', at="enum", en="%s:%s:%s:%s:%s:%s"%(self.sizeCtr,self.sizeSk,self.typeSk,
                                    self.offsetIk,self.numb,self.numbSk ), k=True)
        mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)
        mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')),dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('masterTpl'),nMaster,type='string')
        mc.addAttr(dic['infoName'], shortName='ik',dt='string',multi=True) # add IK control
        [mc.setAttr(dic['infoName']+'.ik['+str(i)+']',each,type='string') for i, each in enumerate(nLsIk)]
        # add ik in sym attributes
        if self.side is not'':
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate([master['c']])]
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate([lsIkCtr[0]['c'],lsIkCtr[-1]['c']])]

        # ADD DICTIONARY ______________________________________________________
        dic['master'] = master['c']
        dic['lsIk'] = lsIkCtr

        return dic

        '''
        newName = RenameRig.NewNameRig(self,ElemTpl[0][0][0],Nomenclature.prefixName[0],Nomenclature.prefixName[47])
        mc.rename(ElemTpl[0][0][0],newName)
        ## Create connection Eyes
        mc.move(0,0,3.5,ElemTpl[4][0],r=True)
        recupadjEye=[]; recupadjEyeConnect=[]
        NameEye = RenameRig.NewNameStringOnly(self,Elem,NameElem,NameElem+"Ctr",0)
        NameRootEye = RenameRig.NewNameRig(self,Elem,Nomenclature.prefixName[0],Nomenclature.prefixName[31])
        NameConnectEye = Elem
        NameConnectRootEye = RenameRig.NewNameRig(self,Elem,Nomenclature.prefixName[0],Nomenclature.prefixName[43])
        NameConnectBufEye = RenameRig.NewNameRig(self,Elem,Nomenclature.prefixName[0],Nomenclature.prefixName[28])
        NamePolVEye = RenameRig.NewNameRig(self,Elem,Nomenclature.prefixName[0],Nomenclature.prefixName[4])
        NameUpVEye = RenameRig.NewNameRig(self,Elem,Nomenclature.prefixName[0],Nomenclature.prefixName[18])

        positions= mc.xform(newName, q=True, ws=True, translation=True); rotations = mc.xform(newName, q=True, ws=True, ro=True)
        mc.select(cl=True)
        ## Create Eyes Ctr
        adjEye = mc.joint(n=NameEye,p=positions,o=rotations,rad=1)
        CustomShapeJoint.FusionJointShape(self,newName,adjEye,0.2,ShapeType,Color,[0,0,0])
        CreateGroupadjEye = CustomShapeJoint.GrpP(self,adjEye,NameRootEye)
        CreateGroupBuf = CustomShapeJoint.GrpP(self,NameRootEye,NameConnectBufEye)
        mc.parent(CreateGroupBuf,newName)
        recupadjEye.append(adjEye)
        # create Attributs
        attribLookAt = mc.addAttr(adjEye,ln="lookAtMv",nn="LookAt Move", at="double",min=0.1,dv=1)
        mc.setAttr(adjEye + ".lookAtMv", e=True, k=True)
        mc.select(cl=True)
        # Create Eyes Jts
        adjEyeConnect = mc.joint(n=NameConnectEye,p=positions,o=rotations,rad=1)
        CustomShapeJoint.FusionJointShape(self,newName,adjEyeConnect,0.4,ShapeType,Color,[0,0,0])
        CreateGroup = CustomShapeJoint.GrpP(self,adjEyeConnect,NameConnectRootEye)
        mc.parent(CreateGroup,ElemTpl[1][0])
        mc.move(0,0,-3.5,CreateGroup,r=True)
        recupadjEyeConnect.append(adjEyeConnect)
        mc.select(cl=True)
        positions2= mc.xform(adjEyeConnect, q=True, ws=True, translation=True)
        count = 0
        recupJts =[]
        for each in range(2):
            RenameRig.NewNameStringOnly(self,Elem,NameElem,NameElem+"Ctr",0)
            adjEyeJts = mc.joint(n= RenameRig.NewNameStringOnly(self,NameUpVEye,NameElem,NameElem+"%s"%(count),0),p=[positions2[0],positions2[1],positions2[2]+count],o=rotations,rad=0.1)
            if count ==0:
                mc.parent(adjEyeJts,adjEyeConnect)
                mc.connectAttr("%s.lookAtMv" %(adjEye), "%s.scaleZ" %(adjEyeJts),force=True)
            else:
                mc.setAttr(adjEyeJts+ ".drawStyle",2)
                mc.setAttr(adjEyeJts+ ".displayHandle",1)
            count += 1
            mc.setAttr(adjEyeJts+ ".overrideEnabled", 1)
            mc.setAttr(adjEyeJts+ ".overrideDisplayType", 2)
            recupJts.append(adjEyeJts)
        NameIk = RenameRig.NewNameRig(self,adjEyeJts,Nomenclature.prefixName[18],"ik")
        CreateIk = mc.ikHandle(n =NameIk, sj = recupJts[0], ee = recupJts[-1], sol='ikRPsolver')
        mc.setAttr(CreateIk[0]+ ".snapEnable", 0)
        mc.setAttr(CreateIk[0]+ ".template", 1)
        mc.parent(CreateIk[0],adjEye); mc.setAttr(CreateIk[0]+ ".translate",0,0,0)

        positions2= mc.xform(adjEyeConnect, q=True, ws=True, translation=True)
        createPoleV = mc.spaceLocator(n=NamePolVEye)
        mc.move(positions2[0],positions2[1]+1,positions2[2],createPoleV,r=True)
        mc.setAttr(createPoleV[0]+ ".visibility", 0)
        mc.parent(createPoleV[0],adjEyeConnect)
        mc.poleVectorConstraint(createPoleV , CreateIk[0])
        mc.setAttr(CreateIk[0]+ ".twist", 90)
        mc.parent(NameConnectBufEye,adjEyeConnect)
        if side =="Left":
            mc.move(0.4,0,0,CreateGroup,r=True)
        else:
            mc.move(-0.4,0,0,CreateGroup,r=True)

        mc.delete(ElemTpl[2][0])
        mc.select(cl=True)
        '''
