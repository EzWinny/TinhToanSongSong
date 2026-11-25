# Tìm kiếm bài báo mới hơn (cuối 2025–2026) về đánh giá LLM sinh mã HPC song song

> Ghi chú phục vụ mục `2.7 Bối cảnh mô hình hiện nay và hướng bổ sung`.
> Mọi thông tin dưới đây đều được **kiểm chứng bằng cách truy xuất trực tiếp nguồn gốc**
> (trang arXiv, trang proceedings, README GitHub). Các con số được chép từ bảng/hình
> trong chính bài báo hoặc README kho mã, không suy diễn từ blog hay bảng xếp hạng.
> Ngày kiểm chứng: 24/11/2026.

---

## 1. Câu trả lời tóm tắt

**Có — và khá nhiều.** Kết luận hiện tại trong mục 2.7 rằng "báo cáo không có số liệu
cho các mô hình mới; muốn bổ sung thì phải có API key" **vẫn đúng với riêng báo cáo này**,
nhưng **không còn đúng với toàn bộ lĩnh vực**: đã có công trình công bố số liệu đo trên
nhiều mô hình **trọng số mở chạy local**, nhiều bài toán, có đo scaling, và — quan trọng
nhất — **công bố cả mã sinh ra lẫn bảng kết quả thô** để người khác tái lập mà không cần
gọi API trả phí.

Ba hướng lấp khoảng trống rõ rệt nhất:

1. **Nhiều mô hình trọng số mở, chạy hoàn toàn local, tự biên dịch/chạy, đo strong scaling**
   — Bantel et al., arXiv:2611.19105 (11/2026), 5 mô hình open-weight, 7 kernel × 4 khung
   OpenMP/HPX/StarPU/TTG, công bố pass@1, PCGQS và thời gian chạy cụ thể.
2. **Bộ benchmark lớn kèm dữ liệu kết quả phát hành công khai** — HPC-Bench,
   arXiv:2611.02752 (11/2026, NeurIPS 2026). README nói rõ: *"The candidates used in the
   paper are included in the repository, so the evaluation can be reproduced without
   API access."* Đây là câu trả lời trực tiếp cho lo ngại "cần API key".
3. **Nhiều mô hình trọng số mở trên đúng toolchain GCC + OpenMP của báo cáo** — Nogueira
   et al., ERAD-RS 2026, DOI 10.5753/eradrs.2026.20521 (06/05/2026), có bảng speedup
   số học cho Qwen, CodeLlama, DeepSeek Coder, Codestral, Granite Code.

Ngoài ra còn các ứng viên bổ trợ: Bantel et al. 2602.22240 (Qwen-Coder 3 30B, kết hợp
pass@1 + strong/weak scaling), ParCoder (IPDPSW 2026, OpenMP **và MPI**, baseline
CodeLlama/StarCoder/DeepSeek-Coder), ReGraphT (arXiv:2510.19873, CUDA, SLM trọng số mở),
ParBench (arXiv:2607.22588), và một nghiên cứu Julia agentic (arXiv:2606.16534).

---

## 2. Bảng so sánh các ứng viên đã kiểm chứng

