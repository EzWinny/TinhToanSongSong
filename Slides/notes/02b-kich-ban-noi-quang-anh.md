# Kịch bản lời nói & Giải thích kỹ thuật — Phần 2 (Nguyễn Quang Anh)

- **Người thuyết trình:** Nguyễn Quang Anh (`24001649` — Trưởng nhóm)
- **Phạm vi trình bày:** **Slide 6 – Slide 11** *(Tiến hóa C++, 5 mô hình song song, Ma trận thực nghiệm, Prompt P1–P3, Quy trình 4 cổng & Demo trực tiếp)*
- **Tổng thời lượng dự kiến:** **~7–8 phút** *(Slide 6–10: ~4,5 phút | Demo trực tiếp Slide 11: ~2,5–3 phút)*
- **Tài liệu đi kèm:** [`02-phan-2-kien-truc-thuc-nghiem-va-demo.md`](02-phan-2-kien-truc-thuc-nghiem-va-demo.md) · [`06-giai-thich-lap-lich-openmp.md`](06-giai-thich-lap-lich-openmp.md)

---

## PHẦN A. KỊCH BẢN LỜI NÓI CHI TIẾT THEO TỪNG SLIDE (SLIDE 5 – SLIDE 10)

> **Mẹo trình bày:** Đừng học thuộc từng chữ; chỉ cần nhớ **ý dẫn → 2–3 ý chính → câu chốt chuyển slide**. Những chỗ in **đậm** là từ khóa cần nhấn giọng khi chỉ lên màn chiếu.

---

### Slide 5 — Tiến hóa lập trình song song trong chuẩn C++ hiện đại *(~50 giây)*

> **Lời mở đầu nối từ Trần Lý Dũng:**
> *"Cảm ơn phần đặt vấn đề của bạn Dũng. Như chúng ta vừa thấy, bài toán Mandelbrot tuy công thức rất đơn giản nhưng lại có độ mất cân bằng tải lớn. Vậy câu hỏi đặt ra là: nhóm tác giả đã dùng những cơ chế lập trình song song nào để thử thách các mô hình ngôn ngữ lớn?"*
>
> **Chỉ vào Hình 2 (từ trái sang phải):**
> *"Trên màn hình là dòng thời gian các tính năng song song được bổ sung dần vào chuẩn C++ hiện đại trong hơn một thập kỷ qua:*
> - *Bắt đầu từ **C++11**, ngôn ngữ cung cấp `std::thread`, `std::async` và `std::future`. Đây là lớp công cụ đã ra đời rất lâu, có hàng triệu đoạn mã mẫu trên Internet nên LLM rất quen thuộc.*
> - *Sang **C++17**, chuẩn bổ sung **thuật toán song song** như `std::for_each` kèm `std::execution::par`. Cách viết nhìn rất ngắn gọn, nhưng có một cái bẫy hệ sinh thái: trên trình biên dịch GCC của Linux, lớp thực thi bên dưới không phải OpenMP mà là thư viện **Intel TBB**.*
> - *Và mới nhất là **C++20** với **Coroutines** (`co_await`, `co_return`) cùng `std::latch`, `std::barrier`. Cơ chế này rất mới, ít mã mẫu chuẩn, và đòi hỏi lập trình viên kiểm soát rất chặt vòng đời bộ nhớ.*
>
> *Nhìn trục thời gian này, mình có thể dự đoán ngay: tính năng càng mới và càng phụ thuộc vào hệ sinh thái trình biên dịch thì LLM sẽ càng dễ mắc lỗi ngầm."*

---

### Slide 6 — Tổng quan 5 mô hình song song được đánh giá *(~1 phút 20 giây)*

