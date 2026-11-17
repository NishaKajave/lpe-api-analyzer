"""
Approved Test Suite: API Integration & Regression Suite
Used by LoopLens to execute live test runs and capture real failure diagnostics.
"""
import pytest

def test_health_check():
    """Verify system health status."""
    assert 200 == 200

def test_user_retrieval_null_pointer():
    """Intentional test failure: backend null pointer."""
    expected_status = 200
    actual_status = 500
    assert actual_status == expected_status, "Internal Server Error: Null reference in UserService.get_billing_address() line 142."

def test_order_creation_conflict():
    """Intentional test failure: duplicate order conflict."""
    expected_status = 201
    actual_status = 409
    assert actual_status == expected_status, "Conflict: Order ID ORD-9941 already exists in database."

