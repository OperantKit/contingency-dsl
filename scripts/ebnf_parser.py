"""
EBNF Parser for contingency-dsl grammar files.

Parses the project's EBNF notation into an AST that can be consumed
by target-specific emitters (Tree-sitter, Langium, etc.).

Notation handled:
  ::=    definition
  |      alternation
  *      zero or more
  +      one or more
  ?      optional
  "x"    terminal literal
  [...]  character class
  (...)  grouping
  ;      line comment (start of line)
  --     inline comment
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union


# === AST Nodes ===

@dataclass
class Terminal:
    """A quoted literal like "let" or "(" """
    value: str


@dataclass
class CharClass:
    """A character class like [a-z_] or [0-9]"""
    pattern: str  # raw content between brackets


@dataclass
class Reference:
    """A reference to another production rule"""
    name: str


@dataclass
class Sequence:
    """Ordered sequence of expressions"""
    elements: List[Expr]


@dataclass
class Alternation:
    """Choice between alternatives"""
    alternatives: List[Expr]


@dataclass
class Repeat:
    """Zero-or-more (*) repetition"""
    expr: Expr


@dataclass
class Repeat1:
    """One-or-more (+) repetition"""
    expr: Expr


@dataclass
class OptionalExpr:
    """Optional (?) expression"""
    expr: Expr


@dataclass
class Group:
    """Parenthesized group"""
    expr: Expr


Expr = Union[Terminal, CharClass, Reference, Sequence, Alternation,
             Repeat, Repeat1, OptionalExpr, Group]


@dataclass
class Rule:
    """A production rule: name ::= expr"""
    name: str
    expr: Expr
    comment: str = ""  # inline comment from first line


@dataclass
class Grammar:
    """Complete parsed grammar"""
    rules: List[Rule]
    source_file: str = ""
    preamble_comments: List[str] = field(default_factory=list)


# === Tokenizer ===

class Token:
    __slots__ = ('type', 'value', 'line')

    def __init__(self, type_: str, value: str, line: int = 0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r})"


# Token types
TOK_IDENT = 'IDENT'
TOK_LITERAL = 'LITERAL'      # "..."
TOK_CHARCLASS = 'CHARCLASS'  # [...]
TOK_DEFN = 'DEFN'            # ::=
TOK_PIPE = 'PIPE'            # |
TOK_STAR = 'STAR'            # *
TOK_PLUS = 'PLUS'            # +
TOK_QUEST = 'QUEST'          # ?
TOK_LPAREN = 'LPAREN'        # (
TOK_RPAREN = 'RPAREN'        # )
TOK_EOF = 'EOF'

# Regex for tokenizing a single cleaned line
_TOKEN_RE = re.compile(r"""
    (?P<literal>"[^"]*"|'[^']*')  |  # quoted literal (double or single quotes)
    (?P<charclass>\[[^\]]*\])     |  # character class
    (?P<defn>::=)                  |  # definition
    (?P<pipe>\|)                   |  # alternation
    (?P<star>\*)                   |  # zero or more
    (?P<plus>\+)                   |  # one or more
    (?P<quest>\?)                  |  # optional
    (?P<lparen>\()                 |  # left paren
    (?P<rparen>\))                 |  # right paren
    (?P<ident>[a-zA-Z_][a-zA-Z0-9_]*) |  # identifier
    (?P<ws>\s+)                       # whitespace (skip)
