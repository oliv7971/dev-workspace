Calcul topo sur excel avec fonction vba---------------------------------------
Url     : http://codes-sources.commentcamarche.net/source/54734-calcul-topo-sur-excel-avec-fonction-vbaAuteur  : cs_richardtDate    : 07/08/2013
Licence :
=========

Ce document intitulé « Calcul topo sur excel avec fonction vba » issu de CommentCaMarche
(codes-sources.commentcamarche.net) est mis à disposition sous les termes de
la licence Creative Commons. Vous pouvez copier, modifier des copies de cette
source, dans les conditions fixées par la licence, tant que cette note
apparaît clairement.

Description :
=============

Le but de TOPOVB est de faire une grande quantit&eacute; de calcul topo sur EXCE
L.
<br />Calculer des points tous les 10 cm sur un axe routier, axe d&eacute;ca
l&eacute;, ...
<br />Il est donc tr&egrave;s pratique en projet routier si l'on
 dispose de la tabulation de l'axe.
<br />Par simple recopier les cellules vers
 le bas.
<br />Exemple :       =XYG(XS;YS;LC(-2);LC(-1)) ici les cellules XStat
ion et YStation sont nom&eacute;es.
<br />		=XYGDX(L24C2;L24C3;LC(-2);LC(-1)) i
ci les cellules XStation et YStation sont fig&eacute;es.
<br />		=RCX($B$102;$C
$102;$D$102;$E$102;$F$102;$G$102;B117) ici les cellules XStation et YStation son
t fig&eacute;es.
<br />		=XYG(100;500;110;510) ici tout est rempli( r&eacute;su
ltat = 50 grades).
<br />
<br />Liste des fonctions disponibles dans TOPOVB:

<br />
<br />= XYG(Xstation, Ystation, Xpoint, Ypoint) Converti des coordonn&ea
cute;es rectangulaires en gisement exprim&eacute;s en Grades.
<br />= XYD(Xstat
ion, Ystation, Xpoint, Ypoint) Converti des coordonn&eacute;es rectangulaires en
 distances.
<br />= XYGDX(Xstation, Ystation, GISEMENT, DISTANCE) Converti des 
coordonn&eacute;es POLAIRES exprim&eacute;s en grades en coordonn&eacute;es X.

<br />= XYGDY(Xstation, Ystation, GISEMENT, DISTANCE) Converti des coordonn&eacu
te;es POLAIRES exprim&eacute;s en grades en coordonn&eacute;es Y.
<br />= DROIT
EABSX(AbsDep, Xdep, Ydep, Xfin, Yfin, AbsPoint) Calcul des points interm&eacute;
diaires sur une droite, donne X.
<br />= DROITEABSY(AbsDep, Xdep, Ydep, Xfin, Y
fin, AbsPoint) Calcul des points interm&eacute;diaires sur une droite, donne Y.

<br />= IDGX(X_Doite_1, Y_Doite_1, Gisement_Doite_1_Grades, X_Doite_2, Y_Doite_
2, Gisement_Doite_2_Grades)
<br />	Calcul l'intersection de 2 droites en X en d
onnant les origines des droites en X/Y et leurs gisements.
<br />= IDGY(X_Doite
_1, Y_Doite_1, Gisement_Doite_1_Grades, X_Doite_2, Y_Doite_2, Gisement_Doite_2_G
rades)
<br />	Calcul l'intersection de 2 droites en Y en donnant les origines d
es droites en X/Y et leurs gisements.
<br />= ICX(X_Centre_1, Y_Centre_1, R1, X
_Centre_2, Y_Centre_2, R2, Solution_D_G)
<br />	Calcul l'intersection de 2 CERC
LES en X en donnant les CENTRES des CERCLES en X/Y et leurs RAYONS.
<br />= ICY
(X_Centre_1, Y_Centre_1, R1, X_Centre_2, Y_Centre_2, R2, Solution_D_G)
<br />	C
alcul l'intersection de 2 CERCLES en Y en donnant les CENTRES des CERCLES en X/Y
 et leurs RAYONS.
