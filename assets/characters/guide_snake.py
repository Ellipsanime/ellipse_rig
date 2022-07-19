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


class Snake(guide_info.Info):

    def __init__(self,name='snake',side='',selObj=None,obj=mc.ls(sl=True),numbIk=5,numbSk=20,numbCtr=10,sizeMast=(2,2,2),shpRotMaster=(0,0,0),
                 shpRotCtr=(90,0,0),sizeCtr=(1,1,1),typeShpMst="circle",**kwargs):
        guide_info.Info.__init__(self,name=name,side=side,selObj=selObj)
        self.selObj = selObj
        self.obj = obj
        self.typeShapeMast = typeShpMst
        color= lib_shapes.side_color(side=side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.valColorCtrMidIK = 'green'
        self.numbIk = 2
        self.numbPath = 5
        self.numb = numbIk
        self.numbCtr = numbCtr
        self.numbSk = numbSk
        self.offsetIk = (0,0,-5)
        self.typeShapeIkPath = "arrowSingle2"
        self.typeShapeIkPath2 = "star"
        self.typeShapeIk = "square"
        self.typeShapeCtr = "circle"
        self.offsetCtr =(0,0,-1)
        self.sizeMast = sizeMast
        self.sizeIk = (4,1.2,1.2)
        self.sizeCtrPath = (0.6,0.6,0.6)
        self.sizeMidIk = (0.5,0.5,0.5)
        self.sizeCtr = (0.3,0.3,0.3)
        self.sizeSk = (0.3,0.3,0.3)
        self.typeSk = (0.3,0.3,0.3)
        self.sizeRigAdd = (0.5,0.5,0.5)
        self.shpRotMaster = shpRotMaster
        self.shpRotIk = (90,0,0)
        self.shpRotCtrPath = (0,0,0)
        self.shpRotCtr = shpRotCtr
        self.rigAdd = "rigAdd"
        self.Ctr = "square"



    def createSnake(self):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = guide_info.Info.infoInc(self)
        # NAME________________________________________________________________
        nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nRoot1 = gloss.name_format(prefix=gloss.lexicon('tplRoot'),name=self.name,nFunc='cv'+str(1), nSide=self.side,incP=dic['incVal'])
        nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=gloss.lexicon('mtr'),nSide=self.side,incP=dic['incVal'])
        nRigAdd = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=gloss.lexicon('add'), nSide=self.side,incP=dic['incVal'])
        nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name, nSide=self.side,incP=dic['incVal'])
        nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nSide=self.side, incP=dic['incVal'])
        nLsIk = [gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nFunc='Ik',inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]

        # GET PARENT HOOK ELEMENT__________________________________________________________
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly +".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0]+'.infPart')+".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)

        # CREATE IK___________________________________________________________
        if mc.objExists(nRIG) is True:
            mc.parent(dic['infoName'],nRIG)
        else:
            RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
            surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
            hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
            master = libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast], color=self.valColorMasterCtr,
            size=self.sizeMast, rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
            attributs={"drawStyle": 2}, worldScale=self.nWorld)
            root1 = libRig.createObj(partial(mc.group, **{'n': nRoot1, 'em': True}), father=master['root'],attrInfo=dic['infoName'])
            rigAdd = libRig.createController(name=nRigAdd, shape=libRig.Shp([self.rigAdd], color=self.valColorCtr,
            size=self.sizeRigAdd,rotShp=self.shpRotMaster),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
            attributs={"drawStyle": 2}, worldScale=self.nWorld)
            mc.setAttr(rigAdd['root'] + '.segmentScaleCompensate', 0)

            # Create IkMid__________________________________________________________________
            lsRootMidIk = []
            lsCtrMidIk = []
            lsCtrIk = []
            lsKnot = []
            lsIkSk = []
            valMoveMidIk = [0, 0,round((float(8 - 1) / float(self.numb - 1)), 3)]

            for numb in range(self.numb):
                incValMove = ((numb * valMoveMidIk[0]), (numb * valMoveMidIk[1]), (numb * valMoveMidIk[2]))
                ''' names '''
                nRopeMidIk = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nFunc='midIk',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                rope = libRig.createController(name=nRopeMidIk,shape=libRig.Shp([self.typeShapeIk], color=self.valColorCtr,
                size=self.sizeMidIk, rotShp=self.shpRotCtr),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0, 0, incValMove[2]-3.5, rope['root'], ls=True)
                # add ctr IK and ctr knot
                if numb == 0 or numb == (self.numb - 1):
                    ''' names '''
                    nIkRope = gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nFunc='Ik',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                    nKnot = gloss.name_format(prefix=gloss.lexicon('tplCtr'),name=self.name,nFunc='knot',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                    ''' create '''
                    ikCtr = libRig.createController(name=nIkRope,shape=libRig.Shp([self.typeShapeIkPath], color=self.valColorMasterCtr,
                    size=self.sizeIk, rotShp=self.shpRotIk),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
                    attributs={"drawStyle": 2}, worldScale=self.nWorld)
                    mc.move(0, 0, incValMove[2]-3.5, ikCtr['root'], ls=True)
                    knotCtr = libRig.createController(name=nKnot,shape=libRig.Shp([self.typeShapeIk], color=self.valColorCtr,
                    size=self.sizeCtr, rotShp=self.shpRotCtr),match=self.selObj, attrInfo=dic['infoName'], father=rope['c'],
                    attributs={"drawStyle": 2}, worldScale=self.nWorld)
                    mc.move(0,0,0.5, knotCtr['root'], os=True)
                    if numb == 0: mc.move(0,0,-0.5, knotCtr['root'], os=True)
                    lsIkSk.append(ikCtr['sk'])
                    # ROOT SEGMENT SCALE COMPENSATE________________________________
                    mc.setAttr(ikCtr['root']+'.segmentScaleCompensate',0)
                    # DISCONNECT ATTRIBUTES CONNECTION______________________________
                    connectPairs = []
                    connect = mc.listConnections(mc.getAttr(ikCtr['c'] + ".sk"), plugs=True, connections=True, destination=False)
                    connectPairs.extend(zip(connect[1::2], connect[::2]))
                    [mc.disconnectAttr(srcAttr, desAttr) for srcAttr, desAttr in connectPairs]
                    mc.parent(ikCtr['sk'],ikCtr['c'])
                    mc.parent(rope['root'],ikCtr['c'])
                    lsKnot.append(knotCtr['c'])
                    lsCtrIk.append(ikCtr['c'])
                lsCtrMidIk.append(rope['c'])
                lsRootMidIk.append(rope['root'])

            # Create Ctr Path__________________________________________________________________
            valMoveCtrPath= [0, 0,round((float(8 - 1) / float(self.numbPath - 1)), 3)]
            lsCtrPath = []
            lsRootPath = []
            for numb in range(self.numbPath):
                incValMovePath = (((numb) * valMoveCtrPath[0]), ((numb) * valMoveCtrPath[1]), ((numb) * valMoveCtrPath[2]))
                nCtrPath = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc='path',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                ctrPath = libRig.createController(name=nCtrPath,shape=libRig.Shp([self.typeShapeIkPath2], color=self.valColorMasterCtr,
                size=self.sizeCtrPath, rotShp=self.shpRotCtrPath),match=self.selObj, attrInfo=dic['infoName'], father=master['c'],
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0, 0,incValMovePath[2]-3.5, ctrPath ['root'], ls=True)
                lsCtrPath.append(ctrPath['c'])
                lsRootPath.append(ctrPath['root'])

            # CREATE CURVE AND LOFT___________________________________________
            getCrv = lib_curves.createDoubleCrv(objLst=lsIkSk, axis='Z', offset=0.2)
            loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
            mc.skinCluster(lsIkSk,loft,tsb=1,mi=1)
            # PARENT INFO AND TPL RIG_________________________________________
            mc.parent(dic['infoName'],nRIG)
            mc.parent(nRIG,self.nWorldGrp)
            # CONNECT TO WORLD________________________________________________
            lib_connectNodes.connectMatrixAxis(driver=self.nFly, slave=hookMaster)
            # CREATE SA___________________________________________________
            # NAME _______________________________________________________________
            nSAWorldGrp = gloss.name_format(prefix=gloss.lexicon('tplSA') + 'World', name=self.name, nSide=self.side,incP=dic['incVal'])
            nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nSide=self.side, incP=dic['incVal'])
           # CREATE GRP SA___________________________________________________
            if mc.attributeQuery("tplSAWorld", node=master['c'], ex=True) is True:
                pass
            else:
                SAWorld = libRig.createObj(partial(mc.group, **{'n': nSAWorldGrp, 'em': True}), father=surfAttach,attrInfo=dic['infoName'], refObj=self.selObj)
                SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), father=SAWorld,refObj=self.selObj)
                mc.addAttr(master['c'], ln='tplSAWorld', dt="string")
                mc.setAttr(master['c'] + '.tplSAWorld', nSAWorldGrp, type="string")
                mc.addAttr(master['c'], ln='tplSA', dt="string")
                mc.setAttr(master['c'] + '.tplSA', nSAGrp, type="string")
            # CREATE ATTRIBUTES UPDATE TO SA WORLD____________________________
            lib_attributes.attrUpdateCtr(selObj=nSAWorldGrp, name=self.name, side=self.side)
            # CONNECT TO LOFT CTR PATH_________________________________________________
            lsSaCtr =[lib_connectNodes.nurbs_attach(lsObj=[loft,each], parentInSA=True, delLoc=True, parentSA=nSAGrp) for i,each in enumerate(lsRootPath)]
            lsSaCtrRename =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True) for each in lsSaCtr]
            mc.parent(lsRootPath[0],lsCtrIk[0])
            mc.parent(lsRootPath[-1],lsCtrIk[-1])
            # CONNECT TO LOFT_________________________________________________
            lSa = lib_connectNodes.surfAttach(selObj=[loft], lNumb=self.numb-2, parentInSA=True, parentSA=nSAGrp,delKnot=True)
            [mc.parent(lsRootMidIk[1:-1][i],each) for i,each in enumerate(lSa['sa'])]
            # CONNECT TO MASTER CONTROL_______________________________________
            lib_connectNodes.connectMatrixAxis(driver=master['c'], slave=SA)

            # Create Ctr__________________________________________________________________
            lsCtr = []
            lsRootCtr = []
            valMove = [0, 0,round((float(8 - 1) / float(self.numbCtr - 1)), 3)]
            for numb in range(self.numbCtr):
                incValMove = ((numb * valMove[0]), (numb * valMove[1]), (numb * valMove[2]))
                ''' names '''
                nRope = gloss.name_format(prefix=gloss.lexicon('tplCtr'),name=self.name,inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                rope = libRig.createController(name=nRope,shape=libRig.Shp([self.typeShapeCtr], color=self.valColorCtrMidIK,
                size=self.sizeCtr, rotShp=self.shpRotCtr),match=self.selObj, attrInfo=dic['infoName'], father=hookMaster,
                attributs={"drawStyle": 2}, worldScale=self.nWorld)
                mc.move(0, 0, incValMove[2]-3.5, rope['root'], ls=True)
                lsCtr.append(rope['c'])
                lsRootCtr.append(rope['root'])

            # CREATE CURVE AND LOFT2_______________________________________________
            nLoft2 = gloss.name_format(prefix=gloss.lexicon('tplLoft'), name=self.name, nFunc='ctr',nSide=self.side, incP=dic['incVal'])
            val = float(mc.getAttr(self.nWorld + '.scaleX'))
            concatSkMidIk = [mc.getAttr(each +'.sk') for each in lsCtrMidIk]
            concatSkMidIk.insert(0,mc.getAttr(lsKnot[0] +'.sk'))
            concatSkMidIk.append(mc.getAttr(lsKnot[-1] +'.sk'))
            getCrv = lib_curves.createDoubleCrv(objLst=concatSkMidIk, axis='Z', offset=0.1 * val,degree=1)
            loft2 = lib_curves.createLoft(name=nLoft2, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True
                                         , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
            mc.skinCluster(concatSkMidIk, loft2, tsb=1, mi=1)
            mc.setAttr(nLoft2+".overrideShading", 0)
            # CREATE ATTRIBUTES UPDATE TO LOFT _____________________________________
            mc.addAttr(nLoft2, ln='infPart', dt="string")
            mc.setAttr(nLoft2 + '.infPart', dic['infoName'], type="string")
            mc.addAttr(nLoft2, ln='updateSk', dt="string")
            mc.setAttr(nLoft2+ '.updateSk', 'partToDel', type="string")
            # CREATE SA___________________________________________________
            # CONNECT TO LOFT_________________________________________________
            for each in enumerate(lsRootCtr):
                if each[1] == lsRootCtr[0]:
                    mc.parent(each[1],lsCtrMidIk[0])
                elif each[1] == lsRootCtr[-1]:
                    mc.parent(each[1],lsCtrMidIk[-1])
                else:
                    saCtr =lib_connectNodes.nurbs_attach(lsObj=[loft2,each[1]], parentInSA=True, delLoc=True, parentSA=nSAGrp)
                    saCtrRename =gloss.renameSplit(selObj=saCtr[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True)
            # Create SK__________________________________________________________________
            lsSk = []
            valMove = [0, 0,round((float(8 - 1) / float(self.numbSk - 1)), 3)]
            for numb in range(self.numbSk):
                incValMove = ((numb * valMove[0]), (numb * valMove[1]), (numb * valMove[2]))
                ''' names '''
                nSk = gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.name,nFunc='sk',inc=str(numb+1),nSide=self.side,incP=dic['incVal'])
                ''' create '''
                sk =libRig.createObj(partial(mc.joint, **{'n':nSk}),match=self.selObj,father=hookMaster,attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
                mc.move(0, 0, incValMove[2]-3.5, sk, ls=True)
                lsSk.append(sk)
            lSaSk =[lib_connectNodes.nurbs_attach(lsObj=[loft2,each[1]], parentInSA=True, delLoc=True, parentSA=nSAGrp)for each in enumerate(lsSk)]
            lsSaRename =[gloss.renameSplit(selObj=each[0], namePart=['sa'], newNamePart=['tplSa'], reNme=True) for each in lSaSk]

            #parent rigAdd
            mc.parent(rigAdd['root'],lsCtrIk[-1])


            # ADJUST POSITION RIGADD___________________________________________________
            getPos = mc.xform(lsCtrIk[-1], q=True, ws=True, translation=True)
            getRot = mc.xform(lsCtrIk[-1], q=True, ws=True, rotation=True)
            mc.xform(rigAdd['root'], worldSpace=True, t=getPos)
            mc.xform(rigAdd['root'], worldSpace=True, ro=getRot)
            mc.setAttr(rigAdd['root']+'.translateY',2.5)

            # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
            mc.addAttr(dic['infoName'], ln='delPart', dt='string', multi=True)  # add master control
            mc.setAttr(dic['infoName'] + '.delPart[0]', nRIG, type='string')
            mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
            mc.addAttr(dic['infoName'], ln='sizeSk', at="enum",
                       en="%s:%s:%s:%s:%s:%s" % (self.sizeCtr, self.sizeSk, self.typeSk,
                                                 self.offsetIk, self.numb, self.numbSk), k=True, p='infoSK')
            mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)
            mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('masterTpl')), dt='string',
                       multi=True)  # add master control
            mc.setAttr(dic['infoName'] + ".%s[0]" % gloss.lexiconAttr('masterTpl'), nMaster, type='string')
            mc.addAttr(dic['infoName'], ln=str(gloss.lexiconAttr('rigAddTpl')),dt='string',multi=True) # add master control
            mc.setAttr(dic['infoName']+".%s[0]"%gloss.lexiconAttr('rigAddTpl'),rigAdd['c'],type='string')
            mc.addAttr(dic['infoName'], ln='ik', dt='string', multi=True)  # add IK control
            [mc.setAttr(dic['infoName'] + '.ik['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrIk)]
            mc.addAttr(dic['infoName'], shortName='ctrPath',dt='string',multi=True)
            [mc.setAttr(dic['infoName'] + '.ctrPath['+str(i)+']', each, type='string') for i, each in enumerate(lsCtrPath)]
            mc.addAttr(dic['infoName'], shortName='ctrMidIk',dt='string',multi=True)
            concatCtrMidIk = lsCtrMidIk
            concatCtrMidIk.insert(0, lsKnot[0])
            concatCtrMidIk.append(lsKnot[-1])
            [mc.setAttr(dic['infoName']+'.ctrMidIk['+str(i)+']',each,type='string') for i, each in enumerate(concatCtrMidIk)]
            mc.addAttr(dic['infoName'], shortName='ctr',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.ctr['+str(i)+']',each,type='string') for i, each in enumerate(lsCtr)]
            mc.addAttr(dic['infoName'], shortName='sk',dt='string',multi=True)
            [mc.setAttr(dic['infoName']+'.sk['+str(i)+']',each,type='string') for i, each in enumerate(lsSk)]
            # add ik in sym attributes
            if self.side is not '':
                # nSym = lib_attributes.attrSymetrie(selObj=nMaster, nameInfo=dic['infoName'])
                mc.setAttr(dic['infoName'] + '.sym[' + str(1) + ']', nMaster, type='string')
                lenSym = mc.getAttr(dic['infoName'] + '.sym', mi=True, s=True)
                [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrIk)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName'] + '.sym[' + str(i + lenSym) + ']', each, type='string') for i, each in enumerate(lsCtrPath)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(concatCtrMidIk)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                [mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',each,type='string') for i, each in enumerate(lsCtr)]
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                mc.setAttr(dic['infoName']+'.sym['+str(i+lenSym)+']',rigAdd['c'],type='string')

            dic['loft'] = loft
            dic['master'] = nMaster
            dic['lsCtrPath'] = lsCtrPath
            dic['lsCtrMidIk'] = concatCtrMidIk
            dic['lsCtr'] = lsCtr
            dic['lsSk'] = lsSk
            return dic
