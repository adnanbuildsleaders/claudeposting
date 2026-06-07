# -*- coding: utf-8 -*-
"""
adnanbuildsleaders — Blog Image Engine
Flat-vector illustrations (no photos). Two modes:
  render(scene, palette, path, mode="blog")  -> 1920x1080 no-text hero illustration (full-bleed)
  render(scene, palette, path, mode="story", hook=..., cta="VISIT habbinson.com/blog") -> 1080x1920 IG Story with text
Scenes map to blog topics. Library grows over time. Public:
  PALETTES, SCENES, pick_scene(topic_keywords), render(...)
"""
import os, math, re
from PIL import Image, ImageDraw, ImageFont

FDIR = r"C:\Windows\Fonts"
def _f(names, size):
    for n in names:
        p = os.path.join(FDIR, n)
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()
def IMP(s): return _f(["impact.ttf","ariblk.ttf"], s)
def AB(s):  return _f(["arialbd.ttf","ariblk.ttf"], s)

def hx(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]

# bright palettes: sky(bg top), bg(bottom), p1 primary subject, p2 secondary, dark, light
PALETTES = {
 "sunny":   dict(top="FFD24D", bot="FF8A3D", p1="2B2D7A", p2="FFE000", dark="1B1530", light="FFF7E6"),
 "sky":     dict(top="63C7FF", bot="2B7FFF", p1="FFD400", p2="FFD400", dark="0B1430", light="EAF6FF"),
 "mint":    dict(top="6BE3C9", bot="13A89B", p1="FF7A59", p2="FFD166", dark="052B28", light="EAFBF6"),
 "grape":   dict(top="B06BFF", bot="6B21D6", p1="FFE34D", p2="FFE34D", dark="160A2E", light="F4ECFF"),
 "coral":   dict(top="FF9A8B", bot="FF4D5E", p1="2B2D7A", p2="FFD24D", dark="2C0A10", light="FFF0EE"),
 "lime":    dict(top="C6FF6B", bot="5FB52E", p1="2B2D7A", p2="FFE000", dark="11240A", light="F4FFE6"),
}
def P(name):
    d=PALETTES[name]; return {k:hx(v) for k,v in d.items()}

# ---------- shape helpers ----------
def sun(d, cx, cy, r, col):
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)
    for a in range(0,360,30):
        x0=cx+math.cos(math.radians(a))*(r+14); y0=cy+math.sin(math.radians(a))*(r+14)
        x1=cx+math.cos(math.radians(a))*(r+46); y1=cy+math.sin(math.radians(a))*(r+46)
        d.line([(x0,y0),(x1,y1)], fill=col, width=14)
def cloud(d, x, y, s, col):
    d.ellipse([x,y,x+s,y+s], fill=col)
    d.ellipse([x+s*0.5,y-s*0.2,x+s*1.5,y+s*0.8], fill=col)
    d.ellipse([x+s*1.1,y,x+s*2.0,y+s], fill=col)
    d.rectangle([x+s*0.4,y+s*0.5,x+s*1.6,y+s], fill=col)
def star(d, cx, cy, r, col):
    pts=[]
    for i in range(10):
        ang=math.pi/2 + i*math.pi/5; rr = r if i%2==0 else r*0.45
        pts.append((cx+math.cos(ang)*rr, cy-math.sin(ang)*rr))
    d.polygon(pts, fill=col)
def person(d, cx, cy, s, body, skin=None, head=True, face=True, arms=True):
    # cy = top of head; s = head radius
    skin = skin or (255, 219, 172)
    by0 = cy+2*s+6; by1 = by0 + s*3.6
    if arms:
        aw=int(s*0.55)
        d.line([(cx-s*1.3,by0+s*0.6),(cx-s*2.3,by0+s*1.9)], fill=body, width=aw)
        d.line([(cx+s*1.3,by0+s*0.6),(cx+s*2.3,by0+s*1.9)], fill=body, width=aw)
        d.ellipse([cx-s*2.5,by0+s*1.7,cx-s*2.5+aw,by0+s*1.7+aw], fill=body)
        d.ellipse([cx+s*2.5-aw,by0+s*1.7,cx+s*2.5,by0+s*1.7+aw], fill=body)
    d.rounded_rectangle([cx-s*1.5,by0,cx+s*1.5,by1], radius=s*0.8, fill=body)
    if head: d.ellipse([cx-s,cy,cx+s,cy+2*s], fill=skin)
    if face and head:
        ey=cy+s*0.85; er=s*0.13
        d.ellipse([cx-s*0.42-er,ey-er,cx-s*0.42+er,ey+er], fill=(45,45,55))
        d.ellipse([cx+s*0.42-er,ey-er,cx+s*0.42+er,ey+er], fill=(45,45,55))
        d.arc([cx-s*0.5,cy+s*1.0,cx+s*0.5,cy+s*1.7], 15,165, fill=(45,45,55), width=max(4,int(s*0.09)))