<br />= RCX(X_Centre, Y_Centre, R_n&eacute;gatif_&agrave;_dro
ite, X_Tg_D&eacute;part, Y_Tg_D&eacute;part, Absisse_Tg_D&eacute;part, Absisse_P
oint)
<br />	Calcul un raccordement circulaire en X en donnant le centre,la tan
gente et sont absisse et l'absisse du point a calculer.
<br />= RCY(X_Centre, Y
_Centre, R_n&eacute;gatif_&agrave;_droite, X_Tg_D&eacute;part, Y_Tg_D&eacute;par
t, Absisse_Tg_D&eacute;part, Absisse_Point)
<br />	Calcul un raccordement circu
laire en Y en donnant le centre,la tangente et sont absisse et l'absisse du poin
t a calculer.
<br />= PIP(Absisse_Tg_A, Z_Tg_A, Pente_en_Tg_A, Absisse_Tg_B, Z_
Tg_B, Pente_en_Tg_B, Rayon_n&eacute;gatif_bosse, Absisse_Point)
<br />	Calcul l
e Z d'un point sur une parabole.
<br />= PIPHBX(Absisse_Tg_A, Z_Tg_A, Pente_en_
Tg_A, Absisse_Tg_B, Z_Tg_B, Pente_en_Tg_B, Rayon_n&eacute;gatif_bosse)
<br />	C
alcul l'absisse du point Haut ou point Bas sur une parabole.
<br />= PICX(X_Tg_
Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_D&eacute;but_DROITE, Y_D&eacute;but_DROITE
, Rayon_n&eacute;gatif_DROITE, Longueur_L, Absisse)
<br />	Calcul des points in
term&eacute;diaires sur une CLOTHOIDE et renvoi l'X.
<br />= PICY(X_Tg_Droite, 
Y_Tg_Droite, Abs_Tg_DROITE, X_D&eacute;but_DROITE, Y_D&eacute;but_DROITE, Rayon_
n&eacute;gatif_DROITE, Longueur_L, Absisse)
<br />	Calcul des points interm&eac
ute;diaires sur une CLOTHOIDE et renvoi l'Y.
<br />= PIC2X(X_Tg_Droite, Y_Tg_Dr
oite, Abs_Tg_DROITE, X_Tg_Cercle, Y_Tg_Cercle, Rayon_n&eacute;gatif_DROITE, Long
ueur_L, Absisse)
<br />	Calcul des points interm&eacute;diaires sur une CLOTHOI
DE et renvoi l'X.
<br />= PIC2Y(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_Tg_C
ercle, Y_Tg_Cercle, Rayon_n&eacute;gatif_DROITE, Longueur_L, Absisse)
<br />	Ca
lcul des points interm&eacute;diaires sur une CLOTHOIDE et renvoi l'Y.
<br />= 
GISAXECLOTH(Gis_droite_Grades, Abs_Tg_DROITE, Abs_Tg_CERCLE, Rayon_n&eacute;gati
f_DROITE, Absisse)
<br />	Calcul le gisement de l'axe sur une clothoide dos &ag
rave; la droite.
<br />= GISAXECLOTH2(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, 
X_Tg_Cercle, Y_Tg_Cercle, Abs_Tg_CERCLE, Ray_n&eacute;g_Droite_D&agrave;Dr, Absi
sse)
<br />	Calcul le gisement de l'axe sur une clothoide dos &agrave; la droit
e.
<br />
<br />Mode op&eacute;ratoire sur EXCEL:
<br />Formules / Ins&eacute
;rer une fonction / Cat&eacute;giries -&gt; Personalis&eacute;es / Choisir une f
onction TOPOVB7 ... / Utiliser la boite de dialogue.
<br /><a name='source-exem
ple'></a><h2> Source / Exemple : </h2>
<br /><pre class='code' data-mode='basi
c'>
'Tous droits réservés    Copyright 1997   TOUBIN RICHARD
'L 'utilisateur p
rend ses responsabilités quant à l'utilisation de ce Programme, à la vérificatio
n des résultats.
'L'AUTEUR N'ASSUME AUCUNE GARANTIE DE QUELQUE NATURE ET A QUEL
QUE TITRE
'QUE CE SOIT EXPLICITE OU IMPLICITE, DE CONFORMITE OU D'ADEQUATION A 
UN USAGE SPECIFIQUE DU LOGICIEL.
'EN TOUT ETAT DE CAUSE LA RESPONSABILITE DE L'
AUTEUR NE POURRA EN AUCUN CAS EXCEDER LE MONTANT EFFECTIVEMENT PAYE POUR L'ACQUI
SITION DU LOGICIEL.
'Ce logiciel est GRATUIT et peut être redistribué dans sont
 intégralité et gratuitement
'
'
'
'Remarques / Remercïments / Dons ...     
  Auteur : richardtoubin@live.fr
'
'
'
'Pour utiliser ce fichier vous pouvez
 :
'       *Ouvrir ce fichier XLS et utiliser les feuilles tells qu'elles. Dans
 ce cas si vous distribuez
