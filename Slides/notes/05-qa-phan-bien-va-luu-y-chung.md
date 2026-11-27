# Bộ câu hỏi Q&A, Phản biện & Lưu ý chung cho cả nhóm

- **Phục vụ cho đoạn:** **Phần Hỏi – Đáp (Q&A) & Phản biện cuối buổi** *(toàn bộ 4 thành viên)*
- **Nguồn tổng hợp:** Phụ lục C (*Câu hỏi vấn đáp và phản biện*), Phần 4–5 (6 điểm lệch nội tại của `LLM.pdf`, giải thích đồ thị Hình 5–6–8) và các câu hỏi thực tế hay gặp khi bảo vệ bài tập lớn môn Tính toán song song.

---

## 1. Phân vai trả lời nhanh khi giảng viên đặt câu hỏi
| Nhóm câu hỏi | Người chính trả lời | Người hỗ trợ |
|---|---|---|
| Bối cảnh, khoảng trống nghiên cứu, tập Mandelbrot, định dạng PBM/PGM | **Trần Lý Dũng** *(Phần 1)* | Nguyễn Quang Anh |
| Tiến hóa C++11/17/20, 5 cơ chế song song, prompt P1–P3, cụm `rostam`, Demo `interactive.py` & `eval_llm.py` | **Nguyễn Quang Anh** *(Phần 2)* | Nguyễn Như Bảo |
| Chi tiết lỗi ChatGPT-4/5, Claude, LLaMA, 6 điểm lệch số liệu, LOC/COCOMO | **Đồng Đức Dương** *(Phần 3)* | Nguyễn Quang Anh |
| Đọc đồ thị Hình 5/6/8, `pixel updates/s`, so sánh mã con người, Gemini 4, khuyến nghị | **Nguyễn Như Bảo** *(Phần 4)* | Nguyễn Quang Anh |

---

## 2. 12 câu hỏi "tủ" giảng viên hay hỏi & Gợi ý trả lời 30 giây

### Câu 1: Vì sao một chương trình biên dịch 100% mà chỉ 20% chạy không lỗi (ChatGPT-4)?
- **Trả lời:** Vì trình biên dịch chỉ kiểm tra cú pháp và kiểu tĩnh, không kiểm tra được ngữ nghĩa song song hay giao diện dòng lệnh. Ví dụ ChatGPT-4 in đầy đủ hướng dẫn CLI nhưng chỉ parse mỗi `-t` (bỏ qua mọi tham số khác), và đặt sai `OPENMP_NUM_THREADS` cho `std::execution::par` dù GCC dùng Intel TBB.

### Câu 2: GCC dùng backend nào cho `std::execution::par`? Đặt số luồng thế nào mới đúng?
- **Trả lời:** Trên Linux/GCC (`libstdc++`), C++17 parallel algorithms dùng **Intel TBB** (không phải OpenMP). Vì vậy `OMP_NUM_THREADS` (hay `OPENMP_NUM_THREADS`) hoàn toàn bị phớt lờ; cách đúng theo chuẩn TBB là dùng đối tượng `tbb::global_control(tbb::global_control::max_allowed_parallelism, num_threads)`.

### Câu 3: Vì sao coroutine của Claude bị treo vô hạn ở vòng `while (!done())`?
- **Trả lời:** Trong C++20, `coroutine_handle::done()` chỉ trả về `true` khi coroutine **tạm dừng ở điểm treo cuối (`final_suspend`)**. Claude viết `final_suspend() { return std::suspend_never{}; }` nên frame tự hủy luôn thay vì dừng lại, khiến vòng lặp chờ `done()` không bao giờ kết thúc. Đổi sang `std::suspend_always` là khắc phục được.

