“””
╔══════════════════════════════════════════════════════════════════════════╗
║         Z-ORDER  ·  Print Workflow Platform  ·  v5.0 FINAL             ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Developer   : Abdulrahman Fallah                                       ║
║  Brand       : Abdulrahman Shawush                                      ║
║  Year        : 2026                                                     ║
╠══════════════════════════════════════════════════════════════════════════╣
║  pip install streamlit pillow                                           ║
║  streamlit run z_order_app.py                                           ║
║  admin@zorder.iq  /  Admin@2025                                         ║
╚══════════════════════════════════════════════════════════════════════════╝
“””
import streamlit as st
import sqlite3, hashlib, datetime, base64
import pandas as pd
from pathlib import Path

st.set_page_config(page_title=“Z-Order | إدارة المطبعة”,
page_icon=“🖨️”, layout=“wide”,
initial_sidebar_state=“collapsed”)

DEVELOPER = “Abdulrahman Fallah”
BRAND     = “Abdulrahman Shawush”
APP_NAME  = “Z-Order”
APP_VER   = “5.0”
YEAR      = “2026”
DB_PATH   = “z_order.db”
UPLOAD_DIR = Path(“z_order_uploads”)
for sub in [“designs”,“agents”]:
(UPLOAD_DIR / sub).mkdir(parents=True, exist_ok=True)

