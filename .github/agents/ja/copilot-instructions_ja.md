# GitHub Copilot 開発ガイドライン

## 概要

このドキュメントは、GitHub Copilot を使用して speckit プロジェクトの開発を加速するためのガイドラインです。

## 環境要件

- Python 3.10 以上
- MQTT 対応の組み込み Linux システム（Raspberry Pi 4/5、Armbian など）
- 必要な Python パッケージ（requirements.txt 参照）

## 推奨される使用方法

### 1. コード生成

Copilot を使用してコードを生成する際は、以下を指定してください：

- **モジュール**: 作成するモジュールの目的
- **関数シグネチャ**: 入出力の型ヒント
- **ドメイン**: MQTT 通信、優先度キュー、非同期処理など

例：
```
# 非同期で MQTT メッセージを処理する関数
# パラメータ: topic (str), payload (bytes)
# 戻り値: Coroutine
async def process_mqtt_message(topic: str, payload: bytes) -> dict:
```

### 2. テスト生成

pytest + pytest-asyncio を使用してテストを生成してください：

```python
@pytest.mark.asyncio
async def test_alert_processor():
    # テスト実装
    pass
```

### 3. ドキュメンテーション

日本語でコメントを記述し、以下の形式を使用してください：

```python
# 火災警報を処理する
# 優先度: 最高（1）
def handle_fire_alert(alert: AlertMessage) -> None:
    """火災警報メッセージを処理します"""
    pass
```

## MQTT 関連の注意点

- QoS レベル: 最小 QoS 1 以上を使用
- トピック: `alert/#` パターンで整理
- ペイロード: JSON 形式で統一

## 非同期処理パターン

asyncio.PriorityQueue を使用して、以下の優先度で処理してください：

1. FIRE（火災警報）= 優先度 1
2. SECURITY（防犯警報）= 優先度 2
3. CALL（来客通話）= 優先度 3

## セキュリティ

- PIN コード検証には bcrypt を使用（rounds=12）
- ネットワークコマンドは暗号化して送信
- ローカル設定ファイルは適切なパーミッションで保護

## パフォーマンス

- SQLite は WAL モードで実行
- 画面の明るさ調整は I2C 光センサーで自動化
- ログは 90 日保持、ストレージの 10% 以下に制限

## トラブルシューティング

### import エラー

パッケージのインポートが失敗する場合は、絶対パスを使用してください：

```python
from src.models.enums import AlertType
from src.core.asyncio_manager import AsyncIOManager
```

### 非同期実行エラー

pytest を実行する前に `pytest.ini` の設定を確認してください：

```ini
[pytest]
asyncio_mode = auto
```

## 参考資料

- plan.md: 実装計画
- tasks.md: タスク一覧（165 タスク）
- data-model.md: データモデル定義
