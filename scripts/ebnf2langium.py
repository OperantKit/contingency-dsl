#!/usr/bin/env python3
"""
EBNF → Langium v4 grammar converter for contingency-dsl.

Reads schema/*/grammar.ebnf files and emits a Langium .langium grammar
to dist/langium/contingency-dsl.langium.

Usage:
    python scripts/ebnf2langium.py [--output dist/langium/contingency-dsl.langium]

Langium v4 requirements handled:
  - Data type rules (pure keyword choices) → `returns string`
  - Parser rules → property assignments (`prop=Rule`, `prop+=Rule`)
  - Repeated elements → `+=` operator
  - Terminal rules → proper regex syntax
  - UpperIdent / AnnotationName → promoted to terminal rules
  - TIME_SEP → stripped of hidden WS reference
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
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
TERMINAL_RULES = {
    'number', 'ident', 'ws', 'time_unit', 'time_sep',
    'string_literal',
}

# Rules to promote from parser to terminal (contain regex patterns)
PROMOTE_TO_TERMINAL = {'upper_ident', 'annotation_name'}

# Rules to skip entirely in output
SKIP_RULES = {
    'reserved',  # documentation-only
    'ws',        # Langium handles whitespace via hidden terminal
}


def _to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase for Langium parser rules."""
    return ''.join(part.capitalize() for part in name.split('_'))


def _to_camel(name: str) -> str:
    """Convert snake_case to camelCase for property names."""
    parts = name.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def _to_upper(name: str) -> str:
    """Convert to UPPER_CASE for Langium terminal rules."""
    return name.upper()


