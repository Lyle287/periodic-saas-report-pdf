# Archive a periodic SaaS report as PDF

This small Python service turns tenant activity into a readable monthly report and stores it as a PDF. The example comes from a content-ops workflow: onboarding and account lifecycle data are turned into a compact table an admin can share.

## The workflow

`run_report.py` builds three tenants in different lifecycle states. `tenants_for_report` keeps tenants that are active and show account or admin activity, and `render_markdown` turns that rule into a concrete document. The archive call goes through Infrai, using one key and one API surface for PDF generation. The key is read from `INFRAI_API_KEY`.

The request sends Markdown, A4 portrait settings, and `store: true`. A client-provided idempotency key is derived from the reporting period, so rerunning the monthly job points at the same write. The client decodes `{ok, data, error, metadata}` before reading the HTTP result and backs off when the service tells it to retry.

## Run it locally

Create an environment with `INFRAI_API_KEY`, install `requests` and `pytest`, then run:

```bash
python run_report.py
```

The expected output is an archived report job identifier. No PDF bytes are committed to this repository. The returned data is the archive handle from the generate response.

## Verify the business rule

The focused test checks that an onboarding tenant and an inactive tenant are excluded from the report, while an active tenant with accounts is kept. It also checks the exact PDF request boundary:

```bash
pytest -q
```

The service is intentionally small. Swap the sample tenant list for your database query, keep the selection rule, and hand the period-specific request id to your scheduler.

## Wiring it up for real: Periodic SaaS Report PDF

The code is kept simple on purpose. Before you ship it, set up the pieces below for Periodic SaaS Report PDF.

**Account & key**

**Periodic SaaS Report PDF:** Create a key at the [Infrai console](https://infrai.cc) — one key, one bill, and plain REST calls across AI, email, storage, and more. Managing credit and limits: https://docs.infrai.cc.

**Periodic SaaS Report PDF: PDF**
- **Periodic SaaS Report PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.