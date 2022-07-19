# coding: utf-8

import maya.cmds as mc
import maya.mel as mel
import re
from functools import partial
from ellipse_rig.library import lib_names
from ellipse_rig.library import lib_connectNodes
from ellipse_rig.library import lib_shapes,lib_attributes, lib_controlGroup
from ellipse_rig.library import lib_glossary as gloss
reload(lib_names)
reload(lib_connectNodes)
reload(lib_shapes)
reload(lib_attributes)
reload(gloss)
reload(lib_controlGroup)

class Shp ( object ):
    def __init__(self, shp_lst, color=lib_names.type_color("yellow"), size=(1,1,1), rotShp=(0, 0, 0)):
        self.shp_lst = shp_lst
        self.color = color
        self.size = size
        self.rotShp = rotShp

class Match( object ):
    def __init__(self, pos=None, rot=None, scl=(1,1,1)):
        self.tr = pos
        self.ro= rot
        self.sc = scl

def createObj(typeObj=None,shape=None,match=None,father=None, childLst=None, attributs=None,refObj=None,attrInfo=False,worldScale=None,*args, **kwargs):
    '''
    :param str typeObj: type object created
    :param shape:
    :param str match: matching object created with a other object
    :param str father: father object of object created
    :param str childLst: child object of object created
    :param attributs: parameters attributs
    :param refObj:
    :return: controller
    '''
    mc.namespace(set=':')
    # unselected all and instanced typeObj
    mc.select(cl=True)
    valType = typeObj()
    # if valType is a list, convert to string or value
    if isinstance(valType, list):
        objCreate = valType[0]
    else:
        objCreate = valType

    # bounding box
    if shape is None:
        shape=Shp(None)
    if refObj is None:
        bBoxSize = shape.size
    else:
        bBox = lib_shapes.bounding_box_utils(refObj, size=shape.size, delete=True)
        bBoxSize = (bBox['sizeX'],bBox['sizeY'],bBox['sizeZ'])

    #check if nameForm for shape object
    if worldScale is None:
        val= (1,1,1)
    else:
        val= mc.getAttr(worldScale+'.scale')[0]
    if shape.shp_lst is not None:
        shpForm = lib_shapes.parent_shp(lsObj=objCreate, lsShp=shape.shp_lst, rotShp=shape.rotShp, delBaseShp=None,
        colorType='Index', color=shape.color, bound={'sizeX': bBoxSize[0]*float(val[0]), 'sizeY': bBoxSize[1]*float(val[1]), 'sizeZ': bBoxSize[2]*float(val[2])})
        if attrInfo != False:
            update = mc.attributeQuery("update",node=attrInfo, listEnum=1)[0]
            if update.split(":")[1] == 'R':
                selShp = mc.listRelatives(objCreate, s=True)[0]
                recCv = mc.ls(selShp + '.cv[*]', fl=True)
                mc.select(recCv)
                mc.rotate(0, 0, 180, recCv)
    ## get position and rotation of target object
    getPos = (0, 0, 0); getRot = (0, 0, 0)
    if match is None :
        pass
    else:
        if isinstance(match, list) or isinstance(match, unicode):
            getPos = mc.xform(match, q=True, ws=True, translation=True)
            getRot = mc.xform(match, q=True, ws=True, rotation=True)
        # {"tr":self.selObj,"ro":self.selObj}
        elif isinstance(match, dict):
            if match['tr'] != []: getPos = match['tr']
            if match['ro'] != []: getRot = match['ro']

    # check if name for parent object
    if father is not None:
        mc.parent(objCreate, father)
    # check if name for child object
    if childLst is not None:
        [mc.parent(each, objCreate) for each in childLst]
    ## set position and rotation of target object

    mc.xform(objCreate, worldSpace=True, t=getPos)
    mc.xform(objCreate, worldSpace=True, ro=getRot)
    # check if obj Type is a joint
    if mc.objectType(objCreate) == 'joint':
        mc.makeIdentity(objCreate, apply=True, t=1, r=1, s=1, n=0, pn=1)
    # if attributs is a dictionary
    if isinstance(attributs, dict):
        [mc.setAttr(objCreate + ".%s" % each, attributs.values()[i]) for i, each in enumerate(attributs)]
    mc.select(cl=True)
    # add info in extra attributs
    if attrInfo != False:
        mc.addAttr(objCreate, ln='infPart', dt="string")
        mc.setAttr(objCreate + '.infPart', attrInfo, type="string")
        # add attributs symetrie
        update = mc.attributeQuery("update",node=attrInfo, listEnum=1)[0]

        nSym = "empty"
        test = objCreate.split("_")
        if update.split(":")[1] == 'L':
            test[-1]='R'
            nSym = "_".join(test)
        elif update.split(":")[1] == 'R':
            test[-1]='L'
            nSym = "_".join(test)
        mc.addAttr(objCreate, ln='symPart', dt="string")
        mc.setAttr(objCreate + '.symPart', nSym, type="string")

    return objCreate
