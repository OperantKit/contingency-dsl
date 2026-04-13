#!/usr/bin/env python3
"""
EBNF → Tree-sitter grammar.js converter for contingency-dsl.

Reads schema/*/grammar.ebnf files and emits a Tree-sitter grammar.js
to dist/tree-sitter/grammar.js.

Usage:
    python scripts/ebnf2treesitter.py [--output dist/tree-sitter/grammar.js]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import indent

from ebnf_parser import (
    Alternation,
    CharClass,
    Expr,
    Grammar,
    Group,
    OptionalExpr,
    Reference,
    Repeat,
    Repeat1,
    Rule,
    Sequence,
    Terminal,
    collect_references,
    merge_grammars,
    parse_ebnf_file,
    rule_names,
)

# Rules that should be emitted as Tree-sitter `token(...)` (lexical rules)
# These are character-level rules that should not create child nodes.
LEXICAL_RULES = {
    'number', 'ident', 'ws', 'time_unit', 'time_sep',
    'string_literal', 'annotation_name',
}

# Rules to skip entirely (handled inline or as extras)
SKIP_RULES = {
    'reserved',  # documentation-only, not a parse rule
    'ws',        # handled by Tree-sitter extras
}

# Character class → regex mapping
CHARCLASS_MAP = {
    '[0-9]': r'[0-9]',
    '[a-z_]': r'[a-z_]',
    '[a-zA-Z0-9_]': r'[a-zA-Z0-9_]',
    '[^"]': r'[^"]',
}


def _escape_js_string(s: str) -> str:
    """Escape a string for JavaScript single-quoted literal."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def _is_single_char_literal(expr: Expr) -> bool:
    """Check if expression is a single-character terminal."""
    return isinstance(expr, Terminal) and len(expr.value) == 1


