@echo off
rem Start the review dashboard of this folder. Double-click this file; keep the window open while you review.
cd /d "%~dp0"
for %%P in ("%USERPROFILE%\anaconda3\python.exe" "%USERPROFILE%\miniconda3\python.exe" "%LOCALAPPDATA%\anaconda3\python.exe" "C:\ProgramData\anaconda3\python.exe" "C:\ProgramData\Anaconda3\python.exe" "C:\ProgramData\miniconda3\python.exe") do (
  if exist %%P (
    echo Using %%P
    %%P serve_dashboard.py
    goto :end
  )
)
where py >nul 2>nul && (py -3 serve_dashboard.py & goto :end)
where python >nul 2>nul && (python serve_dashboard.py & goto :end)
echo.
echo Python was not found. Open Anaconda Prompt (or a terminal), go to this folder and run:
echo   python serve_dashboard.py
:end
pause
