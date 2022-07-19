import maya.cmds as cmds
import maya.mel as mel
import logging

import mgl7ModelingTools as MT
import mgl7ReferenceTool as RT

import mgl7FunctionsUtils as FU


import sgtk
from mgl7SgtkLibs.mgl7SgtkTemplates import get_publish_template_from_work_template
from mgl7SgtkLibs.mgl7SgtkUtils import get_latest_publish_version
import mgl7SgtkLibs.mgl7SgtkUtils as sgtkUtils

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ActorCleaner.py')





print('Hello!')
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////        BLENDSHAPES CLEANER        ///////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
def facial_cleaner():
    rt = RT.referencesTool()
    allTopDag = MT.getTopDags()
    topRefNodeFacial = "NONE"
    for ref in rt.topRefs:
        if [n for n in ref.nodes if "FACIAL_ALL" in n]:
            #On import la ref du Facial
            topRefNodeFacial = ref
            NSFacial = ref.namespace
            ref.importRef(removeNS=True)
            #On tag les topDAG de la REF
            for i in ref.nodes:
                #On supprime le NS du topNode
                i = i.replace(NSFacial+":","")
                for x in allTopDag:
                    if i in x and cmds.nodeType(i) == "transform" and not cmds.objExists(i+".mgFacialTopDag"):
                        if not cmds.objExists(i+".mgFacialTopDag"):
                        	cmds.addAttr(i,ln="mgFacialTopDag",dt="string")
                
        if topRefNodeFacial != "NONE":
            children = topRefNodeFacial.children
            if children:
                for child in children:
                    ## -- (bguillou, 20160623) Added reference node existence check.
                    if cmds.objExists(child):
                        #TAGGUE LE RN pour le delete (.mgRNToDelete)
                        cmds.lockNode(child.replace(NSFacial+":",""),l=0)
                        cmds.addAttr(child.replace(NSFacial+":",""),ln="mgRNToDelete",dt="string")
            
            #selection et suppression des RN TAGGUES
            if cmds.ls("*.mgRNToDelete",o=True):
                for i in cmds.ls("*.mgRNToDelete",o=True) :
                    rt.getRefByRN(i).removeRef()     
    
    
