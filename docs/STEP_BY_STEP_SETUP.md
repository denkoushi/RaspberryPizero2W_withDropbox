# リポジトリから Raspberry Pi に環境構築する手順（理由つき・ワンステップ）

対象リポジトリ：`https://github.com/denkoushi/RaspberryPizero2W_withDropbox`

目的：このリポジトリを使って **Raspberry Pi Zero 2 W** にサイネージ環境を構築できるようになる。  
構成：Dropbox の JSON を取得 → Python(Pillow) で PNG を生成 → feh で全画面表示。ブラウザは使いません。

> ドキュメントの役割分担は `docs/documentation-guidelines.md` を参照してください。

---

## 前提
- Raspberry Pi OS（64-bit、デスクトップ版）で起動していること
- ネットワークに接続できること（Wi‑Fi でも有線でも可）
- Dropbox の「直ダウンロード URL（末尾が `?dl=1`）」を用意できること

---

## STEP 0｜前準備（ネットと必要パッケージ）
**理由**：クローン・描画・表示に必要な道具（git / Pillow / 日本語フォント等）を最初に揃える。

    ping -c1 1.1.1.1
    sudo apt update
    sudo apt full-upgrade -y
    sudo apt install -y git feh python3-pil fonts-noto-cjk fonts-ipafont-gothic curl unclutter
    sudo fc-cache -f -v

---

## STEP 1｜リポジトリをホームにクローン
**理由**：以降の作業の“元”になるファイル一式を取得する。

    cd ~
    git clone https://github.com/denkoushi/RaspberryPizero2W_withDropbox.git
    cd RaspberryPizero2W_withDropbox
    find . -maxdepth 2 -type f | sort    # どんなファイルがあるか確認

---

## STEP 2｜Dropbox 直ダウンロード URL を設定
**理由**：どこから JSON を取得するかをスクリプトに教える。空のままだと取得できない。

1) 直ダウンロード URL の作り方  
   - Dropbox で `signage.json` を右クリック → 「リンクを作成」  
   - URL の末尾が `...?dl=0` の場合、`?dl=1` に変更（直ダウンロード）

2) スクリプトに設定

    nano signage/pull_signage.sh

   ファイル先頭の

    URL="https://www.dropbox.com/scl/fi/XXXX/signage.json?dl=1"

   を、あなたの URL に置き換える。保存（Ctrl+O → Enter）後、終了（Ctrl+X）。

3) 反映を確認

    grep -n '^URL=' signage/pull_signage.sh

---

## STEP 3｜実行場所へ配置（ランタイム一式）
**理由**：実行に期待される定位置（`/usr/local/bin`、`~/.config/systemd/user` など）に置く。

    # 表示・描画スクリプト群
    mkdir -p ~/signage
    cp signage/render_signage.py ~/signage/
    cp signage/tools.json       ~/signage/
    chmod +x ~/signage/render_signage.py

    # 取得スクリプトを共通パスへ
    sudo cp signage/pull_signage.sh /usr/local/bin/
    sudo chmod +x /usr/local/bin/pull_signage.sh

    # systemd --user（定期実行ユニット）
    mkdir -p ~/.config/systemd/user
    cp systemd-user/signage-pull.service ~/.config/systemd/user/
    cp systemd-user/signage-pull.timer   ~/.config/systemd/user/
    systemctl --user daemon-reload

---

## STEP 4｜初回だけ PNG を1回生成しておく
**理由**：表示用画像 `frame.png` を先に作ると、ビューワ（feh）が確実に起動できる。

    systemctl --user start signage-pull.service
    ls -l --full-time "$HOME/signage/frame.png"   # 生成されていればOK

---

## STEP 5｜定期取得（毎分）を有効化
**理由**：手作業での取得をやめ、Pi に任せる。

    systemctl --user enable --now signage-pull.timer
    systemctl --user status signage-pull.timer --no-pager   # active (waiting) ならOK

※ 取得間隔の変更（例：5分=300s、1時間=3600s）

    nano ~/.config/systemd/user/signage-pull.timer
    # OnUnitActiveSec=60s → 300s や 3600s に変更
    systemctl --user daemon-reload
    systemctl --user restart signage-pull.timer

---

## STEP 6｜ログイン時に全画面表示（feh）を自動起動
**理由**：電源を入れたら自動でサイネージ表示になるようにする。

    mkdir -p ~/.config/autostart
    cp autostart/signage-view.desktop ~/.config/autostart/

（すぐ確認したい場合）

    pkill -x feh || true
    feh --quiet --fullscreen --hide-pointer --reload 5 --auto-zoom "$HOME/signage/frame.png"

---

## STEP 7｜動作テスト（更新が反映されるか）
**理由**：取得 → 描画 → 表示の流れがつながっているか確かめる。

A) Dropbox 上の `signage.json` を書き換える（本番想定）  
B) すぐ試す：ローカルのダミー JSON を編集して描画

    nano ~/signage/tools.json
    # 例: "status": "OK" → "status": "CHECK" に変更して保存

    /home/$USER/signage/render_signage.py ~/signage/tools.json ~/signage/frame.png

画面の表が変われば成功。

---

## STEP 8｜運用（停止・再開・確認）
**理由**：現場で止めたい／再開したい／状態を見たい時に使う最小コマンド。

停止（今だけ止める）

    pkill -x feh || true
    systemctl --user stop signage-pull.timer
    systemctl --user stop signage-pull.service

再開（自動取得を復活）

    systemctl --user enable --now signage-pull.timer
    feh --quiet --fullscreen --hide-pointer --reload 5 --auto-zoom "$HOME/signage/frame.png"

状態確認

    systemctl --user status signage-pull.timer --no-pager
    journalctl --user -u signage-pull.service -n 50 -e

詳細版はレポ内の `OPERATIONS.md` も参照。

---

## トラブルシュート（要点）
- 日本語が表示されない  
  → フォントを再インストールする：  
    `sudo apt install -y fonts-noto-cjk fonts-ipafont-gothic && sudo fc-cache -f -v`
- 画像が更新されない  
  → 取得ログを確認：  
    `journalctl --user -u signage-pull.service -n 50 -e`  
  → タイマーの状態を確認：  
    `systemctl --user status signage-pull.timer --no-pager`
- 表示が重い  
  → 行数やフォントサイズは `~/signage/render_signage.py` の `max_rows`、`font_*` を調整。

---

## 次の一歩（任意）
- 取得間隔の最適化（5分/1時間など）
- 時間帯だけネット接続する「バースト接続」（Wi‑Fi ON→取得→OFF）
- 見た目の調整（列幅、色、アイコン）
- Power Automate で Dropbox の `signage.json` を自動更新（本番化）

この手順を上から順に実行すれば、**別の Raspberry Pi でも同じ環境を再現**できます。
