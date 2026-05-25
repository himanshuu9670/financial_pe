"""End-to-end API smoke tests (no DB required for health/metrics)."""

import pytest


@pytest.mark.integration
def test_health_endpoint(api_client):
    r = api_client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") in ("healthy", "degraded", "ok")


@pytest.mark.integration
def test_system_status(api_client):
    r = api_client.get("/api/v1/system-status")
    assert r.status_code == 200


@pytest.mark.integration
def test_metrics_prometheus(api_client):
    r = api_client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "") or r.text


@pytest.mark.integration
def test_openapi_docs(api_client):
    r = api_client.get("/docs")
    assert r.status_code == 200


@pytest.mark.integration
def test_upload_rejects_non_pdf(api_client):
    r = api_client.post(
        "/api/v1/upload",
        files={"file": ("evil.txt", b"not a pdf", "text/plain")},
    )
    assert r.status_code in (400, 422, 500)
