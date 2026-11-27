# Dàn ý chia báo cáo thành 4 phần thuyết trình (20 Slide)

Tài liệu này chia toàn bộ nội dung báo cáo (`Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf`, 49–52 trang) thành **4 phần thuyết trình cân đối (~20 slide, tổng ~21–24 phút + Q&A)**, bám sát phân công 4 thành viên và liên kết thẳng tới các file chú thích chi tiết trong `Slides/notes/`.

---

## Tổng quan phân chia thời lượng & phạm vi báo cáo

| Phần thuyết trình | Slide | Thời lượng | Người trình bày (MSSV) | Phạm vi tương ứng trong báo cáo | File chú thích chi tiết |
|---|---|---|---|---|---|
| **Mở đầu chung** | 1 – 2 | ~0,5 phút | Trần Lý Dũng (`24001658`) | Trang bìa & Bảng 1 (Phân công) | — |
| **Phần 1 • Giới thiệu bài toán** | 3 – 4 | ~3–3,5 phút | Trần Lý Dũng (`24001658`) | Phần 1 (*1.1–1.6*) + Mục 2.1 (*Tập Mandelbrot*) | [`notes/01-phan-1-gioi-thieu-bai-toan.md`](notes/01-phan-1-gioi-thieu-bai-toan.md) |
| **Phần 2 • 5 mô hình, Thực nghiệm & Demo** | 5 – 10 | ~7–8 phút | Nguyễn Quang Anh (`24001649`) | Mục 2.2–2.7 (*C++ & 5 mô hình*) + Phần 3 (*3.1–3.7*) + `Demo/` | [`notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md) |
| **Phần 3 • Phân tích lỗi thực tế** | 11 – 14 | ~5–6 phút | Đồng Đức Dương (`24001659`) | Phần 4 (*4.1–4.5*) + Phần 5 (*5.1–5.5*) | [`notes/03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md) |
| **Phần 4 • Hiệu năng & tổng kết** | 15 – 20 | ~6–7 phút | Nguyễn Như Bảo (`24001655`) | Phần 4 (*4.6–4.9*) + Phần 5 (*5.6–5.7*) + Phần 6 (*6.1–6.4*) | [`notes/04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) |
| **Hỏi – Đáp (Q&A)** | 20 | ~5–10 phút | **Cả 4 thành viên** | Phụ lục C + toàn bộ báo cáo | [`notes/05-qa-phan-bien-va-luu-y-chung.md`](notes/05-qa-phan-bien-va-luu-y-chung.md) |

*(Nếu nhóm chỉ trình bày bản báo cáo gốc 50 trang chưa gồm Gemini 4, có thể lược Slide 17–18, còn lại 18 slide.)*

---

## Mở đầu chung *(Slide 1 – 2)*

- **Slide 1 — Trang bìa:** Tên đề tài (tiếng Việt + tiếng Anh), Trường ĐHKHTN – Khoa Toán-Cơ-Tin học, danh sách 4 thành viên kèm MSSV, GVHD (TS. Nguyễn Hải Vinh, TS. Mạc Đăng Trường).
- **Slide 2 — Bố cục 4 phần thuyết trình:** Hiển thị rõ 4 phần và người phụ trách trình bày từng phần.

---

## Phần 1 • Giới thiệu bài toán *(Slide 3 – 4 | Trần Lý Dũng)*

> Xem giải thích chi tiết từng hình & lời dẫn tại [`notes/01-phan-1-gioi-thieu-bai-toan.md`](notes/01-phan-1-gioi-thieu-bai-toan.md).

| Slide | Tiêu đề slide | Nội dung chính cô đọng | Hình / Bảng đưa lên slide |
|---|---|---|---|
| **Slide 3** | Bối cảnh & Câu hỏi nghiên cứu | Khoảng cách giữa *"biên dịch được"* và *"chạy đúng, mở rộng được"* trong HPC; 3 câu hỏi nghiên cứu (RQ1–RQ3); vị trí bài báo Diehl et al. (2025/2026) so với các công trình trước (tóm gọn Mục 2.6). | Khung 3 câu hỏi RQ |
| **Slide 4** | Bài toán tập Mandelbrot | Công thức lặp $z_{k+1}=z_k^2+c$; tính *song song hiển nhiên* nhưng **mất cân bằng tải tự nhiên** (vùng đen chạm 1000 vòng, nền ngoài thoát sau 1–3 vòng); định dạng ảnh PBM/PGM không cần thư viện ngoài. | **Hình 1** (`Report/figures/mandelbrot_coroutine.png`, `mandelbrot_mpi.jpg`) |

---

## Phần 2 • 5 mô hình, Kiến trúc thực nghiệm & Demo *(Slide 5 – 10 | Nguyễn Quang Anh)*

> Xem giải thích chi tiết & kịch bản lệnh chạy demo tại [`notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md).

