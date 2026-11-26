# Giải trình tài liệu tham khảo

Danh sách tài liệu tham khảo ban đầu đã được rút gọn từ **31 xuống 17 nguồn**, sau đó bổ sung **3 công trình độc lập năm 2026** cho Mục 2.7 (tổng cộng **20 nguồn**). Tất cả 20 nguồn đều được trích dẫn (`\cite`) trong báo cáo — không có nguồn "để đó cho đủ số".

## 1. Nguồn trực tiếp của báo cáo

| Nguồn | Nội dung | Trích dẫn ở đâu |
|---|---|---|
| Diehl, Nader, Gupta (2026) — LLM-HPC++ | Bài báo gốc: số liệu, bảng lỗi, kết quả scaling | Phần 1, 2, 3, 4 (xuyên suốt) |
| Diehl, Brandt, Kaiser (2024) — *Parallel C++* | Mã con người dùng làm mốc so sánh hiệu năng | Phần 1.1, Phần 4.8 |
| Diehl, Brandt, Kaiser (2023) — Shared Memory Parallelism in Modern C++ | Dòng thời gian các tính năng song song của chuẩn C++ | Phần 1.1, Phần 2.2 |

## 2. Công trình liên quan (nhóm 9 nguồn)

Tất cả được trích dẫn trong **Phần 2.6 "Công trình liên quan"**, qua bảng so sánh để làm nổi bật khoảng trống nghiên cứu: chưa có công trình nào đặt nhiều LLM cạnh nhau trên cùng một bài toán, cùng một bộ prompt, từ bộ nhớ chia sẻ đến phân tán.

| Nguồn | Phạm vi công trình | Lý do đưa vào |
|---|---|---|
| LLM4HPC (2023) | Khung HPC đầu tiên: phân tích mã, phát hiện song song, hỏi đáp OpenMP | Đại diện hướng phân tích, chưa đo mở rộng |
| LLM4VV (2024) | Sinh chỉ thị OpenACC | Chỉ một mô hình chỉ thị |
| HPC-GPT (2023) | LLaMA-13B cho quản lý mô hình/dữ liệu, phát hiện tranh chấp | Không so sánh đa mô hình lập trình |
| HPC-Coder (2024) | Hoàn thành mã OpenMP/MPI/CUDA | Bài toán hoàn thành mã, không phải sinh từ đầu |
| HPC-Coder-v2 (2025) | Mở rộng sang ngôn ngữ song song ít tài nguyên | Cập nhật mới nhất của cùng dòng công trình |
| OMPGPT (2024) | Sinh mã OpenMP | Chỉ OpenMP |
| MPIRigen (2024) | Sinh mã MPI | Chỉ MPI |
| Tokompiler (2023) | LLM miền hẹp cho Fortran/C/C++ | Tập trung hoàn thành mã |
| chatHPC (2025) | Chatbot hỏi đáp và sinh script HPC | Không đánh giá mã song song C++ |

## 3. Nguồn nền tảng kỹ thuật

| Nguồn | Nội dung | Trích dẫn ở đâu |
|---|---|---|
| Brooks & Matelski (1980) | Định nghĩa gốc tập Mandelbrot | Phần 2.1.1 |
| Gropp, Lusk, Skjellum (1999) | Mô hình SPMD và truyền thông MPI | Phần 2.4.1 |
| Achiam et al. (2023) | GPT-4 Technical Report | Phần 1.3 (khi nêu các mô hình đánh giá) |
| Touvron et al. (2023) | LLaMA: mô hình nền tảng mở | Phần 1.3 (khi nêu các mô hình đánh giá) |
| Boehm (1984) | Mô hình ước lượng chi phí COCOMO | Phần 3.5.2 |

## 4. Công trình cập nhật cuối năm 2026 (nhóm 3 nguồn — Mục 2.7 & 6.3.3)

Được chọn lọc và kiểm chứng từ `Report/docs/nghien-cuu-bai-moi-hon.md` để bổ sung bối cảnh mô hình mới (kể cả trọng số mở chạy local và tính tái lập không cần khóa API):

| Nguồn | Phạm vi công trình | Lý do đưa vào |
|---|---|---|
| Bantel et al. (11/2026, `arXiv:2611.19105`) | 5 mô hình trọng số mở chạy local theo quy trình agentic trên 7 kernel × 4 khung task-based (OpenMP Tasking, HPX, StarPU, TTG), đo strong scaling tới 64 luồng | Bổ sung bằng chứng mới nhất về open-weight local và xác nhận cảnh báo "đúng chức năng chưa chắc song song thật" |
| Cui et al. — HPC-Bench (11/2026, `arXiv:2611.02752`, NeurIPS 2026) | 114 workload / 16 motif HPC (tuần tự, OpenMP, CUDA), chỉ số `Fast@k` / `Speedup@k`, phát hành sẵn toàn bộ candidate | Trả lời trực tiếp bài toán tái lập không cần API và minh họa phương pháp đo phân phối đa bài toán |
| Nogueira et al. (ERAD-RS 2026, DOI `10.5753/eradrs.2026.20521`) | 5 kernel PolyBench/C với GCC 13.3 `-O3 -fopenmp` (64 luồng), so sánh open-weight (Qwen, Codestral, CodeLlama...) vs đóng vs thủ công vs PoLLy | Gần toolchain GCC + OpenMP của báo cáo nhất, có bảng tăng tốc cụ thể giữa các họ mô hình |

## 5. Các nguồn đã bỏ (14 nguồn)

Đây là phần lớn danh sách gốc của bài báo, nhưng **không được trích dẫn ở bất kỳ đâu** trong báo cáo nên đã loại bỏ:

`chen2024landscape`, `lei2023dataset`, `godoy2023codex`, `valero2023llama`, `godoy2024evaluation`, `chen2021evaluating`, `miller2018cocomo`, `mandelbrot2004`, `drakopoulos2003`, `robey2021`, `diaz2012`, `lin2022isocpp`, `belson2020coroutines`, `kang2015`.

Một số trong đó (Boehm/Miller, Mandelbrot, GPT-4/LLaMA) đã được thay bằng nguồn gốc tương ứng và **được trích dẫn thực tế** ở mục 3 ở trên.
