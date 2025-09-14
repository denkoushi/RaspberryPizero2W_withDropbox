#!/usr/bin/env python3
import sys, os, json, datetime
from PIL import Image, ImageDraw, ImageFont

# 入出力
HOME = os.environ.get("HOME", "/home/pi")
in_json = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, "signage", "tools.json")
out_png = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HOME, "signage", "frame.png")

# キャンバス
W, H = 1280, 720
MARGIN = 40

# 日本語フォント読み込み
def load_font(size):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansJP-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = load_font(36)
font_ts    = load_font(20)
font_cell  = load_font(22)

# JSON読み込み
data = {"updatedAt": "-", "items": []}
try:
    with open(in_json, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    pass

# 時刻整形（ローカル）
def fmt_local(ts):
    try:
        s = str(ts)
        if s.endswith("Z"): s = s[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(s)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)

# ステータス色
def status_color(s):
    t = str(s or "").upper()
    if "NG" in t:     return (220, 0, 0)
    if "CHECK" in t or "WARN" in t: return (180, 110, 0)
    if "OK" in t:     return (0, 140, 0)
    return (0, 0, 0)

# 幅に収める（…で省略）
def ellipsis_to_fit(draw, text, font, max_w):
    limit = max_w - 16
    if limit <= 0: return ""
    try:
        w = draw.textlength(text, font=font)
    except Exception:
        w = draw.textbbox((0,0), text, font=font)[2]
    if w <= limit:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        t = text[:mid] + ell
        try:
            tw = draw.textlength(t, font=font)
        except Exception:
            tw = draw.textbbox((0,0), t, font=font)[2]
        if tw <= limit:
            lo = mid + 1
        else:
            hi = mid
    return text[:max(lo-1,0)] + ell

# 描画
img = Image.new("RGB", (W, H), (255, 255, 255))
drw = ImageDraw.Draw(img)

# タイトル・時刻
drw.text((MARGIN, 20), "工具モニタ", fill=(0, 0, 0), font=font_title)
drw.text((MARGIN, 90), f"最終更新: {fmt_local(data.get('updatedAt','-'))}", fill=(0,0,0), font=font_ts)

# テーブル
x0, y0 = MARGIN, 140
cols = [("ID", 120), ("Model", 420), ("Lot", 300), ("Status", 300)]
row_h = 40
max_rows = 12
table_w = sum(w for _, w in cols)

# ヘッダ
drw.rectangle([x0, y0, x0 + table_w, y0 + row_h], fill=(240, 240, 240))
x = x0
for name, w in cols:
    drw.text((x + 8, y0 + 8), name, fill=(0, 0, 0), font=font_cell)
    x += w

# 外枠
drw.rectangle([x0, y0, x0 + table_w, y0 + row_h * (max_rows + 1)], outline=(180,180,180), width=1)

# データ行（ゼブラ + 省略）
y = y0 + row_h
items = data.get("items", [])[:max_rows]
for i, it in enumerate(items):
    if i % 2 == 1:
        drw.rectangle([x0, y, x0 + table_w, y + row_h], fill=(248, 248, 248))
    drw.line([(x0, y), (x0 + table_w, y)], fill=(220, 220, 220), width=1)
    x = x0
    vals = [str(it.get("id","")), str(it.get("model","")), str(it.get("lot","")), str(it.get("status",""))]
    for (name, w), val in zip(cols, vals):
        txt = ellipsis_to_fit(drw, val, font_cell, w)
        fill = status_color(val) if name == "Status" else (0, 0, 0)
        drw.text((x + 8, y + 8), txt, fill=fill, font=font_cell)
        x += w
    y += row_h

img.save(out_png, "PNG", optimize=True)