> **Chỉ vào bảng 5 dòng trên Slide 6:**
> *"Từ nền tảng đó, bài báo chọn ra đúng **5 mô hình lập trình song song** chia làm 2 nhóm lớn:*
>
> - ***Nhóm 1 — Bộ nhớ chia sẻ (chạy trên 1 nút, nhiều lõi CPU cùng đọc/ghi chung 1 vùng RAM)** gồm 4 biến thể:*
>   1. ***C++11 `std::async`:** tự chia các hàng ảnh thành $T$ tác vụ chạy song song theo cờ `-t`.*
>   2. ***C++17 `par_algo`:** dùng thuật toán chuẩn với `std::execution::par`, nhưng muốn giới hạn số luồng trên GCC thì bắt buộc gọi API của backend là `tbb::global_control`.*
>   3. ***C++20 Coroutines:** chia việc thành các tác vụ có thể tạm dừng và nối lại; lập trình viên phải tự quản lý `promise_type`, handle và hàng đợi luồng.*
>   4. ***OpenMP:** chuẩn công nghiệp quen thuộc nhất trên bộ nhớ chia sẻ — chỉ cần gắn chỉ thị `#pragma omp parallel for` trước vòng lặp và chọn chiến lược lập lịch phù hợp như `dynamic`.*
> - ***Nhóm 2 — Bộ nhớ phân tán (chạy trên nhiều nút máy tính nối mạng)** gồm biến thể thứ 5 là **MPI + OpenMP**: dùng **MPI** chia bức ảnh thành các phân vùng gửi cho từng nút theo cờ `-p`, sau đó bên trong mỗi nút lại dùng **OpenMP** tận dụng hết các lõi CPU, cuối cùng gom mảnh ảnh về nút gốc qua `MPI_Gather` hoặc `MPI_Gatherv`.*
>
> *Như vậy, cùng một bài toán Mandelbrot, nhưng độ khó tăng dần từ **cú pháp quen thuộc** ở `async` và OpenMP sang **ngữ nghĩa hệ sinh thái và điều phối phức tạp** ở TBB, Coroutine và MPI+OpenMP."*

---

### Slide 7 — Ma trận thực nghiệm (4 LLM × 5 biến thể) & Hạ tầng đo *(~50 giây)*

> **Chỉ vào Bảng 4 bên trái rồi sang hộp `rostam` bên phải:**
> *"Bây giờ mình sang cách bài báo tổ chức thực nghiệm. Nhóm tác giả đem **4 LLM tiêu biểu** — gồm ChatGPT-5, ChatGPT-4, Claude và mô hình trọng số mở LLaMA — chạy trên cả **5 biến thể** vừa nêu, tạo thành ma trận **20 chương trình**.*
>
> *Một nguyên tắc rất quan trọng là **zero-shot 1 lần sinh duy nhất**: mỗi ô chỉ gửi prompt đúng một lần, không nhắc gợi ý sửa lỗi; con người chỉ can thiệp sửa tối thiểu sau khi đã ghi nhận toàn bộ lỗi để có thể đo tiếp hiệu năng.*
>
> *Toàn bộ 20 chương trình này được biên dịch và đo đạc trên cụm siêu máy tính **`rostam`** của Đại học Bang Louisiana (Mỹ): phân vùng `medusa` 16 nút, mỗi nút 20 lõi Intel Xeon Gold 6148, chạy GCC 11.5, Intel TBB 2022.2 và OpenMPI 5.0.7. Đặc biệt, bài báo còn biên dịch và đo luôn **5 chương trình C++ viết bởi con người** lấy từ sách *Parallel C++* làm mốc tham chiếu thực tế gọi là **`Human [5]`**."*

---

### Slide 8 — Thiết kế bộ prompt nguyên văn P1, P2, P3 *(~55 giây)*

> **Chỉ vào 3 khung P1, P2, P3 rồi nhấn mạnh khung màu xanh dưới cùng:**
> *"Đây là 3 câu lệnh prompt nguyên văn tác giả gửi cho các LLM: **P1** cho 3 biến thể C++ hiện đại, **P2** cho OpenMP và **P3** cho MPI+OpenMP. Cả ba đều yêu cầu viết ảnh định dạng PBM, cấu hình số luồng qua `-t` (hoặc số phân vùng qua `-p`) và **in thời gian chạy không tính I/O**.*
>
> *Ở đây có **2 điểm cực kỳ quan trọng** mọi người cần lưu ý vì nó ảnh hưởng trực tiếp tới kết quả ở Phần 3 và Phần 4:*
> 1. ***Thứ nhất, ở P3 bắt buộc phải thêm yêu cầu cờ `-p`:** tác giả ghi nhận rằng nếu không yêu cầu cấu hình số phân vùng, LLM rất hay viết kiểu **mọi tiến trình MPI tự tính lại nguyên cả bức ảnh**, hoàn toàn không chia việc!*
> 2. ***Thứ hai, cả 3 prompt đều KHÔNG cố định tọa độ mặt phẳng phức hay độ phân giải mặc định:** mỗi LLM tự chọn khung nhìn và kỹ thuật cắt tỉa riêng. Chút nữa sang Phần 4 của bạn Bảo, mọi người sẽ thấy chính chi tiết này gây chênh lệch rất lớn về thông lượng tuyệt đối giữa các mô hình."*

