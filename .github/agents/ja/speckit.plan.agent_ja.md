````chatagent
---
description: plan テンプレートを使用した実装計画実行ワークフローを実行して、設計成果物を生成します。
handoffs: 
  - label: タスクを作成
    agent: speckit.tasks
    prompt: 計画をタスクに分割
    send: true
  - label: チェックリストを作成
    agent: speckit.checklist
    prompt: 次のドメインのチェックリストを作成...
---

## ユーザー入力

```text
$ARGUMENTS
```

ユーザー入力を考慮してください（空の場合は無視）。

## アウトライン

1. **セットアップ**: リポジトリルートから `.specify/scripts/powershell/setup-plan.ps1 -Json` を実行し、JSON を解析して FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH を取得します。

2. **コンテキストをロード**: FEATURE_SPEC と `.specify/memory/constitution.md` を読み込みます。IMPL_PLAN テンプレート（既にコピー済み）をロードします。

3. **計画ワークフローを実行**: IMPL_PLAN テンプレートの構造に従います：
   - 技術コンテキストを入力
   - 憲法チェックセクションを入力
   - ゲートを評価
   - フェーズ 0：research.md を生成
   - フェーズ 1：data-model.md、contracts/、quickstart.md を生成
   - フェーズ 1：エージェントコンテキストを更新
   - 設計後に憲法チェックを再評価

4. **報告と停止**: フェーズ 2 計画後に停止します。ブランチ名、IMPL_PLAN パス、生成された成果物を報告します。

## フェーズ

### フェーズ 0：アウトラインと研究

1. **技術コンテキストから未知数を抽出**:
   - 各「明確化が必要」→ 研究タスク
   - 各依存関係 → ベストプラクティスタスク

2. **研究エージェントを生成して派遣**:
   ```
   各未知数について:
     タスク: "{unknown} の研究（{機能コンテキスト}用）"
   ```

3. **research.md で結果を統合**:
   - 決定：選択したもの
   - 理由：なぜ選択したか
   - 検討した代替案

**出力**: すべての「明確化が必要」が解決された research.md

### フェーズ 1：設計とコントラクト

**前提条件**: research.md が完成

1. **機能仕様からエンティティを抽出** → `data-model.md`:
   - エンティティ名、フィールド、関係
   - 要件からの検証ルール
   - 該当する場合は状態遷移

2. **機能要件から API コントラクトを生成**:
   - 各ユーザーアクション → エンドポイント
   - 標準 REST/GraphQL パターンを使用
   - OpenAPI/GraphQL スキーマを `/contracts/` に出力

3. **エージェントコンテキストを更新**:
   - `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` を実行
   - スクリプトはどの AI エージェントが使用中かを検出
   - 適切なエージェント固有コンテキストファイルを更新
   - 現在の計画から新しいテクノロジーのみを追加

**出力**: data-model.md、/contracts/*、quickstart.md、エージェント固有ファイル

## 主要ルール

- 絶対パスを使用
- ゲート障害または未解決の明確化でエラーが発生

````