def speech(d, x, y, w, h, col, dark, tail="left"):
    d.rounded_rectangle([x,y,x+w,y+h], radius=h*0.28, fill=col)
    if tail=="left": d.polygon([(x+w*0.2,y+h),(x+w*0.34,y+h),(x+w*0.12,y+h+h*0.35)], fill=col)
    else: d.polygon([(x+w*0.8,y+h),(x+w*0.66,y+h),(x+w*0.88,y+h+h*0.35)], fill=col)
    # 3 dots
    for i in range(3):
        dx=x+w*0.3+i*w*0.2; d.ellipse([dx-h*0.07,y+h*0.45,dx+h*0.07,y+h*0.6], fill=dark)
def plant(d, cx, base, h, stem, leaf):
    d.line([(cx,base),(cx,base-h)], fill=stem, width=18)
    for sgn,off in [(-1,0.45),(1,0.65),(-1,0.85)]:
        ly=base-h*off
        d.ellipse([cx+sgn*10, ly-40, cx+sgn*90, ly+20] if sgn>0 else [cx-90, ly-40, cx-10, ly+20], fill=leaf)
def hill(d, W, H, y, col):
    d.ellipse([-W*0.3, y, W*0.7, y+H*0.7], fill=col)
    d.ellipse([W*0.4, y+30, W*1.3, y+H*0.7+30], fill=col)
    d.rectangle([0, min(y+90, H-1), W, H], fill=col)

# ---------- scenes (draw into full W,H using palette pal) ----------
def _bg(img, d, W, H, pal):
    for y in range(H):
        d.line([(0,y),(W,y)], fill=mix(pal["top"],pal["bot"],y/H))
    sun(d, int(W*0.86), int(H*0.16), 70, pal["p2"])
    cloud(d, int(W*0.10), int(H*0.12), 70, pal["light"])
    cloud(d, int(W*0.62), int(H*0.10), 55, pal["light"])
    for (sx,sy,sr) in [(0.30,0.10,16),(0.45,0.20,12),(0.78,0.30,14)]:
        star(d, int(W*sx), int(H*sy), sr, pal["light"])

def scene_growth(img, d, W, H, pal):
    _bg(img,d,W,H,pal); hill(d,W,H,int(H*0.70),pal["p1"])
    cx=int(W*0.5)
    person(d, cx, int(H*0.44), 72, pal["light"])
    # glowing lightbulb (idea / growing mind) above head
    lx,ly=cx,int(H*0.22); r=58
    for a in range(0,360,45):
        x0=lx+math.cos(math.radians(a))*(r+18); y0=ly+math.sin(math.radians(a))*(r+18)
        x1=lx+math.cos(math.radians(a))*(r+46); y1=ly+math.sin(math.radians(a))*(r+46)
        d.line([(x0,y0),(x1,y1)], fill=pal["p2"], width=11)
    d.ellipse([lx-r,ly-r,lx+r,ly+r], fill=pal["p2"])
    d.rectangle([lx-22,ly+r-6,lx+22,ly+r+30], fill=pal["dark"])
    d.line([(lx,ly-22),(lx,ly+18)], fill=pal["light"], width=10)  # filament
    d.line([(lx-16,ly+6),(lx,ly-10),(lx+16,ly+6)], fill=pal["light"], width=8)
    star(d, int(W*0.34), int(H*0.30), 22, pal["p2"]); star(d, int(W*0.66), int(H*0.28), 18, pal["p2"])