'ce fichier les fonctions personalisée fonctionneron
t car elles font parti du fichier.
'       *Séparer le fichier XLA et le charge
r automatiquement à l'ouverture d'EXCEL.
'Dans ce cas vous pourez utiliser les 
fonctions personalisées dans n'importe que fichier et feuille EXCEL.
'Par contr
e si vous enregistrez un fichier qui utilise une de ces fonctions et que vous do
nnez ce fichier,
'n'oubliez pas de lui fournir aussi le fichier XLA, sans quoi 
l'appel d'une fonction se soldera par un
'   #NOM? car Excel ne trouvera pas la
 fonction sur le PC de votre ami.
'Vous pouvez aussi ne fournir que des données
 avec un copier/colage spécial/coller des valeurs.
'Ou encore enregistrer votre
 fichier au format CSV.
'
'
'
'
'------------------------------------------
---------------------------------------------------
'Début des fonctions person
alisées :
'--------------------------------------------------------------------
-------------------------
' XYG Macro VB
' Macro enregistrée le 16/09/1997 par
 TOUBIN RICHARD
' Converti des coordonnées rectangulaires en gisement exprimés 
en Grades.
'

Function XYG(Xstation, Ystation, Xpoint, Ypoint)
Pi = 4 * Atn(
1)
    If Ypoint - Ystation = 0 Then
        If Xpoint - Xstation &gt; 0 Then

        XYG = 100
        End If
    End If
    If Xpoint - Xstation = 0 The
n
        If Ypoint - Ystation &lt; 0 Then
        XYG = 200
        End If

    End If
    If Ypoint - Ystation = 0 Then
        If Xpoint - Xstation &lt;
 0 Then
        XYG = 300
        End If
    End If
    If Ypoint - Ystation
 &gt; 0 Then
        If Xpoint - Xstation &gt; 0 Then
        XYG = (Atn((Xpoi
nt - Xstation) / (Ypoint - Ystation))) / Pi * 200
        ElseIf Xpoint - Xstat
ion &lt; 0 Then
        'XYG = 300 - (Arctan((Xpoint - Xstation) / (Ypoint - Ys
tation)) / Pi * 200)
        XYG = 400 + ((Atn((Xpoint - Xstation) / (Ypoint - 
Ystation)) / Pi * 200))
        ElseIf Xpoint - Xstation = 0 Then
        XYG 
= 0
        End If
    End If
    If Ypoint - Ystation &lt; 0 Then
        I
f Xpoint - Xstation &gt; 0 Then
        XYG = 200 + (Atn((Xpoint - Xstation) / 
(Ypoint - Ystation)) / Pi * 200)
        ElseIf Xpoint - Xstation &lt; 0 Then

        XYG = 200 + (Atn((Xpoint - Xstation) / (Ypoint - Ystation)) / Pi * 200)

        End If
    End If
End Function

'----------------------------------
-----------------------------------------------------------
' XYD Macro VB
' M
acro enregistrée le 16/09/1997 par TOUBIN RICHARD
' Converti des coordonnées re
ctangulaires en distances.
'

Function XYD(Xstation, Ystation, Xpoint, Ypoint
)
XYD = Sqr((Xpoint - Xstation) ^ 2 + (Ypoint - Ystation) ^ 2)
End Function


'------------------------------------------------------------------------------
---------------
' XYGDX Macro VB
' Macro enregistrée le 16/09/1997 par TOUBIN 
RICHARD
' Converti des coordonnées POLAIRES exprimés en grades en coordonnées X
.
'
Function XYGDX(Xstation, Ystation, GISEMENT, DISTANCE)
Pi = 4 * Atn(1)
X
YGDX = Xstation + (DISTANCE * Sin(GISEMENT / 200 * Pi))
End Function

'------
--------------------------------------------------------------------------------
-------
' XYGDY Macro VB
' Macro enregistrée le 16/09/1997 par TOUBIN RICHARD

' Converti des coordonnées POLAIRES exprimés en grades en coordonnées Y.
'
Fu
nction XYGDY(Xstation, Ystation, GISEMENT, DISTANCE)
Pi = 4 * Atn(1)
XYGDY = Y
station + (DISTANCE * Cos(GISEMENT / 200 * Pi))
End Function

'--------------
-------------------------------------------------------------------------------

' DROITEABSX Macro VB
' Macro enregistrée le 16/09/1997 par TOUBIN RICHARD
' 
Calcul des points intermédiaires sur une droite.
' Les absisse sont considérés 
croissants du départ vers la fin.

