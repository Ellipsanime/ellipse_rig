import re
import os
import pymel.core as pm
import maya.cmds as mc

from ellipse_rig.library import lib_pipe as pipe

"""
RedShift shaders conversions
===============================================
"RedshiftMaterial" is converted to "lambert"
"RedshiftShaderSwitch" is converted to "layeredShader"
"RedshiftColorLayer" is converted to "layeredTexture" 
Other redShift nodes will be ignored...

Materials are then applied to shapes, original RedShift nodes are not removed (a call to "deleteUnsused" will get rid of them)

#START PYTHON

import sys

DEVPATH = r"T:\90_TEAM_SHARE\00_PROGRAMMATION\maya\tech_stp\autoRigWip"

if not DEVPATH in sys.path:
    sys.path.append(DEVPATH)
    
from ellipse_rig.library import lib_shaders as shdlib
reload(shdlib)

shdlib.convertAllShadersType()

#END PYTHON

===============================================
"""

"""
Globals
===============================================
RedShift nodes and Vanilla counterparts are used just to avoid the use of strings everywhere
"""

#RedShift nodes
RSMAT = "RedshiftMaterial"
RSLAYEREDSHD = "RedshiftShaderSwitch"
RSLAYEREDTEX = "RedshiftColorLayer"

#Vanilla counterparts
MAT = "lambert"
LAYEREDSHD = "layeredShader"
LAYEREDTEX = "layeredTexture"

"""
#Conversions functions
===============================================
These functions convert a shader type to another one and return the output of the newly created node.
They are listed in the global "CONVERSIONS" to be able to convert nodes dynamically depending on its type
"""


def convertRSLayeredShdTolayeredShd(inRSLayer):
    """
        Convert a "RedshiftShaderSwitch" to a "layeredShader"
        
        :param inRSLayer: The shader to convert
        :type inRSLayer: str
        :return: The output color of the newly created node
        :rtype: str
    """
    #CGibaud

    converted = mc.shadingNode(
        LAYEREDSHD, asShader=True, name="converted_{0}".format(inRSLayer))

    #Replug input connections
    cons = mc.listConnections(
        inRSLayer, source=True, destination=False, connections=True, plugs=True) or []

    counter = 0
    selectorConnection = None
    connectedShaders = -1

    for i in range(len(cons)/2):
        inputAttr = cons[i*2]
        inputNode,  inputAttrShort = inputAttr.split(".")
        outputAttr = cons[i*2 + 1]
        outputNode, outputAttrShort = outputAttr.split(".")

        if inputAttrShort == "selector":  # We will manage this afterwards
            selectorConnection = outputAttr
            continue
        elif inputAttrShort.startswith("shader"):
            layerNumber = -1
            if inputAttrShort[-1] in ["R", "G", "B"]:
                #Channel specific connection, weird but it's present in the example scene "switch_set_driven_key2.ma"...
                layerNumber = int(inputAttrShort[len("shader"):-1])
                connectedShaders = max(connectedShaders, layerNumber)

                mc.connectAttr(outputAttr, "{0}.inputs[{1}].color{2}".format(
                    converted, layerNumber, inputAttrShort[-1]))

            else:  # Color connection
                layerNumber = int(inputAttrShort[len("shader"):])
                connectedShaders = max(connectedShaders, layerNumber)

                mc.connectAttr(outputAttr, "{0}.inputs[{1}].color".format(
                    converted, layerNumber))

    #Convert the "selector" to a list of conditions ( RedshiftShaderSwitch works with an int which points to the wanted shader,
    #layeredShader works with an opacity for each shader)
    if selectorConnection is not None:
        for i in range(connectedShaders + 1):
            thisCond = mc.shadingNode(
                "condition", asUtility=True, name="selector_{0}_cond_{1}".format(inRSLayer, i))

            mc.setAttr("{0}.colorIfTrueR".format(thisCond), 1.0)
            mc.setAttr("{0}.colorIfTrueG".format(thisCond), 1.0)
            mc.setAttr("{0}.colorIfTrueB".format(thisCond), 1.0)

            mc.setAttr("{0}.colorIfFalseR".format(thisCond), 0.0)
            mc.setAttr("{0}.colorIfFalseG".format(thisCond), 0.0)
            mc.setAttr("{0}.colorIfFalseB".format(thisCond), 0.0)

            mc.connectAttr(selectorConnection,
                           "{0}.firstTerm".format(thisCond))
            mc.setAttr("{0}.secondTerm".format(thisCond), i)

            mc.connectAttr("{0}.outColor".format(thisCond),
                           "{0}.inputs[{1}].transparency".format(converted, i))
    else:
        mc.warning(
            "{0} conversion : selector plug is not connected !".format(inRSLayer))

    return "{0}.outColor".format(converted)


