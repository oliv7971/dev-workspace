:debut
echo off
cls
retm0
if not exist \p65.$$$ goto :prin
p65
del \p65.$$$
goto :debut
:prin
if not exist \prin.$$$ goto :trac
echo on
imprime
:trac
if not exist \trac.$$$ goto :pbsai
echo on
trace
:pbsai
if not exist \pbsai.$$$ goto :p64
command /c pbsai
del \pbsai.$$$
goto :debut
:p64
if not exist \p64.$$$ goto :p34
p64
del \p64.$$$
goto :debut
:p34
if not exist \p34.$$$ goto :cniv
p34
pause
del \p34.$$$
goto :debut
:cniv
if not exist \cniv.$$$ goto :fin
command /c \coralis\exe\cnivmcg
goto :debut
:fin
if not exist \fin.$$$ goto :debut
mode lpt1: > \fin.$$$
del \fin.$$$