""", re.VERBOSE)


def _tokenize_lines(lines: List[str]) -> List[Token]:
    """Tokenize cleaned EBNF lines into a flat token list."""
    tokens = []
    for lineno, line in enumerate(lines, 1):
        pos = 0
        while pos < len(line):
            m = _TOKEN_RE.match(line, pos)
            if not m:
                # Skip unknown character
                pos += 1
                continue
            pos = m.end()
            if m.lastgroup == 'ws':
                continue
            elif m.lastgroup == 'literal':
                # Strip quotes (both " and ')
                raw = m.group()
                tokens.append(Token(TOK_LITERAL, raw[1:-1], lineno))
            elif m.lastgroup == 'charclass':
                tokens.append(Token(TOK_CHARCLASS, m.group(), lineno))
            elif m.lastgroup == 'defn':
                tokens.append(Token(TOK_DEFN, '::=', lineno))
            elif m.lastgroup == 'pipe':
                tokens.append(Token(TOK_PIPE, '|', lineno))
            elif m.lastgroup == 'star':
                tokens.append(Token(TOK_STAR, '*', lineno))
            elif m.lastgroup == 'plus':
                tokens.append(Token(TOK_PLUS, '+', lineno))
            elif m.lastgroup == 'quest':
                tokens.append(Token(TOK_QUEST, '?', lineno))
            elif m.lastgroup == 'lparen':
                tokens.append(Token(TOK_LPAREN, '(', lineno))
            elif m.lastgroup == 'rparen':
                tokens.append(Token(TOK_RPAREN, ')', lineno))
            elif m.lastgroup == 'ident':
                tokens.append(Token(TOK_IDENT, m.group(), lineno))
    tokens.append(Token(TOK_EOF, '', 0))
    return tokens


# === Parser ===

class ParseError(Exception):
    pass


class EBNFParser:
    """Recursive descent parser for the project's EBNF notation."""

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._pos = 0

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, type_: str) -> Token:
        tok = self._advance()
        if tok.type != type_:
            raise ParseError(
                f"Expected {type_}, got {tok.type} ({tok.value!r}) "
                f"at line {tok.line}"
            )
        return tok

    def _at_rule_start(self) -> bool:
        """Check if current position is at the start of a new rule (IDENT ::=)."""
        if self._peek().type != TOK_IDENT:
            return False
        if self._pos + 1 < len(self._tokens):
            return self._tokens[self._pos + 1].type == TOK_DEFN
        return False

    def parse(self) -> List[Rule]:
        """Parse all rules."""
        rules = []
        while self._peek().type != TOK_EOF:
            if self._at_rule_start():
                rules.append(self._parse_rule())
            else:
                # Skip stray tokens (shouldn't happen with clean input)
                self._advance()
        return rules

    def _parse_rule(self) -> Rule:
        name_tok = self._expect(TOK_IDENT)
        self._expect(TOK_DEFN)
        expr = self._parse_alternation()
        return Rule(name=name_tok.value, expr=expr)

    def _parse_alternation(self) -> Expr:
        alternatives = [self._parse_sequence()]
        while self._peek().type == TOK_PIPE:
            self._advance()
            alternatives.append(self._parse_sequence())
        if len(alternatives) == 1:
            return alternatives[0]
        return Alternation(alternatives=alternatives)

    def _parse_sequence(self) -> Expr:
        elements = []
        while True:
            tok = self._peek()
            # Stop conditions: end of input, pipe, rparen, or new rule start
            if tok.type in (TOK_EOF, TOK_PIPE, TOK_RPAREN):
                break
            if self._at_rule_start():
                break
            elem = self._parse_postfix()
            if elem is not None:
                elements.append(elem)
            else:
                break
        if len(elements) == 0:
            # Empty sequence — return a reference to empty (shouldn't happen normally)
            return Sequence(elements=[])
        if len(elements) == 1:
            return elements[0]
        return Sequence(elements=elements)

    def _parse_postfix(self) -> Optional[Expr]:
        atom = self._parse_atom()
        if atom is None:
            return None
        # Check for postfix operators
        while self._peek().type in (TOK_STAR, TOK_PLUS, TOK_QUEST):
            op = self._advance()
            if op.type == TOK_STAR:
                atom = Repeat(expr=atom)
            elif op.type == TOK_PLUS:
                atom = Repeat1(expr=atom)
            elif op.type == TOK_QUEST:
                atom = OptionalExpr(expr=atom)
        return atom

    def _parse_atom(self) -> Optional[Expr]:
        tok = self._peek()
        if tok.type == TOK_LITERAL:
            self._advance()
            return Terminal(value=tok.value)
        elif tok.type == TOK_CHARCLASS:
            self._advance()
            return CharClass(pattern=tok.value)
        elif tok.type == TOK_IDENT:
            # Only consume if not the start of a new rule
            if not self._at_rule_start():
                self._advance()
                return Reference(name=tok.value)
            return None
        elif tok.type == TOK_LPAREN:
            self._advance()
            expr = self._parse_alternation()
            self._expect(TOK_RPAREN)
            return Group(expr=expr)
        return None


# === Public API ===

def _clean_lines(text: str) -> tuple[List[str], List[str]]:
    """
    Clean EBNF source text:
    - Strip full-line comments (starting with ;)
    - Strip inline comments (-- or ; outside quotes)
    - Collapse blank lines
    Returns (cleaned_lines, preamble_comments).
    """
    preamble = []
    cleaned = []
    in_preamble = True

    for line in text.splitlines():
        stripped = line.strip()

        # Full-line comment
        if stripped.startswith(';'):
            if in_preamble:
                preamble.append(stripped[1:].strip())
            continue

        # Empty line
        if not stripped:
            in_preamble = False
            continue

        in_preamble = False

        # Strip inline comments (-- or ;) outside quoted strings
        result = []
        quote_char = None  # None, '"', or "'"
        i = 0
        while i < len(line):
            ch = line[i]
            if quote_char is not None:
                result.append(ch)
                if ch == quote_char:
                    quote_char = None
            elif ch in ('"', "'"):
                quote_char = ch
                result.append(ch)
            elif i + 1 < len(line) and line[i:i+2] == '--':
                break  # inline comment
            elif ch == ';':
                break  # inline comment
            else:
                result.append(ch)
            i += 1

        cleaned_line = ''.join(result).strip()
        if cleaned_line:
            cleaned.append(cleaned_line)

    return cleaned, preamble