def convertRSLayerTolayeredTexture(inRSLayer):
    """
        Convert a "RedshiftColorLayer" to a "layeredTexture"
        
        :param inRSLayer: The shader to convert
        :type inRSLayer: str
        :return: The output color of the newly created node
        :rtype: str
    """
    # CGibaud

    converted = mc.shadingNode(
        LAYEREDTEX, asShader=True, name="converted_{0}".format(inRSLayer))

    # Replug input connections
    cons = mc.listConnections(
        inRSLayer, source=True, destination=False, connections=True, plugs=True) or []

    counter = 0

    for i in range(len(cons)/2):
        inputAttr = cons[i*2]
        inputSplit = inputAttr.split(".")
        inputNode = inputSplit[0]
        inputAttrShort = ".".join(inputSplit[1:])

        outputAttr = cons[i*2 + 1]
        outputSplit = outputAttr.split(".")
        outputNode = outputSplit[0]
        outputAttrShort = ".".join(outputSplit[1:])

        if inputAttrShort.endswith("_color") and mc.attributeQuery(inputAttrShort.replace("_color", "_enable"), node=inputNode, exists=True):
            mc.connectAttr(outputAttr, "{0}.inputs[{1}].color".format(
                converted, counter), force=True)

            enableAttr = inputAttr.replace("_color", "_enable")
            enableCons = mc.listConnections(
                enableAttr, source=True, destination=False, plugs=True) or []
            if len(enableCons) > 0:
                mc.connectAttr(enableCons[0], "{0}.inputs[{1}].alpha".format(
                    converted, counter), force=True)
            else:
                mc.warning("{0} conversion : enable plug is not connected ! ({1})".format(
                    inRSLayer, enableAttr))

            counter += 1

    return converted


def convert_rsmat_to_lambert(inShader, inReassign=True):
    converted = mc.shadingNode(
        MAT, asShader=True, name="converted_{0}".format(inShader))

    mc.setAttr("{0}.colorR".format(converted), mc.getAttr(
        "{0}.diffuse_colorR".format(inShader)))
    mc.setAttr("{0}.colorG".format(converted), mc.getAttr(
        "{0}.diffuse_colorG".format(inShader)))
    mc.setAttr("{0}.colorB".format(converted), mc.getAttr(
        "{0}.diffuse_colorB".format(inShader)))

    # Reconnect input connections (We may have to convert input connections nodes on the fly)
    cons = mc.listConnections(
        inShader, source=True, destination=False, connections=True, plugs=True) or []

    for i in range(len(cons)/2):
        inputAttr = cons[i*2]
        inputSplit = inputAttr.split(".")
        inputNode = inputSplit[0]
        inputAttrShort = ".".join(inputSplit[1:])

        outputAttr = cons[i*2 + 1]
        outputSplit = outputAttr.split(".")
        outputNode = outputSplit[0]
        outputAttrShort = ".".join(outputSplit[1:])

        if inputAttrShort == "diffuse_color":
            nodeType = mc.nodeType(outputNode)
            # if nodeType in CONVERSIONS:
            #     #Do the intermediate node conversion
            #     outputAttr = CONVERSIONS[nodeType][1](outputNode)

            mc.connectAttr(outputAttr, "{0}.color".format(
                converted), force=True)
        else:
            mc.warning("{0} conversion : Does not know how to reconnect input plug '{1}'".format(
                inShader, inputAttr))

    #Reconnect output connections
    cons = mc.listConnections(
        inShader, source=False, destination=True, connections=True, plugs=True) or []

    for i in range(len(cons)/2):
        inputAttr = cons[i*2]
        inputSplit = inputAttr.split(".")
        inputNode = inputSplit[0]
        inputAttrShort = ".".join(inputSplit[1:])

        outputAttr = cons[i*2 + 1]
        outputSplit = outputAttr.split(".")
        outputNode = outputSplit[0]
        outputAttrShort = ".".join(outputSplit[1:])

        if inputAttrShort == "outColor":
            nodeType = mc.nodeType(outputNode)
            if nodeType != "shadingEngine" and nodeType != "materialFacade":
                mc.connectAttr("{0}.outColor".format(
                    converted), outputAttr, force=True)

    if inReassign:
        for obj in getObjectsUsingShader(inShader):
            assignShader(converted, obj)

    #Mark the shader as deleteme
    mc.select(inShader)
    pipe.addDelMe()
    mc.select(clear=True)
    inShader

    return converted


