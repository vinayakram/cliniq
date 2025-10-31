@echo off
echo.
echo ============================================
echo      ClinIQ - Smart Clinic System
echo      Starting... Please wait...
echo ============================================
echo.

:: Change to current folder
cd /d "%~dp0"

:: Create virtual environment if not exists
if not exist "venv" (
    echo Creating Python environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip and install requirements
echo Installing required software...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

:: Run the app
echo.
echo Opening ClinIQ in your browser...
echo Close this window or press Ctrl+C to stop.
echo.
streamlit run app.py --server.port=8501

:: Keep window open if error
pause