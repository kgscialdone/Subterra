@echo off
IF [%JUSTTERMINATE%] == [OKAY] (
    SET JUSTTERMINATE=
		python "%~dp0/bin/subterra.py" %*
) ELSE (
    SET JUSTTERMINATE=OKAY
    CALL %0 %* <NUL
)