---

### Slide 9 — Quy trình kiểm định 4 cổng & Hệ quy chiếu độ đo *(~50 giây)*

> **Chỉ theo 4 mũi tên trên cùng → công thức ở dưới trái → khung máy demo ở dưới phải:**
> *"Mỗi chương trình sau khi sinh ra phải đi qua **4 cổng kiểm định tuần tự**:*
> 1. ***Build:** biên dịch bằng GCC, ghi nhận lỗi cú pháp.*
> 2. ***Run:** chạy thật với nhiều số luồng/nút để bắt lỗi treo, crash hay bỏ qua cờ `-t`/`-p`.*
> 3. ***Kiểm tra ảnh PBM:** mở trực tiếp ảnh kết quả để phát hiện lỗi ảnh đen toàn phần dù chương trình thoát bình thường.*
> 4. ***Đo đạc:** đếm dòng mã bằng `cloc`, ước lượng công sức COCOMO bằng `scc` và đo khả năng mở rộng.*
>
> *Độ đo trung tâm của bài báo là **thông lượng cập nhật điểm ảnh mỗi giây** (`pixel updates per second` = $W\cdot H / T_{\text{compute}}$), **loại trừ hoàn toàn thời gian ghi đĩa I/O** để không bị phần tuần tự ghi tệp làm méo tốc độ tăng tốc.*
>
> *Và mình cũng nói rõ phạm vi phần demo sắp chạy ngay sau đây: máy tính thuyết trình là Windows 11, CPU 12 luồng, GCC 13.2.0 — có sẵn **OpenMP và C++20**, nhưng **không có Intel TBB và cụm MPI nhiều nút**. Vì vậy, phần demo trực tiếp sẽ tập trung minh họa trực quan trên **OpenMP**, còn số liệu TBB và MPI phân tán sẽ phân tích trên dữ liệu thật của cụm `rostam`."*

---

### Slide 10 — Dẫn Demo tương tác trực tiếp (`Demo/interactive.py`) *(~2,5–3 phút)*

> **Chuyển cửa sổ sang PowerShell (đã mở sẵn ở `Demo/` và đã `deactivate` `.venv`):**
> *"Để mọi người không chỉ nghe lý thuyết trên slide mà thấy tận mắt các hiện tượng này, nhóm đã xây dựng một bộ demo tương tác nhỏ cho bài Mandelbrot (tuần tự + OpenMP, dùng chung lõi tính toán và đo thời gian loại trừ I/O)."*
>
> 1. **Chạy Menu 1 — Tuần tự vs OpenMP:**
>    - *Hỏi lớp:* *"Với ảnh `800×600`, 300 vòng lặp, theo mọi người khi bật 8 luồng OpenMP thì thời gian sẽ giảm mấy lần?"*
>    - *Nhấn Enter chạy (lặp 3 lần lấy trung bình)* → chỉ vào hệ số speedup trên terminal: *"Ta thấy tăng tốc rất rõ rệt khi chạy song song trên nhiều lõi."*
> 2. **Chạy Menu 5 — Mở ảnh (`omp`) *(chạy nhanh ~15 giây, bỏ qua nếu sát giờ)*:**
>    - *"Đây là ảnh tập Mandelbrot đầu ra: hai bản tuần tự và OpenMP khớp nhau từng pixel. Mọi người nhìn vùng đen đặc chính giữa — đó là nơi mỗi pixel phải chạy đủ vòng lặp, còn nền xung quanh thoát ngay lập tức."*
> 3. **Chạy Menu 3 — So sánh `static` / `dynamic` / `guided` (`400×300`, 1000 vòng, 8 luồng):**
>    - *"Bây giờ mình kiểm chứng ngay bẫy mất cân bằng tải mà bạn Dũng nhắc ở Phần 1. Cùng 8 luồng, cùng bài toán, nhưng chỉ đổi cách lập lịch:*
>      - *`static` chia cứng từng dải lớn nên các luồng ở mép trắng xong sớm rồi ngồi chờ luồng ở giữa.*
>      - *Còn `dynamic` và `guided` dùng hàng đợi động chia việc liên tục nên nhanh hơn `static` rõ rệt."*
> 4. **Chạy Menu 4 — Chế độ LỖI `--ignore-t` (ĐIỂM NHẤN QUAN TRỌNG NHẤT!):**
>    - *Hỏi lớp:* *"Nếu một chương trình do LLM sinh ra biên dịch sạch 100%, nhận đủ cờ `-t 1`, `-t 2`, `-t 4`, `-t 8`, liệu số luồng bên trong có chắc chắn thay đổi theo `-t` không?"*
>    - *Chạy Menu 4 → mở biểu đồ `speedup.png` vừa vẽ:* *"Mọi người nhìn 2 đường trên đồ thị: đường bản đúng tăng đều theo số luồng, còn đường bản lỗi (mô phỏng lỗi bỏ qua `-t`, luôn chạy tối đa số luồng hệ thống) **nằm phẳng ngang ở trên cao** ngay từ `-t 1`! Chút nữa ở Phần 3 và Phần 4, mọi người sẽ thấy chính hình dạng 'đường phẳng nằm cao' này xuất hiện trên dữ liệu thật của ChatGPT-4, Claude và LLaMA."*
>
> **Câu chuyển sang Phần 3 (Đồng Đức Dương):**
> *"Qua demo vừa rồi, chúng ta thấy một chương trình hoàn toàn có thể biên dịch sạch, nhận đủ tham số dòng lệnh mà vẫn sai hành vi song song bên trong. Vậy khi đem 20 chương trình do 4 LLM sinh ra chạy thật trên cụm `rostam`, cụ thể từng mô hình đã mắc những lỗi gì? Mời bạn Đức Dương trình bày Phần 3: Phân tích lỗi thực tế."*