"""
#CONVERSIONS dictionary
===============================================
Give the function to use for each convertible types (used by "convertShaderType")
"""
CONVERSIONS = {
    RSMAT: (MAT, convert_rsmat_to_lambert),
    RSLAYEREDSHD: (LAYEREDSHD, convertRSLayeredShdTolayeredShd),
    RSLAYEREDTEX: (LAYEREDTEX, convertRSLayerTolayeredTexture),
}


def getShadingGroup(inMaterial):
    """
        Get the shadingGroup from a material, creating one if it does not exists
        
        :param inMaterial: The material to get the shadingGroup from
        :type inMaterial: str
        :return: The shadingGroup
        :rtype: str
    """
    #CGibaud
    shadingGroup = None

    nodes = mc.listHistory(inMaterial, future=True, levels=1)

    for node in nodes:
        nodeType = mc.nodeType(node)
        if not "initialParticleSE" in node and (nodeType == "shadingEngine" or nodeType == "materialFacade"):
            shadingGroup = node
            break

    #No shading group ?
    if shadingGroup == None:
        shadingGroup = mc.sets(
            renderable=True, noSurfaceShader=True, empty=True, name=inMaterial+"SG")
        mc.connectAttr(inMaterial + ".outColor", shadingGroup +
                       ".surfaceShader", force=True)

    return shadingGroup


def assignShader(inMaterial, inObj, inSG=None, inFaces=None):
    """
        Assign a shader to an object
        
        :param inMaterial: The material to apply
        :param inObj: The object to assign the material to
        :param inSG: The optional shading group of the material (autodetected if not given)
        :param inFaces: The optional polygon indices to assign the material to
        :type inMaterial: str
        :type inObj: str
        :type inSg: str
        :type inFaces: list[int]
        :return: The shadingGroup
        :rtype: str
    """
    #CGibaud
    shape = inObj
    if mc.nodeType(inObj) == "transform":
        shapes = mc.listRelatives(inObj, shapes=True)
        if len(shapes) > 0:
            shape = shapes[0]
        else:
            mc.warning("Can't find any shapes on object %s" % inObj)

    shadingGroup = None

    if inSG != None:
        shadingGroup = inSG
    else:
        shadingGroup = getShadingGroup(inMaterial)

    if inFaces is None:
        mc.sets(shape, forceElement=shadingGroup)
    else:
        mc.sets(["{0}.{1}".format(shape, item)
                 for item in inFaces], forceElement=shadingGroup)

    return shadingGroup


def getObjectsUsingShader(inMaterial, inSG=None):
    """
        Return the list of objects using given shader
        
        :param inMaterial: The material to apply
        :param inSG:  The optional shading group of the material (autodetected if not given)
        :type inMaterial: str
        :type inSG: str
        :return: The list of objects using given shader
        :rtype: list[str]
    """
    #CGibaud
    shadingGroup = inSG or getShadingGroup(inMaterial)
    return mc.listConnections("{0}.dagSetMembers".format(shadingGroup), source=True, destination=False) or []


def getRSShaders():
    """
        Return the nodes of type "RedshiftMaterial" (was usefull because at first I didn't have RedShift installed)
        
        :return: The list "RedshiftMaterial" nodes
        :rtype: list[str]
    """
    #CGibaud
    if RSMAT in mc.allNodeTypes():
        return mc.ls(type=RSMAT)

    #When you don't have RS installed...
    rslt = []
    nodes = mc.ls(type="unknown")

    for node in nodes:
        isShader = False
        cons = mc.listConnections(node, source=False, destination=True) or []
        for con in cons:
            if mc.nodeType(con) == "shadingEngine":
                isShader = True
                break

        if isShader:
            rslt.append(node)

    return rslt


