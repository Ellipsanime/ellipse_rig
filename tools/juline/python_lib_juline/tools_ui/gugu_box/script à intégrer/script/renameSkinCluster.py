"""
lister les mesh deformer pour être sure de ne pas louper de skinCluster
"""

import maya.cmds as mc

scn = mc.ls(sl=False)

skinClust = []

for node in scn:
    if mc.nodeType(node) == "skinCluster":
        if not ":" in node:
            skinClust.append(node)

for node in skinClust:
    conx = mc.listConnections(node + ".outputGeometry[0]", type="mesh")
    mesh = []
    if conx != None:
        mesh.append(conx[0])
        mc.rename(node, mesh[0].split(":")[-1] + "_skinCluster")
        set = mc.listConnections(node + ".message", type="objectSet")
        mc.rename(set, mesh[0].split(":")[-1] + "_skinClusterSet")