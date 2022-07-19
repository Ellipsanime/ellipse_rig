# coding: utf-8

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as openMaya
import maya.api.OpenMaya as om
import re
import sys
import fnmatch

from math import fabs, degrees, radians
#from collections.abc import Iterable


# # ------------------------------------ TOOLS ------------------------------------ # #


def sortIntWeightedArray(array=[], weights=[]):
    sortedArray = []
    if len(array) and len(weights) and (len(array) == len(weights)):
        pairs = zip(array, weights)
        sortedPairs = sorted(pairs, key=lambda p: p[1])
        sortedArray = [p[0] for p in sortedPairs]

    return sortedArray


def symmetryMatrix(axis=om.MVector().kXaxisVector, origin=om.MVector().kZeroVector):
    """Builds the plane symmetry (reflection) matrix for symmetry through the plane
    normal to the vector axis passed as argument, and including the point origin
    :param MVector axis: the symetry's plane normal
    :param MVector origin: the origin of the symetry's plane
    :param OpenMaya.MMatrix
    """
    sM = om.MMatrix()  # Symetry matrix
    if isinstance(axis, om.MVector) and isinstance(origin, om.MVector):
        tMa = om.MMatrix()  # Pre-translation
        tMb = om.MMatrix()  # Post-translation

        sM.setElement(0, 0, -(axis.x) * (axis.x) + (axis.y) * (axis.y) + (axis.z) * (axis.z))
        sM.setElement(0, 1, -2 * (axis.x) * (axis.y))
        sM.setElement(0, 2, -2 * (axis.x) * (axis.z))
        sM.setElement(1, 0, sM.getElement(0, 1))
        sM.setElement(1, 1, (axis.x) * (axis.x) - (axis.y) * (axis.y) + (axis.z) * (axis.z))
        sM.setElement(1, 2, -2 * (axis.y) * (axis.z))
        sM.setElement(2, 0, sM.getElement(0, 2))
        sM.setElement(2, 1, sM.getElement(1, 2))
        sM.setElement(2, 2, (axis.x) * (axis.x) + (axis.y) * (axis.y) - (axis.z) * (axis.z))

        if origin != om.MVector().kZeroVector:
            tMa.setElement(3, 0, -origin.x)
            tMa.setElement(3, 1, -origin.y)
            tMa.setElement(3, 2, -origin.z)

            tMb.setElement(3, 0, origin.x)
            tMb.setElement(3, 1, origin.y)
            tMb.setElement(3, 2, origin.z)

            sM = tMa * sM
            sM = sM * tMb
    else:
        raise ValueError('[symmetryMatrix] invalid parameters')
    return sM

# # ------------------------------------ TEMPLATE ------------------------------------ # #


class ControlTemplate(object):
    '''
    Class to handle the rig templates
    '''
    # Define the valids values of the control attribut
    # TODO: Set these values as module Globals?
    kTolerance = .0001
    isBuilt = True
    validBuildTypes = ['joint', 'transform']
    validLocations = ['none', 'left', 'right', 'middle']
    locationsColorIndexes = [0, 13, 6, 17]
    validInverseLocations = ['none', 'right', 'left', 'middle']
    validLocationsSuffixes = ['', '_L', '_R', '']
    validParentScaleStates = ['transform', 'joint']
    validRotateOrders = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
    isMirrored = False
    validMirrorTypes = ['transform', 'joint',
                        'orientation', 'none', 'translate']
    addToCtrlSet = True
    addToSkinSet = True
    iconTypes = ['shape', 'handle', 'locator', 'none']
    buildPoseNode = False
    validRootPrefixes = ['root', 'ro']
    validControlPrefixes = ['c', 'ctl', 'ctrl']
    validSkPrefixes = ['sk', 'j']

    def __init__(self, obj):
        '''
        Constructor create the default attributes or retreive them is the object has already been templated
        '''
        self.apiObject = None
        self.controlTemplate = obj
        # By default the nsTpl node will be built
        self.isBuilt = ControlTemplate.isBuilt
        # By default a transform is use as control
        self.builtType = ControlTemplate.validBuildTypes[1]
        self.location = ControlTemplate.validLocations[0]  # Middle location
        # By default we don't want a compensate scale
        self.parentScale = ControlTemplate.validParentScaleStates[0]
        # By RotateOrder is xyz
        self.rotateOrder = ControlTemplate.validRotateOrders[0]
        self.isMirrored = ControlTemplate.isMirrored  # By Default a tpl is not mirrored
        # By default a mirror control's behaviour is like an fk joint
        self.mirrorType = ControlTemplate.validMirrorTypes[0]
        self.rootPrefix = ControlTemplate.validRootPrefixes[0]
        self.controlPrefix = ControlTemplate.validControlPrefixes[0]
        self.skPrefix = ControlTemplate.validSkPrefixes[0]
        self.baseName = ''
        self.index = 0
        # By default a node is add to the control set
        self.addToCtrlSet = ControlTemplate.addToCtrlSet
        # By default a node is add to the skinning set
        self.addToSkinSet = ControlTemplate.addToSkinSet
        # By default the shape under the nsTpl node will be used, if there is no shape available, the handle will be displayed
        self.iconType = ControlTemplate.iconTypes[0]
        # by default the pose node is not built
        self.buildPoseNode = ControlTemplate.buildPoseNode
        if mc.objExists(obj):
            objType = ObjectType(obj)
            # test if this object has already been templated
            if not objType.isOfType('controlTemplate'):
                self.createControlTemplateAttributes()
            else:  # we supposed that this object is a nsTpl or a control, we retreive all the necessary informations to fill the class
                self.updateControlTemplateAttributes()
        else:
            raise ValueError('[ControlTemplate] Supplied object {} does not exist'.format(obj))

    def __str__(self):
        '''
        Method used to print usefull information about the class
        '''
        return ('{}'.format(self.controlTemplate))

    def createControlTemplateAttributes(self):
        '''
        Method to create all the attributes on the nsTpl object
        '''
        if not mc.objExists(self.controlTemplate):
            return True
        objType = ObjectType(self.controlTemplate)
        # test if this object has already been templated

        if objType.isOfType('controlTemplate'):
            raise RuntimeError('[createControlTemplateAttributes] Supplied object {} has already been templated'.format(
                self.controlTemplate))
        self.apiObject = getMObject(self.controlTemplate)

        # Create the attribute to specified that this node is a nsTpl object
        #
        objType.setRigNodeType('controlTemplate', lockIt=True)

        # Create the attribute to specify if this node is built in the rig
        #
        mc.addAttr(self.controlTemplate, ln='isBuilt',
                   at='bool', dv=self.isBuilt)

        # Create the attribute to set the type of built for the control, transform or joint
        # The root, the pose, and the skin nodes will always be of type joint, only the control can be either a transform or a joint
        mc.addAttr(self.controlTemplate, ln='builtType', at='enum',
                   enumName=':'.join(ControlTemplate.validBuildTypes),
                   dv=ControlTemplate.validBuildTypes.index(self.builtType))

        mc.setAttr('{}.builtType'.format(self.controlTemplate),
                   keyable=True, channelBox=True)
        # Create the attribute to specify the location of the node, the location suffix is calculated based on the world position of the nsTpl node
        #
        self.location = getObjectLocation(self.controlTemplate,
                                          tolerance=ControlTemplate.kTolerance)

        mc.addAttr(self.controlTemplate, ln='location', at='enum',
                   enumName=':'.join(ControlTemplate.validLocations),
                   dv=ControlTemplate.validLocations.index(self.location))

        # Create the attribute to set the behaviour of the inverseScale parameter of the root joint
        #
        mc.addAttr(self.controlTemplate, ln='parentScale', at='enum', enumName=':'.join(
            ControlTemplate.validParentScaleStates), dv=ControlTemplate.validParentScaleStates.index(self.parentScale))
        mc.setAttr('{}.parentScale'.format(self.controlTemplate),
                   keyable=True, channelBox=True)

        # Create the attribute to set the rotateOrder
        #
        try:
            mc.setAttr('{}.rotateOrder'.format(self.controlTemplate),
                       keyable=True, channelBox=True)
            mc.setAttr('{}.rotateOrder'.format(self.controlTemplate),
                       ControlTemplate.validRotateOrders.index(self.rotateOrder))
        except Exception:
            if not mc.attributeQuery('rtOrder', n=self.controlTemplate, ex=True):
                mc.addAttr(self.controlTemplate, ln='rtOrder', at='enum',
                           en='xyz:yzx:zxy:xzy:yxz:zyx:', keyable=True)
                mc.connectAttr('{}.rtOrder'.format(self.controlTemplate),
                               '{}.rotateOrder'.format(self.controlTemplate))

            mc.setAttr('{}.rtOrder'.format(self.controlTemplate),
                       ControlTemplate.validRotateOrders.index(self.rotateOrder))

        # Create the attribute to specify if this node is built in the rig
        #
        if self.location not in ['none', 'middle']:
            self.isMirrored = False
        mc.addAttr(self.controlTemplate, ln='isMirrored',
                   at='bool', dv=self.isMirrored)
        mc.setAttr('{}.isMirrored'.format(self.controlTemplate),
                   keyable=True, channelBox=True)

        # Create the attribute to set the type of mirror, behaviour or orientation
        #
        if self.location not in ['none', 'middle']:
            self.mirrorType = ControlTemplate.validMirrorTypes[1]
        mc.addAttr(self.controlTemplate, ln='mirrorType', at='enum',
                   enumName=':'.join(ControlTemplate.validMirrorTypes),
                   dv=ControlTemplate.validMirrorTypes.index(self.mirrorType))
        mc.setAttr('{}.mirrorType'.format(self.controlTemplate),
                   keyable=True, channelBox=True)

        # Create the attributes to describe the syntax of the objects
        #
        nameParser = NameParser(self.controlTemplate)
        mc.addAttr(self.controlTemplate, ln='name', dt='string')
        self.baseName = nameParser.getBaseName()
        mc.setAttr('{}.name'.format(self.controlTemplate),
                   self.baseName, type='string')
        mc.addAttr(self.controlTemplate, ln='index', dt='string')
        self.index = nameParser.getNameIndex()
        mc.setAttr('{}.index'.format(self.controlTemplate),
                   self.index, type='string')

        # Create the attribute to set the different prefix of a created control
        #
        mc.addAttr(self.controlTemplate, ln='rootPrefix', at='enum',
                   enumName=':'.join(ControlTemplate.validRootPrefixes),
                   dv=ControlTemplate.validRootPrefixes.index(self.rootPrefix))
        mc.addAttr(self.controlTemplate, ln='controlPrefix', at='enum',
                   enumName=':'.join(ControlTemplate.validControlPrefixes),
                   dv=ControlTemplate.validControlPrefixes.index(self.controlPrefix))
        mc.addAttr(self.controlTemplate, ln='skPrefix', at='enum',
                   enumName=':'.join(ControlTemplate.validSkPrefixes),
                   dv=ControlTemplate.validSkPrefixes.index(self.skPrefix))

        # Create the attribute to specify if this node is add to the control Set
        #
        mc.addAttr(self.controlTemplate, ln='ctrlSet',
                   at='bool', dv=self.addToCtrlSet)
        mc.setAttr('{}.ctrlSet'.format(self.controlTemplate),
                   keyable=True, channelBox=True)

        # Create the attribute to specify if this node is add to the skinning Set
        #
        mc.addAttr(self.controlTemplate, ln='skinSet',
                   at='bool', dv=self.addToSkinSet)
        mc.setAttr('{}.skinSet'.format(self.controlTemplate),
                   keyable=True, channelBox=True)

        # Create the attribute to set the type of icon used to display the control, an eventual shape under the nsTpl object, or the handle
        #
        mc.addAttr(self.controlTemplate, ln='iconType', at='enum',
                   enumName=':'.join(ControlTemplate.iconTypes),
                   dv=ControlTemplate.iconTypes.index(self.iconType))
        self.updateIconType()

        # Create the attribute to specify if the pose node is built in the rig
        #
        mc.addAttr(self.controlTemplate, ln='buildPoseNode',
                   at='bool', dv=self.buildPoseNode)
        return True

    def updateControlTemplateAttributes(self):
        '''
        Method to retreive the values of the different nsTpl node attributes
        '''
        if not mc.objExists(self.controlTemplate):
            return True

        objType = ObjectType(self.controlTemplate)

        # test if this object has already been templated
        if not objType.isOfType('controlTemplate'):
            raise RuntimeError('[updateControlTemplateAttributes] Supplied object {} has not been templated'.format(
                self.controlTemplate))

        self.apiObject = getMObject(self.controlTemplate)
        self.isBuilt = mc.getAttr(
            '{}.isBuilt'.format(self.controlTemplate))
        self.builtType = mc.getAttr('{}.builtType'.format(
            self.controlTemplate), asString=True)
        self.location = mc.getAttr('{}.location'.format(
            self.controlTemplate), asString=True)
        self.parentScale = mc.getAttr(
            '{}.parentScale'.format(self.controlTemplate), asString=True)
        self.rotateOrder = mc.getAttr(
            '{}.rotateOrder'.format(self.controlTemplate), asString=True)
        self.isMirrored = mc.getAttr(
            '{}.isMirrored'.format(self.controlTemplate))
        self.mirrorType = mc.getAttr(
            '{}.mirrorType'.format(self.controlTemplate), asString=True)
        # in case of a change in the name
        #
        nameParser = NameParser(self.controlTemplate)
        self.baseName = nameParser.getBaseName()
        mc.setAttr('{}.name'.format(
            self.controlTemplate), self.baseName, type='string')
        self.index = nameParser.getNameIndex()
        mc.setAttr('{}.index'.format(
            self.controlTemplate), self.index, type='string')

        self.addToCtrlSet = mc.getAttr(
            '{}.ctrlSet'.format(self.controlTemplate))
        self.addToSkinSet = mc.getAttr(
            '{}.skinSet'.format(self.controlTemplate))
        self.iconType = mc.getAttr('{}.iconType'.format(
            self.controlTemplate), asString=True)
        self.buildPoseNode = mc.getAttr(
            '{}.buildPoseNode'.format(self.controlTemplate))

        self.rootPrefix = ControlTemplate.validRootPrefixes[0]
        if mc.attributeQuery('rootPrefix', node=self.controlTemplate, exists=True):
            self.rootPrefix = mc.getAttr(
                '{}.rootPrefix'.format(self.controlTemplate), asString=True)

        self.controlPrefix = ControlTemplate.validControlPrefixes[0]
        if mc.attributeQuery('controlPrefix', node=self.controlTemplate, exists=True):
            self.controlPrefix = mc.getAttr(
                '{}.controlPrefix'.format(self.controlTemplate), asString=True)

        self.skPrefix = ControlTemplate.validSkPrefixes[0]
        if mc.attributeQuery('skPrefix', node=self.controlTemplate, exists=True):
            self.skPrefix = mc.getAttr('{}.skPrefix'.format(self.controlTemplate),
                                       asString=True)

        return True

    def updateIconType(self):
        """
        During the creation or the update of the controlTemplate, iniatlize the enum attr based on what is found under the transform
        (shape, locator, handle display)
        """
        ctShapes = mc.listRelatives(self.controlTemplate, s=True, pa=True) or []
        if ctShapes:
            ctDeformableShapes = mc.ls(ctShapes, type='controlPoint') or []
            ctLocatorShapes = mc.ls(ctShapes, type='locator') or []
            if ctDeformableShapes:
                mc.setAttr('{}.iconType'.format(self.controlTemplate), ControlTemplate.iconTypes.index(ControlTemplate.iconTypes[0]))
            elif ctLocatorShapes:
                mc.setAttr('{}.iconType'.format(self.controlTemplate), ControlTemplate.iconTypes.index(ControlTemplate.iconTypes[2]))
        else:
            if mc.getAttr('{}.displayHandle'.format(self.controlTemplate)):
                mc.setAttr('{}.iconType'.format(self.controlTemplate), ControlTemplate.iconTypes.index(ControlTemplate.iconTypes[1]))
            else:
                mc.setAttr('{}.iconType'.format(self.controlTemplate), ControlTemplate.iconTypes.index(ControlTemplate.iconTypes[3]))




    @classmethod
    def locationToSuffix(cls, location):
        '''
        '''
        if isinstance(location, (str, unicode)) and location in ControlTemplate.validLocations:
            return ControlTemplate.validLocationsSuffixes[ControlTemplate.validLocations.index(location)]
        else:
            if location not in ControlTemplate.validLocations:
                raise ValueError('[locationToSuffix] Invalide location supplied')
            return ''



    @classmethod
    def inverseLocation(cls, location):
        '''
        '''
        if isinstance(location, (str, unicode)) and location in ControlTemplate.validLocations:
            return ControlTemplate.validInverseLocations[ControlTemplate.validLocations.index(location)]
        else:
            if location not in ControlTemplate.validLocations:
                raise ValueError('[inverseLocation] Invalide location supplied')
            return ''




    def getControls(self, location='all'):
        '''
        get the control nodes if built, from this nsTpl, and base on the location, if locations is 'all', all locations are returned
        '''
        controls = []
        if mc.objExists(self.controlTemplate):
            outMessagePlugs = mc.connectionInfo('{0}.message'.format(self.controlTemplate), dfs=True) or []
            if len(outMessagePlugs):
                for outMessagePlug in outMessagePlugs:
                    nd = outMessagePlug.split('.')[0]
                    if ObjectType(nd).getRigNodeType() == 'control':
                        attr = baseAttributeName(outMessagePlug)
                        if attr == 'nodes':
                            c = Control(nd)
                            if c.mirrorSide == location or location == 'all':
                                controls.append(nd)
        else:
            raise RuntimeError('[getControls] The nsTpl node {0} does not exist anymore'.format(self.controlTemplate))
        return controls

    def isControlBuilt(self, location='all'):
        '''
        Check if a nsTpl has its corresponding control built
        '''
        built = False
        if mc.objExists(self.controlTemplate):
            controls = self.getControls(location)
            if len(controls):
                built = True
        else:
            raise RuntimeError('[isControlBuilt] The nsTpl node {0} does not exist anymore'.format(self.controlTemplate))
        return built



def getObjectLocation(node, tolerance=.0001):
    '''
    Method to get the location (left, right or middle of a nsTpl node, based on the world position of the node
    '''
    if not mc.objExists(node):
        raise ValueError('[getObjectLocation] The supplied object {} does not exist'.format(node))

    if not mc.objectType(node, isAType='transform'):
        raise ValueError('[getObjectLocation] The supplied object {} is not a transform or a derivated type'.format(node))

    tolerance = fabs(tolerance)
    # the supplied object is a transform or a derivated type
    wordlPos = mc.xform(node, query=True, rp=True, a=True, ws=True)
    # round to 10 digits to avoid floating point imprecision in maya
    xpos = round(wordlPos[0], 10)

    if xpos > tolerance:
        return 'left'
    elif xpos < (tolerance * -1.0):
        return 'right'
    else:
        if xpos <= tolerance:
            return 'middle'
        else:
            return 'none'


# # ------------------------------------ TYPE ------------------------------------ # #

class ObjectType(object):
    '''
    Class used to handle the rig obj's types
    '''

    def __init__(self, obj):
        '''
        Constructor
        '''
        self.obj = ''
        self.mayaNodeType = ''
        self.rigNodeType = ''
        if mc.objExists(obj):
            self.obj = obj
            self.update()
        else:
            raise ValueError(
                '[__init__] The supplied object {} does not exist'.format(obj))

    def update(self):
        '''
        update the class attribute values
        '''
        if mc.objExists(self.obj):
            self.mayaNodeType = mc.nodeType(self.obj)
            if mc.attributeQuery('nodeType', n=self.obj, exists=True):
                self.rigNodeType = mc.getAttr(
                    '{}.nodeType'.format(self.obj))
        else:
            raise ValueError(
                '[__init__] The supplied object {} no longer exists'.format(self.obj))

    def setRigNodeType(self, rigNodeType, lockIt=False):
        '''
        Method to set the rig obj type
        '''
        success = False
        if not mc.objExists(self.obj):
            raise RuntimeError(
                '[setRigNodeType] The object {} does not exist'.format(self.obj))

        if not isinstance(rigNodeType, str):
            return success

        # If the attribute is not present
        if not mc.attributeQuery('nodeType', n=self.obj, exists=True):
            try:
                mc.addAttr(self.obj, ln='nodeType', dt='string')
                mc.setAttr('{}.nodeType'.format(
                    self.obj), rigNodeType, type='string')
                self.rigNodeType = rigNodeType
                # an attribute created on a referenced object can't be locked
                if lockIt and (not mc.referenceQuery(self.obj, isNodeReferenced=True) and not mc.lockNode(self.obj, query=True)[0]):
                    mc.setAttr('{}.nodeType'.format(
                        self.obj), lock=True)
                success = True
            except Exception:
                raise
        else:
            isLocked = mc.getAttr('{}.nodeType'.format(self.obj),
                                  lock=True)
            # an attribute created on a referenced object can't be or unlocked
            if isLocked and (not mc.referenceQuery(self.obj, isNodeReferenced=True) and not mc.lockNode(self.obj, query=True)[0]):
                try:
                    mc.setAttr('{}.nodeType'.format(
                        self.obj), lock=False)
                    mc.setAttr('{}.nodeType'.format(
                        self.obj), rigNodeType, type='string')
                    self.rigNodeType = rigNodeType
                    if lockIt:
                        mc.setAttr('{}.nodeType'.format(
                            self.obj), lock=True)
                    success = True
                except Exception:
                    raise
            elif not isLocked:
                try:
                    mc.setAttr('{}.nodeType'.format(
                        self.obj), rigNodeType, type='string')
                    self.rigNodeType = rigNodeType
                    if lockIt and (not mc.referenceQuery(self.obj, isNodeReferenced=True) and not mc.lockNode(self.obj, query=True)[0]):
                        mc.setAttr('{}.nodeType'.format(
                            self.obj), lock=True)
                    success = True
                except Exception:
                    raise
        return success




    def getRigNodeType(self):
        '''
        '''
        return self.rigNodeType


    def isOfType(self, otherType):
        '''
        compare the current class type with otherType
        '''
        isOfType = False
        if self.rigNodeType == otherType:
            isOfType = True
        elif self.mayaNodeType == otherType:
            isOfType = True

        return isOfType

# # ------------------------------------ OPEN MAYA ------------------------------------ # #


def getAttribute(node, attr):
    """Get an MObject representing an attribute from a maya node and an attribute
    :param unicode node: Maya node
    :param unicode attribute: Maya attribute
    :return: The MObject
    :rtyp: MObject
    """
    oAttribute = openMaya.MObject.kNullObj
    if mc.objExists(node) and mc.attributeQuery(attr, node=node, exists=True):
        oNode = getMObject(node)
        depFn = openMaya.MFnDependencyNode(oNode)
        oAttribute = depFn.attribute(attr)

    return oAttribute


def getMPlug(node, attribute):
    """Get a MPlug from a maya node and an attribute
    :param unicode node: Maya node
    :param unicode attribute: Maya attribute
    :return: The MPlug
    :rtyp: MPlug
    """
    plug = openMaya.MPlug()
    oNode = getMObject(node)
    oAttribute = getAttribute(node, attribute)
    if not oNode.isNull() and not oAttribute.isNull():
        plug = openMaya.MPlug(oNode, oAttribute)

    return plug


def getMObject(dn):
    """
    Utility function to get the MObject associated to a DG node
    """
    if mc.objExists(dn):
        # We create a selection
        sel = openMaya.MSelectionList()
        openMaya.MGlobal.getSelectionListByName(dn, sel)
        mo = openMaya.MObject()
        # We get the first element of the selection list
        sel.getDependNode(0, mo)
        # We return it
        return mo
    else:
        return None


def pathFromMObject(node=openMaya.MObject.kNullObj, full=False):
    """update the control withe the last full path
    """
    path = ''
    if not node.isNull():
        dagNodeFn = openMaya.MFnDagNode(node)
        dagPath = openMaya.MDagPath()
        dagNodeFn.getPath(dagPath)
        if not full:
            path = dagPath.partialPathName()
        else:
            path = dagPath.fullPathName()

    return path


# # ------------------------------------ NAMES ------------------------------------ # #
class NameParser(object):
    '''
    Class to work on the name of the object
    The rules are:
                    max 3 tokens by name, [prefix_]baseName[index][_suffix[variante]]
                    The suffix is used for the location, it is written in upperCase, if we need more information, use the lowerCamelCase baseName to add them, ex: baseNameUp01
                    The prefix is use to describe the use of the object, ex: sk, ro, c, j, hook etc.
                    The baseName in lowerCamelCase is the name of the object with eventually an index ex: sk_joint01_L, sk_joint02_L etc.
    '''
    tokensSeparator = '_'

    def __init__(self, name=None):
        '''
        Constructor
        '''
        self._name = ''
        self._shortName = ''
        self._namespace = ''
        self._path = ''
        self._prefix = ''
        self._suffix = ''
        self._index = ''
        self._baseName = ''

        self.setName(name)

    def setName(self, name):
        """
        Initialize the class
        """
        self._name = ''
        self._shortName = ''
        self._namespace = ''
        self._path = ''
        self._prefix = ''
        self._suffix = ''
        self._index = ''
        self._baseName = ''

        if isinstance(name, (str, unicode)):
            self._name = name
            self._shortName = self._name.rsplit('|', 1)[-1].rsplit(':', 1)[-1]
            # Retreive the namespace
            #
            nameTokens = self._name.rsplit('|', 1)[-1].rsplit(':', 1)
            if len(nameTokens) > 1:
                self._namespace = nameTokens[0]
            # Retreive the path
            #
            nameTokens = self._name.rsplit('|', 1)
            if len(nameTokens) > 1:
                self._path = nameTokens[0]
            # retreive the name different tokens
            #
            self.nameTokens()


    @classmethod
    def getTokensSeparator(cls):
        '''
        Method to get the tokens separator
        '''
        return NameParser.tokensSeparator


    @staticmethod
    def retreiveIndex(strName):
        '''
        Given a string, retreive the digits at the end, if no index return an empty string
        '''
        index = ''
        if isinstance(strName, (str, unicode)):
            searchResult = re.compile(r'(\d+)$').search(strName)
            if searchResult:
                index = searchResult.group(0)
        return index


    @staticmethod
    def validateToken(token, tokenType):
        '''
        Method to validate the different tokens of a name that can be build as follow:
        The different tokens are separated by the char '_'
        validName = [prefix_]baseName[index][_suffix[variante]]
        The prefix is use to define the use of an object, it must containt only lowerCase char and no digits
        The baseName is the name of the object, in lowerCamelCase, followed by an optionnal index
        The suffix is use for the object location and can be L or R but any suffix that starts with an uppercase char is ok, the suffix can be followed by optionnal
        digits to represent variants
        '''
        validToken = False
        if isinstance(token, (str, unicode)):
            if isinstance(tokenType, str):
                if tokenType == 'prefix':
                    if token.isalpha() and token.islower():  # Check if all is in lowerCase and there is no digits in this token
                        validToken = True
                elif tokenType == 'baseName':
                    if token[0:1].islower():  # Check if the first letter is in lowerCase
                        validToken = True
                elif tokenType == 'suffix':
                    # Check if the first letter is in upperCase
                    if not token[0:1].isdigit() and token[0:1].isupper():
                        validToken = True
                else:
                    raise ValueError('[validateToken] Invalid token type name supplied')
            else:
                raise ValueError('[validateToken] Invalid token type supplied')
        else:
            raise ValueError('[validateToken] Invalid token supplied')

        return validToken


    def nameTokens(self):
        '''
        Method that will retreive the prefix, baseName, index and suffix
        '''
        tokens = re.findall(r'[^{}]+'.format(NameParser.tokensSeparator), self._shortName)

        tokensCount = len(tokens)
        if tokensCount == 1:
            self._baseName = tokens[0]
            if not self._baseName:
                self._index = NameParser.retreiveIndex(self._baseName)  # Call a static method

        elif tokensCount == 3:  # Case of one prefix, the baseName and the suffix
            for token in tokens:
                # Check if all is in lowerCase and there is no digits in this token
                if NameParser.validateToken(token, 'prefix') and not self._prefix:
                    self._prefix = token
                # Check if the first letter is in lowerCase
                elif NameParser.validateToken(token, 'baseName') and not self._baseName:
                    self._baseName = token
                # A location suffix start with an upperCase (with perhaps an index if the object is part of a rig with multi instances
                elif NameParser.validateToken(token, 'suffix') and not self._suffix:
                    self._suffix = token

            # search the end digits
            #
            if not self._baseName:
                self._index = NameParser.retreiveIndex(self._baseName)

        elif tokensCount > 3:  # Case where the naming convention is not respected
            tmpTokens = []
            tmpTokens.append(tokens[0])
            tmpTokens.append('_'.join(tokens[1:-1]))
            tmpTokens.append(tokens[-1])
            for token in tmpTokens:
                # Check if all is in lowerCase and there is no digits in this token
                if NameParser.validateToken(token, 'prefix') and not self._prefix:
                    self._prefix = token
                # Check if the first letter is in lowerCase
                elif NameParser.validateToken(token, 'baseName') and not self._baseName:
                    self._baseName = token
                # A location suffix start with an upperCase (with perhaps an index if the object is part of a rig with multi instances
                elif NameParser.validateToken(token, 'suffix') and not self._suffix:
                    self._suffix = token

            # search the end digits
            #
            if self._baseName:
                self._index = NameParser.retreiveIndex(self._baseName)

        elif tokensCount == 2:
            # There is a vaid suffix (with perhaps an index if the object is part of a rig with multi instances
            if NameParser.validateToken(tokens[1], 'suffix'):
                self._suffix = tokens[1]
                if NameParser.validateToken(tokens[0], 'baseName'):
                    self._baseName = tokens[0]
                    # search the end digits
                    #
                    self._index = NameParser.retreiveIndex(self._baseName)

            else:  # Case where there is no suffix but a prefix and a baseName
                if NameParser.validateToken(tokens[0], 'prefix'):
                    self._prefix = tokens[0]
                if NameParser.validateToken(tokens[1], 'baseName'):
                    self._baseName = tokens[1]
                    # search the end digits
                    #
                    self._index = NameParser.retreiveIndex(tokens[1])

        else:
            mc.warning('[nameTokens] Unable to determine name {0} tokens, too much tokens: {1}'.format(
                self._shortName, tokensCount))

    def getShortName(self):
        '''
        Method to get the shorName of an object
        '''
        return self._shortName

    def getNamespace(self):
        '''
        Method to get the namespace
        '''
        return self._namespace

    def getPath(self):
        '''
        Method to get the path
        '''
        return self._path



    def getNamePrefix(self):
        '''
        Method to get the prefix of the object
        '''
        return self._prefix

    def setNamePrefix(self, newPrefix):
        """
        Method to set the prefix of the name
        :param newPrefix: The new prefix
        """
        if self.validateToken(newPrefix, 'prefix'):
            if self._prefix:
                self._shortName = self._shortName.replace(self._prefix, newPrefix, 1)
            else:
                self._shortName = newPrefix + self.tokensSeparator + self._shortName

            self._prefix = newPrefix

            if self._namespace:
                self._name = self._namespace + ':' + self._shortName
            else:
                self._name = self._shortName

        return self._name


    def getNameSuffix(self):
        '''
        Method to get the suffix of the object
        '''
        return self._suffix

    def setNameSuffix(self, newSuffix):
        """
        Method to set the suffix of the name
        :param newSuffix: The new suffix
        """
        if self.validateToken(newSuffix, 'suffix'):
            baseName = self._baseName
            if self._index:
                baseName += self._index

            if not self._prefix:
                self._shortName = baseName + self.tokensSeparator + newSuffix
            else:
                self._shortName = self._prefix + self.tokensSeparator + baseName + self.tokensSeparator + newSuffix

            self._suffix = newSuffix

            if self._namespace:
                self._name = self._namespace + ':' + self._shortName
            else:
                self._name = self._shortName

        return self._name

    def getBaseName(self):
        '''
        Method to get the baseName of the object
        '''
        return self._baseName

    def getNameIndex(self):
        '''
        Method to get the index of the object
        '''
        return self._index

    def getName(self):
        '''
        Method to get the name of the object
        '''
        return self._name

    def getNameWithoutPrefix(self):
        """
        Get the shortName without useCode
        """
        getNameWithoutPrefix = ''
        shortName = self.getShortName()
        prefix = self.getNamePrefix()
        if prefix:
            getNameWithoutPrefix = shortName.replace((prefix + self.getTokensSeparator()), '')
        else:
            getNameWithoutPrefix = shortName

        return getNameWithoutPrefix

    def getNameWithoutSuffix(self):
        """
        Get the shortName without useCode
        """
        getNameWithoutSuffix = ''
        shortName = self.getShortName()
        suffix = self.getNameSuffix()
        if suffix:
            getNameWithoutSuffix = shortName.replace((self.getTokensSeparator() + suffix), '')
        else:
            getNameWithoutSuffix = shortName

        return getNameWithoutSuffix


def getValidLocationSuffixes():
    return ['', 'L', 'R', '']


def isValidSuffixLocation(suffix):
    return (suffix in getValidLocationSuffixes())


def getValidLocations():
    return ['none', 'left', 'right', 'middle']


def getValidInverseLocations():
    return ['none', 'right', 'left', 'middle']


def isValidLocation(location):
    return (location in getValidLocations())


def inverseLocation(location):
    '''
    '''
    validLocations = getValidLocations()
    idx = validLocations.index(location)
    validInverseLocations = getValidInverseLocations()
    return validInverseLocations[idx]


def suffixToLocation(suffix):
    '''
    '''
    validLocationsSuffixes = getValidLocationSuffixes()
    validLocations = getValidLocations()

    location = ''
    if suffix in validLocationsSuffixes:
        idx = validLocationsSuffixes.index(suffix)
        location = validLocations[idx]

    return location


def inverseLocationSuffix(suffix):
    '''
    '''

    if not isValidSuffixLocation(suffix):
        return ''

    validInverseLocationSuffixes = ['', 'R', 'L', '']
    validInverseLocations = getValidInverseLocations()

    location = suffixToLocation(suffix)
    inverseLoc = inverseLocation(location)
    idx = validInverseLocations.index(inverseLoc)
    return validInverseLocationSuffixes[idx]


def nameWithoutPath(name):
    '''
    Remove the path from a name
    '''
    return name.rsplit('|', 1)[-1]


def namespace(name):
    '''
    get the namespace of a name
    '''
    nameNoPath = nameWithoutPath(name)
    namespace = ':'.join(nameNoPath.split(':')[:-1]) + ':'

    return namespace


def isValidObjectName(name):
    '''
    Check if a name is a valid Maya name
    '''
    result = False
    regularExpression = '[a-zA-Z_][a-zA-Z0-9_]*'
    if isinstance(name, basestring):
        if ('' != name) and ('' != regularExpression):
            matchObj = re.match(regularExpression, name)
            if matchObj:
                result = True

    return result


def setLabelsToJoints(joints, verbose=False):
    '''
    Set the label of the joints based on their name
    '''
    if isinstance(joints, list):
        for joint in joints:
            nodeType = mc.nodeType(joint)
            if 'joint' == nodeType:
                if verbose:
                    print('Labelize joint:{0}'.format(joint))

                baseName = NameParser(joint).getBaseName()
                index = NameParser(joint).getNameIndex()
                suffix = NameParser(joint).getNameSuffix()
                if verbose:
                    print('\tbaseName:{0}'.format(baseName))
                    print('\tindex:{0}'.format(index))
                    print('\tsuffix:{0}'.format(suffix))

                try:
                    mc.setAttr(('%s.type' % joint), 18)  # Other
                    mc.setAttr(('%s.otherType' % joint), ('{0}{1}'.format(
                        baseName, index)), type='string')  # Other type
                    if 'L' == suffix:
                        mc.setAttr(('%s.side' % joint), 1)
                    elif 'R' == suffix:
                        mc.setAttr(('%s.side' % joint), 2)
                    else:
                        mc.setAttr(('%s.side' % joint), 0)  # Center
                except Exception:
                    continue
            else:
                mc.warning(
                    '[setLabelsToJoints] Node {0} is not a joint'.format(joint))
    else:
        raise ValueError(
            '[setLabelsToJoints] A list of joints must be supplied')


# # ------------------------------------ ATTRIBUTES ------------------------------------ # #


def isAttributeLocked(node, attribute):
    '''
    '''
    isLocked = False
    if mc.objExists(node) and mc.attributeQuery(attribute, n=node, exists=True):
        plug = '{0}.{1}'.format(node, attribute)
        isLocked = mc.getAttr(plug, lock=True)

    return isLocked


def isAttributeUnLockable(node, attribute):
    '''
    '''
    isAttributeUnLockable = True
    if mc.objExists(node) and mc.attributeQuery(attribute, n=node, exists=True):
        isAttributeUnLockable = not (mc.referenceQuery(node, isNodeReferenced=True) or mc.lockNode(node, query=True)[0])

    return isAttributeUnLockable


def unlockAttributes(node, *attributes):
    '''
    '''
    attributes = convertListArgs(attributes)
    attrs = []
    if mc.objExists(node):
        for at in attributes:
            if mc.attributeQuery(at, n=node, exists=True):
                if isAttributeUnLockable(node, at):
                    plug = ('{0}.{1}'.format(node, at))
                    try:
                        mc.setAttr(plug, lock=False)
                        attrs.append(at)
                    except Exception:
                        mc.warning(
                            '[unlockAttributes] plug {0} can not be unlocked'.format(plug))
                        pass
    return attrs


def isDynamicAttribute(node, attribute):
    isDynamic = False
    if mc.objExists(node):
        nodeType = mc.nodeType(node)
        staticAttributes = mc.attributeInfo(type=nodeType, allAttributes=True)
        if attribute not in staticAttributes:
            isDynamic = True
    return isDynamic


def baseAttributePath(attribute):
    '''
    remove the indexes of an attribute path
    '''
    leaves = attribute.split('.')
    path = []
    for leaf in leaves:
        path.append(leaf.split('[')[0])

    return '.'.join(path)


def isAttributeHidable(node, attribute):
    '''
    '''
    isAttributeHidable = True
    if mc.objExists(node) and mc.attributeQuery(attribute, n=node, exists=True):
        isAttributeHidable = not (mc.referenceQuery(node, isNodeReferenced=True) or mc.lockNode(node, query=True)[0])

    return isAttributeHidable


def hideAttributes(node, *attributes):
    '''
    '''
    attributes = convertListArgs(attributes)
    attrs = []
    if mc.objExists(node):
        for at in attributes:
            if mc.attributeQuery(at, n=node, exists=True):
                if isAttributeHidable(node, at):
                    plug = ('{0}.{1}'.format(node, at))
                    try:
                        mc.setAttr(plug, keyable=False)
                        attrs.append(at)
                    except Exception:
                        mc.warning('[hideAttributes] plug {0} can not be hiden'.format(plug))
                        pass
    return attrs


def isPlugConnectable(plug, side):
    '''
    Check if a plug is connectable as source (side = 0) or as destination (side = 1)
    '''
    isPlugConnectable = False
    if mc.objExists(plug):
        listConnectableReadable = mc.listAttr(plug, c=True, r=True) or []
        listConnectableWritable = mc.listAttr(plug, c=True, w=True) or []

        connectableAsSource = len(listConnectableReadable) > 0
        connectableAsDest = len(listConnectableWritable) > 0

        if side:
            isPlugConnectable = connectableAsDest
        else:
            isPlugConnectable = connectableAsSource

    return isPlugConnectable


def safeDisconnectAttr(source, destination):
    """
    """
    success = False
    if isPlugConnectable(source, 0) and isPlugConnectable(destination, 1) and mc.isConnected(source, destination, iuc=True):
        nodeDest = nodeFromPlug(destination)
        locked = False
        if mc.getAttr(destination, lock=True):
            if mc.referenceQuery(nodeDest, isNodeReferenced=True) or mc.lockNode(nodeDest, query=True)[0]:
                raise RuntimeError('[safeDisconnectAttr] Destination {0} is locked and is from a reference file or on a locked node'.format(destination))
            else:
                mc.setAttr(destination, lock=False)
                locked = True

        try:
            mc.disconnectAttr(source, destination)
            mc.setAttr(destination, lock=locked)
            success = True
        except Exception:
            raise

    else:
        raise ValueError('[safeDisconnectAttr] source {0} and/or destination {1} are not respectively connectable as destination and source, or are not connected'.format(source, destination))

    return success


def safeConnectAttr(source, destination, lockState=False):
    '''
    safely connect two attributes by doing all the necessary checks before the connection
    '''
    success = False
    if isPlugConnectable(source, 0) and isPlugConnectable(destination, 1):
        if not mc.isConnected(source, destination, ignoreUnitConversion=True):
            destNode = destination.split('.')[0]
            try:
                unlocked = True
                if mc.getAttr(destination, lock=True):
                    if not mc.referenceQuery(destNode, isNodeReferenced=True) and not mc.lockNode(destNode, query=True)[0]:
                        mc.setAttr(destination, lock=False)
                    else:
                        unlocked = False
                if unlocked:
                    mc.connectAttr(source, destination, force=True)
                    if lockState:
                        if not mc.referenceQuery(destNode, isNodeReferenced=True) and not mc.lockNode(destNode, query=True)[0]:
                            mc.setAttr(destination, lock=True)

                    success = True
            except Exception:
                raise RuntimeError(
                    '[safeConnectAttr] Problem during the connection of {0} to {1}'.format(source, destination))
    else:
        raise ValueError(
            '[safeConnectAttr] source {0} and/or destination {1} are not respectively connectable as destination and source'.format(source, destination))

    return success

def isIterable(obj):
    """
    :returns: bool -- True if an object is iterable and not a string type,
    False otherwise
    """
    if isinstance(obj, basestring):
        return False
    else:
        try:
            iter(obj)
        except TypeError:
            return False

        return True


def convertListArgs(args):
    """Converts *args parameters to a simple list.
    :returns: args converted to list
    :rtype: list
    """
    if len(args) == 1 and isIterable(args[0]):
        return tuple(args[0])
    return args


def isAttributeLockable(node, attribute):
    '''
    '''
    isAttributeLockable = True
    if mc.objExists(node) and mc.attributeQuery(attribute, n=node, exists=True):
        isAttributeLockable = not (mc.referenceQuery(node, isNodeReferenced=True) or mc.lockNode(node, query=True)[0])

    return isAttributeLockable


def lockAttributes(node, *attributes):
    '''
    '''
    attributes = convertListArgs(attributes)
    attrs = []
    if mc.objExists(node):
        for at in attributes:
            if mc.attributeQuery(at, n=node, exists=True):
                if isAttributeLockable(node, at):
                    plug = ('{0}.{1}'.format(node, at))
                    try:
                        mc.setAttr(plug, lock=True)
                        attrs.append(at)
                    except Exception:
                        mc.warning('[lockAttributes] plug {0} can not be locked'.format(plug))
                        pass
    return attrs


def attributeFromPlug(plug):
    '''
    Procedure attributeFromPlug return the attributes from a plug
    '''
    tokens = plug.split(".", 1)
    attribute = ''
    if len(tokens) > 1:
        attribute = tokens[1]
    return attribute


def nodeFromPlug(plug):
    '''
    Procedure nodeFromPlug return the node from a plug
    '''
    return plug.split('.')[0]


def isPlugConnected(plug, side):
    result = False
    attr = str()
    node = str()

    if len(plug):
        node = plug.split('.')[0]
        attr = plug.split('.')[-1]
        if attr == node:
            return result

    if mc.attributeQuery(attr, node=node, exists=True):
        if side == 2:
            result = mc.connectionInfo(plug, isSource=True) or mc.connectionInfo(plug, isDestination=True)
        elif side == 1:
            result = mc.connectionInfo(plug, isSource=True)
        elif side == 0:
            result = mc.connectionInfo(plug, isDestination=True)

    return result


def attributeLeaf(attribute):
    leaf = ''
    tokens = attribute.split('.')
    if len(tokens):
        leaf = tokens[-1]

    return leaf


def baseAttributeName(plug):
    baseName = attributeLeaf(plug)
    number = baseName.split('[')[-1].split(']')[0]
    if len(number):
        baseName = baseName.split('[')[0]

    return baseName


def getMultiFirstAvailableIndex(node, attribute):
    '''
    '''
    index = -1
    plug = '{0}.{1}'.format(node, attribute)
    if not mc.objExists(plug):
        return index
    if mc.attributeQuery(baseAttributeName(attribute), n=node, multi=True):
        validIndexes = mc.getAttr(plug, multiIndices=True) or []
        size = len(validIndexes)
        index = size  # Initialized to the end of the multi
        for i in xrange(0, size):
            idx = validIndexes[i]
            if i == idx:
                continue
            index = i
            break

    return index


def attributeIndexFromPlug(plug, attribute):
    result = -1
    tokens = plug.split('.')
    for i in range(len(tokens)):
        if result == -1:
            currentAttr = tokens[i]
            number = currentAttr.split('[')[-1].split(']')[0]
            if len(number):
                currentAttrName = currentAttr.split('[')[0]
                if currentAttrName == attribute:
                    result = int(number)

    return result


def isAttributeAlias(node, attribute):
    '''
    Check if an attribute has an aliasAttr
    '''
    isAttributeAlias = False
    if mc.objExists(node):
        aliasList = mc.aliasAttr(node, query=True) or []
        isAttributeAlias = attribute in aliasList
    else:
        mc.error('{0} does not exist'.format(node))

    return isAttributeAlias


def checkNodeAttribute(nodeOrType, attr):
    '''Procedure checkNodeAttribute test if an attribute name is valid for the supplied node.
    @type nodeOrType: string
    @param nodeOrType: The node's name
    @type attr: string
    @param attr: The attribute's name to test
    @rtype: boolean
    @return: True if the passed attribute is a valid attribute name for the supplied node
    '''
    checkSuccess = False

    attributePassedPath = attr.split('.')
    attributeBasePath = []
    attrBase = ''

    # Attention il peut y avoir des 'trous' dans le path, ex: constraint.target[0].targetRotateX.
    #
    for attributePassed in attributePassedPath:
        curAttrBase = baseAttributeName(attributePassed)
        attributeBasePath.append(curAttrBase)
        if(attrBase == ''):
            attrBase = curAttrBase
        else:
            attrBase += ('.' + curAttrBase)

    node = ''
    typ = ''

    if(mc.objExists(nodeOrType)):
        node = nodeOrType
    else:
        typ = nodeOrType

    # verifie la validite des attributs passe en parametre
    #
    if(node != ''):
        # Existence des attributs
        # Support des Alias
        #
        checkSuccess = isAttributeAlias(node, attr)
        if(not checkSuccess):
            try:
                checkSuccess = mc.attributeQuery(
                    attrBase, node=node, exists=True)
            except TypeError:
                print(
                    '[checkNodeAttribute] Unexpected problem on attributeQuery command')
            # Voir pour un attribut sur la shape
            #
            if(not checkSuccess):
                # Renvoie une liste vide plutot que renvoyer NoneType afin de ne pas vautrer le for loop
                shapes = mc.listRelatives(node, shapes=True) or []
                for shape in shapes:
                    try:
                        checkSuccess = mc.attributeQuery(
                            attrBase, node=shape, exists=True)
                        if(checkSuccess):
                            break
                    except TypeError:
                        print(
                            '[checkNodeAttribute] Unexpected problem on attributeQuery command')

            if(not checkSuccess):
                childList = [attributeBasePath[0]]
                checkSuccess = True
                for i in range(len(attributeBasePath)):
                    if(not checkSuccess):
                        break
                    attrBase = attributeBasePath[i]
                    nextBase = ''
                    if i < (len(attributeBasePath) - 1):
                        nextBase = attributeBasePath[i + 1]

                    checkSuccess = False
                    while(len(childList) and not checkSuccess and not ((nextBase != '') and childList.count(nextBase))):
                        if(childList.count(attrBase)):
                            checkSuccess = True
                        else:
                            grandChildList = []
                            del grandChildList[:]  # Clear the list
                            for child in childList:
                                # Concatenate the result of attributeQuery in grandChildList
                                grandChildList.extend(mc.attributeQuery(
                                    child, node=node, listChildren=True))
                            childList = grandChildList

                    if checkSuccess:
                        try:
                            checkSuccess = mc.attributeQuery(
                                attrBase, node=node, exists=True)
                            if(checkSuccess):
                                childList = mc.attributeQuery(
                                    attrBase, node=node, listChildren=True)
                        except TypeError:
                            print(
                                '[checkNodeAttribute] Unexpected problem on attributeQuery command')
                # end for loop
        if checkSuccess:
            # Si des attributs sont passe avec une indication
            # d'index, on verifie qu'il s'agit bien de multi attributs

            for i in range(len(attributePassedPath)):
                if(checkSuccess):
                    if(attributePassedPath[i] != attributeBasePath[i]):
                        if not mc.attributeQuery(attributeBasePath[i], node=node, multi=True):
                            checkSuccess = False
            # end for loop
        # end if
    else:  # sinon c'est un type, mais ce type existe-t-il ?
        try:
            mc.ls(type=typ)
            checkSuccess = True
            childList = [attributeBasePath[0]]
            for i in range(len(attributeBasePath)):
                if(checkSuccess):
                    attrBase = attributeBasePath[i]
                    nextBase = ''
                    if i < (len(attributeBasePath) - 1):
                        nextBase = attributeBasePath[i + 1]
                    checkSuccess = False
                    while len(childList) and not checkSuccess and not ((nextBase != '') and childList.count(nextBase)):
                        if(childList.count(attrBase)):
                            checkSuccess = True
                        else:
                            grandChildList = []
                            del grandChildList[:]
                            for child in childList:
                                grandChildList.expend(mc.attributeQuery(
                                    child, type=typ, listChildren=True))
                            childList = grandChildList
                    # end while
                    if(checkSuccess):
                        try:
                            checkSuccess = mc.attributeQuery(
                                attrBase, type=typ, exists=True)
                        finally:
                            if checkSuccess:
                                childList = mc.attributeQuery(
                                    attrBase, type=typ, listChildren=True)
                    # end if
            # end for loop
            if checkSuccess:
                for i in range(len(attributePassedPath)):
                    if checkSuccess:
                        if attributePassedPath[i] != attributeBasePath[i]:
                            checkSuccess = False
            # end if
        except Exception:
            checkSuccess = False

    return checkSuccess


def checkPlug(plug):
    """Check the existance and the validity of a plug
    :param unicode plug: the to test
    :rtyp: boolean
    """
    result = False
    if plug:
        attribute = attributeFromPlug(plug)
        node = nodeFromPlug(plug)

        result = (mc.objExists(plug) and checkNodeAttribute(node, attribute))

    return result


def unPlug(basePlug, source=False, dest=False, force=False, verbose=False):
    '''
    Unplug a connected plug
    '''
    disconnected = []

    node = basePlug.split('.')[0]
    plugs = mc.listAttr(basePlug, multi=True) or []
    plugList = []
    for i in xrange(len(plugs)):
        plugList.append('{0}.{1}'.format(node, plugs[i]))
    plugList = list(set(plugList))
    if verbose:
        print('{0} plugs list: {1}'.format(basePlug, plugList))
    for plug in plugList:
        connectedSource = []
        connectedDest = []

        if source:
            connectedSource = mc.listConnections(plug, scn=True, s=True, d=False, p=True) or []
        if dest:
            connectedDest = mc.listConnections(plug, scn=True, s=False, d=True, p=True) or []

        for sourcePlug in connectedSource:
            lockState = False
            if force and mc.getAttr(plug, lock=True) and not mc.referenceQuery(node, isNodeReferenced=True) and not mc.lockNode(node, query=True)[0]:
                mc.setAttr(plug, lock=False)
                lockState = True

            try:
                mc.disconnectAttr(sourcePlug, plug)
                disconnected.append((sourcePlug, plug, lockState))
            except Exception:
                if verbose:
                    raise RuntimeWarning('[unPlug] Unable to disconnect {0} from {1}'.format(sourcePlug, plug))

        for destPlug in connectedDest:
            lockState = False
            destNode = destPlug.split('.')[0]
            if force and mc.getAttr(destPlug, lock=True) and not mc.referenceQuery(destNode, isNodeReferenced=True) and not mc.lockNode(destNode, query=True)[0]:
                mc.setAttr(destPlug, lock=False)
                lockState = True

            try:
                mc.disconnectAttr(plug, destPlug)
                disconnected.append((plug, destPlug, lockState))
            except Exception:
                if verbose:
                    raise RuntimeWarning('[unPlug] Unable to disconnect {0} from {1}'.format(plug, destPlug))

    return disconnected


def savePlugConnections(plug, side=0, force=True, verbose=False):
    '''
    Save the uptream and/or downstream connections of a plug
    '''
    dest = (side == 1 or side == 2)
    source = (side == 0 or side == 2)

    disconnected = unPlug(plug, source, dest, force, verbose)

    return disconnected


# # ------------------------------------ RIG/ANIM ------------------------------------ # #


def getSdkAnimCurves(plug, side, verbose=False):
    '''
    '''
    sdkAnimCurves = []
    outCx = []
    if not mc.objExists(plug):
        raise ValueError('[getSdkAnimCurves] Invalid plug {0} supplied'.format(plug))

    if side == 1:  # Destination
        outCx = mc.listConnections(plug, s=False, d=True, scn=True, type='animCurve') or []
        if outCx:
            sdkAnimCurves = mc.ls(outCx, exactType=['animCurveUA',
                                  'animCurveUL', 'animCurveUT',
                                  'animCurveUU'])
    elif side == 0:  # Source, quit difficult, because Maya failed to retreive with the command 'setDrivenKeyframe' drivers if other nodes than unitConversion, blendWeighted or animCurve are in the upstream graph
        # Get the type of the plug
        #
        plugType = mc.getAttr(plug, type=True, silent=True)
        # we use the graph navigation tools from the dgLib module to fing the right curves
        #
        if plugType == 'doubleAngle':
            sdkAnimCurves = getPrunedTypedConnected('animCurveUA',
                                                    plug, returnPlug=False,
                                                    source=True, destination=False,
                                                    pruneType='', depth=-1,
                                                    verbose=verbose)
        elif plugType == 'doubleLinear':
            sdkAnimCurves = getPrunedTypedConnected('animCurveUL',
                                                    plug, returnPlug=False,
                                                    source=True, destination=False,
                                                    pruneType='', depth=-1,
                                                    verbose=verbose)
        elif plugType == 'time':
            sdkAnimCurves = getPrunedTypedConnected('animCurveUT',
                                                    plug, returnPlug=False,
                                                    source=True, destination=False,
                                                    pruneType='', depth=-1,
                                                    verbose=verbose)
        else:
            sdkAnimCurves = getPrunedTypedConnected('animCurveUU',
                                                    plug, returnPlug=False,
                                                    source=True, destination=False,
                                                    pruneType='', depth=-1,
                                                    verbose=verbose)

    return sdkAnimCurves


def getDriverPlugs(drivenPlug):
    '''
    '''
    driverPlugs = []
    if not mc.objExists(drivenPlug):
        raise('[isPlugDrivenBy] The plug {0} does not exist'.format(drivenPlug))

    sdkAnimCurves = getSdkAnimCurves(drivenPlug, 0)
    if sdkAnimCurves:
        for anm in sdkAnimCurves:
            p = anm + '.input'
            inCx = mc.listConnections(p, s=True, d=False,
                                      scn=True, plugs=True) or []
            if inCx:
                driverPlugs.append(inCx[0])

    return driverPlugs


def getSdkAnimCurvesBetween(driverPlug, drivenPlug):
    '''
    '''
    if not mc.objExists(drivenPlug):
        raise(
            '[getSdkAnimCurvesBetween] The plug {0} does not exist'.format(drivenPlug))

    if not mc.objExists(driverPlug):
        raise ValueError(
            '[getSdkAnimCurvesBetween] The plug {0} does not exist'.format(driverPlug))

    inSdkAnimCurves = set(getSdkAnimCurves(drivenPlug,
                          0))  # Get input sdk curves
    outSdkAnimCurves = set(getSdkAnimCurves(driverPlug,
                           1))  # Get ouput sdk curves

    return list(inSdkAnimCurves & outSdkAnimCurves)


class AnimCurve(object):
    '''
    Class to represent animCurves inside Maya
    '''
    infinityConstantNames = {'Constant': 0, 'Linear': 1,
                             'Cycle': 3, 'Cycle with offset': 4, 'Oscillate': 5}
    infinityConstantValues = {0: 'Constant', 1: 'Linear',
                              3: 'Cycle', 4: 'Cycle with offset', 5: 'Oscillate'}
    tangentTypeConstantName = {'Fixed': 1, 'Linear': 2, 'Flat': 3, 'Step': 5, 'Slow': 6,
                               'Fast': 7, 'Spline': 9, 'Clamped': 10, 'Plateau': 16, 'StepNext': 17, 'Auto': 18}
    tangentTypeConstantValues = {1: 'Fixed', 2: 'Linear', 3: 'Flat', 5: 'Step', 6: 'Slow',
                                 7: 'Fast', 9: 'Spline', 10: 'Clamped', 16: 'Plateau', 17: 'StepNext', 18: 'Auto'}
    rotationInterpolationConstantName = {
        'None': 1, 'Euler': 2, 'Quaternion Tangent Dependent': 3, 'Quaternion Slerp': 4, 'Quaternion Squad': 5}
    rotationInterpolationConstantValues = {
        1: 'None', 2: 'Euler', 3: 'Quaternion Tangent Dependent', 4: 'Quaternion Slerp', 5: 'Quaternion Squad'}

    def __init__(self, animCurve=None, verbose=False):
        self.animCurve = None
        self.animCurveType = None
        self.keyframeCount = 0
        self.preAndPostInfinity = []
        self.weightedTangents = False
        self.rotationInterpolation = 1
        self.useCurveColor = False
        self.curveColor = [0.0, 0.0, 0.0]
        self.inTangentType = []
        self.outTangentType = []
        self.keyTanLocked = []
        self.keyWeightLocked = []
        self.inAngle = []
        self.outAngle = []
        self.inWeight = []
        self.outWeight = []
        self.keyTanInX = []
        self.keyTanInY = []
        self.keyTanOutX = []
        self.keyTanOutY = []
        self.keyBreakdown = []
        self.keyTime = []
        self.keyValue = []
        self.drivenKey = False
        self.driver = None

        if animCurve and mc.objectType(animCurve, isAType='animCurve'):
            self.animCurve = animCurve
            self.refreshAnimCurve(verbose=verbose)

    def refreshAnimCurve(self, verbose=False):
        """Fill/refresh the object
        """
        if self.animCurve and mc.objectType(self.animCurve, isAType='animCurve'):
            self.animCurveType = mc.nodeType(self.animCurve)
            self.keyframeCount = mc.keyframe(
                self.animCurve, query=True, keyframeCount=True)
            if self.keyframeCount:
                self.preAndPostInfinity.append(
                    mc.getAttr(self.animCurve + '.preInfinity'))
                self.preAndPostInfinity.append(
                    mc.getAttr(self.animCurve + '.postInfinity'))
                self.weightedTangents = mc.keyTangent(
                    self.animCurve, query=True, weightedTangents=True)[0]
                self.rotationInterpolation = mc.getAttr(
                    self.animCurve + '.rotationInterpolation ')
                self.useCurveColor = mc.getAttr(
                    self.animCurve + '.useCurveColor')
                self.curveColor = mc.getAttr(
                    self.animCurve + '.curveColor')[0]

                if self.animCurveType == 'animCurveTL' or self.animCurveType == 'animCurveTA' or self.animCurveType == 'animCurveTT' or self.animCurveType == 'animCurveTU':
                    self.keyTime = mc.keyframe(
                        self.animCurve, query=True, absolute=True, timeChange=True) or []

                elif self.animCurveType == 'animCurveUL' or self.animCurveType == 'animCurveUA' or self.animCurveType == 'animCurveUT' or self.animCurveType == 'animCurveUU':
                    self.keyTime = mc.keyframe(self.animCurve, query=True,
                                               absolute=True, floatChange=True) or []
                    self.drivenKey = True
                    inCx = mc.listConnections(self.animCurve, source=True,
                                              d=False, scn=True) or []
                    if inCx:
                        self.driver = inCx[0]

                self.keyValue = mc.keyframe(
                    self.animCurve, query=True, absolute=True, valueChange=True) or []

                self.inTangentType = mc.keyTangent(
                    self.animCurve, query=True, inTangentType=True) or []
                self.outTangentType = mc.keyTangent(
                    self.animCurve, query=True, outTangentType=True) or []

                self.keyTanLocked = mc.keyTangent(
                    self.animCurve, query=True, lock=True) or []
                self.keyWeightLocked = mc.keyTangent(
                    self.animCurve, query=True, weightLock=True) or []

                self.inAngle = mc.keyTangent(
                    self.animCurve, query=True, inAngle=True) or []
                self.outAngle = mc.keyTangent(
                    self.animCurve, query=True, outAngle=True) or []

                self.inWeight = mc.keyTangent(
                    self.animCurve, query=True, inWeight=True) or []
                self.outWeight = mc.keyTangent(
                    self.animCurve, query=True, outWeight=True) or []

                self.keyTanInX = mc.keyTangent(
                    self.animCurve, query=True, ix=True) or []
                self.keyTanInY = mc.keyTangent(
                    self.animCurve, query=True, iy=True) or []
                self.keyTanOutX = mc.keyTangent(
                    self.animCurve, query=True, ox=True) or []
                self.keyTanOutY = mc.keyTangent(
                    self.animCurve, query=True, oy=True) or []

            self.keyBreakdown = mc.keyframe(
                self.animCurve, query=True, breakdown=True) or []

        if verbose:
            self.__str__()

    def __str__(self):
        """Print the animation curve
        """
        outStr = ''
        outStr += 'AnimCurve ({0}): {1}, {2} keyframe(s)\n'.format(
            self.animCurve, self.animCurveType, self.keyframeCount)
        if self.preAndPostInfinity:
            outStr += '\tPre-infinity: {0}\n'.format(
                AnimCurve.infinityConstantValues[self.preAndPostInfinity[0]])
            outStr += '\tPost-infinity: {0}\n'.format(
                AnimCurve.infinityConstantValues[self.preAndPostInfinity[1]])
        outStr += '\tWeighted Tangents: {0}\n'.format(self.weightedTangents)
        outStr += '\tRotation Interpolation: {0}\n'.format(
            AnimCurve.rotationInterpolationConstantValues[self.rotationInterpolation])
        outStr += '\tUse Curve Color: {0}\n'.format(self.useCurveColor)
        outStr += '\tCurve Color: {0}\n'.format(self.curveColor)
        outStr += '\tDrivenKeyframe: {0}\n'.format(self.drivenKey)
        outStr += '\tDriver: {0}\n'.format(self.driver)

        for i in range(self.keyframeCount):
            outStr += '\tKeyframe[{0}]\n'.format(i)
            outStr += '\t\tkeyTime: {0}\n'.format(self.keyTime[i])
            if self.drivenKey:
                outStr += '\t\tfloatValue: {0}\n'.format(self.keyValue[i])
            else:
                outStr += '\t\tkeyValue: {0}\n'.format(self.keyValue[i])
            outStr += '\t\t\tkeyTanInType    : {0}\n'.format(
                self.inTangentType[i])
            outStr += '\t\t\tkeyTanOutType   : {0}\n'.format(
                self.outTangentType[i])
            outStr += '\t\t\tkeyTanLocked    : {0}\n'.format(
                self.keyTanLocked[i])
            outStr += '\t\t\tkeyWeightLocked : {0}\n'.format(
                self.keyWeightLocked[i])
            outStr += '\t\t\tkeyTanInAngle   : {0}\n'.format(self.inAngle[i])
            outStr += '\t\t\tkeyTanOutAngle  : {0}\n'.format(self.outAngle[i])
            outStr += '\t\t\tkeyTanInWeight  : {0}\n'.format(self.inWeight[i])
            outStr += '\t\t\tkeyTanOutWeight : {0}\n'.format(self.outWeight[i])
            outStr += '\t\t\tkeyTanInX       : {0}\n'.format(self.keyTanInX[i])
            outStr += '\t\t\tkeyTanInY       : {0}\n'.format(self.keyTanInY[i])
            outStr += '\t\t\tkeyTanOutX      : {0}\n'.format(
                self.keyTanOutX[i])
            outStr += '\t\t\tkeyTanOutY      : {0}\n'.format(
                self.keyTanOutY[i])

        if self.keyBreakdown:
            outStr += '\tBreakdown: {0}\n'.format(self.keyBreakdown)

        return outStr

    def setAnimCurveDescription(self, animCurveDescription):
        """Fill the animCurve with data from a file for example
        :param dict animCurveDict: the animCurve description
        """
        if isinstance(animCurveDescription, dict):
            for key, value in animCurveDescription.iteritems():
                if hasattr(self, key):
                    if key != 'animCurve':  # the name is not really part of a description
                        setattr(self, key, value)

    def getAnimCurveDescription(self):
        """Return the animCurve description dictionnary
        """
        description = {}
        for key, value in self.__dict__.iteritems():
            if key != 'animCurve':  # the name is not really part of a description
                description[key] = value

        return description

    def copy(self, otherAnimCurve, verbose=False):
        """copy the current animCurve to otherAnimCurve, the animCurve types must be the same
        """
        if isinstance(otherAnimCurve, AnimCurve):
            if otherAnimCurve.animCurveType is None:
                otherAnimCurve.animCurveType = self.animCurveType

            if self.animCurveType == otherAnimCurve.animCurveType:
                otherAnimCurve.setAnimCurveDescription(
                    self.getAnimCurveDescription())
                otherAnimCurve.updateAnimCurve(verbose=verbose)
            else:
                raise RuntimeError(
                    '[copy] The animCurve types are not the same')
        else:
            raise ValueError('[copy] Invalid animCurve object supplied')

    def clear(self):
        """Clear all the key from an animCurve
        """
        if self.animCurve and mc.objExists(self.animCurve):
            keyframeCount = mc.keyframe(
                self.animCurve, query=True, keyframeCount=True)
            if keyframeCount:
                animCurveType = mc.nodeType(self.animCurve)
                isDrivenKeyframe = any([animCurveType == 'animCurveUL',
                                        animCurveType == 'animCurveUA',
                                        animCurveType == 'animCurveUT',
                                        animCurveType == 'animCurveUU'])
                if not isDrivenKeyframe:
                    keyTime = mc.keyframe(self.animCurve, query=True,
                                          absolute=True, timeChange=True) or []
                else:
                    keyTime = mc.keyframe(self.animCurve, query=True,
                                          absolute=True, floatChange=True) or []

                mc.lockNode(self.animCurve, lock=True)
                for i in range(self.keyframeCount):
                    if not isDrivenKeyframe:
                        mc.cutKey(self.animCurve, time=(keyTime[i],))
                    else:
                        mc.cutKey(self.animCurve, float=(keyTime[i],))

                mc.lockNode(self.animCurve, lock=False)

    def updateAnimCurve(self, verbose=False):
        """Apply the curve description to the Maya node
        """
        if not self.animCurve or not mc.objExists(self.animCurve):
            return
        # clear the keys if present
        #
        self.clear()
        try:
            mc.setAttr(self.animCurve + '.rotationInterpolation',
                       self.rotationInterpolation)
        except Exception:
            pass

        isDrivenKeyframe = self.drivenKey

        for i in range(self.keyframeCount):
            breakdown = False
            if self.keyTime[i] in self.keyBreakdown:
                breakdown = True

            if verbose:
                print ('Set keyframe ', i, 'on', self.animCurve, 'time/float:', self.keyTime[i],
                       'value:', self.keyValue[i], 'breakdown:', breakdown)

            if not isDrivenKeyframe:
                mc.setKeyframe(self.animCurve, time=(
                    self.keyTime[i],), value=self.keyValue[i], breakdown=breakdown)
                mc.keyTangent(self.animCurve, edit=True, time=(self.keyTime[i],),
                              inTangentType=self.inTangentType[i], outTangentType=self.outTangentType[i],
                              inAngle=self.inAngle[i], outAngle=self.outAngle[i],
                              inWeight=self.inWeight[i], outWeight=self.outWeight[i],
                              lock=self.keyTanLocked[i],
                              )
            else:
                mc.setKeyframe(self.animCurve, float=(
                    self.keyTime[i],), value=self.keyValue[i], breakdown=breakdown)
                mc.keyTangent(self.animCurve, edit=True, float=(self.keyTime[i],),
                              inTangentType=self.inTangentType[i], outTangentType=self.outTangentType[i],
                              inAngle=self.inAngle[i], outAngle=self.outAngle[i],
                              inWeight=self.inWeight[i], outWeight=self.outWeight[i],
                              lock=self.keyTanLocked[i],
                              )

        if self.weightedTangents:
            print('weightedTangents:', self.weightedTangents)

            mc.keyTangent(self.animCurve, edit=True,
                          weightedTangents=self.weightedTangents)
            for i in range(self.keyframeCount):
                print ('time/float:', self.keyTime[i], 'weightLocked:', self.keyWeightLocked[i])
                if not isDrivenKeyframe:
                    mc.keyTangent(self.animCurve, edit=True, time=(self.keyTime[i],), weightLock=self.keyWeightLocked[i],
                                  ix=self.keyTanInX[i], iy=self.keyTanInY[i], ox=self.keyTanOutX[i], oy=self.keyTanOutY[i],
                                  )
                else:
                    mc.keyTangent(self.animCurve, edit=True, float=(self.keyTime[i],), weightLock=self.keyWeightLocked[i],
                                  ix=self.keyTanInX[i], iy=self.keyTanInY[i], ox=self.keyTanOutX[i], oy=self.keyTanOutY[i],
                                  )

        mc.setAttr(self.animCurve + '.preInfinity',
                   self.preAndPostInfinity[0])
        mc.setAttr(self.animCurve + '.postInfinity',
                   self.preAndPostInfinity[1])

        mc.setAttr(self.animCurve + '.useCurveColor', self.useCurveColor)
        mc.setAttr(self.animCurve + '.curveColor',
                   self.curveColor[0], self.curveColor[1], self.curveColor[2], type='double3')

    def duplicate(self, verbose=False):
        """Create a new animCurve based on the current anim curve description
        """
        animCurve = None
        if isinstance(self.animCurveType, basestring) and self.keyframeCount > 0:
            animCurveNode = mc.createNode(self.animCurveType, ss=True)
            animCurve = AnimCurve(animCurveNode)
            self.copy(animCurve, verbose=verbose)

        return animCurve


def setAnimCurveInfinity(animCurve, preInfinity='Constant', postInfinity='Constant'):
    '''
    Set the infinity of an animCurve
    '''
    infinity = {'Constant': 0, 'Linear': 1, 'Cycle': 3, 'Cycle with Offset': 4, 'Oscillate': 5}
    try:
        if mc.objExists(animCurve) and mc.objectType(animCurve, isAType='animCurve'):
            mc.setAttr('{0}.preInfinity'.format(animCurve), infinity[preInfinity])
            mc.setAttr('{0}.postInfinity'.format(animCurve), infinity[postInfinity])
    except Exception:
        raise


def setPlugAnimCurveInfinity(plug, side=0, preInfinity='Constant',
                             postInfinity='Constant', verbose=False):
    '''
    Set the infinity of an upstream, downStream or both animCurve connected to a plug
    '''
    animCurves = list()
    try:
        if mc.objExists(plug):
            if side == 0:
                animCurves = getPrunedTypedConnected('animCurve',
                                                     plug, False, True,
                                                     False, 'dagNode',
                                                     -1, verbose)
            elif side == 1:
                animCurves = getPrunedTypedConnected('animCurve',
                                                     plug, False, False,
                                                     True, 'dagNode',
                                                     -1, verbose)
            elif side == 2:
                animCurves = getPrunedTypedConnected('animCurve',
                                                     plug, False, True,
                                                     True, 'dagNode',
                                                     1, verbose)

            if animCurves:
                for animCurve in animCurves:
                    setAnimCurveInfinity(animCurve, preInfinity, postInfinity)
    except Exception:
        raise


def setDrivenKey(driverPlug, driverValue, drivenPlug, drivenValue, staticCurves=True, blendWeighted=True, createDefaultKey=True, itt='linear', ott='linear', preInfinity='Constant', postInfinity='Constant', verbose=False):
    """Set a driven key on a channel
    :param unicode driverPlug: The driver plug driverNode.driverAttribute
    :param float driverValue: The driver value
    :param unicode drivenPlug: The driven plug drivenNode.drivenAttribute
    :param float drivenValue: The driven value
    :param boolean blendWeighted: if blendWeighted is False, multi drivers values are multiplied and not a weighted sum
    :param str itt: the input tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next", "fixed", "clamped", "plateau", "auto" if None, use linear input tangent type
    :param str ott: the output tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next", "fixed", "clamped", "plateau", "auto" if None, use linear output tangent type
    :param str preInfinity: The pre-infinity of the animCurve, can be "Constant", "Linear", "Cycle", "Cycle with Offset", "Oscillate"
    :param str postInfinity: The post-infinity of the animCurve, can be "Constant", "Linear", "Cycle", "Cycle with Offset", "Oscillate"
    :param boolean verbose: print debug infos
    :return The created or modified animCurve
    :rtyp: unicode
    """
    animCurve = None
    if not checkPlug(driverPlug):
        raise ValueError('[setDrivenKey] Supplied driver plug {0} is invalid'.format(driverPlug))

    if not checkPlug(drivenPlug):
        raise ValueError('[setDrivenKey] Supplied driven plug {0} is invalid'.format(drivenPlug))

    driverNode = nodeFromPlug(driverPlug)
    driverAttr = mc.attributeName(driverPlug, l=True)
    driverPlug = driverNode + '.' + driverAttr  # a plug with long attribute name is rebuilt, Maya returns always long name, it will be required for attributes comparison
    drivenNode = nodeFromPlug(drivenPlug)
    drivenAttr = attributeFromPlug(drivenPlug)
    driverDefault = mc.attributeQuery(driverAttr, node=driverNode, listDefault=True)[0]
    drivenDefault = mc.attributeQuery(drivenAttr, node=drivenNode, listDefault=True)[0]

    if verbose:
        print ('create default key ', driverPlug,
               driverDefault, '->', drivenPlug,
               drivenDefault)

    if verbose:
        print ('SDK: ', driverPlug, driverValue, '->', drivenPlug,
               drivenValue, 'blendWeighted:', blendWeighted, itt,
               ott, preInfinity, postInfinity)

    validTangentTypes = ["spline", "linear", "fast", "slow",
                         "flat", "stepped", "step next", "fixed",
                         "clamped", "plateau", "auto"]

    inTanType = 'linear'
    outTanType = 'linear'

    # Search for upstream sdk anim curve
    #
    sdkAnimCurves = getSdkAnimCurves(drivenPlug, 0)
    # An animation curve exists
    #
    if sdkAnimCurves:
        if verbose:
            print ('Input sdk animation curves found on', drivenPlug)
        driverPlugs = getDriverPlugs(drivenPlug)  # Is there already a sdk animCurve between driverPlug and drivenPlug
        if driverPlug in driverPlugs:  # The animeCurve is modified
            if verbose:
                print ('\tDriver', driverPlug, 'already used')
            sdkAnimCurves = getSdkAnimCurvesBetween(driverPlug, drivenPlug)
            # In the majority of the cases there will only be one curve, but in the case of a more complex rig, more than one curves can be blended, multiplied
            # added, handled by condition nodes etc, so it's hard to take the right decision about how to handle multi input curves to one driven attribute coming from one driver.
            # At this time, I take the decision to handle the first curve found
            #
            animCurve = sdkAnimCurves[0]
            animCurveObject = AnimCurve(animCurve)
            keyTime = animCurveObject.keyTime
            if driverValue not in keyTime:
                if verbose:
                    print ('\t\tDriver value', driverValue,
                           'is not in keyTime, key created for driven value',
                           drivenValue)

                if isinstance(itt, basestring) and itt in validTangentTypes:
                    inTanType = itt

                if isinstance(ott, basestring) and ott in validTangentTypes:
                    outTanType = ott

                mc.setKeyframe(animCurve, float=driverValue, value=drivenValue, itt=inTanType, ott=outTanType)
            else:
                if verbose:
                    print ('\t\tDriver value', driverValue,
                           'is in keyTime, key updated for driven value',
                           drivenValue)

                if isinstance(itt, basestring) and itt in validTangentTypes:
                    inTanType = itt

                if isinstance(ott, basestring) and ott in validTangentTypes:
                    outTanType = ott

                mc.setKeyframe(animCurve, float=driverValue, value=drivenValue, itt=inTanType, ott=outTanType)
                mc.keyTangent(animCurve, edit=True, float=(driverValue,), itt=inTanType)
                mc.keyTangent(animCurve, edit=True, float=(driverValue,), ott=outTanType)

            # Tune the pre and post infinity
            #
            setAnimCurveInfinity(animCurve, preInfinity, postInfinity)

        else:
            if verbose:
                print('Driver',
                      driverPlug, 'never used')
            # There are effectively sdk animCurves connected to this driven plug, but the current driver is a new one, here there are two case
            # n°1: channels like translate or rotate, even shear can be handled automatically by the setDrivenKeyframe command, and a blendWeighted node will be add
            # n°2: scale or poseScale channels for example must be handled differently,the scalability of an object is a multiplicative process, multDoubleLinear  nodes will be added in place of blendWeighted nodes
            # and a linear animCurve will be add to emulate a passive connection
            #
            if not staticCurves and drivenValue == drivenDefault:
                if verbose:
                    mc.warning('[setDrivenKey] No static curves allowed, skip value {0} for driven {1}'.format(drivenValue, drivenNode))
                return

            if blendWeighted:  # Case n°1
                if mc.getAttr(drivenPlug, se=True):
                    if createDefaultKey:
                        mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverDefault, value=drivenDefault, inTangentType='spline', outTangentType='linear')

                    mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverValue, value=drivenValue, inTangentType=inTanType, outTangentType=outTanType)
                    # Tune the pre and post infinity
                    #
                    animCurves = getSdkAnimCurvesBetween(driverPlug, drivenPlug)
                    if animCurves:
                        for animCurve in animCurves:
                            setAnimCurveInfinity(animCurve, preInfinity, postInfinity)
                            setAnimCurveInfinity(animCurve, preInfinity, postInfinity)
                else:
                    mc.warning('[setDrivenKey] Driven plug {0} is not settable'.format(drivenPlug))
            else:  # Case n°2
                # Before doing anything, we try to find the first upstream multDoubleLinear present if more than one driver exists on the driven plug
                #
                multDoubleLinear = getFirstTypedConnected('multDoubleLinear', drivenPlug, False, True, False, -1, False)
                linearCurve = ''
                if mc.objExists(multDoubleLinear):
                    if verbose:
                        print ('\tOther driver for', drivenPlug,
                               'have been found, searching the linear curve that emulate a passive connection')
                    # If a multDoubleLinear has been found, there is usually the linear animCurve dowstream this node to emulate a passive connection
                    #
                    linearCurve = getFirstTypedConnected('animCurve', ('{0}.output'.format(multDoubleLinear)), False, False, True, -1, False)
                    if mc.objExists(linearCurve):
                        drivenPlug = '{0}.input'.format(linearCurve)

                plugInitialCx = savePlugConnections(drivenPlug, side=0, force=True)  # Initial curve output on plugInitialCx[0][0]
                if createDefaultKey:
                    mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverDefault,
                                         value=drivenDefault, inTangentType='spline',
                                         outTangentType='linear')

                mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverValue,
                                     value=drivenValue, inTangentType=inTanType,
                                     outTangentType=outTanType)
                # Tune the pre and post infinity
                #
                animCurves = getSdkAnimCurvesBetween(driverPlug, drivenPlug)
                if animCurves:
                    for animCurve in animCurves:
                        setAnimCurveInfinity(animCurve, preInfinity, postInfinity)
                plugNewCx = savePlugConnections(drivenPlug, side=0, force=True)  # Initial curve output on plugNewCx[0][0]
                newMultDoubleLinear = insertMultDoubleLinear(plugInitialCx[0][0], plugNewCx[0][0], drivenPlug, side=None, name='multDoubleLinear#')
                if not mc.objExists(linearCurve):
                    insertLinearCurve('{0}.output'.format(newMultDoubleLinear), drivenPlug, mult=1.0, reuseInput=True)
    # No animation curve
    #
    else:
        if not staticCurves and drivenValue == drivenDefault:
            if verbose:
                mc.warning('[setDrivenKey] No static curves allowed, skip value {0} for driven {1}'.format(drivenValue, drivenNode))
            return

        if mc.getAttr(drivenPlug, se=True):
            if verbose:
                print('No input sdk animation curves on', drivenPlug)
            if isinstance(itt, basestring) and itt in validTangentTypes:
                inTanType = itt

            if isinstance(ott, basestring) and ott in validTangentTypes:
                outTanType = ott

            if createDefaultKey:
                mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverDefault, value=drivenDefault, inTangentType='spline', outTangentType='linear')

            mc.setDrivenKeyframe(drivenPlug, cd=driverPlug, driverValue=driverValue, value=drivenValue, inTangentType=inTanType, outTangentType=outTanType)
            # Tune the pre and post infinity
            #
            setPlugAnimCurveInfinity(drivenPlug, side=0, preInfinity=preInfinity, postInfinity=postInfinity, verbose=False)
            animCurve = getFirstTypedConnected('animCurve', drivenPlug, False, True, False, -1, False)
        else:
            mc.warning('[setDrivenKey] Driven plug {0} is not settable'.format(drivenPlug))

    return animCurve


def insertLinearCurve(plug, otherPlug, mult=1.0, reuseInput=True):
    """This method is mainly used to simulate passive connection to a node
    :param unicode plug: input plug
    :param unicode otherPlug: output plug
    :param float mult: the slop of the curve, if 1.0, the slop is 1
    :return: the new animCurve
    :rtyp: unicode
    :raises: ValueError Invalid upstream plug
    :raises: ValueError Invalid downstream plug
    :raises: RuntimeError Downstream otherPlug is locked in a referenced file
    """
    if not checkPlug(plug):
        raise ValueError('[insertLinearCurve] Invalid upstream plug '.format(plug))

    if not checkPlug(otherPlug):
        raise ValueError('[insertLinearCurve] Invalid downstream plug '.format(otherPlug))

    node = nodeFromPlug(otherPlug)
    locked = False
    if mc.getAttr(otherPlug, lock=True):
        if not mc.referenceQuery(node,
                                 isNodeReferenced=True) and not mc.lockNode(node, query=True)[0]:
            mc.setAttr(otherPlug, lock=False)
            locked = True
        else:
            raise RuntimeError('[insertLinearCurve] Downstream plug {0} is locked in a referenced file'.format(otherPlug))

    inCx = mc.connectionInfo(otherPlug, sfd=True)
    if mc.objExists(inCx):
        try:
            if mc.nodeType(inCx) == 'unitConversion':
                unitConversion = nodeFromPlug(inCx)
                inCx = mc.connectionInfo('{0}.input'.format(unitConversion), sfd=True)
                mc.disconnectAttr(inCx, '{0}.input'.format(unitConversion))
                mc.disconnectAttr('{0}.output'.format(unitConversion), otherPlug)
                if not mc.referenceQuery(unitConversion, isNodeReferenced=True) and not mc.lockNode(unitConversion, query=True)[0]:
                    mc.delete(unitConversion)
                else:
                    mc.warning('[insertLinearCurve] Unable to delete node {0} from a referenced file'.format(unitConversion))
            else:
                mc.disconnectAttr(inCx, otherPlug)
        except Exception:
            raise

        if reuseInput is True:
            plug = inCx

    mc.setDrivenKeyframe(otherPlug, cd=plug, driverValue=.0,
                         value=.0, inTangentType='spline', outTangentType='spline')
    mc.setDrivenKeyframe(otherPlug, cd=plug, driverValue=1.0,
                         value=mult, inTangentType='spline', outTangentType='spline')

    mc.setAttr(otherPlug, lock=locked)
    # Tune the pre and post infinity
    #
    animCurve = getFirstTypedConnected('animCurve', otherPlug, False, True, False, -1, False)
    if animCurve:
        mc.setAttr('{0}.preInfinity'.format(animCurve), 1)
        mc.setAttr('{0}.postInfinity'.format(animCurve), 1)

    return animCurve


def setJointDrawStyle(joint, drawStyle='Bone'):
    '''
    Set the display of a joint
    :param Maya joint: joint
    :param str: drawStyle
    '''
    success = False
    if mc.objExists(joint) and mc.objectType(joint, isAType='joint'):
        validDrawStyle = {'Bone': 0, 'Multi-child as Box': 1, 'None': 2}
        if drawStyle in validDrawStyle:
            try:
                mc.setAttr('{0}.drawStyle'.format(joint),
                           validDrawStyle.setdefault(drawStyle, 0))
                success = True
            except Exception:
                pass

    return success


def setSkinClusterInMoveJointsMode(skinClusters, state=True):
    """Set the skinClusters in a mode where the bindPreMatrix are automatically updated
    when the skin joints are moved
    :param list skinClusters: the list of skinClusters
    :param boolean state: the state of moveJointsMode
    """
    if isinstance(skinClusters, (list, tuple)):
        for skinCluster in skinClusters:
            try:
                mc.skinCluster(skinCluster, edit=True, moveJointsMode=state)
            except Exception:
                continue


def jointOrientToRotate(joint):
    '''
    Concatenate the complete rotation matrix to the rotate
    '''
    if not mc.objExists(joint):
        mc.error('[jointOrientToRotate] The supplied joint {0} does not exist'.format(joint))
    if not mc.objectType(joint, isAType='joint'):
        mc.error('[jointOrientToRotate] The supplied node {0} is not a joint or a derivate type'.format(joint))
    try:
        selectionList = om.MSelectionList()
        selectionList.add(joint)
        dagPath = selectionList.getDagPath(0)
        inclusiveMatrix = dagPath.inclusiveMatrix()
        exclusiveMatrixInverse = dagPath.exclusiveMatrixInverse()
        matrix = inclusiveMatrix * exclusiveMatrixInverse
        transformationMatrix = om.MTransformationMatrix(matrix)
        eulerRotation = transformationMatrix.rotation(asQuaternion=False)
        eulerRotation.reorderIt(mc.getAttr("{0}.rotateOrder".format(joint)))
        rx = om.MAngle(eulerRotation.x).asDegrees()
        ry = om.MAngle(eulerRotation.y).asDegrees()
        rz = om.MAngle(eulerRotation.z).asDegrees()
        mc.setAttr("{0}.rotateAxis".format(joint), .0, .0, .0)
        mc.setAttr("{0}.rotate".format(joint), rx, ry, rz)
        mc.setAttr("{0}.jointOrient".format(joint), .0, .0, .0)
    except Exception:
        raise


def rotateToJointOrient(joint):
    '''
    Concatenate the complete rotation matrix to the jointOrient
    '''
    if not mc.objExists(joint):
        mc.error('[rotateToJointOrient] The supplied joint {0} does not exist'.format(joint))

    if not mc.objectType(joint, isAType='joint'):
        mc.error('[rotateToJointOrient] The supplied node {0} is not a joint or a derivate type'.format(joint))

    try:
        selectionList = om.MSelectionList()
        selectionList.add(joint)
        dagPath = selectionList.getDagPath(0)

        inclusiveMatrix = dagPath.inclusiveMatrix()
        exclusiveMatrixInverse = dagPath.exclusiveMatrixInverse()
        matrix = inclusiveMatrix * exclusiveMatrixInverse
        transformationMatrix = om.MTransformationMatrix(matrix)

        eulerRotation = transformationMatrix.rotation(asQuaternion=False)
        jointOrientX = om.MAngle(eulerRotation.x).asDegrees()
        jointOrientY = om.MAngle(eulerRotation.y).asDegrees()
        jointOrientZ = om.MAngle(eulerRotation.z).asDegrees()

        mc.setAttr('{0}.rotateAxisX'.format(joint), .0)
        mc.setAttr('{0}.rotateAxisY'.format(joint), .0)
        mc.setAttr('{0}.rotateAxisZ'.format(joint), .0)

        mc.setAttr('{0}.rotateX'.format(joint), .0)
        mc.setAttr('{0}.rotateY'.format(joint), .0)
        mc.setAttr('{0}.rotateZ'.format(joint), .0)

        mc.setAttr('{0}.jointOrientX'.format(joint), jointOrientX)
        mc.setAttr('{0}.jointOrientY'.format(joint), jointOrientY)
        mc.setAttr('{0}.jointOrientZ'.format(joint), jointOrientZ)
    except Exception:
        raise


def setDisplayOverrides(node, enable=True, displayType='Normal', levelOfDetail='Full', color=0, overrideShading=True):
    '''
    Set the drawing overrides of a Maya DagNode
    '''
    displayTypes = {'Normal': 0, 'Template': 1, 'Reference': 2}
    levelOfDetails = {'Full': 0, 'Bounding Box': 1}
    color = min(max(color, 0), 31)
    if mc.objExists(node) and mc.objectType(node, isAType='dagNode'):
        try:
            # OverrideEnabled
            #
            if isAttributeLocked(node, 'overrideEnabled'):
                if isAttributeUnLockable(node, 'overrideEnabled'):
                    unlockAttributes(node, 'overrideEnabled')
                    if not isPlugConnected('{0}.overrideEnabled'.format(node), 0):
                        mc.setAttr(
                            '{0}.overrideEnabled'.format(node), enable)
                else:
                    mc.warning(
                        '[setDisplayOverrides] Unable to set "overrideEnabled" attribute to {0} on node {1}'.format(enable, node))
            else:
                if not isPlugConnected('{0}.overrideEnabled'.format(node), 0):
                    mc.setAttr('{0}.overrideEnabled'.format(node), enable)

            # OverrideDisplayType
            #
            if isAttributeLocked(node, 'overrideDisplayType'):
                if isAttributeUnLockable(node, 'overrideDisplayType'):
                    unlockAttributes(node, 'overrideDisplayType')
                    if not isPlugConnected('{0}.overrideDisplayType'.format(node), 0):
                        mc.setAttr('{0}.overrideDisplayType'.format(
                            node), displayTypes.get(displayType, 0))
                else:
                    mc.warning(
                        '[setDisplayOverrides] Unable to set "overrideDisplayType" attribute to {0} on node {1}'.format(enable, node))
            else:
                if not isPlugConnected('{0}.overrideDisplayType'.format(node), 0):
                    mc.setAttr('{0}.overrideDisplayType'.format(
                        node), displayTypes.get(displayType, 0))

            # OverrideLevelOfDetail
            #
            if isAttributeLocked(node, 'overrideLevelOfDetail'):
                if isAttributeUnLockable(node, 'overrideLevelOfDetail'):
                    unlockAttributes(
                        node, 'overrideLevelOfDetail')
                    if not isPlugConnected('{0}.overrideLevelOfDetail'.format(node), 0):
                        mc.setAttr('{0}.overrideLevelOfDetail'.format(
                            node), levelOfDetails.get(levelOfDetail, 0))
                else:
                    mc.warning(
                        '[setDisplayOverrides] Unable to set "overrideLevelOfDetail" attribute to {0} on node {1}'.format(enable, node))
            else:
                if not isPlugConnected('{0}.overrideLevelOfDetail'.format(node), 0):
                    mc.setAttr('{0}.overrideLevelOfDetail'.format(
                        node), levelOfDetails.get(levelOfDetail, 0))

            # OverrideColor
            #
            if isAttributeLocked(node, 'overrideColor'):
                if isAttributeUnLockable(node, 'overrideColor'):
                    unlockAttributes(node, 'overrideColor')
                    if not isPlugConnected('{0}.overrideColor'.format(node), 0):
                        mc.setAttr('{0}.overrideColor'.format(node), color)
                else:
                    mc.warning(
                        '[setDisplayOverrides] Unable to set "overrideColor" attribute to {0} on node {1}'.format(enable, node))
            else:
                if not isPlugConnected('{0}.overrideColor'.format(node), 0):
                    mc.setAttr('{0}.overrideColor'.format(node), color)

            # OverrideShading
            if isAttributeLocked(node, 'overrideShading'):
                if isAttributeUnLockable(node, 'overrideShading'):
                    unlockAttributes(node, 'overrideShading')
                    if not isPlugConnected('{0}.overrideShading'.format(node), 0):
                        mc.setAttr('{0}.overrideShading'.format(
                            node), overrideShading)
                else:
                    mc.warning('[setDisplayOverrides] Unable to set "overrideShading" attribute to {0} on node {1}'.format(
                        overrideShading, node))
            else:
                if not isPlugConnected('{0}.overrideShading'.format(node), 0):
                    mc.setAttr('{0}.overrideShading'.format(
                        node), overrideShading)

        except Exception:
            raise
    else:
        raise ValueError(
            '[setDisplayOverrides] The supplied node does not exist or is not a DagNode')


def addShape(transformOrShape, otherTransform, space='world', symmetry=[1.0, 1.0, 1.0], delSource=False):
    '''
    Duplicate a shape under a transform/joint and place it under a destination transform/joint, the copie can be in local or world space
    '''
    duplicateShape = ''
    if mc.objExists(otherTransform) and mc.objectType(otherTransform, isAType='transform'):
        if mc.objExists(transformOrShape):
            shape = getFirstShape(transformOrShape)
            # Unlock potential locked channels on the cvs of the shape
            #
            if mc.attributeQuery('controlPoints', node=shape, exists=True):
                cvCount = mc.getAttr(shape + '.controlPoints', size=True)
                if cvCount:
                    channels = ['x', 'y', 'z']
                    for i in xrange(cvCount):
                        for j in xrange(len(channels)):
                            plug = '{0}.controlPoints[{1}].{2}Value'.format(
                                shape, i, channels[j])
                            try:
                                mc.setAttr(plug, lock=False)
                            except Exception:
                                pass

            firstTransform = getFirstTransform(shape)
            # Create a dummy object so the transformations can be frozen as well as reset without the instance connections problems
            #
            emptyGroup = mc.createNode('transform', parent=firstTransform)
            emptyGroup = mc.parent(emptyGroup, world=True)
            dummyShape = mc.parent(shape, emptyGroup, add=True, s=True)[0]
            # Now we can duplicate the dummy en parent it under the destination transform and freeze + reset the transformations
            #
            duplicateTransform = mc.duplicate(emptyGroup,
                                              renameChildren=True,
                                              returnRootsOnly=True)[0]
            # we don't need the empty group anymore
            #
            mc.delete(emptyGroup)

            if mc.objExists(shape) and mc.objectType(shape, isAType='shape'):
                if space == 'local':
                    # here we apply the symmetry (scales) in local space
                    #
                    duplicateTransform = mc.parent(
                        duplicateTransform, otherTransform)[0]
                    mc.makeIdentity(duplicateTransform,
                                    apply=False, t=True, r=True, s=True)
                    duplicateTransform = mc.parent(
                        duplicateTransform, world=True)[0]
                    mc.xform(duplicateTransform, r=True,
                             os=True, scale=symmetry)
                    # Removed for the specular, must be tested more deeply
                    #
                    # mc.makeIdentity(duplicateTransform, apply=True, t=False, r=False, s=True)
                elif space == 'world':
                    # here we apply the symmetry (scales) in world space
                    #
                    scaleGroup = mc.createNode('transform')
                    duplicateTransform = mc.parent(
                        duplicateTransform, scaleGroup)[0]
                    mc.xform(scaleGroup, a=True, ws=True, scale=symmetry)
                    mc.makeIdentity(scaleGroup, apply=True,
                                      t=False, r=False, s=True)
                    duplicateTransform = mc.parent(
                        duplicateTransform, world=True)[0]
                    mc.delete(scaleGroup)
                    # Now we transform the node space to the destination node by parenting it and freezing + reseting its coordinnates
                    #
                    duplicateTransform = mc.parent(
                        duplicateTransform, otherTransform)[0]
                    mc.makeIdentity(duplicateTransform,
                                    apply=True, t=True, r=True, s=True)
                    mc.makeIdentity(duplicateTransform,
                                    apply=False, t=True, r=True, s=True)
                    duplicateTransform = mc.parent(
                        duplicateTransform, world=True)[0]

                # Eventualy clean the shapeOrig, shouldn't have any of them
                #
                cleanShapeOrig(duplicateTransform, fix=True)
                duplicateShape = getFirstShape(duplicateTransform)
                duplicateShape = mc.parent(
                    duplicateShape, otherTransform, add=True, s=True)[0]
                # Format the new shape name
                #
                prefix = NameParser(otherTransform).getNamePrefix()
                baseName = NameParser(otherTransform).getBaseName()
                index = NameParser(otherTransform).getNameIndex()
                suffix = NameParser(otherTransform).getNameSuffix()
                separator = NameParser.getTokensSeparator()

                newShapeName = baseName
                if index:
                    newShapeName += index + 'Shape'
                else:
                    newShapeName += 'Shape'

                if prefix:
                    newShapeName = prefix + separator + newShapeName

                if suffix:
                    newShapeName += separator + suffix

                duplicateShape = mc.rename(duplicateShape, newShapeName)
                setDisplayOverrides(
                    duplicateShape, enable=False, displayType='Normal', levelOfDetail='Full', color=0)
                # Delete contruction nodes
                #
                mc.delete(duplicateTransform)

            else:
                raise ValueError(
                    '[addShape] Invalid space "{0}" supplied'.format(space))

            if delSource:
                try:
                    mc.delete(transformOrShape)
                except Exception:
                    raise

    return duplicateShape


def mirrorLocalPosition(node, mirrorNode, localPosition=om.MPoint.kOrigin, symmetryAxis=om.MVector.kXaxisVector):
    '''
    Take a point node local space, find the same point mirrored
    '''
    mirrorLocalPosition = om.MPoint.kOrigin
    if all([mc.objExists(node), mc.objectType(node, isAType='transform'),
            mc.objExists(mirrorNode),
            mc.objectType(mirrorNode, isAType='transform')]):
        symMatrix = symmetryMatrix(symmetryAxis)
        wm = mc.getAttr('{0}.worldMatrix'.format(node))
        wim = mc.getAttr('{0}.worldInverseMatrix'.format(mirrorNode))
        worldMatrix = om.MMatrix(wm)
        worldInverseMatrix = om.MMatrix(wim)
        worldPosition = localPosition * worldMatrix
        mirrorWorldPosition = worldPosition * symMatrix
        mirrorLocalPosition = mirrorWorldPosition * worldInverseMatrix

    return mirrorLocalPosition


# # ------------------------------------ DAG NODES ------------------------------------ # #


def shearMatrixFromNodeAxis(node, symetryAxis=None, verbose=False):
    """Mirror the shearing along axis
    :param node:
    :param symetryAxis:
    :param verbose:
    """
    validAxis = ['x', 'y', 'z']
    axisTolerance = mc.tolerance(q=True, linear=True)
    shearMatrix = om.MMatrix.kIdentity
    if mc.objExists(node) and mc.objectType(node, isAType='transform'):
        shear = list(mc.getAttr(node + '.shear')[0])
        if isinstance(symetryAxis, basestring) and (symetryAxis in validAxis):
            axis = readNodeAxis(node)
            upAxis = om.MVector(axis[0])
            frontAxis = om.MVector(axis[1])
            rightAxis = om.MVector(axis[2])
            if symetryAxis == 'x':
                if rightAxis.isEquivalent(om.MVector.kXaxisVector, axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[1] *= -1.0
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector, axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[2] *= -1.0
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector, axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector, axisTolerance):
                    shear[1] *= -1.0
                    shear[2] *= -1.0
            elif symetryAxis == 'y':
                if upAxis.isEquivalent(om.MVector.kXaxisVector, axisTolerance) or upAxis.isEquivalent(om.MVector.kXnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[1] *= -1.0
                elif upAxis.isEquivalent(om.MVector.kYaxisVector, axisTolerance) or upAxis.isEquivalent(om.MVector.kYnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[2] *= -1.0
                elif upAxis.isEquivalent(om.MVector.kZaxisVector, axisTolerance) or upAxis.isEquivalent(om.MVector.kZnegAxisVector, axisTolerance):
                    shear[1] *= -1.0
                    shear[2] *= -1.0
            elif symetryAxis == 'z':
                if frontAxis.isEquivalent(om.MVector.kXaxisVector, axisTolerance) or frontAxis.isEquivalent(om.MVector.kXnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[1] *= -1.0
                elif frontAxis.isEquivalent(om.MVector.kYaxisVector, axisTolerance) or frontAxis.isEquivalent(om.MVector.kYnegAxisVector, axisTolerance):
                    shear[0] *= -1.0
                    shear[2] *= -1.0
                elif frontAxis.isEquivalent(om.MVector.kZaxisVector, axisTolerance) or frontAxis.isEquivalent(om.MVector.kZnegAxisVector, axisTolerance):
                    shear[1] *= -1.0
                    shear[2] *= -1.0

        shearMatrix = om.MTransformationMatrix().setShear(shear, om.MSpace.kTransform).asMatrix()

    return shearMatrix


def rotateMatrixFromNodeAxis(node, symetryAxis=None, verbose=False):
    """Create a rotation Matrix from the node's axis
    :param node: The maya dagNode node
    :param symetryAxis: the MVector symetry axis
    :param verbose: boolean debug infos
    """
    currentSel = mc.ls(sl=True) or []
    validAxis = ['x', 'y', 'z']
    scale = [(-1, 1, 1), (1, -1, 1), (1, 1, -1)]
    upInverse = [1, -1, 1]
    frontInverse = [1, 1, -1]
    rotateMatrix = om.MMatrix.kIdentity
    if mc.objExists(node) and mc.objectType(node, isAType='transform'):
        dummy = mc.createNode('transform', name='dummy', parent=node)
        # cancel the scale and shear
        #
        mc.setAttr(dummy + '.translate', 0, 0, 0, type='double3')
        mc.setAttr(dummy + '.rotate', 0, 0, 0, type='double3')
        mc.setAttr(dummy + '.scale', 1, 1, 1, type='double3')
        mc.setAttr(dummy + '.shear', 0, 0, 0, type='double3')
        dummy = mc.parent(dummy, world=True)[0]
        mc.setAttr(dummy + '.scale', 1, 1, 1, type='double3')
        mc.setAttr(dummy + '.shear', 0, 0, 0, type='double3')

        axis = readNodeAxis(node)
        aimVector = axis[1]
        upVector = axis[0]
        if verbose:
            print ('aim vector:', aimVector)
            print ('up vector:', upVector)

        upGroup = mc.createNode('transform', name='upGroup', parent=dummy)
        mc.setAttr(upGroup + '.translate', upVector.x, upVector.y, upVector.z, type='double3')
        upGroup = mc.parent(upGroup, world=True)[0]
        frontGroup = mc.createNode('transform', name='frontGroup', parent=dummy)
        mc.setAttr(frontGroup + '.translate', aimVector.x, aimVector.y, aimVector.z, type='double3')
        frontGroup = mc.parent(frontGroup, world=True)[0]
        rotateGroup = mc.createNode('transform', name='rotateGroup')
        mc.setAttr(rotateGroup + '.rotateOrder', mc.getAttr(node + '.rotateOrder'))
        pntCnst = mc.pointConstraint(dummy, rotateGroup)[0]
        mc.delete(pntCnst)
        mc.delete(dummy)

        if isinstance(symetryAxis, basestring) and (symetryAxis in validAxis):

            aimVector *= frontInverse[validAxis.index(symetryAxis)]
            upVector *= upInverse[validAxis.index(symetryAxis)]
            if verbose:
                print ('aim vector (transformed):', aimVector)
                print ('up vector (transformed):', upVector)

            mainGroup = mc.createNode('transform', name='mainGroup')
            mc.parent([upGroup, frontGroup, rotateGroup], mainGroup)
            mc.setAttr(mainGroup + '.scale', scale[validAxis.index(symetryAxis)][0],
                       scale[validAxis.index(symetryAxis)][1],
                       scale[validAxis.index(symetryAxis)][2])
            mc.parent([upGroup, frontGroup, rotateGroup], world=True)
            mc.setAttr(upGroup + '.scale', 1, 1, 1, type='double3')
            mc.setAttr(frontGroup + '.scale', 1, 1, 1, type='double3')
            mc.setAttr(rotateGroup + '.scale', 1, 1, 1, type='double3')
            mc.delete(mainGroup)

        aimCnst = mc.aimConstraint(frontGroup, rotateGroup,
                                   aimVector=(aimVector.x, aimVector.y, aimVector.z),
                                   upVector=(upVector.x, upVector.y, upVector.z),
                                   worldUpType='object', worldUpObject=upGroup)[0]

        rotateMatrix = om.MTransformationMatrix(om.MMatrix(mc.getAttr(rotateGroup + '.worldMatrix'))).asRotateMatrix()
        if not verbose:
            mc.delete(aimCnst)
            mc.delete(upGroup, frontGroup, rotateGroup)

    if len(currentSel):
        mc.select(currentSel)

    return rotateMatrix


def determineNodeAxis(node, axisType='up', verbose=False):
    """Determine which axis of a joint is the most aligned with the sceneUp axis
    :param node: the node
    :param axisType: the type of axis to determine up, front or right
    :param verbose: debug infos
    """
    alignedAxis = None
    validAxis = ['up', 'front', 'right']
    if axisType not in validAxis:
        raise ValueError(
            '[determineNodeAxis] Invalid axis type {0} supplied'.format(axisType))

    if mc.objExists(node):
        if axisType == 'front':
            rightAxis = determineNodeAxis(
                node, axisType='right', verbose=False)
            upAxis = determineNodeAxis(node, axisType='up', verbose=False)
            frontAxis = (rightAxis ^ upAxis).normalize()
            return frontAxis

        sceneUp = mc.upAxis(query=True, ax=True)
        up = om.MVector.kZeroVector
        front = om.MVector.kZeroVector
        right = om.MVector.kZeroVector
        if sceneUp == 'y':
            up = om.MVector.kYaxisVector
            front = om.MVector.kZaxisVector
            right = om.MVector.kXaxisVector
        elif sceneUp == 'z':
            up = om.MVector.kZaxisVector
            front = om.MVector.kYnegAxisVector
            right = om.MVector.kXaxisVector
        else:
            raise RuntimeError(
                '[determineNodeUpAxis] Unexpected upAxis value: {0}'.format(sceneUp))

        axisToCheck = om.MVector.kZeroVector
        if axisType == 'up':
            axisToCheck = up
        elif axisType == 'front':
            axisToCheck = front
        elif axisType == 'right':
            axisToCheck = right
        else:
            raise ValueError(
                '[determineNodeAxis] Invalid axis type {0} supplied'.format(axisType))

        jointWorldMatrix = om.MMatrix(mc.getAttr(node + '.worldMatrix'))
        jointRotateMatrix = om.MTransformationMatrix(
            jointWorldMatrix).asRotateMatrix()

        xAxis = om.MVector.kXaxisVector
        yAxis = om.MVector.kYaxisVector
        zAxis = om.MVector.kZaxisVector

        xAxis = (xAxis * jointRotateMatrix).normalize()
        yAxis = (yAxis * jointRotateMatrix).normalize()
        zAxis = (zAxis * jointRotateMatrix).normalize()

        allAxis = [om.MVector.kXaxisVector,
                   om.MVector.kYaxisVector,
                   om.MVector.kZaxisVector]
        allNegAxis = [om.MVector.kXnegAxisVector,
                      om.MVector.kYnegAxisVector,
                      om.MVector.kZnegAxisVector]
        allTransformedAxis = [xAxis, yAxis, zAxis]
        transformAxis = None
        dot = .0
        for axis in allTransformedAxis:
            curDot = round(axis * axisToCheck, 6)
            if fabs(curDot) > dot:
                alignedAxis = allAxis[allTransformedAxis.index(axis)]
                transformAxis = axis
                dot = fabs(curDot)

        if (transformAxis * axisToCheck) < .0:
            alignedAxis = allNegAxis[allAxis.index(alignedAxis)]

        return alignedAxis


def writeNodeAxis(node, verbose=False):
    """
    :param node: the to write the axis on
    :param verbose: debug info
    """
    axis = []
    if mc.objExists(node) and mc.objectType(node, isAType='transform'):

        rightAxis = determineNodeAxis(node, axisType='right', verbose=verbose)
        upAxis = determineNodeAxis(node, axisType='up', verbose=verbose)
        frontAxis = (rightAxis ^ upAxis).normalize()

        try:
            if not mc.attributeQuery('upAxis', node=node, exists=True):
                mc.addAttr(node, ln='upAxis', at='double3')
                mc.addAttr(node, ln='upAxisX', at='double', p='upAxis')
                mc.addAttr(node, ln='upAxisY', at='double', p='upAxis')
                mc.addAttr(node, ln='upAxisZ', at='double', p='upAxis')
            mc.setAttr(('%s.upAxis' % node), upAxis.x,
                       upAxis.y, upAxis.z, type='double3')
        except Exception:
            return None
        else:
            axis.append(upAxis)

        try:
            if not mc.attributeQuery('frontAxis', node=node, exists=True):
                mc.addAttr(node, ln='frontAxis', at='double3')
                mc.addAttr(node, ln='frontAxisX', at='double', p='frontAxis')
                mc.addAttr(node, ln='frontAxisY', at='double', p='frontAxis')
                mc.addAttr(node, ln='frontAxisZ', at='double', p='frontAxis')
            mc.setAttr(('%s.frontAxis' % node), frontAxis.x,
                       frontAxis.y, frontAxis.z, type='double3')
        except Exception:
            return None
        else:
            axis.append(frontAxis)

        try:
            if not mc.attributeQuery('rightAxis', node=node, exists=True):
                mc.addAttr(node, ln='rightAxis', at='double3')
                mc.addAttr(node, ln='rightAxisX', at='double', p='rightAxis')
                mc.addAttr(node, ln='rightAxisY', at='double', p='rightAxis')
                mc.addAttr(node, ln='rightAxisZ', at='double', p='rightAxis')
            mc.setAttr(('%s.rightAxis' % node), rightAxis.x,
                       rightAxis.y, rightAxis.z, type='double3')
        except Exception:
            return None
        else:
            axis.append(rightAxis)

    return axis


def readNodeAxis(node):
    """Cette procedure lit et retourne les vecteurs upAxis et frontAxis et rightAxis d'un node
    :param node unicode: le node a interroger
    :rtyp MVector: the axis
    """
    axis = []

    if not mc.objExists(node):
        return None

    upAxis = om.MVector.kZeroVector
    frontAxis = om.MVector.kZeroVector
    rightAxis = om.MVector.kZeroVector

    if mc.attributeQuery('upAxis', n=node, exists=True):
        upAxis = om.MVector(mc.getAttr(node + '.upAxis')[0])
    else:
        writeNodeAxis(node, verbose=False)
        upAxis = om.MVector(mc.getAttr(node + '.upAxis')[0])

    if mc.attributeQuery('frontAxis', n=node, exists=True):
        frontAxis = om.MVector(mc.getAttr(node + '.frontAxis')[0])
    else:
        writeNodeAxis(node, verbose=False)
        frontAxis = om.MVector(mc.getAttr(node + '.frontAxis')[0])

    if mc.attributeQuery('rightAxis', n=node, exists=True):
        rightAxis = om.MVector(mc.getAttr(node + '.rightAxis')[0])
    else:
        writeNodeAxis(node, verbose=False)
        rightAxis = om.MVector(mc.getAttr(node + '.rightAxis')[0])

    axis.extend([upAxis, frontAxis, rightAxis])

    return axis


def copyNodeAxis(source, dest):
    """
    Copy the up, right and front axis vectors from source toward destination
    :param source: The source node
    :param dest: the destination node
    """
    if mc.objExists(dest):
        destAxis = writeNodeAxis(dest, verbose=False)
        sourceAxis = None
        if all([mc.attributeQuery('upAxis', n=source, exists=True),
                mc.attributeQuery('frontAxis', n=source, exists=True),
                mc.attributeQuery('rightAxis', n=source, exists=True)]):
            upAxis = om.MVector(mc.getAttr(source + '.upAxis')[0])
            frontAxis = om.MVector(mc.getAttr(source + '.frontAxis')[0])
            rightAxis = om.MVector(mc.getAttr(source + '.rightAxis')[0])
            sourceAxis = [upAxis, frontAxis, rightAxis]

        if sourceAxis:
            mc.setAttr(dest + '.upAxis', sourceAxis[0].x, sourceAxis[0].y, sourceAxis[0].z, type='double3')
            mc.setAttr(dest + '.frontAxis', sourceAxis[1].x, sourceAxis[1].y, sourceAxis[1].z, type='double3')
            mc.setAttr(dest + '.rightAxis', sourceAxis[2].x, sourceAxis[2].y, sourceAxis[2].z, type='double3')
            return sourceAxis

        return destAxis

    return None


def insertMultDoubleLinear(inPlugOrValue1, inPlugOrValue2, outPlug, side=None, name='multDoubleLinear#'):
    """Insert a multDoubleLinear nor in the dependencygraph
    :param unicode inPlugOrValue1: the connection or the float value to input1
    :param unicode inPlugOrValue2: the connection or the float value to input2
    :param unicode outPlug: where the output is connected
    :param side: int 0 or 1 where the connection to outPlug is redirect
    :param unicode name: the name of the new node
    :return: the new node
    :rtyp: unicode
    :raises: ValueError Invalid output plug
    :raises: RuntimeError Destination plug is locked in a referenced file
    :raises: ValueError Invalid parameter side
    """
    multDoubleLinear = ''

    if not isValidObjectName(name):
        name = 'multDoubleLinear#'

    if outPlug != '':
        if not checkPlug(outPlug):
            raise ValueError(
                '[insertMultDoubleLinear] Invalid output plug '.format(outPlug))

        node = nodeFromPlug(outPlug)
        locked = False
        if mc.getAttr(outPlug, lock=True):
            if not mc.referenceQuery(node, isNodeReferenced=True) and not mc.lockNode(node, query=True)[0]:
                mc.setAttr(outPlug, lock=False)
                locked = True
            else:
                raise RuntimeError(
                    '[insertMultDoubleLinear] Destination plug {0} is locked in a referenced file'.format(outPlug))

        inCx = mc.connectionInfo(outPlug, sfd=True)
        if mc.objExists(inCx):
            try:
                if mc.nodeType(inCx) == 'unitConversion':
                    unitConversion = nodeFromPlug(inCx)
                    inCx = mc.connectionInfo(
                        '{0}.input'.format(unitConversion), sfd=True)
                    mc.disconnectAttr(
                        inCx, '{0}.input'.format(unitConversion))
                    mc.disconnectAttr(
                        '{0}.output'.format(unitConversion), outPlug)
                    if not mc.referenceQuery(unitConversion, isNodeReferenced=True) and not mc.lockNode(unitConversion, query=True)[0]:
                        mc.delete(unitConversion)
                    else:
                        mc.warning('[insertMultDoubleLinear] Unable to delete node {0} from a referenced file'.format(
                            unitConversion))
                else:
                    mc.disconnectAttr(inCx, outPlug)
            except Exception:
                raise

            if side is not None:
                if side == 0:
                    inPlugOrValue1 = inCx
                elif side == 1:
                    inPlugOrValue2 = inCx
                else:
                    raise ValueError(
                        '[insertMultDoubleLinear] Invalid parameter side '.format(side))

        multDoubleLinear = mc.createNode(
            'multDoubleLinear', ss=True, name=name)
        if isinstance(inPlugOrValue1, float):
            mc.setAttr('{0}.input1'.format(multDoubleLinear), inPlugOrValue1)
        else:
            if checkPlug(inPlugOrValue1):
                mc.connectAttr(
                    inPlugOrValue1, '{0}.input1'.format(multDoubleLinear))

        if isinstance(inPlugOrValue2, float):
            mc.setAttr('{0}.input2'.format(multDoubleLinear), inPlugOrValue2)
        else:
            if checkPlug(inPlugOrValue2):
                mc.connectAttr(
                    inPlugOrValue2, '{0}.input2'.format(multDoubleLinear))

        try:
            mc.connectAttr('{0}.output'.format(multDoubleLinear), outPlug)
            mc.setAttr(outPlug, lock=locked)
        except Exception:
            raise

    return multDoubleLinear


def getFirstShape(node):
    '''
    '''
    shape = ''

    if not mc.objExists(node):
        raise ValueError('[getFirstShape] Supplied node {0} does not exist'.format(node))

    shapes = mc.listRelatives(node, ni=True, s=True, pa=True)
    if shapes:
        shape = shapes[0]
    else:
        shape = node

    return shape


def getFirstTransform(node):
    '''
    '''
    transform = ''
    if not mc.objExists(node):
        raise ValueError('[getFirstTransform] Supplied node {0} does not exist'.format(node))

    shape = getFirstShape(node)
    if mc.objExists(shape):
        parents = mc.listRelatives(shape, p=True, pa=True) or []
        if len(parents):
            transform = parents[0]

    return transform


def getFirstTransformMatch(fromObject, pattern, nodeType='transform', relatives='parent'):
    '''
    '''
    matched = None
    if mc.objExists(fromObject):
        nodes = []
        if relatives == 'children':
            nodes = mc.listRelatives(fromObject, pa=True, children=True)
        elif relatives == 'parent':
            nodes = mc.listRelatives(fromObject, pa=True, parent=True)

        if not nodes:
            # print('No children under %s' %root)
            return matched
        else:
            for node in nodes:
                shortName = node.split('|')[-1].split(':')[-1]
                if fnmatch.fnmatch(shortName, pattern) and mc.nodeType(node) == nodeType:
                    matched = node
                    break
                else:
                    result = getFirstTransformMatch(
                        node, pattern, nodeType, relatives)
                    if result:
                        matched = result
                        break
    return matched


def cleanShapeOrig(transform, fix=False):
    '''
    Delete all the shapeOrig under a maya transform
    '''
    shapeBuffer = []
    shapeBufferNi = []

    inShapesCx = []
    outShapesCx = []

    badShapes = []

    shapeBuffer.extend(mc.listRelatives(transform, f=True, shapes=True) or [])
    shapeBufferNi.extend(mc.listRelatives(transform, ni=True, f=True, shapes=True) or [])

    shapeBuffer = [x for x in shapeBuffer if x not in shapeBufferNi]

    for shape in shapeBuffer:
        # What is a shapeOrig
        # Rules: 1 - no input no output and flag intermediateObject
        #        2 - one input no output and flag intermediateObject
        #        3 - no input one output to another shapeOrig (intermediateObject)
        #        4 - one shapeOrig input one shapeOrig output
        # all case are not yet supported here
        #
        incx = mc.listConnections(shape, sh=True, s=True, d=False, scn=True)
        outcx = mc.listConnections(shape, sh=True, s=False, d=True, scn=True)

        szin = 0
        szout = 0

        if incx:
            szin = len(incx)
        if outcx:
            szout = len(outcx)

        if szin + szout:
            if szin:
                continue

            del inShapesCx[:]
            del outShapesCx[:]

            if szout:
                outShapesCx = mc.ls(outcx, s=True)
                if len(outShapesCx) == szout:
                    badShapes.append(shape)
                    if fix:
                        mc.delete(shape)
        else:
            badShapes.append(shape)
            if fix:
                mc.delete(shape)

    return badShapes


def getTypedConnectedLoop(nodeType, nodeOrPlug, returnPlug, source, destination, depth, stopFirst, pruneType, visitedPlugs, plugLevel, verbose):
    '''
    The main graph search loop
    '''
    result = []
    conPlugs = []
    tempPlugs = mc.listConnections(nodeOrPlug, connections=True, plugs=True, source=source, destination=destination, shapes=True) or []

    size = len(tempPlugs)
    curNode = nodeFromPlug(nodeOrPlug)

    if verbose:
        print('- For {} -'.format(nodeOrPlug))
        print('------------------------------')
        for i in xrange(0, size, 2):
            sourcePlug = ''
            destPlug = ''
            knowSide = False
            if source and destination:
                # Impossible to know order
                #
                sourcePlug = tempPlugs[i]
                destPlug = tempPlugs[i + 1]
                knowSide = False
            elif source:
                sourcePlug = tempPlugs[i + 1]
                destPlug = tempPlugs[i]
                knowSide = True
            elif destination:
                sourcePlug = tempPlugs[i]
                destPlug = tempPlugs[i + 1]
                knowSide = True

            if sourcePlug != '' and destPlug != '':
                if knowSide:
                    print('{0} --> {1}'.format(sourcePlug, destPlug))
                else:
                    print('{0} <-> {1}'.format(sourcePlug, destPlug))
        print('------------------------------')

    # Immediatly cut the visited plugs
    #
    for i in xrange(0, size, 2):
        curNodeOrPlug = tempPlugs[i]
        if not plugLevel:
            curNodeOrPlug = nodeFromPlug(curNodeOrPlug)
        if curNodeOrPlug not in visitedPlugs:
            conPlugs.append(tempPlugs[i + 1])

    for i in xrange(0, size, 2):
        curNodeOrPlug = tempPlugs[i]
        if not plugLevel:
            curNodeOrPlug = nodeFromPlug(curNodeOrPlug)
        if curNodeOrPlug not in visitedPlugs:
            visitedPlugs.append(curNodeOrPlug)

    plugsSize = len(conPlugs)
    if verbose:
        print('- Filtered connections -')
        for conPlug in conPlugs:
            print(conPlug)
        print('------------------------')

    for i in range(plugsSize):
        found = False
        keepSearching = False
        alreadyVisited = False
        doPrune = False

        curPlug = conPlugs[i]
        curNode = nodeFromPlug(curPlug)

        if plugLevel:
            alreadyVisited = (curPlug in visitedPlugs)
        else:
            alreadyVisited = (curNode in visitedPlugs)

        if not alreadyVisited:
            if mc.objectType(curNode, isAType=nodeType):
                if returnPlug:
                    if curPlug not in result:
                        result.append(curPlug)
                else:
                    if curNode not in result:
                        result.append(curNode)

                found = True

        if pruneType != '':
            pruneList = pruneType.split()
            if len(pruneList):
                for pType in pruneList:
                    if mc.objectType(curNode, isAType=pType):
                        doPrune = True
                        break
        if verbose:
            print('\tConnected Node: {0}, already visited: {1}, prune: {2}, found: {3}'.format(curNode, alreadyVisited, doPrune, found))

        keepSearching = (not(stopFirst and found) and not doPrune and not alreadyVisited)

        if depth != 0 and keepSearching:
            depth -= 1
            nextResult = getTypedConnectedLoop(nodeType, curNode, returnPlug, source, destination, depth, stopFirst, pruneType, visitedPlugs, plugLevel, verbose)
            result.extend(nextResult)
        else:
            if verbose:
                message = ('Search stop on {0}, at depth {1}'.format(curPlug, depth))
                if alreadyVisited:
                    message += (': already visited')
                elif found:
                    message += (': found')
                elif doPrune:
                    message += (': prune type {0}'.format(pruneType))

                print(message)

    return result


def getFirstTypedConnected(nodeType, nodeOrPlug, returnPlug=False, source=True, destination=False, depth=-1, verbose=False):
    '''
    Search the first node of type nodeType connected upstream or downstrean the node or the plug nodeOrPlug
    '''
    found = ''
    visitedPlugs = []
    stopFirst = True
    pruneType = ''
    plugLevel = returnPlug

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    mc.progressBar(gMainProgressBar,
                   edit=True,
                   beginProgress=True,
                   isInterruptable=True,
                   status='Exploring DG network...',
                   maxValue=100)

    result = getTypedConnectedLoop(nodeType, nodeOrPlug, returnPlug, source,
                                   destination, depth, stopFirst, pruneType, visitedPlugs, plugLevel, verbose)

    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

    if len(result):
        found = result[0]

    return found


def getPrunedTypedConnected(nodeType, nodeOrPlug, returnPlug=False, source=True, destination=False, pruneType='dagNode', depth=-1, verbose=False):
    '''
    Return the first node of type nodeType and prune the search on nodes of type pruneType
    '''
    found = []
    visitedPlugs = []
    stopFirst = False

    # print ("Search start on "+nodeOrPlug+"\n");
    # Pour l'instant, si aucun plug en retour n'est demandé on considère qu'on peut travailler au "node level"

    plugLevel = returnPlug

    result = getTypedConnectedLoop(nodeType, nodeOrPlug, returnPlug, source, destination,
                                   depth, stopFirst, pruneType, visitedPlugs, plugLevel, verbose=verbose)
    if len(result):
        found = list(set(result))

    return found


def getGraphBetween(upStreamNode, upStreamAttr, downStreamNode, downStreamAttr, verbose=False):
    """Get the dependency graph between two plugs
    :param unicode upStreamNode: The node up stream
    :param unicode upStreamAttr: The attr up stream
    :param unicode upStreamNode: The node down stream
    :param unicode upStreamAttr: The attr down stream
    """
    downStreamPlug = downStreamNode + '.' + downStreamAttr
    upStreamNodesVisited = getUpStreamNodes(downStreamPlug, doNotTraverseNodes=(
        'dagNode',), exactType=False, plugLevel=True, traverseIntermediate=True, verbose=verbose)

    # following code to replace when getDownStreamNodes will be implemented
    #
    upStreamPlug = getMPlug(upStreamNode, upStreamAttr)
    dgIt = openMaya.MItDependencyGraph(upStreamPlug, openMaya.MFn.kInvalid, openMaya.MItDependencyGraph.kDownstream,
                                       openMaya.MItDependencyGraph.kDepthFirst, openMaya.MItDependencyGraph.kPlugLevel)
    depFn = openMaya.MFnDependencyNode()
    nodesVisited = []
    while not dgIt.isDone():
        thisPlug = dgIt.thisPlug()
        if not thisPlug.isNull():
            if verbose:
                print ('Iterating on:', thisPlug.info())
            oNode = thisPlug.node()
            depFn.setObject(oNode)
            nodeName = depFn.name()
            if nodeName in upStreamNodesVisited:
                nodesVisited.append(nodeName)
        dgIt.next()


def getHierarchyRoot(node, nodeType, traverse):
    '''
    '''
    objType = nodeType
    default = mc.nodeType(node)

    if nodeType == '':
        objType = default
    elif nodeType == "all":
        objType = 'dagNode'

    root = node
    parents = mc.listRelatives(node, parent=True, pa=True) or []
    while len(parents):
        parent = parents[0]

        if mc.objectType(parent, isAType=objType):
            root = parent
        elif traverse is False:
            break

        parents = mc.listRelatives(parent, parent=True, pa=True) or []

    return root


def getHierarchyNodeDepth(node, typ, traverse=True):
    '''
    '''
    depth = 0
    nodeType = typ
    default = mc.nodeType(node)

    if typ == '':
        nodeType = default
    elif typ == 'all':
        nodeType = 'dagNode'

    parents = mc.listRelatives(node, p=True, pa=True)
    while parents and len(parents):
        parent = parents[0]
        if mc.objectType(parent, isAType=nodeType):
            depth += 1
        elif traverse is False:
            break

        parents = mc.listRelatives(parent, p=True, pa=True)

    return depth


def sortByHierarchyDepth(nodeList, typ, traverse=True):
    '''
    '''
    sortedNodes = []
    if isinstance(nodeList, list) and len(nodeList) > 0:
        rootList = []
        depthList = []
        for node in nodeList:
            root = getHierarchyRoot(node, typ, traverse)
            if root not in rootList:
                rootList.append(root)

        if len(rootList) > 1:
            raise RuntimeError('All nodes should be in the same hierarchy to be depth sorted')
        for i in range(len(nodeList)):
            depthList.append(getHierarchyNodeDepth(nodeList[i], typ, traverse))

        sortedNodes = sortIntWeightedArray(nodeList, depthList)

    return sortedNodes


def isParentOf(dagNode, otherDagNode):
    '''
    Check if a node is the parent of a dagNode
    '''
    isParentOf = False
    if not all([mc.objExists(dagNode), isDagNode(dagNode),
                mc.objExists(otherDagNode), isDagNode(otherDagNode)]):
        return isParentOf

    parents = mc.listRelatives(otherDagNode, p=True, pa=True) or []
    if parents:
        for parent in parents:
            if dagNode in parent:
                isParentOf = True

    return isParentOf


def isDagNode(node):
    '''
    '''
    isDagNode = False
    if not mc.objExists(node):
        return isDagNode

    isDagNode = mc.objectType(node, isAType='dagNode')
    return isDagNode


def isMemberOfASet(theNode):
    """Check if an object is member of a set
    :param theNode Maya object
    :rtype: boolean
    """
    isMemberOfASet = False
    objectSets = mc.listSets(o=theNode) or []
    if objectSets:
        isMemberOfASet = True

    return isMemberOfASet


def removeFromSets(theNode, objectSets=None):
    '''
    Remove a sets from all the sets it belong to
    '''
    if mc.objExists(theNode):
        if not objectSets or not isinstance(objectSets, (list, tuple)):
            objectSets = mc.listSets(o=theNode) or []

        for objectSet in objectSets:
            if mc.objExists(objectSet):
                if mc.sets(theNode, isMember=objectSet):
                    mc.sets(theNode, remove=objectSet)


def addToSets(theNode, theSets, exclusive=True):
    '''
    Add a node to an objectSet
    '''
    if mc.objExists(theNode) and (mc.objExists(theSets) and mc.objectType(theSets, isAType='objectSet')):
        if exclusive:
            removeFromSets(theNode)

        mc.sets(theNode, addElement=theSets)


def isMemberOfSets(theNode, theSets=()):
    """Check if an object is member of a given set
    :param str theNode: Maya object
    :param tuple theSets: Maya objectSets
    :rtype: boolean
    """
    isMemberOf = True
    for objectSet in theSets:
        isMemberOf *= mc.sets(theNode, isMember=objectSet)

    return isMemberOf


def listSets(theNode):
    """List all the sets which theNode is member
    :param str theNode: Maya object
    :return: [objectSet...]
    :rtype: list
    """
    objectSets = []
    if mc.objExists(theNode):
        objectSets = mc.listSets(o=theNode) or []

    return objectSets


def listMembersOfSet(theSet, typ=None):
    """List the members of a Maya objectSet theSet
    :param str theSet: Maya objectSet
    :param str or None typ: the type of the members to filter on
    :return: [objectSet...]
    :rtype: list
    :raises: ValueError if invalid maya type supplied
    :raises: ValueError if invalid type has been supplied for node theSet
    :raises: ValueError if the supplied node theSet does not exist
    """
    members = []
    if mc.objExists(theSet):
        if mc.objectType(theSet, isAType='objectSet'):
            members = mc.sets(theSet, query=True) or []
            if typ is not None and typ in getAllNodeTypes(includeAbstract=True):
                members = mc.ls(members, type=typ) or []
            else:
                raise ValueError('[listMembersOfSet] Invalid type {0} supplied'.format(typ))
        else:
            raise ValueError('[listMembersOfSet] Invalid type "{0}" supplied for node {1}'.format((mc.nodeType(theSet)), theSet))
    else:
        raise ValueError('[listMembersOfSet] The node "{0}" supplied does not exist'.format(theSet))

    return members


def getAllNodeTypes(includeAbstract=False):
    """
    Return all the existing node types
    :param includeAbstract: does the abstract class are return too
    :rtyp: list of unicode
    """
    if not includeAbstract:
        return mc.allNodeTypes(includeAbstract=False)
    else:
        allNodeTypes = mc.allNodeTypes(includeAbstract=True)
        return [t.split()[0] for t in allNodeTypes]


def listAffectedNodes(node, affected=True, verbose=False):
    """List the node downStream affected by the connections from node
    :param Maya Node: the upstreamNode
    :param boolean affected: by default return the affected nodes, if false, the non affected connected nodes will be returned
    :param boolean verbose: Print debub informations
    :return: the affected/unaffected nodes based on flag affected
    :rtype: list
    """
    affectedNodes = []
    unaffectedNodes = []
    if mc.objExists(node):
        plugs = mc.listConnections(node, source=False, destination=True, plugs=True) or []
        if plugs:
            for plug in plugs:
                node = nodeFromPlug(plug)
                nodeType = mc.nodeType(node)
                attribute = attributeLeaf(baseAttributePath(attributeFromPlug(plug)))
                if not isDynamicAttribute(node, attribute):
                    if verbose:
                        print ('Node: ', node, '(', nodeType,
                               '), attribute ->', attribute)
                    affectedAttributes = mc.affects(attribute, type=nodeType, by=True) or []
                    if verbose:
                        print ('\tAffected: ', affectedAttributes)
                    if len(affectedAttributes):
                        affectedNodes.append(node)
                    else:
                        unaffectedNodes.append(node)
    if affected:
        return affectedNodes
    else:
        return unaffectedNodes


def getUpStreamNodes(fromNodeOrPlug, doNotTraverseNodes, exactType=False, plugLevel=False, traverseIntermediate=True, verbose=False):
    """Method to retreive all the nodes that affect a downStream node
    :param: Maya node fromNode
    :param: list of Maya type where the search stops
    :param: boolean exactType if the test on doNotTraverseNodes is base on the exact type or on the derivated types too
    :param: boolean verbose, print debug informations
    :rtyp: list of nodes
    """
    oRoot = openMaya.MObject.kNullObj
    level = openMaya.MItDependencyGraph.kNodeLevel
    node = ''
    if plugLevel:
        if not checkPlug(fromNodeOrPlug):
            raise RuntimeError(
                '[getUpStreamNodes] Invalid plug supplied {0}'.format(fromNodeOrPlug))
        else:
            node = nodeFromPlug(fromNodeOrPlug)
            attr = attributeFromPlug(fromNodeOrPlug)
            oRoot = getMPlug(node, attr)
            level = openMaya.MItDependencyGraph.kPlugLevel
    else:
        if mc.objExists(fromNodeOrPlug):
            node = nodeFromPlug(fromNodeOrPlug)
            oRoot = getMObject(node)

    dgIt = openMaya.MItDependencyGraph(
        oRoot, openMaya.MFn.kInvalid, openMaya.MItDependencyGraph.kUpstream, openMaya.MItDependencyGraph.kDepthFirst, level)
    nodesVisited = []
    toDelete = [node]
    toKeep = []
    toSkip = []
    count = 0
    depFn = openMaya.MFnDependencyNode()
    while not dgIt.isDone():
        oNode = openMaya.MObject.kNullObj
        if not plugLevel:
            thisPlug = dgIt.thisPlug()
            oNode = thisPlug.node()
            depFn.setObject(oNode)
        else:
            oNode = dgIt.currentItem()
            depFn.setObject(oNode)
        nodeName = depFn.name()

        if verbose:
            print ('Iterating on:', nodeName)
        if nodeName == node:
            toSkip.append(nodeName)
        if nodeName in toSkip:
            if verbose:
                print ('\tNode is skipped:', nodeName)
            dgIt.next()
            continue
        stopHere = False
        if isinstance(doNotTraverseNodes, (tuple, list)):
            for doNotTraverseNode in doNotTraverseNodes:
                if not exactType:
                    # One of the type to preserve in the graph
                    if mc.objectType(nodeName, isAType=doNotTraverseNode):
                        stopHere = True
                        break
                else:
                    # One of the type to preserve in the graph
                    if mc.objectType(nodeName, isType=doNotTraverseNode):
                        stopHere = True
                        break

        if mc.objectType(nodeName, isAType='shape'):
            io = mc.getAttr('{0}.intermediateObject'.format(nodeName))
            if io and traverseIntermediate:
                stopHere = False
            elif io and not traverseIntermediate:
                stopHere = True

        if not stopHere:
            if verbose:
                print ('\tNode: ', nodeName, ' visited')
            nodesVisited.append(nodeName)
        else:
            if verbose:
                print ('\tNode: ', nodeName,
                       ' is not traversed, upstream nodes will be skipped')
            upstreamDgIt = openMaya.MItDependencyGraph(oNode, openMaya.MFn.kInvalid, openMaya.MItDependencyGraph.kUpstream,
                                                       openMaya.MItDependencyGraph.kDepthFirst, openMaya.MItDependencyGraph.kNodeLevel)
            while not upstreamDgIt.isDone():
                item = upstreamDgIt.currentItem()
                if not item.isNull():
                    depFn.setObject(item)
                    itemName = depFn.name()
                    toSkip.append(itemName)
                upstreamDgIt.next()
        count += 1
        dgIt.next()

    for i, nodeVisited in enumerate(nodesVisited):  # @UnusedVariable
        if verbose:
            print ('Node visited: ', nodeVisited,
                   ' -> ', mc.nodeType(nodeVisited))
        outCx = mc.listConnections(nodeVisited, source=False,
                                   destination=True, plugs=True) or []
        if not len(outCx):
            if verbose:
                print ('\tTo Delete: ', nodeVisited)
            toDelete.append(nodeVisited)
        elif len(outCx) == 1 and (nodeFromPlug(outCx[0]) in toDelete):
            if verbose:
                print ('\tTo Delete: ', nodeVisited)
            toDelete.append(nodeVisited)
        else:
            unknownOut = ''
            for cx in outCx:
                downStreamNode = nodeFromPlug(cx)
                attribute = attributeFromPlug(cx)  # @UnusedVariable
                nodeType = mc.nodeType(downStreamNode)
                if downStreamNode in listAffectedNodes(nodeVisited, affected=False, verbose=False):
                    if verbose:
                        print ('\tIgnoring: ', cx, ' -> unaffected...')
                    continue
                if verbose:
                    print ('\tTesting: ', cx, ' -> ', nodeType,)
                if (downStreamNode not in toDelete and downStreamNode not in nodesVisited) or (downStreamNode in toKeep):
                    unknownOut = downStreamNode
                    if verbose:
                        print (' Invalid')
                    break
                else:
                    if verbose:
                        print (' Valid')

            if unknownOut:
                if verbose:
                    print('\tConnected to a node outside the graph or to a node that must be kept: ',
                          unknownOut, ' -> ', mc.nodeType(unknownOut))
                toKeep.append(nodeVisited)
            else:
                if verbose:
                    print ('\tTo Delete: ', nodeVisited)
                toDelete.append(nodeVisited)

    if len(toDelete):
        toDelete = toDelete[1:]  # Remove the root node

    return toDelete


def getFirstParentOfTypeLoop(dagNode, nodeType, traverse, noTest):
    '''
    Main loop recurcive function of getFirstParentOfType
    '''
    result = []

    parents = mc.listRelatives(dagNode, p=True, pa=True) or []

    for i in xrange(len(parents)):
        father = parents[i]
        if noTest or mc.objectType(father, isType=nodeType):
            result.append(father)
        elif traverse:
            result.append(getFirstParentOfTypeLoop(father, nodeType, traverse, noTest))

    if len(result):
        return result[0]
    else:
        return ''


def getFirstParentOfType(dagNode, typ='', traverse=True):
    '''
    Get the first parent of the supplied type, the search can traverse dag of different type if traverse is True
    '''
    if mc.objExists(dagNode):
        default = mc.nodeType(dagNode)
        nodeType = typ
        if typ == '':
            nodeType = default
        elif typ == 'all':
            nodeType = 'dagNode'
        noTest = (nodeType == 'dagNode')
        result = getFirstParentOfTypeLoop(dagNode, nodeType, traverse, noTest)
    else:
        raise RuntimeError('[getFirstParentOfType] {0} does not exist or is not a dag node'.format(dagNode))

    return result


def getTransformationsInSpace(transform, otherTransform, space='local'):
    """Retreive the transformations from transform to otherTransform
    :param Maya transform transform: source transform
    :param Maya transform otherTransform: destination transform
    :return: xform matrix
    """
    position = []
    rotation = []
    scale = []
    shear = []
    validSpaces = ['local', 'object', 'world']
    if space not in validSpaces:
        raise ValueError(
            '[getTransformationsInSpace] Invalid space "{0}" supplied'.format(space))

    selection = mc.ls(sl=True) or []
    if mc.objExists(transform) and mc.objectType(transform, isAType='transform'):
        dummy = mc.createNode('transform', ss=True)
        # modification 18/09/2015, dummy must have the same rotateOrder as the source transform
        rotateOrder = mc.getAttr('{0}.rotateOrder'.format(transform))
        mc.setAttr('{0}.rotateOrder'.format(dummy), rotateOrder)
        dummy = mc.parent(dummy, transform, relative=True)[0]

        if space == 'local':
            parent = getFirstParentOfType(otherTransform, typ='all',
                                          traverse=True)
            if mc.objExists(parent):
                dummy = mc.parent(dummy, parent, absolute=True)[0]
            else:
                dummy = mc.parent(world=True, absolute=True)[0]
        elif space == 'object':
            dummy = mc.parent(dummy, otherTransform, absolute=True)[0]
        elif space == 'world':
            dummy = mc.parent(world=True, absolute=True)[0]

        position = mc.getAttr('{0}.translate'.format(dummy))[0]
        rotation = mc.getAttr('{0}.rotate'.format(dummy))[0]
        scale = mc.getAttr('{0}.scale'.format(dummy))[0]
        shear = mc.getAttr('{0}.shear'.format(dummy))[0]

        mc.delete(dummy)
    else:
        return None

    if selection:
        mc.select(selection)
    return (position, rotation, scale, shear)


def getTransformations(transform, space='local', verbose=False):
    """Retreive the transformations from transform to otherTransform
    :param Maya transform: source transform
    :param str space: space to compute the transformation, can be local, object
    :return: xform matrix
    """
    translate = []
    rotate = []
    scale = []
    shear = []
    validSpaces = ['local', 'world']
    if space not in validSpaces:
        raise ValueError(
            '[getTransformations] Invalid space "{0}" supplied'.format(space))
    selection = mc.ls(sl=True) or []
    if mc.objExists(transform) and mc.objectType(transform, isAType='transform'):
        dummy = mc.createNode('transform', ss=True)
        rotateOrder = mc.getAttr('{0}.rotateOrder'.format(transform))
        mc.setAttr('{0}.rotateOrder'.format(dummy), rotateOrder)
        dummy = mc.parent(dummy, transform, relative=True)[0]
        if space == 'local':
            parent = getFirstParentOfType(transform, typ='all', traverse=True)
            if mc.objExists(parent):
                dummy = mc.parent(dummy, parent, absolute=True)[0]
            else:
                dummy = mc.parent(world=True, absolute=True)[0]
        elif space == 'world':
            dummy = mc.parent(world=True, absolute=True)[0]
        else:
            mc.delete(dummy)
            raise ValueError(
                '[getTransformations] Invalid space supplied {0}'.format(space))

        translate = mc.getAttr('{0}.translate'.format(dummy))[0]
        rotate = mc.getAttr('{0}.rotate'.format(dummy))[0]
        scale = mc.getAttr('{0}.scale'.format(dummy))[0]
        shear = mc.getAttr('{0}.shear'.format(dummy))[0]
        if verbose:
            print 'node:', transform
            print 'Translate in World space:', translate
            print 'rotate in World space:', rotate
            print 'scale in World space:', scale
            print 'shear in World space:', shear

        if not verbose:
            mc.delete(dummy)
    else:
        return None

    if selection:
        mc.select(selection)
    return (translate, rotate, scale, shear)

# # ------------------------------------ DECORATORS ------------------------------------ # #


def undoable(function):
    """A decorator that will make commands undoable in maya
    :param function: the function to decorate
    :return The decorated code
    :rtype: function
    """
    def decoratorCode(*args, **kwargs):
        name = function.__name__
        mc.undoInfo(openChunk=True, chunkName=name)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
        except Exception:
            print(sys.exc_info()[1])

        finally:
            mc.undoInfo(closeChunk=True)
            return functionReturn

    return decoratorCode


# # ------------------------------------ CONTROL ------------------------------------ # #


class Control(object):

    '''
    Class to handle the rig control objects
    '''

    def __init__(self, obj):
        '''
        '''
        self.apiObject = None
        self.control = ''
        self.nodesId = []
        self.nodes = []
        self.bindPoseAttrs = []
        self.bindPoseValues = []
        self.parentScale = True
        self.rotateOrder = ControlTemplate.validRotateOrders[0]
        self.mirrorSide = ControlTemplate.validLocations[0]
        self.mirrorType = ControlTemplate.validMirrorTypes[0]

        if mc.objExists(obj):
            self.control = obj
            objType = ObjectType(self.control)
            if objType.isOfType('control'):
                self.updateControl()
            else:
                mc.warning(
                    '[Control] The supplied object {0} is not tagged as control object'.format(obj))
                return None
        else:
            raise ValueError(
                '[Control] Invalid object supplied {0}'.format(obj))

    def __str__(self):
        '''
        Method used to print usefull information about the class
        '''
        return ('{0}'.format(self.control))

    def updateControl(self):
        '''
        '''
        if mc.objExists(self.control):
            self.apiObject = getMObject(self.control)
            self.nodesId = []
            self.nodes = []

            # ==================================================================
            # # Collect the nodesIds
            # #
            # indices = mc.getAttr('{0}.nodesId'.format(self.control), multiIndices=True)
            # for x in indices:
            #     self.nodesId.append(mc.getAttr('{0}.nodesId[{1}]'.format(self.control, x)))
            # # Collect the nodes
            # #
            # indices = mc.getAttr('{0}.nodes'.format(self.control), multiIndices=True)
            # for x in indices:
            #     self.nodes.append(mc.connectionInfo('{0}.nodes[{1}]'.format(self.control, x), sfd=True).split('.')[0])
            # ==================================================================
            # Collect the nodesIds
            #
            indicesToRemove = []
            indices = mc.getAttr('{0}.nodesId'.format(
                self.control), multiIndices=True) or []
            for x in indices:
                inCx = mc.connectionInfo(
                    '{0}.nodes[{1}]'.format(self.control, x), sfd=True)
                if inCx:
                    node = inCx.split('.')[0]
                    identification = mc.getAttr(
                        '{0}.nodesId[{1}]'.format(self.control, x))
                    self.nodesId.append(identification)
                    self.nodes.append(node)
                else:
                    indicesToRemove.append(x)
            # Clean the invalid identifications
            #
            for x in indicesToRemove:
                try:
                    mc.removeMultiInstance(
                        '{0}.nodesId[{1}]'.format(self.control, x))
                    mc.removeMultiInstance(
                        '{0}.nodes[{1}]'.format(self.control, x))
                except Exception:
                    continue

            # Collect the bindPoseAttrs
            #
            indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                self.control), multiIndices=True) or []
            for x in indices:
                self.bindPoseAttrs.append(mc.getAttr(
                    '{0}.bindPoseAttrs[{1}]'.format(self.control, x)))
            # Collect the bindPoseValues
            #
            indices = mc.getAttr('{0}.bindPoseValues'.format(
                self.control), multiIndices=True) or []
            for x in indices:
                self.bindPoseValues.append(mc.getAttr(
                    '{0}.bindPoseValues[{1}]'.format(self.control, x)))

            if mc.attributeQuery('parentScale', node=self.control, exists=True):
                self.parentScale = mc.getAttr(
                    '{0}.parentScale'.format(self.control), asString=True)

            if mc.attributeQuery('rotateOrder', node=self.control, exists=True):
                self.rotateOrder = mc.getAttr(
                    '{0}.rotateOrder'.format(self.control), asString=True)

            if mc.attributeQuery('mirrorSide', node=self.control, exists=True):
                self.mirrorSide = mc.getAttr(
                    '{0}.mirrorSide'.format(self.control), asString=True)

            if mc.attributeQuery('mirrorType', node=self.control, exists=True):
                self.mirrorType = mc.getAttr(
                    '{0}.mirrorType'.format(self.control), asString=True)

    @staticmethod
    def copyControlSettings(sourceControl, destinationControl):
        """
        Copy the values of the custom attrs from source control and copy them to the destination control, multis are ignored
        work only on none referenced controls because locked attributes can't be unlocked on ref
        :param sourceControl: The source maya node
        :param destinationControl: The destination maya node
        :return: success state
        :rtyp: boolean
        """
        success = True
        if mc.objExists(sourceControl) and mc.objExists(destinationControl):
            if mc.referenceQuery(destinationControl, isNodeReferenced=True):
                raise RuntimeError(
                    '[copyControlSettings] The copy can only be done on none referenced destination control')
                return False

            try:
                mc.setAttr('{0}.rotateOrder'.format(destinationControl), mc.getAttr(
                    '{0}.rotateOrder'.format(sourceControl)))
            except Exception:
                success *= False

            userDefinedAttrs = mc.listAttr(
                sourceControl, ud=True, hasData=True, leaf=True) or []
            for userDefinedAttr in userDefinedAttrs:
                try:
                    if mc.attributeQuery(userDefinedAttr, n=destinationControl, exists=True):
                        # Special case of multi attributes on controls are not copyed, because handled independantly
                        if not mc.attributeQuery(userDefinedAttr, n=destinationControl, multi=True):
                            plugSource = sourceControl + '.' + userDefinedAttr
                            plugDestination = destinationControl + '.' + userDefinedAttr

                            unlocked = None
                            if mc.getAttr(plugDestination, lock=True):
                                mc.setAttr(plugDestination, lock=False)
                                unlocked = plugDestination

                            attributeType = mc.getAttr(plugSource, type=True)
                            if mc.getAttr(plugDestination, settable=True):
                                if attributeType == 'string':
                                    mc.setAttr(plugDestination, mc.getAttr(
                                        plugSource), type=attributeType)
                                elif attributeType == 'double3':
                                    double3 = mc.getAttr(plugSource)[0]
                                    mc.setAttr(
                                        plugDestination, double3[0], double3[1], double3[2], type=attributeType)
                                else:
                                    mc.setAttr(plugDestination,
                                               mc.getAttr(plugSource))

                            if unlocked:
                                mc.setAttr(plugDestination, lock=True)

                except Exception:
                    raise
                    success *= False
        else:
            success = False

        return success



    def getControlLocation(self):
        """Return the control mirror side
        :return: location
        :rtype: str
        """
        return self.mirrorSide



    def getControl(self):
        """Return the name of the dag representing this control in a maya scene
        :rtype: Maya dag node
        """
        control = ''
        self.control = pathFromMObject(self.apiObject)
        if mc.objExists(self.control):
            control = self.control
        else:
            raise RuntimeError(
                '[getControl] The control {0} does not exist anymore'.format(self.control))

        return control

    def getControlGroup(self):
        """Get the control group that this control belong to
        :return: controlGroup
        :rtype: ControlGroup or None
        :raises: RuntimeError The control does not exist anymore
        """
        controlGroup = None
        if mc.objExists(self.control):
            networks = mc.listConnections('{0}.message'.format(
                self.control), d=True, s=False, type='network') or []
            if networks:
                for node in networks:
                    if ObjectType(node).isOfType('controlGroup'):
                        controlGroup = ControlGroup(node)
                        if not controlGroup.isCgASplit():  # Not on a split, so we can return the cg, else iterate
                            break
        else:
            raise RuntimeError(
                '[getControlGroup] The control {0} does not exist anymore')

        return controlGroup

    def isInDescendants(self, otherControl):
        """Test if a control is in the descendants of the current control
        :param Control otherControl: the control to test
        :rtype: boolean
        """
        isInDescendants = False
        cAllDescendants = self.listRelativesControl(ad=True)
        for c in cAllDescendants:
            if c.getControl() == otherControl.getControl():
                isInDescendants = True

        return isInDescendants

    def listRelativesControl(self, **kwargs):
        """List all relatives to a control group
        :param boolean children/c        : children of cg
        :param boolean parent/p          : parent of cg
        :param boolean allParents/ap     : all parents of cg
        :param boolean allDescendants/ad : all descendants of cg
        :param boolean siblings/s        : siblings of cg
        """
        result = None
        validsArgs = ['nodeType', 'nt', 'children', 'c', 'parent', 'p',
                      'allParents', 'ap', 'allDescendants', 'ad', 'siblings', 's']
        for arg, value in kwargs.iteritems():
            if arg not in validsArgs:
                raise ValueError(
                    '[listRelativesCg] Invalid argument/value {0} {1}'.format(arg, value))
                return result

        if 'children' in kwargs or 'c' in kwargs:
            if kwargs.get('children') or kwargs.get('c'):
                result = []
                outCx = mc.listConnections('{0}.message'.format(
                    self.control), destination=True, p=True) or []
                if outCx:
                    for cx in outCx:
                        attr = baseAttributeName(cx)
                        if attr != 'nodes':
                            continue

                        node = nodeFromPlug(cx)
                        index = attributeIndexFromPlug(cx, 'nodes')
                        plug = '{0}.nodesId[{1}]'.format(node, index)
                        if mc.getAttr(plug) == 'parent':  # we are on the children
                            result.append(Control(node))

        elif 'parent' in kwargs or 'p' in kwargs:
            if kwargs.get('parent') or kwargs.get('p'):
                result = []
                indices = mc.getAttr('{0}.nodesId'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for index in indices:
                        plug = '{0}.nodesId[{1}]'.format(self.control, index)
                        if mc.getAttr(plug) == 'parent':
                            inCx = mc.listConnections('{0}.nodes[{1}]'.format(
                                self.control, index), source=True) or []
                            if inCx:
                                result.append(Control(inCx[0]))

        elif 'siblings' in kwargs or 's' in kwargs:
            if kwargs.get('siblings') or kwargs.get('s'):
                result = []
                cParents = self.listRelativesControl(parent=True)
                if cParents:
                    cChildren = cParents[0].listRelativesControl(children=True)
                    for cChild in cChildren:
                        if cChild.control != self.control:
                            result.append(cChild)
                else:  # All the control without parents are a sibling
                    controlGroup = self.getControlGroup()
                    rigGroup = controlGroup.getRigGroup()
                    if mc.objExists(rigGroup):
                        children = mc.listRelatives(
                            rigGroup, c=True, pa=True)
                        for child in children:
                            if ObjectType(child).isOfType('root'):
                                outCx = mc.listConnections('{0}.message'.format(
                                    child), d=True, s=False, p=True) or []
                                if outCx:
                                    for plug in outCx:
                                        attr = attributeFromPlug(
                                            plug)
                                        if attr == 'nodes':
                                            node = nodeFromPlug(
                                                plug)
                                            if node != self.control:
                                                result.append(Control(node))
        elif 'allParents' in kwargs or 'ap' in kwargs:
            if kwargs.get('allParents') or kwargs.get('ap'):
                result = []
                cParents = self.listRelativesControl(parent=True)
                for cParent in cParents:
                    result.append(cParent)
                    result += cParent.listRelativesControl(ap=True)
        elif 'allDescendants' in kwargs or 'ad' in kwargs:
            if kwargs.get('allDescendants') or kwargs.get('ad'):
                result = []
                cChildren = self.listRelativesControl(children=True)
                for cChild in cChildren:
                    # print cgChild
                    result.append(cChild)
                    result += cChild.listRelativesControl(ad=True)

        return result

    def getControlMainChildLoop(self, parentAim):
        """
        Find the direction aim of control toward the descendant that is the most aligned with the direction parentAim
        :param parentAim MVector aim direction of the parent
        :rtyp control: the child control the nearest to the parentAim direction
        """
        axisTolerance = mc.tolerance(q=True, linear=True)
        cMainChild = None

        maxDot = 0.0

        cChildren = self.listRelativesControl(c=True)
        if cChildren:
            ctrl = self.getControl()
            ctrlPos = mc.xform(ctrl, q=True, ws=True, t=True)
            # We take the first one if we're the impossibility to find a good candidate
            #
            cMainChild = cChildren[0]

            for cChild in cChildren:
                child = cChild.getControl()
                childPos = mc.xform(child, q=True, ws=True, t=True)
                childDirection = [.0, .0, .0]
                childDirection[0] = childPos[0] - ctrlPos[0]
                childDirection[1] = childPos[1] - ctrlPos[1]
                childDirection[2] = childPos[2] - ctrlPos[2]

                childDirection = om.MVector(
                    childDirection[0], childDirection[1], childDirection[2])
                cNextChild = cChild
                if fabs(childDirection.length()) <= axisTolerance:
                    warningString = child + ' is superposed on ' + ctrl + ', '
                    cNextChild = cChild.getControlMainChildLoop(parentAim)
                    if cNextChild is None:
                        warningString += 'and unable to find suitable child for ' + child
                        childDirection = om.MVector.kZeroVector
                    else:
                        ctrlNextChild = cNextChild.getControl()
                        warningString += 'using ' + ctrlNextChild + ' instead'
                        childPos = mc.xform(
                            ctrlNextChild, q=True, ws=True, t=True)
                        childDirection = [.0, .0, .0]
                        childDirection[0] = childPos[0] - ctrlPos[0]
                        childDirection[1] = childPos[1] - ctrlPos[1]
                        childDirection[2] = childPos[2] - ctrlPos[2]

                        childDirection = om.MVector(
                            childDirection[0], childDirection[1], childDirection[2])

                    print(warningString)

                if fabs(childDirection.length()) <= axisTolerance:
                    mc.warning(
                        '[getControlMainChildLoop] Unable to get valid direction for joint {0}, skipped'.format(child))
                else:
                    curDot = parentAim.normalize() * childDirection.normalize()
                    curDot = fabs(curDot)
                    if curDot > maxDot:
                        maxDot = curDot
                        cMainChild = cNextChild

        return cMainChild

    def getControlMainChild(self):
        """Retreive the nearest control in the aim direction of c (cParent -> c)
        If c hasn't any parent we evaluate the direction [0, 0, 0] toward c as main direction
        :param joint unicode: le joint.
        :param mixed boolean: si true l'exploration traverse les nodes non joints.
        :rtyp unicode: le fils le plus proche dans la direction du aim vector.
        """
        cMainChild = None
        ctrl = self.getControl()
        if mc.objExists(ctrl):
            parentAim = self.getControlParentAim(space=0)
            cMainChild = self.getControlMainChildLoop(parentAim)
        else:
            raise ValueError(
                '[getControlMainChild] joint {0} does not exist'.format(ctrl))

        return cMainChild

    def getControlParentAim(self, space):
        """This methos retreive the direction aim of the parent control
        Cette procedure recupere la direction "aim" du parent du joint.
        space : 0 = world, 1 = local frame of ctrl, 2 = local frame of parent of ctrl
        :param space int: 0, world, 1 local space of the control
        :rtyp MVector: aim vector du joint.
        """
        axisTolerance = mc.tolerance(query=True, linear=True)

        parentAimVector = om.MVector.kZeroVector

        sceneUp = mc.upAxis(query=True, ax=True)
        sceneFront = ''
        sceneRight = ''  # @UnusedVariable

        up = om.MVector.kZeroVector
        front = om.MVector.kZeroVector  # @UnusedVariable
        right = om.MVector.kZeroVector  # @UnusedVariable

        if sceneUp == 'y':
            sceneFront = 'z'
            sceneRight = 'x'  # @UnusedVariable
            up = om.MVector.kYaxisVector
            front = om.MVector.kZaxisVector  # @UnusedVariable
            right = om.MVector.kXaxisVector  # @UnusedVariable
        elif sceneUp == 'z':
            sceneFront = '-y'
            sceneRight = 'x'  # @UnusedVariable
            up = om.MVector.kZaxisVector
            front = om.MVector.kYnegAxisVector  # @UnusedVariable
            right = om.MVector.kXaxisVector  # @UnusedVariable
        else:
            raise RuntimeError(
                '[getJointParentAim] Unexpected upAxis value: {0}'.format(sceneUp))

        ctrl = self.getControl()
        if mc.objExists(ctrl):
            ctrlPos = mc.xform(ctrl, q=True, ws=True, t=True)
            parentAim = [.0, .0, .0]

            cParents = self.listRelativesControl(p=True)

            ctrlParent = ''
            if cParents:
                ctrlParent = cParents[0].getControl()

            if mc.objExists(ctrlParent):
                parentPos = mc.xform(ctrlParent, q=True, ws=True, t=True)
                parentAim[0] = ctrlPos[0] - parentPos[0]
                parentAim[1] = ctrlPos[1] - parentPos[1]
                parentAim[2] = ctrlPos[2] - parentPos[2]
            else:
                mc.warning('[getControlParentAim] {0} has no parent, assuming skeletons face "{1}" direction and using "{2}"'.format(
                    ctrl, sceneFront, sceneUp))
                parentAim[0] = up.x
                parentAim[1] = up.y
                parentAim[2] = up.z

            parentAimVector = om.MVector(
                parentAim[0], parentAim[1], parentAim[2])

            if fabs(parentAimVector.length()) <= axisTolerance:
                mc.warning('[getControlParentAim] {0} is superposed on {1}, using next parent'.format(
                    ctrlParent, ctrl))
                parentAimVector = cParents[0].getJointParentAim(space)
            else:
                parentAimVector.normalize()

            if space == 1:
                ctrlWorldInverseMatrix = om.MMatrix(
                    mc.getAttr(ctrl + '.worldInverseMatrix'))
                parentAimVector *= ctrlWorldInverseMatrix
                parentAimVector.normalize()
            elif space == 2:
                parentWorldInverseMatrix = om.MMatrix(
                    mc.getAttr(ctrlParent + '.worldInverseMatrix'))
                parentAimVector *= parentWorldInverseMatrix
                parentAimVector.normalize()

        else:
            raise ValueError(
                '[getControlParentAim] control {0} does not exist'.format(ctrl))

        return parentAimVector

    @staticmethod
    def searchNodeId(control, nodeId):
        """Search an id in the nodesId multi attr of the current control
        :param str nodeId: the node id to search
        :return: the index found
        :rtype: int
        """
        index = -1
        multiIndices = mc.getAttr(
            '{0}.nodesId'.format(control), multiIndices=True) or []
        for idx in multiIndices:
            if nodeId == mc.getAttr('{0}.nodesId[{1}]'.format(control, idx)):
                index = idx
                return idx

        return index

    @staticmethod
    def setNodeIdToMultis(control, node, nodeId):
        """Set a node id to the nodeIds multi attr of a control and connect it to the nodes multi attrs,
        if the id already exist, the connection to the nodes multi attr is replaced
        :param Maya object node: the node to add
        :param str nodeId: the id of the node
        """
        if mc.objExists(control) and mc.objExists(node):
            nodeOutPlug = '{0}.message'.format(node)
            index = Control.searchNodeId(control, nodeId)
            if index == -1:
                index = getMultiFirstAvailableIndex(
                    control, 'nodesId')

            inNodesIdPlug = '{0}.nodesId[{1}]'.format(control, index)
            inNodesPlug = '{0}.nodes[{1}]'.format(control, index)

            if checkNodeAttribute(control, ('nodes[{0}]'.format(index))):
                outPlug = mc.connectionInfo(inNodesPlug, sfd=True)
                if outPlug:
                    mc.disconnectAttr(outPlug, inNodesPlug)

            mc.setAttr(inNodesIdPlug, nodeId, type='string')
            mc.connectAttr(nodeOutPlug, inNodesPlug, force=True)

    @staticmethod
    def removeNodeIdFromMultis(control, nodeId):
        """Remove a node id from the nodeIds multi attr of a control and deconnect the node from the nodes multi attrs,
        :param str nodeId: the id of the node
        """
        if mc.objExists(control):
            index = Control.searchNodeId(control, nodeId)
            if index != -1:
                inNodesIdPlug = '{0}.nodesId[{1}]'.format(control, index)
                inNodesPlug = '{0}.nodes[{1}]'.format(control, index)

                outPlug = mc.connectionInfo(inNodesPlug, sfd=True)
                if outPlug:
                    mc.disconnectAttr(outPlug, inNodesPlug)

                mc.removeMultiInstance(inNodesIdPlug, b=True)
                mc.removeMultiInstance(inNodesPlug, b=True)

    def isControlInRelatives(self, otherControl=None, direction='parents'):
        """Test if a control is in the relatives of self
        :param Control otherControl: The relatives
        :param str direction: where to search, parent, children, siblings
        :rtyp boolean: if in relatives
        :raises: ValueError unknown direction type
        """
        isInRelatives = False
        if isinstance(otherControl, Control):
            if direction == 'parents':
                controls = self.listRelativesControl(ap=True)
            elif direction == 'descendants':
                controls = self.listRelativesControl(ad=True)
            elif direction == 'siblings':
                controls = self.listRelativesControl(s=True)
            else:
                raise ValueError(
                    '[isControlInRelatives] Unknown direction {0}'.format(direction))

            for c in controls:
                if c.apiObject == otherControl.apiObject:
                    isInRelatives = True
                    break

        return isInRelatives

    def isControlParentOf(self, otherControl=None):
        """Check if a control is the parent of the current control
        :param Control otherControl: the control to check
        :return: True if parent
        :rtype: boolean
        """
        isParent = False
        if mc.objExists(self.control):
            children = self.listRelativesControl(c=True)
            if children:
                for child in children:
                    if child.apiObject == otherControl.apiObject:
                        isParent = True
                        break

        return isParent

    def parentControlTo(self, otherControl=None, below=True):
        """reparent a control in the fk control hierarchy
        :param Control otherControl: the control to parent the current control
        :param boolean below: if the hierarchy below is handled, or re-parented to the father of the current control
        :return: True if everything is ok
        :rtype: boolean
        """
        if isinstance(otherControl, Control):
            if not self.isInDescendants(otherControl) and not otherControl.isControlParentOf(self):
                # the roots are parented under the sk
                otherSk = otherControl.getNode('sk')
                currentRoot = self.getNode('root')
                if not currentRoot:  # not a conventionnal control
                    mc.warning('[parentControlTo] Control {0} is not a classical control, root not detected'.format(
                        self.getControl()))
                    return

                if not otherSk:  # not a conventionnal control
                    mc.warning('[parentControlTo] Control {0} is not a classical control, sk not detected'.format(
                        otherControl.getControl()))
                    return

                if below:

                    try:
                        mc.parent(currentRoot, otherSk)
                    except Exception:
                        print (currentRoot, 'alredy child of', otherSk)
                    if not mc.isConnected('{0}.scale'.format(otherSk), '{0}.inverseScale'.format(currentRoot)):
                        mc.connectAttr('{0}.scale'.format(
                            otherSk), '{0}.inverseScale'.format(currentRoot), force=True)

                    Control.setNodeIdToMultis(
                        self.getControl(), otherControl, 'parent')
                else:
                    cChildren = self.listRelativesControl(c=True)
                    if cChildren:
                        roots = [cChild.getNode('root')
                                 for cChild in cChildren]
                        cParents = self.listRelativesControl(p=True)
                        if cParents:
                            cParent = cParents[0]
                            skParent = cParent.getNode('sk')
                            for root in roots:
                                mc.parent(root, skParent)
                                if not mc.isConnected('{0}.scale'.format(skParent), '{0}.inverseScale'.format(root)):
                                    mc.connectAttr('{0}.scale'.format(
                                        skParent), '{0}.inverseScale'.format(root), force=True)
                            for cChild in cChildren:
                                Control.setNodeIdToMultis(
                                    cChild.getControl(), cParent, 'parent')
                        else:
                            rigGroup = self.getControlGroup().getRigGroup()
                            for root in roots:
                                if not isParentOf(rigGroup, root):
                                    mc.parent(root, rigGroup)

                            for cChild in cChildren:
                                Control.removeNodeIdFromMultis(
                                    cChild.getControl(), 'parent')

                    mc.parent(currentRoot, otherSk)
                    pathFromMObject(self.apiObject)
                    if not mc.isConnected('{0}.scale'.format(otherSk), '{0}.inverseScale'.format(currentRoot)):
                        mc.connectAttr('{0}.scale'.format(
                            otherSk), '{0}.inverseScale'.format(currentRoot), force=True)

                    Control.setNodeIdToMultis(
                        self.getControl(), otherControl, 'parent')

        elif otherControl is None:
            self.unparentControl(below=below)

    def unparentControl(self, below=True):
        """Unparent current control ( to the rig group of the controlGroup in fact)
        :param boolean below: if the hierarchy below is handled, or re-parented to the father of the current control
        """
        selfRoot = self.getNode('root')
        cg = self.getControlGroup()
        rigGroup = cg.getRigGroup()
        if below:
            if mc.objExists(selfRoot) and not isParentOf(rigGroup, selfRoot):
                mc.parent(selfRoot, rigGroup)
                pathFromMObject(self.apiObject)
                Control.removeNodeIdFromMultis(self.getControl(), 'parent')
        else:
            cChildren = self.listRelativesControl(c=True)
            if cChildren:
                roots = [cChild.getNode('root') for cChild in cChildren]
                cParents = self.listRelativesControl(p=True)
                if cParents:
                    cParent = cParents[0]
                    skParent = cParent.getNode('sk')
                    for root in roots:
                        mc.parent(root, skParent)
                        if not mc.isConnected('{0}.scale'.format(skParent), '{0}.inverseScale'.format(root)):
                            mc.connectAttr('{0}.scale'.format(
                                skParent), '{0}.inverseScale'.format(root), force=True)
                    for cChild in cChildren:
                        Control.setNodeIdToMultis(
                            cChild.getControl(), cParent, 'parent')
                else:
                    for root in roots:
                        if not isParentOf(rigGroup, root):
                            mc.parent(root, rigGroup)

                    for cChild in cChildren:
                        Control.removeNodeIdFromMultis(
                            cChild.getControl(), 'parent')

            if mc.objExists(selfRoot) and not isParentOf(rigGroup, selfRoot):
                mc.parent(selfRoot, rigGroup)
                pathFromMObject(self.apiObject)
                Control.removeNodeIdFromMultis(self.getControl(), 'parent')

    def getControlBranchRoot(self):
        """Get the root of the current controls branch
        :return: Control
        """
        cBranchRoot = self
        cParents = self.listRelativesControl(p=True)
        if cParents:
            cChildren = cParents[0].listRelativesControl(c=True)
            if len(cChildren) > 1:  # root branch Y
                cBranchRoot = cParents[0]
            else:
                cBranchRoot = cParents[0].getControlBranchRoot()

        return cBranchRoot

    def isPoseNodeExists(self):
        '''
        Check if a pose node exists above a control
        '''
        exists = False
        if mc.objExists(self.control):
            pose = self.getNode('pose')
            exists = mc.objExists(pose)

        return exists

    def addPoseNode(self):
        """Add a poseNode above the control object, used to applied pre-defigned pose in the rig driven by SDK for example
        """
        pose = ''
        if not mc.objExists(self.control):
            raise RuntimeError(
                '[addPoseNode] The control {0} does not exist anymore'.format(self.control))

        if self.isPoseNodeExists():
            pose = self.getNode('pose')
            return pose

        if mc.referenceQuery(self.control, isNodeReferenced=True):
            mc.warning('[addPoseNode] Unable to add a pose node on a control from a referenced file')

        root = self.getNode('root')
        if not mc.objExists(root):  # Not a classical control
            mc.warning('[addPoseNode] Control {0} is not a classical control, no root detected'.format(
                self.getControl()))
            return pose

        # Creation of the pose node
        #
        np = NameParser(self.control)
        poseName = 'pose' + '_' + np.getBaseName() + np.getNameIndex()
        if np.getNameSuffix() != '':
            poseName += '_' + np.getNameSuffix()

        pose = mc.createNode('joint', name=poseName, parent=root)
        mc.setAttr('{0}.segmentScaleCompensate'.format(
            pose), False, lock=True)
        mc.setAttr('{0}.drawStyle'.format(pose), 2)
        # Create the attribute to specified that this node is a pose
        #
        ObjectType(pose).setRigNodeType('pose', lockIt=True)
        # Register the pose node in the control
        #
        idx = getMultiFirstAvailableIndex(self.control, 'nodesId')
        mc.setAttr('{0}.nodesId[{1}]'.format(
            self.control, idx), 'pose', type='string')
        mc.connectAttr('{0}.message'.format(
            pose), '{0}.nodes[{1}]'.format(self.control, idx))
        self.control = mc.parent(self.control, pose)[0]
        sk = self.getNode('sk')
        sk = mc.parent(sk, pose)[0]
        # Connect the rotateOrders
        #
        mc.connectAttr('{0}.rotateOrder'.format(
            self.control), '{0}.rotateOrder'.format(pose))
        # Creation of the tweak to avoid shear in the hierarchy below the pose when there is non uniform scale on the pose
        #
        mc.addAttr(pose, keyable=True, ln='poseScale', at='double3')
        mc.addAttr(pose, keyable=True, ln='poseScaleX',
                   p='poseScale', at='double', dv=1.0)
        mc.addAttr(pose, keyable=True, ln='poseScaleY',
                   p='poseScale', at='double', dv=1.0)
        mc.addAttr(pose, keyable=True, ln='poseScaleZ',
                   p='poseScale', at='double', dv=1.0)
        # lock and hide the unused attributes
        #
        lockAttributes(pose, 'scaleX', 'scaleY',
                       'scaleZ', 'visibility')
        hideAttributes(pose, 'scaleX', 'scaleY',
                       'scaleZ', 'visibility')
        # Add the multiplyDivide between the pose and the control toward the sk
        #
        sk = self.getNode('sk')
        sourcePlug = mc.connectionInfo('{0}.scale'.format(sk),
                                       sfd=True)
        if checkPlug(sourcePlug):
            safeDisconnectAttr(sourcePlug,
                               '{0}.scale'.format(sk))

        multiplyDivide = mc.createNode('multiplyDivide')
        mc.connectAttr('{0}.poseScale'.format(
            pose), '{0}.input1'.format(multiplyDivide))
        mc.connectAttr('{0}.scale'.format(
            self.control), '{0}.input2'.format(multiplyDivide))
        mc.connectAttr('{0}.output'.format(
            multiplyDivide), '{0}.scale'.format(sk))

        self.updateControl()

        return pose

    def removePoseNode(self, deleteInputs=True, verbose=False):
        """Remove a pose node previously created above the control
        :return: the pose node removed
        :rtype: Maya dagNode
        """
        pose = ''
        if mc.objExists(self.control):
            root = self.getNode('root')
            if not mc.objExists(root):  # Not a classical control
                mc.warning('[removePoseNode] Control {0} is not a classical control, no root detected'.format(
                    self.getControl()))
                return pose

            if mc.referenceQuery(self.control, isNodeReferenced=True):
                mc.warning(
                    '[removePoseNode] Unable to add a pose node on a control from a referenced file')

            if self.isPoseNodeExists():
                pose = self.getNode('pose')
                # Transfert the pose matrix to the control
                #
                self.poseToControl(verbose=False)
                ctrl = self.getControl()
                sk = self.getNode('sk')
                try:
                    if not isParentOf(root, ctrl):
                        ctrl = mc.parent(ctrl, root)[0]
                    if not isParentOf(root, sk):
                        sk = mc.parent(sk, root)[0]
                    # Remove the multiplyDivide between the pose and the control toward the sk
                    #
                    sourcePlug = mc.connectionInfo(
                        '{0}.scale'.format(sk), sfd=True)
                    if checkPlug(sourcePlug):
                        node = nodeFromPlug(sourcePlug)
                        if node != self.control and node != pose:
                            mc.delete(node)  # A multiplyDivide usually
                            safeConnectAttr('{0}.scale'.format(self.control),
                                            '{0}.scale'.format(sk))

                    Control.removeNodeIdFromMultis(self.getControl(), 'pose')
                    if deleteInputs:
                        # initialize an MItDependencyGraph iterator to traverse the graph until a dagNode is found,
                        # typically, we have a dagNode as driver, so, we will stop the iterator when a shape or a transform is found
                        #
                        toDelete = getUpStreamNodes(pose, doNotTraverseNodes=(
                            'dagNode',), exactType=False, verbose=False)
                        inPlugs, outPlugs = [], []
                        for i in range(len(toDelete)):
                            node = toDelete[i]
                            if not mc.objExists(node):
                                if verbose:
                                    mc.warning(
                                        '[removePoseNode] Node ' + node + ' does not exist anymore')
                                continue
                            if verbose:
                                print (node)

                            plugs = mc.listConnections(
                                node, source=False, destination=True, plugs=True, connections=True) or []
                            if plugs:
                                for i in xrange(0, len(plugs), 2):
                                    plug = plugs[i]
                                    if verbose:
                                        print ('\tDisconnect output: ', plug)
                                    temp = unPlug(plug, source=False, dest=True,
                                                  force=True, verbose=False)
                                    outPlugs.extend(temp)

                            plugs = mc.listConnections(node, source=True,
                                                       destination=False, plugs=True,
                                                       connections=True) or []
                            if plugs:
                                for i in xrange(0, len(plugs), 2):
                                    plug = plugs[i]
                                    if verbose:
                                        print('\tDisconnect input: ', plug)
                                    temp = unPlug(plug, source=True,
                                                  dest=False, force=True,
                                                  verbose=False)
                                    inPlugs.extend(temp)

                            mc.delete(node)

                    mc.delete(pose)
                except Exception:
                    raise

    def setControlLabel(self):
        '''
        Set the label to the control if it is a joint
        '''
        success = True
        if mc.objExists(self.control) and mc.objectType(self.control, isAType='joint'):
            setLabelsToJoints([self.control])
        else:
            success = False
        return success

    def getNode(self, groupName):
        '''
        '''
        group = ''
        if groupName in self.nodesId:
            try:
                idx = self.nodesId.index(groupName)
                group = self.nodes[idx]
            except Exception:
                group = ''
                raise
        return group

    @staticmethod
    def getControlFromNode(node):
        """
        Get the control from a node
        :param Maya dagNode: node
        :rtyp: Maya dagNode
        :return: control
        """
        ctrl = ''
        if mc.objExists(node):
            if ObjectType(node).isOfType('control'):
                ctrl = node
            else:
                plugs = mc.connectionInfo(node + '.message', dfs=True) or []
                for plug in plugs:
                    nd = nodeFromPlug(plug)
                    if ObjectType(nd).isOfType('control'):
                        ctrl = nd
                        break

        return ctrl

    def cleanBindPose(self):
        """Clean the bindPose attributes of the control
        """
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in indices:
                        mc.removeMultiInstance(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
            if mc.attributeQuery('bindPoseValues', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseValues'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in indices:
                        mc.removeMultiInstance(
                            '{0}.bindPoseValues[{1}]'.format(self.control, indice))

    def setBindPose(self):
        """Set the current control values as the default bindPose
        """
        if mc.objExists(self.control):
            self.cleanBindPose()
            keyableAttrs = mc.listAttr(
                self.control, visible=True, keyable=True, scalar=True, leaf=True, shortNames=True) or []
            if keyableAttrs:
                self.bindPoseAttrs = []
                self.bindPoseValues = []
                idx = 0
                for indice in xrange(len(keyableAttrs)):
                    plug = '{0}.{1}'.format(self.control, keyableAttrs[indice])
                    if mc.objExists(plug):
                        bpAttrsPlug = '{0}.bindPoseAttrs[{1}]'.format(
                            self.control, idx)
                        mc.setAttr(
                            bpAttrsPlug, keyableAttrs[indice], type='string')
                        self.bindPoseAttrs.append(keyableAttrs[indice])
                        value = mc.getAttr(plug)
                        bpValuesPlug = '{0}.bindPoseValues[{1}]'.format(
                            self.control, idx)
                        mc.setAttr(bpValuesPlug, value)
                        self.bindPoseValues.append(value)
                        idx += 1

    def getBindPose(self):
        """Retreive the current bindPose
        """
        bindPose = {}
        self.bindPoseAttrs = []
        self.bindPoseValues = []
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in xrange(len(indices)):
                        attr = mc.getAttr(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
                        value = mc.getAttr(
                            '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        bindPose[attr] = value
                        self.bindPoseAttrs.append(attr)
                        self.bindPoseValues.append(value)
        return bindPose

    def goToBindPose(self):
        """Set the control to the curent registered pose
        """
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in xrange(len(indices)):
                        attr = mc.getAttr(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
                        if mc.attributeQuery(attr, node=self.control, exists=True):
                            value = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                            try:
                                mc.setAttr('{0}.{1}'.format(
                                    self.control, attr), value)
                            except Exception:
                                continue

    def resetBindPose(self):
        """Reset the bindPose to the default attribute values
        """
        if mc.objExists(self.control):
            self.cleanBindPose()
            keyableAttrs = mc.listAttr(
                self.control, visible=True, keyable=True, leaf=True, shortNames=True) or []
            if keyableAttrs:
                self.bindPoseAttrs = []
                self.bindPoseValues = []
                idx = 0
                for indice in xrange(len(keyableAttrs)):
                    plug = '{0}.{1}'.format(self.control, keyableAttrs[indice])
                    if mc.objExists(plug):
                        bpAttrsPlug = '{0}.bindPoseAttrs[{1}]'.format(
                            self.control, idx)
                        mc.setAttr(
                            bpAttrsPlug, keyableAttrs[indice], type='string')
                        self.bindPoseAttrs.append(keyableAttrs[indice])
                        defaults = mc.attributeQuery(
                            keyableAttrs[indice], node=self.control, listDefault=True)
                        value = defaults[0]
                        bpValuesPlug = '{0}.bindPoseValues[{1}]'.format(
                            self.control, idx)
                        mc.setAttr(bpValuesPlug, value)
                        self.bindPoseValues.append(value)
                        try:
                            mc.setAttr(plug, value)
                        except Exception:
                            continue

                        idx += 1

    def getRotationBindPose(self):
        """Get the bindPose in rotation of this control
        """
        bindPoseRotation = [.0, .0, .0]
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in xrange(len(indices)):
                        attr = mc.getAttr(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
                        if attr == 'rx':
                            bindPoseRotation[0] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'ry':
                            bindPoseRotation[1] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'rz':
                            bindPoseRotation[2] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))

        return bindPoseRotation

    def getTranslationBindPose(self):
        """Get the bindPose in translation of this control
        """
        bindPoseTranslation = [.0, .0, .0]
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in xrange(len(indices)):
                        attr = mc.getAttr(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
                        if attr == 'tx':
                            bindPoseTranslation[0] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'ty':
                            bindPoseTranslation[1] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'tz':
                            bindPoseTranslation[2] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))

        return bindPoseTranslation

    def getScaleBindPose(self):
        """Get the bindPose in scale of this control
        """
        bindPoseScale = [1.0, 1.0, 1.0]
        if mc.objExists(self.control):
            if mc.attributeQuery('bindPoseAttrs', node=self.control, exists=True):
                indices = mc.getAttr('{0}.bindPoseAttrs'.format(
                    self.control), multiIndices=True) or []
                if indices:
                    for indice in xrange(len(indices)):
                        attr = mc.getAttr(
                            '{0}.bindPoseAttrs[{1}]'.format(self.control, indice))
                        if attr == 'sx':
                            bindPoseScale[0] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'sy':
                            bindPoseScale[1] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))
                        elif attr == 'sz':
                            bindPoseScale[2] = mc.getAttr(
                                '{0}.bindPoseValues[{1}]'.format(self.control, indice))

        return bindPoseScale

    def rotateOrderToMTransformationRotateOrder(self):
        '''
        '''
        MTransformationRotateOrders = {0: om.MTransformationMatrix.kXYZ, 1: om.MTransformationMatrix.kXZY, 2: om.MTransformationMatrix.kYXZ,
                                       3: om.MTransformationMatrix.kYZX, 4: om.MTransformationMatrix.kZXY, 5: om.MTransformationMatrix.kZYX}
        return MTransformationRotateOrders[ControlTemplate.validRotateOrders.index(self.rotateOrder)]

    def controlToPose(self, forcePoseNode=False, relative=False, verbose=False):
        """Transfert the current matrix from the control to the pose node
        :param boolean forcePoseNode: force the creation of a poseNode if not present
        :param boolean relative: take account of the local matrix of the pose node
        :param str driverPlug: if specified a driven key is created
        :param str driverValue: if not specified the driven key is created with the current value of the driver
        :param str itt: The in tangent type, or the global in tangent type if not specified
        :param str ott: The out tangent type, or the global out tangent type if not specified
        :param boolean verbose: debug informations
        """
        poseNode = self.getNode('pose')
        if not mc.objExists(poseNode) and forcePoseNode:
            poseNode = self.addPoseNode()

        if mc.objExists(poseNode):
            skNode = self.getNode('sk')
            # We take the sk joint because it has the final scale
            skLocalMatrix = om.MMatrix(
                mc.getAttr('{0}.matrix'.format(skNode)))
            rotateOrder = mc.getAttr('{0}.rotateOrder'.format(skNode))
            skTransformationMatrix = om.MTransformationMatrix(skLocalMatrix)
            if verbose:
                print('Sk Node {0}'.format(poseNode))
                print('\tTranslation: {0}'.format(
                    skTransformationMatrix.translation(om.MSpace.kTransform)))
                rotation = skTransformationMatrix.rotation()
                rotation.reorderIt(rotateOrder)
                rot = [degrees(rotation[0]), degrees(
                    rotation[1]), degrees(rotation[2])]
                print('\tRotation: {0}'.format(rot))
                print('\tScale: {0}'.format(
                    skTransformationMatrix.scale(om.MSpace.kTransform)))
                print('\tShear: {0}'.format(
                    skTransformationMatrix.shear(om.MSpace.kTransform)))

            if verbose:
                print('Pose Node {0}'.format(poseNode))
            # tweak 02/06/2016 test to ignore the jointOrient in the case of a rig where the pose node is not oriented like the root
            # Example: Tongue DODORAPTOR relative to the deformation of the throat
            #
            jointOrient = mc.getAttr('{0}.jointOrient'.format(poseNode))[0]
            jointOrient = om.MEulerRotation([radians(jointOrient[0]), radians(
                jointOrient[1]), radians(jointOrient[2])])
            jointOrientInverseMatrix = om.MMatrix.kIdentity
            if not jointOrient.isZero():
                if verbose:
                    print('\tJointOrient: {0}'.format([degrees(jointOrient.x), degrees(
                        jointOrient.y), degrees(jointOrient.z)]))
                    print('\tCanceling jointOrient...')
                jointOrientInverseMatrix = jointOrient.asMatrix().inverse()

            poseLocalMatrix = om.MMatrix(
                mc.getAttr('{0}.matrix'.format(poseNode)))
            poseLocalMatrix *= jointOrientInverseMatrix
            poseTransformationMatrix = om.MTransformationMatrix(
                poseLocalMatrix)
            if verbose:
                print('\tTranslation: {0}'.format(
                    poseTransformationMatrix.translation(om.MSpace.kTransform)))
                rotation = poseTransformationMatrix.rotation()
                rotation.reorderIt(rotateOrder)
                rot = [degrees(rotation[0]), degrees(
                    rotation[1]), degrees(rotation[2])]
                print('\tRotation: {0}'.format(rot))
                print('\tScale: {0}'.format(
                    poseTransformationMatrix.scale(om.MSpace.kTransform)))
                print('\tShear: {0}'.format(
                    poseTransformationMatrix.shear(om.MSpace.kTransform)))

            matrix = skLocalMatrix * poseLocalMatrix
            if relative:
                matrix *= poseLocalMatrix.inverse()

            transformationMatrix = om.MTransformationMatrix(matrix)
            translation = transformationMatrix.translation(
                om.MSpace.kTransform)
            rotation = transformationMatrix.rotation()
            rotation.reorderIt(rotateOrder)
            scale = transformationMatrix.scale(om.MSpace.kTransform)
            if relative:
                controlLocalMatrix = om.MMatrix(
                    mc.getAttr('{0}.matrix'.format(self.control)))
                controlTransformationMatrix = om.MTransformationMatrix(
                    controlLocalMatrix)
                scale = controlTransformationMatrix.scale(om.MSpace.kTransform)
            shear = transformationMatrix.shear(om.MSpace.kTransform)
            if verbose:
                print('Pose node {0}'.format(poseNode))
                print('\tTranslation: {0}'.format(translation))
                rot = [degrees(rotation[0]), degrees(
                    rotation[1]), degrees(rotation[2])]
                print('\tRotation: {0}'.format(rot))
                print('\tScale: {0}'.format(scale))
                print('\tShear: {0}'.format(shear))

            try:
                mc.setAttr('{0}.translate'.format(
                    self.control), .0, .0, .0, type='double3')
                mc.setAttr('{0}.rotate'.format(
                    self.control), .0, .0, .0, type='double3')
                mc.setAttr('{0}.scale'.format(self.control),
                             1.0, 1.0, 1.0, type='double3')
                mc.setAttr('{0}.shear'.format(
                    self.control), .0, .0, .0, type='double3')

                mc.setAttr('{0}.translate'.format(
                    poseNode), translation.x, translation.y, translation.z, type='double3')
                mc.setAttr('{0}.rotate'.format(poseNode), degrees(
                    rotation.x), degrees(rotation.y), degrees(rotation.z), type='double3')
                mc.setAttr('{0}.poseScale'.format(poseNode),
                             scale[0], scale[1], scale[2], type='double3')
                mc.setAttr('{0}.shear'.format(poseNode),
                             shear[0], shear[1], shear[2], type='double3')
            except Exception:
                mc.warning(
                    '[controlToPose] Problem during the transfert of the control values to the pose node ({0} -> {1})'.format(self.control, poseNode))

    def createPose(self, driverPlug, driverValue, driven, staticCurves=True, itt='linear', ott='linear', preInfinity='Constant', postInfinity='Constant', verbose=False):
        """Create a pose between driver plug and the driven
        :param unicode driverPlug: the driver plug
        :param float driverValue: the value of the driver plug
        :param unicode driven: the driven node
        :param str itt: The in tangent type
        :param str ott: The out tangent type
        :param str preInfinity: The behaviour of the animCurve before the first key
        :param str postInfinity: The behaviour of the animCurve after the last key
        :param boolean verbose: debug informations
        :raises: ValueError Invalid driver plug
        """
        driverNode = nodeFromPlug(driverPlug)
        driverAttr = mc.attributeName(driverPlug, l=True)
        driverPlug = driverNode + '.' + driverAttr
        if checkNodeAttribute(driverNode, driverAttr):
            if not isinstance(driverValue, float):
                mc.warning('[createPose] Invalid driver value {0} supplied, the current value of the driver plug {1} will be used'.format(
                    driverValue, driverPlug))
                driverValue = mc.getAttr(driverPlug)

            channels = mc.listAttr(driven, v=True, k=True, s=True) or []
            for channel in channels:
                # Build the driven plug and retreive its current value
                #
                drivenPlug = ('{0}.{1}'.format(driven, channel))
                if not mc.getAttr(drivenPlug, se=True):
                    mc.warning(
                        '[createPose] Plug {0} is not settable'.format(drivenPlug))
                    continue

                drivenValue = mc.getAttr(drivenPlug)
                blendWeighted = True
                if channel.startswith('scale') or channel.startswith('poseScale'):
                    blendWeighted = False

                mainChannelBoxName = mel.eval('$gDummyName = $gChannelBoxName')
                cbPrecision = mc.channelBox(
                    mainChannelBoxName, query=True, precision=True)

                drivenValue = round(drivenValue, cbPrecision)

                createDefaultKey = True
                setDrivenKey(driverPlug, driverValue, drivenPlug, drivenValue, staticCurves,
                                     blendWeighted, createDefaultKey, itt, ott, preInfinity, postInfinity, verbose)
        else:
            raise ValueError(
                '[createPose] Invalid driver plug {0}'.format(driverPlug))

    def poseToControl(self, verbose=False):
        """Transfert the current matrix from the pose node to the control
        :param boolean absolute: take account of the local matrix of the pose node
        :param boolean verbose: debug informations
        """
        poseNode = self.getNode('pose')
        if not mc.objExists(poseNode):
            mc.warning(
                '[poseToControl] Pose node does not exist for control {0}'.format(self.control))
            return

        # tweak 03/06/2016 test to ignore the jointOrient in the case of a rig where the pose node is not oriented like the root
        # Example: Tongue DODORAPTOR relative to the deformation of the throat
        #
        jointOrient = mc.getAttr('{0}.jointOrient'.format(poseNode))[0]
        jointOrient = om.MEulerRotation([radians(jointOrient[0]), radians(
            jointOrient[1]), radians(jointOrient[2])])
        jointOrientInverseMatrix = om.MMatrix.kIdentity
        if not jointOrient.isZero():
            if verbose:
                print('\tJointOrient: {0}'.format([degrees(jointOrient.x), degrees(
                    jointOrient.y), degrees(jointOrient.z)]))
                print('\tCanceling jointOrient...')
            jointOrientInverseMatrix = jointOrient.asMatrix().inverse()

        poseLocalMatrix = om.MMatrix(
            mc.getAttr('{0}.matrix'.format(poseNode)))
        poseLocalMatrix *= jointOrientInverseMatrix
        rotateOrder = mc.getAttr('{0}.rotateOrder'.format(poseNode))
        if verbose:
            print('Pose Node {0}'.format(poseNode))
            print('\tTranslation: {0}'.format(om.MTransformationMatrix(
                poseLocalMatrix).translation(om.MSpace.kTransform)))
            rotation = om.MTransformationMatrix(poseLocalMatrix).rotation()
            rotation.reorderIt(rotateOrder)
            rot = [degrees(rotation[0]), degrees(
                rotation[1]), degrees(rotation[2])]
            print('\tRotation: {0}'.format(rot))
            print('\tScale: {0}'.format(om.MTransformationMatrix(
                poseLocalMatrix).scale(om.MSpace.kTransform)))
            print('\tShear: {0}'.format(om.MTransformationMatrix(
                poseLocalMatrix).shear(om.MSpace.kTransform)))

        skNode = self.getNode('sk')
        # We take the sk joint because it has the final scale
        skLocalMatrix = om.MMatrix(mc.getAttr('{0}.matrix'.format(skNode)))
        if verbose:
            print('Sk Node {0}'.format(skNode))
            print('\tTranslation: {0}'.format(om.MTransformationMatrix(
                skLocalMatrix).translation(om.MSpace.kTransform)))
            rotation = om.MTransformationMatrix(skLocalMatrix).rotation()
            rotation.reorderIt(rotateOrder)
            rot = [degrees(rotation[0]), degrees(
                rotation[1]), degrees(rotation[2])]
            print('\tRotation: {0}'.format(rot))
            print('\tScale: {0}'.format(om.MTransformationMatrix(
                skLocalMatrix).scale(om.MSpace.kTransform)))
            print('\tShear: {0}'.format(om.MTransformationMatrix(
                skLocalMatrix).shear(om.MSpace.kTransform)))

        matrix = skLocalMatrix * poseLocalMatrix

        transformationMatrix = om.MTransformationMatrix(matrix)
        translation = transformationMatrix.translation(om.MSpace.kTransform)
        rotation = transformationMatrix.rotation()
        rotation.reorderIt(rotateOrder)
        scale = transformationMatrix.scale(om.MSpace.kTransform)
        shear = transformationMatrix.shear(om.MSpace.kTransform)

        if verbose:
            print('Control Node {0}'.format(self.control))
            print('\tTranslation: {0}'.format(translation))
            rot = [degrees(rotation[0]), degrees(
                rotation[1]), degrees(rotation[2])]
            print('\tRotation: {0}'.format(rot))
            print('\tScale: {0}'.format(scale))
            print('\tShear: {0}'.format(shear))

        mc.setAttr('{0}.translate'.format(
            poseNode), .0, .0, .0, type='double3')
        mc.setAttr('{0}.rotate'.format(poseNode), .0, .0, .0, type='double3')
        mc.setAttr('{0}.poseScale'.format(poseNode),
                   1.0, 1.0, 1.0, type='double3')
        mc.setAttr('{0}.shear'.format(poseNode), .0, .0, .0, type='double3')

        mc.setAttr('{0}.translate'.format(self.control),
                   translation.x, translation.y, translation.z, type='double3')
        mc.setAttr('{0}.rotate'.format(self.control), degrees(
            rotation.x), degrees(rotation.y), degrees(rotation.z), type='double3')
        mc.setAttr('{0}.scale'.format(self.control),
                   scale[0], scale[1], scale[2], type='double3')
        mc.setAttr('{0}.shear'.format(self.control),
                   shear[0], shear[1], shear[2], type='double3')

    def mutePose(self):
        """Mute the driven channels of the pose
        """
        poseNode = self.getNode('pose')
        if not mc.objExists(poseNode):
            mc.warning(
                '[mutePose] Pose node does not exist for control {0}'.format(self.control))
            return

        channels = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ',
                    'poseScaleX', 'poseScaleY', 'poseScaleZ', 'shearXY', 'shearXZ', 'shearYZ']
        for channel in channels:
            if isPlugConnected('{0}.{1}'.format(poseNode, channel), 0) and not mc.mute('{0}.{1}'.format(poseNode, channel), query=True):
                mc.mute('{0}.{1}'.format(poseNode, channel))

    def unmutePose(self):
        """Unmute the driven channels of the pose
        """
        poseNode = self.getNode('pose')
        if not mc.objExists(poseNode):
            mc.warning(
                '[unmutePose] Pose node does not exist for control {0}'.format(self.control))
            return

        channels = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ',
                    'poseScaleX', 'poseScaleY', 'poseScaleZ', 'shearXY', 'shearXZ', 'shearYZ']
        for channel in channels:
            if isPlugConnected('{0}.{1}'.format(poseNode, channel), 0) and mc.mute('{0}.{1}'.format(poseNode, channel), query=True):
                mc.mute('{0}.{1}'.format(poseNode, channel), disable=True)

    def getConnectedSkinClusters(self):
        """get all the skinClusters connected to the skin node of this control
        :return: list of skinClusters
        :rtype: list
        """
        skinClusters = []
        skNode = self.getNode('sk')
        if mc.objExists(skNode):
            skinClusters = mc.listConnections(
                skNode, s=False, d=True, type='skinCluster') or []
            skinClusters = list(set(skinClusters))

        return skinClusters

    def mirrorTranslate(self, flip=False, verbose=False):
        """Mirror the translations from the current control to its mirror
        :param boolean flip: the values are flipped and not mirrored
        :param boolean verbose: debug informations
        """
        axisTolerance = mc.tolerance(q=True, linear=True)
        mirror = self.getNode('mirror')
        cMirror = None
        if mc.objExists(mirror):
            cMirror = Control(mirror)

        mirrorType = self.mirrorType

        translateSource = list(mc.getAttr(
            '{0}.translate'.format(self.getControl()))[0])
        translate = [.0, .0, .0]
        if cMirror:
            translateDest = list(mc.getAttr(
                '{0}.translate'.format(cMirror.getControl()))[0])
            if mirrorType == 'joint':
                try:
                    translate[0] = -1.0 * translateSource[0]
                    translate[1] = -1.0 * translateSource[1]
                    translate[2] = -1.0 * translateSource[2]

                    mc.setAttr('{0}.translate'.format(cMirror.getControl(
                    )), translate[0], translate[1], translate[2], type='double3')
                    if flip:
                        translate[0] = -1.0 * translateDest[0]
                        translate[1] = -1.0 * translateDest[1]
                        translate[2] = -1.0 * translateDest[2]
                        mc.setAttr('{0}.translate'.format(
                            self.getControl()), translate[0], translate[1], translate[2], type='double3')
                except Exception:
                    pass

            elif mirrorType == 'transform':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                                                                   axisTolerance):
                    mult = (-1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, -1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, 1.0, -1.0)

                try:
                    translate[0] = mult[0] * translateSource[0]
                    translate[1] = mult[1] * translateSource[1]
                    translate[2] = mult[2] * translateSource[2]
                    mc.setAttr('{0}.translate'.format(cMirror.getControl(
                    )), translate[0], translate[1], translate[2], type='double3')
                    if flip:
                        translate[0] = mult[0] * translateDest[0]
                        translate[1] = mult[1] * translateDest[1]
                        translate[2] = mult[2] * translateDest[2]
                        mc.setAttr('{0}.translate'.format(
                            self.getControl()), translate[0], translate[1], translate[2], type='double3')
                except Exception:
                    pass

            elif mirrorType == 'orientation':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                                                                   axisTolerance):
                    mult = (1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, 1.0, 1.0)

                try:
                    translate[0] = mult[0] * translateSource[0]
                    translate[1] = mult[1] * translateSource[1]
                    translate[2] = mult[2] * translateSource[2]
                    mc.setAttr('{0}.translate'.format(cMirror.getControl(
                    )), translate[0], translate[1], translate[2], type='double3')
                    if flip:
                        translate[0] = mult[0] * translateDest[0]
                        translate[1] = mult[1] * translateDest[1]
                        translate[2] = mult[2] * translateDest[2]
                        mc.setAttr('{0}.translate'.format(
                            self.getControl()), translate[0], translate[1], translate[2], type='double3')
                except Exception:
                    pass
        # No mirror control found
        #
        else:
            if mirrorType != 'none':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                                                                   axisTolerance):
                    if not flip:
                        mult = (.0, 1.0, 1.0)
                    else:
                        mult = (-1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    if not flip:
                        mult = (1.0, .0, 1.0)
                    else:
                        mult = (1.0, -1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    if not flip:
                        mult = (1.0, 1.0, 0.0)
                    else:
                        mult = (1.0, 1.0, -1.0)

                try:
                    translate[0] = mult[0] * translateSource[0]
                    translate[1] = mult[1] * translateSource[1]
                    translate[2] = mult[2] * translateSource[2]

                    mc.setAttr('{0}.translate'.format(
                        self.getControl()), translate[0], translate[1], translate[2], type='double3')
                except Exception:
                    pass

    def mirrorRotate(self, flip=False, verbose=False):
        """Mirror the rotations from the current control to its mirror
        :param boolean restorePose: if the value from the pose node must be transfered on the control before the mirror
        :param boolean flip: the values are flipped and not mirrored
        :param boolean verbose: debug informations
        """
        axisTolerance = mc.tolerance(q=True, linear=True)
        mirror = self.getNode('mirror')
        cMirror = None
        if mc.objExists(mirror):
            cMirror = Control(mirror)

        mirrorType = self.mirrorType

        rotateSource = list(mc.getAttr(
            '{0}.rotate'.format(self.getControl()))[0])
        rotate = [.0, .0, .0]
        if cMirror:
            rotateOrder = mc.getAttr(
                '{0}.rotateOrder'.format(self.getControl()))
            rotateDest = list(mc.getAttr(
                '{0}.rotate'.format(cMirror.getControl()))[0])
            if mc.getAttr('{0}.rotateOrder'.format(cMirror.getControl()), se=True):
                mc.setAttr('{0}.rotateOrder'.format(
                    cMirror.getControl()), rotateOrder)
            else:
                mc.warning(
                    '[mirrorRotate] source and destination rotateOrders are different, unable to change rotate order destination')

            if mirrorType == 'joint':
                try:
                    rotate[0] = 1.0 * rotateSource[0]
                    rotate[1] = 1.0 * rotateSource[1]
                    rotate[2] = 1.0 * rotateSource[2]

                    mc.setAttr('{0}.rotate'.format(cMirror.getControl(
                    )), rotate[0], rotate[1], rotate[2], type='double3')
                    if flip:
                        rotate[0] = 1.0 * rotateDest[0]
                        rotate[1] = 1.0 * rotateDest[1]
                        rotate[2] = 1.0 * rotateDest[2]
                        mc.setAttr('{0}.rotate'.format(
                            self.getControl()), rotate[0], rotate[1], rotate[2], type='double3')
                except Exception:
                    pass

            elif mirrorType == 'transform':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                          axisTolerance):
                    mult = (1.0, -1.0, -1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    mult = (-1.0, 1.0, -1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    mult = (-1.0, -1.0, 1.0)

                try:
                    rotate[0] = mult[0] * rotateSource[0]
                    rotate[1] = mult[1] * rotateSource[1]
                    rotate[2] = mult[2] * rotateSource[2]
                    mc.setAttr('{0}.rotate'.format(cMirror.getControl(
                    )), rotate[0], rotate[1], rotate[2], type='double3')
                    if flip:
                        rotate[0] = mult[0] * rotateDest[0]
                        rotate[1] = mult[1] * rotateDest[1]
                        rotate[2] = mult[2] * rotateDest[2]
                        mc.setAttr('{0}.rotate'.format(
                            self.getControl()), rotate[0], rotate[1], rotate[2], type='double3')
                except Exception:
                    pass

            elif mirrorType == 'orientation':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                                                                   axisTolerance):
                    mult = (1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, 1.0, 1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    mult = (1.0, 1.0, 1.0)

                try:
                    rotate[0] = mult[0] * rotateSource[0]
                    rotate[1] = mult[1] * rotateSource[1]
                    rotate[2] = mult[2] * rotateSource[2]
                    mc.setAttr('{0}.rotate'.format(cMirror.getControl(
                    )), rotate[0], rotate[1], rotate[2], type='double3')
                    if flip:
                        rotate[0] = mult[0] * rotateDest[0]
                        rotate[1] = mult[1] * rotateDest[1]
                        rotate[2] = mult[2] * rotateDest[2]
                        mc.setAttr('{0}.rotate'.format(
                            self.getControl()), rotate[0], rotate[1], rotate[2], type='double3')
                except Exception:
                    pass

        # No mirror control found
        #
        else:
            if mirrorType != 'none':
                axis = readNodeAxis(self.getControl())
                rightAxis = axis[2]
                mult = (1.0, 1.0, 1.0)
                if rightAxis.isEquivalent(om.MVector.kXaxisVector,
                                          axisTolerance) or rightAxis.isEquivalent(om.MVector.kXnegAxisVector,
                                                                                   axisTolerance):
                    if not flip:
                        mult = (1.0, 0.0, 0.0)
                    else:
                        mult = (1.0, -1.0, -1.0)
                elif rightAxis.isEquivalent(om.MVector.kYaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kYnegAxisVector,
                                                                                     axisTolerance):
                    if not flip:
                        mult = (.0, 1.0, .0)
                    else:
                        mult = (-1.0, 1.0, -1.0)
                elif rightAxis.isEquivalent(om.MVector.kZaxisVector,
                                            axisTolerance) or rightAxis.isEquivalent(om.MVector.kZnegAxisVector,
                                                                                     axisTolerance):
                    if not flip:
                        mult = (0.0, 0.0, 1.0)
                    else:
                        mult = (-1.0, -1.0, 1.0)

                try:
                    rotate[0] = mult[0] * rotateSource[0]
                    rotate[1] = mult[1] * rotateSource[1]
                    rotate[2] = mult[2] * rotateSource[2]

                    mc.setAttr('{0}.rotate'.format(
                        self.getControl()), rotate[0], rotate[1], rotate[2], type='double3')
                except Exception:
                    pass

    def mirrorScale(self, flip=False, verbose=False):
        """Mirror the scale from the current control to its mirror
        :param boolean restorePose: if the value from the pose node must be transfered on the control before the mirror
        :param boolean flip: the values are flipped and not mirrored
        :param boolean verbose: debug informations
        """
        mirror = self.getNode('mirror')
        cMirror = None
        if mc.objExists(mirror):
            cMirror = Control(mirror)

        scaleSource = list(mc.getAttr(
            '{0}.scale'.format(self.getControl()))[0])
        scale = [1.0, 1.0, 1.0]
        if cMirror:
            scaleDest = list(mc.getAttr(
                '{0}.scale'.format(cMirror.getControl()))[0])
            try:
                scale[0] = 1.0 * scaleSource[0]
                scale[1] = 1.0 * scaleSource[1]
                scale[2] = 1.0 * scaleSource[2]

                mc.setAttr('{0}.scale'.format(cMirror.getControl()),
                           scale[0], scale[1], scale[2], type='double3')
                if flip:
                    scale[0] = 1.0 * scaleDest[0]
                    scale[1] = 1.0 * scaleDest[1]
                    scale[2] = 1.0 * scaleDest[2]
                    mc.setAttr('{0}.scale'.format(self.getControl()),
                               scale[0], scale[1], scale[2], type='double3')
            except Exception:
                pass

    def mirrorPose(self, restorePose=False, flip=False, verbose=False):
        """Mirror the pose from the current control to its mirror, if the control is on the middle, the mirror is applied inplace
        :param boolean restorePose: if the value from the pose node must be transfered on the control before the mirror
        :param boolean flip: the values are flipped and not mirrored
        :param boolean verbose: debug informations
        """
        mirror = self.getNode('mirror')
        cMirror = None
        if mc.objExists(mirror):
            cMirror = Control(mirror)

        if restorePose:
            self.poseToControl()
            if cMirror:
                cMirror.poseToControl()

        self.mirrorTranslate(flip, verbose)
        self.mirrorRotate(flip, verbose)
        self.mirrorScale(flip, verbose)

    def isDynamicControl(self):
        """
        Check if a control is a control with a dynamique rig attached
        :rtyp: boolean
        """
        isDyn = False
        if mc.objExists(self.control):
            dyn = self.getNode('dyn')
            if mc.objExists(dyn):
                isDyn = True

        return isDyn

    def displayHandle(self, state=True):
        """
        Display the handle of the control
        :param state: True, displayed
        """
        if mc.objExists(self.control):
            plug = '{0}.displayHandle'.format(self.control)
            if mc.getAttr(plug, settable=True):
                try:
                    mc.setAttr(plug, state)
                except Exception:
                    pass

    def displaySk(self, state=True):
        """
        Display the sk of the control
        :param state: True, displayed
        """
        if mc.objExists(self.control):
            sk = self.getNode('sk')
            if mc.objExists(sk):
                if state:
                    setJointDrawStyle(sk, drawStyle='Bone')
                else:
                    setJointDrawStyle(sk, drawStyle='None')


def getSceneControlGroups():
    '''
    Get all the control groups in a scene
    '''
    controlGroups = []
    networks = mc.ls(type='network') or []
    if networks:
        for i, network in enumerate(networks):  # @UnusedVariable
            if ObjectType(network).isOfType('controlGroup'):
                controlGroups.append(ControlGroup(network))

    return controlGroups


# # ------------------------------------ CG ------------------------------------ # #


def isControlObjectInList(controlObject, controlList=()):
    """Check if the object Control is in a list
    :param Control c : control to check
    :param list controlList: list of Control objects
    :rtype: boolean
    """
    isControlInList = False
    if isinstance(controlObject, (ControlTemplate, ControlGroup, Control)) and hasattr(controlObject, 'apiObject'):
        for ctrl in controlList:
            if isinstance(ctrl, (ControlTemplate, ControlGroup, Control)) and hasattr(ctrl, 'apiObject'):
                if ctrl.apiObject == controlObject.apiObject:  # already stored
                    isControlInList = True
                    break
    else:
        raise ValueError('[isControlObjectInList] Invalid Control supplied')

    return isControlInList


def isControlGroupExists(cgName):
    '''
    Verify if in a Maya scene, a control group already exists
    '''
    exists = False
    networks = mc.ls(type='network') or []
    if networks:
        for i, network in enumerate(networks):  # @UnusedVariable i
            if ObjectType(network).isOfType('controlGroup'):
                otherCgName = ControlGroup(network).name
                if otherCgName == cgName:
                    exists = True
                    break

    return exists


def isControlGroup(cg):
    '''
    Test if the supplied node is a control group
    '''
    isControlGroup = False
    if mc.objExists(cg) and ObjectType(cg).isOfType('controlGroup'):
        isControlGroup = True

    return isControlGroup


def objectSetToControlGroup(objectSet):
    """From an objectSet, will return the associated controlGroup
    :param str objectSet: Maya objectSet
    :return: The found ControlGroup
    :rtype: ControlGroup, None if not found
    """
    cg = None
    if mc.objExists(objectSet) and mc.objectType(objectSet, isAType='objectSet'):
        outCx = mc.connectionInfo('{0}.message'.format(objectSet), dfs=True) or []
        if outCx:
            for cx in outCx:
                node = nodeFromPlug(cx)
                if ObjectType(node).isOfType('controlGroup'):
                    cg = ControlGroup(node)
                    break

    return cg


class ControlGroup(object):
    """"Class to handle the control groups
    """

    def __init__(self, obj, doCtrlSet=True, doSkinSet=True, splittable=False, splitted=False):
        '''
        Constructor create the default attributes or retreive them is the object has already been templated
        '''
        self.apiObject = None
        self.controlGroup = ''
        self.name = ''
        self.tplGroup = ''
        self.rigGroup = ''
        self.splittable = splittable
        self.splitted = splitted
        self.ctrlSet = ''
        self.skinSet = ''
        self.members = []
        self.templates = []
        self.parent = None
        self.children = []
        self.membersVisibility = True
        self.doCtrlSet = doCtrlSet
        self.doSkinSet = doSkinSet
        self.camPanels = []

        nameParser = NameParser(obj)
        self.name = nameParser.getBaseName()

        suffix = nameParser.getNameSuffix()

        if suffix:
            self.name += nameParser.getTokensSeparator() + suffix
        if not mc.objExists(obj):
            controlGroupName = 'cg_{}'.format(self.name)
            if mc.objExists(controlGroupName):
                mc.warning('[ControlGroup] The control group node {} already exists'.format(
                    controlGroupName))
                return
            self.controlGroup = mc.createNode('network', name=controlGroupName,
                                              skipSelect=True)
            self.apiObject = getMObject(self.controlGroup)

            objType = ObjectType(self.controlGroup)
            objType.setRigNodeType('controlGroup', lockIt=True)

            # add an attribute for the name
            #
            mc.addAttr(self.controlGroup, ln='name', dt='string')
            mc.setAttr('{}.name'.format(self.controlGroup),
                       self.name, type='string', lock=True)
            # Create the attribute to connect the nsTpl root group
            #
            mc.addAttr(self.controlGroup, ln='tplGroup', at='message')
            # Create the attribute to connect the rig root group
            #
            mc.addAttr(self.controlGroup, ln='rigGroup', at='message')
            # Create the attribute to specify if this controlGroup is splitted, left and right side will be in two differents child controlGroup
            #

            if splittable:
                mc.addAttr(self.controlGroup, ln='splitted', at='bool')
                mc.setAttr('{}.splitted'.format(self.controlGroup),
                           keyable=True, channelBox=True)
            # Create the attribute to specify if this controlGroup has a controlSet
            #
            mc.addAttr(self.controlGroup, ln='doCtrlSet',
                       at='bool', dv=self.doCtrlSet)
            mc.setAttr('{}.doCtrlSet'.format(self.controlGroup),
                       keyable=True, channelBox=True)

            # Create the attribute to connect the ctrl objectSet to this controlGroup
            #
            mc.addAttr(self.controlGroup, ln='ctrlSet', at='message')

            # Create the attribute to specify if this controlGroup has a skinSet
            #
            mc.addAttr(self.controlGroup, ln='doSkinSet',
                       at='bool', dv=self.doSkinSet)
            mc.setAttr('{}.doSkinSet'.format(self.controlGroup),
                       keyable=True, channelBox=True)

            # Create the attribute to connect if this controlGroup to the skin objectSet
            #
            mc.addAttr(self.controlGroup, ln='skinSet', at='message')

            # Creation of the attributes to stock the members of the controlGroup
            #
            mc.addAttr(self.controlGroup, ln='members',
                       multi=True, at='message')

            # Create the attribute to connect the templates object to this controlGroup size will be equal to members
            #
            mc.addAttr(self.controlGroup, ln='templates',
                       multi=True, at='message')

            # Creation of the attributes to stock the parents (other controlGroups) of the controlGroup
            #
            mc.addAttr(self.controlGroup, ln='parent', at='message')

            # Creation of the attributes to stock the children (other controlGroups) of the controlGroup
            #
            mc.addAttr(self.controlGroup, ln='children',
                       multi=True, at='message')

            # Creation of the attributes to stock the cam panels associated with this control group
            #
            mc.addAttr(self.controlGroup, ln='camPanels',
                       multi=True, at='message')

            # Create the attribute to drive the visibility of the members
            #
            mc.addAttr(self.controlGroup, ln='membersVisibility',
                       at='bool', dv=self.membersVisibility)
            mc.setAttr('{}.membersVisibility'.format(self.controlGroup),
                       self.membersVisibility, keyable=True, channelBox=True)

            # Update the control sets
            #
            mc.namespace(set=':')
            self.updateControlGroupSet('all')

            # lock the node to avoid its destruction by Maya if there isn't input or output connections anymore
            #
            mc.lockNode(self.controlGroup, lock=True)

            if self.splittable and self.splitted:
                self.splitCg()

        else:
            if ObjectType(obj).isOfType('controlGroup'):
                self.controlGroup = obj
                self.updateControlGroup()
            else:
                raise ValueError(
                    '[ControlGroup] The supplied object {} exists, but is not a controlGroup'.format(obj))

    def __str__(self):
        '''
        Method used to print usefull information about the class
        '''
        return ('{}'.format(self.controlGroup))

    def updateControlGroup(self):
        '''
        '''
        success = False
        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[updateControlGroup] The controlGroup {} does not exist anymore'.format(self.controlGroup))
        try:
            self.apiObject = getMObject(self.controlGroup)
            self.name = mc.getAttr('{}.name'.format(self.controlGroup))
            self.updateParent()
            self.updateChildren()
            self.doCtrlSet = mc.getAttr(
                '{}.doCtrlSet'.format(self.controlGroup))
            self.doSkinSet = mc.getAttr(
                '{}.doSkinSet'.format(self.controlGroup))
            # add to have the possibility to split a cg
            #
            self.splitted = False
            if mc.attributeQuery('splitted', node=self.controlGroup, exists=True):
                self.splitted = mc.getAttr(
                    '{}.splitted'.format(self.controlGroup))
            self.updateControlGroupSet('all')
            self.tplGroup = self.getTplGroup()
            self.rigGroup = self.getRigGroup()
            self.ctrlSet = self.getControlSet('ctrlSet')
            self.skinSet = self.getControlSet('skinSet')
            self.membersVisibility = mc.getAttr(
                '{}.membersVisibility'.format(self.controlGroup))
            self.cleanUpMembers('all')  # update the nsTpl and members too

            if self.splittable and self.splittable:
                self.updateSplits()

            success = True

        except Exception:
            raise

        return success

    def getSplits(self):
        """
        Return the splits of the cg
        rtyp list: the list of splits (maya network nodetype)
        """
        splits = []
        if not mc.objExists(self.controlGroup):
            return splits
        outMessages = mc.connectionInfo('{}.message'.format(self.controlGroup),
                                        dfs=True) or []
        if not outMessages:
            return splits

        for outMessage in outMessages:
            attr = attributeFromPlug(outMessage)
            if attr == 'split':
                split = nodeFromPlug(outMessage)
                splits.append(split)

        return splits

    def getSplitLocation(self):
        """
        Get the location of the split if the control group is splitted
        :return: the location
        :rtyp str
        """
        splitLocation = ''
        if self.isCgASplit():
            splitSuffix = NameParser(self.controlGroup).getNameSuffix()
            if isValidSuffixLocation(splitSuffix):
                splitLocation = suffixToLocation(splitSuffix)

        return splitLocation

    def updateSplits(self):
        """
        Update the content of the different splits
        """
        if not self.isCgSplitted():
            return
            # print 'Update splitted cg:', self.controlGroup

        splits = self.getSplits()
        if not splits:
            return

        self.updateMembers()
        self.clearSplits()
        for split in splits:
            splitSuffix = NameParser(split).getNameSuffix()
            if not isValidSuffixLocation(splitSuffix):
                continue
            splitLocation = suffixToLocation(splitSuffix)
            cgSplit = ControlGroup(split)
            for member in self.members:
                memberSuffix = NameParser(member).getNameSuffix()
                if not isValidSuffixLocation(memberSuffix):
                    continue

                memberLocation = suffixToLocation(memberSuffix)
                if memberLocation != splitLocation:
                    continue

                cgSplit.addControl(member)
                root = Control(member).getNode('root')
                if mc.objExists(root):
                    insertMultDoubleLinear('{}.membersVisibility'.format(
                        split), 1.0, '{}.visibility'.format(root), side=1)

    def clearSplits(self):
        """
        Clear the content of the splits
        """
        if self.isCgSplitted():
            # print 'Clear splits of cg:', self.controlGroup
            splits = self.getSplits()
            if splits:
                for split in splits:
                    cgSplit = ControlGroup(split)
                    controlGroup = cgSplit.getControlGroup()
                    indices = mc.getAttr('{}.members'.format(
                        controlGroup), multiIndices=True) or []
                    for index in indices:
                        mc.removeMultiInstance('{}.members[{1}]'.format(controlGroup, index),
                                               b=True)
                        # cgSplit.removeMember(member, below=True, deleteMember=False, removeTemplate=False, progressBar=None)

    def splitCg(self):
        """
        Split the control group in two sub control groups left and right
        :return list: the two new sub cg
        """
        createdControlGroups = []
        if self.isCgSplitted() or not self.isCgSplittable():
            return createdControlGroups
            # print 'split cg:', self.controlGroup
        if mc.referenceQuery(self.controlGroup, isNodeReferenced=True):
            raise RuntimeError(
                '[splitCg] the control group {} is referenced, unable to unsplit a reference node'.format(self.controlGroup))

        leftLocation = ControlTemplate.validLocationsSuffixes[1]
        rightLocation = ControlTemplate.validLocationsSuffixes[2]

        splits = self.getSplits()
        if not splits:
            splitsLocations = [leftLocation, rightLocation]
            for splitsLocation in splitsLocations:
                # contruction of the two sub cg names
                #
                cgName = self.name + splitsLocation
                if isControlGroupExists(cgName):
                    raise RuntimeError('[splitCg] A control group named {} already exists in the scene'.format(cgName))

                cg = ControlGroup(
                    cgName, doCtrlSet=False, doSkinSet=False, splitted=False, splittable=False)
                cg.parentCgTo(self)
                controlGroup = cg.getControlGroup()
                if mc.lockNode(controlGroup, query=True, lock=True)[0] is True:
                    mc.lockNode(controlGroup, lock=False)
                mc.addAttr(controlGroup, hidden=True,
                           ln='split', at='message')
                mc.connectAttr(
                    self.controlGroup + '.message', controlGroup + '.split', force=True)
                mc.lockNode(controlGroup, lock=True)
                createdControlGroups.append(controlGroup)

        else:
            for split in splits:
                controlGroup = ControlGroup(split).getControlGroup()
                createdControlGroups.append(controlGroup)

        self.splitted = True
        mc.setAttr('{}.splitted'.format(
            self.controlGroup), self.splitted)
        self.updateSplits()

        return createdControlGroups

    def unsplitCg(self):
        """
        Unsplit a control group (delete the sub cg
        :rrtyp list of removed cg
        """
        deletedControlGroups = []
        if not self.isCgSplitted() or not self.isCgSplittable:
            return deletedControlGroups

        if mc.referenceQuery(self.controlGroup, isNodeReferenced=True):
            raise RuntimeError('[unsplitCg] the control group {} is referenced, unable to unsplit a reference node'.format(self.controlGroup))

        splits = self.getSplits()
        for split in splits:
            cgSplit = ControlGroup(split)
            cgToReparents = cgSplit.listRelativesCg(c=True)
            if cgToReparents:
                for cgToReparent in cgToReparents:
                    cgToReparent.parentCgTo(self)

            if mc.lockNode(split, query=True, lock=True)[0] is True:
                mc.lockNode(split, lock=False)

            cgSplit.doCtrlSet = False
            cgSplit.doSkinSet = False
            cgSplit.updateControlGroupSet()  # Remove the control and skin sets

            mc.delete(split)

            deletedControlGroups.append(split)

        self.splitted = False
        mc.setAttr('{}.splitted'.format(self.controlGroup),
                   self.splitted)
        self.updateControlGroup()

        for member in self.members:
            root = Control(member).getNode('root')
            if mc.objExists(root):
                multdoubleLinear = getFirstTypedConnected('multDoubleLinear', '{}.visibility'.format(
                    root), returnPlug=False, source=True, destination=False, depth=1, verbose=False)
                if not mc.isConnected('{}.membersVisibility'.format(self.controlGroup), '{}.visibility'.format(root)):
                    if mc.getAttr('{}.visibility'.format(root), lock=True):
                        mc.setAttr(
                            '{}.visibility'.format(root), lock=False)
                    mc.connectAttr('{}.membersVisibility'.format(
                        self.controlGroup), '{}.visibility'.format(root), force=True)
                if mc.objExists(multdoubleLinear):
                    mc.delete(multdoubleLinear)

        return deletedControlGroups

    def isCgSplitted(self):
        """
        Check if the current cg is splitted
        :rtyp bool:
        """
        if not mc.objExists(self.controlGroup):
            return False

        if mc.attributeQuery('splitted', node=self.controlGroup, exists=True):
            self.splitted = mc.getAttr('{}.splitted'.format(self.controlGroup))
            return self.splitted

        return False

    def isCgASplit(self):
        """
        Check if the current cg is a split
        :rtyp bool:
        """
        if mc.objExists(self.controlGroup):
            if mc.attributeQuery('split', node=self.controlGroup, exists=True):
                return True

        return False

    def isCgSplittable(self):
        """
        Check if a cg is splittable
        :rtyp: boolean
        """
        isSplittable = False
        if mc.objExists(self.controlGroup):
            if mc.attributeQuery('splitted', node=self.controlGroup, exists=True):
                self.splittable = isSplittable = True

        return isSplittable

    def updateMembers(self):
        '''
        Update the controlGroup class members list
        '''
        if mc.objExists(self.controlGroup):
            self.members = mc.listConnections('{}.members'.format(
                self.controlGroup), sh=True, source=True) or []
        else:
            raise RuntimeError(
                '[updateMembers] The controlGroup {} does not exist anymore'.format(self.controlGroup))

    def updateTemplates(self):
        """Update the controlGroup class templates list
        """
        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[updateTemplates] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        self.templates = mc.listConnections(
            '{}.templates'.format(self.controlGroup), source=True) or []

        if not self.templates:
            return

        self.tplGroup = self.getTplGroup()
        if not mc.objExists(self.tplGroup):
            self.tplGroup = self.createTplGroup()

        roots = []
        for template in self.templates:
            templateRoot = getHierarchyRoot(template, '', True)
            if not any([templateRoot in roots, templateRoot == self.tplGroup, isParentOf(templateRoot, self.tplGroup)]):
                roots.append(templateRoot)

        for root in roots:
            if isParentOf(self.tplGroup, root):
                continue
            mc.parent(root, self.tplGroup)

        return

    def getTemplates(self):
        """Return all the templates connected to the controlGroup
        :return: the templates connected
        :rtype: list of Maya dags
        """
        self.updateTemplates()  # To be sur that the controlGroup is up to date
        return self.templates

    def getMembers(self):
        """Return all the members connected to the controlGroup
        :return: the members connected
        :rtype: list of Maya dags
        """
        self.updateMembers()  # To be sur that the controlGroup is up to date
        return self.members

    def isChildOf(self, parentCg):
        '''
        Check if a control group is already a child of parentCg
        '''
        isChildOf = False
        if not mc.objExists(parentCg) or not ObjectType(parentCg).isOfType('controlGroup'):
            return isChildOf

        if not mc.attributeQuery('parent', node=self.controlGroup, exists=True):
            return isChildOf

        parents = mc.listConnections('{}.parent'.format(
            self.controlGroup), source=True) or []

        for parent in parents:
            node = nodeFromPlug(parent)
            if not ObjectType(node).isOfType('controlGroup'):
                continue

            cg = ControlGroup(node)
            cgName = cg.getControlGroupName()
            if cgName == parentCg.getControlName():
                isChildOf = True
                break

        return isChildOf

    def isInDescendants(self, otherCg):
        '''
        Test if a control group is in the descendants of the current cg
        '''
        isInDescendants = False
        cgAllDescendants = self.listRelativesCg(ad=True)
        for cg in cgAllDescendants:
            if cg.getControlGroup() == otherCg.getControlGroup():
                isInDescendants = True

        return isInDescendants

    def isInParents(self, otherCg):
        '''
        Test if a control group is in the parents of the current cg
        '''
        isInParents = False
        cgAllParents = self.listRelativesCg(ap=True)
        for cg in cgAllParents:
            if cg.getControlGroup() != otherCg.getControlGroup():
                continue

            isInParents = True

        return isInParents

    def isCgParentOf(self, childCg):
        '''
        Check if a control group is already a parent of childCg
        '''
        isCgParentOf = False
        if not mc.objExists(childCg) or not ObjectType(childCg).isOfType('controlGroup'):
            return isCgParentOf

        if not mc.attributeQuery('children', node=self.controlGroup, exists=True):
            return isCgParentOf

        children = mc.listConnections('{}.children'.format(
            self.controlGroup), destination=True) or []
        for child in children:
            node = nodeFromPlug(child)
            if not ObjectType(node).isOfType('controlGroup'):
                continue

            cg = ControlGroup(node)
            cgName = cg.getControlGroupName()
            if cgName == childCg.getControlGroupName():
                isCgParentOf = True
                break

        return isCgParentOf

    def parentCgTo(self, cgParent=None):
        """Parent a controlGroup to another controlGroup
        :param controlGroup cgParent: the future parent controlGroup
        :raises: RuntimeError Invalid parameter cgParent
        :TODO: Debug if a cg with sets is parented to a cg without sets, and the last one already parented to a cg with sets,
        the sets of the first one are not reparented
        """
        if self.isCgASplit():
            raise RuntimeError(
                "[parentCgTo] The node {} is a cg split, and can't be parented".format(self.controlGroup))

        if not cgParent or not isControlGroup(cgParent):
            raise RuntimeError('[parentCgTo] Invalid parameter {}'.format(cgParent))

        if not cgParent:
            self.unparentCg()
            return

        # Check if cgParent is not a child of self
        if self.isInDescendants(cgParent):
            mc.warning('[parentCgTo] Control group {0} is a descendant of control group {1}'.format(cgParent.controlGroup,
                                                                                                    self.controlGroup))
            return

        self.unparentCg()
        parentPlug = '{}.parent'.format(self.controlGroup)
        attribute = 'children'
        parentControlGroup = cgParent.getControlGroup()
        idx = getMultiFirstAvailableIndex(parentControlGroup,
                                          attribute)
        newChildPlug = '{0}.children[{1}]'.format(parentControlGroup,
                                                  idx)
        mc.connectAttr(newChildPlug, parentPlug, force=True)

        # Now handle the control sets
        #
        objectSetTypes = ['ctrlSet', 'skinSet']
        for setType in objectSetTypes:
            objectSet = self.getControlSet(setType)
            otherSet = self.getFirstParentCreatedSet(setType)
            if mc.objExists(objectSet):
                if mc.objExists(otherSet):
                    addToSets(objectSet, otherSet, exclusive=True)
            else:
                members = self.getMembers()
                if not members:
                    continue
                for member in members:
                    if setType == 'skinSet':
                        sk = Control(member).getNode('sk')
                        # the case of a custom control without nsTpl for example
                        if not mc.objExists(sk):
                            continue
                        else:
                            addToSets(sk, otherSet,
                                      exclusive=True)

                    elif setType == 'ctrlSet':
                        addToSets(member, otherSet,
                                  exclusive=True)

            self.updateParent()
        return

    def unparentCg(self):
        '''
        Unparent a control group
        '''
        if self.isCgASplit():
            raise RuntimeError(
                "[unparentCg] The node {} is a cg split, and can't be parented".format(self.controlGroup))

        parentPlug = '{}.parent'.format(self.controlGroup)
        if not isPlugConnected(parentPlug, side=0):
            return

        childPlug = mc.connectionInfo(parentPlug, sfd=True)
        parentControlGroup = nodeFromPlug(childPlug)
        mc.disconnectAttr(childPlug, parentPlug)
        mc.removeMultiInstance(childPlug, b=True)

        # Now handle the control set
        #
        objectSetTypes = ['ctrlSet', 'skinSet']
        for setType in objectSetTypes:
            objectSet = self.getControlSet(setType)
            if mc.objExists(objectSet):
                removeFromSets(objectSet)
                continue

            members = self.getMembers()
            if not members:
                continue

            for member in members:
                if setType not in ['skinSet', 'ctrlSet']:
                    continue

                if setType == 'skinSet':
                    sk = Control(member).getNode('sk')

                    if not mc.objExists(sk):
                        continue
                    removeFromSets(sk)
                    continue

                removeFromSets(member)

        # Now handle the visibility of the children member visibility
        #
        if not mc.attributeQuery('membersVisibility', node=self.controlGroup,
                                 exists=True) or not mc.attributeQuery('membersVisibility',
                                                                       node=parentControlGroup,
                                                                       exists=True):
            return

        if mc.isConnected('{}.membersVisibility'.format(parentControlGroup),
                          '{}.membersVisibility'.format(self.controlGroup),
                          ignoreUnitConversion=True):
            mc.disconnectAttr('{}.membersVisibility'.format(parentControlGroup),
                              '{}.membersVisibility'.format(self.controlGroup))

        return

    def listRelativesCg(self, **kwargs):
        """List all relatives to a control group
        :param  boolean children/c        : children of cg
        :param  boolean parent/p          : parent of cg
        :param  boolean allParents/ap     : all parents of cg
        :param  boolean allDescendants/ad : all descendants of cg
        :param  boolean siblings/s        : siblings of cg
        """
        result = None
        validsArgs = ['children', 'c', 'parent', 'p', 'allParents',
                      'ap', 'allDescendants', 'ad', 'siblings', 's']
        for arg, value in kwargs.iteritems():
            if arg not in validsArgs:
                raise ValueError('[listRelativesCg] Invalid argument/value {0} {1}'.format(arg, value))

        if len(kwargs) > 1:
            raise ValueError('[listRelativesCg] The argument "children/c", "parent/p", "allParents/ap", "allDescendants/ad" and "siblings/s" are mutualy exclusive')

        if 'children' in kwargs or 'c' in kwargs:
            if kwargs.get('children') or kwargs.get('c'):
                nodes = mc.listConnections('{}.children'.format(
                    self.controlGroup), destination=True) or []
                result = []
                for node in nodes:
                    result.append(ControlGroup(node))
        elif 'parent' in kwargs or 'p' in kwargs:
            if kwargs.get('parent') or kwargs.get('p'):
                nodes = mc.listConnections('{}.parent'.format(
                    self.controlGroup), source=True) or []
                result = []
                for node in nodes:
                    result.append(ControlGroup(node))
        elif 'siblings' in kwargs or 's' in kwargs:
            if kwargs.get('siblings') or kwargs.get('s'):
                result = []
                cgParents = self.listRelativesCg(parent=True)
                if cgParents:
                    cgChildren = cgParents[0].listRelativesCg(children=True)
                    for cgChild in cgChildren:
                        if cgChild.controlGroup != self.controlGroup:
                            result.append(cgChild)
                else:  # All the controlGroups without parents are a sibling
                    cgAll = getSceneControlGroups()
                    for cg in cgAll:
                        if cg.controlGroup != self.controlGroup:
                            cgParents = cg.listRelativesCg(parent=True)
                            if not cgParents:
                                result.append(cg)
        elif 'allParents' in kwargs or 'ap' in kwargs:
            if kwargs.get('allParents') or kwargs.get('ap'):
                result = []
                cgParents = self.listRelativesCg(parent=True)
                for cgParent in cgParents:
                    result.append(cgParent)
                    result += cgParent.listRelativesCg(ap=True)
        elif 'allDescendants' in kwargs or 'ad' in kwargs:
            if kwargs.get('allDescendants') or kwargs.get('ad'):
                result = []
                cgChildren = self.listRelativesCg(children=True)
                for cgChild in cgChildren:
                    # print cgChild
                    result.append(cgChild)
                    result += cgChild.listRelativesCg(ad=True)

        return result

    def getControlGroupDepth(self):
        '''
        Get the depth of a control group in a hierarchy
        '''
        depth = 0

        cgParents = self.listRelativesCg(p=True)
        while cgParents:
            cgParent = cgParents[0]
            depth += 1
            cgParents = cgParent.listRelativesCg(p=True)

        return depth

    def getControlGroupRoot(self):
        '''
        Get the upper controlGroup node in a hierarchy
        '''
        root = ''
        result = self.listRelativesCg(ap=True)
        if result:
            root = result[-1]

        return root

    def updateParent(self):
        '''
        update the controlGroup class parent
        '''
        if mc.objExists(self.controlGroup):
            parents = mc.listConnections('{}.parent'.format(
                self.controlGroup), source=True) or []
            if parents:
                self.parent = parents[0]
            else:
                self.parent = None
        else:
            raise RuntimeError(
                '[updateParent] The controlGroup {} does not exist anymore'.format(self.controlGroup))

    def updateChildren(self):
        '''
        update the controlGroup class children list
        '''
        if mc.objExists(self.controlGroup):
            self.children = mc.listConnections(
                '{}.children'.format(self.controlGroup), destination=True) or []
        else:
            raise RuntimeError(
                '[updateChildren] The controlGroup {} does not exist anymore'.format(self.controlGroup))

    def getControlGroupName(self):
        """get the short name of the controlGroup
        :rtype: Maya dag node
        """
        controlGroupName = ''
        if mc.objExists(self.controlGroup):
            controlGroupName = mc.getAttr(
                '{}.name'.format(self.controlGroup))
        else:
            raise RuntimeError(
                '[getControlGroupName] The controlGroup {} does not exist anymore'.format(self.controlGroup))
        return controlGroupName

    def getControlGroup(self):
        """get the Maya node scene name of the controlGroup
        """
        controlGroup = ''
        if mc.objExists(self.controlGroup):
            controlGroup = self.controlGroup
        else:
            raise RuntimeError(
                '[getControlGroup] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        return controlGroup

    def createTplGroup(self):
        '''
        Method to create the tpl group is it not exists
        '''
        name = self.getControlGroupName()
        self.tplGroup = mc.createNode(
            'transform', name='tpl_{}'.format(name))
        mc.connectAttr('{}.message'.format(self.tplGroup),
                         '{}.tplGroup'.format(self.controlGroup))
        return self.tplGroup

    def getTplGroup(self):
        '''
        Try to retreive the group where the nsTpl is store
        '''
        # test the validity of the inputs
        #
        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[getTplGroup] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        self.tplGroup = mc.connectionInfo('{}.tplGroup'.format(self.controlGroup),
                                          sfd=True)
        if mc.objExists(self.tplGroup):
            # Retreive the node, not the plug
            self.tplGroup = self.tplGroup.split('.')[0]
            return self.tplGroup

        if not self.templates:
            return self.tplGroup

        name = self.getControlGroupName()
        match = getFirstTransformMatch(self.templates[0], 'tpl_{}'.format(
            name), nodeType='transform', relatives='parent')
        if not match:
            return self.tplGroup

        self.tplGroup = match
        try:
            mc.connectAttr('{}.message'.format(
                self.tplGroup), '{}.tplGroup'.format(self.controlGroup))
        except Exception:
            raise

        return self.tplGroup

    def createRigGroup(self):
        '''
        Method to create the rig group is it not exists
        '''
        name = self.getControlGroupName()
        self.rigGroup = mc.createNode(
            'transform', name='rig_{}'.format(name))
        mc.connectAttr('{}.message'.format(self.rigGroup),
                         '{}.rigGroup'.format(self.controlGroup))
        return self.rigGroup

    def setRigGroup(self, rigGroup, force=False):
        '''
        Method to set the rig group
        '''
        if mc.objExists(rigGroup) and mc.objectType(rigGroup, isAType='transform'):
            if isPlugConnected('{}.rigGroup'.format(self.controlGroup), 0) and not force:
                mc.warning('[setRigGroup] There is already a rig group {} connected to the controlGroup {1}, use force parameter to force the connection'.format(self.getRigGroup(),
                                                                                                                                                                 self.controlGroup))
                return ''

            mc.connectAttr('{}.message'.format(
                rigGroup), '{}.rigGroup'.format(self.controlGroup), force=force)
            self.rigGroup = rigGroup

        return self.rigGroup

    def getRigGroup(self):
        '''
        Try to retreive the group where the rig is store
        '''
        # test the validity of the inputs
        #
        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[getRigGroup] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        self.rigGroup = mc.connectionInfo('{}.rigGroup'.format(self.controlGroup),
                                          sfd=True)
        if mc.objExists(self.rigGroup):
            self.rigGroup = self.rigGroup.split('.')[0]
            return self.rigGroup

        if not len(self.members):
            return self.rigGroup

        name = self.getControlGroupName()
        match = getFirstTransformMatch(self.members[0], 'rig_{}'.format(
            name), nodeType='transform', relatives='parent')

        if match:
            self.rigGroup = match
            try:
                mc.connectAttr('{}.message'.format(
                    self.rigGroup), '{}.rigGroup'.format(self.controlGroup))
            except Exception:
                raise

        return self.rigGroup

    def getControlSet(self, objectSetType):
        '''
        '''
        objectSet = ''
        validObjectSetType = ['ctrlSet', 'skinSet']
        # test the validity of the inputs
        #
        if not isinstance(objectSetType, str) or objectSetType not in validObjectSetType:
            raise ValueError('[getControlSet] Invalid object type supplied: {}'.format(objectSetType))

        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[getControlSet] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        if objectSetType == 'ctrlSet':
            inCx = mc.connectionInfo(
                '{}.ctrlSet'.format(self.controlGroup), sfd=True)
            if mc.objExists(inCx):
                objectSet = inCx.split('.')[0]
        elif objectSetType == 'skinSet':
            inCx = mc.connectionInfo(
                '{}.skinSet'.format(self.controlGroup), sfd=True)
            if mc.objExists(inCx):
                objectSet = inCx.split('.')[0]

        return objectSet

    def updateSetsMembers(self, objectSetType='all'):
        '''
        Update the skin or control set of the controlGroup
        '''
        validObjectSetType = ['ctrlSet', 'skinSet', 'all']
        if isinstance(objectSetType, str) and objectSetType in validObjectSetType:
            self.updateMembers()
            if len(self.members):
                for member in self.members:
                    template = Control(member).getNode('nsTpl')
                    if mc.objExists(template):
                        if objectSetType == 'ctrlSet' or objectSetType == 'all':
                            if ControlTemplate(template).addToCtrlSet is True and mc.objExists(self.ctrlSet) and not mc.sets(member, isMember=self.ctrlSet):
                                removeFromSets(member)
                                mc.sets(member, forceElement=self.ctrlSet)
                            elif ControlTemplate(template).addToCtrlSet is False and mc.objExists(self.ctrlSet) and mc.sets(member, isMember=self.ctrlSet):
                                mc.sets(member, remove=self.ctrlSet)
                        if objectSetType == 'skinSet' or objectSetType == 'all':
                            sk = Control(member).getNode('sk')
                            if mc.objExists(sk):
                                if ControlTemplate(template).addToSkinSet is True and mc.objExists(self.skinSet) and not mc.sets(sk, isMember=self.skinSet):
                                    removeFromSets(sk)
                                    mc.sets(sk, forceElement=self.skinSet)
                                elif ControlTemplate(template).addToSkinSet is False and mc.objExists(self.skinSet) and mc.sets(sk, isMember=self.skinSet):
                                    mc.sets(sk, remove=self.skinSet)

                    else:
                        # mc.warning('[updateSetsMembers] Unable to find the nsTpl for member {0}'.format(member))
                        if objectSetType == 'ctrlSet' or objectSetType == 'all':
                            if mc.objExists(self.ctrlSet) and not mc.sets(member, isMember=self.ctrlSet):
                                mc.sets(member, forceElement=self.ctrlSet)
                        if objectSetType == 'skinSet' or objectSetType == 'all':
                            sk = Control(member).getNode('sk')
                            if mc.objExists(sk):
                                if mc.objExists(self.skinSet) and not mc.sets(sk, isMember=self.skinSet):
                                    mc.sets(sk, forceElement=self.skinSet)

    def getFirstParentCreatedSet(self, objectSetType):
        """From a control group, go up the virtual hierarchy to find the first created objectSet
        :param str objectSetType: the type of objectSet, can be 'crtlSet' or 'skinSet'
        :return: Maya objectSet
        :rtype: str
        """
        cgAllParents = self.listRelativesCg(ap=True)
        for cgParent in cgAllParents:
            objectSet = cgParent.getControlSet(objectSetType)
            if mc.objExists(objectSet):
                return objectSet

        return ''

    def getAllParentCreatedSet(self, objectSetType):
        """From a control group, go up the virtual hierarchy to find all the created objectSets
        :param str objectSetType: the type of objectSet, can be 'crtlSet' or 'skinSet'
        :return: [Maya objectSet...]
        :rtype: list
        """
        allParentCreatedSet = []
        cgAllParents = self.listRelativesCg(ap=True)
        for cgParent in cgAllParents:
            objectSet = cgParent.getControlSet(objectSetType)
            if mc.objExists(objectSet):
                allParentCreatedSet.append(objectSet)

        return allParentCreatedSet

    def getFirstChildrenCreatedSet(self, objectSetType):
        """From a control group, go down the virtual hierarchy to find the children created objectSet
        :param str objectSetType: the type of objectSet, can be 'crtlSet' or 'skinSet'
        :return: [Maya objectSets...]
        :rtype: list
        """
        objectSets = []
        cgAllDescendants = self.listRelativesCg(ad=True)
        for cgDescendant in cgAllDescendants:
            objectSet = cgDescendant.getControlSet(objectSetType)
            if mc.objExists(objectSet):
                objectSets.append(objectSet)

        return objectSets

    def isParentedAboveRelative(self, objectSetType):
        """Test if a control objectSet is parented to an objectSet above its logical one (its parent objectSet), in the case of hole in the sets hierarchy
        :param str objectSetType: the type of objectSet, can be 'crtlSet' or 'skinSet'
        :return: True if the current objectSet is parented above
        :rtype: boolean
        """
        isParentedAboveRelative = False

        objectSet = self.getControlSet(objectSetType)
        if mc.objExists(objectSet):
            cgParents = self.listRelativesCg(p=True)
            if cgParents:
                cgParent = cgParents[0]
                parentObjectSet = cgParent.getControlSet(objectSetType)
                if mc.objExists(parentObjectSet):
                    if not isMemberOfSets(objectSet, (parentObjectSet,)):
                        isParentedAboveRelative = True
                else:
                    isParentedAboveRelative = True

        return isParentedAboveRelative

    def getObjectSetDepth(self, objectSetType):
        """Return the depth of an objectSet based on the depth of its controlGroup
        :param str objectSetType: the type of objectSet, can be 'crtlSet' or 'skinSet'
        :return: The depth of the objectSet
        :rtype: int
        """
        depth = -1
        objectSet = self.getControlSet(objectSetType)
        if mc.objExists(objectSet):
            depth = self.getControlGroupDepth()

        return depth

    def updateControlGroupSet(self, objectSetType='all', verbose=False):
        """Based on the objectSet options on the controlGroup, update the corresponding ctrlSet and/or skinSet
        :param str objectSetType: the type of objectSet, can be 'crtlSet', 'skinSet' or 'all'
        :rtype: None
        :raises: RuntimeError if unable to delete the control set
        :raises: RuntimeError if The controlGroup does not exist
        :raises: ValueError if invalid object type supplied
        """

        validObjectSetType = ['ctrlSet', 'skinSet', 'all']
        # test the validity of the inputs
        #
        if not isinstance(objectSetType, str) or objectSetType not in validObjectSetType:
            raise ValueError('[createControlGroupSet] Invalid object type supplied: {}'.fomat(objectSetType))

        if not mc.objExists(self.controlGroup):
            raise RuntimeError('[createControlGroupSet] The node {} does no more exist'.fomat(self.controlGroup))

        self.updateMembers()  # Update the members of the class so the sets will be synchronized without error before leaving the function

        setTypes = []
        doSetAttributes = []
        if objectSetType == 'ctrlSet' or objectSetType == 'all':
            setTypes.append('ctrlSet')
            doSetAttributes.append('doCtrlSet')
        if objectSetType == 'skinSet' or objectSetType == 'all':
            setTypes.append('skinSet')
            doSetAttributes.append('doSkinSet')

        for i, setType in enumerate(setTypes):
            prefix = setType.replace('Set', '')
            doSetAttribute = doSetAttributes[i]
            inPlug = mc.connectionInfo('{0}.{1}'.format(self.controlGroup, setType), sfd=True)

            if not mc.objExists(inPlug) and getattr(self, doSetAttribute):
                # Create the objectSet and fill the attribute in the class
                setattr(self, setType,
                        mc.createNode('objectSet',
                                      name=('{}{}_{}'.format(namespace(self.controlGroup),
                                                             prefix, self.name))))

                mc.connectAttr(('{}.message'.format(getattr(self, setType))), ('{0}.{1}'.format(
                    self.controlGroup, setType)))  # connect the newly created objectSet to the controlGroup
                # Then we proces the parent relationship
                #
                parentObjectSet = self.getFirstParentCreatedSet(
                    setType)
                if mc.objExists(parentObjectSet):
                    addToSets(getattr(self, setType), parentObjectSet, exclusive=True)
                # Then we proces the children relationship
                #
                childrenObjectSets = self.getFirstChildrenCreatedSet(setType)
                if len(childrenObjectSets):
                    # get the depth of the newly created objectSet (it matches the depth of the cg
                    currentSetDepth = self.getObjectSetDepth(setType)
                    if verbose:
                        print ('current set depth: ', currentSetDepth)
                    for childObjectSet in childrenObjectSets:
                        if verbose:
                            print ('ObjectSet: ', childObjectSet)
                        childCg = objectSetToControlGroup(childObjectSet)
                        if verbose:
                            print ('ChildCg: ', childCg)
                        # We know that in the case of controlGroup, the members of a set can only be in one set at once
                        parentSets = listSets(childObjectSet)
                        if verbose:
                            print ('Parent set: ', parentSets)
                        parentSetDepth = -1
                        if len(parentSets):
                            parentCg = objectSetToControlGroup(parentSets[0])
                            if verbose:
                                print ('ParentCg: ', parentCg)
                            parentSetDepth = parentCg.getObjectSetDepth(
                                setType)
                            if verbose:
                                print ('parent depth: ', parentSetDepth)

                        # isolated set or parented to a node above the current one
                        if not isMemberOfASet(childObjectSet) or (childCg.isParentedAboveRelative(setType) and parentSetDepth < currentSetDepth):
                            addToSets(childObjectSet, getattr(self, setType),
                                      exclusive=True)

                # Add this set all the members of the cg below in the hierarchy that are not in an objectSet
                #
                cgChildren = self.listRelativesCg(ad=True)
                if cgChildren:
                    for cgChild in cgChildren:
                        cgChildMembers = cgChild.getMembers()
                        if cgChildMembers:
                            for cgChildMember in cgChildMembers:
                                if setType == 'skinSet':
                                    sk = Control(
                                        cgChildMember).getNode('sk')
                                    # the case of a custom control without nsTpl for example
                                    if not mc.objExists(sk):
                                        continue
                                    else:
                                        if not isMemberOfASet(sk):
                                            addToSets(sk, getattr(
                                                self, setType), exclusive=True)

                                elif setType == 'ctrlSet':
                                    if not isMemberOfASet(cgChildMember):
                                        addToSets(cgChildMember, getattr(
                                            self, setType), exclusive=True)

            elif mc.objExists(inPlug) and not getattr(self, doSetAttribute):
                objectSet = inPlug.split('.')[0]
                try:
                    # Before deleting the set, re-parenting the subsets to the parent sets of the sets that is going to be deleted
                    #
                    parentObjectSets = listSets(getattr(self,
                                                        setType))
                    if len(parentObjectSets):
                        childrenObjectSets = listMembersOfSet(
                            getattr(self, setType), typ='objectSet')
                        if len(childrenObjectSets):
                            for childObjectSet in childrenObjectSets:
                                addToSets(
                                    childObjectSet, parentObjectSets[0], exclusive=True)

                        # to move the member of the deleted set to the parent set
                        #
                        memberOfSets = listMembersOfSet(
                            getattr(self, setType), typ='dagNode')
                        if len(memberOfSets):
                            for memberOfSet in memberOfSets:
                                addToSets(
                                    memberOfSet, parentObjectSets[0], exclusive=True)

                        # get the members of the set that will be deleted and move them in the first existing parent set
                        #
                    # Remove the connection to the controlGroup
                    #
                    mc.disconnectAttr('{}.message'.format(
                        objectSet), '{0}.{1}'.format(self.controlGroup, setType))
                    # clean the connections to avoid auto-deletion of controlGroup nodes
                    #
                    otherConnections = mc.connectionInfo(
                        '{}.message'.format(objectSet), dfs=True) or []
                    if otherConnections:
                        for otherConnection in otherConnections:
                            mc.disconnectAttr('{}.message'.format(
                                objectSet), otherConnection)
                    # Finally delete the set and update the set variable in the ControlGroup object
                    #
                    mc.delete(objectSet)
                    setattr(self, setType, '')
                except Exception:
                    raise RuntimeError(
                        '[createControlGroupSet] Unable to delete control set')

        # now fill or remove the members
        #
        self.updateSetsMembers(objectSetType)

    def isMemberOf(self, obj, memberType):
        """check if an object is already a member of the controlGroup's members or templates
        :param str: Maya node name
        :param str: memberType
        :rtype: boolean
        """
        validMemberType = ['members', 'templates']
        isMember = False
        if isinstance(memberType, str) and memberType in validMemberType:
            if mc.objExists(self.controlGroup):
                if memberType == 'members':
                    if obj in self.members:
                        isMember = True
                elif memberType == 'templates':
                    if obj in self.templates:
                        isMember = True
            else:
                raise RuntimeError(
                    '[isMemberOf] The controlGroup {} does not exist anymore'.format(self.controlGroup))
        else:
            raise RuntimeError(
                '[isMemberOf] The supplied memberType is invalid'.format(memberType))
        return isMember

    def addTemplates(self, nodes):
        """add the supplied nodes to the controlGroup templates, the nodes must be templated before with the Class ControlTemplate
        :param list nodes: The list of templatd nodes
        :return: added nodes
        :rtype: list
        :raises: RuntimeError The nsTpl node is already used by another controlGroup
        :raises: RuntimeError The nsTpl node does not exist anymore
        """
        addedNodes = []
        if mc.objExists(self.controlGroup):

            if self.isCgASplit():
                raise RuntimeError(
                    '[addTemplates] The node {} is a cg split, and templates must be add to the master cg'.format(self.controlGroup))

            for node in nodes:
                outMessagePlugs = mc.connectionInfo(
                    '{}.message'.format(node), dfs=True) or []
                alreadyTemplate = False
                if outMessagePlugs:
                    for outMessagePlug in outMessagePlugs:
                        outMessageNode = outMessagePlug.split('.')[0]
                        if outMessageNode == self.controlGroup:
                            alreadyTemplate = True
                            break
                        else:
                            outMessageAttr = baseAttributeName(
                                outMessagePlug)
                            if outMessageAttr == 'templates':  # Check if already templated to another cgGroup
                                if ObjectType(outMessageNode).isOfType('controlGroup'):
                                    alreadyTemplate = True
                                    pass
                                    #raise RuntimeError('[addTemplates] The node {0} is already used by another controlGroup {1}'.format(
                                    #    node, outMessageNode))
                                    #alreadyTemplate = True
                                    #break

                if not alreadyTemplate:
                    idx = getMultiFirstAvailableIndex(self.controlGroup, 'templates')
                    ct = ControlTemplate(node)
                    mc.connectAttr('{}.message'.format(
                        node), '{0}.templates[{1}]'.format(self.controlGroup, idx))
                    addedNodes.append(ct)
                else:
                    print('[addTemplates] The node {0} is already a nsTpl of the controlGroup {1}'.format(
                        node, self.controlGroup))
        else:
            raise RuntimeError(
                '[addTemplates] The node {} does not exist anymore'.format(self.controlGroup))
        # Update the object
        #
        self.updateTemplates()
        return addedNodes

    def removeTemplate(self, template, below=False, removeMember=True, deleteMember=False, progressBar=None):
        """Remove nsTpl nodes from the controlGroup, and optionnaly destroye the corresponding controls
        :param Maya dagNode template: the templates to remove
        :param boolean below: indicate that the hierarchy below the nsTpl as well as the controls will be deleted
        :param boolean removeMember: if the members are built ( root, c, pose, sk) they will be removed from the control group
        :param boolean deleteMember: if the members are built ( root, c, pose, sk) they will be deleted from the Maya scene
        :return: the removed templates
        :rtype: list
        :raises: RuntimeError The controlGroup does not exist anymore
        :raises: RuntimeError Receive index -1 for the control index
        :raises: RuntimeError The root does not exist anymore
        """
        removedTemplates = []
        if not mc.objExists(self.controlGroup) or not mc.objExists(template):
            raise RuntimeError('[removeTemplates] The controlGroup {} does not exist anymore'.format(self.controlGroup))
        # Probaly change that if we want to build nsTpl with locators too
        hierarchyBelow = mc.listRelatives(
            template, ad=True, pa=True, type='joint') or []
        toRemove = [template]
        if below:
            toRemove += hierarchyBelow
        # sort the hierarchy and reverse it, so from the leaves to the root
        toRemove = sortByHierarchyDepth(toRemove, '', True)[::-1]

        for i, tpl in enumerate(toRemove):  # @UnusedVariable
            if tpl in removedTemplates or not self.isMemberOf(tpl, 'templates'):
                continue

            index = self.getMemberIndex(tpl, 'templates')
            if index == -1:
                continue
            ct = ControlTemplate(tpl)

            controls = ct.getControls(location='all')
            for ctrl in controls:
                if not removeMember:
                    continue
                idx = self.getMemberIndex(ctrl, 'members')
                if idx == -1:
                    raise RuntimeError(
                        '[removeTemplates] Receive idx -1 for the control {} index'.format(ctrl))
                memberPlug = '{0}.members[{1}]'.format(self.controlGroup, idx)
                if not deleteMember:
                    mc.disconnectAttr('{}.message'.format(ctrl), memberPlug)
                    continue
                c = Control(ctrl)
                root = c.getNode('root')
                if not mc.objExists(root):
                    raise RuntimeError('[removeTemplates] The root {} does not exist anymore'.format(root))

                if below:
                    c.unparentControl(below=below)
                    continue

                cChildren = c.listRelativesControl(
                    c=True)
                if cChildren:
                    cParents = c.listRelativesControl(
                        p=True)
                    if cParents:
                        for cChild in cChildren:
                            cChild.parentControlTo(
                                cParents[0])
                    else:  # The control c is directly parented under the rig group
                        for cChild in cChildren:
                            cChild.unparentControl()

                mc.delete(root)

                mc.removeMultiInstance(memberPlug, b=True)

            # print 'nsTpl', tpl, (mc.getAttr('{}.templates'.format(self), multiIndices=True)), self.getMemberIndex(tpl, 'templates')
            # re-read the index, because the control group could have been cleanup during the previous iteration, and the indexes are no more valid
            #
            index = self.getMemberIndex(tpl, 'templates')
            templatePlug = '{0}.templates[{1}]'.format(
                self.controlGroup, index)
            mc.disconnectAttr(
                '{}.message'.format(tpl), templatePlug)
            mc.removeMultiInstance(templatePlug, b=True)
            removedTemplates.append(tpl)

        self.cleanUpMembers('all')

        return removedTemplates

    def removeMember(self, member, below=False, deleteMember=False, removeTemplate=True, progressBar=None):
        """Remove member nodes from the controlGroup, and optionnaly destroye the corresponding nsTpl
        :param maya dagNode member: the member to remove
        :param boolean below: indicate that the hierarchy below the member as well as the nsTpl will be deleted
        :param boolean deleteMember: if the members are built ( root, c, pose, sk) they will be deleted from the Maya scene
        :param boolean removeTemplate: if the member's nsTpl is built, it will be removed from the control group
        :return: the removed templates
        :rtype: list
        :raises: RuntimeError The controlGroup does not exist anymore
        :raises: RuntimeError Receive index -1 for the control index
        :raises: RuntimeError The root does not exist anymore
        :TODO: debug si remove all members, deletion of the last one failed
        """
        removedMembers = []
        if mc.objExists(self.controlGroup) and mc.objExists(member) and self.isMemberOf(member, 'members'):
            c = Control(member)
            toRemove = [c]
            if below:
                hierarchyBelow = c.listRelativesControl(ad=True)
                toRemove += hierarchyBelow
            # sort the hierarchy and reverse it, so from the leaves to the root, here an object is directly use thanx to the __str__ function that return the maya unicode name
            toRemove = sortByHierarchyDepth(toRemove, '', True)[::-1]

            #if isinstance(progressBar, QProgressBar):
            #progressBar.setMinimum(0)
            #progressBar.setMaximum(len(toRemove))
            #progressBar.setVisible(True)

            for i, c in enumerate(toRemove):  # @UnusedVariable
                if not isControlObjectInList(c, removedMembers):
                    index = self.getMemberIndex(c.getControl(), 'members')
                    if index != -1:
                        tpl = c.getNode('nsTpl')
                        if removeTemplate and mc.objExists(tpl):
                            self.removeTemplate(
                                tpl, below=False, removeMember=False, deleteMember=False)
                        # re-read the index, because the control group could have been cleanup during the previous iteration, and the indexes are no more valid
                        #
                        c.unparentControl(below=False)
                        mirrorControl = c.getNode('mirror')
                        if mc.objExists(mirrorControl):
                            cMirror = Control(mirrorControl)
                            Control.removeNodeIdFromMultis(
                                cMirror.getControl(), 'mirror')
                        index = self.getMemberIndex(c.getControl(), 'members')
                        memberPlug = '{0}.members[{1}]'.format(
                            self.controlGroup, index)
                        mc.disconnectAttr('{}.message'.format(
                            c.getControl()), memberPlug)
                        mc.removeMultiInstance(memberPlug, b=True)
                        # remove from its ctrl and skin sets
                        #
                        ctrlSet = self.getControlSet('ctrlSet')
                        skinSet = self.getControlSet('skinSet')
                        removeFromSets(c.getControl(), [ctrlSet, skinSet])
                        root = c.getNode('root')
                        inVis = mc.connectionInfo(
                            root + '.visibility', sfd=True)
                        if mc.objExists(inVis):
                            mc.setAttr(root + '.visibility', lock=False)
                            multdoubleLinear = getFirstTypedConnected('multDoubleLinear', '{}.visibility'.format(
                                root), returnPlug=False, source=True, destination=False, depth=1, verbose=False)
                            if mc.objExists(multdoubleLinear):
                                mc.delete(multdoubleLinear)
                            else:
                                mc.disconnectAttr(inVis, root + '.visibility')
                        elif isPlugConnected('{}.visibility'.format(member), side=0):
                            inVis = mc.connectionInfo(
                                '{}.visibility'.format(member), sfd=True)
                            # The controlGroup is connected directly to the control, surely du to a addNodeAsControl
                            if nodeFromPlug(inVis) == self.controlGroup:
                                mc.setAttr('{}.visibility'.format(
                                    member), lock=False)
                                mc.disconnectAttr(
                                    inVis, '{}.visibility'.format(member))

                        if deleteMember:
                            if mc.objExists(root):
                                try:
                                    mc.delete(root)
                                except Exception:
                                    raise
                            else:
                                try:
                                    mc.delete(c.getControl())
                                except Exception:
                                    raise
                        removedMembers.append(c)

                #if isinstance(progressBar, QProgressBar):
                    #progressBar.setValue(i)

            #if isinstance(progressBar, QProgressBar):
                #progressBar.reset()
                #progressBar.setVisible(False)
            # reorganize the nsTpl and members multi attributes to avoid hole in the logical indexe
            #
            self.cleanUpMembers('all')
        else:
            raise RuntimeError(
                '[removeTemplates] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        return removedMembers

    def getMemberIndex(self, member, memberType):
        '''
        Retreive the index of a member in the controlGroup
        '''
        validMemberType = ['members', 'templates']
        index = -1
        if isinstance(memberType, str) and memberType in validMemberType:
            if mc.objExists(self.controlGroup):
                members = []
                if memberType == 'members':
                    members = self.members
                elif memberType == 'templates':
                    members = self.templates

                if member in members:
                    plug = '{0}.{1}'.format(self.controlGroup, memberType)
                    inCx = mc.listConnections(
                        plug, s=True, d=False, p=True, c=True) or []
                    if inCx:
                        for i in xrange(0, len(inCx), 2):
                            node = nodeFromPlug(inCx[i + 1])
                            if node == member:
                                index = attributeIndexFromPlug(
                                    inCx[i], memberType)
                    # index = members.index(member)
            else:
                raise RuntimeError(
                    '[getMemberIndex] The controlGroup {} does not exist anymore'.format(self.controlGroup))
        return index

    def cleanUpMembers(self, memberType):
        '''
        '''
        validMemberType = ['members', 'templates', 'all']
        if mc.objExists(self.controlGroup):
            if isinstance(memberType, basestring) and memberType in validMemberType:
                attributes = []
                if memberType == 'members':
                    attributes.append('members')
                elif memberType == 'templates':
                    attributes.append('templates')
                elif memberType == 'all':
                    attributes.extend(['members', 'templates'])

                for attribute in attributes:
                    members = mc.listConnections('{0}.{1}'.format(
                        self.controlGroup, attribute), source=True, destination=False, plugs=True) or []
                    # now break the connections
                    #
                    connections = mc.listConnections('{0}.{1}'.format(
                        self.controlGroup, attribute), source=True, destination=False, plugs=True, connections=True) or []
                    for i in xrange(0, len(connections), 2):
                        dest = connections[i]
                        source = connections[i + 1]
                        mc.disconnectAttr(source, dest)

                    indices = mc.getAttr('{0}.{1}'.format(
                        self.controlGroup, attribute), multiIndices=True) or []
                    # mc.select(cl=True)
                    for indice in indices:
                        mc.removeMultiInstance('{0}.{1}[{2}]'.format(
                            self.controlGroup, attribute, indice), b=True)

                    for indice, member in enumerate(members):
                        mc.connectAttr(member, '{0}.{1}[{2}]'.format(
                            self.controlGroup, attribute, indice))
                # update the object
                #
                self.updateTemplates()
                self.updateMembers()

    @staticmethod
    def createControlAttributes(dagNode):
        """
        create the controls attributes on a dagNode node
        """
        if mc.objExists(dagNode):
            # Create the attribute to specified that this node is a control
            #
            if not ObjectType(dagNode).isOfType('control'):
                ObjectType(dagNode).setRigNodeType(
                    'control', lockIt=True)

            # Create the description attrs and connect the nsTpl to the first ids
            #
            if not mc.attributeQuery('nodesId', node=dagNode, exists=True):
                mc.addAttr(dagNode, ln='nodesId', multi=True, dt='string')

            if not mc.attributeQuery('nodes', node=dagNode, exists=True):
                mc.addAttr(dagNode, ln='nodes', multi=True, at='message')
            # Create de bindPose storing attrs
            #
            if not mc.attributeQuery('bindPoseAttrs', node=dagNode, exists=True):
                mc.addAttr(dagNode, ln='bindPoseAttrs',
                             multi=True, dt='string')

            if not mc.attributeQuery('bindPoseValues', node=dagNode, exists=True):
                mc.addAttr(dagNode, ln='bindPoseValues',
                             multi=True, at='float')

            if mc.objectType(dagNode, isAType='transform'):
                # if mc.objectType(dagNode, isAType='joint'):
                if not mc.attributeQuery('parentScale', node=dagNode, exists=True):
                    parentScaleDefault = True
                    mc.addAttr(dagNode, ln='parentScale', k=True,
                                 at='bool', dv=parentScaleDefault)
                    if not mc.referenceQuery(dagNode, isNodeReferenced=True) and not mc.lockNode(dagNode, query=True)[0]:
                        mc.setAttr(
                            '{}.parentScale'.format(dagNode), cb=True)

                if not mc.attributeQuery('mirrorSide', node=dagNode, exists=True):
                    mc.addAttr(dagNode, ln='mirrorSide', at='enum',
                                 enumName=':'.join(ControlTemplate.validLocations))
                    defaultSide = ControlTemplate.validLocations.index(
                        getObjectLocation(dagNode, tolerance=.0001))

                    mc.addAttr(dagNode + '.mirrorSide',
                                 edit=True, dv=defaultSide)
                    mc.setAttr('{}.mirrorSide'.format(dagNode), defaultSide)
                    if not mc.referenceQuery(dagNode, isNodeReferenced=True) and not mc.lockNode(dagNode, query=True)[0]:
                        mc.setAttr('{}.mirrorSide'.format(
                            dagNode), lock=True)

                if not mc.attributeQuery('mirrorType', node=dagNode, exists=True):
                    mc.addAttr(dagNode, ln='mirrorType', at='enum', enumName=':'.join(
                        ControlTemplate.validMirrorTypes))
                    defaultMirrorType = ControlTemplate.validMirrorTypes.index(
                        'none')
                    mc.addAttr(dagNode + '.mirrorType',
                                 edit=True, dv=defaultMirrorType)
                    mc.setAttr('{}.mirrorType'.format(
                        dagNode), defaultMirrorType)
                    if not mc.referenceQuery(dagNode, isNodeReferenced=True) and not mc.lockNode(dagNode, query=True)[0]:
                        mc.setAttr('{}.mirrorType'.format(
                            dagNode), lock=True)

                if not mc.referenceQuery(dagNode, isNodeReferenced=True) and not mc.lockNode(dagNode, query=True)[0]:
                    mc.setAttr('{}.rotateOrder'.format(
                        dagNode), k=True, cb=True)

            if not mc.referenceQuery(dagNode, isNodeReferenced=True) and not mc.lockNode(dagNode, query=True)[0]:
                mc.setAttr('{}.visibility'.format(dagNode), cb=True)

    def addControlAttributes(self, obj, ct):
        '''
        '''
        if mc.objExists(obj) and isinstance(ct, ControlTemplate):
            if mc.objExists(ct.controlTemplate):

                ControlGroup.createControlAttributes(obj)

                mc.setAttr('{}.rotateOrder'.format(obj), mc.getAttr(
                    '{}.rotateOrder'.format(ct.controlTemplate)))

                parentScaleDefault = True
                if ct.parentScale == 'joint':
                    parentScaleDefault = False
                mc.setAttr('{}.parentScale'.format(obj), parentScaleDefault)
                mc.addAttr(obj + '.parentScale', edit=True,
                             dv=parentScaleDefault)

                mc.setAttr('{}.mirrorSide'.format(obj), lock=False)
                mc.addAttr(obj + '.mirrorSide', edit=True,
                             dv=ControlTemplate.validLocations.index(ct.location))
                mc.setAttr('{}.mirrorSide'.format(
                    obj), ControlTemplate.validLocations.index(ct.location), lock=True)

                mc.setAttr('{}.mirrorType'.format(obj), lock=False)
                mc.addAttr(obj + '.mirrorType', edit=True,
                             dv=ControlTemplate.validMirrorTypes.index(ct.mirrorType))
                mc.setAttr('{}.mirrorType'.format(
                    obj), ControlTemplate.validMirrorTypes.index(ct.mirrorType), lock=True)

    @staticmethod
    def connectControlToSkin(control, skin):
        '''
        Connect the control object to the skinning joint
        '''
        success = True
        if mc.objExists(control) and mc.objExists(skin):
            attributes = ['translate', 'rotate', 'scale',
                          'shear', 'rotateOrder', 'jointOrient']
            for attr in attributes:
                if mc.attributeQuery(attr, node=control, exists=True) and mc.attributeQuery(attr, node=skin, exists=True):
                    pSrc = '{0}.{1}'.format(control, attr)
                    pDst = '{0}.{1}'.format(skin, attr)
                    try:
                        mc.connectAttr(pSrc, pDst)
                    except Exception:
                        raise
                        success = False
                        continue
        return success

    @staticmethod
    def connectParentScale(control, root):
        '''
        Connect the parentScale attribute (allow a control hierachy to scame or not with its parent) to the segmentScaleCompensate of the root joint
        '''
        success = True
        if mc.objExists(control) and mc.objExists(root):
            if mc.attributeQuery('parentScale', node=control, exists=True):
                if not isPlugConnected('{}.segmentScaleCompensate'.format(root), 0) and not mc.getAttr('{}.segmentScaleCompensate'.format(root), lock=True):
                    reverseNode = mc.createNode('reverse')
                    mc.connectAttr('{}.parentScale'.format(
                        control), '{}.inputX'.format(reverseNode))
                    mc.connectAttr('{}.outputX'.format(
                        reverseNode), '{}.segmentScaleCompensate'.format(root))
                else:
                    success = False
            else:
                success = False
        else:
            success = False

        return success

    def getFirstBuiltParent(self, obj):
        """From a built control, search its built parent by searching in the nsTpl hierachy
        :param Control or dagNode: the supplied control is of type Control (handle by the class Control) or a Maya transform Node
        :return: The built parent
        :rtype: list
        :raises: ValueError The supplied node does not exist anymore or is not of type control, or a Control object has not been passed
        :raises: RuntimeError Unable to find the matching nsTpl node
        """
        built = []
        # check if a Control has been passed
        if isinstance(obj, Control) and mc.objExists(obj.control):
            c = obj
        # Check if a maya node has been passed and test its type as well
        elif ObjectType(obj).isOfType('control'):
            c = Control(obj)
        else:
            raise ValueError(
                '[getFirstBuiltParent] The supplied node does not exist anymore or is not of type control, or a Control object has not been passed')

        template = c.getNode('nsTpl')  # Return a Maya node
        if not mc.objExists(template):
            raise RuntimeError(
                '[getFirstBuiltParent] Unable to find the matching nsTpl node')

        found = False
        while(not found):
            parents = mc.listRelatives(template, pa=True,
                                       p=True, type='transform') or []
            if not parents:
                break

            if not ObjectType(parents[0]).isOfType('controlTemplate'):
                template = parents[0]
                continue

            ct = ControlTemplate(parents[0])
            if not ct.isBuilt:
                template = parents[0]
                continue

            if ct.isControlBuilt(c.mirrorSide):  # if we found control built on the same side
                built = ct.getControls(c.mirrorSide)
                found = True
                break

            if ct.isControlBuilt():  # else we take all the locations
                side = ControlTemplate.validLocations[3]
                built = ct.getControls(side)
                if built:
                    found = True
                    break
                template = parents[0]

        if built:
            return built[0]
        return None

    def buildControls(self, verbose=False, progressBar=None, freeNaming=True):
        '''
        Build all the controls based on the class's templates
        '''
        createdControls = []
        if not mc.objExists(self.controlGroup):
            raise RuntimeError(
                '[createControls] The controlGroup {} does not exist anymore'.format(self.controlGroup))

        if self.isCgASplit():
            raise RuntimeError("[buildControls] The node {} is a cg split, and can't be built".format(self.controlGroup))

        if not len(self.templates):
            raise RuntimeWarning('[createControls] No templates to build for the controlGroup {}'.format(self.controlGroup))
        sortedTemplates = sortByHierarchyDepth(
            self.templates, 'dagNode', traverse=True)

        count = 0
        for template in sortedTemplates:
            if not mc.objExists(template):
                raise RuntimeError('[createControls] The controlTemplate {} does not exist anymore'.format(template))
            ct = ControlTemplate(template)
            if not ct.isControlBuilt():
                if ct.isBuilt:
                    print (ct, ' -> controls on both sides ', ct.location,
                           ' and ', ct.inverseLocation(ct.location), " doesn't exist")
                    try:
                        builtControls = self.createControl(
                            template, side='bothSide', verbose=False, freeNaming=True)
                        if builtControls:
                            createdControls.extend(builtControls)
                    except Exception:
                        raise
            else:  # The control is already built, we will check the hierarchy to verify it's ok based on the tpl hierarchy
                # search for the side of the nsTpl
                existingControls = ct.getControls(ct.location)
                if existingControls:
                    if verbose:
                        print (ct, ' -> control on side ', ct.location, ' exists')
                        print ('\tUpdating hierarchy...')

                    c = Control(existingControls[0])
                    parent = self.getFirstBuiltParent(c)
                    if parent:
                        cParent = Control(parent)
                        if isinstance(cParent, Control):
                            c.parentControlTo(cParent)

                    # Update the transformations on the root
                    #
                    if verbose:
                        print ('\tUpdating matrix...')

                    skinClusters = c.getConnectedSkinClusters()
                    setSkinClusterInMoveJointsMode(
                        skinClusters, state=True)

                    root = c.getNode('root')
                    xform = getTransformationsInSpace(template, root)
                    try:
                        mc.setAttr('{}.translate'.format(
                            root), xform[0][0], xform[0][1], xform[0][2], type='double3')
                        mc.setAttr('{}.jointOrient'.format(
                            root), .0, .0, .0, type='double3')
                        mc.setAttr('{}.rotate'.format(
                            root), xform[1][0], xform[1][1], xform[1][2], type='double3')
                        mc.setAttr('{}.scale'.format(
                            root), xform[2][0], xform[2][1], xform[2][2], type='double3')
                        mc.setAttr('{}.shear'.format(
                            root), xform[3][0], xform[3][1], xform[3][2], type='double3')

                        # Write the global direction of the joint
                        #
                        writeNodeAxis(c.getControl(), verbose=False)

                        # here transfert rotation to the jointOrient
                        #
                        rotateToJointOrient(root)
                    except Exception:
                        pass
                    finally:
                        setSkinClusterInMoveJointsMode(
                            skinClusters, state=False)
                else:
                    if verbose:
                        print (ct, ' -> control on side ',
                               ct.location, 'does not exist')

                    builtControls = self.createControl(
                        template, side='templateSide', verbose=False, freeNaming=True)
                    if builtControls:
                        createdControls.extend(builtControls)

                isMirrored = ct.isMirrored
                if isMirrored:
                    existingControls = ct.getControls(
                        ct.inverseLocation(ct.location))
                    if existingControls:
                        if verbose:
                            print (ct, ' -> control on side ',
                                   ct.inverseLocation(ct.location),
                                   ' exists')
                            print ('\tUpdating hierarchy...')

                        cMirror = Control(existingControls[0])
                        mirrorParent = self.getFirstBuiltParent(
                            cMirror)
                        if mirrorParent:
                            cMirrorParent = Control(mirrorParent)
                            if isinstance(cMirrorParent, Control):
                                cMirror.parentControlTo(
                                    cMirrorParent)

                        # Update the transformations on the root
                        #
                        if verbose:
                            print ('\tUpdating matrix...')

                        skinClusters = cMirror.getConnectedSkinClusters()
                        setSkinClusterInMoveJointsMode(
                            skinClusters, state=True)
                        # Creation of a dummy joint to be sur that the world transform will be retreive especially for the scale with the shear
                        #
                        tmpRoot = mc.createNode('joint')
                        rotateOrder = mc.getAttr(
                            '{}.rotateOrder'.format(existingControls[0]))
                        mc.setAttr('{}.rotateOrder'.format(
                            tmpRoot), rotateOrder)
                        xform = getTransformations(template, space='world')

                        mc.setAttr('{}.translate'.format(
                            tmpRoot), xform[0][0], xform[0][1], xform[0][2], type='double3')
                        mc.setAttr('{}.rotate'.format(
                            tmpRoot), xform[1][0], xform[1][1], xform[1][2], type='double3')
                        mc.setAttr('{}.scale'.format(
                            tmpRoot), xform[2][0], xform[2][1], xform[2][2], type='double3')
                        mc.setAttr('{}.shear'.format(
                            tmpRoot), xform[3][0], xform[3][1], xform[3][2], type='double3')

                        # Write the global direction of the joint
                        #
                        writeNodeAxis(tmpRoot, verbose=False)

                        mirrorType = ct.mirrorType
                        tmpMirrorRoot = ''

                        if 'transform' == mirrorType:
                            tmpMirrorRoot = mc.mirrorJoint(
                                tmpRoot, mirrorYZ=True)[0]
                            # new method
                            #
                            mirrorRootMirrorMatrix = rotateMatrixFromNodeAxis(tmpRoot,
                                                                              symetryAxis='x',
                                                                              verbose=False)
                            mirrorWorldEulerRotation = om.MTransformationMatrix(
                                mirrorRootMirrorMatrix).rotation()
                            mirrorWorldEulerRotation.reorderIt(
                                rotateOrder)
                            mirrorWorldRot = [degrees(mirrorWorldEulerRotation.x),
                                              degrees(mirrorWorldEulerRotation.y),
                                              degrees(mirrorWorldEulerRotation.z)]

                            jointOrientToRotate(tmpMirrorRoot)
                            # mc.xform(tmpMirrorRoot, a=True, ws=True, ro=[mirrorWorldRot[0], mirrorWorldRot[1], mirrorWorldRot[2]])
                            mc.setAttr('{}.rotate'.format(
                                tmpMirrorRoot), mirrorWorldRot[0], mirrorWorldRot[1], mirrorWorldRot[2], type='double3')
                            rotateToJointOrient(
                                tmpMirrorRoot)
                            # Write the global direction of the joint
                            #
                            writeNodeAxis(tmpMirrorRoot, verbose=False)
                            # Mirror the shear
                            #
                            mirrorShearMatrix = shearMatrixFromNodeAxis(tmpRoot,
                                                                        symetryAxis='x',
                                                                        verbose=False)
                            mirrorWorldShear = om.MTransformationMatrix(
                                mirrorShearMatrix).shear(om.MSpace.kTransform)
                            mc.setAttr('{}.shear'.format(
                                tmpMirrorRoot), mirrorWorldShear[0], mirrorWorldShear[1], mirrorWorldShear[2], type='double3')
                            mc.delete(tmpRoot)
                        elif 'joint' == mirrorType:
                            tmpMirrorRoot = mc.mirrorJoint(
                                tmpRoot, mirrorBehavior=True, mirrorYZ=True)[0]
                            # Write the global direction of the joint
                            #
                            writeNodeAxis(tmpMirrorRoot, verbose=False)
                            mc.delete(tmpRoot)
                        elif 'orientation' == mirrorType:  # For the specular by example
                            # Write the global direction of the joint
                            #
                            writeNodeAxis(tmpRoot, verbose=False)
                            tmpMirrorRoot = mc.mirrorJoint(
                                tmpRoot, mirrorYZ=True)[0]
                            mc.delete(tmpRoot)
                        elif 'translate' == mirrorType:
                            tmpMirrorRoot = mc.mirrorJoint(
                                tmpRoot, mirrorYZ=True)[0]
                            tmpDum = mc.createNode('transform')
                            tmpDumRoot = mc.createNode(
                                'transform')
                            mc.parent(tmpDum, tmpDumRoot)
                            mc.delete(mc.parentConstraint(
                                tmpMirrorRoot, tmpDum, mo=False))
                            mc.setAttr(tmpDum+'.rotateY', 180)
                            mc.delete(mc.orientConstraint(tmpDum,
                                                          tmpMirrorRoot,
                                                          mo=False))
                            mc.delete(tmpDumRoot)
                            mc.setAttr(tmpMirrorRoot+'.jointOrientY',
                                       mc.getAttr(tmpMirrorRoot+'.rotateY'))
                            mc.setAttr(tmpMirrorRoot+'.rotateY', 0)

                            # Write the global direction of the joint
                            #
                            writeNodeAxis(
                                tmpMirrorRoot, verbose=False)
                            mc.delete(tmpRoot)

                        mirrorRoot = cMirror.getNode('root')
                        xform = getTransformationsInSpace(
                            tmpMirrorRoot, mirrorRoot)
                        if mc.objExists(tmpMirrorRoot):
                            mc.delete(tmpMirrorRoot)
                        try:
                            mc.setAttr('{}.translate'.format(
                                mirrorRoot), xform[0][0], xform[0][1], xform[0][2], type='double3')
                            mc.setAttr('{}.jointOrient'.format(
                                mirrorRoot), .0, .0, .0, type='double3')
                            mc.setAttr('{}.rotate'.format(
                                mirrorRoot), xform[1][0], xform[1][1], xform[1][2], type='double3')
                            mc.setAttr('{}.scale'.format(
                                mirrorRoot), xform[2][0], xform[2][1], xform[2][2], type='double3')
                            mc.setAttr('{}.shear'.format(
                                mirrorRoot), xform[3][0], xform[3][1], xform[3][2], type='double3')

                            # Write the global direction of the joint
                            #
                            writeNodeAxis(
                                cMirror.getControl(), verbose=False)

                            # here transfert rotation to the jointOrient
                            #
                            rotateToJointOrient(
                                mirrorRoot)
                        except Exception:
                            pass
                        finally:
                            setSkinClusterInMoveJointsMode(
                                skinClusters, state=False)
                    else:
                        if verbose:
                            print ct, ' -> control on side ', ct.inverseLocation(
                                ct.location), 'does not exist'
                        builtControls = self.createControl(
                            template, side='oppositeSide', verbose=False, freeNaming=True)
                        if builtControls:
                            createdControls.extend(builtControls)
            count += 1

        # in case of a partial reconstruction of the controls we need to fix lost mirror connections
        #
        self.restoreMirrorConnections(verbose=verbose)
        # Here clean the hierarchy and create the rig group if necessary
        #
        mc.hide(self.tplGroup)
        self.updateMembers()
        if self.isCgSplittable() and self.isCgSplitted():
            self.updateSplits()
        # Update the control sets
        #
        self.updateControlGroupSet('all')

    def restoreMirrorConnections(self, verbose=False):
        """If only missing controls are rebuilt, we must found their mirror and restore the mirror connections between the two controls so we can have the flip and mirror
        functions available
        """
        members = self.getMembers()

        for i in xrange(0, len(members)):
            ctrl = Control(members[i])
            controlName = ctrl.getControl()
            mirrorSide = ctrl.mirrorSide
            if mirrorSide in ['middle', 'none']:
                continue

            mirrorCtrl = ctrl.getNode('mirror')
            if mc.objExists(mirrorCtrl):
                continue

            oppositeSide = ControlTemplate.inverseLocation(
                mirrorSide)
            baseName = NameParser(
                controlName).getBaseName()
            nameIndex = NameParser(
                controlName).getNameIndex()
            baseName += nameIndex
            for j in xrange(i, len(members)):
                otherCtrl = Control(members[j])
                otherControlName = otherCtrl.getControl()
                otherBaseName = NameParser(
                    otherControlName).getBaseName()
                otherNameIndex = NameParser(
                    otherControlName).getNameIndex()
                otherBaseName += otherNameIndex
                if baseName != otherBaseName:
                    continue

                otherMirrorSide = otherCtrl.mirrorSide
                if oppositeSide != otherMirrorSide:
                    continue
                Control.setNodeIdToMultis(
                    ctrl.getControl(), otherControlName, 'mirror')
                Control.setNodeIdToMultis(
                    otherCtrl.getControl(), controlName, 'mirror')
                if verbose:
                    print('Restoring mirror connections between', controlName, 'and', otherControlName)

    def createControl(self, controlTemplate, side='bothSide', verbose=False, freeNaming=True):
        """Create an FK control
        :param Maya DagNode controlTemplate: the joint templated
        :param str side: which side is built, templateSide: the same nsTpl's side, bothSide: the two side, oppositeSide: the opposite side of the nsTpl
        :param boolean varbose: to print debug informations
        :raises: ValueError invalid side supplied
        :TODO: Normalized the scale
        :TODO: Replace getMultiFirstAvailableIndex by static method in Control: Control.setNodeIdToMultis
        """
        validSides = ['templateSide', 'bothSide', 'oppositeSide']

        if not mc.objExists(controlTemplate):
            raise ValueError(
                '[createControl] Invalid nsTpl {} supplied'.format(controlTemplate))
            return None

        if side not in validSides:
            raise ValueError(
                '[createControl] Invalid side {} supplied'.format(side))
            return None

        ct = ControlTemplate(controlTemplate)
        if ct.isBuilt:
            baseName = ct.baseName
            index = ct.index
            rootPrefix = ct.rootPrefix
            controlPrefix = ct.controlPrefix
            skPrefix = ct.skPrefix
            location = ct.locationToSuffix(ct.location)
            inverseLocation = ct.locationToSuffix(
                ct.inverseLocation(ct.location))
            isMirrored = ct.isMirrored
            mirrorType = ct.mirrorType
            rotateOrder = ct.validRotateOrders.index(ct.rotateOrder)
            addToCtrlSet = ct.addToCtrlSet
            addToSkinSet = ct.addToSkinSet
            iconType = ct.iconType
            mirrorType = ct.mirrorType
            controlTemplate = ct.controlTemplate

            rootName = rootPrefix + '_' + baseName + index + location

            if side == 'oppositeSide':
                rootName = rootPrefix + '_' + baseName + index + inverseLocation

            if freeNaming == True:
                rootName = controlTemplate.replace('tpl', 'root')
                if side == 'oppositeSide':
                    if '_L' in rootName:
                        rootName = rootName.replace('_L', '_R')
                    elif '_R' in rootName:
                        rootName = rootName.replace('_R', '_L')

            root = mc.createNode('joint', name=rootName)

            # Draw style is None by default
            mc.setAttr('{}.drawStyle'.format(root), 2)
            mc.setAttr('{}.radius'.format(root), 0)
            mc.setAttr('{}.rotateOrder'.format(root), rotateOrder)
            # Creation of a dummy to be sur that the world transform will be retreive especially for the scale with the shear
            #
            dummy = mc.createNode('transform', name=(
                'dummy_{}'.format(ct.controlTemplate)))
            mc.setAttr('{}.rotateOrder'.format(dummy), rotateOrder)
            dummy = mc.parent(dummy, ct.controlTemplate, relative=True)[0]
            dummy = mc.parent(dummy, world=True, a=True)[0]

            worldPos = mc.getAttr('{}.translate'.format(dummy))[0]
            worldRot = mc.getAttr('{}.rotate'.format(dummy))[0]
            worldScl = mc.getAttr('{}.scale'.format(dummy))[0]
            worldShr = mc.getAttr('{}.shear'.format(dummy))[0]

            rotateToJointOrient(root)

            # here normalize the scale
            # Create the attribute to specified that this node is a control root
            #
            ObjectType(root).setRigNodeType('root', lockIt=True)
            # Set the world transformations on the root previously created
            #
            mc.setAttr('{}.translate'.format(
                root), worldPos[0], worldPos[1], worldPos[2], type='double3')
            mc.setAttr('{}.rotate'.format(
                root), worldRot[0], worldRot[1], worldRot[2], type='double3')
            mc.setAttr('{}.scale'.format(
                root), worldScl[0], worldScl[1], worldScl[2], type='double3')
            mc.setAttr('{}.shear'.format(
                root), worldShr[0], worldShr[1], worldShr[2], type='double3')

            if mc.objExists(dummy):
                mc.delete(dummy)

            # copy the global direction of the joint
            #
            # writeNodeAxis(root, verbose=False)
            copyNodeAxis(controlTemplate, root)

            if side == 'oppositeSide':
                if 'transform' == mirrorType:
                    # new method
                    #
                    oppositeSideRoot = mc.mirrorJoint(root, mirrorYZ=True)[0]
                    oppositeSideRootMatrix = rotateMatrixFromNodeAxis(
                        root, symetryAxis='x', verbose=False)
                    oppositeSideRootWorldEulerRotation = om.MTransformationMatrix(
                        oppositeSideRootMatrix).rotation()
                    oppositeSideRootWorldEulerRotation.reorderIt(rotateOrder)
                    oppositeSideRootWorldRot = [degrees(oppositeSideRootWorldEulerRotation.x), degrees(
                        oppositeSideRootWorldEulerRotation.y), degrees(oppositeSideRootWorldEulerRotation.z)]
                    jointOrientToRotate(oppositeSideRoot)
                    # mc.xform(oppositeSideRoot, a=True, ws=True, ro=[oppositeSideRootWorldRot[0], oppositeSideRootWorldRot[1], oppositeSideRootWorldRot[2]])
                    mc.setAttr('{}.rotate'.format(oppositeSideRoot), oppositeSideRootWorldRot[0],
                               oppositeSideRootWorldRot[1], oppositeSideRootWorldRot[2],
                               type='double3')

                    rotateToJointOrient(oppositeSideRoot)
                    # Mirror the shear
                    #
                    oppositeSideRootShearMatrix = shearMatrixFromNodeAxis(root,
                                                                          symetryAxis='x',
                                                                          verbose=False)
                    oppositeSideRootWorldShear = om.MTransformationMatrix(oppositeSideRootShearMatrix).shear(om.MSpace.kTransform)
                    mc.setAttr('{}.shear'.format(oppositeSideRoot),
                               oppositeSideRootWorldShear[0],
                               oppositeSideRootWorldShear[1],
                               oppositeSideRootWorldShear[2],
                               type='double3')

                    mc.delete(root)
                    root = mc.rename(oppositeSideRoot, rootName)
                    # Write the global direction of the joint
                    #
                    # writeNodeAxis(root, verbose=False)
                    copyNodeAxis(controlTemplate, root)
                elif 'joint' == mirrorType:
                    oppositeSideRoot = mc.mirrorJoint(
                        root, mirrorBehavior=True, mirrorYZ=True, searchReplace=[location, inverseLocation])[0]
                    mc.delete(root)
                    root = mc.rename(oppositeSideRoot, rootName)
                    # Write the global direction of the joint
                    #
                    writeNodeAxis(root, verbose=False)
                elif 'orientation' == mirrorType:  # For the specular by example
                    oppositeSideRoot = mc.mirrorJoint(root, mirrorYZ=True, searchReplace=[
                                                        location, inverseLocation])[0]
                    mc.delete(root)
                    root = mc.rename(oppositeSideRoot, rootName)
                    # Write the global direction of the joint
                    #
                    writeNodeAxis(root, verbose=False)

                elif 'translate' == mirrorType:
                    oppositeSideRoot = mc.mirrorJoint(root, mirrorYZ=True, searchReplace=[
                                                        location, inverseLocation])[0]
                    mc.delete(root)
                    tmpDum = mc.createNode('transform')
                    tmpDumRoot = mc.createNode('transform')
                    mc.parent(tmpDum, tmpDumRoot)
                    mc.delete(mc.parentConstraint(
                        oppositeSideRoot, tmpDum, mo=False))
                    mc.setAttr(tmpDum+'.rotateY', 180)
                    mc.delete(mc.orientConstraint(
                        tmpDum, oppositeSideRoot, mo=False))
                    mc.delete(tmpDumRoot)
                    mc.setAttr(oppositeSideRoot+'.jointOrientY',
                                 mc.getAttr(oppositeSideRoot+'.rotateY'))
                    mc.setAttr(oppositeSideRoot+'.rotateY', 0)
                    root = mc.rename(oppositeSideRoot, rootName)
                    # Write the global direction of the joint
                    #
                    writeNodeAxis(root, verbose=False)

            # Here we keep the scale so we can have non uniform deformations like in the eyes
            # By freezing the matrix, we have the rotation transferred to the jointOrient
            #
            mc.makeIdentity(root, apply=True, t=False, r=True, s=False)
            # connect the cgGroup members visibility attrs to the root joint
            #
            mc.connectAttr('{}.membersVisibility'.format(
                self.controlGroup), '{}.visibility'.format(root))
            # Creation of the mirror root
            #
            mirroredRoot = ''
            if isMirrored and side == 'bothSide':
                if verbose:
                    print('\tMirrorType: {}'.format(mirrorType))
                if 'transform' == mirrorType:
                    mirroredRoot = mc.mirrorJoint(root, mirrorYZ=True, searchReplace=[
                                                    location, inverseLocation])[0]
                    # new method
                    #
                    mirrorRootMirrorMatrix = rotateMatrixFromNodeAxis(
                        root, symetryAxis='x', verbose=False)
                    mirrorWorldEulerRotation = om.MTransformationMatrix(
                        mirrorRootMirrorMatrix).rotation()
                    mirrorWorldEulerRotation.reorderIt(rotateOrder)
                    mirrorWorldRot = [degrees(mirrorWorldEulerRotation.x), degrees(
                        mirrorWorldEulerRotation.y), degrees(mirrorWorldEulerRotation.z)]
                    jointOrientToRotate(mirroredRoot)
                    # mc.xform(mirroredRoot, a=True, ws=True, ro=[mirrorWorldRot[0], mirrorWorldRot[1], mirrorWorldRot[2]])
                    mc.setAttr('{}.rotate'.format(
                        mirroredRoot), mirrorWorldRot[0], mirrorWorldRot[1], mirrorWorldRot[2], type='double3')

                    ###########################################################
                    # if mirroredRoot == 'root_eyeBall_R':
                    #     print '_DEBUG_:', mirroredRoot, mirrorWorldRot
                    #     return
                    ###########################################################
                    rotateToJointOrient(mirroredRoot)
                    # Write the global direction of the joint
                    #
                    copyNodeAxis(root, mirroredRoot)
                    # Mirror the shear
                    #
                    mirrorShearMatrix = shearMatrixFromNodeAxis(
                        root, symetryAxis='x', verbose=False)
                    mirrorWorldShear = om.MTransformationMatrix(
                        mirrorShearMatrix).shear(om.MSpace.kTransform)
                    mc.setAttr('{}.shear'.format(
                        mirroredRoot), mirrorWorldShear[0], mirrorWorldShear[1], mirrorWorldShear[2], type='double3')
                elif 'joint' == mirrorType:
                    mirroredRoot = mc.mirrorJoint(root, mirrorBehavior=True, mirrorYZ=True, searchReplace=[
                                                    location, inverseLocation])[0]
                    # Write the global direction of the joint
                    #
                    writeNodeAxis(mirroredRoot, verbose=False)
                elif 'orientation' == mirrorType:  # For the specular by example
                    mirroredRoot = mc.mirrorJoint(root, mirrorYZ=True, searchReplace=[
                                                    location, inverseLocation])[0]
                    # Write the global direction of the joint
                    #
                    writeNodeAxis(mirroredRoot, verbose=False)

                elif 'translate' == mirrorType:
                    mirroredRoot = mc.mirrorJoint(root, mirrorYZ=True, searchReplace=[
                                                    location, inverseLocation])[0]
                    tmpDum = mc.createNode('transform')
                    tmpDumRoot = mc.createNode('transform')
                    mc.parent(tmpDum, tmpDumRoot)
                    mc.delete(mc.parentConstraint(
                        mirroredRoot, tmpDum, mo=False))
                    mc.setAttr(tmpDum+'.rotateY', 180)
                    mc.delete(mc.orientConstraint(
                        tmpDum, mirroredRoot, mo=False))
                    mc.delete(tmpDumRoot)
                    mc.setAttr(mirroredRoot+'.jointOrientY',
                                 mc.getAttr(mirroredRoot+'.rotateY'))
                    mc.setAttr(mirroredRoot+'.rotateY', 0)

                    # Write the global direction of the joint
                    #
                    writeNodeAxis(mirroredRoot, verbose=False)

                mc.setAttr('{}.drawStyle'.format(mirroredRoot), 2)
                mc.setAttr('{}.radius'.format(mirroredRoot), 0)
                mc.setAttr('{}.rotateOrder'.format(
                    mirroredRoot), rotateOrder)
                # Create the attribute to specified that this node is a control root
                #
                ObjectType(mirroredRoot).setRigNodeType(
                    'root', lockIt=True)
                # connect the cgGroup members visibility attrs to the root joint
                #
                mc.connectAttr('{}.membersVisibility'.format(
                    self.controlGroup), '{}.visibility'.format(mirroredRoot))
            # Creation of the control
            #
            buildType = ct.builtType
            ctrlName = controlPrefix + '_' + baseName + index + location
            if side == 'oppositeSide':
                ctrlName = controlPrefix + '_' + baseName + index + inverseLocation

            if freeNaming == True:
                ctrlName = rootName.replace('root_', 'c_')

            control = ''
            mirroredControl = ''
            if 'transform' == buildType:
                control = mc.createNode(
                    'transform', name=ctrlName, parent=root)
            elif 'joint' == buildType:
                control = mc.createNode('joint', name=ctrlName, parent=root)
                mc.setAttr('{}.segmentScaleCompensate'.format(
                    control), False, lock=True)
                mc.setAttr('{}.drawStyle'.format(control), 0)
                mc.setAttr('{}.radius'.format(control), 0)
            mc.setAttr('{}.rotateOrder'.format(control), rotateOrder)

            # Write the global direction of the joint
            #
            copyNodeAxis(root, control)

            # Tune the displayOverrides
            #
            if side != 'oppositeSide':
                setDisplayOverrides(control, enable=True, displayType='Normal', levelOfDetail='Full',
                                               color=ct.locationsColorIndexes[ct.validLocations.index(ct.location)])
            else:
                setDisplayOverrides(control, enable=True, displayType='Normal', levelOfDetail='Full',
                                               color=ct.locationsColorIndexes[ct.validLocations.index(ct.inverseLocation(ct.location))])
            # Add to the controlSet
            # ['ctrlSet', 'skinSet']
            ctrlSet = self.getControlSet('ctrlSet')
            if mc.objExists(ctrlSet) and self.doCtrlSet and addToCtrlSet:
                mc.sets(control, forceElement=ctrlSet)
            # Create the attribute to specified that this node is a control
            #
            # Add the attributes
            #
            self.addControlAttributes(control, ct)
            mc.setAttr('{}.visibility'.format(control), cb=True)

            if side == 'oppositeSide':
                # This node is on the opposite side, immediatly, we set its mirrorSide to the opposite of the master control
                #
                mc.setAttr('{}.mirrorSide'.format(control), lock=False)
                mc.setAttr('{}.mirrorSide'.format(
                    control), ControlTemplate.validInverseLocations.index(ct.location))
                mc.setAttr('{}.mirrorSide'.format(control), lock=True)

            # Connection to the cgGroup
            #
            idx = getMultiFirstAvailableIndex(
                self.controlGroup, 'members')
            mc.connectAttr('{}.message'.format(
                control), '{0}.members[{1}]'.format(self.controlGroup, idx))
            # Connect the rotateOrders
            #
            mc.connectAttr('{}.rotateOrder'.format(
                control), '{}.rotateOrder'.format(root))
            # Handle the display of this control (shape, handle) based on the nsTpl attribute iconType
            #
            if addToCtrlSet:
                if side == 'oppositeSide':
                    ControlGroup.addShapeToControl(
                        control, controlTemplate, iconType, mirrorType, mirror=True)
                else:
                    ControlGroup.addShapeToControl(
                        control, controlTemplate, iconType, mirrorType, mirror=False)

            # search empty index to connect the nsTpl
            #
            idx = getMultiFirstAvailableIndex(control, 'nodesId')
            mc.setAttr('{0}.nodesId[{1}]'.format(
                control, idx), 'nsTpl', type='string')
            mc.connectAttr('{}.message'.format(
                ct.controlTemplate), '{0}.nodes[{1}]'.format(control, idx))
            # search empty index to connect the root previously created
            #
            idx = getMultiFirstAvailableIndex(control, 'nodesId')
            mc.setAttr('{0}.nodesId[{1}]'.format(
                control, idx), 'root', type='string')
            mc.connectAttr('{}.message'.format(
                root), '{0}.nodes[{1}]'.format(control, idx))
            # connection of the parentScale attribute
            #
            ControlGroup.connectParentScale(control, root)
            if isMirrored and side == 'bothSide':
                if 'transform' == buildType:
                    mirroredControl = mc.createNode('transform', name=ctrlName.replace(
                        location, inverseLocation), parent=mirroredRoot)
                elif 'joint' == buildType:
                    mirroredControl = mc.createNode('joint', name=ctrlName.replace(
                        location, inverseLocation), parent=mirroredRoot)
                    mc.setAttr('{}.segmentScaleCompensate'.format(
                        mirroredControl), False, lock=True)
                    mc.setAttr('{}.drawStyle'.format(mirroredControl), 0)
                    mc.setAttr('{}.radius'.format(mirroredControl), 0)
                mc.setAttr('{}.rotateOrder'.format(
                    mirroredControl), rotateOrder)

                # Write the global direction of the joint
                #
                copyNodeAxis(mirroredRoot, mirroredControl)
                # Tune the displayOverrides
                #
                setDisplayOverrides(mirroredControl, enable=True, displayType='Normal', levelOfDetail='Full',
                                               color=ct.locationsColorIndexes[ct.validLocations.index(ct.inverseLocation(ct.location))])
                # Add to the controlSet
                # ['ctrlSet', 'skinSet']
                ctrlSet = self.getControlSet('ctrlSet')
                if mc.objExists(ctrlSet) and self.doCtrlSet and addToCtrlSet:
                    mc.sets(mirroredControl, forceElement=ctrlSet)
                # Create the attribute to specified that this node is a control
                #
                # Add the attributes
                #
                self.addControlAttributes(mirroredControl, ct)
                mc.setAttr('{}.visibility'.format(mirroredControl), cb=True)
                # This node is a mirror, immediatly, we set its mirrorSide to the opposite of the master control
                #
                mc.setAttr('{}.mirrorSide'.format(
                    mirroredControl), lock=False)
                mc.setAttr('{}.mirrorSide'.format(
                    mirroredControl), ControlTemplate.validInverseLocations.index(ct.location))
                mc.setAttr('{}.mirrorSide'.format(
                    mirroredControl), lock=True)
                # Connect the rotateOrders
                #
                mc.connectAttr('{}.rotateOrder'.format(
                    mirroredControl), '{}.rotateOrder'.format(mirroredRoot))
                # Handle the display of this mirrored control (shape, handle) based on the nsTpl attribute iconType
                #
                if addToCtrlSet:
                    ControlGroup.addShapeToControl(
                        mirroredControl, controlTemplate, iconType, mirrorType, mirror=True)
                # Connections to the control
                #
                # search empty index to connect the nsTpl
                #
                idx = getMultiFirstAvailableIndex(
                    mirroredControl, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    mirroredControl, idx), 'nsTpl', type='string')
                mc.connectAttr('{}.message'.format(
                    ct.controlTemplate), '{0}.nodes[{1}]'.format(mirroredControl, idx))
                # search empty index to connect the root
                #
                idx = getMultiFirstAvailableIndex(
                    mirroredControl, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    mirroredControl, idx), 'root', type='string')
                mc.connectAttr('{}.message'.format(
                    mirroredRoot), '{0}.nodes[{1}]'.format(mirroredControl, idx))
                # connection of the parentScale attribute
                #
                ControlGroup.connectParentScale(mirroredControl, mirroredRoot)
                # Mirror infos
                #
                idx = getMultiFirstAvailableIndex(
                    control, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    control, idx), 'mirror', type='string')
                mc.connectAttr('{}.message'.format(
                    mirroredControl), '{0}.nodes[{1}]'.format(control, idx))

                idx = getMultiFirstAvailableIndex(
                    mirroredControl, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    mirroredControl, idx), 'mirror', type='string')
                mc.connectAttr('{}.message'.format(
                    control), '{0}.nodes[{1}]'.format(mirroredControl, idx))
                # Connection to the cgGroup
                #
                idx = getMultiFirstAvailableIndex(
                    self.controlGroup, 'members')
                mc.connectAttr('{}.message'.format(
                    mirroredControl), '{0}.members[{1}]'.format(self.controlGroup, idx))

            # Creation of the skin joint
            #
            skinName = skPrefix + '_' + baseName + index + location
            if side == 'oppositeSide':
                skinName = skPrefix + '_' + baseName + index + inverseLocation

            if freeNaming == True:
                skinName = rootName.replace('root_', 'sk_')

            sk = mc.createNode('joint', name=skinName, parent=root)
            setLabelsToJoints([sk])
            mc.setAttr('{}.segmentScaleCompensate'.format(
                sk), False, lock=True)
            if addToSkinSet:
                mc.setAttr('{}.drawStyle'.format(sk), 0)
            else:
                mc.setAttr('{}.drawStyle'.format(sk), 2)  # Hide the joint

            # Write the global direction of the joint
            #
            copyNodeAxis(control, sk)

            # Add to the controlSet
            # ['ctrlSet', 'skinSet']
            #
            skinSet = self.getControlSet('skinSet')
            if mc.objExists(skinSet) and self.doSkinSet and addToSkinSet:
                mc.sets(sk, forceElement=skinSet)
            # Create the attribute to specified that this node is a skinjoint
            #
            ObjectType(sk).setRigNodeType('skin', lockIt=True)
            ControlGroup.connectControlToSkin(control, sk)
            # Connections of the sk to the control
            #
            idx = getMultiFirstAvailableIndex(control, 'nodesId')
            mc.setAttr('{0}.nodesId[{1}]'.format(
                control, idx), 'sk', type='string')
            mc.connectAttr('{}.message'.format(
                sk), '{0}.nodes[{1}]'.format(control, idx))
            mirroredSk = ''
            if isMirrored and side == 'bothSide':
                mirroredSk = mc.createNode('joint', name=skinName.replace(
                    location, inverseLocation), parent=mirroredRoot)
                setLabelsToJoints([mirroredSk])
                mc.setAttr('{}.segmentScaleCompensate'.format(
                    mirroredSk), False, lock=True)
                mc.setAttr('{}.drawStyle'.format(mirroredSk), 0)
                if addToSkinSet:
                    mc.setAttr('{}.drawStyle'.format(mirroredSk), 0)
                else:
                    mc.setAttr('{}.drawStyle'.format(
                        mirroredSk), 2)  # Hide the joint

                # Write the global direction of the joint
                #
                copyNodeAxis(mirroredControl, mirroredSk)

                # Add to the controlSet
                # ['ctrlSet', 'skinSet']
                #
                skinSet = self.getControlSet('skinSet')
                if mc.objExists(skinSet) and self.doSkinSet and addToSkinSet:
                    mc.sets(mirroredSk, forceElement=skinSet)
                # Create the attribute to specified that this node is a skinjoint
                #
                ObjectType(mirroredSk).setRigNodeType(
                    'skin', lockIt=True)
                ControlGroup.connectControlToSkin(mirroredControl, mirroredSk)
                # Connections of the mirrored sk to the mirrored control
                #
                idx = getMultiFirstAvailableIndex(
                    mirroredControl, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    mirroredControl, idx), 'sk', type='string')
                mc.connectAttr('{}.message'.format(
                    mirroredSk), '{0}.nodes[{1}]'.format(mirroredControl, idx))

            # Save the current transformation of the control as bindPose
            #
            Control(control).setBindPose()
            if isMirrored and side == 'bothSide':
                Control(mirroredControl).setBindPose()
            # Creation of the pose node
            #
            if ct.buildPoseNode:
                Control(control).addPoseNode()
                if isMirrored and side == 'bothSide':
                    Control(mirroredControl).addPoseNode()
            # Here, we build the hierarchy the method return a Maya object
            #
            # Can be call with an Object or a Maya node, here call with a node, always return a Control object
            parentControl = self.getFirstBuiltParent(control)
            if parentControl:
                parentSkin = Control(parentControl).getNode('sk')
                if verbose:
                    print ('\tParent control ', parentControl, ' sk: ', parentSkin)
                # Creation of a dummy to be sur that the world transform will be retreive especially for the scale with the shear
                #
                parentingDummy = mc.createNode(
                    'transform', name='parentingDummy_{}'.format(root))
                mc.setAttr('{}.rotateOrder'.format(
                    parentingDummy), rotateOrder)
                parentingDummy = mc.parent(
                    parentingDummy, root, relative=True)[0]
                parentingDummy = mc.parent(
                    parentingDummy, parentSkin, a=True)[0]
                # Now parenting the root
                #
                mc.parent(root, parentSkin, relative=True)
                if not mc.isConnected('{}.scale'.format(parentSkin), '{}.inverseScale'.format(root)):
                    mc.connectAttr('{}.scale'.format(
                        parentSkin), '{}.inverseScale'.format(root), force=True)
                # Replace all the local transformation everything
                #
                pos = mc.getAttr('{}.translate'.format(parentingDummy))[0]
                rot = mc.getAttr('{}.rotate'.format(parentingDummy))[0]
                scl = mc.getAttr('{}.scale'.format(parentingDummy))[0]
                shr = mc.getAttr('{}.shear'.format(parentingDummy))[0]

                mc.setAttr('{}.translate'.format(root),
                             pos[0], pos[1], pos[2], type='double3')
                mc.setAttr('{}.rotate'.format(root),
                             rot[0], rot[1], rot[2], type='double3')
                mc.setAttr('{}.scale'.format(root),
                             scl[0], scl[1], scl[2], type='double3')
                mc.setAttr('{}.shear'.format(root),
                             shr[0], shr[1], shr[2], type='double3')
                mc.setAttr('{}.jointOrient'.format(
                    root), .0, .0, .0, type='double3')

                mc.delete(parentingDummy)
                # Connections of the parent to the control
                #
                idx = getMultiFirstAvailableIndex(
                    control, 'nodesId')
                mc.setAttr('{0}.nodesId[{1}]'.format(
                    control, idx), 'parent', type='string')
                mc.connectAttr('{}.message'.format(
                    parentControl), '{0}.nodes[{1}]'.format(control, idx))
                if isMirrored and side == 'bothSide':
                    mirroredParentControl = self.getFirstBuiltParent(
                        mirroredControl)
                    if mirroredParentControl:
                        mirroredParentSkin = Control(
                            mirroredParentControl).getNode('sk')
                        if verbose:
                            print ('\tParent mirror control ', mirroredParentControl, ' mirror sk: ', mirroredParentSkin)
                        # Creation of a dummy to be sur that the world transform will be retreive especially for the scale with the shear
                        #
                        mirrorParentingDummy = mc.createNode(
                            'transform', name='mirrorParentingDummy_{}'.format(mirroredRoot))
                        mc.setAttr('{}.rotateOrder'.format(
                            mirrorParentingDummy), rotateOrder)
                        mirrorParentingDummy = mc.parent(
                            mirrorParentingDummy, mirroredRoot, relative=True)[0]
                        mirrorParentingDummy = mc.parent(
                            mirrorParentingDummy, mirroredParentSkin, a=True)[0]
                        # Now parenting the root
                        #
                        mc.parent(
                            mirroredRoot, mirroredParentSkin, relative=True)
                        if not mc.isConnected('{}.scale'.format(mirroredParentSkin), '{}.inverseScale'.format(mirroredRoot)):
                            mc.connectAttr('{}.scale'.format(
                                mirroredParentSkin), '{}.inverseScale'.format(mirroredRoot), force=True)
                        # Replace all the local transformation everything
                        #
                        pos = mc.getAttr(
                            '{}.translate'.format(mirrorParentingDummy))[0]
                        rot = mc.getAttr(
                            '{}.rotate'.format(mirrorParentingDummy))[0]
                        scl = mc.getAttr(
                            '{}.scale'.format(mirrorParentingDummy))[0]
                        shr = mc.getAttr(
                            '{}.shear'.format(mirrorParentingDummy))[0]

                        mc.setAttr('{}.translate'.format(
                            mirroredRoot), pos[0], pos[1], pos[2], type='double3')
                        mc.setAttr('{}.rotate'.format(
                            mirroredRoot), rot[0], rot[1], rot[2], type='double3')
                        mc.setAttr('{}.scale'.format(
                            mirroredRoot), scl[0], scl[1], scl[2], type='double3')
                        mc.setAttr('{}.shear'.format(
                            mirroredRoot), shr[0], shr[1], shr[2], type='double3')
                        mc.setAttr('{}.jointOrient'.format(
                            mirroredRoot), .0, .0, .0, type='double3')

                        mc.delete(mirrorParentingDummy)
                        # Connections of the parent to the control
                        #
                        idx = getMultiFirstAvailableIndex(
                            mirroredControl, 'nodesId')
                        mc.setAttr('{0}.nodesId[{1}]'.format(
                            mirroredControl, idx), 'parent', type='string')
                        mc.connectAttr('{}.message'.format(
                            mirroredParentControl), '{0}.nodes[{1}]'.format(mirroredControl, idx))

                    return [control, mirroredControl]
            else:
                self.rigGroup = self.getRigGroup()
                if not mc.objExists(self.rigGroup):
                    self.rigGroup = self.createRigGroup()
                root = mc.parent(root, self.rigGroup)[0]
                if isMirrored and side == 'bothSide':
                    mirroredRoot = mc.parent(mirroredRoot, self.rigGroup)[0]
                    return [control, mirroredControl]

            return [control]

    @staticmethod
    def addShapeToControl(control, sourceControl, iconType='handle', mirrorType='joint', mirror=False):
        """
        Add a shape if available to the controls
        :param Maya dagNode control: the control object
        :param ControlTemplate controlTemplate: the control nsTpl object
        :param boolean mirror: if the shape from tpl is mirrored
        """
        if not all([mc.objExists(control), isDagNode(control), mc.objExists(sourceControl) and isDagNode(sourceControl)]):
            return

        locationSuffix = NameParser(control).getNameSuffix()
        if isValidSuffixLocation(locationSuffix):
            invLocationSuffix = inverseLocationSuffix(locationSuffix)
            locationSuffix = NameParser.tokensSeparator + locationSuffix
            invLocationSuffix = NameParser.tokensSeparator + invLocationSuffix
        else:
            locationSuffix = ''
            invLocationSuffix = ''

        selectHandlePos = om.MPoint([mc.getAttr('{}.selectHandleX'.format(sourceControl)), mc.getAttr(
            '{}.selectHandleY'.format(sourceControl)), mc.getAttr('{}.selectHandleZ'.format(sourceControl)), 1.0])
        if iconType == 'shape' or iconType == 'locator':
            ctShapes = mc.listRelatives(
                sourceControl, s=True, ni=True, pa=True) or []
            if ctShapes:
                for ctShape in ctShapes:
                    if mc.objExists(ctShape) and mc.objectType(ctShape, isAType='shape'):
                        if not mirror:
                            controlShape = addShape(ctShape,
                                                    control,
                                                    space='world')
                        else:
                            if mirrorType != 'orientation':
                                controlShape = addShape(ctShape,
                                                        control,
                                                        space='world',
                                                        symmetry=[-1, 1, 1])
                            else:
                                controlShape = addShape(ctShape,
                                                        control,
                                                        space='local')

                        mc.setAttr('{}.visibility'.format(
                            controlShape), True)
            else:
                loc = mc.createNode('locator', name=(
                    control + 'Shape'), p=control)
                if mirror:
                    otherSide = control.replace(
                        locationSuffix, invLocationSuffix)
                    selectHandlePos = mirrorLocalPosition(otherSide, control,
                                                          localPosition=selectHandlePos,
                                                          symmetryAxis=om.MVector.kXaxisVector)

                mc.setAttr('{}.localPositionX'.format(loc),
                           selectHandlePos.x)
                mc.setAttr('{}.localPositionY'.format(loc),
                           selectHandlePos.y)
                mc.setAttr('{}.localPositionZ'.format(loc),
                           selectHandlePos.z)

            cShapes = mc.listRelatives(control, s=True,
                                       ni=True, pa=True) or []
            if cShapes:
                for cShape in cShapes:
                    mc.connectAttr(
                        control + '.overrideEnabled', cShape + '.overrideEnabled')
                    mc.connectAttr(
                        control + '.overrideDisplayType', cShape + '.overrideDisplayType')
                    mc.connectAttr(
                        control + '.overrideLevelOfDetail', cShape + '.overrideLevelOfDetail')
                    mc.connectAttr(
                        control + '.overrideShading', cShape + '.overrideShading')
                    mc.connectAttr(
                        control + '.overrideTexturing', cShape + '.overrideTexturing')
                    mc.connectAttr(
                        control + '.overridePlayback', cShape + '.overridePlayback')
                    mc.connectAttr(
                        control + '.overrideVisibility', cShape + '.overrideVisibility')
                    mc.connectAttr(
                        control + '.overrideColor', cShape + '.overrideColor')

        elif iconType == 'handle':
            mc.setAttr('{}.displayHandle'.format(control), True)
            # Retreive the first Shape under the controlTemplate and check if it's a locator that will indicate the position of the displayHandle
            ctShape = getFirstShape(sourceControl)
            if all([mc.objExists(ctShape), mc.objectType(ctShape, isAType='shape'),
                    mc.objectType(ctShape, isAType='locator')]):
                locatorPos = om.MPoint([mc.getAttr('{}.localPositionX'.format(ctShape)), mc.getAttr(
                    '{}.localPositionY'.format(ctShape)), mc.getAttr('{}.localPositionZ'.format(ctShape)), 1.0])
                if mirror:
                    otherSide = control.replace(
                        locationSuffix, invLocationSuffix)
                    locatorPos = mirrorLocalPosition(
                        otherSide, control, localPosition=locatorPos, symmetryAxis=om.MVector.kXaxisVector)

                mc.setAttr('{}.selectHandleX'.format(
                    control), locatorPos.x)
                mc.setAttr('{}.selectHandleY'.format(
                    control), locatorPos.y)
                mc.setAttr('{}.selectHandleZ'.format(
                    control), locatorPos.z)
            else:
                if mirror:
                    otherSide = control.replace(
                        locationSuffix, invLocationSuffix)
                    selectHandlePos = mirrorLocalPosition(
                        otherSide, control, localPosition=selectHandlePos, symmetryAxis=om.MVector.kXaxisVector)

                mc.setAttr('{}.selectHandleX'.format(
                    control), selectHandlePos.x)
                mc.setAttr('{}.selectHandleY'.format(
                    control), selectHandlePos.y)
                mc.setAttr('{}.selectHandleZ'.format(
                    control), selectHandlePos.z)

    def controlToTipJoint(self, controlTemplate, verbose=False):
        """In the case of a control at the end of a chain, we can decide to transform it in a tip joint, without sk and c
        """
        jnts = []
        ct = ControlTemplate(controlTemplate)
        if ct.isBuilt:
            # Check if there is a child nsTpl
            #
            children = ct.listRelativesTemplate(children=True)
            if not children:
                controls = ct.getControls()
                if controls:
                    for ctrl in controls:
                        c = Control(ctrl)
                        if c.isPoseNodeExists():
                            c.removePoseNode()
                        root = c.getNode('root')
                        sk = c.getNode('sk')
                        cg = c.getControlGroup()  # @UnusedVariable
                        try:
                            mc.delete(c.control)
                            mc.delete(sk)
                            prefix = NameParser(root).getNamePrefix()
                            rootNewName = root.replace(prefix, 'jnt', 1)
                            jnt = mc.rename(root, rootNewName)
                            ObjectType(jnt).setRigNodeType(
                                'joint', lockIt=True)
                            jnts.append(jnt)
                        except Exception:
                            raise

        return jnts

    def addControl(self, obj):
        """Add a control to a cg without any nsTpl, some functionnalities won't be available
        :param Maya dagNode obj
        :return: str new control or None
        :rtyp: str
        """
        if mc.objExists(obj) and mc.objectType(obj, isAType='dagNode'):
            self.updateMembers()
            if obj in self.members:
                return None

            ControlGroup.createControlAttributes(obj)

            c = Control(obj)
            ro = c.getNode('root')
            if mc.objExists(ro):
                # ParentScale is usefull only if the added control is an old templated control, or a joint
                ControlGroup.connectParentScale(obj, ro)
            else:
                if mc.objectType(obj, isAType='transform'):
                    if mc.objectType(obj, isAType='joint'):
                        if mc.attributeQuery('parentScale', node=obj, exists=True):
                            parentScaleDefault = True
                            mc.addAttr(obj + '.parentScale',
                                         edit=True, dv=parentScaleDefault)
                            ControlGroup.connectParentScale(obj, obj)
                    else:
                        if mc.attributeQuery('parentScale', node=obj, exists=True) and not mc.referenceQuery(obj, isNodeReferenced=True):
                            mc.deleteAttr(obj, attribute='parentScale')

            # connect the cgGroup members visibility attrs to the root joint
            #
            if not mc.objExists(ro):
                if not isPlugConnected('{}.visibility'.format(obj), 0) and mc.getAttr('{}.visibility'.format(obj), se=True):
                    try:
                        mc.connectAttr('{}.membersVisibility'.format(
                            self.controlGroup), '{}.visibility'.format(obj))
                        mc.setAttr('{}.visibility'.format(
                            obj), lock=True, keyable=False)
                    except Exception:
                        pass
            else:
                if not isPlugConnected('{}.visibility'.format(ro), 0) and mc.getAttr('{}.visibility'.format(obj), se=True):
                    try:
                        mc.connectAttr('{}.membersVisibility'.format(
                            self.controlGroup), '{}.visibility'.format(ro))
                        mc.setAttr('{}.visibility'.format(
                            ro), lock=True, keyable=False)
                    except Exception:
                        pass

            # Add to the controlSet
            # ['ctrlSet', 'skinSet']
            ctrlSet = self.getControlSet('ctrlSet')
            if mc.objExists(ctrlSet) and self.doCtrlSet:
                mc.sets(obj, forceElement=ctrlSet)

            # Connection to the cgGroup
            #
            idx = getMultiFirstAvailableIndex(
                self.controlGroup, 'members')
            mc.connectAttr('{}.message'.format(
                obj), '{0}.members[{1}]'.format(self.controlGroup, idx))
            # Save the current transformation of the control as bindPose
            #
            Control(obj).setBindPose()

            if mc.objectType(obj, isAType='transform'):
                writeNodeAxis(obj, False)

            self.updateMembers()

            return obj

        return None

    def goToBindPoseCg(self, progressBar=None):
        """Set the control group to the curent registered pose for all the controls
        """
        if mc.objExists(self.controlGroup):
            self.updateMembers()

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)

            for i, member in enumerate(self.members):
                c = Control(member)
                c.goToBindPose()

                if isinstance(progressBar, QProgressBar):
                    progressBar.setValue(i)

            if isinstance(progressBar, QProgressBar):
                progressBar.reset()
                progressBar.setVisible(False)"""

    def setBindPoseCg(self, progressBar=None):
        """Set the bindPose of all the controls of the control group
        """
        if mc.objExists(self.controlGroup):
            self.updateMembers()

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)"""

            for i, member in enumerate(self.members):
                c = Control(member)
                c.setBindPose()

                """if isinstance(progressBar, QProgressBar):
                    progressBar.setValue(i)"""

            """if isinstance(progressBar, QProgressBar):
                progressBar.reset()
                progressBar.setVisible(False)"""

    def resetBindPoseCg(self, progressBar=None):
        """Reset the bindPose to the default attribute values for all the cg controls
        :param QProgressBar progressBar: an optionnal progressBar
        """
        if mc.objExists(self.controlGroup):
            self.updateMembers()

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)"""

            for i, member in enumerate(self.members):
                c = Control(member)
                c.resetBindPose()

                """if isinstance(progressBar, QProgressBar):
                    progressBar.setValue(i)"""

            """if isinstance(progressBar, QProgressBar):
                progressBar.reset()
                progressBar.setVisible(False)"""

    def createPoseCg(self, driverPlug, relative=False, staticCurves=True, inTangentType='linear',
                     outTangentType='linear', preInfinity='Constant', postInfinity='Constant',
                     progressBar=None, verbose=False):
        """Transfert all the current values of the controls to the pose node, if a driver is specified, a driven key is created
        :param str driverPlug: if specified a driven key is created
        :param str driverValue: if not specified the driven key is created with the current value of the driver
        :param QProgressBar progressBar: an optionnal progressBar
        :param boolean verbose: debug informations
        """
        if mc.objExists(self.controlGroup):
            if not mc.objExists(driverPlug):
                om.MGlobal.displayError(
                    '[createPoseCg] The supplied driver plug {} does not exist'.format(driverPlug))

            self.updateMembers()  # To be sure that we are up-to-date with the Maya scene

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)"""

            ctrlSet = self.getControlSet('ctrlSet')

            for i, member in enumerate(self.members):
                c = Control(member)
                ctrl = c.getControl()

                if not isMemberOfSets(ctrl, theSets=(ctrlSet,)):
                    continue

                c.controlToPose(forcePoseNode=True,
                                relative=relative, verbose=False)
                poseNode = c.getNode('pose')
                currentValue = mc.getAttr(driverPlug)
                c.createPose(driverPlug, driverValue=currentValue, driven=poseNode, staticCurves=staticCurves,
                             itt=inTangentType, ott=outTangentType, preInfinity=preInfinity, postInfinity=postInfinity, verbose=False)

                """if isinstance(progressBar, QProgressBar):
                    progressBar.setFormat('Create pose for {} %p%'.format(member))
                    progressBar.setValue(i)"""

            """if isinstance(progressBar, QProgressBar):
                progressBar.reset()
                progressBar.setVisible(False)"""

    def removePoseCg(self, driverPlug=None, progressBar=None, verbose=False):
        """Remove all the pose created with this driver
        It could be quiet long to execute, because all the down stream graph must be analyze to search for the driven plugs
        :param str driverPlug: if specified a driven key is created
        :param QProgressBar progressBar: an optionnal progressBar
        :param boolean verbose: debug informations
        """
        if mc.objExists(self.controlGroup):
            if checkPlug(driverPlug):
                driverNode = nodeFromPlug(driverPlug)
                driverAttr = mc.attributeName(driverPlug, l=True)
                driverPlug = driverNode + '.' + driverAttr
                self.updateMembers()  # To be sure that we are up-to-date with the Maya scene

                """if isinstance(progressBar, QProgressBar):
                    progressBar.setMinimum(0)
                    progressBar.setMaximum(len(self.members))
                    progressBar.setVisible(True)"""

                for i, member in enumerate(self.members):
                    c = Control(member)
                    poseNode = c.getNode('pose')
                    if mc.objExists(poseNode):
                        poseAttributes = mc.listAttr(
                            poseNode, v=True, k=True, leaf=True, scalar=True) or []
                        for poseAttribute in poseAttributes:
                            drivenPlug = poseNode + '.' + poseAttribute
                            if isPlugConnected(drivenPlug, side=0):
                                self.removePose(
                                    driverPlug, drivenPlug, verbose)

                    """if isinstance(progressBar, QProgressBar):
                        progressBar.setValue(i)"""

                """if isinstance(progressBar, QProgressBar):
                    progressBar.reset()
                    progressBar.setVisible(False)"""

    def removePose(self, driverPlug, drivenPlug, verbose=False):
        """Remove the driving plug from a driven plug
        :param unicode driverPlug: the driver plug
        :param unicode drivenPlug: the driven plug
        :param QProgressBar progressBar: an optionnal progressBar
        :param boolean verbose: debug informations
        """
        if checkPlug(driverPlug) and checkPlug(drivenPlug):
            driverNode = nodeFromPlug(driverPlug)
            driverAttr = mc.attributeName(driverPlug, l=True)
            driverPlug = driverNode + '.' + driverAttr

            drivenNode = nodeFromPlug(drivenPlug)
            drivenAttr = mc.attributeName(drivenPlug, l=True)
            graphNodes = getGraphBetween(driverNode, driverAttr, drivenNode, drivenAttr, verbose=False)
            # Here more than one case can appeared
            # Case n1: There is only one driver plug for this driven plug, and obvioulsy, deleting the graph between these plugs will remove the pose,
            #           and a reset of the default value of the driven plug will terminate the operation
            # Case n2: More than one driver plug for this driven plug, we have to analyze which kind of driven plug it is, again two case
            #   Case 2.1: The driven plug is a plug with a classical blendWeighted graph, the nodes upstream the blendWeighted must be deleted, the blendWeighted optimized/cleaned
            #             If there is only one entry in the input attribute of the blendWeighted, this one must be deleted, and the remaining connection connected to the output of the
            #             blendWeighted node (Usually the driven plug)
            #   Case 2.2: The drivenPlug is driven with a mult network, this one must be analyzed in order to delete only the node
            sdkAnimCurves = getSdkAnimCurves(drivenPlug, 0, verbose=False)
            if not sdkAnimCurves:
                if verbose:
                    print(
                        '[removePose] No sdk animCurves found for plug {}'.format(drivenPlug))
                return
            if len(sdkAnimCurves) == 1:
                try:
                    if verbose:
                        print 'The nodes ', graphNodes, 'will be deleted and the plug', drivenPlug, 'reset to its default value'
                    if graphNodes:
                        mc.delete(graphNodes)
                        default = mc.attributeQuery(
                            drivenAttr, node=drivenNode, listDefault=True)[0]
                        mc.setAttr(drivenPlug, default)
                    else:
                        mc.warning('[removePose] No sdk animCurves found between driver plug {} and drivenPlug {1}'.format(
                            driverPlug, drivenPlug))
                except Exception:
                    raise
            else:
                blendWeighted = mc.ls(graphNodes, type='blendWeighted') or []
                if blendWeighted:  # Case n2.1
                    blendWeighted = blendWeighted[0]
                    inputCount = mc.getAttr(
                        '{}.input'.format(blendWeighted), size=True)
                    if inputCount == 1:
                        try:
                            mc.delete(blendWeighted)
                        except Exception:
                            raise
                    else:
                        animCurves = getPrunedTypedConnected(
                            'animCurve', blendWeighted, returnPlug=False, source=True, destination=False, pruneType='dagNode', depth=-1, verbose=False)
                        for sdkAnimCurve in animCurves:
                            if sdkAnimCurve in graphNodes:
                                sdkAnimCurveOutputPlug = sdkAnimCurve + '.output'
                                blendWeightedInputPlug = mc.listConnections(
                                    sdkAnimCurveOutputPlug, s=False, d=True, scn=True, p=True)[0]
                                index = attributeIndexFromPlug(blendWeightedInputPlug, 'input')
                                # In case of a unitConversion on blendWeighted.input[index] (rotate connected for example, we read the input again to retreive the unitConversion node
                                # because we use listConnections with scn argument
                                #
                                upstreamPlug = mc.connectionInfo(
                                    blendWeightedInputPlug, sfd=True)
                                mc.disconnectAttr(
                                    upstreamPlug, blendWeightedInputPlug)
                                mc.removeMultiInstance(
                                    blendWeightedInputPlug, b=True)
                                # Still exists? Maya sometimes clean nodes... sometimes NOT!
                                if mc.objExists(sdkAnimCurve):
                                    mc.delete(sdkAnimCurve)
                                blendWeightedWeightPlug = '{}.weight'.format(
                                    blendWeighted)
                                weightIndices = mc.getAttr(
                                    blendWeightedWeightPlug, multiIndices=True) or []
                                if weightIndices and index in weightIndices:
                                    blendWeightedWeightPlug = '{0}.weight[{1}]'.format(
                                        blendWeighted, index)
                                    mc.removeMultiInstance(
                                        blendWeightedWeightPlug, b=True)

                                # Test if the blendWeighted is still necessary
                                #
                                blendWeightedInputPlug = '{}.input'.format(
                                    blendWeighted)
                                inputIndices = mc.getAttr(
                                    blendWeightedInputPlug, multiIndices=True) or []
                                if len(inputIndices) == 1:
                                    if verbose:
                                        print('The blendWeighted', blendWeighted,
                                              ' has only one input and is therefore no longer necessary, it will be deleted, and its input redirect to its output')
                                    blendWeightedInputPlug = '{}[{1}]'.format(
                                        blendWeightedInputPlug, inputIndices[0])
                                    upstreamPlug = mc.listConnections(
                                        blendWeightedInputPlug, s=True, d=False, scn=True, p=True)[0]
                                    blendWeightedOutputPlug = '{}.output'.format(
                                        blendWeighted)
                                    downstreamPlug = mc.listConnections(
                                        blendWeightedOutputPlug, s=False, d=True, scn=True, p=True)[0]
                                    # In case of a unitConversion on downstreamPlug (rotate connected for example, we read the plug again to retreive the unitConversion node
                                    # because we use listConnections with scn argument
                                    #
                                    outPlug = mc.connectionInfo(
                                        downstreamPlug, sfd=True)
                                    mc.disconnectAttr(
                                        outPlug, downstreamPlug)
                                    mc.connectAttr(
                                        upstreamPlug, downstreamPlug)
                                    # unitConversion node should be removed automatically
                                    mc.delete(blendWeighted)
                                break
                else:
                    jobDone = False
                    for sdkAnimCurve in sdkAnimCurves:
                        if sdkAnimCurve in graphNodes:
                            if verbose:
                                print('sdk animCurve:', sdkAnimCurve)
                            sdkAnimCurveOutputPlug = sdkAnimCurve + '.output'
                            downstreamPlug = mc.listConnections(
                                sdkAnimCurveOutputPlug, s=False, d=True, scn=True, p=True)[0]
                            downstreamNode = nodeFromPlug(
                                downstreamPlug)
                            downstreamAttr = attributeFromPlug(
                                downstreamPlug)
                            if mc.objExists(downstreamNode) and 'multDoubleLinear' == mc.nodeType(downstreamNode):
                                multOutputPlug = downstreamNode + '.output'
                                otherInputAttr = 'input2'
                                if downstreamAttr == 'input2':
                                    otherInputAttr = 'input1'

                                otherInputPlug = downstreamNode + '.' + otherInputAttr
                                otherSdkAnimCurveOuputPlug = mc.connectionInfo(
                                    otherInputPlug, sfd=True)
                                otherNode = nodeFromPlug(
                                    otherSdkAnimCurveOuputPlug)
                                # Now we check the type connected to the multDoubleLinear's output, if it's an other animCurve
                                # We are in the process of removing the last multDoubleLinear, so we don't need anymore to emulate a passive connection on the
                                # driven plug, because we will connect the last remaining driver directly on this atttr
                                #
                                outputPlug = mc.connectionInfo(
                                    multOutputPlug, dfs=True)[0]
                                outputNode = nodeFromPlug(outputPlug)
                                outputAttr = attributeFromPlug(outputPlug)  # @UnusedVariable

                                mc.disconnectAttr(multOutputPlug, outputPlug)
                                # The last multDoubleLinear to remove
                                if mc.objectType(outputNode, isAType='animCurve') and mc.objectType(otherNode, isAType='animCurve'):
                                    if verbose:
                                        print ('The node', downstreamNode, 'and', sdkAnimCurve,
                                               'will be deleted, the node', downstreamNode,
                                               'is the last multDoubleLinear to remove, the node', outputNode,
                                               'will be deleted too and the plug', otherSdkAnimCurveOuputPlug,
                                               'reconnected to', drivenPlug)
                                    mc.delete(outputNode)
                                    mc.connectAttr(
                                        otherSdkAnimCurveOuputPlug, drivenPlug)
                                else:  # at least two driver for this driven plug
                                    if verbose:
                                        print ('The nodes', downstreamNode, 'and', sdkAnimCurve,
                                               'will be deleted, the plug', otherSdkAnimCurveOuputPlug,
                                               'will reconnected to', downstreamNode)
                                    mc.connectAttr(otherSdkAnimCurveOuputPlug, outputPlug)
                                mc.delete(sdkAnimCurve, downstreamNode)
                                jobDone = True
                                break
                    if not jobDone:
                        mc.warning(
                            '[removePose] No sdk animCurves found for plug {}'.format(drivenPlug))

        return

    def restorePoseCg(self, progressBar=None, verbose=False):
        """Transfert all the current values of the pose nodes to the controls
        :param QProgressBar progressBar: an optionnal progressBar
        :param boolean verbose: debug informations
        """
        if mc.objExists(self.controlGroup):
            self.updateMembers()  # To be sure that we are up-to-date with the Maya scene

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)"""

            for i, member in enumerate(self.members):
                c = Control(member)
                c.poseToControl(verbose)


    def storePoseCg(self, progressBar=None, verbose=False):
        """Transfert all the current values of the controls to the pose node
        :param boolean verbose: debug informations
        """
        if mc.objExists(self.controlGroup):
            self.updateMembers()  # To be sure that we are up-to-date with the Maya scene

            """if isinstance(progressBar, QProgressBar):
                progressBar.setMinimum(0)
                progressBar.setMaximum(len(self.members))
                progressBar.setVisible(True)"""

            for i, member in enumerate(self.members):
                c = Control(member)
                c.controlToPose(forcePoseNode=True,
                                relative=False, verbose=verbose)

    def mirrorPoseCg(self, restorePose=False, direction='right', flip=False, progressBar=None, verbose=False):
        """Mirror the current pose of the controlGroup
        :param restorePose: Boolean specify if the transformations stored on the poseNode should be restored on the control
        :param direction: str 'right' or 'left', specify the direction of the mirror/flip
        :param flip: Boolean, False, the values are mirrored, True, the values are flipped
        :param verbose: Boolean, True, print debug informations
        """
        validDirections = ['right', 'left']
        if direction not in validDirections:
            raise ValueError(
                '[mirrorPoseCg] invalid direction "{}" supplied'.format(direction))

        sideToSearch = {'right': ('left', 'middle', 'none'), 'left': (
            'right', 'middle', 'none')}
        members = self.getMembers()

        """if isinstance(progressBar, QProgressBar):
            progressBar.setMinimum(0)
            progressBar.setMaximum(len(members))
            progressBar.setVisible(True)"""

        for i, member in enumerate(members):
            c = Control(member)
            mirrorSide = c.mirrorSide
            if mirrorSide in sideToSearch[direction]:
                c.mirrorPose(restorePose, flip, verbose)

    @undoable
    def renameCg(self):
        """Rename a cg as well as the rig, tpl, and sets
        """
        controlGroup = self.getControlGroup()
        if not mc.objExists(controlGroup):
            return

        controlGroupName = self.getControlGroupName()
        if mc.referenceQuery(controlGroup, isNodeReferenced=True):
            mc.confirmDialog(title='Rename ControlGroup', icon='critical',
                                message='The controlGroup {} is from a reference file'.format(controlGroup),
                                button='OK', defaultButton='OK')
            return False

        result = mc.promptDialog(title='Rename Control Group',
                                    message='Enter Name:',
                                    text=controlGroupName,
                                    button=['OK', 'Cancel'],
                                    defaultButton='OK',
                                    cancelButton='Cancel',
                                    dismissString='Cancel')

        if result != 'OK':
            return

        text = mc.promptDialog(query=True, text=True)
        name = NameParser(text).getBaseName()
        index = NameParser(text).getNameIndex()
        suffix = NameParser(text).getNameSuffix()
        name += index
        if suffix:
            name += ('_' + suffix)

        cgName = 'cg_' + name
        if mc.objExists(cgName):
            mc.confirmDialog(title='Rename ControlGroup', icon='critical',
                             message='The controlGroup {} already exists'.format(cgName),
                             button='OK', defaultButton='OK')
            return False

        mc.lockNode(controlGroup, lock=False)
        self.controlGroup = mc.rename(controlGroup, cgName)
        mc.setAttr('{}.name'.format(
            self.controlGroup), lock=False)
        self.name = name
        mc.setAttr('{}.name'.format(self.controlGroup),
                        self.name, type='string', lock=True)
        mc.lockNode(self.controlGroup, lock=True)

        confirm = mc.confirmDialog(title='Rename ControlGroup', icon='question', messageAlign='center',
                                   message='Would you like to rename the tpl and rig groups\nas well as the control sets?',
                                   button=['Cancel', 'OK'], defaultButton='OK', dismissString='Cancel')
        if confirm == 'OK':
            tplGroup = self.getTplGroup()
            if mc.objExists(tplGroup):
                self.tplGroup = mc.rename(
                    tplGroup, ('tpl_' + self.name))
            rigGroup = self.getRigGroup()
            if mc.objExists(rigGroup):
                self.rigGroup = mc.rename(
                    rigGroup, ('rig_' + self.name))

            ctrlSet = self.getControlSet('ctrlSet')
            if mc.objExists(ctrlSet):
                self.ctrlSet = mc.rename(
                    ctrlSet, ('ctrl_' + self.name))
            skinSet = self.getControlSet('skinSet')
            if mc.objExists(skinSet):
                self.skinSet = mc.rename(skinSet, ('skin_' + self.name))

        self.updateControlGroup()

