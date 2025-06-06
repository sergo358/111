@echo off
title TeleZapis Bot
echo Установка зависимостей...
pip install -r requirements.txt
echo.
echo Запуск бота...
set PYTHONIOENCODING=UTF-8
python main.py
pause