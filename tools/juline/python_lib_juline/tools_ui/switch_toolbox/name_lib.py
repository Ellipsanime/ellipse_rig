# coding: utf-8

class SwitchName(object):
    # Attribute info
    MOD_DICT =     'dict_state_vis'
    POS_DICT =     'dict_state_pos'
    SHD_DICT =     'dict_state_tex'
    ANI_DICT =     'dict_state_ani'
    ALL_DICT = (MOD_DICT, POS_DICT, SHD_DICT, ANI_DICT)

    # Attribute info long name
    MOD_DICT_LONG = 'MOD_CTRL.dict_state_vis'
    POS_DICT_LONG = 'dict_state_pos'
    SHD_DICT_LONG = 'SHD_CTRL.dict_state_tex'
    ANI_DICT_LONG = 'c_rigAdd.dict_state_ani'
    ALL_DICT_LONG = (MOD_DICT_LONG, POS_DICT_LONG, SHD_DICT_LONG, ANI_DICT_LONG)

    # CTRL_SWITCH
    MOD_CTRL =     'MOD_CTRL'
    SHD_CTRL =     'SHD_CTRL'
    ANI_CTRL =     'c_rigAdd'
    ALL_SWITCH_CTRL = (MOD_CTRL, SHD_CTRL, ANI_CTRL)

    # PREFIXE
    MOD_PREFIX =   'mod_'
    TEX_PREFIX =   'tex_'
    LGT_PREFIX =   'lgt_'
    ANI_PREFIX =   'ubi_'
    ALL_SWITCH_PREFIX =   (MOD_PREFIX, TEX_PREFIX, LGT_PREFIX, ANI_PREFIX)
