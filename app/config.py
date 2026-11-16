"""Cấu hình cho Trợ lý Tài liệu AI.

Đọc cấu hình từ biến môi trường, có hỗ trợ file .env ở thư mục gốc của project.
File .env chứa secret thật và KHÔNG bao giờ được commit (đã có trong .gitignore).
Trong repo chỉ có .env.example ghi tên biến, không có giá trị thật.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Chưa có GEMINI_API_KEY. Hãy copy .env.example thành .env "
            "và điền API key của bạn vào đó (key không được commit lên git)."
        )
    return key


def get_model() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()


def get_price_per_1m(kind: str) -> float | None:
    """Đơn giá USD cho 1 triệu token, do người dùng tự cấu hình trong .env.

    kind là 'input' hoặc 'output'. Trả về None nếu chưa cấu hình,
    khi đó app chỉ hiện số token chứ không tính tiền.
    """
    name = "GEMINI_INPUT_PRICE_PER_1M" if kind == "input" else "GEMINI_OUTPUT_PRICE_PER_1M"
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None