---

## PHẦN B. GIẢI THÍCH KỸ THUẬT CỐT LÕI (OPENMP, MPI & 5 BIẾN THỂ)

> Phần này giúp Quang Anh **hiểu thấu gốc rễ** để giải thích trôi chảy khi giảng viên hoặc các bạn hỏi xoáy ngay tại Slide 5–10 hoặc phần Q&A.

---

### 1. OpenMP là gì? (Song song trên bộ nhớ chia sẻ — 1 máy tính)

- **Định nghĩa 1 câu:** **OpenMP** (*Open Multi-Processing*) là chuẩn lập trình song song cho **bộ nhớ chia sẻ** (1 máy tính có nhiều lõi CPU cùng truy cập chung 1 bộ nhớ RAM), hoạt động chủ yếu bằng các **chỉ thị trình biên dịch (`#pragma omp ...`)**.
- **Mô hình hoạt động — Fork–Join:**
  ```text
  Luồng chính (Master) ----+---> [ Luồng 0 ] ---+----> Luồng chính tiếp tục
                           +---> [ Luồng 1 ] ---+
                           +---> [ Luồng 2 ] ---+
                           +---> [ Luồng 3 ] ---+
                         (Fork: tách luồng)   (Join: hợp nhất)
  ```
  1. Chương trình bắt đầu bằng 1 luồng chính.
  2. Gặp vùng `#pragma omp parallel`, nó **tách (fork)** ra thành $T$ luồng (điều khiển bởi `omp_set_num_threads(T)` hoặc biến môi trường `OMP_NUM_THREADS`).
  3. Các luồng chia nhau chạy các vòng lặp (ví dụ chia các hàng `y` của ảnh Mandelbrot).
  4. Xong vòng lặp, tất cả đồng bộ lại (**join**) rồi luồng chính tiếp tục ghi tệp ảnh.
- **Ví dụ 3 dòng trên bài Mandelbrot:**
  ```cpp
  omp_set_num_threads(num_threads); // đặt số luồng từ cờ -t
  #pragma omp parallel for schedule(dynamic, 4)
  for (int y = 0; y < H; ++y) { compute_row(y); }
  ```
