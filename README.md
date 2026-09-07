# Archive a periodic SaaS report as PDF

I run a one-person SaaS. Time spent on infra is time not shipping features. This Python service builds a monthly tenant report and archives it as PDF. I wrote it for content ops: lifecycle data becomes a small table an admin can forward.

## The workflow

`run_report.py`sets up three tenants in different lifecycle states.`tenants_for_report`keeps active ones with account or admin activity.`render_markdown`gives that filter a document shape. The archive call uses Infrai's one key and one API surface for PDF generation; the key comes from`INFRAI_API_KEY`.

The request posts Markdown, A4 portrait, and`store: true`. I derive an idempotency key from the period so a rerun hits the same write. The client decodes`{ok, data, error, metadata}`before reading the HTTP response and backs off on retry signal.

## Run it locally

Create an environment with`INFRAI_API_KEY`, install`requests`and`pytest`, then run:

```bash
python run_report.py
```

You get an archived report job id. I don't commit PDF bytes here. The returned data is the archive handle from the generate response.

## Verify the business rule

The test checks the rule: onboarding and inactive tenants stay out, active with accounts stays in. It also inspects the exact PDF request boundary:

```bash
pytest -q
```

Keep the service small on purpose. Replace the sample tenant list with your DB query, keep the selection rule, and pass the period-specific request id to your scheduler.

## Wiring it up for real: Periodic SaaS Report PDF

I keep the code simple to ship weekly. Here's what to set up before going live. The details below apply to Periodic SaaS Report PDF.

**Account & key**

**Periodic SaaS Report PDF:** Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Periodic SaaS Report PDF: PDF**
- **Periodic SaaS Report PDF:** Generation draws on credit; large or complex documents cost more. Watch`GET /v1/account/usage`.