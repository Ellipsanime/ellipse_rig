"""
imaginons une veste dont les cols sont modelises sur le meme mesh.
1_ Dupliquer le mesh vesteBase
2_ Faire un extract du col de vesteDuplicata (FACES selectionnees par l'utilisateur)
   >> on se retrouver avec 2 meshs (colDuplicata + vesteSansColDuplicata)

3_a selectionner les joints qui skin le meshBase
3_b skinner les meshDup avec ces joints
3_c copier le skin entre mshBase et meshDup
3_d convertir selection faceBase en vertexBase
3_e copy skin de meshDup a vertexBase
(
3_ Faire un skinAs de vesteBase sur vesteSansColDuplicata
4_ Selectionner les vertexs du col de vesteBase et creer un set setColVesteBase
5_ Selectionner vesteSansColDuplicata et en mel entrer "select -add setColVesteBase" et faire un copySkinWeight
)
4_ supprimer meshs duplicata
"""

import maya.cmds as mc

# 0 : L'utilisateur doit selectionner les vertex sur lesquels il veut copier le skin.
facesBase = mc.ls(sl=True)

# 1 : Dupliquer le meshBase et la lister la selection de faceDup
mshBase = facesBase[0].split(".")[0]
mshDup = mc.duplicate(mshBase, name=mshBase + "Dup")
facesDup = []
for f in facesBase:
    facesDup.append(f.replace(".", "Dup."))

# 2 : Separer le mesh
mc.polyChipOff(facesDup, ch=True, keepFacesTogether=True, duplicate=False, offset=False)
mshSep = mc.polySeparate(mshDup, ch=True, name=mshBase + "DupSep")

# 3_a/b : skinner le meshDupSep avec les joints skinant le meshBase

lsHistMshBase = mc.listHistory(mshBase, levels=2)
for node in lsHistMshBase:
    if mc.nodeType(node) == "skinCluster":
        skinClusterBase = node

joints = mc.listConnections(skinClusterBase, destination=True, type="joint")
mc.skinCluster(mshSep[0], joints)

lsHistMshDup = mc.listHistory(mshSep[0], levels=2)
for node in lsHistMshDup:
    if mc.nodeType(node) == "skinCluster":
        skinClusterDup = node
    
shpDup = mc.listRelatives(mshSep[0], allDescendents=True)[0]

# 3_c : copier le skin entre mshBase et mshDup

mc.copySkinWeights(destinationSkin=str(skinClusterDup), influenceAssociation="closestJoint", sourceSkin=str(skinClusterBase), surfaceAssociation="closestPoint")

# 3_d

vertexBase = mc.polyListComponentConversion(facesBase, toVertex=True)

# 3_e

mc.copySkinWeights(destinationSkin=vertexBase, influenceAssociation="closestJoint", sourceSkin=str(skinClusterDup), surfaceAssociation="closestPoint")



""" copySkinWeights de maya en mannuel

CopySkinWeights;
performCopySkinWeights false;
copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint;
// Result: Copied 1 skins.
// Result: doCopySkinWeightsArgList( 2, {" -surfaceAssociation closestPoint -influenceAssociation closestJoint"} ) // 
editMenuUpdate MayaWindow|mainEditMenu;

Script qa copy skin 

$source_pointJointWeights[$l] = `skinPercent -t $current_joint -q  $skinCluster $current_point` ;

string $pointJoints[] = `skinPercent -ib 0.0001 -q -t $skinCluster $pt`;
"""