# Ghi chú thuyết trình — Phần 2: Kiến trúc thực nghiệm & Demo

- **Phục vụ cho đoạn:** **Phần 2 • Kiến trúc thực nghiệm** *(kèm minh họa demo trực tiếp, dự kiến ~5–7 phút)*
- **Người thuyết trình phụ trách:** Nguyễn Quang Anh (`24001649` — Trưởng nhóm)
- **Tài liệu báo cáo tương ứng:** Phần 3 (*Phương pháp đánh giá*, Mục 3.1–3.7) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf` và thư mục `Demo/` (`Demo/interactive.py`, `Demo/PLAN.md`, `Demo/eval_llm.py`)
- **Tệp bảng / mã / công cụ sử dụng:**
  - **Bảng 4** (*Ma trận thực nghiệm: 4 LLM × 5 biến thể = 20 chương trình*)
  - **Bảng 5** (*Cấu hình cụm `rostam` của bài báo gốc*)
  - 3 prompt nguyên văn **P1, P2, P3** (Mục 3.3)
  - Bộ demo tương tác: `Demo/interactive.py` (dự phòng: `Demo/run_demo.bat`)

---

## 1. Mục tiêu đoạn thuyết trình này
1. Trình bày rõ **cách bài báo gốc tổ chức thí nghiệm** (4 LLM × 5 biến thể, 3 prompt P1–P3, quy trình 4 bước kiểm định, độ đo `pixel updates/s`, môi trường cụm `rostam`).
2. Thực hiện **demo tương tác ngắn trên máy cục bộ** để khán giả *tự nhìn thấy* 3 hiện tượng cốt lõi của báo cáo: tăng tốc OpenMP, mất cân bằng tải (`static` vs `dynamic`), và **bẫy "có cờ `-t` nhưng bỏ qua" (`--ignore-t`)**.

---

## 2. Chú thích các nội dung & bảng biểu trên slide

### A. Ma trận thực nghiệm (Bảng 4) & 4 mô hình LLM
- **4 LLM được đánh giá trong bài báo gốc:** ChatGPT-5, ChatGPT-4 (OpenAI), Claude (Anthropic), LLaMA (Meta, trọng số mở).
- **5 biến thể cho mỗi LLM:** C++11 async, C++17 parallel algorithms, C++20 coroutines, OpenMP (4 bản bộ nhớ chia sẻ) + MPI+OpenMP (1 bản phân tán) → tổng cộng **20 chương trình**.
- **Cách sinh mã:** mỗi cặp *(mô hình, biến thể)* chỉ sinh **1 lần duy nhất** (*zero-shot*, không nhắc lại lỗi) — ưu điểm là mô phỏng đúng người dùng phổ thông gửi một câu lệnh; hạn chế là chưa có phân tích thống kê nhiều lần chạy.

### B. 3 prompt nguyên văn P1, P2, P3 — **2 ĐIỂM CỰC KỲ CẦN NHẤN**
1. **Tại sao P3 (MPI+OpenMP) bắt buộc thêm yêu cầu cờ `-p` (số phân vùng)?**
   - Trong bài báo gốc (`LLM.pdf`, trang 3), nếu không yêu cầu rõ cấu hình số phân vùng `-p`, LLM thường sinh mã kiểu **mỗi rank MPI tự tính lại nguyên cả bức ảnh Mandelbrot** (tính lặp dư thừa, không hề chia tải phân tán!).
2. **Cả P1, P2, P3 đều KHÔNG cố định tọa độ phức, độ phân giải mặc định hay hàm tô màu:**
   - Chỉ yêu cầu: *bài toán Mandelbrot + cơ chế song song + định dạng PBM + cờ `-t`/`-p` + in thời gian loại trừ I/O*.
   - **Ý quan trọng để mở đường cho Phần 4:** vì prompt để mở nên mỗi LLM tự chọn khung nhìn mặt phẳng phức, độ phân giải mặc định hoặc tối ưu cắt tỉa khác nhau → làm thông lượng tuyệt đối giữa các mô hình có thể chênh rất lớn dù chạy cùng bài toán.

### C. Quy trình kiểm định 4 bước & Độ đo (Mục 3.4–3.5)
- **4 cổng kiểm định tuần tự:**
  1. **Biên dịch (`Build`)** với GCC 11.5.0 → nếu lỗi, ghi nhận và sửa tối thiểu để đi tiếp.
  2. **Thực thi (`Run`)** → kiểm tra crash, segfault, treo vô hạn, lỗi phân tích cờ `-t`/`-p`.
  3. **Kiểm tra ảnh (`Correctness`)** → mở ảnh PBM/PGM kiểm tra trực quan (tránh lỗi ảnh đen P4/P5).
  4. **Đo chất lượng & mở rộng (`LOC`, `COCOMO`, `Scaling`)** → đếm dòng mã bằng `cloc`, ước lượng công sức bằng `scc` (COCOMO), rồi chạy đo tăng tốc.
- **Độ đo thông lượng trung tâm của bài báo (Công thức Mục 3.5.3):**
  $$\text{Throughput} = \frac{W \cdot H}{T_{\text{compute}}} \quad (\text{pixel updates per second})$$
  - **Bắt buộc loại trừ thời gian ghi ảnh (I/O)** khỏi $T_{\text{compute}}$, nếu không phần ghi đĩa tuần tự sẽ che lấp hoàn toàn khả năng tăng tốc tính toán (định luật Amdahl).

### D. Môi trường thực nghiệm cụm `rostam` (Bảng 5) vs Máy demo cục bộ
- **Cụm `rostam` (ĐH Bang Louisiana — LSU, bài báo gốc):** 16 nút `medusa`, mỗi nút 1 CPU Intel Xeon Gold 6148 **20 lõi**, 92 GB RAM; GCC 11.5.0, Intel TBB 2022.2, OpenMPI 5.0.7.
  - Bộ nhớ chia sẻ: quét `1 → 20` lõi trên 1 nút.
  - Bộ nhớ phân tán: ảnh `12000 × 80000`, `1000` vòng lặp, quét `1, 2, 4, 8, 12` nút (mỗi nút 1 rank MPI × 20 lõi OpenMP).
- **Máy demo cục bộ của nhóm:** Windows 11, CPU **12 luồng logic**, MinGW-W64 GCC 13.2.0 (`E:\Strawberry\c\bin\g++.exe`), có OpenMP + C++20, **không có Intel TBB và MPI** → **nói rõ ngay từ đầu** rằng demo live minh họa phần OpenMP (và kiểm chứng bổ sung Gemini 4 ở cuối Phần 4), còn phần MPI/TBB trình bày qua số liệu bài báo gốc.

---

## 3. Kịch bản chạy Demo trực tiếp (2–3 phút, rút gọn từ `Demo/PLAN.md`)

### Chuẩn bị trước khi lên bảng (bắt buộc kiểm tra!)
```powershell
cd "e:\Code stuffs\Universal-projects\TinhToanSongSong\Demo"
deactivate          # QUAN TRỌNG: thoát .venv nếu đang bật, vì matplotlib/Pillow nằm ở Python hệ thống
python interactive.py
```
- **Lưu ý kỹ thuật:** nếu lỡ đang mở `speedup.png` trong Windows Photos, script đã tự chống lỗi `Errno 22` bằng cách lưu sang `speedup_1.png`, nhưng tốt nhất cứ đóng sẵn trình xem ảnh trước khi demo.
- **Dự phòng nếu terminal trục trặc:** chạy `.\run_demo.bat` (~1 phút, tự biên dịch + đo + vẽ `speedup.png`).

### Trình tự 4 bước demo gọn, có tương tác với lớp
1. **Menu 1 — Tuần tự vs OpenMP** *(nhấn Enter dùng mặc định `800×600, 300 vòng`, `-t 8`)*:
   - Hỏi lớp: *"Theo mọi người 8 luồng nhanh hơn bản tuần tự mấy lần?"* → Chạy cho thấy speedup thật (lặp 3 lần lấy trung bình, đã loại I/O).
2. **Menu 5 — Mở ảnh kết quả** *(gõ `omp`)*:
   - Mở `mandel_view.png` cho lớp thấy tập Mandelbrot rõ biên, vùng đen đặc ở giữa chính là nơi tốn nhiều vòng lặp nhất.
3. **Menu 3 — So sánh `static` / `dynamic` / `guided`** *(gợi ý `400×300, 1000 vòng`, chunk `0`, `8` luồng)*:
   - Minh họa trực tiếp lý thuyết Phần 1: vì Mandelbrot mất cân bằng tải tự nhiên nên `dynamic`/`guided` nhanh hơn `static` rõ rệt.
4. **Menu 4 — Chế độ LỖI: bỏ qua `-t` (`--ignore-t`)** *(khoảnh khắc "a-ha"!)*:
   - Hỏi lớp: *"Nếu mình gõ `-t 1`, `-t 2`, `-t 4`, `-t 8` vào chương trình có hỗ trợ cờ `-t`, số luồng thực tế có chắc chắn là 1, 2, 4, 8 không?"*
   - Chạy Menu 4 → terminal in song song bản đúng (tăng theo `-t`) và bản lỗi (`--ignore-t`, luôn dùng đủ 12 luồng dù gõ `-t 1`!) và xuất biểu đồ **đường phẳng nằm ngang** (`speedup.png`).
   - Chốt câu nối: *"Đây chính xác là loại lỗi tinh vi mà LLM mắc phải dù chương trình biên dịch 100% không một lỗi cú pháp!"*

---

## 4. Câu chuyển mượt sang Phần 3 (Đồng Đức Dương)
> *"Qua demo vừa rồi, chúng ta thấy một chương trình hoàn toàn có thể biên dịch sạch, nhận đủ cờ dòng lệnh mà vẫn sai hành vi song song bên trong. Vậy khi chạy 20 chương trình do 4 LLM sinh ra trên cụm HPC thật, những lỗi cụ thể nào đã xảy ra? Mời bạn Đức Dương trình bày Phần 3: Phân tích lỗi thực tế."*
