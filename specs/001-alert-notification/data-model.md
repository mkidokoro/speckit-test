# Data Model Design: 火災・防犯警報通知システム

**Branch**: `001-alert-notification` | **Date**: 2026-01-31 | **Phase**: 1 - Design

## Overview

本ドキュメントは、警報通知システムのデータモデル・スキーマ・エンティティ関係を定義します。

---

## Entity Diagram

```
┌─────────────┐
│   User      │
├─────────────┤
│ user_id (PK)│
│ user_type   │◄─────┐
│ pin_hash    │      │ 1:N (User creates logs)
│ created_at  │      │
│ last_login  │      │
└─────────────┘      │
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌─────────────┐  ┌─────────────┐  ┌─────────────────┐
│   Alert     │  │ VisitorCall │  │   AuditLog      │
├─────────────┤  ├─────────────┤  ├─────────────────┤
│ alert_id(PK)│  │ call_id(PK) │  │ log_id(PK)      │
│ alert_type  │  │ timestamp   │  │ timestamp       │
│ timestamp   │  │ visitor_id  │  │ event_type      │
│ sensor_id   │  │ call_status │  │ user_id (FK)    │
│ priority    │◄─┤ audio_stream│  │ alert_id (FK)   │
│ state       │  └─────────────┘  │ call_id (FK)    │
│ ...         │                   │ details (JSON)  │
└─────────────┘                   └─────────────────┘

┌──────────────────┐
│  DisplayState    │
├──────────────────┤
│ state_id (PK)    │
│ state_type       │
│ active_alert_id  │ ──► Alert
│ on_duration      │
│ last_updated     │
└──────────────────┘

┌──────────────────┐
│    Settings      │
├──────────────────┤
│ key (PK)         │
│ value            │
│ updated_at       │
└──────────────────┘
```

---

## Core Entities

### 1. Alert（警報）

**Purpose**: 火災・防犯センサーから受信した警報情報を管理

**Attributes**:
```python
@dataclass
class Alert:
    alert_id: str              # UUID: "alert_20260131_001"
    alert_type: AlertType      # Enum: FIRE | SECURITY
    timestamp: int             # Unix timestamp (警報発生時刻)
    sensor_id: str             # "fire_sensor_1" | "security_sensor_2"
    priority_level: int        # 1=FIRE(最高), 2=SECURITY, 3=CALL
    display_color: str         # '#FF0000' (FIRE) | '#FFD700' (SECURITY)
    sound_pattern: str         # 'pattern_fire' | 'pattern_security'
    state: AlertState          # Enum: PENDING | DISPLAYED | CLEARED
    duration_seconds: int      # 警報表示持続時間（秒）
    created_at: int            # ログレコード作成時刻
    cleared_at: int | None     # クリア時刻（自動 or ユーザー操作）
    sensor_alive: bool         # True=ハートビート受信済み, False=故障状態
```

**Lifecycle**:
```
PENDING (キューで待機)
  ↓
DISPLAYED (画面表示中)
  ↓
CLEARED (センサー信号 or ユーザー操作で解除)
```

**Business Rules**:
- 同一 alert_id の警報は重複表示しない（FR-009：重複判定）
- 火災警報は必ず優先表示（FR-004）
- ネットワーク遮断時もローカルキャッシュで表示継続（FR-009）

---

### 2. User（ユーザー）

**Purpose**: 住人・ゲストの認証・権限管理

**Attributes**:
```python
@dataclass
class User:
    user_id: str               # "resident_1" | "guest_1"
    user_type: UserType        # Enum: RESIDENT | GUEST
    pin_hash: str | None       # bcrypt hash (RESIDENT のみ)
    display_name: str          # "山田太郎"
    created_at: int            # ユーザー登録日時
    last_login: int | None     # 最終ログイン日時
    is_active: bool            # True=有効, False=無効
    permissions: Dict[str, bool]  # 権限マップ
```

**Permissions** (FR-014, FR-015):
```python
RESIDENT_PERMISSIONS = {
    'view_alerts': True,
    'mute_sound': True,
    'adjust_volume': True,
    'clear_alert': True,
    'access_logs': True,
    'change_settings': True,
    'manage_users': True,
    'clear_logs': True,  # PIN保護
    'factory_reset': True,  # PIN保護
}

GUEST_PERMISSIONS = {
    'view_alerts': True,
    'mute_sound': False,
    'adjust_volume': False,
    'clear_alert': False,
    'access_logs': False,
    'change_settings': False,
}
```

---

### 3. VisitorCall（来客通話）

**Purpose**: インターフォン・来客通話の状態管理

**Attributes**:
```python
@dataclass
class VisitorCall:
    call_id: str               # UUID: "call_20260131_001"
    timestamp: int             # 呼び出し開始時刻
    visitor_id: str            # "visitor_camera_1"
    call_status: CallStatus    # Enum: RINGING | CONNECTED | HELD | ENDED
    audio_stream_url: str      # RTP/RTSP ストリーム URL
    video_stream_url: str      # ビデオストリーム URL (オプション)
    created_at: int
    ended_at: int | None
    duration_seconds: int      # 通話時間（秒）
    was_answered: bool         # True=応答, False=タイムアウト
```

