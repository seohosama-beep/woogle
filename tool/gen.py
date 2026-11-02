from PIL import Image, ImageDraw, ImageFont
import numpy as np, math, os, shutil, subprocess, wave, random, sys
W,H=1080,1920; S=2; FPS=30; INK=(25,25,30)
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
if not os.path.exists(FB):
    import glob; FB=[f for f in glob.glob('/usr/share/fonts/**/*CJK*',recursive=True)][0]
def font(sz):
    try: return ImageFont.truetype(FB,sz*S,index=1)
    except Exception: return ImageFont.truetype(FB,sz*S)
TOFU=(255,252,240); TOP=(240,232,205)
def text_c(d,txt,y,sz,col=INK,stroke=0,sc='white',cx=None):
    f=font(sz); cx=(W/2 if cx is None else cx)
    for i,l in enumerate(txt.split('\n')):
        w=d.textlength(l,font=f); d.text((cx*S-w/2,(y+i*sz*1.3)*S),l,font=f,fill=col,stroke_width=stroke*S,stroke_fill=sc)
def tofu(mood='happy',col=TOFU):
    cw,ch=560,640; im=Image.new('RGBA',(cw*S,ch*S),(0,0,0,0)); d=ImageDraw.Draw(im); s=S; lw=7*s
    arms={'happy':[((90,380),(20,250)),((470,380),(540,250))],'shock':[((90,380),(30,300)),((470,380),(530,300))],
          'smug':[((90,400),(60,520)),((470,400),(500,520))],'dead':[((90,430),(50,560)),((470,430),(510,560))],
          'derp':[((90,380),(10,300)),((470,400),(545,470))],'angry':[((90,380),(40,280)),((470,380),(520,280))]}[mood]
    for a,b in arms: d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=INK,width=lw)
    d.line([(200*s,560*s),(195*s,620*s)],fill=INK,width=lw); d.line([(360*s,560*s),(365*s,620*s)],fill=INK,width=lw)
    d.polygon([(90*s,200*s),(170*s,120*s),(500*s,120*s),(470*s,200*s)],fill=TOP,outline=INK,width=lw)
    d.rounded_rectangle([90*s,200*s,470*s,565*s],radius=18*s,fill=col,outline=INK,width=lw)
    d.polygon([(470*s,200*s),(500*s,120*s),(500*s,490*s),(470*s,565*s)],fill=TOP,outline=INK,width=lw)
    if mood=='happy':
        for ex in (205,355): d.arc([(ex-32)*s,300*s,(ex+32)*s,350*s],200,340,fill=INK,width=8*s)
        d.ellipse([160*s,360*s,200*s,385*s],fill=(255,170,170)); d.ellipse([360*s,360*s,400*s,385*s],fill=(255,170,170))
        d.chord([245*s,365*s,315*s,425*s],0,180,fill=INK)
    elif mood=='shock':
        for ex in (205,355):
            d.ellipse([(ex-38)*s,280*s,(ex+38)*s,356*s],fill='white',outline=INK,width=6*s); d.ellipse([(ex-13)*s,305*s,(ex+13)*s,331*s],fill=INK)
        d.ellipse([260*s,395*s,300*s,455*s],fill=INK)
    elif mood=='smug':
        for ex in (205,355):
            d.line([(ex-30)*s,325*s,(ex+30)*s,325*s],fill=INK,width=8*s); d.ellipse([(ex-10)*s,327*s,(ex+10)*s,345*s],fill=INK)
        d.arc([245*s,375*s,320*s,415*s],10,170,fill=INK,width=7*s)
    elif mood=='dead':
        for ex in (205,355):
            d.line([(ex-25)*s,300*s,(ex+25)*s,345*s],fill=INK,width=8*s); d.line([(ex+25)*s,300*s,(ex-25)*s,345*s],fill=INK,width=8*s)
        d.line([255*s,415*s,305*s,415*s],fill=INK,width=7*s)
        for c in [[(130,220),(170,280),(150,330)],[(430,230),(400,300),(440,350)]]: d.line([(x*s,y*s) for x,y in c],fill=INK,width=5*s)
    elif mood=='angry':
        for ex,sg in ((205,1),(355,-1)):
            d.line([(ex-35)*s,(290-12*sg)*s,(ex+35)*s,(290+12*sg)*s],fill=INK,width=9*s); d.ellipse([(ex-12)*s,310*s,(ex+12)*s,334*s],fill=INK)
        d.arc([245*s,395*s,320*s,440*s],200,340,fill=INK,width=8*s)
        d.ellipse([400*s,215*s,440*s,250*s],fill=(230,60,60))
    else:
        d.ellipse([150*s,265*s,260*s,375*s],fill='white',outline=INK,width=6*s); d.ellipse([160*s,300*s,195*s,335*s],fill=INK)
        d.ellipse([340*s,305*s,380*s,345*s],fill='white',outline=INK,width=5*s); d.ellipse([362*s,310*s,378*s,326*s],fill=INK)
        d.arc([220*s,370*s,350*s,440*s],10,160,fill=INK,width=7*s)
        d.chord([275*s,410*s,320*s,465*s],0,180,fill=(255,120,140),outline=INK,width=4*s)
    return im.resize((cw,ch),Image.LANCZOS)
