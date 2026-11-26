# Ghi chú thuyết trình — Phần 4: Hiệu năng & tổng kết

- **Phục vụ cho đoạn:** **Phần 4 • Hiệu năng & tổng kết** *(đoạn chốt bài, dự kiến ~6–7 phút)*
- **Người thuyết trình phụ trách:** Nguyễn Như Bảo (`24001655`)
- **Tài liệu báo cáo tương ứng:** Phần 4 (Mục 4.6–4.9: *Mở rộng 1 nút, Mở rộng phân tán, So sánh mã con người, Thử nghiệm bổ sung Gemini 4 Hydrogen*), Phần 5 (Mục 5.6–5.7) và Phần 6 (*Kết luận và hướng phát triển*) trong `Report/Bao-cao-LLM-HPC-Mandelbrot-bo-sung-Gemini4.pdf`
- **Tệp hình ảnh / bảng cần đưa lên slide:**
  - `Report/figures/fig_scaling_shared.png` *(Hình 5 — Mở rộng trên 1 nút, 1–20 lõi)*
  - `Report/figures/fig_scaling_dist.png` *(Hình 6 — Mở rộng phân tán, 1–12 nút)*
  - **Bảng 10** (*So sánh với mã con người `Human [5]`*)
  - *(Nếu trình bày bản mở rộng Gemini 4):* `Report/figures/fig_gemini4_mandelbrot.png` *(Hình 7)*, `Report/figures/fig_gemini4_scaling.png` *(Hình 8)*, **Bảng 11**
  - Tóm tắt **5 khuyến nghị** + **Danh mục kiểm duyệt (Bảng 12)** + **4 hướng phát triển**

---

## 1. Giải thích chi tiết từng minh họa hiệu năng

### Minh họa 1: Hình 5 — Mở rộng trên 1 nút (`fig_scaling_shared.png`, 1 → 20 lõi)
- **Cách đọc trục & ký hiệu:**
  - Trục ngang: số lõi yêu cầu qua `-t` (`1 → 20` trên nút Xeon Gold 6148).
  - Trục dọc: **`pixel updates per second`** (số cập nhật điểm ảnh/giây — **càng cao càng nhanh, dốc lên càng đều thì mở rộng càng tốt**).
  - **CHÚ Ý hệ số trục dọc khác nhau tới 100 lần:** Hình **(a)** và **(d)** là **`×10⁹`**, còn Hình **(b)** và **(c)** là **`×10⁷`**!
  - Ký hiệu: `■` ChatGPT-4 | `▲` ChatGPT-5 | `◆` Claude | `○` LLaMA | `♥` *(xanh dương)* **Human [5]** (mã chuẩn từ sách *Parallel C++* chạy thật trên cùng cụm `rostam`).
- **Tóm tắt từng hình con (nói mỗi hình 1–2 câu sắc gọn):**
  - **(a) Async (`×10⁹`):** ChatGPT-4 (`■`) tăng tuyến tính rất cao lên ~`5,6×10⁹` (nhanh nhất). ChatGPT-5, Claude, Human thực tế *vẫn tăng đều* ở mức `~10⁷` nhưng bị ép sát đáy trên thang `×10⁹`.
  - **(b) Parallel algorithms (`×10⁷`):** **3 đường phẳng nằm ngang hoàn toàn** (Claude `◆`, ChatGPT-4 `■`, LLaMA `○`) vì bỏ qua `-t` / đặt nhầm `OPENMP_NUM_THREADS`, luôn chạy full 20 lõi! Chỉ **ChatGPT-5 (`▲`)** dùng đúng `tbb::global_control` nên mở rộng tuyến tính, nhưng vẫn chậm hơn `Human` (`♥`, ~`2,1×10⁷`) hơn 2 lần.
  - **(c) Coroutines (`×10⁷`):** LLaMA (`○`) lại phẳng tít trên cao (~`1,3×10⁷`, bỏ qua `-t`). Trong nhóm mở rộng đúng, **Human (`♥`, ~`1,06×10⁷`) dẫn đầu**, ChatGPT-4 và ChatGPT-5 trùng nhau (~`0,8×10⁷`), Claude chậm nhất (~`0,4×10⁷`).
  - **(d) OpenMP (`×10⁹`):** một đường tăng tuyến tính vọt lên ~`6,2×10⁹`, vượt xa cả mã con người (`♥`). *(Lưu ý cho Q&A: văn bản bài báo ghi ChatGPT-5 vượt mã con người ở OpenMP, nhưng trên đồ thị gốc ký hiệu lại là ô vuông `■` của ChatGPT-4 — khả năng cao tác giả nhầm nhãn legend khi vẽ hình.)*
