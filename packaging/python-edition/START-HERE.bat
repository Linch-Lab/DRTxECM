@echo off
rem ============================================================
rem  DRTxECM - Python edition launcher
rem
rem  FIRST RUN : creates a private Python environment in .venv and
rem              installs the dependencies. Needs internet, takes a
rem              few minutes, happens only once.
rem  LATER RUNS: starts the program immediately.
rem
rem  USAGE
rem    double-click START-HERE.bat      normal start
rem    START-HERE.bat repair            delete .venv and reinstall
rem    START-HERE.bat console           show messages and errors
rem    (DEBUG.bat does the same as 'console')
rem
rem  WHY THIS FILE IS PURE ASCII
rem    cmd.exe reads .bat/.cmd using the system ANSI codepage (CP950 on
rem    Traditional Chinese Windows). Non-ASCII bytes corrupt its
rem    byte-offset tracking and it can then misread EARLIER lines of this
rem    same file - that bug cost us a broken build once. All Chinese
rem    instructions therefore live in READ-ME-FIRST.txt, which this script
rem    opens in Notepad when it needs to explain something. Keep CRLF line
rem    endings too; see .gitattributes.
rem
rem  OPTIONAL
rem    Set DRTXECM_PYTHON to the full path of a python.exe to force which
rem    interpreter is used, for example when it is not on PATH.
rem ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"
title DRTxECM

set "VENV=.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "VPYW=%VENV%\Scripts\pythonw.exe"
set "DONE=%VENV%\.installed"
set "READMEFILE=READ-ME-FIRST.txt"
set "ACTION=%~1"
set "MODE=gui"
if /i "%ACTION%"=="console" set "MODE=console"

echo ============================================================
echo   DRTxECM  -  Python edition
echo ============================================================
echo.

if not exist "launch.py" (
    echo [ERROR] launch.py was not found in this folder.
    echo.
    echo         This launcher must stay in the DRTxECM folder, next to
    echo         launch.py. If you moved it, move it back, or re-extract
    echo         the ZIP and run it from there.
    echo.
    goto :explain
)

if /i "%ACTION%"=="repair" (
    echo Repair requested - deleting the existing environment.
    if exist "%VENV%" rmdir /s /q "%VENV%"
    echo.
)

rem ---- already installed: start immediately ----
if exist "%DONE%" if exist "%VPYW%" goto :run

rem ============================================================
rem  Find a usable Python
rem ============================================================
echo Looking for Python 3.10 or 3.11 ...
echo.

set "PYCMD="
set "SAWVER="

if defined DRTXECM_PYTHON if exist "%DRTXECM_PYTHON%" call :trypath "%DRTXECM_PYTHON%"
if defined PYCMD goto :found
call :tryver py -3.10
if defined PYCMD goto :found
call :tryver py -3.11
if defined PYCMD goto :found
call :tryplain python
if defined PYCMD goto :found
if defined SAWVER goto :badver
goto :nopython

:trypath
"%~1" -c "import sys" >nul 2>&1
if errorlevel 1 exit /b
"%~1" -c "import sys;print(sys.version.split()[0])" >"%TEMP%\drtxecm_pyver.txt" 2>nul
if errorlevel 1 exit /b
set /p SAWVER=<"%TEMP%\drtxecm_pyver.txt"
"%~1" -c "import sys;sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,11) else 2)" >nul 2>&1
if errorlevel 1 exit /b
set PYCMD="%~1"
exit /b

:tryver
%1 %2 -c "import sys" >nul 2>&1
if errorlevel 1 exit /b
%1 %2 -c "import sys;print(sys.version.split()[0])" >"%TEMP%\drtxecm_pyver.txt" 2>nul
if errorlevel 1 exit /b
set /p SAWVER=<"%TEMP%\drtxecm_pyver.txt"
%1 %2 -c "import sys;sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,11) else 2)" >nul 2>&1
if errorlevel 1 exit /b
set PYCMD=%1 %2
exit /b

:tryplain
%1 -c "import sys" >nul 2>&1
if errorlevel 1 exit /b
%1 -c "import sys;print(sys.version.split()[0])" >"%TEMP%\drtxecm_pyver.txt" 2>nul
if errorlevel 1 exit /b
set /p SAWVER=<"%TEMP%\drtxecm_pyver.txt"
%1 -c "import sys;sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,11) else 2)" >nul 2>&1
if errorlevel 1 exit /b
set PYCMD=%1
exit /b

