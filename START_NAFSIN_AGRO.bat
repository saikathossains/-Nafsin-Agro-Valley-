@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Could not install requirements. Please install Python 3.11 or newer.
  pause
  exit /b 1
)
py -3 -m streamlit run app.py
pause
