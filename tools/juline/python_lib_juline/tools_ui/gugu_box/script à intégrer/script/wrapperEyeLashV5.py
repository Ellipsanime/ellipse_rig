"""
SCRIPT WRAPPER EYELASHES V5
L'utilisateur doit selectionner dans l'ordre :
1 _ La selection des faces qui seront utilisees pour le wrap
2 _ le mesh a wrapper
3 _ le mesh eyesOpen en dernier

DEBUG :
1_ DONE _enlever la detection de EyeLash/EyeBrow (car tous les mesh ne sont pas nomme de la
meme facon
2_ DONE _mettre les sides minuscule
3_ DONE _detection de la shape EyesOpen par la selection -> selectionner le mesh eyesOpen en dernier
4_ DONE _enlever cycle wrap dans input du wrapper >> se faisait a la creation du wrap > suppr arg wrpr dans le deformer
5_ DONE _name node laisser les Sahpe, ShapeDef... virer les MAJ
6_ DONE _"_grp" a la fin
7_ DONE _renommer tweak mesh wrprBase + eyeLash
8_ DONE _trouver body shapeDeformed et eyesOpenShape via connection et non par le nom
9_ TO DO _ interface 3 boutons (1 par argument) faces , meshToWrap , meshBase > Body/EyesOpen
"""

import maya.cmds as mc
import maya.mel as mel

# wrapped = 'L_eyeBrows_mshShapeDeformed'
# wrapper = 'body_mshShapeDeformed'
# wrapper_base = 'Sarah_ModelingOk:body_mshShape'
# face_list = ['f[1729:1731]', 'f[1740]', 'f[1819]', 'f[1821]', 'f[2384]']
# dilili_create_facial_wrapper( wrapped, wrapper, wrapper_base=wrapper_base, face_list=face_list )

def dilili_create_facial_wrapper( wrapped, wrapper, wrapper_base=None, face_list=list() ):

    """
    Help.

    :params     wrapped (str): .
                wrapper (str): .
                wrapper_base (str): .
                face_list (list): .
    :return     None
    """

    if wrapper_base is None:
        raise( Exception( 'No wrapper base specified.' ) )
    if len( face_list ) == 0:
        raise( Exception( 'No face list specified.' ) )

    print( 'Hello world!' )

    return

sel = mc.ls(sl=True)
faces = []
mshToWrap= sel[-2]

for s in sel:
    typ = mc.nodeType(s)
    if typ == "mesh":
        faces.append(s)

meshBody = faces[0].split(".f")[0]
#bodyShpDef = meshBody.split(":")[-1] + "ShapeDeformed" #listConnection
bodyShpDef = []
shpsMeshBody = mc.listRelatives(meshBody.split("Shape")[0], allDescendents=True)
for shp in shpsMeshBody :
    shpSets = mc.listConnections(shp, type="objectSet")
    for s in shpSets :
        if "skinCluster" in s:
            bodyShpDef.append(shp)

nameSpace = meshBody.split(":")[0]

#eyesOpenShape = sel[-1] + "Shape"
# trouver eyesOpenShape via connections
eyesOpen = sel[-1]
eyesOpenShape = mc.listRelatives(eyesOpen, allDescendents=True)
eyesOpenShape = eyesOpenShape[0]

nameToWrap = mshToWrap.split(":")[-1]
nameLower = nameToWrap.lower()[:1] + nameToWrap[1:]
wrpr = mc.createNode("mesh", name=nameLower + "_wrapperShape")
mc.connectAttr(bodyShpDef[0] + ".outMesh", wrpr + ".inMesh")

facesWrpr = []
for f in faces:
    facesWrpr.append(wrpr + "." + f.split(".")[-1])
    
mc.select(facesWrpr)
mel.eval("invertSelection;")
mc.delete()

#rename deleteComponent
lsConWrpr = mc.listConnections(wrpr)
delCompWrpr = []
for node in lsConWrpr:
    if mc.nodeType(node) == "deleteComponent":
        node2 = mc.rename(node, wrpr + "_deleteComponent1")
        delCompWrpr.append(node2)
                
