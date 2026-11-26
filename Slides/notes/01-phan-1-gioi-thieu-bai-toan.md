# Ghi chú thuyết trình — Phần 1: Giới thiệu bài toán

- **Phục vụ cho đoạn:** **Phần 1 • Giới thiệu bài toán** *(đầu buổi thuyết trình, dự kiến ~4–5 phút)*
- **Người thuyết trình phụ trách:** Trần Lý Dũng (`24001658`)
- **Tài liệu báo cáo tương ứng:** Phần 1 (*Giới thiệu*) và Phần 2 (*Cơ sở lý thuyết*, Mục 2.1–2.7) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf`
- **Tệp hình ảnh / bảng cần đưa lên slide:**
  - `Report/figures/mandelbrot_coroutine.png` & `Report/figures/mandelbrot_mpi.jpg` *(Hình 1)*
  - `Report/figures/fig_timeline.png` *(Hình 2)*
  - Tóm tắt **Bảng 2** (*So sánh các cơ chế song song bộ nhớ chia sẻ trong C++*)

---

## 1. Mục tiêu đoạn thuyết trình này
Giúp người nghe nắm rõ **3 câu hỏi nền** trước khi vào phần thực nghiệm:
1. **Tại sao phải đánh giá LLM trong HPC?** — LLM viết mã tuần tự rất tốt, nhưng mã song song đòi hỏi hiểu sâu bộ nhớ, đồng bộ, backend trình biên dịch và truyền thông; *"biên dịch được"* khác rất xa *"chạy đúng và mở rộng được"*.
2. **Tại sao bài báo chọn tập Mandelbrot làm bài toán thử?** — Dễ hiểu, không cần thư viện ngoài, nhưng có bẫy cân bằng tải rất hay.
3. **5 mô hình lập trình song song được kiểm thử là gì?** — Từ chuẩn C++ hiện đại đến OpenMP và mô hình lai MPI+OpenMP.

---

## 2. Giải thích chi tiết các minh họa dùng ở Phần 1

### Minh họa 1: Hình 1 — Tập Mandelbrot (`mandelbrot_coroutine.png` và `mandelbrot_mpi.jpg`)
- **Ý nghĩa toán học ngắn gọn (nói trong 20 giây):**
  - Với mỗi điểm ảnh tương ứng một số phức $c$, lặp $z_{k+1} = z_k^2 + c$ từ $z_0 = 0$.
  - Nếu $|z_k| > 2$ thì điểm đó **thoát** (nằm ngoài tập); nếu sau $I_{\max} = 1000$ vòng vẫn không thoát thì nằm **trong tập** (vùng đen đặc ở giữa).
- **3 điểm "ăn tiền" cần nhấn khi chỉ vào hình:**
  1. **Song song hiển nhiên (*embarrassingly parallel*):** các điểm ảnh hoàn toàn độc lập nhau, không có phụ thuộc dữ liệu giữa pixel này với pixel khác → nếu LLM còn gặp lỗi ở bài toán "dễ chia" như thế này thì với bài toán HPC thật (stencil, FFT) sẽ càng khó hơn.
  2. **Mất cân bằng tải tự nhiên (cực kỳ quan trọng — móc nối sang Demo & Phần 4):** điểm nền trắng bên ngoài thoát chỉ sau 1–3 vòng lặp, còn điểm đen trong ruột tập Mandelbrot phải chạy đủ `1000` vòng lặp. Chia tĩnh theo hàng (`static`) sẽ làm các luồng/nút ôm vùng giữa chậm gấp nhiều lần các luồng ở rìa!
  3. **Chi tiết thú vị trên chính 2 ảnh của Hình 1:** cả hai ảnh đều do **ChatGPT-5** sinh (ảnh trái là coroutine, ảnh phải là MPI+OpenMP, cùng $1920\times 1080$, $I_{\max}=1000$, tâm $(-0{,}75; 0)$, tỉ lệ $3{,}0$), nhưng lại cho **hai bảng màu khác nhau** vì prompt gốc không cố định hàm tô màu.

### Minh họa 2: Hình 2 — Dòng thời gian song song trong C++ (`fig_timeline.png`)
- **Cách đọc hình theo trục thời gian (từ trái sang phải):**
  - **C++11 (2011):** `std::thread`, `std::async` / `std::future`, smart pointer, lambda — phổ biến lâu đời, rất nhiều ví dụ trên Internet.
  - **C++14 (2014):** generic lambda, `shared_mutex` (bổ trợ).
  - **C++17 (2017):** **Parallel algorithms** (`std::for_each(std::execution::par, ...)`) — viết ngắn gọn, nhưng **ẩn backend thực thi bên dưới** (trên GCC Linux là **Intel TBB**, không phải OpenMP!).
  - **C++20 (2020):** **Coroutines** (`co_await`, `co_return`), `std::latch`, `std::barrier` — mới nhất, độ phức tạp cao nhất về quản lý vòng đời frame và bộ nhớ.
- **Điểm cần nhấn để dẫn dắt tâm lý người nghe:** tính năng càng mới và trừu tượng (như C++20 coroutine) thì dữ liệu huấn luyện mẫu chuẩn trên mạng càng ít → **dự đoán trước** rằng LLM sẽ dễ vấp nhất ở C++17 (nhầm backend) và C++20 (sai vòng đời coroutine).

### Minh họa 3: Tóm tắt Bảng 2 — 5 biến thể song song trong nghiên cứu
*(Trên slide chỉ nên tóm gọn thành bảng 5 dòng ngắn, không chép nguyên văn dài)*:

| Biến thể | Mô hình bộ nhớ | Cách điều khiển số luồng / phân vùng | Điểm dễ sai với LLM |
|---|---|---|---|
| **C++11 `std::async`** | Chia sẻ (1 nút) | Tự chia tác vụ thành $T$ phần (`-t`) | Quên `std::launch::async` hoặc chia tải mất cân bằng |
| **C++17 `par_algo`** | Chia sẻ (1 nút) | Qua API backend (`tbb::global_control` trên GCC) | Đặt nhầm `OMP_NUM_THREADS` → bị bỏ qua |
| **C++20 Coroutines** | Chia sẻ (1 nút) | Tự quản lý `promise_type`, handle, thread pool | Treo `done()`, double-free, segfault |
| **OpenMP** | Chia sẻ (1 nút) | Chỉ thị `#pragma omp parallel for` + `-t` | Quên cân bằng tải (`dynamic`) hoặc bỏ qua `-t` |
| **MPI + OpenMP** | Phân tán (nhiều nút) | Rank MPI chia phân vùng (`-p`) + OpenMP trong nút | Sai `MPI_Gather`/`Gatherv`, đặt timer trước `MPI_Gather` |

