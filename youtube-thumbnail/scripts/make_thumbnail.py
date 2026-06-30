#!/usr/bin/env python3
"""흰 배경 + 검은 글씨 썸네일 문구 이미지 생성기 (1280x720, 3종).

사용:
  python make_thumbnail.py \
    --copies "서브카피1|헤드카피1" "서브카피2|헤드카피2" "서브카피3|헤드카피3" \
    --labels "1안설명" "2안설명" "3안설명" \
    --out-dir ./out
"""
import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720


def find_cjk_font():
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Bold.otf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


FONT_PATH = find_cjk_font()
if FONT_PATH is None:
    sys.exit(
        "한글 폰트를 찾지 못했습니다.\n"
        " - Mac: 기본 내장 폰트가 있어야 합니다\n"
        " - Linux: apt-get install -y fonts-noto-cjk"
    )


def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size, index=0)
    except Exception:
        return ImageFont.truetype(FONT_PATH, size)


def fit_font(draw, text, max_w, start_size, min_size=36):
    size = start_size
    while size > min_size:
        f = get_font(size)
        bbox = draw.textbbox((0, 0), text, font=f)
        if bbox[2] - bbox[0] <= max_w:
            return f, size
        size -= 4
    return get_font(min_size), min_size


def draw_centered(draw, y, text, font, fill=(0, 0, 0)):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (W - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def make_image(sub_copy, head_copy, label, out_path):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    max_w = W - 160

    sub_font, _ = fit_font(draw, sub_copy,  max_w, 72)
    head_font, _ = fit_font(draw, head_copy, max_w, 128)

    sub_bbox  = draw.textbbox((0, 0), sub_copy,  font=sub_font)
    head_bbox = draw.textbbox((0, 0), head_copy, font=head_font)
    sub_h  = sub_bbox[3]  - sub_bbox[1]
    head_h = head_bbox[3] - head_bbox[1]

    gap = 36
    sep_h = 3
    total_h = sub_h + gap + sep_h + gap + head_h
    top = (H - total_h) // 2

    draw_centered(draw, top, sub_copy, sub_font)

    sep_y = top + sub_h + gap
    draw.rectangle([W // 2 - 140, sep_y, W // 2 + 140, sep_y + sep_h], fill=(0, 0, 0))

    draw_centered(draw, sep_y + sep_h + gap, head_copy, head_font)

    label_font = get_font(26)
    draw.text((40, H - 50), label, font=label_font, fill=(180, 180, 180))

    img.save(out_path)
    print(f"저장: {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copies", nargs=3, required=True,
                    help="'서브카피|헤드카피' 형식으로 3개")
    ap.add_argument("--labels", nargs=3, default=["1안", "2안", "3안"])
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    for i, (copy_str, label) in enumerate(zip(a.copies, a.labels), 1):
        parts = copy_str.split("|", 1)
        if len(parts) != 2:
            sys.exit(f"--copies 형식 오류: '{copy_str}' → '서브카피|헤드카피' 형식이어야 합니다.")
        sub, head = parts
        out_path = os.path.join(a.out_dir, f"thumbnail_{i}.png")
        make_image(sub.strip(), head.strip(), label, out_path)

    print("완료.")


if __name__ == "__main__":
    main()
