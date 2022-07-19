# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.assets.props.wheel import guide_wheel
from ellipse_rig.library import lib_glossary as gloss
reload(guide_wheel)

reload(gloss)



def delPart(selObj=mc.ls(sl=True)):
    getInfo =mc.getAttr(selObj[0] + ".infPart")
    delP = mc.getAttr(getInfo + ".delPart[0]")
    mc.delete(delP)

def delCtr(selObj=None,numb=None):
    if selObj == []:
        mc.warning('no object selected')
    else:
        if mc.objExists(selObj[0] + ".infPart") is False:
            mc.warning('please select object of part member !!!!!')
        else:
            # INSPECT SCENE________________________________________
            objScene = mc.ls(tr=True)
            # GET TPL INFO_________________________________________
            getInfo = mc.getAttr(selObj[0] + ".infPart")
            enumUpdate = mc.attributeQuery("update",node=getInfo, listEnum=1)[0]
            enumList = enumUpdate.split(":")
            enumSize = mc.attributeQuery("sizeSk",node=getInfo, listEnum=1)[0]
            enumListSize = enumSize.split(":")
            # DIC TO ENUM UPDATE___________________________________
            dic ={"name":enumList[0],"side":enumList[1],"sizeCtr":enumListSize[0],"sizeSk":enumListSize[1],
                  "typeSk":enumListSize[2],"offsetIk":enumListSize[3],"numb":enumListSize[4],"numbSk":enumListSize[5]}
            if numb == int(dic["numb"]):
                lsObjInfo =[ each for each in objScene if mc.objExists(each + ".infPart")
                             and mc.getAttr(each + ".infPart") == getInfo and mc.objExists(each + ".updateSk")]
            else:
                lsObjInfo =[ each for each in objScene if mc.objExists(each + ".infPart")
                             and mc.getAttr(each + ".infPart") == getInfo and mc.objExists(each + ".update")]
            # DELETE______________________________________________
            for each in lsObjInfo:
                mc.delete(each)
            return dic

def cnsPointPart(selObj=mc.ls(sl=True)):
    # GET INFO NAME____________________________________
    if selObj !=[]:
        # CHECK ATTRIBUTE CNSPART EXIST________________
        if len(selObj) == 1:
            infoName = mc.getAttr(selObj[0] + '.infPart')
            if mc.objExists(infoName+".cnsPart") is True:
                attrCns = mc.getAttr(infoName + ".cnsPart")
                mc.deleteAttr(infoName, at='cnsPart')
                mc.delete(attrCns)
            else:
                print("{} don't exist !!!".format(infoName + ".cnsPart"))
        else:
            for each in selObj[:-1]:
                infoName = mc.getAttr(each+'.infPart')
                if mc.objExists(infoName+".cnsPart") is True:
                    attrCns = mc.getAttr(infoName + ".cnsPart")
                    mc.deleteAttr(infoName, at='cnsPart')
                    mc.delete(attrCns)
                else:
                    splitObj = each.split("_")
                    nCnsPoint = gloss.renameSplit(selObj=each, namePart=[splitObj[0]],
                                                  newNamePart=[gloss.lexicon('tplCnsPt')], reNme=False)
                    cnsPoint = mc.pointConstraint(selObj[-1], each, n=nCnsPoint, mo=True)
                    mc.addAttr(infoName, ln='cnsPart', dt="string")
                    mc.setAttr(infoName + '.cnsPart', nCnsPoint, type="string")
    else:
        mc.warning('please select Object !!!')

