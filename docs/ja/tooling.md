# ツーリング — エディタ支援と生成成果物

このドキュメントは、contingency-dsl が文法仕様からエディタツーリング
（構文ハイライト、LSP）をどのように提供するか、および生成成果物の
配布方法を説明する。

---

## アーキテクチャ

```
schema/*/grammar.ebnf          （正典 — git で追跡）
        │
        ├─→ scripts/gen-treesitter.sh ─→ dist/tree-sitter/
        │       grammar.js, parser.c, parser.wasm
        │
        └─→ scripts/gen-langium.sh ───→ dist/langium/
                contingency-dsl.langium, LSP サーババンドル, .vsix
```

`schema/` ディレクトリに規範的な EBNF 文法が 仕様と同じレイアウトで
格納されている:

| ファイル | スコープ |
|---|---|
| `schema/foundations/grammar.ebnf` | パラダイム中立な形式基盤（CFG 骨格、メタ文法） |
| `schema/operant/grammar.ebnf` | オペラント・スケジュール（FR, VI, Chain, Conc 等） |
| `schema/operant/stateful/grammar.ebnf` | Operant.Stateful（Pctl, Adj, Interlocking） |
| `schema/operant/trial-based/grammar.ebnf` | Operant.TrialBased（MTS, Go/NoGo） |
| `schema/respondent/grammar.ebnf` | レスポンデント Tier A primitive + 拡張ポイント |

これらの EBNF ファイルが**唯一の正典**である。すべてのツーリング成果物は
これらから派生し、`scripts/gen-langium.sh` と `scripts/gen-treesitter.sh`
で再現可能な形式で `dist/` に出力される。

### EBNF ローダ順序

両コンバータ・スクリプトは層依存関係を保つ決定論的な順序で EBNF 断片を
ロードする:

1. **基盤 (Foundations)** を最初に（パラダイム中立な字句規則とメタ文法）
2. **オペラント (Operant)** （三項随伴性）
3. **Operant.Stateful**（`operant/stateful/grammar.ebnf`）
4. **Operant.TrialBased**（`operant/trial-based/grammar.ebnf`）
5. **レスポンデント (Respondent)**（Tier A primitive + 拡張ポイント）

順序つき接頭部のロード後、スクリプトは `schema/` 配下の追加 `grammar.ebnf`
を `rglob` で発見しソート順に追記する。これにより新しい拡張層（例: 将来
の注釈固有 EBNF 断片）をコンバータ編集なしでビルドに加えられる。

順序ポリシーは `scripts/ebnf2langium.py` および `scripts/ebnf2treesitter.py`
（Langium 側の変数 `_LOAD_ORDER`）に存在する。順序つき接頭部外の文法断片
がレスポンデントより前に必要な場合は `_LOAD_ORDER` に昇格する。

---

## Tree-sitter（I-9）