def _escape_langium_string(s: str) -> str:
    """Escape for Langium single-quoted string literal."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


class LangiumEmitter:
    """Emit Langium v4 .langium grammar from parsed EBNF."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.defined = rule_names(grammar)
        self._rules_by_name = {r.name: r for r in grammar.rules}
        # Classify rules
        self._data_type_rules: set[str] = set()
        self._classify_rules()
        # Per-rule property counter (reset per rule)
        self._prop_counter: Counter = Counter()

    # ------------------------------------------------------------------
    # Rule classification
    # ------------------------------------------------------------------

    def _classify_rules(self) -> None:
        """Identify data type rules (pure keyword/terminal alternations)."""
        for rule in self.grammar.rules:
            if rule.name in SKIP_RULES or rule.name in TERMINAL_RULES:
                continue
            if rule.name in PROMOTE_TO_TERMINAL:
                continue
            if self._is_data_type_expr(rule.expr):
                self._data_type_rules.add(rule.name)

    def _is_data_type_expr(self, expr: Expr) -> bool:
        """Conservative check: expression is only literal alternatives
        and/or single terminal-rule references (no parser-rule refs)."""
        if isinstance(expr, Terminal):
            return True
        if isinstance(expr, Reference):
            return expr.name in TERMINAL_RULES or expr.name in PROMOTE_TO_TERMINAL
        if isinstance(expr, Alternation):
            return all(self._is_data_type_expr(a) for a in expr.alternatives)
        if isinstance(expr, Group):
            return self._is_data_type_expr(expr.expr)
        # Sequences of terminals/terminal-refs also qualify
        # (e.g., 'relative' '-' 'range' as a compound keyword)
        if isinstance(expr, Sequence):
            return all(self._is_data_type_expr(e) for e in expr.elements)
        return False

    # ------------------------------------------------------------------
    # Top-level emit
    # ------------------------------------------------------------------

    def emit(self) -> str:
        """Generate complete .langium content."""
        lines = [
            '// contingency-dsl — Langium Grammar (v4)',
            '// Auto-generated from schema/*/grammar.ebnf',
            '// Do not edit manually.',
            '//',
            '// Regenerate: ./scripts/gen-langium.sh',
            '',
            'grammar ContingencyDsl',
            '',
        ]

        parser_rules: list[Rule] = []
        terminal_rules: list[Rule] = []

        for rule in self.grammar.rules:
            if rule.name in SKIP_RULES:
                continue
            if rule.name in TERMINAL_RULES or rule.name in PROMOTE_TO_TERMINAL:
                terminal_rules.append(rule)
            else:
                parser_rules.append(rule)

        # --- Parser rules ---
        # Determine entry point: 'file' if it exists, else first parser rule.
        entry_rule_name = 'file' if 'file' in self.defined else None
        entry_assigned = entry_rule_name is not None
        for rule in parser_rules:
            if rule.name in self._data_type_rules:
                lines.append(self._emit_data_type_rule(rule))
            else:
                is_entry = (rule.name == entry_rule_name
                            or (not entry_assigned))
                lines.append(self._emit_parser_rule(rule, entry=is_entry))
                if is_entry:
                    entry_assigned = True
            lines.append('')

        # --- Terminal rules ---
        lines.append('// === Terminal Rules ===')
        lines.append('')
        for rule in terminal_rules:
            lines.append(self._emit_terminal_rule(rule))
            lines.append('')

        # --- Synthetic terminal for annotation_name (if not in EBNF) ---
        defined_names = {r.name for r in self.grammar.rules}
        if 'annotation_name' not in defined_names:
            lines.append(
                '// annotation_name: program-specific, not in EBNF.\n'
                'terminal ANNOTATION_NAME: /[a-zA-Z_][a-zA-Z0-9_]*/;'
            )
            lines.append('')

        # --- Hidden terminals ---
        lines.append('// === Hidden Terminals ===')
        lines.append('')
        lines.append("hidden terminal WS: /\\s+/;")
        lines.append("hidden terminal ML_COMMENT: /--[^\\n\\r]*/;")
        lines.append('')

        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # Data type rules: `RuleName returns string: ...;`
    # ------------------------------------------------------------------

    def _emit_data_type_rule(self, rule: Rule) -> str:
        name = _to_pascal(rule.name)
        body = self._emit_plain_expr(rule.expr)
        return f'{name} returns string:\n    {body};'

    def _emit_plain_expr(self, expr: Expr) -> str:
        """Emit expression without property assignments (for data type rules)."""
        if isinstance(expr, Terminal):
            return f"'{_escape_langium_string(expr.value)}'"

        if isinstance(expr, Reference):
            if expr.name in SKIP_RULES:
                return ''
            if expr.name in TERMINAL_RULES or expr.name in PROMOTE_TO_TERMINAL:
                return _to_upper(expr.name)
            return _to_pascal(expr.name)

        if isinstance(expr, Sequence):
            parts = [self._emit_plain_expr(e) for e in expr.elements]
            parts = [p for p in parts if p]
            return ' '.join(parts) if parts else "''"

        if isinstance(expr, Alternation):
            alts = [self._emit_plain_expr(a) for a in expr.alternatives]
            alts = [a for a in alts if a]
            return ' | '.join(alts) if len(alts) > 1 else (alts[0] if alts else "''")

        if isinstance(expr, Group):
            inner = self._emit_plain_expr(expr.expr)
            return f'({inner})'

        if isinstance(expr, OptionalExpr):
            inner = self._emit_plain_expr(expr.expr)
            if ' | ' in inner or ' ' in inner:
                return f'({inner})?'
            return f'{inner}?'

        if isinstance(expr, Repeat):
            inner = self._emit_plain_expr(expr.expr)
            if ' | ' in inner or ' ' in inner:
                return f'({inner})*'
            return f'{inner}*'

        if isinstance(expr, Repeat1):
            inner = self._emit_plain_expr(expr.expr)
            if ' | ' in inner or ' ' in inner:
                return f'({inner})+'
            return f'{inner}+'

        if isinstance(expr, CharClass):
            return f'/{expr.pattern}/'

        return "''"

    # ------------------------------------------------------------------
    # Parser rules with property assignments
    # ------------------------------------------------------------------

    def _emit_parser_rule(self, rule: Rule, entry: bool = False) -> str:
        name = _to_pascal(rule.name)
        self._prop_counter = Counter()
        body = self._emit_assigned(rule.expr, in_repeat=False)
        prefix = 'entry ' if entry else ''
        return f'{prefix}{name}:\n    {body};'

    def _get_prop_name(self, base: str) -> str:
        """Get unique property name, appending index if duplicated."""
        count = self._prop_counter[base]
        self._prop_counter[base] = count + 1
        if count == 0:
            return base
        return f'{base}{count + 1}'

    def _emit_assigned(self, expr: Expr, in_repeat: bool = False) -> str:
        """Emit parser expression with property assignments for References."""
        if isinstance(expr, Terminal):
            return f"'{_escape_langium_string(expr.value)}'"

        if isinstance(expr, CharClass):
            return f'/{expr.pattern}/'

        if isinstance(expr, Reference):
            ref_name = expr.name
            if ref_name in SKIP_RULES:
                return ''

            is_terminal = (ref_name in TERMINAL_RULES
                           or ref_name in PROMOTE_TO_TERMINAL)
            is_data_type = ref_name in self._data_type_rules

            langium_name = (_to_upper(ref_name) if is_terminal
                           else _to_pascal(ref_name))

            # Property assignment
            prop_base = _to_camel(ref_name)
            prop = self._get_prop_name(prop_base)
            op = '+=' if in_repeat else '='

            return f'{prop}{op}{langium_name}'

        if isinstance(expr, Sequence):
            parts = []
            for elem in expr.elements:
                e = self._emit_assigned(elem, in_repeat=in_repeat)
                if e:
                    parts.append(e)
            return ' '.join(parts) if parts else "''"

        if isinstance(expr, Alternation):
            alts = []
            for alt in expr.alternatives:
                e = self._emit_assigned(alt, in_repeat=in_repeat)
                if e:
                    alts.append(e)
            if len(alts) == 1:
                return alts[0]
            return ' | '.join(alts)

        if isinstance(expr, Repeat):
            inner = self._emit_assigned(expr.expr, in_repeat=True)
            if not inner:
                return ''
            if ' | ' in inner or ' ' in inner:
                return f'({inner})*'
            return f'{inner}*'

        if isinstance(expr, Repeat1):
            inner = self._emit_assigned(expr.expr, in_repeat=True)
            if not inner:
                return ''
            if ' | ' in inner or ' ' in inner:
                return f'({inner})+'
            return f'{inner}+'

        if isinstance(expr, OptionalExpr):
            inner = self._emit_assigned(expr.expr, in_repeat=in_repeat)
            if not inner:
                return ''
            if ' | ' in inner or ' ' in inner:
                return f'({inner})?'
            return f'{inner}?'

        if isinstance(expr, Group):
            inner = self._emit_assigned(expr.expr, in_repeat=in_repeat)
            if not inner:
                return ''
            return f'({inner})'

        return "''"

    # ------------------------------------------------------------------
    # Terminal rules
    # ------------------------------------------------------------------

    def _emit_terminal_rule(self, rule: Rule) -> str:
        """Emit a Langium terminal rule with proper regex."""
        name = _to_upper(rule.name)

        # --- Special-case terminals ---

        if rule.name == 'time_sep':
            # Original references hidden WS — just match hyphen;
            # Langium hidden WS handles whitespace automatically.
            return "terminal TIME_SEP: '-';"

        if rule.name == 'number':
            return r"terminal NUMBER: /[0-9]+(\.[0-9]+)?/;"

        if rule.name == 'ident':
            return r"terminal IDENT: /[a-z_][a-zA-Z0-9_]*/;"

        if rule.name == 'string_literal':
            return r'terminal STRING_LITERAL: /"[^"]*"/;'

        if rule.name == 'time_unit':
            # Use alternation of keywords; order longest-first for
            # correct longest-match behaviour.
            return "terminal TIME_UNIT: /sec|min|ms|s/;"

        if rule.name == 'upper_ident':
            return r"terminal UPPER_IDENT: /[A-Z][a-zA-Z0-9_]*/;"

        if rule.name == 'annotation_name':
            return r"terminal ANNOTATION_NAME: /[a-zA-Z_][a-zA-Z0-9_]*/;"

        if rule.name == 'ws':
            # Handled as hidden terminal in main emit; skip here
            return f"// (ws handled as hidden terminal)"

        # --- Generic fallback ---
        body = self._emit_terminal_expr(rule.expr)
        return f'terminal {name}: {body};'

    def _emit_terminal_expr(self, expr: Expr) -> str:
        """Emit a Langium terminal-level expression (regex-based)."""
        if isinstance(expr, Terminal):
            return f"'{_escape_langium_string(expr.value)}'"

        if isinstance(expr, CharClass):
            return f'/{expr.pattern}/'

        if isinstance(expr, Reference):
            return _to_upper(expr.name)

        if isinstance(expr, Sequence):
            parts = [self._emit_terminal_expr(e) for e in expr.elements]
            return ' '.join(parts)

        if isinstance(expr, Alternation):
            alts = [self._emit_terminal_expr(a) for a in expr.alternatives]
            return ' | '.join(alts)

        if isinstance(expr, Repeat):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})*'
            return f'{inner}*'

        if isinstance(expr, Repeat1):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})+'
            return f'{inner}+'

        if isinstance(expr, OptionalExpr):
            inner = self._emit_terminal_expr(expr.expr)
            if ' ' in inner or '|' in inner:
                return f'({inner})?'
            return f'{inner}?'

        if isinstance(expr, Group):
            inner = self._emit_terminal_expr(expr.expr)
            return f'({inner})'

        return "''"