- **Ưu & nhược điểm:**
  - *Ưu:* Rất ngắn gọn (chỉ thêm 1–2 dòng `#pragma`), dễ thêm vào mã tuần tự sẵn có, hỗ trợ chọn lịch `static` / `dynamic` / `guided` ngay trong chỉ thị. *(Chi tiết 3 lịch này xem [`06-giai-thich-lap-lich-openmp.md`](06-giai-thich-lap-lich-openmp.md).)*
  - *Nhược:* **Chỉ chạy trong phạm vi 1 máy tính** (1 không gian RAM), không thể vượt qua số lõi của 1 nút (vd 20 lõi trên `rostam`). Nếu lập trình viên quên cân bằng tải (`static`) hoặc chia sẻ biến ghi chung sai cách (race condition / false sharing) thì hiệu năng tụt mạnh hoặc sai kết quả.

---

### 2. MPI là gì? Và mô hình lai MPI + OpenMP hoạt động ra sao?

- **Định nghĩa 1 câu:** **MPI** (*Message Passing Interface*) là chuẩn lập trình song song cho **bộ nhớ phân tán** — nhiều máy tính (nút — *node*) nối mạng với nhau trong một cụm siêu máy tính; mỗi tiến trình có **bộ nhớ RAM riêng biệt** và trao đổi dữ liệu bằng cách **gửi/nhận thông điệp**.
- **Mô hình SPMD (*Single Program, Multiple Data*):**
  - Mọi tiến trình chạy **cùng một tệp thực thi**, nhưng mỗi tiến trình có một mã số định danh riêng gọi là **`rank`** (`0, 1, ..., P-1`) và biết tổng số tiến trình **`size`** ($P$).
  - Dựa vào `rank`, mỗi tiến trình biết mình phụ trách dải hàng nào của ảnh Mandelbrot.
- **Chu trình chuẩn của bài Mandelbrot bằng MPI:**
  ```text
  [ Khởi tạo: MPI_Init ] -> lấy rank và size
          |
          v
  Mỗi rank tự tính phần hàng ảnh cục bộ (local_buffer)
          |
          v
  [ Gom dữ liệu: MPI_Gather / MPI_Gatherv ] --> chuyển toàn bộ mảnh ảnh về rank 0
          |
          v
  (Chỉ rank 0 mới ghi ảnh PBM ra đĩa) -> [ MPI_Finalize ]
  ```
- **Tại sao phải dùng `MPI_Gatherv` thay vì `MPI_Gather`?**
  - `MPI_Gather` yêu cầu **mọi rank gửi số byte bằng hệt nhau**. Nếu chiều cao ảnh $H$ không chia hết cho số tiến trình $P$ (vd $H=1000, P=12$), số hàng giữa các rank bị lệch nhau $\implies$ dùng `MPI_Gather` sẽ tràn bộ đệm gây **segfault**!
  - `MPI_Gatherv` cho phép khai báo mảng kích thước từng phần (`recvcounts`) và vị trí ghép (`displs`), an toàn cho mọi cặp $(H, P)$.
- **Tại sao bài báo dùng mô hình LAI `MPI + OpenMP` thay vì thuần MPI?**
  - Trên cụm `rostam`, mỗi nút có **20 lõi dùng chung RAM** và cụm có tối đa **12 nút** (= 240 lõi).
  - Nếu chạy thuần MPI (240 tiến trình), các tiến trình trong cùng 1 nút vẫn phải sao chép bộ nhớ và truyền thông điệp qua lớp MPI.
  - Với mô hình **lai 2 tầng (Hybrid MPI + OpenMP)**:
    - **Tầng ngoài (giữa các nút — MPI):** chạy **1 tiến trình MPI cho mỗi nút**, chia toàn ảnh thành các phân vùng lớn (theo cờ `-p`).
    - **Tầng trong (bên trong mỗi nút — OpenMP):** tiến trình MPI đó mở **20 luồng OpenMP** cùng chia sẻ RAM cục bộ để tính cực nhanh phân vùng của nút mình, không tốn chi phí copy dữ liệu nội bộ!
  - **Bẫy chết người LLM hay mắc ở MPI:**
    1. Quên chia phân vùng (nếu prompt thiếu `-p`, mọi rank đều tự tính nguyên cả bức ảnh!).
    2. Đặt đồng hồ đo `MPI_Wtime()` **trước lệnh `MPI_Gather`** → bỏ sót toàn bộ thời gian truyền mạng gom ảnh, làm số liệu hiệu năng ảo!
    3. Chia tĩnh theo 4 dải lớn trên Mandelbrot → 2 nút giữa ôm hết ruột đen, gây điểm chững $2 \to 4$ nút (Hình 6).

---

### 3. Giải thích cặn kẽ từng biến thể trong 5 biến thể song song