def recreateFacialConnections(pModelingGroup):
    nodeFacial = "FACIAL_ALL"
    if cmds.objExists(nodeFacial):
        cmds.setAttr(nodeFacial+".v",1)
        # -----------------------------------------------------------------------------
        #On gere les nodes Apres le clean des refs, Ils sont taggue avec mgFacialTopDag
        topDagFacial = cmds.ls("*.mgFacialTopDag",o=True)
        #On supprime les TRASH du facial
        [cmds.delete(x) for x in topDagFacial if "TRASH" in x]
        
        #GESTION DES DIFFERENTS DOSSIER(FACIAL_DRIVERS,FACIAL_SKIN,FACIAL_SHAPES,FACIAL_TO_CONNECT)
        for itemGroupFacial in cmds.listRelatives("FACIAL_ALL",c=True,type="transform"):
            if itemGroupFacial == "FACIAL_SKIN" or itemGroupFacial == "FACIAL_SHAPES":
                cmds.setAttr(itemGroupFacial+".v",0)

            elif itemGroupFacial == "FACIAL_TO_CONNECT":
                listMeshes = cmds.ls(cmds.listRelatives("FACIAL_TO_CONNECT",ad=True,c=True,f=True),type="mesh",l=True)
                listTransform = []
                for x in cmds.listRelatives(listMeshes,p=True,f=True):
                    if x not in listTransform:
                        listTransform.append(x)
                #On parse toutes les shapes dans le groupe FACIAL_TO_CONNECT
                for i in listTransform:
                    #On cherche le node de blendShape associer (le premier dans son historique)
                    bsNode = cmds.ls(cmds.listHistory(i),typ="blendShape",l=True)[0]
                    if cmds.nodeType(bsNode) == 'blendShape':
                        #On recupere les meshes en input du BS
                        BSToConnect =  cmds.ls(cmds.listConnections(bsNode,d=False),typ="transform")
                        #On constitue la liste des poids 
                        weightBS = []
                        for num in range(0,len(BSToConnect)):
                            weightBS.append([num,1])
                        print pModelingGroup
                        for modelingMsh in cmds.listRelatives(pModelingGroup,type="transform",ad=True,f=True):
                            if modelingMsh.split("|")[-1] == i.split("|")[-1]:
                                #check si un BlendShape existe sur le modeling 
                                blenShapeOnModeling = cmds.ls(cmds.listHistory(modelingMsh),typ="blendShape")
                                if blenShapeOnModeling:
                                    BSNode=blenShapeOnModeling

                                    ## -- (bguillou, 20161007) > Modified method to get how many targets
                                    ## -- already exist on modeling blend-shape node. Corrective-shapes sculpted
                                    ## -- with Shapes are not meshes connected as blend-shape input. So they
                                    ## -- aren't returned when targets are queried.
                                    # indexBSToAddStart = len(cmds.blendShape(BSNode[0],q=True,t=True,ib=False))
                                    indexBSToAddStart = cmds.blendShape(BSNode[0],q=True,wc=True)
                                    indexBSToAdd = indexBSToAddStart
                                    for bs in BSToConnect:
                                        cmds.blendShape(BSNode[0],e=True,t=(modelingMsh,indexBSToAdd,bs,1)) 
                                        indexBSToAdd += 1
                                else:
                                    BSNode = cmds.blendShape(BSToConnect,modelingMsh,name=modelingMsh.split("|")[-1]+"_BS",origin="local",frontOfChain=True,w=weightBS,tc=True)
                                
                                #On list les targets du BS
                                targetList = cmds.blendShape(BSNode[0],q=True,t=True,ib=False)
                                #On lock les Weight
                                for itemBS in BSToConnect:
                                    if itemBS in targetList:
                                        cmds.setAttr(BSNode[0]+"."+itemBS,1)
                                        cmds.setAttr(BSNode[0]+"."+itemBS,lock=True)
                                        
                cmds.delete(itemGroupFacial)
            else:
                #FACIAL_DRIVERS ajouter dans les sets pour le picker
                eyebrowsFacialCtrl = ['r_brow_CTRL', 'r_browMicroIn_CTRL', 'r_browMicroMid_CTRL', 'r_browMicroOut_CTRL', 'r_furrowOut_CTRL','r_browRot_CTRL','r_furrowIn_CTRL','l_brow_CTRL','l_browMicroIn_CTRL','l_browMicroMid_CTRL','l_browMicroOut_CTRL','l_furrowOut_CTRL','l_browRot_CTRL','l_furrowIn_CTRL']
                eyesFacialCtrl = ['r_eye_upLidBlink_CTRL','l_eye_upLidBlink_CTRL','r_eye_loLidBlink_CTRL','l_eye_loLidBlink_CTRL']
                noseFacialCtrl = ['r_nose_CTRL', 'l_nose_CTRL']
                mouthFacialCtrl = ['r_cheek_CTRL','r_cheekbone_CTRL','l_cheek_CTRL','l_cheekbone_CTRL','mouthAll_CTRL','r_mouth_CTRL','r_corner_CTRL','l_mouth_CTRL','l_corner_CTRL','r_topLip_CTRL','l_topLip_CTRL','mid_topLip_CTRL','mid_botLip_CTRL','r_botLip_CTRL','l_botLip_CTRL','jaw_CTRL','r_pinch_CTRL','l_pinch_CTRL','jawUp_jntCTRL','jawDn_jntCTRL']
                if cmds.objExists("ANIM_BROWS_Set"):
                    cmds.sets(eyebrowsFacialCtrl,e=True,forceElement="ANIM_BROWS_Set")
                if cmds.objExists("ANIM_EYES_Set"):
                    cmds.sets(eyesFacialCtrl,e=True,forceElement="ANIM_EYES_Set")
                if cmds.objExists("ANIM_MOUTH_Set"):
                    cmds.sets(mouthFacialCtrl,e=True,forceElement="ANIM_MOUTH_Set")
                if cmds.objExists("ANIM_NOSE_Set"):
                    cmds.sets(noseFacialCtrl,e=True,forceElement="ANIM_NOSE_Set")
        #lock All Facial nodes under FACIAL_ALL
        #listToLock = cmds.listRelatives(nodeFacial,c=True,ad=True,f=True)
        #for i in listToLock:
        #    cmds.lockNode(i,l=True)

                
            
  




#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////            ACTOR CLEANER          ///////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////

