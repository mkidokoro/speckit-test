# Implementation Plan: 火災・防犯警報通知システム

**Branch**: `001-alert-notification` | **Date**: 2026-01-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-alert-notification/spec.md`

**Status**: Phase 0 - Technical Research & Clarification

## Summary

組込みLinux（Raspberry Pi/Armbian）ベースのインターホン住戸内モニター向けリアルタイム警報通知システム。火災・防犯センサーからMQTT経由で警報を受信し、優先度ベースでUI表示・警告音再生・通話制御を実行。システムは永続化・センサー監視・ユーザー認証・監査ログ・ネットワーク同期を備え、高い信頼性と実時間性を実現する。

## Technical Context

**Language/Version**: Python 3.10+ (組込みLinux親和性、MQTT/非同期処理ライブラリ充実)  
**Primary Dependencies**: 
- MQTT: `paho-mqtt` (センサー通信)
- UI: `GTK+ 3` または `PySimpleGUI` (軽量UI)
- Database: `SQLite` (ログ・警報永続化)
- Async: `asyncio` (非同期イベント処理、リアルタイム警報)
- Audio: `PulseAudio` + `pyaudio` (警告音制御)
- Display: `Pillow` (画像処理、明るさ調整)

**Storage**: SQLite ローカルファイル (ログ・警報履歴・ユーザー設定・永続化警報)  
**Testing**: `pytest`, `pytest-asyncio`, `unittest.mock` (MQTT/UIモック)  
**Target Platform**: Linux ARM (Raspberry Pi 4/5 相当, Armbian)  
**Project Type**: 組込みデスクトップアプリケーション  
**Performance Goals**: 
- 警報受信→画面表示: **100msec以下** (FR-001, FR-002)
- 警告音再生開始: **500msec以下** (FR-006)
- ディスプレイ明度調整: **200msec以内** (NFR)
- ハートビート監視: **60秒間隔** (NFR)

**Constraints**: 
- メモリ: <150MB実行時 (起動時100MB未満)
- ストレージ: ログ容量ストレージ10%上限
- CPU: 通常時5%、最大30%
- ネットワーク: オフラインで完全動作 (ローカルキャッシュ利用)
- リアルタイム性: 非ブロッキング非同期処理、割り込みベース警報処理

**Scale/Scope**: 
- 単一住戸内モニター (マルチテナント非対応)
- UI画面: 約5～7画面 (通常待機、火災警報、防犯警報、来客通話、設定、ログ閲覧)
- 警報キャッシュ: 最大100件待機 (メモリ効率)
- ログ保有: 90日間、容量10%上限自動削除

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle 1: Memory Efficiency** (メモリ効率性)
- ✅ 実行時150MB制限、起動100MB未満設計
- ✅ SQLiteログローテーション (90日、10%容量上限自動削除)
- ✅ 警報キャッシュ最大100件メモリ制限
- Status: **PASS** (明確な制約・実装パターン定義済み)

**Principle 2: Hardware Independence** (ハードウェア独立性)
- ✅ Raspberry Pi/Armbian対応 (汎用Linux ARM)
- ✅ 外部ハードウェア依存は MQTT/I2C標準プロトコル
- ✅ UIフォールバック (GTK+→PySimpleGUI)
- ✅ オーディオフォールバック (PulseAudio→ALSA)
- Status: **PASS** (多くのハードウェアで実行可能な設計)

**Principle 3: Test-First Development** (テスト優先開発)
- ✅ pytest + pytest-asyncio + unittest.mock採用
- ✅ 単体/統合/e2eテスト戦略定義済み (quickstart.md参照)
- ✅ MQTT/UIはモック可能設計 (依存性注入)
- ✅ データ永続化もsqlite-in-memory テスト用
- Status: **PASS** (全層テスト可能な設計)

**Principle 4: Security & Privacy** (セキュリティ・プライバシー)
- ✅ PIN暗号化 (bcrypt rounds=12)
- ✅ 監査ログローカル保存のみ (外部送信無し)
- ✅ Rate limiting (3回失敗で1分ロック)
- ✅ ネットワーク: MQTTのみ (認証トークン検証予定)
- ✅ データ保有: ローカルみ、オフラインで完全動作
- Status: **PASS** (プライバシー第一、ローカルキャッシュ戦略)

**Principle 5: Scalability & Maintainability** (拡張性・保守性)
- ✅ モジュラー設計 (core/models/services/ui層分離)
- ✅ イベント駆動アーキテクチャ (MQTT pub/sub + asyncio)
- ✅ DI + 単体テスト → 容易な機能追加
- ✅ SQLiteスキーマ版管理 (マイグレーション対応)
- Status: **PASS** (新機能追加・レイヤー追加容易な構造)

**Overall**: ✅ **CONSTITUTION GATES PASSED** - Phase 0研究開始承認

## Project Structure

### Documentation (this feature)

```text
specs/001-alert-notification/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technical research (8 topics)
├── data-model.md        # Phase 1: Entity definitions + SQLite DDL
├── quickstart.md        # Phase 1: Installation/setup/testing guide
├── checklists/
│   └── requirements.md  # Requirements tracking
├── quickstart.md        # Phase 1: Installation/setup/testing guide
├── contracts/           # Phase 1: MQTT/UI contracts
│   ├── mqtt-topics.json     # MQTT topic schema
│   ├── ui-screens.md        # UI screen specifications
│   └── api-events.json      # Event type definitions
└── tasks.md             # Phase 2: Implementation tasks (未作成)
```

### Source Code (repository root)

**Selected Structure**: Single Project Pattern (組込みアプリケーション)

```text
alert-notification-system/
├── src/
│   ├── __init__.py
│   ├── main.py              # アプリケーションエントリー
│   ├── core/
│   │   ├── __init__.py
│   │   ├── asyncio_manager.py       # イベントループ・優先度キュー管理
│   │   ├── mqtt_broker.py           # MQTT接続・購読・メッセージ処理
│   │   ├── priority_queue.py        # 警報優先度キュー
│   │   └── state_machine.py         # システム状態機械
│   ├── models/
│   │   ├── __init__.py
│   │   ├── entities.py              # SQLAlchemy ORM: Alert, User, VisitorCall等
│   │   ├── database.py              # SQLiteコネクションプール、WAL設定
│   │   ├── validators.py            # 入力検証 (PIN, 警報タイプ等)
│   │   └── enums.py                 # AlertType, AlertState等
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alert_processor.py       # 警報処理・優先度判定・コマンド生成
│   │   ├── audio_service.py         # 警告音生成・再生 (pyaudio)
│   │   ├── display_service.py       # 画面制御・明度調整 (Pillow, I2C)
│   │   ├── auth_service.py          # PIN認証・レート制限 (bcrypt)
│   │   ├── sensor_monitor.py        # ハートビート監視・接続状態
│   │   ├── persistence_service.py   # ログ永続化・ローテーション
│   │   ├── network_sync.py          # ネットワーク状態同期
│   │   └── visitor_call_handler.py  # 来客通話管理
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py           # メインウィンドウ (GTK+ / PySimpleGUI)
│       ├── screens/
│       │   ├── __init__.py
│       │   ├── normal_screen.py     # 待機画面
│       │   ├── fire_alert_screen.py # 火災警報画面
│       │   ├── security_alert_screen.py  # 防犯警報画面
│       │   ├── visitor_call_screen.py    # 来客通話画面
│       │   ├── settings_screen.py   # 設定画面
│       │   └── logs_screen.py       # ログ画面
│       ├── components/
│       │   ├── __init__.py
│       │   ├── alert_banner.py      # 警報バナー
│       │   ├── visitor_panel.py     # 来客パネル
│       │   └── action_buttons.py    # アクションボタン
│       └── accessibility.py         # WCAG AAA: コントラスト比7:1, フォント18pt
├── config/
│   ├── __init__.py
│   ├── default.yaml         # デフォルト設定
│   ├── logging.conf         # Pythonログ設定
│   └── systemd/
│       └── alert-notification.service  # systemdサービス定義
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest共有フィクスチャ (MQTT/DB/UIモック)
│   ├── unit/
│   │   ├── test_alert_processor.py      # 警報処理ロジック
│   │   ├── test_audio_service.py        # 警告音生成
│   │   ├── test_auth_service.py         # PIN認証・bcrypt
│   │   ├── test_persistence_service.py  # ログ永続化・ローテーション
│   │   └── test_validators.py           # 入力検証
│   ├── integration/
│   │   ├── test_mqtt_flow.py       # MQTT受信→警報処理フロー
│   │   ├── test_ui_integration.py   # UI更新・イベントフロー
│   │   ├── test_database_operations.py  # DB操作・トランザクション
│   │   └── test_end_to_end.py      # 完全フロー (火災警報受信→表示→音声)
│   └── e2e/
│       ├── test_fire_alert_scenario.py
│       ├── test_security_alert_scenario.py
│       └── test_visitor_call_scenario.py
├── docs/
│   ├── architecture.md      # システムアーキテクチャ
│   ├── deployment.md        # デプロイ手順
│   └── troubleshooting.md   # トラブルシューティング
├── requirements.txt         # Python依存関係
├── setup.py                 # インストール定義
├── Dockerfile               # Docker構築ファイル
├── docker-compose.yml       # MQTT ブローカー + アプリ
├── pytest.ini               # pytest設定
├── .flake8                  # flake8リント設定
├── .github/
│   └── workflows/
│       ├── test.yml         # CI: ユニット・統合テスト
│       └── lint.yml         # CI: flake8, isort
└── README.md                # プロジェクト概要
```

**Structure Decision**: 組込みデスクトップアプリケーション向けの単一プロジェクト構造を採用。core/(非同期/MQTT)、models/(ORM/検証)、services/(ビジネスロジック)、ui/(UI層)の責任分離により、テスト容易性・保守性を実現。

## Phase 0: Technical Research Tasks

**Output**: `research.md` (8個のテクニカルトピック調査)

| Task ID | Topic | Key Questions | Deliverable | Assigned To |
|---------|-------|--------------|-------------|------------|
| RES-001 | MQTT非同期パターン | paho-mqtt async統合、ハートビート、再接続 | MQTT実装パターン、ライブラリ比較 | - |
| RES-002 | UI フレームワーク選択 | GTK+/PySimpleGUI比較、Armbian対応、軽量性 | フレームワーク選択マトリックス、サンプルコード | - |
| RES-003 | SQLiteチューニング | WAL、PRAGMA最適化、ログローテーション | SQLiteベストプラクティス、DDL案 | - |
| RES-004 | 非同期設計パターン | asyncio + PriorityQueue、タイムアウト処理 | 非同期設計パターン、割り込み実装例 | - |
| RES-005 | オーディオ管理 | pyaudio波形生成、dB→線形変換、音量制御 | 警告音実装パターン、テスト戦略 | - |
| RES-006 | ディスプレイ制御 | Pillow + I2Cセンサー、ガンマ補正、自動明度調整 | 画面制御実装、アクセシビリティ対応 | - |
| RES-007 | PIN認証・レート制限 | bcrypt round数、失敗追跡、ロック機構 | 認証実装パターン、セキュリティ考慮 | - |
| RES-008 | Linux ARM最適化 | メモリ監視、CPU制御、リソース制限 | 最適化チェックリスト、パフォーマンス測定 | - |

**Status**: ✅ **完了** - research.md に8個のトピック完全記述

## Phase 1: Design & Contracts

**Prerequisites**: research.md ✅ 完了

### 1.1 Data Model Design

**Output**: `data-model.md` (SQLiteスキーマ + 6エンティティ定義)

| Entity | Fields | Relationships | Lifecycle |
|--------|--------|---------------|-----------|
| Alert | alert_id, alert_type, timestamp, priority_level, state | - | PENDING→DISPLAYED→CLEARED (可逆) |
| User | user_id, user_type, pin_hash, permissions, created_at | N:M AlertLog | Create→Update→Delete |
| VisitorCall | call_id, call_status, audio_stream_url, started_at, ended_at | N:1 Alert | RINGING→CONNECTED→HELD→ENDED |
| DisplayState | state_id, state_type, active_alert_id, brightness, pending_count | 1:N Alert | Real-time sync |
| AuditLog | log_id, event_type, user_id, alert_id, severity, details (JSON) | N:1 User, N:1 Alert | Immutable append |
| Settings | key, value, last_modified | - | Key-value config |

**Status**: ✅ **完了** - data-model.md にDDL + 検証ルール記述

### 1.2 API/MQTT Contracts

**Output**: `contracts/` フォルダ

| Contract | Format | Topics/Endpoints | Status |
|----------|--------|------------------|--------|
| mqtt-topics.json | JSON | sensor/*, visitor/*, monitor/* | 未作成 |
| ui-screens.md | Markdown | 5-7画面定義、UI遷移図 | 未作成 |
| api-events.json | JSON | Event payloads、タイムスタンプ | 未作成 |

**Status**: ⏳ **Phase 1.3 - 作成予定**

### 1.3 Quick Start Guide

**Output**: `quickstart.md` (インストール～デプロイ)

**Sections**:
- Prerequisites (Python 3.10+, GTK+ dev, systemd)
- Installation (pip, venv, Dockerfile)
- Initialization (MQTT ブローカー設定、初期DB作成)
- Startup (手動実行、systemdサービス)
- Testing (pytest, MQTT emit シミュレーション)
- Configuration Reference
- Troubleshooting

**Status**: ✅ **完了** - quickstart.md に実装ステップ記述

### 1.4 Agent Context Update

**Action**: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`

**Status**: ⏳ **Phase 1 完了後実行予定**

## Phase 2: Tasks Generation

**Output**: `tasks.md` (Sprint分割、実装タスク 50～100個)

**Scope**: 未実施 (Phase 1 完了後実行)

### Timeline

- **Phase 0** (Research): ✅ 完了
- **Phase 1** (Design): ✅ data-model.md/quickstart.md 完了 → ⏳ contracts/ 作成中
- **Phase 2** (Tasks): ⏹️ Phase 1 完了後実行

## Next Actions

1. **contracts/ フォルダ作成**: MQTT topics schema, UI contracts, API events定義
2. **Agent context更新**: update-agent-context.ps1 実行
3. **Phase 2 タスク生成**: tasks.md へ実装タスクリスト 50～100個
4. **ソースコード初期化**: src/ フォルダ構造とスケルトンコード生成
