@echo off
rem ============================================================
rem  DRTxECM startup diagnostic
rem
rem  Run this when DRTxECM.exe will not start, then send the whole
rem  output back to the developer. It only READS settings; it does
rem  not change anything unless you explicitly answer Y at the
rem  unblock prompt.
rem
rem  HOW TO RUN
rem    Put this file in the SAME FOLDER as DRTxECM.exe, then
rem    double-click it. If Windows also blocks this file,
rem    right-click it, choose Properties, tick "Unblock", then run
rem    it again.
rem
rem  IMPORTANT: keep this file pure ASCII.
rem    cmd.exe reads .bat/.cmd using the system ANSI codepage (CP950
rem    on Traditional Chinese Windows). Multi-byte characters corrupt
rem    its byte-offset tracking and it can then misread EARLIER lines
rem    of the same file. Same rule as build.bat.
rem
rem  Keep CRLF line endings. git stores text blobs as LF by default,
rem  and cmd.exe can misparse an LF-only batch file (multi-line if
rem  blocks and for /f loops are the known trouble spots). The repo
rem  marks *.cmd as -text in .gitattributes so the bytes are kept.
rem ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"
set "SELF=%~dp0"
set "EXE=DRTxECM.exe"

echo ============================================================
echo   DRTxECM startup diagnostic
echo ============================================================
echo   folder : %SELF%
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format s"') do echo   time   : %%T   ^(ISO, locale-neutral so it pastes cleanly^)
echo.

echo [1] Bundle integrity
echo ------------------------------------------------------------
if exist "%EXE%" (
  for %%A in ("%EXE%") do echo    OK      %EXE%  %%~zA bytes   [expected 11352605]
  for /f %%H in ('powershell -NoProfile -Command "(Get-FileHash -LiteralPath '%EXE%' -Algorithm SHA256).Hash"') do echo    SHA256 : %%H
  echo             ^(give the SHA256 to IT if they need to allowlist the file^)
) else (
  echo    MISSING %EXE%
  echo            ^>^> an antivirus product may have quarantined it
)
if exist "_internal" (
  for /f %%C in ('dir /s /b /a-d "_internal" 2^>nul ^| find /c /v ""') do echo    OK      _internal\  %%C files   [expected roughly 1300-1500]
) else (
  echo    MISSING _internal\
  echo            ^>^> the ZIP was not fully extracted, or extraction failed
)
echo.

echo [2] Where this folder is
echo ------------------------------------------------------------
for /f %%L in ('powershell -NoProfile -Command "(Get-Location).Path.Length"') do set "PLEN=%%L"
for /f %%R in ('powershell -NoProfile -Command "159 - (Get-Location).Path.Length"') do set "ROOM=%%R"
echo    path length : !PLEN! characters
echo    Windows allows 260 characters. The longest file in this bundle is
echo    100 characters, so the folder must stay under about 159.
echo    room to spare : !ROOM! characters
if !ROOM! LSS 0 (
  echo    WARNING: this path is TOO LONG. Extract to C:\DRTxECM instead.
) else (
  echo    OK - the path is short enough, this is not the problem.
)
echo %SELF% | findstr /i /c:"\AppData\Local\Temp\" >nul
if not errorlevel 1 (
  echo    WARNING: this looks like a temporary folder, i.e. the program
  echo             is being run from INSIDE the ZIP. Extract it first.
)
for /f %%O in ('powershell -NoProfile -Command "try { ((Get-Item -LiteralPath '%EXE%').Attributes -band [IO.FileAttributes]::Offline) -ne 0 } catch { 'unknown' }"') do (
  if /i "%%O"=="True" echo    WARNING: the file is a OneDrive "online only" placeholder. Right-click the folder and choose "Always keep on this device".
)
echo.

echo [3] Mark of the Web  (the "downloaded file" block)
echo ------------------------------------------------------------
dir /r "%EXE%" 2>nul | findstr /i "Zone.Identifier" >nul
if not errorlevel 1 (
  echo    PRESENT - Windows has flagged this file as downloaded from
  echo              the internet, which can block it from running.
) else (
  echo    not present on %EXE%
)
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Attachments" /v SaveZoneInformation 2>nul | findstr /i "SaveZoneInformation" || echo    HKCU SaveZoneInformation : not set ^(default^)
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Attachments" /v SaveZoneInformation 2>nul | findstr /i "SaveZoneInformation" || echo    HKLM SaveZoneInformation : not set ^(default^)
echo    ^(a value of 0x3 means the organisation forces the download
echo     mark to stay, so "Unblock" will not be available^)
echo.
set "ANS="
set /p "ANS=Try to remove the download mark from all files here? [Y/N] "
if /i "%ANS%"=="Y" (
  powershell -NoProfile -Command "Get-ChildItem -LiteralPath '.' -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue" 2>nul
  echo    re-checking %EXE% after the unblock...
  dir /r "%EXE%" 2>nul | findstr /i "Zone.Identifier" >nul
  if errorlevel 1 (
    echo    CLEARED - no download mark left. Try starting DRTxECM.exe again now.
  ) else (
    echo    STILL PRESENT - the mark could not be removed ^(a policy may
    echo    force it, or the file is read-only^).
  )
)
echo.

