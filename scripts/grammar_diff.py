#!/usr/bin/env python3
"""
Differential test of the EBNF grammar against the Python reference parser.

The script builds a second parser from schema/**/grammar.ebnf on every run
(Lark, Earley) and feeds the same inputs to it and to the reference parser
(contingency-dsl-py). It compares only acceptance: does each parser accept or
reject the input. ASTs are not compared; for inputs both parsers accept, the
script prints which top-level grammar rule maps to which reference AST class.

Rules the generator adds that the EBNF files do not spell out as productions
(each one is listed here and in the output; anything else that turns out to
be needed is a finding about the grammar, not something to patch here):

  1. Reading order and duplicates. schema/foundations is read first, the rest
     in path order. A rule defined twice with the same expression is kept
     once. A rule defined twice with different expressions takes the later
     definition and is reported as a grammar conflict. Exception: respondent's
     `arg_list` (and the references to it inside the respondent grammar) is
     renamed `respondent__arg_list`. Integration points written in a grammar
     as a comment `;   rule ::= ... | ext_rule` add `ext_rule` as an
     alternative of `rule`.
  2. Start symbol: `file`.
  3. Whitespace and comments. Spaces, tabs, newlines and `--` to end of line
     are skipped between tokens. `ws` is "one or more spaces". Indentation
     carries no meaning: no production of the experiment layer refers to
     indentation or line breaks.
  4. Lexical rules. A rule whose expression contains a character class
     (number, ident, upper_ident, digit_ident, string_literal, ...) becomes a
     single regular-expression token; so does a rule that only refers to one
     such rule (ident_upper, annotation_name). Quoted literals carry no word
     boundary: the grammar builds keywords from adjacent letters (`dist`
     "F" followed by `domain` "R" gives `FR`).
  5. Reserved words. The words listed (directly or through references) by the
     documentation rule `reserved` are excluded from `ident`.
  6. Undefined references become a token that never matches, and are
     reported.

Inputs:
  conformance   every string `input` in conformance/**/*.json (except
                representations/), plus `lhs` / `rhs` of algebra equations.
  syntax-examples
                the examples in docs/{en,ja}/syntax-examples.md, split the
                same way as scripts/check_docs_examples.py.
  code-blocks   every fenced code block in spec/, docs/ (other pages) and
                README*.md, one block per input. Blocks neither parser accepts
                are counted, not listed.

Usage:
    python -m pip install lark git+https://github.com/OperantKit/contingency-dsl-py
    python scripts/grammar_diff.py                 # tables and mismatches
    python scripts/grammar_diff.py --dump-lark     # print the generated grammar
    python scripts/grammar_diff.py --json rows.json
    python scripts/grammar_diff.py --extra "rs=contingency-dsl-rs check -"
        (an extra parser: one input on stdin, exit status 0 = accept)

Exit status: 0 when the comparison ran (mismatches are reported, not fatal);
2 when the grammar could not be built.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import re
import shlex
import signal
import subprocess
import sys
import time
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, ClassVar

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ebnf_parser as E  # noqa: E402
from check_docs_examples import BUNDLED, PAGES, split_block  # noqa: E402
from lark import Lark  # noqa: E402
from lark.exceptions import LarkError  # noqa: E402

from contingency_dsl import parse  # noqa: E402
from contingency_dsl.errors import LexError, ParseError  # noqa: E402
from contingency_dsl.extensions import ExtensionRegistry  # noqa: E402

DSL_ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_S = 5
RESP_ARG_LIST = "respondent__arg_list"
INTEGRATION = re.compile(r"^;\s*(\w+)\s*::=\s*\.\.\.\s*\|\s*(\w+)\s*$", re.MULTILINE)
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)

# Annotation keywords the conformance runner of the reference parser accepts
# without a bundled extension (its catch-all shim). Kept in step with that
# runner so that both judge annotations the same way.
CATCH_ALL_KEYWORDS = frozenset({
    "reinforcer", "sd", "operandum", "brief", "punisher", "consequentStimulus",
    "stimulus_classes", "training", "testing", "s_delta", "subject",
    "interlocking", "session_end", "baseline", "steady_state",
    "dependent_measure", "training_volume", "microstructure", "phase_end",
    "logging", "iri_window", "warmup_exclude", "species", "strain",
    "deprivation", "history", "n", "subjects", "chamber", "interface",
    "hardware", "hw", "apparatus", "clock", "warmup", "algorithm", "context",
    "cs", "us", "iti", "cs_interval", "omission", "avoidance", "session",
    "trial_mix", "probe_policy",
})


class _CatchAll:
    name: ClassVar[str] = "grammar-diff-catchall"
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


def registry() -> ExtensionRegistry:
    owned = frozenset().union(*(ext.annotation_keywords for ext in BUNDLED))
    return ExtensionRegistry.build(*BUNDLED, _CatchAll(CATCH_ALL_KEYWORDS - owned))


# === Grammar assembly (rules 1, 5, 6) ===


@dataclasses.dataclass
class Assembly:
    rules: dict[str, E.Expr]
    conflicts: list[tuple[str, str, str, str, str]]  # name, file a, expr a, file b, expr b
    renamed: list[str]
    integrations: list[tuple[str, str, str]]  # rule, added alternative, file
    undefined: set[str]
    reserved: set[str]


def _rename(expr: E.Expr, old: str, new: str) -> E.Expr:
    if isinstance(expr, E.Reference):
        return E.Reference(new) if expr.name == old else expr
    if isinstance(expr, (E.Sequence,)):
        return E.Sequence([_rename(x, old, new) for x in expr.elements])
    if isinstance(expr, E.Alternation):
        return E.Alternation([_rename(x, old, new) for x in expr.alternatives])
    if isinstance(expr, (E.Repeat, E.Repeat1, E.OptionalExpr, E.Group)):
        return type(expr)(_rename(expr.expr, old, new))
    return expr


def _show(expr: E.Expr) -> str:
    return emit(expr, {}, set())


def grammar_files() -> list[Path]:
    rest = sorted(p for p in (DSL_ROOT / "schema").rglob("grammar.ebnf")
                  if p.parent.name != "foundations")
    return [DSL_ROOT / "schema/foundations/grammar.ebnf", *rest]


def assemble() -> Assembly:
    rules: dict[str, E.Expr] = {}
    origin: dict[str, str] = {}
    conflicts, renamed, integrations = [], [], []
    for path in grammar_files():
        rel = path.relative_to(DSL_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        respondent = path.parent.name == "respondent"
        for rule in E.parse_ebnf(text, rel).rules:
            name, expr = rule.name, rule.expr
            if respondent:
                expr = _rename(expr, "arg_list", RESP_ARG_LIST)
                if name == "arg_list":
                    name = RESP_ARG_LIST
                    renamed.append(f"{rel}: arg_list -> {RESP_ARG_LIST}")
            if name in rules and rules[name] != expr:
                conflicts.append((name, origin[name], _show(rules[name]), rel, _show(expr)))
            rules[name] = expr
            origin[name] = rel
        for target, alt in INTEGRATION.findall(text):
            integrations.append((target, alt, rel))
    for target, alt, _ in integrations:
        base = rules[target]
        alts = base.alternatives if isinstance(base, E.Alternation) else [base]
        rules[target] = E.Alternation([*alts, E.Reference(alt)])
    referenced = set().union(*(E.collect_references(x) for x in rules.values()))
    return Assembly(rules, conflicts, renamed, integrations,
                    referenced - rules.keys(), _words(rules, "reserved", set()))


def _words(rules: dict[str, E.Expr], name: str, seen: set[str]) -> set[str]:
    if name in seen or name not in rules:
        return set()
    seen.add(name)
    found = set(E.collect_terminals(rules[name]))
    for ref in E.collect_references(rules[name]):
        found |= _words(rules, ref, seen)
    return found


# === Lark emission (rules 2, 3, 4, 6) ===


def charclasses(expr: E.Expr) -> list[str]:
    if isinstance(expr, E.CharClass):
        return [expr.pattern]
    if isinstance(expr, E.Sequence):
        return [p for x in expr.elements for p in charclasses(x)]
    if isinstance(expr, E.Alternation):
        return [p for x in expr.alternatives for p in charclasses(x)]
    if isinstance(expr, (E.Repeat, E.Repeat1, E.OptionalExpr, E.Group)):
        return charclasses(expr.expr)
    return []


def lexical_rules(rules: dict[str, E.Expr]) -> set[str]:
    """Rules with a character class (or a bare reference) whose references
    are all lexical themselves."""
    candidates = {n for n, x in rules.items()
                  if n != "reserved" and (charclasses(x) or isinstance(x, E.Reference))}
    lex: set[str] = set()
    changed = True
    while changed:
        changed = False
        for n in sorted(candidates - lex):
            if E.collect_references(rules[n]) <= lex:
                lex.add(n)
                changed = True
    return lex


def odd_charclasses(rules: dict[str, E.Expr]) -> list[tuple[str, str]]:
    """Brackets that hold quoted literals: written as an optional, read as a
    character class by the project's EBNF notation."""
    return [(n, p) for n, x in rules.items() for p in charclasses(x)
            if '"' in p and n != "string_literal"]