---

## 3. Những điều cần LƯU Ý & TRÁNH NHẦM LẪN
- **Không sa đà giải thích công thức phức tạp** hay đọc toàn bộ 17–20 tài liệu liên quan ở Mục 2.6–2.7 — chỉ cần nói gọn 1 câu: *"Các nghiên cứu trước thường tập trung OpenMP/MPI riêng lẻ hoặc chỉ chấm tỉ lệ biên dịch; bài báo của Diehl, Nader & Gupta (2025/2026) là một trong những đánh giá đầu tiên kiểm thử xuyên suốt cả C++ hiện đại (11/17/20), OpenMP và MPI+OpenMP cho tới tận đo khả năng mở rộng trên cụm HPC thật."*
- **Nhấn rõ định dạng PBM/PGM:** bài báo chọn định dạng ảnh **Netpbm (PBM/PGM)** vì là định dạng tối giản, không cần thư viện ngoài (như libpng/OpenCV) — nhưng sẽ tạo ra bẫy nhầm giữa **P4 (1 bit/pixel)** và **P5 (8 bit/pixel)** ở Phần 3.
- **Không làm lộ hết kết quả Phần 3 & 4** — chỉ đặt câu hỏi gợi mở (*"Liệu biên dịch 100% có đồng nghĩa chạy đúng và mở rộng tốt?"*).

---

## 4. Câu chuyển mượt sang Phần 2 (Nguyễn Quang Anh)
> *"Vậy nhóm tác giả đã thiết kế prompt, môi trường đo và quy trình kiểm duyệt như thế nào để phát hiện những lỗi ẩn sâu trong mã song song — và chúng ta sẽ trực tiếp kiểm chứng hiện tượng này qua demo ngay sau đây. Mời bạn Quang Anh trình bày Phần 2: Kiến trúc thực nghiệm."*
