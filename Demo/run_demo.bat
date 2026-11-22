@echo off
chcp 65001 >nul
cd /d %~dp0mandelbrot

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
