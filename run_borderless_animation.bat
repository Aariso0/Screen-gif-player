@echo off
REM Start from the folder this script lives in, so relative config paths work.
cd /d "%~dp0"

REM Launch the generic transparent/borderless animation player.
python borderless_animation_player.py
