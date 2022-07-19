"""
 1_a.si sel transform : convertir selection en selection de vertex
 1_b.si sel selection de vertex : trouver le trqnsform\
     le dupliquer
     selectionner les vertex sur le mesh dup
 2_creer un cluster sur cible
 3_creer loc, name = loc_centerSel
 4_consttraint parent sans maintain offset du cluster sur le loc
 5_del constrainte/cluster/dup
 """
 
import maya.cmds as mc

sel = mc.ls(sl=True)
selDup = []
trsf = []
loc = []
# 1_a if transform
for s in sel:
    typ = mc.objectType(s)
    if typ == "transform":
        print "if a " + s
        sDup = mc.duplicate(s, name=s+"Dup")
        mc.parent(sDup, world=True)
        selDup = sDup
    # 1_b
    if typ == "mesh":
        print "if b " + s
        if "vtx" in s:
            trsf = s.split(".vtx")[0]
            sDup = s.replace(".", "Dup.")
            selDup.append(sDup)
print trsf
if trsf:
    tDup = mc.duplicate(trsf, name=trsf + "Dup")
    mc.parent(tDup, world=True)
# 2    
clst = mc.cluster(selDup)
loc = mc.createNode("locator")
tLoc = mc.listRelatives(loc, allParents=True)
const = mc.parentConstraint(loc, clst, maintainOffset=False)
mc.delete(clst, tDup)
mc.rename(tLoc, "centerLoc")

"""
fonctionne pour 1 obj select
NON vertex / multObj