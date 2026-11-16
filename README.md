# Trợ lý Tài liệu AI

Project duy nhất xuyên suốt lộ trình học AI Engineer của Tai. Không có project phụ:
mỗi giai đoạn của lộ trình chỉ thêm một phần nhỏ vào chính app này, như phát triển
một sản phẩm thật theo từng phiên bản.

App giúp người dùng đưa tài liệu và nội dung vào, hiểu nhanh, hỏi đáp và biến
thành việc làm được.

## Lộ trình phát triển của chính project này

| Phiên bản | Giai đoạn học | Phần được thêm vào app |
| --- | --- | --- |
| v0.1 | Giai đoạn 0: nền tảng LLM | Lõi gọi model: tóm tắt nội dung, so sánh temperature ngay trong app, hiện token đã dùng sau mỗi lần gọi |
| v0.2 | Giai đoạn 1: prompt và structured output | Trích xuất ý chính và việc cần làm ra JSON có schema |
| v0.3 | Giai đoạn 2: RAG | Kho tài liệu riêng, hỏi đáp dựa trên tài liệu của người dùng kèm trích dẫn |
| v0.4 | Giai đoạn 3: agents và tool calling | Trợ lý tự làm việc nhiều bước trên kho tài liệu, người dùng duyệt trước khi thực hiện |
| v0.5 | Giai đoạn 4: production AI | Bộ đánh giá chất lượng, theo dõi chi phí và lỗi, deploy cho người khác dùng thử |
| v0.6 | Giai đoạn 5: multimodal và fine-tune | Thêm xử lý ảnh hoặc âm thanh, hoặc fine-tune một tính năng có sẵn |
| v1.0 | Capstone | Hoàn thiện chính app này thành sản phẩm portfolio |

## Trạng thái hiện tại: v0.1

Đã có:

- `app/gemini_client.py`: client gọi Gemini API (Interactions API), truyền temperature,
  đọc usage (token vào, token ra, tổng token) sau mỗi lần gọi.
- `app/main.py`: giao diện dòng lệnh với hai lệnh `summarize` và `compare`.
  Lệnh `compare` là phần thực hành của Bài 1 (token, context window, temperature):
  cùng một nội dung chạy ở temperature 0.2 và 0.9, xem hai kết quả cạnh nhau.
- `app/config.py`: đọc API key từ biến môi trường hoặc file `.env`. Key không nằm trong code.

Chưa có (thuộc các phần học sau của Giai đoạn 0): giao diện web, streaming, FastAPI.

## Cách chạy

Yêu cầu: Python 3.11 trở lên. Không cần cài thêm thư viện nào cho v0.1.

1. Tạo API key miễn phí tại Google AI Studio (trang API keys), bằng tài khoản Google.
2. Copy `.env.example` thành `.env` và điền key vào biến `GEMINI_API_KEY`.
   File `.env` đã nằm trong `.gitignore`, không được commit.
3. Chạy thử:

```bash
python -m app.main summarize --file sample.txt
python -m app.main compare --file sample.txt
```

## Nhật ký học (blog)

Quá trình học được viết lại mỗi ngày trên blog cá nhân
[taiphanvan.dev](https://taiphanvan.dev/vi/blog), theo tinh thần học công khai:
mỗi bài gắn với đúng phần app vừa được làm xong.

- Ngày 1 (16/11/2026): [Bắt đầu học AI Engineer, và quyết định chỉ làm đúng một project](https://taiphanvan.dev/vi/blog/ngay-1-bat-dau-hoc-ai-engineer)

## Quy tắc secret

- Không bao giờ dán API key vào chat, vào code hoặc vào commit.
- Key chỉ sống trong file `.env` ở máy chạy app, hoặc trong kho bảo mật khi nhờ Muse chạy hộ.
- Tạo một key riêng cho project này và giới hạn key chỉ dùng cho Gemini API.
  Nếu lỡ lộ key, xoá key cũ và tạo key mới.
