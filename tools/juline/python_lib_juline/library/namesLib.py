# coding: utf-8
import maya.cmds as mc
from itertools import takewhile

def type_name(key):
    ############################## TYPE ######################################
    nTypes = {}
    #TEMPLATE_________________________________________________________________
    nTypes['tpl'] = 'tpl' # template

    #RIGGING__________________________________________________________________
    nTypes['hook'] = 'hook' # hook
    nTypes['inf'] = 'inf' # info
    nTypes['offSet'] = 'offSet' # offSet
    nTypes['root'] = 'root' # root
    nTypes['c'] = 'c' # controller
    nTypes['sk'] = 'sk' # skin joint
    nTypes['jt'] = 'jt' # joint
    nTypes['upV'] = 'upV' # up vector
    nTypes['eff'] = 'eff' # effector
    nTypes['aim'] = 'aim' # aim
    nTypes['lookAt'] = 'lookAt' # lookAt
    nTypes['o'] = 'o' # o
    nTypes['ao'] = 'ao' # ao
    nTypes['ik'] = 'ik' # ik
    nTypes['trf'] = 'trf' # transform
    nTypes['trans'] = 'trans' # translate
    nTypes['rot'] = 'rot' # rotate
    nTypes['scl'] = 'scl' # scale
    nTypes['check'] = 'check' # checker
    nTypes['chain'] = 'chain' # chain
    nTypes['roll'] = 'roll' # roll
    nTypes['end'] = 'end' # end
    nTypes['target'] = 'target' # target
    nTypes['mtr'] = 'mtr' # master
    nTypes['hdl'] = 'hdl' # Handle

    # CONSTRAINT________________________________________________________________
    nTypes['cns'] = 'cns' # constraint
    nTypes['lnk'] = 'lnk' # link
    nTypes['cnsO'] = 'cnsO' # constraintO
    nTypes['inst'] = 'inst' # instance

    # NODE______________________________________________________________________
    nTypes['mtxDcp'] = 'mtxDcp' # matrixDecomposition
    nTypes['mtxMlt'] = 'mtxMlt' # matrixMultiply
    nTypes['mtxFour'] = 'mtxFour' # matrixFourByFour
    nTypes['mtxInv'] = 'mtxInv' # matrixInverse
    nTypes['mltDiv'] = 'mltDiv' # multiplyDivide
    nTypes['mltDblLin'] = 'mltDblLin' # mltDoubleLinear
    nTypes['addDblLin'] = 'addDblLin' # addDoubleLinear
    nTypes['distDim'] = 'distDim' # distanceDimension
    nTypes['ptOnSurf'] = 'ptOnSurf' # pointOnSurface
    nTypes['clsSurf'] = 'clsSurf' # closeSurface
    nTypes['trfNod'] = 'trfNod' # transformNode

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multMatrix

    # DEFORMS____________________________________________________________________
    nTypes['bend'] = 'bend' # bend
    nTypes['ltc'] = 'ltc' # lattice
    nTypes['hdl'] = 'hdl' # handle

    # SHAPE______________________________________________________________________
    nTypes['geo'] = 'geo' # geometry
    nTypes['cv'] = 'cv' # curve
    nTypes['loft'] = 'loft' # loft
    nTypes['surf'] = 'surf' # surface
    nTypes['shp'] = 'shp' # shape

    # EXPRESSION CONNECTION_______________________________________________________
    nTypes['exp'] = 'exp' # expression
    nTypes['attr'] ='attr' # attributes

    # SET_________________________________________________________________________
    nTypes['set'] = 'set' # set

    # RIGGING CHARACTER___________________________________________________________
    nTypes['clav'] = 'clav' # clavicule
    nTypes['eyeTarget'] = 'eyeTarget' # eyeTarget
    nTypes['footRoll'] = 'footRoll' # footRoll
    nTypes['ballRoll'] = 'ballRoll' # ballRoll

    return nTypes[key]
# type_name(nTypes['set'])


def current_name(name=None, key=None):
    ############################## CURRENT NAME ###############################
    nCurrent ={}
    # RIGGING__________________________________________________________________
    nCurrent[''] = name  # empty
    nCurrent['all'] = 'ALL' # top Node
    nCurrent['world'] = 'WORLD' # world
    nCurrent['walk'] = 'WALK' # world
    nCurrent['fly'] = 'FLY' # fly
    nCurrent['rig'] = 'RIG'  # rig
    nCurrent['geo'] = 'GEO'  # geo
    nCurrent['nHdl'] = name + 'Hdl' # name + Handle
    nCurrent['nRoot'] = name + 'Root'  # name + Root
    nCurrent['nOffSet'] = name + 'OffSet'  # name + OffSet
    nCurrent['switch'] = 'switch' # switch
    nCurrent['all_switch'] = 'ALL_SWITCH'  # all switch
    nCurrent['tpl'] = name +'tpl'  # switch
    # RIGGING CHARACTER___________________________________________________________

    return nCurrent[key]
# current_name(name='toto',key='nHdl')


def side_name(key=None):
    ############################## SIDE ######################################
    nSide = {}
    # RIGGING__________________________________________________________________
    nSide[''] = ''  # left
    nSide['L'] = 'L'  # left
    nSide['R'] = 'R'  # right
    nSide['M'] = 'M'  # middle
    return nSide[key]
# side_name(key='nHdl')


