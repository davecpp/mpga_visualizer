@echo off
REM Script to run the MPGA GUI application on Windows

REM Check for Python 3
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.6+ and try again.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYVER=%%i
echo %PYVER% | findstr /r "^3\." >NUL
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3 is required but Python %PYVER% was found.
    echo Please install Python 3.6+ and try again.
    pause
    exit /b 1
)

REM Check for required packages
echo Checking for required packages...
set MISSING_PACKAGES=0

python -c "import PyQt5" 2>NUL
if %ERRORLEVEL% NEQ 0 set MISSING_PACKAGES=1

python -c "import numpy" 2>NUL
if %ERRORLEVEL% NEQ 0 set MISSING_PACKAGES=1

python -c "import matplotlib" 2>NUL
if %ERRORLEVEL% NEQ 0 set MISSING_PACKAGES=1

if %MISSING_PACKAGES% NEQ 0 (
    echo Some required packages are missing.
    echo Would you like to install them now? (Y/N)
    set /p ANSWER=
    if /i "%ANSWER%"=="Y" (
        echo Installing required packages...
        python -m pip install PyQt5 numpy matplotlib
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install required packages.
            pause
            exit /b 1
        )
    ) else (
        echo Please install the required packages and try again.
        pause
        exit /b 1
    )
)

REM Create necessary directories if they don't exist
if not exist core mkdir core
if not exist ui mkdir ui
if not exist utils mkdir utils

REM Run the application
echo Starting MPGA GUI...
python main.py

pause
