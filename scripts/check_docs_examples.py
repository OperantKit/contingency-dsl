#!/usr/bin/env python3
"""
Parse every DSL example in docs/en/syntax-examples.md and
docs/ja/syntax-examples.md with the Python reference parser.

Each unlabelled ``` block is split into examples:
  - A block that contains a `phase` line is a list of whole programs,
    separated by column-0 `--` comment lines.
  - Any other block lists one example per column-0 line. Indented lines
    continue the example above; a `let` line also takes the next line,
    because a program ends with a schedule.

Examples are parsed with the six annotation extensions bundled with the
reference parser. Some annotation keywords are defined by the spec but
rejected by the reference parser (see KNOWN_UNREGISTERED). An example that
fails only on such a keyword is parsed again with that keyword added, and
must then pass; the page marks those examples with a note.

    pip install contingency-dsl-py
    python scripts/check_docs_examples.py

Exit status:
  0  -- every example parsed.
  1  -- an example failed, or a KNOWN_UNREGISTERED keyword no longer needs
        the workaround (drop it here and remove the note from the page).
"""

from __future__ import annotations

import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, ClassVar

from contingency_dsl import parse
from contingency_dsl.annotations import (
    ApparatusExtension,
    ComposedExtension,
    MeasurementExtension,
    StimulusExtension,
    SubjectsExtension,
    TemporalExtension,
)
from contingency_dsl.extensions import ExtensionRegistry

DSL_ROOT = Path(__file__).resolve().parent.parent
PAGES = ("docs/en/syntax-examples.md", "docs/ja/syntax-examples.md")
BLOCK = re.compile(r"^```\n(.*?)^```", re.DOTALL | re.MULTILINE)
UNKNOWN = re.compile(r"unknown annotation '@(\w+)'")

# Annotation keyword -> why the reference parser rejects it.
KNOWN_UNREGISTERED: dict[str, str] = {
    "punisher": (
        "alias of @reinforcer in procedure-stimulus.schema.json; the parser "
        "checks the source keyword before resolving the alias"
    ),
    "cs": "respondent-annotator.schema.json; no bundled extension",
    "us": "respondent-annotator.schema.json; no bundled extension",
}

BUNDLED = (
    StimulusExtension(),
    TemporalExtension(),
    SubjectsExtension(),
    ApparatusExtension(),
    ComposedExtension(),
    MeasurementExtension(),
)


class _KeywordShim:
    """Registers annotation keywords without validating their arguments."""

    name: ClassVar[str] = "docs-examples-shim"
    version: ClassVar[str] = "0.1.0"

    def __init__(self, keywords: frozenset[str]) -> None:
        self._keywords = keywords

    @property
    def annotation_keywords(self) -> frozenset[str]:
        return self._keywords

    @property
    def annotation_types(self) -> Mapping[str, type]:
        return {}

    def validate(self, annotations: Sequence[Any]) -> list[str]:
        return []

    @property
    def requires(self) -> frozenset[str]:
        return frozenset()


def split_block(block: str) -> list[tuple[int, str]]:
    """Return (line offset in block, source) for each example in a block."""
    lines = block.splitlines()
    programs = any(line.startswith("phase ") for line in lines)
    examples: list[tuple[int, list[str]]] = []
    current: list[str] | None = None
    for offset, line in enumerate(lines):
        if line.startswith("--"):
            current = None
            continue
        if not line.strip():
            if not programs:
                current = None
            continue
        joins = line[0].isspace() or programs or (
            current is not None and current[-1].startswith("let ")
        )
        if current is None or not joins:
            current = []
            examples.append((offset, current))
        current.append(line)
    return [(offset, "\n".join(body)) for offset, body in examples]


def main() -> int:
    bundled = ExtensionRegistry.build(*BUNDLED)
    failures = 0
    needed: set[str] = set()
    for page in PAGES:
        text = (DSL_ROOT / page).read_text(encoding="utf-8")
        for match in BLOCK.finditer(text):
            first_line = text[: match.start(1)].count("\n") + 1
            for offset, source in split_block(match.group(1)):
                label = f"{page}:{first_line + offset}"
                try:
                    parse(source, extensions=bundled)
                except Exception as exc:  # noqa: BLE001 -- report and go on
                    keywords = set(UNKNOWN.findall(str(exc)))
                    if not keywords or not keywords <= KNOWN_UNREGISTERED.keys():
                        print(f"[fail] {label}: {exc}")
                        failures += 1
                        continue
                    # Re-parse until every known keyword the example uses is
                    # registered (the parser reports one at a time).
                    while True:
                        shim = _KeywordShim(frozenset(keywords))
                        try:
                            parse(
                                source,
                                extensions=ExtensionRegistry.build(*BUNDLED, shim),
                            )
                        except Exception as again:  # noqa: BLE001
                            more = set(UNKNOWN.findall(str(again))) - keywords
                            if more and more <= KNOWN_UNREGISTERED.keys():
                                keywords |= more
                                continue
                            print(f"[fail] {label}: {again}")
                            failures += 1
                        else:
                            needed |= keywords
                            names = ", ".join(f"@{k}" for k in sorted(keywords))
                            print(f"[known] {label}: {names} not registered")
                        break
                else:
                    print(f"[ok] {label}")
    for keyword in sorted(KNOWN_UNREGISTERED.keys() - needed):
        print(f"[stale] @{keyword} now parses; drop it from KNOWN_UNREGISTERED")
        failures += 1
    for keyword in sorted(needed):
        print(f"[note] @{keyword}: {KNOWN_UNREGISTERED[keyword]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
