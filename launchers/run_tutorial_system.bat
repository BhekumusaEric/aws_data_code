@echo off
echo ========================================
echo Student Insights Pipeline - Tutorial System
echo ========================================
echo.

echo Checking Python installation...
py --version
if %errorlevel% neq 0 (
    echo Error: Python not found! Please install Python first.
    pause
    exit /b 1
)

echo.
echo Installing required packages...
py -m pip install streamlit plotly pandas numpy boto3
if %errorlevel% neq 0 (
    echo Warning: Some packages may not have installed correctly.
    echo You can continue anyway or install manually.
    pause
)

echo.
echo ========================================
echo Starting Student Insights Pipeline
echo ========================================
echo.
echo Features included:
echo   * Interactive tutorials for new users
echo   * Contextual hints and tips
echo   * Role-specific guidance
echo   * Step-by-step learning modules
echo.
echo The system will open in your browser at:
echo http://localhost:8501
echo.
echo To stop the system, press Ctrl+C
echo.

py -m streamlit run main.py --server.port=8501

echo.
echo System stopped. Press any key to exit.
pause
