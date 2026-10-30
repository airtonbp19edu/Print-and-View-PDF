@echo off
setlocal
set "PREVIEW_RUNTIME=%PRINT_VIEW_RUNTIME%"
if not defined PREVIEW_RUNTIME if exist "%LOCALAPPDATA%\Programs\PrintViewPDF\python\pythonw.exe" set "PREVIEW_RUNTIME=%LOCALAPPDATA%\Programs\PrintViewPDF"
if not defined PREVIEW_RUNTIME (
  echo Configure PRINT_VIEW_RUNTIME com a pasta de uma instalacao Windows do PrintViewPDF.
  pause
  exit /b 1
)
start "" "%PREVIEW_RUNTIME%\python\pythonw.exe" "%~dp0preview_preferences.py" --runtime "%PREVIEW_RUNTIME%"
