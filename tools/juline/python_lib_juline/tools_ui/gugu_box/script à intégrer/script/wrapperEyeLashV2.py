"""
SCRIPT WRAPPER EYELASHES V2
L'utilisateur doit sélectionner :
le mesh à wrapper + la sélection des faces qui seront utilisées pour le wrap

debug : imposible de connecter le skinCluster dans le wrapper base
TEST > création du skinCluster avant la connection du deleteComp pour générer un ShapeOrig
"""

import maya.cmds as mc
import maya.mel as mel
sel = mc.ls(sl=True)
faces = []
mshToWrap= []

for s in sel:
    typ = mc.nodeType(s)
    if typ == "mesh":
        faces.append(s)
    if typ == "transform":
        mshToWrap.append(s)

meshBody = faces[0].split(".f")[0]
bodyShpDef = meshBody.split(":")[-1] + "ShapeDeformed"
nameSpace = meshBody.split(":")[0]
eyesOpenShape = nameSpace + ":eyesOpen_mshShape"
wrpr = mc.createNode("mesh", name=mshToWrap[0].split(":")[-1] + "_wrapperShape")
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
        node2 = mc.rename(node, wrpr + "_deleteComponent")
        delCompWrpr.append(node2)
                
#creation du wrap
wrap = mc.deformer(mshToWrap, wrpr,type="wrap", name=mshToWrap[0].split(":")[-1] + "_wrap")
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
mc.connectAttr(meshBody + "Shape.outMesh", wrprBase + ".inMesh")
sknClstWrprBase = mc.skinCluster(nameSpace.replace("ModelingOk","RigOk") + ":head_skn", wrprBase.split("Shape")[0], name=wrpr.split("Shape")[0] + "_skinCluster")

# creation delCompBase et connection du delComp dans le delCompBase
delCompWrprBase = mc.createNode("deleteComponent", name=wrprBase + "_deleteComponent")
if "eyebrow" in mshToWrap[0]:
    print "Ce mesh est un eyebrow"
    mc.connectAttr(meshBody + "Shape.outMesh", delCompWrprBase + ".inputGeometry")
if "eyeLash" in mshToWrap[0]:
    print "Ce mesh est un eyeLash"
    mc.connectAttr(eyesOpenShape + ".outMesh", delCompWrprBase + ".inputGeometry")

mc.connectAttr(delCompWrpr[0] + ".deleteComponents", delCompWrprBase + ".deleteComponents")
# TEST connecter le delComp dans la ShapeOrig
wrprBaseOrig = wrprBase + "Orig"
mc.connectAttr(delCompWrprBase + ".outputGeometry", wrprBaseOrig + ".inMesh")
mc.connectAttr(sknClstWrprBase[0] + ".outputGeometry[0]", delCompWrprBase + ".inputGeometry", force=True)

#connection wrprBase dans wrap
mc.connectAttr(wrprBase + ".worldMesh[0]", wrap[0] + ".basePoints[0]")

#skiner wrprBase
#mc.skinCluster(nameSpace.replace("ModelingOk","RigOk") + ":head_skn", wrprBase, name=wrpr.split("Shape")[0] + "_skinCluster")

#ranger les wrapper dans un groupe et le cacher
grp = mc.createNode("transform", name="grp_" + mshToWrap[0].split(":")[-1].replace("msh", "wrapper"))
mc.parent(wrpr.split("Shape")[0], grp)
mc.parent(wrprBase.split("Shape")[0], grp)
mc.setAttr(grp + ".visibility", 0)
