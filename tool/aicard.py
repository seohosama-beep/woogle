# KANG AI 카드뉴스 릴스 생성기 — python3 aicard.py spec.json
# spec: name, seed, key, title{top, l1, l2}, icon, items[{icon, t, d}], cta
import json, sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from music2 import music, SR

W, H, FPS = 1080, 1920, 30
BG = (243, 238, 228); INK = (20, 20, 22); SUB = (90, 88, 84)
HL = (255, 214, 64); ACC = (40, 92, 255); TILE = (255, 255, 255)
BLK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(sz, black=True): return ImageFont.truetype(BLK if black else BLD, sz, index=1)

def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def fit(d, s, sz, maxw, black=True):
    while sz > 30 and tw(d, s, F(sz, black)) > maxw: sz -= 4
    return F(sz, black)
def center(d, s, y, f, col):
    d.text(((W - tw(d, s, f)) / 2, y), s, font=f, fill=col)

def pill(im, y=250):
    d = ImageDraw.Draw(im); f = F(40); s = 'KANG AI'
    w = tw(d, s, f) + 120; x = (W - w) // 2
    d.rounded_rectangle([x, y, x + w, y + 76], 38, fill=INK)
    d.ellipse([x + 12, y + 10, x + 68, y + 66], fill=ACC)
    d.text((x + 25, y + 10), 'K', font=F(36), fill=(255, 255, 255))
    d.text((x + 82, y + 10), s, font=f, fill=(255, 255, 255))

def icon(im, kind, cx, cy, r=110):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx - r - 6, cy - r - 2, cx + r + 6, cy + r + 10], 52, fill=(220, 214, 200))
    d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], 48, fill=TILE)
    k = r * .55
    if kind == 'bolt':
        d.polygon([(cx + .15*k, cy - k), (cx - .6*k, cy + .15*k), (cx - .05*k, cy + .15*k), (cx - .2*k, cy + k), (cx + .6*k, cy - .2*k), (cx + .05*k, cy - .2*k)], fill=ACC)
    elif kind == 'chart':
        for i, h in enumerate([.5, .9, 1.4, 2.0]):
            x = cx - k + i * .55 * k; d.rounded_rectangle([x, cy + k - h * k * .9, x + .38 * k, cy + k], 6, fill=ACC if i == 3 else (150, 175, 255))
    elif kind == 'mail':
        d.rounded_rectangle([cx - k, cy - .65*k, cx + k, cy + .65*k], 14, fill=ACC)
        d.line([(cx - k + 10, cy - .55*k), (cx, cy + .1*k), (cx + k - 10, cy - .55*k)], fill=(255, 255, 255), width=12)
    elif kind == 'doc':
        d.rounded_rectangle([cx - .7*k, cy - k, cx + .7*k, cy + k], 16, fill=ACC)
        for i in range(4): d.rounded_rectangle([cx - .45*k, cy - .55*k + i*.35*k, cx + (.45 if i < 3 else .1)*k, cy - .43*k + i*.35*k], 5, fill=(255, 255, 255))
    elif kind == 'clock':
        d.ellipse([cx - k, cy - k, cx + k, cy + k], fill=ACC)
        d.line([(cx, cy), (cx, cy - .6*k)], fill=(255, 255, 255), width=14); d.line([(cx, cy), (cx + .45*k, cy + .2*k)], fill=(255, 255, 255), width=14)
    elif kind == 'robot':
        d.rounded_rectangle([cx - .85*k, cy - .55*k, cx + .85*k, cy + .85*k], 30, fill=ACC)
        d.line([(cx, cy - .55*k), (cx, cy - k)], fill=ACC, width=10); d.ellipse([cx - 14, cy - k - 14, cx + 14, cy - k + 14], fill=HL)
        for sx in (-1, 1): d.ellipse([cx + sx*.4*k - 18, cy - .05*k - 18, cx + sx*.4*k + 18, cy - .05*k + 18], fill=(255, 255, 255))
        d.rounded_rectangle([cx - .35*k, cy + .4*k, cx + .35*k, cy + .55*k], 6, fill=(255, 255, 255))
    else:  # spark
        for a in range(8):
            t = a * np.pi / 4; L = k if a % 2 == 0 else .6 * k
            d.line([(cx, cy), (cx + L*np.cos(t), cy + L*np.sin(t))], fill=ACC, width=18)

