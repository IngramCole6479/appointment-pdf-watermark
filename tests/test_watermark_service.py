from src.watermark_service import ShareRequest, prepare_external_share


class RecordingClient:
    def __init__(self):
        self.calls = []

    def watermark(self, pdf, text, position="bottom-right"):
        self.calls.append((pdf, text, position))
        return {"id": "wm-123"}


def test_external_share_watermarks_and_notifies_patient_safe(recorder=None):
    client = recorder or RecordingClient()
    result = prepare_external_share(ShareRequest("apt-42", "pdf-bytes", "external"), client)
    assert result["status"] == "ready_for_external_share"
    assert result["notification"].startswith("The appointment document")
    assert client.calls == [("pdf-bytes", "CONFIDENTIAL - appointment apt-42", "bottom-right")]


def test_internal_share_skips_watermark():
    client = RecordingClient()
    result = prepare_external_share(ShareRequest("apt-42", "pdf-bytes", "internal"), client)
    assert result["status"] == "internal"
    assert client.calls == []