def get_rs_by_selection(selection_list):
    """
    
    Returns
    -------

    """
    if RSMAT in mc.allNodeTypes():
        return [x for x in selection_list if mc.nodeType(x) == RSMAT]

    #When you don't have RS installed...
    rslt = []
    nodes = (x for x in selection_list if mc.nodeType(x) =="unknown")
    
    for node in nodes:
        isShader = False
        cons = mc.listConnections(node, source=False, destination=True) or []
        for con in cons:
            if mc.nodeType(con) == "shadingEngine":
                isShader = True
                break

        if isShader:
            rslt.append(node)

    return rslt


def getRSShaderSwitches():
    """
        Return the nodes of type "RedshiftShaderSwitch" (was usefull because at first I didn't have RedShift installed)
        
        :return: The list "RedshiftShaderSwitch" nodes
        :rtype: list[str]
    """
    #CGibaud
    if RSLAYEREDSHD in mc.allNodeTypes():
        return mc.ls(type=RSLAYEREDSHD)

    return []


def isRSLayer(inNode):
    """
        Verify if given node is of type "RedshiftColorLayer" (was usefull because at first I didn't have RedShift installed)
        
        :param inNode: The node to test
        :type inNode: str
        :return: True if given node is a "RedshiftColorLayer", False otherwise
        :rtype: bool
    """
    #CGibaud
    if RSLAYER in mc.allNodeTypes():
        return mc.nodeType(inNode) == RSLAYER

    #When you don't have RS installed...
    return mc.nodeType(inNode) == "unknown" and mc.attributeQuery("advanced_mode", node=inNode, exists=True)


def convertShaderType(inShader, inToShaderType="lambert", inReassign=True):
    #CGibaud
    """
        Convert a shader to another type, using "CONVERSIONS" global to figure out how
        
        :param inShader: The shader to convert
        :param inToShaderType: The shader type to convert to 
        :param inReassign: True if we want to assign the converted shader to objects using the original one
        :type inShader: str
        :type inToShaderType: str
        :type inReassign: bool
        :return: The converted shader
        :rtype: str
    """
    rootNodeType = mc.nodeType(inShader)
    if rootNodeType in CONVERSIONS:  # Simple case, we have the conversion method in "CONVERSIONS"
        outputAttr = CONVERSIONS[rootNodeType][1](inShader)
        converted = outputAttr.split(".")[0]
    else:  # Convert the base shader
        converted = mc.shadingNode(
            inToShaderType, asShader=True, name="converted_{0}".format(inShader))

        mc.setAttr("{0}.colorR".format(converted), mc.getAttr(
            "{0}.diffuse_colorR".format(inShader)))
        mc.setAttr("{0}.colorG".format(converted), mc.getAttr(
            "{0}.diffuse_colorG".format(inShader)))
        mc.setAttr("{0}.colorB".format(converted), mc.getAttr(
            "{0}.diffuse_colorB".format(inShader)))

        #Reconnect input connections (We may have to convert input connections nodes on the fly)
        cons = mc.listConnections(
            inShader, source=True, destination=False, connections=True, plugs=True) or []
        for i in range(len(cons)/2):
            inputAttr = cons[i*2]
            inputSplit = inputAttr.split(".")
            inputNode = inputSplit[0]
            inputAttrShort = ".".join(inputSplit[1:])

            outputAttr = cons[i*2 + 1]
            outputSplit = outputAttr.split(".")
            outputNode = outputSplit[0]
            outputAttrShort = ".".join(outputSplit[1:])

            if inputAttrShort == "diffuse_color":
                nodeType = mc.nodeType(outputNode)
                if nodeType in CONVERSIONS:
                    #Do the intermediate node conversion
                    outputAttr = CONVERSIONS[nodeType][1](outputNode)

                mc.connectAttr(outputAttr, "{0}.color".format(
                    converted), force=True)
            else:
                mc.warning("{0} conversion : Does not know how to reconnect input plug '{1}'".format(
                    inShader, inputAttr))

        #Reconnect output connections
        cons = mc.listConnections(
            inShader, source=False, destination=True, connections=True, plugs=True) or []

        for i in range(len(cons)/2):
            inputAttr = cons[i*2]
            inputSplit = inputAttr.split(".")
            inputNode = inputSplit[0]
            inputAttrShort = ".".join(inputSplit[1:])

            outputAttr = cons[i*2 + 1]
            outputSplit = outputAttr.split(".")
            outputNode = outputSplit[0]
            outputAttrShort = ".".join(outputSplit[1:])

            if inputAttrShort == "outColor":
                nodeType = mc.nodeType(outputNode)
                if nodeType != "shadingEngine" and nodeType != "materialFacade":
                    mc.connectAttr("{0}.outColor".format(
                        converted), outputAttr, force=True)

    if inReassign:
        for obj in getObjectsUsingShader(inShader):
            assignShader(converted, obj)

    #Mark the shader as deleteme
    mc.select(inShader)
    pipe.addDelMe()
    mc.select(clear=True)
    inShader

    return converted