# selObj = mc.ls(sl=True)
# obj= createObj(partial(mc.group, **{'n':'toto', 'em': True}),match={"Pos":selObj,"Rot":selObj,"Scl":selObj},fatherEl=None, childEl=None,attributs={"visibility":1})
# obj= createObj(partial(mc.joint, **{'n':'toto'}),match={"Pos":selObj,"Rot":selObj,"Scl":selObj},fatherEl=None, childEl=None,attributs={"drawStyle":2})


def createController(name=None,shape=None,match=None,father=None,childLst=None,refObj=None,addInf=False,addBuf=False,attrInfo=False,attributs={"drawStyle": 2},worldScale=None,*args, **kwargs):
    '''
    create a controller with root and sk
    :param str name: names
    :param shapeCtr:
    :param match:
    :param father:
    :param childLst:
    :param refObj:
    :return: dic controller (root,controller,sk)
    '''
    mc.select(cl=True)
    if shape is None:
        shape=Shp(None)
    dicController ={}
    ctrCreate = createObj(partial(mc.joint, **{'n': name}),shape= Shp(shape.shp_lst,color=shape.color,size= shape.size,
    rotShp=shape.rotShp),childLst=childLst,attributs=attributs, refObj=refObj,attrInfo=attrInfo,worldScale=worldScale)
    ''' names '''
    splitName = name.split("_")
    # adjust gloss.lexicon if word tpl in split [0]
    nSk = gloss.lexicon('tplSk')
    nRoot = gloss.lexicon('tplRoot')
    nInf = gloss.lexicon('tplInf')
    nBuf = gloss.lexicon('tplBuf')
    if splitName[0] =="c":
        nSk = gloss.lexicon('sk')
        nRoot = gloss.lexicon('root')
        nInf = gloss.lexicon('inf')
        nBuf = gloss.lexicon('buf')
    skName = name.replace(splitName[0],nSk,1)
    rootName = name.replace(splitName[0],nRoot,1)
    ''' Create '''

    # SK
    skCreate = createObj(partial(mc.joint, **{'n': skName}),attributs=attributs,refObj=refObj)
    lib_connectNodes.connectAxis(name, skName)


    # add group info
    ctrInf = ''
    if addInf is False:
        childrenList = [ctrCreate,skCreate]
    else:
        infName = gloss.renameSplit(selObj=name, namePart=[splitName[0]], newNamePart=[nInf])
        ctrInf= createObj(partial(mc.group, **{'n': infName,'em':True}), childLst=[ctrCreate,skCreate], refObj=refObj)
        childrenList = [ctrInf]
        dicController['inf'] = infName

    # ROOT
    rootCreate = createObj(partial(mc.joint, **{'n': rootName}),match=match,father=father,childLst=childrenList,
                 refObj=refObj,attributs=attributs)
    # add group buf
    ctrBuf =''
    if addBuf is False:
        pass
    else:
        bufName = gloss.renameSplit(selObj=name, namePart=[splitName[0]], newNamePart=[nBuf])
        ctrBuf= createObj(partial(mc.group, **{'n': bufName,'em':True}),match=match,father=father, childLst=[rootCreate], refObj=refObj)
        dicController['buf'] = bufName

    # add info in extra attributs
    if attrInfo != False:
        mc.addAttr(ctrCreate, ln='root', dt="string")
        mc.setAttr(ctrCreate + '.root', rootCreate, type="string")
        mc.addAttr(ctrCreate, ln='sk', dt="string")
        mc.setAttr(ctrCreate + '.sk', skCreate, type="string")

        if addInf is True:
            mc.addAttr(ctrCreate, ln='inf', dt="string")
            mc.setAttr(ctrCreate + '.inf', ctrInf, type="string")
        if addBuf is True:
            mc.addAttr(ctrCreate, ln='inf', dt="string")
            mc.setAttr(ctrCreate + '.inf', ctrBuf, type="string")

    dicController['sk'] = skName
    dicController['c'] = name
    dicController['root'] = rootName
    mc.select(cl=True)
    return dicController