- **Điểm "ăn tiền" bắt buộc phải nhấn mạnh khi chỉ Hình 5 — PHÂN BIỆT 2 KIỂU ĐƯỜNG PHẲNG:**
  1. **Đường phẳng nằm CAO** *(hình b: Claude/ChatGPT-4/LLaMA; hình c: LLaMA)* = **LỖI bỏ qua `-t`** (chạy hết 20 lõi ngay cả khi truyền `-t 1`).
  2. **Đường phẳng nằm SÁT TRỤC `0`** *(hình a & d: Human/ChatGPT-5/Claude)* = **KHÔNG phải lỗi**, mà do **thang tuyến tính `×10⁹`** nén các đường `×10⁷` xuống sát đáy!

---

### Minh họa 2: Hình 6 — Mở rộng phân tán (`fig_scaling_dist.png`, 1 → 12 nút MPI+OpenMP)
- **Cấu hình đo:** ảnh cực lớn `12000 × 80000`, `1000` vòng lặp; mỗi nút chạy `1` rank MPI × `20` lõi OpenMP; trục ngang là số nút (`1, 2, 4, 8, 12`), **cả hai trục đều theo thang logarit cơ số 2** (`2¹⁹ → 2²³` `pixel updates/s`).
- **3 quan sát cốt lõi cần chỉ trực tiếp trên đồ thị:**
  1. **Mã con người (`♥` xanh dương) dẫn đầu tuyệt đối** trên toàn dải và tăng thẳng tắp đều đặn trên thang log-log.
  2. **Sau khi sửa lỗi thực thi, cả 4 LLM đều mở rộng được:** ChatGPT-5 (`▲`) & ChatGPT-4 (`■`) thuộc nhóm trên (ngang nhau ở 8–12 nút); LLaMA (`●`) & Claude (`◆`) thuộc nhóm dưới (thấp hơn khoảng ~2 lần).
  3. **Hiện tượng "gãy khúc / chững tăng tốc" từ 2 → 4 nút ở CẢ 4 LLM (điểm giải thích cực hay!):**
     - Từ `1 → 2` nút, mọi đường tăng rất đẹp; nhưng từ **`2 → 4` nút** cả 4 đường LLM đều gần như nằm ngang, trong khi mã con người vẫn tăng đều!
     - **Giải thích toán học cực thuyết phục:** tập Mandelbrot **đối xứng qua trục thực** ($y = 0$). Khi chia tĩnh ảnh theo hàng thành **2 nút**, nửa trên và nửa dưới có khối lượng tính **bằng nhau tuyệt đối**. Nhưng khi chia tĩnh thành **4 dải hàng**, **2 dải giữa ôm gần trọn phần ruột đen Mandelbrot**, còn 2 dải trên/dưới rất nhẹ → nút giữa chạy chậm nhất chặn toàn bộ hệ thống trước `MPI_Gather`! (Mã con người tránh được nhờ chiến lược phân vùng/cân bằng tải tốt hơn.)

---

### Minh họa 3: Bảng 10 — So sánh tổng thể với mã con người (`Human [5]`)
- **Cách lấy mốc so sánh (nếu giảng viên hỏi):** `Human [5]` là **5 chương trình chạy thật** từ sách *Parallel C++* (Diehl et al., 2024) — mã sạch, chuẩn mực nhưng không tối ưu cực đoan — chạy trên **cùng cụm `rostam`** với mã LLM.
- **Kết luận 2 chiều:**
  - **Mẫu đơn giản (Async, OpenMP):** LLM mạnh có thể **ngang hoặc vượt** mã sách nhờ tự thêm tối ưu.
  - **Mẫu điều phối phức tạp (C++17 par_algo, C++20 coroutine, MPI+OpenMP):** **mã con người vẫn thắng** vì đòi hỏi kiểm soát vòng đời tài nguyên, backend và phân vùng truyền thông.

---

### Minh họa 4 (Bản mở rộng — Mục 4.9): Kiểm chứng bổ sung trên **Gemini 4 Hydrogen**
*(Dùng Hình 7 `fig_gemini4_mandelbrot.png`, Hình 8 `fig_gemini4_scaling.png` và Bảng 11 — rất đáng nói 1,5–2 phút để tạo điểm nhấn sáng tạo của nhóm!)*

