# AGENTS.md

RaspberryPizero2W_withDropbox リポジトリで作業するエージェント向けの指針です。新しいスレッドや自動化タスクを開始するときは、最初に確認してください。

## 1. リポジトリ概要
- ルートパス: `/Users/tsudatakashi/RaspberryPizero2W_withDropbox`
- 主要ドキュメント:
  - `README.md`: プロジェクト概要とドキュメント案内
  - `docs/STEP_BY_STEP_SETUP.md`: 初期セットアップ手順
  - `docs/APPLY_UPDATES.md`: GitHub から更新を取り込む手順
  - `OPERATIONS.md`: 停止・再開などの日常運用コマンド
  - `docs/requirements.md`: 要件・将来課題
  - `docs/documentation-guidelines.md`: ドキュメントの役割と更新ルール

## 2. 作業フロー
1. `git status -sb` でブランチとローカル変更を確認する。
2. 上記ドキュメントを読み、最新の手順・要件に整合しているか確認する。
3. 不明点や追加要件は作業前にユーザーへ確認し、回答を `docs/requirements.md` に追記する。
4. 小規模変更は `main` に直接コミット。リスクの高い変更や影響範囲が大きい場合はブランチを切り、検証後にマージする。
5. スクリプトや手順を更新した場合は、関連ドキュメント（README、STEP_BY_STEP_SETUP 等）を忘れずに更新する。

## 3. コマンド提示ルール
- すべて日本語で説明する。
- コマンドはコードブロックで提示し、以下をセットで示す:
  1. 実行コマンド
  2. 期待される結果の目安
  3. エラー時の診断コマンド
  4. 必要であれば再起動・状態確認・ロールバック手順

## 4. エラー対応
- エラーが起こったら原因と復旧手順を提示し、可能であれば予防策も述べる。
- ロールバックの判断に迷う場合はユーザーへ確認する。

## 5. 提案スタイル
- 複数案を示し、推奨案と理由、トレードオフを明示する。
- 決定事項は `docs/requirements.md` 等に反映し、関連文書も更新する。

## 6. 参考リンク
- ドキュメント運用ガイドライン: `docs/documentation-guidelines.md`
- 初期セットアップ: `docs/STEP_BY_STEP_SETUP.md`
- 更新手順: `docs/APPLY_UPDATES.md`
- 要件・ロードマップ: `docs/requirements.md`
