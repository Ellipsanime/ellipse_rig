import maya.cmds as mc

skinList = mc.ls(sl=0, type ="skinCluster")

for skin in skinList:
    skinSet = mc.listConnections(skin + ".message", destination=True, type="objectSet")
    
    if skinSet == None:
        print ( "ce skinCluster << " + str(skin) + " >> n'a pas de SkinClusterSet")
    
    if skinSet:
        shapeSkined = mc.listConnections(skinSet[0] + ".dagSetMembers[0]", destination=True, shapes=True, type="mesh")
        if shapeSkined == None:
            print ( "le skinCluster: << " + str(skin) + " >> n'est connecte a aucune shape" )
        else:
            if ":" in skin:
                pass
            else:
                mc.rename(skin, shapeSkined[0] + "_skinCluster1")