@echo off
rem ============================================================
rem  DRTxECM - troubleshooting launcher (console mode)
rem
rem  Same as START-HERE.bat, but it keeps this black window open
rem  and shows every message and error from the program itself.
rem
rem  Use it when the normal launcher appears to do nothing, or when
rem  the program window closes immediately. Copy whatever this window
rem  prints and send it back.
rem
rem  Pure ASCII, CRLF. See the notes at the top of START-HERE.bat for
rem  why those two rules matter.
rem ============================================================
call "%~dp0START-HERE.bat" console
