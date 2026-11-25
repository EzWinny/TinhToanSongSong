@echo off
chcp 65001 >nul
cd /d %~dp0mandelbrot

REM Uu tien MinGW-W64 ho tro OpenMP neu g++ mac dinh la MinGW 32-bit cu
if exist "E:\Strawberry\c\bin\g++.exe" set "PATH=E:\Strawberry\c\bin;%PATH%"
if exist "C:\msys64\ucrt64\bin\g++.exe" set "PATH=C:\msys64\ucrt64\bin;%PATH%"
if exist "C:\msys64\mingw64\bin\g++.exe" set "PATH=C:\msys64\mingw64\bin;%PATH%"

echo Dang bien dich...
g++ -O2 -std=c++17 -fopenmp -Wall mandel_seq.cpp -o mandel_seq.exe || exit /b 1
g++ -O2 -std=c++17 -fopenmp -Wall mandel_omp.cpp -o mandel_omp.exe || exit /b 1

> results.txt (
  echo === Ban tuan tu ===
  mandel_seq.exe -t 1 -w 800 -h 600 -i 300
  echo.
  echo === OpenMP theo so luong ===
  for %%T in (1 2 4 8 16) do mandel_omp.exe -t %%T -w 800 -h 600 -i 300
)
type results.txt

echo.
echo === Ve bieu do ===
cd /d %~dp0
python plot_speedup.py mandelbrot\results.txt

echo.
echo Da xong. Nhan phim bat ky de dong cua so...
pause >nul