def scene_talk(img, d, W, H, pal):
    _bg(img,d,W,H,pal); hill(d,W,H,int(H*0.74),pal["p1"])
    person(d, int(W*0.36), int(H*0.42), 75, pal["p2"])
    person(d, int(W*0.64), int(H*0.42), 75, pal["light"])
    speech(d, int(W*0.10), int(H*0.18), int(W*0.20), int(H*0.16), pal["light"], pal["dark"], "right")
    speech(d, int(W*0.70), int(H*0.16), int(W*0.20), int(H*0.16), pal["p2"], pal["dark"], "left")
def scene_independence(img, d, W, H, pal):
    _bg(img,d,W,H,pal); hill(d,W,H,int(H*0.74),pal["p1"])
    person(d, int(W*0.34), int(H*0.42), 80, pal["light"])      # parent
    person(d, int(W*0.56), int(H*0.52), 52, pal["p2"])         # child (smaller)
    # bird leaving nest
    bx,by=int(W*0.80),int(H*0.26)
    d.arc([bx-50,by-20,bx,by+20],180,360, fill=pal["dark"], width=12)
    d.arc([bx,by-20,bx+50,by+20],180,360, fill=pal["dark"], width=12)
def scene_confidence(img, d, W, H, pal):
    _bg(img,d,W,H,pal); hill(d,W,H,int(H*0.74),pal["p1"])
    cx=int(W*0.5)
    d.rectangle([cx-90,int(H*0.62),cx+90,int(H*0.82)], fill=pal["dark"])  # podium
    person(d, cx, int(H*0.34), 70, pal["p2"])
    d.line([(cx+70,int(H*0.50)),(cx+150,int(H*0.44))], fill=pal["dark"], width=16)  # mic arm
    d.ellipse([cx+140,int(H*0.40),cx+185,int(H*0.49)], fill=pal["dark"])           # mic
    for i,r in enumerate([60,110,160]):  # soundwaves
        d.arc([cx+150-r,int(H*0.30)-r,cx+150+r,int(H*0.55)+r], 300,60, fill=pal["light"], width=10)
def scene_resilience(img, d, W, H, pal):
    _bg(img,d,W,H,pal)
    # stairs to a flag (climbing)
    for i in range(5):
        x=int(W*0.2)+i*int(W*0.12); y=int(H*0.80)-i*int(H*0.12)
        d.rectangle([x,y,x+int(W*0.12),int(H*0.85)], fill=pal["p1"])
    fx=int(W*0.2)+5*int(W*0.12); fy=int(H*0.80)-5*int(H*0.12)
    d.line([(fx,fy),(fx,fy-120)], fill=pal["dark"], width=12)
    d.polygon([(fx,fy-120),(fx+90,fy-95),(fx,fy-70)], fill=pal["p2"])
    person(d, int(W*0.5), int(H*0.40), 60, pal["light"])

SCENES = {
 "growth": scene_growth, "talk": scene_talk, "independence": scene_independence,
 "confidence": scene_confidence, "resilience": scene_resilience,
}
_TOPIC_MAP = [
 (["smart","praise","effort","growth","intelligen","mindset"], "growth"),
 (["talk","open up","listen","conversation","communicat","express"], "talk"),
 (["rescu","independ","overparent","let go","responsibil","fail","resilien","grit"], "resilience"),
 (["confiden","speak","stage","public"], "confidence"),
 (["choice","decision","cooperat","calm","emotion"], "talk"),
]
def pick_scene(text):
    t=text.lower()
    for keys,scene in _TOPIC_MAP:
        if any(k in t for k in keys): return scene
    return "growth"