def sparkle(d,cx,cy,r):
    pts=[(cx*S+(r if i%2==0 else r*.28)*math.cos(i*math.pi/4)*S, cy*S+(r if i%2==0 else r*.28)*math.sin(i*math.pi/4)*S) for i in range(8)]
    d.polygon(pts,fill='white',outline=INK,width=4*S)
# ---------- audio
SR=44100
def envl(n,a,dc): t=np.arange(n)/SR; return np.minimum(t/a,1)*np.exp(-t/dc)
def pluck(f,du,dc=.18,v=.3):
    n=int(du*SR); t=np.arange(n)/SR; return v*(np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)+.15*np.sin(6*np.pi*f*t))*envl(n,.003,dc)
def bass(f,du,v=.35):
    n=int(du*SR); t=np.arange(n)/SR; return v*(np.sign(np.sin(2*np.pi*f*t))*.5+.5*np.sin(2*np.pi*f*t))*envl(n,.005,.15)
def kick(v=.8):
    n=int(.25*SR); t=np.arange(n)/SR; f=120*np.exp(-t*25)+45; return v*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
def snare(v=.35):
    n=int(.18*SR); t=np.arange(n)/SR; return v*(np.random.randn(n)*.7+.3*np.sin(2*np.pi*190*t))*np.exp(-t*22)
def hat(v=.12):
    n=int(.05*SR); t=np.arange(n)/SR; return v*np.random.randn(n)*np.exp(-t*80)
def add(buf,x,at):
    i=int(at*SR); e=min(len(buf),i+len(x));
    if e>i: buf[i:e]+=x[:e-i]
