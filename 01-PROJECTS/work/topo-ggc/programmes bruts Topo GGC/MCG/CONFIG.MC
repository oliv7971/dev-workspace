mescom    # pour p5 menu page 1 y et u
0 1 19 17 500 200
0 58 88 78 13  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0
0 19 19 84 13  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0
0 58 77 84 13  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0 0
# comi, protocole soft 0/non 1/oui, xoff, xon, frequence xoff/xon affichage
#			, wait (10 millisec)
# mess open : ncar  :XN
# mess close        ctrl s
# mes en vue de ...

# donner le nom de votre editeur ( ici me )
editeur
me
extensions fichiers donnees resultats
p002d d02
p007d d07
p008d d08
p012d d12
p016d d16

p011d1 xyz
p011r1 jsi

p011d2 jsi
p011r2 xyz

p011d3 res xyz
p011r3 xym

p011d4 top
p011r4 gdt

p011d5
p011r5

p011d6 cdi
p011r6 d65

p011d7 res
p011r7 rec

p011d8 d57
p011r8 d34

p023d1 dxf fxd # entrees dxf
p023r1 fxd   # elimination des codes 42 (courbes->segments)
p023r2  xyz  # extraction xyz
p023r3 dao   # dxf->pytha
p023r4  rpt  # rapport

p033d1 gdt gre obs d33 ter odb top jsi rec wil
p033r car d34  # can et cpt generes

p034d car can d34 tou
p034r res xyz # cdi genere

p035d1 res xyz	# donnees n x y z
p035d2 car d34  # donnees carnet pour p34
#p035r  cdi # genere par p35 : entree geocode ou ...

p040d d40
p040r r40

p041d d41
p041r r41

p044d d44
p044r r44

p057d d57
p057r r57

p058d d58

p064d mpa d64

fin

FECRG.MCG============
? COMPATIBLES  IBM PC	 2    640*480 VGA COULEUR zenith ftm 1490
240 576 180 480 640   480 30 16 8 0   12 15 0 0 3   5 1 4 320 240
0 2 2 3 4 5 6 7   8 9 10 11 12 13 14 15
0 72 80 75 77	13 45 16  16  5
0  8  8 18 03   3  40  2 000  0   10 0 0 0 0   0 0 0 0 0
0  0  0  0  0   0  00 14  36  0    0 0 0 0 0   0 0 0 0 1

pagesgr2
    9 	12  1  2  2 20   64  4  1 3  0 0 0
  135 	12  1  2  2 20   44  4  1 3  0 0 0
 1700 	12  1  2  2 16   72  4  1 3  0 0 0
 9990   12  1  0  0 00   00 14  1 11  13  0  0
   19  	 8  1  2  2 20   70  4  1 3  0 0 0
   20	 8  1  4  5 20   36  4  1 3  0 0 0
   34 	15  1  5 10 26   40  4  9 3  0 0 0
   41 	10  1 02 02 14   48  4  1 3  0 0 0
#pages 19,20,34,41 inutiles dans v4 : module py
#page 	cb cf L1 C1 ML   MC cl md c2 c3
#cb/couleur cadre, cf/couleur fond, L1,C1/position ligne 1,colonne 1
#cb/couleur cadre, cf/inutilise, L1,C1/position ligne 1,colonne 1          !!
#ML,MC/maxi lignes,colonnes cl/couleur lettres(iso) md/mode fond (set/xor) !!
#ML,MC/maxi lignes,colonnes cl/couleur lettres(iso) md/couleur fond (set/xor)
# 9990 = page 0 (toutvenant)
# c2 couleur lignes 1 et 2 (pyt)
# page 34 utilise par files, calques
# page 9/lc 135/lstxyz 19/type 20/futi 41/mocl

FECR.MCG--------ECRAN ALPHANUMERIQUE
? COMPATIBLES  IBM PC    2
03  0  0  0 0         0 28  0  0000 30    0 0 29 0 0    1 0 2  5  6
0   0  0  0 0         0  0  0    0  0     0 0  0 0 0    0
0   0  0  0 0         0  0  0    0  0
0   0  0  0 0         0  0  2    0  1     0 0  0 0 0    0 0 0  0  0
00 00 00 00 0         0 03 254  31  37    0 0  0 0 0    0 0 0  0  99

#codes fecr.mcg
#	       Version 4 ( 8 mega )
#	       le code couleur pointe vers la table fecr.p65
#
#	       11(77)	code ibm (pytha) blancs aabb	VD=0816  *
#	       12(78)	code bleu clair		 	VD= 4
#	       13(79)	code vert			VD= 3
#	       14(80)	couleurs du menu fond/texte	VD= 4/p11
#	       15(81)	couleur texte ligne 1  		VD= 8/blanc
#	       16(82)	couleur texte ligne 2  		VD= 4/bleu clair
#	       17(83)	couleur du fond lignes 1 et 2	VD= 9/gris
#	       18(84)	code gris			vd= 9
#	       19(85)   code rouge			vd= 5
#
#	       20(86)	99 trace des fichiers ouverts dans PYTHA.DBG
#			   ( PYTHAL.DBG pour v4)
#			   trace sauvegarde des pages graphiques,
#			   etc...misopoint ( VD=0 )
#	* aa=blanc normal, bb=blanc surbrillant
#

FDIG.MCG-------------------
? NUMONICS NS2202 400*300  UNITES 0.1 MM 14 caracteres, 9600,n,7,2  o=0,0
6 4000 3000 0000 0000 4000 3000 1 200 200    85 50 56 1 14 315 0 0 0 0
CNXXXXNNNYYYYNNNNNNNNNNNNNNNNNNNNNNNNNN
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 52 49


FDIG.MCG-------------------
? NUMONICS NS2202 400*300  UNITES 0.1 MM 6 caracteres binaire,9600,n,8,1
60 4000 3000 0000 0000 4000 3000 1 200 200 00 02 08 1 11 315 0 0 0 0
CNXXXXNYYYYNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
22  58 83 84 13  58 77 84 13  58 65 66 13  58 70 49 48 13  58 70 54 48 13 0 0
0 0 0 0 0 0 0 0 0 0          0 0 0 0 0 0 0 0 0 0  0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
#:ST :MT :AB :F10 :F60 stream,metric,absolu,sup derxy, pas de sep

FDIG.MCG-------------------
? NUMONICS NS2202 400*300  UNITES 0.1 MM  11 caracteres, 9600,n,7,2  o=0,0
6 4000 3000 0000 0000 4000 3000 1 200 200    85 50 56 1 11 315 0 0 0 0
CNXXXXNYYYYNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
22  58 83 84 13  58 77 84 13  58 65 66 13  58 70 49 48 13  58 70 54 48 13 0 0
0 0 0 0 0 0 0 0 0 0          0 0 0 0 0 0 0 0 0 0  0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
#:ST :MT :AB :F10 :F60 stream,metric,absolu,sup derxy, pas de sep

$clecpu$12345678   # cle cpu
PRINTERSysteme   nom de l'imprimante
PRN

IMPRIMANTE
0
0
0
0

# exemple de parametrage de l'imprimante : envoi d'un message a
 l'ouverture et a la fermeture
	   d
        IMPRIMANTE
        7
        65 66 67 32 100 32 69
        1
        12


        envoyer 7 caracteres a l'ouverture de l'imprimante :
        ( fichier ou imprimante )
        soit ABC d E

        envoyer 1 caractere a la fermeture
        ici FF ( form feed = saut page ), code decimal 12
        en principe l'imprimante va vider le buffer et sortir la
        derniere page
