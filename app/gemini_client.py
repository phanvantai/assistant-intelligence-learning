"""Client gọi Gemini API (Interactions API) bằng thư viện chuẩn của Python.

Bài học Giai đoạn 0 nằm ngay trong file này:
- API key chỉ đọc từ biến môi trường, gửi qua header x-goog-api-key, không hard-code.
- temperature được truyền trong generation_config.
- Mỗi lần gọi, API trả về usage gồm token đầu vào và đầu ra. Đó là cơ sở tính chi phí.
"""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import get_api_key, get_model, get_price_per_1m

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


@dataclass
class GenerationResult:
    text: str
    model: str
    temperature: float | None
    input_tokens: int
    output_tokens: int
    total_tokens: int

    def estimated_cost_usd(self) -> float | None:
        input_price = get_price_per_1m("input", self.model)
        output_price = get_price_per_1m("output", self.model)
        if input_price is None or output_price is None:
            return None
        return (
            self.input_tokens * input_price + self.output_tokens * output_price
        ) / 1_000_000


class GeminiClient:
    def __init__(self, model: str | None = None):
        self.model = model or get_model()
        self._api_key = get_api_key()

    def generate(self, prompt: str, temperature: float | None = None) -> GenerationResult:
        body: dict = {"model": self.model, "input": prompt}
        if temperature is not None:
            body["generation_config"] = {"temperature": temperature}

        request = urllib.request.Request(
            API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"Gemini API trả lỗi HTTP {error.code}: {detail}") from error

        text = ""
        for step in data.get("steps", []):
            if step.get("type") == "model_output":
                for part in step.get("content", []):
                    text += part.get("text", "")

        usage = data.get("usage", {})
        return GenerationResult(
            text=text.strip(),
            model=self.model,
            temperature=temperature,
            input_tokens=int(usage.get("total_input_tokens", 0)),
            output_tokens=int(usage.get("total_output_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
        )

    def generate_stream(
        self, prompt: str, temperature: float | None = None, on_text=None
    ) -> GenerationResult:
        """Gọi Gemini ở chế độ streaming (Bài 3).

        Request thêm "stream": true, response trả về dạng SSE (server-sent
        events) với chuỗi sự kiện:
          interaction.created -> step.start -> step.delta (nhiều lần)
          -> step.stop -> interaction.completed
        Mỗi step.delta mang một mẩu chữ mới trong delta.text (khi delta.type
        là "text"); nhận mẩu nào thì gọi on_text ngay để in ra màn hình.
        usage chỉ xuất hiện ở sự kiện interaction.completed cuối cùng, nên
        token và chi phí chỉ biết chắc khi stream đã kết thúc. Nếu stream đứt
        trước sự kiện đó thì lần gọi coi như thất bại, dù đã nhận một phần chữ.
        """
        body: dict = {"model": self.model, "input": prompt, "stream": True}
        if temperature is not None:
            body["generation_config"] = {"temperature": temperature}

        request = urllib.request.Request(
            API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )

        text_parts: list[str] = []
        usage: dict | None = None
        event_name = ""
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8", "replace").strip()
                    if line.startswith("event:"):
                        event_name = line[len("event:"):].strip()
                        continue
                    if not line.startswith("data:"):
                        continue
                    payload = line[len("data:"):].strip()
                    if not payload or payload == "[DONE]":
                        continue
                    event = json.loads(payload)
                    event_type = event.get("event_type", "") or event_name
                    if event_type == "step.delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text":
                            chunk = delta.get("text", "")
                            if chunk:
                                text_parts.append(chunk)
                                if on_text is not None:
                                    on_text(chunk)
                    elif event_type == "interaction.completed":
                        interaction = event.get("interaction", event)
                        usage = interaction.get("usage", {})
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"Gemini API trả lỗi HTTP {error.code}: {detail}") from error
        except (urllib.error.URLError, ConnectionError) as error:
            raise RuntimeError(
                f"Stream bị đứt giữa chừng, kết quả chưa hoàn chỉnh: {error}"
            ) from error

        if usage is None:
            raise RuntimeError(
                "Stream kết thúc mà không có sự kiện interaction.completed, "
                "kết quả chưa hoàn chỉnh nên coi như lần gọi thất bại."
            )
        return GenerationResult(
            text="".join(text_parts).strip(),
            model=self.model,
            temperature=temperature,
            input_tokens=int(usage.get("total_input_tokens", 0)),
            output_tokens=int(usage.get("total_output_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
        )
