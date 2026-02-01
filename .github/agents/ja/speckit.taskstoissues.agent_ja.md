````chatagent
---
description: 既存のタスクを、利用可能な設計成果物に基づいて、アクション可能で依存関係が順序付けられた GitHub イシューに変換します。
tools: ['github/github-mcp-server/issue_write']
---

## ユーザー入力

```text
$ARGUMENTS
```

ユーザー入力を考慮してください（空の場合は無視）。

## アウトライン

1. リポジトリルートから `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` を実行し、FEATURE_DIR と AVAILABLE_DOCS リストを解析します。すべてのパスは絶対パスである必要があります。

2. 実行されたスクリプトから、**tasks** へのパスを抽出します。

3. 以下を実行して Git リモートを取得します：

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> リモートが GitHub URL である場合のみ次のステップに進んでください

4. リスト内の各タスクについて、GitHub MCP サーバーを使用して、Git リモートに相当するリポジトリに新しいイシューを作成します。

> [!CAUTION]
> リモート URL と一致しないリポジトリにはイシューを作成しないでください

````