:found
echo   Found Python %SAWVER%
echo.
echo Creating a private environment in .venv ...
%PYCMD% -m venv "%VENV%"
if not exist "%VPY%" goto :venvfail

echo.
echo Installing dependencies.
echo   About 150 MB is downloaded and it takes a few minutes.
echo   This happens only once - later starts are immediate.
echo   Please leave this window open until it finishes.
echo.
"%VPY%" -m pip install --upgrade pip --disable-pip-version-check --quiet
"%VPY%" -m pip install -r requirements.txt click --disable-pip-version-check --progress-bar off
if errorlevel 1 goto :pipfail

echo.
echo Checking the installation ...
"%VPY%" -c "import importlib.util as u,sys;m=[x for x in ['numpy','scipy','pandas','matplotlib','sklearn','cvxopt','PyQt5','click'] if u.find_spec(x) is None];sys.stdout.write('  missing: '+', '.join(m)+'\n') if m else sys.stdout.write('  all dependencies present\n');sys.exit(1 if m else 0)"
if errorlevel 1 goto :verifyfail

echo ok>"%DONE%"
echo.
echo Setup complete.
echo.
goto :run

rem ============================================================
rem  Start the program
rem ============================================================
:run
echo Starting DRTxECM ...
echo.
echo   The program window can take 10 to 30 seconds to appear, because it
echo   loads large scientific libraries on startup. Please be patient.
echo   If nothing appears at all, close this window and run DEBUG.bat
echo   instead - that keeps the window open and shows the real error.
echo.
if /i "%MODE%"=="console" goto :runconsole

rem pythonw.exe for a clean start, leaving no console window behind.
rem Deliberately no "did it start?" check: startup legitimately takes
rem 10-30 s, so any short timeout would report false failures.
start "" "%VPYW%" launch.py
exit /b 0

:runconsole
echo Console mode. Messages and errors from the program appear below.
echo Close this window, or press Ctrl+C, to stop the program.
echo ------------------------------------------------------------
echo.
"%VPY%" launch.py
echo.
echo ------------------------------------------------------------
echo The program has exited. Press any key to close this window.
pause >nul
exit /b 0

rem ============================================================
rem  Problems
rem ============================================================
:nopython
echo [ERROR] Python was not found on this computer.
echo.
echo         DRTxECM needs Python 3.10 or 3.11. Nothing else is required
echo         and you do NOT need administrator rights.
echo.
goto :explain

:badver
echo [ERROR] Python %SAWVER% was found, but it cannot be used.
echo.
echo         DRTxECM needs Python 3.10 or 3.11.
echo         The scientific libraries it uses are pinned to versions that
echo         have no packages for 3.12 and newer, so with 3.12 or 3.13 the
echo         program would fail to start.
echo.
echo         Install Python 3.10 from python.org, tick "Add python.exe to
echo         PATH" during setup, then run this file again.
echo         You do NOT need to uninstall %SAWVER%.
echo.
goto :explain

:explain
echo Opening READ-ME-FIRST.txt, which explains this in Chinese ...
if exist "%READMEFILE%" start "" notepad "%READMEFILE%"
echo.
echo Press any key to close this window.
pause >nul
exit /b 1

:venvfail
echo [ERROR] Could not create the Python environment .venv
echo.
echo         Usual causes:
echo           - not enough free disk space, about 1 GB is needed
echo           - the folder is inside OneDrive or another synced folder
echo           - antivirus software blocked the files being written
echo.
echo         Extract DRTxECM to a short local path such as C:\DRTxECM and
echo         run this file again.
echo.
echo Press any key to close this window.
pause >nul
exit /b 1

:pipfail
echo [ERROR] Installing the dependencies failed.
echo.
echo         Usual causes:
echo           - no internet, or a firewall or proxy blocks pypi.org
echo           - antivirus software blocked the downloaded files
echo           - a temporary network problem - simply run this file again
echo.
echo         On a school or company network PyPI is often blocked. In that
echo         case use the prebuilt Windows ZIP instead: it needs no
echo         downloading of libraries.
echo.
echo Press any key to close this window.
pause >nul
exit /b 1

:verifyfail
echo [ERROR] Some dependencies are missing after installation.
echo.
echo         Run this file once more - a partial download is often
echo         completed on the second attempt.
echo         To start over from scratch, run:
echo             START-HERE.bat repair
echo.
echo Press any key to close this window.
pause >nul
exit /b 1
