@echo off
setlocal

rem ============================================================
rem  Build flash-attn-v100 natively on Windows (V100 / sm_70)
rem  Edit the settings below to match YOUR machine.
rem ============================================================

rem --- Settings ------------------------------------------------
set "VENV=D:\ComfyTesla124\.venv"
set "REPO=D:\tmp\flash-attn-v100"
set "CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4"

rem Path to vcvarsall.bat (adjust if vswhere doesn't find your VS)
set "VCTOOLS="

rem --- Resolve VS install path via vswhere ---------------------
if "%VCTOOLS%"=="" (
  for /f "usebackq tokens=*" %%i in (`"^C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -property installationPath`) do set "VSROOT=%%i"
  if defined VSROOT (
    set "VCTOOLS=%VSROOT%\VC\Auxiliary\Build\vcvarsall.bat"
  )
)
if not defined VCTOOLS (
  echo ERROR: vcvarsall.bat not found. Edit VCTOOLS in this file.
  exit /b 1
)

rem --- Activate environment ------------------------------------
call "%VENV%\Scripts\activate.bat"
if errorlevel 1 (
    echo venv activation FAILED
    exit /b 1
)
call "%VCTOOLS%" x64 -vcvars_ver=14.38
if errorlevel 1 (
    echo vcvarsall FAILED
    exit /b 1
)

set DISTUTILS_USE_SDK=1
set "PATH=%PATH%;%CUDA_HOME%\bin"

rem --- THE fix: full parallelism crashes nvcc/linker -----------
set MAX_JOBS=4

cd /d "%REPO%"

rem --- Preflight checks ----------------------------------------
where cl
where nvcc
python -c "import torch; print('torch cuda:', torch.version.cuda, torch.cuda.is_available())"

rem --- Build and install ---------------------------------------
python setup.py install
