# Checklist: 火災・防犯警報通知システム 要件品質検証

**Purpose**: 実装前に仕様書の完全性と品質を検証
**Created**: 2026-03-15
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 - すべての警報タイプ（火災、防犯）の受信・表示・警告音要件が定義されているか？ [Completeness, Spec §User Story 1,2]
- [ ] CHK002 - 来客通話機能の要件が完全定義されているか？ [Completeness, Spec §User Story 3]
- [ ] CHK003 - 優先度順序（火災 > 防犯 > 通話）の要件が明確に記載されているか？ [Completeness, Spec §Input]
- [ ] CHK004 - エッジケース（複数警報同時発生、センサー故障）の要件が定義されているか？ [Completeness, Spec §Edge Cases]
- [ ] CHK005 - 非機能要件（レスポンス時間、音量レベル、ディスプレイ調整）が指定されているか？ [Completeness, Spec §Clarifications]

## Requirement Clarity

- [ ] CHK006 - 警報受信から画面表示までの時間（100msec以下）が測定可能に定義されているか？ [Clarity, Spec §User Story 1]
- [ ] CHK007 - 警告音再生開始時間（500msec以下）が明確に指定されているか？ [Clarity, Spec §User Story 1,2]
- [ ] CHK008 - 音量レベル（火災85dB、防犯80dB、通話70dB）が具体的に定義されているか？ [Clarity, Spec §Clarifications]
- [ ] CHK009 - ディスプレイ明るさ調整（環境適応、最大120%）の基準が明確か？ [Clarity, Spec §Clarifications]
- [ ] CHK010 - コントラスト比（7:1、WCAG AAA準拠）の要件が具体的に記載されているか？ [Clarity, Spec §Clarifications]

## Requirement Consistency

- [ ] CHK011 - 警報優先度の定義が仕様全体で一貫しているか？ [Consistency, Spec §Input, User Stories]
- [ ] CHK012 - センサー通信プロトコル（MQTT）の使用が一貫して記載されているか？ [Consistency, Spec §Clarifications]
- [ ] CHK013 - タイムアウト設定（30秒）が通話機能で一貫して適用されているか？ [Consistency, Spec §User Story 3]
- [ ] CHK014 - ユーザー認証（PIN 4桁）の要件が一貫しているか？ [Consistency, Spec §Clarifications]

## Acceptance Criteria Quality

- [ ] CHK015 - 各ユーザーストーリーの受け入れシナリオが独立してテスト可能か？ [Acceptance Criteria, Spec §User Stories]
- [ ] CHK016 - 成功基準が測定可能（時間、音量、表示など）で定義されているか？ [Measurability, Spec §Clarifications]
- [ ] CHK017 - 各警報タイプの表示色（赤色、黄色）が明確に指定されているか？ [Measurability, Spec §User Stories]

## Scenario Coverage

- [ ] CHK018 - 主要シナリオ（火災警報受信、防犯警報受信、通話開始）がカバーされているか？ [Coverage, Spec §User Stories]
- [ ] CHK019 - 代替シナリオ（警報中の通話保留、複数警報待機）が定義されているか？ [Coverage, Spec §User Stories]
- [ ] CHK020 - 例外シナリオ（ネットワーク切断、センサー故障）が記載されているか？ [Coverage, Spec §Edge Cases, Clarifications]

## Edge Case Coverage

- [ ] CHK021 - 複数警報同時発生時の処理が定義されているか？ [Edge Case, Spec §Edge Cases]
- [ ] CHK022 - センサー故障時のハートビート監視と警告表示が指定されているか？ [Edge Case, Spec §Clarifications]
- [ ] CHK023 - システム再起動後の待機警報復元が定義されているか？ [Edge Case, Spec §Clarifications]
- [ ] CHK024 - ネットワーク復帰後の状態同期が記載されているか？ [Edge Case, Spec §Clarifications]

## Non-Functional Requirements

- [ ] CHK025 - パフォーマンス要件（100msec表示、500msec音声）が明確に定義されているか？ [NFR, Spec §Clarifications]
- [ ] CHK026 - セキュリティ要件（PIN認証、監査ログ）が指定されているか？ [NFR, Spec §Clarifications]
- [ ] CHK027 - アクセシビリティ要件（コントラスト比、フォントサイズ）が定義されているか？ [NFR, Spec §Clarifications]
- [ ] CHK028 - 信頼性要件（オフライン動作、永続化）が記載されているか？ [NFR, Spec §Clarifications]

## Dependencies & Assumptions

- [ ] CHK029 - MQTTブローカーの依存関係が明確に記載されているか？ [Dependency, Spec §Clarifications]
- [ ] CHK030 - センサーからの自動解除信号の仮定が検証されているか？ [Assumption, Spec §Clarifications]
- [ ] CHK031 - ローカル保存のみのログ要件が一貫しているか？ [Assumption, Spec §Clarifications]

## Ambiguities & Conflicts

- [ ] CHK032 - 警報解除の判定基準が曖昧でないか？ [Ambiguity, Spec §Clarifications]
- [ ] CHK033 - 待機警報のUI表示（カウンター）が他の要件と矛盾しないか？ [Conflict, Spec §Clarifications]
- [ ] CHK034 - 音量調整範囲（60dB～90dB）が固定値と矛盾しないか？ [Conflict, Spec §Clarifications]