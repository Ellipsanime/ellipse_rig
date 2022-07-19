"""
SCRIPT WRAPPER EYELASHES V4
L'utilisateur doit selectionner dans l'ordre :
1 _ La selection des faces qui seront utilisees pour le wrap
2 _ le mesh a wrapper
3 _ le mesh eyesOpen en dernier

DEBUG :
1_DONE_enlever la detection de EyeLash/EyeBrow (car tous les mesh ne sont pas nomme de la
meme facon
2_DONE_mettre les sides minuscule
3_DONE_detection de la shape EyesOpen par la selection -> selectionner le mesh eyesOpen en dernier
4_DONE_enlever cycle wrap dans input du wrapper >> se faisait a la creation du wrap > suppr arg wrpr dans le deformer
5_TO_TEST_name node laisser les Sahpe, ShapeDef... voir pour virer les MAJ
6_DONE_grp a la fin
7_renommer tweak
"""
import maya.cmds as mc
import maya.mel as mel
sel = mc.ls(sl=True)
faces = []
mshToWrap= sel[-2]

for s in sel:
    typ = mc.nodeType(s)
    if typ == "mesh":
        faces.append(s)

meshBody = faces[0].split(".f")[0]
bodyShpDef = meshBody.split(":")[-1] + "ShapeDeformed"
nameSpace = meshBody.split(":")[0]
eyesOpenShape = sel[-1] + "Shape"
nameToWrap = mshToWrap.split(":")[-1]
nameLower = nameToWrap.lower()[:1] + nameToWrap[1:]
wrpr = mc.createNode("mesh", name=nameLower + "_wrapperShape")
mc.connectAttr(bodyShpDef + ".outMesh", wrpr + ".inMesh")

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
wrap = mc.deformer(mshToWrap, type="wrap", name=mshToWrap.split(":")[-1] + "_wrap1")
mc.setAttr(wrap[0] + ".maxDistance", 1)
mc.setAttr(wrap[0] + ".autoWeightThreshold", 1)
mc.setAttr(wrap[0] + ".exclusiveBind", 1)
mc.connectAttr(wrpr + ".worldMesh[0]", wrap[0] + ".driverPoints[0]")
transformWrpr = mc.listRelatives(wrpr, parent=True)
mc.addAttr(transformWrpr[0], defaultValue=4, hasMaxValue=True, hasMinValue=True, keyable=True, maxValue=20, minValue=0, shortName="dropoff")
mc.connectAttr(transformWrpr[0] + ".dropoff", wrap[0] + ".dropoff[0]")
mc.addAttr(transformWrpr[0], defaultValue=2, hasMaxValue=True, hasMinValue=True, hidden=True, maxValue=2, minValue=1, shortName="inflType")
mc.connectAttr(transformWrpr[0] + ".inflType", wrap[0] + ".inflType[0]")
mc.addAttr(transformWrpr[0], defaultValue=0, hasMinValue=True, keyable=True, minValue=0, shortName="smoothness")
mc.connectAttr(transformWrpr[0] + ".smoothness", wrap[0] + ".smoothness[0]")

#creation wrapper base
wrprBase = mc.createNode("mesh", name=wrpr.split("Shape")[0] + "BaseShape")

# creation delCompBase et connection du delComp dans le delCompBase
delCompWrprBase = mc.createNode("deleteComponent", name=wrprBase + "_deleteComponent1")
mc.connectAttr(eyesOpenShape + ".outMesh", delCompWrprBase + ".inputGeometry")

mc.connectAttr(delCompWrpr[0] + ".deleteComponents", delCompWrprBase + ".deleteComponents")
mc.connectAttr(delCompWrprBase + ".outputGeometry", wrprBase + ".inMesh")

#connection wrprBase dans wrap
mc.connectAttr(wrprBase + ".worldMesh[0]", wrap[0] + ".basePoints[0]")

#skiner wrprBase
mc.skinCluster(nameSpace.replace("ModelingOk","RigOk") + ":head_skn", wrprBase, name=wrpr + "_skinCluster1")

#ranger les wrapper dans un groupe et le cacher
grp = mc.createNode("transform", name=nameLower.replace("msh", "wrapper") + "_grp")
mc.parent(wrpr.split("Shape")[0], grp)
mc.parent(wrprBase.split("Shape")[0], grp)
mc.setAttr(grp + ".visibility", 0)