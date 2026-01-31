# Quick Start Guide: 火災・防犯警報通知システム

**Branch**: `001-alert-notification` | **Date**: 2026-01-31 | **Phase**: 1 - Quickstart

## Prerequisites

- **Hardware**: Raspberry Pi 4/5 (4GB RAM 推奨) または Armbian 対応 SBC
- **OS**: Debian/Armbian (Linux Kernel 5.x+)
- **Python**: 3.10 以上
- **ディスプレイ**: HDMI 4～7 インチ (800x480 以上)
- **スピーカー**: 3.5mm ジャック or HDMI オーディオ
- **センサー**: I2C 周囲光センサー (BMP280 等)

---

## Installation

### 1. リポジトリクローン & 環境構築

```bash
cd /opt
sudo git clone https://github.com/your-org/alert-monitor.git
cd alert-monitor

# Python venv 作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. システムレベルの依存関係

```bash
# GTK+ 3 & development headers
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Audio libraries
sudo apt-get install pulseaudio pyaudio libportaudio2

# I2C tools (周囲光センサー)
sudo apt-get install i2c-tools python3-smbus

# データベース
# SQLite は Python bundled（追加インストール不要）

# システムモニタリング
pip install psutil
```

### 3. I2C 周囲光センサー設定

```bash
# I2C ポート確認
i2cdetect -y 1

# BMP280 が 0x76 or 0x77 に見つかることを確認
# 見つからない場合、センサーの接続とアドレスを確認
```

---

## Initial Setup

### 1. 設定ファイルの生成

```bash
python alert_monitor/main.py --init-setup
```

**初期設定ウィザード:**

```
========================================
  Alert Monitor - First Time Setup
========================================

Step 1: Administrator PIN Setup
  PIN (4-6 digits): ****
  Confirm PIN: ****

Step 2: MQTT Broker Configuration
  Broker Host [localhost]: 192.168.1.100
  Broker Port [1883]: 1883
  Username []: 
  Password []: 

Step 3: Display Configuration
  Display Size (800x480) [OK]: OK
  Brightness Auto Adapt [Yes]: Yes

Step 4: Audio Configuration
  Audio Output Device [default]: default
  Fire Alert Volume (fixed at 85dB) [OK]: OK
  Security Alert Volume [80]: 80

Step 5: Timezone Configuration
  Timezone [Asia/Tokyo]: Asia/Tokyo

========================================
Setup Complete! Starting application...
```

設定は `config/settings.json` に保存されます。

### 2. MQTT ブローカーの起動（開発環境）

```bash
# Docker で MQTT ブローカー (EMQX) を起動
docker-compose up -d

# ブローカー確認
docker ps
# emqx container が起動していることを確認
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  emqx:
    image: emqx/emqx:latest
    ports:
      - "1883:1883"   # MQTT
      - "8083:8083"   # WebSocket
      - "8084:8084"   # WebSocket Secure
      - "8888:8888"   # Dashboard
    environment:
      - EMQX_ALLOW_ANONYMOUS=true
```

---

## Application Startup

### 基本起動

```bash
python alert_monitor/main.py
```

**起動ログ:**
```
[INFO] 2026-01-31 10:00:00 - Alert Monitor v1.0.0 starting...
[INFO] 2026-01-31 10:00:01 - Loading configuration from config/settings.json
[INFO] 2026-01-31 10:00:02 - Connecting to MQTT broker (192.168.1.100:1883)
[INFO] 2026-01-31 10:00:03 - MQTT connected successfully
[INFO] 2026-01-31 10:00:04 - Initializing UI (GTK+ 3)
[INFO] 2026-01-31 10:00:05 - Starting sensor heartbeat monitor (60s interval)
[INFO] 2026-01-31 10:00:06 - Application ready
```

### バックグラウンド起動（systemd）

```bash
# systemd service 作成
sudo cp alert-monitor.service /etc/systemd/system/

# サービス有効化
sudo systemctl daemon-reload
sudo systemctl enable alert-monitor
sudo systemctl start alert-monitor

# ステータス確認
sudo systemctl status alert-monitor
```

**alert-monitor.service**:
```ini
[Unit]
Description=Alert Monitor - Fire & Security Alert System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/alert-monitor
ExecStart=/opt/alert-monitor/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## Testing

### ユニットテスト

```bash
# pytest 実行
pytest tests/unit -v

# カバレッジ確認
pytest tests/unit --cov=alert_monitor --cov-report=html
```

### 統合テスト

```bash
# MQTT ブローカーが起動していることを確認してから実行
pytest tests/integration -v
```

### 手動テスト：モック火災警報送信

