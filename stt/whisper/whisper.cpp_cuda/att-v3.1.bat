@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Audio File Text Converter v3.1

echo.
echo ========================================
echo         Audio File Text Converter
echo ========================================
echo.

:main_loop
REM Record start time for this session
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set "start_hour=%%a"
    set "start_min=%%b"
    set "start_sec=%%c"
)

REM Remove leading space from hour if present
if "!start_hour:~0,1!"==" " set "start_hour=!start_hour:~1!"

echo.
echo ========================================
echo         New Conversion Session
echo ========================================
echo.

REM Get input values
set /p yearmonth="Year/Month (e.g., 202501): "
if "%yearmonth%"=="" goto :exit_program

set /p day="Day (e.g., 05): "
if "%day%"=="" goto :exit_program

set /p filetype="File type (txt/vtt) [default: txt]: "
if "%filetype%"=="" (
    set "filetype=txt"
    echo Using default file type: txt
)

echo.
echo Entered date: %yearmonth% year/month %day% day
echo File type: .%filetype%
echo.

REM Set paths
set "source_path=audio\%yearmonth%\%day%"
set "target_path=text\%yearmonth%\%day%"

REM Set target type based on filetype
if /i "%filetype%"=="txt" (
    set "target_type=otxt"
) else if /i "%filetype%"=="vtt" (
    set "target_type=ovtt"
) else (
    echo Error: Invalid file type. Please use 'txt' or 'vtt'.
    echo Using default file type: txt
    set "filetype=txt"
    set "target_type=otxt"
)

REM Check source folder
if not exist "%source_path%" (
    echo Error: Cannot find folder %source_path%.
    echo.
    echo Please check:
    echo - Make sure you entered the correct year/month and day
    echo - Verify that the folder exists in the audio directory
    echo.
    pause
    goto :main_loop
)

REM Create target folder
if not exist "%target_path%" (
    echo Creating target folder: %target_path%
    mkdir "%target_path%" 2>nul
    if errorlevel 1 (
        echo Error: Failed to create target folder.
        pause
        goto :main_loop
    )
)

echo Converting audio files to text...
echo.

set "processed=0"
set "errors=0"

REM Count audio files
set "file_count=0"
for %%f in ("%source_path%\*.wav" "%source_path%\*.mp3" "%source_path%\*.webm" "%source_path%\*.m4a" "%source_path%\*.flac" "%source_path%\*.ogg" "%source_path%\*.aac" "%source_path%\*.wma") do set /a file_count+=1

if %file_count%==0 (
    echo Warning: No audio files found in %source_path% folder.
    echo Supported formats: .wav, .mp3, .webm, .m4a, .flac, .ogg, .aac, .wma
    echo.
    pause
    goto :main_loop
)

echo Processing %file_count% audio files in total.
echo.

REM Process files
set "current_file=0"
for %%f in ("%source_path%\*.wav" "%source_path%\*.mp3" "%source_path%\*.webm" "%source_path%\*.m4a" "%source_path%\*.flac" "%source_path%\*.ogg" "%source_path%\*.aac" "%source_path%\*.wma") do (
    set /a current_file+=1
    set "filename=%%~nf"
    set "output_file=%target_path%\!filename!"
    
    echo Processing: %%~nxf [!current_file!/%file_count%]
    
    REM Execute whisper-cli and check results
    whisper-cli.exe -l ko -m models/ggml-large-v2-q8_0.bin -f "%%f" -%target_type% -of "!output_file!" > temp_output.txt 2>&1
   
    REM Consider successful if "total time" is included
    findstr /c:"total time" temp_output.txt >nul
    if !errorlevel! equ 0 (
        echo   ✓ Completed: !filename!.%filetype%
        set /a processed+=1
    ) else (
        echo   ✗ Failed: !filename!.%filetype%
        set /a errors+=1
    )
    
    REM Delete temporary file
    del temp_output.txt >nul 2>&1
)

echo.
echo ========================================
echo              Processing Complete
echo ========================================
echo  Success: %processed% files
echo  Failed: %errors% files
echo  Save location: %target_path%

REM Calculate elapsed time
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set "end_hour=%%a"
    set "end_min=%%b"
    set "end_sec=%%c"
)

REM Remove leading space from hour if present
if "!end_hour:~0,1!"==" " set "end_hour=!end_hour:~1!"

REM Initialize variables
set "hour_diff=0"
set "min_diff=0"
set "sec_diff=0"

REM Calculate time difference (Windows 10/11 compatible)
set /a "start_total_secs=!start_hour!*3600+!start_min!*60+!start_sec!"
set /a "end_total_secs=!end_hour!*3600+!end_min!*60+!end_sec!"

REM Handle day wrap-around
if !end_total_secs! lss !start_total_secs! (
    set /a "end_total_secs+=86400"
)

set /a "total_diff=!end_total_secs!-!start_total_secs!"
set /a "hour_diff=!total_diff!/3600"
set /a "min_diff=(!total_diff!%%3600)/60"
set /a "sec_diff=!total_diff!%%60"

echo  Elapsed time: !hour_diff!h !min_diff!m !sec_diff!s
echo ========================================
echo.

REM Ask if user wants to continue with another directory
echo.
set /p continue="Process another directory? (y/n): "
if /i "!continue!"=="y" goto :main_loop
if /i "!continue!"=="yes" goto :main_loop

:exit_program
echo.
echo Thank you for using Audio File Text Converter!
echo.
pause 