def symCtr(side=None):

    # FILTER SYMETRIE OBJECTS____________________________________
    selObj = mc.ls(sl=True)
    objScene = mc.ls(tr=True)
    filterScene = []
    name = ''
    if selObj ==[]:
        for each in objScene:
            name = each
            filterScene.append(name)
    elif selObj !=[]:
        setObj =set()
        for each in selObj:
            name = each
            setObj.add(mc.getAttr(name+'.infPart'))
        [filterScene.append(each) for each in setObj]
    for each in filterScene:
        name = each
        #get tplInfo of side part
        splitObj = name.split("_")
        if splitObj[-1] == side:
            if "tplInfo" in name:
                update = mc.attributeQuery("update",node=name, listEnum=1)[0]
                symInfo =name.split("_")
                nSym = "empty"
                if update.split(":")[1] == 'L':
                    symInfo[-1]='R'
                    nSym = "_".join(symInfo)
                elif update.split(":")[1] == 'R':
                    symInfo[-1]='L'
                    nSym = "_".join(symInfo)
                objExist = True
                if mc.objExists(nSym):
                    pass
                elif selObj != []:
                    update = mc.attributeQuery("update",node=mc.getAttr(name+'.infPart'), listEnum=1)[0]
                    enumList = update.split(":")
                    enumSize = mc.attributeQuery("sizeSk",node=mc.getAttr(name+'.infPart'), listEnum=1)[0]
                    enumListSize = enumSize.split(":")
                    if enumList[0] == 'leg' or enumList[0] == 'arm':
                        # DIC TO ENUM UPDATE___________________________________
                        dic ={"name":enumList[0],"side":enumList[1],"sizeCtr":enumListSize[0],"sizeSk":enumListSize[1],
                              "typeSk":enumListSize[2],"offsetIk":enumListSize[3],"numb":enumListSize[4],"numbSk":enumListSize[5],
                              "numbStartMb": mc.getAttr(name+'.infoNumbMb[0]'),"numbMidMb":mc.getAttr(name+'.infoNumbMb[1]'),
                              "numbEndMb":mc.getAttr(name+'.infoNumbMb[2]'),"subDvEndMb":mc.getAttr(name+'.infoNumbMb[3]')}
                    else:
                        # DIC TO ENUM UPDATE___________________________________
                        dic ={"name":enumList[0],"side":enumList[1],"sizeCtr":enumListSize[0],"sizeSk":enumListSize[1],
                              "typeSk":enumListSize[2],"offsetIk":enumListSize[3],"numb":enumListSize[4],"numbSk":enumListSize[5]}

                    # INVERT SIDE__________________________________________
                    side2 = ''
                    if dic["side"] == 'L':
                        side2 ='R'
                    elif dic["side"] == 'R':
                        side2 ='L'
                    # getAxis World______________________________________
                    worldScale = gloss.name_format(prefix=gloss.lexicon('tpl'),name=gloss.lexicon('world'),incP='')
                    #valTr = mc.getAttr(worldScale + '.translate')[0]
                    #valRot = mc.getAttr(worldScale + '.rotate')[0]
                    valScl = mc.getAttr(worldScale + '.scale')[0]
                    # getAxis Init  temporary World _____________________
                    getRootMaster = mc.getAttr(mc.getAttr(name+'.masterTpl[0]')+ '.root')
                    getFatherRootMaster = mc.listRelatives(getRootMaster,p=True)
                    if "transform" in getFatherRootMaster[0]:
                        pass
                    else:
                        # mc.setAttr(worldScale + '.translate',0,0,0)
                        # mc.setAttr(worldScale + '.rotate',0,0,0)
                        mc.setAttr(worldScale + '.scale',1,1,1)

                    # CREATE SYM PART______________________________________
                    if dic['name'] == 'wheel':
                        reload(guide_wheel)
                        guide = guide_wheel.Wheel(name=dic["name"],selObj=None,side=side2,numb=int(dic["numb"]),numbSk=int(dic["numbSk"]))# instance class charGuide
                        dic = guide.createWheel()
                        print dic
                    else:
                        mc.warning('module no define')

                    # CONNECT MIRROR________________________________________
                    mc.connectAttr(each+'.moduleMirror', dic['infoName']+'.moduleMirror', force=True)
                    #filterScene.append(dic['infoName'])
                    # getAxis val with scale __________
                    #mc.setAttr(worldScale + '.translate',valTr[0],valTr[1],valTr[2])
                    #mc.setAttr(worldScale + '.rotate',valRot[0],valRot[1],valRot[2])
                    mc.setAttr(worldScale + '.scale',valScl[0],valScl[1],valScl[2])

                    # ADJUST POS AND ROT ON ROOT MASTER__________________________________________
                    getRootMasterMirror = mc.getAttr(dic['master']+ '.root')
                    getFatherRootMasterMirror = mc.listRelatives(getRootMasterMirror,p=True)
                    getPos = mc.xform(getRootMaster, q=True, ws=True, translation=True)
                    getRot = mc.xform(getRootMaster, q=True, ws=True, rotation=True)
                    mc.xform(getRootMasterMirror, worldSpace=True, t=getPos)
                    mc.xform(getRootMasterMirror, worldSpace=True, ro=getRot)

                    # ADJUST POS AND ROT ON TRANSFORM GRP________________________________________
                    if "transform" in getFatherRootMasterMirror[0]:
                        mc.setAttr(getFatherRootMasterMirror[0] + '.translate',0,0,0)
                        mc.setAttr(getFatherRootMasterMirror[0] + '.rotate',0,0,0)
                        if mc.objExists(dic['infoName']+'.masterStart[0]') is True :
                            getRootMasterMirror = mc.getAttr(mc.getAttr(dic['infoName']+'.masterStart[0]')+'.root')
                            getFatherRootMasterMirror = mc.listRelatives(getRootMasterMirror,p=True)
                            mc.setAttr(getFatherRootMasterMirror[0] + '.translate',0,0,0)
                            mc.setAttr(getFatherRootMasterMirror[0] + '.rotate',0,0,0)
                        else:
                            print 'no'
                    else:
                        pass

                    '''
                    # GET SIMILAR OBJECT IN ATTRIBUTE PARENT________________________________________
                    getParentConnection = mc.listConnections(name+'.parent')
                    getChildConnection = mc.listConnections(name+'.children')
                    for each in getChildConnection:
                        mc.connectAttr(getParentConnection[0] +".%s"%gloss.lexiconAttr('attrChild'),each+'.parent',f=True)
                    '''
                else:
                    mc.warning('no {} object exist !!!!'.format(nSym))
                    objExist = False

                if objExist is True:
                    lenSym = mc.getAttr(name+'.sym', mi=True,s=True)
                    for attr in range(lenSym):
                        # adjust Shape Form
                        try:
                            selShp1 = mc.listRelatives(mc.getAttr(name+'.sym[%s]'%attr), s=True)[0]
                            selShp2 = mc.listRelatives(mc.getAttr(nSym+'.sym[%s]'%attr), s=True)[0]
                            recCv1 = mc.ls(selShp1 + '.cv[*]', fl=True)
                            recCv2 = mc.ls(selShp2 + '.cv[*]', fl=True)
                            getPos1 = [mc.pointPosition(each, l=True) for each in recCv1]
                            [mc.move(-getPos1[i][0], getPos1[i][1], getPos1[i][2], each, os=True) for i, each in enumerate(recCv2)]
                        except:
                            pass
                        # get axis object in scene
                        getPos = mc.xform(mc.getAttr(name+'.sym[%s]'%attr), q=True, a=True, translation=True)
                        getRot = mc.xform(mc.getAttr(name+'.sym[%s]'%attr), q=True, a=True, rotation=True)
                        getScal = mc.xform(mc.getAttr(name+'.sym[%s]'%attr), q=True,r=True,scale=True)
                        # sym object
                        mc.xform(mc.getAttr(nSym+'.sym[%s]'%attr), t=(-getPos[0],getPos[1],getPos[2]))
                        mc.xform(mc.getAttr(nSym+'.sym[%s]'%attr), ro=(getRot[0],-getRot[1],-getRot[2]))
                        mc.xform(mc.getAttr(nSym+'.sym[%s]'%attr), s=(getScal[0],getScal[1],getScal[2]))

        else:
            pass


        '''
        # adjust rotation shape R
        try:
            selShp = mc.listRelatives(objCreate, s=True)[0]
            if mc.objExists(selShp) == True:
                recCv = mc.ls(selShp + '.cv[*]', fl=True)
                mc.select(recCv)
                mc.rotate(0,0,180,recCv)
        except:
            pass

        print(dic["name"])
        guide = guide_leg.Leg(guide_member.Member(),name=str(dic["name"]),side="R",selObj=mc.ls(sl=True),numb=dic["numb"],numbSk=dic["numbSk"]) # instance class charGuide
        guide.createLeg()

        module = import('{project}.foundation_rig.assets.{template}.guide_{module}'.format(project='X:\SETUP\maya', template='characters', module=dic["name"]), globals(), locals(), [''])
        reload(module)
        modulePart = dic["name"].capitalize()
        c = module.modulePart(name=dic["name"],side=dic["side"],selObj=mc.ls(sl=True),numb=dic["numb"],numbSk=dic["numbSk"])
        '''




'''
# Import de la librairie sys
import sys
import maya.cmds as mc
import maya.mel as mel
# Définition du chemin des scripts
pathCustom ='S:\SETUP\maya'

# Si le chemin n'est pas déjà configuré
if not pathCustom in sys.path:
    # On l'ajoute
    sys.path.append(pathCustom)
# Import du module et définition d'un nom d'appel
# Refresh du module
from ellipse_rig.assets.characters import guide_tool
reload(guide_tool)

#___________CnsPart Action_______________________
reload(guide_tool); test = guide_tool.cnsPointPart() # instance class charGuide

#___________Delete Action_______________________
#reload(guide_tool); delFunc =guide_tool.delCtr(selObj=mc.ls(sl=True))

#___________Update Action_______________________
#reload(guide_tool); updFunc = guide_tool.updateGuide(selObj=mc.ls(sl=True),numb=3,numbSk=12) # instance class charGuide

#___________Sym Action_______________________
reload(guide_tool); guide = guide_tool.symCtr(side='L') # instance class charGuide

'''
