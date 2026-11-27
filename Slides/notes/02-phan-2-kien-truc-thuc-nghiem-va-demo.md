# Ghi chú thuyết trình — Phần 2: 5 mô hình song song, Kiến trúc thực nghiệm & Demo

- **Phục vụ cho đoạn:** **Phần 2 • 5 mô hình, Thực nghiệm & Demo** *(Slide 6–11, kèm minh họa demo trực tiếp, dự kiến ~7–8 phút)*
- **Người thuyết trình phụ trách:** Nguyễn Quang Anh (`24001649` — Trưởng nhóm)
- **Kịch bản lời nói đầy đủ + Giải thích OpenMP, MPI & 5 biến thể:** [`02b-kich-ban-noi-quang-anh.md`](02b-kich-ban-noi-quang-anh.md)
- **Tài liệu báo cáo tương ứng:** Mục 2.2–2.7 (*C++ hiện đại & 5 mô hình song song*), Phần 3 (*Phương pháp đánh giá*, Mục 3.1–3.7) trong `Report/Bao-cao-LLM-HPC-Mandelbrot*.pdf` và thư mục `Demo/` (`Demo/interactive.py`, `Demo/PLAN.md`, `Demo/eval_llm.py`)
- **Tệp hình ảnh / bảng / công cụ sử dụng:**
  - `Report/figures/fig_timeline.png` *(Hình 2 — Slide 6)*
  - Tóm tắt **Bảng 2** (*So sánh các cơ chế song song trong C++, OpenMP, MPI+OpenMP* — Slide 7)
  - **Bảng 4** (*Ma trận thực nghiệm: 4 LLM × 5 biến thể = 20 chương trình* — Slide 8)
  - **Bảng 5** (*Cấu hình cụm `rostam` của bài báo gốc* — Slide 8)
  - 3 prompt nguyên văn **P1, P2, P3** (Mục 3.3 — Slide 9)
  - Bộ demo tương tác: `Demo/interactive.py` (dự phòng: `Demo/run_demo.bat` — Slide 11)

---

## 1. Mục tiêu đoạn thuyết trình này
1. Giới thiệu nhanh **dòng tiến hóa song song trong C++11/17/20** và **5 mô hình lập trình song song** được đem vào kiểm thử (Slide 5–6, nói gọn ~1,5 phút).
2. Trình bày rõ **cách bài báo gốc tổ chức thí nghiệm** (4 LLM × 5 biến thể, 3 prompt P1–P3, quy trình 4 bước kiểm định, độ đo `pixel updates/s`, môi trường cụm `rostam` — Slide 7–9, ~3 phút).
3. Thực hiện **demo tương tác ngắn trên máy cục bộ** (Slide 10, ~2,5–3 phút) để khán giả *tự nhìn thấy* 3 hiện tượng cốt lõi của báo cáo: tăng tốc OpenMP, mất cân bằng tải (`static` vs `dynamic`), và **bẫy "có cờ `-t` nhưng bỏ qua" (`--ignore-t`)**.

---

## 2. Chú thích các minh họa, nội dung & bảng biểu trên slide

### A. Hình 2 — Dòng thời gian song song trong C++ (`fig_timeline.png` — Slide 5)
*(Nói gọn ~45 giây, nhấn vào trục thời gian và độ mới của tính năng)*:
- **C++11 (2011):** `std::thread`, `std::async` / `std::future`, smart pointer, lambda — phổ biến lâu đời, rất nhiều ví dụ chuẩn trên Internet.
- **C++14 (2014):** generic lambda, `shared_mutex` (bổ trợ).
- **C++17 (2017):** **Parallel algorithms** (`std::for_each(std::execution::par, ...)`) — viết ngắn gọn, nhưng **ẩn backend thực thi bên dưới** (trên GCC Linux là **Intel TBB**, không phải OpenMP!).
- **C++20 (2020):** **Coroutines** (`co_await`, `co_return`), `std::latch`, `std::barrier` — mới nhất, độ phức tạp cao nhất về quản lý vòng đời frame và bộ nhớ.
- **Câu chốt dẫn dắt:** tính năng càng mới và trừu tượng thì dữ liệu huấn luyện mẫu chuẩn càng ít → **dự đoán trước** rằng LLM sẽ dễ vấp nhất ở C++17 (nhầm backend TBB/OpenMP) và C++20 (sai vòng đời coroutine).

### B. Tóm tắt Bảng 2 — 5 biến thể song song được đánh giá (Slide 6)
*(Nói gọn ~45 giây, lướt nhanh từ bộ nhớ chia sẻ sang phân tán)*:

