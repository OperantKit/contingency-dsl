#!/usr/bin/env python3
"""
EBNF → Langium grammar converter for contingency-dsl.

Reads schema/*/grammar.ebnf files and emits a Langium .langium grammar
to dist/langium/contingency-dsl.langium.

Usage:
    python scripts/ebnf2langium.py [--output dist/langium/contingency-dsl.langium]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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

# Rules that should become Langium `terminal` rules
# (character-level lexing, not parser rules)
TERMINAL_RULES = {
    'number', 'ident', 'ws', 'time_unit', 'time_sep',
    'string_literal',
}

# Rules to skip entirely in output
SKIP_RULES = {
    'reserved',  # documentation-only
    'ws',        # Langium handles whitespace automatically
}

# Rules whose name should be PascalCase in Langium (parser rules)
# Terminal rules stay UPPER_CASE by convention


def _to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase for Langium parser rules."""
    return ''.join(part.capitalize() for part in name.split('_'))


def _to_upper(name: str) -> str:
    """Convert to UPPER_CASE for Langium terminal rules."""
    return name.upper()


def _escape_langium_string(s: str) -> str:
    """Escape for Langium single-quoted string literal."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def _charclass_to_regex(pattern: str) -> str:
    """Convert EBNF character class to regex pattern."""
    # Pattern is like [a-z_] — already valid regex
    return pattern


class LangiumEmitter:
    """Emit Langium .langium grammar from parsed EBNF."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.defined = rule_names(grammar)
        self._property_counters: dict[str, int] = {}

    def emit(self) -> str:
        """Generate complete .langium content."""
        lines = [
            '// contingency-dsl — Langium Grammar',
            '// Auto-generated from schema/*/grammar.ebnf',
            '// Do not edit manually.',
            '//',
            '// Regenerate: ./scripts/gen-langium.sh',
            '',
            'grammar ContingencyDsl',
            '',
        ]

        # Separate parser rules and terminal rules
        parser_rules = []
        terminal_rules = []

        for rule in self.grammar.rules:
            if rule.name in SKIP_RULES:
                continue
            if rule.name in TERMINAL_RULES:
                terminal_rules.append(rule)
            else:
                parser_rules.append(rule)

        # Emit parser rules
        first = True
        for rule in parser_rules:
            if first:
                lines.append(self._emit_parser_rule(rule, entry=True))
                first = False
            else:
                lines.append(self._emit_parser_rule(rule))
            lines.append('')

        # Emit terminal rules
        if terminal_rules:
            lines.append('// === Terminal Rules ===')
            lines.append('')
            for rule in terminal_rules:
                lines.append(self._emit_terminal_rule(rule))
                lines.append('')

        # Synthetic rules not in EBNF

        # annotation_name: program-specific, not defined in EBNF
        defined_names = {r.name for r in self.grammar.rules}
        if 'annotation_name' not in defined_names:
            lines.append('// annotation_name is program-specific (not in EBNF).')
            lines.append('// This fallback accepts any identifier-like token.')
            lines.append('AnnotationName:')
            lines.append("    /[a-zA-Z_][a-zA-Z0-9_]*/;")
            lines.append('')

        # Hidden terminal for whitespace and comments
        lines.append('// === Hidden Terminals ===')
        lines.append('')
        lines.append("hidden terminal WS: /\\s+/;")
        lines.append("hidden terminal ML_COMMENT: /--[^\\n\\r]*/;")
        lines.append('')

        return '\n'.join(lines)

    def _emit_parser_rule(self, rule: Rule, entry: bool = False) -> str:
        """Emit a Langium parser rule."""
        name = _to_pascal(rule.name)
        body = self._emit_parser_expr(rule.expr, rule.name)
        prefix = 'entry ' if entry else ''
        return f'{prefix}{name}:\n    {body};'

    def _emit_terminal_rule(self, rule: Rule) -> str:
        """Emit a Langium terminal rule."""
        name = _to_upper(rule.name)
        body = self._emit_terminal_expr(rule.expr)
        return f'terminal {name}: {body};'

    def _emit_parser_expr(self, expr: Expr, context: str = '') -> str:
        """Emit a Langium parser-level expression."""
        if isinstance(expr, Terminal):
            return f"'{_escape_langium_string(expr.value)}'"

        elif isinstance(expr, CharClass):
            # In parser rules, character classes should reference terminals
            return f'/{_charclass_to_regex(expr.pattern)}/'

        elif isinstance(expr, Reference):
            if expr.name in SKIP_RULES:
                return None
            if expr.name in TERMINAL_RULES:
                return _to_upper(expr.name)
            return _to_pascal(expr.name)

        elif isinstance(expr, Sequence):
            parts = []
            for elem in expr.elements:
                emitted = self._emit_parser_expr(elem, context)
                if emitted is not None:
                    parts.append(emitted)
            if not parts:
                return "''"
            return ' '.join(parts)

        elif isinstance(expr, Alternation):
            alts = []
            for alt in expr.alternatives:
                emitted = self._emit_parser_expr(alt, context)
                if emitted is not None:
                    alts.append(emitted)
            if len(alts) == 1:
                return alts[0]
            return ' | '.join(alts)

        elif isinstance(expr, Repeat):
            inner = self._emit_parser_expr(expr.expr, context)
            if inner is None:
                return None
            if ' | ' in inner or ' ' in inner:
                return f'({inner})*'
            return f'{inner}*'

        elif isinstance(expr, Repeat1):
            inner = self._emit_parser_expr(expr.expr, context)
            if inner is None:
                return None
            if ' | ' in inner or ' ' in inner:
                return f'({inner})+'
            return f'{inner}+'

        elif isinstance(expr, OptionalExpr):
            inner = self._emit_parser_expr(expr.expr, context)
            if inner is None:
                return None
            if ' | ' in inner or ' ' in inner:
                return f'({inner})?'
            return f'{inner}?'

        elif isinstance(expr, Group):
            inner = self._emit_parser_expr(expr.expr, context)
            if inner is None:
                return None
            return f'({inner})'

        return "''"

    def _emit_terminal_expr(self, expr: Expr) -> str:
        """Emit a Langium terminal-level expression (regex-based)."""
        if isinstance(expr, Terminal):
            return f"'{_escape_langium_string(expr.value)}'"

        elif isinstance(expr, CharClass):
            return f'/{_charclass_to_regex(expr.pattern)}/'

        elif isinstance(expr, Reference):
            # In terminal context, inline the reference if possible
            # For simplicity, emit as a fragment reference
            return _to_upper(expr.name)

        elif isinstance(expr, Sequence):
            parts = []
            for elem in expr.elements:
                parts.append(self._emit_terminal_expr(elem))
            return ' '.join(parts)

        elif isinstance(expr, Alternation):
            alts = [self._emit_terminal_expr(a) for a in expr.alternatives]
            return ' | '.join(alts)

        elif isinstance(expr, Repeat):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})*'
            return f'{inner}*'

        elif isinstance(expr, Repeat1):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})+'
            return f'{inner}+'

        elif isinstance(expr, OptionalExpr):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})?'
            return f'{inner}?'

        elif isinstance(expr, Group):
            inner = self._emit_terminal_expr(expr.expr)
            return f'({inner})'

        return "''"


def _find_schema_dir() -> Path:
    """Find the schema directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    return repo_root / 'schema'


def _load_grammars(schema_dir: Path) -> Grammar:
    """Load and merge all EBNF grammar files."""
    grammars = []

    core = schema_dir / 'core' / 'grammar.ebnf'
    if core.exists():
        grammars.append(parse_ebnf_file(core))

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
        description='Convert contingency-dsl EBNF to Langium grammar'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output path (default: dist/langium/contingency-dsl.langium)'
    )
    parser.add_argument(
        '--schema-dir',
        default=None,
        help='Path to schema/ directory (auto-detected by default)'
    )
    args = parser.parse_args()

    schema_dir = Path(args.schema_dir) if args.schema_dir else _find_schema_dir()
    grammar = _load_grammars(schema_dir)

    emitter = LangiumEmitter(grammar)
    output = emitter.emit()

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = schema_dir.parent / 'dist' / 'langium' / 'contingency-dsl.langium'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding='utf-8')
    print(f"Generated: {out_path}")
    print(f"  Rules: {len(grammar.rules)}")


if __name__ == '__main__':
    main()
