# Technical Research: 火災・防犯警報通知システム

**Branch**: `001-alert-notification` | **Date**: 2026-01-31 | **Phase**: 0 - Research

## Overview

本ドキュメントは `plan.md` の Technical Context に記載された 8 つのリサーチタスクの調査結果を記載します。

---

## 1. MQTT実装パターン

**Decision**: `paho-mqtt` + `asyncio` ハイブリッド非同期モデル

**Rationale**:
- `paho-mqtt` の `Client()` は同期API、`loop_start()` でバックグラウンド実行可能
- ハートビート監視（60秒間隔）・オフライン復帰を独立したasyncioタスクで管理
- MQTT接続喪失時はローカルキャッシュ自動切り替え（FR-009）

**Implementation Pattern**:
```python
# mqtt_handler.py
import paho.mqtt.client as mqtt
import asyncio

class MQTTHandler:
    def __init__(self, broker_host, broker_port=1883):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.broker_host = broker_host
        self.heartbeat_timeout = {}  # {sensor_id: timestamp}
        
    async def connect_async(self):
        self.client.connect_async(self.broker_host, 1883, keepalive=60)
        self.client.loop_start()
        await asyncio.sleep(1)  # 接続確立待ち
        
    async def monitor_heartbeat(self, sensor_id, timeout=300):
        """60秒ごとにハートビート監視、5分タイムアウト検知"""
        while True:
            await asyncio.sleep(60)
            last_beat = self.heartbeat_timeout.get(sensor_id)
            if last_beat and (time.time() - last_beat) > timeout:
                # FR-013: センサー故障警告
                await self.emit_sensor_fault_warning(sensor_id)
```

**Alternatives Rejected**:
- `asyncio-mqtt`: 非同期ネイティブだが、外部ブローカー連携が複雑
- 独自実装: 開発時間・テストコストが大きい

---

## 2. UI Framework: PySimpleGUI vs GTK+

**Decision**: **GTK+ 3** を推奨、PySimpleGUI をフォールバック

| 評価項目 | GTK+ 3 | PySimpleGUI |
|---|---|---|
| **軽量性** | 中 (システム共有ライブラリ) | ◎ (Python純粋) |
| **Linux ARM対応** | ◎ (Debian/Armbian標準) | ○ (依存関係多) |
| **リアルタイム性** | ◎ (ネイティブ、低遅延) | ◎ (Tk ベース) |
| **テスト可能性** | ◎ (GTK+ テストツール) | ○ (モック必須) |
| **開発速度** | ○ (学習曲線あり) | ◎ (素早いプロトタイプ) |
| **カスタマイズ** | ◎ (CSS/テーマ対応) | ○ (限定的) |

**Rationale**:
- GTK+ は Raspberry Pi/Armbian で標準搭載、追加インストール不要
- PyGObject (Python-GTK バインディング) でPython統合可能
- CSS スタイル対応で、WCAG AAA コントラスト比 7:1 実装容易

**Implementation Pattern** (GTK+):
```python
# ui/screens/fire_alert_screen.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class FireAlertScreen(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_default_size(800, 480)
        
        # CSS: コントラスト比 7:1
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            #fire_alert {
                background-color: #FF0000;
                color: #FFFFFF;
                font-size: 72px;
                font-weight: bold;
            }
        """)
        context = self.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
```

**Fallback**: PySimpleGUI でプロトタイプ後、GTK+ への移行は機械的に実施可能

---

## 3. SQLite設計・最適化

**Decision**: SQLite + WAL (Write-Ahead Logging) + 定期VACUUM

**Schema Design**:
```sql
-- alerts テーブル
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    alert_type TEXT NOT NULL,  -- 'FIRE' or 'SECURITY'
    timestamp INTEGER NOT NULL,  -- Unix timestamp
    sensor_id TEXT NOT NULL,
    priority_level INTEGER,  -- 1=FIRE(最高), 2=SECURITY, 3=CALL
    display_color TEXT,  -- '#FF0000' for FIRE
    sound_pattern TEXT,
    state TEXT DEFAULT 'PENDING',  -- PENDING/DISPLAYED/CLEARED
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_state ON alerts(state);

-- audit_logs テーブル
CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    event_type TEXT,  -- 'ALERT_RECEIVED', 'ALERT_DISPLAYED', 'USER_ACTION', etc.
    user_id TEXT,
    alert_id TEXT,
    details TEXT,  -- JSON
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
CREATE INDEX idx_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_logs_event_type ON audit_logs(event_type);

-- users テーブル
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    user_type TEXT NOT NULL,  -- 'RESIDENT' or 'GUEST'
    pin_hash TEXT,  -- bcrypt hash (RESIDENT only)
    created_at INTEGER
);

-- settings テーブル
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at INTEGER
);
```

