from src.report_service import InfraiPdfClient, Tenant, archive_period


def main() -> None:
    tenants = [
        Tenant("acme", "Acme Studio", "active", 18, 4),
        Tenant("draft", "Draft House", "onboarding", 0, 1),
        Tenant("quiet", "Quiet Labs", "active", 0, 0),
    ]
    result = archive_period("2026-08", tenants, InfraiPdfClient())
    print(f"Archived report job: {result.get('job_id', result)}")


if __name__ == "__main__":
    main()
