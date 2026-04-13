#!/usr/bin/env bash
# gen-langium.sh — Generate Langium LSP server from EBNF sources
#
# Usage: ./scripts/gen-langium.sh
#
# Source of truth: schema/*/grammar.ebnf
# Output:         dist/langium/
#
# Prerequisites:
#   Python 3.10+
#   npm install langium-cli   (or: npx langium generate)
#
# Future: Called by CI on release tags to produce VS Code extension
# .vsix for GitHub Releases.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="${REPO_ROOT}/scripts"
DIST_DIR="${REPO_ROOT}/dist/langium"

echo "==> Cleaning dist/langium/"
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# --- Step 1: Generate .langium from EBNF ---
echo "==> Generating .langium from EBNF"
python3 "${SCRIPTS_DIR}/ebnf2langium.py" \
  --schema-dir "${REPO_ROOT}/schema" \
  --output "${DIST_DIR}/contingency-dsl.langium"

# --- Step 2: Run langium generate (if CLI available) ---
if command -v npx &>/dev/null && npx langium --version &>/dev/null 2>&1; then
  echo "==> Running langium generate"
  cd "${DIST_DIR}"
  npx langium generate

  # --- Step 3: Build & bundle LSP server ---
  echo "==> Building LSP server"
  npm run build 2>/dev/null || echo "WARN: npm build not configured yet"
else
  echo "WARN: langium CLI not found. .langium grammar generated but LSP not built."
  echo "      Install: npm install langium-cli"
  echo "      Then re-run this script."
fi

echo "==> Done. Artifacts in dist/langium/"
