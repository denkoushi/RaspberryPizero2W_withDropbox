#!/usr/bin/env python3
import sys, os, json, datetime, csv
from PIL import Image, ImageDraw, ImageFont

# 入出力（JSONは items 形式 or カラム型JSON（header+rows）どちらでもOK）
HOME = os.environ.get("HOME", "/home/pi")
in_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, "signage", "tools.json")
out_png = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HOME, "signage", "frame.png")

# キャンバス
W, H = 1280, 720
MARGIN = 40

# 日本語フォント
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

# ---- データ読込（items形式 or カラム型JSON）---------------------------------
def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 既存：{"updatedAt": "...", "items":[{"id":..,"model":..,"lot":..,"status":..}, ...]}
    if isinstance(raw, dict) and "items" in raw:
        return {
            "updatedAt": raw.get("updatedAt"),
            "items": list(raw.get("items") or []),
        }

    # カラム型：{"updatedAt":"...","header":["id","model","lot","status"],"rows":[[...],[...],...]}
    if isinstance(raw, dict) and "header" in raw and "rows" in raw:
        header = [str(h).strip().lower() for h in (raw.get("header") or [])]
        rows   = raw.get("rows") or []
        # 欲しい列（小文字）
        want = {"id", "model", "lot", "status"}

        # header から列インデックスを作る
        idx = {k: (header.index(k) if k in header else None) for k in want}

        items = []
        for row in rows:
            if isinstance(row, (list, tuple)):
                def at(k):
                    i = idx[k]
                    return str(row[i]) if (i is not None and i < len(row)) else ""
                items.append({
                    "id": at("id"),
                    "model": at("model"),
                    "lot": at("lot"),
                    "status": at("status"),
                })
            elif isinstance(row, dict):
                # rows が dict の場合も一応対応（キーは小文字で見る）
                rd = {str(k).strip().lower(): v for k, v in row.items()}
                def pick(k):
                    return str(rd.get(k, ""))
                items.append({
                    "id": pick("id"),
                    "model": pick("model"),
                    "lot": pick("lot"),
                    "status": pick("status"),
                })
        return {"updatedAt": raw.get("updatedAt"), "items": items}

    # どれでもなければ空
    return {"updatedAt": datetime.datetime.now().astimezone().isoformat(), "items": []}

try:
    data = load_data(in_path)
except Exception:
    data = {"updatedAt": "-", "items": []}

# ---- 表示ユーティリティ ------------------------------------------------------
def fmt_local(ts):
    try:
        s = str(ts)
        if s.endswith("Z"): s = s[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(s)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)

def status_color(s):
    t = str(s or "").upper()
    if "NG" in t: return (220, 0, 0)
    if "CHECK" in t or "WARN" in t: return (180, 110, 0)
    if "OK" in t: return (0, 140, 0)
    return (0, 0, 0)

def ellipsis_to_fit(draw, text, font, max_w):
    limit = max_w - 16
    if limit <= 0: return ""
    try: w = draw.textlength(text, font=font)
    except Exception: w = draw.textbbox((0,0), text, font=font)[2]
    if w <= limit: return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        t = text[:mid] + ell
        try: tw = draw.textlength(t, font=font)
        except Exception: tw = draw.textbbox((0,0), t, font=font)[2]
        if tw <= limit: lo = mid + 1
        else: hi = mid
    return text[:max(lo-1,0)] + ell

# ---- 描画 ---------------------------------------------------------------------
img = Image.new("RGB", (W, H), (255, 255, 255))
drw = ImageDraw.Draw(img)

drw.text((MARGIN, 20), "工具モニタ", fill=(0,0,0), font=font_title)
drw.text((MARGIN, 90), f"最終更新: {fmt_local(data.get('updatedAt','-'))}", fill=(0,0,0), font=font_ts)

x0, y0 = MARGIN, 140
cols = [("ID", 120), ("Model", 420), ("Lot", 300), ("Status", 300)]
row_h = 40
max_rows = 12
table_w = sum(w for _, w in cols)

# ヘッダ
drw.rectangle([x0, y0, x0 + table_w, y0 + row_h], fill=(240,240,240))
x = x0
for name, w in cols:
    drw.text((x + 8, y0 + 8), name, fill=(0,0,0), font=font_cell)
    x += w

# 外枠
drw.rectangle([x0, y0, x0 + table_w, y0 + row_h * (max_rows + 1)], outline=(180,180,180), width=1)

# データ行
y = y0 + row_h
items = data.get("items", [])[:max_rows]
for i, it in enumerate(items):
    if i % 2 == 1:
        drw.rectangle([x0, y, x0 + table_w, y + row_h], fill=(248,248,248))
    drw.line([(x0, y), (x0 + table_w, y)], fill=(220,220,220), width=1)
    x = x0
    vals = [str(it.get("id","")), str(it.get("model","")), str(it.get("lot","")), str(it.get("status",""))]
    for (name, w), val in zip(cols, vals):
        txt = ellipsis_to_fit(drw, val, font_cell, w)
        fill = status_color(val) if name == "Status" else (0,0,0)
        drw.text((x + 8, y + 8), txt, fill=fill, font=font_cell)
        x += w
    y += row_h

img.save(out_png, "PNG", optimize=True)
