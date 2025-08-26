@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000 "') do taskkill /PID %%a /F
echo Port 5000 terminated.
pause