def note(m): return 440*2**((m-69)/12)
def music(total,seed,key):
    np.random.seed(seed); rng=random.Random(seed)
    b=60/rng.choice([118,124,128,132]); buf=np.zeros(int(total*SR)+SR)
    prog=rng.choice([[[60,64,67],[57,60,64],[53,57,60],[55,59,62]],[[60,64,67],[55,59,62],[57,60,64],[53,57,60]],[[60,64,67],[65,69,72],[67,71,74],[60,64,67]]])
    scale=[60,62,64,67,69,72,74,76,79]; mel=[rng.choice(scale)+12 for _ in range(16)]
    t=0; beat=0
    while t<total:
        ch=prog[(beat//4)%4]
        if beat%4 in (0,2): add(buf,kick(),t)
        if beat%2==1: add(buf,snare(),t)
        add(buf,hat(),t); add(buf,hat(.07),t+b/2)
        add(buf,bass(note(ch[0]-12+key),b*.45),t); add(buf,bass(note(ch[0]+key),b*.3,.2),t+b/2)
        for m in ch: add(buf,pluck(note(m+key),b*.5,.08,.09),t+b/2)
        add(buf,pluck(note(mel[beat%16]+key),b,.22,.22),t)
        t+=b; beat+=1
    buf=buf[:int(total*SR)]; fd=int(.6*SR); buf[-fd:]*=np.linspace(1,0,fd); return buf*.55
def boing(v=.4):
    n=int(.4*SR); t=np.arange(n)/SR; f=300+200*np.sin(2*np.pi*12*t)*np.exp(-t*4); return v*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5)
def crush(v=.6):
    n=int(.5*SR); t=np.arange(n)/SR; f=400*np.exp(-t*6)+60; return v*(np.sin(2*np.pi*np.cumsum(f)/SR)*.6+np.random.randn(n)*.3*np.exp(-t*8))*np.exp(-t*4)
def savewav(name,x):
    x=x/max(1e-9,np.abs(x).max())*.85; st=(np.stack([x,x],1)*32767).astype(np.int16)
    w=wave.open(name,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
# ---------- reels
def render(name,scenes,seed,key):
    out='fr_'+name; shutil.rmtree(out,ignore_errors=True); os.makedirs(out); fi=0; cuts=[]
    for draw_base,chars,sec in scenes:
        cuts.append(fi/FPS)
        base=Image.new('RGB',(W*S,H*S),'white'); d=ImageDraw.Draw(base); draw_base(d)
        base=base.resize((W,H),Image.LANCZOS).convert('RGBA')
        cs=[(tofu(m,c).resize((w,int(w*640/560))),x,y) for m,c,w,x,y in chars]
        for t in range(int(sec*FPS)):
            fr=base.copy(); bob=int(12*math.sin(t/FPS*2*math.pi*1.6)); pop=0 if t>5 else (5-t)*14
            for k,(im,x,y) in enumerate(cs): fr.alpha_composite(im,(x,y+(bob if k%2==0 else -bob)+pop))
            fr.convert('RGB').save(f'{out}/{fi:05d}.png'); fi+=1
    T=fi/FPS
    import music2; a=music2.music(T,seed,key)
    for c in cuts[1:-1]: add(a,boing(),c)
    add(a,crush(),cuts[-1]); savewav(name+'.wav',a)
    subprocess.run(f'ffmpeg -y -loglevel error -framerate 30 -i {out}/%05d.png -i {name}.wav -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 192k -shortest -movflags +faststart {name}.mp4',shell=True,check=True)
    shutil.rmtree(out)
def vs(name,L,R,beats,ending,lc,rc,seed,key):
    def bg(extra):
        def f(d):
            d.rectangle([0,0,W//2*S,H*S],fill=lc); d.rectangle([W//2*S,0,W*S,H*S],fill=rc)
            d.line([(W//2*S,0),(W//2*S,H*S)],fill=INK,width=6*S)
            text_c(d,L,150,64,cx=270); text_c(d,R,150,64,cx=810); extra(d)
        return f
    sc=[]
    def title(d):
        d.ellipse([(430)*S,790*S,650*S,1010*S],fill=(230,50,50),outline=INK,width=8*S); text_c(d,'VS',840,100,'white')
    sc.append((bg(title),[('happy',TOFU,420,60,560),('dead',TOFU,420,600,560)],2.0))
    for lt,rt,lm,rm in beats:
        sc.append((bg(lambda d,lt=lt,rt=rt:(text_c(d,lt,1420,54,cx=270),text_c(d,rt,1420,54,cx=810))),[(lm,TOFU,420,60,560),(rm,TOFU,420,600,560)],2.4))
    def end(d):
        d.rectangle([0,1350*S,W*S,1750*S],fill=(30,30,36)); text_c(d,ending,1440,68,'white')
    sc.append((bg(end),[('smug',TOFU,420,60,560),('dead',TOFU,420,600,560)],2.6))
    render(name,sc,seed,key)
def types(name,title,items,ending,seed,key):
    cols=[(255,214,214),(214,236,255),(220,245,215),(255,236,200),(235,220,255)]
    sc=[]
    def t0(d):
        text_c(d,title,300,96); random.seed(seed)
        for _ in range(6): sparkle(d,random.choice([random.randint(80,240),random.randint(840,1000)]),random.randint(700,1400),random.randint(28,48))
    sc.append((t0,[('derp',TOFU,560,260,700)],2.0))
    for i,(tag,q,m) in enumerate(items):
        def f(d,tag=tag,q=q,c=cols[i%5]):
            d.rectangle([0,0,W*S,H*S],fill=c); d.rounded_rectangle([240*S,180*S,840*S,330*S],radius=75*S,fill=INK)
            text_c(d,tag,205,72,'white'); text_c(d,q,1440,58)
        sc.append((f,[(m,TOFU,560,260,700)],2.6))
    def e(d): d.rectangle([0,0,W*S,H*S],fill=(30,30,36)); text_c(d,ending,1440,68,'white')
    sc.append((e,[('dead',TOFU,560,260,700)],2.4))
    render(name,sc,seed,key)
job=sys.argv[1]
if job=='4': types('reel4','회식 자리\n유형별 특징',[
  ('막내형','"고기 제가 굽겠습니다!!"\n(본인은 한 점도 못 먹음)','shock'),('부장님형','"자, 마지막 한 잔만~"\n(이게 다섯 번째)','smug'),
  ('총무형','"N빵 하면 1인당\n37,250원입니다"','happy'),('유령형','"화장실 좀…"\n(그 뒤로 아무도 못 봄)','derp')],'당신은 어떤 유형? 댓글로 ㄱㄱ',4,2)
elif job=='5': vs('reel5',"월요일 아침\n다짐","월요일 아침\n현실",[
  ('"6시 기상!\n미라클 모닝"','"알람 5번\n다시 끔"','happy','dead'),('"출근길에\n영어 공부"','"출근길에\n숏폼 2시간"','smug','derp'),
  ('"오늘 업무\n다 끝낸다!"','"벌써\n금요일 언제 와"','happy','dead'),('"칼퇴하고\n헬스장 간다"','"칼퇴하고\n침대 직행"','smug','dead')],'다짐은 다음 주 월요일에…',(255,236,200),(225,225,235),5,4)
elif job=='6': vs('reel6',"주말 계획\n(금요일 밤)","주말 현실\n(일요일 밤)",[
  ('"아침 일찍 일어나\n운동하고~"','"눈 떠보니\n오후 2시"','happy','dead'),
  ('"밀린 책\n다 읽어야지"','"유튜브 알고리즘에\n납치당함"','smug','derp'),
  ('"맛집 탐방\n가즈아!"','"배달앱 최근 주문\n재주문"','happy','smug'),
  ('"방 청소\n싹 해야지"','"빨래 산이\n더 커짐"','happy','shock')],'월요일: 안녕? ^^',(255,240,200),(215,225,245),6,0)
elif job=='7': types('reel7','택배 기다리는\n유형별 특징',[
  ('새로고침형','"배송조회 1분에\n12번 누름"','shock'),('현관 대기형','"발소리만 나면\n문 앞으로 질주"','derp'),
  ('해탈형','"언젠간 오겠지…"\n(3주째)','smug'),('분노형','"배송완료인데\n왜 없냐고!!"','angry')],'당신은 몇 번? 댓글 ㄱㄱ',7,3)
elif job=='8': vs('reel8',"장보기 전\n다짐","장보기 후\n현실",[
  ('"필요한 것만\n딱 3개!"','"카트 꽉 참"','smug','shock'),
  ('"간식은\n절대 안 사"','"1+1이라\n어쩔 수 없었어"','happy','derp'),
  ('"예산 3만원\n지킨다"','"영수증 89,400원"','happy','dead'),
  ('"채소 많이\n먹어야지"','"채소는 냉장고에서\n자연사"','smug','dead')],'다음 주엔 진짜 3개만…',(220,245,215),(255,220,215),8,5)
elif job=='9': types('reel9','단톡방\n유형별 특징',[
  ('읽씹형','"1 사라짐…\n그리고 침묵"','smug'),('ㅋㅋ봇형','"ㅋㅋㅋㅋㅋㅋㅋㅋ"\n(내용은 안 읽음)','happy'),
  ('새벽 폭주형','"새벽 3시에\n메시지 300개"','derp'),('투표 안 함형','"약속 날짜 투표\n끝까지 안 누름"','shock')],'단톡방에 태그해 봐 ㅋㅋ',9,-3)
elif job=='10': vs('reel10',"알람 맞출 때\n나","알람 울릴 때\n나",[
  ('"6시에 일어나서\n여유롭게~"','"5분만…\n(x7)"','happy','dead'),
  ('"알람 하나면\n충분해"','"알람 12개\n다 끔"','smug','derp'),
  ('"아침밥\n챙겨 먹어야지"','"양치하면서\n신발 신음"','happy','shock'),
  ('"오늘부터\n갓생 산다"','"지각 사유\n고민 중"','smug','dead')],'내일의 내가 하겠지 뭐',(255,236,200),(225,225,235),10,7)

def meme(name,frames,seed,key):
    sc=[]
    for top,bot,mood,bg,sec in frames:
        def f(d,top=top,bot=bot,bg=bg):
            d.rectangle([0,0,W*S,H*S],fill=bg)
            d.rectangle([0,0,W*S,420*S],fill='white'); d.line([(0,420*S),(W*S,420*S)],fill=INK,width=6*S)
            text_c(d,top,130 if top.count('\n')==0 else 90,82)
            if bot:
                d.rounded_rectangle([60*S,1440*S,1020*S,1760*S],radius=40*S,fill=(30,30,36))
                text_c(d,bot,1500 if bot.count('\n')==0 else 1470,68,'white')
        sc.append((f,[(mood,TOFU,620,230,620)] if mood else [],sec))
    render(name,sc,seed,key)
if job=='11': meme('reel11',[
  ('아무도:','', None,(245,245,245),1.2),
  ('나:','', 'smug',(255,236,200),1.0),
  ('퇴근 10분 전\n갑자기 일 잘하는 나','업무 능력 200% 각성 ⚡','happy',(255,214,214),2.6),
  ('퇴근 10분 전\n갑자기 일 잘하는 나','(오전 내내는 뭐 했냐고?)','derp',(255,214,214),2.4),
  ('퇴근 10분 전\n갑자기 일 잘하는 나','…모르겠음 ㅎ','dead',(30,30,36),2.2)],11,0)
elif job=='12': meme('reel12',[
  ('POV:\n엄마가 "잠깐 이리 와봐"','', 'shock',(214,236,255),2.0),
  ('내 머릿속 1초 만에','설거지 안 했나…?','shock',(255,236,200),2.0),
  ('내 머릿속 1초 만에','택배 온 거 들켰나…?','dead',(255,214,214),2.0),
  ('내 머릿속 1초 만에','카드값 문자 봤나…?','dead',(235,220,255),2.0),
  ('엄마:','"이거 사진 어떻게 보내?"','derp',(220,245,215),2.6)],12,5)
elif job=='13': meme('reel13',[
  ('월급 3주 뒤\n통장 잔고 확인하는 나','','smug',(245,245,245),1.8),
  ('1단계','손가락으로 눈 가리고 앱 켬','shock',(255,236,200),2.2),
  ('2단계','실눈 뜨고 숫자만 봄','derp',(214,236,255),2.2),
  ('3단계','…','dead',(255,214,214),1.8),
  ('결론','0원 아니면 다행이다 ^^','happy',(30,30,36),2.4)],13,-2)
elif job=='14': meme('reel14',[
  ('다이어트 3일차\n치킨 냄새 맡았을 때','','smug',(245,245,245),1.8),
  ('뇌','"참아. 넌 할 수 있어"','smug',(214,236,255),2.0),
  ('위','"…조금만 먹으면 괜찮아"','derp',(255,236,200),2.0),
  ('코','"치킨. 치킨. 치킨."','shock',(255,214,214),2.0),
  ('결과','1인 1닭 + 콜라 1.25L','happy',(30,30,36),2.6)],14,7)

if job.endswith('.json'):
    import json; sp=json.load(open(job)); k=sp.pop('kind')
    if 'lc' in sp: sp['lc']=tuple(sp['lc']); sp['rc']=tuple(sp['rc'])
    if k=='meme': sp['frames']=[(a,b,c,tuple(d),e) for a,b,c,d,e in sp['frames']]
    if k=='types': sp['items']=[tuple(x) for x in sp['items']]
    if k=='vs': sp['beats']=[tuple(x) for x in sp['beats']]
    {'vs':vs,'types':types,'meme':meme}[k](**sp); sys.exit(0)
