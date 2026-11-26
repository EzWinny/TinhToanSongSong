# Ghi chú thuyết trình — Phần 3: Phân tích lỗi thực tế

- **Phục vụ cho đoạn:** **Phần 3 • Phân tích lỗi thực tế** *(dự kiến ~5–6 phút)*
- **Người thuyết trình phụ trách:** Đồng Đức Dương (`24001659`)
- **Tài liệu báo cáo tương ứng:** Phần 4 (Mục 4.1–4.5: *Tỉ lệ thành công, Lỗi theo từng mô hình, Phân loại lỗi, Chất lượng & chi phí LOC/COCOMO*) và Phần 5 (Mục 5.1–5.5: *Phân tích nguyên nhân gốc rễ*) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf`
- **Tệp hình ảnh / bảng cần đưa lên slide:**
  - **Bảng 6** (*Tỉ lệ thành công trên 5 biến thể*) & **Bảng 7** (*Tổng hợp lỗi tiêu biểu*) & **Bảng 8** (*Phân loại lỗi theo tầng*)
  - `Report/figures/fig_loc.png` *(Hình 3 — Số dòng mã LOC, kèm Bảng 9 cho MPI+OpenMP)*
  - `Report/figures/fig_cocomo.png` *(Hình 4 — Biểu đồ Chất lượng vs Công sức COCOMO)*

---

## 1. Thông điệp cốt lõi của Phần 3
> **"Biên dịch thành công 100% KHÔNG có nghĩa là chạy đúng."**  
> Cú pháp C++ không còn là rào cản chính — rào cản thực sự của LLM trong lập trình song song nằm ở **ngữ nghĩa thực thi, backend trình biên dịch, vòng đời tài nguyên (coroutine) và định dạng dữ liệu (PBM/MPI)**.

---

## 2. Giải thích chi tiết từng bảng, đoạn mã lỗi và minh họa

### A. Bảng 6 — Tỉ lệ thành công: "Cú rơi tự do" từ Biên dịch sang Thực thi
| Tiêu chí | ChatGPT-5 | ChatGPT-4 | Claude | LLaMA |
|---|---:|---:|---:|---:|
| **Biên dịch (Build)** | **100%** (5/5) | **100%** (5/5) | **100%** (5/5) | 40% / 60% (3/5)\* |
| **Thực thi (Run)** | **100%** (5/5) | **20%** (1/5) | 40% / 60% (3/5)\* | **0%** (0/5)\* |
| **Tính đúng (Ảnh)** | **100%** (5/5) | **100%** (5/5) | **100%** (5/5) | 40% / 60% (3/5)\* |

- **Cách đọc gây ấn tượng:**
  - 3/4 mô hình biên dịch sạch **100%**, nhưng khi chạy thật: **ChatGPT-4 tụt từ 100% xuống chỉ còn 20%** (chỉ 1/5 biến thể — MPI+OpenMP — chạy không lỗi!), **LLaMA đạt 0%** ở các bảng tổng hợp.
  - Duy nhất **ChatGPT-5 đạt 100% cả 3 tiêu chí** (biên dịch, thực thi, ảnh đúng) — cho thấy sự nhảy vọt rõ rệt so với ChatGPT-4.
- **Lưu ý quan trọng để KHÔNG BỊ LÚNG TÚNG khi giảng viên hỏi về số `40% / 60%`:**
  - Đây là điểm **nhóm chủ động đối chiếu và phát hiện sai lệch nội tại trong chính bài báo gốc**: Bảng III của tác giả in `40%` cho Claude (Thực thi) và LLaMA (Biên dịch, Tính đúng), nhưng nếu đếm trực tiếp từng dấu `✓` trong Bảng I & II của chính bài báo đó thì là `3/5 = 60%`! Báo cáo ghi minh bạch cả hai số (`40% / 60%`) — nếu giảng viên hỏi, chỉ cần giải thích điều này sẽ là **điểm cộng rất lớn về độ kỹ lưỡng**.

---

### B. 4 nhóm lỗi kỹ thuật kinh điển phải phân tích trên slide (Bảng 7 & Mục 4.2–4.3)

#### 1. ChatGPT-4 — Lỗi "đặc tả bề mặt" & nhầm backend TBB/OpenMP
- **Lỗi dòng lệnh (4/4 bản bộ nhớ chia sẻ):** in đầy đủ hướng dẫn sử dụng (`[-t] [width height [max_iter ...]]`), nhưng trong code **chỉ parse mỗi `-t`**, còn kích thước ảnh, số vòng lặp, tọa độ bị phớt lờ hoàn toàn!
- **Lỗi hệ sinh thái backend (`par_algo`):** giả định GCC dùng OpenMP cho `std::execution::par` nên đặt biến môi trường `OPENMP_NUM_THREADS` *(thậm chí gõ sai cả tên biến chuẩn `OMP_NUM_THREADS`)*. Thực tế `libstdc++` trên GCC dùng **Intel TBB**, nên biến đó vô tác dụng → chương trình luôn chạy full 20 lõi!
  - **Cách sửa chuẩn:** dùng API `tbb::global_control(max_allowed_parallelism, num_threads)` (ChatGPT-5 làm đúng điểm này).

#### 2. Claude — Lỗi vòng đời C++20 Coroutine (treo vô hạn) & "lời hứa trong comment"
- **Treo vô hạn (`coroutine`):** dùng vòng lặp `while (!tasks[i].done()) std::this_thread::yield();` nhưng lại khai báo `final_suspend() { return std::suspend_never{}; }`.
  - **Giải thích dễ hiểu trong 15 giây:** trong C++20, `handle.done()` **chỉ trả về `true` khi coroutine dừng lại ở điểm treo cuối (`final_suspend`)**. Nếu trả về `suspend_never`, coroutine tự hủy luôn mà không dừng lại → `done()` không bao giờ hợp lệ/không bao giờ thành `true` → treo mãi mãi! Sửa thành `std::suspend_always` là hết treo.
- **Lỗi "ghi chú thay vì làm" (`par_algo`):** viết hẳn một đoạn comment rất chuyên nghiệp giải thích cần giới hạn số luồng cho C++17 parallel algorithms... nhưng **không viết dòng code nào để đặt số luồng**!

#### 3. LLaMA — Chuỗi lỗi chồng chất (cú pháp, bộ nhớ, định dạng ảnh, đo sai MPI)
- **Lỗi biên dịch:** gọi sai `std::distance(vector::iterator, Pixel*)` khác kiểu iterator; dùng biến `execution_policy_tag` chưa khai báo; coroutine dùng `co_return` nhưng thiếu `promise_type::return_void()`.
- **Lỗi thực thi nguy hiểm (Segfault — Double-free):** ở coroutine, cả `final_suspend = suspend_never` lẫn destructor đều giải phóng cùng một đối tượng tác vụ → giải phóng 2 lần gây `Segmentation fault (core dumped)`!
- **Lỗi ảnh đen toàn phần (nhầm P4 / P5):** tính giá trị màu xám 8-bit theo kiểu **P5 (PGM, 1 byte/pixel)** nhưng lại ghi header **P4 (PBM nhị phân, 1 bit/pixel)** → ảnh xuất ra toàn màu đen dù không hề có lỗi biên dịch hay cảnh báo!
- **Lỗi đo đạc ở MPI+OpenMP:** đặt mốc dừng `MPI_Wtime()` **TRƯỚC `MPI_Gather`** → bỏ sót hoàn toàn thời gian truyền thông gom dữ liệu giữa các nút, làm tốc độ nhìn có vẻ nhanh giả tạo!

#### 4. Bảng 8 — Tổng hợp 2 lớp kiến thức (Mục 5.1)
- **Lớp 1 (Cú pháp & khung thuật toán):** vòng lặp thoát Mandelbrot, cấu trúc `#pragma omp`, khung gọi `MPI_Init`/`MPI_Finalize` → **LLM làm rất tốt**.
- **Lớp 2 (Ngữ cảnh thực thi & vòng đời tài nguyên):** backend TBB của GCC, hợp đồng trạng thái `final_suspend` của coroutine, kích thước buffer & mốc đo `MPI_Gather`, định dạng bit P4 vs P5 → **đây là điểm yếu chí mạng của LLM**.

