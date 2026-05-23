P33        #parametres pour p33.............?/query */noquery/noconfirm
wild P36nul G122 TOPFC2 G120 REC200 MIC1 Wild topojis odb pentax zeiss/m5
`!$')+,abcd*	 CODES FC2
001002003004005006007008009010011012013014015016017018019020 MIC1
 $$ $$ 2= 3= 5= $$ 5= 9= 8= 7= 6= 4= $$ $$ $$ $$ $$ $$ $$ $$ =G122
#codifpoint	# la codif est une codif point (symbolique)
#codprecedent	# le code s'applique au point precedent
#zone44	# zone 44 wild off, laisser # en col 1 !!!!!
#f28azero	# le code chgmt de station/wild peut etre 0
numerowild 9 15
#appareil     1 2 3 4 5 6
tempression   0 0 0 0 0 2 #formules de correction atmospherique des distances
tempmini  -50	# limites mini maxi : temperature
tempmaxi   50   #
prmini    800	# pression
prmaxi   1500	#
humimini    0	# et humidite
humimaxi  100   #
#editatmosphere	# editer les corrections atmospheriques par station
#editcodpytha	# editer le code en clair sur la liste
#dispente	# sortir les distances suivant la pente
#jsinfo		# sortie du carnet au format jsinfo
nocpt		# pas de sortie du fichier *.cpt
#nocan
numorigine 32000# origine numeros si nuls
#pythaoff
fin	#parametres pour p33

UNITES33  #valeur en mm d'une unite de saisie en nombre entier
utourillons	1	# 1.532 ou 1532 =1m532 1=0m001	(f28)
umire		1	# idem / mire (canne)		(f30,f17)
uexcligne	1	# excentricite en ligne	et ...	(f9,f25),(f97,f98)
uexctrans	1	# excentricite transversale	(f10,f26)
uexctz		1	#    ''        en Z		(f11,f27)
ucteappa	1	# constante appareil (sur distances) (f12)
uctearefl	1	#    ''     reflecteur    ''		(f13)
uexcaodi	1	# excentricite axe optique/distancemetre (f18)
f14		1	# distance horizontale chainee (f14)
f15		1	# distance horizontale chainee, pas de Z (f15)
hnul		9999	# voir ci-dessous 1
#
#1/valeur symbolique pour hm signifiant pas de Z pour le(s) point(s)
#ici 9999 mm . La valeur utilisee pour le calcul sera -0.001 metres.
#La lecture mire peut etre 9999 ou 9.999 ou -0.001 ou -1 .
#hnul est un nombre entier en mm .
FIN

fonc33	  #fonctions standard de 1 a 100 (informations generales)
 01 02 03 04 05 06 07 08 09 10    11 12 13 14 15 16 17 18 -1 20
 -1 -1 -1 -1 25 26 27 28 29 30    31 32 33 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 97 98 99 -1

#wild (leica) baillet  08/01/00 19:22
WGRE3  # baillet jacques
 19 00 00 00 00 00 00 00 43 41    42 61 62 00 46 44 49 00 00 00
 00 00 00 00 75 76 77 20 48 50    00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00
#WGRE3IGNORE codes (20 max) du carnet a ignorer
30


GEODAT   		........
 01 02 03 04 05 06 07 08 09 10    11 12 13 14 15 16 17 18 -1 20
 -1 -1 -1 -1 25 26 27 28 29 30    -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1    -1 -1 -1 -1 -1 -1 97 98 99 -1

# fin des parametres p33 ................

# table des fonctions (fonc33)
#wild (leica)  exemple
#WGRE3  # as  : position 25 = fonction 25 code user=42
 10 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00   f1 a f20
 00 00 00 00 42 43 00 20 00 222    00 00 00 00 00 00 00 00 00 00  f21 a 40
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00   f41 a 60
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 00 00   f61 a 80
 00 00 00 00 00 00 00 00 00 00    00 00 00 00 00 00 00 00 13 00   f81 a 100
#WGRE3IGNORE codes (20 max) du carnet a ignorer
30
# code utilisateur en regard dans la table wild par exemple
	     1	  date		! date et dossier peuvent etre fournis
	     2	  dossier	! avec une seule fonction ( ex / Wild )
	T    3	  temp‚rature	! correction atmospherique
	T    4	  pression      ! correction atmospherique
	T    5	  collimation horizontale
	T    6	  collimation verticale
	T    7	  humidit‚      ! correction atmospherique
	     8	  r‚serv‚
	P    9	  excentricit‚ en ligne
	P   10	  excentricit‚ transversale (+ a droite, - a gauche)
	P   11	  excentricit‚ en z 	    (+/monter,-/descendre)
	T   12	  constante appareil
	T   13	  constante r‚flecteur
	P   14	  distance horizontale chain‚e
	P   15	  distance horiz.chain‚e, pas de Z
	P   16	  pas de Z
	P   17	  changement provisoire de hmire
	T   18	  excentricit‚ axe optique/axe distancemetre
	    19	  r‚serv‚
	    20	  r‚p‚ter l'enregistrement pr‚c‚dent, sauf
	      	  valeurs fournies ,ex code du point et nø point
	    21    r‚serv‚
	    22    r‚serv‚
	    23    r‚serv‚
	    24    r‚serv‚
	S   25	  excentricit‚ en ligne
	S   26	       	"      transversale (+ a droite, - a gauche)
	S   27	       	"      en Z         (+/monter,-/descendre)
	T   28	  r‚serv‚/changement de station/wild (ns et hi)
     *  TS  29	  r‚serv‚/codif du point ( voir A7 )/wild
	T   30	  r‚serv‚/changement de hmire/wild
	ts  31    reserve/changement de classe objet/wild/geocode
	s   32	  reserve/information/wild/geocode
	ts  33	  reserve/raz code liaison info/wild/geocode
	     a    .......
	    96    reserve
	    97    point perpendiculaire aux 2 precedents a +ou- distance
	    98    prolonger les 2 points precedents de +ou- distance
	    99	  fin des donn‚es
	   100	  origine de la codification en zones 41 … 45 (wild),
	   	  sinon 0 ( code = donnee du bloc 41 - f100 )

	* si GEOCODE, recengre ( conversion rec en gre ) utilise la
	  fonction 29 : la zone 71 attachee  au point n'est plus servie
