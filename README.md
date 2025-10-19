# Raspberry Pi Zero 2 W × Dropbox サイネージ（ブラウザ非使用）

Dropbox 上の JSON を取得し、Python (Pillow) で PNG を生成して `feh` で全画面表示する軽量サイネージです。Chromium を使わないため負荷が小さく、オフライン時も最後に生成した PNG を表示し続けます。

## ドキュメント一覧
- 初期セットアップ手順: `docs/STEP_BY_STEP_SETUP.md`
- 運用時の更新手順 (Git Pull): `docs/APPLY_UPDATES.md`
- 一時停止・再開などの運用メモ: `OPERATIONS.md`
- 要件・今後の課題: `docs/requirements.md`
- ドキュメント運用ルール: `docs/documentation-guidelines.md`
- エージェント向け指針: `docs/AGENTS.md`

## セットアップの流れ（概要）
1. 必要パッケージをインストールし、リポジトリをクローン。
2. `signage/pull_signage.sh` に Dropbox の直ダウンロード URL (`?dl=1`) を設定。
3. スクリプトと systemd --user タイマーを所定の場所に配置して定期取得を有効化。
4. `autostart/signage-view.desktop` を配置してログイン時に `feh` を全画面起動。
5. 更新や調整が必要になった場合は `docs/APPLY_UPDATES.md` と `OPERATIONS.md` を参照。

詳細なコマンドやトラブルシュートは `docs/STEP_BY_STEP_SETUP.md` に集約しています。

## 他システムとの連携方針
- **Window A（tool-management-system02）**: `part_locations` や工程情報を提供する API/CSV との連携を計画中。サイネージに所在・作業進捗を表示する場合は Window A 側の JSON 生成プロセスと整合させる。
- **OnSiteLogistics（ハンディリーダ）**: Window A の `POST /api/v1/scans` で登録されたデータを間接的に参照し、Dropbox 経由でサイネージへ配信する。フォーマット確定後は `signage/render_signage.py` のテンプレートに反映する。
- **Window B（DocumentViewer）**: 要領書／計画データの更新状況を通知するためのメタ情報を取り込む構想あり。必要に応じて Dropbox JSON に追加フィールドを設計する。

## フォルダ構成
```
RaspberryPizero2W_withDropbox/
├─ README.md
├─ docs/
│  ├─ STEP_BY_STEP_SETUP.md    # 初期構築手順
│  ├─ APPLY_UPDATES.md         # GitHub から更新を取り込む手順
│  └─ documentation-guidelines.md
├─ signage/
│  ├─ render_signage.py        # JSON → PNG 描画スクリプト
│  ├─ pull_signage.sh          # Dropbox 取得 → PNG 生成
│  └─ tools.json               # 動作確認用ダミーデータ
├─ systemd-user/               # systemd --user 用ユニット
└─ autostart/                  # デスクトップ自動起動の設定
```

## ライセンス
ライセンスの扱いについては管理者に確認してください。
