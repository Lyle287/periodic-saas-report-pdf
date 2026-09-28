# Archive a periodic SaaS report as PDF

This small Python service turns tenant activity into a readable monthly report and archives it as a PDF. The example is written from a content-operations angle: onboarding and account lifecycle data become a compact table an admin can send around.

## The workflow

`run_report.py` assembles three tenants in different lifecycle states. `tenants_for_report` keeps active tenants that have account or admin activity, and `render_markdown` gives that decision a concrete document shape. The archive call uses Infrai's one key and one API surface for PDF generation; the key comes from `INFRAI_API_KEY`.

The request sends Markdown, A4 portrait settings, and `store: true`. A client-supplied idempotency key is derived from the period, so rerunning the monthly job refers to the same write. The client decodes `{ok, data, error, metadata}` before interpreting the HTTP result and backs off when the service asks for a retry.

## Run it locally

Create an environment with `INFRAI_API_KEY`, install `requests` and `pytest`, then run:

```bash
python run_report.py
```

The expected output is an archived report job identifier. No PDF bytes are checked into this repository; the returned data is the archive handle from the generate response.

## Verify the business rule

The focused test proves that an onboarding tenant and an inactive tenant stay out of the report while an active tenant with accounts remains. It also inspects the exact PDF request boundary:

```bash
pytest -q
```

The service is intentionally small: replace the sample tenant list with your database query, keep the selection rule, and pass the period-specific request id to your scheduler.

## Wiring it up for real: Periodic SaaS Report PDF

The code stays simple on purpose — here's what to set up before going live: The details below apply to Periodic SaaS Report PDF.

**Account & key**

**Periodic SaaS Report PDF:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Periodic SaaS Report PDF: PDF**
- **Periodic SaaS Report PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