# =====================================================================
# CLI / loader (unchanged from original)
# =====================================================================

def _find_schema_dir() -> Path:
    """Find the schema directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    return repo_root / 'schema'


_LOAD_ORDER = (
    'foundations',
    'operant',
    'operant/stateful',
    'operant/trial-based',
    'respondent',
)


def _load_grammars(schema_dir: Path) -> Grammar:
    """Load and merge all EBNF grammar files under layout.

    Foundations is loaded first (paradigm-neutral lexical rules), then
    Operant (three-term contingency), then Operant.Stateful,
    Operant.TrialBased, and Respondent. Any additional grammar.ebnf
    files encountered elsewhere are appended in sorted order so new
    extension layers can be added without editing this script.
    """
    grammars: list[Grammar] = []
    loaded: set[Path] = set()

    for rel in _LOAD_ORDER:
        ebnf = schema_dir / rel / 'grammar.ebnf'
        if ebnf.exists():
            grammars.append(parse_ebnf_file(ebnf))
            loaded.add(ebnf.resolve())

    for ebnf in sorted(schema_dir.rglob('grammar.ebnf')):
        if ebnf.resolve() in loaded:
            continue
        grammars.append(parse_ebnf_file(ebnf))

    if not grammars:
        print(f"ERROR: No grammar.ebnf files found in {schema_dir}",
              file=sys.stderr)
        sys.exit(1)

    return merge_grammars(grammars)


def main():
    parser = argparse.ArgumentParser(
        description='Convert contingency-dsl EBNF to Langium v4 grammar'
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
