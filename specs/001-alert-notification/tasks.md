# 実装タスク: 火災・防犯警報通知システム

**ブランチ**: `001-alert-notification` | **日付**: 2026-01-31 | **フェーズ**: 2 - タスク  
**入力**: [spec.md](spec.md)、[plan.md](plan.md) からの仕様  

**コマンド**: `/speckit.tasks` | **出力**: このファイル

---

## プロジェクト範囲 & フェーズ

**対象プラットフォーム**: Linux ARM (Raspberry Pi 4/5, Armbian)  
**言語**: Python 3.10+  
**主要マイルストーン**:
- **フェーズ 1** ✅: 仕様+設計 (完了)
- **フェーズ 2** ⏳: 基盤・インフラ
- **フェーズ 3** ⏳: ユーザーストーリー1 - 火災警報 (P1)
- **フェーズ 4** ⏳: ユーザーストーリー2 - 防犯警報 (P2)
- **フェーズ 5** ⏳: ユーザーストーリー3 - 来客通話 (P3)
- **フェーズ 6** ⏳: ポーランド & 横断的関心事

**総タスク数**: 165 タスク  
**MVP 範囲**: フェーズ 2 + フェーズ 3 (火災警報のみ、約 81 タスク)

---

## フェーズ 2: 基盤・インフラストラクチャ構築

**目標**: プロジェクト構造、依存関係、非同期フレームワーク、データベーススキーマ初期化  
**期間**: 3～4 日  
**独立テスト基準**: 
- [ ] プロジェクトビルド完了（pytest 設定有効）
- [ ] データベーススキーマ展開（SQLite WAL + VACUUM 有効）
- [ ] Core asyncio + PriorityQueue 動作確認（ユニットテスト合格）
- [ ] MQTT ブローカー接続確認（モックテスト）
- [ ] requirements.txt 依存関係インストール完了（競合なし）

### 基盤タスク

- [ ] **T001** プロジェクト構造作成: src/、tests/、config/、docs/ ディレクトリ、__init__.py ファイル [src/](src/)
- [ ] **T002** [P] requirements.txt 作成: paho-mqtt 1.6.1、pytest 7.4、pytest-asyncio 0.21、GTK+ 3 dev ヘッダー、pyaudio 0.2.13、Pillow 10.0、bcrypt 4.0 [requirements.txt](requirements.txt)
- [ ] **T003** [P] setup.py 作成、エントリーポイント `alert-notification` [setup.py](setup.py)
- [ ] **T004** [P] pytest.ini 作成: asyncio モード、テスト検出パターン [pytest.ini](pytest.ini)
- [ ] **T005** [P] .flake8 リンター設定作成: line-length=100、ignore=E501,W503 [.flake8](.flake8)
- [ ] **T006** [P] config/default.yaml 作成、システムデフォルト: log_retention_days=90、volume_fire_db=85、volume_security_db=80、volume_call_db=70、max_alert_cache=100 [config/default.yaml](config/default.yaml)
- [ ] **T007** [P] config/logging.conf 作成、Python ログフォーマッター (タイムスタンプ、レベル、ロガー名) [config/logging.conf](config/logging.conf)
- [ ] **T008** [P] Dockerfile 作成: Python 3.10 ベース、apt-get install GTK+ dev、systemd 統合 [Dockerfile](Dockerfile)
- [ ] **T009** [P] docker-compose.yml 作成: MQTT ブローカー (mosquitto) + アプリケーション [docker-compose.yml](docker-compose.yml)
- [ ] **T010** config/systemd/alert-notification.service 作成: ExecStart、Restart=always、User=root [config/systemd/alert-notification.service](config/systemd/alert-notification.service)
- [ ] **T011** [P] README.md 作成: プロジェクト概要、クイックスタート (pip install、pytest、systemd)、前提条件 [README.md](README.md)
- [ ] **T012** src/__init__.py 作成: __version__ = "0.1.0" [src/__init__.py](src/__init__.py)
- [ ] **T013** src/main.py 作成: エントリーポイント asyncio.run(main_async()) プレースホルダー [src/main.py](src/main.py)
- [ ] **T014** src/models/__init__.py 作成（空モジュール） [src/models/__init__.py](src/models/__init__.py)
- [ ] **T015** src/models/enums.py 作成: AlertType (FIRE、SECURITY)、AlertState (PENDING、DISPLAYED、CLEARED)、UserType (RESIDENT、GUEST)、CallStatus (RINGING、CONNECTED、HELD、ENDED) [src/models/enums.py](src/models/enums.py)
- [ ] **T016** src/models/database.py 作成: SQLite 接続プール、WAL モード (PRAGMA journal_mode=WAL)、VACUUM 設定、接続コンテキストマネージャ [src/models/database.py](src/models/database.py)
- [ ] **T017** src/models/entities.py 作成: dataclass Alert、VisitorCall、User、DisplayState、AuditLog、Settings（型ヒント付き） [src/models/entities.py](src/models/entities.py)
- [ ] **T018** src/models/validators.py 作成: validate_pin()、validate_alert_type()、validate_sensor_id()、validate_priority_level() [src/models/validators.py](src/models/validators.py)
- [ ] **T019** SQLite スキーママイグレーションスクリプト作成: alerts、users、visitor_calls、display_state、audit_logs、settings テーブル [src/models/schema.sql](src/models/schema.sql)
- [ ] **T020** tests/conftest.py 作成: pytest フィクスチャ: mock_mqtt_client、mock_database (in-memory sqlite)、mock_audio、mock_display、mock_ui、event_loop [tests/conftest.py](tests/conftest.py)
- [ ] **T021** [P] tests/__init__.py 作成（空モジュール） [tests/__init__.py](tests/__init__.py)
- [ ] **T022** [P] tests/unit/__init__.py 作成（空モジュール） [tests/unit/__init__.py](tests/unit/__init__.py)
- [ ] **T023** [P] tests/integration/__init__.py 作成（空モジュール） [tests/integration/__init__.py](tests/integration/__init__.py)
- [ ] **T024** [P] tests/e2e/__init__.py 作成（空モジュール） [tests/e2e/__init__.py](tests/e2e/__init__.py)

