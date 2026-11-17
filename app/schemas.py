import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
ALLOWED_FILE_EXTENSIONS = (".py", ".ts", ".js")
REJECTION_REASONS = {
    "Incorrect root cause",
    "Insufficient evidence",
    "Incorrect target file",
    "Recommendation is incomplete",
    "Recommendation is unsafe",
    "Missing context",
    "Other",
}

class AnalysisCreate(BaseModel):
    test_name: str = Field(min_length=2, max_length=200, description="Descriptive name of the failed test")
    endpoint: str = Field(min_length=1, max_length=250, description="API endpoint path starting with /")
    method: str = Field(default="GET", description="HTTP Method")
    expected_status: int = Field(default=200, ge=100, le=599, description="Expected HTTP response status code")
    actual_status: int = Field(ge=100, le=599, description="Actual HTTP response status code")
    error_message: str = Field(min_length=1, max_length=10000, description="Error message, exception text or response body")
    test_file: str = Field(default="tests/api_test.py", max_length=300, description="Associated test file path (.py, .ts, .js)")
    start_now: bool = Field(default=False, description="Whether to start analysis loop immediately upon creation")

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("/"):
            raise ValueError("API endpoint must start with /")
        return v

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ALLOWED_METHODS:
            raise ValueError(f"Method must be one of: {', '.join(sorted(ALLOWED_METHODS))}")
        return v

    @field_validator("test_file")
    @classmethod
    def validate_test_file(cls, v: str) -> str:
        v = v.strip()
        if not any(v.endswith(ext) for ext in ALLOWED_FILE_EXTENSIONS):
            raise ValueError(f"Test file must end with one of: {', '.join(ALLOWED_FILE_EXTENSIONS)}")
        return v

    @field_validator("error_message")
    @classmethod
    def validate_error_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Please enter an error message or response payload.")
        return v


class Decision(BaseModel):
    reviewer_name: str = Field(default="Nisha Kajave", min_length=2, max_length=120)
    decision: Literal["APPROVED", "REJECTED"]
    rejection_reason: Optional[str] = Field(default=None, max_length=120)
    comments: str = Field(default="", max_length=5000)

    @field_validator("comments")
    @classmethod
    def validate_comments_on_rejection(cls, v: str, info) -> str:
        # Note: in pydantic v2, data can be checked
        return v


class ContextProvide(BaseModel):
    environment: Optional[str] = Field(default="development", max_length=50)
    stack_trace: Optional[str] = Field(default="", max_length=10000)
    request_body: Optional[str] = Field(default="", max_length=10000)
    response_body: Optional[str] = Field(default="", max_length=10000)
    service_logs: Optional[str] = Field(default="", max_length=10000)
    correlation_id: Optional[str] = Field(default="", max_length=100)
    related_file: Optional[str] = Field(default="", max_length=300)
    additional_notes: Optional[str] = Field(default="", max_length=2000)


class TestSuiteRunRequest(BaseModel):
    suite_path: str = Field(default="tests/test_api.py", description="Path to approved test suite")


class LiveProbeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=1000, description="Target live URL or relative demo endpoint")
    method: str = Field(default="GET", description="HTTP Method")
    expected_status: int = Field(default=200, ge=100, le=599)
    headers: dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = Field(default=None)

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ALLOWED_METHODS:
            raise ValueError(f"Method must be one of: {', '.join(sorted(ALLOWED_METHODS))}")
        return v


class LiveIngestRequest(BaseModel):
    url: str = Field(min_length=1, max_length=1000)
    method: str = Field(default="GET")
    actual_status: int = Field(ge=100, le=599)
    expected_status: int = Field(default=200, ge=100, le=599)
    error_message: str = Field(min_length=1, max_length=10000)
    latency_ms: float = Field(default=0.0, ge=0.0)
    test_name: Optional[str] = Field(default=None, max_length=200)
    test_file: Optional[str] = Field(default="tests/live_prober_suite.py", max_length=300)
    start_now: bool = Field(default=True)
