@echo off
title Kilo Bridge 24/7 Autonomous Employment Daemon
echo ======================================================================
echo KILO BRIDGE 24/7 AUTONOMOUS EMPLOYMENT DAEMON
echo ======================================================================
cd /d "%~dp0"
venv\Scripts\python.exe scripts\lane_daemon.py %*
pause
