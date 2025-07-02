@echo off
echo Building whisper.cpp for Windows with static linking...

REM 빌드 디렉토리 생성
if exist build-for-windows rmdir /s /q build-for-windows
mkdir build-for-windows
cd build-for-windows

REM CMake 설정 (정적 링킹) Visual Studio 17 2022 필수
cmake .. -DBUILD_SHARED_LIBS=OFF -G "Visual Studio 17 2022"
cmake --build . --config Release

echo Build completed!
echo Executable location: build-for-windows\bin\whisper-cli.exe
pause 