def _charclass(pattern: str) -> str:
    return pattern if pattern.startswith("[") else "[" + pattern + "]"


def regex_of(expr: E.Expr, rules: dict[str, E.Expr]) -> str:
    if isinstance(expr, E.Terminal):
        return re.escape(expr.value)
    if isinstance(expr, E.CharClass):
        return _charclass(expr.pattern)
    if isinstance(expr, E.Reference):
        return "(?:" + regex_of(rules[expr.name], rules) + ")"
    if isinstance(expr, E.Sequence):
        return "".join(regex_of(x, rules) for x in expr.elements)
    if isinstance(expr, E.Alternation):
        return "(?:" + "|".join(regex_of(x, rules) for x in expr.alternatives) + ")"
    suffix = {E.Repeat: "*", E.Repeat1: "+", E.OptionalExpr: "?", E.Group: ""}
    return "(?:" + regex_of(expr.expr, rules) + ")" + suffix[type(expr)]


def _lit(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit(expr: E.Expr, lex: Mapping[str, str], defined: set[str]) -> str:
    if isinstance(expr, E.Terminal):
        return _lit(expr.value)
    if isinstance(expr, E.CharClass):
        return "/" + _charclass(expr.pattern) + "/"
    if isinstance(expr, E.Reference):
        if expr.name == "ws":
            return "WS_REQ"
        if expr.name in lex:
            return lex[expr.name]
        if defined and expr.name not in defined:
            return "UNDEFINED_" + expr.name.upper()
        return expr.name
    if isinstance(expr, E.Sequence):
        return " ".join(emit(x, lex, defined) for x in expr.elements)
    if isinstance(expr, E.Alternation):
        return "(" + " | ".join(emit(x, lex, defined) for x in expr.alternatives) + ")"
    suffix = {E.Repeat: "*", E.Repeat1: "+", E.OptionalExpr: "?", E.Group: ""}
    return "(" + emit(expr.expr, lex, defined) + ")" + suffix[type(expr)]


def lark_text(asm: Assembly) -> str:
    rules = asm.rules
    lex_names = lexical_rules(rules)
    lex = {n: "T_" + n.upper() for n in lex_names}
    out = []
    for name, expr in rules.items():
        if name in {"reserved", "ws"}:
            continue
        if name in lex_names:
            pattern = regex_of(expr, rules)
            if name == "ident":
                words = sorted(w for w in asm.reserved if re.fullmatch(pattern, w))
                guard = "|".join(re.escape(w) for w in words)
                pattern = f"(?!(?:{guard})(?![A-Za-z0-9_])){pattern}"
            out.append(f"{lex[name]}: /{pattern.replace('/', chr(92) + '/')}/")
        else:
            out.append(f"{name}: {emit(expr, lex, set(rules))}")
    for name in sorted(asm.undefined):
        out.append(f'UNDEFINED_{name.upper()}: "\\x00undefined_{name}"')
    out.append("WS_REQ: / +/")
    out.append(r"%ignore /[ \t\r\n]+/")
    out.append(r"%ignore /--[^\n]*/")
    return "\n".join(out) + "\n"


# === Corpus ===


@dataclasses.dataclass(frozen=True)
class Case:
    corpus: str
    where: str
    source: str
    expect: str  # accept | reject | semantic | none


def _expectation(case: Mapping[str, Any]) -> str:
    err = case.get("expected_error") or case.get("error") or case.get("errors")
    if err is None:
        return "accept"
    kinds = {e.get("type") for e in (err if isinstance(err, list) else [err])
             if isinstance(e, Mapping)}
    if kinds & {"ParseError", "LexError"}:
        return "reject"
    if "SemanticError" in kinds:
        return "semantic"
    return "none"


def conformance_cases() -> Iterator[Case]:
    root = DSL_ROOT / "conformance"
    for path in sorted(root.rglob("*.json")):
        rel = path.relative_to(DSL_ROOT).as_posix()
        if "representations" in path.relative_to(root).parts:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for case in data if isinstance(data, list) else []:
            if not isinstance(case, Mapping):
                continue
            where = f"{rel}#{case.get('id')}"
            if isinstance(case.get("input"), str):
                yield Case("conformance", where, case["input"], _expectation(case))
            for side in ("lhs", "rhs"):
                if isinstance(case.get(side), str):
                    yield Case("conformance", f"{where}.{side}", case[side], "accept")


def syntax_example_cases() -> Iterator[Case]:
    for page in PAGES:
        text = (DSL_ROOT / page).read_text(encoding="utf-8")
        for match in re.finditer(r"^```\n(.*?)^```", text, re.DOTALL | re.MULTILINE):
            first = text[: match.start(1)].count("\n") + 1
            for offset, source in split_block(match.group(1)):
                yield Case("syntax-examples", f"{page}:{first + offset}", source, "accept")


def code_block_cases() -> Iterator[Case]:
    pages = sorted({*DSL_ROOT.glob("spec/**/*.md"), *DSL_ROOT.glob("docs/**/*.md"),
                    *DSL_ROOT.glob("README*.md")} - {DSL_ROOT / p for p in PAGES})
    for path in pages:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(DSL_ROOT).as_posix()
        for match in FENCE.finditer(text):
            line = text[: match.start(1)].count("\n") + 1
            yield Case("code-blocks", f"{rel}:{line}", match.group(1).rstrip("\n"), "none")


# === Judging ===


class _Timeout(Exception):
    pass


def _alarm(*_: object) -> None:
    raise _Timeout()


def _where_stopped(source: str, exc: LarkError) -> str:
    line = getattr(exc, "line", 0) or 0
    col = getattr(exc, "column", 0) or 0
    if line < 1:
        return "<end of input>"
    text = source.splitlines()[line - 1][col - 1:]
    return text[:14] or "<end of line>"


def judge_generated(parser: Lark, source: str) -> tuple[str, str | None, str | None]:
    """(verdict, root rule when accepted, text where it stopped when rejected)."""
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TIMEOUT_S)
    try:
        tree = parser.parse(source)
    except LarkError as exc:
        return "reject", None, _where_stopped(source, exc)
    except _Timeout:
        return "timeout", None, None
    finally:
        signal.alarm(0)
    child = tree.children[0] if tree.children else None
    return "accept", getattr(child, "data", None), None


