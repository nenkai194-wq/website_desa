import os
from PIL import Image, ImageDraw, ImageFont

def create_a4_poster():
    # A4 Dimensions at 150 DPI: 1240 x 1754
    width = 1240
    height = 1754
    
    # Create base image
    img = Image.new('RGB', (width, height), '#F8FAFC')
    draw = ImageDraw.Draw(img)

    # Load Windows Fonts
    font_bold = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg = "C:/Windows/Fonts/segoeui.ttf"
    font_arial_bd = "C:/Windows/Fonts/arialbd.ttf"
    font_arial = "C:/Windows/Fonts/arial.ttf"

    def get_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    f_title = get_font(font_bold, 52)
    f_header_top = get_font(font_bold, 24)
    f_header_sub = get_font(font_bold, 28)
    f_header_small = get_font(font_reg, 20)
    f_badge = get_font(font_bold, 22)
    f_desc_head = get_font(font_bold, 30)
    f_body = get_font(font_reg, 32)
    f_body_bold = get_font(font_bold, 32)
    f_card_title = get_font(font_bold, 24)
    f_card_desc = get_font(font_reg, 19)
    f_footer_bold = get_font(font_bold, 22)
    f_footer_reg = get_font(font_reg, 19)

    # 1. Background Header Banner (Deep Emerald Gradient Simulation)
    header_height = 360
    for y in range(header_height):
        # Gradient from #064E3B (6, 78, 59) to #0F766E (15, 118, 110)
        ratio = y / header_height
        r = int(6 + (15 - 6) * ratio)
        g = int(78 + (118 - 78) * ratio)
        b = int(59 + (110 - 59) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Gold Accent Stripe below header
    stripe_y = header_height
    draw.rectangle([(0, stripe_y), (width, stripe_y + 12)], fill='#D97706')
    draw.rectangle([(0, stripe_y + 12), (width, stripe_y + 16)], fill='#FBBF24')

    # Draw Header Pattern / Background Circles
    for r_circle in range(250, 450, 30):
        draw.arc([width - 200, -100, width + 400, 500], 0, 360, fill=(255, 255, 255, 15), width=2)
        draw.arc([-150, -50, 250, 350], 0, 360, fill=(255, 255, 255, 12), width=2)

    # 2. Add Logo Tasikmalaya in Header
    logo_path = 'static/images/logo_tasikmalaya.png'
    logo_w = 120
    logo_h = 137
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        logo_x = 90
        logo_y = 100
        img.paste(logo, (logo_x, logo_y), logo)
    else:
        logo_x = 90
        logo_y = 100

    # Header Texts
    text_x = logo_x + logo_w + 35
    draw.text((text_x, 102), "PEMERINTAH KABUPATEN TASIKMALAYA", fill='#A7F3D0', font=f_header_top)
    draw.text((text_x, 136), "KECAMATAN JATIWARAS • DESA PAPAYAN", fill='#FFFFFF', font=f_header_sub)
    draw.text((text_x, 180), "Portal Resmi Pelayanan Administrasi & Sistem Informasi Publik", fill='#D1FAE5', font=f_header_small)
    draw.line([(text_x, 218), (text_x + 560, 218)], fill='#F59E0B', width=3)
    draw.text((text_x, 230), "Alamat: Jl. Raya Papayan No. 01, Kec. Jatiwaras, Kab. Tasikmalaya 46181", fill='#99F6E4', font=get_font(font_reg, 17))

    # 3. Main Center Content Area
    content_y = 420

    # Badge: "PEMBERITAHUAN RESMI"
    badge_w = 420
    badge_h = 50
    badge_x = (width - badge_w) // 2
    badge_y = content_y
    draw.rounded_rectangle([(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)], radius=25, fill='#ECFDF5', outline='#10B981', width=2)
    badge_text = "📢 PEMBERITAHUAN RESMI PENGUNJUNG"
    b_box = draw.textbbox((0, 0), badge_text, font=f_badge)
    b_text_x = badge_x + (badge_w - (b_box[2] - b_box[0])) // 2
    draw.text((b_text_x, badge_y + 11), badge_text, fill='#065F46', font=f_badge)

    # Main Title: "Selamat Datang di Website Uji Coba"
    title_text = "Selamat Datang di Website Uji Coba"
    t_box = draw.textbbox((0, 0), title_text, font=f_title)
    t_x = (width - (t_box[2] - t_box[0])) // 2
    title_y = badge_y + 75
    draw.text((t_x, title_y), title_text, fill='#0F172A', font=f_title)

    # Decorative underline for Title
    draw.line([(t_x + 80, title_y + 75), (t_x + (t_box[2] - t_box[0]) - 80, title_y + 75)], fill='#059669', width=4)
    draw.ellipse([(width//2 - 5, title_y + 73), (width//2 + 5, title_y + 83)], fill='#D97706')

    # 4. Large Notice Card Container (Kotak Pengumuman Utama)
    card_margin = 85
    card_x1 = card_margin
    card_x2 = width - card_margin
    card_y1 = title_y + 115
    card_y2 = card_y1 + 450

    # Card Drop Shadow simulation
    draw.rounded_rectangle([(card_x1 + 4, card_y1 + 4), (card_x2 + 4, card_y2 + 4)], radius=28, fill='#E2E8F0')
    # Card Body
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=28, fill='#FFFFFF', outline='#CBD5E1', width=2)

    # Card Top Accent Band
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y1 + 80)], radius=28, fill='#FEF3C7')
    draw.rectangle([(card_x1, card_y1 + 40), (card_x2, card_y1 + 80)], fill='#FEF3C7')
    draw.line([(card_x1, card_y1 + 80), (card_x2, card_y1 + 80)], fill='#F59E0B', width=2)

    # Card Header Text
    card_head_text = "⚠️ INFORMASI PENTING / DISCLAIMER"
    draw.text((card_x1 + 40, card_y1 + 24), card_head_text, fill='#92400E', font=f_desc_head)

    # Body Paragraph Requested by User:
    # "website ini adalah website uji coba hanya untuk keperluan promosi, simulasi dan konten didalamnya hanya fiktif belaka, apabila ada kesamaan nama, alamat dan hal lainya hanya kebetulan saja. Terimakasih."
    para_lines = [
        "Website ini adalah website uji coba hanya untuk keperluan",
        "promosi, simulasi dan konten didalamnya hanya fiktif belaka,",
        "apabila ada kesamaan nama, alamat dan hal lainnya",
        "hanya kebetulan saja.",
        "",
        "Terimakasih."
    ]

    body_start_y = card_y1 + 125
    for i, line in enumerate(para_lines):
        curr_y = body_start_y + (i * 48)
        if line == "Terimakasih.":
            draw.text((card_x1 + 45, curr_y + 10), line, fill='#047857', font=get_font(font_bold, 36))
        else:
            draw.text((card_x1 + 45, curr_y), line, fill='#334155', font=f_body)

    # 5. Three Visual Icon Feature Blocks (Fitur Penjelas)
    block_y = card_y2 + 45
    block_w = (width - (card_margin * 2) - 40) // 3
    block_h = 240

    features = [
        {
            "icon": "🛡️",
            "title": "Status Sistem",
            "desc": "Lingkungan server simulasi & demo interaktif",
            "color": "#EFF6FF",
            "border": "#BFDBFE",
            "text_color": "#1E40AF"
        },
        {
            "icon": "🧪",
            "title": "Data Uji Coba",
            "desc": "Konten & pengaduan contoh fiktif belaka",
            "color": "#FEF3C7",
            "border": "#FDE68A",
            "text_color": "#92400E"
        },
        {
            "icon": "🌐",
            "title": "Fungsi Layanan",
            "desc": "Eksplorasi modul surat & profil wilayah desa",
            "color": "#ECFDF5",
            "border": "#A7F3D0",
            "text_color": "#065F46"
        }
    ]

    for idx, feat in enumerate(features):
        bx1 = card_margin + idx * (block_w + 20)
        bx2 = bx1 + block_w
        by1 = block_y
        by2 = by1 + block_h

        # Shadow
        draw.rounded_rectangle([(bx1 + 3, by1 + 3), (bx2 + 3, by2 + 3)], radius=20, fill='#E2E8F0')
        # Block Box
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=20, fill=feat['color'], outline=feat['border'], width=2)

        # Icon / Header
        draw.text((bx1 + 25, by1 + 25), feat['icon'], font=get_font(font_bold, 38))
        draw.text((bx1 + 25, by1 + 80), feat['title'], fill=feat['text_color'], font=f_card_title)
        
        # Wrapped Desc
        words = feat['desc'].split()
        l1 = " ".join(words[:4])
        l2 = " ".join(words[4:])
        draw.text((bx1 + 25, by1 + 125), l1, fill='#475569', font=f_card_desc)
        if l2:
            draw.text((bx1 + 25, by1 + 155), l2, fill='#475569', font=f_card_desc)

    # 6. Official Stamp / Badge Graphic in Bottom Right of Content
    stamp_cx = width - card_margin - 140
    stamp_cy = block_y + block_h + 90
    stamp_r = 75
    # Outer dashed circle
    draw.ellipse([(stamp_cx - stamp_r, stamp_cy - stamp_r), (stamp_cx + stamp_r, stamp_cy + stamp_r)], outline='#059669', width=3)
    draw.ellipse([(stamp_cx - stamp_r + 6, stamp_cy - stamp_r + 6), (stamp_cx + stamp_r - 6, stamp_cy + stamp_r - 6)], outline='#10B981', width=1)
    stamp_f_bold = get_font(font_bold, 13)
    stamp_f_center = get_font(font_bold, 18)
    draw.text((stamp_cx - 48, stamp_cy - 36), "★ PEMERINTAH ★", fill='#047857', font=stamp_f_bold)
    draw.text((stamp_cx - 38, stamp_cy - 12), "UJI COBA", fill='#059669', font=stamp_f_center)
    draw.text((stamp_cx - 52, stamp_cy + 14), "★ RESMI DESA ★", fill='#047857', font=stamp_f_bold)

    # Verification Note next to stamp
    verif_x = card_margin + 20
    verif_y = block_y + block_h + 60
    draw.text((verif_x, verif_y), "Catatan Administrator Sistem:", fill='#1E293B', font=get_font(font_bold, 20))
    draw.text((verif_x, verif_y + 30), "• Seluruh fitur permohonan surat, peta SLS, dan katalog UMKM siap ditinjau.", fill='#64748B', font=get_font(font_reg, 18))
    draw.text((verif_x, verif_y + 58), "• Tanggapan, aspirasi, atau evaluasi pengujian dapat disampaikan ke pengelola.", fill='#64748B', font=get_font(font_reg, 18))

    # 7. Bottom Footer Area
    footer_h = 130
    footer_y = height - footer_h
    draw.rectangle([(0, footer_y), (width, height)], fill='#0F172A')
    draw.line([(0, footer_y), (width, footer_y)], fill='#059669', width=4)

    draw.text((card_margin, footer_y + 30), "PEMERINTAH DESA PAPAYAN • KECAMATAN JATIWARAS • KABUPATEN TASIKMALAYA", fill='#F8FAFC', font=f_footer_bold)
    draw.text((card_margin, footer_y + 68), "Hak Cipta © 2026 Portal Website Resmi Desa Papayan. Halaman ini khusus untuk simulasi & uji coba.", fill='#94A3B8', font=f_footer_reg)

    # Save to static/images
    out_dir = 'static/images'
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, 'poster_uji_coba.png')
    out_jpg = os.path.join(out_dir, 'poster_uji_coba.jpg')
    
    # Also save to uploads directory
    uploads_dir = 'static/images/uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    out_upload_png = os.path.join(uploads_dir, 'poster_uji_coba_a4.png')
    out_upload_jpg = os.path.join(uploads_dir, 'poster_uji_coba_a4.jpg')

    img.save(out_png, 'PNG', quality=95)
    img.save(out_jpg, 'JPEG', quality=92)
    img.save(out_upload_png, 'PNG', quality=95)
    img.save(out_upload_jpg, 'JPEG', quality=92)

    print(f"Poster A4 berhasil dibuat:")
    print(f" - {out_png} ({os.path.getsize(out_png)} bytes)")
    print(f" - {out_jpg} ({os.path.getsize(out_jpg)} bytes)")
    print(f" - {out_upload_png}")
    print(f" - {out_upload_jpg}")

if __name__ == '__main__':
    create_a4_poster()
