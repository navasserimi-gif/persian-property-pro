from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
import urllib.request

app = Flask(__name__)

# Templates
TEMPLATES = {
    "luxury":   {"bg": (10, 31, 62),    "accent": (212, 169, 42),  "text": (255,255,255), "sub": (212,169,42),  "item": (255,255,255), "desc": (147,197,253), "num_bg": (212,169,42), "num_text": (10,31,62),  "footer_bg": (212,169,42), "footer_text": (10,31,62)},
    "dark":     {"bg": (13, 13, 13),    "accent": (201, 162, 39),  "text": (255,255,255), "sub": (201,162,39),  "item": (255,255,255), "desc": (156,163,175), "num_bg": (201,162,39), "num_text": (17,17,17),  "footer_bg": (201,162,39), "footer_text": (17,17,17)},
    "modern":   {"bg": (21, 101, 192),  "accent": (255,255,255),   "text": (255,255,255), "sub": (187,222,251), "item": (255,255,255), "desc": (187,222,251), "num_bg": (255,255,255), "num_text": (21,101,192),"footer_bg": (255,255,255),"footer_text": (21,101,192)},
    "green":    {"bg": (6, 78, 59),     "accent": (16, 185, 129),  "text": (255,255,255), "sub": (110,231,183), "item": (255,255,255), "desc": (110,231,183), "num_bg": (16,185,129),  "num_text": (6,78,59),   "footer_bg": (16,185,129), "footer_text": (6,78,59)},
    "purple":   {"bg": (46, 16, 101),   "accent": (168, 85, 247),  "text": (255,255,255), "sub": (216,180,254), "item": (255,255,255), "desc": (216,180,254), "num_bg": (168,85,247),  "num_text": (255,255,255),"footer_bg": (168,85,247), "footer_text": (255,255,255)},
    "bold":     {"bg": (127, 29, 29),   "accent": (255, 214, 0),   "text": (255,255,255), "sub": (255,214,0),   "item": (255,255,255), "desc": (252,165,165), "num_bg": (255,214,0),   "num_text": (127,29,29), "footer_bg": (255,214,0),  "footer_text": (127,29,29)},
}

ICONS = {
    "luxury": "🏢", "dark": "💎", "modern": "🏙️",
    "green": "🌿", "purple": "⭐", "bold": "🔥"
}

def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + 2*radius, y1 + 2*radius], fill=fill)
    draw.ellipse([x2 - 2*radius, y1, x2, y1 + 2*radius], fill=fill)
    draw.ellipse([x1, y2 - 2*radius, x1 + 2*radius, y2], fill=fill)
    draw.ellipse([x2 - 2*radius, y2 - 2*radius, x2, y2], fill=fill)

