"""Điểm vào của Trợ lý Tài liệu AI (bản v0.1, chạy bằng dòng lệnh).

Cách dùng:
  python -m app.main summarize --file sample.txt
  python -m app.main summarize --text "nội dung cần tóm tắt" --temperature 0.2
  python -m app.main compare --file sample.txt

Lệnh compare là phần thực hành của Bài 1: cùng một nội dung, chạy ở
temperature 0.2 và 0.9 rồi đặt hai kết quả cạnh nhau, kèm số token đã dùng.
"""
import argparse
import sys
from pathlib import Path

from .gemini_client import GeminiClient, GenerationResult

SUMMARIZE_PROMPT = """Hãy tóm tắt nội dung sau thành một đoạn ngắn, giữ lại các ý quan trọng nhất, không thêm thông tin ngoài nội dung gốc.

Nội dung:
{text}
"""


def _read_input(args) -> str:
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    if getattr(args, "text", None):
        return args.text
    raise SystemExit("Cần --file hoặc --text để có nội dung đầu vào.")


def _print_result(label: str, result: GenerationResult) -> None:
    print(f"\n--- {label} (model: {result.model}, temperature: {result.temperature}) ---")
    print(result.text)
    cost = result.estimated_cost_usd()
    cost_text = f", chi phí ước tính: ${cost:.6f}" if cost is not None else ""
    print(
        f"[token] vào: {result.input_tokens}, ra: {result.output_tokens}, "
        f"tổng: {result.total_tokens}{cost_text}"
    )


def cmd_summarize(args) -> None:
    client = GeminiClient(model=args.model)
    prompt = SUMMARIZE_PROMPT.format(text=_read_input(args))
    result = client.generate(prompt, temperature=args.temperature)
    _print_result("Tóm tắt", result)


def cmd_compare(args) -> None:
    client = GeminiClient(model=args.model)
    prompt = SUMMARIZE_PROMPT.format(text=_read_input(args))
    low = client.generate(prompt, temperature=0.2)
    high = client.generate(prompt, temperature=0.9)
    _print_result("Temperature 0.2 (ổn định, bám sát gốc)", low)
    _print_result("Temperature 0.9 (đa dạng, dễ thêm ý)", high)
    print(
        "\nĐể ý: temperature thấp cho bản tóm tắt bám sát nội dung gốc hơn, "
        "temperature cao diễn đạt khác đi nhiều hơn và dễ thêm ý không có trong bài. "
        "Số token vào bằng nhau, token ra khác nhau một chút giữa hai lần chạy."
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="tro-ly-tai-lieu-ai")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("summarize", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--file", help="Đường dẫn file văn bản đầu vào")
        p.add_argument("--text", help="Nội dung đầu vào viết trực tiếp")
        p.add_argument(
            "--model",
            default=None,
            help="Model Gemini cho lần chạy này, ví dụ gemini-3.1-flash-lite. "
            "Không truyền thì dùng GEMINI_MODEL trong .env",
        )
        if name == "summarize":
            p.add_argument("--temperature", type=float, default=0.2)

    args = parser.parse_args()
    if args.command == "summarize":
        cmd_summarize(args)
    elif args.command == "compare":
        cmd_compare(args)


if __name__ == "__main__":
    sys.exit(main())
