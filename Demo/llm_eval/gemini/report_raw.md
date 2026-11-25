# Kết quả đánh giá bổ sung: `gemini` (giai đoạn `raw`)

- **Thời điểm chạy:** 2026-11-26 00:49:03
- **Hệ điều hành / CPU:** Windows 11 — 12 luồng logic
- **Trình biên dịch:** `g++.exe (MinGW-W64 x86_64-ucrt-posix-seh, built by Brecht Sanders, r8) 13.2.0`
- **Hỗ trợ sẵn trên máy:** OpenMP = Có, C++20 coroutines = Có, Intel TBB = Không, MPI = Không
- **Dãy `-t` kiểm thử:** [1, 2, 4, 8, 12] (lặp 3 lần lấy trung bình)

## Tổng hợp theo biến thể

| Biến thể | Trạng thái | LOC | Biên dịch (cảnh báo) | Thực thi | Ảnh Netpbm | Speedup (-t max/-t 1) | Nghi ngờ bỏ qua -t | Ghi chú |
|---|---|---:|---|---|---|---|---|---|
| C++11 std::async | `PASS` | 133 | ✓ (0) | ✓ | ✓ (P4, 1920×1080) | 10.16× (stdout) | Không | — |
| C++17 parallel algorithms | `SKIPPED_NO_TBB` | 163 | — | — | — | — | — | Co dung tbb::global_control |
| C++20 coroutines | `PASS` | 205 | ✓ (0) | ✓ | ✓ (P4, 1920×1080) | 10.11× (stdout) | Không | — |
| OpenMP | `PASS` | 100 | ✓ (0) | ✓ | ✓ (P4, 2048×2048) | 9.53× (stdout) | Không | — |
| MPI+OpenMP | `STATIC_ONLY_NO_MPI` | 199 | — | — | — | — | — | Dung MPI_Gatherv (an toan khi H khong chia het cho P) |

## Mốc tham chiếu cục bộ (`Demo/mandelbrot/mandel_omp.cpp`, 1920×1080, 1000 vòng)

- Tuần tự: `0.4134 s`
- OpenMP `-t 1`: `0.4127 s` → `-t 12`: `0.0401 s` (tăng tốc `10.28×`)
