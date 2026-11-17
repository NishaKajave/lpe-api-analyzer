import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get('/')
    assert response.status_code == 200
    assert "LoopLens" in response.text

def test_list_analyses():
    response = client.get('/api/analyses')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 20

def test_metrics_endpoint():
    response = client.get('/api/metrics')
    assert response.status_code == 200
    m = response.json()
    assert "total_failures" in m
    assert "average_attempts_to_pass" in m
    assert "attempt_distribution" in m

def test_secret_masking():
    payload = {
        "test_name": "Test Auth Secret Leak",
        "endpoint": "/api/v1/auth/test",
        "method": "POST",
        "expected_status": 200,
        "actual_status": 401,
        "error_message": "Invalid credentials for Authorization: Bearer superSecretToken1234567890 and password=mySecretPassword123",
        "test_file": "tests/test_auth.py",
        "start_now": False
    }
    response = client.post('/api/analyses', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[MASKED" in data["error_message"]
    assert "superSecretToken1234567890" not in data["error_message"]
    assert "mySecretPassword123" not in data["error_message"]
    assert data["masked_value_count"] >= 2

def test_create_and_run_auth_record():
    payload = {
        "test_name": "Integration Auth Test",
        "endpoint": "/api/v1/auth/user",
        "method": "GET",
        "expected_status": 200,
        "actual_status": 401,
        "error_message": "Unauthorized: token expired",
        "test_file": "tests/test_auth.py",
        "start_now": False
    }
    created = client.post('/api/analyses', json=payload)
    assert created.status_code == 200
    rec_id = created.json()['id']

    # Run analysis
    result = client.post(f"/api/analyses/{rec_id}/run")
    assert result.status_code == 200
    res_data = result.json()
    assert res_data['status'] in ['AWAITING_APPROVAL', 'APPROVED']
    assert res_data['attempts_used'] >= 1
    assert res_data['validation_score'] >= 80
    assert res_data['confidence_score'] >= 80
    assert res_data['stop_reason'] == "PASSED_VALIDATION"

    # Verify attempts history stored separately
    attempts_resp = client.get(f"/api/analyses/{rec_id}/attempts")
    assert attempts_resp.status_code == 200
    attempts = attempts_resp.json()
    assert len(attempts) == res_data['attempts_used']
    assert "required_fields_score" in attempts[0]
    assert "evidence_score" in attempts[0]

def test_human_approval_decision():
    # Create and run
    payload = {
        "test_name": "Approval Test Case",
        "endpoint": "/api/v1/users/42",
        "method": "GET",
        "expected_status": 200,
        "actual_status": 401,
        "error_message": "Unauthorized token",
        "test_file": "tests/test_auth.py",
        "start_now": True
    }
    res = client.post('/api/analyses', json=payload).json()
    rec_id = res['id']

    # Test approval
    dec_payload = {
        "reviewer_name": "Nisha Kajave",
        "decision": "APPROVED",
        "comments": "The recommendation correctly identifies the expired token."
    }
    dec_res = client.post(f"/api/analyses/{rec_id}/decision", json=dec_payload)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data['status'] == "APPROVED"
    assert dec_data['reviewed_by'] == "Nisha Kajave"

def test_human_rejection_mandatory_reason():
    payload = {
        "test_name": "Rejection Test Case",
        "endpoint": "/api/v1/users/55",
        "method": "GET",
        "expected_status": 200,
        "actual_status": 401,
        "error_message": "Unauthorized token",
        "test_file": "tests/test_auth.py",
        "start_now": True
    }
    res = client.post('/api/analyses', json=payload).json()
    rec_id = res['id']

    # Reject without reason should fail
    bad_dec = {
        "reviewer_name": "Nisha Kajave",
        "decision": "REJECTED",
        "comments": ""
    }
    bad_res = client.post(f"/api/analyses/{rec_id}/decision", json=bad_dec)
    assert bad_res.status_code == 400

    # Reject with reason and comment should succeed
    good_dec = {
        "reviewer_name": "Nisha Kajave",
        "decision": "REJECTED",
        "rejection_reason": "Incorrect target file",
        "comments": "The suggested file is incorrect. The authentication fixture is located in tests/conftest.py."
    }
    good_res = client.post(f"/api/analyses/{rec_id}/decision", json=good_dec)
    assert good_res.status_code == 200
    assert good_res.json()['status'] == "REJECTED"
    assert good_res.json()['rejection_reason'] == "Incorrect target file"

def test_needs_more_context_workflow():
    payload = {
        "test_name": "Vague Server Error",
        "endpoint": "/api/v1/orders/dispatch",
        "method": "POST",
        "expected_status": 200,
        "actual_status": 500,
        "error_message": "Something went wrong",
        "test_file": "tests/test_orders.py",
        "start_now": True
    }
    res = client.post('/api/analyses', json=payload).json()
    assert res['status'] == "NEEDS_MORE_CONTEXT"
    assert res['stop_reason'] == "INSUFFICIENT_CONTEXT"

    # Provide more context
    ctx_payload = {
        "environment": "staging",
        "stack_trace": "File 'order_service.py', line 92 in dispatch: KeyError 'customer_id'",
        "request_body": "{\"order_id\": 992}",
        "response_body": "{\"error\": \"Something went wrong\"}",
        "service_logs": "2026-11-03 ERROR [OrderService] Customer identifier missing in payload.",
        "correlation_id": "CORR-9921-X",
        "related_file": "app/services/order_service.py",
        "additional_notes": "Added customer verification context"
    }
    re_res = client.post(f"/api/analyses/{res['id']}/context", json=ctx_payload)
    assert re_res.status_code == 200
    assert re_res.json()['status'] in ["AWAITING_APPROVAL", "APPROVED"]
    assert re_res.json()['stop_reason'] == "PASSED_VALIDATION"

def test_approved_pytest_execution():
    payload = {"suite_path": "tests/test_auth_suite.py"}
    response = client.post('/api/test-suite/run', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "suite_name" in data
    assert data["failed"] >= 1
    assert data["ingested_count"] >= 1