### コア非同期フレームワークタスク

- [ ] **T025** src/core/__init__.py 作成（空モジュール） [src/core/__init__.py](src/core/__init__.py)
- [ ] **T026** src/core/asyncio_manager.py 作成: AsyncIOManager クラス: get_event_loop()、run_main()、graceful_shutdown()、asyncio.CancelledError ハンドリング [src/core/asyncio_manager.py](src/core/asyncio_manager.py)
- [ ] **T027** src/core/priority_queue.py 作成: AlertPriorityQueue クラス: put(alert, priority)、get_async()、task_done()、優先度レベル FIRE=1、SECURITY=2、CALL=3 [src/core/priority_queue.py](src/core/priority_queue.py)
- [ ] **T028** src/core/mqtt_broker.py 作成: MQTTBrokerClient クラス: __init__(broker_host、broker_port、topics)、connect()、disconnect()、subscribe(topic、callback)、publish(topic、payload)、heartbeat_monitor() [src/core/mqtt_broker.py](src/core/mqtt_broker.py)
- [ ] **T029** src/core/state_machine.py 作成: SystemStateMachine クラス: init_state、dispatch(event)、transition(from_state、to_state)、状態別コールバック、状態: IDLE、FIRE_ALERT、SECURITY_ALERT、VISITOR_CALL、HOLD [src/core/state_machine.py](src/core/state_machine.py)

### サービス層スタブ

