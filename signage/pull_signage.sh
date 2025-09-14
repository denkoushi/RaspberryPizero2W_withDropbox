#!/usr/bin/env bash
set -euo pipefail

# ▼ここをあなたの Dropbox 共有リンク（末尾 ?dl=1）に置き換える
URL="https://www.dropbox.com/scl/fi/XXXX/signage.json?dl=1"

DIR="${HOME}/signage"
JSON="${DIR}/tools.json"
PNG="${DIR}/frame.png"
RENDER="${DIR}/render_signage.py"
TMP="${JSON}.tmp"

mkdir -p "$DIR"

# 取得（3回リトライ、TLS、短いタイムアウト）
curl --proto '=https' --tlsv1.2 --retry 3 --retry-delay 2 --max-time 20 \
     -fsSL "$URL" -o "$TMP"

# JSON妥当性チェック（壊れていれば採用しない）
python3 - <<'PY' "$TMP"
import json, sys
json.load(open(sys.argv[1], encoding='utf-8'))
PY

# 原子的置換
mv -f "$TMP" "$JSON"

# PNG 生成（失敗しても既存表示は維持）
"$RENDER" "$JSON" "$PNG" || true
