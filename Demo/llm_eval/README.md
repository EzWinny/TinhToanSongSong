# Đánh giá bổ sung LLM hiện đại (môi trường cục bộ)

Thư mục này dùng để chạy thử nghiệm kiểm chứng trên một (hoặc nhiều) mô hình LLM hiện đại theo đúng bộ prompt và quy trình kiểm định của bài báo gốc *LLM-HPC++* (Phần 3.3–3.4 trong báo cáo), nhưng tách biệt rõ môi trường cục bộ (Windows + MinGW-W64 GCC) với cụm Linux `rostam` của bài báo gốc.

## 1. Khởi tạo thư mục cho mô hình mới

Từ thư mục `Demo/`, chạy:

```powershell
python eval_llm.py --init gemini-4
```

Lệnh này tạo sẵn cấu trúc:

```text
Demo/llm_eval/gemini-4/
├── raw/        # Lưu NGUYÊN BẢN mã lần sinh đầu tiên (chưa sửa gì)
├── fixed/      # (Nếu cần) Bản sửa tối thiểu để chạy được
└── notes.md    # Nhật ký lỗi, dòng sửa và thông tin phiên bản mô hình
```

## 2. Nguyên văn 5 prompt (mỗi biến thể 1 phiên chat mới)

Gửi đúng từng prompt sau (trích nguyên văn từ Phần 3.3 của báo cáo) trong **một cuộc hội thoại mới** (không kèm ngữ cảnh trước), rồi lưu đoạn mã C++ duy nhất mà mô hình sinh ra vào đúng tên tệp trong `raw/`:

| Tệp trong `raw/` | Biến thể | Prompt nguyên văn |
|---|---|---|
| `async.cpp` | C++11 bất đồng bộ | `Write a parallel code for the Mandelbrot set using C++ 11 async future and write the output to the PBM format. Make the number of threads configurable with the command line option -t and print the runtime excluding IO.` |
| `par_algo.cpp` | C++17 thuật toán song song | `Write a parallel code for the Mandelbrot set using C++ 17 parallel algorithms and write the output to the PBM format. Make the number of threads configurable with the command line option -t and print the runtime excluding IO.` |
| `coroutine.cpp` | C++20 coroutine | `Write a parallel code for the Mandelbrot set using C++ 20 coroutines and write the output to the PBM format. Make the number of threads configurable with the command line option -t and print the runtime excluding IO.` |
| `openmp.cpp` | OpenMP | `Write a parallel code for the Mandelbrot set using C++ using OpenMP and write the output to the PBM format. Make the number of threads configurable with the command line option -t and print the runtime excluding IO.` |
| `mpi_omp.cpp` | MPI+OpenMP | `Write a distributed code using MPI for the Mandelbrot set and using OpenMP for parallelism in C++ and write the output to the PBM format. Make the number of partitions configurable with the command line option -p and print the runtime excluding IO.` |

*(Không bắt buộc phải có đủ cả 5 tệp cùng lúc — `eval_llm.py` tự động chấm những tệp hiện có.)*

## 3. Chạy chấm tự động & vẽ biểu đồ

```powershell
# Chấm mã nguyên bản (lần sinh đầu)
python eval_llm.py gemini-4

# Tuỳ chọn dãy số luồng / số lần lặp
python eval_llm.py gemini-4 --threads 1 2 4 8 12 --repeats 3

# Sau khi chép file lỗi sang fixed/ và sửa tối thiểu, chấm lại bản fixed
python eval_llm.py gemini-4 --stage fixed
```

## 4. Kết quả đầu ra

Mỗi lần chạy sinh các tệp trong `Demo/llm_eval/<model>/`:
- `report_<stage>.md`: bảng tổng hợp Biên dịch / Cảnh báo / Thực thi / Kiểm tra ảnh Netpbm / Speedup / Dấu hiệu bỏ qua `-t` / Kiểm duyệt tĩnh.
- `scaling_<stage>.png`: biểu đồ tăng tốc và thời gian tính so với `mandel_omp.cpp` tham chiếu trên cùng máy.
- `preview_<stage>_<variant>.png`: ảnh xem nhanh chuyển từ PBM/PGM/PPM để kiểm tra trực quan tập Mandelbrot.
- `results_<stage>.json`: toàn bộ số liệu thô, stdout, cảnh báo trình biên dịch và thông số máy.

## 5. Giới hạn môi trường cục bộ cần nêu rõ khi trích dẫn

- **Chạy đo thực tế đầy đủ:** `async.cpp`, `coroutine.cpp` (`-std=c++20`), `openmp.cpp` (`-fopenmp`).
- **TBB (`par_algo.cpp`):** nếu trình biên dịch cục bộ chưa cài Intel TBB (`<tbb/global_control.h>`), công cụ chuyển sang kiểm tra tĩnh (xem mã có dùng `tbb::global_control` hay nhầm `OMP_NUM_THREADS`) và đánh dấu `SKIPPED_NO_TBB`.
- **MPI (`mpi_omp.cpp`):** nếu máy không có `mpic++`/`mpiexec`, công cụ chỉ kiểm duyệt tĩnh theo danh mục Bảng 10 của báo cáo (`MPI_Gather`/`MPI_Gatherv`, phân vùng `-p`, mốc timer sau gather) và đánh dấu `STATIC_ONLY_NO_MPI`.
- **Nguyên tắc trình bày:** không trộn số liệu máy cục bộ vào Bảng 5 / Bảng 11 của cụm Linux `rostam` trong bài báo gốc; trình bày thành một tiểu mục thực nghiệm bổ sung riêng.