Function DROITEABSX(AbsDep, Xdep, Ydep, Xfi
n, Yfin, AbsPoint)
Pi = 4 * Atn(1)
If XYD(Xdep, Ydep, Xfin, Yfin) = 0 Then
  
 DROITEABSX = 0
Else: DROITEABSX = XYGDX(Xdep, Ydep, XYG(Xdep, Ydep, Xfin, Yfin
), AbsPoint - AbsDep)
End If
End Function

'--------------------------------
-------------------------------------------------------------
' DROITEABSY Macr
o VB
' Macro enregistrée le 16/09/1997 par TOUBIN RICHARD
' Calcul des points 
intermédiaires sur une droite.
' Les absisses sont considérés croissants du dép
art vers la fin.

Function DROITEABSY(AbsDep, Xdep, Ydep, Xfin, Yfin, AbsPoint
)
Pi = 4 * Atn(1)
If XYD(Xdep, Ydep, Xfin, Yfin) = 0 Then
   DROITEABSY = 0

Else: DROITEABSY = XYGDY(Xdep, Ydep, XYG(Xdep, Ydep, Xfin, Yfin), AbsPoint - Abs
Dep)
End If
End Function

'-------------------------------------------------
--------------------------------------------
' IDGX Macro VB
' Macro enregistr
ée le 19/09/1997 par TOUBIN RICHARD
' Calcul l'intersection de 2 droites en X e
n donnant les origines des droites en X/Y
' et leurs gisements.
Function IDGX(
X_Doite_1, Y_Doite_1, Gisement_Doite_1_Grades, X_Doite_2, Y_Doite_2, Gisement_Do
ite_2_Grades)
Pi = 4 * Atn(1)
G1 = Gisement_Doite_1_Grades / 200 * Pi
G2 = Gi
sement_Doite_2_Grades / 200 * Pi
G3 = XYG(X_Doite_2, Y_Doite_2, X_Doite_1, Y_Do
ite_1) / 200 * Pi
DAB = XYD(X_Doite_1, Y_Doite_1, X_Doite_2, Y_Doite_2)
LM = (
Sin(G2 - G3) * DAB) / Cos(G1 - (G2 + (Pi / 2)))
IDGX = XYGDX(X_Doite_1, Y_Doite
_1, G1 / Pi * 200, LM)
End Function

'---------------------------------------
------------------------------------------------------
' IDGY Macro VB
' Macro
 enregistrée le 19/09/1997 par TOUBIN RICHARD
' Calcul l'intersection de 2 droi
tes en Y en donnant les origines des droites en X/Y
' et leurs gisements.
Func
tion IDGY(X_Doite_1, Y_Doite_1, Gisement_Doite_1_Grades, X_Doite_2, Y_Doite_2, G
isement_Doite_2_Grades)
Pi = 4 * Atn(1)
G1 = Gisement_Doite_1_Grades / 200 * P
i
G2 = Gisement_Doite_2_Grades / 200 * Pi
G3 = XYG(X_Doite_2, Y_Doite_2, X_Doi
te_1, Y_Doite_1) / 200 * Pi
DAB = XYD(X_Doite_1, Y_Doite_1, X_Doite_2, Y_Doite_
2)
LM = (Sin(G2 - G3) * DAB) / Cos(G1 - (G2 + (Pi / 2)))
IDGY = XYGDY(X_Doite_
1, Y_Doite_1, G1 / Pi * 200, LM)
End Function

'-----------------------------
----------------------------------------------------------------
' ICX Macro VB

' Macro enregistrée le 22/09/1997 par TOUBIN RICHARD
' Calcul l'intersection 
de 2 CERCLES en X en donnant les CENTRES des CERCLES en X/Y
' et leurs RAYONS.


Function ICX(X_Centre_1, Y_Centre_1, R1, X_Centre_2, Y_Centre_2, R2, Solution
_D_G)
Pi = 4 * Atn(1)
DCC = XYD(X_Centre_1, Y_Centre_1, X_Centre_2, Y_Centre_2
)
C1H = ((DCC * DCC) + (R1 * R1) - (R2 * R2)) / (2 * DCC)
HI = Sqr((R1 * R1) -
 (C1H * C1H))
Alpha = Atn(HI / C1H) / Pi * 200
GCC = XYG(X_Centre_1, Y_Centre_
1, X_Centre_2, Y_Centre_2)
    If Solution_D_G = &quot;D&quot; Then
        IC
X = XYGDX(X_Centre_1, Y_Centre_1, GCC + Alpha, R1)
        ElseIf Solution_D_G 
