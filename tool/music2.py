import numpy as np, random
SR=44100
def add(buf,x,at):
    i=int(at*SR); e=min(len(buf),i+len(x))
    if e>i: buf[i:e]+=x[:e-i]
def note(m): return 440*2**((m-69)/12)
def kick(v=.8):
    n=int(.25*SR); t=np.arange(n)/SR; f=120*np.exp(-t*25)+45; return v*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
def hat(v=.12):
    n=int(.05*SR); t=np.arange(n)/SR; return v*np.random.randn(n)*np.exp(-t*80)
def saw(f,du,v=.18,dc=.12):
    n=int(du*SR); t=np.arange(n)/SR; ph=(f*t)%1
    x=2*ph-1; x=x+0.5*(2*((f*1.005*t)%1)-1)
    a=np.minimum(t/.004,1)*np.exp(-t/dc); return v*x*a
def clap(v=.4):
    n=int(.2*SR); t=np.arange(n)/SR; nz=np.random.randn(n)
    e=np.exp(-t*30)+0.6*np.exp(-np.maximum(t-.012,0)*30)*(t>.012)
    return v*nz*e
def openhat(v=.14):
    n=int(.18*SR); t=np.arange(n)/SR; return v*np.random.randn(n)*np.exp(-t*18)
def sub(f,du,v=.4):
    n=int(du*SR); t=np.arange(n)/SR; return v*np.sin(2*np.pi*f*t)*np.minimum(t/.004,1)*np.exp(-t/.18)
def riser(du,v=.25):
    n=int(du*SR); t=np.arange(n)/SR; f=300+2500*(t/du)**2
    return v*np.sin(2*np.pi*np.cumsum(f)/SR)*(t/du)
def music(total,seed,key):
    np.random.seed(seed); rng=random.Random(seed)
    bpm=rng.choice([150,156,160]); b=60/bpm
    buf=np.zeros(int(total*SR)+SR)
    prog=rng.choice([[[60,64,67],[67,71,74],[69,72,76],[65,69,72]],[[57,60,64],[65,69,72],[60,64,67],[67,71,74]],[[60,64,67],[65,69,72],[67,71,74],[67,71,74]]])
    hook=[rng.choice([0,2,4,7,9,12]) for _ in range(8)]
    t=0; beat=0
    while t<total:
        ch=prog[(beat//4)%4]; root=ch[0]+key
        add(buf,kick(.9),t)
        add(buf,openhat(),t+b/2); add(buf,hat(.1),t+b/4); add(buf,hat(.1),t+3*b/4)
        if beat%2==1: add(buf,clap(),t)
        add(buf,sub(note(root-24),b*.5),t+b/2)
        # 16th arpeggio
        for k in range(4):
            m=ch[k%3]+12+key+(12 if k==3 else 0)
            add(buf,saw(note(m),b/4,.07,.05),t+k*b/4)
        # hook lead every bar on 8ths
        if (beat//4)%2==1 or beat>=16:
            for k in range(2):
                m=60+key+hook[(beat*2+k)%8]+12
                add(buf,saw(note(m),b/2,.13,.1),t+k*b/2)
        t+=b; beat+=1
    if total>3: add(buf,riser(1.5),max(0,total-3.5))
    buf=buf[:int(total*SR)]; fd=int(.5*SR); buf[-fd:]*=np.linspace(1,0,fd)
    return buf*.6
