# 更新手順（GitHub の変更を Raspberry Pi に反映する）

この文書は、GitHub 上のファイル更新を **Raspberry Pi に取り込み（pull）**、その内容を **運用で使う場所へ反映（上書きコピー）** する具体的な手順をまとめたものです。  
初学者向けに、コマンドには短い説明を付けています。

> ドキュメントの役割分担は `docs/documentation-guidelines.md` を参照してください。

---

## 用語と場所（最重要ポイント）

- **作業用のフォルダ** … GitHub から取得した内容が入る場所（ここで更新内容を受け取ります）
  - `~/RaspberryPizero2W_withDropbox/`
- **運用で使う場所** … 実際にサイネージが参照して動く場所（ここを上書きして反映します）
  - 取得スクリプト：`/usr/local/bin/pull_signage.sh`
  - 描画スクリプト：`~/signage/render_signage.py`
  - 入力データ（JSON）：`~/signage/tools.json`（Dropboxから取得）
  - 出力画像（PNG）：`~/signage/frame.png`（画面に表示）

> ポイント：**作業用**と**運用**は **別々に存在**します。  
> GitHub → 作業用フォルダ（pull） → 運用の場所（上書きコピー）という順で反映します。

---

## 最短手順（毎回同じ 3 ステップ）

> 下のブロックを **そのまま貼り付けて実行**して構いません。

```bash
set -e

# 1) 作業用のフォルダを最新化（初回は clone、2回目以降は pull）
cd ~
if [ -d ~/RaspberryPizero2W_withDropbox/.git ]; then
  cd ~/RaspberryPizero2W_withDropbox
  git fetch --quiet origin      # 更新の有無を取得
  git pull --ff-only            # 変更分だけ取り込み
else
  git clone https://github.com/denkoushi/RaspberryPizero2W_withDropbox.git
  cd ~/RaspberryPizero2W_withDropbox
fi

# 2) 運用の場所へ上書きコピー（ここで反映される）
mkdir -p "$HOME/signage"
install -m 755 -T signage/render_signage.py "$HOME/signage/render_signage.py"      # 描画スクリプト
sudo   install -m 755 -T signage/pull_signage.sh /usr/local/bin/pull_signage.sh   # 取得スクリプト

# 3) 新しい実体で 1 回だけ実行して確認（取得→描画）
systemctl --user start signage-pull.service
systemctl --user status signage-pull.service --no-pager   # Status=0/SUCCESS を目安に
ls -l --full-time "$HOME/signage/frame.png"               # PNG の更新時刻が「今」に近いか確認
