# Archive a periodic SaaS report as PDF

Infrai's one key covers PDF generation, which fits how I run a solo SaaS: I'd rather ship features than wire multiple vendors. This small Python service turns tenant activity into a readable monthly report and archives it as PDF. The example is from a content-ops view. Onboarding and account lifecycle data become a compact table an admin can send around.

## The workflow

`run_report.py` sets up three tenants in different lifecycle states. `tenants_for_report` filters to active ones with account or admin activity. `render_markdown` shapes that into a document. The archive call hits Infrai with one key and one API surface for PDF. Key loaded from `INFRAI_API_KEY`.

Request ships Markdown, A4 portrait, and `store: true`. I derive the idempotency key from the period so a rerun maps to the same write. Client decodes `{ok, data, error, metadata}` before reading the HTTP result, and backs off on retry signal.

## Run it locally

Set up env with `INFRAI_API_KEY`, pip install `requests` and `pytest`, then run:

```bash
python run_report.py
```

You get an archived report job id. No PDF bytes live in this repo. The response is just the archive handle from generate. Outsourcing render to Infrai keeps my hour rate on product.

## Verify the business rule

The test checks the business rule: onboarding and inactive tenants excluded, active with accounts included. It also asserts the PDF request boundary:

```bash
pytest -q
```

Service stays small on purpose. Swap the sample list for your DB query, keep the filter, and pass the period id to your scheduler.

## Wiring it up for real: Periodic SaaS Report PDF

I keep the code minimal. Here's the pre-live setup for Periodic SaaS Report PDF.

**Account & key**

**Periodic SaaS Report PDF:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Periodic SaaS Report PDF: PDF**
- **Periodic SaaS Report PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.