**Optimization PRAGMA**:
```python
# storage_service.py
def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # WAL mode: 書き込みパフォーマンス向上 (レイテンシ↓)
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # キャッシュサイズ: 2000 ページ (= 8MB @ 4KB/page)
    cursor.execute("PRAGMA cache_size=2000")
    
    # 同期レベル: NORMAL (パフォーマンス↑, 安全性-低)
    cursor.execute("PRAGMA synchronous=NORMAL")
    
    # 自動VACUUM: 1000 ページ削除時にVACUUM実行
    cursor.execute("PRAGMA auto_vacuum=INCREMENTAL")
    cursor.execute("PRAGMA incremental_vacuum(1000)")
```

**Log Retention Strategy**:
```python
# storage_service.py - 90日ごとのクリーンアップ
async def cleanup_old_logs(db_path, days=90):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 90日以前のログを削除
    cutoff_timestamp = int(time.time()) - (days * 86400)
    cursor.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff_timestamp,))
    
    # ストレージ10%チェック
    storage_used = os.path.getsize(db_path)
    storage_limit = os.path.getsize("/") * 0.1  # ファイルシステムの10%
    if storage_used > storage_limit:
        cursor.execute("DELETE FROM audit_logs ORDER BY timestamp ASC LIMIT 1000")
    
    cursor.execute("VACUUM")
    conn.commit()
```

**Alternatives Rejected**:
- PostgreSQL: ARM環境でのセットアップ複雑、メモリ使用量多い
- JSON Files: トランザクション・インデックス機能なし

---

## 4. 非同期設計・優先度キューイング

**Decision**: `asyncio` + カスタム `PriorityQueue`

**Architecture**:
```python
# core/alert_queue.py
import asyncio
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class AlertTask:
    priority: int  # 1=FIRE(最高), 2=SECURITY, 3=CALL
    timestamp: float = field(compare=False)
    alert: Any = field(compare=False)

class AlertQueue:
    def __init__(self, max_pending=100):
        self.queue = asyncio.PriorityQueue(maxsize=max_pending)
        self.handlers = {}  # {priority: handler_coro}
        
    async def enqueue(self, alert, priority):
        """警報をキューに追加（FR-004優先度処理）"""
        task = AlertTask(priority, time.time(), alert)
        try:
            self.queue.put_nowait(task)
        except asyncio.QueueFull:
            # キュー満杯時は最低優先度のアイテムを削除
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(task)
            except:
                pass
    
    async def process_queue(self):
        """優先度順に警報を処理"""
        while True:
            task = await self.queue.get()
            
            # 割り込み処理: 高優先度警報が到着したら現在の処理中断
            handler = self.handlers.get(task.priority)
            if handler:
                await handler(task.alert)
            
            self.queue.task_done()

# main.py
async def main():
    alert_queue = AlertQueue()
    
    # 各優先度のハンドラ登録
    alert_queue.handlers[1] = handle_fire_alert
    alert_queue.handlers[2] = handle_security_alert
    alert_queue.handlers[3] = handle_visitor_call
    
    # MQTT受信タスク
    mqtt_task = asyncio.create_task(mqtt_handler.listen_for_alerts())
    
    # キュー処理タスク
    queue_task = asyncio.create_task(alert_queue.process_queue())
    
    # ハートビート監視タスク
    heartbeat_task = asyncio.create_task(mqtt_handler.monitor_heartbeat('fire_sensor', timeout=300))
    
    await asyncio.gather(mqtt_task, queue_task, heartbeat_task)
```

**Interrupt Pattern**:
```python
# 火災警報受信時、防犯警報の処理を中断
async def handle_alert_interrupt(queue, priority):
    while True:
        task = await queue.queue.get()
        if task.priority < priority:  # より高優先度の警報が到着
            # 現在の処理をキャンセル
            current_task = asyncio.current_task()
            current_task.cancel()
            # より高優先度の処理へ
        await queue.process_queue()
```

---

## 5. PulseAudio/pyaudio 音声制御

**Decision**: `pyaudio` + `numpy` + `scipy` (波形生成・音量制御)

