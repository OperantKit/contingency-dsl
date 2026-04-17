# Tooling — Editor Support & Generated Artifacts

This document describes how contingency-dsl provides editor tooling
(syntax highlighting, LSP) from its grammar specification, and how
generated artifacts are distributed.

---

## Architecture

```
schema/*/grammar.ebnf          (source of truth — tracked in git)
        │
        ├─→ scripts/gen-treesitter.sh ─→ dist/tree-sitter/
        │       grammar.js, parser.c, parser.wasm
        │
        └─→ scripts/gen-langium.sh ───→ dist/langium/
                contingency-dsl.langium, LSP server bundle, .vsix
```

The `schema/` directory contains the normative EBNF grammars arranged to
mirror the Ψ spec layout:

| File | Scope |
|---|---|
| `schema/foundations/grammar.ebnf` | Paradigm-neutral formal base (CFG skeleton, meta-grammar) |
| `schema/operant/grammar.ebnf` | Operant schedules (FR, VI, Chain, Conc, etc.) |
| `schema/operant/stateful/grammar.ebnf` | Operant.Stateful (Pctl, Adj, Interlocking) |
| `schema/operant/trial-based/grammar.ebnf` | Operant.TrialBased (MTS, Go/NoGo) |
| `schema/respondent/grammar.ebnf` | Respondent Tier A primitives + extension point |

These EBNF files are the **single source of truth**. All tooling
artifacts are derived from them and are distributed as reproducible
outputs under `dist/` (generated via `scripts/gen-langium.sh` and
`scripts/gen-treesitter.sh`).

### EBNF loader order

Both converter scripts load the EBNF fragments in a deterministic order
that guarantees the merged grammar respects layer dependencies:

1. **Foundations** first (paradigm-neutral lexical and meta-grammar rules)
2. **Operant** (three-term contingency)
3. **Operant.Stateful** (`operant/stateful/grammar.ebnf`)
4. **Operant.TrialBased** (`operant/trial-based/grammar.ebnf`)
5. **Respondent** (two-term Tier A primitives + extension point)

After the ordered prefix is loaded, the script discovers any additional
`grammar.ebnf` files under `schema/` via `rglob` and appends them in
sorted order. This lets new extension layers (for example, future
annotation-specific EBNF fragments) be added to the build without
editing the converter scripts.

The ordering policy lives in `scripts/ebnf2langium.py` and
`scripts/ebnf2treesitter.py` (variable `_LOAD_ORDER` in Langium). If a
grammar fragment outside the ordered prefix needs to precede Respondent,
promote it in `_LOAD_ORDER`.

---

## Tree-sitter (I-9)

