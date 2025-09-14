# Raspberry Pi Zero 2 W × Dropbox サイネージ（ブラウザ非使用）

Dropbox 上の JSON を Raspberry Pi Zero 2 W で取得し、Python(Pillow) で PNG を生成し、軽量ビューア feh で全画面表示します。  
Chromium を使わない構成のため軽量で、オフライン時も最後の PNG を表示し続けます。

---

## フォルダ構成（この README を保存後に、他ファイルを追加します）

    RaspberryPizero2W_withDropbox/
    ├─ README.md
    ├─ signage/
    │  ├─ render_signage.py        # JSON→PNG 描画（日本語対応／省略記号／ゼブラ行）
    │  ├─ pull_signage.sh          # Dropbox 取得→検証→PNG生成（URL差し替え必須）
    │  └─ tools.json               # 動作確認用ダミー
    ├─ systemd-user/
    │  ├─ signage-pull.service     # 取得スクリプトを1回実行（oneshot）
    │  └─ signage-pull.timer       # 定期実行（初期: 1分ごと）
    └─ autostart/
       └─ signage-view.desktop     # ログイン時に feh を全画面起動

---

## 事前準備：Dropbox の直ダウンロード URL（?dl=1）
1. Dropbox で `signage.json` を右クリック → 「リンクを作成」  
2. 取得 URL の末尾が `...?dl=0` の場合、`?dl=1` に変更（直ダウンロード）※。 ?dl=1 のリンクはURLを知っている人なら誰でもアクセスできます。公開が不安な場合は「アプリフォルダ」権限の共有リンクを使う・リンクを定期的に再発行する等を検討してください。


---

## Raspberry Pi 側セットアップ（そのまま貼り付けて実行可能）

### 1) 必要パッケージ
    sudo apt update
    sudo apt full-upgrade -y
    sudo apt install -y feh python3-pil fonts-noto-cjk fonts-ipafont-gothic curl unclutter
    sudo fc-cache -f -v

### 2) リポジトリを取得
    cd ~
    git clone https://github.com/denkoushi/RaspberryPizero2W_withDropbox.git
    cd RaspberryPizero2W_withDropbox

### 3) ファイルを所定の場所へ配置
    # 表示・描画
    mkdir -p ~/signage
    cp signage/render_signage.py ~/signage/
    cp signage/tools.json       ~/signage/
    chmod +x ~/signage/render_signage.py

    # 取得スクリプト（システム共通パス）
    sudo cp signage/pull_signage.sh /usr/local/bin/
    sudo chmod +x /usr/local/bin/pull_signage.sh

    # systemd --user（定期実行）
    mkdir -p ~/.config/systemd/user
    cp systemd-user/signage-pull.service ~/.config/systemd/user/
    cp systemd-user/signage-pull.timer   ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now signage-pull.timer
    systemctl --user status signage-pull.timer --no-pager

### 3.5) 初回 PNG を生成（feh を設定する前に1回だけ実行）
    systemctl --user start signage-pull.service
    ls -l --full-time "$HOME/signage/frame.png"    # 生成されたことを確認

### 4) feh をログイン時に全画面起動
    mkdir -p ~/.config/autostart
    cp autostart/signage-view.desktop ~/.config/autostart/

    # すぐ試す（任意）
    pkill -x feh || true
    feh --quiet --fullscreen --hide-pointer --reload 5 --auto-zoom "$HOME/signage/frame.png"

### 5) Dropbox URL を設定（重要）
`/usr/local/bin/pull_signage.sh` の先頭 `URL="..."` を、あなたの共有リンク（末尾が `?dl=1`）に置き換えます。

    sudo nano /usr/local/bin/pull_signage.sh
    # 保存: Ctrl+O → Enter / 終了: Ctrl+X

### 6) 動作確認
    # 手動で1回実行
    systemctl --user start signage-pull.service
    systemctl --user status signage-pull.service --no-pager

    # PNG の更新時刻
    ls -l --full-time "$HOME/signage/frame.png"

### 7) 取得間隔の変更（任意）
`~/.config/systemd/user/signage-pull.timer` の `OnUnitActiveSec=60s` を `300s`（5分）や `3600s`（1時間）に変更。

    nano ~/.config/systemd/user/signage-pull.timer
    systemctl --user daemon-reload
    systemctl --user restart signage-pull.timer

---

## nano の基本操作
- 開く：`nano <ファイル名>`  
- 貼り付け：右クリック または Shift+Insert  
- 保存：Ctrl + O → Enter  
- 終了：Ctrl + X  

---

## トラブル時の確認
- 日本語が正しく出ない：
  
      sudo apt install -y fonts-noto-cjk fonts-ipafont-gothic && sudo fc-cache -f -v

- 画像が更新されない：
  
      journalctl --user -u signage-pull.service -n 50 -e

- 表示を軽くしたい：  
  行数やフォントは `signage/render_signage.py` 内の定数を調整