| Slide | Tiêu đề slide | Nội dung chính cô đọng | Hình / Bảng đưa lên slide |
|---|---|---|---|
| **Slide 5** | Song song hóa trong C++ hiện đại | Sự tiến hóa chuẩn C++11 (`std::async`) → C++17 (`std::execution::par`) → C++20 (`coroutines`, `latch`/`barrier`); tính năng càng mới dữ liệu huấn luyện càng ít. | **Hình 2** (`Report/figures/fig_timeline.png`) |
| **Slide 6** | 5 mô hình song song được đánh giá | Tóm tắt cơ chế, cách chỉnh số luồng/phân vùng và điểm dễ sai của 4 biến thể bộ nhớ chia sẻ (C++11, C++17, C++20, OpenMP) + 1 biến thể phân tán (MPI+OpenMP). | Tóm tắt **Bảng 2** (5 dòng ngắn) |
| **Slide 7** | Ma trận thực nghiệm & Hạ tầng đo | 4 LLM (ChatGPT-5, ChatGPT-4, Claude, LLaMA) × 5 biến thể = **20 chương trình** (zero-shot 1 lần sinh); cụm `rostam` (Xeon Gold 6148, 20 lõi/nút, GCC 11.5, Intel TBB 2022.2, OpenMPI 5.0.7). | **Bảng 4** & tóm tắt **Bảng 5** |
| **Slide 8** | Thiết kế bộ prompt P1, P2, P3 | Trích ngắn gọn P1 (C++11/17/20), P2 (OpenMP), P3 (MPI+OpenMP); nhấn **2 chi tiết sống còn**: P3 bắt buộc có cờ `-p` (tránh mọi rank tính lặp cả ảnh) và prompt **không cố định tọa độ/độ phân giải**. | Khung 3 prompt P1–P3 |
| **Slide 9** | Quy trình kiểm định & Độ đo | 4 cổng kiểm định (Build → Run → Kiểm tra ảnh → LOC/COCOMO/Scaling); công thức thông lượng `pixel updates per second` = $(W\cdot H)/T_{\text{compute}}$ **loại trừ I/O**; giới hạn so sánh với máy local (12 luồng, không có TBB/MPI). | Sơ đồ 4 bước + công thức Throughput |
| **Slide 10** | Minh họa Demo trực tiếp (`Demo/`) | Chạy `python interactive.py` (sau `deactivate` `.venv`): **Menu 1** (tuần tự vs OpenMP) → **Menu 5** (mở ảnh) → **Menu 3** (`static` vs `dynamic`) → **Menu 4** (`--ignore-t` tạo đường phẳng tái hiện lỗi ChatGPT-4). | Live terminal + `Demo/speedup.png` / `mandel_view.png` |

---

## Phần 3 • Phân tích lỗi thực tế *(Slide 11 – 14 | Đồng Đức Dương)*

> Xem giải thích chi tiết các lỗi & cách đọc Hình 3–4 tại [`notes/03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md).

| Slide | Tiêu đề slide | Nội dung chính cô đọng | Hình / Bảng đưa lên slide |
|---|---|---|---|
| **Slide 11** | Tỉ lệ thành công: Hố ngăn cách Build vs Run | 3/4 mô hình biên dịch 100% nhưng thực thi tụt mạnh: ChatGPT-4 còn 20% (1/5), Claude 40%/60%, LLaMA 0%; chỉ ChatGPT-5 đạt 100% cả 3 tiêu chí. *(Ghi chú ngắn việc đối chiếu phát hiện lệch nội tại Bảng III vs I–II.)* | **Bảng 6** |
| **Slide 12** | 4 nhóm lỗi thực tế tiêu biểu theo mô hình | • **ChatGPT-4:** chỉ parse `-t`, đặt nhầm `OPENMP_NUM_THREADS` (thực ra GCC dùng TBB → `tbb::global_control`).<br>• **Claude:** coroutine treo vô hạn ở `done()` vì `final_suspend = suspend_never`; viết comment nhưng quên đặt luồng.<br>• **LLaMA:** lỗi iterator/biến, **double-free segfault**, **ảnh đen do nhầm P4/P5**, đặt `MPI_Wtime()` trước `MPI_Gather`. | Tóm tắt **Bảng 7** + 2 snippet ngắn (`while (!done())`, `OPENMP_NUM_THREADS`) |
| **Slide 13** | Phân loại lỗi & Hai lớp kiến thức | Phân tầng lỗi (cú pháp / giao diện / hệ sinh thái / vòng đời tài nguyên / định dạng / đo đạc); giải thích vì sao LLM mạnh ở *Lớp 1 (cú pháp)* nhưng yếu ở *Lớp 2 (ngữ cảnh thực thi)*. | Tóm tắt **Bảng 8** |
| **Slide 14** | Độ dài mã (LOC) & Công sức COCOMO | LLaMA coroutine phải vá thêm 37–39 dòng; Claude viết dài nhất nhưng vẫn lỗi → **chất lượng không tỉ lệ với số dòng mã**; đọc biểu đồ COCOMO (ChatGPT-5 ở góc trên `Good`, 2 outlier LLaMA ở dưới) & hạn chế của COCOMO với HPC. | **Hình 3** (`Report/figures/fig_loc.png`), **Bảng 9**, **Hình 4** (`Report/figures/fig_cocomo.png`) |

---

## Phần 4 • Hiệu năng & tổng kết *(Slide 15 – 20 | Nguyễn Như Bảo)*

> Xem giải thích chi tiết Hình 5–8 & kết luận tại [`notes/04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md).