---

### C. Giải thích Minh họa Hình 3 (`fig_loc.png`) & Hình 4 (`fig_cocomo.png`)

#### Minh họa Hình 3 — Số dòng mã LOC (`fig_loc.png`, kèm Bảng 9 cho MPI+OpenMP)
- **Cách đọc hình:** 4 biểu đồ ngang cho 4 biến thể bộ nhớ chia sẻ `(a) Coroutines`, `(b) Async`, `(c) Parallel Algorithms`, `(d) OpenMP`. Trục ngang là số dòng mã (LOC, đo bằng `cloc`).
- **2 điểm cần chỉ trực tiếp trên hình:**
  1. **Thanh hai màu ở Hình 3a (LLaMA — Coroutines):** thanh xám đậm (`~98 LOC`) là mã sinh ban đầu (`Generated LOC`), phần nối thêm sáng hơn (`+37` dòng theo chú thích hình / `+39` dòng theo văn bản → `~135–137 LOC`) là phần con người **phải viết thêm rất nhiều để vá lỗi** `promise_type`, double-free và định dạng P4/P5. *(Ở MPI+OpenMP Bảng 9, LLaMA cũng phải sửa từ `71` → `82` LOC.)*
  2. **Chất lượng KHÔNG tỉ lệ thuận với độ dài mã:** nhìn cả 4 hình, **Claude luôn viết dài nhất** (~`137–192 LOC`), dài hơn cả ChatGPT-5 ở async/par_algo/OpenMP, nhưng vẫn mắc lỗi treo coroutine và bỏ qua `-t`! Viết dài nhiều chú thích không đảm bảo mã đúng.

