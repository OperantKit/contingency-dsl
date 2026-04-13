#!/usr/bin/env bash
# gen-treesitter.sh — Generate Tree-sitter grammar from EBNF sources
#
# Usage: ./scripts/gen-treesitter.sh
#
# Source of truth: schema/*/grammar.ebnf
# Output:         dist/tree-sitter/
#
# Prerequisites:
#   Python 3.10+
#   npm install tree-sitter-cli   (or: cargo install tree-sitter-cli)
#
# Future: Called by CI on release tags to produce parser binaries
# for GitHub Releases (WASM, shared libraries).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="${REPO_ROOT}/scripts"
DIST_DIR="${REPO_ROOT}/dist/tree-sitter"

echo "==> Cleaning dist/tree-sitter/"
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# --- Step 1: Generate grammar.js from EBNF ---
echo "==> Generating grammar.js from EBNF"
python3 "${SCRIPTS_DIR}/ebnf2treesitter.py" \
  --schema-dir "${REPO_ROOT}/schema" \
  --output "${DIST_DIR}/grammar.js"

# --- Step 2: Run tree-sitter generate ---
if command -v tree-sitter &>/dev/null || command -v npx &>/dev/null; then
  echo "==> Running tree-sitter generate"
  cd "${DIST_DIR}"

  # Initialize package.json if absent (tree-sitter generate requires it)
  if [ ! -f package.json ]; then
    cat > package.json <<'PKGJSON'
{
  "name": "tree-sitter-contingency-dsl",
  "version": "0.0.1",
  "description": "Tree-sitter grammar for contingency-dsl",
  "main": "grammar.js",
  "tree-sitter": [
    {
      "scope": "source.contingency-dsl",
      "file-types": ["cdsl"]
    }
  ]
}
PKGJSON
  fi

  if command -v tree-sitter &>/dev/null; then
    tree-sitter generate
  else
    npx tree-sitter-cli generate
  fi

  # --- Step 3: Build WASM (for web / playground) ---
  echo "==> Building WASM"
  if command -v tree-sitter &>/dev/null; then
    tree-sitter build --wasm . 2>/dev/null || echo "WARN: WASM build skipped (emscripten not found)"
  else
    npx tree-sitter-cli build --wasm . 2>/dev/null || echo "WARN: WASM build skipped (emscripten not found)"
  fi
else
  echo "WARN: tree-sitter CLI not found. grammar.js generated but parser.c not built."
  echo "      Install: npm install -g tree-sitter-cli  (or: cargo install tree-sitter-cli)"
  echo "      Then re-run this script."
fi

echo "==> Done. Artifacts in dist/tree-sitter/"
