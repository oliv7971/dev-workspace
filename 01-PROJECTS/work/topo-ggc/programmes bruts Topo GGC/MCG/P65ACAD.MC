# tables interface p65 --> AutoCAD

COULEURS        # ligne 1 acad , 2 pytha , valides 2 a 16
16 13 11 12 9 14 10 15 8  5  3  4  1  6  2  7
1  2  3  4  5 6  7  8  9  10 11 12 13 14 15 16
# pytha
# noir bleu vert bleuclair rouge violet jaune blanc
#    1    2    3         4     5      6     7     8
# gris les memes plus brillantes
#    9   10   11        12    13     14    15    16

#DXFSEMIS  # couleurs pytha des layers predefinis
# pique numero     altitudes hach talus cartouche
#  15    4          3         9    8     4
# jaune bleu clair vert      gris blanc bleu clair
3                       #unit‚ rotation ‚critures semis 1=rd 2=deg 3=grad
cart  3                 #r‚serv‚
2                       #position ecritures  1 ou 2
#code_pt   plan    trait  couleur       99 lignes maxi
02       Z-ASSAIN    1       1

DXFPLANS
#PLANBLOC_PYTHA NOM_PLAN_ACAD TRAI COULEUR_acad  (999 maxi)
# predifinis toujours dans cet ordre
10001 piques   	1	-2	#      FG3-2 ( nom dde )
10002 numeros  	1	-12	#      FF2-2
10003 altitudes	1	-11	#      FGT-2
10004 hachures	1	-8	#hachures
10005 barbtalus	1	-15	#talus
10006 cartouche	1	-12	#cartouche
10007 pointacad	1	7	#point/acad
10008 poubelle	1       -6	#poubelle toujours le dernier
# predifinis end toujours dans cet ordre
0101 FA1   1 -1
0201 FAS   1 -1
0102 FAS   1 -1
0301 FAT   1 -1
0103 FAT   1 -1
0402 FB1   1 -14
0502 FB2   1 -14
0602 FB3   1 -14
0702 FB4   1 -14
0802 FB5   1 -14
0902 FBS   1 -14
1002 FBT   1 -14
1103 FC1   1 -7
1204 FD1   1 -7
1304 FDS   1 -7
1404 FDT   1 -7
1505 FE1   1 -5
1605 FES   1 -5
1705 FET   1 -5
1806 FF1   1 -7
1906 FF2   1 -7
2006 FFS   1 -7
2106 FFT   1 -7
2207 FG1   1 -10
2307 FG2   1 -10
2407 FG3   1 -10
2507 FG4   1 -10
2607 FGS   1 -10
2707 FGT   1 -10
2808 FH1   1 -7
2908 FHS   1 -7
3008 FHT   1 -7
3109 FI1   1 -3
3209 FIS   1 -3
3309 FIT   1 -3
3410 FJ1   1 -14
3510 FJS   1 -14
3610 FJT   1 -14
3711 FK1   1 -7
3811 FKS   1 -7
3911 FKT   1 -7
4012 FL1   1 -7
4112 FLS   1 -7
4212 FLT   1 -7
4313 FM1   1 -7
4413 FMS   1 -7
4513 FMT   1 -7
4614 FN1   1 -7
4714 FNS   1 -7
4814 FNT   1 -7
4915 FO1   1 -7
5015 FOS   1 -7
5115 FOT   1 -7
5216 FP1   1 -7
5316 FPS   1 -7
5416 FPT   1 -7
5501 FA3   1 -7
5602 FB2V  1 -14
5702 FB2H  1 -14
5802 FB2R  1 -14
5902 FBTV  1 -14
6002 FBTH  1 -14
6102 FBTR  1 -14
6204 FD1D  1 -7
6304 FD1P  1 -7
6404 FD1C  1 -7
6504 FDTD  1 -7
6604 FDTP  1 -7
6704 FDTC  1 -7
6806 FF1P  1 -7
6906 FF1N  1 -7
7006 FFTP  1 -7
7107 FG4H  1 -10
7207 FG4B  1 -10
7311 FK1A  1 -7
7411 FK1E  1 -7
7511 FKTA  1 -7
7611 FKTE  1 -7
7712 FL1A  1 -7
7812 FL1E  1 -7
7912 FLTA  1 -7
8012 FLTE  1 -7
8114 FN1A  1 -7
8214 FN1E  1 -7
8314 FNTA  1 -7
8414 FNTE  1 -7
8515 FO1A  1 -7
8615 FO1E  1 -7
8715 FOTA  1 -7
8815 FOTE  1 -7
8917 FQ1   1 -7
9017 FQS   1 -7
9117 FQT   1 -7
9218 FR1   1 -7
9318 FRT1  1 -7
9418 FRT2  1 -7
9519 FS1   1 -7
9619 FS2   1 -7
0189 CART 1 -7
#PLANS des codes du semis … definir obligatoirement dans le dessin.
0190 CARTOUCHE 1 -1
9898 Z-ASSAIN    1      -1