```bash
# ターミナル1: Alert Monitor 起動
python alert_monitor/main.py

# ターミナル2: モック火災警報を MQTT 送信
python -c "
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect('localhost', 1883, 60)

alert = {
    'alert_id': 'test_fire_001',
    'alert_type': 'FIRE',
    'sensor_id': 'fire_sensor_1',
    'timestamp': int(time.time()),
    'priority_level': 1
}

client.publish('sensor/fire/alert', json.dumps(alert))
print('Fire alert sent!')
client.disconnect()
"

# → Alert Monitor の画面が赤色に変わり、警告音が鳴ることを確認
```

### 手動テスト：PIN認証

```bash
# 設定画面を開く (画面で「設定」をタップ)
# PIN 入力を促されたら、初期設定で設定した PIN を入力
# 正しく入力できれば、設定画面が表示される
```

---

## Configuration Reference

### config/settings.json

```json
{
  "mqtt": {
    "broker_host": "192.168.1.100",
    "broker_port": 1883,
    "username": "",
    "password": "",
    "keepalive": 60,
    "qos": 1
  },
  "audio": {
    "volume_fire_db": 85,
    "volume_security_db": 80,
    "volume_call_db": 70,
    "audio_output_device": "default"
  },
  "display": {
    "width": 800,
    "height": 480,
    "brightness_auto_adapt": true,
    "brightness_normal_percent": 80,
    "brightness_dark_percent": 120
  },
  "sensors": {
    "heartbeat_interval_seconds": 60,
    "heartbeat_timeout_seconds": 300
  },
  "logging": {
    "retention_days": 90,
    "storage_limit_percent": 10
  },
  "timezone": "Asia/Tokyo",
  "language": "ja"
}
```

---

## Troubleshooting

### MQTT 接続失敗

```
[ERROR] Failed to connect to MQTT broker
```

**対処:**
```bash
# ブローカー接続確認
nc -zv 192.168.1.100 1883

# ファイアウォール確認
sudo ufw allow 1883

# ブローカーが起動しているか確認
docker ps | grep emqx
```

### 警告音が出ない

```
[WARNING] Audio stream error
```

**対処:**
```bash
# PulseAudio ステータス確認
pactl list short sinks

# オーディオデバイス確認
aplay -l

# テスト音声出力
speaker-test -t sine -f 1000 -l 1
```

### I2C センサーが認識されない

```
[ERROR] Light sensor initialization failed
```

**対処:**
```bash
# I2C デバイス確認
i2cdetect -y 1

# I2C enable 確認
raspi-config  # Raspberry Pi の場合
  → Interface Options → I2C → Enable
```

### メモリ不足エラー

```
[ERROR] MemoryError: Unable to allocate memory
```

**対処:**
```bash
# メモリ使用状況確認
free -h

# ガベージコレクション強制実行
python -c "import gc; gc.collect()"

# 古いログ削除
python -c "
import sqlite3
conn = sqlite3.connect('data/alert_monitor.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM audit_logs WHERE timestamp < ?', (int(time.time()) - 30*86400,))
conn.commit()
"
```

---

## Logs

### ログファイル

```bash
# systemd ジャーナルで確認
sudo journalctl -u alert-monitor -f

# または、アプリケーション内ログ
cat logs/alert_monitor.log

# リアルタイムログ監視
tail -f logs/alert_monitor.log
```

### ログレベル

```
DEBUG: 詳細なデバッグ情報
INFO: 一般情報
WARNING: 警告（機能動作するが注意が必要）
ERROR: エラー（機能に支障）
CRITICAL: 致命的エラー（システム停止）
```

---

## Performance Monitoring

### リソース使用状況確認

```bash
# CPU・メモリ・ストレージ確認
top -p $(pgrep -f 'alert_monitor')

# または専用スクリプト
python alert_monitor/monitoring.py
```

**期待値:**
- メモリ: 100-150 MB
- CPU (通常): 5%
- CPU (警報処理時): 30% 以下
- ストレージ (ログ): <50 MB (10% 上限)

---

## Deployment

### 本番環境デプロイ

```bash
# 1. 本番用 Docker イメージビルド
docker build -f Dockerfile.prod -t alert-monitor:1.0.0 .

# 2. Raspberry Pi にイメージ転送
docker save alert-monitor:1.0.0 | ssh pi@192.168.1.50 docker load

# 3. 本番用 docker-compose 起動
docker-compose -f docker-compose.prod.yml up -d

# 4. ヘルスチェック
curl http://localhost:8000/health
```

---

## Support

### ドキュメント
- [Architecture Guide](ARCHITECTURE.md)
- [API Reference](API.md)
- [Testing Guide](TESTING.md)

### サポート連絡先
- Issue: GitHub Issues
- Bug Report: [project-repo]/issues/new?template=bug_report.md
- Feature Request: [project-repo]/issues/new?template=feature_request.md

---

**Quick Start Complete!** 🚀

次のステップ:
- [Architecture Guide](ARCHITECTURE.md) で詳細な設計を確認
- [Testing Guide](TESTING.md) で詳細なテスト手順を確認
- GitHub Issues でフィードバックを提供
