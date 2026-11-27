# Tài liệu thuyết trình & Ghi chú minh họa (`Slides/`)

Thư mục này chứa toàn bộ tài liệu hướng dẫn, dàn ý 20 slide, chú thích hình vẽ/bảng biểu và lưu ý kỹ thuật cho 4 thành viên khi thiết kế slide và thuyết trình đề tài **Đánh giá mã C++ hiện đại và MPI+OpenMP do LLM sinh cho bài toán tập Mandelbrot có khả năng mở rộng**.

> **Slide thành phẩm (LaTeX Beamer 16:9, 20 trang):** [`Slide-LLM-HPC-Mandelbrot.pdf`](Slide-LLM-HPC-Mandelbrot.pdf) — mã nguồn: [`slides.tex`](slides.tex)  
> **Xem nhanh dàn ý chi tiết từng slide (Slide 1 – Slide 20):** [`outline-slides.md`](outline-slides.md)

### Biên dịch lại slide (nếu chỉnh sửa `slides.tex`)
Chạy pdfLaTeX **2 lượt** từ bên trong thư mục `Slides/` (dùng phông Latin Modern Sans T5 chuẩn Beamer tiếng Việt, để số tổng trang `X/20` và thanh tiến trình khớp):
```powershell
cd Slides
pdflatex -interaction=nonstopmode slides.tex
pdflatex -interaction=nonstopmode slides.tex
```
*(Sau khi biên dịch, đổi tên `slides.pdf` thành `Slide-LLM-HPC-Mandelbrot.pdf`.)*

---

## 1. Bản đồ phân công — File nào phục vụ cho đoạn nào?

