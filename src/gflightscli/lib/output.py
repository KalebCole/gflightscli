"""Output formatters — JSON, table, YAML, CSV."""

from __future__ import annotations

import csv
import io
import json
import sys

import click
import yaml


def get_ctx_opts(ctx) -> tuple[str, str | None, bool]:
    """Extract common options from Click context."""
    return (
        ctx.obj.get("format", "json"),
        ctx.obj.get("output"),
        ctx.obj.get("dry_run", False),
    )


def format_output(data: dict | list, metadata: dict, fmt: str) -> str:
    """Format data + metadata into the requested output format string."""
    if fmt == "json":
        return _format_json(data, metadata)
    elif fmt == "table":
        return _format_table(data, metadata)
    elif fmt == "yaml":
        return _format_yaml(data, metadata)
    elif fmt == "csv":
        return _format_csv(data, metadata)
    else:
        return _format_json(data, metadata)


def emit(data: dict | list, metadata: dict, fmt: str, output_path: str | None = None) -> None:
    """Format and write output to stdout or file."""
    text = format_output(data, metadata, fmt)
    if output_path:
        with open(output_path, "w") as f:
            f.write(text)
            f.write("\n")
        click.echo(f"Output written to {output_path}", err=True)
    else:
        click.echo(text)


def success_envelope(data: dict | list, metadata: dict | None = None) -> dict:
    """Wrap data in the standard success envelope."""
    envelope = {"status": "success", "data": data}
    if metadata:
        envelope["metadata"] = metadata
    return envelope


def _format_json(data: dict | list, metadata: dict) -> str:
    envelope = success_envelope(data, metadata)
    return json.dumps(envelope, indent=2, default=str)


def _format_yaml(data: dict | list, metadata: dict) -> str:
    envelope = success_envelope(data, metadata)
    return yaml.dump(envelope, default_flow_style=False, sort_keys=False).rstrip()


def _format_table(data: dict | list, metadata: dict) -> str:
    rows = data if isinstance(data, list) else [data]
    if not rows:
        return "(no results)"
    if isinstance(rows[0], dict):
        headers = list(rows[0].keys())
        col_widths = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers}
        header_line = "  ".join(h.ljust(col_widths[h]) for h in headers)
        sep_line = "  ".join("-" * col_widths[h] for h in headers)
        lines = [header_line, sep_line]
        for row in rows:
            lines.append("  ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers))
        return "\n".join(lines)
    else:
        return "\n".join(str(r) for r in rows)


def _format_csv(data: dict | list, metadata: dict) -> str:
    rows = data if isinstance(data, list) else [data]
    if not rows or not isinstance(rows[0], dict):
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().rstrip()