#selObj = mc.ls(sl=True)
#ctr = createController(name='testou', match={"Pos": selObj, "Rot": selObj, "Scl": selObj})




def chainJoint(lstChain=None,shape=None,lstNameChain=None, lsRotOrder=None, aim=(0,1,0), upV=(0,0,1), posUpV =(1,0,0),convertChain=True):
    '''
    configuration of chainJoint
    :param lstChain: list joints of chain
    :param rotOrder: order of rotation
    :param aim: direction of aim
    :param upV: direction of upVector
    :param convertChain: create chain with aim direction, delete aimConstraint
    '''
    mc.select(cl=True)
    if shape is None:
        shape=Shp(None)

    lstJts = []
    lstAim = []
    lstUpV = []
    for i, chain in enumerate(lstChain):
        mc.select(cl=True)
        # get position and rotation of lstChain
        positions = mc.xform(chain, q=True, ws=True, translation=True)
        rotations = mc.xform(chain, q=True, ws=True, rotation=True)
        split = lstChain[i].split("_")
        # adjust name if len of split > 1
        if len(split) > 1:
            nameChain = chain.replace(split[0], "jnt", 1)
            nameAim = chain.replace(split[0], "aim", 1)
            nameUpV = chain.replace(split[0], "upV", 1)
        else:
            nameChain = "jnt_" + chain
            nameAim = "aim_" + chain
            nameUpV = "upV_" + chain

        # create joints to chain
        jntChain = createObj(partial(mc.joint, **{'n': lstNameChain[i]}),shape= Shp(shape.shp_lst,color=shape.color,size= shape.size,
        rotShp=shape.rotShp),match=[chain],father=None, refObj=chain)
        lstJts.insert(i, jntChain)
        # adjust rotate order
        if lsRotOrder == None:
            rotOrd = 0
        else:
            rotOrd = lsRotOrder[i]
        mc.joint(jntChain, e=True, roo='xyz')
        mc.setAttr(jntChain + ".rotateOrder",rotOrd,l=False,k=True)
        # create aim
        aimCreate = createObj(partial(mc.spaceLocator, **{'n': nameAim}),match=[chain],father=None, refObj=chain)
        mc.xform(aimCreate, t=positions, ro=rotations, ws=True)
        lstAim.insert(i, aimCreate)
        # create upVector
        upVCreate = createObj(partial(mc.joint, **{'n': nameUpV}),match=[chain],father=aimCreate, refObj=chain)
        mc.move(posUpV[0],posUpV[1], posUpV[2], upVCreate, ls=True)
        lstUpV.insert(i, upVCreate)

    # create aimConstraint
    [mc.aimConstraint(lstAim[j + 1], each, aim=aim, u=upV, wut='object', wuo=lstUpV[j]) for j, each in enumerate(lstJts[:-1])]
    # convert to chain
    if convertChain == True:
        mc.delete(lstAim)
        [mc.parent(each, lstJts[i]) for i, each in enumerate(lstJts[1:])]  # create hierarchie joint
        [mc.makeIdentity(each, apply=True, r=1, s=1, n=0, pn=1) for i, each in enumerate(lstJts)]  # makeIdentity
        mc.joint(lstJts[-1], e=True, o=(0, 0, 0))  # last joint value 0
    else:
        mc.delete(lstAim[0])
    return lstJts
# list joints create
#chainJoint(lstChain=mc.ls(sl=True), convertChain=False)


