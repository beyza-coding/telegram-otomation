import os,re,sys,json,mimetypes
from datetime import datetime,date
import requests
B=os.path.dirname(os.path.abspath(__file__))
T=os.environ.get("BOT_TOKEN");C=os.environ.get("CHANNEL_ID")
if not T or not C: sys.exit("no token")
A="https://api.telegram.org/bot"+T
SF=B+"/sent.log";LF=B+"/last_send.txt"
sent=set(open(SF,encoding="utf-8").read().split()) if os.path.exists(SF) else set()
BTN=json.dumps({"inline_keyboard":[[{"text":"\U0001F464 Guncel Giris","url":"https://bit.ly/bymvtlgrm"}],[{"text":"\U0001F4F1 Twitter","url":"https://x.com/BayMavi_Resmi26"}],[{"text":"\U0001F4F8 Instagram","url":"https://bit.ly/baymavi-guncel"}]]})
med=[]
for r,d,fs in os.walk(B):
 if ".git" in r: continue
 for f in fs:
  fl=f.lower()
  if fl.endswith((".mp4",".png",".jpg",".jpeg")) and "story" not in fl: med.append(os.path.join(r,f))
rel=lambda p:os.path.relpath(p,B).replace("\\","/")
def fd(f):
 m=re.search(r'(\d{2})-(\d{2})-(\d{4})',os.path.basename(f))
 try: return date(int(m[3]),int(m[2]),int(m[1])) if m else None
 except: return None
def sc(f):
 fl=f.lower()
 if fl.endswith(".mp4"): return 0
 for i,k in enumerate(["banner","promosyon","rectangle","ig_post","square","e_posta"]):
  if k in fl: return 1+i
 return 30
today=date.today()
td=sorted([f for f in med if fd(f)==today and rel(f) not in sent],key=sc)
t=td[0] if td else None
if not t:
 last=None
 if os.path.exists(LF):
  try: last=datetime.fromisoformat(open(LF).read().strip())
  except: last=None
 if last and (datetime.now()-last).total_seconds()<10800: sys.exit("gap")
 seen=set();cand=[]
 for f in sorted(med):
  if fd(f): continue
  fo=os.path.dirname(f)
  if fo in seen: continue
  seen.add(fo)
  b=sorted([g for g in med if os.path.dirname(g)==fo and not fd(g)],key=sc)[0]
  if rel(b) not in sent: cand.append(b)
 t=cand[0] if cand else None
if not t: sys.exit("yok")
nm=re.sub(r'^\d{2}-\d{2}-\d{4}-','',os.path.splitext(os.path.basename(t))[0]).replace("_"," ").replace("-"," ").strip().title()
fn=os.path.basename(os.path.dirname(t)).replace("_"," ").strip()
p=t.lower()
if fd(t)==today or "spor" in p: cap="\u26BD "+nm+"\n\n\U0001F3C6 Bugunun maci BayMavi'de! En yuksek oranlar seni bekliyor.\n\n\U0001F3AF Bahsini yap, kazanan taraf ol!"
elif "ilk yatirim" in p or "i_lk_yatirim" in p or "hos_geldi" in p: cap="\U0001F381 \u0130lk Yat\u0131r\u0131m Bonusu\n\n\U0001F4B0 \u0130lk iki yat\u0131r\u0131m\u0131na %100, 30.000 TL'ye kadar bonus! Hem casino hem sporda ge\u00E7erli.\n\n\U0001F3AF Hemen yat\u0131r, bonusu kap!"
elif "bonus" in p: cap="\U0001F381 "+fn+"\n\n\U0001F4B0 "+fn+" \u015Fimdi BayMavi'de! F\u0131rsat\u0131 ka\u00E7\u0131rma.\n\n\U0001F3AF Hemen kat\u0131l, avantaj\u0131 kap!"
elif "tournament" in p: cap="\U0001F3C6 Turnuva: "+nm+"\n\n\u26A1 Buyuk odul havuzu BayMavi'de!\n\n\U0001F3AF Hemen katil, zirveye oyna!"
elif "sosyal" in p: cap="\U0001F4E2 "+nm+"\n\n\U0001F499 BayMavi'yle kal, firsatlari kacirma!\n\n\U0001F3AF Takipte kal!"
else: cap="\U0001F3B0 Yeni Oyun: "+nm+"\n\n\u2728 "+nm+" artik BayMavi'de!\n\n\U0001F3AF Hemen oyna, kazanci yakala!"
mt="video" if p.endswith(".mp4") else "photo"
with open(t,"rb") as fh:
 r=requests.post(A+"/"+("sendVideo" if mt=="video" else "sendPhoto"),data={"chat_id":C,"caption":cap,"reply_markup":BTN},files={mt:(os.path.basename(t),fh,mimetypes.guess_type(t)[0])},timeout=180)
try: ok=r.json().get("ok")
except: ok=False
print(("OK " if ok else "ERR ")+rel(t)+("" if ok else " "+r.text[:200]))
if ok:
 open(SF,"a",encoding="utf-8").write(rel(t)+"\n");open(LF,"w").write(datetime.now().isoformat())
