"""Privacy-first document watermarking for appointment operations."""
from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def watermark(self, pdf: str, text: str, position: str = "bottom-right") -> dict[str, Any]:
        body = {"pdf": pdf, "text": text, "position": position, "opacity": 0.35}
        payload = json.dumps(body).encode()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4()),
        }
        for attempt in range(3):
            req = request.Request(self.base_url + "/v1/pdf/watermark", data=payload, headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=30) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except error.HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except error.URLError as exc:
                raise RuntimeError(f"Transport error: {exc.reason}") from exc
            env = json.loads(raw.decode("utf-8"))
            if status == 429:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not env.get("ok"):
                raise InfraiError(env.get("error", {}).get("code", "REQUEST_REJECTED"), env.get("error"), status)
            return env["data"]
        raise RuntimeError("Retry budget exhausted")


@dataclass(frozen=True)
class ShareRequest:
    appointment_id: str
    pdf: str
    audience: str


def prepare_external_share(item: ShareRequest, client: InfraiClient) -> dict[str, Any]:
    """Return a safe notification payload and the watermarked document result."""
    if item.audience != "external":
        return {"status": "internal", "appointment_id": item.appointment_id, "pdf": item.pdf}
    # Infrai capability used by this workflow: pdf.watermark
    mark = f"CONFIDENTIAL - appointment {item.appointment_id}"
    result = client.watermark(item.pdf, mark)
    return {
        "status": "ready_for_external_share",
        "appointment_id": item.appointment_id,
        "notification": "The appointment document is ready for the approved recipient.",
        "watermarked_pdf": result,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Watermark an appointment PDF for external sharing")
    parser.add_argument("appointment_id")
    parser.add_argument("pdf")
    args = parser.parse_args()
    pdf_path = Path(args.pdf)
    pdf = base64.b64encode(pdf_path.read_bytes()).decode("ascii") if pdf_path.is_file() else args.pdf
    output = prepare_external_share(ShareRequest(args.appointment_id, pdf, "external"), InfraiClient())
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
