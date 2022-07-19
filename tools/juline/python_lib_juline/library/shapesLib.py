# coding: utf-8
# author Juline BRETON

import maya.cmds as mc


def rename_shapes(ls_transform):
    for obj in ls_transform:
        #lShp = mc.listRelatives(obj, shapes=True) or []
        ls_shp = mc.listRelatives(obj, shapes=True, fullPath=True) or []
        if len(ls_shp) > 1:
            for i in range(len(ls_shp)):
                if not mc.listAttr(ls_shp[i], userDefined=True):  # if not instance shape with extra attr
                    mc.rename(ls_shp[i].split('|')[-1], obj + 'Shape' + str(i + 1))
        if len(ls_shp) == 1:
            print "ls_shp", ls_shp
            if not mc.listAttr(ls_shp[0], userDefined=True):  # if not instance shape with extra attr
                if not mc.objExists(obj + 'Shape'):
                    try:
                        mc.rename(ls_shp[0], obj + 'Shape')
                    except:
                        print obj + " shape(s) can't be renamed"
                else:
                    try:
                        mc.rename(ls_shp[0], obj + 'Shape1')
                    except:
                        print obj + " shape(s) can't be renamed"

##lCtrl = ctrlShapesLib.get_all_ctrl()
##rename_shapes(lCtrl)