ROLES = {
“admin”:      {“ar”:“المدير العام”,    “icon”:“🛡️”,“clr”:”#e8a020”},
“sales”:      {“ar”:“المبيعات”,         “icon”:“💼”,“clr”:”#3b82f6”},
“design”:     {“ar”:“التصميم”,          “icon”:“🎨”,“clr”:”#a855f7”},
“purchase”:   {“ar”:“المشتريات”,        “icon”:“📦”,“clr”:”#22c55e”},
“production”: {“ar”:“الإنتاج”,          “icon”:“🖨️”,“clr”:”#ff6b35”},
“agent”:      {“ar”:“مندوب مبيعات”,    “icon”:“🗺️”,“clr”:”#06b6d4”},
}

ROLE_PAGES = {
“admin”:      [“📊 الرئيسية”,“👥 الموظفون”,“📋 الأوردرات”,“💰 المالية”,“🚨 البلاغات”,“🗺️ المندوبون”],
“sales”:      [“📊 الرئيسية”,“➕ أوردر جديد”,“📋 أوردراتي”,“💰 تقرير مبيعات”,“📦 طلب شراء”,“🚨 بلاغ”],
“design”:     [“📊 الرئيسية”,“🎨 التصميم”,“📦 طلب شراء”,“🚨 بلاغ”],
“purchase”:   [“📊 الرئيسية”,“📦 طلبات الشراء”,“🚨 بلاغ”],
“production”: [“📊 الرئيسية”,“🖨️ الإنتاج”,“📋 الأوردرات”,“📦 طلب شراء”,“🚨 بلاغ”],
“agent”:      [“📊 الرئيسية”,“🗺️ زيارة جديدة”,“📋 زياراتي”,“🚨 بلاغ”],
}

CSS = “””

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
:root{
  --bg0:#07080b;--bg1:#0c0e14;--bg2:#12151f;--bg3:#181c28;--bg5:#242a40;
  --bdr:#232840;--bdr2:#2c3352;
  --acc:#e8a020;--acc2:#ff6b35;
  --blue:#3b82f6;--green:#22c55e;--red:#ef4444;--purple:#a855f7;
  --t1:#edf0f6;--t2:#8892a8;--t3:#404860;
  --r:10px;--r2:14px;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'IBM Plex Sans Arabic',sans-serif !important;
  background:var(--bg0) !important;color:var(--t1) !important;direction:rtl !important;}
section[data-testid="stSidebar"]{display:none !important;}
[data-testid="collapsedControl"]{display:none !important;}
.stApp{background:var(--bg0) !important;}
.main .block-container{padding:0 !important;max-width:100% !important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg1);}
::-webkit-scrollbar-thumb{background:var(--bg5);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--acc);}

/* inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,
.stSelectbox>div>div,.stNumberInput>div>div>input,
[data-baseweb="input"] input{
  background:var(--bg3) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r) !important;color:var(--t1) !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;font-size:.9rem !important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
  border-color:var(--acc) !important;box-shadow:0 0 0 3px rgba(232,160,32,.12) !important;}

/* buttons */
.stButton>button{
  background:linear-gradient(135deg,var(--acc),var(--acc2)) !important;
  color:#07080b !important;font-weight:700 !important;border:none !important;
  border-radius:var(--r) !important;padding:.55rem 1.2rem !important;
  min-height:42px !important;width:100% !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;
  transition:transform .15s,box-shadow .15s !important;cursor:pointer;}
.stButton>button:hover{transform:translateY(-2px) !important;
  box-shadow:0 6px 20px rgba(232,160,32,.35) !important;}
.stButton>button:active{transform:translateY(0) !important;}

/* tabs */
.stTabs [data-baseweb="tab-list"]{
  background:var(--bg3) !important;border-radius:var(--r) !important;
  gap:3px !important;padding:4px !important;border:1px solid var(--bdr) !important;
  overflow-x:auto !important;flex-wrap:nowrap !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:var(--t2) !important;
  border-radius:7px !important;font-size:.82rem !important;border:none !important;white-space:nowrap !important;}
.stTabs [aria-selected="true"]{background:var(--bg5) !important;color:var(--acc) !important;
  border-bottom:2px solid var(--acc) !important;}

/* metrics */
[data-testid="stMetric"]{background:var(--bg2) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r2) !important;padding:.9rem 1rem !important;}
[data-testid="stMetricLabel"]{color:var(--t2) !important;font-size:.72rem !important;}
[data-testid="stMetricValue"]{color:var(--acc) !important;
  font-family:'JetBrains Mono',monospace !important;font-size:1.3rem !important;}

/* expanders */
.streamlit-expanderHeader{background:var(--bg2) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r) !important;font-size:.88rem !important;}
.streamlit-expanderContent{background:var(--bg1) !important;border:1px solid var(--bdr2) !important;
  border-top:none !important;}

/* dataframes */
.stDataFrame,[data-testid="stDataFrame"],iframe[title="st.dataframe"]{
  width:100% !important;border-radius:var(--r) !important;
  border:1px solid var(--bdr) !important;overflow-x:auto !important;}

/* misc */
[data-testid="stFileUploader"]{background:var(--bg3) !important;
  border:1.5px dashed var(--bdr2) !important;border-radius:var(--r) !important;}
.stAlert{background:var(--bg2) !important;border-radius:var(--r) !important;}
hr{border-color:var(--bdr) !important;margin:.9rem 0 !important;}

/* top nav */
.topnav{position:sticky;top:0;z-index:999;background:var(--bg1);
  border-bottom:1px solid var(--bdr);padding:.5rem 1.1rem;
  display:flex;align-items:center;gap:.55rem;flex-wrap:nowrap;overflow-x:auto;}
.topnav-logo{font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;
  color:var(--acc);letter-spacing:-.06em;white-space:nowrap;flex-shrink:0;}
.topnav-logo .sep{color:var(--t3);}
.topnav-user{display:flex;align-items:center;gap:.4rem;background:var(--bg3);
  border:1px solid var(--bdr2);border-radius:999px;padding:.28rem .7rem .28rem .35rem;
  white-space:nowrap;flex-shrink:0;margin-right:auto;}
.uavatar{width:26px;height:26px;background:linear-gradient(135deg,var(--acc),var(--acc2));
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.7rem;font-weight:700;color:#07080b;flex-shrink:0;}

/* page wrap */
.pw{padding:1.1rem 1.4rem 6.5rem;max-width:1300px;margin:0 auto;}

/* page header */
.ph{display:flex;align-items:center;gap:.7rem;margin-bottom:1.15rem;}
.ph-icon{font-size:1.5rem;background:var(--bg2);border:1px solid var(--bdr2);
  border-radius:var(--r);width:46px;height:46px;display:flex;
  align-items:center;justify-content:center;flex-shrink:0;}
.ph h2{font-size:1.15rem;font-weight:700;color:var(--t1);margin:0;}
.ph p{font-size:.74rem;color:var(--t3);margin:0;}

/* cards */
.card{background:var(--bg2);border:1px solid var(--bdr2);border-radius:var(--r2);
  padding:1rem 1.2rem;margin-bottom:.65rem;transition:border-color .2s,transform .15s;}
.card:hover{border-color:var(--acc);transform:translateY(-1px);}

/* info card */
.icard{background:linear-gradient(135deg,rgba(232,160,32,.07),rgba(255,107,53,.04));
  border:1px solid rgba(232,160,32,.2);border-right:3px solid var(--acc);
  border-radius:var(--r2);padding:.85rem 1.1rem;margin-bottom:.9rem;
  font-size:.82rem;color:var(--t2);line-height:1.85;}

/* badges */
.badge{display:inline-flex;align-items:center;gap:3px;padding:.16rem .55rem;
  border-radius:999px;font-size:.63rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;}
.b-new{background:rgba(59,130,246,.14);color:#60a5fa;border:1px solid rgba(59,130,246,.25);}
.b-ready{background:rgba(34,197,94,.14);color:#4ade80;border:1px solid rgba(34,197,94,.25);}
.b-print{background:rgba(255,107,53,.14);color:#fb923c;border:1px solid rgba(255,107,53,.25);}
.b-done{background:rgba(34,197,94,.1);color:#16a34a;border:1px solid rgba(34,197,94,.2);}
.b-deliv{background:rgba(6,182,212,.12);color:#06b6d4;border:1px solid rgba(6,182,212,.2);}
.b-pend{background:rgba(251,191,36,.12);color:#fbbf24;border:1px solid rgba(251,191,36,.2);}
.b-appr{background:rgba(34,197,94,.12);color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-rej{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.2);}
.b-sev-lo{background:rgba(34,197,94,.12);color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-sev-md{background:rgba(251,191,36,.12);color:#fbbf24;border:1px solid rgba(251,191,36,.2);}
.b-sev-hi{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.2);}
.b-abuy{background:rgba(34,197,94,.12);color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-apot{background:rgba(59,130,246,.12);color:#3b82f6;border:1px solid rgba(59,130,246,.2);}
.b-ano{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.2);}

/* section label */
.sec{font-size:.67rem;font-weight:700;color:var(--t3);
  text-transform:uppercase;letter-spacing:.1em;margin:.85rem 0 .45rem;}

/* footer */
.footer{position:fixed;bottom:0;left:0;right:0;background:var(--bg1);
  border-top:1px solid var(--bdr);padding:.42rem 1.1rem;
  display:flex;align-items:center;justify-content:space-between;
  font-size:.66rem;color:var(--t3);z-index:9999;gap:.4rem;flex-wrap:wrap;}
.footer .hi{color:var(--acc);font-weight:600;}

/* login */
.logo-big{font-family:'JetBrains Mono',monospace;font-size:2.1rem;font-weight:700;
  color:var(--acc);letter-spacing:-.07em;text-align:center;}
.logo-big .sep{color:var(--t3);}

/* nav selectbox */
.nav-sel .stSelectbox>div>div{background:var(--bg2) !important;
  border:1px solid var(--acc) !important;font-weight:600 !important;
  font-size:.87rem !important;border-radius:var(--r) !important;}

/* mobile */
@media(max-width:768px){
  .pw{padding:.65rem .45rem 6.5rem;}
  .ph-icon{width:34px;height:34px;font-size:1.1rem;}
  .ph h2{font-size:.98rem;}
  [data-testid="column"]{width:100% !important;flex:0 0 100% !important;
    min-width:100% !important;padding:0 !important;}
  .stButton>button{font-size:.83rem !important;min-height:46px !important;}
  [data-testid="stMetricValue"]{font-size:1rem !important;}
  .topnav{padding:.4rem .55rem;}
  .footer{font-size:.59rem;padding:.32rem .55rem;}
}
</style>

“””
st.markdown(CSS, unsafe_allow_html=True)

# ─── DB ────────────────────────────────────────────────────────────────────────

def _conn():
c = sqlite3.connect(DB_PATH, check_same_thread=False)
c.row_factory = sqlite3.Row; return c

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def qall(sql, p=()):
c=_conn(); r=c.execute(sql,p).fetchall(); c.close(); return [dict(x) for x in r]

def qone(sql, p=()):
c=_conn(); r=c.execute(sql,p).fetchone(); c.close(); return dict(r) if r else None

def qrun(sql, p=()):
c=_conn(); cur=c.execute(sql,p); c.commit(); lid=cur.lastrowid; c.close(); return lid

def init_db():
c=_conn(); x=c.cursor()
x.execute(””“CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
full_name TEXT NOT NULL, username TEXT UNIQUE NOT NULL,
email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
role TEXT NOT NULL, is_active INTEGER DEFAULT 1,
created_at TEXT DEFAULT(datetime(‘now’,‘localtime’)))”””)
x.execute(””“CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_number TEXT UNIQUE NOT NULL, customer_name TEXT NOT NULL,
description TEXT NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL,
created_at TEXT DEFAULT(datetime(‘now’,‘localtime’)),
created_by_id INTEGER, created_by_name TEXT,
status TEXT DEFAULT ‘جديد’,
design_status TEXT DEFAULT ‘قيد الانتظار’,
design_file_path TEXT DEFAULT ‘’, design_link TEXT DEFAULT ‘’,
design_notes TEXT DEFAULT ‘’, design_updated TEXT DEFAULT ‘’, design_by TEXT DEFAULT ‘’,
production_status TEXT DEFAULT ‘قيد الانتظار’,
production_notes TEXT DEFAULT ‘’, production_updated TEXT DEFAULT ‘’, production_by TEXT DEFAULT ‘’,
delivered INTEGER DEFAULT 0, delivered_at TEXT DEFAULT ‘’, delivered_by TEXT DEFAULT ‘’)”””)
x.execute(””“CREATE TABLE IF NOT EXISTS purchase_requests(
id INTEGER PRIMARY KEY AUTOINCREMENT,
requester_id INTEGER NOT NULL, requester_name TEXT NOT NULL, department TEXT NOT NULL,
item_name TEXT NOT NULL, quantity TEXT NOT NULL, urgency TEXT DEFAULT ‘عادي’,
notes TEXT DEFAULT ‘’, status TEXT DEFAULT ‘قيد المراجعة’,
reviewed_by TEXT DEFAULT ‘’, reviewed_at TEXT DEFAULT ‘’,
created_at TEXT DEFAULT(datetime(‘now’,‘localtime’)))”””)
x.execute(””“CREATE TABLE IF NOT EXISTS incident_reports(
id INTEGER PRIMARY KEY AUTOINCREMENT,
reporter_id INTEGER, reporter_name TEXT, department TEXT,
description TEXT NOT NULL, severity TEXT DEFAULT ‘متوسط’,
status TEXT DEFAULT ‘مفتوح’,
created_at TEXT DEFAULT(datetime(‘now’,‘localtime’)),
resolved_at TEXT DEFAULT ‘’)”””)
x.execute(””“CREATE TABLE IF NOT EXISTS agent_visits(
id INTEGER PRIMARY KEY AUTOINCREMENT,
agent_id INTEGER, agent_name TEXT, customer_name TEXT NOT NULL,
location TEXT DEFAULT ‘’, visit_status TEXT DEFAULT ‘محتمل’,
notes TEXT DEFAULT ‘’, image_path TEXT DEFAULT ‘’,
visited_at TEXT DEFAULT(datetime(‘now’,‘localtime’)))”””)
try:
x.execute(“INSERT INTO users(full_name,username,email,password,role) VALUES(?,?,?,?,?)”,
(“المدير العام”,“admin”,“admin@zorder.iq”,_hash(“Admin@2025”),“admin”))
except sqlite3.IntegrityError: pass
c.commit(); c.close()

def order_no():
n=(qone(“SELECT COUNT(*) c FROM orders”) or {}).get(“c”,0)
return f”ZO-{datetime.date.today().strftime(’%y%m%d’)}-{n+1:04d}”

def sync_status(oid):
o=qone(“SELECT design_status,production_status,delivered FROM orders WHERE id=?”,(oid,))
if not o: return
ds,ps,dv=o[“design_status”],o[“production_status”],o[“delivered”]
s=(“تم التسليم” if dv else “مكتمل” if ps==“مكتمل” else
“جاري الإنتاج” if ps==“جاري الإنتاج” else
“جاهز للإنتاج” if ds==“مكتمل” else “جديد”)
qrun(“UPDATE orders SET status=? WHERE id=?”,(s,oid))

def save_upload(f,sub=“designs”):
if not f: return “”
d=UPLOAD_DIR/sub; d.mkdir(exist_ok=True)
ts=datetime.datetime.now().strftime(”%Y%m%d%H%M%S”)
safe=””.join(ch for ch in f.name if ch.isalnum() or ch in “.*-”)
p=d/f”{ts}*{safe}”; p.write_bytes(f.read()); return str(p)

def dl_btn(fp, lbl=“⬇️ تحميل”):
p=Path(fp)
if p.exists(): st.download_button(lbl,p.read_bytes(),file_name=p.name,use_container_width=True)
else: st.caption(“⚠️ الملف غير موجود”)

# ─── UI Helpers ────────────────────────────────────────────────────────────────

ORD_BADGE={“جديد”:(“b-new”,“🔵 جديد”),“جاهز للإنتاج”:(“b-ready”,“🟢 جاهز”),
“جاري الإنتاج”:(“b-print”,“🟠 إنتاج”),“مكتمل”:(“b-done”,“✅ مكتمل”),
“تم التسليم”:(“b-deliv”,“📦 تسليم”)}
PUR_BADGE={“قيد المراجعة”:(“b-pend”,“⏳ قيد”),“موافق عليه”:(“b-appr”,“✅ موافق”),“مرفوض”:(“b-rej”,“❌ مرفوض”)}
SEV_BADGE={“منخفض”:(“b-sev-lo”,“🟢”),“متوسط”:(“b-sev-md”,“🟡”),“عالي”:(“b-sev-hi”,“🔴”)}
AGT_BADGE={“اشترى”:(“b-abuy”,“✅ اشترى”),“محتمل”:(“b-apot”,“🔵 محتمل”),“لن يشتري”:(“b-ano”,“❌ لا”)}

def badge(k,t): cls,lbl=t.get(k,(“b-pend”,k)); return f’<span class="badge {cls}">{lbl}</span>’
def hdr(icon,title,sub=””): st.markdown(f’<div class="ph"><div class="ph-icon">{icon}</div><div><h2>{title}</h2><p>{sub}</p></div></div>’,unsafe_allow_html=True)
def guide(txt):
with st.expander(“💡 إرشادات”,expanded=False):
st.markdown(f’<div class="icard">{txt}</div>’,unsafe_allow_html=True)
def footer():
st.markdown(f’<div class="footer"><span>🖨️ <span class="hi">{APP_NAME}</span> v{APP_VER}</span><span><span class="hi">{BRAND}</span> · Dev: <span class="hi">{DEVELOPER}</span></span><span>© {YEAR}</span></div>’,unsafe_allow_html=True)
def show_orders(role,uid_filter=None,title=“الأوردرات”):
hdr(“📋”,title)
hide_price=role not in (“admin”,“sales”)
sql=“SELECT * FROM orders”+(” WHERE created_by_id=?” if uid_filter else “”)+” ORDER BY id DESC”
rows=qall(sql,(uid_filter,) if uid_filter else ())
if not rows: st.info(“لا توجد أوردرات.”); return
sts=[“الكل”]+sorted({r[“status”] for r in rows})
sel=st.selectbox(“الحالة”,sts,key=f”o_{role}”)
if sel!=“الكل”: rows=[r for r in rows if r[“status”]==sel]
cols=[“order_number”,“customer_name”,“description”,“quantity”,“status”,“design_status”,“production_status”,“created_at”]
if not hide_price: cols.insert(4,“price”)
lbl={“order_number”:“الأوردر”,“customer_name”:“العميل”,“description”:“الوصف”,“quantity”:“الكمية”,
“price”:“السعر”,“status”:“الحالة”,“design_status”:“التصميم”,“production_status”:“الإنتاج”,“created_at”:“التاريخ”}
df=pd.DataFrame(rows); ok=[c for c in cols if c in df.columns]
st.dataframe(df[ok].rename(columns=lbl),use_container_width=True,hide_index=True)

# ─── GATEKEEPER ────────────────────────────────────────────────────────────────

def gatekeeper():
if st.session_state.get(“auth”): return True
*,col,*=st.columns([1,1.4,1])
with col:
st.markdown(”<br><br>”,unsafe_allow_html=True)
st.markdown(f’<div class="logo-big">Z<span class="sep">-</span>Order</div><div style="text-align:center;color:var(--t3);font-size:.77rem;margin:.3rem 0 1.4rem">Print Workflow Platform · v{APP_VER}</div>’,unsafe_allow_html=True)
st.markdown(’<div style="background:var(--bg2);border:1px solid var(--bdr2);border-radius:14px;padding:1.6rem 1.4rem;">’,unsafe_allow_html=True)
idn=st.text_input(“📧 الإيميل أو اسم المستخدم”,placeholder=“admin@zorder.iq”,key=“gk_i”)
pw=st.text_input(“🔒 كلمة المرور”,type=“password”,key=“gk_p”)
btn=st.button(“دخول ←”,key=“gk_b”)
st.markdown(”</div>”,unsafe_allow_html=True)
if btn:
if not idn or not pw: st.error(“يرجى إدخال البيانات.”); return False
i=idn.strip().lower()
u=qone(“SELECT * FROM users WHERE (lower(email)=? OR lower(username)=?) AND password=? AND is_active=1”,(i,i,_hash(pw)))
if u:
st.session_state.update(auth=True,uid=u[“id”],uname=u[“full_name”],role=u[“role”])
st.rerun()
else: st.error(“❌ بيانات غير صحيحة أو الحساب موقوف.”)
st.markdown(f’<div style="text-align:center;margin-top:1.1rem;color:var(--t3);font-size:.64rem">Dev: <b style="color:var(--acc)">{DEVELOPER}</b></div>’,unsafe_allow_html=True)
return False

# ─── TOP NAV ───────────────────────────────────────────────────────────────────

def top_nav():
role=st.session_state[“role”]; uname=st.session_state[“uname”]
ri=ROLES.get(role,{“ar”:role,“icon”:“👤”,“clr”:”#e8a020”})
init=””.join(w[0] for w in uname.split()[:2]).upper() or “?”
pages=ROLE_PAGES.get(role,[])
st.markdown(f’<div class="topnav"><div class="topnav-logo">Z<span class="sep">-</span>Order</div><div class="topnav-user" style="margin-right:auto"><div class="uavatar">{init}</div><div style="display:flex;flex-direction:column;gap:0"><span style="font-size:.76rem;font-weight:600;color:var(--t1);line-height:1.15">{uname}</span><span style=“font-size:.61rem;color:{ri[“clr”]}”>{ri[“icon”]} {ri[“ar”]}</span></div></div></div>’,unsafe_allow_html=True)
c1,c2=st.columns([5,1])
with c1:
st.markdown(’<div class="nav-sel">’,unsafe_allow_html=True)
if “page” not in st.session_state or st.session_state[“page”] not in pages:
st.session_state[“page”]=pages[0]
active=st.selectbox(””,pages,index=pages.index(st.session_state[“page”]),key=“nav_sel”,label_visibility=“collapsed”)
st.session_state[“page”]=active
st.markdown(’</div>’,unsafe_allow_html=True)
with c2:
if st.button(“خروج 🚪”,key=“lo”):
for k in list(st.session_state.keys()): del st.session_state[k]
st.rerun()
return active

# ─── PAGES ─────────────────────────────────────────────────────────────────────

def pg_admin_dash():
hdr(“🛡️”,“لوحة المدير العام”,“إحصائيات حية”)
guide(“① راقب الأوردرات والمالية<br>② راجع طلبات الشراء والبلاغات<br>③ أضف موظفين من «الموظفون»”)
today=datetime.date.today().isoformat()
tot=(qone(“SELECT COUNT(*) c FROM orders”) or {}).get(“c”,0)
tod=(qone(“SELECT COUNT(*) c FROM orders WHERE created_at LIKE ?”,(f”{today}%”,)) or {}).get(“c”,0)
dn=(qone(“SELECT COUNT(*) c FROM orders WHERE status IN (‘مكتمل’,‘تم التسليم’)”) or {}).get(“c”,0)
rv=(qone(“SELECT COALESCE(SUM(price),0) s FROM orders WHERE status IN (‘مكتمل’,‘تم التسليم’)”) or {}).get(“s”,0)
tv=(qone(“SELECT COALESCE(SUM(price),0) s FROM orders”) or {}).get(“s”,0)
opr=(qone(“SELECT COUNT(*) c FROM incident_reports WHERE status=‘مفتوح’”) or {}).get(“c”,0)
pp=(qone(“SELECT COUNT(*) c FROM purchase_requests WHERE status=‘قيد المراجعة’”) or {}).get(“c”,0)
us=(qone(“SELECT COUNT(*) c FROM users WHERE is_active=1”) or {}).get(“c”,0)
c1,c2,c3,c4=st.columns(4)
c1.metric(“أوردرات اليوم”,tod); c2.metric(“مكتملة/إجمالي”,f”{dn}/{tot}”)
c3.metric(“إيراد محصّل (د.ع)”,f”{rv:,.0f}”); c4.metric(“طلبات شراء معلقة”,pp)
c5,c6,c7,c8=st.columns(4)
c5.metric(“إجمالي القيمة (د.ع)”,f”{tv:,.0f}”); c6.metric(“قيد التنفيذ (د.ع)”,f”{tv-rv:,.0f}”)
c7.metric(“بلاغات مفتوحة”,opr); c8.metric(“موظفون نشطون”,us)
st.markdown(”—”)
t1,t2,t3,t4=st.tabs([“📋 آخر الأوردرات”,“📦 طلبات الشراء”,“🚨 البلاغات”,“🗺️ المندوبون”])
with t1:
rows=qall(“SELECT order_number,customer_name,quantity,price,status,created_at FROM orders ORDER BY id DESC LIMIT 15”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“order_number”:“الأوردر”,“customer_name”:“العميل”,“quantity”:“الكمية”,“price”:“السعر”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
else: st.info(“لا توجد أوردرات.”)
with t2:
rows=qall(“SELECT requester_name,department,item_name,quantity,urgency,status,created_at FROM purchase_requests ORDER BY id DESC LIMIT 20”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“requester_name”:“الموظف”,“department”:“القسم”,“item_name”:“الصنف”,“quantity”:“الكمية”,“urgency”:“الأولوية”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
else: st.info(“لا توجد طلبات.”)
with t3:
rows=qall(“SELECT reporter_name,department,description,severity,status,created_at FROM incident_reports ORDER BY id DESC LIMIT 15”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“reporter_name”:“المبلّغ”,“department”:“القسم”,“description”:“الوصف”,“severity”:“الخطورة”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
else: st.success(“🎉 لا بلاغات!”)
with t4:
rows=qall(“SELECT agent_name,COUNT(*) v,SUM(CASE WHEN visit_status=‘اشترى’ THEN 1 ELSE 0 END) bought,SUM(CASE WHEN visit_status=‘محتمل’ THEN 1 ELSE 0 END) pot FROM agent_visits GROUP BY agent_id ORDER BY v DESC”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“agent_name”:“المندوب”,“v”:“الزيارات”,“bought”:“اشترى”,“pot”:“محتمل”}),use_container_width=True,hide_index=True)
else: st.info(“لا توجد زيارات.”)

def pg_employees():
hdr(“👥”,“إدارة الموظفين”,“أضف الفريق وحدد صلاحياتهم”)
guide(“① المدير هو الوحيد الذي يضيف موظفين<br>② الموظف يدخل بإيميله أو اسم المستخدم<br>③ يمكن تعطيل أي حساب”)
rows=qall(“SELECT id,full_name,username,email,role,is_active,created_at FROM users ORDER BY id”)
if rows:
df=pd.DataFrame(rows); df[“is_active”]=df[“is_active”].map({1:“✅ نشط”,0:“🚫 موقوف”})
st.dataframe(df.rename(columns={“id”:”#”,“full_name”:“الاسم”,“username”:“المستخدم”,“email”:“الإيميل”,“role”:“الدور”,“is_active”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
st.markdown(”—”)
st.markdown(’<div class="sec">➕ إضافة موظف جديد</div>’,unsafe_allow_html=True)
with st.form(“add_emp”,clear_on_submit=True):
c1,c2=st.columns(2); fn=c1.text_input(“الاسم الكامل *”); un=c2.text_input(“اسم المستخدم *”)
c3,c4=st.columns(2); em=c3.text_input(“الإيميل *”)
rl=c4.selectbox(“الدور *”,[r for r in ROLES if r!=“admin”],format_func=lambda r:f”{ROLES[r][‘icon’]} {ROLES[r][‘ar’]}”)
c5,c6=st.columns(2); p1=c5.text_input(“كلمة المرور *”,type=“password”); p2=c6.text_input(“التأكيد *”,type=“password”)
ok=st.form_submit_button(“✅ إضافة”,use_container_width=True)
if ok:
errs=[]
if not all([fn,un,em,p1]): errs.append(“جميع الحقول مطلوبة.”)
if p1 and p1!=p2: errs.append(“كلمتا المرور غير متطابقتين.”)
if p1 and len(p1)<6: errs.append(“كلمة المرور 6 أحرف على الأقل.”)
for e in errs: st.error(e)
if not errs:
try:
qrun(“INSERT INTO users(full_name,username,email,password,role) VALUES(?,?,?,?,?)”,(fn.strip(),un.strip().lower(),em.strip().lower(),*hash(p1),rl))
st.success(f”✅ تم إضافة **{fn}**!”); st.rerun()
except sqlite3.IntegrityError: st.error(“❌ اسم المستخدم أو الإيميل مستخدم بالفعل.”)
st.markdown(”—”)
st.markdown(’<div class="sec">🔄 تفعيل / تعطيل</div>’,unsafe_allow_html=True)
all_u=qall(“SELECT id,full_name,username FROM users WHERE role!=‘admin’ ORDER BY id”)
if all_u:
opts={f”{u[‘id’]} — {u[‘full_name’]} ({u[‘username’]})”:u[“id”] for u in all_u}
sel=st.selectbox(“الموظف”,list(opts.keys()))
uid_t=opts[sel]; ca,cb,*=st.columns([1,1,3])
if ca.button(“✅ تفعيل”,key=“act”): qrun(“UPDATE users SET is_active=1 WHERE id=?”,(uid_t,)); st.rerun()
if cb.button(“🚫 تعطيل”,key=“dact”): qrun(“UPDATE users SET is_active=0 WHERE id=?”,(uid_t,)); st.rerun()
else: st.info(“لا يوجد موظفون مضافون.”)

def pg_sales_dash():
hdr(“📊”,“لوحة المبيعات”,“أوردراتك وإحصائياتك”)
guide(“① أضف أوردراً من «أوردر جديد»<br>② السعر سري ولا يظهر للأقسام الأخرى<br>③ تابع حالة الأوردر من «أوردراتي»”)
uid=st.session_state[“uid”]
tot=(qone(“SELECT COUNT(*) c FROM orders WHERE created_by_id=?”,(uid,)) or {}).get(“c”,0)
dn=(qone(“SELECT COUNT(*) c FROM orders WHERE created_by_id=? AND status IN (‘مكتمل’,‘تم التسليم’)”,(uid,)) or {}).get(“c”,0)
rv=(qone(“SELECT COALESCE(SUM(price),0) s FROM orders WHERE created_by_id=? AND status IN (‘مكتمل’,‘تم التسليم’)”,(uid,)) or {}).get(“s”,0)
nw=(qone(“SELECT COUNT(*) c FROM orders WHERE created_by_id=? AND status=‘جديد’”,(uid,)) or {}).get(“c”,0)
c1,c2,c3,c4=st.columns(4)
c1.metric(“إجمالي أوردراتي”,tot); c2.metric(“مكتملة”,dn)
c3.metric(“الإيراد (د.ع)”,f”{rv:,.0f}”); c4.metric(“جديدة”,nw)
st.markdown(”—”); show_orders(“sales”,uid_filter=uid,title=“أوردراتي الأخيرة”)

def pg_add_order():
hdr(“➕”,“أوردر جديد”,“أدخل تفاصيل طلب العميل”)
with st.form(“new_order”,clear_on_submit=True):
c1,c2=st.columns(2); cust=c1.text_input(“👤 اسم العميل *”); qty=c2.number_input(“📦 الكمية *”,min_value=1,value=1)
desc=st.text_area(“📝 وصف الطلب *”,placeholder=“المقاس، نوع الورق، التفاصيل…”)
c3,_=st.columns(2); price=c3.number_input(“💰 السعر (د.ع) *”,min_value=0.0,step=500.0)
sub=st.form_submit_button(“✅ حفظ الأوردر”,use_container_width=True)
if sub:
if not cust.strip() or not desc.strip() or price<=0: st.error(“يرجى تعبئة جميع الحقول — السعر يجب أن يكون أكبر من صفر.”)
else:
ono=order_no()
qrun(“INSERT INTO orders(order_number,customer_name,description,quantity,price,created_by_id,created_by_name) VALUES(?,?,?,?,?,?,?)”,
(ono,cust.strip(),desc.strip(),qty,price,st.session_state[“uid”],st.session_state[“uname”]))
st.success(f”✅ تم حفظ الأوردر **{ono}** — سيظهر لقسم التصميم فوراً!”)

def pg_design():
hdr(“🎨”,“قسم التصميم”,“ارفع ملف التصميم لكل أوردر”)
guide(“① ارفع ملف التصميم (PDF/AI/PSD/PNG) لكل أوردر<br>② الملف يُحفظ مرتبطاً بالأوردر في قاعدة البيانات<br>③ الإنتاج لن يبدأ إلا بعد رفع الملف”)
rows=qall(“SELECT * FROM orders ORDER BY id DESC”)
pend=[r for r in rows if r[“design_status”]==“قيد الانتظار”]
done=[r for r in rows if r[“design_status”]==“مكتمل”]
t1,t2=st.tabs([f”⏳ قيد الانتظار ({len(pend)})”,f”✅ مكتملة ({len(done)})”])
with t1:
if not pend: st.success(“🎉 لا توجد مهام تصميم معلقة!”)
for r in pend:
with st.expander(f”🔷 {r[‘order_number’]}  —  {r[‘customer_name’]}”):
c1,c2=st.columns(2)
c1.markdown(f”**الوصف:** {r[‘description’]}”)
c1.markdown(f”**الكمية:** {r[‘quantity’]}”)
c2.markdown(f”**التاريخ:** {r[‘created_at’]}”)
c2.markdown(f”**أضافه:** {r[‘created_by_name’]}”)
st.markdown(”—”)
upld=st.file_uploader(“📎 رفع ملف التصميم *”,key=f”du_{r[‘id’]}”,
type=[“pdf”,“png”,“jpg”,“jpeg”,“ai”,“psd”,“svg”,“eps”,“zip”,“cdr”],
help=“ارفع ملف التصميم النهائي المراد طباعته”)
dl=st.text_input(“🔗 أو رابط التصميم”,value=r[“design_link”] or “”,key=f”dl_{r[‘id’]}”)
notes=st.text_area(“📝 ملاحظات للإنتاج”,value=r[“design_notes”] or “”,key=f”dn_{r[‘id’]}”,height=65)
if st.button(“✅ تأكيد رفع التصميم”,key=f”d_ok_{r[‘id’]}”):
fp=save_upload(upld,“designs”) if upld else (r[“design_file_path”] or “”)
if not fp and not dl.strip(): st.error(“⚠️ يجب رفع ملف أو إدخال رابط التصميم.”)
else:
now=datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
qrun(“UPDATE orders SET design_status=‘مكتمل’,design_file_path=?,design_link=?,design_notes=?,design_updated=?,design_by=? WHERE id=?”,
(fp,dl.strip(),notes.strip(),now,st.session_state[“uname”],r[“id”]))
sync_status(r[“id”]); st.success(“✅ تم رفع التصميم! الأوردر جاهز للإنتاج.”); st.rerun()
with t2:
if not done: st.info(“لا توجد تصاميم مكتملة.”)
for r in done:
co1,co2=st.columns([4,2])
with co1:
st.markdown(f’<div class="card"><b>{r[“order_number”]}</b> — {r[“customer_name”]} {badge(“مكتمل”,ORD_BADGE)}<br><small style="color:var(--t3)">🗓 {r[“design_updated”]} | 👤 {r[“design_by”]}</small></div>’,unsafe_allow_html=True)
with co2:
if r.get(“design_file_path”) and Path(r[“design_file_path”]).exists(): dl_btn(r[“design_file_path”],“⬇️ تحميل”)
elif r.get(“design_link”): st.markdown(f’[🔗 رابط]({r["design_link"]})’)

def pg_production():
hdr(“🖨️”,“قسم الإنتاج”,“نفّذ الأوردرات الجاهزة”)
guide(“① الأوردر يظهر هنا فقط بعد رفع التصميم<br>② حمّل ملف التصميم واطبع<br>③ عند الانتهاء غيّر الحالة إلى مكتمل”)
rows=qall(“SELECT * FROM orders ORDER BY id DESC”)
ready=[r for r in rows if r[“design_status”]==“مكتمل” and r[“production_status”]==“قيد الانتظار”]
printing=[r for r in rows if r[“production_status”]==“جاري الإنتاج”]
done=[r for r in rows if r[“production_status”]==“مكتمل”]
t1,t2,t3=st.tabs([f”🟢 جاهز ({len(ready)})”,f”🟠 جاري ({len(printing)})”,f”✅ مكتمل ({len(done)})”])
with t1:
if not ready: st.info(“⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم.”)
for r in ready:
with st.expander(f”🟢 {r[‘order_number’]}  —  {r[‘customer_name’]}”):
c1,c2=st.columns(2)
c1.markdown(f”**الوصف:** {r[‘description’]}”)
c1.markdown(f”**الكمية:** {r[‘quantity’]}”)
c2.markdown(f”**ملاحظات التصميم:** {r[‘design_notes’] or ‘—’}”)
c2.markdown(f”**صمّمه:** {r[‘design_by’] or ‘—’}”)
if r.get(“design_file_path”) and Path(r[“design_file_path”]).exists(): dl_btn(r[“design_file_path”],“⬇️ تحميل ملف التصميم للطباعة”)
elif r.get(“design_link”): st.markdown(f’[🔗 فتح رابط التصميم]({r["design_link"]})’)
pnotes=st.text_area(“📝 ملاحظات”,key=f”pn_{r[‘id’]}”,height=55)
col1,col2=st.columns(2)
if col1.button(“▶️ بدء الطباعة”,key=f”st_{r[‘id’]}”):
now=datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
qrun(“UPDATE orders SET production_status=‘جاري الإنتاج’,production_notes=?,production_updated=?,production_by=? WHERE id=?”,(pnotes,now,st.session_state[“uname”],r[“id”]))
sync_status(r[“id”]); st.success(“▶️ بدأ الإنتاج!”); st.rerun()
if col2.button(“✅ إتمام مباشر”,key=f”fi_{r[‘id’]}”):
now=datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
qrun(“UPDATE orders SET production_status=‘مكتمل’,production_notes=?,production_updated=?,production_by=? WHERE id=?”,(pnotes,now,st.session_state[“uname”],r[“id”]))
sync_status(r[“id”]); st.success(“✅ مكتمل!”); st.rerun()
with t2:
if not printing: st.info(“لا توجد طباعة جارية.”)
for r in printing:
with st.expander(f”🟠 {r[‘order_number’]}  —  {r[‘customer_name’]}”):
st.markdown(f”**الوصف:** {r[‘description’]} | **الكمية:** {r[‘quantity’]}”)
if r.get(“design_file_path”) and Path(r[“design_file_path”]).exists(): dl_btn(r[“design_file_path”])
if st.button(“✅ تحديد كمكتمل”,key=f”fn_{r[‘id’]}”):
qrun(“UPDATE orders SET production_status=‘مكتمل’,production_updated=? WHERE id=?”,(datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”),r[“id”]))
sync_status(r[“id”]); st.success(“✅ مكتمل!”); st.rerun()
with t3:
if not done: st.info(“لا توجد أوردرات مكتملة.”)
for r in done:
st.markdown(f’<div class="card"><b>{r[“order_number”]}</b> — {r[“customer_name”]} {badge(“مكتمل”,ORD_BADGE)}<br><small style="color:var(--t3)">اكتمل: {r[“production_updated”]}</small></div>’,unsafe_allow_html=True)

def pg_purchase_submit():
hdr(“📦”,“طلب شراء”,“اطلب مواد أو أدوات من المشتريات”)
with st.form(“pur_req”,clear_on_submit=True):
c1,c2=st.columns(2)
item=c1.text_input(“اسم الصنف المطلوب *”,placeholder=“حبر أسود، ورق A3…”)
qty=c2.text_input(“الكمية *”,placeholder=“5 علب، 10 رزمة…”)
urg=st.selectbox(“الأولوية”,[“عادي”,“عاجل”,“طارئ”])
notes=st.text_area(“ملاحظات”,height=65)
sub=st.form_submit_button(“📤 إرسال الطلب”,use_container_width=True)
if sub:
if not item.strip() or not qty.strip(): st.error(“يرجى تحديد الصنف والكمية.”)
else:
role=st.session_state[“role”]
qrun(“INSERT INTO purchase_requests(requester_id,requester_name,department,item_name,quantity,urgency,notes) VALUES(?,?,?,?,?,?,?)”,
(st.session_state[“uid”],st.session_state[“uname”],ROLES[role][“ar”],item.strip(),qty.strip(),urg,notes.strip()))
st.success(“✅ تم إرسال طلب الشراء!”)
st.markdown(”—”)
st.markdown(”**📋 طلباتي السابقة**”)
rows=qall(“SELECT item_name,quantity,urgency,status,created_at FROM purchase_requests WHERE requester_id=? ORDER BY id DESC LIMIT 10”,(st.session_state[“uid”],))
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“item_name”:“الصنف”,“quantity”:“الكمية”,“urgency”:“الأولوية”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
else: st.info(“لم تقدم أي طلب بعد.”)

def pg_purchase_manage():
hdr(“📦”,“إدارة طلبات الشراء”,“راجع وأدر جميع الطلبات الواردة”)
guide(“① الطارئ والعاجل يظهران أولاً<br>② وافق أو ارفض كل طلب<br>③ يمكن للمدير الاطلاع على السجل الكامل”)
rows=qall(“SELECT * FROM purchase_requests ORDER BY CASE urgency WHEN ‘طارئ’ THEN 0 WHEN ‘عاجل’ THEN 1 ELSE 2 END,id DESC”)
pend=[r for r in rows if r[“status”]==“قيد المراجعة”]
rest=[r for r in rows if r[“status”]!=“قيد المراجعة”]
t1,t2=st.tabs([f”⏳ قيد المراجعة ({len(pend)})”,f”📋 السجل ({len(rest)})”])
with t1:
if not pend: st.success(“🎉 لا توجد طلبات معلقة!”)
for r in pend:
uc={“طارئ”:“var(–red)”,“عاجل”:“var(–acc2)”,“عادي”:“var(–t2)”}.get(r[“urgency”],“var(–t2)”)
with st.expander(f”📦 {r[‘item_name’]} — {r[‘requester_name’]} [{r[‘department’]}]”):
st.markdown(f”**الصنف:** {r[‘item_name’]} | **الكمية:** {r[‘quantity’]}<br>**الأولوية:** <span style='color:{uc}'>{r[‘urgency’]}</span> | **التاريخ:** {r[‘created_at’]}{’<br>**ملاحظات:** ’+r[‘notes’] if r[‘notes’] else ‘’}”,unsafe_allow_html=True)
col1,col2=st.columns(2)
if col1.button(“✅ موافقة”,key=f”app_{r[‘id’]}”):
now=datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
qrun(“UPDATE purchase_requests SET status=‘موافق عليه’,reviewed_by=?,reviewed_at=? WHERE id=?”,(st.session_state[“uname”],now,r[“id”]))
st.success(“✅ موافق عليه.”); st.rerun()
if col2.button(“❌ رفض”,key=f”rej_{r[‘id’]}”):
now=datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”)
qrun(“UPDATE purchase_requests SET status=‘مرفوض’,reviewed_by=?,reviewed_at=? WHERE id=?”,(st.session_state[“uname”],now,r[“id”]))
st.warning(“تم الرفض.”); st.rerun()
with t2:
if not rest: st.info(“لا يوجد سجل بعد.”)
else:
df=pd.DataFrame(rest)[[“requester_name”,“department”,“item_name”,“quantity”,“urgency”,“status”,“reviewed_by”,“created_at”]]
st.dataframe(df.rename(columns={“requester_name”:“الموظف”,“department”:“القسم”,“item_name”:“الصنف”,“quantity”:“الكمية”,“urgency”:“الأولوية”,“status”:“الحالة”,“reviewed_by”:“راجعه”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)

def pg_agent_new():
hdr(“🗺️”,“تسجيل زيارة عميل”,“وثّق زيارتك الميدانية”)
guide(“① سجّل كل زيارة مع اسم المحل والموقع<br>② أرفق صورة المحل<br>③ المدير يتابع أداءك من لوحته”)
with st.form(“av”,clear_on_submit=True):
cust=st.text_input(“👤 اسم العميل / المحل *”)
loc=st.text_input(“📍 العنوان”,placeholder=“الشارع، الحي، المدينة”)
vs=st.selectbox(“📊 حالة العميل”,[“محتمل”,“اشترى”,“لن يشتري”])
notes=st.text_area(“📝 ملاحظات”,height=65)
img=st.file_uploader(“📸 صورة المحل”,type=[“jpg”,“jpeg”,“png”,“webp”])
sub=st.form_submit_button(“✅ حفظ الزيارة”,use_container_width=True)
if sub:
if not cust.strip(): st.error(“يرجى إدخال اسم العميل.”)
else:
ip=save_upload(img,“agents”) if img else “”
qrun(“INSERT INTO agent_visits(agent_id,agent_name,customer_name,location,visit_status,notes,image_path) VALUES(?,?,?,?,?,?,?)”,
(st.session_state[“uid”],st.session_state[“uname”],cust.strip(),loc.strip(),vs,notes.strip(),ip))
st.success(f”✅ تم تسجيل زيارة **{cust.strip()}**!”)

def pg_agent_my():
hdr(“📋”,“زياراتي”,“سجل زياراتك الميدانية”)
rows=qall(“SELECT * FROM agent_visits WHERE agent_id=? ORDER BY id DESC”,(st.session_state[“uid”],))
if not rows: st.info(“لم تسجّل أي زيارة بعد.”); return
for r in rows:
cls,lbl=AGT_BADGE.get(r[“visit_status”],(“b-apot”,r[“visit_status”]))
ih=””
if r.get(“image_path”) and Path(r[“image_path”]).exists():
raw=Path(r[“image_path”]).read_bytes()
b64=base64.b64encode(raw).decode()
ext=Path(r[“image_path”]).suffix.lstrip(”.”) or “jpeg”
ih=f’<br><img src="data:image/{ext};base64,{b64}" style="max-width:100%;max-height:155px;border-radius:8px;margin-top:.4rem;object-fit:cover">’
st.markdown(f’<div class="card"><b>{r[“customer_name”]}</b> <span class="badge {cls}">{lbl}</span><br><small style="color:var(--t2)">📍 {r[“location”] or “—”} | 🗓 {r[“visited_at”]}</small>{”<br><small>”+r[“notes”]+”</small>” if r[“notes”] else “”}{ih}</div>’,unsafe_allow_html=True)

def pg_agent_reports():
hdr(“🗺️”,“تقارير المندوبين”,“أداء فريق المبيعات”)
rows=qall(“SELECT agent_name,COUNT(*) v,SUM(CASE WHEN visit_status=‘اشترى’ THEN 1 ELSE 0 END) bought,SUM(CASE WHEN visit_status=‘محتمل’ THEN 1 ELSE 0 END) pot,SUM(CASE WHEN visit_status=‘لن يشتري’ THEN 1 ELSE 0 END) nob,MAX(visited_at) lv FROM agent_visits GROUP BY agent_id ORDER BY v DESC”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“agent_name”:“المندوب”,“v”:“الزيارات”,“bought”:“اشترى”,“pot”:“محتمل”,“nob”:“لن يشتري”,“lv”:“آخر زيارة”}),use_container_width=True,hide_index=True)
else: st.info(“لا توجد زيارات.”)

def pg_incident_submit():
role=st.session_state[“role”]
hdr(“🚨”,“بلاغ خلل أو نقص”,“أبلغ المدير عن أي مشكلة”)
with st.form(“inc”,clear_on_submit=True):
desc=st.text_area(“📝 وصف المشكلة *”,placeholder=“نقص حبر، عطل طابعة…”)
sev=st.selectbox(“⚠️ الخطورة”,[“منخفض”,“متوسط”,“عالي”])
sub=st.form_submit_button(“📤 إرسال”,use_container_width=True)
if sub:
if not desc.strip(): st.error(“يرجى كتابة الوصف.”)
else:
qrun(“INSERT INTO incident_reports(reporter_id,reporter_name,department,description,severity) VALUES(?,?,?,?,?)”,
(st.session_state[“uid”],st.session_state[“uname”],ROLES[role][“ar”],desc.strip(),sev))
st.success(“✅ تم إرسال البلاغ للمدير!”)
st.markdown(”—”)
rows=qall(“SELECT description,severity,status,created_at FROM incident_reports WHERE reporter_id=? ORDER BY id DESC LIMIT 8”,(st.session_state[“uid”],))
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“description”:“الوصف”,“severity”:“الخطورة”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)

def pg_all_incidents():
hdr(“🚨”,“بلاغات الأعطال”,“جميع البلاغات الواردة”)
rows=qall(“SELECT * FROM incident_reports ORDER BY id DESC”)
if not rows: st.success(“🎉 لا توجد بلاغات!”); return
op=[r for r in rows if r[“status”]==“مفتوح”]; rs=[r for r in rows if r[“status”]==“محلول”]
t1,t2=st.tabs([f”🔴 مفتوحة ({len(op)})”,f”✅ محلولة ({len(rs)})”])
for tab,lst in [(t1,op),(t2,rs)]:
with tab:
if not lst: st.info(“لا توجد.”); continue
for r in lst:
sc,sl=SEV_BADGE.get(r[“severity”],(“b-sev-md”,r[“severity”]))
with st.expander(f’{sl} {r[“severity”]}  —  {r[“department”]}  —  {r[“created_at”][:16]}’):
st.markdown(f”**المبلّغ:** {r[‘reporter_name’]}<br>**الوصف:** {r[‘description’]}”,unsafe_allow_html=True)
if r[“status”]==“مفتوح”:
if st.button(“✅ محلول”,key=f”rs_{r[‘id’]}”):
qrun(“UPDATE incident_reports SET status=‘محلول’,resolved_at=? WHERE id=?”,(datetime.datetime.now().strftime(”%Y-%m-%d %H:%M”),r[“id”])); st.rerun()
else: st.caption(f”تم الحل: {r[‘resolved_at’]}”)

def pg_financial():
hdr(“💰”,“التقارير المالية”,“للمبيعات والمدير فقط”)
tv=(qone(“SELECT COALESCE(SUM(price),0) s FROM orders”) or {}).get(“s”,0)
rv=(qone(“SELECT COALESCE(SUM(price),0) s FROM orders WHERE status IN (‘مكتمل’,‘تم التسليم’)”) or {}).get(“s”,0)
cnt=(qone(“SELECT COUNT(*) c FROM orders”) or {}).get(“c”,0)
avg=tv/cnt if cnt else 0
c1,c2,c3,c4=st.columns(4)
c1.metric(“إجمالي القيمة (د.ع)”,f”{tv:,.0f}”); c2.metric(“محصّل (د.ع)”,f”{rv:,.0f}”)
c3.metric(“قيد التنفيذ (د.ع)”,f”{tv-rv:,.0f}”); c4.metric(“متوسط الأوردر”,f”{avg:,.0f}”)
st.markdown(”—”)
rows=qall(“SELECT order_number,customer_name,quantity,price,status,created_at FROM orders ORDER BY id DESC”)
if not rows: st.info(“لا توجد أوردرات.”); return
df=pd.DataFrame(rows)
st.dataframe(df.rename(columns={“order_number”:“الأوردر”,“customer_name”:“العميل”,“quantity”:“الكمية”,“price”:“السعر (د.ع)”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)
hdr_txt=(f”Z-Order — تقرير مالي\nDeveloped by: {DEVELOPER}\nBrand: {BRAND}\nتاريخ: {datetime.datetime.now().strftime(’%Y-%m-%d %H:%M’)}\n\n”)
st.download_button(“⬇️ تصدير CSV”,(hdr_txt+df.to_csv(index=False)).encode(“utf-8-sig”),
file_name=f”zorder_fin_{datetime.date.today()}.csv”,mime=“text/csv”,use_container_width=True)

def pg_generic_dash(role):
hdr(“📊”,“لوحتي”,“نظرة عامة”)
tot=(qone(“SELECT COUNT(*) c FROM orders”) or {}).get(“c”,0)
nw=(qone(“SELECT COUNT(*) c FROM orders WHERE status=‘جديد’”) or {}).get(“c”,0)
ip=(qone(“SELECT COUNT(*) c FROM orders WHERE production_status=‘جاري الإنتاج’”) or {}).get(“c”,0)
dn=(qone(“SELECT COUNT(*) c FROM orders WHERE status IN (‘مكتمل’,‘تم التسليم’)”) or {}).get(“c”,0)
c1,c2,c3,c4=st.columns(4)
c1.metric(“إجمالي”,tot); c2.metric(“جديدة”,nw); c3.metric(“جاري”,ip); c4.metric(“مكتملة”,dn)
st.markdown(”—”)
rows=qall(“SELECT order_number,customer_name,description,quantity,status,created_at FROM orders ORDER BY id DESC LIMIT 10”)
if rows: st.dataframe(pd.DataFrame(rows).rename(columns={“order_number”:“الأوردر”,“customer_name”:“العميل”,“description”:“الوصف”,“quantity”:“الكمية”,“status”:“الحالة”,“created_at”:“التاريخ”}),use_container_width=True,hide_index=True)

# ─── MAIN ROUTER ───────────────────────────────────────────────────────────────

def main():
init_db()
if not gatekeeper():
footer(); return
role=st.session_state[“role”]
active=top_nav()
st.markdown(’<div class="pw">’,unsafe_allow_html=True)

```
# ADMIN
if   active=="📊 الرئيسية" and role=="admin": pg_admin_dash()
elif active=="👥 الموظفون": pg_employees()
elif active=="📋 الأوردرات" and role=="admin": show_orders("admin",title="جميع الأوردرات")
elif active=="💰 المالية": pg_financial()
elif active=="🚨 البلاغات": pg_all_incidents()
elif active=="🗺️ المندوبون": pg_agent_reports()
# SALES
elif active=="📊 الرئيسية" and role=="sales": pg_sales_dash()
elif active=="➕ أوردر جديد": pg_add_order()
elif active=="📋 أوردراتي": show_orders("sales",uid_filter=st.session_state["uid"],title="أوردراتي")
elif active=="💰 تقرير مبيعات": pg_financial()
# DESIGN
elif active=="📊 الرئيسية" and role=="design": pg_generic_dash(role)
elif active=="🎨 التصميم": pg_design()
# PURCHASE
elif active=="📊 الرئيسية" and role=="purchase": pg_generic_dash(role)
elif active=="📦 طلبات الشراء": pg_purchase_manage()
# PRODUCTION
elif active=="📊 الرئيسية" and role=="production": pg_generic_dash(role)
elif active=="🖨️ الإنتاج": pg_production()
elif active=="📋 الأوردرات" and role=="production": show_orders("production",title="الأوردرات")
# AGENT
elif active=="📊 الرئيسية" and role=="agent": pg_generic_dash(role)
elif active=="🗺️ زيارة جديدة": pg_agent_new()
elif active=="📋 زياراتي": pg_agent_my()
# SHARED
elif active=="📦 طلب شراء": pg_purchase_submit()
elif active=="🚨 بلاغ": pg_incident_submit()
else: st.warning(f"الصفحة «{active}» غير متاحة.")

st.markdown('</div>',unsafe_allow_html=True)
footer()
```

if **name**==”**main**”:
main()