**Call State Transitions**:
```
RINGING (30秒タイムアウト)
  ↓
[住人が「応答」をタップ]
  ↓
CONNECTED (通話中)
  ↓
[火災警報到着] → HELD (待機)
  ↓
[住人が「終了」をタップ or 警報解除後自動再開]
  ↓
ENDED
```

---

### 4. DisplayState（ディスプレイ状態）

**Purpose**: 画面の現在表示状態を管理

**Attributes**:
```python
@dataclass
class DisplayState:
    state_id: str              # "display_state"
    state_type: StateType      # Enum: NORMAL | FIRE_ALERT | SECURITY_ALERT | CALL
    active_alert_id: str | None  # 現在表示中の alert_id
    on_duration_seconds: int   # ディスプレイ点灯時間（秒）
    pending_alerts_count: int  # 待機中の警報件数（FR-008：カウンター表示）
    brightness_percent: int    # 現在の画面明度 (0-120%)
    last_updated: int
    is_muted: bool             # 警告音消音状態
```

---

### 5. AuditLog（監査ログ）

**Purpose**: 全イベント・操作・警報をログ記録（FR-010）

**Attributes**:
```python
@dataclass
class AuditLog:
    log_id: int                # 自動採番
    timestamp: int             # イベント発生時刻
    event_type: str            # "ALERT_RECEIVED" | "USER_ACTION" | "SYSTEM_ERROR"
    user_id: str | None        # イベント実行ユーザー (ユーザー操作の場合)
    alert_id: str | None       # 関連する alert_id
    call_id: str | None        # 関連する call_id
    details: str               # JSON: event_data
    severity: str              # "INFO" | "WARNING" | "ERROR"
    created_at: int
```

**Event Types**:
```python
EVENT_TYPES = {
    # 警報イベント
    'ALERT_RECEIVED': '火災・防犯センサーから警報受信',
    'ALERT_DISPLAYED': '警報を画面表示',
    'ALERT_CLEARED': '警報クリア（自動 or 手動）',
    'ALERT_MUTED': '警告音消音',
    
    # 通話イベント
    'CALL_INCOMING': '来客通話受信',
    'CALL_ANSWERED': '通話応答',
    'CALL_REJECTED': '通話拒否',
    'CALL_ENDED': '通話終了',
    
    # ユーザー操作
    'USER_LOGIN': 'ユーザーログイン',
    'PIN_CHANGED': 'PIN変更',
    'VOLUME_ADJUSTED': '音量調整',
    'LOG_CLEARED': 'ログ削除',
    'FACTORY_RESET': 'ファクトリーリセット',
    
    # システムイベント
    'SENSOR_FAULT': 'センサー故障検知',
    'SENSOR_RECOVERY': 'センサー復帰',
    'NETWORK_OFFLINE': 'ネットワークオフライン',
    'NETWORK_ONLINE': 'ネットワーク復帰',
    'SYSTEM_RECOVERY': 'システム復旧',
    'SYSTEM_ERROR': 'システムエラー',
}
```

---

### 6. Settings（設定）

**Purpose**: ユーザー設定・システム設定を保管

**Key-Value Schema**:
```python
SETTINGS = {
    # 音量設定
    'volume_fire': 85,           # dB (固定, FR-006)
    'volume_security': 80,       # dB (ユーザー調整可)
    'volume_call': 70,           # dB (ユーザー調整可)
    
    # 明度設定
    'brightness_auto_adapt': True,   # 周囲光自動適応
    'brightness_normal': 80,         # 通常時 (500-1000ルクス)
    'brightness_dark': 120,          # 暗い環境 (<100ルクス)
    
    # ログ設定
    'log_retention_days': 90,
    'log_storage_limit_percent': 10,
    
    # センサー監視
    'heartbeat_interval_seconds': 60,
    'heartbeat_timeout_seconds': 300,  # 5分
    
    # 表示言語・タイムゾーン
    'language': 'ja',
    'timezone': 'Asia/Tokyo',
    
    # 初期化フラグ
    'is_first_setup_done': False,
}
```

---

## Database Schema (SQLite)

### DDL (Data Definition Language)

