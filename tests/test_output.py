"""Tests for output formatters."""

import json

import yaml

from gflightscli.lib.output import format_output, success_envelope


SAMPLE_DATA = [
    {"airline": "AA", "price": 450, "stops": 0},
    {"airline": "UA", "price": 520, "stops": 1},
]
SAMPLE_METADATA = {"origin": "SEA", "destination": "JFK"}


def test_json_format():
    result = format_output(SAMPLE_DATA, SAMPLE_METADATA, "json")
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert len(parsed["data"]) == 2
    assert parsed["metadata"]["origin"] == "SEA"
    assert parsed["data"][0]["price"] == 450


def test_yaml_format():
    result = format_output(SAMPLE_DATA, SAMPLE_METADATA, "yaml")
    parsed = yaml.safe_load(result)
    assert parsed["status"] == "success"
    assert len(parsed["data"]) == 2


def test_table_format():
    result = format_output(SAMPLE_DATA, SAMPLE_METADATA, "table")
    lines = result.strip().split("\n")
    assert len(lines) == 4  # header + separator + 2 rows
    assert "airline" in lines[0]
    assert "AA" in lines[2]


def test_csv_format():
    result = format_output(SAMPLE_DATA, SAMPLE_METADATA, "csv")
    lines = result.strip().replace("\r", "").split("\n")
    assert lines[0] == "airline,price,stops"
    assert "AA,450,0" in lines[1]


def test_success_envelope():
    env = success_envelope({"foo": "bar"}, {"key": "val"})
    assert env["status"] == "success"
    assert env["data"]["foo"] == "bar"
    assert env["metadata"]["key"] == "val"


def test_success_envelope_no_metadata():
    env = success_envelope([1, 2, 3])
    assert "metadata" not in env
    assert env["data"] == [1, 2, 3]


def test_empty_list_table():
    result = format_output([], {}, "table")
    assert result == "(no results)"


def test_single_dict_formats():
    data = {"name": "test", "value": 42}
    # JSON
    parsed = json.loads(format_output(data, {}, "json"))
    assert parsed["data"]["name"] == "test"
    # Table
    table = format_output(data, {}, "table")
    assert "name" in table
    assert "test" in table
