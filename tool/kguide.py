# K-Seoul guide info-card reel generator (original graphics + original music)
# usage: python3 kguide.py spec.json  -> <name>.mp4 (1080x1920)
import json, sys, os, math, shutil, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music2
W,H=1080,1920; S=2; FPS=30
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; FM='/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
IDX={'ko':1,'ja':0,'zh':2,'en':1}
def F(sz,lang='ko',bold=True): return ImageFont.truetype(FB if bold else FM, int(sz*S), index=IDX[lang])
NAVY=(18,24,48); GOLD=(255,196,61); PINK=(255,92,122); WHITE=(255,255,255); SKY=(120,200,255)
PALS=[(255,92,122),(255,170,60),(80,200,140),(90,150,255),(190,110,255),(255,120,60)]
def ctext(d,txt,y,sz,col,lang='ko',bold=True,maxw=960):
    f=F(sz,lang,bold); lines=[]
    for raw in txt.split('\n'):
        cur=''
        toks=[w+' ' for w in raw.split(' ')] if lang=='en' else list(raw)
        for ch in toks:
            if d.textlength((cur+ch).rstrip(),font=f)>maxw*S and cur: lines.append(cur.rstrip()); cur=ch
            else: cur+=ch
        lines.append(cur.rstrip())
    for i,l in enumerate(lines):
        w=d.textlength(l,font=f); d.text(((W*S-w)/2,(y+i*sz*1.28)*S),l,font=f,fill=col)
    return y+len(lines)*sz*1.28
def icon(d,kind,cx,cy,r,col):
    s=S; cx*=s; cy*=s; r*=s; lw=int(6*s); ink=(25,25,30)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col,outline=ink,width=lw)
    k=kind
    if k=='egg':
        d.rounded_rectangle([cx-r*.6,cy-r*.15,cx+r*.6,cy+r*.45],radius=r*.2,fill=(240,190,110),outline=ink,width=lw)
        d.ellipse([cx-r*.35,cy-r*.45,cx+r*.35,cy+r*.15],fill=WHITE,outline=ink,width=lw)
        d.ellipse([cx-r*.15,cy-r*.3,cx+r*.15,cy],fill=(255,190,40))
    elif k=='potato':
        d.line([cx,cy-r*.75,cx,cy+r*.75],fill=(150,110,70),width=lw)
        for i in range(6):
            y=cy-r*.55+i*r*.22; w=r*(.45-abs(i-2.5)*.05)
            d.ellipse([cx-w,y-r*.08,cx+w,y+r*.08],fill=(245,200,90),outline=ink,width=int(3*s))
    elif k=='ricecake':
        d.ellipse([cx-r*.7,cy-r*.1,cx+r*.7,cy+r*.55],fill=(230,70,50),outline=ink,width=lw)
        for dx,dy in [(-.3,0),(0,.1),(.3,0),(-.15,.25),(.18,.28)]:
            d.rounded_rectangle([cx+dx*r-r*.18,cy+dy*r-r*.07,cx+dx*r+r*.18,cy+dy*r+r*.07],radius=r*.06,fill=(255,235,220),outline=ink,width=int(3*s))
    elif k=='pancake':
        d.ellipse([cx-r*.65,cy-r*.4,cx+r*.65,cy+r*.4],fill=(210,150,80),outline=ink,width=lw)
        d.arc([cx-r*.4,cy-r*.2,cx+r*.4,cy+r*.25],200,340,fill=(140,80,30),width=lw)
    elif k=='skewer':
        d.line([cx-r*.7,cy+r*.6,cx+r*.6,cy-r*.6],fill=(150,110,70),width=lw)
        for t in (-.35,0,.3):
            x=cx+t*r; y=cy-t*r*.95
            d.ellipse([x-r*.22,y-r*.22,x+r*.22,y+r*.22],fill=(200,90,40),outline=ink,width=int(3*s))
    elif k=='hotel':
        d.rectangle([cx-r*.5,cy-r*.55,cx+r*.5,cy+r*.55],fill=WHITE,outline=ink,width=lw)
        for i in range(3):
            for j in range(2): d.rectangle([cx-r*.35+j*r*.42,cy-r*.42+i*r*.3,cx-r*.12+j*r*.42,cy-r*.25+i*r*.3],fill=SKY)
    elif k=='subway':
        d.rounded_rectangle([cx-r*.5,cy-r*.55,cx+r*.5,cy+r*.45],radius=r*.15,fill=WHITE,outline=ink,width=lw)
        d.rectangle([cx-r*.38,cy-r*.42,cx+r*.38,cy-r*.05],fill=SKY)
        for x in (-.25,.25): d.ellipse([cx+x*r-r*.08,cy+r*.15,cx+x*r+r*.08,cy+r*.31],fill=ink)
    elif k=='shop':
        d.rectangle([cx-r*.5,cy-r*.15,cx+r*.5,cy+r*.55],fill=WHITE,outline=ink,width=lw)
        d.polygon([(cx-r*.6,cy-r*.15),(cx+r*.6,cy-r*.15),(cx+r*.45,cy-r*.5),(cx-r*.45,cy-r*.5)],fill=PINK,outline=ink)
    elif k=='camera':
        d.rounded_rectangle([cx-r*.6,cy-r*.35,cx+r*.6,cy+r*.45],radius=r*.12,fill=(60,60,70),outline=ink,width=lw)
        d.ellipse([cx-r*.28,cy-r*.2,cx+r*.28,cy+r*.36],fill=SKY,outline=WHITE,width=lw)
    elif k=='coffee':
        d.rounded_rectangle([cx-r*.4,cy-r*.35,cx+r*.3,cy+r*.5],radius=r*.1,fill=WHITE,outline=ink,width=lw)
        d.arc([cx+r*.15,cy-r*.15,cx+r*.55,cy+r*.25],270,90,fill=ink,width=lw)
    elif k=='map':
        d.polygon([(cx,cy+r*.6),(cx-r*.38,cy),(cx+r*.38,cy)],fill=PINK,outline=ink)
        d.ellipse([cx-r*.4,cy-r*.55,cx+r*.4,cy+r*.2],fill=PINK,outline=ink,width=lw)
        d.ellipse([cx-r*.14,cy-r*.3,cx+r*.14,cy-r*.02],fill=WHITE)
    else:
        pts=[(cx+(r*.6 if i%2==0 else r*.25)*math.cos(-math.pi/2+i*math.pi/5),cy+(r*.6 if i%2==0 else r*.25)*math.sin(-math.pi/2+i*math.pi/5)) for i in range(10)]
        d.polygon(pts,fill=GOLD,outline=ink)
