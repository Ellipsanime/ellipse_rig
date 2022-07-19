import maya.cmds as mc

"""
transferCvPosition

L'utilisateur doit sélectionner la shape de référence puis la shape à modifier
"""

sel = mc.ls(sl=True)
shapeRef = sel[0]
shapeV2 = sel[1]

indicesRef = mc.getAttr(shapeRef + ".controlPoints", multiIndices=True)

for index in indicesRef :
    object = shapeRef + ".cv[" + str(index) + "]"
    position = mc.pointPosition(object, world=True)
    objectTarget = shapeV2 + ".cv[" + str(index) + "]"
    mc.xform(objectTarget, translation=position, worldSpace=True)