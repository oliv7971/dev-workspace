
# A partir du caractere # ( diese ) les donnees sont ignorees par
# les routines d'entree. Utile pour ignorer temporairement certaines
# donnees ...
# Pour avoir diese  sur azerty / compatibles ibm => CTRL ALT 3 ??
# Les caracteres de tabulation dans les donnees sont equivalents a
# un espace.


p64             #parametres generaux par defaut pour p64
M G I, 17 chemin des Sources, 38240 MEYLAN
dossier 	#dossier		ligne 2
titre   	#titre			ligne 3
d64xyz.tmp      #nom du fichier points	ligne 4

# Les 4 1eres lignes doivent etre positionnees  derriere P64
# Les autres parametres sont a MOTCLE, et peuvent etres donnes en
# desordre. Les MOTCLE peuvent etre ecrits en MAJUSCULES/minuscules
# (melange auTOrIse). Apres le motcle remarque ou commentaire, la
# suite de la ligne est ignoree. (idem a partir de #)

XA 999999.999   YA 999999.999   # X Y bas gauche fenˆtre

ECHELLE 1000   GAB 111.11

LFEN 0000   HFEN 000                    #   L et H fenetre

# report numero, endroit, stabiphane, ecritures a 0 grades/ox
NUMERO   ENDROIT   PAPIER STABIPHANE     ANGECRITURE 0.000

MG 005 MD 005 MB 005 MH 005             REMARQUE    marges

CADR1 EP1 0 CADR2 EP2 0 remarque cadres 1 et 2, ep trait type 0

# pas d'ecriture echelle ni fleche nord
XECH 0001 YECH 5000   XNORD 0001 YNORD 5000

# affichage visu,les points ne superposent pas. La plume
# est positionnee en fin de report (pas de superposition)
           AFFICHE   NCHEVAUCHEMENT  NCHEVNUM  NCHEVALTI  NSUPERPOSE

# ecriture de tous les chiffres/nos et z. Si pas = 10, les ecritures
# seront : 1 a 9, 10, 1 a 9, 20 etc.. idel en Z. Allege la densite
# de la minute et permet de ne pas chevaucher...
                PASNUMERO 0001  PASALTITUDE 001

NBDZ 2          # nbre de decimales pour les  Z = 2

#  POINT nsym taille
#   POINT -1  0.6   #pique (baisse de plume)
#   POINT  0    0   #rien
#   POINT  1  2.4   #?
#   POINT  2  0.6   #carre de .6 mm
#   POINT  3  0.6   #cercle
#   POINT  4  0.6   #triangle
#   POINT  5  0.2   #carre de 0.2 mm
    POINT  6  0.6   #+ de .6 mm
#   point  7  1.2   #phi : cercle et / de 1.2 mm
#   point  8  1.2   #- (moins) de 1.2 mm
#   POINT  9  0.6   #x de 0.6 mm
#   POINT 10  3     #fleche nord de 3 mm

        TAILN 1.2  TAILZ 1.5     # taille no , taille z
        penteN 0   penteZ 25     # pente? 25 pour ecriture penchee
        penteM 00       # idem/ecriture des Marqueurs XY

#               NUMERO        ALTITUDE       NUMERO  et  ALTITUDE
 CALECRITURE  1.2   0       1.5    0        0   -1.2    0     0.75
#CALECRITURE  1.2   0       1.5    0      -1.2    0     1.5    0
remarque    calxp calyp   calxz calyz   calxp calyp  calxz calyz

#   CROIX et nord..........tailcroix 0    pas de croix
TAILCROIX 10       CARR   100     SYMBCROIX 6   SYMBNORD 10

PLUMBLEU 2  PLUMNOIR 3  # nø des plumes logiques bleu et noir

cartouche 1 gauche 015 droite 005 bas 000 haut 000 ctouxy 005
MARQNORMALES DESSINFENETRE REPORTFENETRE


#  FACTURATION===========start, si # devant prix : pas d'edition
#    fixe pu no pu z pu n+z pu croix pu format pu traceur coef
 prix  80   0.7  0.8  1.2    0.5      60          2000       0.5