def render(scene, palette, path, mode="blog", hook="", cta="VISIT habbinson.com/blog"):
    pal=P(palette)
    if mode=="story":
        W,H=1080,1920
    else:
        W,H=1920,1080
    img=Image.new("RGB",(W,H),pal["top"]); d=ImageDraw.Draw(img)
    fn=SCENES.get(scene, scene_growth)
    if mode=="story":
        # draw scene as a square band that fills the middle, then text top + CTA bottom
        band=Image.new("RGB",(1080,1080),pal["top"]); bd=ImageDraw.Draw(band)
        fn(band,bd,1080,1080,pal)
        img.paste(band,(0,470))
        # top text
        tf=IMP(96); t="NEW BLOG"; tw=d.textlength(t,font=tf)
        d.text(((W-tw)/2,150), t, font=tf, fill=pal["dark"])
        tf2=IMP(80); t2="IS LIVE"; tw2=d.textlength(t2,font=tf2)
        d.text(((W-tw2)/2,250), t2, font=tf2, fill=pal["p2"])
        if hook:
            hf=AB(46)
            words=hook.upper().split(); lines=[]; cur=[]
            for w in words:
                if not cur or d.textlength(" ".join(cur+[w]),font=hf)<=W-160: cur.append(w)
                else: lines.append(cur); cur=[w]
            if cur: lines.append(cur)
            yy=400
            for ln in lines[:3]:
                s=" ".join(ln); ww=d.textlength(s,font=hf); d.text(((W-ww)/2,yy),s,font=hf,fill=pal["dark"]); yy+=56
        # bottom CTA band
        d.rounded_rectangle([90,H-260,W-90,H-120], radius=40, fill=pal["dark"])
        cf=AB(54); cw=d.textlength(cta,font=cf)
        d.text(((W-cw)/2,H-225), cta, font=cf, fill=pal["light"])
        d.polygon([(W/2-26,H-300),(W/2+26,H-300),(W/2,H-262)], fill=pal["dark"])  # down arrow
    else:
        fn(img,d,W,H,pal)
    img.save(path,"PNG"); return path

import re as _re
def _norm(s): return _re.sub(r"[^A-Z0-9]","",s.upper())
def _wrap(words,fnt,d,maxw):
    lines=[];cur=[]
    for w in words:
        if not cur or d.textlength(" ".join(cur+[w]),font=fnt)<=maxw: cur.append(w)
        else: lines.append(cur);cur=[w]
    if cur: lines.append(cur)
    return lines
def _paste_rounded(base, card, xy, radius=46):
    mask=Image.new("L",card.size,0); md=ImageDraw.Draw(mask)
    md.rounded_rectangle([0,0,card.size[0]-1,card.size[1]-1], radius=radius, fill=255)
    base.paste(card, xy, mask)

# ===== v11 redesign: split layout (tagline + flat graphic motif | audience headline) =====
TAGLINE_1 = "DON'T RAISE A CHILD."
TAGLINE_2 = "RAISE A LEADER."

def _A(c,a): return (c[0],c[1],c[2],a)

