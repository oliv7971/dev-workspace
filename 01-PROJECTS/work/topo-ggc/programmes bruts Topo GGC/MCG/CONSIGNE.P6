finlistauto	# sortir de la saisie si la liste est fermee + son 1
noconfirm	# pas de confirmation ok<o>/n apres fin de la saisie
msg667off	# pas de message 667 "nos ou pointes
affinume off	# affichage des numeros off
#affinume on	# affichage des numeros on

#sons : frequence*10 = hertz, temps en centiemes de secondes
# 20Šme = bip
frequences
 1000  100  900  440  200  300  700  800  400  600
  110  120  130  140  150  160  170  180  190 2000

temps
   20   20   20   20   20   20   20   20   20   20
   20   20   20   20   20   20   20   20   20   10

#son   1  2  3  4  5  6
#son 1 sortie liste fermee
#son 2 utilise par getlis (pe/di  )
#son 3 fin saisie parcelle, ok
#son 4 fin parcelles + ilot ok
#son 5 appel a _marqueur
fichcalage
c.app		# si # en col1 query kbd

fils/peres
254 -1
256 276 291 256
257 276 256 291 257
276 254 291
277 276
278 276 256
291 254 276 291
fin

##### consignes pour digit objets fermes/cadastre/ex
startconsignes  avant/apres la commande
calage     0 1 symb 128
calage     0 1 trai 0
ilot       0 1 plu  5
ilot       0 5 sizt 4   4   0.001 0 1
parcelle   0 1 plu  3
parcelle   0 5 sizt 2   2   0.001 0 1
b=parcel   0 1 plu  4
b=parcel   0 5 sizt 2   2   0.001 0 1
batidur    0 1 plu  4
batidur    0 5 sizt 2   2   0.001 0 1
batidur   +2 5 sizt 1.5 1.5 0.001 0 1
batileger  0 1 plu  7
batileger  0 5 sizt 2   2   0.001 0 1
batileger +2 5 sizt 1.5 1.5 0.001 0 1
subdifis   0 1 plu  8
subdifis   0 5 sizt 2   2   0.001 0 1
subdifis  +2 5 sizt 3   3   0.001 0 1
courbati   0 1 plu  6
courbati   0 5 sizt 2   2   0.001 0 1
courbati  +2 5 sizt 3   3   0.001 0 1
numvoiri   0 1 plu  5
numvoiri   0 5 sizt 2   2   0.001 0 1
numvoiri  +2 5 sizt 1.5 1.5 0.001 0 1
tetieres   0 1 plu  9
#tetieres   0 1 bloc 91
fin

pcontour # no change !!!! fonction -n debut +n segment (contour) 0 en vue
253 -5 +10 0 section
254 -5 +10 0 ilot
256 -5 +5  0 batidur
257 -5 +5  0 batileger
258 -5 +5  0 numvoirie
259 -5 +10 0 troncons
261 -5 +10 0 subdifis
262 -5 +10 0 pseuparcelle
263 -5 +10 0 pseutroncon
276 -5 +10 0 parcelle
#277 -5 +5  0 b=parcelle
278 -5 +5  0 courbati
291 -4 +4  0 tetieres
# -5	debut
#  0	nomfonction
# +10	pointeur vers le contour
# zones non utilisees : fonction 310 ( nulloper )
fin