def frame_title(sp):
    im=Image.new('RGB',(W*S,H*S),NAVY); d=ImageDraw.Draw(im)
    random.seed(1)
    for _ in range(40):
        x=random.randint(0,W*S); y=random.randint(0,H*S); r=random.randint(2,6)*S; d.ellipse([x-r,y-r,x+r,y+r],fill=(60,70,110))
    d.rounded_rectangle([140*S,330*S,940*S,430*S],radius=50*S,fill=GOLD)
    ctext(d,sp.get('badge','SEOUL GUIDE'),345,58,NAVY,'en')
    if sp.get('hook'): ctext(d,sp['hook'],140,58,PINK,'en')
    y=ctext(d,sp['title']['en'],560,92,WHITE,'en')
    y=ctext(d,sp['title']['ko'],y+40,64,GOLD,'ko')
    y=ctext(d,sp['title']['ja'],y+30,54,WHITE,'ja',False)
    y=ctext(d,sp['title']['zh'],y+20,54,WHITE,'zh',False)
    icon(d,sp.get('title_icon','star'),540,1520,170,PINK)
    return im.resize((W,H),Image.LANCZOS)
def frame_item(sp,i,it):
    col=PALS[i%len(PALS)]
    im=Image.new('RGB',(W*S,H*S),NAVY); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W*S,230*S],fill=col)
    n=len(sp['items'])-i if sp.get('countdown',True) else i+1
    ctext(d,f"#{n}",50,120,WHITE,'en')
    icon(d,it.get('icon','star'),540,560,230,col)
    y=ctext(d,it['ko'],870,96,WHITE,'ko')
    if it.get('roman'): y=ctext(d,it['roman'],y,48,GOLD,'en',False)
    d.line([(160*S,(y+30)*S),(920*S,(y+30)*S)],fill=(70,80,120),width=4*S)
    y+=70
    for lang,colr in (('en',WHITE),('ja',(220,225,255)),('zh',(220,225,255))):
        y=ctext(d,it[lang],y,50,colr,lang,lang=='en')+22
    return im.resize((W,H),Image.LANCZOS)
def frame_outro(sp):
    im=Image.new('RGB',(W*S,H*S),GOLD); d=ImageDraw.Draw(im)
    y=ctext(d,sp.get('outro_en','Save this for your Seoul trip!'),620,80,NAVY,'en')
    y=ctext(d,sp.get('outro_ja','ソウル旅行のために保存してね！'),y+40,56,NAVY,'ja')
    y=ctext(d,sp.get('outro_zh','收藏起来，首尔旅行用得上！'),y+20,56,NAVY,'zh')
    d.rounded_rectangle([200*S,(y+80)*S,880*S,(y+200)*S],radius=60*S,fill=NAVY)
    ctext(d,'@kangdalcom',y+100,64,WHITE,'en')
    return im.resize((W,H),Image.LANCZOS)
def render(sp):
    name=sp['name']; out='fr_'+name; shutil.rmtree(out,ignore_errors=True); os.makedirs(out); fi=0; cuts=[]
    scenes=[(frame_title(sp),1.4)]+[(frame_item(sp,i,it),2.3) for i,it in enumerate(sp['items'])]+[(frame_outro(sp),1.4)]
    for img,sec in scenes:
        cuts.append(fi/FPS); n=int(sec*FPS)
        for t in range(n):
            k=1+0.05*min(1,t/n)  # zoom
            w,h=int(W*k),int(H*k); fr=img.resize((w,h),Image.BILINEAR).crop(((w-W)//2,(h-H)//2,(w-W)//2+W,(h-H)//2+H))
            if t<7:  # quick slide-in from right
                off=int(W*(1-t/7)**2); bg=Image.new('RGB',(W,H),NAVY); bg.paste(fr,(off,0)); fr=bg
            fr.save(f'{out}/{fi:05d}.jpg',quality=92); fi+=1
    T=fi/FPS; a=music2.music(T,sp.get('seed',1),sp.get('key',0))
    for c in cuts[1:]:
        n=int(.3*44100); t=np.arange(n)/44100; music2.add(a,.35*np.sin(2*np.pi*np.cumsum(500+900*t/.3)/44100)*np.exp(-t*8),c-0.05 if c>0.05 else c)
    a=a/np.abs(a).max()*.85
    import wave; st=(np.stack([a,a],1)*32767).astype(np.int16)
    w=wave.open(name+'.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(st.tobytes()); w.close()
    subprocess.run(f'ffmpeg -y -loglevel error -framerate {FPS} -i {out}/%05d.jpg -i {name}.wav -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart {name}.mp4',shell=True,check=True)
    shutil.rmtree(out); os.remove(name+'.wav')
if __name__=='__main__': render(json.load(open(sys.argv[1])))