def connectScale(name='head',shp=['sphere'],rotShp=(0, 0, 0),sizeShp=(0.5,0.5,0.5),matchObj='',father='',child='',*args):
    # names to Scale system
    #nScaleRig = gloss.name_format(prefix=gloss.lexicon('rig'),name=gloss.lexicon('scale'),nFunc=name,incP='')
    nScale = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('scale'),nFunc=name,incP='')
    nSclScale = gloss.name_format(prefix=gloss.lexicon('s'),name=gloss.lexicon('scale'),nFunc=name,incP='')
    nRevScale = gloss.name_format(prefix=gloss.lexicon('rev'),name=gloss.lexicon('scale'),nFunc=name,incP='')
    nLoc = gloss.name_format(prefix=gloss.lexicon('loc'),name=name,incP='')
    nExpScl = gloss.name_format(prefix=gloss.lexicon('exp'),name=gloss.lexicon('scale'),nFunc=name,incP='')

    # CREATE SCALE HEAD SYSTEM______________________________
    # CREATE SCALE ______________________________
    # CREATE SCl_SCALE __________________________
    #sclRig = createObj(partial(mc.group, **{'n':nScaleRig , 'em': True}), father=father)
    sclW = mc.getAttr('tpl_WORLD' +'.scale')[0]
    scale = createController(name=nScale, shape=Shp(shp,rotShp=rotShp,
                            size= (sizeShp[0]*sclW[0],sizeShp[1]*sclW[0],sizeShp[2]*sclW[0]),color="yellow"), father=father, attributs={"drawStyle": 2})
    mc.delete(scale['sk'])
    # CREATE SCl_SCALE __________________________
    sclScale = createObj(partial(mc.group, **{'n':nSclScale, 'em': True}), father=scale['c'])
    # CREATE SCl_SCALE __________________________
    revScale = createObj(partial(mc.group, **{'n':nRevScale, 'em': True}), father=sclScale)
    # CREATE SCl_SCALE __________________________
    loc = createObj(partial(mc.group, **{'n':nLoc, 'em': True}), father=revScale)
    # ADJUST ROOT To HEAD __________________________
    getPos = mc.xform(matchObj, q=True, ws=True, translation=True)
    getRot = mc.xform(matchObj, q=True, ws=True, rotation=True)
    mc.xform(scale['root'], worldSpace=True, t=getPos)
    mc.xform(scale['root'], worldSpace=True, ro=getRot)

    # CREATE ATTRIBUTE SCALE_____________________
    attrSquash = mc.addAttr(scale['c'], ln="squash", nn="Squash", at="double", min=0, max=1, dv=1)
    mc.setAttr(scale['c'] + ".squash", e=True, k=True)
    MultMatrix = mc.createNode("multMatrix", n="mltM_scale%s"%(name))
    DecompMatrix = mc.createNode("decomposeMatrix", n="dM_scale%s"%(name))
    mc.connectAttr((scale['root'] + ".inverseMatrix"), (MultMatrix + ".matrixIn[0]"));
    mc.connectAttr((MultMatrix + ".matrixSum"), (DecompMatrix + ".inputMatrix"))
    mc.connectAttr((DecompMatrix + ".outputRotate"), (revScale + ".rotate"));
    mc.connectAttr((DecompMatrix + ".outputScale"), (revScale + ".scale"));
    mc.connectAttr((DecompMatrix + ".outputShear"), (revScale + ".shear"));
    mc.connectAttr((DecompMatrix + ".outputTranslate"), (revScale + ".translate"))
    mc.connectAttr((scale['c'] + ".inverseMatrix"), (MultMatrix + ".matrixIn[1]"))
    mc.select(cl=True)

    # EXPRESSION FOR SCALE_________________________
    expressionScale = "//world scale expression;\n" + "$sq = %s" % (
        scale['c'] + ".squash;\n") + "$sx = %s" % (scale['c'] + ".scaleX;\n") + "$sy = %s" % (
        scale['c'] + ".scaleY;\n") + "$sz = %s" % (scale['c'] + ".scaleZ;\n") + "%s=$sx;\n" % (
        sclScale + ".scaleX") + "%s=$sy;\n" % (sclScale + ".scaleY") + "%s=$sz;\n" % (
        sclScale + ".scaleZ")
    expressionScale2 = "%s\n" % (
        expressionScale) + "if ($sq>0);\n" + "{\n" + "$sqx = 1/sqrt(abs($sx));\n" + "$sqy = 1/sqrt(abs($sy));\n" + "$sqz = 1/sqrt(abs($sz));\n"
    expressionScale3 = "%s" % (expressionScale2) + "%s=$sq*($sx*$sqy*$sqz)+(1-$sq)*$sx;\n" % (
        sclScale + ".scaleX") + "%s=$sq*($sy*$sqx*$sqz)+(1-$sq)*$sy;\n" % (
        sclScale + ".scaleY") + "%s=$sq*($sz*$sqx*$sqy)+(1-$sq)*$sz;\n" % (
    sclScale + ".scaleZ") + "}"
    mc.expression(s="%s" % (expressionScale3), n=nExpScl)

    mc.parent(child,loc)
    return scale
    '''
    # CONNECT LOC SCALE____________________________
    MultMatrix = mc.createNode("multMatrix", n="mltM_loc%s"%(name))
    DecompMatrix = mc.createNode("decomposeMatrix", n="dM_loc%s"%(name))
    mc.connectAttr((loc + ".worldMatrix"), (MultMatrix + ".matrixIn[0]"));
    mc.connectAttr((MultMatrix + ".matrixSum"), (DecompMatrix + ".inputMatrix"))
    mc.connectAttr((DecompMatrix + ".outputRotate"), (toConnect + ".rotate"));
    mc.connectAttr((DecompMatrix + ".outputScale"), (toConnect + ".scale"));
    mc.connectAttr((DecompMatrix + ".outputShear"), (toConnect + ".shear"));
    mc.connectAttr((DecompMatrix + ".outputTranslate"), (toConnect + ".translate"))
    mc.select(cl=True)
    '''


