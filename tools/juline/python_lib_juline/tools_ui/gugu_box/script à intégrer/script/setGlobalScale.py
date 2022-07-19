"""
			CREATION DE L'ATTR PERMETANT DE SETTER LE GLOBAL SCLAE
1_L'utilisateur doit selectionner le group NomDuPerso_Setup
2_Lancer le script
3_setter la valeur de scal dans la fenêtre qui pop
"""
import maya.cmds as mc

selection = mc.ls(sl=True)

if len(selection) == 0:
    raise( Exception( "Selectionner le groupe SETUP" ) )

groupeSetup = selection
nameSpace = groupeSetup[0].split(":")[0]

print ( "Entrez la valeur de scale du perso " + nameSpace.split("_")[0] )

scalePerso = input()

attr = mc.addAttr(groupeSetup[0], attributeType='double', defaultValue=1.0, hasMinValue=True, minValue=0.01, hidden=False, keyable=False, shortName='lineupScale')
mc.setAttr(groupeSetup[0] + '.lineupScale', scalePerso, channelBox=True)

print ( "le scale de " + nameSpace.split("_")[0] + " est : " + str(scalePerso) )

"""
			TROUVER L'ATTRIBUT ET LE SETTER DANS LA SCENE DE SKIN OK

import maya.cmds as mc

allTransform = mc.ls(sl=False, type='transform')

groupSetup = []
scaleValue = ()
ctrlPosition = []
for transform in allTransform:
    lsAttributes = mc.listAttr(transform, userDefined=True)
    if "task" in lsAttributes:
        task = mc.getAttr(transform + ".task")
        if task == "Rig":
            groupSetup.append(transform)
    if "globalScale" in lsAttributes:
        ctrlPosition.append(transform)
    if "lineupScale" in lsAttributes:
        scaleValue = mc.getAttr(transform + ".lineupScale")

mc.setAttr(ctrlPosition[0] + ".globalScale", scaleValue)


			lister par plugs 
"""

ctrlPosition = mc.ls("*.globalScale")
ctrlLineupScale = mc.ls("*.lineupScale")
scaleValue = mc.getAttr(ctrlLineupScale[0])

mc.setAttr(ctrlPosition[0], scaleValue)


"""
constraindre les yeux après skinOk

1_ DONE _liste sur l/r_eye : parent/aim/orient/point Constraint et les supprimer
2_ DONE _listAttr userDefined > si commence par Blend suppr
3_ DONE _faire une liste des attr trs/rot/scl
boucler sur chaque plug (=node.attr)
		L> faire une boucle sur chaque ctrl
				L> dans cette boucle une boucle sur chaque attr de la liste

				= SetAttr locked = False puis break connecxion

4_ DONE _const Point/Orient sans off   ]   du ctrl sur loc
	const Scale avec off		 ]
"""

#liste ctrl eyes

ctrlsEye = ("l_eye", "r_eye")
locsEye = ("l_eye_ctl", "r_eye_ctl")

# Lister et supprimer les constraints
for loc in locsEye:
    lsParentConstraint = mc.parentConstraint(loc, query=True)
    lsPointConstraint = mc.pointConstraint(loc, query=True)
    lsOrientConstraint = mc.orientConstraint(loc, query=True)
    lsAimConstraint = mc.aimConstraint(loc, query=True)
    # L>  la aimConstraint presente sur l'oeil droit n'envoie rien dans les inputs du loc et n'est donc pas trouvee
    blendParent = mc.listAttr(loc, userDefined=True)
    
    if lsParentConstraint != None:
        print lsParentConstraint
        mc.delete(lsParentConstraint)
    
    if lsPointConstraint != None:
        print lsPointConstraint
        mc.delete(lsPointConstraint)
    
    if lsOrientConstraint != None:
        print lsOrientConstraint
        mc.delete(lsOrientConstraint)
    
    if lsAimConstraint != None:
        print lsAimConstraint
        mc.delete(lsAimConstraint)
	
	# Cleaner BlendParent residuel
    for attr in blendParent :
        if "blend" in attr :
            mc.deleteAttr(loc + "." + attr)

	# Liste attributs de base a delocker
    attrBase = (".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz")
    for attr in attrBase:
    	mc.setAttr(loc + attr, lock=False)
    	connexion = mc.listConnections(loc + attr, destination=False, source=True, plugs=True)
    	print connexion
    	if connexion != None:
    	    mc.disconnectAttr(connexion[0], loc + attr)
# Trouver et supprimer l'AimConstraint qui sert au modeling et qui est deco dans la scene de skin
allAimConstraint = mc.ls(type="aimConstraint")

for const in allAimConstraint:
    conx = mc.listConnections(const, destination=True, source=False, plugs=True)
    if len(conx) <= 2:
        for c in conx:
            if "hyperLayout" in c:
                conx.remove(c)
            if str(const) in c:
                conx.remove(c)
        if len(conx) == 0:
            #print ( const + " n'est plus connectee" )
            mc.delete(const)


# constraindre le loc au ctrl
mc.pointConstraint("l_eye", "l_eye_ctl", maintainOffset=False)
mc.orientConstraint("l_eye", "l_eye_ctl", maintainOffset=False)
mc.scaleConstraint("l_eye", "l_eye_ctl", maintainOffset=True)

mc.pointConstraint("r_eye", "r_eye_ctl", maintainOffset=False)
mc.orientConstraint("r_eye", "r_eye_ctl", maintainOffset=False)
mc.scaleConstraint("r_eye", "r_eye_ctl", maintainOffset=True)