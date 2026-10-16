#!/usr/bin/env python3
"""
Execute every ```python block in README.md and README.ja.md.

The examples read files relative to the repository root (schema/, conformance/),
so each block runs with the repository root as the working directory. They
need the Python reference parser and a JSON Schema validator:

    pip install contingency-dsl-py jsonschema
    python scripts/check_readme_examples.py

Exit status:
  0  -- every block ran without raising.
  1  -- a README has no python block, or a block raised.
"""

from __future__ import annotations

import os
import re
import sys
import traceback
from pathlib import Path

DSL_ROOT = Path(__file__).resolve().parent.parent
READMES = ("README.md", "README.ja.md")
BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def main() -> int:
    os.chdir(DSL_ROOT)
    failures = 0
    for name in READMES:
        blocks = BLOCK.findall((DSL_ROOT / name).read_text(encoding="utf-8"))
        if not blocks:
            print(f"[fail] {name}: no python block")
            failures += 1
            continue
        for index, source in enumerate(blocks):
            label = f"{name}#{index}"
            try:
                exec(compile(source, label, "exec"), {"__name__": "__readme__"})
            except Exception:
                traceback.print_exc()
                print(f"[fail] {label}")
                failures += 1
            else:
                print(f"[ok] {label}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
