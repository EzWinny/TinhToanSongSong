# Nhật ký đánh giá mô hình `gemini`

- **Ngày sinh mã:** 2026-11-26
- **Phiên bản / nguồn mô hình:** Gemini 4 Hydrogen (Effort: High)
- **Cách sinh:** 1 lần sinh duy nhất cho mỗi biến thể, mỗi prompt gửi ở một phiên chat mới hoàn toàn trống (zero-shot, nguyên văn prompt từ Phần 3.3 của báo cáo).
- **Môi trường kiểm thử cục bộ:** Windows 11, CPU 12 luồng logic, MinGW-W64 GCC 13.2.0 (`E:\Strawberry\c\bin\g++.exe`), không cài Intel TBB và không có MPI.

## Kết quả chạy nguyên bản (`raw/` — không cần sửa dòng nào)

| Biến thể | LOC | Biên dịch (`-Wall -Wextra`) | Thực thi | Ảnh P4 | Thời gian (`-t 1` → `-t 12`) | Speedup (`-t 12 / -t 1`) | Ghi chú kỹ thuật |
|---|---:|---|---|---|---|---:|---|
| `async.cpp` | 133 | ✓ (0 cảnh báo) | ✓ | ✓ (1920×1080) | `1,311 s` → `0,129 s` | **10,16×** | `std::launch::async` + hàng đợi động `std::atomic<int> next_row`, giữ tỉ lệ khung hình |
| `par_algo.cpp` | 163 | ✓ (0 cảnh báo)* | ✓ (tuần tự không TBB) | ✓ (1920×1080) | `0,071 s` → `0,070 s`* | 1,02×* | Dùng `__has_include(<tbb/global_control.h>)` + `tbb::global_control` (fallback ConcRT / in cảnh báo rõ ràng khi thiếu TBB); có tối ưu bỏ qua hình tim + bóng chu kỳ 2 |
| `coroutine.cpp` | 205 | ✓ (0 cảnh báo) | ✓ | ✓ (1920×1080) | `1,144 s` → `0,113 s` | **10,11×** | Tự xây `ThreadPool` (`std::jthread`), `co_await pool.schedule()`, đồng bộ bằng `std::latch`, không dùng vòng lặp chờ `.done()` nên tránh triệt để lỗi treo/UB |
| `openmp.cpp` | 100 | ✓ (0 cảnh báo) | ✓ | ✓ (2048×2048) | `1,492 s` → `0,157 s` | **9,53×** | `omp_set_num_threads` + `num_threads` + `schedule(dynamic, 1)`; lưu ý nhỏ: dùng `std::fill` mà thiếu `#include <algorithm>` (GCC 13.2 kéo gián tiếp qua header khác, có thể cần thêm ở trình biên dịch chặt hơn) |
| `mpi_omp.cpp` | 199 | *(chưa biên dịch — thiếu MPI)* | *(kiểm duyệt tĩnh)* | — | — | — | Dùng `MPI_Init_thread(MPI_THREAD_FUNNELED)`, phân vùng block-cyclic theo `-p`, `MPI_Gatherv`, đặt `MPI_Barrier` + `MPI_Wtime()` sau gather và loại I/O |

*\*Lưu ý `par_algo.cpp`:* biên dịch sạch không lỗi/cảnh báo ngay cả khi máy cục bộ thiếu Intel TBB, nhưng libstdc++ rơi về thực thi tuần tự và chương trình tự in cảnh báo `"Warning: No TBB or ConcRT backend detected; -t may be ignored."`. Thời gian đơn luồng rất nhanh (`~71 ms`) nhờ cắt tỉa toán học hình tim chính và bóng chu kỳ 2.

## Nhật ký sửa lỗi tối thiểu (`raw/` -> `fixed/`)

Không phát sinh lỗi biên dịch, lỗi thực thi hay lỗi ảnh nào trên các biến thể chạy được tại môi trường cục bộ → không cần tạo bản sửa trong `fixed/`.
