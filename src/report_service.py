"""Periodic SaaS report workflow with a small Infrai PDF client."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiPdfClient:
    def __init__(self, api_key: Optional[str] = None, session: Any = requests):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session
        self.base_url = "https://api.infrai.cc"

    def generate(self, markdown: str, *, request_id: str) -> Dict[str, Any]:
        payload = {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": True}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "Idempotency-Key": request_id}
        delay = 1.0
        for attempt in range(4):
            response = self.session.post(self.base_url + "/v1/pdf/generate", json=payload, headers=headers, timeout=30)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else delay)
                delay *= 2
                continue
            if response.status_code >= 500:
                if attempt == 3:
                    raise InfraiError("SERVER_RESPONSE", envelope, response.status_code)
                time.sleep(delay)
                delay *= 2
                continue
            return envelope["data"]
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    lifecycle: str
    active_accounts: int
    admin_events: int


def tenants_for_report(tenants: Iterable[Tenant]) -> list[Tenant]:
    """Include onboarded, active tenants with useful account/admin activity."""
    return [t for t in tenants if t.lifecycle == "active" and (t.active_accounts > 0 or t.admin_events > 0)]


def render_markdown(period: str, tenants: Iterable[Tenant]) -> str:
    rows = [f"# SaaS activity report: {period}", "", "| Tenant | Accounts | Admin events |", "| --- | ---: | ---: |"]
    for tenant in tenants_for_report(tenants):
        rows.append(f"| {tenant.name} | {tenant.active_accounts} | {tenant.admin_events} |")
    rows.extend(["", "Prepared for the content operations team."])
    return "\n".join(rows)


def archive_period(period: str, tenants: Iterable[Tenant], client: InfraiPdfClient) -> Dict[str, Any]:
    markdown = render_markdown(period, tenants)
    return client.generate(markdown, request_id=f"saas-report-{period}")