### Câu 4: Phân biệt P4 và P5? Vì sao sai định dạng lại ra ảnh đen mà không báo lỗi?
- **Trả lời:** **P4 (PBM nhị phân)** dùng **1 bit/pixel** (8 pixel đóng gói trong 1 byte, 0 = trắng, 1 = đen); **P5 (PGM nhị phân)** dùng **1 byte/pixel** (giá trị xám `0..255`). LLaMA tính mảng byte kiểu P5 nhưng lại ghi header `P4` → trình đọc ảnh đọc nhầm byte màu xám thành từng chuỗi bit đen đặc nên ra ảnh đen toàn phần mà chương trình vẫn thoát bình thường (`exit 0`).

### Câu 5: Vì sao `MPI_Gather` dễ gây segfault và khi nào phải dùng `MPI_Gatherv`?
- **Trả lời:** `MPI_Gather` bắt buộc **mọi tiến trình gửi đúng cùng một số phần tử (`sendcount`)**. Nếu chiều cao ảnh $H$ không chia hết cho số tiến trình $P$ (hoặc một rank tính nhiều hơn 1 hàng), kích thước bộ đệm nhận/gửi lệch nhau sẽ đọc/ghi tràn bộ nhớ gây segfault. Dùng `MPI_Gatherv` (truyền mảng `recvcounts` và `displs`) an toàn cho mọi $H$ và $P$.

### Câu 6: Nhìn Hình 5 (Hình 6 gốc), làm sao phân biệt "đường phẳng do lỗi" với "đường phẳng do thang đo"?
- **Trả lời:**
  - **Đường phẳng nằm CAO** (vd: Claude, ChatGPT-4, LLaMA ở Hình 5b; LLaMA ở Hình 5c): là **lỗi bỏ qua `-t`**, luôn dùng full 20 lõi kể cả khi truyền `-t 1`.
  - **Đường phẳng nằm SÁT TRỤC `0`** (vd: Human, ChatGPT-5, Claude ở Hình 5a và 5d): **vẫn mở rộng tốt**, nhưng thông lượng ở mức `~10⁷` bị nén sát đáy khi vẽ chung trên thang tuyến tính `×10⁹` với đường đạt `6×10⁹`.

### Câu 7: Vì sao trên Hình 6 (MPI+OpenMP phân tán), cả 4 LLM đều chững tăng tốc ở bước `2 → 4` nút còn mã con người thì không?
- **Trả lời:** Tập Mandelbrot đối xứng qua trục thực ($y=0$). Khi chia tĩnh thành 2 dải hàng trên/dưới (2 nút), tải hai nút bằng nhau tuyệt đối. Khi chia tĩnh thành 4 dải (4 nút), **2 dải giữa ôm gần trọn phần ruột tập đen (chạm 1000 vòng)** còn 2 dải rìa rất nhẹ → nút chậm nhất chặn toàn hệ thống trước `MPI_Gather`. Mã con người tránh được nhờ phân vùng cân bằng tải tốt hơn (và `mpi_omp.cpp` của Gemini 4 cũng chủ động chia *block-cyclic*).

### Câu 8: "Mã con người (`Human [5]`)" lấy ở đâu ra và so sánh kiểu gì?
- **Trả lời:** Trong bài báo gốc, `Human [5]` là **5 chương trình C++ thật** từ sách *Parallel C++* (Diehl et al., 2024), biên dịch và chạy trên **cùng cụm `rostam`** với mã LLM. Ở thử nghiệm bổ sung Gemini 4 trên máy local (12 luồng), nhóm dùng `Demo/mandelbrot/mandel_omp.cpp` làm mốc tham chiếu cục bộ trên cùng phần cứng và trình biên dịch GCC 13.2.0.