**Implementation**:
```python
# core/audio_manager.py
import pyaudio
import numpy as np
from scipy import signal
import threading

class AudioManager:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.volume_levels = {
            'FIRE': 85,      # dB (固定、FR-006)
            'SECURITY': 80,  # dB (ユーザー調整可)
            'CALL': 70       # dB (ユーザー調整可)
        }
        
    def _db_to_linear(self, db):
        """dB → リニア変換"""
        return 10 ** (db / 20.0)
    
    async def play_alert_sound(self, sound_type, duration=5):
        """警告音再生（FR-006: 500msec以内に開始）"""
        try:
            # 音声ストリーム初期化
            sample_rate = 44100
            frequency = 1000 if sound_type == 'FIRE' else 800  # Hz
            
            # 波形生成（正弦波 + エンベロープ）
            t = np.linspace(0, duration, int(sample_rate * duration))
            waveform = np.sin(2 * np.pi * frequency * t)
            
            # エンベロープ (attack 100ms, decay 100ms)
            envelope = signal.windows.tukey(len(t), 0.1)
            waveform = waveform * envelope
            
            # 音量調整（dB → リニア）
            volume_linear = self._db_to_linear(self.volume_levels[sound_type])
            waveform = waveform * volume_linear
            
            # 16-bit PCM 変換
            audio_data = (waveform * 32767).astype(np.int16).tobytes()
            
            # pyaudio ストリーム生成（FR-003: 500msec以内）
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            # 音声出力
            self.stream.write(audio_data)
            self.is_playing = True
            
        except Exception as e:
            print(f"Audio Error: {e}")
            # FR-006: フォールバック（ビジュアル警告 + 振動）
            await self.fallback_visual_warning()
    
    async def fallback_visual_warning(self):
        """オーディオ失敗時のフォールバック"""
        # 画面点滅 + 振動（対応デバイス）
        pass
    
    def set_volume(self, sound_type, db_level):
        """ユーザー音量調整"""
        if sound_type == 'FIRE':
            return  # 固定、変更不可
        if 60 <= db_level <= 90:
            self.volume_levels[sound_type] = db_level
```

**Alternatives Rejected**:
- `python-sounddevice`: ARM環境での依存関係複雑
- 事前生成音声ファイル: ストレージ制約（10% 上限）

---

## 6. Pillow による環境適応型明度制御

**Decision**: `Pillow` + GPIO (I2C 周囲光センサー) + ガンマ補正

**Implementation**:
```python
# core/display_manager.py
from PIL import Image, ImageDraw, ImageEnhance
import board
import busio
import adafruit_bmp280
import asyncio

class DisplayManager:
    def __init__(self, display_device="/dev/fb0"):
        self.display_device = display_device
        self.brightness = 80  # 初期値 80%
        self.response_time = 0.2  # 200msec以内に調整（NFR）
        
        # I2C 周囲光センサー初期化
        i2c = busio.I2C(board.SCL, board.SDA)
        self.light_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        
    async def monitor_ambient_light(self):
        """周囲光監視・自動明度調整"""
        while True:
            try:
                lux = self.light_sensor.illuminance  # ルクス値取得
                
                # 照度レベル → 画面明度マッピング
                if lux < 100:
                    target_brightness = 120  # 自動増光（最大120%）
                elif lux < 500:
                    target_brightness = 100
                elif lux < 1000:
                    target_brightness = 80  # 標準
                elif lux < 2000:
                    target_brightness = 100
                else:
                    target_brightness = 100  # 反射低減
                
                # スムーズ遷移（応答時間 200msec以内）
                self.brightness = target_brightness
                await self.apply_brightness(self.brightness)
                
            except Exception as e:
                print(f"Light sensor error: {e}")
            
            await asyncio.sleep(1)  # 1秒ごとに監視
    
    async def apply_brightness(self, brightness_percent):
        """ガンマ補正で明度調整"""
        # ガンマ値計算
        gamma = (brightness_percent / 100.0) ** (1.0 / 2.2)
        
        # フレームバッファに適用
        # (実装は GTK+ または PySimpleGUI の API に依存)
        pass
    
    async def render_alert_screen(self, alert_type):
        """警報画面レンダリング（WCAG AAA コントラスト比 7:1）"""
        # 色設定 (色覚異常対応)
        colors = {
            'FIRE': ('#FF0000', '#FFFFFF'),      # 赤色背景、白テキスト
            'SECURITY': ('#FFD700', '#000000'),  # 黄色背景、黒テキスト
        }
        
        fg_color, bg_color = colors.get(alert_type, ('#FFFFFF', '#000000'))
        
        # コントラスト比確認
        contrast_ratio = self._calc_contrast_ratio(fg_color, bg_color)
        assert contrast_ratio >= 7.0, f"WCAG AAA violation: {contrast_ratio}"
    
    def _calc_contrast_ratio(self, color1, color2):
        """WCAG コントラスト比計算"""
        # (実装: sRGB → luminance 変換)
        pass
```

**Sensor Options**:
- BMP280 (温度・気圧・湿度): 一般的な組込みセンサー
- 代替: 抵抗型 CdS セル (アナログ, GPIO ADC)

---

## 7. bcrypt PIN 暗号化・レート制限

**Decision**: `bcrypt` + レート制限カウンター

