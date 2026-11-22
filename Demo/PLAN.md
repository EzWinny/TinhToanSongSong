# Kế hoạch Demo — Báo cáo LLM-HPC++ (Tập Mandelbrot)

## 1. Mục tiêu

Trong 15–20 phút, chứng minh 3 kết luận chính của báo cáo:

1. Cùng một prompt sinh ra 5 biến thể song song C++ (C++11 async, C++17 algorithms, C++20 coroutines, OpenMP, MPI+OpenMP).
2. Lỗi nguy hiểm nằm ở **ngữ nghĩa và toolchain**, không phải cú pháp: nhầm TBB/OpenMP, `final_suspend`, P4/P5, `MPI_Gather`.
3. Phải **đo mới biết** chương trình có tôn trọng số luồng hay không.

## 2. Định dạng và môi trường

- Thời lượng 15–20 phút, 1 người thuyết trình + 1 người chạy (nếu có 2 người).
- Máy local: Windows, g++ 16.2.0 (MinGW-W64), OpenMP hoạt động (`-fopenmp`); cmake có sẵn.
- **Không có MPI trên máy local** → phần phân tán dùng ảnh/biểu đồ có sẵn trong báo cáo, không chạy live.
- Lưu ý: báo cáo đo trên GCC 11.5.0 + Intel TBB 2022.2. Máy local dùng GCC 16.2.0 nên lỗi "backend TBB" **không tái hiện được ở đây** — chỉ trình chiếu slide cho lỗi này.

## 3. Chuẩn bị (xong trước demo 1 ngày)

- [ ] `Demo/mandelbrot/` — 2 chương trình tự viết, tối giản: `mandel_seq.cpp` và `mandel_omp.cpp` (cùng hàm `escape()`, khác nhau ở vòng lặp).
- [ ] `Demo/run_demo.bat` — biên dịch (`g++ -O2 -fopenmp`) và chạy với `-t 1,2,4,8,16`; xuất ảnh PGM.
- [ ] `Demo/plot_speedup.py` — đọc thời gian, vẽ biểu đồ speedup bằng matplotlib.
- [ ] Ảnh tham chiếu có sẵn: `Report/Bao-cao-LLM-HPC-LaTeX/figures/mandelbrot_coroutine.png`, `mandelbrot_mpi.jpg`.
- [ ] Slide (3 ảnh có sẵn): `fig_timeline.png`, `fig_scaling_shared.png`, `fig_loc.png`.
- [ ] Dự phòng: quay màn hình các lệnh chạy để chiếu nếu máy chiếu/laptop lỗi.
- [ ] Chạy thử với ảnh `800×600`, 300 vòng lặp (nhẹ hơn cấu hình báo cáo `1920×1080`, 1000 vòng) để demo không bị chậm.

## 4. Kịch bản trình chiếu

| Phút | Nội dung | Thao tác |
|------|----------|----------|
| 0–2 | Mở đầu | Hỏi khán giả: "Có tham số `-t` có nghĩa là dùng đúng số luồng?" |
| 2–5 | Bài toán và 5 biến thể | Chiếu ảnh Mandelbrot; giải thích "song song hiển nhiên"; chạy bản tuần tự và OpenMP, mở ảnh kết quả. |
| 5–10 | 3 lỗi điển hình | (a) đặt `OMP_NUM_THREADS` nhưng backend là TBB → đường phẳng (chỉ chiếu slide); (b) coroutine treo do `suspend_never` (chiếu code + giải thích); (c) ảnh đen do tính màu P5 nhưng ghi P4 (chiếu ảnh). |
| 10–15 | Đo mở rộng live | Chạy `-t 1,2,4,8,16`, ghi thời gian (loại I/O), vẽ speedup ngay tại chỗ; so với đường mã con người trong báo cáo. |
| 15–18 | Phân tán | Chiếu Hình 7 (1–12 nút); giải thích giảm tốc ở bước 2→4 nút và vì sao mã con người vẫn dẫn đầu. |
| 18–20 | Kết luận + Q&A | 3 khuyến nghị: coi mã LLM là bản nháp; đo thay vì tin cờ; soát coroutine/MPI. |

## 5. Phiên bản tối thiểu (nếu thiếu thời gian)

Chỉ cần `mandel_seq.cpp` + `mandel_omp.cpp`, chạy 1→N lõi và vẽ 1 đường speedup. Mọi lỗi còn lại chiếu slide sẵn có.

## 6. Rủi ro và dự phòng

| Rủi ro | Dự phòng |
|--------|----------|
| Không có MPI | Dùng biểu đồ có sẵn, không chạy live |
| GCC local khác bản báo cáo | Không demo lỗi TBB live, chỉ chiếu slide |
| Ảnh lớn chạy chậm | Giảm còn 800×600, 300 vòng lặp |
| Thời gian đo nhiễu | Chạy 3 lần, lấy trung bình |
| Lỗi máy chiếu | Quay sẵn video các lệnh chạy |

## 7. Tiêu chí thành công

- Khán giả trả lời được 3 câu: backend TBB, `done()`/`final_suspend`, P4 vs P5.
- Có ít nhất 1 biểu đồ speedup thu được ngay trong buổi demo.