def ActorCleaner():
    rt = RT.referencesTool()
    
    print "======================================"
    print "======================================"
    print "    >>>>> ACTOR CLEANING START <<<<<  "
    print "======================================"
    print "======================================"
    #/////////////////////////////////////////////////////////////////////////////////////////////    
    #//////////////////Initialisation des scripts/////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////

    mel.eval("mgRig_source")
    mel.eval("source dynSolverMenuItems")
    
    cmds.currentTime(1)
    #On Tag les topDag pas en ref
    #    ---------------------------------------------------
    
    '''TODO - TAG des non ref'''
    
    #     On repare les assignations des shaders qui auraient saute sur les mesh en ref
    #    ---------------------------------------------------*/
    mel.eval("mgUtils_fixShaderFromRef")
    
    #/////////////////////////////////////////////////////////////////////////////////////////////    
    #//////////////////IMPORT DES REFS/////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #On part du postulat qu la scene de rig est en ref Et qu le modeling est en ref a l'interieur
    #rt.importAllRef()
    
    
    
    # Cleaner du facial si il existe:
    facial_cleaner()
    modelingGroup = ""
    #    ON ENLEVE TOUS LES NAMESPACES sau celui du modeling
    # ------------------------------------------------------------------------*/
    #RT.removeAllNS()
    rt = RT.referencesTool()
    for ref in rt.topRefs:
        listNodeStepped = [x for x in ref.nodes if cmds.objExists(x+".step")]
        if listNodeStepped:
            if cmds.getAttr(listNodeStepped[0]+".step").upper() == "MODELING":
                ref.importRef(removeNS=True)
                modelingGroup = listNodeStepped[0].split(":")[-1]
            elif cmds.getAttr(listNodeStepped[0]+".step").upper() == "SETUP":
                #On import la ref de RIG
                ref.importRef(removeNS=True)
                if rt.topRefs:
                    for refSecondaries in rt.topRefs:
                        if [n for n in refSecondaries.nodes if "MANIPS_DUPLI" in n]:
                            refSecondaries.importRef(removeNS=True)
    
    #On degage toutes les autres refs
    rt = RT.referencesTool()
    rt.removeAllRef()
    
    
    #/////////////////////////////////////////////////////////////////////////////////////////////  
    #//////////////////CLEAN DES SETS //////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////  

    # TO DO
    
    
    
    #    ON DELOCKE TOUS LES NODES LOCKES
    #    ---------------------------------------------------*/
    FU.mgl7UnlockAllNodes()
    

    print ">>>>> ALL NODES UNLOCKED"
    
    
    #    ON FINIALISE LE FACIAL
    #    ---------------------------------------------------*/
    recreateFacialConnections(modelingGroup)
    print ">>>>> FACIAL DONE"
    

    print "\n======================================";
    print "        >>>>> CLEANING <<<<<";
    print "======================================";
    
    # ------------------------------------------------------------------------*/
    #          Partie des TrashSET a remettre???? 
    # ------------------------------------------------------------------------*/
        
    
    #CLEAN skin clusters
    # --------------------------------------------------------------------------*/
    FU.mgl7CleanSkinCluster()
    print "\n>>>>> CLEAN SKIN CLUSTERS DONE <<<<<";

    #    LOCK skin clusters
    #--------------------------------------------------------------------------*/
    cmds.select (cl=True)
    FU.mgl7LockSkinClusters()
    print "\n>>>>> LOCK SKIN CLUSTERS DONE <<<<<";
    
    """
    # ---------------- Partie en commentaire dans le Happy --------------------
    #    CLEAN clusters
    #--------------------------------------------------------------------------
    cmds.select (cl=True)
    mgl7Clust_optimize(cmds.ls(r=True,type="cluster"))
    print "\n>>>>> CLEAN CLUSTERS DONE <<<<<";
    """
    
    #--------------------------------------------------------------------------
    #-----------------------      Clean des Sets       ------------------------
    #--------------------------------------------------------------------------
    
    #    CLEAN deformSets
    #--------------------------------------------------------------------------
    allDeformSets = cmds.ls("*.mgDeformSet",l=True,o=True,type="objectSet")
    if allDeformSets:
        cmds.delete(allDeformSets)
        
    print "\n>>>>> CLEAN DEFORM SETS DONE <<<<<";

    #    CLEAN unused ANIM Sets
    #--------------------------------------------------------------------------
    if cmds.objExists("ANIM_SET_TO_CHECK"):
        content = cmds.listConnections("ANIM_SET_TO_CHECK.dnSetMembers",s=True,d=False)
        if content:
            cmds.delete(content)
        
        print "\n>>>>> CLEAN ANIM SETS DONE <<<<<"
        
    #    CLEAN unuesed RLO Sets
    #--------------------------------------------------------------------------
    if cmds.objExists("RLO_SETS"):
        content = cmds.listConnections("RLO_SETS.dnSetMembers",s=True, d=False)
        if content:
            cmds.delete(content)

    print "\n\n>>>>> CLEAN RLO SETS DONE <<<<<\n";

    #    CLEAN isolate and shape sets
    #--------------------------------------------------------------------------
    allSets = cmds.ls(type="objectSet")

    for set in [s for s in allSets  if "ViewSelectedSet" in s]:
            if not cmds.referenceQuery(set,inr=True):
                cmds.delete(set)

    print "\n>>>>> CLEAN UNUSED SETS DONE <<<<<";
    
    #    CLEAN TOUS LES SETS AVEC UN NAMESPACE
    #    ----------------------------------
    allSetsToDelete = [x for x in cmds.lsThroughFilter('defaultSetFilter') if ":" in x]
    for set in allSetsToDelete:
        if not cmds.referenceQuery(set,inr=True):
            print set
            cmds.delete(set)    

    #    CLEAN TRIM SETS (encore utile???)
    #--------------------------------------------------------------------------
    trimSets = cmds.ls("*TRIM*SET",r=True)
    if trimSets:
        cmds.delete(trimSets)

    #    CLEAN RESULTS GROUPS (encore utile???)
    # --------------------------------------------------------------------------
    tplResultGrps = cmds.ls("*.mgTplResultsGrp",o=True)
    if tplResultGrps:
        cmds.delete(tplResultGrps)

    print "\n>>>>> CLEAN RESULT GROUPS DONE <<<<<";
    
    
    # --------------------------------------------------------------------------
    # --- ON NETTOIE TOUS LES FRAMECACHE
    # --- (qui provoquent des cycles lors de contraintes d'un perso sur un autre)
    # --- on liste tous les framecache, on remonte dans les iks correspondantes, et on les passe une par une
    # --- au script qui "bake" les framecache et qui les nettoie
    # ----------------------------------------------------------------------------------------------------------

    #    NETTOYAGE DES FRAMECACHES SUR LES IKS
    # --------------------------------------------------------------------------
    ikHandles= cmds.ls(type="ikHandle")
    if ikHandles :
        for ik in ikHandles:
            FU.mgl7CleanIkFrameCaches(ik)
            
    print "\n>>>>> CLEAN FRAMECACHES DONE <<<<<"

    #    CLEAN animCurves residuelles restees eventuellement dans l'actor
    # --------------------------------------------------------------------------*/
    FU.mgl7cleanAnimCurves(1)

    print "\n>>>>> CLEAN ANIM CURVES DONE <<<<<";


    #   Remove vray viewport previews
    #---------------------------------------------------------------------

    if cmds.objExists("vraySettings"):
       envPrev = cmds.ls(type="VRayEnvironmentPreview")
       for item in envPrev:
           parent = MT.getShapeAndTrm(item)[1] # get the parent transform
           children = cmds.listRelatives(parent,path=True,children=True)
           if len(children) == 1: # if parent has only 1 children, delete it
               cmds.delete(parent)
           else:
               cmds.delete(item) # else delete only the node





    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////


    print "\n======================================";
    print "        >>>>> RANGEMENT <<<<<          ";
    print "======================================";

    #    CREATION GROUPE ALL
    # --------------------------------------------------------------------------
    ALL_grp = "|"+cmds.group(em=True)    #-- astuce pour recuperer le nom long du groupe cree
    #    --- lock attributs
    FU.mgl7Do_mgUtils_attr(ALL_grp,"lockHide",["t","r","s"],[])

    #    CREATION GROUPE TO_CHECK SOUS ALL
    # --------------------------------------------------------------------------
    TO_CHECK_grp = cmds.group(em=True,p=ALL_grp)
    cmds.setAttr(TO_CHECK_grp+".v", 0)
    #--- lock attributs
    FU.mgl7Do_mgUtils_attr(TO_CHECK_grp,"lockHide",["t","r","s"])
    FU.mgl7Do_mgUtils_attr(TO_CHECK_grp,"unkeyable",["v"])


    #    METTRE TPL_ACTOR: DANS ALL
    # --------------------------------------------------------------------------
    ACTOR = cmds.ls("*.mgOrigin",r=True, o=True)
    if cmds.objExists(ACTOR[0]):
        cmds.parent(ACTOR,ALL_grp)
        print ("\n>>>>> PARENTED "+ ACTOR[0]+" UNDER ALL GROUP <<<<<")
    else:
        print ("\n>>>>> NO ACTOR TO PARENT UNDER ALL GROUP <<<<<")

    #    METTRE LE MODELING DANS ALL 
    # --------------------------------------------------------------------------
    if modelingGroup != "":
        MODELING_root = modelingGroup
        #--- lock attributs
        FU.mgl7Do_mgUtils_attr(MODELING_root,"lockHide",["t","r","s"])
        FU.mgl7Do_mgUtils_attr(MODELING_root,"unkeyable",["v"])
        
        if cmds.getAttr(MODELING_root + ".v",se=True):
            cmds.setAttr(MODELING_root + ".v", 1)

        if MODELING_root != ALL_grp:
            cmds.parent(MODELING_root,ALL_grp)

        print ("\n>>>>> PARENTED "+ MODELING_root +" UNDER ALL GROUP <<<<<")
    else:
        print ("\n>>>> MODELING NOT PARENTED UNDER ALL GROUP <<<<<")
  
    #    METTRE FACIAL DANS ALL ET AJOUT DU NAMESPACE -TODO : Partie Facial A verifier
    # --------------------------------------------------------------------------*/
    if cmds.objExists("FACIAL_ALL"):
    
        cmds.parent("FACIAL_ALL", ALL_grp)
        print ("\n>>>>> PARENTED FACIAL_ALL UNDER ALL GROUP  <<<<<");

        '''
        facial_ns = "FACIAL";
        cmds.namespace(facial_ns,add=True)
        
        facial_content = FU.mgl7HierarchySort(cmds.ls("FACIAL_ALL",l=True,dag=True), 1);
        dontRename = cmds.ls("FROM_ACTOR_RIG",l=True,dag=True)
        for i in dontRename:
            facial_content.remove(i)
        for item in facial_content:
            sn = cmds.ls(item,sn=True)[0]
            cmds.rename(item,facial_ns + ":" + sn)
        '''
    else:
        print ("\n>>>>> NO FACIAL_ALL TO PARENT UNDER ALL GROUP  <<<<<")

    #    METTRE MANIPS_DUPLI DANS ALL
    # --------------------------------------------------------------------------*/

    if cmds.objExists("MANIPS_DUPLI"):
        cmds.parent("MANIPS_DUPLI",ALL_grp)
        print ("\n>>>>> PARENTED MANIPS_DUPLI UNDER ALL GROUP  <<<<<")
    else:
        print ("\n>>>>> NO MANIPS_DUPLI TO PARENT UNDER ALL GROUP  <<<<<")

    #    METTRE HAIRS DANS ALL
    # --------------------------------------------------------------------------*/

    if cmds.objExists("HAIR_ALL"):
        cmds.parent("HAIR_ALL",ALL_grp)
        print ("\n>>>>> PARENTED HAIR_ALL UNDER ALL GROUP  <<<<<")
    else:
        print ("\n>>>>> NO HAIR_ALL TO PARENT UNDER ALL GROUP  <<<<<")



    #    METTRE LOW_DEF DANS ALL
    # --------------------------------------------------------------------------*/
    if (cmds.objExists("LOWDEF")):
        cmds.parent("LOWDEF",ALL_grp)
        print ("\n- PARENTED LOWDEF UNDER ALL GROUP")
    elif cmds.objExists("BDD:LOWDEF"):
        cmds.parent("BDD:LOWDEF",ALL_grp)
        print ("\n>>>>> PARENTED BDD:LOWDEF UNDER ALL GROUP <<<<<");
    else:
        print ("\n>>>>> NO LOWDEF TO PARENT UNDER ALL GROUP <<<<<");
        
    #    GROUPER TOUS LES OBJETS RESIDUELS NON RIGGES DANS TO_CHECK
    # --------------------------------------------------------------------------*/
    topDagList = MT.getTopDags(noUndeletableNodes=True)
    residus = topDagList.remove(ALL_grp)

    if residus and cmds.objExists(ALL_grp):
        cmds.parent(residus, TO_CHECK_grp)
        print (">>>>> PARENTED :\t\t"+ residus+ " IN TO_CHECK <<<<<")

    #    RENOMMAGE GROUPES RANGEMENTS
    # --------------------------------------------------------------------------*/
    cmds.rename(ALL_grp, "ALL")
    ALL_grp = "ALL"
    cmds.rename( TO_CHECK_grp, "TO_CHECK")
        

    #    ON COMPACTE TOUS LES SETS
    #    ----------------------------------*/
    cmds.sets(em=True,n= "ALL_SETS")

    topSets = FU.mgl7ListTopSets()
    listSetToParent = cmds.sets([ts for ts in topSets if not len(ts.split("tweak"))>1 and not len(ts.split("sknClust"))>1 and not len(ts.split("ALL_SETS"))>1],add="ALL_SETS")


    print ("\n>>>>> COMPACT SETS DONE <<<<<");

    
    # CLEAN LE RESTE QUI N'EST PAS DANS LE GROUPE ALL
    #    ----------------------------------*/
    print ">>>>>>>> CLEAN DES TOP DAG <<<<<<<<<"
    listDontTouch = ["|top","|front","|side","|persp","|ALL"]
    listToDelete = [x for x in MT.getTopDags() if not x in listDontTouch]
    for x in listToDelete:
        print "topDag " +str(x) + " is deleted!"
        cmds.delete(x)

    # CLEAN LES DISPLAY LAYERS
    # ---------------------------------------------*/
    displayLayerNotRemove = ["BDD_"]
    layers = cmds.ls(type="displayLayer")
    saveLayers = []
    for i in displayLayerNotRemove:
        saveLayers.extend(cmds.ls("*" + i + "*",type="displayLayer"))
    defaultLayer = cmds.ls("defaultLayer",type="displayLayer")
    saveLayers.extend(defaultLayer)
    
    deleteLayers = layers
    if saveLayers:
        deleteLayers = [x for x in layers if x not in saveLayers]
    
    if deleteLayers:
        cmds.delete(deleteLayers)
        
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    print "\n======================================";
    print "       >>>>> FINISH / UTILITIES <<<<<   ";
    print "========================================";

    
    #    RESETTER TOUS LES MANIPS AU CAS OU ILS AURAIENT ETE BOUGES DANS LA SCENE DE SKIN
    # --------------------------------------------------------------------------*/
    """
    topSets = cmds.ls("*.mgAnimTopSet",o=True)
    allAnim = []
    if len(topSets):
        allAnim = mel.eval("mgUtils_listSetContent "+topSets)
        mel.eval("mgAnim_resetAttr"+ allAnim)
        print "\n>>>>> RESETMANIPS DONE <<<<<"
    """


    #    REPASSER LES JAMBES EN IK ET LES BRAS EN FK
    # --------------------------------------------------------------------------*/
    allLimbTpls = FU.mgl7FindRigType("LIMB")
    position=""
    name=""
    ikBlendManip=""
    
    for tpl in allLimbTpls:
        position = cmds.getAttr(tpl+".mgRigPosition")
        name = tpl.replace("TPL_","")
        
        ikBlendManip = name+"_SWITCH"
        
        if cmds.objExists(ikBlendManip+".ikBlend"):
            if (position == "arm"):
               cmds.setAttr(ikBlendManip+".ikBlend",0) 
            if (position == "leg"):
               cmds.setAttr(ikBlendManip+".ikBlend",1)
         
        print "\n>>>>> LEGS AND ARMS CHECKED <<<<<";


    #    ON CREE LES DUPLIS DES MANIPS QUI AURAIENT ETE AJOUTES APRES L'ACTOR CLEANER (EX : STICKYS)
    # --------------------------------------------------------------------------------------------------*/
    topSets = cmds.ls("*.mgAnimTopSet",l=True, r=True, o=True, type="objectSet")
    if topSets:
        setsToManips = mel.eval("mgRig_setsToManips")
        if setsToManips:
            print "\n>>>>> SETS TO MANIPS DONE <<<<<";
        else:
            cmds.warning("\n>>>>> SETS TO MANIPS FAILED <<<<<")
    
    #    METTRE MANIPS DUPLI DANS ALL
    #--------------------------------------------------------------------------*/
    ALL_grp = "ALL"
    if cmds.objExists(setsToManips[0]) and len(cmds.ls(setsToManips[0],l=True)[0].split("|"+ALL_grp))==1:
        cmds.parent(setsToManips[0],ALL_grp)
        print ("\n>>>>> PARENTED MANIPS DUPLI UNDER ALL GROUP  <<<<<")

    #    ATTRIBUT mgNoSelect sur tous les objets que les animateurs ne doivent pas selectionner
    # --------------------------------------------------------------------------*/
    allMeshes = cmds.listRelatives(cmds.ls(type="mesh"),p=True,type="transform")

    if cmds.objExists("ANIM_SET"):
        allManips = cmds.ls(FU.mgl7ListSetContent (["ANIM_SET"]),l=True)
        allManipsDuplis = cmds.ls("*.mgManipDupli",l=True,o=True)
        allFacialDuplis = cmds.ls("*.mgAttrManip",l=True,o=True)
        allNodes = cmds.ls(l=True,type="transform")

        toLockNodes = [x for x in allNodes if x not in allManips]
        toLockNodes  = [x for x in toLockNodes if x not in allManipsDuplis]
        toLockNodes  = [x for x in toLockNodes if x not in allFacialDuplis]
        toLockNodes  = [x for x in toLockNodes if x not in allMeshes]

        for n in toLockNodes:
            if cmds.objExists(n) and not cmds.objExists(n+".mgNoSelect") and ("*MANIPS_DUPLI" not in n) :
                cmds.addAttr(n,ln="mgNoSelect",at="bool")
    print "\n>>>>> NO SELECT DONE <<<<<"


    #    AFFICHAGE DES SETS D"ANIM ET HIDE DES SHAPES DE CLUSTER
    # --------------------------------------------------------------------------------*/
    cmds.select(cl=True)

    animSet = "ANIM_SET"
    if cmds.objExists(animSet):
        cmds.showHidden(animSet,a=True)

    allInScene = cmds.ls(l=True,dag=True,type="transform")

    for ctrl in allInScene:
        shapes = cmds.listRelatives(ctrl,f=True, s=True)
        if shapes:
            for shape in shapes:
                if cmds.nodeType(shape) == "clusterHandle" and cmds.getAttr(shape+".v",se=True):
                    cmds.setAttr(shape+".v", 0)


    print "\n>>>>> ALL ANIM CTRLS VISIBLE DONE <<<<<";



    #    ON CALCULE LES IMAGES POUR L'INTERFACE DE SELECTION (TODO - obsolete?)
    # --------------------------------------------------------------------------*/
        #mel.eval("mgRig_makeId;")

        #print "\n>>>>> MAKE IDS DONE <<<<<";

    #    ON CONFORME TOUS LES RADIUS DES JOINTS A 0.05
    # --------------------------------------------------------------------------------*/
    allJoints = cmds.ls(l=True,type="joint")
    for jnt in allJoints:
        if cmds.getAttr(jnt+".radius",se=True):
            cmds.setAttr(jnt+".radius",0.05)
    #    ON SE MET EN DISPLAY DE SUBDIV 1
    #    ----------------------------------*/
    cmds.displaySmoothness(cmds.ls(),divisionsU=0, divisionsV=0, pointsWire=4, pointsShaded=1, polygonObject=1)
        

    #    ON CACHE LES DEFORMERS
    # --------------------------------------------------------------------------------*/
    lattices = cmds.ls(type="lattice")
    clusters = cmds.ls(type="clusterHandle")
    deformers = lattices.extend(clusters)
    if deformers:
        for d in deformers:
            if cmds.getAttr(d+".v",se=True):
                cmds.setAttr (d+".v", 0)

    print "\n>>>>> DEFORMERS HIDDEN <<<<<";

    #    ON REASSIGNE LES SHADERS STOCKES DANS LE NODE CREE PAR LE MODEL CLEANER
    # --------------------------------------------------------------------------------*/
    FU.mgl7ShadingSetsImportExport("read", "BDD:", "", "")

    #    ON CACHE LES HISTORIQUE AVEC UN ATTRIBUT CACHE DANS LE POSITION     (attention il faut rajouter une manip supplementaire dans le makeCustom)
    # --------------------------------------------------------------------------------*/
    fileName = cmds.file(q=True,sn=True)
    if "/CHARS/" in fileName:
        #   Creation du set CHARS_POS_SET (Utilisation FLO => anim)
        # ------------------------------------------------------------------*/

        if cmds.objExists("POSITION") and cmds.objExists("TRAJ"):
            cmds.sets(n="CHARS_POS_SET")
            cmds.sets(["POSITION", "TRAJ"],add="CHARS_POS_SET")
            cmds.addAttr("CHARS_POS_SET",ln="mgPosSet",at="bool")
            if cmds.objExists("ALL_SETS"):
                cmds.sets("CHARS_POS_SET",add="ALL_SETS")

    mgSets = cmds.sets("ALL_SETS",q=True)
    set2Ignore = ["defaultObjectSet","BDD:CFX_CHARS_EXPORT_SET"]
    mgSets = [x for x in mgSets if x not in set2Ignore]

    for ms in mgSets:
        attrSet = cmds.listAttr(ms,st="mg*")
        if not attrSet:
            cmds.delete(ms)


    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////////////////////////////////////////
    print "\n======================================";
    print "          >>>>> LOCKS <<<<<";
    print "======================================";


    #    LOCK DE TOUS LES OBJETS
    # --------------------------------------------------------------------------*/

    if allMeshes:
        for obj in allMeshes:
            if cmds.objExists(obj):
                if not cmds.referenceQuery(obj,inr=True):
                    if cmds.objectType(obj)!= "transform":
                        obj = mel.eval("firstParentOf "+obj)
                    cmds.setAttr(obj+".tx",lock=True)
                    cmds.setAttr(obj+".ty",lock=True)
                    cmds.setAttr(obj+".tz",lock=True)
                    cmds.setAttr(obj+".rx",lock=True)
                    cmds.setAttr(obj+".ry",lock=True)
                    cmds.setAttr(obj+".rz",lock=True)
                    cmds.setAttr(obj+".sx",lock=True)
                    cmds.setAttr(obj+".sy",lock=True)
                    cmds.setAttr(obj+".sz",lock=True)

    print "\n>>>>> LOCK MESHES DONE <<<<<";

    #    LOCK DES COURBES D'ANIM RESTANTES QUI SONT EN PRINCIPE TOUTES LES DRIVENKEYS
    # --------------------------------------------------------------------------*/
    animCrv = cmds.ls(type="animCurve")
    if animCrv:
        for crv in animCrv:
            cmds.setAttr(crv + ".keyTimeValue",l=True)
        print "\n>>>>> LOCK DRIVEN KEYS DONE <<<<<";

    #    LOCKAGE DE TOUS LES ATTRIBUTS TAGGES POUR CA
    # --------------------------------------------------------------------------------*/
    mel.eval("mgUtils_bigLock;")
    print "\n>>>>> BIG LOCK DONE <<<<<"


    #    CLEAN TPLs MEMBERS
    # --------------------------------------------------------------------------*/
    FU.mgUtils_membersCleaner()

    print "\n>>>>> CLEAN TPLs MEMBERS DONE <<<<<";




    print "\n======================================";
    print "         >>>>> CUSTOM / TEMP <<<<<";
    print "======================================";


    #    On cache des attributs inutiles sur le lookAt
    # --------------------------------------------------------------------------------
    lookAt = "lookAt_ctrl"
    facial_version = mel.eval("mgFacial_checkVersion(1)")
    if cmds.objExists(lookAt):
        if facial_version <4:
            attrsToLock = cmds.listAttr(lookAt,k=True, string=["*_eye_upLid*","*_eye_loLid*"])
            FU.mgl7Do_mgUtils_attr(lookAt,"lockHide",attrsToLock,[])
        else:
            userAttrs = FU.mgl7ListChannelBoxAttrs(lookAt,"userDefined")
            FU.mgl7Do_mgUtils_attr(lookAt,"lockHide",userAttrs,["FREE_AIM","aimLook"])


    #    ON RELOADE LE CONTENU DES SETS D'EXPORTS
    #    ----------------------------------

        if cmds.objExists("BDD:MODEL_HI"):
            FU.mgl7SetContentToAttr("read", "BDD:", "BDD:MODEL_HI")
        print "\n>>>>> EXPORT SET CLEANED <<<<<";

    #    HIDE DES ENVELOPPES NURBS
    # --------------------------------------------------------------------------
    nurbsElem = cmds.ls("MECHES_GRP_NURBS",r=1)
    nurbsElem = nurbsElem.extend(cmds.ls("hairsCurves",r=1))
    
    if nurbsElem:
        for ne in nurbsElem:
            cmds.setAttr(ne + ".v",0)
    
    '''
    # ON INSTALL LES LOCATORS DES EYES POUR LE LIGHTING
    # --------------------------------------------------------------------------
    if cmds.objExists("l_eye_loc"):
        cmds.delete("l_eye_loc")
    if cmds.objExists("r_eye_loc"):
        cmds.delete("r_eye_loc")

    FU.mgl7EyesTransformExport()
    print ">>>>> DONE LOC EYES <<<<<";
    '''
    #    TEMPORAIRE : ON MET LES ALLOWSQUASH A 1 ET ON LEUR SETTE 1 COMME DV
    # --------------------------------------------------------------------------*/
    allowSquashAttrs = cmds.ls("*.allowSquash",r=1)
    for attr in allowSquashAttrs:
        if cmds.getAttr(attr,se=True):
            cmds.setAttr(attr,1)
            cmds.addAttr(attr,e=True,dv=1)

    #    ON CACHE LES EMITTERS
    # --------------------------------------------------------------------------*/
    emitters= cmds.ls("BDD:*Emitters")
    for i in range(0,len(emitters)):
        cmds.setAttr(emitters[i]+".visibility", 0)

    '''
    #    SHADING MOUTH POUR ANIM (TO-DO - UTILITE???)
    # --------------------------------------------------------------------------*/
    filename = cmds.file(q=True,sn=True)

    if not "-Rlo-" in filename and "/CHARS/" in filename:
        mel.eval(mgAnim_MouthShading)
    '''

    #    on installe un groupParts devant chaque inMesh d'un poly si celui ci prend
    #    une connection en entree, comme ca le Lo et le Hi seront raccord
    # --------------------------------------------------------------------------
    FU.mgl7InstallGroupParts()
    print ">>>>> GROUP PARTS INSTALLED <<<<<"


    #    on trouve le groupParts en entree de la shapeDeformed et on le renome pour eviter
    #    les deconnection due a des deformers par la suite
    # --------------------------------------------------------------------------*/
    FU.mgl7RenameGroupParts()
    print ">>>>> GROUP PARTS RENAMED <<<<<";
    
    
        
    
    print "======================================";
    print "    >>>>> ADDITIONNAL CLEAN <<<<<";
    print "======================================";
    
    
    
    #LookAt
    if cmds.objExists("lookAt_ctrl"):
        cmds.setAttr("lookAt_ctrl.rx",k=True, lock=False)
        cmds.setAttr("lookAt_ctrl.ry",k=True, lock=False)
        cmds.setAttr("lookAt_ctrl.rz",k=True, lock=False)
        
        #Left eye
        cmds.setAttr("l_eye.tx",k=True, lock=False)
        cmds.setAttr("l_eye.ty",k=True, lock=False)
        cmds.setAttr("l_eye.tz",k=True, lock=False)
        cmds.setAttr("l_eye.sx",k=True, lock=False)
        cmds.setAttr("l_eye.sy",k=True, lock=False)
        cmds.setAttr("l_eye.sz",k=True, lock=False)
        
        #Right eye
        cmds.setAttr("r_eye.tx",k=True, lock=False)
        cmds.setAttr("r_eye.ty",k=True, lock=False)
        cmds.setAttr("r_eye.tz",k=True, lock=False)
        cmds.setAttr("r_eye.sx",k=True, lock=False)
        cmds.setAttr("r_eye.sy",k=True, lock=False)
        cmds.setAttr("r_eye.sz",k=True, lock=False)
    



    #SETTER LE GLOBAL SCALE (Juline)
    # --------------------------------------------------------------------------*/
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
    # --------------------------------------------------------------------------*/



    #recuperation des infos SG
    current_engine = sgtk.platform.current_engine()
    if current_engine:
        
        scene_path = cmds.file(q=True,sn=True)
        current_engine = sgtk.platform.current_engine()
        tk = current_engine.sgtk
        ctx = current_engine.context   # le context courant de la scene
        work_template = tk.template_from_path(scene_path)
        template_fields = work_template.get_fields(scene_path)
        taskSg = current_engine.context.task["name"]

        #recuperer le template de publish a partir de celui de work
        publish_template = get_publish_template_from_work_template(tk,
        work_template)
        VersionLastPublish = str(int(get_latest_publish_version(tk,
                                         ctx,
                                        "Maya Scene",
                                        publish_template,
                                        template_fields) ) + 1)
        
        code = ctx.entity["name"]
        id = ctx.entity["id"] 
        sg_asset_type_current = work_template.get_fields(scene_path).get("sg_asset_type")
        stepSg = ctx.step["name"]
        
        sg_mg_subtype = tk.shotgun.find("Asset", 
                      [ ["project", "is", ctx.project], 
                        ["id", "is", ctx.entity["id"]]],
                        ["sg_mg_subtype"])[0]["sg_mg_subtype"]      
        
        cmds.addAttr(ALL_grp,ln="code",dt="string")
        cmds.addAttr(ALL_grp,ln="sg_asset_type",dt="string")
        cmds.addAttr(ALL_grp,ln="sg_mg_subtype",dt="string")
        cmds.addAttr(ALL_grp,ln="id",dt="string")
        cmds.addAttr(ALL_grp,ln="revision",dt="string")
        cmds.addAttr(ALL_grp,ln="published_file_type",dt="string")
        cmds.addAttr(ALL_grp,ln="step",dt="string")
        cmds.addAttr(ALL_grp,ln="task",dt="string")
        
        if code:
            cmds.setAttr(ALL_grp+".code",code,typ="string")
        if sg_asset_type_current:
            cmds.setAttr(ALL_grp+".sg_asset_type",sg_asset_type_current,typ="string")
        if sg_mg_subtype:
            cmds.setAttr(ALL_grp+".sg_mg_subtype",sg_mg_subtype,typ="string")
        if id:
            cmds.setAttr(ALL_grp+".id",id,typ="string")
        if VersionLastPublish:
            cmds.setAttr(ALL_grp+".revision",VersionLastPublish,typ="string")
        cmds.setAttr(ALL_grp+".published_file_type","maya_scene",typ="string")
        if stepSg:
            cmds.setAttr(ALL_grp+".step",stepSg,typ="string")
        if taskSg:
            cmds.setAttr(ALL_grp+".task",taskSg,typ="string")

        cmds.rename(ALL_grp,code+"_Actor")

    
    print "======================================\n";
    print "    >>>>> CLEANING DONE <<<<<\n";
    print "======================================\n";



    print "======================================";
    print "======================================";
    print "    >>>>> ACTOR CLEANING DONE <<<<<";
    print "======================================";
    print "======================================\n\n";
