= &quot;G&quot; Then
        ICX = XYGDX(X_Centre_1, Y_Centre_1, GCC - Alpha, R
1)
    End If
End Function

'-----------------------------------------------
----------------------------------------------
' ICY Macro VB
' Macro enregist
rée le 22/09/1997 par TOUBIN RICHARD
' Calcul l'intersection de 2 CERCLES en Y 
en donnant les CENTRES des CERCLES en X/Y
' et leurs RAYONS.

Function ICY(X_
Centre_1, Y_Centre_1, R1, X_Centre_2, Y_Centre_2, R2, Solution_D_G)
Pi = 4 * At
n(1)
DCC = XYD(X_Centre_1, Y_Centre_1, X_Centre_2, Y_Centre_2)
C1H = ((DCC * D
CC) + (R1 * R1) - (R2 * R2)) / (2 * DCC)
HI = Sqr((R1 * R1) - (C1H * C1H))
Alp
ha = Atn(HI / C1H) / Pi * 200
GCC = XYG(X_Centre_1, Y_Centre_1, X_Centre_2, Y_C
entre_2)
    If Solution_D_G = &quot;D&quot; Then
        ICY = XYGDY(X_Centre
_1, Y_Centre_1, GCC + Alpha, R1)
        ElseIf Solution_D_G = &quot;G&quot; Th
en
        ICY = XYGDY(X_Centre_1, Y_Centre_1, GCC - Alpha, R1)
    End If
En
d Function

'-----------------------------------------------------------------
----------------------------
' RCX Macro VB
' Macro enregistrée le 25/09/1997 
par TOUBIN RICHARD
' Calcul un raccordement circulaire en X en donnant le centr
e,la tangente et sont
' absisse et l'absisse du point a calculer.

Function R
CX(X_Centre, Y_Centre, R_négatif_à_droite, X_Tg_Départ, Y_Tg_Départ, Absisse_Tg_
Départ, Absisse_Point)
Pi = 4 * Atn(1)
G = XYG(X_Centre, Y_Centre, X_Tg_Départ
, Y_Tg_Départ)
L = Absisse_Point - Absisse_Tg_Départ
RCX = XYGDX(X_Centre, Y_C
entre, G + ((200 * L) / (-Pi * R_négatif_à_droite)), Abs(R_négatif_à_droite))
E
nd Function

'----------------------------------------------------------------
-----------------------------
' RCY Macro VB
' Macro enregistrée le 25/09/1997
 par TOUBIN RICHARD
' Calcul un raccordement circulaire en Y en donnant le cent
re,la tangente et sont
' absisse et l'absisse du point a calculer.

Function 
RCY(X_Centre, Y_Centre, R_négatif_à_droite, X_Tg_Départ, Y_Tg_Départ, Absisse_Tg
_Départ, Absisse_Point)
Pi = 4 * Atn(1)
G = XYG(X_Centre, Y_Centre, X_Tg_Dépar
t, Y_Tg_Départ)
L = Absisse_Point - Absisse_Tg_Départ
RCY = XYGDY(X_Centre, Y_
Centre, G + ((200 * L) / (-Pi * R_négatif_à_droite)), Abs(R_négatif_à_droite))

End Function

'---------------------------------------------------------------
------------------------------
' PIP Macro VB
' Macro enregistrée le 29/09/199
7 par TOUBIN RICHARD
' Calcul le Z d'un point sur une parabole.

Function PIP
(Absisse_Tg_A, Z_Tg_A, Pente_en_Tg_A, Absisse_Tg_B, Z_Tg_B, Pente_en_Tg_B, Rayon
_négatif_bosse, Absisse_Point)
PA = Pente_en_Tg_A / 100
PB = Pente_en_Tg_B / 1
00
W = Absisse_Tg_B - Absisse_Tg_A
Q = W * PA
U = Z_Tg_A + Q
P = U - Z_Tg_B

t = W * (-PB)
H = Z_Tg_B + t
I = (H) - (Z_Tg_A)
HB = (W * P) / (I + P)
HA =
 W - HB
XS = Absisse_Tg_A + HA
ZS = Z_Tg_B - (HB * PB)
E = Rayon_négatif_boss
e * PA
u_F = Rayon_négatif_bosse * PB
L = u_F - E
TE = L / 2
G = XS - TE
Y 
= XS + TE
m = ZS + (TE * (-PA))
V = ZS + (TE * PB)
XO = G - E
N = (Rayon_nég
atif_bosse / 2) * (PA * PA)
O = m - N
X = Absisse_Point - XO
Y2 = (X * X) / (
2 * Rayon_négatif_bosse)
Z = O + Y2
PIP = Z
End Function

