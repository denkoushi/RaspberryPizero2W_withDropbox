# 要件とロードマップ

Raspberry Pi Zero 2 W × Dropbox サイネージ（Window C）の現況・要件・決定事項・今後の課題を整理する。セットアップ手順や運用コマンドは README と `docs/STEP_BY_STEP_SETUP.md` を参照すること。

---

## 0. 現況サマリー（2025-10-31 時点）
- **役割**: Pi5（RaspberryPiServer）や Window A（tool-management-system02）が生成する所在・工程情報を Dropbox 経由で受信し、Pillow で描画した PNG を `feh` の全画面で掲示する軽量サイネージ。
- **稼働状況**: Pi Zero 2 W 実機で systemd --user タイマーと autostart により 1 分間隔の描画が安定稼働。ダミー JSON で表示確認済み。
- **依存関係**: Dropbox 共有リンク、Pi5 側バッチ、Window A の API/CSV 出力。ホスト名は `raspi-server-*.local` 変化に追従する。
- **未解決課題**: Pi5 由来データスキーマ確定、Window A と Dropbox の連携方式、Wi‑Fi 運用（バースト更新）など。

---

## 1. ゴール
1. Pi5／Window A で生成した最新の所在・工程データをサイネージへ反映し、現場へ即時共有する。
2. ネットワーク断や Dropbox 障害時も直近の PNG を表示し続け、確認手段を維持する。
3. 将来的に Window D（OnSiteLogistics）や DocumentViewer と同じ情報基盤を共有し、表示内容を統一する。

---

## 2. 関係者と責務

| 区分 | 役割 | 主な責務 |
| --- | --- | --- |
| プロダクトオーナー（ユーザー） | 運用要求・表示項目の決定、Dropbox 共有設定の管理 |
| RaspberryPiServer チーム（Window E） | JSON 生成バッチ／API の提供、Pi5 ホスト名・公開方法の維持 |
| Window A チーム（tool-management-system02） | 工具管理データ/API の提供、Pi5 へのデータ反映手順の維持 |
| 本リポジトリ担当（Window C） | Pi Zero 2 W 構成の保守、描画スクリプトと systemd --user 運用、ドキュメント棚卸し |

---

## 3. 機能要件（ステータス付き）

| 状態 | ID | 内容 | 実装メモ |
| --- | --- | --- | --- |
| ✅ | F-01 | Dropbox 共有リンク（`?dl=1`）から JSON をダウンロードし、一時保存する | `signage/pull_signage.sh` |
| ✅ | F-02 | JSON を Pillow で PNG 化し、日本語フォント・省略表示・ゼブラ行に対応する | `signage/render_signage.py` |
| ✅ | F-03 | `feh` を kiosk モードで起動し、PNG をループ表示する | `autostart/signage-view.desktop` |
| ✅ | F-04 | systemd --user タイマーで定期取得・描画を行う | `systemd-user/signage-pull.{service,timer}` |
| ☐ | F-05 | Pi5 で生成した所在・工程データの JSON スキーマを固定化し、Dropbox へ自動配置する | RaspberryPiServer 側と整合中 |
| ☐ | F-06 | Window A（工具管理）からの API/CSV を Dropbox JSON に統合する | 更新周期・差分設計を決定する |

---

## 4. 非機能要件
- **性能**: 取得〜描画〜表示まで 1 分以内（デフォルト）。JSON レコード数は 1,000 件程度を上限とし、描画時間を監視する。
- **可用性**: `autostart` と `systemd --user` によりログイン直後から自動起動。`loginctl enable-linger` でセッション切断後も継続させる。
- **保守性**: 実機更新は「GitHub → 作業フォルダ → `/usr/local/bin/` / `$HOME/signage` へ同期」の二段階。`rsync` と `git status` で差分確認。
- **セキュリティ**: Dropbox 共有リンクは定期ローテーションを前提とし、更新時は `pull_signage.sh` と systemd ユニット環境ファイルの双方を更新する。

---

## 5. インターフェースと依存関係
- **Pi5 (RaspberryPiServer)**: `/srv/rpi-server/documents/` で生成した JSON/PDF を Dropbox に渡す想定。ホスト名の変更履歴（`raspi-server.local` → `raspi-server-3.local` 等）を `docs/STEP_BY_STEP_SETUP.md` に即時反映する。
- **Window A (tool-management-system02)**: `part_locations`, `work_orders` 等の API/CSV を Pi5 側で JSON 化する。マッピング表と更新頻度を決定する。
- **OnSiteLogistics (Window D)**: ハンディリーダで登録したイベントを Pi5 が取り込み、必要に応じてサイネージへ反映する。
- **Font / 画像資源**: `signage/fonts` で管理。ブランド画像やアイコンが必要な場合は `assets/` ディレクトリを追加する。

---

## 6. 決定履歴

| 決定日 | 内容 | 理由 / 影響 |
| --- | --- | --- |
| 2025-09-14 | ブラウザではなく `feh` を採用する | Pi Zero 2 W の負荷低減とオフライン継続表示の実現 |
| 2025-09-14 | systemd --user タイマーで 1 分間隔更新 | cron よりもユーザー単位で制御しやすく、ログも集約できる |
| 2025-10-31 | Pi5／Window A 連携時は Dropbox JSON のスキーマを統一して運用する | 各クライアント（Window B/C/D）で表示内容を共通化するため |

---

## 7. 未対応課題・バックログ

- **優先度: 高**
  - Pi5 側 JSON 生成スクリプトを整備し、テスト用データと更新手順を共有する。
  - Dropbox 取得失敗時に通知（Slack／メール等）できる監視フローを設計する。
- **優先度: 中**
  - Wi‑Fi を時間限定で ON/OFF 切り替えする「バースト接続」機能。
  - 表示テーマ（列幅・配色・表題）を設定ファイル化し、フロア別テンプレートを切り替える。
- **優先度: 低**
  - CSV 入力サンプルと変換スクリプトの整備。
  - 画面ページングやアニメーション演出の検討。

課題を着手・完了した際は本書を更新し、完了内容を `HISTORY.md` に移して履歴化する。

---

## 8. 参照ドキュメント
- セットアップ手順: `docs/STEP_BY_STEP_SETUP.md`
- 更新・運用手順: `docs/APPLY_UPDATES.md`, `OPERATIONS.md`
- ドキュメント運用ルール: `docs/documentation-guidelines.md`
- 棚卸し索引: `docs/docs-index.md`
