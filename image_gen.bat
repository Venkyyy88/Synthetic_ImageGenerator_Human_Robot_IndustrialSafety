@echo off
REM num_runs - number of times to run main.py script
set num_runs=1
REM Get the directory where this batch script is located
set "SCRIPT_DIR=%~dp0"

REM Change to the directory where the batch script is located
cd /d "%SCRIPT_DIR%"

for /l %%x in (1,1,%num_runs%) do (
    echo Running iteration %%x
    REM Use relative paths for BlenderProc run command
    blenderproc run code/image_gen.py
)