| Slide | Tiêu đề slide | Nội dung chính cô đọng | Hình / Bảng đưa lên slide |
|---|---|---|---|
| **Slide 15** | Mở rộng trên 1 nút (1–20 lõi) | Đọc 4 đồ thị `(a) Async`, `(b) Par_algo`, `(c) Coroutine`, `(d) OpenMP` theo `pixel updates/s`; nhấn mạnh **2 kiểu đường phẳng trái ngược** (phẳng trên cao = bỏ qua `-t` vs phẳng sát trục `0` = bị nén trên thang `×10⁹`); lưu ý nhãn Hình 5d. | **Hình 5** (`Report/figures/fig_scaling_shared.png`) |
| **Slide 16** | Mở rộng phân tán (1–12 nút) & So sánh mã con người | Thang log₂ trên ảnh `12000×80000`: cả 4 LLM mở rộng được sau khi sửa nhưng **đều chững ở bước `2→4` nút** (do chia tĩnh hàng gặp mất cân bằng đối xứng Mandelbrot); tổng kết so với `Human [5]` (sách *Parallel C++*): LLM ngang/vượt ở mẫu đơn giản, thua ở coroutine & MPI. | **Hình 6** (`Report/figures/fig_scaling_dist.png`) + **Bảng 10** |
| **Slide 17** *(Bản mở rộng)* | Kiểm chứng bổ sung trên **Gemini 4 Hydrogen** | Gửi nguyên văn P1–P3 trên máy cục bộ (12 luồng, GCC 13.2): **0 lỗi, 0 cảnh báo, 0 dòng phải sửa** ở các biến thể chạy được; ảnh P4 đúng ngay lần đầu; khắc phục triệt để lỗi coroutine (`std::jthread` + `std::latch`), TBB (`__has_include` + cảnh báo) và MPI (`block-cyclic` + `MPI_Gatherv`). | **Hình 7** (`Report/figures/fig_gemini4_mandelbrot.png`) + **Bảng 11** |
| **Slide 18** *(Bản mở rộng)* | Thông lượng `×10⁷ px/s` & Speedup của Gemini 4 | Đưa về cùng hệ quy chiếu `pixel updates/s`: OpenMP (`3,23×10⁷`, `11,23×`) dẫn đầu nhóm Gemini 4 do xử lý `2048×2048`, kế tiếp coroutine (`1,85×10⁷`, `10,50×`) và async (`1,75×10⁷`, `10,56×`); giải thích độ cao chênh với `mandel_omp` (`5,36×10⁷`) do diện tích miền phức mặc định khác nhau. | **Hình 8** (`Report/figures/fig_gemini4_scaling.png`) |
| **Slide 19** | Kết luận, 5 Khuyến nghị & Hướng phát triển | LLM là trợ lý sinh bản nháp HPC tốt nhưng chưa thay thế kỹ sư; **5 khuyến nghị thực dụng** + danh mục kiểm duyệt (Bảng 12); hạn chế nghiên cứu (sinh 1 lần, bài toán đơn giản) và 4 hướng mở rộng (stencil/FFT, lặp thống kê, agentic 2026 `[9]–[11]`). | 5 gạch đầu dòng khuyến nghị + tóm tắt **Bảng 12** |
| **Slide 20** | Cảm ơn & Hỏi – Đáp (Q&A) | Chốt bài và mở phần hỏi đáp *(cả 4 thành viên cùng tham gia theo phân vai tại [`notes/05-qa-phan-bien-va-luu-y-chung.md`](notes/05-qa-phan-bien-va-luu-y-chung.md))*. | Slide kết gọn gàng |
