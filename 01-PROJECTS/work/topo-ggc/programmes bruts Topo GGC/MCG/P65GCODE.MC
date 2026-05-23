##########################################################################

# tables interface geocode --> p65

# table de correspondance symb geocode to p65
# 238 geocode remplace par symbole 78/p65 hx=3 hy=3 ( pour avoir 3 metres si
# pas de dimension fournie)
# symb de p65 dimensionnes a 100 ( = 1m ) rapport hx/hy respecte si une seule
# des 2 dimensions est fournie
fontegcode
pkern
symgcode
   122    74   1.00  1.00 # BORNE INCENDIE   SYMBOLE
   136    73   1.00  1.00 # FEU TRIC.PIETON  SYMBOLE
   155    72   1.00  1.00 # FEU PIETON       SYMBOLE
   156    71   1.20  1.20 # ARMOIRE DIVERSE  SYMBOLE
   160    70   0.20  0.20 # BORNE COCHERE    SYMBOLE
   211    69   0.60  0.60 # DETECTEUR DE FEU SYMBTEX
   214    67   2.00  2.00 # PLAQUE RESEAU    SYMBOLE
   247    66   1.00  1.00 # BOUCHE NON SPECI SYMBOLE
   354    64   0.80  0.80 # COFFRET S300 EDF SYMBOLE
   374    63   1.60  1.60 # ENTREE + PILIERS SYMBOLE
   812    62   1.00  1.00 # SENS INTERDIT    SYMBOLE
   820    61   1.00  1.00 # LIMITATION EN HA SYMBOLE
   847    55   1.00  1.00 # POTEAU DOUBLE DI SYMBOLE
   802    75   1.00  1.00 # FLECHE DROITE    SYMBOLE
    30   128   1.00  1.00 # ARBRE 0< 20 CM   SYMBOLE
    31   127   1.00  1.00 # ARBRE 25<0<60    SYMBOLE
    34   126   1.00  1.00 # ARBRE CONIFERE   SYMBOLE
   116   125   1.00  1.00 # BALISE ROUTIERE  SYMBOLE
   125   124   1.00  1.00 # POTELET(NOM DE R SYMBOLE
   141   123   1.50  1.50 # PANNEAU AFFICHAG SYMBOLE
   162   122   1.00  1.00 # ALTITUDE VOIE    SYMBALT
   163   121   1.00  1.00 # ALTITUDE SEUIL   SYMBALT
   172   120   0.75  0.75 # NUMERO POLICE    SYMBTEX
   180   119   2.25  2.25 # BANC SIMPLE      SYMBOLE
   182   111   1.00  1.00 # BORNE PROPRETE   SYMBOLE
   203   110   1.00  1.00 # GRILLE AVALOIR R SYMBOLE
   206   109   1.00  1.00 # AVALOIR+GRILLE   SYMBOLE
   208   108   0.40  0.40 # PLAQ. EGOUT ROND SYMBOLE
   209   107   1.00  1.00 # PLAQ. EGOUT CARR SYMBOLE
   213   106   1.95  1.95 # PLAQUE RESEAU PT SYMBOLE
   217   105   1.00  1.00 # POTEAU PTT       SYMBOLE
   218   104   1.00  1.00 # POTEAU EDF       SYMBOLE
   219   103   0.50  0.50 # POTEAU EDF RECT. SYMBOLE
   237   102   1.00  1.00 # LAMPADAIRE + EDF SYMBOLE
   245   101   1.00  1.00 # BOUCHE D'EAU     SYMBOLE
   248   100   1.00  1.00 # GAZ COLONNE MONT SYMBOLE
   273    99   1.50  1.50 # PLAQUE PTT 2ELMT SYMBOLE
   319    98   1.20  1.20 # PORTE ACCES PIET SYMBOLE
   320    97   2.00  2.00 # PORTAIL VEHICULE SYMBOLE
   328    96   1.00  1.00 # MITOYEN          SYMBOLE
   373    95   0.65  0.65 # PILIER AVEC INFO SYMBOLE
   675    94   1.00  1.00 # ALT. TEMPON EU   SYMBALT
   676    93   1.00  1.00 # ALT. TAMPON EP   SYMBALT
   695    91   1.00  1.00 # RADIER EU        SYMBALT
   696    88   1.00  1.00 # RADIER EP        SYMBALT
   819    87   1.00  1.00 # VITESSE LIMITEE  SYMBTEX
   831    86   1.00  1.00 # DANGER DIVERS    SYMBOLE
   846    85   1.00  1.00 # POTEAU DIRECTION SYMBOLE
   901    84   1.00  1.00 # POINT I.G.N.     SYMBTEX
   904    76   1.00  1.00 # STATION POLYGO.  SYMBTEX
# + pvc1kt.seq
# + pruqi.seq
# + pkern.seq
238  78 3 3	# lampadaire simple
372  77 4 2	# acces vehicule+pilier !!! leve pas de dim en y !!!
810   1 3 3	# stop
838   3 1 1	# passage pietons
999999
# table types de traits -> traits.mcg
#309 geocode correspond a trait3 : 3000+500+info=3500+epaisseur
# si epaisseur pas trouve, arrondir a 5 (cm) . si pas de trait
# trait 1 (nominal)
traigcode	# en principe ligpara seulement
101	3000  900  5		# trottoir
309	3000  500  5		# mur epais
311     3000  800  5		# mur bahut
315	cloture			# cloture par nom de la macro (cloture(.mac))
615	3000  600  5		# reseau eu
616	3000  700  5		# reseau ep
999999
# tables geocode --> p65	end !!!!!!!!!!!!!!
##########################################################################