def crtHook(driver, father):
    hook = 'hook'+driver[len(driver.split('_')[0]):]
    if not mc.objExists('hook'+driver[len(driver.split('_')[0]):]):
        hook = mc.createNode('transform', n='hook'+driver[len(driver.split('_')[0]):])
        dMat = mc.createNode('decomposeMatrix', n='dM'+driver[len(driver.split('_')[0]):])
        mMat = mc.createNode('multMatrix', n='mltM'+driver[len(driver.split('_')[0]):])
        mc.connectAttr(driver + '.worldMatrix[0]', mMat + '.matrixIn[0]')
        mc.connectAttr(hook + '.parentInverseMatrix[0]', mMat + '.matrixIn[1]')
        mc.connectAttr(mMat + '.matrixSum', dMat + '.inputMatrix')
        lAttr = ['translate', 'rotate', 'scale', 'shear']
        for i, attr in enumerate(['outputTranslate', 'outputRotate', 'outputScale', 'outputShear']):
            mc.connectAttr(dMat + '.' + attr, hook + '.' + lAttr[i])
        if father:
            mc.parent(hook, father)
    return hook


def crtFreeRotCtrl():
    nRoot = 'root_rot'
    nCtrl = 'c_rot'
    nInfTrs = 'inf_rotTrs'
    nInfOrt = 'inf_rotOrt'
    nRev = 'rev_rot'
    nMltM = 'mltM_freeRot'
    nDM = 'dM_freeRot'

    root = nRoot
    ctrl = nCtrl
    infTrs = nInfTrs
    infOrt = nInfOrt
    rev = nRev
    mltM = nMltM
    dM = nDM

    if not mc.objExists(nRoot):
        root = mc.createNode('transform', n=nRoot)
    if not mc.objExists(nCtrl):
        ctrl = mc.createNode('transform', n=nCtrl)
    if not mc.objExists(nInfTrs):
        infTrs = mc.createNode('transform', n=nInfTrs)
    if not mc.objExists(nInfOrt):
        infOrt = mc.createNode('transform', n=nInfOrt)
    if not mc.objExists(nRev):
        rev = mc.createNode('transform', n=nRev)
    if not mc.objExists(nMltM):
        mltM = mc.createNode('multMatrix', n=nMltM)
    if not mc.objExists(nDM):
        dM = mc.createNode('decomposeMatrix', n=nDM)

    mc.parent(ctrl, root)
    mc.parent(rev, infOrt)
    mc.parent(infOrt, infTrs)
    mc.parent(infTrs, root)

    mc.connectAttr(ctrl+'.translate', infTrs+'.translate', f=True)
    mc.connectAttr(ctrl+'.rotate', infOrt+'.rotate', f=True)
    mc.connectAttr(root+'.inverseMatrix', mltM+'.matrixIn[0]', f=True)
    mc.connectAttr(infTrs+'.inverseMatrix', mltM+'.matrixIn[1]', f=True)
    mc.connectAttr(mltM+'.matrixSum', dM+'.inputMatrix')
    mc.connectAttr(dM+'.outputTranslate', rev+'.translate')

    return ctrl