def namespace(key=None):
    nSpace = {}
    # NAMESPACES__________________________________________________________________
    nSpace['TPL'] = 'TPL' # template
    nSpace['ARM'] = 'ARM'
    nSpace['WORLD'] = 'WORLD'
    nSpace['EYE'] = 'EYE'
    nSpace['FINGER'] = 'FINGER'
    nSpace['FOOT'] = 'FOOT'
    nSpace['HAND'] = 'HAND'
    nSpace['HEAD'] = 'HEAD'
    nSpace['LEG'] = 'LEG'
    nSpace['NECK'] = 'NECK'
    nSpace['CLAV'] = 'CLAV'
    nSpace['SPINE'] = 'SPINE'
    nSpace['TAIL'] = 'TAIL'
    nSpace['THUMB'] = 'THUMB'
    nSpace['TOE'] = 'TOE'
    return nSpace[key]
# namespace(key='TPL')


def name_format(type=None, name=None, funct=None,inc=None, side=None, order=[0, 1, 2, 3], **kwargs):
    prefix = type_name(type)
    name = current_name(name, funct)
    nSide = side_name(side)
    # nameBuilder
    # no inc of the name ###
    incStat = None
    if incStat == None:
        # no side of the name
        if side == "":
            name_format = ('{%s}_{%s}{%s}{%s}' % (order[0], order[1], order[2], order[3])).format(prefix, name, inc, nSide)
        else:
            name_format = ('{%s}_{%s}{%s}_{%s}' % (order[0], order[1], order[2], order[3])).format(prefix, name, inc, nSide)
    elif incStat == "inc":
        # no side of the name
        if side == "":
            name_format = ('{%s}_{%s}_{%s}{%s}' % (order[0], order[1], order[2], order[3])).format(prefix, name,
                                                                                                  nSide, inc)
        else:
            name_format = ('{%s}_{%s}_{%s}_{%s}' % (order[0], order[1], order[2], order[3])).format(prefix, name,
                                                                                                   nSide, inc)
    return name_format


# name_format(type='tpl', name='toto', suffix='nHdl', side='L', inc='1', order=[0, 1, 2, 3], option=None)



def get_increment(strNum):
    ## Gugu
    r = strNum[-1::-1]
    d = [c.isdigit() for c in r]
    ## retourne le nombre de fin de la string
    num = ''.join((i[0] for i in takewhile(lambda (x, y): y, zip(r, d))))[-1::-1] or None
    if num:
        strCutNum = strNum.split(num)[0]
        return strCutNum, num
    else:
        #print '##   no incrementation exist on ', strNum
        return strNum, None

def set_increment(name):
    ## Gugu
    strCutNum, num = get_increment(name)
    lAllTrsf = mc.ls(sl=False, type='transform')
    lNamed = []
    ## checker ds tous les trsfm s'il n'existe pas d'autre obj incremente
    for transform in lAllTrsf:
        if strCutNum in transform:
            ## checker que les caracteres suivant le nom coupe soit bien un digit
            if len(transform) > len(strCutNum):
                if transform[len(strCutNum)].isdigit():
                    lNamed.append(transform)
    lNum = []
    for named in lNamed:
        strCutNum2, num2 = get_increment(named)
        if num2:
            lNum.append(num2)
    if lNum:
        numMax = max(lNum)
    else :
        numMax = 0
    newName = strCutNum + str(int(numMax) + 1)
    return newName

def duplicate_rename(obj, prefix='', suffix=''):
    ## Gugu
    lDup = []
    objDup = mc.duplicate(obj, name=prefix + obj + suffix)
    lDup.append(objDup[0])
    ## rename shape
    lObjDupShp = mc.listRelatives(objDup[0], shapes=True, fullPath=True) or []
    for objDupShp in lObjDupShp:
        mc.rename(objDupShp, prefix + objDupShp.split('|')[-1] + suffix)
    lChild = mc.listRelatives(objDup[0], allDescendents=True, shapes=False, type='transform',
                              fullPath=True) or []
    lToRename = []
    for child in lChild:
        lToRename.append(child)
        mc.delete(child, constructionHistory=True)
    for child in lToRename:
        childRenamed = mc.rename(child, prefix + child.split('|')[-1] + suffix)
        lDup.append(childRenamed)
    return lDup

## CONVERSION CONVENTION NAME
def lower_case_to_camelCase(name):
    ## Gugu
    if '_' in name:
        i = name.find('_')
        newName = name[:i] + name[i + 1:].capitalize()
        if '_' in newName:
            return lower_case_to_camelCase(newName)
        else:
            return newName
    if name[0].isupper():
        name = name[0].lower() + name[1:]
        return name
    else:
        return name

def convert_namespace(name, keepNamespace=True):
    ## Gugu
    if keepNamespace:
        if ':' in name:
            i = name.find(':')
            newName = name[:i] + name[i + 1:].capitalize()
            if ':' in newName:
                return convert_namespace(newName)
            else:
                return newName
        else:
            return name
    else:
        newName = name.split(':')[-1]
        return newName


def keep_only_2_underscores(name_to_convert):
    '''
    Keep only 1st & last "_"
    :param name_to_convert:
    :return:
    '''
    if name_to_convert.count('_') > 2:
        mid_name = ''
        for i in range(1, name_to_convert.count('_')):
            print i
            if not mid_name:
                mid_name = name_to_convert.split('_')[i]
            else:
                mid_name = mid_name + (name_to_convert.split('_')[i]).replace(name_to_convert.split('_')[i][0],
                                                                              name_to_convert.split('_')[i][0].upper())

        name_converted = name_to_convert.split('_')[0] + "_" + mid_name + "_" + name_to_convert.split('_')[-1]
        return name_converted
    else:
        return name_to_convert

def get_prefix(name):
    if "_" in name:
        prefix_ind = name.find("_")
        prefix = name[:prefix_ind]
    else:
        prefix = ""
    return prefix

def replace_prefix(name, new_prefix):
    prefix = get_prefix(name)
    new_name = name.replace(prefix, new_prefix)
    return new_name