#  FACTURATION===============end
pasbal 10 pasxg 10 pasyg 10 elimcase 0 miso 0 #parmsys, don't change
FIN  PARAMETRES generaux par defaut pourP64>>>>>>>>>>>>>>

#nouveaux parametres : octobre 90 <<<<<<<<<<<<<<<<

# ecritures penchees pour N, Z, marqueurs : si a=0, ecriture droite
# a=25 / penchee . a est la tangente en % par rapport a oy
# PENTEN a
# PENTEZ a
# PENTEM a

# marqueurs
#MARQNORMALES / marques // aux cotes de la feuille
#MARQCADASTRE / marques // aux axes X ou Y
#MARQOFF      / pas de marques

# limitation dessin/report
# DESSINFENETRE le dessin est limite a la fentre
# DESSINPAPIER  le dessin est limite au format papier
# REPORTPAPIER  lE report est limite au format papier
# REPORTFENETRE le report est limite a la fenetre

#marges entre cadre 2 et format papier
#GAUCHE v DROITE v BAS v HAUT v
#CTOUXY v
# v valeur en mm. ctouxy est la marge entre les 2 cadres 1 et 2

#<<<<<<<<<<<<<<<<<<<<<<<<<<<


ca00.p64                #parametres cartouche 0/p64
	#sigle
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
marqoff mg 0 md 0 mb 0 mh 0
cartouche 0 gauche 000 droite 000 bas 000 haut 000 ctouxy 000
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00   tailcroix 00     FIN

ca01.p64                #parametres cartouche 1/p64
M G I
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00  prix #edition prix off
cartouche 1 gauche 015 droite 005 bas 000 haut 000 ctouxy 005
FIN

ca02.p64                #parametres cartouche 2/p64
M G I
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00
cartouche 2 gauche 000 droite 000 bas 000 haut 000 ctouxy 005
fin

ca03.p64                #parametres cartouche 3/p64
M G I
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
cartouche 3 gauche 000 droite 000 bas 000 haut 000 ctouxy 005
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00
marqcadastre dessinpapier FIN

ca04.p64                #parametres cartouche 4/p64
M G I
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
TAILN 1.2  penteN 00 TAILZ 1.5 penteZ 00
cartouche 4 gauche 048 droite 048 bas 048 haut 048 ctouxy 002
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00
marqcadastre dessinpapier FIN

ca0A.p64                #parametres cartouche 0A/p64
M G I
        #dossier                                ligne 2
        #titre                                  ligne 3
        #nom du fichier points                  ligne 4
mg 0 md 0 mb 0 mh 0
cartouche 10 gauche 000 droite 000 bas 000 haut 000 ctouxy 50
supcadr1 ep1 0 supcadr2 ep2 0 penteM 00   tailcroix 20  carr 100
marqcadastre dessinpapier FIN


#LEC 1/binary 0/ad  ECR 1/binary 0/ad 8/9/10=1 1 0/ms  1 0 0/lahey(mem haute)
#enr1 10 l1
#enr2 idoubl(40) l2/l3	! integre
#enr3 modfi(18) blodescart vd 90, blocencart vd 91  ligne4
#enr4 ioper1(40) l5/l6
#enr5 ifcptr(40) l7/l8
#enr6 ilrang(80) l9/l10/l11/l12

P031P065  parametres PYTHA-GRAPH , ne PAs modifier !!!8/9/10/lec/ecr/cmcg
15 51 53 54 100 251 300 1 1 1
3 14 27 28 46 104 147 149 150 156 165 166 177 159 152 193 192 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
10 10 0 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 29 62 107 121 122 81 144 145 146 44 155 168 169 170 125 308 310 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 29 107 62 81 121 122 144 44 155 125 168 169 170 308 300 310 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 46 14 27 3 28 29 62 107 81 121 122 30 104 147 144 149 150 156 155
44 165 166 125 168 169 170 177 159 152 193 192 308 300 310 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
RAPPEL  des fonctions avec return (40 maxi)
1 81 164
FINRAPPEL
masque  # 40 maxi
125 44 #125/hach 44/talus
finmasque
