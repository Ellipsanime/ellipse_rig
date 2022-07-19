import maya.cmds as mc

"""
Selectionner la body_shapeDeformes
"""
bodyShpDef = mc.ls(sl=True)

mshRiv = mc.createNode("mesh", name="face_rivet_mshShape")
mc.connectAttr(bodyShpDef[0] + ".outMesh", mshRiv + ".inMesh")

grp = mc.createNode("transform", name="face_rivet_grp")
mc.parent(mshRiv.split("Shape")[0], grp)