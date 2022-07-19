"""
lister les mesh deformer pour être sure de ne pas louper de skinCluster
"""

import maya.cmds as mc

skinClust = mc.ls(sl=True)

for node in skinClust:
    conx = mc.listConnections(node + ".outputGeometry[0]", type="mesh")
    mesh = []
    if conx != None:
        mesh.append(conx[0])
        node = mc.rename(node, mesh[0].split(":")[-1] + "_skinCluster")
        set = mc.listConnections(node + ".message", type="objectSet")
        mc.rename(set, mesh[0].split(":")[-1] + "_skinClusterSet")


"""
#recuperation de la shapeDeformed associee au skinCluster
"""
mc.listConnections("L_eyeLashesDn_msh_skinCluster1Set" + ".dagSetMembers[0]", destination=True, shapes=True, type="mesh")




import maya.cmds as mc

skinList = mc.ls(type ='skinCluster')
    for 'skinCluster' in skinList
        print skin

"""
RENAMER SKINCLUSTER
Lister les skinCluster puis voir s'ils sont associes a une shapeDeformed et les renommer
"""
import maya.cmds as mc

skinList = mc.ls(sl=0, type ="skinCluster")
#skinList = mc.ls(sl=True)

for skin in skinList:
    skinSet = mc.listConnections(skin + ".message", source=True, type="objectSet")
    #print skinSet
    
    if skinSet == None:
        print ( "ce skinCluster << " + str(skin) + " >> n'a pas de SkinClusterSet")
    
    if skinSet:
        shapeSkined = mc.listConnections(skinSet[0] + ".dagSetMembers[0]", source=True, shapes=True, type="mesh")
        #print shapeSkined
        
        if shapeSkined == None:
            print ( "le skinCluster: << " + str(skin) + " >> n'est connecte a aucun mesh" )
        else:
            if ":" in skin:
                print ( "le skinCluster: << " + str(skin) + " >> est en reference" )
            else:
                mc.rename(skin, shapeSkined[0] + "_skinCluster1")
                mc.rename(skinSet, shapeSkined[0] + "_skinCluster1Set")