- **Bối cảnh trung thực (nói rõ ngay đầu):** chạy độc lập trên máy cục bộ (**12 luồng, MinGW-W64 GCC 13.2.0, không cài Intel TBB/MPI**), dùng **nguyên văn 5 prompt P1–P3** (lần sinh đầu, **0 chỉnh sửa**), tách biệt hoàn toàn với bảng kết quả trên cụm `rostam`.
- **Hình 7 (4 ảnh P4 Mandelbrot):** cả 4 biến thể bộ nhớ chia sẻ biên dịch **0 lỗi, 0 cảnh báo** (`-Wall -Wextra`) và xuất ảnh P4 đúng tỉ lệ, rõ biên fractal ngay từ lần đầu — không còn lỗi ảnh đen P4/P5.
- **Hình 8 (cùng hệ quy chiếu `×10⁷ pixel updates/s` + Speedup) & Bảng 11:**
  - **Tham chiếu cục bộ (`mandel_omp.cpp`, `1920×1080`):** `0,51 → 5,36 × 10⁷` px/s (**`10,55×`**).
  - **Gemini 4 — OpenMP (`2048×2048`):** `0,29 → 3,23 × 10⁷` px/s (**`11,23×`**) — **dẫn đầu cả thông lượng lẫn speedup** trong 3 biến thể đa luồng của Gemini 4 (nhờ quy đổi về `px/s`, loại bỏ sai lệch do xử lý gấp đôi số điểm ảnh `4,19M` vs `2,07M`).
  - **Gemini 4 — C++20 coroutine (`1920×1080`):** `0,18 → 1,85 × 10⁷` px/s (**`10,50×`**) — tự xây `ThreadPool` (`std::jthread`) + `co_await` + `std::latch`, **triệt tiêu hoàn toàn** lỗi treo `done()` của Claude và double-free của LLaMA!
  - **Gemini 4 — C++11 async (`1920×1080`):** `0,17 → 1,75 × 10⁷` px/s (**`10,56×`**).
  - **Gemini 4 — C++17 `par_algo.cpp`:** kiểm tra `__has_include(<tbb/global_control.h>)`, dùng đúng `tbb::global_control` và tự in cảnh báo khi máy thiếu TBB; đạt **`2,91 × 10⁷` px/s ngay trên 1 luồng** nhờ tự thêm cắt tỉa hình tim + bóng chu kỳ 2!
  - **Gemini 4 — `mpi_omp.cpp` (kiểm duyệt tĩnh):** đạt toàn bộ checklist (`MPI_THREAD_FUNNELED`, chia **block-cyclic** theo `-p` tránh lỗi chững `2→4` nút, dùng `MPI_Gatherv`, đặt `MPI_Wtime()` sau gather).
- **LƯU Ý ĐỂ TRẢ LỜI NẾU GIẢNG VIÊN HỎI TẠI SAO `mandel_omp` (`5,36×10⁷`) CAO HƠN GEMINI 4 (`1,75–3,23×10⁷`) TRÊN HÌNH 8a:**
  - Vì **prompt gốc P1/P2 không cố định khung tọa độ phức**: `mandel_omp` phủ diện tích mặt phẳng phức **`16,0`** (rất nhiều điểm nền thoát sau 1–3 vòng), trong khi `openmp.cpp` phủ **`9,0`** (nhỏ hơn `1,78×`) và `async.cpp` phủ **`5,06`** (phóng sát hơn `3,16×` vào ruột tập đen). Nếu quy đổi theo diện tích miền phức, tốc độ tính thuần của Gemini 4 **ngang ngửa mốc con người** — củng cố khuyến nghị phải cố định tọa độ trong prompt khi benchmark!

---

## 2. Chốt bài — Tổng kết, Khuyến nghị & Hướng phát triển (Phần 6)
Trình bày gọn trong **3 ý chốt dễ nhớ**:
1. **Kết luận trung tâm:** LLM đã đủ năng lực làm **trợ lý sinh bản nháp HPC rất hiệu quả** (thế hệ mới 2026 như Gemini 4 khắc phục rõ rệt lỗi coroutine/TBB/MPI của thế hệ 2025), nhưng **chưa thể thay thế kỹ sư HPC** vì vẫn cần kiểm duyệt ngữ cảnh thực thi, header/cờ dòng lệnh và hiệu năng.
2. **5 khuyến nghị thực hành (dùng làm slide chốt):**
   - Coi mã LLM là bản nháp, luôn bật `-Wall -Wextra` và kiểm tra đầu ra.
   - **Đo khả năng mở rộng thay vì tin vào sự tồn tại của cờ `-t`**.
   - Soát kỹ **vòng đời coroutine** (`final_suspend`, `promise_type`) và **MPI** (`Gatherv`, mốc đo sau gather).
   - Kiểm tra trực quan ảnh/header đầu ra (tránh lỗi P4/P5).
   - Viết prompt rõ ràng buộc phi chức năng: độ phân giải, miền tọa độ phức, backend, loại trừ I/O.
3. **Hướng phát triển (Mục 6.3 & bối cảnh 3 nghiên cứu 2026 `[18]–[20]`):** mở rộng sang bài toán truyền thông dày (stencil, FFT, FEM), lặp nhiều lần sinh để thống kê, đánh giá quy trình agentic (tự biên dịch–sửa lỗi) và xây dựng bộ tiêu chí HPC ngoài tỉ lệ biên dịch.

---

## 3. Câu kết thúc bài thuyết trình & mở Q&A
> *"Trên đây là toàn bộ phần trình bày của nhóm về đánh giá năng lực sinh mã C++ song song và MPI+OpenMP của các mô hình LLM cùng thực nghiệm kiểm chứng bổ sung. Nhóm rất mong nhận được ý kiến đóng góp và câu hỏi phản biện từ thầy và các bạn. Xin cảm ơn!"*
