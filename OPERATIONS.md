# 運用メモ（停止・再開の方法）

Raspberry Pi 上で動作中のサイネージ（feh の全画面表示＋Dropbox 定期取得）を  
**今すぐ止める**／**今後も起動しないようにする**／**再開する**ための手順です。  
※ すべて Raspberry Pi のターミナルで実行します。

---

## 1) 一時停止（今すぐ止める）

画面表示と自動取得を**その場で停止**します。再ログイン／再起動すると復活する可能性があります。

- 画面表示（feh）を止める  
    pkill -x feh || true

- 自動取得（systemd --user タイマー）を止める  
    systemctl --user stop signage-pull.timer  
    systemctl --user stop signage-pull.service

---

## 2) 自動起動を無効化（今後も起動しないようにする）

次回ログイン以降も立ち上がらないようにします。

- ログイン時の全画面起動（autostart）を無効化  
  ※ 削除はせず、拡張子を変えて無効化します。元に戻すのも簡単です。  
    mv ~/.config/autostart/signage-view.desktop ~/.config/autostart/signage-view.desktop.off

- 自動取得のタイマーを無効化  
    systemctl --user disable --now signage-pull.timer

---

## 3) 状態確認（任意）

- タイマーの状態を確認  
    systemctl --user status signage-pull.timer --no-pager

- feh が動いていないことを確認  
    pgrep -a feh || echo "feh は動いていません"

---

## 4) 再開（元に戻す）

- 画面表示の自動起動を再有効化  
    mv ~/.config/autostart/signage-view.desktop.off ~/.config/autostart/signage-view.desktop

- 自動取得のタイマーを再有効化  
    systemctl --user enable --now signage-pull.timer

- 今すぐ1回だけ取得して PNG を更新（任意）  
    systemctl --user start signage-pull.service

---

## 5) 参考（過去に service 方式で起動したことがある場合のみ）

このリポジトリでは autostart 方式を採用していますが、過去の検証で  
`systemd` のサービスを作っていた場合は、下記で無効化できます（存在しない場合は無視されます）。

> ドキュメントの役割分担は `docs/documentation-guidelines.md` を参照してください。

- 旧サービスの停止と無効化  
    sudo systemctl disable --now signage-view.service  || true  
    sudo systemctl disable --now signage-http.service  || true

---

## 6) まとめ（ワンライナー）

- **今すぐ全部止める（表示＋自動取得）**  
    pkill -x feh || true; systemctl --user stop signage-pull.timer; systemctl --user stop signage-pull.service

- **すべて再開（自動起動＋定期取得）**  
    mv ~/.config/autostart/signage-view.desktop.off ~/.config/autostart/signage-view.desktop 2>/dev/null || true; systemctl --user enable --now signage-pull.timer