def judge_reference(source: str, ext: ExtensionRegistry) -> tuple[str, str | None, str | None]:
    """(verdict, AST class or exception name when accepted, message when rejected)."""
    try:
        program = parse(source, extensions=ext)
    except (ParseError, LexError) as exc:
        return "reject", None, f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001 -- SemanticError and others accept syntax
        return "accept", type(exc).__name__, None
    return "accept", type(program).__name__, None


def judge_extra(command: str, source: str) -> str:
    try:
        done = subprocess.run(shlex.split(command), input=source, text=True,
                              capture_output=True, timeout=TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired:
        return "timeout"
    return "accept" if done.returncode == 0 else "reject"


def mismatch(row: Mapping[str, Any]) -> bool:
    ref, gen, exp = row["ref"], row["gen"], row["expect"]
    if gen == "timeout":
        return False
    if exp == "semantic":
        return gen != "accept"
    if exp in {"accept", "reject"}:
        return ref != exp or gen != exp
    return ref != gen


# === Report ===


def _short(source: str, width: int = 90) -> str:
    one = source.replace("\n", "\\n")
    return one if len(one) <= width else one[: width - 3] + "..."


STOP_WORD = re.compile(r"^(@?[A-Za-z_][A-Za-z0-9_]*|[0-9]+|.)([=.(\[{]?)")


def cause_key(row: Mapping[str, Any]) -> str:
    """The token where the rejecting parser stopped (generated parser), or the
    reference parser's message with names and numbers folded."""
    if row["gen"] == "reject":
        stop = row["gen_why"] or ""
        if stop.startswith("<"):
            return "gen stopped at " + stop
        match = STOP_WORD.match(stop)
        token = re.sub(r"^[0-9]+$", "<number>", match.group(1)) + match.group(2)
        return f"gen stopped at {token!r}"
    message = (row["ref_why"] or "").splitlines()[0] if row["ref_why"] else ""
    message = re.sub(r"line \d+,? col(umn)? \d+:?\s*", "", message)
    message = re.sub(r"'[^']*'", "'…'", message)
    return "ref: " + re.sub(r"[0-9]+", "9", message)[:110]


def report(asm: Assembly, rows: list[dict[str, Any]], extras: list[str],
           elapsed: float) -> None:
    print("== generator rules applied")
    for line in asm.renamed:
        print(f"  renamed   {line}")
    for target, alt, rel in asm.integrations:
        print(f"  integrate {target} |= {alt}  ({rel})")
    print(f"  reserved words excluded from ident: {len(asm.reserved)}")
    print(f"\n== grammar conflicts (same rule name, different expression): {len(asm.conflicts)}")
    for name, fa, xa, fb, xb in asm.conflicts:
        print(f"  {name}\n    {fa}: {xa}\n    {fb}: {xb}   <- used")
    print(f"\n== undefined references: {sorted(asm.undefined) or 'none'}")
    odd = odd_charclasses(asm.rules)
    print(f"== brackets holding quoted literals (read as a character class): {len(odd)}")
    for name, pattern in odd:
        print(f"  {name}: [{pattern}]")

    print(f"\n== inputs: {len(rows)} in {elapsed:.1f} s")
    cols = ["ref", "gen", *extras]
    for corpus in ("conformance", "syntax-examples", "code-blocks"):
        part = [r for r in rows if r["corpus"] == corpus]
        if corpus == "code-blocks":
            both = [r for r in part if all(r[c] == "reject" for c in cols)]
            print(f"\n-- {corpus}: {len(part)} blocks, {len(both)} rejected by every parser"
                  " (not DSL; not counted below)")
            part = [r for r in part if r not in both]
        else:
            print(f"\n-- {corpus}: {len(part)}")
        table = collections.Counter((r["expect"], *(r[c] for c in cols)) for r in part)
        print("  " + "  ".join(f"{h:<8}" for h in ["count", "expect", *cols]) + "  mismatch")
        for key, n in sorted(table.items()):
            flag = "yes" if mismatch(dict(zip(["expect", *cols], key))) else ""
            print("  " + "  ".join(f"{v:<8}" for v in [n, *key]) + f"  {flag}")

    semantic_parse = [r for r in rows if r["expect"] == "semantic" and r["ref"] == "reject"
                      and r["gen"] == "accept"]
    print(f"\n== SemanticError expected, reference rejects while parsing, generated accepts:"
          f" {len(semantic_parse)} (not a mismatch)")
    timeouts = [r for r in rows if r["gen"] == "timeout"]
    print(f"== generated-parser timeouts (> {TIMEOUT_S} s): {len(timeouts)}")
    for r in timeouts:
        print(f"  {r['where']}")

    bad = [r for r in rows if mismatch(r)
           and not (r["corpus"] == "code-blocks" and all(r[c] == "reject" for c in cols))]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in bad:
        groups[(f"{r['expect']}/ref={r['ref']}/gen={r['gen']}", cause_key(r))].append(r)
    print(f"\n== mismatches: {len(bad)} in {len(groups)} groups"
          " (grouped by where the rejecting parser stopped)")
    for (verdicts, key), part in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        first = part[0]
        print(f"  {len(part):4}  [{verdicts}] {key}\n"
              f"        e.g. {first['where']}\n        {_short(first['source'])}")

    roots = collections.Counter((r["gen_root"], r["ref_root"]) for r in rows
                                if r["ref"] == "accept" and r["gen"] == "accept")
    print("\n== root rule (generated) -> AST class (reference), inputs both accept")
    for (g, ref), n in sorted(roots.items(), key=lambda kv: -kv[1]):
        print(f"  {n:5}  {g} -> {ref}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dump-lark", action="store_true", help="print the generated grammar")
    ap.add_argument("--json", type=Path, help="write every row to this file")
    ap.add_argument("--extra", action="append", default=[], metavar="NAME=COMMAND",
                    help="another parser: input on stdin, exit status 0 = accept")
    args = ap.parse_args()

    asm = assemble()
    text = lark_text(asm)
    if args.dump_lark:
        sys.stdout.write(text)
        return 0
    try:
        parser = Lark(text, parser="earley", start="file", ambiguity="resolve")
    except LarkError as exc:
        print(f"grammar build failed: {exc}", file=sys.stderr)
        return 2
    extras = dict(item.split("=", 1) for item in args.extra)
    ext = registry()
    started = time.monotonic()
    rows = []
    for case in [*conformance_cases(), *syntax_example_cases(), *code_block_cases()]:
        ref, ref_root, ref_why = judge_reference(case.source, ext)
        gen, gen_root, gen_why = judge_generated(parser, case.source)
        row = {**dataclasses.asdict(case), "ref": ref, "gen": gen,
               "ref_root": ref_root, "gen_root": gen_root,
               "ref_why": ref_why, "gen_why": gen_why}
        for name, command in extras.items():
            row[name] = judge_extra(command, case.source)
        rows.append(row)
    report(asm, rows, list(extras), time.monotonic() - started)
    if args.json:
        args.json.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
