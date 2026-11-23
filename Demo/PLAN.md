# Kế hoạch Demo tương tác — LLM-HPC++ (Tập Mandelbrot)

## 1. Vấn đề của demo hiện tại

`run_demo.bat` chỉ chạy một kịch bản cố định: người xem đứng yên xem số chạy qua rồi biểu đồ hiện ra. Họ không điều khiển được gì, nên khó nhớ và không "cảm" được các ý chính của báo cáo (số luồng có được tôn trọng không, cân bằng tải, lỗi ngữ nghĩa).

Mục tiêu của bản tương tác: **khán giả tự chọn thông số, đoán kết quả, rồi tự xem kết quả đó đúng hay sai ngay tại chỗ.**

## 2. Ý tưởng tương tác chính

| Tương tác | Nội dung báo cáo tương ứng | Hiệu ứng với khán giả |
|---|---|---|
| Chọn kích thước ảnh / số vòng lặp | Cấu hình thí nghiệm (Phần 3.6) | Thấy chi phí tính tăng tuyến thế nào |
| Chọn danh sách số luồng, xem speedup vẽ ra ngay | Khả năng mở rộng (Phần 4.6) | Tự nhận ra đường không tuyến tính |
| Chọn `static` / `dynamic` / `guided` | Mất cân bằng tải tự nhiên (Phần 2.1.2) | Thấy chia việc tĩnh có thể thua động |
| Bật chế độ "bỏ qua `-t`" | Lỗi ChatGPT-4: có tham số nhưng không dùng (Phần 4.2.1) | Thấy đường phẳng, hiểu vì sao phải đo |
| Đoán trước, chạy sau | Toàn bộ báo cáo | Biến người xem thành người tham gia |

## 3. Các file cần làm / chỉnh

- `Demo/mandelbrot/mandel.h`: thêm các trường `schedule` (`static`/`dynamic`/`guided`), `chunk`, `ignore_t` vào `Config`; parse thêm `-s`, `-b`, `--ignore-t`.
- `Demo/mandelbrot/mandel_omp.cpp`: dùng `#pragma omp parallel for schedule(<kind>, <chunk>)`; nếu `--ignore-t` thì gọi `omp_set_num_threads(omp_get_num_procs())` để **cố tình phản hồi sai `-t`**; in ra cả số luồng thực tế (`omp_get_max_threads()`).
- `Demo/interactive.py` (mới): giao diện menu trên terminal, gọi `subprocess` chạy các file `.exe`, parse dòng `mode=... threads=... time=...`, in bảng so sánh, vẽ lại `speedup.png`, và mở ảnh kết quả.
- `Demo/run_demo.bat`: giữ nguyên làm chế độ chạy nhanh, không tương tác (dự phòng khi hết thời gian hoặc lỗi terminal).

Không cần cài thêm gì: đã có sẵn `g++` (MinGW-W64, OpenMP), `matplotlib` 3.11 và `Pillow` 12.3. Pillow dùng để đổi `.pgm` sang `.png` cho dễ mở bằng trình xem ảnh Windows.

## 4. Menu đề xuất trong `interactive.py`

```
=== DEMO TƯƠNG TÁC: MANDELBROT SONG SONG ===
1. Tuần tự vs OpenMP        - chọn W, H, iterations; so sánh thời gian
2. Quét số luồng            - nhập dãy như 1 2 4 8 16; vẽ speedup ngay
3. Thử chiến lược chia việc - static / dynamic / guided + chunk size
4. Chế độ LỖI: bỏ qua -t    - xem đường phẳng, đoán rồi mới giật mình
5. Xem ảnh kết quả          - đổi PGM sang PNG và mở bằng viewer
6. Thoát
Chọn (1-6):
```

Mỗi mục đều có bước **"Theo bạn ...?"** trước khi chạy (ví dụ: "Theo bạn 8 luồng nhanh hơn bao nhiêu lần?"), sau đó in kết quả kèm một câu nhận xét nối lại vào báo cáo.

## 5. Kịch bản trình chiếu (20–25 phút)

| Phút | Việc | Thao tác |
|---|---|---|
| 0–2 | Mở đầu | Hỏi: "Có tham số `-t` có nghĩa là dùng đúng số luồng?" Ghi nhận câu trả lời, chưa tiết lộ. |
| 2–6 | Menu 1 | Khán giả chọn ảnh (mặc định 800×600, 300 vòng). Chạy tuần tự + OpenMP 8 luồng, hiện thời gian. |
| 6–12 | Menu 2 | Khán giả chọn dãy luồng. Chạy, vẽ speedup ngay; so với đường tuyến tính. |
| 12–16 | Menu 3 | Giảm ảnh còn 400×300, tăng 1000 vòng để lộ mất cân bằng tải. So sánh static vs dynamic. |
| 16–20 | Menu 4 | Hỏi lại câu ở phút 0, rồi bật `--ignore-t`: terminal in ra số lõi vật lý (máy này là 12) dù gõ `-t 4`. Đây là "khoảnh khắc a-ha". |
| 20–23 | Menu 5 + Q&A | Mở ảnh, nhắc 3 lỗi: TBB/OpenMP, coroutine, P4/P5. |
| 23–25 | Chốt | 3 khuyến nghị: coi mã LLM là bản nháp, đo thay vì tin, soát coroutine/MPI. |

## 6. Tiêu chí thành công

- Khán giả tự thay đổi ít nhất 2 thông số (số luồng, kích thước ảnh hoặc schedule).
- Có ít nhất một lần đoán sai được phản hồi bằng số liệu thật (đặc biệt ở Menu 4).
- Ra về trả lời được: vì sao `-t` chưa chắc đúng, vì sao dynamic thắng static, và vì sao phải loại I/O khỏi phép đo.

## 7. Rủi ro và dự phòng

| Rủi ro | Dự phòng |
|---|---|
| Hết thời gian | Chạy `run_demo.bat` (bản cũ, ~1 phút) rồi chiếu slide |
| Terminal tương tác lỗi | Dùng bản `.bat`; các thông số vẫn sửa được bằng tay trong lệnh |
| Ảnh PGM không mở được | Pillow đổi sang PNG (đã có sẵn) |
| Máy không có MPI | Không đổi: phần phân tán vẫn chỉ chiếu biểu đồ Hình 7 |
| Số đo nhiễu | Mỗi cấu hình chạy 3 lần, lấy trung bình (thêm vào `interactive.py`) |

## 8. Phạm vi ngoài demo

Không thêm model AI mới trong đợt này (chưa có số liệu thật). Phần bổ sung model mới đã được ghi thành đề xuất có phương pháp ở Phần 6.3.3 của báo cáo.
