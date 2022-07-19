"""
EYE BROWS
script wrapper visage
SETPS :
1_Check if eyeBrows et eyeLash sont skine sinon les skiner
2_L'utilisateur doit selectionner les faces qu'il veut utiliser pour wrapper sont element
Tester interface QT pour pouvoir setter notre obj puis selectionner les faces EXEMPLE ubiViz
3_mesh1 = createNode Mesh , en fonction du mesh sette nommer le wrapper
4_connecter le outMesh du mesh dont les faces ont ete selectionnees dans le inmesh du createNode
5_sur le mesh1 deleter les faces non selectionnees + renomer le deleteComponent
6_wrapper le mesh sur le meshDup parametre de base + ExclusiveBind = True
7_connection outMesh > inMesh du bodyShape dans wrapper_BaseShape
8_sur le wrapper on deleter une face qui nest pas dans les faces utiles
9_renommer le deleteComponent
10_connection des 2 deleteComponent wrapper dans wrapperBase deleteComponent>deleteComponent
11_skiner wrapperBase avec sk_head
"""

import maya.cmds as mc
msh = "R_eyebrow_msh"

wrpr = mc.createNode("mesh", name=msh + "Shape")

mc.connectAttr("body_mshShapeDeformed.outMesh", wrpr + ".inMesh")

#les faces selectionnées par l'utilisateur, on inverse la selection puis on delete les faces inutiles

body = "MarieCur_model:body_msh"

#creation du wrap
#wrap = mc.deformer(body, type='wrap', name="body_msh_wrap")[0]
wrprBase = "eyebrows_wrapper_mshBase"
mc.connectAttr(body + "Shape.outMesh", wrprBase + "Shape.inMesh")
# delet
mc.skinCluster("MarieCur_RigOk:head_skn", "eyebrows_wrapper_mshBase", name="eyebrows_wrapper_msh_skinCluster")

lsCWrpr = mc.listConnections(wrpr)
for node in lsCWrpr:
    if mc.nodeType(node) == "deleteComponent":
        mc.rename(node, wrpr.split("Shape")[0] + "_deleteComponent")

_____________________________________

import maya.cmds as mc
import maya.mel as mel
sel = mc.ls(sl=True)
print sel
faces = []
mshToWrap= []

for s in sel:
    print s
    typ = mc.nodeType(s) #faces == mesh // mesh à wrapper == transform
    if typ == "mesh":
        faces.append(s)
    if typ == "transform":
        mshToWrap.append(s)

meshBody = faces[0].split(".f")[0]
bodyShpDef = meshBody.split(":")[-1] + "ShapeDeformed"
#mc.select(mshToWrap[0]+"Shape")
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
for node in lsConWrpr:
    print node
    if mc.nodeType(node) == "deleteComponent":
        mc.rename(node, wrpr + "_deleteComponent")

#creation du wrap
wrap = mc.deformer(mshToWrap, wrpr,type="wrap", name=mshToWrap[0].split(":")[-1] + "_wrap")
print wrap
mc.connectAttr(wrpr + ".worldMesh[0]", wrap[0] + ".driverPoints[0]")

wrprBase = "R_eyebrow_mshBase"
mc.connectAttr(body + "2Shape.outMesh", wrprBase + "Shape.inMesh")

delComp = mc.createNode("deleteComponent", name=msh + "BaseShape_deleteComponent")
mc.connectAttr(delComp + ".outputGeometry", wrprBase + "Shape.inMesh")

# delete
mc.skinCluster("MarieCur_RigOk:head_skn", "eyebrows_wrapper_mshBase", name="eyebrows_wrapper_msh_skinCluster")

lsCWrpr = mc.listConnections(wrpr)
for node in lsCWrpr:
    if mc.nodeType(node) == "deleteComponent":
        mc.rename(node, wrpr.split("Shape")[0] + "_deleteComponent")