'----------------
-----------------------------------------------------------------------------
'
 PIPHBX Macro VB
' Macro enregistrée le 29/09/1997 par TOUBIN RICHARD
' Calcul
 l'absisse du point Haut ou point Bas sur une parabole.

Function PIPHBX(Absis
se_Tg_A, Z_Tg_A, Pente_en_Tg_A, Absisse_Tg_B, Z_Tg_B, Pente_en_Tg_B, Rayon_négat
if_bosse)
PA = Pente_en_Tg_A / 100
PB = Pente_en_Tg_B / 100
W = Absisse_Tg_B 
- Absisse_Tg_A
Q = W * PA
U = Z_Tg_A + Q
P = U - Z_Tg_B
t = W * (-PB)
H = Z
_Tg_B + t
I = (H) - (Z_Tg_A)
HB = (W * P) / (I + P)
HA = W - HB
XS = Absisse
_Tg_A + HA
E = Rayon_négatif_bosse * PA
u_F = Rayon_négatif_bosse * PB
L = u_
F - E
TE = L / 2
G = XS - TE
XO = G - E
PIPHBX = XO
End Function

'------
--------------------------------------------------------------------------------
-------
' PICX Macro VB
' Macro enregistrée le 29/09/1997 par TOUBIN RICHARD

' Calcul des points intermédiaires sur une CLOTHOIDE et renvoi l'X.

Function 
PICX(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_Début_DROITE, Y_Début_DROITE, Ra
yon_négatif_DROITE, Longueur_L, Absisse)
Pi = 4 * Atn(1)
L = Longueur_L
R = R
ayon_négatif_DROITE
AP = Sqr(Abs(R * L))
XA = (L - ((L ^ 5) / (40 * (AP ^ 4)))
) + ((L ^ 9) / (3456 * (AP ^ 8)))
YA = ((L ^ 3) / (6 * (AP ^ 2))) - ((L ^ 7) / 
(336 * (AP ^ 6))) + ((L ^ 11) / (42240 * (AP ^ 10)))
'Calcul du gisement GD en 
RADIAN de la droite
GD = XYG(X_Début_DROITE, Y_Début_DROITE, X_Tg_Droite, Y_Tg_
Droite) / 200 * Pi
'Calcul d'un point intermédiaire.
LP = Abs(Absisse - Abs_Tg
_DROITE)
XB = (LP - ((LP ^ 5) / (40 * (AP ^ 4)))) + ((LP ^ 9) / (3456 * (AP ^ 8
)))
YB = ((LP ^ 3) / (6 * (AP ^ 2))) - ((LP ^ 7) / (336 * (AP ^ 6))) + ((LP ^ 1
1) / (42240 * (AP ^ 10)))
XO = X_Tg_Droite
If R &lt; 0 Then
    X = XO + (XB 
* (Sin(GD))) + (YB * (Cos(GD)))
    Else: X = XO + (XB * (Sin(GD))) - (YB * (Co
s(GD)))
End If
PICX = X
End Function

'------------------------------------
---------------------------------------------------------
' PICY Macro VB
' Ma
cro enregistrée le 29/09/1997 par TOUBIN RICHARD
' Calcul des points intermédia
ires sur une CLOTHOIDE et renvoi l'Y.

Function PICY(X_Tg_Droite, Y_Tg_Droite,
 Abs_Tg_DROITE, X_Début_DROITE, Y_Début_DROITE, Rayon_négatif_DROITE, Longueur_L
, Absisse)
Pi = 4 * Atn(1)
L = Longueur_L
R = Rayon_négatif_DROITE
AP = Sqr(
Abs(R * L))
XA = (L - ((L ^ 5) / (40 * (AP ^ 4)))) + ((L ^ 9) / (3456 * (AP ^ 8
)))
YA = ((L ^ 3) / (6 * (AP ^ 2))) - ((L ^ 7) / (336 * (AP ^ 6))) + ((L ^ 11) 
/ (42240 * (AP ^ 10)))
'Calcul du gisement GD en RADIAN de la droite
GD = XYG(
X_Début_DROITE, Y_Début_DROITE, X_Tg_Droite, Y_Tg_Droite) / 200 * Pi
'Calcul d'
un point intermédiaire.
LP = Abs(Absisse - Abs_Tg_DROITE)
XB = (LP - ((LP ^ 5)
 / (40 * (AP ^ 4)))) + ((LP ^ 9) / (3456 * (AP ^ 8)))
