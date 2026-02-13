@echo off
chcp 65001 >nul
cd /d "C:\Users\Microsoft\Desktop\local_progs\tahfeed_professional_website_2\myproject"
echo Applying migrations...
python manage.py migrate
echo.
echo Running setup calendar...
python setup_calendar.py
echo.
echo Done!
pause
