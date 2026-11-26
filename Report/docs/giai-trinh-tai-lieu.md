# Giải trình tài liệu tham khảo

Danh sách tài liệu tham khảo đã được tinh gọn xuống còn **11 nguồn cốt lõi** (từ 31 nguồn ban đầu $\to$ 17 $\to$ 20 $\to$ **11 nguồn**). Mọi nguồn trong `sections/08-tai-lieu.tex` đều được trích dẫn (`\cite`) trực tiếp trong báo cáo — không có nguồn thừa hay trích dẫn lướt.

## 1. Nguồn trực tiếp của báo cáo (3 nguồn)

| STT | Nguồn | Nội dung | Trích dẫn ở đâu |
|---:|---|---|---|
| `[1]` | Diehl, Nader, Gupta (2026) — LLM-HPC++ | Bài báo gốc: số liệu, bảng lỗi, kết quả scaling | Phần 1, 2, 3, 4 (xuyên suốt) |
| `[2]` | Diehl, Brandt, Kaiser (2024) — *Parallel C++* | Mã con người dùng làm mốc so sánh hiệu năng (`Human [5]`) | Phần 1.1, Phần 4.8 |
| `[3]` | Diehl, Brandt, Kaiser (2023) — Shared Memory Parallelism in Modern C++ | Dòng thời gian các tính năng song song của chuẩn C++ (Hình 2) | Phần 1.1, Phần 2.2 |

## 2. Công trình liên quan tiêu biểu (4 nguồn — Mục 2.6)

Giữ lại 4 công trình đại diện sát nhất cho 4 hướng nghiên cứu (phân tích mã HPC, hoàn thành mã đa mô hình, chuyên OpenMP, chuyên MPI) để làm rõ khoảng trống của bài báo gốc:

| STT | Nguồn | Phạm vi công trình | Lý do giữ lại |
|---:|---|---|---|
| `[4]` | LLM4HPC (2023) | Khung HPC đầu tiên: phân tích mã, phát hiện song song, hỏi đáp OpenMP | Đại diện hướng phân tích, chưa đo mở rộng |
| `[5]` | HPC-Coder-v2 (2025) | Hoàn thành mã OpenMP/MPI/CUDA & ngôn ngữ song song ít tài nguyên | Đại diện mới nhất cho hướng hoàn thành mã (thay bản v1) |
| `[6]` | OMPGPT (2024) | Sinh mã OpenMP | Trực tiếp liên quan biến thể OpenMP |
| `[7]` | MPIRigen (2024) | Sinh mã MPI | Trực tiếp liên quan biến thể MPI |

## 3. Nguồn phương pháp đo (1 nguồn)

| STT | Nguồn | Nội dung | Trích dẫn ở đâu |
|---:|---|---|---|
| `[8]` | Boehm (1984) | Mô hình ước lượng chi phí/công sức phần mềm COCOMO (nền tảng công cụ `scc` và Hình 4) | Phần 3.5.2 |

## 4. Công trình cập nhật cuối năm 2026 (3 nguồn — Mục 2.7 & 6.3.3)

Được chọn lọc và kiểm chứng từ `Report/docs/nghien-cuu-bai-moi-hon.md` để bổ sung bối cảnh mô hình mới (open-weight chạy local và tái lập không cần khóa API):

| STT | Nguồn | Phạm vi công trình | Lý do giữ lại |
|---:|---|---|---|
| `[9]` | Bantel et al. (11/2026, `arXiv:2611.19105`) | 5 mô hình trọng số mở chạy local theo quy trình agentic trên 7 kernel × 4 khung task-based, đo strong scaling tới 64 luồng | Bằng chứng mới nhất về open-weight local và xác nhận cảnh báo "đúng chức năng chưa chắc song song thật" |
| `[10]` | Cui et al. — HPC-Bench (11/2026, `arXiv:2611.02752`, NeurIPS 2026) | 114 workload / 16 motif HPC (tuần tự, OpenMP, CUDA), chỉ số `Fast@k`/`Speedup@k`, phát hành sẵn candidate | Giải quyết bài toán tái lập không cần API và minh họa đánh giá đa bài toán |
| `[11]` | Nogueira et al. (ERAD-RS 2026, DOI `10.5753/eradrs.2026.20521`) | 5 kernel PolyBench/C với GCC 13.3 `-O3 -fopenmp` (64 luồng), so sánh open-weight vs đóng vs thủ công vs PoLLy | Gần toolchain GCC + OpenMP của báo cáo nhất, có bảng tăng tốc cụ thể |

## 5. Các nguồn đã lược bỏ

- **Đợt 1 (14 nguồn không được trích dẫn từ danh sách 31 nguồn gốc):** `chen2024landscape`, `lei2023dataset`, `godoy2023codex`, `valero2023llama`, `godoy2024evaluation`, `chen2021evaluating`, `miller2018cocomo`, `mandelbrot2004`, `drakopoulos2003`, `robey2021`, `diaz2012`, `lin2022isocpp`, `belson2020coroutines`, `kang2015`.
- **Đợt 2 (9 nguồn trích lướt / trùng vai trò khi tinh gọn 20 $\to$ 11):**
  - 5 nguồn trong Bảng 2.6: `munley2024llm4vv` (OpenACC), `ding2023hpcgpt` (quản lý AI/data), `nichols2024hpccoder` (trùng dòng với bản v2), `kadosh2023tokompiler` (trùng hướng hoàn thành mã), `yin2025chathpc` (chatbot script).
  - 4 nguồn nền tảng chỉ trích 1 câu: `achiam2023gpt4`, `touvron2023llama` (chỉ gắn tên mô hình và thiếu GPT-5/Claude), `brooks1980` (định nghĩa tập Mandelbrot kinh điển), `gropp1999` (giáo trình MPI kinh điển).
