rem ! envoyer un fichier sur le traceur avec copy
rem ! 		ou avec print du systeme
rem ! le traceur est connecte sur le port com1: 
rem mode com1: ..... a mettre dans autoexec.bat
rem mode com1:96,n,8,1,p
copy %1 com1:
rem  			ou !!!
rem mode lpt1:=com1:
rem print %1
