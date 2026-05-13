"""
╔══════════════════════════════════════════════════════════════════════════╗
║         Z-ORDER  ·  Print Workflow Platform  ·  v4.1                   ║
║         نظام إدارة المطبعة — واجهة متجاوبة                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Developer   : Abdulrahman Fallah                                       ║
║  Version     : 4.1.0  (Mobile-Safe, Collapsed Sidebar)                  ║
║  Stack       : Python 3.x · Streamlit · SQLite3                         ║
╠══════════════════════════════════════════════════════════════════════════╣
║  التشغيل:                                                               ║
║    pip install streamlit pillow                                         ║
║    streamlit run z_order_app.py                                         ║
║                                                                          ║
║  حساب المدير الافتراضي:                                                 ║
║    Email    : admin@zorder.iq                                           ║
║    Password : Admin@2025                                                ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import sqlite3
import hashlib
import datetime
import base64
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
#  initial_sidebar_state="collapsed" → الـ Sidebar مغلق افتراضياً
#  هذا يحل مشكلة الموبايل: المستخدم يفتحه بنفسه عند الحاجة
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Z-Order | نظام إدارة المطبعة",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",          # ← الإصلاح الرئيسي للموبايل
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER  = "Abdulrahman Fallah"
APP_NAME   = "Z-Order"
APP_VER    = "4.1.0"
DB_PATH    = "z_order.db"
UPLOAD_DIR = Path("z_order_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ROLES = {
    "admin":      {"label": "المدير العام",    "icon": "🛡️", "color": "#e8a020"},
    "sales":      {"label": "المبيعات",         "icon": "💼", "color": "#3b82f6"},
    "design":     {"label": "التصميم",          "icon": "🎨", "color": "#a855f7"},
    "production": {"label": "الإنتاج",          "icon": "🖨️", "color": "#ff6b35"},
    "agent":      {"label": "مندوب المبيعات",   "icon": "🗺️", "color": "#22c55e"},
}

ROLE_PAGES = {
    "admin": [
        "📊 لوحة المدير",
        "👥 إدارة الموظفين",
        "📋 جميع الأوردرات",
        "💰 التقارير المالية",
        "🗺️ تقارير المندوبين",
        "🚨 بلاغات الأعطال",
    ],
    "sales": [
        "📊 لوحتي",
        "➕ أوردر جديد",
        "📋 أوردراتي",
        "💰 تقرير المبيعات",
        "🚨 بلاغ خلل",
    ],
    "design": [
        "📊 لوحتي",
        "🎨 مهام التصميم",
        "📋 عرض الأوردرات",
        "🚨 بلاغ خلل",
    ],
    "production": [
        "📊 لوحتي",
        "🖨️ الإنتاج والطباعة",
        "📋 عرض الأوردرات",
        "🚨 بلاغ خلل",
    ],
    "agent": [
        "📊 لوحتي",
        "🗺️ تسجيل زيارة",
        "📋 زياراتي",
        "🚨 بلاغ خلل",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS — Dark Industrial · Mobile-First · No JS dependencies
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ── Tokens ───────────────────────────────────── */
:root {
  --bg0:#07080b; --bg1:#0d0f14; --bg2:#131620; --bg3:#191d2a;
  --bg4:#1f2436; --bg5:#252b40;
  --bdr:#252a3a; --bdr2:#2d3450;
  --acc:#e8a020; --acc2:#ff6b35;
  --blue:#3b82f6; --green:#22c55e; --red:#ef4444;
  --purple:#a855f7;
  --t1:#edf0f5; --t2:#8b94a8; --t3:#444c65;
  --r:10px; --r2:14px; --r3:20px;
  --shadow: 0 4px 20px rgba(0,0,0,.5);
  --shadow-lg: 0 8px 40px rgba(0,0,0,.65);
}

/* ── Base ─────────────────────────────────────── */
*, *::before, *::after { box-sizing:border-box; }

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans Arabic', sans-serif !important;
  background:  var(--bg0) !important;
  color:       var(--t1) !important;
  direction:   rtl !important;
}

/* ── Scrollbar ────────────────────────────────── */
::-webkit-scrollbar           { width:5px; height:5px; }
::-webkit-scrollbar-track     { background:var(--bg1); }
::-webkit-scrollbar-thumb     { background:var(--bg5); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:var(--acc); }

/* ── App shell ────────────────────────────────── */
.stApp { background:var(--bg0) !important; }

/* ── Sidebar ──────────────────────────────────── */
section[data-testid="stSidebar"] {
  background:  var(--bg1) !important;
  border-left: 1px solid var(--bdr) !important;
}
section[data-testid="stSidebar"] * { color:var(--t1) !important; }
section[data-testid="stSidebar"] .stRadio label {
  font-size:.88rem !important;
  padding:.35rem 0 !important;
  cursor:pointer;
}

/* ── Main content area ────────────────────────── */
.main .block-container {
  padding:    1.5rem 1.5rem 6.5rem !important;
  max-width:  1380px !important;
  width:      100% !important;
}

/* ── Inputs ───────────────────────────────────── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background:    var(--bg3) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r) !important;
  color:         var(--t1) !important;
  font-family:   'IBM Plex Sans Arabic', sans-serif !important;
  font-size:     .92rem !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
  border-color: var(--acc) !important;
  box-shadow:   0 0 0 3px rgba(232,160,32,.12) !important;
  outline:      none !important;
}

/* ── Buttons ──────────────────────────────────── */
.stButton>button {
  background:    linear-gradient(135deg,var(--acc),var(--acc2)) !important;
  color:         #07080b !important;
  font-weight:   700 !important;
  font-size:     .9rem !important;
  border:        none !important;
  border-radius: var(--r) !important;
  padding:       .6rem 1.4rem !important;
  width:         100% !important;
  min-height:    44px !important;
  font-family:   'IBM Plex Sans Arabic', sans-serif !important;
  transition:    transform .18s, box-shadow .18s !important;
  cursor:        pointer;
}
.stButton>button:hover {
  transform:  translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(232,160,32,.38) !important;
}
.stButton>button:active { transform:translateY(0) !important; }

/* ── Tabs ─────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background:    var(--bg3) !important;
  border-radius: var(--r) !important;
  gap:           3px !important;
  padding:       4px !important;
  border:        1px solid var(--bdr) !important;
  overflow-x:    auto !important;
  flex-wrap:     nowrap !important;
}
.stTabs [data-baseweb="tab"] {
  background:    transparent !important;
  color:         var(--t2) !important;
  border-radius: 7px !important;
  font-weight:   500 !important;
  font-size:     .84rem !important;
  border:        none !important;
  white-space:   nowrap !important;
}
.stTabs [aria-selected="true"] {
  background:    var(--bg5) !important;
  color:         var(--acc) !important;
  border-bottom: 2px solid var(--acc) !important;
}

/* ── Metrics ──────────────────────────────────── */
[data-testid="stMetric"] {
  background:    var(--bg2) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
  padding:       1rem 1.1rem !important;
}
[data-testid="stMetricLabel"] { color:var(--t2) !important; font-size:.75rem !important; }
[data-testid="stMetricValue"] {
  color:       var(--acc) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size:   1.35rem !important;
}

/* ── Expanders ────────────────────────────────── */
.streamlit-expanderHeader {
  background:    var(--bg2) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r) !important;
  color:         var(--t1) !important;
  font-size:     .9rem !important;
}
.streamlit-expanderContent {
  background:    var(--bg1) !important;
  border:        1px solid var(--bdr2) !important;
  border-top:    none !important;
  border-radius: 0 0 var(--r) var(--r) !important;
}

/* ── Dataframes — always full width ──────────── */
.stDataFrame,
[data-testid="stDataFrame"],
iframe[title="st.dataframe"] {
  width:        100% !important;
  max-width:    100% !important;
  border-radius: var(--r) !important;
  border:        1px solid var(--bdr) !important;
  overflow-x:    auto !important;
}

/* ── Alerts ───────────────────────────────────── */
.stAlert { background:var(--bg2) !important; border-radius:var(--r) !important; }

/* ── File uploader ────────────────────────────── */
[data-testid="stFileUploader"] {
  background:    var(--bg3) !important;
  border:        1.5px dashed var(--bdr2) !important;
  border-radius: var(--r) !important;
}

/* ── Divider ──────────────────────────────────── */
hr { border-color:var(--bdr) !important; margin:1.2rem 0 !important; }

/* ══════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════ */

.z-logo {
  font-family:    'JetBrains Mono', monospace;
  font-size:      2rem; font-weight:700;
  color:          var(--acc); letter-spacing:-.07em; line-height:1;
}
.z-logo .sep { color:var(--t3); }

/* Page header */
.ph { display:flex; align-items:center; gap:.8rem; margin-bottom:1.5rem; }
.ph-icon {
  font-size:      1.7rem; background:var(--bg2);
  border:         1px solid var(--bdr2); border-radius:var(--r);
  width:52px; height:52px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.ph h2 { font-size:1.3rem; font-weight:700; color:var(--t1); margin:0; }
.ph p  { font-size:.8rem;  color:var(--t3); margin:0; }

/* Cards */
.card {
  background:var(--bg2); border:1px solid var(--bdr2);
  border-radius:var(--r2); padding:1.15rem 1.4rem;
  margin-bottom:.8rem; transition:border-color .2s,transform .15s;
}
.card:hover { border-color:var(--acc); transform:translateY(-1px); }

/* Info card */
.info-card {
  background:linear-gradient(135deg,rgba(232,160,32,.07),rgba(255,107,53,.04));
  border:1px solid rgba(232,160,32,.2); border-right:3px solid var(--acc);
  border-radius:var(--r2); padding:1rem 1.3rem;
  margin-bottom:1rem; font-size:.85rem; color:var(--t2); line-height:1.9;
}

/* Badges */
.badge {
  display:inline-flex; align-items:center; gap:4px;
  padding:.2rem .65rem; border-radius:999px;
  font-size:.68rem; font-weight:700;
  letter-spacing:.04em; text-transform:uppercase;
}
.b-new      {background:rgba(59,130,246,.14); color:#60a5fa; border:1px solid rgba(59,130,246,.25);}
.b-design   {background:rgba(168,85,247,.14); color:#c084fc; border:1px solid rgba(168,85,247,.25);}
.b-purchase {background:rgba(232,160,32,.14); color:#fbbf24; border:1px solid rgba(232,160,32,.25);}
.b-ready    {background:rgba(34,197,94,.14);  color:#4ade80; border:1px solid rgba(34,197,94,.25);}
.b-print    {background:rgba(255,107,53,.14); color:#fb923c; border:1px solid rgba(255,107,53,.25);}
.b-done     {background:rgba(34,197,94,.1);   color:#16a34a; border:1px solid rgba(34,197,94,.2);}
.b-abuy     {background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2);}
.b-apot     {background:rgba(59,130,246,.12); color:#3b82f6; border:1px solid rgba(59,130,246,.2);}
.b-ano      {background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2);}
.b-sev-lo   {background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2);}
.b-sev-md   {background:rgba(251,191,36,.12); color:#fbbf24; border:1px solid rgba(251,191,36,.2);}
.b-sev-hi   {background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2);}

/* User chip */
.uchip {
  display:flex; align-items:center; gap:.65rem;
  background:var(--bg3); border:1px solid var(--bdr2);
  border-radius:var(--r2); padding:.6rem .9rem; margin-bottom:1rem;
}
.uavatar {
  width:34px; height:34px;
  background:linear-gradient(135deg,var(--acc),var(--acc2));
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:.82rem; font-weight:700; color:#07080b; flex-shrink:0;
}

/* Section label */
.sec-title {
  font-size:.72rem; font-weight:700; color:var(--t3);
  text-transform:uppercase; letter-spacing:.1em; margin:1.2rem 0 .6rem;
}

/* Footer — fixed at bottom */
.footer {
  position:fixed; bottom:0; left:0; right:0;
  background:var(--bg1); border-top:1px solid var(--bdr);
  padding:.55rem 1.5rem;
  display:flex; align-items:center; justify-content:space-between;
  font-size:.7rem; color:var(--t3); z-index:9999;
  gap:.5rem; flex-wrap:wrap;
}
.footer .hi { color:var(--acc); font-weight:600; }

/* ══════════════════════════════════════════════
   MOBILE  ≤ 768px
   الـ Sidebar يكون مطوياً بالإعداد الافتراضي.
   هنا نضمن أن المحتوى ملائم لعرض الشاشة.
═══════════════════════════════════════════════ */
@media (max-width: 768px) {

  /* محتوى كامل العرض */
  .main .block-container {
    padding:    .75rem .55rem 7rem !important;
    max-width:  100% !important;
    margin:     0 !important;
  }

  /* Metrics */
  [data-testid="stMetricValue"] { font-size:1rem !important; }
  [data-testid="stMetric"]      { padding:.65rem .75rem !important; }

  /* Page header */
  .ph-icon { width:34px; height:34px; font-size:1.1rem; }
  .ph h2   { font-size:1rem; }
  .ph p    { font-size:.72rem; }

  /* Cards */
  .card { padding:.8rem .9rem; }

  /* الأعمدة تتكدس رأسياً */
  [data-testid="column"] {
    width:     100% !important;
    flex:      0 0 100% !important;
    min-width: 100% !important;
    padding:   0 !important;
  }

  /* Buttons — سهل للمس */
  .stButton>button {
    font-size:  .86rem !important;
    padding:    .65rem .9rem !important;
    min-height: 48px !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] { font-size:.72rem !important; padding:.3rem .45rem !important; }

  /* Inputs */
  .stTextInput>div>div>input,
  .stTextArea>div>div>textarea,
  .stSelectbox>div>div { font-size:.86rem !important; }

  /* Footer */
  .footer { font-size:.62rem; padding:.4rem .6rem; }

  /* جداول كاملة العرض مع تمرير أفقي */
  .stDataFrame,
  [data-testid="stDataFrame"],
  iframe[title="st.dataframe"] {
    width:      100% !important;
    overflow-x: auto !important;
    font-size:  .8rem !important;
  }

  /* Expanders */
  .streamlit-expanderHeader { font-size:.82rem !important; }

  /* Badges أصغر قليلاً */
  .badge { font-size:.62rem !important; }
}

/* ══════════════════════════════════════════════
   DESKTOP  ≥ 769px
═══════════════════════════════════════════════ */
@media (min-width: 769px) {
  .stDataFrame,
  [data-testid="stDataFrame"],
  iframe[title="st.dataframe"] { width:100% !important; }
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DATABASE LAYER
# ─────────────────────────────────────────────────────────────────────────────

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def qall(sql, p=()):
    conn = _conn(); rows = conn.execute(sql, p).fetchall(); conn.close()
    return [dict(r) for r in rows]

def qone(sql, p=()):
    conn = _conn(); row = conn.execute(sql, p).fetchone(); conn.close()
    return dict(row) if row else None

def qrun(sql, p=()):
    conn = _conn(); cur = conn.execute(sql, p); conn.commit()
    lid = cur.lastrowid; conn.close(); return lid


def init_db():
    conn = _conn(); c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'print_shop',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name  TEXT    NOT NULL,
        username   TEXT    UNIQUE NOT NULL,
        email      TEXT    UNIQUE NOT NULL,
        password   TEXT    NOT NULL,
        role       TEXT    NOT NULL,
        company_id INTEGER DEFAULT 1,
        is_active  INTEGER DEFAULT 1,
        created_at TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number       TEXT    UNIQUE NOT NULL,
        customer_name      TEXT    NOT NULL,
        description        TEXT    NOT NULL,
        quantity           INTEGER NOT NULL,
        price              REAL    NOT NULL,
        company_id         INTEGER DEFAULT 1,
        created_at         TEXT    DEFAULT (datetime('now','localtime')),
        created_by_id      INTEGER,
        created_by_name    TEXT,
        status             TEXT    DEFAULT 'New',
        design_status      TEXT    DEFAULT 'Pending',
        design_link        TEXT    DEFAULT '',
        design_file_path   TEXT    DEFAULT '',
        design_notes       TEXT    DEFAULT '',
        design_updated     TEXT    DEFAULT '',
        design_by          TEXT    DEFAULT '',
        purchase_status    TEXT    DEFAULT 'Pending',
        purchase_notes     TEXT    DEFAULT '',
        purchase_updated   TEXT    DEFAULT '',
        production_status  TEXT    DEFAULT 'Pending',
        production_notes   TEXT    DEFAULT '',
        production_updated TEXT    DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS agent_visits (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id      INTEGER,
        agent_name    TEXT,
        customer_name TEXT    NOT NULL,
        location_text TEXT    DEFAULT '',
        lat           REAL    DEFAULT 0,
        lng           REAL    DEFAULT 0,
        status        TEXT    DEFAULT 'potential',
        notes         TEXT    DEFAULT '',
        image_path    TEXT    DEFAULT '',
        visited_at    TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS incident_reports (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_id   INTEGER,
        reporter_name TEXT,
        department    TEXT,
        description   TEXT NOT NULL,
        severity      TEXT DEFAULT 'medium',
        status        TEXT DEFAULT 'open',
        created_at    TEXT DEFAULT (datetime('now','localtime')),
        resolved_at   TEXT DEFAULT ''
    )""")

    c.execute("INSERT OR IGNORE INTO companies (id,name) VALUES (1,'Z-Order Print Shop')")
    try:
        c.execute(
            "INSERT INTO users (full_name,username,email,password,role,company_id) VALUES (?,?,?,?,?,?)",
            ("المدير العام", "admin", "admin@zorder.iq", _hash("Admin@2025"), "admin", 1),
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit(); conn.close()


def new_order_no() -> str:
    row = qone("SELECT COUNT(*) c FROM orders")
    n   = row["c"] if row else 0
    return f"ZO-{datetime.date.today().strftime('%y%m%d')}-{n+1:04d}"


def refresh_order_status(oid: int):
    o = qone("SELECT design_status,purchase_status,production_status FROM orders WHERE id=?", (oid,))
    if not o: return
    ds, ps, prs = o["design_status"], o["purchase_status"], o["production_status"]
    if   prs == "Done":                   s = "Completed"
    elif prs == "Printing":              s = "In Production"
    elif ds == "Done" and ps == "Ready": s = "Ready for Production"
    elif ds == "Done":                   s = "Design Done"
    elif ps == "Ready":                  s = "Materials Ready"
    else:                                s = "New"
    qrun("UPDATE orders SET status=? WHERE id=?", (s, oid))


# ─────────────────────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

STATUS_BADGES = {
    "New":                  ("b-new",     "🔵 جديد"),
    "Design Done":          ("b-design",  "🟣 تصميم جاهز"),
    "Materials Ready":      ("b-purchase","🟡 مواد جاهزة"),
    "Ready for Production": ("b-ready",   "🟢 جاهز للإنتاج"),
    "In Production":        ("b-print",   "🟠 تحت الطباعة"),
    "Completed":            ("b-done",    "✅ مكتمل"),
}
AGENT_BADGES = {
    "bought":    ("b-abuy", "✅ اشترى"),
    "potential": ("b-apot", "🔵 محتمل"),
    "no":        ("b-ano",  "❌ لن يشتري"),
}
SEV_BADGES = {
    "low":    ("b-sev-lo", "🟢 منخفض"),
    "medium": ("b-sev-md", "🟡 متوسط"),
    "high":   ("b-sev-hi", "🔴 عالي"),
}

def mk_badge(key, table=None):
    t = table or STATUS_BADGES
    cls, lbl = t.get(key, ("b-new", key))
    return f'<span class="badge {cls}">{lbl}</span>'

def page_hdr(icon, title, sub=""):
    st.markdown(
        f'<div class="ph"><div class="ph-icon">{icon}</div>'
        f'<div><h2>{title}</h2><p>{sub}</p></div></div>',
        unsafe_allow_html=True,
    )

GUIDES = {
    "admin": (
        "📌 <b>صلاحياتك كمدير عام:</b><br>"
        "① أنت الوحيد الذي يضيف موظفين جدد ويتحكم بصلاحياتهم<br>"
        "② راقب إحصائيات النظام والبلاغات وأداء المندوبين<br>"
        "③ لديك وصول كامل للأوردرات والتقارير المالية"
    ),
    "sales": (
        "📌 <b>مهامك كقسم مبيعات:</b><br>"
        "① أضف أوردراً جديداً بتفاصيل العميل والكمية والسعر<br>"
        "② تابع حالة أوردراتك من «أوردراتي»<br>"
        "③ السعر والتقارير المالية سرية ولا تظهر للأقسام الأخرى"
    ),
    "design": (
        "📌 <b>مهامك كقسم تصميم:</b><br>"
        "① راجع الأوردرات الواردة وارفع ملف التصميم أو رابطه<br>"
        "② عدّل الحالة إلى Done — الإنتاج لن يبدأ إلا بعد التصميم والمشتريات"
    ),
    "production": (
        "📌 <b>مهامك كقسم إنتاج:</b><br>"
        "① الأوردرات الجاهزة = تصميم ✅ + مشتريات ✅<br>"
        "② حمّل ملف التصميم وابدأ الطباعة<br>"
        "③ عند الانتهاء غيّر الحالة إلى Done"
    ),
    "agent": (
        "📌 <b>مهامك كمندوب مبيعات:</b><br>"
        "① سجّل زيارتك مع صورة المحل وموقعه الجغرافي<br>"
        "② حدّد حالة العميل: اشترى / محتمل / لن يشتري<br>"
        "③ المدير يتابع أداءك من لوحته"
    ),
}

def guide(role_key: str):
    txt = GUIDES.get(role_key, "")
    if txt:
        with st.expander("💡 كيف يعمل هذا القسم؟", expanded=False):
            st.markdown(f'<div class="info-card">{txt}</div>', unsafe_allow_html=True)

def footer_bar():
    yr = datetime.date.today().year
    st.markdown(
        f'<div class="footer">'
        f'<span>🖨️ <span class="hi">{APP_NAME}</span> &nbsp;v{APP_VER}</span>'
        f'<span>Developed by <span class="hi">{DEVELOPER}</span></span>'
        f'<span>© {yr} All rights reserved</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def save_file(uploaded, sub="designs") -> str:
    if not uploaded: return ""
    d = UPLOAD_DIR / sub; d.mkdir(exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe = "".join(ch for ch in uploaded.name if ch.isalnum() or ch in "._-")
    p    = d / f"{ts}_{safe}"; p.write_bytes(uploaded.read()); return str(p)

def dl_button(fpath: str, label="⬇️ تحميل الملف"):
    p = Path(fpath)
    if p.exists():
        st.download_button(label, p.read_bytes(), file_name=p.name, use_container_width=True)
    else:
        st.caption("⚠️ الملف غير متوفر")

def orders_table(role, uid_filter=None):
    """Full-width filterable orders table."""
    hide_price = role not in ("admin", "sales")
    sql  = "SELECT * FROM orders" + (" WHERE created_by_id=?" if uid_filter else "") + " ORDER BY id DESC"
    rows = qall(sql, (uid_filter,) if uid_filter else ())
    if not rows:
        st.info("لا توجد أوردرات بعد."); return

    statuses = ["الكل"] + sorted({r["status"] for r in rows})
    sel = st.selectbox("📌 فلتر الحالة", statuses, key=f"flt_{role}_{uid_filter}")
    if sel != "الكل":
        rows = [r for r in rows if r["status"] == sel]

    cols = ["order_number","customer_name","description","quantity",
            "status","design_status","purchase_status","production_status","created_at"]
    if not hide_price: cols.insert(4, "price")

    labels = {
        "order_number":"رقم الأوردر","customer_name":"العميل","description":"الوصف",
        "quantity":"الكمية","price":"السعر (د.ع)","status":"الحالة",
        "design_status":"التصميم","purchase_status":"المشتريات",
        "production_status":"الإنتاج","created_at":"التاريخ",
    }
    df = pd.DataFrame(rows)
    ok = [c for c in cols if c in df.columns]
    # use_container_width=True → يمتد الجدول لكامل عرض الشاشة دائماً
    st.dataframe(df[ok].rename(columns=labels), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  GATEKEEPER  — strict login screen, blocks all content until auth
# ─────────────────────────────────────────────────────────────────────────────

def gatekeeper() -> bool:
    if st.session_state.get("authenticated"):
        return True

    # Hide sidebar on login screen
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none!important}</style>",
        unsafe_allow_html=True,
    )

    col = st.columns([1, 1.5, 1])[1]
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;margin-bottom:1.75rem">'
            f'<div class="z-logo">Z<span class="sep">-</span>Order</div>'
            f'<div style="color:var(--t3);font-size:.8rem;margin-top:.4rem">'
            f'Print Workflow Platform &nbsp;·&nbsp; v{APP_VER}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown(
                '<div style="background:var(--bg2);border:1px solid var(--bdr2);'
                'border-radius:var(--r2);padding:2rem 1.75rem;">',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="sec-title" style="text-align:center;margin-top:0">'
                'تسجيل الدخول</div>',
                unsafe_allow_html=True,
            )
            ident = st.text_input(
                "📧 الإيميل أو اسم المستخدم",
                placeholder="admin@zorder.iq  أو  admin",
                key="gk_id",
            )
            pw = st.text_input("🔒 كلمة المرور", type="password", placeholder="••••••••", key="gk_pw")
            clicked = st.button("دخول ←", key="gk_btn")
            st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            if not ident or not pw:
                st.error("يرجى إدخال بيانات الدخول.")
                return False
            i = ident.strip().lower()
            user = qone(
                "SELECT * FROM users WHERE (lower(email)=? OR lower(username)=?) AND password=? AND is_active=1",
                (i, i, _hash(pw)),
            )
            if user:
                st.session_state.update({
                    "authenticated": True,
                    "uid":        user["id"],
                    "uname":      user["full_name"],
                    "username":   user["username"],
                    "email":      user["email"],
                    "role":       user["role"],
                    "company_id": user["company_id"],
                })
                st.rerun()
            else:
                st.error("❌ بيانات غير صحيحة أو الحساب موقوف.")

        st.markdown(
            f'<div style="text-align:center;margin-top:1.5rem;color:var(--t3);font-size:.68rem">'
            f'Developed by <b style="color:var(--acc)">{DEVELOPER}</b></div>',
            unsafe_allow_html=True,
        )
    return False


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR NAV  — st.sidebar.radio (works on both desktop & mobile)
#  On mobile: sidebar is collapsed by default (set_page_config).
#             User taps the ☰ arrow to open it — native Streamlit UX.
# ─────────────────────────────────────────────────────────────────────────────

def build_nav() -> str:
    role  = st.session_state["role"]
    uname = st.session_state["uname"]
    rinfo = ROLES.get(role, {"label": role, "icon": "👤", "color": "#e8a020"})
    initials = "".join(w[0] for w in uname.split()[:2]).upper() or "?"

    # ── Logo ──
    st.sidebar.markdown(
        f'<div style="padding:.4rem 0 .3rem">'
        f'<div class="z-logo">Z<span class="sep">-</span>Order</div>'
        f'<div style="color:var(--t3);font-size:.7rem;margin-top:2px">Print Workflow Platform</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── User chip ──
    st.sidebar.markdown(
        f'<div class="uchip">'
        f'<div class="uavatar">{initials}</div>'
        f'<div>'
        f'<div style="font-size:.84rem;font-weight:600;line-height:1.2">{uname}</div>'
        f'<div style="font-size:.69rem;color:{rinfo["color"]};margin-top:1px">'
        f'{rinfo["icon"]} {rinfo["label"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Navigation radio ──
    pages  = ROLE_PAGES.get(role, [])
    active = st.sidebar.radio("", pages, label_visibility="collapsed")

    st.sidebar.markdown("---")

    # ── Developer credit ──
    st.sidebar.markdown(
        f'<div style="font-size:.66rem;color:var(--t3);text-align:center;line-height:1.9">'
        f'Developed by<br><b style="color:var(--acc)">{DEVELOPER}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Logout ──
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪  تسجيل الخروج"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    return active


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────

# ── Admin: Dashboard ──────────────────────────────────────────────────────────
def pg_admin_dash():
    page_hdr("🛡️", "لوحة المدير العام", "إحصائيات حية وإدارة شاملة")
    guide("admin")

    today   = datetime.date.today().isoformat()
    total   = (qone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    today_o = (qone("SELECT COUNT(*) c FROM orders WHERE created_at LIKE ?", (f"{today}%",)) or {}).get("c", 0)
    done    = (qone("SELECT COUNT(*) c FROM orders WHERE production_status='Done'") or {}).get("c", 0)
    rev     = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE production_status='Done'") or {}).get("s", 0)
    total_v = (qone("SELECT COALESCE(SUM(price),0) s FROM orders") or {}).get("s", 0)
    open_r  = (qone("SELECT COUNT(*) c FROM incident_reports WHERE status='open'") or {}).get("c", 0)
    agents  = (qone("SELECT COUNT(DISTINCT agent_id) c FROM agent_visits WHERE visited_at LIKE ?", (f"{today}%",)) or {}).get("c", 0)
    users   = (qone("SELECT COUNT(*) c FROM users WHERE is_active=1") or {}).get("c", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("أوردرات اليوم",          today_o)
    c2.metric("مكتملة / الإجمالي",      f"{done}/{total}")
    c3.metric("إيراد المكتمل (د.ع)",    f"{rev:,.0f}")
    c4.metric("بلاغات مفتوحة",          open_r)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("إجمالي القيمة (د.ع)",    f"{total_v:,.0f}")
    c6.metric("قيد التنفيذ (د.ع)",      f"{total_v - rev:,.0f}")
    c7.metric("مندوبون نشطون اليوم",    agents)
    c8.metric("موظفون نشطون",           users)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 آخر الأوردرات", "🗺️ أداء المندوبين", "🚨 البلاغات"])

    with tab1:
        rows = qall("SELECT order_number,customer_name,quantity,price,status,created_at FROM orders ORDER BY id DESC LIMIT 15")
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "order_number":"الأوردر","customer_name":"العميل",
                "quantity":"الكمية","price":"السعر","status":"الحالة","created_at":"التاريخ"
            }), use_container_width=True, hide_index=True)
        else: st.info("لا توجد أوردرات.")

    with tab2:
        rows = qall("""SELECT agent_name,COUNT(*) visits,
               SUM(CASE WHEN status='bought' THEN 1 ELSE 0 END) bought,
               SUM(CASE WHEN status='potential' THEN 1 ELSE 0 END) potential,
               SUM(CASE WHEN status='no' THEN 1 ELSE 0 END) lost
            FROM agent_visits GROUP BY agent_id ORDER BY visits DESC""")
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "agent_name":"المندوب","visits":"الزيارات",
                "bought":"اشترى","potential":"محتمل","lost":"لن يشتري"
            }), use_container_width=True, hide_index=True)
        else: st.info("لا توجد زيارات.")

    with tab3:
        rows = qall("SELECT reporter_name,department,description,severity,status,created_at FROM incident_reports ORDER BY id DESC LIMIT 10")
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "reporter_name":"المبلّغ","department":"القسم",
                "description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"
            }), use_container_width=True, hide_index=True)
        else: st.success("🎉 لا توجد بلاغات!")


