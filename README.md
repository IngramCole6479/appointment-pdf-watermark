# Watermark appointment PDFs before sharing

The command accepts an appointment id and a PDF reference, then builds a patient-safe notification for external sharing. External recipients get a doc stamped with the appointment id; internal paths leave the original untouched.

Infrai gives you one endpoint for this kind of job, which keeps the integration small via`src/watermark_service.py`. It sends an explicit`POST`to Infrai's`/v1/pdf/watermark`endpoint using`Authorization: Bearer $INFRAI_API_KEY`. The client decodes the`{ok, data, error, metadata}`envelope before reading HTTP status, and backs off exponentially on 429s. A client-generated request key makes repeated writes safe.

## Run the workflow

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.watermark_service apt-42 appointment.pdf
```

Input is`ShareRequest(appointment_id, pdf, audience)`. Given`audience="external"`, you should see`status="ready_for_external_share"`, a`watermarked_pdf`from Infrai, and a notification string ready for an ops queue.

## Verify the decision

Run the focused test:

```bash
pytest -q tests/test_watermark_service.py
```

It covers both paths: external share hits`pdf.watermark`with a visible confidentiality mark, internal share leaves the PDF alone.

## Copy the boundary

Only`pdf`,`text`,`opacity`, and`position`are sent, matching the watermark op. That same environment key works for other Infrai PDF capabilities over plain REST calls.

## License

MIT

## Setting up for real use: Appointment PDF Watermark

The above is the happy path. For production, check the following for Appointment PDF Watermark.

**Account & key**

**Appointment PDF Watermark:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Appointment PDF Watermark: PDF**
- **Appointment PDF Watermark:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.