def crtRigAdd():
    rigAdd = 'c_rigAdd'
    root = 'root_rigAdd'
    if not mc.objExists(rigAdd):
        rigAdd = mc.curve(n=rigAdd, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                  28,
                  29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                  54, 55,
                  56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                  81, 82,
                  83], p=[(0.0, 0.0, 0.0), (0.6, 0.0, 0.0), (0.8, 0.2, 0.0), (1.0, 0.0, 0.0), (0.8, -0.2, 0.0),
                      (0.6, 0.0, 0.0),
                      (0.8, 0.0, 0.2), (1.0, 0.0, 0.0), (0.8, 0.0, -0.2), (0.8, 0.2, 0.0), (0.8, 0.0, 0.2),
                      (0.8, -0.2, 0.0),
                      (0.8, 0.0, -0.2), (0.6, 0.0, 0.0), (0.0, 0.0, 0.0), (-0.6, 0.0, 0.0), (-0.8, 0.2, 0.0),
                      (-1.0, 0.0, 0.0),
                      (-0.8, -0.2, 0.0), (-0.6, 0.0, 0.0), (-0.8, 0.0, 0.2), (-1.0, 0.0, 0.0), (-0.8, 0.0, -0.2),
                      (-0.8, 0.2, 0.0), (-0.8, 0.0, 0.2), (-0.8, -0.2, 0.0), (-0.8, 0.0, -0.2), (-0.6, 0.0, 0.0),
                      (0.0, 0.0, 0.0), (0.0, 0.6, 0.0), (0.0, 0.8, -0.2), (0.0, 1.0, 0.0), (0.0, 0.8, 0.2),
                      (0.0, 0.6, 0.0),
                      (-0.2, 0.8, 0.0), (0.0, 1.0, 0.0), (0.2, 0.8, 0.0), (0.0, 0.8, 0.2), (-0.2, 0.8, 0.0),
                      (0.0, 0.8, -0.2),
                      (0.2, 0.8, 0.0), (0.0, 0.6, 0.0), (0.0, 0.0, 0.0), (0.0, -0.6, 0.0), (0.0, -0.8, -0.2),
                      (0.0, -1.0, 0.0),
                      (0.0, -0.8, 0.2), (0.0, -0.6, 0.0), (-0.2, -0.8, 0.0), (0.0, -1.0, 0.0), (0.2, -0.8, 0.0),
                      (0.0, -0.8, -0.2), (-0.2, -0.8, 0.0), (0.0, -0.8, 0.2), (0.2, -0.8, 0.0), (0.0, -0.6, 0.0),
                      (0.0, 0.0, 0.0), (0.0, 0.0, -0.6), (0.0, 0.2, -0.8), (0.0, 0.0, -1.0), (0.0, -0.2, -0.8),
                      (0.0, 0.0, -0.6),
                      (-0.2, 0.0, -0.8), (0.0, 0.0, -1.0), (0.2, 0.0, -0.8), (0.0, 0.2, -0.8), (-0.2, 0.0, -0.8),
                      (0.0, -0.2, -0.8), (0.2, 0.0, -0.8), (0.0, 0.0, -0.6), (0.0, 0.0, 0.0), (0.0, 0.0, 0.6),
                      (0.0, 0.2, 0.8),
                      (0.0, 0.0, 1.0), (0.0, -0.2, 0.8), (0.0, 0.0, 0.6), (-0.2, 0.0, 0.8), (0.0, 0.0, 1.0),
                      (0.2, 0.0, 0.8),
                      (0.0, 0.2, 0.8), (-0.2, 0.0, 0.8), (0.0, -0.2, 0.8), (0.2, 0.0, 0.8), (0.0, 0.0, 0.6)])
        mc.addAttr(rigAdd, ln='ctrlSwitcher', at='bool', dv=True)
        mc.setAttr(rigAdd+'.ctrlSwitcher', True)
        mc.setAttr(rigAdd+'.overrideEnabled', True)
        mc.setAttr(rigAdd+'.overrideColor', 6)
    if not mc.objExists(root):
        root = mc.createNode('transform', n=root)
    mc.parent(rigAdd, root)
    lCg = lib_controlGroup.getAllCg()
    cgBox = 'cg_all'
    if not cgBox in lCg:
        if 'RIG:cg_all' in lCg:
            cgBox = 'RIG:cg_all'
    lib_controlGroup.addCtrlToCg([rigAdd], cgBox)
    return rigAdd








'''
# Import de la librairie sys
import sys
import maya.cmds as mc
import maya.mel as mel
# Définition du chemin des scripts
pathCustom ='Z:/JOB/Maya_work/scripts_pycharm_work'

# Si le chemin n'est pas déjà configuré
if not pathCustom in sys.path:
    # On l'ajoute
    sys.path.append(pathCustom)
# Import du module et définition d'un nom d'appel
# Refresh du module

from ellipse_rig.library import rigs_lib
reload(rigs_lib)
rigs_lib.chainJoint(lstChain=mc.ls(sl=True), convertChain=False)
'''