### Câu 9: Trên Hình 8a (Gemini 4), tại sao thông lượng của `mandel_omp.cpp` (`5,36×10⁷` px/s) cao hơn `openmp.cpp` (`3,23×10⁷`) và `async`/`coroutine` (`1,75–1,85×10⁷`) dù speedup ngang nhau?
- **Trả lời:** Do **prompt gốc P1/P2 không cố định tọa độ mặt phẳng phức**: `mandel_omp.cpp` phủ vùng phức diện tích `16,0` (nhiều điểm nền thoát sớm sau 1–3 vòng), còn `openmp.cpp` phủ diện tích `9,0` (hẹp hơn `1,78×`) và `async.cpp` phủ `5,06` (phóng sát gấp `3,16×` vào ruột tập Mandelbrot). Quy đổi theo diện tích khung nhìn thì hiệu năng tính thuần của Gemini 4 tương đương mốc con người.

### Câu 10: Vì sao bảng kết quả báo cáo ghi `40% / 60%` và nhắc lỗi ký hiệu ở Hình 5d?
- **Trả lời:** Khi đọc kỹ `LLM.pdf`, nhóm phát hiện **6 điểm không nhất quán nội tại trong chính bài báo gốc** (Bảng III in 40% trong khi đếm Bảng I–II là 3/5 = 60%; văn bản Mục VIII.A nói ChatGPT-5 thắng ở OpenMP nhưng Hình 6d gốc lại vẽ ký hiệu ô vuông `■` của ChatGPT-4; Mục VI.A.1 ghi 24 lõi còn phần cứng thực tế là 20 lõi...). Nhóm giữ nguyên số gốc để trung thực nhưng chú thích rõ để người đọc kiểm chứng.

### Câu 11: Tại sao không chạy demo MPI và C++17 TBB trực tiếp trên máy thuyết trình?
- **Trả lời:** Máy trình chiếu chạy Windows 11 với MinGW-W64 GCC 13.2.0 (có sẵn OpenMP và C++20 coroutines) nhưng không cài Intel TBB và không có cụm MPI nhiều nút. Nhóm tách rõ phạm vi: demo trực tiếp OpenMP + tái hiện lỗi `--ignore-t` + chạy thử nghiệm Gemini 4 (bộ nhớ chia sẻ), còn `par_algo.cpp` kiểm chứng hành vi cảnh báo khi thiếu TBB và `mpi_omp.cpp` kiểm duyệt tĩnh theo danh mục Bảng 12.

### Câu 12: Mô hình COCOMO có thực sự phù hợp để đánh giá mã HPC không?
- **Trả lời:** Không hoàn toàn. COCOMO ước lượng công sức theo số dòng mã tuần tự (KLOC), bỏ qua chi phí gỡ lỗi đồng bộ, race condition, vòng đời coroutine hay tối ưu truyền thông MPI. Như bài báo gốc thừa nhận, chưa có mô hình chi phí chuẩn riêng cho HPC nên COCOMO chỉ dùng làm thước đo tương đối giữa các biến thể cùng bài toán.

---

## 3. Checklist 5 phút trước giờ thuyết trình
- [ ] Kiểm tra 2 file PDF thành phẩm đã mở sẵn (hoặc chọn sẵn bản nộp):
  - Bản gốc (49 trang): `Report/Bao-cao-LLM-HPC-Mandelbrot.pdf`
  - Bản mở rộng có Gemini 4 (52 trang): `Report/Bao-cao-LLM-HPC-Mandelbrot-bo-sung-Gemini4.pdf`
- [ ] Mở sẵn PowerShell ở `Demo/`, chạy `deactivate` nếu thấy `(.venv)`, test nhanh `python interactive.py` (Menu 1 & 4) và đóng trình xem ảnh `speedup.png` / `mandel_view.png`.
- [ ] Để sẵn `Demo/run_demo.bat` làm phương án dự phòng nếu thiếu thời gian.
- [ ] Thống nhất thời lượng từng người (tổng ~21–24 phút + Q&A):
  - **Phần 1 (Dũng — Slide 1–4):** ~3–3,5 phút
  - **Phần 2 + Demo (Quang Anh — Slide 5–10):** ~7–8 phút
  - **Phần 3 (Dương — Slide 11–14):** ~5–6 phút
  - **Phần 4 (Bảo — Slide 15–20):** ~6–7 phút
