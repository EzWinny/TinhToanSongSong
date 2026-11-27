# Ghi chú thuyết trình — Phần 1: Giới thiệu bài toán

- **Phục vụ cho đoạn:** **Mở đầu & Phần 1 • Giới thiệu bài toán** *(Slide 1–5, dự kiến ~4–4,5 phút)*
- **Người thuyết trình phụ trách:** Trần Lý Dũng (`24001658`)
- **Tài liệu báo cáo tương ứng:** Phần 1 (*Giới thiệu*, Mục 1.1–1.4) và Mục 2.1 (*Tập Mandelbrot*) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf`
- **Tệp hình ảnh / bảng cần đưa lên slide:**
  - `Report/figures/mandelbrot_coroutine.png` & `Report/figures/mandelbrot_mpi.jpg` *(Hình 1 — Slide 5)*

---

## 1. Mục tiêu đoạn thuyết trình này
Mở màn gọn gàng (giới thiệu nhóm & bố cục 4 phần tại Slide 1–2) và trình bày kỹ **3 slide nền tảng (Slide 3–5)** trước khi chuyển sang 5 mô hình song song & thực nghiệm:
1. **Bối cảnh & 3 khoảng trống nghiên cứu (Slide 3 — Mục 1.1–1.2):** HPC có 2 trụ cột chia sẻ/phân tán; mã song song dễ gặp lỗi ngầm dù biên dịch sạch; các công trình trước thiếu đánh giá đa mô hình, thiếu đo scaling thật và bỏ ngỏ hệ sinh thái công cụ.
2. **Mục tiêu, 3 câu hỏi RQ & Đóng góp (Slide 4 — Mục 1.3–1.4):** 4 LLM × 5 biến thể (ảnh chụp thời điểm), 3 câu hỏi RQ1–RQ3, cùng 4 đóng góp bài báo gốc + 3 đóng góp mở rộng của báo cáo nhóm.
3. **Tại sao chọn tập Mandelbrot làm phép thử? (Slide 5 — Mục 2.1):** Dễ hiểu, không cần thư viện ngoài (dùng định dạng Netpbm), nhưng có bẫy mất cân bằng tải tự nhiên cực hay.

---

## 2. Giải thích chi tiết nội dung & minh họa dùng ở Phần 1

### Slide 3: Bối cảnh & Vấn đề nghiên cứu (Mục 1.1 – 1.2)
- **Mục 1.1 (Bối cảnh):** phân biệt ngắn 2 trụ cột HPC (*bộ nhớ chia sẻ*: nhiều luồng chung RAM, lo đồng bộ/tranh chấp; *bộ nhớ phân tán*: nhiều nút trao đổi thông điệp, lo độ trễ/băng thông). Nhấn sự phong phú của C++11/17/20, OpenMP, MPI làm mở rộng không gian lỗi — đánh giá LLM ở mã HPC khó hơn mã tuần tự rất nhiều.
- **Mục 1.2 (Vấn đề & 3 khoảng trống):** nêu rõ 3 thiếu hụt của nghiên cứu trước (`LLM4HPC`, `HPC-Coder-v2`, `OMPGPT`, `MPIRigen`): (1) chỉ xét 1 mô hình đơn lẻ, (2) hay dừng ở tỉ lệ biên dịch thay vì đo scaling trên cụm HPC thật, (3) ít kiểm chứng hiểu biết về trình biên dịch/backend thư viện.
- **Vai trò Mandelbrot:** đóng vai trò *benchmark tối thiểu có kiểm soát* (không cần bộ giải số ngoài) để cô lập thuần năng lực sinh mã song song của LLM.

### Slide 4: Mục tiêu, 3 Câu hỏi RQ & Đóng góp (Mục 1.3 – 1.4)
- **Mục 1.3:** nhấn rõ 4 LLM (ChatGPT-4, ChatGPT-5, Claude, LLaMA) là *ảnh chụp tại một thời điểm*, không phải xếp hạng vĩnh viễn. Đọc mạch lạc 3 câu hỏi: **RQ1** (biên dịch), **RQ2** (lỗi thực thi/ngữ nghĩa & nguyên nhân gốc), **RQ3** (mở rộng & so với mã con người).
- **Mục 1.4:** phân tách rõ **4 đóng góp của bài gốc** (bộ prompt nhất quán, phân tích lỗi chi tiết, đánh giá C++20 coroutine đang tích hợp vào Kokkos/HPX, phân loại lỗi & giới hạn LLM) và **3 đóng góp mở rộng của báo cáo nhóm** (giải thích nguyên nhân gốc từ lý thuyết, phân tầng 6 lớp lỗi, quy trình/danh mục kiểm duyệt thực dụng kèm demo & Gemini 4).

### Minh họa: Hình 1 — Tập Mandelbrot (`mandelbrot_coroutine.png` và `mandelbrot_mpi.jpg` — Slide 5)
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