def convertAllShadersType(inToShaderType="lambert", inReassign=True):
    """
        Convert all shaders to another type, calling convertShaderType on all nodes of the consistent types
        
        :param inToShaderType: The shader type to convert to 
        :param inReassign: True if we want to assign the converted shader to objects using the original one
        :type inToShaderType: str
        :type inReassign: bool
    """
    
    #Convert "Basic" RS Shaders
    allRSShaders = list()
    
    by_selection = mc.ls(sl=True)
    
    if not by_selection:
        allRSShaders = getRSShaders()
    else:
        allRSShaders = get_rs_by_selection(by_selection)

    for RSShader in allRSShaders:
        print "Converting '{0}'...".format(RSShader)
        convertShaderType(
            RSShader, inToShaderType=inToShaderType, inReassign=inReassign)


redshift_to_lambert_equivalent_attribut = {"diffuse_color": "color",
                                           "opacity_color": "transparency",
                                           #    "ambientColor",
                                           #    "incandescence",
                                           "diffuse_weight": "diffuse",
                                           "outColor": "outColor"}
TEXTURED_SETS = "map_set"
IM_path = r"T:\00_PROGRAMMATION\01_TOOLS\ImageMagick\convert.exe"


def get_objects_using_shader(rs_shader, shading_group=None):
    """
        Return the list of objects using given shader
        
        :param shader: The material to apply
        :param shading_group:  The optional shading group of the material (autodetected if not given)
        :type shader: str
        :type shading_group: str
        :return: The list of objects using given shader
        :rtype: list[str]
    """
    if shading_group is None:
        shading_groups = rs_shader.shadingGroups()
    else:
        shading_groups = [shading_group]
    list_shape = []
    for shading_group in shading_groups:
        list_shape.extend(shading_group.members())
    list_transform = pm.listRelatives(list_shape, parent=True)
    return list_transform


def keep_texture_on_lambert(rs_shader):
    object_shade = get_objects_using_shader(rs_shader)
    try:
        textured_set = pm.PyNode(TEXTURED_SETS)
    except:
        print("{} Does not Exist: Delete texture").format(TEXTURED_SETS)
        return False
    textured_object = textured_set.members()
    if (set(object_shade) & set(textured_object)):
        return True
    print("Not in {}: Delete texture").format(TEXTURED_SETS)
    return False


def get_rs_shaders():
    """
        Return the nodes of type "RedshiftMaterial" (was usefull because at first I didn't have RedShift installed)
        
        :return: The list "RedshiftMaterial" nodes
        :rtype: list[str]
    """
    list_shader = []
    for type_shader in ["RedshiftMaterial"]:
        if type_shader in pm.allNodeTypes():
            list_shader.extend(pm.ls(type=type_shader))

    return list_shader


def convert_all_rs_shader_to_lambert():
    """
        convert_all_rs_shader_to_lambert [summary]
    """

    #Convert "Basic" RS Shaders
    all_rs_shaders = get_rs_shaders()

    for rs_shader in all_rs_shaders:
        print "Converting '{0}'...".format(rs_shader)
        # If the shader has a mesh in the map_set group,
        # we maintain the texture,
        # otherwise we convert the texture to an average color

        keep_tex = keep_texture_on_lambert(rs_shader)
        if keep_tex:
            convert_rs_shading_node_to_maya_standart(rs_shader)
        else:
            convert_rs_shader_to_average_color_lambert(rs_shader)


def convert_rs_shading_node_to_maya_standart(rs_shading_node):
    print("Converting {}".format(rs_shading_node))
    shading_node_type = rs_shading_node.type()

    outputs_attr = rs_shading_node.outputs(plugs=1)
    if shading_node_type in CONVERSIONS.keys():
        new_node = CONVERSIONS[shading_node_type][1](rs_shading_node.name())
        new_node = pm.PyNode(new_node)
        for attr in outputs_attr:
            pm.connectAttr(new_node.attr("outColor"), attr, force=True)

    all_connected_node = rs_shading_node.inputs()

    print "input shader: {}".format(all_connected_node)

    if all_connected_node != []:
        for connected_node in all_connected_node:
            print "input type: {}".format(connected_node.type())

            convert_rs_shading_node_to_maya_standart(connected_node)