def hl_text(d, s, y, f):
    w = tw(d, s, f); x = (W - w) / 2; b = d.textbbox((x, y), s, font=f)
    d.rectangle([x - 8, b[3] - 30, x + w + 8, b[3] + 4], fill=HL); d.text((x, y), s, font=f, fill=INK)

def cover(sp):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); pill(im)
    icon(im, sp.get('icon', 'bolt'), W // 2, 520)
    t = sp['title']
    hl_text(d, t['top'], 720, fit(d, t['top'], 78, 960))
    center(d, t['l1'], 840, fit(d, t['l1'], 150, 1000), INK)
    center(d, t['l2'], 1020, fit(d, t['l2'], 150, 1000), INK)
    center(d, '끝까지 보고 저장하세요 ↓', 1300, F(46, False), SUB)
    return im

def item(sp, i, it):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); pill(im)
    n = len(sp['items'])
    for j in range(n):  # progress dots
        x = W / 2 - (n - 1) * 30 + j * 60; c = ACC if j == i else (205, 198, 184)
        d.ellipse([x - 12, 380, x + 12, 404], fill=c)
    d.ellipse([W/2 - 80, 470, W/2 + 80, 630], fill=INK)
    center(d, str(i + 1), 478, F(110), HL)
    icon(im, it.get('icon', 'spark'), W // 2, 820, 95)
    hl_text(d, it['t'], 990, fit(d, it['t'], 92, 980))
    y = 1150
    for line in it['d'].split('\n'):
        center(d, line, y, fit(d, line, 58, 960, False), SUB); y += 86
    return im

def outro(sp):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); pill(im)
    icon(im, 'robot', W // 2, 560)
    hl_text(d, sp.get('cta', '저장하고 하나씩 따라 해보세요'), 780, F(70))
    center(d, '팔로우하면', 940, F(110), INK)
    center(d, '매일 AI 꿀팁 도착', 1090, F(110), INK)
    center(d, '@kangdalcom', 1320, F(56, False), ACC)
    return im

def render(sp):
    name = sp['name']; os.makedirs('/tmp/ac_' + name, exist_ok=True); fd = '/tmp/ac_' + name
    scenes = [(cover(sp), 2.4)] + [(item(sp, i, it), 2.6) for i, it in enumerate(sp['items'])] + [(outro(sp), 2.2)]
    total = sum(s for _, s in scenes); k = 0
    for idx, (im, dur) in enumerate(scenes):
        nf = int(dur * FPS)
        for f in range(nf):
            p = f / nf; z = 1 + 0.03 * p
            fr = im.resize((int(W*z), int(H*z)), Image.LANCZOS)
            ox = (fr.width - W) // 2; oy = (fr.height - H) // 2; fr = fr.crop((ox, oy, ox + W, oy + H))
            if idx > 0 and f < 6:  # slide-in
                sh = int(W * (1 - f / 6) ** 2); base = prev.copy(); base.paste(fr.crop((0, 0, W - sh, H)), (sh, 0)); fr = base
            fr.save(f'{fd}/{k:05d}.png'); k += 1
        prev = im
    a = music(total, sp.get('seed', 1), sp.get('key', 0)); a = a[:int(total * SR)]
    a = a / (np.abs(a).max() + 1e-9) * .7
    fade = int(.6 * SR); a[-fade:] *= np.linspace(1, 0, fade)
    import wave
    with wave.open(f'{fd}/a.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 32767).astype(np.int16).tobytes())
    out = sp.get('out', f'{name}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{fd}/%05d.png', '-i', f'{fd}/a.wav',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', out], check=True)
    cover(sp).save(out.replace('.mp4', '_cover.jpg'), quality=92)
    return out

if __name__ == '__main__':
    print(render(json.load(open(sys.argv[1]))))