| Biến thể | Mô hình bộ nhớ | Cách điều khiển số luồng / phân vùng | Điểm dễ sai với LLM |
|---|---|---|---|
| **C++11 `std::async`** | Chia sẻ (1 nút) | Tự chia tác vụ thành $T$ phần (`-t`) | Quên `std::launch::async` hoặc chia tải mất cân bằng |
| **C++17 `par_algo`** | Chia sẻ (1 nút) | Qua API backend (`tbb::global_control` trên GCC) | Đặt nhầm `OMP_NUM_THREADS` → bị bỏ qua |
| **C++20 Coroutines** | Chia sẻ (1 nút) | Tự quản lý `promise_type`, handle, thread pool | Treo `done()`, double-free, segfault |
| **OpenMP** | Chia sẻ (1 nút) | Chỉ thị `#pragma omp parallel for` + `-t` | Quên cân bằng tải (`dynamic`) hoặc bỏ qua `-t` |
| **MPI + OpenMP** | Phân tán (nhiều nút) | Rank MPI chia phân vùng (`-p`) + OpenMP trong nút | Sai `MPI_Gather`/`Gatherv`, đặt timer trước `MPI_Gather` |

### C. Ma trận thực nghiệm (Bảng 4) & 4 mô hình LLM (Slide 7)
- **4 LLM được đánh giá trong bài báo gốc:** ChatGPT-5, ChatGPT-4 (OpenAI), Claude (Anthropic), LLaMA (Meta, trọng số mở).
- **5 biến thể vừa nêu ở Slide 6 cho mỗi LLM** → tổng cộng **20 chương trình**.
- **Cách sinh mã:** mỗi cặp *(mô hình, biến thể)* chỉ sinh **1 lần duy nhất** (*zero-shot*, không nhắc lại lỗi) — ưu điểm là mô phỏng đúng người dùng phổ thông gửi một câu lệnh; hạn chế là chưa có phân tích thống kê nhiều lần chạy.

### D. 3 prompt nguyên văn P1, P2, P3 — **2 ĐIỂM CỰC KỲ CẦN NHẤN** (Slide 8)
1. **Tại sao P3 (MPI+OpenMP) bắt buộc thêm yêu cầu cờ `-p` (số phân vùng)?**
   - Trong bài báo gốc (`LLM.pdf`, trang 3), nếu không yêu cầu rõ cấu hình số phân vùng `-p`, LLM thường sinh mã kiểu **mỗi rank MPI tự tính lại nguyên cả bức ảnh Mandelbrot** (tính lặp dư thừa, không hề chia tải phân tán!).
2. **Cả P1, P2, P3 đều KHÔNG cố định tọa độ phức, độ phân giải mặc định hay hàm tô màu:**
   - Chỉ yêu cầu: *bài toán Mandelbrot + cơ chế song song + định dạng PBM + cờ `-t`/`-p` + in thời gian loại trừ I/O*.
   - **Ý quan trọng để mở đường cho Phần 4:** vì prompt để mở nên mỗi LLM tự chọn khung nhìn mặt phẳng phức, độ phân giải mặc định hoặc tối ưu cắt tỉa khác nhau → làm thông lượng tuyệt đối giữa các mô hình có thể chênh rất lớn dù chạy cùng bài toán.

### E. Quy trình kiểm định 4 bước & Độ đo (Mục 3.4–3.5 — Slide 9)
- **4 cổng kiểm định tuần tự:**
  1. **Biên dịch (`Build`)** với GCC 11.5.0 → nếu lỗi, ghi nhận và sửa tối thiểu để đi tiếp.
  2. **Thực thi (`Run`)** → kiểm tra crash, segfault, treo vô hạn, lỗi phân tích cờ `-t`/`-p`.
  3. **Kiểm tra ảnh (`Correctness`)** → mở ảnh PBM/PGM kiểm tra trực quan (tránh lỗi ảnh đen P4/P5).
  4. **Đo chất lượng & mở rộng (`LOC`, `COCOMO`, `Scaling`)** → đếm dòng mã bằng `cloc`, ước lượng công sức bằng `scc` (COCOMO), rồi chạy đo tăng tốc.
- **Độ đo thông lượng trung tâm của bài báo (Công thức Mục 3.5.3):**
  $$\text{Throughput} = \frac{W \cdot H}{T_{\text{compute}}} \quad (\text{pixel updates per second})$$
  - **Bắt buộc loại trừ thời gian ghi ảnh (I/O)** khỏi $T_{\text{compute}}$, nếu không phần ghi đĩa tuần tự sẽ che lấp hoàn toàn khả năng tăng tốc tính toán (định luật Amdahl).