def convert_rs_shader_to_average_color_lambert(rs_shader):
    """convert_rs_shader_to_average_color_lambert 
    
    Arguments:
        rs_shader {string} -- redshift shader to convert
    """
    rs_attributs = get_redshift_attr(rs_shader)
    lambert_attributs = redshift_attributs_to_lambert_attributs(rs_attributs)
    lambert = create_lambert_from_dict(lambert_attributs)


def get_redshift_attr(rs_shader):
    all_attributs = {"name": rs_shader.name()}
    for rs_attribut_name in redshift_to_lambert_equivalent_attribut.keys():
        attribut = rs_shader.attr(rs_attribut_name)
        attribut_input = attribut.inputs()
        attribut_output = attribut.outputs(plugs=1)
        if len(attribut_input) == 1:
            all_attributs[rs_attribut_name] = get_average_color_on_attribut(
                attribut_input[0])
        elif len(attribut_input) > 1:
            raise IndexError("Multiple shader connection not implemented")
        elif attribut_output != []:
            all_attributs[rs_attribut_name] = attribut_output
        else:
            all_attributs[rs_attribut_name] = attribut.get()
    return all_attributs


def get_average_color_on_attribut(shading_node):
    if shading_node.type() == "file":
        filepath = shading_node.attr("fileTextureName").get()
        filepath = os.path.expandvars(filepath)
        if os.path.exists(filepath):
            return get_average_color_on_image(filepath)
        return (0, 0, 0)
    elif shading_node.type() == "RedshiftColorCorrection":
        input = shading_node.attr("input").inputs()[0]
        return get_average_color_on_attribut(input)
    elif shading_node.type() == "RedshiftColorLayer":
        input = get_used_texture_in_rs_layer(shading_node)
        return get_average_color_on_attribut(input)
    else:
        print("Conversion not Yet implemented type {} for shader {}".format(
            shading_node.type(), shading_node))
        return (0, 0, 0)


def get_used_texture_in_rs_layer(rs_layer_node):
    enable_attr = rs_layer_node.listAttr(string="*_enable")
    for enable in enable_attr:
        if enable.get():
            return enable


def get_average_color_on_image(image):
    if os.path.exists(image):
        from subprocess import Popen, PIPE

        p = Popen([IM_path, image, "-resize", "1x1", 'txt:-'],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(
            b"input data that is passed to subprocess' stdin")
        rc = p.returncode
        color = re.findall(
            r"srgb\(([0-9]{,3}),([0-9]{,3}),([0-9]{,3})\)", output)[0]
        return (float(color[0])/255, float(color[1])/255, float(color[2])/255)


def redshift_attributs_to_lambert_attributs(rs_attributs):
    lambert_attributs = {}
    for rs_attr in rs_attributs.keys():
        if rs_attr == "name":
            lambert_attributs["name"] = "converted_{}".format(
                rs_attributs["name"])
            continue

        lam_attr = redshift_to_lambert_equivalent_attribut[rs_attr]
        if lam_attr == "transparency":
            lambert_attributs[lam_attr] = (1-rs_attributs[rs_attr][0],
                                           1-rs_attributs[rs_attr][1],
                                           1-rs_attributs[rs_attr][2])
            continue
        lambert_attributs[lam_attr] = rs_attributs[rs_attr]
    return lambert_attributs


def create_lambert_from_dict(lambert_attributs):
    lambert_name = lambert_attributs["name"]
    if pm.ls(lambert_name, type="lambert") == []:
        lambert = pm.shadingNode(
            "lambert", asShader=True, name=lambert_attributs["name"])
    else:
        lambert = pm.PyNode(lambert_name)
    lambert_attributs.pop("name")
    for attr, value in lambert_attributs.iteritems():
        lamber_attr = lambert.attr(attr)
        if type(value) is list:
            for to_connnect in value:
                if to_connnect.isConnected():
                    inputs = to_connnect.inputs(plugs=1)
                    for input in inputs:
                        input.disconnect(to_connnect)
                        # to_connnect.disconnect(input)
                lamber_attr.connect(to_connnect)
            continue
        lamber_attr.unlock()
        lamber_attr.set(value)
    return lambert