def motif(od, region, scene, acc, light):
    """Flat, bold, accent-coloured abstract graphic (NO cartoons)."""
    x0,y0,x1,y1=region; w=x1-x0; h=y1-y0; cx=x0+w//2; cy=y0+h//2; A=_A
    if scene=="growth":
        bw=w*0.16
        for i in range(4):
            bh=h*(0.30+0.16*i); bx=x0+w*0.10+i*bw*1.15
            od.rounded_rectangle([bx,y1-bh,bx+bw,y1], radius=14, fill=A(acc, 235 if i%2 else 170))
        od.line([(x0+w*0.10,y1-h*0.30),(x1-w*0.10,y0+h*0.10)], fill=A(light,210), width=16)
        p=(x1-w*0.10,y0+h*0.10)
        od.polygon([p,(p[0]-46,p[1]+6),(p[0]-8,p[1]+50)], fill=A(light,210))
    elif scene=="talk":
        od.rounded_rectangle([x0+w*0.08,y0+h*0.16,x0+w*0.62,y0+h*0.54], radius=34, fill=A(acc,230))
        od.polygon([(x0+w*0.20,y0+h*0.54),(x0+w*0.34,y0+h*0.54),(x0+w*0.16,y0+h*0.70)], fill=A(acc,230))
        od.rounded_rectangle([x0+w*0.40,y0+h*0.46,x0+w*0.92,y0+h*0.82], radius=34, fill=A(light,180))
        od.polygon([(x0+w*0.80,y0+h*0.82),(x0+w*0.66,y0+h*0.82),(x0+w*0.84,y0+h*0.97)], fill=A(light,180))
    elif scene=="resilience":
        od.polygon([(x0+w*0.05,y1),(x0+w*0.40,y0+h*0.30),(x0+w*0.70,y1)], fill=A(acc,210))
        od.polygon([(x0+w*0.45,y1),(x0+w*0.74,y0+h*0.48),(x1,y1)], fill=A(light,160))
        fx,fy=x0+w*0.40,y0+h*0.30
        od.line([(fx,fy),(fx,fy-h*0.20)], fill=A(light,230), width=12)
        od.polygon([(fx,fy-h*0.20),(fx+w*0.16,fy-h*0.14),(fx,fy-h*0.08)], fill=A(light,230))
    elif scene=="confidence":
        for a in range(-60,61,24):
            x=cx+math.cos(math.radians(a))*w*0.6; y=cy+math.sin(math.radians(a))*w*0.6
            od.line([(x0+w*0.16,cy),(x,y)], fill=A(light,120), width=10)
        r=min(w,h)*0.20; pts=[]
        for i in range(10):
            ang=math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*0.45
            pts.append((x0+w*0.20+math.cos(ang)*rr, cy-math.sin(ang)*rr))
        od.polygon(pts, fill=A(acc,235))
    else:  # independence -> chevrons + doorway
        od.rounded_rectangle([x0+w*0.10,y0+h*0.18,x0+w*0.42,y1-h*0.06], radius=20, outline=A(light,200), width=16)
        for i in range(3):
            bx=x0+w*0.50+i*w*0.15
            od.polygon([(bx,cy-h*0.18),(bx+w*0.11,cy),(bx,cy+h*0.18)], fill=A(acc, 235-50*i))

def _halftone(od, region, acc, alpha=42, step=46, r=7):
    x0,y0,x1,y1=region
    for yy in range(int(y0), int(y1), step):
        for xx in range(int(x0), int(x1), step):
            od.ellipse([xx-r,yy-r,xx+r,yy+r], fill=(acc[0],acc[1],acc[2],alpha))

def _bigmark(od, region, ch, acc, alpha=34, size=620):
    x0,y0,x1,y1=region
    f=IMP(size); od.text((x0+(x1-x0)*0.04, y0-size*0.18), ch, font=f, fill=(acc[0],acc[1],acc[2],alpha))

def _draw_left(panel, scene, acc, light, white):
    """panel: RGBA dark left panel. Draws halftone + motif + big quote mark + tagline."""
    W,H=panel.size; od=ImageDraw.Draw(panel,"RGBA")
    _halftone(od,(0,0,W,int(H*0.55)),acc,alpha=40)
    _bigmark(od,(0,0,W,H),"“",acc,alpha=30,size=int(H*0.55))
    motif(od,(int(W*0.06),int(H*0.10),int(W*0.94),int(H*0.50)),scene,acc,light)
    f1=AB(int(W*0.085)); f2=IMP(int(W*0.150)); ty=int(H*0.62)
    od.text((int(W*0.08),ty), TAGLINE_1, font=f1, fill=white)
    l2w=od.textlength(TAGLINE_2,font=f2)
    od.text((int(W*0.075),ty+int(W*0.10)), TAGLINE_2, font=f2, fill=acc)
    od.rectangle([int(W*0.08),ty+int(W*0.10)+int(W*0.165), int(W*0.08)+min(l2w,W*0.82), ty+int(W*0.10)+int(W*0.18)], fill=acc)