# ── Admin: Employee Management ────────────────────────────────────────────────
def pg_employees():
    page_hdr("👥", "إدارة الموظفين", "أضف أعضاء الفريق وتحكم بصلاحياتهم")
    guide("admin")

    st.markdown('<div class="sec-title">الفريق الحالي</div>', unsafe_allow_html=True)
    rows = qall("SELECT id,full_name,username,email,role,is_active,created_at FROM users ORDER BY id")
    if rows:
        df = pd.DataFrame(rows)
        df["is_active"] = df["is_active"].map({1: "✅ نشط", 0: "🚫 موقوف"})
        st.dataframe(df.rename(columns={
            "id":"#","full_name":"الاسم","username":"المستخدم",
            "email":"الإيميل","role":"القسم","is_active":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sec-title">➕ إضافة موظف جديد</div>', unsafe_allow_html=True)

    with st.form("add_emp", clear_on_submit=True):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("الاسم الكامل *", placeholder="محمد أحمد")
        username  = c2.text_input("اسم المستخدم *", placeholder="mohammed_a")
        c3, c4 = st.columns(2)
        email = c3.text_input("الإيميل *", placeholder="m@company.com")
        dept  = c4.selectbox("القسم *",
            ["sales","design","production","agent"],
            format_func=lambda r: f"{ROLES[r]['icon']}  {ROLES[r]['label']}")
        c5, c6 = st.columns(2)
        pw1 = c5.text_input("كلمة المرور *", type="password")
        pw2 = c6.text_input("تأكيد كلمة المرور *", type="password")
        sub = st.form_submit_button("✅ إضافة الموظف", use_container_width=True)

    if sub:
        errs = []
        if not all([full_name, username, email, pw1]): errs.append("يرجى تعبئة جميع الحقول.")
        if pw1 and pw2 and pw1 != pw2: errs.append("كلمتا المرور غير متطابقتين.")
        if pw1 and len(pw1) < 6: errs.append("كلمة المرور 6 أحرف على الأقل.")
        for e in errs: st.error(e)
        if not errs:
            try:
                qrun("INSERT INTO users (full_name,username,email,password,role) VALUES (?,?,?,?,?)",
                     (full_name.strip(), username.strip().lower(), email.strip().lower(), _hash(pw1), dept))
                st.success(f"✅ تم إضافة **{full_name}** — يدخل بـ «{username.strip().lower()}» أو إيميله.")
                st.rerun()
            except sqlite3.IntegrityError as ex:
                st.error("❌ اسم المستخدم أو الإيميل مستخدم بالفعل." if "UNIQUE" in str(ex).upper() else f"❌ {ex}")

    st.markdown("---")
    st.markdown('<div class="sec-title">🔄 تفعيل / تعطيل موظف</div>', unsafe_allow_html=True)
    all_u = qall("SELECT id,full_name,username,is_active FROM users WHERE role!='admin' ORDER BY id")
    if all_u:
        opts  = {f"{u['id']} — {u['full_name']} ({u['username']})": u["id"] for u in all_u}
        label = st.selectbox("اختر الموظف", list(opts.keys()))
        uid_t = opts[label]
        col1, col2, _ = st.columns([1,1,2])
        if col1.button("✅ تفعيل",  key="act_btn"):   qrun("UPDATE users SET is_active=1 WHERE id=?", (uid_t,)); st.rerun()
        if col2.button("🚫 تعطيل", key="deact_btn"): qrun("UPDATE users SET is_active=0 WHERE id=?", (uid_t,)); st.rerun()
    else:
        st.info("لا يوجد موظفون مضافون بعد.")


# ── Sales: Dashboard ──────────────────────────────────────────────────────────
def pg_sales_dash():
    page_hdr("📊", "لوحتي", "نظرة سريعة على أوردراتك")
    guide("sales")
    uid    = st.session_state["uid"]
    total  = (qone("SELECT COUNT(*) c FROM orders WHERE created_by_id=?", (uid,)) or {}).get("c", 0)
    done   = (qone("SELECT COUNT(*) c FROM orders WHERE created_by_id=? AND production_status='Done'", (uid,)) or {}).get("c", 0)
    rev    = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE created_by_id=? AND production_status='Done'", (uid,)) or {}).get("s", 0)
    new_   = (qone("SELECT COUNT(*) c FROM orders WHERE created_by_id=? AND status='New'", (uid,)) or {}).get("c", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي أوردراتي", total)
    c2.metric("مكتملة",          done)
    c3.metric("إيراداتي (د.ع)",  f"{rev:,.0f}")
    c4.metric("جديدة",           new_)
    st.markdown("---")
    orders_table("sales", uid_filter=uid)


# ── Sales: Add Order ──────────────────────────────────────────────────────────
def pg_add_order():
    page_hdr("➕", "أوردر جديد", "أدخل تفاصيل طلب العميل")
    guide("sales")
    with st.form("new_order", clear_on_submit=True):
        c1, c2 = st.columns(2)
        customer    = c1.text_input("👤 اسم العميل *")
        quantity    = c2.number_input("📦 الكمية *", min_value=1, value=1)
        description = st.text_area("📝 وصف الطلب *", placeholder="تفاصيل الطباعة: المقاس، الورق...")
        c3, _ = st.columns(2)
        price = c3.number_input("💰 السعر (د.ع) *", min_value=0.0, step=500.0)
        sub   = st.form_submit_button("✅ حفظ الأوردر", use_container_width=True)
    if sub:
        if not customer.strip() or not description.strip() or price <= 0:
            st.error("يرجى تعبئة جميع الحقول — السعر يجب أن يكون أكبر من صفر.")
        else:
            ono = new_order_no()
            qrun("INSERT INTO orders (order_number,customer_name,description,quantity,price,created_by_id,created_by_name) VALUES (?,?,?,?,?,?,?)",
                 (ono, customer.strip(), description.strip(), quantity, price,
                  st.session_state["uid"], st.session_state["uname"]))
            st.success(f"✅ تم حفظ الأوردر **{ono}** بنجاح!")


# ── Design: Tasks ─────────────────────────────────────────────────────────────
def pg_design():
    page_hdr("🎨", "مهام التصميم", "راجع الأوردرات وارفع ملفات التصميم")
    guide("design")
    rows    = qall("SELECT * FROM orders ORDER BY id DESC")
    pending = [r for r in rows if r["design_status"] == "Pending"]
    done    = [r for r in rows if r["design_status"] == "Done"]

    tab1, tab2 = st.tabs([f"⏳ قيد الانتظار ({len(pending)})", f"✅ مكتملة ({len(done)})"])

    with tab1:
        if not pending: st.success("🎉 لا توجد مهام تصميم معلقة!")
        for r in pending:
            with st.expander(f"🔷 {r['order_number']}  —  {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**التاريخ:** {r['created_at']}")
                c2.markdown(f"**أضافه:** {r['created_by_name']}")
                st.markdown("---")
                dl    = st.text_input("🔗 رابط التصميم", value=r["design_link"] or "", key=f"dl_{r['id']}")
                upld  = st.file_uploader("📎 رفع ملف التصميم", key=f"du_{r['id']}",
                                          type=["pdf","png","jpg","jpeg","ai","psd","svg","eps","zip"])
                notes = st.text_area("📝 ملاحظات", value=r["design_notes"] or "", key=f"dn_{r['id']}", height=70)
                if st.button("✅ تحديث → Design Done", key=f"d_done_{r['id']}"):
                    fp = save_file(upld, "designs") if upld else (r["design_file_path"] or "")
                    if not dl.strip() and not fp:
                        st.error("يرجى رفع ملف أو إدخال رابط التصميم.")
                    else:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        qrun("UPDATE orders SET design_status='Done',design_link=?,design_file_path=?,design_notes=?,design_updated=?,design_by=? WHERE id=?",
                             (dl.strip(), fp, notes.strip(), now, st.session_state["uname"], r["id"]))
                        refresh_order_status(r["id"])
                        st.success("✅ تم تحديث التصميم!"); st.rerun()

    with tab2:
        if not done: st.info("لا توجد تصاميم مكتملة بعد.")
        for r in done:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{mk_badge("Design Done")}'
                f'<br><small style="color:var(--t3)">🔗 {r["design_link"] or "—"} | 🗓 {r["design_updated"]}</small></div>',
                unsafe_allow_html=True)
            if r.get("design_file_path"): dl_button(r["design_file_path"], "⬇️ تحميل ملف التصميم")


# ── Production: Tasks ─────────────────────────────────────────────────────────
def pg_production():
    page_hdr("🖨️", "الإنتاج والطباعة", "فقط الأوردرات الجاهزة (تصميم ✅ + مشتريات ✅)")
    guide("production")
    rows      = qall("SELECT * FROM orders ORDER BY id DESC")
    available = [r for r in rows if r["design_status"]=="Done" and r["purchase_status"]=="Ready" and r["production_status"]!="Done"]
    printing  = [r for r in rows if r["production_status"]=="Printing"]
    completed = [r for r in rows if r["production_status"]=="Done"]
    with_file = [r for r in rows if r.get("design_file_path")]

    tab1, tab2, tab3, tab4 = st.tabs([
        f"🟢 جاهز ({len(available)})",
        f"🟠 طباعة ({len(printing)})",
        f"✅ مكتمل ({len(completed)})",
        f"📁 الملفات ({len(with_file)})",
    ])

    with tab1:
        if not available: st.info("⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم والمشتريات.")
        for r in available:
            with st.expander(f"🟢 {r['order_number']}  —  {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**رابط التصميم:** {r['design_link'] or '—'}")
                if r.get("design_file_path"): dl_button(r["design_file_path"], "⬇️ تحميل ملف التصميم")
                notes = st.text_area("📝 ملاحظات الإنتاج", key=f"pn_{r['id']}", height=60)
                col1, col2 = st.columns(2)
                if col1.button("▶️ بدء الطباعة", key=f"start_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    qrun("UPDATE orders SET production_status='Printing',production_notes=?,production_updated=? WHERE id=?", (notes, now, r["id"]))
                    refresh_order_status(r["id"]); st.success("▶️ بدأت الطباعة!"); st.rerun()
                if col2.button("✅ إتمام مباشر", key=f"fin2_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    qrun("UPDATE orders SET production_status='Done',production_notes=?,production_updated=? WHERE id=?", (notes, now, r["id"]))
                    refresh_order_status(r["id"]); st.success("✅ اكتمل!"); st.rerun()

    with tab2:
        if not printing: st.info("لا توجد طباعة جارية.")
        for r in printing:
            with st.expander(f"🟠 {r['order_number']}  —  {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c2.markdown(f"**الكمية:** {r['quantity']}")
                if r.get("design_file_path"): dl_button(r["design_file_path"])
                if st.button("✅ تحديد كـ مكتمل", key=f"fin_{r['id']}"):
                    qrun("UPDATE orders SET production_status='Done',production_updated=? WHERE id=?",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                    refresh_order_status(r["id"]); st.success("✅ اكتمل!"); st.rerun()

    with tab3:
        if not completed: st.info("لا توجد أوردرات مكتملة.")
        for r in completed:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{mk_badge("Completed")}'
                f'<br><small style="color:var(--t3)">اكتمل: {r["production_updated"]}</small></div>',
                unsafe_allow_html=True)

    with tab4:
        if not with_file: st.info("لا توجد ملفات مرفوعة.")
        for r in with_file:
            c1, c2 = st.columns([3,1])
            c1.markdown(f"**{r['order_number']}** — {r['customer_name']}")
            with c2: dl_button(r["design_file_path"], "⬇️")


# ── Agent: Register Visit ─────────────────────────────────────────────────────
def pg_agent_visit():
    page_hdr("🗺️", "تسجيل زيارة عميل", "وثّق زيارتك الميدانية")
    guide("agent")
    with st.form("visit_form", clear_on_submit=True):
        customer = st.text_input("👤 اسم العميل / المحل *")
        location = st.text_input("📍 العنوان", placeholder="مثال: شارع المتنبي، بغداد")
        c1, c2 = st.columns(2)
        lat = c1.number_input("خط العرض (Lat)", value=33.3406, format="%.6f")
        lng = c2.number_input("خط الطول (Lng)", value=44.4009, format="%.6f")
        vs  = st.selectbox("📊 حالة العميل", ["potential","bought","no"],
                            format_func=lambda s: {"bought":"✅ اشترى","potential":"🔵 محتمل","no":"❌ لن يشتري"}[s])
        notes = st.text_area("📝 ملاحظات الزيارة", height=80)
        image = st.file_uploader("📸 صورة المحل (اختياري)", type=["jpg","jpeg","png","webp"])
        sub   = st.form_submit_button("✅ حفظ الزيارة", use_container_width=True)
    if sub:
        if not customer.strip(): st.error("يرجى إدخال اسم العميل.")
        else:
            ip = save_file(image, "agent_imgs") if image else ""
            qrun("INSERT INTO agent_visits (agent_id,agent_name,customer_name,location_text,lat,lng,status,notes,image_path) VALUES (?,?,?,?,?,?,?,?,?)",
                 (st.session_state["uid"], st.session_state["uname"],
                  customer.strip(), location.strip(), lat, lng, vs, notes.strip(), ip))
            st.success(f"✅ تم تسجيل الزيارة للعميل **{customer.strip()}**!")


# ── Agent: My Visits ──────────────────────────────────────────────────────────
def pg_agent_my_visits():
    page_hdr("📋", "زياراتي", "سجل زياراتك الميدانية")
    uid  = st.session_state["uid"]
    rows = qall("SELECT * FROM agent_visits WHERE agent_id=? ORDER BY id DESC", (uid,))
    if not rows: st.info("لم تسجّل أي زيارة بعد."); return
    for r in rows:
        cls, lbl = AGENT_BADGES.get(r["status"], ("b-apot", r["status"]))
        img_html = ""
        if r.get("image_path") and Path(r["image_path"]).exists():
            raw = Path(r["image_path"]).read_bytes()
            b64 = base64.b64encode(raw).decode()
            ext = Path(r["image_path"]).suffix.lstrip(".") or "jpeg"
            img_html = (f'<br><img src="data:image/{ext};base64,{b64}" '
                        f'style="max-width:100%;max-height:180px;border-radius:8px;margin-top:.5rem;object-fit:cover">')
        st.markdown(
            f'<div class="card"><b>{r["customer_name"]}</b>&nbsp;<span class="badge {cls}">{lbl}</span>'
            f'<br><small style="color:var(--t2)">📍 {r["location_text"] or "—"}&nbsp;|&nbsp;🗓 {r["visited_at"]}</small>'
            f'{"<br><small style=color:var(--t2)>"+r["notes"]+"</small>" if r["notes"] else ""}'
            f'{img_html}</div>', unsafe_allow_html=True)


# ── Agent Reports (admin) ─────────────────────────────────────────────────────
def pg_agent_reports():
    page_hdr("🗺️", "تقارير المندوبين", "أداء فريق المبيعات الميداني")
    rows = qall("""SELECT agent_name,COUNT(*) visits,
               SUM(CASE WHEN status='bought' THEN 1 ELSE 0 END) bought,
               SUM(CASE WHEN status='potential' THEN 1 ELSE 0 END) potential,
               SUM(CASE WHEN status='no' THEN 1 ELSE 0 END) lost,
               MAX(visited_at) last_visit
            FROM agent_visits GROUP BY agent_id ORDER BY visits DESC""")
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "agent_name":"المندوب","visits":"الزيارات","bought":"اشترى",
            "potential":"محتمل","lost":"لن يشتري","last_visit":"آخر زيارة"
        }), use_container_width=True, hide_index=True)
    else: st.info("لا توجد زيارات بعد.")
    st.markdown("---")
    all_v = qall("SELECT agent_name,customer_name,location_text,status,notes,visited_at FROM agent_visits ORDER BY id DESC")
    if all_v:
        st.dataframe(pd.DataFrame(all_v).rename(columns={
            "agent_name":"المندوب","customer_name":"العميل","location_text":"الموقع",
            "status":"الحالة","notes":"ملاحظات","visited_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


# ── Incident: Submit ──────────────────────────────────────────────────────────
def pg_submit_incident():
    role = st.session_state["role"]
    page_hdr("🚨", "بلاغ خلل أو نقص", "أبلغ المدير عن أي مشكلة")
    with st.form("incident_form", clear_on_submit=True):
        desc = st.text_area("📝 وصف المشكلة *", placeholder="مثال: نقص حبر، عطل طابعة رقم 2...")
        sev  = st.selectbox("⚠️ درجة الخطورة", ["low","medium","high"],
                             format_func=lambda s: {"low":"🟢 منخفض","medium":"🟡 متوسط","high":"🔴 عالي"}[s])
        sub  = st.form_submit_button("📤 إرسال البلاغ", use_container_width=True)
    if sub:
        if not desc.strip(): st.error("يرجى كتابة وصف المشكلة.")
        else:
            qrun("INSERT INTO incident_reports (reporter_id,reporter_name,department,description,severity) VALUES (?,?,?,?,?)",
                 (st.session_state["uid"], st.session_state["uname"], ROLES[role]["label"], desc.strip(), sev))
            st.success("✅ تم إرسال البلاغ! سيراجعه المدير العام.")
    st.markdown("---")
    st.markdown("**📋 بلاغاتي السابقة**")
    rows = qall("SELECT description,severity,status,created_at FROM incident_reports WHERE reporter_id=? ORDER BY id DESC LIMIT 10",
                (st.session_state["uid"],))
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)
    else: st.info("لا توجد بلاغات سابقة.")


# ── Incident: All (admin) ─────────────────────────────────────────────────────
def pg_all_incidents():
    page_hdr("🚨", "بلاغات الأعطال", "جميع البلاغات الواردة من الأقسام")
    rows = qall("SELECT * FROM incident_reports ORDER BY id DESC")
    if not rows: st.success("🎉 لا توجد بلاغات مفتوحة!"); return

    open_r   = [r for r in rows if r["status"] == "open"]
    resolved = [r for r in rows if r["status"] == "resolved"]
    tab1, tab2 = st.tabs([f"🔴 مفتوحة ({len(open_r)})", f"✅ محلولة ({len(resolved)})"])

    for tab, flist in [(tab1, open_r), (tab2, resolved)]:
        with tab:
            if not flist: st.info("لا توجد بلاغات هنا."); continue
            for r in flist:
                sev_cls, sev_lbl = SEV_BADGES.get(r["severity"], ("b-sev-md", r["severity"]))
                with st.expander(f'{sev_lbl}  —  {r["department"]}  —  {r["created_at"][:16]}'):
                    st.markdown(f"**المبلّغ:** {r['reporter_name']}")
                    st.markdown(f"**الوصف:** {r['description']}")
                    if r["status"] == "open":
                        if st.button("✅ تحديد كـ محلول", key=f"res_{r['id']}"):
                            qrun("UPDATE incident_reports SET status='resolved',resolved_at=? WHERE id=?",
                                 (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                            st.success("تم تحديث البلاغ."); st.rerun()
                    else:
                        st.caption(f"تم الحل: {r['resolved_at']}")


# ── Financial Reports ─────────────────────────────────────────────────────────
def pg_financial():
    page_hdr("💰", "التقارير المالية", "ملخص مالي — للمبيعات والمدير فقط")
    total_v = (qone("SELECT COALESCE(SUM(price),0) s FROM orders") or {}).get("s", 0)
    rev     = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE production_status='Done'") or {}).get("s", 0)
    count   = (qone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    avg     = (total_v / count) if count else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي قيمة الأوردرات",  f"{total_v:,.0f} د.ع")
    c2.metric("إيرادات المكتملة",        f"{rev:,.0f} د.ع")
    c3.metric("قيد التنفيذ",             f"{total_v-rev:,.0f} د.ع")
    c4.metric("متوسط قيمة الأوردر",      f"{avg:,.0f} د.ع")
    st.markdown("---")

    rows = qall("SELECT order_number,customer_name,quantity,price,status,created_at FROM orders ORDER BY id DESC")
    if not rows: st.info("لا توجد أوردرات."); return
    df = pd.DataFrame(rows)
    st.dataframe(df.rename(columns={
        "order_number":"رقم الأوردر","customer_name":"العميل",
        "quantity":"الكمية","price":"السعر (د.ع)","status":"الحالة","created_at":"التاريخ"
    }), use_container_width=True, hide_index=True)

    header = (
        f"Z-Order — تقرير مالي\n"
        f"Developed by: {DEVELOPER}\n"
        f"تاريخ الاستخراج: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    )
    st.download_button("⬇️ تصدير CSV",
        (header + df.to_csv(index=False)).encode("utf-8-sig"),
        file_name=f"zorder_financial_{datetime.date.today()}.csv",
        mime="text/csv", use_container_width=True)


# ── Generic Dashboard (non-admin) ─────────────────────────────────────────────
def pg_generic_dash(role):
    page_hdr("📊", "لوحتي", "نظرة عامة على الأوردرات")
    guide(role)
    total  = (qone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    new_   = (qone("SELECT COUNT(*) c FROM orders WHERE status='New'") or {}).get("c", 0)
    inprod = (qone("SELECT COUNT(*) c FROM orders WHERE production_status='Printing'") or {}).get("c", 0)
    done   = (qone("SELECT COUNT(*) c FROM orders WHERE production_status='Done'") or {}).get("c", 0)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي", total); c2.metric("جديدة", new_)
    c3.metric("طباعة", inprod); c4.metric("مكتملة", done)
    st.markdown("---")
    rows = qall("SELECT order_number,customer_name,description,quantity,status,created_at FROM orders ORDER BY id DESC LIMIT 10")
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "order_number":"رقم الأوردر","customer_name":"العميل",
            "description":"الوصف","quantity":"الكمية","status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


# ── View orders ───────────────────────────────────────────────────────────────
def pg_view_orders(role):
    page_hdr("📋", "جميع الأوردرات", "عرض كامل")
    orders_table(role)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # 1. Init DB
    init_db()

    # 2. GATEKEEPER — nothing shows until login
    if not gatekeeper():
        return

    role = st.session_state["role"]

    # 3. Build navigation sidebar
    #    On mobile: sidebar is collapsed by default (set_page_config).
    #    User taps the ☰ toggle to open it — zero JS needed.
    active = build_nav()

    # 4. Route pages
    if active == "📊 لوحة المدير":
        pg_admin_dash()
    elif active == "👥 إدارة الموظفين":
        pg_employees()
    elif active == "📋 جميع الأوردرات":
        pg_view_orders(role)
    elif active == "💰 التقارير المالية":
        pg_financial()
    elif active == "🗺️ تقارير المندوبين":
        pg_agent_reports()
    elif active == "🚨 بلاغات الأعطال":
        pg_all_incidents()

    elif active == "📊 لوحتي" and role == "sales":
        pg_sales_dash()
    elif active == "➕ أوردر جديد":
        pg_add_order()
    elif active == "📋 أوردراتي":
        page_hdr("📋", "أوردراتي", "الأوردرات التي أضفتها")
        orders_table("sales", uid_filter=st.session_state["uid"])
    elif active == "💰 تقرير المبيعات":
        pg_financial()

    elif active == "📊 لوحتي" and role == "design":
        pg_generic_dash(role)
    elif active == "🎨 مهام التصميم":
        pg_design()
    elif active == "📋 عرض الأوردرات" and role == "design":
        pg_view_orders(role)

    elif active == "📊 لوحتي" and role == "production":
        pg_generic_dash(role)
    elif active == "🖨️ الإنتاج والطباعة":
        pg_production()
    elif active == "📋 عرض الأوردرات" and role == "production":
        pg_view_orders(role)

    elif active == "📊 لوحتي" and role == "agent":
        pg_generic_dash(role)
    elif active == "🗺️ تسجيل زيارة":
        pg_agent_visit()
    elif active == "📋 زياراتي":
        pg_agent_my_visits()

    elif active == "🚨 بلاغ خلل":
        pg_submit_incident()

    else:
        st.warning(f"الصفحة «{active}» غير متاحة.")

    # 5. Fixed footer — every page
    footer_bar()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
