"""
╔══════════════════════════════════════════════════════════════════════════╗
║   Z-ORDER · Built for Organized Teams · v7.0                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Developer : Abdulrahman Fallah                                         ║
║  Year      : 2026                                                       ║
║  Backend   : Supabase (PostgreSQL + Storage)                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  SETUP:                                                                 ║
║    pip install streamlit pillow requests                                ║
║    streamlit run z_order_app.py                                         ║
║                                                                         ║
║  Platform Super-Admin:                                                  ║
║    Email    : admin@zorder.iq   Password : Admin@2025                  ║
║                                                                         ║
║  SUPABASE SQL — Run once in Supabase SQL Editor:                        ║
║  (full schema at bottom of this file)                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import hashlib
import datetime
import base64
import requests
import pandas as pd
from io import BytesIO

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Z-ORDER | Built for Organized Teams",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER     = "Abdulrahman Fallah"
APP_NAME      = "Z-ORDER"
APP_TAGLINE   = "Built for Organized Teams"
APP_VER       = "7.0"
YEAR          = "2026"
SUPPORT_WA    = "https://wa.me/9647768723110"
SUPPORT_PHONE = "+964 776 872 3110"

# ── Supabase Config ──────────────────────────────────────────────────────────
SUPA_URL    = "https://iiytcythowpemjxcxfsf.supabase.co"
SUPA_KEY    = "sb_publishable_0cJhgmY3C3Q5KfdVp6R0aQ_3t0gvuuz"
REST_URL    = f"{SUPA_URL}/rest/v1"
STORAGE_URL = f"{SUPA_URL}/storage/v1"
BUCKET      = "designs"

HEADERS = {
    "apikey":        SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

# ─────────────────────────────────────────────────────────────────────────────
#  ROLES & PAGES
# ─────────────────────────────────────────────────────────────────────────────
ROLES = {
    "superadmin": {"ar": "المشرف العام",    "icon": "⭐", "clr": "#ffd166"},
    "admin":      {"ar": "مدير الشركة",     "icon": "🛡️", "clr": "#e8a020"},
    "sales":      {"ar": "المبيعات",         "icon": "💼", "clr": "#3b82f6"},
    "design":     {"ar": "التصميم",          "icon": "🎨", "clr": "#a855f7"},
    "purchase":   {"ar": "المشتريات",        "icon": "📦", "clr": "#22c55e"},
    "production": {"ar": "الإنتاج",          "icon": "🖨️", "clr": "#ff6b35"},
    "agent":      {"ar": "مندوب مبيعات",    "icon": "🗺️", "clr": "#06b6d4"},
}

ROLE_PAGES = {
    "superadmin": ["📊 لوحة التحكم", "🏢 الشركات", "👥 المستخدمون", "📊 الإحصائيات"],
    "admin":      ["📊 الرئيسية", "👥 الفريق", "📋 الأوردرات", "💰 المالية",
                   "🚨 البلاغات", "🗺️ المندوبون", "💬 المحادثة", "📞 الدعم الفني"],
    "sales":      ["📊 الرئيسية", "➕ أوردر جديد", "📋 أوردراتي", "🖼️ معاينة التصاميم",
                   "💰 تقريري", "📦 طلب شراء", "💬 المحادثة", "🚨 بلاغ"],
    "design":     ["📊 الرئيسية", "🎨 التصميم", "💬 المحادثة", "📦 طلب شراء", "🚨 بلاغ"],
    "purchase":   ["📊 الرئيسية", "📦 طلبات الشراء", "💬 المحادثة", "🚨 بلاغ"],
    "production": ["📊 الرئيسية", "🖨️ الإنتاج", "📋 الأوردرات", "💬 المحادثة", "📦 طلب شراء", "🚨 بلاغ"],
    "agent":      ["📊 الرئيسية", "🗺️ زيارة جديدة", "📋 زياراتي", "💬 المحادثة", "🚨 بلاغ"],
}

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  — Dark Gold Theme · Mobile-First
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
:root{
  --bg0:#070809;--bg1:#0b0d12;--bg2:#10131c;--bg3:#161924;--bg5:#222638;
  --bdr:#1e2235;--bdr2:#272d44;
  --gold:#e8a020;--gold2:#ffd166;--acc2:#ff6b35;
  --blue:#3b82f6;--green:#22c55e;--red:#ef4444;--purple:#a855f7;--cyan:#06b6d4;
  --t1:#f0f2f8;--t2:#8590a8;--t3:#3c4460;
  --r:10px;--r2:15px;
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
::-webkit-scrollbar-thumb:hover{background:var(--gold);}

/* inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,
.stSelectbox>div>div,.stNumberInput>div>div>input{
  background:var(--bg3) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r) !important;color:var(--t1) !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;font-size:.9rem !important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
  border-color:var(--gold) !important;box-shadow:0 0 0 3px rgba(232,160,32,.12) !important;}

/* buttons */
.stButton>button{
  background:linear-gradient(135deg,var(--gold),var(--acc2)) !important;
  color:#07080b !important;font-weight:700 !important;border:none !important;
  border-radius:var(--r) !important;padding:.6rem 1.2rem !important;
  min-height:44px !important;width:100% !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;
  transition:transform .15s,box-shadow .15s !important;cursor:pointer;}
.stButton>button:hover{transform:translateY(-2px) !important;
  box-shadow:0 8px 24px rgba(232,160,32,.35) !important;}
.stButton>button:active{transform:translateY(0) !important;}

/* tabs */
.stTabs [data-baseweb="tab-list"]{background:var(--bg3) !important;border-radius:var(--r) !important;
  gap:3px !important;padding:4px !important;border:1px solid var(--bdr) !important;
  overflow-x:auto !important;flex-wrap:nowrap !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:var(--t2) !important;
  border-radius:7px !important;font-size:.82rem !important;border:none !important;white-space:nowrap !important;}
.stTabs [aria-selected="true"]{background:var(--bg5) !important;color:var(--gold) !important;
  border-bottom:2px solid var(--gold) !important;}

/* metrics */
[data-testid="stMetric"]{background:var(--bg2) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r2) !important;padding:.9rem 1rem !important;}
[data-testid="stMetricLabel"]{color:var(--t2) !important;font-size:.72rem !important;}
[data-testid="stMetricValue"]{color:var(--gold) !important;
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

/* ── Top navigation bar ── */
.topbar{position:sticky;top:0;z-index:999;background:var(--bg1);
  border-bottom:1px solid var(--bdr);padding:.5rem 1.2rem;
  display:flex;align-items:center;gap:.7rem;overflow-x:auto;flex-wrap:nowrap;}
.zlogo{font-family:'JetBrains Mono',monospace;font-size:1.35rem;font-weight:700;
  color:var(--gold);letter-spacing:-.06em;line-height:1;white-space:nowrap;flex-shrink:0;}
.zlogo .sep{color:var(--t3);}
.zlogo .tag{font-family:'IBM Plex Sans Arabic',sans-serif;font-size:.58rem;
  font-weight:400;color:var(--t3);letter-spacing:.01em;display:block;margin-top:1px;}
.uchip{display:flex;align-items:center;gap:.45rem;background:var(--bg3);
  border:1px solid var(--bdr2);border-radius:999px;padding:.3rem .75rem .3rem .35rem;
  white-space:nowrap;flex-shrink:0;margin-right:auto;}
.uavatar{width:28px;height:28px;background:linear-gradient(135deg,var(--gold),var(--acc2));
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:700;color:#07080b;flex-shrink:0;}

/* ── Page content ── */
.pw{padding:1.1rem 1.4rem 6.5rem;max-width:1300px;margin:0 auto;}

/* ── Page header ── */
.ph{display:flex;align-items:center;gap:.75rem;margin-bottom:1.15rem;}
.ph-icon{font-size:1.55rem;background:var(--bg2);border:1px solid var(--bdr2);
  border-radius:var(--r);width:48px;height:48px;display:flex;
  align-items:center;justify-content:center;flex-shrink:0;}
.ph h2{font-size:1.15rem;font-weight:700;color:var(--t1);margin:0;}
.ph p{font-size:.74rem;color:var(--t3);margin:0;}

/* ── Cards ── */
.card{background:var(--bg2);border:1px solid var(--bdr2);border-radius:var(--r2);
  padding:1rem 1.2rem;margin-bottom:.65rem;transition:border-color .2s,transform .15s;}
.card:hover{border-color:var(--gold);transform:translateY(-1px);}

/* ── Info card ── */
.icard{background:linear-gradient(135deg,rgba(232,160,32,.07),rgba(255,107,53,.04));
  border:1px solid rgba(232,160,32,.2);border-right:3px solid var(--gold);
  border-radius:var(--r2);padding:.85rem 1.1rem;margin-bottom:.9rem;
  font-size:.82rem;color:var(--t2);line-height:1.85;}

/* ── Support card ── */
.support-card{background:linear-gradient(135deg,rgba(34,197,94,.06),rgba(6,182,212,.04));
  border:1px solid rgba(34,197,94,.2);border-radius:var(--r2);
  padding:1.5rem 1.4rem;text-align:center;}
.wa-btn{display:inline-flex;align-items:center;gap:.5rem;background:#25D366;
  color:#fff !important;padding:.65rem 1.5rem;border-radius:var(--r);
  font-weight:700;text-decoration:none;font-size:.9rem;margin-top:.75rem;
  transition:opacity .2s;}
.wa-btn:hover{opacity:.85;}

/* ── Chat bubbles ── */
.chat-wrap{display:flex;flex-direction:column;gap:.55rem;
  margin-bottom:1rem;max-height:420px;overflow-y:auto;padding:.4rem;}
.bubble{max-width:75%;padding:.55rem .85rem;border-radius:var(--r2);
  font-size:.85rem;line-height:1.5;}
.bubble.me{background:rgba(232,160,32,.15);border:1px solid rgba(232,160,32,.2);align-self:flex-start;}
.bubble.other{background:var(--bg3);border:1px solid var(--bdr2);align-self:flex-end;}
.bubble .bname{font-size:.65rem;font-weight:700;color:var(--gold);margin-bottom:2px;}
.bubble .btime{font-size:.6rem;color:var(--t3);margin-top:3px;}

/* ── Badges ── */
.badge{display:inline-flex;align-items:center;gap:3px;padding:.17rem .58rem;
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

.sec{font-size:.67rem;font-weight:700;color:var(--t3);text-transform:uppercase;
  letter-spacing:.1em;margin:.85rem 0 .45rem;}

/* ── Footer ── */
.footer{position:fixed;bottom:0;left:0;right:0;background:var(--bg1);
  border-top:1px solid var(--bdr);padding:.44rem 1.2rem;
  display:flex;align-items:center;justify-content:space-between;
  font-size:.66rem;color:var(--t3);z-index:9999;gap:.4rem;flex-wrap:wrap;}
.footer .hi{color:var(--gold);font-weight:600;}

/* ── Login ── */
.logo-big{font-family:'JetBrains Mono',monospace;font-size:2.4rem;font-weight:700;
  color:var(--gold);letter-spacing:-.07em;text-align:center;line-height:1;}
.logo-big .sep{color:var(--t3);}
.logo-tag{text-align:center;font-size:.72rem;color:var(--t3);
  letter-spacing:.12em;text-transform:uppercase;margin-top:.35rem;}
.nav-sel .stSelectbox>div>div{background:var(--bg2) !important;
  border:1px solid var(--gold) !important;font-weight:600 !important;
  font-size:.87rem !important;border-radius:var(--r) !important;}

/* ── Connection status ── */
.conn-ok{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);
  border-radius:var(--r);padding:.4rem .8rem;font-size:.72rem;color:#22c55e;
  display:inline-flex;align-items:center;gap:.4rem;}
.conn-err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);
  border-radius:var(--r);padding:.4rem .8rem;font-size:.72rem;color:#ef4444;
  display:inline-flex;align-items:center;gap:.4rem;}

/* ── Mobile ── */
@media(max-width:768px){
  .pw{padding:.65rem .45rem 6.5rem;}
  .ph-icon{width:36px;height:36px;font-size:1.15rem;}
  .ph h2{font-size:1rem;}
  [data-testid="column"]{width:100% !important;flex:0 0 100% !important;
    min-width:100% !important;padding:0 !important;}
  .stButton>button{font-size:.83rem !important;min-height:46px !important;}
  [data-testid="stMetricValue"]{font-size:1.05rem !important;}
  .topbar{padding:.42rem .6rem;}
  .footer{font-size:.59rem;padding:.32rem .55rem;}
  .bubble{max-width:90%;}
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SUPABASE DATA LAYER  — REST API (no extra SDK required)
# ─────────────────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def now_ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ── Generic REST helpers ────────────────────────────────────────────────────

def sb_select(table: str, filters: dict = None, order: str = None,
              limit: int = 1000, single: bool = False):
    """SELECT from Supabase table. Returns list or dict."""
    params = {"limit": limit}
    if order:
        params["order"] = order
    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"

    try:
        r = requests.get(f"{REST_URL}/{table}", headers=HEADERS, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data[0] if (single and data) else (None if single else data)
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
    return None if single else []


def sb_insert(table: str, data: dict):
    """INSERT a row. Returns inserted row dict or None."""
    try:
        r = requests.post(f"{REST_URL}/{table}", headers=HEADERS, json=data, timeout=10)
        if r.status_code in (200, 201):
            res = r.json()
            return res[0] if isinstance(res, list) and res else res
        st.error(f"خطأ إضافة ({table}): {r.text[:200]}")
    except Exception as e:
        st.error(f"خطأ: {e}")
    return None


def sb_update(table: str, match: dict, data: dict):
    """UPDATE rows matching match dict."""
    params = {k: f"eq.{v}" for k, v in match.items()}
    try:
        r = requests.patch(f"{REST_URL}/{table}", headers=HEADERS,
                           json=data, params=params, timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        st.error(f"خطأ تحديث: {e}")
        return False


def sb_count(table: str, filters: dict = None) -> int:
    """Return count of rows matching filters."""
    params = {"select": "id"}
    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"
    h = {**HEADERS, "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"}
    try:
        r = requests.get(f"{REST_URL}/{table}", headers=h, params=params, timeout=10)
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            return int(cr.split("/")[1])
    except Exception:
        pass
    return 0


def sb_sum(table: str, col: str, filters: dict = None) -> float:
    """Return SUM of a column (fetches all rows, sums locally)."""
    rows = sb_select(table, filters=filters, limit=5000)
    return sum(float(r.get(col, 0) or 0) for r in rows)


def ping_supabase() -> bool:
    """Check if Supabase is reachable."""
    try:
        r = requests.get(f"{REST_URL}/users", headers=HEADERS,
                         params={"limit": 1}, timeout=8)
        return r.status_code in (200, 206)
    except Exception:
        return False


# ── Supabase Storage helpers ─────────────────────────────────────────────────

def storage_upload(file_bytes: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """Upload file to Supabase Storage bucket. Returns public URL or ''."""
    ts   = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = f"{ts}_{filename}"
    url  = f"{STORAGE_URL}/object/{BUCKET}/{path}"
    h    = {
        "apikey":        SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Content-Type":  content_type,
        "x-upsert":      "true",
    }
    try:
        r = requests.post(url, headers=h, data=file_bytes, timeout=60)
        if r.status_code in (200, 201):
            return f"{STORAGE_URL}/object/public/{BUCKET}/{path}"
        st.error(f"⚠️ خطأ رفع الملف: {r.text[:200]}")
    except Exception as e:
        st.error(f"⚠️ خطأ رفع: {e}")
    return ""


def storage_download_url(file_url: str) -> str:
    """Return a public download URL (already public from bucket settings)."""
    return file_url


def dl_btn_url(url: str, label="⬇️ تحميل", filename="file"):
    """Download button that fetches from URL."""
    if not url:
        st.caption("⚠️ لا يوجد ملف مرفوع"); return
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            fname = url.split("/")[-1]
            st.download_button(label, r.content, file_name=fname, use_container_width=True)
        else:
            st.markdown(f'<a href="{url}" target="_blank">🔗 فتح الملف</a>', unsafe_allow_html=True)
    except Exception:
        st.markdown(f'<a href="{url}" target="_blank">🔗 فتح الملف</a>', unsafe_allow_html=True)


# ── Business helpers ─────────────────────────────────────────────────────────

def wid() -> int:
    return st.session_state.get("workspace_id", 0)

def order_no() -> str:
    n = sb_count("orders", {"workspace_id": wid()})
    return f"ZO-{datetime.date.today().strftime('%y%m%d')}-{n+1:04d}"

def sync_status(order_id: int):
    o = sb_select("orders", {"id": order_id}, single=True)
    if not o: return
    ds  = o.get("design_status",    "قيد الانتظار")
    ps  = o.get("production_status","قيد الانتظار")
    dv  = o.get("delivered", False)
    s = ("تم التسليم"   if dv
         else "مكتمل"           if ps == "مكتمل"
         else "جاري الإنتاج"   if ps == "جاري الإنتاج"
         else "جاهز للإنتاج"   if ds == "مكتمل"
         else "جديد")
    sb_update("orders", {"id": order_id}, {"status": s})

def upload_design_file(uploaded_file) -> str:
    """Upload design file to Supabase Storage, return public URL."""
    if not uploaded_file:
        return ""
    content_type = uploaded_file.type or "application/octet-stream"
    safe = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._-")
    return storage_upload(uploaded_file.read(), safe, content_type)

def upload_agent_image(uploaded_file) -> str:
    """Upload agent photo. Returns public URL."""
    if not uploaded_file:
        return ""
    content_type = uploaded_file.type or "image/jpeg"
    safe = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._-")
    return storage_upload(uploaded_file.read(), f"agent_{safe}", content_type)


# ─────────────────────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

ORD_BADGE = {
    "جديد":          ("b-new",   "🔵 جديد"),
    "جاهز للإنتاج":  ("b-ready", "🟢 جاهز"),
    "جاري الإنتاج":  ("b-print", "🟠 إنتاج"),
    "مكتمل":         ("b-done",  "✅ مكتمل"),
    "تم التسليم":    ("b-deliv", "📦 تسليم"),
}
SEV_BADGE = {"منخفض":("b-sev-lo","🟢"),"متوسط":("b-sev-md","🟡"),"عالي":("b-sev-hi","🔴")}
AGT_BADGE = {"اشترى":("b-abuy","✅ اشترى"),"محتمل":("b-apot","🔵 محتمل"),"لن يشتري":("b-ano","❌ لا")}

def badge(k, t):
    cls, lbl = t.get(k, ("b-pend", k))
    return f'<span class="badge {cls}">{lbl}</span>'

def hdr(icon, title, sub=""):
    st.markdown(
        f'<div class="ph"><div class="ph-icon">{icon}</div>'
        f'<div><h2>{title}</h2><p>{sub}</p></div></div>',
        unsafe_allow_html=True)

def guide(txt):
    with st.expander("💡 إرشادات", expanded=False):
        st.markdown(f'<div class="icard">{txt}</div>', unsafe_allow_html=True)

def footer():
    st.markdown(
        f'<div class="footer">'
        f'<span>🖨️ <span class="hi">{APP_NAME}</span> v{APP_VER}</span>'
        f'<span class="hi">{APP_TAGLINE}</span>'
        f'<span>Developed by <span class="hi">{DEVELOPER}</span> &nbsp;©{YEAR}</span>'
        f'</div>', unsafe_allow_html=True)

def show_orders_table(role, uid_filter=None, title="الأوردرات"):
    hdr("📋", title)
    hide_price = role not in ("admin","sales","superadmin")
    filters = {"workspace_id": wid()}
    if uid_filter:
        filters["created_by_id"] = uid_filter
    rows = sb_select("orders", filters=filters, order="id.desc")
    if not rows:
        st.info("لا توجد أوردرات."); return

    sts = ["الكل"] + sorted({r.get("status","") for r in rows})
    sel = st.selectbox("الحالة", sts, key=f"o_{role}_{uid_filter}")
    if sel != "الكل":
        rows = [r for r in rows if r.get("status") == sel]

    cols = ["order_number","customer_name","description","quantity",
            "status","design_status","production_status","created_at"]
    if not hide_price: cols.insert(4, "price")
    lbl = {"order_number":"الأوردر","customer_name":"العميل","description":"الوصف",
           "quantity":"الكمية","price":"السعر","status":"الحالة",
           "design_status":"التصميم","production_status":"الإنتاج","created_at":"التاريخ"}
    df = pd.DataFrame(rows)
    ok = [c for c in cols if c in df.columns]
    st.dataframe(df[ok].rename(columns=lbl), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  GATEKEEPER
# ─────────────────────────────────────────────────────────────────────────────

def gatekeeper() -> bool:
    if st.session_state.get("auth"):
        return True

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="logo-big">Z<span class="sep">-</span>ORDER</div>'
            f'<div class="logo-tag">{APP_TAGLINE}</div>'
            f'<div style="text-align:center;color:var(--t3);font-size:.66rem;margin-top:.4rem">v{APP_VER} · Cloud Edition</div>',
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div style="background:var(--bg2);border:1px solid var(--bdr2);'
            'border-radius:16px;padding:1.75rem 1.5rem;">',
            unsafe_allow_html=True)

        idn     = st.text_input("📧 الإيميل أو اسم المستخدم", placeholder="admin@zorder.iq", key="gk_i")
        pw      = st.text_input("🔒 كلمة المرور", type="password", key="gk_p")
        clicked = st.button("دخول ←", key="gk_b")

        st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            if not idn or not pw:
                st.error("يرجى إدخال البيانات."); return False

            i  = idn.strip().lower()
            pw_hash = _hash(pw)

            # Search by email OR username
            rows = sb_select("users", limit=2)
            user = None

            # Try email match
            r1 = requests.get(f"{REST_URL}/users", headers=HEADERS,
                              params={"email": f"eq.{i}", "password": f"eq.{pw_hash}",
                                      "is_active": "eq.true", "limit": 1}, timeout=8)
            if r1.status_code == 200 and r1.json():
                user = r1.json()[0]

            # Try username match
            if not user:
                r2 = requests.get(f"{REST_URL}/users", headers=HEADERS,
                                  params={"username": f"eq.{i}", "password": f"eq.{pw_hash}",
                                          "is_active": "eq.true", "limit": 1}, timeout=8)
                if r2.status_code == 200 and r2.json():
                    user = r2.json()[0]

            if user:
                ws_id   = user.get("workspace_id", 0)
                ws_name = "Z-ORDER Platform"
                if ws_id and ws_id > 0:
                    ws = sb_select("workspaces", {"id": ws_id}, single=True)
                    ws_name = ws.get("name", "") if ws else ""

                st.session_state.update(
                    auth=True,
                    uid=user["id"],
                    uname=user["full_name"],
                    role=user["role"],
                    workspace_id=ws_id,
                    workspace_name=ws_name,
                )
                st.rerun()
            else:
                st.error("❌ بيانات غير صحيحة أو الحساب موقوف.")

        st.markdown(
            f'<div style="text-align:center;margin-top:1.1rem;color:var(--t3);font-size:.64rem">'
            f'Developed by <b style="color:var(--gold)">{DEVELOPER}</b></div>',
            unsafe_allow_html=True)
    return False


# ─────────────────────────────────────────────────────────────────────────────
#  TOP NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────

def top_nav() -> str:
    role  = st.session_state["role"]
    uname = st.session_state["uname"]
    wsn   = st.session_state.get("workspace_name", "")
    ri    = ROLES.get(role, {"ar": role, "icon":"👤", "clr":"#e8a020"})
    init  = "".join(w[0] for w in uname.split()[:2]).upper() or "?"
    pages = ROLE_PAGES.get(role, [])

    st.markdown(
        f'<div class="topbar">'
        f'<div class="zlogo">Z<span class="sep">-</span>ORDER'
        f'<span class="tag">{APP_TAGLINE}</span></div>'
        f'<div class="uchip" style="margin-right:auto">'
        f'<div class="uavatar">{init}</div>'
        f'<div style="display:flex;flex-direction:column;gap:0">'
        f'<span style="font-size:.76rem;font-weight:600;color:var(--t1);line-height:1.2">{uname}</span>'
        f'<span style="font-size:.6rem;color:{ri["clr"]}">{ri["icon"]} {ri["ar"]}'
        f'{" · "+wsn if wsn else ""}</span>'
        f'</div></div></div>',
        unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown('<div class="nav-sel">', unsafe_allow_html=True)
        if "page" not in st.session_state or st.session_state["page"] not in pages:
            st.session_state["page"] = pages[0]
        active = st.selectbox("", pages,
                               index=pages.index(st.session_state["page"]),
                               key="nav_sel", label_visibility="collapsed")
        st.session_state["page"] = active
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if st.button("خروج 🚪", key="lo_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    return active


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: SUPER-ADMIN
# ─────────────────────────────────────────────────────────────────────────────

def pg_super_dash():
    hdr("⭐","لوحة التحكم — Platform Admin","إدارة جميع الشركات")
    # Connection status
    ok = ping_supabase()
    st.markdown(
        f'<div class="{"conn-ok" if ok else "conn-err"}">'
        f'{"🟢 متصل بـ Supabase" if ok else "🔴 تعذّر الاتصال بـ Supabase"}'
        f'</div><br>', unsafe_allow_html=True)

    ws_count = sb_count("workspaces")
    u_count  = sb_count("users")
    o_count  = sb_count("orders")
    rev      = sb_sum("orders","price")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("الشركات المسجلة", ws_count)
    c2.metric("المستخدمون", u_count)
    c3.metric("إجمالي الأوردرات", o_count)
    c4.metric("الإيراد الكلي (د.ع)", f"{rev:,.0f}")

    st.markdown("---")
    ws_list = sb_select("workspaces", order="id.desc")
    if ws_list:
        df = pd.DataFrame(ws_list)[["id","name","slug","plan","is_active","created_at"]]
        st.dataframe(df.rename(columns={"id":"#","name":"الشركة","slug":"Slug",
                                        "plan":"الخطة","is_active":"نشطة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


def pg_super_workspaces():
    hdr("🏢","إدارة الشركات","أضف شركات وأنشئ مديريها")
    guide("① أنشئ شركة جديدة وحدد مديرها<br>② كل شركة Workspace معزول تماماً<br>③ المدير يضيف موظفيه بنفسه")

    ws_list = sb_select("workspaces", order="id.asc")
    if ws_list:
        df = pd.DataFrame(ws_list)
        if "is_active" in df.columns:
            df["is_active"] = df["is_active"].map({True:"✅",False:"🚫",1:"✅",0:"🚫"})
        st.dataframe(df[["id","name","slug","plan","is_active"]].rename(columns={
            "id":"#","name":"الشركة","slug":"Slug","plan":"الخطة","is_active":"نشطة"
        }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sec">➕ شركة جديدة + مديرها</div>', unsafe_allow_html=True)
    with st.form("add_ws", clear_on_submit=True):
        c1,c2 = st.columns(2)
        ws_name = c1.text_input("اسم الشركة *")
        ws_slug = c2.text_input("Slug (حروف إنجليزية) *", placeholder="my-company")
        plan    = st.selectbox("الخطة", ["starter","pro","enterprise"])
        st.markdown('<div class="sec">بيانات مدير الشركة</div>', unsafe_allow_html=True)
        c3,c4 = st.columns(2)
        adm_fn = c3.text_input("اسم المدير *")
        adm_un = c4.text_input("اسم المستخدم *")
        c5,c6  = st.columns(2)
        adm_em = c5.text_input("إيميل المدير *")
        adm_pw = c6.text_input("كلمة مرور المدير *", type="password")
        sub    = st.form_submit_button("✅ إنشاء الشركة والمدير", use_container_width=True)

    if sub:
        if not all([ws_name, ws_slug, adm_fn, adm_un, adm_em, adm_pw]):
            st.error("يرجى تعبئة جميع الحقول.")
        else:
            slug = ws_slug.strip().lower().replace(" ","-")
            ws = sb_insert("workspaces", {"name":ws_name.strip(),"slug":slug,"plan":plan})
            if ws:
                ws_id = ws.get("id")
                adm = sb_insert("users", {
                    "workspace_id": ws_id,
                    "full_name":    adm_fn.strip(),
                    "username":     adm_un.strip().lower(),
                    "email":        adm_em.strip().lower(),
                    "password":     _hash(adm_pw),
                    "role":         "admin",
                    "created_by":   0,
                    "is_active":    True,
                })
                if adm:
                    st.success(f"✅ تم إنشاء الشركة **{ws_name}** والمدير **{adm_fn}**!")
                    st.rerun()


def pg_super_users():
    hdr("👥","جميع المستخدمين","عرض عبر كل الشركات")
    rows = sb_select("users", order="workspace_id.asc,id.asc")
    if rows:
        df = pd.DataFrame(rows)[["id","workspace_id","full_name","username","email","role","is_active","created_at"]]
        df["is_active"] = df["is_active"].map({True:"✅",False:"🚫",1:"✅",0:"🚫"})
        st.dataframe(df.rename(columns={"id":"#","workspace_id":"WS","full_name":"الاسم",
                                        "username":"المستخدم","email":"الإيميل","role":"الدور",
                                        "is_active":"نشط","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


def pg_super_stats():
    hdr("📊","الإحصائيات العامة","بيانات كل الشركات")
    ws_list = sb_select("workspaces", order="id.asc")
    if not ws_list:
        st.info("لا توجد شركات."); return
    stats = []
    for ws in ws_list:
        orders = sb_select("orders", {"workspace_id": ws["id"]})
        total  = sum(float(o.get("price",0) or 0) for o in orders)
        done   = sum(float(o.get("price",0) or 0) for o in orders
                     if o.get("status") in ("مكتمل","تم التسليم"))
        stats.append({"الشركة":ws["name"],"الأوردرات":len(orders),
                      "إجمالي القيمة":f"{total:,.0f}","الإيراد المحصّل":f"{done:,.0f}"})
    st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: WORKSPACE ADMIN
# ─────────────────────────────────────────────────────────────────────────────

def pg_admin_dash():
    hdr("🛡️","لوحة المدير","إحصائيات شركتك")
    guide("① راقب الأوردرات والمالية<br>② راجع طلبات الشراء والبلاغات<br>③ أضف الفريق من «الفريق»")
    WID   = wid()
    today = datetime.date.today().isoformat()

    orders = sb_select("orders", {"workspace_id": WID})
    tot = len(orders)
    tod = sum(1 for o in orders if o.get("created_at","").startswith(today))
    dn  = sum(1 for o in orders if o.get("status") in ("مكتمل","تم التسليم"))
    rv  = sum(float(o.get("price",0) or 0) for o in orders if o.get("status") in ("مكتمل","تم التسليم"))
    tv  = sum(float(o.get("price",0) or 0) for o in orders)

    prs = sb_select("purchase_requests", {"workspace_id": WID, "status": "قيد المراجعة"})
    irs = sb_select("incident_reports",  {"workspace_id": WID, "status": "مفتوح"})
    usr = sb_select("users",             {"workspace_id": WID, "is_active": True})

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("أوردرات اليوم", tod);           c2.metric("مكتملة/إجمالي", f"{dn}/{tot}")
    c3.metric("إيراد محصّل (د.ع)",f"{rv:,.0f}"); c4.metric("طلبات شراء معلقة", len(prs))
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("إجمالي القيمة (د.ع)",f"{tv:,.0f}"); c6.metric("قيد التنفيذ (د.ع)",f"{tv-rv:,.0f}")
    c7.metric("بلاغات مفتوحة", len(irs));         c8.metric("موظفون نشطون", len(usr))

    st.markdown("---")
    t1,t2,t3,t4 = st.tabs(["📋 آخر الأوردرات","📦 طلبات الشراء","🚨 البلاغات","🗺️ المندوبون"])
    with t1:
        rows = sb_select("orders",{"workspace_id":WID}, order="id.desc", limit=15)
        if rows:
            df = pd.DataFrame(rows)[["order_number","customer_name","quantity","price","status","created_at"]]
            st.dataframe(df.rename(columns={"order_number":"الأوردر","customer_name":"العميل",
                                            "quantity":"الكمية","price":"السعر","status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.info("لا توجد أوردرات.")
    with t2:
        rows = sb_select("purchase_requests",{"workspace_id":WID}, order="id.desc", limit=20)
        if rows:
            df = pd.DataFrame(rows)[["requester_name","department","item_name","quantity","urgency","status","created_at"]]
            st.dataframe(df.rename(columns={"requester_name":"الموظف","department":"القسم",
                                            "item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية",
                                            "status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.info("لا توجد طلبات.")
    with t3:
        rows = sb_select("incident_reports",{"workspace_id":WID}, order="id.desc", limit=15)
        if rows:
            df = pd.DataFrame(rows)[["reporter_name","department","description","severity","status","created_at"]]
            st.dataframe(df.rename(columns={"reporter_name":"المبلّغ","department":"القسم","description":"الوصف",
                                            "severity":"الخطورة","status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.success("🎉 لا بلاغات!")
    with t4:
        visits = sb_select("agent_visits",{"workspace_id":WID})
        if visits:
            agents = {}
            for v in visits:
                an = v.get("agent_name","")
                if an not in agents: agents[an]={"اشترى":0,"محتمل":0,"لن يشتري":0,"الزيارات":0}
                agents[an]["الزيارات"] += 1
                agents[an][v.get("visit_status","محتمل")] = agents[an].get(v.get("visit_status","محتمل"),0)+1
            st.dataframe(pd.DataFrame([{"المندوب":k,**v} for k,v in agents.items()]),
                         use_container_width=True, hide_index=True)
        else: st.info("لا توجد زيارات.")


def pg_team():
    hdr("👥","إدارة الفريق","أضف أعضاء الفريق")
    guide("① أنت المدير — الوحيد الذي يضيف موظفين لشركتك<br>② كل موظف يرى فقط بيانات شركتك<br>③ يمكن تعطيل أي حساب")
    WID = wid()
    rows = sb_select("users", {"workspace_id":WID}, order="id.asc")
    if rows:
        df = pd.DataFrame(rows)[["id","full_name","username","email","role","is_active","created_at"]]
        df["is_active"] = df["is_active"].map({True:"✅ نشط",False:"🚫 موقوف",1:"✅ نشط",0:"🚫 موقوف"})
        st.dataframe(df.rename(columns={"id":"#","full_name":"الاسم","username":"المستخدم",
                                        "email":"الإيميل","role":"الدور","is_active":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sec">➕ إضافة موظف جديد</div>', unsafe_allow_html=True)
    with st.form("add_emp", clear_on_submit=True):
        c1,c2 = st.columns(2)
        fn = c1.text_input("الاسم الكامل *"); un = c2.text_input("اسم المستخدم *")
        c3,c4 = st.columns(2)
        em = c3.text_input("الإيميل *")
        rl = c4.selectbox("الدور *",
                          [r for r in ROLES if r not in ("superadmin","admin")],
                          format_func=lambda r: f"{ROLES[r]['icon']} {ROLES[r]['ar']}")
        c5,c6 = st.columns(2)
        p1 = c5.text_input("كلمة المرور *", type="password")
        p2 = c6.text_input("التأكيد *", type="password")
        ok = st.form_submit_button("✅ إضافة", use_container_width=True)

    if ok:
        errs = []
        if not all([fn,un,em,p1]): errs.append("جميع الحقول مطلوبة.")
        if p1 and p1!=p2:          errs.append("كلمتا المرور غير متطابقتين.")
        if p1 and len(p1)<6:       errs.append("كلمة المرور 6 أحرف على الأقل.")
        for e in errs: st.error(e)
        if not errs:
            res = sb_insert("users", {
                "workspace_id": WID,
                "full_name":    fn.strip(),
                "username":     un.strip().lower(),
                "email":        em.strip().lower(),
                "password":     _hash(p1),
                "role":         rl,
                "created_by":   st.session_state["uid"],
                "is_active":    True,
            })
            if res:
                st.success(f"✅ تم إضافة **{fn}**!"); st.rerun()
            else:
                st.error("❌ اسم المستخدم أو الإيميل مستخدم بالفعل.")

    st.markdown("---")
    st.markdown('<div class="sec">🔄 تفعيل / تعطيل</div>', unsafe_allow_html=True)
    all_u = [u for u in rows if u.get("role") != "admin"] if rows else []
    if all_u:
        opts  = {f"{u['id']} — {u['full_name']} ({u['username']})": u["id"] for u in all_u}
        label = st.selectbox("الموظف", list(opts.keys()))
        ut    = opts[label]
        ca,cb,_ = st.columns([1,1,3])
        if ca.button("✅ تفعيل",  key="act"):  sb_update("users",{"id":ut},{"is_active":True});  st.rerun()
        if cb.button("🚫 تعطيل", key="dact"): sb_update("users",{"id":ut},{"is_active":False}); st.rerun()
    else:
        st.info("لا يوجد موظفون مضافون بعد.")


def pg_support():
    hdr("📞","الدعم الفني","تواصل مع فريق Z-ORDER")
    st.markdown(
        f'<div class="support-card">'
        f'<div style="font-size:2rem;margin-bottom:.5rem">🛎️</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:var(--t1);margin-bottom:.3rem">فريق دعم Z-ORDER</div>'
        f'<div style="color:var(--t2);font-size:.85rem;margin-bottom:.4rem">نحن هنا لمساعدتك في أي وقت</div>'
        f'<div style="font-size:.95rem;color:var(--gold);font-weight:600;margin:.5rem 0">📞 {SUPPORT_PHONE}</div>'
        f'<a class="wa-btn" href="{SUPPORT_WA}" target="_blank">'
        f'<span style="font-size:1.1rem">💬</span> تواصل عبر واتساب</a>'
        f'</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: SALES
# ─────────────────────────────────────────────────────────────────────────────

def pg_sales_dash():
    hdr("📊","لوحتي","أوردراتك وإحصائياتك")
    uid = st.session_state["uid"]; WID = wid()
    orders = sb_select("orders",{"workspace_id":WID,"created_by_id":uid})
    tot = len(orders)
    dn  = sum(1 for o in orders if o.get("status") in ("مكتمل","تم التسليم"))
    rv  = sum(float(o.get("price",0) or 0) for o in orders if o.get("status") in ("مكتمل","تم التسليم"))
    nw  = sum(1 for o in orders if o.get("status") == "جديد")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي أوردراتي",tot); c2.metric("مكتملة",dn)
    c3.metric("إيراداتي (د.ع)",f"{rv:,.0f}"); c4.metric("جديدة",nw)
    st.markdown("---")
    show_orders_table("sales", uid_filter=uid, title="أوردراتي الأخيرة")


def pg_add_order():
    hdr("➕","أوردر جديد","أدخل تفاصيل طلب العميل")
    with st.form("new_order", clear_on_submit=True):
        c1,c2 = st.columns(2)
        cust  = c1.text_input("👤 اسم العميل *")
        qty   = c2.number_input("📦 الكمية *", min_value=1, value=1)
        desc  = st.text_area("📝 وصف الطلب *", placeholder="المقاس، نوع الورق، التفاصيل...")
        c3,_  = st.columns(2)
        price = c3.number_input("💰 السعر (د.ع) *", min_value=0.0, step=500.0)
        sub   = st.form_submit_button("✅ حفظ الأوردر", use_container_width=True)
    if sub:
        if not cust.strip() or not desc.strip() or price <= 0:
            st.error("يرجى تعبئة جميع الحقول — السعر يجب أن يكون أكبر من صفر.")
        else:
            ono = order_no()
            res = sb_insert("orders", {
                "workspace_id":    wid(),
                "order_number":    ono,
                "customer_name":   cust.strip(),
                "description":     desc.strip(),
                "quantity":        int(qty),
                "price":           float(price),
                "created_by_id":   st.session_state["uid"],
                "created_by_name": st.session_state["uname"],
                "status":          "جديد",
                "design_status":   "قيد الانتظار",
                "production_status":"قيد الانتظار",
                "delivered":       False,
            })
            if res:
                st.success(f"✅ تم حفظ الأوردر **{ono}** — سيظهر لقسم التصميم فوراً!")


def pg_sales_design_preview():
    hdr("🖼️","معاينة التصاميم","عرض الملفات المرفوعة من المصممين")
    guide("① يمكنك تحميل أو فتح ملف التصميم للتأكد قبل الإنتاج<br>② لا يمكنك تعديل التصميم من هنا")
    rows = sb_select("orders",{"workspace_id":wid(),"design_status":"مكتمل"}, order="design_updated.desc")
    if not rows:
        st.info("لا توجد تصاميم مكتملة بعد."); return
    for r in rows:
        with st.expander(f"🎨 {r.get('order_number','')} — {r.get('customer_name','')}"):
            c1,c2 = st.columns(2)
            c1.markdown(f"**الوصف:** {r.get('description','')}")
            c1.markdown(f"**الكمية:** {r.get('quantity','')}")
            c2.markdown(f"**صمّمه:** {r.get('design_by','—')}")
            c2.markdown(f"**تاريخ التصميم:** {r.get('design_updated','—')}")
            if r.get("design_notes"):
                st.markdown(f"**ملاحظات المصمم:** {r.get('design_notes','')}")
            st.markdown("---")
            file_url = r.get("design_file_url","") or r.get("design_link","")
            if file_url:
                col1,col2 = st.columns(2)
                with col1: dl_btn_url(file_url,"⬇️ تحميل ملف التصميم")
                with col2: st.markdown(f'<a href="{file_url}" target="_blank" style="color:var(--gold)">🔗 فتح في المتصفح</a>', unsafe_allow_html=True)
                # Image preview
                ext = file_url.split(".")[-1].lower()
                if ext in ["png","jpg","jpeg","webp","gif"]:
                    try:
                        r2 = requests.get(file_url, timeout=15)
                        if r2.status_code == 200:
                            st.image(r2.content, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.caption("لا يوجد ملف مرفوع بعد.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: DESIGN
# ─────────────────────────────────────────────────────────────────────────────

def pg_design():
    hdr("🎨","قسم التصميم","ارفع ملف التصميم لكل أوردر")
    guide("① الملف يُرفع مباشرة لـ Supabase Storage — لن يضيع أبداً<br>② الإنتاج لن يبدأ إلا بعد رفع الملف<br>③ قسم المبيعات يمكنه معاينة الملف")
    WID = wid()
    rows = sb_select("orders",{"workspace_id":WID}, order="id.desc")
    pend = [r for r in rows if r.get("design_status") == "قيد الانتظار"]
    done = [r for r in rows if r.get("design_status") == "مكتمل"]

    t1,t2 = st.tabs([f"⏳ قيد الانتظار ({len(pend)})", f"✅ مكتملة ({len(done)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد مهام تصميم معلقة!")
        for r in pend:
            with st.expander(f"🔷 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r.get('description','')}")
                c1.markdown(f"**الكمية:** {r.get('quantity','')}")
                c2.markdown(f"**التاريخ:** {r.get('created_at','')}")
                c2.markdown(f"**أضافه:** {r.get('created_by_name','')}")
                st.markdown("---")
                upld  = st.file_uploader("📎 رفع ملف التصميم *", key=f"du_{r['id']}",
                                          type=["pdf","png","jpg","jpeg","ai","psd","svg","eps","zip","cdr"],
                                          help="يُرفع إلى Supabase Storage تلقائياً")
                dl    = st.text_input("🔗 أو رابط التصميم (بديل)", value=r.get("design_link","") or "", key=f"dl_{r['id']}")
                notes = st.text_area("📝 ملاحظات للإنتاج", value=r.get("design_notes","") or "",
                                     key=f"dn_{r['id']}", height=65)

                if st.button("✅ تأكيد رفع التصميم", key=f"d_ok_{r['id']}"):
                    with st.spinner("جاري رفع الملف إلى السحابة..."):
                        file_url = upload_design_file(upld) if upld else (r.get("design_file_url","") or "")
                        link     = dl.strip() or r.get("design_link","")

                    if not file_url and not link:
                        st.error("⚠️ يجب رفع ملف أو إدخال رابط التصميم.")
                    else:
                        now = now_ts()
                        sb_update("orders", {"id": r["id"]}, {
                            "design_status":   "مكتمل",
                            "design_file_url": file_url,
                            "design_link":     link,
                            "design_notes":    notes.strip(),
                            "design_updated":  now,
                            "design_by":       st.session_state["uname"],
                        })
                        sync_status(r["id"])
                        st.success("✅ تم رفع التصميم إلى السحابة! الأوردر جاهز للإنتاج.")
                        st.rerun()

    with t2:
        if not done: st.info("لا توجد تصاميم مكتملة.")
        for r in done:
            co1,co2 = st.columns([4,2])
            with co1:
                st.markdown(
                    f'<div class="card"><b>{r.get("order_number","")}</b> — {r.get("customer_name","")}'
                    f'&nbsp;{badge("مكتمل",ORD_BADGE)}'
                    f'<br><small style="color:var(--t3)">🗓 {r.get("design_updated","—")} | 👤 {r.get("design_by","—")}</small></div>',
                    unsafe_allow_html=True)
            with co2:
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu:
                    dl_btn_url(fu,"⬇️ تحميل")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: PRODUCTION
# ─────────────────────────────────────────────────────────────────────────────

def pg_production():
    hdr("🖨️","قسم الإنتاج","نفّذ الأوردرات الجاهزة")
    guide("① الأوردر يظهر هنا فقط بعد رفع التصميم<br>② حمّل ملف التصميم من Supabase Storage<br>③ عند الانتهاء غيّر الحالة إلى مكتمل")
    WID  = wid()
    rows = sb_select("orders",{"workspace_id":WID}, order="id.desc")
    ready    = [r for r in rows if r.get("design_status")=="مكتمل" and r.get("production_status")=="قيد الانتظار"]
    printing = [r for r in rows if r.get("production_status")=="جاري الإنتاج"]
    done     = [r for r in rows if r.get("production_status")=="مكتمل"]

    t1,t2,t3 = st.tabs([f"🟢 جاهز ({len(ready)})",f"🟠 جاري ({len(printing)})",f"✅ مكتمل ({len(done)})"])

    with t1:
        if not ready: st.info("⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم.")
        for r in ready:
            with st.expander(f"🟢 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r.get('description','')}")
                c1.markdown(f"**الكمية:** {r.get('quantity','')}")
                c2.markdown(f"**ملاحظات التصميم:** {r.get('design_notes','—')}")
                c2.markdown(f"**صمّمه:** {r.get('design_by','—')}")
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu:
                    dl_btn_url(fu,"⬇️ تحميل ملف التصميم للطباعة")
                pn = st.text_area("📝 ملاحظات الإنتاج", key=f"pn_{r['id']}", height=55)
                col1,col2 = st.columns(2)
                if col1.button("▶️ بدء الطباعة", key=f"st_{r['id']}"):
                    now = now_ts()
                    sb_update("orders",{"id":r["id"]},{
                        "production_status":"جاري الإنتاج",
                        "production_notes":pn,
                        "production_updated":now,
                        "production_by":st.session_state["uname"]})
                    sync_status(r["id"]); st.success("▶️ بدأ الإنتاج!"); st.rerun()
                if col2.button("✅ إتمام مباشر", key=f"fi_{r['id']}"):
                    now = now_ts()
                    sb_update("orders",{"id":r["id"]},{
                        "production_status":"مكتمل",
                        "production_notes":pn,
                        "production_updated":now,
                        "production_by":st.session_state["uname"]})
                    sync_status(r["id"]); st.success("✅ مكتمل!"); st.rerun()

    with t2:
        if not printing: st.info("لا توجد طباعة جارية.")
        for r in printing:
            with st.expander(f"🟠 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                st.markdown(f"**الوصف:** {r.get('description','')} | **الكمية:** {r.get('quantity','')}")
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu: dl_btn_url(fu)
                if st.button("✅ تحديد كمكتمل", key=f"fn_{r['id']}"):
                    sb_update("orders",{"id":r["id"]},{
                        "production_status":"مكتمل",
                        "production_updated":now_ts()})
                    sync_status(r["id"]); st.success("✅ مكتمل!"); st.rerun()

    with t3:
        if not done: st.info("لا توجد أوردرات مكتملة.")
        for r in done:
            st.markdown(
                f'<div class="card"><b>{r.get("order_number","")}</b> — {r.get("customer_name","")}'
                f'&nbsp;{badge("مكتمل",ORD_BADGE)}'
                f'<br><small style="color:var(--t3)">اكتمل: {r.get("production_updated","—")}</small></div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: PURCHASE
# ─────────────────────────────────────────────────────────────────────────────

def pg_purchase_submit():
    hdr("📦","طلب شراء","اطلب مواد من قسم المشتريات")
    with st.form("pur_req", clear_on_submit=True):
        c1,c2 = st.columns(2)
        item  = c1.text_input("اسم الصنف المطلوب *", placeholder="حبر أسود، ورق A3...")
        qty   = c2.text_input("الكمية *", placeholder="5 علب، 10 رزمة...")
        urg   = st.selectbox("الأولوية", ["عادي","عاجل","طارئ"])
        notes = st.text_area("ملاحظات", height=65)
        sub   = st.form_submit_button("📤 إرسال الطلب", use_container_width=True)
    if sub:
        if not item.strip() or not qty.strip():
            st.error("يرجى تحديد الصنف والكمية.")
        else:
            role = st.session_state["role"]
            res  = sb_insert("purchase_requests", {
                "workspace_id":   wid(),
                "requester_id":   st.session_state["uid"],
                "requester_name": st.session_state["uname"],
                "department":     ROLES[role]["ar"],
                "item_name":      item.strip(),
                "quantity":       qty.strip(),
                "urgency":        urg,
                "notes":          notes.strip(),
                "status":         "قيد المراجعة",
            })
            if res: st.success("✅ تم إرسال طلب الشراء!")
    st.markdown("---")
    rows = sb_select("purchase_requests",
                     {"workspace_id":wid(),"requester_id":st.session_state["uid"]},
                     order="id.desc", limit=10)
    if rows:
        df = pd.DataFrame(rows)[["item_name","quantity","urgency","status","created_at"]]
        st.dataframe(df.rename(columns={"item_name":"الصنف","quantity":"الكمية",
                                        "urgency":"الأولوية","status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("لم تقدم أي طلب بعد.")


def pg_purchase_manage():
    hdr("📦","إدارة طلبات الشراء","راجع وأدر جميع الطلبات")
    guide("① الطارئ والعاجل يظهران أولاً<br>② وافق أو ارفض كل طلب")
    WID  = wid()
    rows = sb_select("purchase_requests",{"workspace_id":WID}, order="id.desc")
    rows_sorted = sorted(rows, key=lambda r: {"طارئ":0,"عاجل":1,"عادي":2}.get(r.get("urgency","عادي"),2))
    pend = [r for r in rows_sorted if r.get("status") == "قيد المراجعة"]
    rest = [r for r in rows_sorted if r.get("status") != "قيد المراجعة"]

    t1,t2 = st.tabs([f"⏳ قيد المراجعة ({len(pend)})", f"📋 السجل ({len(rest)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد طلبات معلقة!")
        for r in pend:
            uc = {"طارئ":"var(--red)","عاجل":"var(--acc2)","عادي":"var(--t2)"}.get(r.get("urgency","عادي"),"var(--t2)")
            with st.expander(f"📦 {r.get('item_name','')} — {r.get('requester_name','')} [{r.get('department','')}]"):
                st.markdown(
                    f"**الصنف:** {r.get('item_name','')} | **الكمية:** {r.get('quantity','')}"
                    f"<br>**الأولوية:** <span style='color:{uc}'>{r.get('urgency','')}</span>"
                    f" | **التاريخ:** {r.get('created_at','')}"
                    f"{'<br>**ملاحظات:** '+r.get('notes','') if r.get('notes') else ''}",
                    unsafe_allow_html=True)
                col1,col2 = st.columns(2)
                if col1.button("✅ موافقة", key=f"app_{r['id']}"):
                    sb_update("purchase_requests",{"id":r["id"]},{
                        "status":"موافق عليه","reviewed_by":st.session_state["uname"],"reviewed_at":now_ts()})
                    st.success("✅ موافق."); st.rerun()
                if col2.button("❌ رفض", key=f"rej_{r['id']}"):
                    sb_update("purchase_requests",{"id":r["id"]},{
                        "status":"مرفوض","reviewed_by":st.session_state["uname"],"reviewed_at":now_ts()})
                    st.warning("تم الرفض."); st.rerun()
    with t2:
        if not rest: st.info("لا يوجد سجل.")
        else:
            df = pd.DataFrame(rest)[["requester_name","department","item_name","quantity","urgency","status","reviewed_by","created_at"]]
            st.dataframe(df.rename(columns={"requester_name":"الموظف","department":"القسم",
                                            "item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية",
                                            "status":"الحالة","reviewed_by":"راجعه","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: AGENT
# ─────────────────────────────────────────────────────────────────────────────

def pg_agent_new():
    hdr("🗺️","تسجيل زيارة عميل","وثّق زيارتك الميدانية")
    with st.form("av", clear_on_submit=True):
        cust  = st.text_input("👤 اسم العميل / المحل *")
        loc   = st.text_input("📍 العنوان", placeholder="الشارع، الحي، المدينة")
        vs    = st.selectbox("📊 حالة العميل", ["محتمل","اشترى","لن يشتري"])
        notes = st.text_area("📝 ملاحظات", height=65)
        img   = st.file_uploader("📸 صورة المحل", type=["jpg","jpeg","png","webp"])
        sub   = st.form_submit_button("✅ حفظ الزيارة", use_container_width=True)
    if sub:
        if not cust.strip():
            st.error("يرجى إدخال اسم العميل.")
        else:
            with st.spinner("جاري رفع الصورة..."):
                ip = upload_agent_image(img) if img else ""
            res = sb_insert("agent_visits", {
                "workspace_id": wid(),
                "agent_id":     st.session_state["uid"],
                "agent_name":   st.session_state["uname"],
                "customer_name": cust.strip(),
                "location":     loc.strip(),
                "visit_status": vs,
                "notes":        notes.strip(),
                "image_path":   ip,
            })
            if res: st.success(f"✅ تم تسجيل زيارة **{cust.strip()}**!")


def pg_agent_my():
    hdr("📋","زياراتي","سجل زياراتك")
    rows = sb_select("agent_visits",{"workspace_id":wid(),"agent_id":st.session_state["uid"]},
                     order="id.desc")
    if not rows: st.info("لم تسجّل أي زيارة بعد."); return
    for r in rows:
        cls, lbl = AGT_BADGE.get(r.get("visit_status","محتمل"),("b-apot",r.get("visit_status","")))
        img_html = ""
        ip = r.get("image_path","")
        if ip and ip.startswith("http"):
            try:
                ir = requests.get(ip, timeout=10)
                if ir.status_code == 200:
                    b64 = base64.b64encode(ir.content).decode()
                    ctype = ir.headers.get("content-type","image/jpeg")
                    img_html = f'<br><img src="data:{ctype};base64,{b64}" style="max-width:100%;max-height:155px;border-radius:8px;margin-top:.4rem;object-fit:cover">'
            except Exception:
                pass
        st.markdown(
            f'<div class="card"><b>{r.get("customer_name","")}</b>&nbsp;<span class="badge {cls}">{lbl}</span>'
            f'<br><small style="color:var(--t2)">📍 {r.get("location","—")} | 🗓 {r.get("visited_at","")}</small>'
            f'{"<br><small>"+r.get("notes","")+"</small>" if r.get("notes") else ""}'
            f'{img_html}</div>', unsafe_allow_html=True)


def pg_agent_reports():
    hdr("🗺️","تقارير المندوبين","أداء فريق المبيعات الميداني")
    visits = sb_select("agent_visits",{"workspace_id":wid()})
    if not visits: st.info("لا توجد زيارات."); return
    agents = {}
    for v in visits:
        an = v.get("agent_name","")
        if an not in agents: agents[an]={"الزيارات":0,"اشترى":0,"محتمل":0,"لن يشتري":0,"آخر زيارة":""}
        agents[an]["الزيارات"] += 1
        agents[an][v.get("visit_status","محتمل")] = agents[an].get(v.get("visit_status","محتمل"),0)+1
        if v.get("visited_at","") > agents[an]["آخر زيارة"]:
            agents[an]["آخر زيارة"] = v.get("visited_at","")
    st.dataframe(pd.DataFrame([{"المندوب":k,**v} for k,v in agents.items()]),
                 use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: SHARED CHAT  — workspace-isolated
# ─────────────────────────────────────────────────────────────────────────────

def pg_chat():
    hdr("💬","محادثة الفريق","تواصل مع فريقك في نفس الشركة")
    guide("① المحادثة مشتركة بين جميع أقسام شركتك فقط<br>② لا يرى موظفو الشركات الأخرى رسائلك")
    WID = wid()
    uid = st.session_state["uid"]

    with st.form("chat_form", clear_on_submit=True):
        msg  = st.text_input("✍️ اكتب رسالتك...", placeholder="مناقشة مهمة، ملاحظة، سؤال...")
        sent = st.form_submit_button("إرسال ←", use_container_width=True)
    if sent and msg.strip():
        sb_insert("chat_messages", {
            "workspace_id": WID,
            "sender_id":    uid,
            "sender_name":  st.session_state["uname"],
            "sender_role":  st.session_state["role"],
            "message":      msg.strip(),
        })
        st.rerun()

    msgs = sb_select("chat_messages",{"workspace_id":WID}, order="id.desc", limit=60)
    msgs.reverse()
    if not msgs: st.info("لا توجد رسائل بعد. ابدأ المحادثة!"); return

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for m in msgs:
        is_me = m.get("sender_id") == uid
        ri    = ROLES.get(m.get("sender_role",""), {"clr":"#e8a020"})
        cls   = "me" if is_me else "other"
        st.markdown(
            f'<div class="bubble {cls}">'
            f'<div class="bname" style="color:{ri["clr"]}">'
            f'{m.get("sender_name","")} · {ROLES.get(m.get("sender_role",""),{"ar":""})["ar"]}</div>'
            f'{m.get("message","")}'
            f'<div class="btime">{m.get("sent_at","")}</div>'
            f'</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: INCIDENTS
# ─────────────────────────────────────────────────────────────────────────────

def pg_incident_submit():
    role = st.session_state["role"]
    hdr("🚨","بلاغ خلل أو نقص","أبلغ المدير عن أي مشكلة")
    with st.form("inc", clear_on_submit=True):
        desc = st.text_area("📝 وصف المشكلة *", placeholder="نقص حبر، عطل طابعة...")
        sev  = st.selectbox("⚠️ الخطورة", ["منخفض","متوسط","عالي"])
        sub  = st.form_submit_button("📤 إرسال", use_container_width=True)
    if sub:
        if not desc.strip(): st.error("يرجى كتابة الوصف.")
        else:
            res = sb_insert("incident_reports", {
                "workspace_id":   wid(),
                "reporter_id":    st.session_state["uid"],
                "reporter_name":  st.session_state["uname"],
                "department":     ROLES[role]["ar"],
                "description":    desc.strip(),
                "severity":       sev,
                "status":         "مفتوح",
            })
            if res: st.success("✅ تم إرسال البلاغ للمدير!")
    st.markdown("---")
    rows = sb_select("incident_reports",
                     {"workspace_id":wid(),"reporter_id":st.session_state["uid"]},
                     order="id.desc", limit=8)
    if rows:
        df = pd.DataFrame(rows)[["description","severity","status","created_at"]]
        st.dataframe(df.rename(columns={"description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


def pg_all_incidents():
    hdr("🚨","بلاغات الأعطال","جميع البلاغات الواردة")
    rows = sb_select("incident_reports",{"workspace_id":wid()}, order="id.desc")
    if not rows: st.success("🎉 لا توجد بلاغات!"); return
    op = [r for r in rows if r.get("status")=="مفتوح"]
    rs = [r for r in rows if r.get("status")=="محلول"]
    t1,t2 = st.tabs([f"🔴 مفتوحة ({len(op)})", f"✅ محلولة ({len(rs)})"])
    for tab,lst in [(t1,op),(t2,rs)]:
        with tab:
            if not lst: st.info("لا توجد."); continue
            for r in lst:
                sc,sl = SEV_BADGE.get(r.get("severity","متوسط"),("b-sev-md","🟡"))
                with st.expander(f'{sl} {r.get("severity","")}  —  {r.get("department","")}  —  {str(r.get("created_at",""))[:16]}'):
                    st.markdown(f"**المبلّغ:** {r.get('reporter_name','')}<br>**الوصف:** {r.get('description','')}", unsafe_allow_html=True)
                    if r.get("status")=="مفتوح":
                        if st.button("✅ محلول", key=f"rs_{r['id']}"):
                            sb_update("incident_reports",{"id":r["id"]},{"status":"محلول","resolved_at":now_ts()})
                            st.rerun()
                    else:
                        st.caption(f"تم الحل: {r.get('resolved_at','')}")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: FINANCIAL
# ─────────────────────────────────────────────────────────────────────────────

def pg_financial():
    hdr("💰","التقارير المالية","للمبيعات ومدير الشركة فقط")
    WID   = wid()
    rows  = sb_select("orders",{"workspace_id":WID}, order="id.desc")
    tv    = sum(float(o.get("price",0) or 0) for o in rows)
    rv    = sum(float(o.get("price",0) or 0) for o in rows if o.get("status") in ("مكتمل","تم التسليم"))
    cnt   = len(rows)
    avg   = tv/cnt if cnt else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي القيمة (د.ع)",   f"{tv:,.0f}")
    c2.metric("محصّل من مكتملة (د.ع)", f"{rv:,.0f}")
    c3.metric("قيد التنفيذ (د.ع)",      f"{tv-rv:,.0f}")
    c4.metric("متوسط الأوردر (د.ع)",   f"{avg:,.0f}")
    st.markdown("---")
    if not rows: st.info("لا توجد أوردرات."); return
    df = pd.DataFrame(rows)[["order_number","customer_name","quantity","price","status","created_at"]]
    st.dataframe(df.rename(columns={"order_number":"الأوردر","customer_name":"العميل","quantity":"الكمية",
                                    "price":"السعر (د.ع)","status":"الحالة","created_at":"التاريخ"}),
                 use_container_width=True, hide_index=True)
    ws_name = st.session_state.get("workspace_name","")
    hdr_txt = (f"Z-ORDER — تقرير مالي\nWorkspace: {ws_name}\n"
               f"Developed by: {DEVELOPER}\nتاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    st.download_button("⬇️ تصدير CSV",
        (hdr_txt+df.to_csv(index=False)).encode("utf-8-sig"),
        file_name=f"zorder_fin_{datetime.date.today()}.csv",
        mime="text/csv", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: GENERIC DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def pg_generic_dash(role):
    hdr("📊","لوحتي","نظرة عامة")
    WID   = wid()
    rows  = sb_select("orders",{"workspace_id":WID})
    today = datetime.date.today().isoformat()
    tot   = len(rows)
    nw    = sum(1 for o in rows if o.get("status")=="جديد")
    ip    = sum(1 for o in rows if o.get("production_status")=="جاري الإنتاج")
    dn    = sum(1 for o in rows if o.get("status") in ("مكتمل","تم التسليم"))
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي",tot); c2.metric("جديدة",nw); c3.metric("جاري",ip); c4.metric("مكتملة",dn)
    st.markdown("---")
    recent = sorted(rows, key=lambda x: x.get("id",0), reverse=True)[:10]
    if recent:
        df = pd.DataFrame(recent)[["order_number","customer_name","description","quantity","status","created_at"]]
        st.dataframe(df.rename(columns={"order_number":"الأوردر","customer_name":"العميل","description":"الوصف",
                                        "quantity":"الكمية","status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not gatekeeper():
        footer(); return

    role   = st.session_state["role"]
    active = top_nav()

    st.markdown('<div class="pw">', unsafe_allow_html=True)

    # ── SUPER-ADMIN ────────────────────────────────────────────────────────
    if   role == "superadmin" and active == "📊 لوحة التحكم": pg_super_dash()
    elif role == "superadmin" and active == "🏢 الشركات":      pg_super_workspaces()
    elif role == "superadmin" and active == "👥 المستخدمون":   pg_super_users()
    elif role == "superadmin" and active == "📊 الإحصائيات":   pg_super_stats()

    # ── WORKSPACE ADMIN ────────────────────────────────────────────────────
    elif role == "admin" and active == "📊 الرئيسية":  pg_admin_dash()
    elif role == "admin" and active == "👥 الفريق":    pg_team()
    elif role == "admin" and active == "📋 الأوردرات": show_orders_table("admin", title="جميع الأوردرات")
    elif role == "admin" and active == "💰 المالية":   pg_financial()
    elif role == "admin" and active == "🚨 البلاغات":  pg_all_incidents()
    elif role == "admin" and active == "🗺️ المندوبون": pg_agent_reports()
    elif role == "admin" and active == "💬 المحادثة":  pg_chat()
    elif role == "admin" and active == "📞 الدعم الفني": pg_support()

    # ── SALES ──────────────────────────────────────────────────────────────
    elif role == "sales" and active == "📊 الرئيسية":   pg_sales_dash()
    elif active == "➕ أوردر جديد":                      pg_add_order()
    elif active == "📋 أوردراتي":                        show_orders_table("sales", uid_filter=st.session_state["uid"], title="أوردراتي")
    elif active == "🖼️ معاينة التصاميم":                 pg_sales_design_preview()
    elif role == "sales" and active == "💰 تقريري":      pg_financial()

    # ── DESIGN ─────────────────────────────────────────────────────────────
    elif role == "design" and active == "📊 الرئيسية":   pg_generic_dash(role)
    elif active == "🎨 التصميم":                          pg_design()

    # ── PURCHASE ───────────────────────────────────────────────────────────
    elif role == "purchase" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "📦 طلبات الشراء":                      pg_purchase_manage()

    # ── PRODUCTION ─────────────────────────────────────────────────────────
    elif role == "production" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "🖨️ الإنتاج":                             pg_production()
    elif role == "production" and active == "📋 الأوردرات": show_orders_table("production", title="الأوردرات")

    # ── AGENT ──────────────────────────────────────────────────────────────
    elif role == "agent" and active == "📊 الرئيسية":   pg_generic_dash(role)
    elif active == "🗺️ زيارة جديدة":                   pg_agent_new()
    elif active == "📋 زياراتي":                        pg_agent_my()

    # ── SHARED ─────────────────────────────────────────────────────────────
    elif active == "📦 طلب شراء":  pg_purchase_submit()
    elif active == "🚨 بلاغ":       pg_incident_submit()
    elif active == "💬 المحادثة":   pg_chat()

    else:
        st.warning(f"الصفحة «{active}» غير متاحة.")

    st.markdown('</div>', unsafe_allow_html=True)
    footer()


if __name__ == "__main__":
    main()


# ═════════════════════════════════════════════════════════════════════════════
#  SUPABASE SQL SCHEMA  — Run ONCE in Supabase SQL Editor
#  https://iiytcythowpemjxcxfsf.supabase.co → SQL Editor → New Query
# ═════════════════════════════════════════════════════════════════════════════
"""
-- 1. workspaces
CREATE TABLE IF NOT EXISTS workspaces (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    slug       TEXT UNIQUE NOT NULL,
    plan       TEXT DEFAULT 'starter',
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. users
CREATE TABLE IF NOT EXISTS users (
    id           BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT DEFAULT 0,
    full_name    TEXT NOT NULL,
    username     TEXT NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    role         TEXT NOT NULL,
    created_by   BIGINT DEFAULT 0,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (workspace_id, username)
);

-- 3. orders
CREATE TABLE IF NOT EXISTS orders (
    id                 BIGSERIAL PRIMARY KEY,
    workspace_id       BIGINT NOT NULL,
    order_number       TEXT NOT NULL,
    customer_name      TEXT NOT NULL,
    description        TEXT NOT NULL,
    quantity           INT NOT NULL,
    price              NUMERIC NOT NULL,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    created_by_id      BIGINT,
    created_by_name    TEXT,
    status             TEXT DEFAULT 'جديد',
    design_status      TEXT DEFAULT 'قيد الانتظار',
    design_file_url    TEXT DEFAULT '',
    design_link        TEXT DEFAULT '',
    design_notes       TEXT DEFAULT '',
    design_updated     TIMESTAMPTZ,
    design_by          TEXT DEFAULT '',
    production_status  TEXT DEFAULT 'قيد الانتظار',
    production_notes   TEXT DEFAULT '',
    production_updated TIMESTAMPTZ,
    production_by      TEXT DEFAULT '',
    delivered          BOOLEAN DEFAULT FALSE,
    delivered_at       TIMESTAMPTZ,
    delivered_by       TEXT DEFAULT '',
    UNIQUE (workspace_id, order_number)
);

-- 4. purchase_requests
CREATE TABLE IF NOT EXISTS purchase_requests (
    id             BIGSERIAL PRIMARY KEY,
    workspace_id   BIGINT NOT NULL,
    requester_id   BIGINT NOT NULL,
    requester_name TEXT NOT NULL,
    department     TEXT NOT NULL,
    item_name      TEXT NOT NULL,
    quantity       TEXT NOT NULL,
    urgency        TEXT DEFAULT 'عادي',
    notes          TEXT DEFAULT '',
    status         TEXT DEFAULT 'قيد المراجعة',
    reviewed_by    TEXT DEFAULT '',
    reviewed_at    TIMESTAMPTZ,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- 5. incident_reports
CREATE TABLE IF NOT EXISTS incident_reports (
    id            BIGSERIAL PRIMARY KEY,
    workspace_id  BIGINT NOT NULL,
    reporter_id   BIGINT,
    reporter_name TEXT,
    department    TEXT,
    description   TEXT NOT NULL,
    severity      TEXT DEFAULT 'متوسط',
    status        TEXT DEFAULT 'مفتوح',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    resolved_at   TIMESTAMPTZ
);

-- 6. agent_visits
CREATE TABLE IF NOT EXISTS agent_visits (
    id            BIGSERIAL PRIMARY KEY,
    workspace_id  BIGINT NOT NULL,
    agent_id      BIGINT,
    agent_name    TEXT,
    customer_name TEXT NOT NULL,
    location      TEXT DEFAULT '',
    visit_status  TEXT DEFAULT 'محتمل',
    notes         TEXT DEFAULT '',
    image_path    TEXT DEFAULT '',
    visited_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 7. chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id           BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    sender_id    BIGINT NOT NULL,
    sender_name  TEXT NOT NULL,
    sender_role  TEXT NOT NULL,
    message      TEXT NOT NULL,
    sent_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Seed: Platform Super-Admin
INSERT INTO users (workspace_id, full_name, username, email, password, role)
VALUES (0, 'Platform Admin', 'superadmin', 'admin@zorder.iq',
        encode(sha256('Admin@2025'::bytea), 'hex'), 'superadmin')
ON CONFLICT (email) DO NOTHING;

-- 9. Disable RLS on all tables (use service role key for admin operations)
ALTER TABLE workspaces        DISABLE ROW LEVEL SECURITY;
ALTER TABLE users             DISABLE ROW LEVEL SECURITY;
ALTER TABLE orders            DISABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_requests DISABLE ROW LEVEL SECURITY;
ALTER TABLE incident_reports  DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_visits      DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages     DISABLE ROW LEVEL SECURITY;

-- 10. Storage bucket
-- Go to: Storage → New Bucket → name: "designs" → Public: ON
"""
