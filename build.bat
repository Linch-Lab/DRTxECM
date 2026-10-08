@echo off
rem ============================================================
rem  DRTxECM build script
rem
rem  Output: dist\DRTxECM\DRTxECM.exe                    (test copy)
rem          releases\v<version>\DRTxECM-win64.zip       (release asset)
rem          releases\v<version>\SHA256SUMS.txt
rem
rem  IMPORTANT: keep this file pure ASCII.
rem  cmd.exe reads .bat files using the system ANSI codepage (CP950 on
rem  Traditional Chinese Windows). Multi-byte characters in a .bat file
rem  corrupt cmd.exe's byte-offset tracking and it can then misread
rem  EARLIER lines of the same file. Using only ASCII avoids that class
rem  of bug entirely.
rem
rem  Requires Python 3.10. See packaging\README.md for why.
rem ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10 and tick "Add Python to PATH".
    pause
    exit /b 1
)

rem ---- read version from version.txt (single source of truth) ----
set "VER="
set /p VER=<version.txt
if "%VER%"=="" set "VER=0.0.0"

echo ==========================================
echo   DRTxECM build   version %VER%
echo ==========================================
echo.

echo [1/6] Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install -r packaging\requirements-build.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo [2/6] Generating Windows version resource...
python packaging\make_version_info.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate packaging\version_info.txt.
    pause
    exit /b 1
)

echo.
echo [3/6] Building EXE (onedir). This takes a few minutes...
python -m PyInstaller --noconfirm --clean DRTxECM.spec
if not exist "dist\DRTxECM\DRTxECM.exe" (
    echo.
    echo [ERROR] Build failed. Check the PyInstaller output above.
    pause
    exit /b 1
)

rem Ship the user-facing help files INSIDE the bundle so they are present
rem after extraction. DRTxECM.exe is unsigned, so users on managed machines
rem can hit policy or antivirus blocks; without these files a blocked user
rem has nothing to act on and nothing to report back.
rem Keep this echo ASCII-only - see the note at the top of this file.
if exist "packaging\extras" (
    copy /y "packaging\extras\*" "dist\DRTxECM\" >nul
    echo       bundled the pre-flight readme and the diagnose script
) else (
    echo [WARN] packaging\extras not found - shipping without help files
)

set "OUTDIR=releases\v%VER%"
echo.
echo [4/6] Preparing %OUTDIR% ...
if not exist "releases" mkdir "releases" >nul 2>nul
if not exist "%OUTDIR%" mkdir "%OUTDIR%" >nul 2>nul

echo.
echo [5/6] Packing and hashing...
powershell -NoProfile -Command "Compress-Archive -Path 'dist\DRTxECM\*' -DestinationPath '%OUTDIR%\DRTxECM-win64.zip' -Force"
powershell -NoProfile -Command "Get-FileHash '%OUTDIR%\DRTxECM-win64.zip' -Algorithm SHA256 | ForEach-Object { $_.Hash + '  DRTxECM-win64.zip' } | Out-File -Encoding utf8 '%OUTDIR%\SHA256SUMS.txt'"

echo.
echo [6/6] Done.
type "%OUTDIR%\SHA256SUMS.txt"
echo.
echo   Test copy : dist\DRTxECM\DRTxECM.exe
echo   Release   : %OUTDIR%\DRTxECM-win64.zip
echo.
echo Next: git tag v%VER% ^&^& git push origin v%VER%
pause
