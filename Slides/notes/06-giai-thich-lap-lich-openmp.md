# Giải thích nhanh: Lập lịch OpenMP (`static` / `dynamic` / `guided`)

> **Phục vụ cho:**
> - **Phần 1 — Slide 5** (Mất cân bằng tải tự nhiên trên tập Mandelbrot) — Trần Lý Dũng
> - **Phần 2 — Slide 11** (Demo `Menu 3` so sánh `static` / `dynamic` / `guided` trên `Demo/interactive.py`) — Nguyễn Quang Anh
> - **Phần 4 — Slide 18** (Giải thích vì sao cả 4 LLM chững ở $2 \to 4$ nút MPI do chia dải tĩnh) — Nguyễn Như Bảo
> - **Hỏi – Đáp (Q&A):** Khi giảng viên hỏi sâu về lập lịch OpenMP và tham số `chunk`.

---

## 1. Bối cảnh: Tại sao bài Mandelbrot cần quan tâm đến lập lịch?

Trong bài toán tập Mandelbrot, mỗi điểm ảnh $(x, y)$ tính độc lập theo công thức $z_{k+1} = z_k^2 + c$, nhưng **khối lượng tính toán giữa các hàng chênh lệch cực lớn**:

```text
Hàng trên (mép ảnh)   : [ trắng - trắng - trắng - trắng ]  --> thoát sau 1–3 vòng (siêu nhẹ)
Hàng giữa (ruột đen)  : [ trắng - ĐEN ĐEN ĐEN ĐEN - trắng ] --> chạy đủ I_max = 1000 vòng (siêu nặng)
Hàng dưới (mép ảnh)   : [ trắng - trắng - trắng - trắng ]  --> thoát sau 1–3 vòng (siêu nhẹ)
```

Nếu chia số hàng đều nhau mà không cân bằng tải, một số luồng sẽ xong sớm rồi **ngồi chờ (idle)** các luồng gánh phần ruột đen $\implies$ giảm mạnh tốc độ tăng tốc (speedup).

---

## 2. So sánh 3 chiến lược lập lịch trong OpenMP

Giả sử ta có **400 hàng ảnh** cần chia cho **4 luồng CPU** (`T0, T1, T2, T3`):

| Chiến lược | Cú pháp OpenMP | Cách chia việc | Ưu điểm | Nhược điểm | Hiệu quả trên Mandelbrot |
|---|---|---|---|---|---|
| **`static`** *(Tĩnh — mặc định)* | `schedule(static)` hoặc `schedule(static, chunk)` | Chia **cứng từ trước khi chạy**:<br>• Không ghi `chunk`: mỗi luồng 1 khối liền `100` hàng (`T0: 0–99`, `T1: 100–199`, `T2: 200–299`, `T3: 300–399`).<br>• Có `chunk` (vd `chunk=4`): chia vòng tròn từng miếng 4 hàng (`T0→T1→T2→T3→T0...`). | Chi phí điều phối (overhead) **gần bằng 0**; truy cập bộ nhớ liền mạch, thân thiện với cache. | Nếu không đặt `chunk` nhỏ, `T0` & `T3` (vùng trắng) xong ngay rồi ngồi chờ `T1` & `T2` (ruột đen). | **Chậm nhất** khi dùng mặc định (`static` không `chunk`). |
| **`dynamic`** *(Động)* | `schedule(dynamic, chunk)` | Gom toàn bộ các miếng việc (mỗi miếng `chunk` hàng, mặc định `1`) vào **hàng đợi chung**. Luồng nào làm xong miếng hiện tại thì tự động lấy miếng tiếp theo. | **Cân bằng tải tốt nhất** — không luồng nào bị rảnh sớm; luồng gặp hàng trắng xong nhanh sẽ phụ gánh hàng đen. | Tốn chi phí đồng bộ khi nhiều luồng tranh nhau lấy việc từ hàng đợi (đặc biệt nếu `chunk=1` mà mỗi hàng quá nhẹ). | **Nhanh và ổn định nhất** (chọn `chunk` nhỏ như `1–8` hàng). |
| **`guided`** *(Hướng dẫn / Giảm dần)* | `schedule(guided, chunk)` | Cũng dùng **hàng đợi chung** như `dynamic`, nhưng kích thước miếng việc **giảm dần theo hàm mũ**:<br>lúc đầu giao miếng lớn $\approx \frac{\text{số hàng còn lại}}{2 \times \text{số luồng}}$, càng về cuối miếng càng nhỏ dần xuống tối thiểu `chunk`. | Ít tranh chấp hàng đợi ở đầu chương trình (do lấy miếng to), vẫn cân bằng tốt ở cuối chương trình (do miếng nhỏ dần). | Nếu miếng to giao lúc đầu rơi đúng vào vùng ruột đen dày đặc thì cuối cùng vẫn có thể hơi lệch tải một chút so với `dynamic`. | **Gần ngang `dynamic`**, vượt xa `static`. |

---

## 3. Minh họa trực quan (4 luồng, 400 hàng)

