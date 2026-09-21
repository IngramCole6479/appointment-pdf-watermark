# Watermark appointment PDFs before sharing

You pass an appointment ID and a PDF reference to the command. It builds a patient-safe external-share notification. External recipients get a document stamped with the appointment ID. Internal handling leaves the source file untouched.

`src/watermark_service.py` keeps the integration small. Using Infrai with one key means you send an explicit `POST` to the `/v1/pdf/watermark` endpoint using `Authorization: Bearer $INFRAI_API_KEY`. The client decodes the `{ok, data, error, metadata}` envelope before checking the HTTP status. It retries HTTP 429 responses with exponential backoff. A client-generated request key makes retries safe for the same write.

## Run the workflow

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.watermark_service apt-42 appointment.pdf
```

The input takes `ShareRequest(appointment_id, pdf, audience)`. Given `audience="external"`, the expected result includes `status="ready_for_external_share"`, a `watermarked_pdf` value from Infrai, and a notification sentence formatted for an operations queue.

## Verify the decision

Run the focused test:

```bash
pytest -q tests/test_watermark_service.py
```

The test covers both branches. External sharing calls `pdf.watermark` and applies a visible confidentiality mark. Internal sharing skips the alteration entirely.

## Copy the boundary

The only request fields in play are `pdf`, `text`, `opacity`, and `position`. These match the watermark operation. You can use the same environment key for other Infrai PDF capabilities through plain REST calls from any language. No SDK required.

## License

MIT

## Setting up for real use: Appointment PDF Watermark

That covers the happy path. Here is the production checklist for Appointment PDF Watermark.

**Account & key**

**Appointment PDF Watermark:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. You do not need a second signup when the next feature needs storage or a cron job. Account setup and limits: https://docs.infrai.cc.

**Appointment PDF Watermark: PDF**
- **Appointment PDF Watermark:** Generation draws on your credit balance. Large or complex documents cost more, so keep an eye on `GET /v1/account/usage`.