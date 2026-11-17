import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_mock_live_services():
    r1 = client.get('/api/live-demo/auth-gateway')
    assert r1.status_code == 401
    assert "JWT_EXPIRED" in r1.text

    r2 = client.get('/api/live-demo/order-service')
    assert r2.status_code == 500
    assert "NullPointerException" in r2.text

    r3 = client.get('/api/live-demo/inventory-service')
    assert r3.status_code == 409

    r4 = client.get('/api/live-demo/health')
    assert r4.status_code == 200
    assert r4.json()["status"] == "HEALTHY"

def test_live_probe_and_ingest_loop():
    # 1. Probe local demo endpoint
    probe_payload = {
        "url": "/api/live-demo/auth-gateway",
        "method": "GET",
        "expected_status": 200
    }
    probe_res = client.post('/api/live/probe', json=probe_payload)
    assert probe_res.status_code == 200
    pdata = probe_res.json()
    assert pdata["status_code"] == 401
    assert pdata["status_matches"] is False
    assert "latency_ms" in pdata

    # 2. Ingest live failure and run loop engineering
    ingest_payload = {
        "url": "/api/live-demo/auth-gateway",
        "method": "GET",
        "actual_status": 401,
        "expected_status": 200,
        "error_message": pdata["body"],
        "latency_ms": pdata["latency_ms"],
        "test_name": "Live Auth Gateway Probe",
        "test_file": "tests/test_live_auth.py",
        "start_now": True
    }
    ingest_res = client.post('/api/live/ingest', json=ingest_payload)
    assert ingest_res.status_code == 200
    idata = ingest_res.json()
    assert idata["is_live"] is True
    assert idata["actual_status"] == 401
    assert idata["status"] in ["AWAITING_APPROVAL", "APPROVED"]
    assert idata["code_patch"] is not None
    assert "--- a/" in idata["code_patch"]
    assert idata["opszero_level"] in ["L3-ZeroTouch", "L2-Assisted"]

    # 3. Test verification
    verify_res = client.post(f"/api/live/verify/{idata['id']}")
    assert verify_res.status_code == 200
    vdata = verify_res.json()
    assert "probe_result" in vdata

