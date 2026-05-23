#p033p034.mcg  config pour P33/P34  !21/04/92 12:38

PARA.P33   parametres passes a P34  ( par P33 ) ............
iter 500
#isole  # plusieurs leves independants dans le meme fichier
#         les canevas doivent etre calculables par p57
tolz 0.20  # 200 mm / Dz
told 0.20  # 200 mm / distances, 400 mm sur geodesie et fermeture polygo
schema 10000 1.8 #ignore par p34, valide pour p44
gauss	   # sortir le classement des ecarts
#ustatmgr	# unite de classement des ecarts angulaires : mgr (standard)
#ustatsec       # unite de classement des ecarts angulaires : sec
qd2 6.57895  # qd utilis‚ = 6.57895e-8
$p57 trilater #passer la main a P57 (passer a 0 sur pts d'appui)
#		  calcul en mode trilateration
#zoff
cgcdon si AV > 200 g (cercle a droite), AH=AH+200
# dans tous les cas si AV > 200, AV=400-AV
verif	# chercher les chemins les + courts entre les pts connus (p44)
### reduction au niveau zero (ellipsoide ou plan de reference)
# calcul des distances reduites au niveau zero (ou autre) a partir des Z de
# chaque point, voir P43 : entrees ex4.d34 et ex4.res par ex
# carnet reduit dans ex4.r43 = nouvelle entree pour p34
# le Zmoyen du 1er calcul doit etre fourni !!!!
#niveauzero 000 metres : plan de reference de la reduction pour p43
rayon 6372000  rayon de courbure en metres
###
#
Zmoyen 0000 metres
projection 000 mm/km # passer par P43 pour avoir les corrections a partir
#	des XY de chaque point des zones Lambert 1,2,3,4 (10=moyenne 1,2,3)
#	la correction moyenne du 1er calcul doit etre fournie !!!!
#	nota : P43 prend en compte les corrections niveau ref et/ou Lambert
# tolpolygo 1 1296 3600 16 16 160
# tolpolygo 1 3600 400 200 2.0 5
tolpolygo 1 1600 400  81 0.5 5
tolangle 0.1000 #fermeture polygo
cordistance 0.000  metres par portee
epspoint 0.0003
epsbloc 0.00000010
colver 0.0000  # collimation verticale
#echelle1      # conserver les distances terrain
#tolerances pour le balancement des stations reprises debut
preprise 10000 0.010# poids=distance, 10000. par defaut, tolrahm 10 mm
# tolrahm : si d*ecartah < tolrahm ou ecartah < tolrah visee ok
# ecartah = ecart angulaire
tolrah 0.0100  # 10 mgr / ang hor
tolrav 0.0200  # 20 mgr / ang vert
tolrdh 0.050   # 50 mm / delta Distance
tolrdz 0.100   # 100 mm / Delta Z
#tolerances pour le balancement des stations reprises fin
tolechel 0.002 #tolerance/echelles locales (0.002 = 20cm a 100m)
parallaxe 0 #excentrement des axes optique et distancemetre en mm
 supiter1 # pas d'edition de la premiere iteration
 supitern # pas d'edition de la derniere iteration
codification  1  # type du fichier N X Y Z code(s) , 1 ou 2 ou 3 ....
# 1 >  N X Y Z cccliiii		(0 a gauche de la zone cccliiii )
# 2 >  N X Y Z ccc l j iii	(code point avec 0 a gauche)
# 3 >  N X Y Z ccc l iiii	(code point avec 0 a gauche)
# 4 >  N X Y Z c1 c2 c3 c4 c5	(c1=code points, autres = infos)
#	pas de zeros a gauche des zones c1 a c5. Le type 4 est active
#	si au moins l'une des zones c2 a c5 est differente de 0 .
#distpente # les distances sont suivant la pente
#pdist57
geodesie
999999
fin       des parametres pour p34

XYZBASE
basegene.xyz  #nom fichier general pour la recherche des points connus
#c:\mcg\basegene.mcg  #nom fichier general pour la recherche des points connus


PARA.P34	  parametres passes a P57 par p34
bloc 10000
trilateration
slan
gauss
annule   #poids 1 pour les visees a partir des points anciens
tolsecondes 10000 decimilligrades / 1 visee
tolcm  5000 cm / 1 visee, distance
epsp 1
epsbloc 0.003	#  p57 seul avec distances, pas de stations : 0.0003 ou moins
#		   et monter les iter : bloc 20000 par ex
fin

PA41.P34	    # parametres passes a P41 par P34
BLOC 1000	    # valeurs utilis‚es par p41 sauf autres valeurs
qd2 6.57895	    # fournies par p34
told 0.20
tol  0.10
gauss
poids			# passer pres des visees courtes
fin

pa40.p33	# parametres passes a p40 par p33 ( fichiers na2000/3000)
bloc 2000
gauss
epsb 0.000000000010
tol 0.01 metre
nedite		# ne pas editer les observations
fin