#### Minh họa Hình 4 — Biểu đồ Chất lượng & Công sức COCOMO (`fig_cocomo.png`)
- **Cách đọc 2 hệ trục (rất dễ nhầm nếu không giải thích kỹ cho khán giả!):**
  - **Trục ngang:** công sức ước lượng theo mô hình COCOMO (`Easy` bên trái → `Difficult` bên phải, đơn vị người-tháng, đo bằng `scc`).
  - **Trục dọc:** chất lượng mã tổng hợp (`Poor` ở dưới → `Good` ở trên).
  - **Vị trí lý tưởng:** càng lên **góc trên** (`Good`) càng tốt!
- **Cách đọc ký hiệu (CHÚ Ý: 2 hình trái và phải dùng bộ ký hiệu KHÁC NHAU!):**
  - **Hình trái (Bộ nhớ chia sẻ):**
    - **Màu sắc = Mô hình LLM:** **Đen** = ChatGPT-5 | **Xanh dương** = ChatGPT-4 | **Xanh lá** = Claude | **Xám** = LLaMA.
    - **Hình dạng = Biến thể:** `x` = Coroutines | `♠` = Async | `♣` = Parallel Algorithms | `★` = OpenMP.
    - **Điểm cần chỉ:** cụm chấm **đen (ChatGPT-5)** nằm gọn ở góc trên (`Good`), còn **2 điểm ngoại lai (outliers) màu xám của LLaMA** (`♣` par_algo ở thấp và `x` coroutine rơi tuột xuống sát đáy `Poor` bên phải `Difficult`) thể hiện rõ chi phí sửa lỗi nặng nề nhất.
  - **Hình phải (Bộ nhớ phân tán — MPI+OpenMP):**
    - Tất cả đều màu đen, **Hình dạng = Mô hình LLM:** `♠` = ChatGPT-5 (cao nhất, công sức lớn hơn chút) | `♣` = Claude & `x` = ChatGPT-4 (gần nhau, chất lượng cao) | `★` = LLaMA (rơi xuống thấp hơn rõ rệt do là mô hình duy nhất lỗi thực thi).
- **Nhận xét phản biện hay về COCOMO:** COCOMO vốn được xây cho phần mềm tuần tự dựa trên số dòng mã (KLOC), **không tính được độ khó của gỡ lỗi song song/treo coroutine/race condition** → chỉ nên đọc như thước đo tương đối!

---

## 3. Câu chuyển mượt sang Phần 4 (Nguyễn Như Bảo)
> *"Sau khi các lỗi biên dịch và lỗi thực thi vừa nêu được con người vá tối thiểu, liệu những chương trình LLM này chạy nhanh đến đâu, có thực sự mở rộng khi tăng lên 20 lõi hay 12 nút không, và thế hệ mô hình mới cuối năm 2026 như Gemini 4 Hydrogen đã khắc phục được các lỗi này chưa? Mời bạn Như Bảo trình bày Phần 4: Hiệu năng và tổng kết."*