#creation du wrap
wrap = mc.deformer(mshToWrap, type="wrap", name=nameLower + "ShapeDeformed_wrap1")
wrap = wrap[0]
mc.setAttr(wrap + ".maxDistance", 1)
mc.setAttr(wrap + ".autoWeightThreshold", 1)
mc.setAttr(wrap + ".exclusiveBind", 1)
mc.connectAttr(wrpr + ".worldMesh[0]", wrap + ".driverPoints[0]")
transformWrpr = mc.listRelatives(wrpr, parent=True)
mc.addAttr(transformWrpr[0], defaultValue=4, hasMaxValue=True, hasMinValue=True, keyable=True, maxValue=20, minValue=0, shortName="dropoff")
mc.connectAttr(transformWrpr[0] + ".dropoff", wrap + ".dropoff[0]")
mc.addAttr(transformWrpr[0], defaultValue=2, hasMaxValue=True, hasMinValue=True, hidden=True, maxValue=2, minValue=1, shortName="inflType")
mc.connectAttr(transformWrpr[0] + ".inflType", wrap + ".inflType[0]")
mc.addAttr(transformWrpr[0], defaultValue=0, hasMinValue=True, keyable=True, minValue=0, shortName="smoothness")
mc.connectAttr(transformWrpr[0] + ".smoothness", wrap + ".smoothness[0]")

#creation wrapper base
wrprBase = mc.createNode("mesh", name=nameLower + "_wrapperBaseShape")

# creation delCompBase et connection avec delComp
delCompWrprBase = mc.createNode("deleteComponent", name=wrprBase + "_deleteComponent1")
mc.connectAttr(eyesOpenShape + ".outMesh", delCompWrprBase + ".inputGeometry")
mc.connectAttr(delCompWrpr[0] + ".deleteComponents", delCompWrprBase + ".deleteComponents")
mc.connectAttr(delCompWrprBase + ".outputGeometry", wrprBase + ".inMesh")

#connection wrprBase dans wrap
mc.connectAttr(wrprBase + ".worldMesh[0]", wrap + ".basePoints[0]")

#skiner wrprBase
mc.skinCluster(nameSpace.replace("ModelingOk","RigOk") + ":head_skn", wrprBase, name=wrpr + "Deformed_skinCluster1")

#ranger les wrapper dans un groupe et le cacher
grp = mc.createNode("transform", name=nameLower.replace("msh", "wrapper") + "_grp")
mc.parent(wrpr.split("Shape")[0], grp)
mc.parent(wrprBase.split("Shape")[0], grp)
mc.setAttr(grp + ".visibility", 0)

#rename tweak mesh to wrap
shpsMshToWrap = mc.listRelatives(mshToWrap.split("Shape")[0], allDescendents=True)
for shp in shpsMshToWrap :
    tweakMshToWrap = mc.listConnections(shp, type="tweak")
    if tweakMshToWrap :
        #print shp + " est la shape connectee"
        tweakMshToWrap = mc.rename(tweakMshToWrap, shp + "_tweak1")
        tweakMshToWrapSet = mc.listConnections(tweakMshToWrap, type="objectSet")
        tweakMshToWrapSet = mc.rename(tweakMshToWrapSet, tweakMshToWrap + "Set")

#rename tweak wrapperBase
shpsWrprBase = mc.listRelatives(wrprBase.split("Shape")[0], allDescendents=True)
for shp in shpsWrprBase :
    tweakWrprBase = mc.listConnections(shp, type="tweak")
    if tweakWrprBase :
        #print shp + " est la shape connectee"
        tweakWrprBase = mc.rename(tweakWrprBase, shp + "_tweak1")
        tweakWrprBaseSet = mc.listConnections(tweakWrprBase, type="objectSet")
        tweakWrprBaseSet = mc.rename(tweakWrprBaseSet, tweakWrprBase + "Set")
        