def _draw_headline(d, region, headline, key, acc, white, on):
    x0,y0,x1,y1=region; bw=x1-x0; words=headline.upper().split(); keyset={_norm(key)}
    size=int((y1-y0)*0.42)
    while size>40:
        hf=IMP(size); lines=_wrap(words,hf,d,bw); lh=int(size*1.0); total=lh*len(lines)
        widest=max(d.textlength(" ".join(l),font=hf) for l in lines)
        if total<=(y1-y0) and widest<=bw: break
        size-=4
    hf=IMP(size); lines=_wrap(words,hf,d,bw); lh=int(size*1.0); total=lh*len(lines)
    y=y0+max(0,((y1-y0)-total)//2)
    for l in lines:
        x=x0; sp=d.textlength(" ",font=hf)
        for w in l:
            ww=d.textlength(w,font=hf)
            if _norm(w) in keyset:
                d.rounded_rectangle([x-10,y+8,x+ww+10,y+lh-2], radius=12, fill=acc); d.text((x,y),w,font=hf,fill=on)
            else: d.text((x,y),w,font=hf,fill=white)
            x+=ww+sp
        y+=lh

def render_featured(headline, key, scene, palette, path):
    """1920x1080: LEFT dark panel (tagline + flat graphic motif) | RIGHT bright audience headline + brand."""
    pal=P(palette); W,H=1920,1080
    bot=pal["bot"]; acc=pal["p2"]; dark=pal["dark"]; light=pal["light"]; white=(255,255,255); on=(20,20,26)
    img=Image.new("RGB",(W,H),bot); d=ImageDraw.Draw(img)
    LW=int(W*0.40)
    left=Image.new("RGBA",(LW,H),dark+(255,)); _draw_left(left, scene, acc, light, white)
    img.paste(left.convert("RGB"),(0,0))
    d.rectangle([LW-10,0,LW,H], fill=acc)  # divider
    _draw_headline(d,(LW+64,120,W-70,H-180),headline,key,acc,white,on)
    bf=AB(40); brand="habbinson.com  •  @adnanbuildsleaders"; bw2=d.textlength(brand,font=bf)
    d.rounded_rectangle([LW+58,H-150,LW+58+bw2+24,H-86], radius=14, fill=acc)
    d.text((LW+72,H-142), brand, font=bf, fill=on)
    img.save(path,"PNG"); return path

def render_story(headline, key, scene, palette, state, when_str, path):
    """9:16 (1080x1920) IG Story. Same left/right split + state pill + schedule band + CTA."""
    pal=P(palette); W,H=1080,1920
    bot=pal["bot"]; acc=pal["p2"]; dark=pal["dark"]; light=pal["light"]; white=(255,255,255); on=(20,20,26)
    img=Image.new("RGB",(W,H),bot); d=ImageDraw.Draw(img)
    LW=int(W*0.42)
    left=Image.new("RGBA",(LW,H),dark+(255,)); _draw_left(left, scene, acc, light, white)
    img.paste(left.convert("RGB"),(0,0))
    d.rectangle([LW-9,0,LW,H], fill=acc)
    rx0=LW+34; rx1=W-34
    label = "NEW BLOG DROPPING" if state=="scheduled" else "NOW LIVE"
    pf=AB(40); lw=d.textlength(label,font=pf)
    d.rounded_rectangle([rx0,120,rx0+lw+56,200], radius=40, fill=acc)
    d.text((rx0+28,138), label, font=pf, fill=on)
    _draw_headline(d,(rx0,300,rx1,1180),headline,key,acc,white,on)
    bt = ("PUBLISHING "+when_str) if state=="scheduled" else "READ IT NOW"
    ssz=44; sf=AB(ssz)
    while d.textlength(bt,font=sf) > (rx1-rx0-44) and ssz>22: ssz-=2; sf=AB(ssz)
    btw=d.textlength(bt,font=sf)
    d.rounded_rectangle([rx0,1250,min(rx0+btw+44,rx1),1250+ssz+40], radius=16, fill=dark)
    d.text((rx0+22,1268), bt, font=sf, fill=acc)
    cta="VISIT  habbinson.com/blog"; cf=AB(52); cw=d.textlength(cta,font=cf)
    d.rounded_rectangle([(W-cw-100)/2,H-210,(W+cw+100)/2,H-96], radius=40, fill=acc)
    d.text(((W-cw)/2,H-178), cta, font=cf, fill=on)
    img.save(path,"PNG"); return path

if __name__=="__main__":
    render_featured("Get Your CHILD to Open Up","OPEN UP","talk","mint", r"D:\Claude\Kids\Communication\_feat.png")
    render_story("Get Your CHILD to Open Up","OPEN UP","talk","mint","scheduled","JUN 4 · 5 PM IST", r"D:\Claude\Kids\Communication\_story.png")
    print("ok")