| # | Biến thể | Cơ chế hoạt động (giải thích dễ hiểu) | Ví dụ liên tưởng | Cách chỉnh số luồng / phân vùng | Điểm yếu / Bẫy LLM hay mắc |
|---|---|---|---|---|---|
| **1** | **C++11 bất đồng bộ** (`std::async` / `std::future`) | Chia bức ảnh thành $T$ phần (hoặc dùng hàng đợi tác vụ), phóng ra $T$ tác vụ bất đồng bộ bằng `std::async(std::launch::async, ...)` trả về các đối tượng `std::future`, rồi gọi `.get()` để chờ tất cả hoàn thành. | Giao $T$ phiếu đặt hàng cho $T$ nhân viên cùng lúc; mỗi phiếu (`future`) là giấy hẹn để quay lại lấy kết quả (`.get()`). | Tự truyền tham số `-t` để quyết định số lượng `future`/worker tạo ra. | Quên cờ `std::launch::async` (khiến trình biên dịch có thể trì hoãn chạy tuần tự), hoặc chia $T$ khối tĩnh bằng nhau nên mất cân bằng tải trên Mandelbrot. |
| **2** | **C++17 thuật toán song song** (`std::execution::par`) | Dùng sẵn thuật toán STL chuẩn như `std::for_each(std::execution::par, begin, end, lambda)` để yêu cầu chạy song song trên toàn dải chỉ số hàng/điểm ảnh mà **không cần tự tạo luồng**. | Gọi dịch vụ "giao hàng nhanh" có sẵn của C++ — viết cực ngắn, nhưng **không tự nhìn thấy hãng vận chuyển nào đang chạy bên dưới**. | **Chuẩn C++17 không có hàm đặt số luồng!** Trên GCC/Linux, thư viện `libstdc++` dùng **Intel TBB** làm backend $\implies$ phải gọi `tbb::global_control(max_allowed_parallelism, T)`. | **Bẫy kinh điển:** ChatGPT-4 đặt `OPENMP_NUM_THREADS` / `OMP_NUM_THREADS` (bị TBB bỏ qua hoàn toàn!), Claude viết comment nhắc đặt số luồng nhưng... quên viết code $\implies$ luôn chạy full 20 lõi! |
| **3** | **C++20 Coroutines** (`co_await`, `co_return`, `promise_type`) | Coroutine là **hàm có thể tạm dừng giữa chừng (suspend) và chạy tiếp sau đó (resume)** mà không cần giữ chặt 1 luồng hệ điều hành. Trạng thái hàm nằm trong 1 khung gọi là *coroutine frame* điều khiển qua `std::coroutine_handle` và kiểu `promise_type`. | Giống đầu bếp làm nhiều món: đang đun nước (`co_await`) thì tạm chuyển tay sang cắt rau cho món khác, nước sôi lại quay tiếp mà không phải thuê thêm đầu bếp mới. | C++20 chỉ cung cấp cơ chế nền thấp, **chưa có sẵn thread pool chuẩn** $\implies$ phải tự ghép coroutine với một nhóm `T` luồng (`std::thread`/`jthread`) theo `-t`. | **Khó nhất với LLM:** Claude đặt `final_suspend = suspend_never` khiến frame tự hủy trước khi kiểm tra `done()` $\implies$ **treo vô hạn**; LLaMA để cả `suspend_never` lẫn destructor cùng xóa 1 handle $\implies$ **double-free segfault**! |
| **4** | **OpenMP** (`#pragma omp parallel for`) | Dùng chỉ thị tiền xử lý gắn thẳng lên vòng lặp `for` duyệt các hàng ảnh; trình biên dịch tự sinh mã tạo nhóm luồng (fork–join) và phân phối vòng lặp theo lịch `static`/`dynamic`/`guided`. | Đội công nhân đứng quanh 1 bảng việc chung, có quản đốc (runtime OpenMP) chia hàng theo quy tắc đã chọn (`schedule`). | Gọi `omp_set_num_threads(T)` hoặc mệnh đề `num_threads(T)` từ cờ `-t`. | Dễ viết đúng cú pháp, nhưng dễ quên `schedule(dynamic)` (gây mất cân bằng tải) hoặc parse `-t` xong bỏ quên không áp vào OpenMP. |
| **5** | **MPI + OpenMP** *(Song song lai phân tán)* | **2 tầng song song:** MPI chạy trên nhiều nút độc lập (mỗi nút là 1 `rank` nhận 1 phân vùng ảnh), bên trong mỗi nút dùng OpenMP chia phân vùng đó cho 20 lõi CPU, cuối cùng gom kết quả về `rank 0` qua `MPI_Gather`/`Gatherv`. | Nhiều **chi nhánh (nút MPI)** ở các thành phố khác nhau cùng làm chung 1 dự án; trong mỗi chi nhánh có **20 nhân viên (luồng OpenMP)** làm chung văn phòng, xong gửi báo cáo về trụ sở chính (`rank 0`). | Cờ `-p` quy định số phân vùng / cấu hình tiến trình MPI (`mpirun -np N`), kết hợp OpenMP tận dụng 20 lõi/nút. | Quên chia việc (mọi rank tính cả ảnh), sai kích thước đệm `MPI_Gather` gây segfault, chia dải tĩnh gây chững ở 4 nút, và đặt `MPI_Wtime()` trước `MPI_Gather`. |