def parse_ebnf(text: str, source_file: str = "") -> Grammar:
    """Parse EBNF text into a Grammar AST."""
    cleaned, preamble = _clean_lines(text)
    tokens = _tokenize_lines(cleaned)
    parser = EBNFParser(tokens)
    rules = parser.parse()
    return Grammar(
        rules=rules,
        source_file=source_file,
        preamble_comments=preamble,
    )


def parse_ebnf_file(path: str | Path) -> Grammar:
    """Parse an EBNF file into a Grammar AST."""
    path = Path(path)
    text = path.read_text(encoding='utf-8')
    return parse_ebnf(text, source_file=str(path))


def merge_grammars(grammars: List[Grammar]) -> Grammar:
    """
    Merge multiple grammars (core + extensions) into one.
    Later rules with the same name override earlier ones.

    Also performs extension integration: if extension grammars define
    rules like `adj_schedule`, `interlock_schedule`, `trial_based_schedule`
    that are documented as extending `base_schedule`, the merger
    appends them as alternatives to the `base_schedule` rule.
    """
    seen: dict[str, int] = {}
    all_rules: list[Rule] = []
    all_comments: list[str] = []

    # Known extension rules that should be added to base_schedule
    BASE_SCHEDULE_EXTENSIONS = {
        'adj_schedule', 'interlock_schedule', 'trial_based_schedule',
    }

    extension_rules_found: list[str] = []

    for g in grammars:
        all_comments.extend(g.preamble_comments)
        for rule in g.rules:
            if rule.name in seen:
                # Replace existing rule (extension overrides core)
                idx = seen[rule.name]
                all_rules[idx] = rule
            else:
                seen[rule.name] = len(all_rules)
                all_rules.append(rule)

            if rule.name in BASE_SCHEDULE_EXTENSIONS:
                extension_rules_found.append(rule.name)

    # Integrate extension rules into base_schedule
    if extension_rules_found and 'base_schedule' in seen:
        idx = seen['base_schedule']
        base = all_rules[idx]
        expr = base.expr

        # Append extension references as new alternatives
        new_alts = [Reference(name=name) for name in extension_rules_found]

        if isinstance(expr, Alternation):
            expr = Alternation(alternatives=expr.alternatives + new_alts)
        else:
            expr = Alternation(alternatives=[expr] + new_alts)

        all_rules[idx] = Rule(name=base.name, expr=expr, comment=base.comment)

    return Grammar(
        rules=all_rules,
        source_file="<merged>",
        preamble_comments=all_comments,
    )


# === Utility: collect rule names ===

def rule_names(grammar: Grammar) -> set[str]:
    """Return set of all defined rule names."""
    return {r.name for r in grammar.rules}


def collect_terminals(expr: Expr) -> set[str]:
    """Recursively collect all terminal literals from an expression."""
    if isinstance(expr, Terminal):
        return {expr.value}
    elif isinstance(expr, (CharClass, Reference)):
        return set()
    elif isinstance(expr, Sequence):
        result = set()
        for e in expr.elements:
            result |= collect_terminals(e)
        return result
    elif isinstance(expr, Alternation):
        result = set()
        for a in expr.alternatives:
            result |= collect_terminals(a)
        return result
    elif isinstance(expr, (Repeat, Repeat1, OptionalExpr, Group)):
        return collect_terminals(expr.expr)
    return set()


def collect_references(expr: Expr) -> set[str]:
    """Recursively collect all rule references from an expression."""
    if isinstance(expr, Reference):
        return {expr.name}
    elif isinstance(expr, (Terminal, CharClass)):
        return set()
    elif isinstance(expr, Sequence):
        result = set()
        for e in expr.elements:
            result |= collect_references(e)
        return result
    elif isinstance(expr, Alternation):
        result = set()
        for a in expr.alternatives:
            result |= collect_references(a)
        return result
    elif isinstance(expr, (Repeat, Repeat1, OptionalExpr, Group)):
        return collect_references(expr.expr)
    return set()