- [ ] **T030** src/services/__init__.py 作成（空モジュール） [src/services/__init__.py](src/services/__init__.py)
- [ ] **T031** src/services/alert_processor.py 作成: AlertProcessor クラス (スタブ): process_alert(alert)、prioritize()、execute_command() [src/services/alert_processor.py](src/services/alert_processor.py)
- [ ] **T032** src/services/audio_service.py 作成: AudioService クラス (スタブ): play_alert(sound_type)、stop_audio()、set_volume(db_level) [src/services/audio_service.py](src/services/audio_service.py)
- [ ] **T033** src/services/display_service.py 作成: DisplayService クラス (スタブ): show_alert(alert_type)、update_brightness(percent)、show_visitor_call() [src/services/display_service.py](src/services/display_service.py)
- [ ] **T034** src/services/auth_service.py 作成: AuthService クラス (スタブ): verify_pin(pin_str)、rate_limit_check()、lock_on_failure() [src/services/auth_service.py](src/services/auth_service.py)
- [ ] **T035** src/services/persistence_service.py 作成: PersistenceService クラス (スタブ): save_alert(alert)、load_alerts()、rotate_logs() [src/services/persistence_service.py](src/services/persistence_service.py)
- [ ] **T036** src/services/sensor_monitor.py 作成: SensorMonitor クラス (スタブ): monitor_heartbeat(sensor_id)、detect_failure()、notify_failure() [src/services/sensor_monitor.py](src/services/sensor_monitor.py)
- [ ] **T037** src/services/network_sync.py 作成: NetworkSync クラス (スタブ): sync_on_reconnect()、request_state()、merge_state_diff() [src/services/network_sync.py](src/services/network_sync.py)
- [ ] **T038** src/services/visitor_call_handler.py 作成: VisitorCallHandler クラス (スタブ): handle_incoming_call(call_data)、hold_call()、resume_call() [src/services/visitor_call_handler.py](src/services/visitor_call_handler.py)

### UI 層スタブ

- [ ] **T039** src/ui/__init__.py 作成（空モジュール） [src/ui/__init__.py](src/ui/__init__.py)
- [ ] **T040** src/ui/main_window.py 作成: MainWindow クラス (GTK+ スタブ): __init__()、run()、draw_normal_screen()、draw_fire_alert_screen() [src/ui/main_window.py](src/ui/main_window.py)
- [ ] **T041** src/ui/screens/__init__.py 作成（空モジュール） [src/ui/screens/__init__.py](src/ui/screens/__init__.py)
- [ ] **T042** [P] src/ui/screens/normal_screen.py 作成: NormalScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/normal_screen.py](src/ui/screens/normal_screen.py)
- [ ] **T043** [P] src/ui/screens/fire_alert_screen.py 作成: FireAlertScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/fire_alert_screen.py](src/ui/screens/fire_alert_screen.py)
- [ ] **T044** [P] src/ui/screens/security_alert_screen.py 作成: SecurityAlertScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/security_alert_screen.py](src/ui/screens/security_alert_screen.py)
- [ ] **T045** [P] src/ui/screens/visitor_call_screen.py 作成: VisitorCallScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/visitor_call_screen.py](src/ui/screens/visitor_call_screen.py)
- [ ] **T046** [P] src/ui/screens/settings_screen.py 作成: SettingsScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/settings_screen.py](src/ui/screens/settings_screen.py)
- [ ] **T047** [P] src/ui/screens/logs_screen.py 作成: LogsScreen クラス (スタブ): display()、handle_tap() [src/ui/screens/logs_screen.py](src/ui/screens/logs_screen.py)
- [ ] **T048** src/ui/components/__init__.py 作成（空モジュール） [src/ui/components/__init__.py](src/ui/components/__init__.py)
- [ ] **T049** src/ui/components/alert_banner.py 作成: AlertBanner クラス (スタブ): display_fire()、display_security()、show_counter() [src/ui/components/alert_banner.py](src/ui/components/alert_banner.py)
- [ ] **T050** src/ui/components/visitor_panel.py 作成: VisitorPanel クラス (スタブ): display_incoming()、show_accept_button() [src/ui/components/visitor_panel.py](src/ui/components/visitor_panel.py)
- [ ] **T051** src/ui/components/action_buttons.py 作成: ActionButtons クラス (スタブ): show_mute()、show_clear()、show_decline() [src/ui/components/action_buttons.py](src/ui/components/action_buttons.py)
- [ ] **T052** src/ui/accessibility.py 作成: AccessibilityConfig クラス: font_size_pt=18、contrast_ratio_min=7、FIRE/SECURITY/NORMAL 警報用カラーペア [src/ui/accessibility.py](src/ui/accessibility.py)