class TreeSitterEmitter:
    """Emit Tree-sitter grammar.js from parsed EBNF."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.defined = rule_names(grammar)
        self._inline_rules: set[str] = set()

    def emit(self) -> str:
        """Generate complete grammar.js content."""
        lines = [
            '// contingency-dsl — Tree-sitter Grammar',
            '// Auto-generated from schema/*/grammar.ebnf',
            '// Do not edit manually.',
            '//',
            '// Regenerate: ./scripts/gen-treesitter.sh',
            '',
            '/// <reference types="tree-sitter-cli/dsl" />',
            '// @ts-check',
            '',
            'module.exports = grammar({',
            "  name: 'contingency_dsl',",
            '',
            '  extras: $ => [',
            '    /\\s+/,',
            '    $.comment,',
            '  ],',
            '',
            '  word: $ => $.ident,',
            '',
            '  conflicts: $ => [',
            '    // LL(2) decision points documented in grammar.ebnf:',
            '    // annotation: "@" name optional("(" args ")") — "(" ambiguity',
            '    [$.annotation],',
            '    // atomic_or_second: parametric_atomic optional("(" unit ")") — second-order',
            '    [$.atomic_or_second],',
            '    // positional_args vs keyword_arg in compound arg_list',
            '    [$.positional_args],',
            '    // schedule: base_schedule optional(LH value) — LH ambiguity',
            '    [$.schedule],',
            '  ],',
            '',
            '  rules: {',
        ]

        for rule in self.grammar.rules:
            if rule.name in SKIP_RULES:
                continue
            rule_js = self._emit_rule(rule)
            lines.append('')
            lines.append(indent(rule_js, '    '))

        # Add synthetic rules not in EBNF but needed for a working parser

        # annotation_name: program-specific, not defined in EBNF.
        # Fallback: any identifier (upper or lowercase).
        if 'annotation_name' not in {r.name for r in self.grammar.rules}:
            lines.append('')
            lines.append("    // annotation_name is program-specific (not in EBNF).")
            lines.append("    // This fallback accepts any identifier-like token.")
            lines.append("    annotation_name: $ => token(/[a-zA-Z_][a-zA-Z0-9_]*/),")

        lines.append('')
        lines.append("    comment: $ => token(seq('--', /[^\\n]*/)),")

        lines.append('  },')
        lines.append('});')
        lines.append('')

        return '\n'.join(lines)

    def _emit_rule(self, rule: Rule) -> str:
        """Emit a single rule definition."""
        name = self._ts_name(rule.name)
        body = self._emit_expr(rule.expr)

        if rule.name in LEXICAL_RULES:
            return f"{name}: $ => token({body}),"
        else:
            return f"{name}: $ => {body},"

    def _emit_expr(self, expr: Expr, in_token: bool = False) -> str:
        """Recursively emit a Tree-sitter expression."""
        if isinstance(expr, Terminal):
            return f"'{_escape_js_string(expr.value)}'"

        elif isinstance(expr, CharClass):
            # Escape forward slashes in regex for JS
            pattern = expr.pattern.replace('/', '\\/')
            return f'/{pattern}/'

        elif isinstance(expr, Reference):
            if expr.name in SKIP_RULES:
                # ws → handled by extras, skip
                return None
            if expr.name in LEXICAL_RULES and expr.name != 'ws':
                return f'$.{self._ts_name(expr.name)}'
            return f'$.{self._ts_name(expr.name)}'

        elif isinstance(expr, Sequence):
            parts = []
            for elem in expr.elements:
                emitted = self._emit_expr(elem, in_token)
                if emitted is not None:
                    parts.append(emitted)
            if len(parts) == 0:
                return "''"
            if len(parts) == 1:
                return parts[0]
            joined = ', '.join(parts)
            return f'seq({joined})'

        elif isinstance(expr, Alternation):
            alts = []
            for alt in expr.alternatives:
                emitted = self._emit_expr(alt, in_token)
                if emitted is not None:
                    alts.append(emitted)
            if len(alts) == 1:
                return alts[0]
            joined = ', '.join(alts)
            return f'choice({joined})'

        elif isinstance(expr, Repeat):
            inner = self._emit_expr(expr.expr, in_token)
            if inner is None:
                return None
            return f'repeat({inner})'

        elif isinstance(expr, Repeat1):
            inner = self._emit_expr(expr.expr, in_token)
            if inner is None:
                return None
            return f'repeat1({inner})'

        elif isinstance(expr, OptionalExpr):
            inner = self._emit_expr(expr.expr, in_token)
            if inner is None:
                return None
            return f'optional({inner})'

        elif isinstance(expr, Group):
            return self._emit_expr(expr.expr, in_token)

        return "''"

    def _ts_name(self, name: str) -> str:
        """Convert EBNF rule name to Tree-sitter rule name."""
        # Tree-sitter uses snake_case, which matches our EBNF convention
        return name


def _find_schema_dir() -> Path:
    """Find the schema directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    return repo_root / 'schema'


def _load_grammars(schema_dir: Path) -> Grammar:
    """Load and merge all EBNF grammar files."""
    grammars = []

    # Core grammar (always first)
    core = schema_dir / 'core' / 'grammar.ebnf'
    if core.exists():
        grammars.append(parse_ebnf_file(core))

    # Extensions (additive)
    for ext_dir in sorted(schema_dir.iterdir()):
        if ext_dir.is_dir() and ext_dir.name != 'core':
            ebnf = ext_dir / 'grammar.ebnf'
            if ebnf.exists():
                grammars.append(parse_ebnf_file(ebnf))

    if not grammars:
        print(f"ERROR: No grammar.ebnf files found in {schema_dir}",
              file=sys.stderr)
        sys.exit(1)

    return merge_grammars(grammars)


def main():
    parser = argparse.ArgumentParser(
        description='Convert contingency-dsl EBNF to Tree-sitter grammar.js'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output path (default: dist/tree-sitter/grammar.js)'
    )
    parser.add_argument(
        '--schema-dir',
        default=None,
        help='Path to schema/ directory (auto-detected by default)'
    )
    args = parser.parse_args()

    schema_dir = Path(args.schema_dir) if args.schema_dir else _find_schema_dir()
    grammar = _load_grammars(schema_dir)

    emitter = TreeSitterEmitter(grammar)
    output = emitter.emit()

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = schema_dir.parent / 'dist' / 'tree-sitter' / 'grammar.js'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding='utf-8')
    print(f"Generated: {out_path}")
    print(f"  Rules: {len(grammar.rules)}")
    print(f"  Source files: {len(set(r.comment for r in grammar.rules if r.comment))}")


if __name__ == '__main__':
    main()