| Công trình (nguồn) | Ngày / nơi công bố | Mô hình được đo (⚠ = trọng số mở) | Phương pháp đánh giá | Có số liệu công bố trích được không? | Mức độ khớp với khoảng trống của báo cáo |
|---|---|---|---|---|---|
| **Can Agentic LLMs Write Task-Based Parallel Code? A Study of OpenMP Tasking, HPX, StarPU and TTG** — Bantel, Roth, Thüring, Posner, Pflüger. [arXiv:2611.19105](https://arxiv.org/abs/2611.19105) · [full text](https://arxiv.org/html/2611.19105v1) | Nộp 14/11/2026; "Will be published at WAMTA2027" | 5 mô hình, **tất cả open-weight, tự host bằng llama.cpp trên 4×V100 32GB**: ⚠Qwen3.8-27B (`Qwen3.8-27B`, Q4_K_M), ⚠Ornith-1.5-35B (Q4_K_M), ⚠Nemotron-3-Nano-30B-A3B (IQ4_XS), ⚠NVIDIA-Nemotron-3-Nano-4B (Q8_0), ⚠Qwen3.6-35B | **Agentic** (dùng `opencode` 1.18.31, công cụ chuẩn), 7 kernel (π, AXPY, GEMV, GEMM, Cholesky, LU, solve) × bản tuần tự + 4 khung (OpenMP Tasking, HPX, StarPU, TTG) = 175 kernel. Độ đúng tại p∈{1,2,4,8,16,32,64}, strong scaling, peak RSS; pass@1 + điểm PCGQS. GCC 13.3.0, 2×EPYC 7542 | **Có, rất chi tiết.** 30/35, 29/35, 29/35 kernel đúng cho 3 mô hình đầu (còn 6 và 0 cho 2 mô hình Nemotron); PCGQS 0.67/0.64/0.43/0.08/0.00; tăng tốc π 48–61× ở 64 luồng; GEMM+factorization trung vị 10.2×; kernel tốt nhất thắng OpenBLAS (GEMM 0,159 s so với 0,176 s; Cholesky 0,246 so với 0,322; LU 0,604 so với 0,753). Có Bảng 1 phân loại 42 lỗi | **Rất cao**: mới hơn LLM-HPC++, toàn bộ là open-weight local, đa bài toán, có scaling, không cần API |
| **HPC-Bench: A Comprehensive Benchmark for High Performance Computing Codes** — Cui, Yin, Ramesh, Lim, Hernandez, Zhou. [arXiv:2611.02752](https://arxiv.org/abs/2611.02752) · [GitHub](https://github.com/Deep-Learning-Profiling-Tools/HPC-Bench) | Nộp 02/11/2026; **NeurIPS 2026 Evaluations & Datasets Track (poster)** | GPT-5.1, Claude Sonnet 4.5, ⚠Qwen3-Coder-480B-A35B-Instruct | 114 workload / 16 motif (92 CPU + 22 CUDA). EX1 tuần tự, **EX2 OpenMP** (`OMP_NUM_THREADS` = 1,2,8,16,32, cấm hard-code số luồng), EX3 CUDA. N=10 mẫu mỗi workload; chỉ số **Fast@k / Speedup@k** có kiểm soát đúng đắn, k=3, ngưỡng p_thr=1.0/1.5. EPYC 7543, GCC 14.2, A100/CUDA 12.4 | **Có, kèm dữ liệu thô.** Bảng README: EX2 Fast@3 (Claude/GPT/Qwen) 0,35/0,36/0,27; Speedup@3 2,70×/2,72×/1,67× ở p_thr=1.0. Tỉ lệ đúng 76,9% (EX1), 61,4% (EX2), 38,8% (EX3). Kho chứa `final_data/unified_results.csv` + 30 candidate đã sinh; README khẳng định tái lập **không cần API** | **Rất cao**: trực tiếp giải quyết "không muốn gọi API trả phí"; phương pháp đo khác (Fast@k/Speedup@k) nên cần nhắc không so trực tiếp số với báo cáo |
| **Avaliação de Modelos de Linguagem de Grande Escala na Geração Automática de Código Paralelo OpenMP** — Nogueira, Kawamoto, Fabrício Filho, Gonçalves (UTFPR). [DOI 10.5753/eradrs.2026.20521](https://doi.org/10.5753/eradrs.2026.20521) · [trang SBC](https://sol.sbc.org.br/index.php/eradrs/article/view/42728) | 06/05/2026, Anais XXVI ERAD-RS, Bagé/RS, tr. 169–172 | ⚠CodeLlama, ⚠Codestral, ⚠DeepSeek Coder, ⚠Granite Code, ⚠Qwen; Gemini 3 và ChatGPT 4.5 (đóng) | Zero-shot, 5 kernel PolyBench/C 4.2.1 (2mm, 3mm, gemm, atax, syr2k); so sánh 3 paradigm: chuyên gia viết tay / PoLLy-DawnCC / LLM. GCC 13.3 `-O3 -fopenmp`, Threadripper 7970X (64 thread), trung bình 10 lần chạy; tập Standard và Large | **Có, Bảng 1.** ChatGPT 4.5 38,77× (hiệu suất 0,61), Gemini 3 35,56× (0,56), OpenMP thủ công 31,98× (0,50), Codestral 30,06× (0,47), **Qwen 28,96× (0,45)**, PoLLy 18,24× (0,28), **CodeLlama 11,05× (0,17)**. syr2k/Large: thủ công 23,98×, PoLLy 59,32×; gemm/Standard: ChatGPT 51,81×. Công bố artifact | **Cao**: đúng C++/OpenMP/GCC như báo cáo; có Qwen/CodeLlama/DeepSeek Coder; đo speedup. Nhược: 4 trang, một prompt, không MPI |
| **From Prompts to Performance: Evaluating LLMs for Task-based Parallel Code Generation** — Bantel, M. Strack, A. Strack, Pflüger. [arXiv:2602.22240](https://arxiv.org/abs/2602.22240) · [full text](https://arxiv.org/html/2602.22240v1) | Nộp 24/02/2026; WAMTA 2026; in trong *Asynchronous Many-Task Systems and Applications*, tr. 15–26 | ChatGPT-5, ⚠**Qwen-Coder 3 (30B)** = `Qwen/Qwen3-Coder-30B-A3B-Instruct`, Gemini-3 | 4 bài (π, merge sort, GEMM, CG) × 3 dạng prompt (mô tả / mã tuần tự / giả mã song song) × 3 khung (OpenMP Tasking, C++ standard parallelism, HPX); pass@1 theo 4 mức sửa lỗi, `scc`, **PCGQS** = ½C(c)+½S(c) với cả strong lẫn weak scaling tới 128 luồng. EPYC 7742, GCC 13.3.0 | **Có.** Bảng 2 PCGQS: ChatGPT 0,7425; Gemini 0,7008; **Qwen 0,5702**. Bảng 1 số liệu độ phức tạp. Hình 3–4 scaling (dạng biểu đồ) | **Khá**: tiền nhiệm trực tiếp của 2611.19105; có open-weight Qwen-Coder 30B, đa bài toán + scaling. Ngày (02/2026) hơi trước bản v2 của LLM-HPC++ |
| **ParCoder: Harnessing Transformer Models for Parallel Code Generation with OpenMP and MPI** — Chen, Bhattacharjee, Ahmed, Hasabnis, Capotă, Munoz, Oren, Vo, Chapman, Jannesari. [DOI 10.1109/IPDPSW71298.2026.00034](https://doi.org/10.1109/IPDPSW71298.2026.00034) · [PDF](https://swapp.cs.iastate.edu/files/inline-files/ParCoder_Harnessing_Transformer_Models_for_Parallel_Code_Generation_with_OpenMP_and_MPI.pdf) | IPDPSW 2026, New Orleans, 25–29/05/2026, tr. 216–225 | Mô hình đề xuất ⚠ParCoder 1,7B (kiến trúc Llama); baseline ⚠CodeLlama, ⚠StarCoder, ⚠DeepSeek-Coder, GPT-4 | Fill-in-the-middle cho **OpenMP và MPI**, huấn luyện 19,8B token; đánh giá trên PolyBench + ParEval bằng CompCheck/ExecCheck/CorrectCheck/**SpeedupCheck**, k=1,5,10 | **Có.** Bảng III tăng tốc tuyệt đối trung bình (8 luồng): CodeLlama 1,82×; StarCoder 0,24×; DeepSeek-Coder 1,82×; ParCoder 2,29×. Bảng II SpeedupCheck pass@1: 58,3% / 66,6% / 76,4% | **Khá–cao**: là một trong ít công trình 2026 có **MPI** + baseline trọng số mở. Nhược: là bài về mô hình chuyên biệt, sinh kiểu điền chỗ trống chứ không sinh từ đầu |
| **From Large to Small: Transferring CUDA Optimization Expertise via Reasoning Graph (ReGraphT)** — Gong, Wei, Chen, Liu, Li. [arXiv:2510.19873](https://arxiv.org/abs/2510.19873) · [full text](https://arxiv.org/html/2510.19873) | Nộp 22/10/2025 | ⚠DeepSeek-Coder-V2-Lite-Instruct, ⚠Qwen2.5-Coder-7B-Instruct, ⚠HPC-Coder-V2; đối chiếu ⚠DeepSeek-V3-0324, ⚠DeepSeek-R1 | CUDA từ mã tuần tự; CUDAEval (313 task, 106 easy/105 medium/102 hard) + ParEval (60 task CUDA); pass@k, **speedup@k**; vLLM BF16 trên A100-80GB | **Có, Bảng 1 & 2.** Ví dụ CUDAEval pass@1/speedup@1: DeepSeek-Coder-V2-Lite + ReGraphT-MCGS 75,1 / 14,46; Qwen2.5-Coder-7B 72,2 / 14,31; HPC-Coder-V2 72,5 / 14,39; DeepSeek-R1 CoT 82,1 / 19,14 | **Trung bình**: chứng minh SLM trọng số mở cải thiện được bằng phương pháp không huấn luyện, nhưng **chỉ CUDA**, không OpenMP/MPI |
| **Generated, Parallel, Scalable? A Study of Agentic AI-Generated Julia Code on Supercomputers** — Bantel, Roth, Posner, Pflüger. [arXiv:2606.16534](https://arxiv.org/abs/2606.16534) | Nộp 15/06/2026, sửa 16/06/2026 | GPT-5.5, Claude Opus 4.7, ⚠**Qwen3-Coder-Next** | Agentic (OpenCode + MCP tài liệu Julia), 3 bài (π, GEMM khối, Cholesky khối); Dagger.jl so với Base.Threads và MPI.jl; tới **192 lõi** và 2 nút | Abstract công bố kết quả dạng nhận định (chạy được ở input nhỏ, fail ở quy mô lớn do deadlock/oversubscription/OOM; mô hình open-weight chịu ảnh hưởng nặng nhất). **Tôi chỉ kiểm chứng abstract, chưa kiểm chứng bảng số cụ thể** | **Trung bình**: bằng chứng bổ trợ cho nhận định "trọng số mở yếu hơn ở quy mô lớn"; nhưng Julia, không phải C++ |
| **ParBench: A Benchmark for Reliable Evaluation of LLM Parallel Code Translation** — Jhaveri, Kaplan, Yotam, Chen, Bitan, Hasabnis, Oren. [arXiv:2607.22588](https://arxiv.org/abs/2607.22588) · [GitHub](https://github.com/Scientific-Computing-Lab/ParBench) | Nộp 09/06/2026; repo ghi NeurIPS 2026 | Abstract chỉ ghi "state-of-the-art open and proprietary LLMs"; README/repo ghi **3 mô hình** nhưng **không nêu tên trong phần tôi truy xuất được → không xác minh được tên cụ thể** | Dịch kernel giữa CUDA, OpenMP, OpenCL, OpenMP target offload; 96 spec tuyển chọn, 87 đủ điều kiện, 136 cặp dịch; augment nguồn do AST dẫn dắt để chống học thuộc; pass@k, bảng phân loại lỗi | **Có.** `results/analysis/final/` chứa 2.160 bản ghi hợp lệ kèm mọi số trong bài; artifact `parbench-artifact-neurips2026.zip` | **Trung bình**: tốt cho "phương pháp đo" và dữ liệu công khai, nhưng là **dịch API**, không phải sinh mã từ đầu |

### Một ứng viên cần đính chính thông tin ngày

- [arXiv:2504.03665](https://arxiv.org/abs/2504.03665) *"LLM & HPC: Benchmarking DeepSeek's
  Performance in High-Performance Computing Tasks"* (Nader, Diehl, Brandt, Kaiser) thực chất
  nộp **15/03/2025**, sửa lần cuối **28/04/2025** (đăng trong LNCS, DOI
  10.1007/978-3-032-07612-0_48) — **không phải 2026** như một số kết quả tìm kiếm ghi.
  Nội dung vẫn hữu ích: ⚠DeepSeek so với GPT-4 trên CG, heat equation, matmul, DGEMM,
  STREAM triad bằng C++/Fortran/Julia/Python, có đo correctness/performance/scaling và 3 bảng.
  Nếu trích dẫn, phải ghi đúng ngày 2025 và coi đây là công trình **cùng thế hệ hoặc cũ hơn**
  LLM-HPC++, không phải "mới hơn".

---

## 3. Kết luận: nên trích 1–3 công trình nào trong mục 2.7

### Ưu tiên 1 — Bantel et al., arXiv:2611.19105 (11/2026)

**Cách dùng:** thay/ bổ sung câu cuối đoạn 2.7 ("báo cáo không có số liệu cho các mô hình
mới…") bằng một câu dạng: *đã có công trình độc lập (Bantel et al., 2026) đo năm mô hình
trọng số mở chạy local trên bảy kernel HPC và bốn khung task-based, công bố pass@1, PCGQS
và tăng tốc thực đo — tức là khoảng trống "nhiều LLM cùng bài toán" đã bắt đầu được lấp,
dù chưa có ai lặp lại đúng thiết kế Mandelbrot P1/P2/P3 của báo cáo này*.

**Lý do:** mới nhất, toàn bộ open-weight, có agentic loop (liên quan trực tiếp đến nhận xét
"nên lặp nhiều lần sinh"), có cả số liệu lẫn lời giải thích tại sao "đúng" chưa đủ
(một số kernel gọi là song song thực ra chạy tuần tự) — rất khớp với cách mục 2.7 đang
phân biệt "bài toán đơn đo sâu" và "bộ nhiều bài toán đo khái quát".

**URL:** <https://arxiv.org/abs/2611.19105> · <https://arxiv.org/html/2611.19105v1>

### Ưu tiên 2 — HPC-Bench, arXiv:2611.02752 (11/2026, NeurIPS 2026)

**Cách dùng:** trích ngay vào câu về "đòi hỏi API key". Viết đại loại: *một nhược điểm thường
thấy là cần khóa API, nhưng HPC-Bench đã công bố toàn bộ 30 candidate đã sinh cùng bảng
kết quả thô (`final_data/unified_results.csv`), cho phép tái lập phép đo mà không gọi API*.
Đồng thời thêm một câu cảnh báo (đúng với tinh thần đoạn 2.7 hiện tại): Fast@k/Speedup@k
và N=10 mẫu là **phân phối**, không so trực tiếp được với tỉ lệ biên dịch của báo cáo.

**Lý do:** đây là nguồn duy nhất trong danh sách khẳng định rõ ràng bằng văn bản rằng việc
đánh giá có thể lặp lại **without API access** — đáp ứng đúng câu hỏi của người dùng.

**URL:** <https://arxiv.org/abs/2611.02752> · <https://github.com/Deep-Learning-Profiling-Tools/HPC-Bench>

### Ưu tiên 3 — Nogueira et al., ERAD-RS 2026 (DOI 10.5753/eradrs.2026.20521)

**Cách dùng:** dùng Bảng 1 của họ làm ví dụ số cụ thể cho câu "có sẵn số liệu công bố".
Có thể viết: *trên PolyBench/C với GCC 13.3 và `-O3 -fopenmp`, Qwen (trọng số mở) đạt
speedup trung bình 28,96× so với 31,98× của bản thủ công, trong khi CodeLlama chỉ 11,05×
và PoLLy 18,24×*. Đây là con số dễ đối chiếu với báo cáo vì cùng dùng OpenMP/GCC/speedup.

**Lý do:** gần toolchain của báo cáo nhất, có nhiều mô hình open-weight cùng bảng, và là
bài proceedings có DOI ổn định (dễ thêm `\bibitem`).

**URL:** <https://doi.org/10.5753/eradrs.2026.20521> · <https://sol.sbc.org.br/index.php/eradrs/article/view/42728>

> **Nếu chỉ được trích một bài:** chọn arXiv:2611.19105. Nếu mục tiêu đặc biệt là phản biện
> câu "cần API key": chọn HPC-Bench.

---

## 4. Cách kết nối với các bảng hiện có của báo cáo (không cần sửa định nghĩa tiêu chí)

- Các bài trên **đều dùng nhiều bài toán**, đúng với gợi ý cuối đoạn 2.7: *"trước tiên sàng
  nhiều bài toán để tìm mô hình tốt, sau đó mới đo sâu scaling trên một bài đại diện như
  Mandelbrot"*. Có thể trích chúng làm bằng chứng rằng thiết kế hai lớp này đã được áp dụng.
- **Không có bài nào** trong danh sách đo đúng bài Mandelbrot với ba prompt P1/P2/P3 và
  năm biến thể như báo cáo. Vì vậy kết luận của báo cáo về GPT/Claude/LLaMA vẫn là đóng góp
  riêng của nó; các bài mới bổ sung **bối cảnh**, không thay thế số liệu.
- Các chỉ số khác nhau cần được giữ nguyên tên khi trích: `pass@1` (2602.22240, 2611.19105),
  `PCGQS` (2602.22240, 2611.19105), `Fast@k`/`Speedup@k` (HPC-Bench), `speedup@k`
  (ReGraphT), `CompCheck/ExecCheck/CorrectCheck/SpeedupCheck` (ParCoder).

---

## 5. Danh sách nguồn đã thực sự truy xuất

| Mục đích | URL |
|---|---|
| Xác nhận tiêu đề/tác giả/ngày 2611.19105 | <https://arxiv.org/abs/2611.19105> |
| Xác nhận mô hình, 175 kernel, bảng lỗi, PCGQS, thời gian chạy | <https://arxiv.org/html/2611.19105v1> |
| Xác nhận tiêu đề/tác giả/ngày HPC-Bench | <https://arxiv.org/abs/2611.02752> |
| Xác nhận bảng Fast@3/Speedup@3 và câu "reproduced without API access" | <https://github.com/Deep-Learning-Profiling-Tools/HPC-Bench> |
| Xác nhận tiêu đề/tác giả/ngày 2602.22240 | <https://arxiv.org/abs/2602.22240> |
| Xác nhận Qwen-Coder 3 30B, PCGQS 0,7425/0,7008/0,5702 | <https://arxiv.org/html/2602.22240v1> |
| Xác nhận ERAD-RS 2026, tác giả, DOI, trang, Bảng 1 | <https://doi.org/10.5753/eradrs.2026.20521> và <https://sol.sbc.org.br/index.php/eradrs/article/view/42728> |
| Xác nhận ParCoder (IPDPSW 2026, DOI, Bảng II/III) | <https://doi.org/10.1109/IPDPSW71298.2026.00034> và <https://swapp.cs.iastate.edu/files/inline-files/ParCoder_Harnessing_Transformer_Models_for_Parallel_Code_Generation_with_OpenMP_and_MPI.pdf> |
| Xác nhận ReGraphT (ngày, mô hình, Bảng 1/2) | <https://arxiv.org/abs/2510.19873> và <https://arxiv.org/html/2510.19873> |
| Xác nhận 2606.16534 (mô hình, 192 lõi, 2 nút) | <https://arxiv.org/abs/2606.16534> |
| Xác nhận ParBench (ngày, 136 cặp dịch, 2.160 bản ghi) | <https://arxiv.org/abs/2607.22588> và <https://github.com/Scientific-Computing-Lab/ParBench> |
| Đính chính ngày arXiv:2504.03665 (v1 15/03/2025, v2 28/04/2025) | <https://arxiv.org/abs/2504.03665> |

---

## 6. Giới hạn của lần tìm kiếm này

- Không kiểm chứng được **tên cụ thể của 3 mô hình** trong ParBench: abstract chỉ nói
  "open and proprietary", README chỉ nói "three models". Không nên đoán.
- Với arXiv:2606.16534 (Julia) tôi mới đọc abstract; chưa mở full text để chép bảng số.
- Không tra cứu IEEE Xplore ở chế độ đăng nhập (bài ParCoder bị chặn paywall); đã dùng
  PDF công khai của Iowa State và trang DOI/proceedings để kiểm chứng.
- Phạm vi find: arXiv, proceedings ACM/IEEE/SBC, README GitHub. Không dùng blog,
  leaderboard hay bài liệt kê làm bằng chứng.
- Không chỉnh sửa file `.tex` nào, không commit/push.
