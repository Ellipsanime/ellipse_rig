"""
PROUST VARIATIONS

VAR_COST
[u'varcost_shirt_msh', u'varcost_Lcuff_msh', u'varcost_col_msh', u'varcost_Rcuff_msh', u'varcost_button_msh', u'varcost_pants_msh', u'varcost_petale9_msh', u'varcost_petale8_msh', u'varcost_petale7_msh', u'varcost_petale6_msh', u'varcost_petale5_msh', u'varcost_petale4_msh', u'varcost_petale3_msh', u'varcost_petale2_msh', u'varcost_petale1_msh', u'varcost_flower_msh', u'varcost_chest2_msh', u'varcost_chest1_msh', u'varcost_chest3_msh', u'varcost_r_shoe_msh', u'varcost_l_shoe_msh', u'EyesRig_EyeRig:x_eye_ctl', u'hair_msh', u'mustache_msh', u'l_eyebrows_msh', u'l_eyebrowsLock_msh', u'r_eyebrows_msh', u'r_eyebrowsLock_msh', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'bud_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh']

VAR_VILLE

[u'varcost_shirt_msh', u'varcost_Lcuff_msh', u'varcost_Rcuff_msh', u'varcost_pants_msh', u'varcost_r_shoe_msh', u'varcost_l_shoe_msh', u'varville_strand_msh', u'varville_pearl_msh', u'varville_tie_msh', u'varville_col_msh', u'varville_tissue_msh', u'varville_pocket_msh', u'EyesRig_EyeRig:x_eye_ctl', u'hair_msh', u'mustache_msh', u'l_eyebrows_msh', u'l_eyebrowsLock_msh', u'r_eyebrows_msh', u'r_eyebrowsLock_msh', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'bud_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh']
"""


import maya.cmds as mc

sel = mc.ls(sl=True)
print sel

sel = [u'varcost_shirt_msh', u'varcost_Lcuff_msh', u'varcost_col_msh', u'varcost_Rcuff_msh', u'varcost_button_msh', u'varcost_pants_msh', u'varcost_petale9_msh', u'varcost_petale8_msh', u'varcost_petale7_msh', u'varcost_petale6_msh', u'varcost_petale5_msh', u'varcost_petale4_msh', u'varcost_petale3_msh', u'varcost_petale2_msh', u'varcost_petale1_msh', u'varcost_flower_msh', u'varcost_chest2_msh', u'varcost_chest1_msh', u'varcost_chest3_msh', u'varcost_r_shoe_msh', u'varcost_l_shoe_msh', u'EyesRig_EyeRig:x_eye_ctl', u'hair_msh', u'mustache_msh', u'l_eyebrows_msh', u'l_eyebrowsLock_msh', u'r_eyebrows_msh', u'r_eyebrowsLock_msh', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'bud_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh']
selVarCost = []
for s in sel:
    s2 = str("Proust_ModelingOk:" + s)
    print s2
    selVarCost.append(s2)
    
print selVarCost
print len(selVarCost)
mc.select(clear=True)
for Item in selVarCost:
    mc.select(Item, add=True)

print type(selVarCost)

"""
var A :
[u'EyesRig_EyeRig:x_eye_ctl', u'EyesRig_EyeRig:l_eye_ctl', u'EyesRig_EyeRig:l_choroid_srf', u'EyesRig_EyeRig:l_cornea_srf', u'EyesRig_EyeRig:l_iris_srf', u'EyesRig_EyeRig:l_highlight_srf', u'EyesRig_EyeRig:l_pupil_srf', u'EyesRig_EyeRig:l_specular1_srf', u'EyesRig_EyeRig:l_specular1_ctl', u'EyesRig_EyeRig:r_eye_ctl', u'EyesRig_EyeRig:r_choroid_srf', u'EyesRig_EyeRig:r_cornea_srf', u'EyesRig_EyeRig:r_iris_srf', u'EyesRig_EyeRig:r_highlight_srf', u'EyesRig_EyeRig:r_pupil_srf', u'EyesRig_EyeRig:r_specular1_srf', u'EyesRig_EyeRig:r_specular1_ctl', u'EyesRig_EyeRig:x_eye_directionalLight1', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_hair_msh', u'varA_hair_locks_msh', u'varA_l_eyebrows_msh', u'varA_r_eyebrows_msh', u'varA_mustache_msh', u'varA_mustache_locks_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh']
var B :
[u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varB_hair_msh', u'varB_l_eyebrows_msh', u'varB_r_eyebrows_msh', u'varB_mustache_msh']
var C :
[u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varB_hair_msh', u'varC_hair_msh', u'varC_l_eyebrows_msh', u'varC_r_eyebrows_msh']
var D :
[u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varB_hair_msh', u'varD_l_eyebrows_msh', u'varD_r_eyebrows_msh', u'varD_mustache_msh']
var MMgardeN :
[u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varB_hair_msh', u'varC_hair_msh', u'varC_l_eyebrows_msh', u'varC_r_eyebrows_msh']
var papaB :
[u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_mustache_msh', u'varA_mustache_locks_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varPapaB_beret_msh', u'varPapaB_l_eyebrows_msh', u'varPapaB_r_eyebrows_msh', u'varPapaB_hair_msh', u'varPapaB_coat_msh']
var passantA :
[u'EyesRig_EyeRig:x_eye_ctl', u'varPassantA_hat_msh', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hair_msh', u'varA_hair_locks_msh', u'varA_l_eyebrows_msh', u'varA_r_eyebrows_msh', u'varA_mustache_msh', u'varA_mustache_locks_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh']
"""


import maya.cmds as mc

sel = [u'EyesRig_EyeRig:x_eye_ctl', u'l_up_eyelashes_msh', u'l_dn_eyelashes_msh', u'r_up_eyelashes_msh', u'r_dn_eyelashes_msh', u'up_gum_msh', u'dn_gum_msh', u'up_teeth_msh', u'dn_teeth_msh', u'tongue_msh', u'body_msh', u'l_hand_msh', u'r_hand_msh', u'varA_hatA_msh', u'varA_hatB_msh', u'varA_col_msh', u'varA_shirt_msh', u'varA_tie_msh', u'varA_l_cuff_msh', u'varA_r_cuff_msh', u'varA_coat_msh', u'varA_l_shoe_msh', u'varA_r_shoe_msh', u'varA_pants_msh', u'varB_hair_msh', u'varD_l_eyebrows_msh', u'varD_r_eyebrows_msh', u'varD_mustache_msh']
selVarSkinOk = []

for s in sel:
    s2 = s.split(":")[-1]
    selVarSkinOk.append(s2)
    
mc.select(selVarSkinOk)