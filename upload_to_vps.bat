@echo off
REM Quick Upload Script for Windows
REM This uploads your Forex Engine to your VPS

echo ================================
echo Forex Engine - Upload to VPS
echo ================================
echo.

REM Ask for VPS IP
set /p VPS_IP="Enter your VPS IP address: "

echo.
echo Uploading files to %VPS_IP%...
echo.

REM Upload files using SCP
scp -r C:\Users\rajpa\Desktop\Engine\*.py root@%VPS_IP%:/opt/forex-engine/
scp -r C:\Users\rajpa\Desktop\Engine\.env root@%VPS_IP%:/opt/forex-engine/
scp -r C:\Users\rajpa\Desktop\Engine\requirements.txt root@%VPS_IP%:/opt/forex-engine/

echo.
echo ================================
echo Upload Complete!
echo ================================
echo.
echo Next steps:
echo 1. SSH into your VPS: ssh root@%VPS_IP%
echo 2. Start the service: systemctl start forex-engine
echo 3. Check status: systemctl status forex-engine
echo.
pause