YB = ((LP ^ 3) / (6 * (AP
 ^ 2))) - ((LP ^ 7) / (336 * (AP ^ 6))) + ((LP ^ 11) / (42240 * (AP ^ 10)))
YO 
= Y_Tg_Droite
If R &lt; 0 Then
    Y = YO + (XB * (Cos(GD))) - (YB * (Sin(GD))
)
    Else: Y = YO + (XB * (Cos(GD))) + (YB * (Sin(GD)))
End If
PICY = Y
End
 Function

'------------------------------------------------------------------
---------------------------
' PIC2X Macro VB
' Macro enregistrée le 29/09/1997
 par TOUBIN RICHARD
' Calcul des points intermédiaires sur une CLOTHOIDE et ren
voi l'X.

Function PIC2X(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_Tg_Cercle,
 Y_Tg_Cercle, Rayon_négatif_DROITE, Longueur_L, Absisse)
Pi = 4 * Atn(1)
L = L
ongueur_L
R = Rayon_négatif_DROITE
AP = Sqr(Abs(R * L))
XA = (L - ((L ^ 5) / 
(40 * (AP ^ 4)))) + ((L ^ 9) / (3456 * (AP ^ 8)))
YA = ((L ^ 3) / (6 * (AP ^ 2)
)) - ((L ^ 7) / (336 * (AP ^ 6))) + ((L ^ 11) / (42240 * (AP ^ 10)))
'Calcul du
 gisement G2 en radian de la Tg à la droite vers la Tg au cercle
G2 = XYG(X_Tg_
Droite, Y_Tg_Droite, X_Tg_Cercle, Y_Tg_Cercle) / 200 * Pi
'Calcul du gisement G
D en radian de la droite
Alpha = (Pi / 2) - (Atn(XA / YA))
If R &lt; 0 Then
 
   GD = G2 - Alpha
    Else: GD = G2 + Alpha
End If
'Calcul d'un point interm
édiaire.
LP = Abs(Absisse - Abs_Tg_DROITE)
XB = (LP - ((LP ^ 5) / (40 * (AP ^ 
4)))) + ((LP ^ 9) / (3456 * (AP ^ 8)))
YB = ((LP ^ 3) / (6 * (AP ^ 2))) - ((LP 
^ 7) / (336 * (AP ^ 6))) + ((LP ^ 11) / (42240 * (AP ^ 10)))
XO = X_Tg_Droite

If R &lt; 0 Then
    X = XO + (XB * (Sin(GD))) + (YB * (Cos(GD)))
    Else: X 
= XO + (XB * (Sin(GD))) - (YB * (Cos(GD)))
End If
PIC2X = X
End Function

'
--------------------------------------------------------------------------------
-------------
' PIC2Y Macro VB
' Macro enregistrée le 29/09/1997 par TOUBIN RI
CHARD
' Calcul des points intermédiaires sur une CLOTHOIDE et renvoi l'Y.

Fu
nction PIC2Y(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_Tg_Cercle, Y_Tg_Cercle, 
Rayon_négatif_DROITE, Longueur_L, Absisse)
Pi = 4 * Atn(1)
L = Longueur_L
R =
 Rayon_négatif_DROITE
AP = Sqr(Abs(R * L))
XA = (L - ((L ^ 5) / (40 * (AP ^ 4)
))) + ((L ^ 9) / (3456 * (AP ^ 8)))
YA = ((L ^ 3) / (6 * (AP ^ 2))) - ((L ^ 7) 
/ (336 * (AP ^ 6))) + ((L ^ 11) / (42240 * (AP ^ 10)))
'Calcul du gisement G2 e
n radian de la Tg à la droite vers la Tg au cercle
G2 = XYG(X_Tg_Droite, Y_Tg_D
roite, X_Tg_Cercle, Y_Tg_Cercle) / 200 * Pi
'Calcul du gisement GD en radian de
 la droite
Alpha = (Pi / 2) - (Atn(XA / YA))
If R &lt; 0 Then
    GD = G2 - A
lpha
    Else: GD = G2 + Alpha
End If
'Calcul d'un point intermédiaire.
LP =
 Abs(Absisse - Abs_Tg_DROITE)
XB = (LP - ((LP ^ 5) / (40 * (AP ^ 4)))) + ((LP ^
 9) / (3456 * (AP ^ 8)))
