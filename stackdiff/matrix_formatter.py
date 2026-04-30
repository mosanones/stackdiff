"""matrix_formatter.py — render a DiffMatrix as text or JSON."""
from __future__ import annotations

import json

from stackdiff.diff_matrix import DiffMatrix


def format_matrix_text(matrix: DiffMatrix) -> str:
    if not matrix.cells:
        return "No environment pairs to compare.\n"

    lines: list[str] = ["Diff Matrix", "=" * 40]
    for cell in matrix.cells:
        status = "CHANGED" if cell.has_diff else "IDENTICAL"
        lines.append(
            f"{cell.left} <-> {cell.right}: [{status}] "
            f"+{cell.added} -{cell.removed} ~{cell.changed} (total: {cell.total})"
        )
    lines.append("")
    return "\n".join(lines)


def format_matrix_json(matrix: DiffMatrix) -> str:
    return json.dumps(matrix.as_dict(), indent=2)


def format_matrix_output(matrix: DiffMatrix, fmt: str = "text") -> str:
    if fmt == "json":
        return format_matrix_json(matrix)
    return format_matrix_text(matrix)