headerdxf
/!
0/SECTION/2/HEADER
9/$ACADVER/1/AC1009
9/$LUPREC/70/2
9/$LTSCALE/40/1
9/$AUNITS/70/2
9/$AUPREC/70/1
9/$ANGBASE/50/90
9/$ANGDIR/70/1
9/$COORDS/70/2/9/$limmin/10/!/20/!/9/$limmax/10/!/20/!/0/ENDSEC/0
SECTION/2/TABLES/0/TABLE/2/VPORT/70/2/0
VPORT/2/*ACTIVE/70/0/10/0/20/0/11/1/21/1/12/0/22/0
13/0/23/0/14/1/24/1/15/0/25/0/16/0/26/0
36/1/17/!/27/!/37/0/40/1/41/1/42/50/43/0/44/0/50/0/51/!/71
0/72/100/73/1/74/1/75/0/76/0/77/0/78/0/0/ENDTAB
fin

styledxf        # polices de caracteres nouvelles a ajouter si necessaire
/!romans  col 3 a 10 police par defaut (romans si blanc)
0/table/2/STYLE/70/1
0/STYLE/2/STANDARD/70/64/40/0/41/1/50/0/71/0/42/0.2/3/txt/4/
0/STYLE/2/fonte/70/64/40/0/41/1/50/0/71/0/42/10/3/romans/4/
0/STYLE/2/pol1/70/64/40/0/41/1/50/0/71/0/42/10/3/romans/4/
0/STYLE/2/pol2/70/64/40/0/41/1/50/0/71/0/42/10/3/italict/4/
0/STYLE/2/pol3/70/64/40/0/41/1/50/0/71/0/42/10/3/romanc/4/
0/STYLE/2/pol4/70/64/40/0/41/1/50/0/71/0/42/10/3/romand/4/
0/STYLE/2/pol5/70/64/40/0/41/1/50/0/71/0/42/10/3/romant/4/
0/STYLE/2/pol6/70/64/40/0/41/1/50/0/71/0/42/10/3/scriptc/4/
0/STYLE/2/txt/70/64/40/0/41/1/50/0/71/0/42/10/3/txt/4/
0/STYLE/2/romans/70/64/40/0/41/1/50/0/71/0/42/10/3/romans/4/
0/STYLE/2/italict/70/64/40/0/41/1/50/0/71/0/42/10/3/italict/4/
0/STYLE/2/romanc/70/64/40/0/41/1/50/0/71/0/42/10/3/romanc/4/
0/STYLE/2/romand/70/64/40/0/41/1/50/0/71/0/42/10/3/romand/4/
0/STYLE/2/romant/70/64/40/0/41/1/50/0/71/0/42/10/3/romant/4/
0/STYLE/2/scriptc/70/64/40/0/41/1/50/0/71/0/42/10/3/scriptc/4/
0/STYLE/2/pkern/70/64/40/0/41/1/50/0/71/0/42/10/3/romans/4/
0
endtab
FIN
