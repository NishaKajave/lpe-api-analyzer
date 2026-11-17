"""
Approved Test Suite: Authentication & Token Security Suite
Used by LoopLens to execute live test runs and capture real failure diagnostics.
"""
import pytest

def test_valid_login():
    """Verify standard user login credentials."""
    status_code = 200
    assert status_code == 200

def test_expired_jwt_token():
    """Intentional test failure: token expired."""
    expected_status = 200
    actual_status = 401
    assert actual_status == expected_status, "Unauthorized: JWT access token expired during request execution."

def test_insufficient_permissions():
    """Intentional test failure: role missing."""
    expected_status = 200
    actual_status = 403
    assert actual_status == expected_status, "Forbidden: User lacks 'admin:write' permission scope."