[Tree-sitter](https://tree-sitter.github.io/tree-sitter/) provides
incremental parsing for syntax highlighting, code folding, and
structural queries in editors (Neovim, Helix, Zed, Emacs, VS Code
via extensions).

### Generation pipeline

```
grammar.ebnf ──[ebnf2treesitter]──→ grammar.js ──[tree-sitter generate]──→ parser.c
                                                                            ├── src/parser.c
                                                                            ├── src/tree_sitter/parser.h
                                                                            └── src/grammar.json
```

1. **EBNF → grammar.js**: A converter script (`scripts/ebnf2treesitter.py`,
   not yet implemented) reads the EBNF and emits a Tree-sitter
   `grammar.js` using the Tree-sitter DSL.

2. **grammar.js → parser.c**: `tree-sitter generate` compiles the
   JavaScript grammar into a C parser.

3. **WASM build** (optional): `tree-sitter build-wasm` produces a
   `.wasm` binary for web-based editors and the Tree-sitter playground.

### Output (`dist/tree-sitter/`)

| File | Description |
|---|---|
| `grammar.js` | Tree-sitter grammar definition |
| `src/parser.c` | Generated C parser |
| `src/tree_sitter/parser.h` | Parser header |
| `src/grammar.json` | Serialized grammar (for queries) |
| `tree-sitter-contingency-dsl.wasm` | WASM parser (for web editors) |

### Usage

```bash
./scripts/gen-treesitter.sh
```

### Editor integration

Once generated, the Tree-sitter grammar can be registered with
editors that support Tree-sitter grammars natively:

- **Neovim**: Add to `nvim-treesitter` parser list
- **Helix**: Add grammar entry to `languages.toml`
- **Zed**: Register as a Tree-sitter extension
- **VS Code**: Use via `vscode-anycode` or a dedicated extension

---

## Langium LSP Server (I-11)

[Langium](https://langium.org/) is a language engineering framework
for VS Code and the web. It generates a full Language Server Protocol
(LSP) server from a grammar definition, providing:

- Syntax error diagnostics
- Auto-completion
- Hover documentation
- Go-to-definition (for `let` bindings)
- Symbol outline

### Generation pipeline

```
grammar.ebnf ──[ebnf2langium]──→ .langium ──[langium generate]──→ src/generated/
                                                                    ├── ast.ts
                                                                    ├── grammar.ts
                                                                    └── module.ts
```

1. **EBNF → .langium**: A converter script (`scripts/ebnf2langium.py`,
   not yet implemented) translates EBNF into Langium grammar syntax.

   Key transformations:
   - Add `entry` keyword to the root rule
   - Convert repetition (`*`, `+`) to property assignments (`+=`)
   - Add `terminal` definitions for lexical tokens (ID, INT, FLOAT, etc.)
   - Map optional (`?`) to `?=` boolean properties where appropriate

2. **langium generate**: Produces TypeScript AST types and grammar
   access modules from the `.langium` file.

3. **Build**: Standard TypeScript compilation + bundling into a
   standalone LSP server.

### Output (`dist/langium/`)

| File | Description |
|---|---|
| `contingency-dsl.langium` | Langium grammar (generated from EBNF) |
| `src/generated/ast.ts` | TypeScript AST node types |
| `src/generated/grammar.ts` | Grammar access module |
| `out/` | Compiled LSP server |
| `contingency-dsl-*.vsix` | VS Code extension package |

### Usage

```bash
./scripts/gen-langium.sh
```

---

## Distribution

Generated artifacts are reproducible from the tracked EBNF sources via
`scripts/gen-langium.sh` and `scripts/gen-treesitter.sh`. They are not
committed to git and are intended to be distributed through GitHub
Releases (when a release pipeline is configured).

### Release workflow

```
git tag v1.0.0 && git push --tags
        │
        └─→ CI (.github/workflows/release.yml)
              ├── scripts/gen-treesitter.sh
              │     └── produces: tree-sitter-contingency-dsl.wasm
              ├── scripts/gen-langium.sh
              │     └── produces: contingency-dsl-lsp-*.vsix
              └── gh release upload v1.0.0 dist/**
```

### Release assets

Each tagged release publishes the following assets to the GitHub
Releases page:

| Asset | Format | Use case |
|---|---|---|
| `tree-sitter-contingency-dsl.wasm` | WASM | Web playground, browser-based editors |
| `tree-sitter-contingency-dsl-{os}-{arch}.so/dylib/dll` | Shared library | Native editors (Neovim, Helix) |
| `contingency-dsl-lsp-{version}.vsix` | VS Code extension | VS Code / Cursor / VS Code forks |
| `contingency-dsl-lsp-{os}-{arch}` | Standalone binary | Non-VS Code LSP clients (Neovim, Emacs) |

### Installing from a release

```bash
# Tree-sitter (Neovim example)
gh release download v1.0.0 -p "tree-sitter-contingency-dsl-darwin-arm64.dylib"

# VS Code extension
gh release download v1.0.0 -p "contingency-dsl-lsp-*.vsix"
code --install-extension contingency-dsl-lsp-*.vsix
```

---

## Implementation status

| Component | Status | Blocker |
|---|---|---|
| `scripts/gen-treesitter.sh` | Scaffold | `ebnf2treesitter.py` converter |
| `scripts/gen-langium.sh` | Scaffold | `ebnf2langium.py` converter |
| `dist/tree-sitter/` | Directory ready | Generation script |
| `dist/langium/` | Directory ready | Generation script |
| CI release workflow | Not yet | Converters must exist first |

### Dependency chain

```
ebnf2treesitter.py ──→ gen-treesitter.sh works ──→ CI can build Tree-sitter assets
ebnf2langium.py    ──→ gen-langium.sh works    ──→ CI can build Langium/.vsix assets
                                                ──→ release.yml publishes to GitHub Releases
```

---

## References

- Fowler, M. (2010). *Domain-Specific Languages*. §33 Language Workbench.
- Tree-sitter documentation: https://tree-sitter.github.io/tree-sitter/
- Langium documentation: https://langium.org/docs/