[Tree-sitter](https://tree-sitter.github.io/tree-sitter/) は
インクリメンタルパーシングによる構文ハイライト、コード折りたたみ、
構造的クエリをエディタ（Neovim, Helix, Zed, Emacs, VS Code 拡張経由）で
提供する。

### 生成パイプライン

```
grammar.ebnf ──[ebnf2treesitter]──→ grammar.js ──[tree-sitter generate]──→ parser.c
                                                                            ├── src/parser.c
                                                                            ├── src/tree_sitter/parser.h
                                                                            └── src/grammar.json
```

1. **EBNF → grammar.js**: 変換スクリプト（`scripts/ebnf2treesitter.py`、
   未実装）が EBNF を読み、Tree-sitter DSL で `grammar.js` を出力する。

2. **grammar.js → parser.c**: `tree-sitter generate` が JavaScript 文法を
   C パーサにコンパイルする。

3. **WASM ビルド**（任意）: `tree-sitter build-wasm` が Web エディタ・
   Tree-sitter Playground 用の `.wasm` バイナリを生成する。

### 出力（`dist/tree-sitter/`）

| ファイル | 説明 |
|---|---|
| `grammar.js` | Tree-sitter 文法定義 |
| `src/parser.c` | 生成された C パーサ |
| `src/tree_sitter/parser.h` | パーサヘッダ |
| `src/grammar.json` | シリアライズ済み文法（クエリ用） |
| `tree-sitter-contingency-dsl.wasm` | WASM パーサ（Web エディタ用） |

### 使い方

```bash
./scripts/gen-treesitter.sh
```

### エディタ統合

生成後の Tree-sitter 文法は、Tree-sitter をネイティブサポートする
エディタに登録できる:

- **Neovim**: `nvim-treesitter` パーサリストに追加
- **Helix**: `languages.toml` に文法エントリを追加
- **Zed**: Tree-sitter 拡張として登録
- **VS Code**: `vscode-anycode` または専用拡張経由で使用

---

## Langium LSP サーバ（I-11）

[Langium](https://langium.org/) は VS Code および Web 向けの言語
エンジニアリングフレームワークである。文法定義から完全な Language Server
Protocol（LSP）サーバを生成し、以下を提供する:

- 構文エラー診断
- 自動補完
- ホバードキュメント
- 定義へのジャンプ（`let` バインディング用）
- シンボルアウトライン

### 生成パイプライン

```
grammar.ebnf ──[ebnf2langium]──→ .langium ──[langium generate]──→ src/generated/
                                                                    ├── ast.ts
                                                                    ├── grammar.ts
                                                                    └── module.ts
```

1. **EBNF → .langium**: 変換スクリプト（`scripts/ebnf2langium.py`、
   未実装）が EBNF を Langium 文法構文に変換する。

   主な変換点:
   - ルートルールに `entry` キーワードを追加
   - 繰り返し（`*`, `+`）をプロパティ代入（`+=`）に変換
   - 字句トークンの `terminal` 定義を追加（ID, INT, FLOAT 等）
   - 任意（`?`）を適宜 `?=` ブーリアンプロパティにマップ

2. **langium generate**: `.langium` ファイルから TypeScript の AST 型と
   文法アクセスモジュールを生成する。

3. **ビルド**: 標準的な TypeScript コンパイル + スタンドアロン LSP サーバへの
   バンドル。

### 出力（`dist/langium/`）

| ファイル | 説明 |
|---|---|
| `contingency-dsl.langium` | Langium 文法（EBNF から生成） |
| `src/generated/ast.ts` | TypeScript AST ノード型 |
| `src/generated/grammar.ts` | 文法アクセスモジュール |
| `out/` | コンパイル済み LSP サーバ |
| `contingency-dsl-*.vsix` | VS Code 拡張パッケージ |

### 使い方

```bash
./scripts/gen-langium.sh
```

---

## 配布

生成成果物は `scripts/gen-langium.sh` と `scripts/gen-treesitter.sh` に
より追跡済みの EBNF ソースから再現可能である。git にコミットせず、
リリース・パイプラインの整備後は GitHub Releases を通じて配布する想定。

### リリースワークフロー

```
git tag v1.0.0 && git push --tags
        │
        └─→ CI (.github/workflows/release.yml)
              ├── scripts/gen-treesitter.sh
              │     └── 生成: tree-sitter-contingency-dsl.wasm
              ├── scripts/gen-langium.sh
              │     └── 生成: contingency-dsl-lsp-*.vsix
              └── gh release upload v1.0.0 dist/**
```

### リリースアセット

タグ付きリリースごとに以下のアセットを GitHub Releases ページに公開する:

| アセット | 形式 | 用途 |
|---|---|---|
| `tree-sitter-contingency-dsl.wasm` | WASM | Web Playground、ブラウザベースエディタ |
| `tree-sitter-contingency-dsl-{os}-{arch}.so/dylib/dll` | 共有ライブラリ | ネイティブエディタ（Neovim, Helix） |
| `contingency-dsl-lsp-{version}.vsix` | VS Code 拡張 | VS Code / Cursor / VS Code フォーク |
| `contingency-dsl-lsp-{os}-{arch}` | スタンドアロンバイナリ | VS Code 以外の LSP クライアント（Neovim, Emacs） |

### リリースからのインストール

```bash
# Tree-sitter（Neovim の例）
gh release download v1.0.0 -p "tree-sitter-contingency-dsl-darwin-arm64.dylib"

# VS Code 拡張
gh release download v1.0.0 -p "contingency-dsl-lsp-*.vsix"
code --install-extension contingency-dsl-lsp-*.vsix
```

---

## 実装状況

| コンポーネント | ステータス | ブロッカー |
|---|---|---|
| `scripts/gen-treesitter.sh` | スキャフォールド | `ebnf2treesitter.py` 変換器 |
| `scripts/gen-langium.sh` | スキャフォールド | `ebnf2langium.py` 変換器 |
| `dist/tree-sitter/` | ディレクトリ準備済み | 生成スクリプト |
| `dist/langium/` | ディレクトリ準備済み | 生成スクリプト |
| CI リリースワークフロー | 未着手 | 変換器が先 |

### 依存チェーン

```
ebnf2treesitter.py ──→ gen-treesitter.sh 動作 ──→ CI が Tree-sitter アセットをビルド可能
ebnf2langium.py    ──→ gen-langium.sh 動作    ──→ CI が Langium/.vsix アセットをビルド可能
                                               ──→ release.yml が GitHub Releases に公開
```

---

## 参照

- Fowler, M. (2010). *Domain-Specific Languages*. §33 Language Workbench.
- Tree-sitter documentation: https://tree-sitter.github.io/tree-sitter/
- Langium documentation: https://langium.org/docs/
