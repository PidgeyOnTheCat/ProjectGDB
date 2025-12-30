threats = [
    ", I think you should kill yourself. Honestly think about it.",
    ", In dieser sehr verstrickten Situation solltest du dir den Strick geben",
    ", Young man kill yourself.",
    ", Your life is worth nothing. You serve zero purpose. You should kill yourself now. ",
    ", Bro just jump off a cliff nobody would give a fuck anyway.",
    ", Today is the perfect day to kill yourself. "
]

roasts = [
    ", You're ugly as fuck."
]

nword_list = [
    # Core and direct variations
    'nigger', 'nigga', 'niger', 'nigar', 'niggr', 'niggar', 'niggah', 'niggur', 'niggor',
    'neger', 'negar', 'negro', 'negur', 'neeger', 'neegar', 'neegro', 'neegur', 'necher',
    
    # Leetspeak and character substitution (i -> 1, e -> 3, g -> 9/6, o -> 0, s -> 5, a -> 4/@)
    'n1gger', 'n1gg3r', 'n1gg4', 'n1gga', 'n1gah', 'n1gger', 'n1ggar', 'n1ggur', 'n1gg0r',
    'nigg3r', 'nigg4', 'nigga', 'nigga', 'nigga', 'nigga', 'nigga', 'nigga', 'nigga',
    'n9gger', 'n9gg3r', 'n9gg4', 'n9gga', 'n9gah', 'n9gger', 'n9ggar', 'n9ggur', 'n9gg0r',
    'n6gger', 'n6gg3r', 'n6gg4', 'n6gga', 'n6gah', 'n6gger', 'n6ggar', 'n6ggur', 'n6gg0r',
    'n3gger', 'n3gg3r', 'n3gg4', 'n3gga', 'n3gah', 'n3gger', 'n3ggar', 'n3ggur', 'n3gg0r',
    'n0gger', 'n0gg3r', 'n0gg4', 'n0gga', 'n0gah', 'n0gger', 'n0ggar', 'n0ggur', 'n0gg0r',
    'negg3r', 'negg4', 'negg@', 'neggah', 'n3gg3r', 'n3gg4', 'n3gg@', 'n3ggah',
    'n3g3r', 'n3g4r', 'n3g@r', 'n3g@h', 'n3gur', 'n3g0r',
    'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0', 'n1gr0',
    
    # Separated characters and spaces
    'n i g g e r', 'n i g g a', 'n i g g a h', 'n i g g u r', 'n i g g o r',
    'n-i-g-g-e-r', 'n-i-g-g-a', 'n-i-g-g-a-h', 'n-i-g-g-u-r', 'n-i-g-g-o-r',
    'n.i.g.g.e.r', 'n.i.g.g.a', 'n.i.g.g.a.h', 'n.i.g.g.u.r', 'n.i.g.g.o.r',
    'n_i_g_g_e_r', 'n_i_g_g_a', 'n_i_g_g_a_h', 'n_i_g_g_u_r', 'n_i_g_g_o_r',
    'n!g!ger', 'n!g!ga', 'n!g!gah', 'n!g!gur', 'n!g!gor',
    'n@gger', 'n@gga', 'n@ggah', 'n@ggur', 'n@ggor',
    
    # Appended/Prepended characters and common suffixes/prefixes
    'niggerz', 'niggaz', 'niggerz', 'niggaz', 'niggers', 'niggas', 'niggerz', 'niggaz',
    'niggerboy', 'niggaboy', 'niggerman', 'niggaman',
    'mynigger', 'mynigga', 'thenigger', 'thenigga', 'anigger', 'anigga',
    'niggerish', 'niggarish', 'niggish', 'niggazish',
    
    # Phonetic and visual approximations
    'niglet', 'niglet', 'niglett', 'niglette', 'niglet', 'niglet', 'niglet',
    'nig nog', 'nignog', 'nig-nog', 'nig nog', 'nignog', 'nig-nog',
    'darkie', 'darky', 'darkie', 'darky', 'darkie', 'darky',
    'coon', 'coons', 'coonn', 'coonz',
    'jigaboo', 'jigaboo', 'jigaboo', 'jigaboo', 'jigaboo', 'jigaboo',
    'sambo', 'sambo', 'sambo', 'sambo', 'sambo', 'sambo',
    
    # Reverse and mixed spellings
    'reggin', 'reggin', 'reggin', 'reggin', 'reggin', 'reggin',
    'ggin', 'ggin', 'ggin', 'ggin', 'ggin', 'ggin',
    
    # Cyrillic, Greek, and other script homoglyphs
    'піgger', 'піggа', 'піggаh', 'піggur', 'піgg0r',  # Cyrillic 'i'
    'піggeя', 'піggа', 'піggаh', 'піggur', 'піgg0я',  # Cyrillic 'i' and 'ya'
    'nіgger', 'nіgga', 'nіggah', 'nіggur', 'nіgg0r',  # Cyrillic 'i'
    'nіggeя', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0я',  # Cyrillic 'i' and 'ya'
    'nіggеr', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіgger', 'nіgga', 'nіggah', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggeя', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0я',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіgger', 'nіgga', 'nіggah', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggeя', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0я',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіgger', 'nіgga', 'nіggah', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіggeя', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0я',  # Mix of Cyrillic and Latin
    'nіggег', 'nіggа', 'nіggаh', 'nіggur', 'nіgg0r',  # Mix of Cyrillic and Latin
    'nіgger', 'nіgga', 'nіggah',

    # My additions
    'neg3r', 'nickur', 'niker', 'nicker'


]

cog_list = [
    'console',
    'economy',
    'moderation',
    'test',
    'uncathegorized',
    'voice'
]

rank_roles = {
    5: 1065622522390908948, # Good Pigeon
    10: 1065623070271864863, # Pro Pigeon
    15: 1065624978323681341, # Insane Pigeon
    20: 1065625410559295518, # Ultra Pigeon
    30: 1072936830745448498, # Veteran Pigeon
    40: 1072938262861201409, # Distinguished Pigeon
    50: 1065625836948037692, # God Pigeon
    69: 1065625980586164224, # MLG Pigeon
    100: 1065627903292887080 # Religion SEED
}