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

    def __init__(self, name='default', side='', selObj=None, incVal=None,**kwargs):
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


class FeatherGuide(Info):

    def __init__(self,name='default',side='',selObj=None,obj=mc.ls(sl=True),numb=1,numbSk=1,offsetIk=(0,4,0),shpRotIk=(0,0,0)
                 ,sizeMast=(2,2,2),sizeIk=(1.2,1.2,1.2),shpRotMaster=(0,0,0),shpRotCtr=(0,0,0),sizeCtr=(1,1,1),sizeSk=(0.7,0.7,0.7),
                 typeBox="cube",typeShpMst="circle",typeShpIk="square",typeShp="circle", incVal=None,degree=None,featherLineBase=None,
                 featherLineBack=None,featherLineAim=None, **kwargs):
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

        '''
        self.countLines = countLines
        self.countFeathers = countFeathers
        self.Part = 'Line%s'%(self.countLines)+'Nb%s'%(self.countFeathers)
        '''

    def template(self,dicLinesBase=None,dicLinesBack=None,dicLinesAim=None):
        '''
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        # GET SCALE WORLD__________________________
        valInfo = mc.getAttr(self.nWorld+ '.scale')[0][0]
        valTmp = 1
        # GET TEMPORARY SCALE WORLD BY 1__________________________
        mc.setAttr(self.nWorld+ '.scaleX',1)
        mc.setAttr(self.nWorld+ '.scaleY',1)
        mc.setAttr(self.nWorld+ '.scaleZ',1)

        dic = Info.infoInc(self, self.incVal)

        nRIGGlobal = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name,nFunc='global', nSide=self.side,incP=dic['incVal'])
        RIGGlobal = libRig.createObj(partial(mc.group, **{'n': nRIGGlobal, 'em': True}))

        listLineLocArm = []
        print dicLinesBase
        for key,values in sorted(dicLinesBase.items()):
            listLineLoc = []
            for j, each in enumerate(values):
                listLineLoc.append(each)
            listLineLocArm.append(listLineLoc)


        listMaster = []
        listMaster2 = []
        dicIkBase = {}
        dicIkBack = {}
        dicFk = {}
        dicSk = {}
        for key,values in sorted(dicLinesAim.items()):
            lsIkBase = []
            lsIkBack = []
            lsFkFeather = []
            lsSkFeather = []
            listMasterInter =[]
            for j, each in enumerate(values):
                nPart = 'Nb%s'%(j+1)+'Line%s'%(key)

                # CONTROLS IK_________________________________________
                # NAME________________________________________________________________
                nRIG = gloss.name_format(prefix=gloss.lexicon('tplRig'),name=self.name,nFunc=nPart, nSide=self.side,incP=dic['incVal'])
                nSurfAttach = gloss.name_format(prefix=gloss.lexicon('tplSurfAttach'),name=self.name,nFunc=nPart, nSide=self.side,incP=dic['incVal'])
                nLoft = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name,nFunc=nPart, nSide=self.side,incP=dic['incVal'])
                nHookMaster = gloss.name_format(prefix=gloss.lexicon('tplHook'), name=self.name,nFunc=nPart,nSide=self.side, incP=dic['incVal'])
                nMaster = gloss.name_format(prefix=gloss.lexicon('tpl'),name=self.name,nFunc=nPart+'Mtr',nSide=self.side,incP=dic['incVal'])
                nLsIk = [gloss.name_format(prefix=gloss.lexicon('tplIk'),name=self.name,nFunc=nPart+'Ik',inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]
                nLsIkSk = [gloss.name_format(prefix=gloss.lexicon('tplSk'),name=self.name,nFunc=nPart+'Ik',inc=str(knot + 1),nSide=self.side,incP=dic['incVal']) for knot in range(self.numbIk)]

                RIG = libRig.createObj(partial(mc.group, **{'n': nRIG, 'em': True}))
                surfAttach = libRig.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}),father=RIG,attrInfo=dic['infoName'])
                hookMaster = libRig.createObj(partial(mc.group, **{'n': nHookMaster, 'em': True}),father=RIG)
                master = libRig.createController(name=nMaster,shape=libRig.Shp([self.typeShapeMast],color=self.valColorMasterCtr,
                        size=self.sizeMast,rotShp=self.shpRotMaster),match=None,attrInfo=dic['infoName'],addBuf=False,attributs={"drawStyle": 2},worldScale=self.nWorld)

                listMaster.append(master['c'])
                listMasterInter.append(master['c'])

                shapeMst = mc.listRelatives(master['c'], s=True)[0]
                mc.setAttr(shapeMst + ".overrideEnabled", True)
                mc.setAttr(shapeMst + '.overrideRGBColors', 1)
                if self.side == 'L':
                    mc.setAttr(shapeMst + '.overrideColorRGB', 1, (float(int(key)-1)/5), (float(int(key)-1)/5))
                else:
                    mc.setAttr(shapeMst + '.overrideColorRGB', (float(int(key)-1)/5), (float(int(key)-1)/5),1)

                # CREATE U Attributes_______________________________________________________
                mc.addAttr(master['c'], ln="UVal", at="double",dv=mc.getAttr(listLineLocArm[int(key)-1][j]+'.U'))
                mc.setAttr(master['c'] + ".UVal", e=True, k=True)

                # CREATE IK________________________________________________________
                lsIk = []
                for knot in range(self.numbIk):
                    if knot == 0  and self.name =='arm':
                        shpForm = 'circle'
                    elif knot == 0  and self.name =='leg':
                        shpForm = 'circle'
                    else:
                        shpForm = self.typeShapeIk
                    ikCtr = libRig.createController(name=nLsIk[knot], shape=libRig.Shp([shpForm],color=self.valColorCtrIK,size=self.sizeIk,rotShp=self.shpRotIk),
                            match=None,father=master['c'],attrInfo=dic['infoName'],addBuf=False,worldScale=self.nWorld)

                    shapeIk = mc.listRelatives(ikCtr['c'], s=True)[0]
                    mc.setAttr(shapeIk + ".overrideEnabled", True)
                    mc.setAttr(shapeIk + '.overrideRGBColors', 1)
                    if self.side == 'L':
                        mc.setAttr(shapeIk + '.overrideColorRGB', 1, (float(int(key)-1)/5), (float(int(key)-1)/5))
                    else:
                        mc.setAttr(shapeIk + '.overrideColorRGB', (float(int(key)-1)/5), (float(int(key)-1)/5),1)

                    # OFFSET IK____________________________________________________
                    valK = knot
                    mc.move(self.offsetIk[0]*valK,self.offsetIk[1]*valK,self.offsetIk[2]*valK,ikCtr['root'],os=True)
                    # ROOT SEGMENT SCALE COMPENSATE________________________________
                    mc.setAttr(ikCtr['root']+'.segmentScaleCompensate',0)
                    # DISCONNECT ATTRIBUTES CONNECTION______________________________
                    connectPairs = []
                    connect = mc.listConnections(mc.getAttr(ikCtr['c'] + ".sk"), plugs=True, connections=True, destination=False)
                    connectPairs.extend(zip(connect[1::2], connect[::2]))
                    [mc.disconnectAttr(srcAttr, desAttr) for srcAttr, desAttr in connectPairs]
                    mc.parent(ikCtr['sk'],ikCtr['c'])
                    lsIk.append(ikCtr['c'])
                lsIkBack.append(lsIk[-1])
                lsIkBase.append(lsIk[0])
                # CREATE CURVE AND LOFT___________________________________________
                getCrv = lib_curves.createDoubleCrv(objLst=nLsIkSk, axis='Z', offset=0.2)
                loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True,degree=None)
                mc.skinCluster(nLsIkSk,loft,tsb=1,mi=1)
                # PARENT TPL RIG_________________________________________
                mc.parent(nRIG,nRIGGlobal)
                # CONNECT TO WORLD________________________________________________
                lib_connectNodes.connectMatrixAxis(driver=self.nWorld, slave=hookMaster)
                # PARENT__________________________________________________________
                mc.parent(master['root'],nHookMaster)

                # CONTROLS FK_________________________________________
                # NAME _______________________________________________________________
                nSAWorldGrp = gloss.name_format(prefix=gloss.lexicon('tplSA') + 'World', name=self.name,nFunc=nPart, nSide=self.side,incP=dic['incVal'])
                nSAGrp = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name,nFunc=nPart, nSide=self.side, incP=dic['incVal'])

                nLsCtr = [gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name,nFunc=nPart, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numb[int(key)-1])]


                nLsCtrNew = [gloss.name_format(prefix=gloss.lexicon('tpl'), name=self.name,nFunc=nPart+'Fk', inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numb[int(key)-1])]
                nLsCtrSk = [gloss.name_format(prefix=gloss.lexicon('tplSk'), name=self.name,nFunc=nPart, inc=str(val + 1),nSide=self.side, incP=dic['incVal']) for val in range(self.numb[int(key)-1])]
                # CREATE CTR__________________________________________________________
                if mc.objExists(nSAWorldGrp) is True:
                    pass
                else:
                    # CREATE GRP SA___________________________________________________
                    SAWorld = libRig.createObj(partial(mc.group, **{'n': nSAWorldGrp, 'em': True}), father=nSurfAttach, attrInfo=dic['infoName'],refObj=self.selObj)
                    SA = libRig.createObj(partial(mc.group, **{'n': nSAGrp, 'em': True}), father=SAWorld, refObj=self.selObj)
                    if mc.attributeQuery("tplSAWorld", node=nMaster, ex=True) is True:
                        pass
                    else:
                        mc.addAttr(nMaster, ln='tplSAWorld', dt="string")
                        mc.setAttr(nMaster + '.tplSAWorld', nSAWorldGrp, type="string")
                        mc.addAttr(nMaster, ln='tplSA', dt="string")
                        mc.setAttr(nMaster + '.tplSA', nSAGrp, type="string")
                    # CREATE ATTRIBUTES UPDATE TO SA WORLD____________________________
                    lib_attributes.attrUpdateCtr(selObj=nSAWorldGrp, name=self.name, side=self.side)
                    # CONNECT TO LOFT_________________________________________________
                    lSa = lib_connectNodes.surfAttach(selObj=[nLoft], lNumb=self.numb[int(key)-1], parentInSA=True, parentSA=nSAGrp,delKnot=True)

                    # CREATE CTR______________________________________________________
                    lsFK = []
                    for val in range(self.numb[int(key)-1]):
                        if self.side == 'L':
                            rotshape = self.shpRotCtr
                        else:
                            rotshape = (180,0,0)
                        ctr = libRig.createController(name=nLsCtr[val],shape=libRig.Shp([self.typeShape], color=self.valColorCtr,
                             size=self.sizeCtr,rotShp=rotshape),match=lSa['sa'][val], attrInfo=dic['infoName'], father=lSa['sa'][val],worldScale=self.nWorld)

                        shape = mc.listRelatives(ctr['c'], s=True)[0]
                        mc.setAttr(shape + ".overrideEnabled", True)
                        mc.setAttr(shape + '.overrideRGBColors', 1)
                        if self.side == 'L':
                            mc.setAttr(shape + '.overrideColorRGB', 1, (float(int(key)-1)/5), (float(int(key)-1)/5))
                        else:
                            mc.setAttr(shape + '.overrideColorRGB', (float(int(key)-1)/5), (float(int(key)-1)/5),1)
                        mc.setAttr(ctr['root'] + '.rotateZ', -90)  # adjust orientation
                        mc.setAttr(ctr['root'] + '.rotateY', 180)  # adjust orientation
                        mc.rename(ctr['c'],nLsCtrNew[val])
                        lsFK.append(nLsCtrNew[val])
                    lsFkFeather.append(lsFK)
                    # CONNECT TO MASTER CONTROL_______________________________________
                    lib_connectNodes.connectMatrixAxis(driver=nMaster, slave=SA)
                # FUSION SK: IK and CTR_______________________________________________
                nConcatSk = nLsCtrSk
                nConcatSk.insert(0, nLsIkSk[0])
                nConcatSk.insert(len(nLsCtrSk) + 1, nLsIkSk[-1])

                # CONTROLS SK_________________________________________
                # NAME _______________________________________________________________
                nSAGrpSk = gloss.name_format(prefix=gloss.lexicon('tplSA'), name=self.name, nFunc=nPart+'Sk',nSide=self.side,incP=dic['incVal'])
                nLoft2 = gloss.name_format(prefix=gloss.lexicon('tplLoft'),name=self.name, nFunc=nPart+'Sk',nSide=self.side,incP=dic['incVal'])
                nLsBox = [gloss.name_format(prefix='box', name=self.name, inc=str(val + 1), nFunc=nPart+'Sk',nSide=self.side, incP=dic['incVal']) for val in range(self.numbSk)]
                # CREATE GRP SA_______________________________________________________
                SA = libRig.createObj(partial(mc.group, **{'n': nSAGrpSk, 'em': True}),father=None,attrInfo=dic['infoName'],refObj=self.selObj)
                # CREATE ATTRIBUTES UPDATE TO SA _____________________________________
                mc.addAttr(nSAGrpSk, ln='updateSk', dt="string")
                mc.setAttr(nSAGrpSk + '.updateSk', 'partToDel', type="string")
                # CREATE CURVE AND LOFT_______________________________________________
                #val = float(mc.getAttr(self.nWorld + '.scaleX'))
                getCrv = lib_curves.createDoubleCrv(objLst=nConcatSk, axis='X', offset=0.2 * valTmp)
                loft = lib_curves.createLoft(name=nLoft2, objLst=getCrv['crv'], father=None, deleteCrv=True,degree=self.degree
                                             , attributs={"visibility":1,"overrideEnabled":1,"overrideDisplayType":2})
                mc.skinCluster(nConcatSk, loft, tsb=1, mi=1)
                mc.setAttr(nLoft2+".overrideShading", 0)
                # CREATE ATTRIBUTES UPDATE TO LOFT _____________________________________
                mc.addAttr(nLoft2, ln='infPart', dt="string")
                mc.setAttr(nLoft2 + '.infPart', dic['infoName'], type="string")
                mc.addAttr(nLoft2, ln='updateSk', dt="string")
                mc.setAttr(nLoft2+ '.updateSk', 'partToDel', type="string")
                # CONNECT TO LOFT_____________________________________________________
                lSa = lib_connectNodes.surfAttach(selObj=[nLoft2], lNumb=self.numbSk,parentInSA=True, parentSA=nSAGrpSk,delKnot=True)
                if self.degree == 1:
                    for i, eachU in enumerate(lSa['loc']):
                        mc.setAttr(eachU +'.U',(0.5+i))
                # CREATE SK___________________________________________________________
                lsSk = []
                for val in range(self.numbSk):
                    scaleWX= 1
                    scaleSk = 1
                    # ADJUST TYPE BOX_________________________________________________
                    ctr =libRig.createObj(partial(mc.joint, **{'n': nLsBox[val]}),shape= libRig.Shp([self.typeSk],
                        size= (scaleWX*0.4,scaleWX*self.sizeSk[1]*0.4,scaleWX*self.sizeSk[2]*0.4)),match=lSa['sa'][val],
                                          father=lSa['sa'][val],refObj=self.selObj,attributs={"drawStyle": 2,"overrideEnabled": 1,"visibility": 0})
                    shp = mc.listRelatives(ctr, s=True)[0]
                    mc.setAttr(shp+".overrideDisplayType", 2)
                    lsSk.append(str(ctr))
                lsSkFeather.append(lsSk)
                # CREATE ATTRIBUTES VIS TO LOCATOR Sk_________________________________
                mc.addAttr(nMaster, ln='visSK', at="enum", en="%s:%s" % ('Off', 'On'), k=True)
                mc.setAttr(nMaster + '.visSK', e=True, cb=True)
                [mc.connectAttr(nMaster + '.visSK',eachLoc+ '.visibility',f=True) for eachLoc in lSa['loc']]
                lib_attributes.lockAndHideAxis(lSa['loc'], transVis=True, rotVis=True, sclVis=True)
                [mc.setAttr(eachLoc+ '.V',l=True, k=False,cb=False) for eachLoc in lSa['loc']]

                # PARENT______________________________________________________________
                mc.parent(nSAGrpSk, nSAGrp)
                mc.parent(nLoft2,nSAWorldGrp)

                # MATCH FEATHERS TO BASE LINES__________________________________
                getPos = mc.xform(each, q=True, ws=True, translation=True)
                getRot = mc.xform(each, q=True, ws=True, rotation=True)
                mc.xform(master['root'], worldSpace=True, t=getPos)
                mc.xform(master['root'], worldSpace=True, ro=getRot)
                #mc.parent(master['root'],each)
                mc.parentConstraint(each,master['root'],mo=True)


            dicIkBase['Ik%s'%(int(key))] = lsIkBase
            dicIkBack['Ik%s'%(int(key))] = lsIkBack
            dicFk['Fk%s'%(int(key))] = lsFkFeather
            dicSk['Fk%s'%(int(key))] = lsSkFeather
            listMaster2.append(listMasterInter)

        listIkBase = []
        for key,values in sorted(dicIkBase.items()):
            for j, each in enumerate(values):
                listIkBase.append(each)

        listIkBack = []
        for key,values in sorted(dicIkBack.items()):
            for j, each in enumerate(values):
                listIkBack.append(each)

        listIkConcat = []
        for a, b in zip(listIkBase, listIkBack):
            listIkConcat.append((a,b))

        listFk = []
        for key,values in sorted(dicFk.items()):
            for j, each in enumerate(values):
                listFk.append(each)

        listSk = []
        for key,values in sorted(dicSk.items()):
            for j, each in enumerate(values):
                listSk.append(each)

        # ADD ATTRIBUTES ON TEMPLATE INFO _____________________________________
        mc.addAttr(dic['infoName'], ln='delPart',dt='string',multi=True) # add master control
        mc.setAttr(dic['infoName']+'.delPart[0]',nRIGGlobal,type='string')
        mc.addAttr(dic['infoName'], longName='infoSK', numberOfChildren=1, attributeType='compound')
        mc.addAttr(dic['infoName'], ln='sizeSk', at="enum", en="%s:%s:%s:%s:%s:%s"%(self.sizeCtr,self.sizeSk,self.typeSk,
                                    self.offsetIk,self.numb,self.numbSk), k=True, p='infoSK')
        mc.setAttr(dic['infoName'] + '.sizeSk', e=True, cb=True)

        mc.addAttr(dic['infoName'], shortName='masterTpl',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.masterTpl['+ str(i)+']',each,type='string') for i, each in enumerate(listMaster)]

        mc.addAttr(dic['infoName'], shortName='ik',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.ik['+ str(i)+']',each,type='string') for i, each in enumerate(listIkConcat)]
        mc.addAttr(dic['infoName'], shortName='ctr',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.ctr['+ str(i)+']',each,type='string') for i, each in enumerate(listFk)]

        mc.addAttr(dic['infoName'], shortName='sk',dt='string',multi=True)
        [mc.setAttr(dic['infoName']+'.sk['+ str(i)+']',each,type='string') for i, each in enumerate(listSk)]

        # ADD ATTRIBUTES SYM _____________________________________
        if self.side is not'':
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            [mc.setAttr(dic['infoName']+'.sym['+str(lenSym+i)+']',each,type='string') for i,each in enumerate(listMaster)]

            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            for key,values in sorted(dicIkBase.items()):
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                for j, each in enumerate(values):
                    mc.setAttr(dic['infoName']+'.sym['+str(lenSym+j)+']',each,type='string')

            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            for key,values in sorted(dicIkBack.items()):
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                for j, each in enumerate(values):
                    mc.setAttr(dic['infoName']+'.sym['+str(lenSym+j)+']',each,type='string')

            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            for key,values in sorted(dicFk.items()):
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                for j, each in enumerate(values):
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    for k, each2 in enumerate(each):
                        mc.setAttr(dic['infoName']+'.sym['+str(lenSym+k)+']',each2,type='string')

            '''
            lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
            for key,values in sorted(dicSk.items()):
                lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                for j, each in enumerate(values):
                    lenSym = mc.getAttr(dic['infoName']+'.sym', mi=True,s=True)
                    for k, each2 in enumerate(each):
                        mc.setAttr(dic['infoName']+'.sym['+str(lenSym+k)+']',each2,type='string')
            '''

        # ADD NAME MIRROR TO ATTRIBUT MIRROR _____________________________________
        splitObj = dic['infoName'].split("_")
        if splitObj[-1] == self.side:
            if "tplInfo" in dic['infoName']:
                update = mc.attributeQuery("update",node=dic['infoName'], listEnum=1)[0]
                symInfo =dic['infoName'].split("_")
                nSym = "empty"
                if update.split(":")[1] == 'L':
                    symInfo[-1]='R'
                    nSym = "_".join(symInfo)
                elif update.split(":")[1] == 'R':
                    symInfo[-1]='L'
                    nSym = "_".join(symInfo)
            if mc.objExists(nSym) == True :
                mc.connectAttr(nSym+'.moduleMirror', dic['infoName']+'.moduleMirror', force=True)

        '''
        listLinesBack = []
        for key,values in sorted(dicLinesBack.items()):
            for j, each in enumerate(values):
                listLinesBack.append(each)

        for i, each in enumerate(listLinesBack):
            mc.parentConstraint(each,mc.getAttr(listIkBack[i]+'.root'),mo=True)
        '''

        # PARENT INFO _________________________________________
        mc.parent(dic['infoName'],nRIGGlobal)
        # PARENT TPL RIG_________________________________________
        mc.parent(nRIGGlobal,self.nWorldGrp)
        # HIDE VISIBILITY_________________________________________
        for key,values in sorted(dicLinesBack.items()):
            for j, each in enumerate(values):
                mc.setAttr(each+'.visibility',0)


        # CONNECT U VALUE_________________________________________
        for i,eachLine in enumerate(listLineLocArm):
            for j,each in enumerate(eachLine):
                mc.connectAttr(listMaster2[i][j]+'.UVal',each+'.U')
                mc.setAttr(each+'.visibility',0)


        '''
        for i, each in enumerate(listMaster):
            mc.setAttr(mc.listRelatives(each, shapes=True)[0]+'.visibility',0)
        '''



        for key,values in sorted(dicIkBase.items()):
            for j, each in enumerate(values):
                mc.setAttr(mc.listRelatives(each, shapes=True)[0]+'.visibility',0)

        # GET PARENT HOOK ELEMENT__________________________________________________________
        if self.obj == []: # check if objRef is empty
            mc.connectAttr(self.nInfoFly +".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)
        else:
            mc.connectAttr(mc.getAttr(self.obj[0]+'.infPart')+".%s"%gloss.lexiconAttr('attrChild'),dic['infoName']+".%s"%gloss.lexiconAttr('attrParent'),f=True)

        # GET SCALE WORLD SET __________________________
        mc.setAttr(self.nWorld+ '.scaleX',valInfo)
        mc.setAttr(self.nWorld+ '.scaleY',valInfo)
        mc.setAttr(self.nWorld+ '.scaleZ',valInfo)
        print 'ZIZILOOOOL'





class Feather(FeatherGuide):

    def __init__(self,name='feather',side='',selObj=None,lsNbfk =(2,3,3),numb=1,numbSk=1,offsetIk=(0,3,0),offsetT=(0,6.5,0),offsetR=(-90,0,0),countLines=None,countFeathers=None,**kwargs):
        FeatherGuide.__init__(self, name=name, side=side, selObj=selObj,lsNbfk=lsNbfk, numb=numb, numbSk=numbSk,countLines=countLines,countFeathers=countFeathers)
        self.name = name
        self.offsetIk = offsetIk
        self.sizeMast = (0.1,0.1,0.2)
        self.sizeIk = (0.3,0.3,0.1)
        self.sizeCtr = (0.3,0.3,0.1)
        self.sizeSk = (0.3,0.3,0.3)
        self.offsetMasterTr = offsetT
        self.offsetMasterRo = offsetR
        self.typeShapeMast = 'cube'
        self.typeShape = 'pyramide'
        self.numbSk = (numb*2)+1
        self.lsNbFk = lsNbfk

    def createFeather(self):

        # INSPECT IF WINGS PART EXIST_________________________________________
        if len(self.selObj) == 0: # check if objRef is empty
            mc.warning('please select object')
        else:
            infoPart = mc.getAttr(self.selObj[0]+'.infPart')
            side = (mc.attributeQuery("update",node=infoPart, listEnum=1)[0]).split(":")[1]
            if 'wing' in infoPart:
                # GET LINE NUMBERS AND BASE FEATHERS NUMBERS_________________________________________
                dicTplFeatherLinesBase ={}
                for i in range(mc.getAttr(infoPart+'.featherLinesBase', mi=True,s=True)):
                        baseMb = mc.getAttr(infoPart+'.featherLinesBase[%s]'%i).replace(" ", "")
                        splitNlsTplBaseMb = baseMb[1:-1].split(",")
                        lsTplBaseMb =[each[1:-1] for each in splitNlsTplBaseMb]
                        dicTplFeatherLinesBase["%s"%(i+1)]= lsTplBaseMb

                dicTplFeatherLinesBack ={}
                for i in range(mc.getAttr(infoPart+'.featherLinesBack', mi=True,s=True)):
                        backMb = mc.getAttr(infoPart+'.featherLinesBack[%s]'%i).replace(" ", "")
                        splitNlsTplBackMb = backMb[1:-1].split(",")
                        lsTplBackMb =[each[1:-1] for each in splitNlsTplBackMb]
                        dicTplFeatherLinesBack["%s"%(i+1)]= lsTplBackMb

                dicTplFeatherLinesAim ={}
                for i in range(mc.getAttr(infoPart+'.featherLinesAim', mi=True,s=True)):
                        aimMb = mc.getAttr(infoPart+'.featherLinesAim[%s]'%i).replace(" ", "")
                        splitNlsTplAimMb = aimMb[1:-1].split(",")
                        lsTplAimMb =[each[1:-1] for each in splitNlsTplAimMb]
                        dicTplFeatherLinesAim["%s"%(i+1)]= lsTplAimMb

                rigGuide = FeatherGuide(name=self.name, side=side, selObj=self.selObj[0], numb=self.lsNbFk, numbSk=self.numbSk,
                                                offsetIk=self.offsetIk, shpRotIk=self.shpRotIk,
                                                sizeMast=self.sizeMast, sizeIk=self.sizeIk,shpRotCTR=self.shpRotCtr,
                                                sizeCtr=self.sizeCtr,sizeSk=self.sizeSk, typeBox=self.typeSk,
                                                typeShp=self.typeShape, typeShpMst=self.typeShapeMast,degree=3,
                                                featherLineBase=dicTplFeatherLinesBase,featherLineBack=dicTplFeatherLinesBack,featherLineAim=dicTplFeatherLinesAim)  # instance class CharGuide

                dic = rigGuide.template(dicLinesBase=dicTplFeatherLinesBase,dicLinesBack=dicTplFeatherLinesBack,dicLinesAim=dicTplFeatherLinesAim)  # run method createRig
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

            else:
                mc.warning('please select wing member')





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
