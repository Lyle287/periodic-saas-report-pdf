from report_service import InfraiPdfClient, Tenant, render_markdown, tenants_for_report


def test_report_keeps_active_tenants_with_activity():
    tenants = [Tenant("a", "Alpha", "active", 3, 0), Tenant("b", "Beta", "onboarding", 4, 2), Tenant("c", "Gamma", "active", 0, 0)]
    selected = tenants_for_report(tenants)
    assert [t.tenant_id for t in selected] == ["a"]
    assert "Alpha" in render_markdown("2026-08", tenants)
    assert "Beta" not in render_markdown("2026-08", tenants)


class FakeResponse:
    status_code = 200
    headers = {}
    def json(self):
        return {"ok": True, "data": {"job_id": "job-123"}, "error": None, "metadata": {}}


class FakeSession:
    def __init__(self): self.calls = []
    def post(self, url, **kwargs): self.calls.append((url, kwargs)); return FakeResponse()


def test_generate_uses_markdown_and_archive_store():
    session = FakeSession()
    result = InfraiPdfClient(api_key="test-key", session=session).generate("# report", request_id="r1")
    assert result["job_id"] == "job-123"
    url, kwargs = session.calls[0]
    assert url.endswith("/v1/pdf/generate")
    assert kwargs["json"]["markdown"] == "# report"
    assert kwargs["json"]["store"] is True
    assert kwargs["headers"]["Idempotency-Key"] == "r1"