def create_infographic(title, subtitle, points_raw, hashtags, account, template_name, musik):
    W, H = 1080, 1350
    T = TEMPLATES.get(template_name, TEMPLATES["luxury"])
    
    img = Image.new("RGB", (W, H), T["bg"])
    draw = ImageDraw.Draw(img)

    try:
        font_large  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_tiny   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_num    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        font_large = font_medium = font_small = font_tiny = font_num = ImageFont.load_default()

    # Header background
    draw_rounded_rect(draw, [0, 0, W, 220], 0, T["accent"])
    draw.rectangle([0, 180, W, 220], fill=T["accent"])

    # Account name
    draw.text((W//2, 40), account, font=font_tiny, fill=T["num_text"], anchor="mm")

    # Divider
    draw.rectangle([W//2 - 80, 65, W//2 + 80, 68], fill=T["num_text"])

    # Title
    title_lines = textwrap.wrap(title, width=22)
    y_title = 100
    for line in title_lines[:2]:
        draw.text((W//2, y_title), line, font=font_large, fill=T["num_text"], anchor="mm")
        y_title += 58

    # Subtitle
    draw.text((W//2, y_title + 10), f"— {subtitle} —", font=font_small, fill=T["num_text"], anchor="mm")

    # Points
    points = [p.strip() for p in points_raw.split('\n') if p.strip()]
    y_pos = 260

    for i, point in enumerate(points[:6]):
        parts = [p.strip() for p in point.split('|')]
        p_icon  = parts[0] if len(parts) > 0 else "📌"
        p_title = parts[1] if len(parts) > 1 else ""
        p_desc  = parts[2] if len(parts) > 2 else ""

        # Row background
        if i % 2 == 0:
            draw.rectangle([20, y_pos - 10, W - 20, y_pos + 110], fill=(*T["bg"], 80))

        # Number circle
        draw_rounded_rect(draw, [30, y_pos, 85, y_pos + 55], 27, T["num_bg"])
        draw.text((57, y_pos + 27), str(i+1), font=font_num, fill=T["num_text"], anchor="mm")

        # Icon box
        draw_rounded_rect(draw, [100, y_pos, 165, y_pos + 55], 10, (*T["accent"], 30))
        draw.text((132, y_pos + 27), p_icon, font=font_medium, fill=T["accent"], anchor="mm")

        # Title
        draw.text((185, y_pos + 10), p_title[:35], font=font_small, fill=T["item"])

        # Description
        desc_lines = textwrap.wrap(p_desc, width=42)
        for j, dl in enumerate(desc_lines[:2]):
            draw.text((185, y_pos + 48 + j * 28), dl, font=font_tiny, fill=T["desc"])

        # Separator line
        draw.rectangle([30, y_pos + 108, W - 30, y_pos + 110], fill=(*T["accent"], 60))

        y_pos += 150

    # Musik box
    musik_y = y_pos + 10
    draw_rounded_rect(draw, [20, musik_y, W - 20, musik_y + 80], 12, (*T["accent"], 25))
    draw.text((W//2, musik_y + 20), "🎵 Trending Musik", font=font_small, fill=T["accent"], anchor="mm")
    draw.text((W//2, musik_y + 55), musik[:60], font=font_tiny, fill=T["text"], anchor="mm")

    # Footer
    footer_y = H - 90
    draw.rectangle([0, footer_y, W, H], fill=T["footer_bg"])
    draw.text((W//2, footer_y + 28), account + "  •  PersianPropertyPro 🏢", font=font_small, fill=T["footer_text"], anchor="mm")
    draw.text((W//2, footer_y + 62), hashtags[:60], font=font_tiny, fill=T["footer_text"], anchor="mm")

    # Corner decorations
    acc = T["accent"]
    for pts in [[(20,60),(20,20),(60,20)], [(W-20,60),(W-20,20),(W-60,20)], [(20,H-60),(20,H-20),(60,H-20)], [(W-20,H-60),(W-20,H-20),(W-60,H-20)]]:
        draw.line(pts, fill=acc, width=4)

    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf

@app.route('/')
def home():
    return jsonify({"status": "PersianPropertyPro API running! 🏢"})

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        data = request.args
    else:
        data = request.json or request.form

    title    = data.get('title', 'راهنمای خرید ملک')
    subtitle = data.get('subtitle', 'نکات طلایی')
    points   = data.get('points', '🏦 | بررسی مالی | توان مالی خود را بررسی کنید\n📋 | بودجه‌بندی | هزینه‌های جانبی را لحاظ کنید\n🔍 | بازدید | ملک را حضوری بازدید کنید')
    hashtags = data.get('hashtags', '#خرید_ملک #آلمان #Immobilien')
    account  = data.get('account', '@PersianPropertyPro')
    template = data.get('template', 'luxury')
    musik    = data.get('musik', 'Unstoppable - Sia | Blinding Lights - The Weeknd')

    buf = create_infographic(title, subtitle, points, hashtags, account, template, musik)
    return send_file(buf, mimetype='image/png', as_attachment=False, download_name='infographic.png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