### 基盤テストタスク

- [ ] **T053** [P] tests/unit/test_enums.py 作成: AlertType、AlertState、UserType、CallStatus enum のユニットテスト [tests/unit/test_enums.py](tests/unit/test_enums.py)
- [ ] **T054** [P] tests/unit/test_validators.py 作成: validate_pin()、validate_alert_type()、validate_sensor_id()、validate_priority_level() のユニットテスト [tests/unit/test_validators.py](tests/unit/test_validators.py)
- [ ] **T055** [P] tests/unit/test_priority_queue.py 作成: AlertPriorityQueue.put()、get_async()、優先度順序 (FIRE > SECURITY > CALL) のユニットテスト [tests/unit/test_priority_queue.py](tests/unit/test_priority_queue.py)
- [ ] **T056** [P] tests/unit/test_asyncio_manager.py 作成: AsyncIOManager ライフサイクル、graceful_shutdown()、CancelledError ハンドリングのユニットテスト [tests/unit/test_asyncio_manager.py](tests/unit/test_asyncio_manager.py)
- [ ] **T057** tests/unit/test_database.py 作成: SQLite 接続、WAL モード検証、スキーマ作成のユニットテスト [tests/unit/test_database.py](tests/unit/test_database.py)

---

## フェーズ 3: ユーザーストーリー1 - 火災警報 (P1)

**目標**: 火災警報受信 → 画面表示 → 音声通知パイプライン完成  
**期間**: 5～7 日  
**独立テスト基準**:
- [ ] MQTT 火災警報トピック: システムで 100msec 以内にアラート生成
- [ ] アラート画面に赤色「火災警報」テキスト表示
- [ ] 音声アラート 500msec 以内に開始
- [ ] ディスプレイスリープ状態から自動起動
- [ ] 火災警報が全警報・通話より優先度最高
- [ ] 永続化: システムクラッシュ後に復旧、再起動時に復元

### 火災警報検出 & 受信

- [ ] **T058** [US1] AlertProcessor.process_fire_alert() のユニットテスト作成 [tests/unit/test_alert_processor.py](tests/unit/test_alert_processor.py)
- [ ] **T059** [US1] AlertProcessor.process_fire_alert(alert_data: dict) 実装 → Alert オブジェクト (alert_type=FIRE、priority_level=1) [src/services/alert_processor.py](src/services/alert_processor.py)
- [ ] **T060** [US1] MQTT 火災トピック購読・メッセージルーティングの統合テスト作成 [tests/integration/test_mqtt_flow.py](tests/integration/test_mqtt_flow.py)
- [ ] **T061** [US1] MQTT `sensor/fire/alert` トピック購読実装、MQTTBrokerClient にコールバックルーティング追加 [src/core/mqtt_broker.py](src/core/mqtt_broker.py)
- [ ] **T062** [US1] TimingMonitor: 警報受信→画面表示レイテンシ <100msec 検証のユニットテスト作成 [tests/unit/test_timing_monitor.py](tests/unit/test_timing_monitor.py)

### 火災警報表示