```sql
-- Alerts テーブル
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('FIRE', 'SECURITY')),
    timestamp INTEGER NOT NULL,
    sensor_id TEXT NOT NULL,
    priority_level INTEGER NOT NULL,
    display_color TEXT,
    sound_pattern TEXT,
    state TEXT NOT NULL DEFAULT 'PENDING' CHECK(state IN ('PENDING', 'DISPLAYED', 'CLEARED')),
    duration_seconds INTEGER DEFAULT 0,
    sensor_alive BOOLEAN DEFAULT 1,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    cleared_at INTEGER,
    CONSTRAINT fk_sensor FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
);
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_state ON alerts(state);
CREATE INDEX idx_alerts_priority ON alerts(priority_level);

-- Users テーブル
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    user_type TEXT NOT NULL CHECK(user_type IN ('RESIDENT', 'GUEST')),
    pin_hash TEXT,
    display_name TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    last_login INTEGER,
    is_active BOOLEAN DEFAULT 1
);

-- VisitorCalls テーブル
CREATE TABLE visitor_calls (
    call_id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    visitor_id TEXT NOT NULL,
    call_status TEXT NOT NULL CHECK(call_status IN ('RINGING', 'CONNECTED', 'HELD', 'ENDED')),
    audio_stream_url TEXT,
    video_stream_url TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    ended_at INTEGER,
    duration_seconds INTEGER DEFAULT 0,
    was_answered BOOLEAN DEFAULT 0
);
CREATE INDEX idx_calls_timestamp ON visitor_calls(timestamp DESC);

-- DisplayState テーブル
CREATE TABLE display_state (
    state_id TEXT PRIMARY KEY DEFAULT 'display_state',
    state_type TEXT NOT NULL CHECK(state_type IN ('NORMAL', 'FIRE_ALERT', 'SECURITY_ALERT', 'CALL')),
    active_alert_id TEXT,
    on_duration_seconds INTEGER DEFAULT 0,
    pending_alerts_count INTEGER DEFAULT 0,
    brightness_percent INTEGER DEFAULT 80,
    last_updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    is_muted BOOLEAN DEFAULT 0,
    FOREIGN KEY (active_alert_id) REFERENCES alerts(alert_id)
);

-- AuditLogs テーブル
CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    user_id TEXT,
    alert_id TEXT,
    call_id TEXT,
    details TEXT,
    severity TEXT DEFAULT 'INFO' CHECK(severity IN ('INFO', 'WARNING', 'ERROR')),
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (call_id) REFERENCES visitor_calls(call_id)
);
CREATE INDEX idx_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_logs_user ON audit_logs(user_id);

-- Settings テーブル
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Sensors テーブル (マスタ)
CREATE TABLE sensors (
    sensor_id TEXT PRIMARY KEY,
    sensor_type TEXT CHECK(sensor_type IN ('FIRE', 'SECURITY')),
    location TEXT,
    last_heartbeat INTEGER,
    is_alive BOOLEAN DEFAULT 1,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
```

---

## Data Persistence Strategy (FR-012)

**Pending Alert Persistence**:
```python
# システムクラッシュ時、待機中警報をストレージに自動保存
async def persist_pending_alerts(alerts: List[Alert]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for alert in alerts:
        if alert.state == AlertState.PENDING:
            cursor.execute("""
                INSERT INTO alerts (
                    alert_id, alert_type, timestamp, sensor_id, 
                    priority_level, state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id, alert.alert_type, alert.timestamp,
                alert.sensor_id, alert.priority_level, 'PENDING',
                int(time.time())
            ))
    conn.commit()

# 復帰時、永続化された警報を復元
async def recover_pending_alerts() -> List[Alert]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE state = 'PENDING' ORDER BY timestamp")
    rows = cursor.fetchall()
    
    alerts = [Alert.from_row(row) for row in rows]
    # [システム復旧] インジケーター表示（FR-012）
    return alerts
```

---

## Validation Rules

### Alert Validation
```python
class AlertValidator:
    @staticmethod
    def validate(alert: Alert) -> bool:
        # 必須フィールド
        assert alert.alert_id, "alert_id required"
        assert alert.alert_type in ['FIRE', 'SECURITY'], "invalid alert_type"
        assert alert.priority_level in [1, 2, 3], "invalid priority"
        
        # FIRE 警報は優先度 1 必須
        if alert.alert_type == 'FIRE':
            assert alert.priority_level == 1, "FIRE must have priority=1"
            assert alert.display_color == '#FF0000', "FIRE must be red"
        
        # 重複判定（1分以内の同一警報は統合）
        if existing := Alert.find_by_id(alert.alert_id):
            if abs(alert.timestamp - existing.timestamp) < 60:
                return False  # 重複
        
        return True
```

---

## Relationships

### Alert → User (監査ログ経由)
- 1 Alert : N AuditLog (1つの警報に複数のログレコード)

### User → AuditLog
- 1 User : N AuditLog (1人のユーザーの操作複数)

### Alert → DisplayState
- 1 Alert : 0..1 DisplayState (現在表示中の警報)

### VisitorCall → DisplayState
- 1 VisitorCall : 0..1 DisplayState (現在表示中の通話)

---

## Data Migration Strategy

Version upgrade 時のマイグレーション:
```python
# migrations/001_initial_schema.py
def up():
    # 初期スキーマ作成
    pass

# migrations/002_add_pending_alerts_persistence.py
def up():
    """Ver 1.1: 永続化機能追加"""
    cursor.execute("ALTER TABLE alerts ADD COLUMN sensor_alive BOOLEAN DEFAULT 1")
    
def down():
    """Rollback"""
    cursor.execute("ALTER TABLE alerts DROP COLUMN sensor_alive")
```

---

## Summary

✅ **Data Model 確定**:
- 6つのコア エンティティ定義
- SQLite スキーマ完全定義
- 永続化戦略確実
- Validation ルール明確
- 関係性マッピング完了

次フェーズ: **Contracts & API Design**
