# AGENTS.md

## Hard rule

- **Hỏi người dùng trước khi `git commit` hoặc `git push` bất cứ thứ gì lên GitHub.** Kể cả commit "rõ ràng" hay push lên branch hiện tại. Được tự do sửa file và `git add`, nhưng chỉ commit/push sau khi có xác nhận.

## Cấu trúc repo

- Đây là repo tài liệu + demo môn Tính toán song song, **không phải ứng dụng**: không có build system, test, lint hay CI — đừng tốn thời gian tìm.
- `Report/` là nguồn thật của báo cáo. `Bao-cao-LLM-HPC-Mandelbrot.pdf` là sản phẩm sinh ra; sửa `main.tex` và `sections/*.tex`, thêm ảnh vào `figures/`. Các ghi chú/giải trình nằm ở `Report/docs/`.
- `Report/LLM.pdf` là bài báo gốc. Báo cáo LaTeX (`main.tex`) là bản phân tích mở rộng; bản `.docx` cũ đã bị xóa khỏi repo.
- `Demo/` là demo Mandelbrot chạy được (tuần tự + OpenMP). `Slides/` hiện chỉ có README.
- `.agents/` và `.serena/` là thư mục công cụ nội bộ, đã nằm trong `.gitignore` — không đụng vào.

## Biên dịch báo cáo

- Chạy XeLaTeX **từ bên trong** `Report/`:
  `xelatex -interaction=nonstopmode main.tex`
- **Chạy 2–3 lần (đến khi số trang Mục lục ổn định).** Lần đầu luôn báo `Citation ... undefined` / `Reference ... undefined` và số trang sai — bỏ qua, chỉ kiểm tra lần cuối. Dùng `pdflatex` sẽ lỗi (cần `fontspec`, Times New Roman, babel tiếng Việt).
- Model không đọc trực tiếp được file PDF ở môi trường này. Để kiểm tra PDF dùng Python `pymupdf` (`len(doc)`, `page.get_text()`), không dùng công cụ Read.

## Demo

- `Demo/run_demo.bat` là bản chạy nhanh, không tương tác: biên dịch 2 chương trình, chạy `-t 1,2,4,8,16`, ghi `mandelbrot/results.txt`, vẽ `speedup.png`.
- `Demo/interactive.py` là bản demo tương tác (menu 1–6): chạy `python interactive.py` từ thư mục `Demo/`. Tự compile, lặp 3 lần lấy trung bình, vẽ biểu đồ, đổi PGM→PNG bằng Pillow để mở ảnh. Cần `matplotlib` + `Pillow` (đều có sẵn).
- `mandel_omp.cpp` nhận `-s static|dynamic|guided`, `-b <chunk>` và `--ignore-t` (cố tình bỏ qua `-t`, dùng `omp_get_num_procs()`) để tái hiện lỗi "có tham số nhưng không dùng" trong báo cáo. Đừng xóa flag này — nó là phần tương tác chính.
- Hai chương trình dùng chung `Demo/mandelbrot/mandel.h`; giữ `render_rows()` giống hệt để ảnh đầu ra khớp nhau. Phép đo thời gian phải loại I/O ghi ảnh.
- PowerShell **không** chạy `.exe` từ thư mục hiện tại nếu thiếu `.\`: dùng `.\mandel_omp.exe -t 8 ...`, không phải `mandel_omp.exe ...`. (Trong file `.bat` thì không cần.)
- Máy local: MinGW-W64 g++ 16.2.0, có OpenMP, **không có MPI** — đừng hứa demo MPI live. Các lỗi TBB/GCC 11.5 của bài báo cũng không tái hiện được ở đây (chỉ chiếu slide).

## Quy ước báo cáo

- Viết tiếng Việt. Mọi `\bibitem` trong `sections/08-tai-lieu.tex` phải có `\cite` tương ứng (hiện 20 nguồn).
- Bảng giải trình tài liệu và kết quả tra cứu bài mới nằm ở `Report/docs/` (`giai-trinh-tai-lieu.md`, `nghien-cuu-bai-moi-hon.md`). Đọc trước khi đổi tên tác giả, danh sách tài liệu tham khảo hoặc mục 2.7.
- File sinh ra (`*.aux`, `*.log`, `*.toc`, `*.lof`, `*.lot`, `*.out`, `*.exe`, `*.pgm`, `results.txt`, `speedup.png`) đã được ignore — không commit.

## Git

- Remote `origin` = github.com/EzWinny/TinhToanSongSong. Branch hiện tại `main` (đã merge `report-update`); tag `checkpoint-before-fixes` đánh dấu trạng thái trước đợt sửa báo cáo.
- Nhắc lại: mọi commit/push đều phải hỏi trước (xem Hard rule).