**Implementation**:
```python
# services/auth_service.py
import bcrypt
import time
from typing import Dict

class AuthService:
    def __init__(self):
        self.pin_hash = None
        self.failed_attempts = {}  # {user_id: (count, timestamp)}
        self.lockout_duration = 60  # 秒
        
    def setup_pin(self, pin: str) -> None:
        """初回 PIN 設定（4～6桁）"""
        if len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
            raise ValueError("PIN must be 4-6 digits")
        
        # bcrypt でハッシュ化（ソルト自動生成）
        self.pin_hash = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt(rounds=12))
    
    def verify_pin(self, user_id: str, pin: str) -> bool:
        """PIN 検証 + レート制限チェック"""
        # レート制限チェック
        if user_id in self.failed_attempts:
            count, last_attempt = self.failed_attempts[user_id]
            if count >= 3:
                if time.time() - last_attempt < self.lockout_duration:
                    return False  # ロック中
                else:
                    # ロック時間終了、カウンターリセット
                    self.failed_attempts[user_id] = (0, time.time())
        
        # PIN 検証
        if not bcrypt.checkpw(pin.encode('utf-8'), self.pin_hash):
            # 失敗カウント増加
            count, _ = self.failed_attempts.get(user_id, (0, time.time()))
            self.failed_attempts[user_id] = (count + 1, time.time())
            return False
        
        # 成功: カウンターリセット
        self.failed_attempts[user_id] = (0, time.time())
        return True
    
    def change_pin(self, user_id: str, old_pin: str, new_pin: str) -> bool:
        """PIN 変更"""
        if not self.verify_pin(user_id, old_pin):
            return False
        self.setup_pin(new_pin)
        return True
```

**Security Best Practices**:
- bcrypt rounds: 12 (standard)
- ハッシュの平文保存禁止
- PIN ハッシュはストレージ暗号化（FDE）で保護
- PIN 入力時はメモリ上で即座にクリア

---

## 8. Linux ARM 最適化

**Decision**: メモリ効率・CPU最適化・リソース監視

**Memory Optimization**:
```python
# src/main.py
import psutil
import gc
import sys

class MemoryManager:
    def __init__(self, max_memory_mb=150):
        self.max_memory = max_memory_mb * 1024 * 1024
        
    async def monitor_memory(self):
        """メモリ使用率監視"""
        while True:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            
            # 起動時: <100MB, 実行時: <150MB
            if mem_info.rss > self.max_memory:
                # 強制ガベージコレクション
                gc.collect()
                
                # 古いログをメモリから削除
                await self.storage_service.flush_cache()
            
            await asyncio.sleep(5)
    
    def _reduce_memory_footprint(self):
        """メモリフットプリント削減"""
        # __slots__ 使用
        # 不要なモジュール preload 廃止
        # キャッシュサイズ制限
        pass
```

**CPU Optimization**:
```python
# スケーラビリティ最適化
# - asyncio 非ブロッキング処理
# - スレッドプール最小化
# - イベント駆動アーキテクチャ

import multiprocessing
import os

# CPU コア数に応じた最適化
cpu_count = os.cpu_count()
# Raspberry Pi: 4 cores, デフォルト asyncio タスク < 4
```

**Resource Monitoring**:
```python
# config/monitoring.py
RESOURCE_LIMITS = {
    'memory': 150,      # MB
    'cpu': 30,          # %
    'disk': 512,        # MB (ログ上限)
    'uptime': 604800    # 秒 (7日連続稼働)
}

async def check_resource_health():
    """リソースヘルスチェック"""
    mem_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=1)
    
    if mem_percent > RESOURCE_LIMITS['memory']:
        logger.warning("Memory exceeded")
    if cpu_percent > RESOURCE_LIMITS['cpu']:
        logger.warning("CPU exceeded")
```

**Alternatives Rejected**:
- Cython コンパイル: 開発複雑度↑、メンテナンスコスト高い
- マルチプロセッシング: Raspberry Pi CPU限定、オーバーヘッド大

---

## Summary: Research Findings

| リサーチ項目 | 決定 | 実装ステータス |
|---|---|---|
| MQTT | paho-mqtt + asyncio | ✅ Design Ready |
| UI Framework | GTK+ 3 (PySimpleGUI Fallback) | ✅ Design Ready |
| Database | SQLite + WAL + VACUUM | ✅ Schema Ready |
| Async Design | asyncio + PriorityQueue | ✅ Architecture Ready |
| Audio | pyaudio + numpy + scipy | ✅ Implementation Ready |
| Display | Pillow + I2C Light Sensor | ✅ Design Ready |
| Authentication | bcrypt + Rate Limiting | ✅ Implementation Ready |
| Optimization | Memory/CPU monitoring | ✅ Strategy Ready |

---

## Clarifications Resolved

✅ すべての NEEDS CLARIFICATION 解決（Phase 0 完了）

次フェーズ: **Phase 1 - Data Model & Contracts**
