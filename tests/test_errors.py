"""Tests for error types and envelopes."""

import json

import pytest

from gflightscli.lib.errors import (
    APIError,
    GFlightsError,
    InternalError,
    NotFoundError,
    ValidationError,
    handle_error,
)


def test_api_error_code():
    e = APIError("api broke")
    assert e.code == 1
    assert e.error_type == "api_error"


def test_validation_error_code():
    e = ValidationError("bad input")
    assert e.code == 3
    assert e.error_type == "validation_error"


def test_not_found_error_code():
    e = NotFoundError("nothing here")
    assert e.code == 4
    assert e.error_type == "not_found"


def test_internal_error_code():
    e = InternalError("oops")
    assert e.code == 5
    assert e.error_type == "internal_error"


def test_error_to_dict():
    e = ValidationError("missing field X")
    d = e.to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == 3
    assert d["error"]["type"] == "validation_error"
    assert d["error"]["message"] == "missing field X"


def test_error_json_serializable():
    e = APIError("timeout")
    text = json.dumps(e.to_dict())
    parsed = json.loads(text)
    assert parsed["error"]["code"] == 1


def test_handle_error_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        handle_error(NotFoundError("no flights"))
    assert exc_info.value.code == 4
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["status"] == "error"
    assert parsed["error"]["code"] == 4


def test_base_error_defaults():
    e = GFlightsError("generic")
    assert e.code == 5
    assert e.error_type == "internal_error"