### F. Môi trường thực nghiệm cụm `rostam` (Bảng 5) vs Máy demo cục bộ (Slide 7 & 9)
- **Cụm `rostam` (ĐH Bang Louisiana — LSU, bài báo gốc):** 16 nút `medusa`, mỗi nút 1 CPU Intel Xeon Gold 6148 **20 lõi**, 92 GB RAM; GCC 11.5.0, Intel TBB 2022.2, OpenMPI 5.0.7.
  - Bộ nhớ chia sẻ: quét `1 → 20` lõi trên 1 nút.
  - Bộ nhớ phân tán: ảnh `12000 × 80000`, `1000` vòng lặp, quét `1, 2, 4, 8, 12` nút (mỗi nút 1 rank MPI × 20 lõi OpenMP).
- **Máy demo cục bộ của nhóm:** Windows 11, CPU **12 luồng logic**, MinGW-W64 GCC 13.2.0 (`E:\Strawberry\c\bin\g++.exe`), có OpenMP + C++20, **không có Intel TBB và MPI** → **nói rõ ngay từ đầu** rằng demo live minh họa phần OpenMP (và kiểm chứng bổ sung Gemini 4 ở cuối Phần 4), còn phần MPI/TBB trình bày qua số liệu bài báo gốc.

---

## 3. Kịch bản chạy Demo trực tiếp (2,5–3 phút — Slide 10)

### Chuẩn bị trước khi lên bảng (bắt buộc kiểm tra!)
```powershell
cd "e:\Code stuffs\Universal-projects\TinhToanSongSong\Demo"
deactivate          # QUAN TRỌNG: thoát .venv nếu đang bật, vì matplotlib/Pillow nằm ở Python hệ thống
python interactive.py
```
- **Lưu ý kỹ thuật:** nếu lỡ đang mở `speedup.png` trong Windows Photos, script đã tự chống lỗi `Errno 22` bằng cách lưu sang `speedup_1.png`, nhưng tốt nhất cứ đóng sẵn trình xem ảnh trước khi demo.
- **Dự phòng nếu terminal trục trặc:** chạy `.\run_demo.bat` ($\approx$1 phút, tự biên dịch + đo + vẽ `speedup.png`).

### Trình tự demo gọn, có tương tác với lớp
*(Nếu thời gian còn dư chạy đủ 4 bước; nếu sát giờ có thể gộp nhanh Menu 5 và tập trung vào Menu 1 → Menu 3 → Menu 4)*:
1. **Menu 1 — Tuần tự vs OpenMP** *(nhấn Enter dùng mặc định `800×600, 300 vòng`, `-t 8`)*:
   - Hỏi lớp: *"Theo mọi người 8 luồng nhanh hơn bản tuần tự mấy lần?"* → Chạy cho thấy speedup thật (lặp 3 lần lấy trung bình, đã loại I/O).
2. **Menu 5 — Mở ảnh kết quả** *(gõ `omp`, chạy nhanh nếu dư giờ)*:
   - Mở `mandel_view.png` cho lớp thấy tập Mandelbrot rõ biên, vùng đen đặc ở giữa chính là nơi tốn nhiều vòng lặp nhất.
3. **Menu 3 — So sánh `static` / `dynamic` / `guided`** *(gợi ý `400×300, 1000 vòng`, chunk `0`, `8` luồng)*:
   - Minh họa trực tiếp lý thuyết mất cân bằng tải ở Phần 1: `dynamic`/`guided` nhanh hơn `static` rõ rệt. *(Xem mẹo giải thích nhanh tại [`06-giai-thich-lap-lich-openmp.md`](06-giai-thich-lap-lich-openmp.md).)*
4. **Menu 4 — Chế độ LỖI: bỏ qua `-t` (`--ignore-t`)** *(khoảnh khắc "a-ha"!)*:
   - Hỏi lớp: *"Nếu mình gõ `-t 1`, `-t 2`, `-t 4`, `-t 8` vào chương trình có hỗ trợ cờ `-t`, số luồng thực tế có chắc chắn là 1, 2, 4, 8 không?"*
   - Chạy Menu 4 → terminal in song song bản đúng (tăng theo `-t`) và bản lỗi (`--ignore-t`, luôn dùng đủ 12 luồng dù gõ `-t 1`!) và xuất biểu đồ **đường phẳng nằm ngang** (`speedup.png`).
   - Chốt câu nối: *"Đây chính xác là loại lỗi tinh vi mà LLM mắc phải dù chương trình biên dịch 100% không một lỗi cú pháp!"*

---

## 4. Câu chuyển mượt sang Phần 3 (Đồng Đức Dương)
> *"Qua demo vừa rồi, chúng ta thấy một chương trình hoàn toàn có thể biên dịch sạch, nhận đủ cờ dòng lệnh mà vẫn sai hành vi song song bên trong. Vậy khi chạy 20 chương trình do 4 LLM sinh ra trên cụm HPC thật, những lỗi cụ thể nào đã xảy ra? Mời bạn Đức Dương trình bày Phần 3: Phân tích lỗi thực tế."*
