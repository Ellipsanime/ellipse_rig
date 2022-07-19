# coding: utf-8
# 2019 Juline BRETON
#
# [X] 1_ Depuis le tpl info trouver le type de module creer le groupe de locator dedie
# [X] 2_ Sur le group des loc ajouter des attr d'info avec le parent et les enfants du module
# [X] 3_ Lister dans l'ordre de mise en place les ctrl (ordre des attributs sur le TPL info à partir du master tpl)
# [X] 4_ Creer les locators dans cette ordre et stocker leur nom dans une liste (pour conserver l'ordre)
# [ ] 5_ Supprimer le module
# [ ] 6_ Rebuilder le rig avec les nouveaux parametres et resetter info PARENT, ENFANT et avec le meme NOM !!
# [ ] pour garder l'inc dans guide_base il faudrait changer la ligne 38 qui ne serait active que si la nouvelle variable incVal n'est pas reneignée par l'utilisateur
# [ ] 7_ Snaper les nouveaux controlleur sur les locators > WARNING POP UP pour flagger ce qui n'a put etre remis en place

import maya.cmds as mc

def create_locator_position(tpl):
    #grp_loc_module = create_module_groupe_locator(tpl_info)
    loc = mc.spaceLocator(tpl, name=tpl.replace('tpl', 'loc'))[0]
    #mc.parent(loc, grp_loc_module)
    snap(loc, tpl)
    return loc

def create_group(name):
    if not mc.objExists(name):
        grp = mc.createNode('transform', name=name)
    else:
        grp = name
    return grp

def snap(slave, master):
    print 'master', master, 'slave', slave
    # check if attr t and r are locked
    ls_axis = ['x', 'y', 'z']
    ls_trs_locked = []
    ls_rot_locked = []
    for axis in ls_axis:
        if mc.getAttr(slave + '.t' + axis, lock=True):
            ls_trs_locked.append(axis)
        if mc.getAttr(slave + '.r' + axis, lock=True):
            ls_rot_locked.append(axis)
    const = mc.parentConstraint(master, slave, maintainOffset=False, skipTranslate=ls_trs_locked, skipRotate=ls_rot_locked)
    mc.delete(const)

def create_module_group_locator(tpl_info):
    # check if group already exist
    if not mc.objExists('LOC_KEEP_POSITION'):
        grp_loc = create_group('LOC_KEEP_POSITION')
    else:
        grp_loc = 'LOC_KEEP_POSITION'
    name_grp_loc_module = 'GRP_LOC_' + mc.getAttr(tpl_info + '.moduleType') + '_' + mc.getAttr(tpl_info + '.incInfo')
    if mc.objExists(name_grp_loc_module):
        mc.delete(name_grp_loc_module)
    grp_loc_module = create_group(name_grp_loc_module)
    mc.parent(grp_loc_module, grp_loc)

    return grp_loc_module