# 実装計画: [機能]

**ブランチ**: `[###-feature-name]` | **日付**: [日付] | **仕様**: [リンク]
**入力**: `/specs/[###-feature-name]/spec.md` からの機能仕様

**注**: このテンプレートは `/speckit.plan` コマンドによって埋められます。実行ワークフローについては `.specify/templates/commands/plan.md` を参照してください。

## 概要

[機能仕様から抽出: 主要要件 + 研究からの技術アプローチ]

## 技術コンテキスト

<!--
  アクション必須: このセクションの内容をプロジェクトの技術詳細に置き換えてください。ここでの構造は反復プロセスをガイドするためのアドバイザリ容量で提示されています。
-->

**言語/バージョン**: [例: Python 3.11, Swift 5.9, Rust 1.75 または NEEDS CLARIFICATION]  
**主要依存関係**: [例: FastAPI, UIKit, LLVM または NEEDS CLARIFICATION]  
**ストレージ**: [該当する場合、例: PostgreSQL, CoreData, files または N/A]  
**テスト**: [例: pytest, XCTest, cargo test または NEEDS CLARIFICATION]  
**ターゲットプラットフォーム**: [例: Linux server, iOS 15+, WASM または NEEDS CLARIFICATION]
**プロジェクトタイプ**: [single/web/mobile - ソース構造を決定]  
**パフォーマンス目標**: [ドメイン固有、例: 1000 req/s, 10k lines/sec, 60 fps または NEEDS CLARIFICATION]  
**制約**: [ドメイン固有、例: <200ms p95, <100MB memory, offline-capable または NEEDS CLARIFICATION]  
**スケール/スコープ**: [ドメイン固有、例: 10k users, 1M LOC, 50 screens または NEEDS CLARIFICATION]

## 憲法チェック

*ゲート: Phase 0研究前に合格する必要。Phase 1設計後に再チェック。*

[憲法ファイルに基づいて決定されたゲート]

## プロジェクト構造

### ドキュメント (この機能)

```text
specs/[###-feature]/
├── plan.md              # このファイル (/speckit.plan コマンド出力)
├── research.md          # Phase 0出力 (/speckit.plan コマンド)
├── data-model.md        # Phase 1出力 (/speckit.plan コマンド)
├── quickstart.md        # Phase 1出力 (/speckit.plan コマンド)
├── contracts/           # Phase 1出力 (/speckit.plan コマンド)
└── tasks.md             # Phase 2出力 (/speckit.tasks コマンド - /speckit.plan によって作成されない)
```

### ソースコード (リポジトリルート)
<!--
  アクション必須: 下記のプレースホルダーツリーをこの機能の具体的なレイアウトに置き換えてください。未使用のオプションを削除し、選択した構造を実際のパスで拡張してください (例: apps/admin, packages/something)。提供される計画はオプションラベルを含まないようにしてください。
-->

```text
# [未使用の場合削除] オプション1: 単一プロジェクト (デフォルト)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [未使用の場合削除] オプション2: Webアプリケーション ("frontend" + "backend" が検出された場合)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [未使用の場合削除] オプション3: Mobile + API ("iOS/Android" が検出された場合)
api/
└── [上記のbackendと同じ]

ios/ or android/
└── [プラットフォーム固有構造: feature modules, UI flows, platform tests]
```

**構造決定**: [選択した構造を文書化し、上記でキャプチャされた実際のディレクトリを参照]

## 複雑さ追跡

> **憲法チェックに違反があり、正当化が必要な場合のみ記入**

| 違反 | なぜ必要か | 拒否されたよりシンプルな代替案 |
|-----------|------------|-------------------------------------|
| [例: 4番目のプロジェクト] | [現在の必要性] | [なぜ3つのプロジェクトが不十分か] |
| [例: Repositoryパターン] | [特定のプロブレム] | [なぜ直接DBアクセスが不十分か] |