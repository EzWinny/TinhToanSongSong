# Ghi chú thuyết trình — Phần 1: Giới thiệu bài toán

- **Phục vụ cho đoạn:** **Mở đầu & Phần 1 • Giới thiệu bài toán** *(Slide 1–4, dự kiến ~3–3,5 phút)*
- **Người thuyết trình phụ trách:** Trần Lý Dũng (`24001658`)
- **Tài liệu báo cáo tương ứng:** Phần 1 (*Giới thiệu*) và Mục 2.1 (*Tập Mandelbrot*) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf`
- **Tệp hình ảnh / bảng cần đưa lên slide:**
  - `Report/figures/mandelbrot_coroutine.png` & `Report/figures/mandelbrot_mpi.jpg` *(Hình 1 — Slide 4)*

---

## 1. Mục tiêu đoạn thuyết trình này
Mở màn gọn gàng (giới thiệu nhóm & bố cục 4 phần tại Slide 1–2) và giúp người nghe nắm rõ **2 câu hỏi nền** trước khi chuyển sang 5 mô hình song song & thực nghiệm:
1. **Tại sao phải đánh giá LLM trong HPC? (Slide 3)** — LLM viết mã tuần tự rất tốt, nhưng mã song song đòi hỏi hiểu sâu bộ nhớ, đồng bộ, backend trình biên dịch và truyền thông; *"biên dịch được"* khác rất xa *"chạy đúng và mở rộng được"*.
2. **Tại sao bài báo chọn tập Mandelbrot làm bài toán thử? (Slide 4)** — Dễ hiểu, không cần thư viện ngoài (dùng định dạng Netpbm), nhưng có bẫy mất cân bằng tải tự nhiên cực hay.

---

## 2. Giải thích chi tiết nội dung & minh họa dùng ở Phần 1

### Slide 3: Bối cảnh, khoảng trống nghiên cứu & 3 câu hỏi RQ
- **Khoảng trống nghiên cứu (Mục 2.6 — nói gọn trong 20 giây):** các công trình trước như `LLM4HPC`, `HPC-Coder-v2`, `OMPGPT`, `MPIRigen` thường chỉ tập trung một mô hình riêng lẻ (chỉ OpenMP hoặc chỉ MPI), bài toán hoàn thành mã hoặc dừng ở tỉ lệ biên dịch; bài báo của **Diehl, Nader & Gupta (2026)** là một trong những nghiên cứu đầu tiên đặt 4 LLM cạnh nhau xuyên suốt từ C++11/17/20, OpenMP đến MPI+OpenMP và đo khả năng mở rộng trên cụm HPC thật.
- **3 câu hỏi nghiên cứu:**
  - **RQ1:** Tính đúng đắn qua 3 cổng *Biên dịch → Thực thi → Ảnh đầu ra* & các lỗi đặc thù.
  - **RQ2:** Khả năng mở rộng (scaling) trên 1 nút (20 lõi) và phân tán (1–12 nút).
  - **RQ3:** Hiệu năng & chi phí/chất lượng (LOC, COCOMO) khi đặt cạnh mã con người từ sách *Parallel C++*.

### Minh họa: Hình 1 — Tập Mandelbrot (`mandelbrot_coroutine.png` và `mandelbrot_mpi.jpg` — Slide 4)
- **Ý nghĩa toán học ngắn gọn (nói trong 20 giây):**
  - Với mỗi điểm ảnh tương ứng một số phức $c$, lặp $z_{k+1} = z_k^2 + c$ từ $z_0 = 0$.
  - Nếu $|z_k| > 2$ thì điểm đó **thoát** (nằm ngoài tập); nếu sau $I_{\max} = 1000$ vòng vẫn không thoát thì nằm **trong tập** (vùng đen đặc ở giữa).
- **3 điểm "ăn tiền" cần nhấn khi chỉ vào hình:**
  1. **Song song hiển nhiên (*embarrassingly parallel*):** các điểm ảnh hoàn toàn độc lập nhau, không có phụ thuộc dữ liệu giữa pixel này với pixel khác → nếu LLM còn gặp lỗi ở bài toán "dễ chia" như thế này thì với bài toán HPC thật (stencil, FFT) sẽ càng khó hơn.
  2. **Mất cân bằng tải tự nhiên (cực kỳ quan trọng — móc nối sang Demo & Phần 4):** điểm nền trắng bên ngoài thoát chỉ sau 1–3 vòng lặp, còn điểm đen trong ruột tập Mandelbrot phải chạy đủ `1000` vòng lặp. Chia tĩnh theo hàng (`static`) sẽ làm các luồng/nút ôm vùng giữa chậm gấp nhiều lần các luồng ở rìa! *(Xem thêm giải thích nhanh tại [`06-giai-thich-lap-lich-openmp.md`](06-giai-thich-lap-lich-openmp.md).)*
  3. **Chi tiết thú vị trên chính 2 ảnh của Hình 1:** cả hai ảnh đều do **ChatGPT-5** sinh (ảnh trái là coroutine, ảnh phải là MPI+OpenMP, cùng $1920\times 1080$, $I_{\max}=1000$, tâm $(-0{,}75; 0)$, tỉ lệ $3{,}0$), nhưng lại cho **hai bảng màu khác nhau** vì prompt gốc không cố định hàm tô màu.

---

## 3. Những điều cần LƯU Ý & TRÁNH NHẦM LẪN
- **Nhấn rõ định dạng PBM/PGM:** bài báo chọn định dạng ảnh **Netpbm (PBM/PGM)** vì là định dạng tối giản, không cần thư viện ngoài (như libpng/OpenCV) — nhưng sẽ tạo ra bẫy nhầm giữa **P4 (1 bit/pixel)** và **P5 (8 bit/pixel)** ở Phần 3.
- **Không làm lộ hết kết quả Phần 3 & 4** — chỉ đặt câu hỏi gợi mở (*"Liệu biên dịch 100% có đồng nghĩa chạy đúng và mở rộng tốt?"*).
- **Giữ nhịp gọn (~3–3,5 phút)** vì toàn bộ phần Tiến hóa C++ và 5 mô hình song song (Slide 5–6) được chuyển liền mạch sang Phần 2 để Quang Anh dẫn thẳng vào Ma trận thực nghiệm & Demo.

---

## 4. Câu chuyển mượt sang Phần 2 (Nguyễn Quang Anh)
> *"Trên bài toán tập Mandelbrot vừa đơn giản về thuật toán vừa giàu tính thử thách về cân bằng tải như vậy, nhóm tác giả đã lựa chọn 5 mô hình lập trình song song nào của C++, OpenMP và MPI, đồng thời thiết kế bộ prompt và quy trình kiểm định ra sao — kèm phần demo trực tiếp ngay tại lớp? Mời bạn Quang Anh trình bày Phần 2."*