- [ ] **T063** [US1] FireAlertScreen.display() 赤背景 + 「火災警報」テキストレンダリングのユニットテスト作成 [tests/unit/test_fire_alert_screen.py](tests/unit/test_fire_alert_screen.py)
- [ ] **T064** [US1] FireAlertScreen.display(alert: Alert) 実装: 赤背景 (#FF0000)、大きい白「火災警報」テキスト、中央揃え [src/ui/screens/fire_alert_screen.py](src/ui/screens/fire_alert_screen.py)
- [ ] **T065** [US1] DisplayService.show_fire_alert(alert: Alert) 実装、火災警報画面へ遷移 [src/services/display_service.py](src/services/display_service.py)
- [ ] **T066** [US1] 火災警報が MQTT メッセージ受信から 100msec 以内に画面表示されることの統合テスト作成 [tests/integration/test_ui_integration.py](tests/integration/test_ui_integration.py)
- [ ] **T067** [US1] DisplayService.auto_wake_display() 実装: スリープから起動、警報受信時に明度最大に [src/services/display_service.py](src/services/display_service.py)

### 火災警報音声

- [ ] **T068** [US1] AudioService.play_fire_alert() 85dB トーン 2～3 秒生成のユニットテスト作成 [tests/unit/test_audio_service.py](tests/unit/test_audio_service.py)
- [ ] **T069** [US1] AudioService.play_fire_alert(duration_sec=5) 実装: 1kHz サイン波、85dB 固定レベル (変更不可)、2 秒間再生 [src/services/audio_service.py](src/services/audio_service.py)
- [ ] **T070** [US1] 火災警報音声が画面表示から 500msec 以内に開始することの統合テスト作成 [tests/integration/test_audio_integration.py](tests/integration/test_audio_integration.py)
- [ ] **T071** [US1] AudioService.mute_alert() 実装: 音声停止、画面表示は継続 [src/services/audio_service.py](src/services/audio_service.py)

### 火災警報永続化

- [ ] **T072** [US1] PersistenceService.save_alert(alert: Alert) → SQLite alerts テーブルに挿入のユニットテスト作成 [tests/unit/test_persistence_service.py](tests/unit/test_persistence_service.py)
- [ ] **T073** [US1] PersistenceService.save_alert(alert: Alert) 実装: データベースに挿入 (タイムスタンプ、タイプ、state=PENDING) [src/services/persistence_service.py](src/services/persistence_service.py)
- [ ] **T074** [US1] PersistenceService.load_alerts() → 起動時にデータベースから待機中警報復元のユニットテスト作成 [tests/unit/test_persistence_service.py](tests/unit/test_persistence_service.py)
- [ ] **T075** [US1] PersistenceService.load_alerts() 実装: アプリ起動時に警報をロード (state='PENDING')、「[システム復旧]」インジケーター付きで表示 [src/services/persistence_service.py](src/services/persistence_service.py)
- [ ] **T076** [US1] 火災警報がシステムクラッシュシミュレーション後に永続化・復元される統合テスト作成 [tests/integration/test_persistence_flow.py](tests/integration/test_persistence_flow.py)

### 火災警報優先度

- [ ] **T077** [US1] AlertPriorityQueue 優先度順序: FIRE (1) > SECURITY (2) > CALL (3) のユニットテスト作成 [tests/unit/test_priority_queue.py](tests/unit/test_priority_queue.py)
- [ ] **T078** [US1] SystemStateMachine FIRE_ALERT 状態へ遷移実装、SECURITY_ALERT/VISITOR_CALL 状態をオーバーライド [src/core/state_machine.py](src/core/state_machine.py)
- [ ] **T079** [US1] 火災警報が来客通話を中断、火災解除後に通話に戻ることの統合テスト作成 [tests/integration/test_state_transitions.py](tests/integration/test_state_transitions.py)
- [ ] **T080** [US1] AlertProcessor.clear_fire_alert() 実装: センサー「クリア」信号受信時、画面自動消去、前状態復元 [src/services/alert_processor.py](src/services/alert_processor.py)

### 火災警報 E2E テスト

- [ ] **T081** [US1] 完全な火災警報シナリオ E2E テスト作成 (MQTT 送信 → 100ms 表示 → 500ms 音声 → ミュート → クリア) [tests/e2e/test_fire_alert_scenario.py](tests/e2e/test_fire_alert_scenario.py)

---

## フェーズ 4: ユーザーストーリー2 - 防犯警報 (P2)

**目標**: 防犯警報受信 → 画面表示 → 音声通知パイプライン完成  
**期間**: 3～4 日  

- [ ] **T082** [US2] AlertProcessor.process_security_alert() のユニットテスト作成
- [ ] **T083** [US2] AlertProcessor.process_security_alert(alert_data: dict) 実装
- [ ] **T084** [US2] MQTT `sensor/security/alert` トピック購読実装
- [ ] **T085** [US2] SecurityAlertScreen.display() のユニットテスト作成
- [ ] **T086** [US2] SecurityAlertScreen.display(alert: Alert) 実装
- [ ] **T087** [US2] DisplayService.show_security_alert() 実装
- [ ] **T088** [US2] AlertBanner.show_counter() 実装
- [ ] **T089** [US2] AudioService.play_security_alert() のユニットテスト作成
- [ ] **T090** [US2] AudioService.play_security_alert(volume_db=80) 実装
- [ ] **T091** [US2] SettingsScreen 防犯警報音量コントロール実装
- [ ] **T092** [US2] 防犯警報キューイングの統合テスト作成
- [ ] **T093** [US2] AlertProcessor.enqueue_alert() 実装
- [ ] **T094** [US2] SystemStateMachine 遷移実装
- [ ] **T095** [US2] PersistenceService 防犯警報永続化実装
- [ ] **T096** [US2] 防犯警報シナリオ E2E テスト作成

---

## フェーズ 5: ユーザーストーリー3 - 来客通話 (P3)

**目標**: 来客通話受信 → 画面表示 → 音声通知 → 接続ハンドリング  
**期間**: 4～5 日  

- [ ] **T097** [US3] VisitorCallHandler.handle_incoming_call() のユニットテスト作成
- [ ] **T098** [US3] VisitorCallHandler.handle_incoming_call() 実装
- [ ] **T099** [US3] MQTT `visitor/call/incoming` トピック購読実装
- [ ] **T100** [US3] VisitorCallScreen.display() のユニットテスト作成
- [ ] **T101** [US3] VisitorCallScreen.display() 実装
- [ ] **T102** [US3] VisitorPanel.display_incoming() 実装
- [ ] **T103** [US3] DisplayService.show_visitor_call() 実装
- [ ] **T104** [US3] AudioService.play_visitor_call_tone() のユニットテスト作成
- [ ] **T105** [US3] AudioService.play_visitor_call_tone() 実装
- [ ] **T106** [US3] SettingsScreen 通話音量コントロール実装
- [ ] **T107** [US3] VisitorCallHandler.accept_call() のユニットテスト作成
- [ ] **T108** [US3] VisitorCallHandler.accept_call() 実装
- [ ] **T109** [US3] ActionButtons.show_accept() 実装
- [ ] **T110** [US3] VisitorCallHandler.decline_call() 実装
- [ ] **T111** [US3] 通話保留の統合テスト作成
- [ ] **T112** [US3] VisitorCallHandler.hold_call() 実装
- [ ] **T113** [US3] VisitorCallHandler.resume_call() 実装
- [ ] **T114** [US3] SystemStateMachine 通話保留遷移実装
- [ ] **T115** [US3] VisitorCallHandler タイムアウトのユニットテスト作成
- [ ] **T116** [US3] タイムアウトハンドリング実装
- [ ] **T117** [US3] 来客通話シナリオ E2E テスト作成

---

## フェーズ 6: ポーランド & 横断的関心事

**目標**: セキュリティ、監査ログ、センサー監視、ネットワーク同期、アクセシビリティ、パフォーマンス最適化  
**期間**: 5～7 日  

### 認証・認可

- [ ] **T118** AuthService.verify_pin() のユニットテスト作成
- [ ] **T119** AuthService.verify_pin() 実装 (bcrypt)
- [ ] **T120** AuthService.rate_limit_check() のユニットテスト作成
- [ ] **T121** AuthService.rate_limit_check() 実装
- [ ] **T122** 重要操作への PIN 保護実装
- [ ] **T123** UserType パーミッション検証のユニットテスト作成
- [ ] **T124** パーミッション確認実装

### 監査ログ

- [ ] **T125** AuditLogService.log_event() のユニットテスト作成
- [ ] **T126** AuditLogService クラス作成
- [ ] **T127** 警報処理への監査ログ統合
- [ ] **T128** ユーザー操作への監査ログ統合
- [ ] **T129** PersistenceService.rotate_logs() 実装
- [ ] **T130** LogsScreen 監査ログ表示実装

### センサー監視

- [ ] **T131** SensorMonitor.monitor_heartbeat() のユニットテスト作成
- [ ] **T132** SensorMonitor.monitor_heartbeat() 実装
- [ ] **T133** SensorMonitor.detect_failure() 実装
- [ ] **T134** SensorMonitor.notify_failure() 実装
- [ ] **T135** センサー故障検出の統合テスト作成
- [ ] **T136** DisplayService 自動明度調整のユニットテスト作成
- [ ] **T137** DisplayService.auto_adjust_brightness() 実装

### ネットワーク同期

- [ ] **T138** NetworkSync.sync_on_reconnect() のユニットテスト作成
- [ ] **T139** NetworkSync.sync_on_reconnect() 実装
- [ ] **T140** NetworkSync.request_state() 実装
- [ ] **T141** NetworkSync.merge_state_diff() 実装
- [ ] **T142** ネットワーク同期の統合テスト作成
- [ ] **T143** 同期タイムアウト実装

### アクセシビリティ

- [ ] **T144** WCAG AAA コントラスト比チェック実装
- [ ] **T145** フォントサイズ最小化実装
- [ ] **T146** AccessibilityConfig カラースキーム設定
- [ ] **T147** 振動フィードバック実装
- [ ] **T148** アクセシビリティテスト実施

### パフォーマンス

- [ ] **T149** メモリ監視のユニットテスト作成
- [ ] **T150** AsyncIOManager メモリ監視実装
- [ ] **T151** パフォーマンスベンチマーク作成
- [ ] **T152** AlertProcessor 最適化
- [ ] **T153** CPU スロットリング実装
- [ ] **T154** systemd リソース制限設定

### ドキュメント・CI/CD

- [ ] **T155** docs/architecture.md 作成
- [ ] **T156** docs/deployment.md 作成
- [ ] **T157** docs/troubleshooting.md 作成
- [ ] **T158** README.md 更新
- [ ] **T159** .github/workflows/test.yml 作成
- [ ] **T160** .github/workflows/lint.yml 作成

### 最終統合

- [ ] **T161** 包括的な E2E テスト作成
- [ ] **T162** 全テストスイート実行 (>80% カバレッジ)
- [ ] **T163** Raspberry Pi での手動テスト
- [ ] **T164** 実 MQTT ブローカーとの検証
- [ ] **T165** 今後の拡張について記述

---

## MVP 範囲

**Minimum Viable Product** (火災警報のみ):
- フェーズ 2: 基盤 (T001-T057) — 約 57 タスク、3～4 日
- フェーズ 3: 火災警報 (T058-T081) — 約 24 タスク、5～7 日
- **合計 MVP**: 約 81 タスク、**8～11 日**、1 つのユーザーストーリー完全動作

**MVP 成功基準**:
- ✅ MQTT 火災警報受信→画面表示 <100msec
- ✅ 音声アラート (85dB 固定) 再生開始 <500msec
- ✅ システムクラッシュ復旧 (永続化) 動作
- ✅ 全 MVP タスク ユニット + 統合テスト合格

**推奨最初のインクリメント**:
1. フェーズ 2 (基盤)
2. フェーズ 3 (火災警報) — 最小限で実行可能
3. フェーズ 4-5 (防犯警報、来客通話) 次スプリント
4. フェーズ 6 (ポーランド) 最終スプリント

---

## 成功メトリクス

| メトリクス | 目標値 |
|-----------|-------|
| 火災警報レイテンシ | <100msec |
| 音声開始レイテンシ | <500msec |
| システムアップタイム | 7+ 日 |
| コードカバレッジ | >80% |
| アクセシビリティ | WCAG AAA |
| メモリ使用量 | <150MB |
| CPU 使用率 | <30% |
| ログ保有期間 | 90 日 |
| テスト合格率 | 100% |

---

**生成**: 2026-01-31 (speckit.tasks ワークフロー)  
**ステータス**: 実装準備完了  
**次ステップ**: フェーズ 2 基盤タスク (T001-T057) 開始