| Thứ tự trình bày | Đoạn thuyết trình | Người thuyết trình (MSSV) | File ghi chú chi tiết | Phần tương ứng trong báo cáo | Thời lượng gợi ý |
|---|---|---|---|---|---|
| **1** | **Phần 1 • Giới thiệu bài toán** *(Slide 1–4)* | Trần Lý Dũng (`24001658`) | [`notes/01-phan-1-gioi-thieu-bai-toan.md`](notes/01-phan-1-gioi-thieu-bai-toan.md) | Phần 1 (*Giới thiệu*) & Mục 2.1 (*Tập Mandelbrot*) | ~3–3,5 phút |
| **2** | **Phần 2 • 5 mô hình, Thực nghiệm & Demo** *(Slide 5–10)* | Nguyễn Quang Anh (`24001649` — Trưởng nhóm) | [`notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md)<br>*(Lời nói + giải thích OpenMP/MPI/5 biến thể: [`notes/02b-kich-ban-noi-quang-anh.md`](notes/02b-kich-ban-noi-quang-anh.md))* | Mục 2.2–2.7 (*C++ & 5 mô hình*), Phần 3 (*Phương pháp*) & `Demo/` | ~7–8 phút |
| **3** | **Phần 3 • Phân tích lỗi thực tế** | Đồng Đức Dương (`24001659`) | [`notes/03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md) | Phần 4.1–4.5 (*Kết quả & lỗi, LOC/COCOMO*) & Phần 5.1–5.5 | ~5–6 phút |
| **4** | **Phần 4 • Hiệu năng & tổng kết** *(+ Gemini 4)* | Nguyễn Như Bảo (`24001655`) | [`notes/04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) | Phần 4.6–4.9 (*Mở rộng, Mã con người, Gemini 4*), Phần 5.6–5.7 & Phần 6 | ~6–7 phút |
| **5** | **Hỏi – Đáp (Q&A) & Phản biện** | **Cả 4 thành viên** | [`notes/05-qa-phan-bien-va-luu-y-chung.md`](notes/05-qa-phan-bien-va-luu-y-chung.md) | Phụ lục C + toàn bộ báo cáo | ~5–10 phút |
| **Bổ trợ** | **Giải thích nhanh: `static` / `dynamic` / `guided`** | **Cả 4 thành viên** | [`notes/06-giai-thich-lap-lich-openmp.md`](notes/06-giai-thich-lap-lich-openmp.md) | Mục 2.3 (OpenMP), Demo Menu 3 & Hình 6 (MPI) | Tra cứu nhanh |

---

## 2. Tra cứu nhanh: Minh họa (`Report/figures/`) → Phục vụ cho đoạn nào?

| Minh họa trong báo cáo | File ảnh gốc | Phục vụ cho đoạn | Xem giải thích chi tiết tại |
|---|---|---|---|
| **Hình 1** — Tập Mandelbrot (coroutine vs MPI) | `Report/figures/mandelbrot_coroutine.png`, `mandelbrot_mpi.jpg` | Phần 1 (Giới thiệu bài toán) | [`01-phan-1-gioi-thieu-bai-toan.md`](notes/01-phan-1-gioi-thieu-bai-toan.md) |
| **Hình 2** — Dòng thời gian tính năng song song C++ | `Report/figures/fig_timeline.png` | Phần 2 (5 mô hình, Thực nghiệm & Demo) | [`02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md) |
| **Demo trực tiếp** (`interactive.py`, `speedup.png`, `mandel_view.png`) | `Demo/interactive.py` *(dự phòng `Demo/run_demo.bat`)* | Phần 2 (Kiến trúc thực nghiệm & Demo) | [`02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md) |
| **Hình 3** — Số dòng mã LOC (4 biến thể bộ nhớ chia sẻ) | `Report/figures/fig_loc.png` | Phần 3 (Phân tích lỗi thực tế) | [`03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md) |
| **Hình 4** — Chất lượng & công sức COCOMO | `Report/figures/fig_cocomo.png` | Phần 3 (Phân tích lỗi thực tế) | [`03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md) |
| **Hình 5** — Mở rộng trên 1 nút (1–20 lõi, `pixel updates/s`) | `Report/figures/fig_scaling_shared.png` | Phần 4 (Hiệu năng & tổng kết) | [`04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) |
| **Hình 6** — Mở rộng phân tán (1–12 nút, thang log₂) | `Report/figures/fig_scaling_dist.png` | Phần 4 (Hiệu năng & tổng kết) | [`04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) |
| **Hình 7** *(bản mở rộng)* — 4 ảnh P4 của Gemini 4 Hydrogen | `Report/figures/fig_gemini4_mandelbrot.png` | Phần 4 (Hiệu năng & tổng kết — Mục 4.9) | [`04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) |
| **Hình 8** *(bản mở rộng)* — Mở rộng 1 nút (`×10⁷ px/s`) & Speedup Gemini 4 | `Report/figures/fig_gemini4_scaling.png` | Phần 4 (Hiệu năng & tổng kết — Mục 4.9) | [`04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md) |

---

## 3. Tra cứu nhanh: Các bảng số liệu quan trọng trong báo cáo

- **Bảng 1:** Phân công công việc (4 thành viên + MSSV) → Slide giới thiệu nhóm.
- **Bảng 2:** So sánh 4 cơ chế song song C++ → [`02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md).
- **Bảng 4 & Bảng 5:** Ma trận 4×5 & cấu hình cụm `rostam` → [`02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](notes/02-phan-2-kien-truc-thuc-nghiem-va-demo.md).
- **Bảng 6, 7, 8, 9:** Tỉ lệ thành công, 19 lỗi tiêu biểu, phân loại lỗi, LOC MPI+OpenMP → [`03-phan-3-phan-tich-loi-thuc-te.md`](notes/03-phan-3-phan-tich-loi-thuc-te.md).
- **Bảng 10, 11, 12:** So sánh với mã con người, tổng hợp Gemini 4 Hydrogen *(bản mở rộng)*, danh mục kiểm duyệt mã song song → [`04-phan-4-hieu-nang-va-tong-ket.md`](notes/04-phan-4-hieu-nang-va-tong-ket.md).