### `static` (mặc định — chia 4 dải lớn)
```text
T0 (hàng   0– 99, toàn trắng) : [==] .......................... (ngồi chờ)
T1 (hàng 100–199, ruột đen)   : [=============================] (chạy lâu nhất)
T2 (hàng 200–299, ruột đen)   : [=============================] (chạy lâu nhất)
T3 (hàng 300–399, toàn trắng) : [==] .......................... (ngồi chờ)
                                                               ^ Tổng thời gian = T1/T2
```

### `dynamic` (chia miếng nhỏ từ hàng đợi chung)
```text
T0 : [nhẹ][nhẹ][nặng  ][nhẹ][nặng  ][nhẹ]
T1 : [nhẹ][nặng  ][nhẹ][nặng  ][nhẹ][nhẹ]
T2 : [nặng  ][nhẹ][nhẹ][nặng  ][nhẹ][nhẹ]
T3 : [nhẹ][nhẹ][nặng  ][nặng  ][nhẹ][nhẹ]
                                         ^ Cả 4 luồng về đích gần như cùng lúc!
```

### `guided` (miếng lớn trước $\to$ miếng nhỏ dần về cuối)
```text
Đầu vòng lặp  : giao miếng ~50 hàng -> ~43 -> ~38 -> ... (ít phải gọi hàng đợi)
Cuối vòng lặp : giao miếng ~8 -> ~4 -> ~2 -> 1 hàng      (lấp kín khe hở tải ở cuối)
```

---

## 4. Ví dụ đời thực dễ nói trên bục thuyết trình

> Hãy tưởng tượng có **4 quầy thu ngân** xử lý **400 giỏ hàng**, trong đó 200 giỏ ở giữa đầy ắp (vùng ruột đen), còn 200 giỏ ở hai đầu chỉ mua 1 chai nước (nền trắng):
> - **`static`:** Chia sẵn 4 hàng cố định mỗi quầy 100 giỏ. Hai quầy hai đầu xong trong 1 phút rồi đứng nhìn 2 quầy ở giữa làm mất 10 phút $\implies$ tổng thời gian vẫn là **10 phút**.
> - **`dynamic`:** Xếp chung **1 hàng đợi duy nhất** (như ngân hàng/sân bay). Quầy nào trống gọi ngay người kế tiếp $\implies$ cả 4 quầy xong gần như **cùng lúc**.
> - **`guided`:** Cũng 1 hàng đợi chung, nhưng lúc đầu phát mỗi quầy **1 xấp lớn** để đỡ đi lấy nhiều lần; gần hết việc thì phát **lẻ từng giỏ** để mọi quầy kết thúc đồng đều.

---

## 5. Tham số `chunk` là gì? Chọn sao cho hợp lý?

- **`chunk`** là số vòng lặp (số hàng ảnh) tối thiểu được gom thành **một gói việc** giao cho luồng mỗi lần lấy.
- **Nếu `chunk` quá nhỏ** (ví dụ `1` trên ảnh rất nhỏ): cân bằng tải tối đa, nhưng luồng phải liên tục đồng bộ với hàng đợi $\implies$ tăng chi phí điều phối (scheduling overhead).
- **Nếu `chunk` quá lớn** (ví dụ `100` trên ảnh 400 hàng): gần như quay về `static` $\implies$ mất cân bằng tải trở lại.
- **Mức hợp lý cho Mandelbrot:** `dynamic, 1` đến `dynamic, 8` (hoặc `guided, 1`), vì mỗi hàng ảnh đã chứa hàng trăm–hàng nghìn điểm ảnh, đủ nặng để chi phí lấy hàng đợi trở nên không đáng kể.

---

## 6. Liên hệ trực tiếp với Demo & Báo cáo của nhóm

1. **Demo trực tiếp (`Demo/interactive.py` — Menu 3):**
   - Chương trình `Demo/mandelbrot/mandel_omp.cpp` hỗ trợ cờ `-s static|dynamic|guided` và `-b <chunk>`.
   - Lệnh chạy tay minh họa (PowerShell từ `Demo/mandelbrot/`):
     ```powershell
     .\mandel_omp.exe -t 8 -w 800 -h 600 -m 1000 -s static  -b 0
     .\mandel_omp.exe -t 8 -w 800 -h 600 -m 1000 -s dynamic -b 4
     .\mandel_omp.exe -t 8 -w 800 -h 600 -m 1000 -s guided  -b 4
     ```
   - Kết quả quan sát: `dynamic` và `guided` nhanh hơn rõ rệt so với `static` mặc định.
2. **Liên hệ Hình 6 (Mở rộng phân tán MPI 1–12 nút — Slide 16):**
   - Tập Mandelbrot **đối xứng qua trục thực**: khi chia tĩnh **2 nút** (nửa trên / nửa dưới), tải cân bằng tuyệt đối.
   - Khi lên **4 nút** bằng cách chia 4 dải tĩnh (giống `static` trong OpenMP), **2 nút ở giữa ôm gần hết ruột đen** còn 2 nút ngoài toàn nền trắng $\implies$ chặn bước `MPI_Gather`, gây ra điểm **chững rõ rệt ở mốc $2 \to 4$ nút** trên cả 4 LLM!
   - Ngược lại, trong mã MPI+OpenMP của **Gemini 4 Hydrogen** (Mục 4.9), mô hình dùng phân vùng **block-cyclic** (tương đương `static` với `chunk` nhỏ rải đều) nên tránh được bẫy mất cân bằng tải giữa các nút.