YB = ((LP ^ 3) / (6 * (AP ^ 2))) - ((LP ^ 7) / (336 * 
(AP ^ 6))) + ((LP ^ 11) / (42240 * (AP ^ 10)))
YO = Y_Tg_Droite
If R &lt; 0 Th
en
    Y = YO + (XB * (Cos(GD))) - (YB * (Sin(GD)))
    Else: Y = YO + (XB * (
Cos(GD))) + (YB * (Sin(GD)))
End If
PIC2Y = Y
End Function

'--------------
-------------------------------------------------------------------------------

' GISAXECLOTH Macro VB
' Macro enregistrée le 29/09/1997 par TOUBIN RICHARD
'
 Calcul le gisement de l'axe sur une clothoide dos à la droite.
Function GISAXE
CLOTH(Gis_droite_Grades, Abs_Tg_DROITE, Abs_Tg_CERCLE, Rayon_négatif_DROITE, Abs
isse)
Pi = 4 * Atn(1)
L = Abs(Abs_Tg_CERCLE - Abs_Tg_DROITE)
RC = Rayon_négat
if_DROITE
AC = Sqr(Abs(RC * L))
LP = Abs(Absisse - Abs_Tg_DROITE)
If LP = 0 T
hen
    TETA = 0
    Else: RP = (AC ^ 2) / LP
          TETA = LP / (2 * RP) 
'en radians
End If

If RC &lt; 0 Then
     GISCLOT = (Gis_droite_Grades / 20
0 * Pi) + TETA 'en radians
    Else: GISCLOT = (Gis_droite_Grades / 200 * Pi) -
 TETA 'en radians
End If

GISAXECLOTH = 400 - (GISCLOT / Pi * 200)
If GISAXE
CLOTH &gt;= 400 Then
GISAXECLOTH = GISAXECLOTH - 400
End If
If GISAXECLOTH &l
t; 0 Then
GISAXECLOTH = GISAXECLOTH + 400
End If
End Function

'-----------
--------------------------------------------------------------------------------
--
' GISAXECLOTH2 Macro VB
' Macro enregistrée le 29/09/1997 par TOUBIN RICHAR
D
' Calcul le gisement de l'axe sur une clothoide dos à la droite.
Function GI
SAXECLOTH2(X_Tg_Droite, Y_Tg_Droite, Abs_Tg_DROITE, X_Tg_Cercle, Y_Tg_Cercle, Ab
s_Tg_CERCLE, Ray_nég_Droite_DàDr, Absisse)
Pi = 4 * Atn(1)
L = Abs_Tg_CERCLE -
 Abs_Tg_DROITE
R = Ray_nég_Droite_DàDr
AP = Sqr(Abs(R * L))
XA = (L - ((L ^ 5
) / (40 * (AP ^ 4)))) + ((L ^ 9) / (3456 * (AP ^ 8)))
YA = ((L ^ 3) / (6 * (AP 
^ 2))) - ((L ^ 7) / (336 * (AP ^ 6))) + ((L ^ 11) / (42240 * (AP ^ 10)))
'Calcu
l du gisement G2 en radian de la Tg à la droite vers la Tg au cercle
G2 = XYG(X
_Tg_Droite, Y_Tg_Droite, X_Tg_Cercle, Y_Tg_Cercle) / 200 * Pi
'Calcul du giseme
nt GD en radian de la droite
Alpha = (Pi / 2) - (Atn(XA / YA))
'--------------
--------------------------------
If R &lt; 0 Then
    GD = G2 - Alpha
    Els
e: GD = G2 + Alpha
End If
RC = Ray_nég_Droite_DàDr
AC = Sqr(Abs(R * L))
LP =
 Abs(Absisse - Abs_Tg_DROITE)
If LP = 0 Then
    TETA = 0
    Else: RP = (AC 
^ 2) / LP
          TETA = (LP / (2 * RP)) 'en radians
End If
If RC &lt; 0 Th
en
    GISAXECLOTH2 = (GD + TETA) / Pi * 200
    Else: GISAXECLOTH2 = (GD - TE
TA) / Pi * 200
End If
If L &lt; 0 Then
    GISAXECLOTH2 = GISAXECLOTH2 + 200

End If
If GISAXECLOTH2 &gt;= 400 Then
    GISAXECLOTH2 = GISAXECLOTH2 - 400

End If
If GISAXECLOTH2 &lt; 0 Then
    GISAXECLOTH2 = GISAXECLOTH2 + 400
End 
If

GISAXECLOTH2 = 400 - GISAXECLOTH2
End Function
</pre>
<br /><a name='co
nclusion'></a><h2> Conclusion : </h2>
<br />Util en calul topo, notement en pr
ojet