echo [4] Policies that block unsigned programs
echo ------------------------------------------------------------
echo -- AppLocker (effective policy) --
powershell -NoProfile -Command "try { $p = Get-AppLockerPolicy -Effective -ErrorAction Stop; $c = @($p.RuleCollections); if ($c.Count -eq 0) { 'not configured' } else { foreach ($rc in $c) { 'collection ' + $rc.CollectionType + '  enforcement=' + $rc.EnforcementMode + '  rules=' + @($rc.Rules).Count } } } catch { 'cannot query (AppLocker module not available on this edition)' }"
echo -- AppLocker enforcement service (AppIDSvc) --
sc query AppIDSvc 2>nul | findstr /i "STATE" || echo    service not present
echo -- WDAC / Code Integrity policy --
powershell -NoProfile -Command "$d='C:\Windows\System32\CodeIntegrity\CiPolicies\Active'; if (Test-Path $d) { $f=@(Get-ChildItem $d -ErrorAction SilentlyContinue); if ($f.Count -eq 0) { 'no active policy files' } else { 'policy file count: ' + $f.Count + '  (Windows itself ships several; they are not necessarily enforced)' } } else { 'no active policy files' }"
echo -- Defender ASR rule: block untrusted/unsigned executables --
powershell -NoProfile -Command "try { $mode=(Get-MpComputerStatus).AMRunningMode; if ($mode -match 'Passive') { 'N/A - Defender is passive, so its ASR rules are not in force here' } else { $ids=@(Get-MpPreference).AttackSurfaceReductionRules_Ids; $acts=@(Get-MpPreference).AttackSurfaceReductionRules_Actions; $g='01443614-cd74-433a-b99e-2ecdc07bfc25'; $i=[array]::IndexOf($ids,$g); if ($i -ge 0) { 'SET  action=' + $acts[$i] + '   (1 = Block)' } else { 'not set' } } } catch { 'cannot query' }"
echo -- Controlled Folder Access --
powershell -NoProfile -Command "try { 'EnableControlledFolderAccess = ' + (Get-MpPreference).EnableControlledFolderAccess } catch { 'cannot query' }"
echo.

echo [5] Antivirus state  (the usual cause on a managed machine)
echo ------------------------------------------------------------
powershell -NoProfile -Command "try { Get-MpComputerStatus | Select-Object AMRunningMode,RealTimeProtectionEnabled,IsTamperProtected | Format-List } catch { 'cannot query Defender status' }"
echo -- which product is actually in charge --
powershell -NoProfile -Command "try { $m=(Get-MpComputerStatus).AMRunningMode; if ($m -match 'Passive') { 'Defender is PASSIVE: a third-party product is the primary antivirus and is what would block the program.' } elseif ($m -match 'Normal') { 'Defender is the primary antivirus.' } else { 'Defender running mode: ' + $m } } catch { 'cannot query' }"
echo -- third-party security services installed --
powershell -NoProfile -Command "try { $s=@(Get-Service | Where-Object { $_.DisplayName -match 'WithSecure|F-Secure|Sophos|Symantec|Broadcom|Trend|Kaspersky|ESET|CrowdStrike|SentinelOne|McAfee|Trellix|Palo Alto|Fortinet|Check ?Point|Bitdefender|Avast|AVG|Malwarebytes' }); if ($s.Count -eq 0) { 'none found' } else { $s | Select-Object Status,Name,DisplayName | Format-Table -AutoSize } } catch { 'cannot enumerate services' }"
echo -- all registered antivirus products --
powershell -NoProfile -Command "try { Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct -ErrorAction Stop | Select-Object displayName,productState | Format-Table -AutoSize } catch { 'none reported' }"
echo -- threat detections mentioning DRTxECM --
powershell -NoProfile -Command "try { $d=@(Get-MpThreatDetection -ErrorAction Stop | Where-Object { $_.Resources -match 'DRTxECM' }); if ($d.Count -eq 0) { 'none' } else { $d | Select-Object -First 5 ThreatID,InitialDetectionTime,Resources | Format-List } } catch { 'Defender detections unavailable (passive mode, or needs an administrator prompt)' }"
echo.
echo    NOTE: if a third-party product is listed above, its blocking rules
echo    are administered centrally by your organisation's IT department and
echo    cannot be changed from this machine. Ask IT to allow DRTxECM.exe,
echo    and give them the SHA256 printed in section [1].
echo.

echo [6] System
echo ------------------------------------------------------------
powershell -NoProfile -Command "$o=Get-CimInstance Win32_OperatingSystem; 'Windows build ' + $o.BuildNumber + '  ' + $o.OSArchitecture + '  locale ' + (Get-Culture).Name"
powershell -NoProfile -Command "'is elevated (admin): ' + ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
powershell -NoProfile -Command "'user: ' + $env:USERNAME + '   profile: ' + $env:USERPROFILE"
echo.

echo ============================================================
echo   Copy EVERYTHING above and send it back for diagnosis.
echo ============================================================
pause
