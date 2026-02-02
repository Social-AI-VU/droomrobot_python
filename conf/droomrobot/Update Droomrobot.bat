@echo off
REM === Git Pull Script for Droomrobot Repository ===
REM Location: C:\Users\external\repositories\droomrobot_python

SET REPO_DIR=C:\Users\external\repositories\droomrobot_python

echo Navigating to repository directory...
cd /d "%REPO_DIR%"

echo Resetting local changes...
git reset --hard

echo Cleaning untracked files and directories...
git clean -fd

echo Pulling latest changes from origin...
git pull origin main

echo Done!
pause