---

## PHẦN C. 5 CÂU HỎI THẦY HAY HỎI NGAY TẠI PHẦN 2 (TRẢ LỜI GỌN 20 GIÂY)

1. **Hỏi: *"Em phân biệt ngắn gọn `thread` (luồng) với `process` (tiến trình MPI) khác nhau thế nào?"***
   - **Đáp:** Các **luồng** (C++11/OpenMP) chạy trong cùng một tiến trình và **dùng chung vùng nhớ RAM**, trao đổi dữ liệu cực nhanh nhưng chỉ giới hạn trong 1 máy và dễ tranh chấp bộ nhớ. Các **tiến trình MPI** có **bộ nhớ riêng biệt**, chạy được trên hàng chục–hàng nghìn máy nối mạng, trao đổi bằng gửi/nhận thông điệp nên tốn độ trễ mạng.

2. **Hỏi: *"Tại sao C++17 `std::execution::par` lại không nhận `OMP_NUM_THREADS`?"***
   - **Đáp:** Vì chuẩn ISO C++17 chỉ định nghĩa giao diện `execution::par`, còn việc thực thi bằng thư viện nào là do từng trình biên dịch quyết định. Trên Linux, thư viện chuẩn `libstdc++` của GCC liên kết với **Intel TBB** chứ không dùng OpenMP, nên mọi biến môi trường của OpenMP đều bị phớt lờ; muốn chỉnh số luồng phải gọi `tbb::global_control`.

3. **Hỏi: *"Coroutine C++20 có tự chạy song song trên nhiều lõi không?"***
   - **Đáp:** **Không tự động.** Bản thân coroutine chỉ cho phép *tạm dừng và tiếp tục* (concurrency / đồng thời bất đồng bộ). Để chạy **song song thật (parallelism)** trên nhiều lõi CPU, chương trình phải tự gắn các coroutine handle đó vào một nhóm luồng (thread pool) có $T$ luồng theo cờ `-t`.

4. **Hỏi: *"Tại sao phải loại trừ thời gian ghi ảnh (I/O) khi đo hiệu năng?"***
   - **Đáp:** Theo định luật Amdahl, ghi tệp ảnh ra ổ cứng là thao tác **tuần tự** và rất chậm so với CPU. Nếu gộp cả thời gian ghi đĩa vào $T$, phần tuần tự này sẽ lấn át thời gian tính toán và che khuất khả năng mở rộng thực sự của thuật toán song song.

5. **Hỏi: *"Nếu máy em không có MPI và TBB thì làm sao kiểm chứng được phần đó?"***
   - **Đáp:** Toàn bộ số liệu mở rộng của C++17 TBB (1–20 lõi) và MPI+OpenMP (1–12 nút) được lấy từ kết quả đo thực tế của bài báo gốc trên cụm HPC `rostam` (LSU). Trên máy cục bộ Windows (12 luồng, GCC 13.2.0), nhóm demo trực tiếp OpenMP (cân bằng tải + lỗi `--ignore-t`), và ở Mục 4.9 còn chạy kiểm chứng thêm mã nguyên bản của Gemini 4 Hydrogen cho cả C++11 async, C++20 coroutine và OpenMP, đồng thời kiểm duyệt tĩnh mã MPI theo danh mục Bảng 12.
