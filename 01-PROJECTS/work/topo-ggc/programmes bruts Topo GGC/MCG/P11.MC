0 1 2 3 4 5 6 7 # nom des plumes bgl sur 2 caractere
40 40 1000      # HPGL pas au mm (x/y), diagonale papier mm
20 20 1 256 1   # BGL  40 40 pas au mm (x/y)
#               # tester arrondis (0=non)
#               # 256=tailbuffer
#               # 0/ras 1/pas de dep absolu negatif
bglmsgdebut messages en code bgl debut du trace entre cette ligne et fin
fin
bglmsgfin messages en code bgl fin du trace entre cette ligne et fin
fin

#Formater un fichier NXYZ(C) en colonnes:
#Formats:255 caracteres maxi,   1ere ligne = avec code (si nbv > 4)
#                               2eme ligne = sans code (si nbv = 3 ou 4)
#                               le code est un entier
NXYZC
(I6,1X,F11.4,1X,F11.4,1X,F9.4,1X,i8.8)
(I6,1X,F11.4,1X,F11.4,1X,F9.4)

