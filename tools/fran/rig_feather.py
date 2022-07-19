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
reload(rig_world)
rig_world.RigWorld().createRig()  # instance class charGuide and run method createRig



class Feather(rig_world.RigWorld):

    def __init__(self, name='feather', tplInfo='tplInfo', hook = '',*args):
        rig_world.RigWorld.__init__(self)
        self.hook =hook
        self.name = name
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.typePin = "pinSimple"
        self.shpRotIk = (0,45,0)

    def createFeather(self):
        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        # CREATE RIG TO LISTE INFO_________________________________
        dicBuf = {}
        dicSk = {}
        lCtrl = []
        for i, eachTpl in enumerate(lsInfo):
            # GET INFO TO CREATE RIG________________________________
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
            lsTplIk =[mc.getAttr(eachTpl+'.ik[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ik', mi=True,s=True))]
            lsTplCtr =[mc.getAttr(eachTpl+'.ctr[%s]'%i) for i in range(mc.getAttr(eachTpl+'.ctr', mi=True,s=True))]
            # NAME________________________________________________________________
            nSwitchsRoot = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nSwitchsCtr = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('switch'), nSide=side,incP=incPart)
            nCvSpine = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nSide=side,incP=incPart)
            nArcLen = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nSide=side,incP=incPart)
            nArcLenStretch = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nFunc=gloss.lexicon('stretch'),nSide=side,incP=incPart)
            nNoTouch = gloss.name_format(prefix=gloss.lexicon('NoTouch'),name=self.name,nSide=side,incP=incPart)
            nHook = gloss.name_format(prefix=gloss.lexicon('rig'),name=self.name,nSide=side,incP=incPart)
            nCog = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('cog'),nFunc=self.name,nSide=side,incP=incPart)
            nDownIk = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('pelvis'),nFunc=self.name+'Ik',nSide=side,incP=incPart)
            nTopIk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=self.name+'Ik',nSide=side,incP=incPart)


            # FUSION TPL IK and CTR_______________________________________________
            concatIkFk = lsTplCtr
            concatIkFk.insert(0, lsTplIk[0])
            concatIkFk.insert(len(lsTplCtr) + 1, lsTplIk[-1])
            # ADJUST DEGRE WITH SUBDIVISE_________________________________________
            if len(concatIkFk) <= 2:
                degres = 1
                numbJtLen = len(concatIkFk) + 1
            elif len(concatIkFk) == 3:
                degres = 2
                numbJtLen = len(concatIkFk)
            else:
                degres = 3
                numbJtLen = len(concatIkFk) - 1
            # CREATE RIG CURVE____________________________________________________
            pos =[mc.xform(each2, q=True, ws=True, t=True) for each2 in concatIkFk]

            # HOOK________________________________________________________________
            hookTail = libRig.createObj(partial(mc.group, **{'n': nHook, 'em': True}), Match=self.nFly,father=self.nRig)
            # CREATE GRP NO TOUCH________________________________________________
            GrpNoTouch = libRig.createObj(partial(mc.group, **{'n': nNoTouch, 'em': True}),typeFunction={"group": {"visibility": 0}})
            # parentage group NoTouch avec HookSpine
            mc.parent(GrpNoTouch, hookTail)
            # COG___________________________________________________________________
            ctrCog = libRig.createController(name=nCog,shape=libRig.Shp([self.typeCircle],color=valColorMstCtr,size=(1.5,1.5,1.5)),match=master,father=hookTail)
            mc.setAttr(ctrCog["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)

            ################################# IK_###################################
            # CREATE ______________________________________________________________
            downIK = libRig.createController(name=nDownIk,shape=libRig.Shp([self.typeSquare],color=valColorCtrIK,size=(1,1,1),rotShp=self.shpRotIk),match=lsTplIk[0],father=None)
            mc.setAttr(downIK ["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
            mc.setAttr(downIK ["root"] + ".segmentScaleCompensate",0)
            topIK = libRig.createController(name=nTopIk,shape=libRig.Shp([self.typeSquare],color=valColorCtrIK,size=(1,1,1),rotShp=self.shpRotIk),match=lsTplIk[-1],father=None)
            mc.setAttr(topIK["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)

            # CREATE FK__________________________________________________________
            lsFkControl = []
            lsFkRoot = []
            lsFkControlAll = []
            if len(concatIkFk) > 2:
                for i, elemFK in enumerate(concatIkFk[0:-1]):
                    # NAME_______________________________________________________
                    nFk = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name+str(i+1), nSide=side,incP=incPart)
                    # CREATE_____________________________________________________
                    createFk = libRig.createController(name=nFk,shape=libRig.Shp([self.typeCircle],color=valColorCtr,size=(1,1,1)),match=[elemFK])
                    mc.setAttr(createFk["root"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
                    mc.setAttr(createFk["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
                    skCtr= gloss.renameSplit(selObj=createFk["sk"], namePart=['sk'], newNamePart=['jnt'], reNme=True)
                    lCtrl.append(createFk)
                    lsFkControl.append(createFk["c"])
                    lsFkRoot.append(createFk["root"])
                    lsFkControlAll.append(createFk["c"])
                # PARENT FK BETWEEN THEM_________________________________________
                [mc.parent(lsFkRoot[i + 1], lsFkControl[i]) for i, each in enumerate(lsFkRoot[1:])]
                mc.setAttr(lsFkRoot[0] + ".segmentScaleCompensate", 0)
            else:
                pass
            #lsFkControlAll.insert(0,ctrCog['c'])

            # CREATE ADD IK CONTROL MIDDLE_______________________________________
            # CREATE Loft To Parent ctr middle____________________________________
            getCrv = lib_curves.createDoubleCrv(objLst=concatIkFk, axis='X', offset=0.2)
            # ADD 2 POINTS ON CURVE______________________________________________
            lib_curves.crvSubdivide(crv=getCrv['crv'][0], subDiv=0, subDivKnot=1, degree=degres)
            lib_curves.crvSubdivide(crv=getCrv['crv'][1], subDiv=0, subDivKnot=1, degree=degres)
            cv1 = mc.rename(getCrv['crv'][0],gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name+'Cls1',nSide=side,incP=incPart))
            cv2 = mc.rename(getCrv['crv'][1],gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name+'Cls2',nSide=side,incP=incPart))
            recCv = mc.ls(cv1 + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(cv1 + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(cv1 + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            recCv = mc.ls(cv1 + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            recCv = mc.ls(cv2 + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(cv2 + '.cv[*]', fl=True)
            mc.delete(recCv[2],s=True)
            recCv = mc.ls(cv2 + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            recCv = mc.ls(cv2 + '.cv[*]', fl=True)
            mc.delete(recCv[-3],s=True)
            nLoftBase = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name+'Cls',nSide=side,incP=incPart)
            loftBase = libRig.createObj(partial(mc.loft, cv1, cv2,**{'n':nLoftBase, 'ch':True, 'u':True,'c':0,'ar':1,'d':3,'ss':0,'rn':0,'po':0,'rsn':True})
                                      , father=self.nWorldCenter, refObj=None, incPart=False, attributs={"visibility":0})

            mc.parent(cv1,self.nWorldCenter)
            mc.parent(cv2,self.nWorldCenter)

            # SKIN CVS____________________________________________________________
            lsSkin =(downIK ["sk"],topIK ["sk"])
            mc.skinCluster(lsSkin, cv1, tsb=True, mi=1)
            mc.skinCluster(lsSkin, cv2, tsb=True, mi=1)

            # RETURN SKIN CLUSTER________________________________________________
            ListHist = mc.listHistory(cv1, pdo=True)
            SkinCluster1 = mc.ls(ListHist, type="skinCluster")
            recCv1 = mc.ls(cv1 + '.cv[*]', fl=True)

            ListHist = mc.listHistory(cv2, pdo=True)
            SkinCluster2 = mc.ls(ListHist, type="skinCluster")
            recCv2 = mc.ls(cv2 + '.cv[*]', fl=True)

            adjustNumb = 1
            selDiv2 = int(math.ceil(float(len(recCv1))/adjustNumb))
            val = 0
            dictPointSk ={}
            for each2 in range(selDiv2):
                part = []
                for each in range(adjustNumb):
                    part.append(recCv1[each+val])
                val += adjustNumb
                dictPointSk[each2]= part
            val = [round(abs(-i/float(dictPointSk.keys()[-3])), 4) for i, each in enumerate(recCv1[1:-1])]
            invertVal = val[::-1]
            for i, each in enumerate(recCv1[1:-2]):
                mc.skinPercent(SkinCluster1[0], each, r=False,transformValue=[(lsSkin[0], invertVal[i]),(lsSkin[1],val[i])])
            for i, each in enumerate(recCv2[1:-2]):
                mc.skinPercent(SkinCluster2[0], each, r=False,transformValue=[(lsSkin[0], invertVal[i]),(lsSkin[1],val[i])])

            # ADJUST SKIN 2 LAST CV______________________________________________
            mc.skinPercent(SkinCluster1[0], recCv1[0], r=False,transformValue=(lsSkin[0], 1))
            mc.skinPercent(SkinCluster1[0], recCv1[-1], r=False,transformValue=(lsSkin[1], 1))
            mc.skinPercent(SkinCluster2[0], recCv2[0], r=False,transformValue=(lsSkin[0], 1))
            mc.skinPercent(SkinCluster2[0], recCv2[-1], r=False,transformValue=(lsSkin[1], 1))


            ########
            # CREATE ADD IK CONTROL_______________________
            lsAddIk = []
            lsAddIk.extend(lsFkControlAll)
            lsAddIk.append(topIK["c"])
            lsRootIkAdd =[]
            sclWorld = mc.getAttr("tpl_WORLD"+".scaleX")
            for k, each in enumerate(lsAddIk):
                # NAME_______________________________________________________
                nIkAdd = gloss.name_format(prefix=gloss.lexicon('c'),name=self.name,nFunc=gloss.lexicon('add')+'Ik'+str(k+1),nSide=side,incP=incPart)
                # CREATE_____________________________________________________
                createIkAdd = libRig.createController(name=nIkAdd,shape=libRig.Shp([self.typePin],color=valColorCtrIK,size=(1*sclWorld,1*sclWorld,1*sclWorld),rotShp=(0,90,0)),match=[each])
                mc.setAttr(createIkAdd["c"] + ".rotateOrder",libRgPreset.configAxis(mb="rOrdSpine",side=side)["rOrdFk"], l=False, k=True)
                # ADD SWITCH TO ADD IK CONTROL MIDDLE_________________________________
                lsRootIkAdd.append(createIkAdd["root"])
            lsRootIkAdd.append(loftBase)

            # CREATE SA_______________________
            lSa = lib_connectNodes.nurbs_attach(lsObj =lsRootIkAdd,parentInSA=True,delLoc=True)
            mc.parent(lSa[0],self.nSa)
            [mc.parent(each,lSa[i]) for i, each in enumerate(lSa[1:])]
            # CREATE BUF TO DRIVE FK_______________________
            lsBuf =[]
            for k, each in enumerate(lSa):
                nFkBuf = gloss.name_format(prefix=gloss.lexicon('buf'),name=self.name+str(k+1), nSide=side,incP=incPart)
                fkBuf =libRig.createObj(partial(mc.group, **{'n': nFkBuf, 'em': True}), Match=None,father=self.nSa)
                mc.connectAttr(each + '.translate', fkBuf + '.translate', f=True)
                mc.connectAttr(each + '.rotate', fkBuf + '.rotate', f=True)
                lsBuf.append(fkBuf)

            [mc.parent(each,lsBuf[i]) for i, each in enumerate(lsBuf[1:])]

            lsTamp =[]
            for k, each in enumerate(lSa):
                nFkTamp = gloss.name_format(prefix='tamp',name=self.name+str(k+1), nSide=side,incP=incPart)
                fktamp =libRig.createObj(partial(mc.group, **{'n': nFkTamp, 'em': True}), Match=[lsBuf[k]],father=lsBuf[k])
                mc.setAttr(fktamp +'.translateX',0);mc.setAttr(fktamp +'.translateY',0);mc.setAttr(fktamp +'.translateZ',0)
                mc.setAttr(fktamp +'.rotateX',0);mc.setAttr(fktamp +'.rotateY',0);mc.setAttr(fktamp +'.rotateZ',0)
                lsTamp.append(fktamp)


            # HIDE IK HANDLE AND CURVE___________________________
            mc.setAttr(cv1 +".visibility",0)
            mc.setAttr(cv2 +".visibility",0)


            ############################ Parentage et connection elements ###########################################

            # contraindre premier fk avec ctr Cog
            mc.parent(downIK['root'], ctrCog['c'])
            mc.parent(topIK['root'], ctrCog['c'])
            #Adjust Hierachie
            for k, each in enumerate(lsTamp):
                mc.parent(each,self.nSa)

            mc.parent(lsFkRoot[0],lsBuf[0])
            mc.parent(lsTamp[0],lsFkControl[0])

            for k, each in enumerate(lsFkRoot[1:]):
                mc.parent(lsBuf[k+1],lsTamp[k])
                mc.parent(each,lsBuf[k+1])
                mc.parent(lsTamp[k+1],lsFkControl[k+1])

            for k, each in enumerate(lsTamp):
                mc.parent(lsRootIkAdd[k],each)

            mc.parent(lsBuf[-1],lsTamp[-2])
            mc.parent(lsTamp[-1],lsBuf[-1])
            # SNAP CVS____________________________________________
            # MASTER______________________________________________
            lib_shapes.snapShpCv(shpRef=master, shpTarget=nCog)
            # IK______________________________________________
            [lib_shapes.snapShpCv(shpRef=each, shpTarget=[downIK['c'],topIK['c']][i]) for i, each in enumerate(lsTplIk)]
            # FK______________________________________________
            [lib_shapes.snapShpCv(shpRef=concatIkFk[0:-1][i], shpTarget=each) for i, each in enumerate(lsFkControl)]

            mc.setAttr(downIK['root'] +".visibility",0)
            '''
            # SET SKIN_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'), name=gloss.lexicon('skin'), incP=incPart)
            if not mc.objExists(nSetPart): mc.sets(n=nSetPart, em=True)
            for i, each in enumerate(lsSk):
                mc.sets(each, edit=True, forceElement=nSetPart)
            '''
            '''
            # LIST HOOK IN TPL INFO_________________________________________
            lsHooks = lsAnchor[1:]
            if mc.objExists(eachTpl+'.%s'%gloss.lexiconAttr('listHooks')):
                pass
            else:
                mc.addAttr(eachTpl, ln=gloss.lexiconAttr('listHooks'),dt='string',multi=True) # add Buf
            [mc.setAttr(eachTpl+'.%s['%gloss.lexiconAttr('listHooks')+str(i)+']',each,type='string') for i, each in enumerate(lsHooks)]
            '''

            # ATTRIBUTES TO CONTROL GRP________________________________________________
            cogCtr = ctrCog["c"]
            lsIkCtr = [downIK['c'],topIK['c']]
            lsFkCtr = lsFkControl
            # NAME CG_____________________________________________
            cgMaster = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgMaster'),nSide=side,incP=incPart)
            cgSwitch = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgSwitch'),nSide=side,incP=incPart)
            cgIk = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgIk'),nSide=side,incP=incPart)
            cgFk = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgFkMb'),nSide=side,incP=incPart)

            if mc.objExists(eachTpl+'.%s'%cgMaster):
                pass
            else:
                mc.addAttr(eachTpl, ln=cgMaster,dt='string',multi=True) # add Cg Master
                #mc.addAttr(eachTpl, ln=cgSwitch,dt='string',multi=True) # add Cg switch
                mc.addAttr(eachTpl, ln=cgIk,dt='string',multi=True) # add Cg ik
                mc.addAttr(eachTpl, ln=cgFk,dt='string',multi=True) # add Cg fk
            mc.setAttr(eachTpl+'.%s['%(cgMaster) +str(0)+']',cogCtr,type='string')
            #mc.setAttr(eachTpl+'.%s['%(cgSwitch) +str(0)+']',createSwitchs,type='string')
            [mc.setAttr(eachTpl+'.%s['%(cgIk) +str(i)+']',each,type='string') for i, each in enumerate(lsIkCtr)]
            [mc.setAttr(eachTpl+'.%s['%(cgFk) +str(i)+']',each,type='string') for i, each in enumerate(lsFkCtr)]

            # PARENT HOOK WITH RIG MEMBER________________________________________________
            #mc.parent(hookTail,self.hook)

        return dicBuf, dicSk, lCtrl
