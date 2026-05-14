"""
╔══════════════════════════════════════════════════════════════════════════╗
║   Z-ORDER · Built for Organized Teams · v6.0                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Developer : Abdulrahman Fallah                                         ║
║  Year      : 2026                                                       ║
╠══════════════════════════════════════════════════════════════════════════╣
║  QUICK START:                                                           ║
║    pip install streamlit pillow                                         ║
║    streamlit run z_order_app.py                                         ║
║                                                                         ║
║  Super-Admin (Platform Owner):                                          ║
║    Email    : admin@zorder.iq   Password : Admin@2025                  ║
║                                                                         ║
║  SUPABASE MIGRATION GUIDE (section at bottom of file)                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ARCHITECTURE: Multi-Tenant SaaS                                        ║
║  Each "workspace" (company) is fully isolated via workspace_id.         ║
║  Super-admin sees all workspaces; workspace-admin sees only his team.   ║
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
import json
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Z-ORDER | Built for Organized Teams",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",   # sidebar collapsed → mobile-safe
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER    = "Abdulrahman Fallah"
APP_NAME     = "Z-ORDER"
APP_TAGLINE  = "Built for Organized Teams"
APP_VER      = "6.0"
YEAR         = "2026"
SUPPORT_WA   = "https://wa.me/9647768723110"
SUPPORT_PHONE= "+964 776 872 3110"
DB_PATH      = "z_order.db"
UPLOAD_DIR   = Path("z_order_uploads")
for _sub in ["designs", "agents", "chat"]:
    (UPLOAD_DIR / _sub).mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ROLES
# ─────────────────────────────────────────────────────────────────────────────
ROLES = {
    "superadmin": {"ar": "المشرف العام",     "icon": "⭐", "clr": "#ffd166"},
    "admin":      {"ar": "مدير الشركة",      "icon": "🛡️", "clr": "#e8a020"},
    "sales":      {"ar": "المبيعات",          "icon": "💼", "clr": "#3b82f6"},
    "design":     {"ar": "التصميم",           "icon": "🎨", "clr": "#a855f7"},
    "purchase":   {"ar": "المشتريات",         "icon": "📦", "clr": "#22c55e"},
    "production": {"ar": "الإنتاج",           "icon": "🖨️", "clr": "#ff6b35"},
    "agent":      {"ar": "مندوب مبيعات",     "icon": "🗺️", "clr": "#06b6d4"},
}

ROLE_PAGES = {
    "superadmin": ["📊 لوحة التحكم", "🏢 الشركات",      "👥 المستخدمون", "📊 الإحصائيات"],
    "admin":      ["📊 الرئيسية",    "👥 الفريق",        "📋 الأوردرات",  "💰 المالية",
                   "🚨 البلاغات",    "🗺️ المندوبون",    "💬 المحادثة",  "📞 الدعم الفني"],
    "sales":      ["📊 الرئيسية",    "➕ أوردر جديد",   "📋 أوردراتي",  "🖼️ معاينة التصاميم",
                   "💰 تقريري",      "📦 طلب شراء",     "💬 المحادثة",  "🚨 بلاغ"],
    "design":     ["📊 الرئيسية",    "🎨 التصميم",       "💬 المحادثة",  "📦 طلب شراء",     "🚨 بلاغ"],
    "purchase":   ["📊 الرئيسية",    "📦 طلبات الشراء",  "💬 المحادثة",  "🚨 بلاغ"],
    "production": ["📊 الرئيسية",    "🖨️ الإنتاج",      "📋 الأوردرات", "💬 المحادثة",     "📦 طلب شراء", "🚨 بلاغ"],
    "agent":      ["📊 الرئيسية",    "🗺️ زيارة جديدة", "📋 زياراتي",   "💬 المحادثة",     "🚨 بلاغ"],
}

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  — Dark Gold Theme · Mobile-First · No sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* ── Tokens ───────────────────────────────── */
:root {
  --bg0: #070809;
  --bg1: #0b0d12;
  --bg2: #10131c;
  --bg3: #161924;
  --bg4: #1c2030;
  --bg5: #222638;
  --bdr: #1e2235;
  --bdr2: #272d44;

  /* Gold palette */
  --gold:  #e8a020;
  --gold2: #ffd166;
  --gold3: #b87a10;
  --acc2:  #ff6b35;

  /* Semantic */
  --blue:   #3b82f6;
  --green:  #22c55e;
  --red:    #ef4444;
  --purple: #a855f7;
  --cyan:   #06b6d4;

  /* Text */
  --t1: #f0f2f8;
  --t2: #8590a8;
  --t3: #3c4460;

  --r:  10px;
  --r2: 15px;
  --r3: 20px;
}

/* ── Reset ────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans Arabic', sans-serif !important;
  background:  var(--bg0) !important;
  color:       var(--t1) !important;
  direction:   rtl !important;
}

/* ── Hide sidebar completely ─────────────── */
section[data-testid="stSidebar"]  { display: none !important; }
[data-testid="collapsedControl"]   { display: none !important; }

/* ── App ──────────────────────────────────── */
.stApp { background: var(--bg0) !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Scrollbar ────────────────────────────── */
::-webkit-scrollbar           { width: 4px; height: 4px; }
::-webkit-scrollbar-track     { background: var(--bg1); }
::-webkit-scrollbar-thumb     { background: var(--bg5); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── Inputs ───────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
[data-baseweb="input"] input {
  background:    var(--bg3) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r) !important;
  color:         var(--t1) !important;
  font-family:   'IBM Plex Sans Arabic', sans-serif !important;
  font-size:     .9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--gold) !important;
  box-shadow:   0 0 0 3px rgba(232,160,32,.12) !important;
}

/* ── Buttons ──────────────────────────────── */
.stButton > button {
  background:    linear-gradient(135deg, var(--gold) 0%, var(--acc2) 100%) !important;
  color:         #07080b !important;
  font-weight:   700 !important;
  font-size:     .9rem !important;
  border:        none !important;
  border-radius: var(--r) !important;
  padding:       .6rem 1.2rem !important;
  min-height:    44px !important;
  width:         100% !important;
  font-family:   'IBM Plex Sans Arabic', sans-serif !important;
  transition:    transform .15s, box-shadow .15s !important;
  cursor:        pointer;
}
.stButton > button:hover {
  transform:  translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(232,160,32,.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Tabs ─────────────────────────────────── */
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
  font-size:     .82rem !important;
  border:        none !important;
  white-space:   nowrap !important;
}
.stTabs [aria-selected="true"] {
  background:    var(--bg5) !important;
  color:         var(--gold) !important;
  border-bottom: 2px solid var(--gold) !important;
}

/* ── Metrics ──────────────────────────────── */
[data-testid="stMetric"] {
  background:    var(--bg2) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
  padding:       .9rem 1rem !important;
}
[data-testid="stMetricLabel"] { color: var(--t2) !important; font-size: .72rem !important; }
[data-testid="stMetricValue"] {
  color:       var(--gold) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size:   1.3rem !important;
}

/* ── Expanders ────────────────────────────── */
.streamlit-expanderHeader {
  background:    var(--bg2) !important;
  border:        1px solid var(--bdr2) !important;
  border-radius: var(--r) !important;
  font-size:     .88rem !important;
}
.streamlit-expanderContent {
  background:    var(--bg1) !important;
  border:        1px solid var(--bdr2) !important;
  border-top:    none !important;
}

/* ── Dataframes ───────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"],
iframe[title="st.dataframe"] {
  width:         100% !important;
  border-radius: var(--r) !important;
  border:        1px solid var(--bdr) !important;
  overflow-x:    auto !important;
}

/* ── File uploader ────────────────────────── */
[data-testid="stFileUploader"] {
  background:    var(--bg3) !important;
  border:        1.5px dashed var(--bdr2) !important;
  border-radius: var(--r) !important;
}

/* ── Alerts ───────────────────────────────── */
.stAlert { background: var(--bg2) !important; border-radius: var(--r) !important; }
hr { border-color: var(--bdr) !important; margin: .9rem 0 !important; }

/* ════════════════════════════════════════════
   COMPONENT LIBRARY
════════════════════════════════════════════ */

/* ── Top navigation bar ──────────────────── */
.topbar {
  position:      sticky;
  top:           0;
  z-index:       999;
  background:    var(--bg1);
  border-bottom: 1px solid var(--bdr);
  padding:       .5rem 1.2rem;
  display:       flex;
  align-items:   center;
  gap:           .7rem;
  overflow-x:    auto;
  flex-wrap:     nowrap;
}

/* ── Logo ─────────────────────────────────── */
.zlogo {
  font-family:    'JetBrains Mono', monospace;
  font-size:      1.35rem;
  font-weight:    700;
  color:          var(--gold);
  letter-spacing: -.06em;
  line-height:    1;
  white-space:    nowrap;
  flex-shrink:    0;
}
.zlogo .sep { color: var(--t3); }
.zlogo .tag {
  font-family: 'IBM Plex Sans Arabic', sans-serif;
  font-size:   .58rem;
  font-weight: 400;
  color:       var(--t3);
  letter-spacing: .01em;
  display:     block;
  margin-top:  1px;
}

/* ── User chip ────────────────────────────── */
.uchip {
  display:       flex;
  align-items:   center;
  gap:           .45rem;
  background:    var(--bg3);
  border:        1px solid var(--bdr2);
  border-radius: 999px;
  padding:       .3rem .75rem .3rem .35rem;
  white-space:   nowrap;
  flex-shrink:   0;
  margin-right:  auto;
}
.uavatar {
  width:           28px;
  height:          28px;
  background:      linear-gradient(135deg, var(--gold), var(--acc2));
  border-radius:   50%;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       .72rem;
  font-weight:     700;
  color:           #07080b;
  flex-shrink:     0;
}

/* ── Page content wrapper ─────────────────── */
.pw { padding: 1.1rem 1.4rem 6.5rem; max-width: 1300px; margin: 0 auto; }

/* ── Page header ──────────────────────────── */
.ph { display: flex; align-items: center; gap: .75rem; margin-bottom: 1.15rem; }
.ph-icon {
  font-size:       1.55rem;
  background:      var(--bg2);
  border:          1px solid var(--bdr2);
  border-radius:   var(--r);
  width: 48px; height: 48px;
  display:         flex;
  align-items:     center;
  justify-content: center;
  flex-shrink:     0;
}
.ph h2 { font-size: 1.15rem; font-weight: 700; color: var(--t1); margin: 0; }
.ph p  { font-size: .74rem;  color: var(--t3); margin: 0; }

/* ── Cards ────────────────────────────────── */
.card {
  background:    var(--bg2);
  border:        1px solid var(--bdr2);
  border-radius: var(--r2);
  padding:       1rem 1.2rem;
  margin-bottom: .65rem;
  transition:    border-color .2s, transform .15s;
}
.card:hover { border-color: var(--gold); transform: translateY(-1px); }
.card.gold-border { border-color: rgba(232,160,32,.35); }

/* ── Info card ────────────────────────────── */
.icard {
  background:    linear-gradient(135deg, rgba(232,160,32,.07), rgba(255,107,53,.04));
  border:        1px solid rgba(232,160,32,.2);
  border-right:  3px solid var(--gold);
  border-radius: var(--r2);
  padding:       .85rem 1.1rem;
  margin-bottom: .9rem;
  font-size:     .82rem;
  color:         var(--t2);
  line-height:   1.85;
}

/* ── Support card ─────────────────────────── */
.support-card {
  background:    linear-gradient(135deg, rgba(34,197,94,.06), rgba(6,182,212,.04));
  border:        1px solid rgba(34,197,94,.2);
  border-radius: var(--r2);
  padding:       1.2rem 1.4rem;
  text-align:    center;
}
.wa-btn {
  display:         inline-flex;
  align-items:     center;
  gap:             .5rem;
  background:      #25D366;
  color:           #fff !important;
  padding:         .65rem 1.5rem;
  border-radius:   var(--r);
  font-weight:     700;
  text-decoration: none;
  font-size:       .9rem;
  margin-top:      .75rem;
  transition:      opacity .2s;
}
.wa-btn:hover { opacity: .85; }

/* ── Chat bubble ──────────────────────────── */
.chat-wrap { display: flex; flex-direction: column; gap: .55rem; margin-bottom: 1rem; max-height: 420px; overflow-y: auto; padding: .4rem; }
.bubble {
  max-width:     75%;
  padding:       .55rem .85rem;
  border-radius: var(--r2);
  font-size:     .85rem;
  line-height:   1.5;
  position:      relative;
}
.bubble.me    { background: rgba(232,160,32,.15); border: 1px solid rgba(232,160,32,.2); align-self: flex-start; }
.bubble.other { background: var(--bg3);            border: 1px solid var(--bdr2);          align-self: flex-end; }
.bubble .bname  { font-size: .65rem; font-weight: 700; color: var(--gold); margin-bottom: 2px; }
.bubble .btime  { font-size: .6rem; color: var(--t3); margin-top: 3px; }

/* ── Badges ───────────────────────────────── */
.badge {
  display:        inline-flex;
  align-items:    center;
  gap:            3px;
  padding:        .17rem .58rem;
  border-radius:  999px;
  font-size:      .63rem;
  font-weight:    700;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.b-new  { background:rgba(59,130,246,.14); color:#60a5fa; border:1px solid rgba(59,130,246,.25); }
.b-ready{ background:rgba(34,197,94,.14);  color:#4ade80; border:1px solid rgba(34,197,94,.25);  }
.b-print{ background:rgba(255,107,53,.14); color:#fb923c; border:1px solid rgba(255,107,53,.25); }
.b-done { background:rgba(34,197,94,.1);   color:#16a34a; border:1px solid rgba(34,197,94,.2);   }
.b-deliv{ background:rgba(6,182,212,.12);  color:#06b6d4; border:1px solid rgba(6,182,212,.2);   }
.b-pend { background:rgba(251,191,36,.12); color:#fbbf24; border:1px solid rgba(251,191,36,.2);  }
.b-appr { background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2);   }
.b-rej  { background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2);   }
.b-sev-lo{background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2);   }
.b-sev-md{background:rgba(251,191,36,.12); color:#fbbf24; border:1px solid rgba(251,191,36,.2);  }
.b-sev-hi{background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2);   }
.b-abuy { background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2);   }
.b-apot { background:rgba(59,130,246,.12); color:#3b82f6; border:1px solid rgba(59,130,246,.2);  }
.b-ano  { background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2);   }

/* ── Section label ────────────────────────── */
.sec {
  font-size:      .67rem;
  font-weight:    700;
  color:          var(--t3);
  text-transform: uppercase;
  letter-spacing: .1em;
  margin:         .85rem 0 .45rem;
}

/* ── Footer ───────────────────────────────── */
.footer {
  position:        fixed;
  bottom:          0; left: 0; right: 0;
  background:      var(--bg1);
  border-top:      1px solid var(--bdr);
  padding:         .44rem 1.2rem;
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  font-size:       .66rem;
  color:           var(--t3);
  z-index:         9999;
  gap:             .4rem;
  flex-wrap:       wrap;
}
.footer .hi { color: var(--gold); font-weight: 600; }

/* ── Login ────────────────────────────────── */
.logo-big {
  font-family:    'JetBrains Mono', monospace;
  font-size:      2.4rem;
  font-weight:    700;
  color:          var(--gold);
  letter-spacing: -.07em;
  text-align:     center;
  line-height:    1;
}
.logo-big .sep { color: var(--t3); }
.logo-tag {
  text-align:  center;
  font-size:   .72rem;
  color:       var(--t3);
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-top:  .35rem;
}

/* ── Nav selectbox ────────────────────────── */
.nav-sel .stSelectbox > div > div {
  background:    var(--bg2) !important;
  border:        1px solid var(--gold) !important;
  font-weight:   600 !important;
  font-size:     .87rem !important;
  border-radius: var(--r) !important;
}

/* ════════════════════════════════════════════
   MOBILE  ≤ 768 px
════════════════════════════════════════════ */
@media (max-width: 768px) {
  .pw { padding: .65rem .45rem 6.5rem; }
  .ph-icon { width: 36px; height: 36px; font-size: 1.15rem; }
  .ph h2   { font-size: 1rem; }

  [data-testid="column"] {
    width:     100% !important;
    flex:      0 0 100% !important;
    min-width: 100% !important;
    padding:   0 !important;
  }

  .stButton > button { font-size: .83rem !important; min-height: 46px !important; }
  [data-testid="stMetricValue"] { font-size: 1.05rem !important; }

  .topbar { padding: .42rem .6rem; }
  .footer { font-size: .59rem; padding: .32rem .55rem; }

  .stDataFrame,
  [data-testid="stDataFrame"],
  iframe[title="st.dataframe"] { overflow-x: auto !important; }

  .bubble { max-width: 90%; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DATABASE  — Multi-Tenant Schema
# ─────────────────────────────────────────────────────────────────────────────

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def qall(sql, p=()):
    c = _conn(); r = c.execute(sql, p).fetchall(); c.close()
    return [dict(x) for x in r]

def qone(sql, p=()):
    c = _conn(); r = c.execute(sql, p).fetchone(); c.close()
    return dict(r) if r else None

def qrun(sql, p=()):
    c = _conn(); cur = c.execute(sql, p); c.commit()
    lid = cur.lastrowid; c.close(); return lid


def init_db():
    c = _conn(); x = c.cursor()

    # ── Workspaces (companies) ──────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS workspaces (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT    NOT NULL,
        slug       TEXT    UNIQUE NOT NULL,
        plan       TEXT    DEFAULT 'starter',   -- starter | pro | enterprise
        is_active  INTEGER DEFAULT 1,
        created_at TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    # ── Users ───────────────────────────────────────────────────────────────
    # workspace_id = 0 → superadmin (platform owner)
    x.execute("""CREATE TABLE IF NOT EXISTS users (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id INTEGER DEFAULT 0,
        full_name    TEXT    NOT NULL,
        username     TEXT    NOT NULL,
        email        TEXT    UNIQUE NOT NULL,
        password     TEXT    NOT NULL,
        role         TEXT    NOT NULL,
        created_by   INTEGER DEFAULT 0,   -- admin who added this user
        is_active    INTEGER DEFAULT 1,
        created_at   TEXT    DEFAULT (datetime('now','localtime')),
        UNIQUE (workspace_id, username)
    )""")

    # ── Orders ──────────────────────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS orders (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id       INTEGER NOT NULL,
        order_number       TEXT    NOT NULL,
        customer_name      TEXT    NOT NULL,
        description        TEXT    NOT NULL,
        quantity           INTEGER NOT NULL,
        price              REAL    NOT NULL,
        created_at         TEXT    DEFAULT (datetime('now','localtime')),
        created_by_id      INTEGER,
        created_by_name    TEXT,
        status             TEXT    DEFAULT 'جديد',
        design_status      TEXT    DEFAULT 'قيد الانتظار',
        design_file_path   TEXT    DEFAULT '',
        design_link        TEXT    DEFAULT '',
        design_notes       TEXT    DEFAULT '',
        design_updated     TEXT    DEFAULT '',
        design_by          TEXT    DEFAULT '',
        production_status  TEXT    DEFAULT 'قيد الانتظار',
        production_notes   TEXT    DEFAULT '',
        production_updated TEXT    DEFAULT '',
        production_by      TEXT    DEFAULT '',
        delivered          INTEGER DEFAULT 0,
        delivered_at       TEXT    DEFAULT '',
        delivered_by       TEXT    DEFAULT '',
        UNIQUE (workspace_id, order_number)
    )""")

    # ── Purchase requests ────────────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS purchase_requests (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id   INTEGER NOT NULL,
        requester_id   INTEGER NOT NULL,
        requester_name TEXT    NOT NULL,
        department     TEXT    NOT NULL,
        item_name      TEXT    NOT NULL,
        quantity       TEXT    NOT NULL,
        urgency        TEXT    DEFAULT 'عادي',
        notes          TEXT    DEFAULT '',
        status         TEXT    DEFAULT 'قيد المراجعة',
        reviewed_by    TEXT    DEFAULT '',
        reviewed_at    TEXT    DEFAULT '',
        created_at     TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    # ── Incident reports ─────────────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS incident_reports (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id  INTEGER NOT NULL,
        reporter_id   INTEGER,
        reporter_name TEXT,
        department    TEXT,
        description   TEXT    NOT NULL,
        severity      TEXT    DEFAULT 'متوسط',
        status        TEXT    DEFAULT 'مفتوح',
        created_at    TEXT    DEFAULT (datetime('now','localtime')),
        resolved_at   TEXT    DEFAULT ''
    )""")

    # ── Agent visits ─────────────────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS agent_visits (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id INTEGER NOT NULL,
        agent_id     INTEGER,
        agent_name   TEXT,
        customer_name TEXT   NOT NULL,
        location     TEXT    DEFAULT '',
        visit_status TEXT    DEFAULT 'محتمل',
        notes        TEXT    DEFAULT '',
        image_path   TEXT    DEFAULT '',
        visited_at   TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    # ── Shared chat ──────────────────────────────────────────────────────────
    x.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id INTEGER NOT NULL,
        sender_id    INTEGER NOT NULL,
        sender_name  TEXT    NOT NULL,
        sender_role  TEXT    NOT NULL,
        message      TEXT    NOT NULL,
        sent_at      TEXT    DEFAULT (datetime('now','localtime'))
    )""")

    # ── Seed: platform superadmin (workspace_id = 0) ──────────────────────
    try:
        x.execute("""INSERT INTO users (workspace_id, full_name, username, email, password, role)
                     VALUES (0,'Platform Admin','superadmin','admin@zorder.iq',?,?)""",
                  (_hash("Admin@2025"), "superadmin"))
    except sqlite3.IntegrityError:
        pass

    c.commit(); c.close()


# ─── DB helpers ────────────────────────────────────────────────────────────────

def wid() -> int:
    """Current workspace_id from session."""
    return st.session_state.get("workspace_id", 0)

def order_no() -> str:
    n = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=?", (wid(),)) or {}).get("c", 0)
    return f"ZO-{datetime.date.today().strftime('%y%m%d')}-{n+1:04d}"

def sync_status(oid: int):
    o = qone("SELECT design_status, production_status, delivered FROM orders WHERE id=?", (oid,))
    if not o: return
    ds, ps, dv = o["design_status"], o["production_status"], o["delivered"]
    s = ("تم التسليم"   if dv
         else "مكتمل"           if ps == "مكتمل"
         else "جاري الإنتاج"   if ps == "جاري الإنتاج"
         else "جاهز للإنتاج"   if ds == "مكتمل"
         else "جديد")
    qrun("UPDATE orders SET status=? WHERE id=?", (s, oid))

def save_upload(f, sub="designs") -> str:
    if not f: return ""
    d = UPLOAD_DIR / sub; d.mkdir(exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe = "".join(ch for ch in f.name if ch.isalnum() or ch in "._-")
    p    = d / f"{ts}_{safe}"; p.write_bytes(f.read()); return str(p)

def dl_btn(fp: str, lbl="⬇️ تحميل"):
    p = Path(fp)
    if p.exists():
        st.download_button(lbl, p.read_bytes(), file_name=p.name, use_container_width=True)
    else:
        st.caption("⚠️ الملف غير متوفر")


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
PUR_BADGE = {"قيد المراجعة":("b-pend","⏳"),"موافق عليه":("b-appr","✅"),"مرفوض":("b-rej","❌")}
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
        f'</div>',
        unsafe_allow_html=True)

def show_orders(role, uid_filter=None, title="الأوردرات"):
    hdr("📋", title)
    hide_price = role not in ("admin", "sales", "superadmin")
    sql = ("SELECT * FROM orders WHERE workspace_id=?" +
           (" AND created_by_id=?" if uid_filter else "") +
           " ORDER BY id DESC")
    params = (wid(), uid_filter) if uid_filter else (wid(),)
    rows = qall(sql, params)
    if not rows: st.info("لا توجد أوردرات."); return

    sts = ["الكل"] + sorted({r["status"] for r in rows})
    sel = st.selectbox("الحالة", sts, key=f"o_{role}_{uid_filter}")
    if sel != "الكل": rows = [r for r in rows if r["status"] == sel]

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
#  GATEKEEPER  — strict login, blocks everything until authenticated
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
            f'<div style="text-align:center;color:var(--t3);font-size:.68rem;margin-top:.5rem">v{APP_VER}</div>',
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.container():
            st.markdown(
                '<div style="background:var(--bg2);border:1px solid var(--bdr2);'
                'border-radius:16px;padding:1.75rem 1.5rem;">',
                unsafe_allow_html=True)
            idn = st.text_input("📧 الإيميل أو اسم المستخدم",
                                placeholder="admin@zorder.iq", key="gk_i")
            pw  = st.text_input("🔒 كلمة المرور", type="password", key="gk_p")
            clicked = st.button("دخول ←", key="gk_b")
            st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            if not idn or not pw:
                st.error("يرجى إدخال البيانات."); return False
            i = idn.strip().lower()
            u = qone("SELECT * FROM users WHERE (lower(email)=? OR lower(username)=?) "
                     "AND password=? AND is_active=1", (i, i, _hash(pw)))
            if u:
                # Resolve workspace info
                ws_id   = u["workspace_id"]
                ws_name = ""
                if ws_id > 0:
                    ws = qone("SELECT name FROM workspaces WHERE id=?", (ws_id,))
                    ws_name = ws["name"] if ws else ""
                else:
                    ws_name = "Z-ORDER Platform"

                st.session_state.update(
                    auth=True,
                    uid=u["id"],
                    uname=u["full_name"],
                    role=u["role"],
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
#  TOP NAVIGATION BAR
# ─────────────────────────────────────────────────────────────────────────────

def top_nav() -> str:
    role  = st.session_state["role"]
    uname = st.session_state["uname"]
    wsn   = st.session_state.get("workspace_name", "")
    ri    = ROLES.get(role, {"ar": role, "icon": "👤", "clr": "#e8a020"})
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
        st.markdown("</div>", unsafe_allow_html=True)
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
    hdr("⭐", "لوحة التحكم — Platform Admin", "إدارة جميع الشركات والنظام")
    ws_count  = (qone("SELECT COUNT(*) c FROM workspaces") or {}).get("c", 0)
    usr_count = (qone("SELECT COUNT(*) c FROM users WHERE workspace_id>0") or {}).get("c", 0)
    ord_count = (qone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    rev_total = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE status IN ('مكتمل','تم التسليم')") or {}).get("s", 0)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("الشركات المسجلة", ws_count)
    c2.metric("المستخدمون", usr_count)
    c3.metric("إجمالي الأوردرات", ord_count)
    c4.metric("الإيراد الكلي (د.ع)", f"{rev_total:,.0f}")

    st.markdown("---")
    ws_list = qall("SELECT id,name,slug,plan,is_active,created_at FROM workspaces ORDER BY id DESC")
    if ws_list:
        st.dataframe(pd.DataFrame(ws_list).rename(columns={
            "id":"#","name":"الشركة","slug":"Slug","plan":"الخطة",
            "is_active":"نشطة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


def pg_super_workspaces():
    hdr("🏢", "إدارة الشركات", "أضف شركات جديدة وأنشئ مديريها")
    ws_list = qall("SELECT id,name,slug,plan,is_active FROM workspaces ORDER BY id")
    if ws_list:
        df = pd.DataFrame(ws_list)
        df["is_active"] = df["is_active"].map({1:"✅", 0:"🚫"})
        st.dataframe(df.rename(columns={"id":"#","name":"الشركة","slug":"Slug","plan":"الخطة","is_active":"نشطة"}),
                     use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sec">➕ شركة جديدة + إنشاء مديرها</div>', unsafe_allow_html=True)
    with st.form("add_ws", clear_on_submit=True):
        c1,c2 = st.columns(2)
        ws_name = c1.text_input("اسم الشركة *")
        ws_slug = c2.text_input("Slug (حروف إنجليزية صغيرة) *", placeholder="my-company")
        plan    = st.selectbox("الخطة", ["starter","pro","enterprise"])
        st.markdown('<div class="sec">بيانات مدير الشركة</div>', unsafe_allow_html=True)
        c3,c4 = st.columns(2)
        adm_fn = c3.text_input("اسم المدير *")
        adm_un = c4.text_input("اسم المستخدم *")
        c5,c6 = st.columns(2)
        adm_em = c5.text_input("إيميل المدير *")
        adm_pw = c6.text_input("كلمة مرور المدير *", type="password")
        sub    = st.form_submit_button("✅ إنشاء الشركة والمدير", use_container_width=True)

    if sub:
        if not all([ws_name, ws_slug, adm_fn, adm_un, adm_em, adm_pw]):
            st.error("يرجى تعبئة جميع الحقول.")
        else:
            slug = ws_slug.strip().lower().replace(" ", "-")
            try:
                ws_id = qrun("INSERT INTO workspaces (name,slug,plan) VALUES (?,?,?)",
                             (ws_name.strip(), slug, plan))
                qrun("INSERT INTO users (workspace_id,full_name,username,email,password,role,created_by) VALUES (?,?,?,?,?,?,?)",
                     (ws_id, adm_fn.strip(), adm_un.strip().lower(),
                      adm_em.strip().lower(), _hash(adm_pw), "admin", 0))
                st.success(f"✅ تم إنشاء الشركة **{ws_name}** والمدير **{adm_fn}**!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ الـ Slug أو الإيميل مستخدم بالفعل.")


def pg_super_users():
    hdr("👥", "جميع المستخدمين", "عرض وبحث عبر كل الشركات")
    rows = qall("""SELECT u.id, w.name ws, u.full_name, u.username, u.email,
                          u.role, u.is_active, u.created_at
                   FROM users u
                   LEFT JOIN workspaces w ON w.id=u.workspace_id
                   WHERE u.workspace_id > 0
                   ORDER BY u.workspace_id, u.id""")
    if rows:
        df = pd.DataFrame(rows)
        df["is_active"] = df["is_active"].map({1:"✅",0:"🚫"})
        st.dataframe(df.rename(columns={
            "id":"#","ws":"الشركة","full_name":"الاسم","username":"المستخدم",
            "email":"الإيميل","role":"الدور","is_active":"نشط","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


def pg_super_stats():
    hdr("📊", "الإحصائيات العامة", "بيانات كل الشركات")
    rows = qall("""SELECT w.name ws, COUNT(o.id) orders,
                          COALESCE(SUM(o.price),0) total_val,
                          COALESCE(SUM(CASE WHEN o.status IN ('مكتمل','تم التسليم') THEN o.price ELSE 0 END),0) rev
                   FROM workspaces w
                   LEFT JOIN orders o ON o.workspace_id=w.id
                   GROUP BY w.id ORDER BY total_val DESC""")
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "ws":"الشركة","orders":"الأوردرات","total_val":"إجمالي القيمة","rev":"الإيراد المحصّل"
        }), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: WORKSPACE ADMIN
# ─────────────────────────────────────────────────────────────────────────────

def pg_admin_dash():
    hdr("🛡️", "لوحة المدير", "إحصائيات شركتك")
    guide("① راقب الأوردرات والمالية<br>② راجع طلبات الشراء والبلاغات<br>③ أضف الفريق من «الفريق»")
    today = datetime.date.today().isoformat()
    WID   = wid()
    tot  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=?", (WID,)) or {}).get("c",0)
    tod  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND created_at LIKE ?", (WID,f"{today}%")) or {}).get("c",0)
    dn   = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND status IN ('مكتمل','تم التسليم')", (WID,)) or {}).get("c",0)
    rv   = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE workspace_id=? AND status IN ('مكتمل','تم التسليم')", (WID,)) or {}).get("s",0)
    tv   = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE workspace_id=?", (WID,)) or {}).get("s",0)
    opr  = (qone("SELECT COUNT(*) c FROM incident_reports WHERE workspace_id=? AND status='مفتوح'", (WID,)) or {}).get("c",0)
    pp   = (qone("SELECT COUNT(*) c FROM purchase_requests WHERE workspace_id=? AND status='قيد المراجعة'", (WID,)) or {}).get("c",0)
    us   = (qone("SELECT COUNT(*) c FROM users WHERE workspace_id=? AND is_active=1", (WID,)) or {}).get("c",0)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("أوردرات اليوم", tod);        c2.metric("مكتملة/إجمالي", f"{dn}/{tot}")
    c3.metric("إيراد محصّل (د.ع)", f"{rv:,.0f}"); c4.metric("طلبات شراء معلقة", pp)
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("إجمالي القيمة (د.ع)", f"{tv:,.0f}"); c6.metric("قيد التنفيذ (د.ع)", f"{tv-rv:,.0f}")
    c7.metric("بلاغات مفتوحة", opr);         c8.metric("موظفون نشطون", us)

    st.markdown("---")
    t1,t2,t3,t4 = st.tabs(["📋 آخر الأوردرات","📦 طلبات الشراء","🚨 البلاغات","🗺️ المندوبون"])
    with t1:
        rows = qall("SELECT order_number,customer_name,quantity,price,status,created_at FROM orders WHERE workspace_id=? ORDER BY id DESC LIMIT 15", (WID,))
        if rows: st.dataframe(pd.DataFrame(rows).rename(columns={"order_number":"الأوردر","customer_name":"العميل","quantity":"الكمية","price":"السعر","status":"الحالة","created_at":"التاريخ"}), use_container_width=True, hide_index=True)
        else: st.info("لا توجد أوردرات.")
    with t2:
        rows = qall("SELECT requester_name,department,item_name,quantity,urgency,status,created_at FROM purchase_requests WHERE workspace_id=? ORDER BY id DESC LIMIT 20", (WID,))
        if rows: st.dataframe(pd.DataFrame(rows).rename(columns={"requester_name":"الموظف","department":"القسم","item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية","status":"الحالة","created_at":"التاريخ"}), use_container_width=True, hide_index=True)
        else: st.info("لا توجد طلبات.")
    with t3:
        rows = qall("SELECT reporter_name,department,description,severity,status,created_at FROM incident_reports WHERE workspace_id=? ORDER BY id DESC LIMIT 15", (WID,))
        if rows: st.dataframe(pd.DataFrame(rows).rename(columns={"reporter_name":"المبلّغ","department":"القسم","description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"}), use_container_width=True, hide_index=True)
        else: st.success("🎉 لا بلاغات!")
    with t4:
        rows = qall("""SELECT agent_name,COUNT(*) v,
            SUM(CASE WHEN visit_status='اشترى' THEN 1 ELSE 0 END) bought,
            SUM(CASE WHEN visit_status='محتمل' THEN 1 ELSE 0 END) pot
            FROM agent_visits WHERE workspace_id=? GROUP BY agent_id ORDER BY v DESC""", (WID,))
        if rows: st.dataframe(pd.DataFrame(rows).rename(columns={"agent_name":"المندوب","v":"الزيارات","bought":"اشترى","pot":"محتمل"}), use_container_width=True, hide_index=True)
        else: st.info("لا توجد زيارات.")


def pg_team():
    hdr("👥", "إدارة الفريق", "أضف أعضاء الفريق وحدد صلاحياتهم")
    guide("① أنت المدير — الوحيد الذي يضيف موظفين لشركتك<br>② الموظفون يرون فقط بيانات شركتك<br>③ يمكن تعطيل أي حساب")
    WID = wid()

    rows = qall("SELECT id,full_name,username,email,role,is_active,created_at FROM users WHERE workspace_id=? ORDER BY id", (WID,))
    if rows:
        df = pd.DataFrame(rows)
        df["is_active"] = df["is_active"].map({1:"✅ نشط", 0:"🚫 موقوف"})
        st.dataframe(df.rename(columns={"id":"#","full_name":"الاسم","username":"المستخدم",
                                        "email":"الإيميل","role":"الدور","is_active":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sec">➕ إضافة موظف جديد</div>', unsafe_allow_html=True)
    with st.form("add_emp", clear_on_submit=True):
        c1,c2 = st.columns(2)
        fn = c1.text_input("الاسم الكامل *");   un = c2.text_input("اسم المستخدم *")
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
        if not all([fn, un, em, p1]): errs.append("جميع الحقول مطلوبة.")
        if p1 and p1 != p2:           errs.append("كلمتا المرور غير متطابقتين.")
        if p1 and len(p1) < 6:        errs.append("كلمة المرور 6 أحرف على الأقل.")
        for e in errs: st.error(e)
        if not errs:
            try:
                qrun("INSERT INTO users (workspace_id,full_name,username,email,password,role,created_by) VALUES (?,?,?,?,?,?,?)",
                     (WID, fn.strip(), un.strip().lower(), em.strip().lower(),
                      _hash(p1), rl, st.session_state["uid"]))
                st.success(f"✅ تم إضافة **{fn}**!"); st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ اسم المستخدم أو الإيميل مستخدم بالفعل.")

    st.markdown("---")
    st.markdown('<div class="sec">🔄 تفعيل / تعطيل</div>', unsafe_allow_html=True)
    all_u = qall("SELECT id,full_name,username FROM users WHERE workspace_id=? AND role!='admin' ORDER BY id", (WID,))
    if all_u:
        opts  = {f"{u['id']} — {u['full_name']} ({u['username']})": u["id"] for u in all_u}
        label = st.selectbox("الموظف", list(opts.keys()))
        ut    = opts[label]
        ca, cb, _ = st.columns([1,1,3])
        if ca.button("✅ تفعيل",  key="act"):  qrun("UPDATE users SET is_active=1 WHERE id=?", (ut,)); st.rerun()
        if cb.button("🚫 تعطيل", key="dact"): qrun("UPDATE users SET is_active=0 WHERE id=?", (ut,)); st.rerun()
    else:
        st.info("لا يوجد موظفون مضافون بعد.")


def pg_support():
    hdr("📞", "الدعم الفني", "تواصل مع فريق Z-ORDER")
    st.markdown(
        f'<div class="support-card">'
        f'<div style="font-size:2rem;margin-bottom:.5rem">🛎️</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:var(--t1);margin-bottom:.3rem">فريق دعم Z-ORDER</div>'
        f'<div style="color:var(--t2);font-size:.85rem;margin-bottom:.4rem">'
        f'نحن هنا لمساعدتك في أي وقت</div>'
        f'<div style="font-size:.95rem;color:var(--gold);font-weight:600;margin:.5rem 0">'
        f'📞 {SUPPORT_PHONE}</div>'
        f'<a class="wa-btn" href="{SUPPORT_WA}" target="_blank">'
        f'<span style="font-size:1.1rem">💬</span> تواصل عبر واتساب</a>'
        f'</div>',
        unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f'<div style="color:var(--t3);font-size:.8rem;text-align:center">'
        f'Developed by <b style="color:var(--gold)">{DEVELOPER}</b>'
        f' · {APP_NAME} v{APP_VER}</div>',
        unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: SALES
# ─────────────────────────────────────────────────────────────────────────────

def pg_sales_dash():
    hdr("📊", "لوحتي", "أوردراتك وإحصائياتك")
    guide("① أضف أوردراً من «أوردر جديد»<br>② السعر سري — لا يظهر لباقي الأقسام<br>③ يمكنك معاينة ملفات التصميم من «معاينة التصاميم»")
    uid = st.session_state["uid"]; WID = wid()
    tot = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND created_by_id=?", (WID,uid)) or {}).get("c",0)
    dn  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND created_by_id=? AND status IN ('مكتمل','تم التسليم')", (WID,uid)) or {}).get("c",0)
    rv  = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE workspace_id=? AND created_by_id=? AND status IN ('مكتمل','تم التسليم')", (WID,uid)) or {}).get("s",0)
    nw  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND created_by_id=? AND status='جديد'", (WID,uid)) or {}).get("c",0)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي أوردراتي",tot); c2.metric("مكتملة",dn)
    c3.metric("إيراداتي (د.ع)",f"{rv:,.0f}"); c4.metric("جديدة",nw)
    st.markdown("---")
    show_orders("sales", uid_filter=uid, title="أوردراتي الأخيرة")


def pg_add_order():
    hdr("➕", "أوردر جديد", "أدخل تفاصيل طلب العميل")
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
            qrun("INSERT INTO orders (workspace_id,order_number,customer_name,description,quantity,price,created_by_id,created_by_name) VALUES (?,?,?,?,?,?,?,?)",
                 (wid(), ono, cust.strip(), desc.strip(), qty, price,
                  st.session_state["uid"], st.session_state["uname"]))
            st.success(f"✅ تم حفظ الأوردر **{ono}** — سيظهر لقسم التصميم فوراً!")


def pg_sales_design_preview():
    """Sales can preview uploaded design files before they go to production."""
    hdr("🖼️", "معاينة التصاميم", "عرض الملفات المرفوعة من المصممين")
    guide("① هذه المعاينة للتأكد من التصميم قبل إرساله للإنتاج<br>② يمكنك تحميل الملف أو فتح الرابط<br>③ لا يمكنك تعديل التصميم من هنا")
    rows = qall("SELECT * FROM orders WHERE workspace_id=? AND design_status='مكتمل' ORDER BY design_updated DESC", (wid(),))
    if not rows:
        st.info("لا توجد تصاميم مكتملة بعد.")
        return
    for r in rows:
        with st.expander(f"🎨 {r['order_number']} — {r['customer_name']}"):
            c1,c2 = st.columns(2)
            c1.markdown(f"**الوصف:** {r['description']}")
            c1.markdown(f"**الكمية:** {r['quantity']}")
            c2.markdown(f"**صمّمه:** {r['design_by'] or '—'}")
            c2.markdown(f"**تاريخ التصميم:** {r['design_updated'] or '—'}")
            if r.get("design_notes"):
                st.markdown(f"**ملاحظات المصمم:** {r['design_notes']}")
            st.markdown("---")
            if r.get("design_file_path") and Path(r["design_file_path"]).exists():
                dl_btn(r["design_file_path"], "⬇️ تحميل ملف التصميم")
                # Image preview
                ext = Path(r["design_file_path"]).suffix.lower()
                if ext in [".png",".jpg",".jpeg",".webp"]:
                    try:
                        st.image(r["design_file_path"], use_container_width=True)
                    except Exception:
                        pass
            elif r.get("design_link"):
                st.markdown(f'[🔗 فتح رابط التصميم]({r["design_link"]})')
            else:
                st.caption("لا يوجد ملف أو رابط.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: DESIGN
# ─────────────────────────────────────────────────────────────────────────────

def pg_design():
    hdr("🎨", "قسم التصميم", "ارفع ملف التصميم لكل أوردر")
    guide("① ارفع ملف التصميم — الملف مرتبط بالأوردر في قاعدة البيانات<br>② الإنتاج لن يبدأ إلا بعد رفع الملف<br>③ يمكن لقسم المبيعات معاينة الملف قبل الطباعة")
    WID = wid()
    rows = qall("SELECT * FROM orders WHERE workspace_id=? ORDER BY id DESC", (WID,))
    pend = [r for r in rows if r["design_status"] == "قيد الانتظار"]
    done = [r for r in rows if r["design_status"] == "مكتمل"]

    t1, t2 = st.tabs([f"⏳ قيد الانتظار ({len(pend)})", f"✅ مكتملة ({len(done)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد مهام تصميم معلقة!")
        for r in pend:
            with st.expander(f"🔷 {r['order_number']}  —  {r['customer_name']}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**التاريخ:** {r['created_at']}")
                c2.markdown(f"**أضافه:** {r['created_by_name']}")
                st.markdown("---")
                upld  = st.file_uploader("📎 رفع ملف التصميم *", key=f"du_{r['id']}",
                                          type=["pdf","png","jpg","jpeg","ai","psd","svg","eps","zip","cdr"],
                                          help="ارفع الملف النهائي للطباعة")
                dl    = st.text_input("🔗 أو رابط التصميم", value=r["design_link"] or "", key=f"dl_{r['id']}")
                notes = st.text_area("📝 ملاحظات للإنتاج", value=r["design_notes"] or "",
                                     key=f"dn_{r['id']}", height=65)
                if st.button("✅ تأكيد رفع التصميم", key=f"d_ok_{r['id']}"):
                    fp = save_upload(upld, "designs") if upld else (r["design_file_path"] or "")
                    if not fp and not dl.strip():
                        st.error("⚠️ يجب رفع ملف أو إدخال رابط التصميم.")
                    else:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        qrun("UPDATE orders SET design_status='مكتمل',design_file_path=?,design_link=?,design_notes=?,design_updated=?,design_by=? WHERE id=?",
                             (fp, dl.strip(), notes.strip(), now, st.session_state["uname"], r["id"]))
                        sync_status(r["id"])
                        st.success("✅ تم رفع التصميم! الأوردر جاهز للإنتاج."); st.rerun()

    with t2:
        if not done: st.info("لا توجد تصاميم مكتملة.")
        for r in done:
            co1,co2 = st.columns([4,2])
            with co1:
                st.markdown(
                    f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                    f'&nbsp;{badge("مكتمل",ORD_BADGE)}'
                    f'<br><small style="color:var(--t3)">🗓 {r["design_updated"]} | 👤 {r["design_by"]}</small></div>',
                    unsafe_allow_html=True)
            with co2:
                if r.get("design_file_path") and Path(r["design_file_path"]).exists():
                    dl_btn(r["design_file_path"], "⬇️ تحميل")
                elif r.get("design_link"):
                    st.markdown(f'[🔗 رابط]({r["design_link"]})')


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: PRODUCTION
# ─────────────────────────────────────────────────────────────────────────────

def pg_production():
    hdr("🖨️", "قسم الإنتاج", "نفّذ الأوردرات الجاهزة")
    guide("① الأوردر يظهر هنا فقط بعد رفع التصميم<br>② حمّل ملف التصميم واطبع<br>③ عند الانتهاء غيّر الحالة إلى مكتمل")
    WID  = wid()
    rows = qall("SELECT * FROM orders WHERE workspace_id=? ORDER BY id DESC", (WID,))
    ready    = [r for r in rows if r["design_status"]=="مكتمل" and r["production_status"]=="قيد الانتظار"]
    printing = [r for r in rows if r["production_status"]=="جاري الإنتاج"]
    done     = [r for r in rows if r["production_status"]=="مكتمل"]

    t1,t2,t3 = st.tabs([f"🟢 جاهز ({len(ready)})",f"🟠 جاري ({len(printing)})",f"✅ مكتمل ({len(done)})"])

    with t1:
        if not ready: st.info("⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم.")
        for r in ready:
            with st.expander(f"🟢 {r['order_number']}  —  {r['customer_name']}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**ملاحظات التصميم:** {r['design_notes'] or '—'}")
                c2.markdown(f"**صمّمه:** {r['design_by'] or '—'}")
                if r.get("design_file_path") and Path(r["design_file_path"]).exists():
                    dl_btn(r["design_file_path"], "⬇️ تحميل ملف التصميم للطباعة")
                elif r.get("design_link"):
                    st.markdown(f'[🔗 فتح رابط التصميم]({r["design_link"]})')
                pn = st.text_area("📝 ملاحظات الإنتاج", key=f"pn_{r['id']}", height=55)
                col1,col2 = st.columns(2)
                if col1.button("▶️ بدء الطباعة", key=f"st_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    qrun("UPDATE orders SET production_status='جاري الإنتاج',production_notes=?,production_updated=?,production_by=? WHERE id=?",
                         (pn, now, st.session_state["uname"], r["id"]))
                    sync_status(r["id"]); st.success("▶️ بدأ الإنتاج!"); st.rerun()
                if col2.button("✅ إتمام مباشر", key=f"fi_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    qrun("UPDATE orders SET production_status='مكتمل',production_notes=?,production_updated=?,production_by=? WHERE id=?",
                         (pn, now, st.session_state["uname"], r["id"]))
                    sync_status(r["id"]); st.success("✅ مكتمل!"); st.rerun()

    with t2:
        if not printing: st.info("لا توجد طباعة جارية.")
        for r in printing:
            with st.expander(f"🟠 {r['order_number']}  —  {r['customer_name']}"):
                st.markdown(f"**الوصف:** {r['description']} | **الكمية:** {r['quantity']}")
                if r.get("design_file_path") and Path(r["design_file_path"]).exists():
                    dl_btn(r["design_file_path"])
                if st.button("✅ تحديد كمكتمل", key=f"fn_{r['id']}"):
                    qrun("UPDATE orders SET production_status='مكتمل',production_updated=? WHERE id=?",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                    sync_status(r["id"]); st.success("✅ مكتمل!"); st.rerun()

    with t3:
        if not done: st.info("لا توجد أوردرات مكتملة.")
        for r in done:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{badge("مكتمل",ORD_BADGE)}'
                f'<br><small style="color:var(--t3)">اكتمل: {r["production_updated"]}</small></div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: PURCHASE
# ─────────────────────────────────────────────────────────────────────────────

def pg_purchase_submit():
    hdr("📦", "طلب شراء", "اطلب مواد أو أدوات من قسم المشتريات")
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
            qrun("INSERT INTO purchase_requests (workspace_id,requester_id,requester_name,department,item_name,quantity,urgency,notes) VALUES (?,?,?,?,?,?,?,?)",
                 (wid(), st.session_state["uid"], st.session_state["uname"],
                  ROLES[role]["ar"], item.strip(), qty.strip(), urg, notes.strip()))
            st.success("✅ تم إرسال طلب الشراء!")
    st.markdown("---")
    rows = qall("SELECT item_name,quantity,urgency,status,created_at FROM purchase_requests WHERE workspace_id=? AND requester_id=? ORDER BY id DESC LIMIT 10",
                (wid(), st.session_state["uid"]))
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={"item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية","status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("لم تقدم أي طلب بعد.")


def pg_purchase_manage():
    hdr("📦", "إدارة طلبات الشراء", "راجع وأدر جميع الطلبات الواردة")
    guide("① الطارئ والعاجل يظهران أولاً<br>② وافق أو ارفض كل طلب<br>③ السجل الكامل في تاب «السجل»")
    WID  = wid()
    rows = qall("""SELECT * FROM purchase_requests WHERE workspace_id=?
                   ORDER BY CASE urgency WHEN 'طارئ' THEN 0 WHEN 'عاجل' THEN 1 ELSE 2 END, id DESC""", (WID,))
    pend = [r for r in rows if r["status"] == "قيد المراجعة"]
    rest = [r for r in rows if r["status"] != "قيد المراجعة"]

    t1,t2 = st.tabs([f"⏳ قيد المراجعة ({len(pend)})", f"📋 السجل ({len(rest)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد طلبات معلقة!")
        for r in pend:
            uc = {"طارئ":"var(--red)","عاجل":"var(--acc2)","عادي":"var(--t2)"}.get(r["urgency"],"var(--t2)")
            with st.expander(f"📦 {r['item_name']} — {r['requester_name']} [{r['department']}]"):
                st.markdown(
                    f"**الصنف:** {r['item_name']} | **الكمية:** {r['quantity']}"
                    f"<br>**الأولوية:** <span style='color:{uc}'>{r['urgency']}</span>"
                    f" | **التاريخ:** {r['created_at']}"
                    f"{'<br>**ملاحظات:** '+r['notes'] if r['notes'] else ''}",
                    unsafe_allow_html=True)
                col1,col2 = st.columns(2)
                if col1.button("✅ موافقة", key=f"app_{r['id']}"):
                    qrun("UPDATE purchase_requests SET status='موافق عليه',reviewed_by=?,reviewed_at=? WHERE id=?",
                         (st.session_state["uname"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                    st.success("✅ موافق عليه."); st.rerun()
                if col2.button("❌ رفض", key=f"rej_{r['id']}"):
                    qrun("UPDATE purchase_requests SET status='مرفوض',reviewed_by=?,reviewed_at=? WHERE id=?",
                         (st.session_state["uname"], datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                    st.warning("تم الرفض."); st.rerun()
    with t2:
        if not rest: st.info("لا يوجد سجل.")
        else:
            df = pd.DataFrame(rest)[["requester_name","department","item_name","quantity","urgency","status","reviewed_by","created_at"]]
            st.dataframe(df.rename(columns={"requester_name":"الموظف","department":"القسم","item_name":"الصنف",
                                            "quantity":"الكمية","urgency":"الأولوية","status":"الحالة",
                                            "reviewed_by":"راجعه","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: AGENT
# ─────────────────────────────────────────────────────────────────────────────

def pg_agent_new():
    hdr("🗺️", "تسجيل زيارة عميل", "وثّق زيارتك الميدانية")
    guide("① سجّل كل زيارة مع صورة المحل<br>② حدّد حالة العميل بدقة<br>③ المدير يتابع أداءك من لوحته")
    with st.form("av", clear_on_submit=True):
        cust  = st.text_input("👤 اسم العميل / المحل *")
        loc   = st.text_input("📍 العنوان", placeholder="الشارع، الحي، المدينة")
        vs    = st.selectbox("📊 حالة العميل", ["محتمل","اشترى","لن يشتري"])
        notes = st.text_area("📝 ملاحظات", height=65)
        img   = st.file_uploader("📸 صورة المحل", type=["jpg","jpeg","png","webp"])
        sub   = st.form_submit_button("✅ حفظ الزيارة", use_container_width=True)
    if sub:
        if not cust.strip(): st.error("يرجى إدخال اسم العميل.")
        else:
            ip = save_upload(img, "agents") if img else ""
            qrun("INSERT INTO agent_visits (workspace_id,agent_id,agent_name,customer_name,location,visit_status,notes,image_path) VALUES (?,?,?,?,?,?,?,?)",
                 (wid(), st.session_state["uid"], st.session_state["uname"],
                  cust.strip(), loc.strip(), vs, notes.strip(), ip))
            st.success(f"✅ تم تسجيل زيارة **{cust.strip()}**!")


def pg_agent_my():
    hdr("📋", "زياراتي", "سجل زياراتك")
    rows = qall("SELECT * FROM agent_visits WHERE workspace_id=? AND agent_id=? ORDER BY id DESC",
                (wid(), st.session_state["uid"]))
    if not rows: st.info("لم تسجّل أي زيارة بعد."); return
    for r in rows:
        cls, lbl = AGT_BADGE.get(r["visit_status"], ("b-apot", r["visit_status"]))
        ih = ""
        if r.get("image_path") and Path(r["image_path"]).exists():
            raw = Path(r["image_path"]).read_bytes()
            b64 = base64.b64encode(raw).decode()
            ext = Path(r["image_path"]).suffix.lstrip(".") or "jpeg"
            ih  = (f'<br><img src="data:image/{ext};base64,{b64}" '
                   f'style="max-width:100%;max-height:155px;border-radius:8px;'
                   f'margin-top:.4rem;object-fit:cover">')
        st.markdown(
            f'<div class="card"><b>{r["customer_name"]}</b>&nbsp;<span class="badge {cls}">{lbl}</span>'
            f'<br><small style="color:var(--t2)">📍 {r["location"] or "—"} | 🗓 {r["visited_at"]}</small>'
            f'{"<br><small>"+r["notes"]+"</small>" if r["notes"] else ""}'
            f'{ih}</div>',
            unsafe_allow_html=True)


def pg_agent_reports():
    hdr("🗺️", "تقارير المندوبين", "أداء فريق المبيعات الميداني")
    rows = qall("""SELECT agent_name, COUNT(*) v,
        SUM(CASE WHEN visit_status='اشترى'     THEN 1 ELSE 0 END) bought,
        SUM(CASE WHEN visit_status='محتمل'      THEN 1 ELSE 0 END) pot,
        SUM(CASE WHEN visit_status='لن يشتري'  THEN 1 ELSE 0 END) nob,
        MAX(visited_at) lv
        FROM agent_visits WHERE workspace_id=? GROUP BY agent_id ORDER BY v DESC""", (wid(),))
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "agent_name":"المندوب","v":"الزيارات","bought":"اشترى",
            "pot":"محتمل","nob":"لن يشتري","lv":"آخر زيارة"
        }), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد زيارات.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: SHARED CHAT  — per-workspace, isolated
# ─────────────────────────────────────────────────────────────────────────────

def pg_chat():
    hdr("💬", "محادثة الفريق", "تواصل مع فريقك في نفس الشركة")
    guide("① المحادثة مشتركة بين جميع أقسام شركتك فقط<br>② لا يرى موظفو الشركات الأخرى رسائلك<br>③ يمكن مناقشة المهام والأوردرات هنا")
    WID = wid()
    uid = st.session_state["uid"]
    unm = st.session_state["uname"]
    rol = st.session_state["role"]

    # ── Send message ──
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("✍️ اكتب رسالتك...", placeholder="مناقشة مهمة، ملاحظة، سؤال...")
        sent = st.form_submit_button("إرسال ←", use_container_width=True)
    if sent and msg.strip():
        qrun("INSERT INTO chat_messages (workspace_id,sender_id,sender_name,sender_role,message) VALUES (?,?,?,?,?)",
             (WID, uid, unm, rol, msg.strip()))
        st.rerun()

    # ── Messages (last 60) ──
    msgs = qall("SELECT * FROM chat_messages WHERE workspace_id=? ORDER BY id DESC LIMIT 60", (WID,))
    msgs.reverse()

    if not msgs:
        st.info("لا توجد رسائل بعد. ابدأ المحادثة!")
        return

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for m in msgs:
        is_me = m["sender_id"] == uid
        ri    = ROLES.get(m["sender_role"], {"clr": "#e8a020"})
        cls   = "me" if is_me else "other"
        name_color = ri["clr"]
        st.markdown(
            f'<div class="bubble {cls}">'
            f'<div class="bname" style="color:{name_color}">'
            f'{m["sender_name"]} · {ROLES.get(m["sender_role"],{"ar":m["sender_role"]})["ar"]}'
            f'</div>'
            f'{m["message"]}'
            f'<div class="btime">{m["sent_at"]}</div>'
            f'</div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: INCIDENTS
# ─────────────────────────────────────────────────────────────────────────────

def pg_incident_submit():
    role = st.session_state["role"]
    hdr("🚨", "بلاغ خلل أو نقص", "أبلغ المدير عن أي مشكلة")
    with st.form("inc", clear_on_submit=True):
        desc = st.text_area("📝 وصف المشكلة *", placeholder="نقص حبر، عطل طابعة...")
        sev  = st.selectbox("⚠️ الخطورة", ["منخفض","متوسط","عالي"])
        sub  = st.form_submit_button("📤 إرسال", use_container_width=True)
    if sub:
        if not desc.strip(): st.error("يرجى كتابة الوصف.")
        else:
            qrun("INSERT INTO incident_reports (workspace_id,reporter_id,reporter_name,department,description,severity) VALUES (?,?,?,?,?,?)",
                 (wid(), st.session_state["uid"], st.session_state["uname"],
                  ROLES[role]["ar"], desc.strip(), sev))
            st.success("✅ تم إرسال البلاغ للمدير!")
    st.markdown("---")
    rows = qall("SELECT description,severity,status,created_at FROM incident_reports WHERE workspace_id=? AND reporter_id=? ORDER BY id DESC LIMIT 8",
                (wid(), st.session_state["uid"]))
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


def pg_all_incidents():
    hdr("🚨", "بلاغات الأعطال", "جميع البلاغات الواردة")
    rows = qall("SELECT * FROM incident_reports WHERE workspace_id=? ORDER BY id DESC", (wid(),))
    if not rows: st.success("🎉 لا توجد بلاغات!"); return
    op = [r for r in rows if r["status"]=="مفتوح"]
    rs = [r for r in rows if r["status"]=="محلول"]
    t1,t2 = st.tabs([f"🔴 مفتوحة ({len(op)})", f"✅ محلولة ({len(rs)})"])
    for tab, lst in [(t1, op), (t2, rs)]:
        with tab:
            if not lst: st.info("لا توجد."); continue
            for r in lst:
                sc, sl = SEV_BADGE.get(r["severity"], ("b-sev-md", r["severity"]))
                with st.expander(f'{sl} {r["severity"]}  —  {r["department"]}  —  {r["created_at"][:16]}'):
                    st.markdown(f"**المبلّغ:** {r['reporter_name']}<br>**الوصف:** {r['description']}", unsafe_allow_html=True)
                    if r["status"] == "مفتوح":
                        if st.button("✅ محلول", key=f"rs_{r['id']}"):
                            qrun("UPDATE incident_reports SET status='محلول',resolved_at=? WHERE id=?",
                                 (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), r["id"]))
                            st.rerun()
                    else:
                        st.caption(f"تم الحل: {r['resolved_at']}")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: FINANCIAL
# ─────────────────────────────────────────────────────────────────────────────

def pg_financial():
    hdr("💰", "التقارير المالية", "للمبيعات ومدير الشركة فقط")
    WID = wid()
    tv  = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE workspace_id=?", (WID,)) or {}).get("s",0)
    rv  = (qone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE workspace_id=? AND status IN ('مكتمل','تم التسليم')", (WID,)) or {}).get("s",0)
    cnt = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=?", (WID,)) or {}).get("c",0)
    avg = tv / cnt if cnt else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي القيمة (د.ع)",   f"{tv:,.0f}")
    c2.metric("محصّل من مكتملة (د.ع)", f"{rv:,.0f}")
    c3.metric("قيد التنفيذ (د.ع)",      f"{tv-rv:,.0f}")
    c4.metric("متوسط الأوردر (د.ع)",   f"{avg:,.0f}")
    st.markdown("---")
    rows = qall("SELECT order_number,customer_name,quantity,price,status,created_at FROM orders WHERE workspace_id=? ORDER BY id DESC", (WID,))
    if not rows: st.info("لا توجد أوردرات."); return
    df = pd.DataFrame(rows)
    st.dataframe(df.rename(columns={
        "order_number":"الأوردر","customer_name":"العميل","quantity":"الكمية",
        "price":"السعر (د.ع)","status":"الحالة","created_at":"التاريخ"
    }), use_container_width=True, hide_index=True)
    ws_name = st.session_state.get("workspace_name","")
    header  = (f"Z-ORDER — تقرير مالي\n"
               f"Workspace: {ws_name}\n"
               f"Developed by: {DEVELOPER}\n"
               f"تاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    st.download_button("⬇️ تصدير CSV",
        (header + df.to_csv(index=False)).encode("utf-8-sig"),
        file_name=f"zorder_fin_{datetime.date.today()}.csv",
        mime="text/csv", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES: GENERIC DASHBOARD (design / purchase / production / agent)
# ─────────────────────────────────────────────────────────────────────────────

def pg_generic_dash(role):
    hdr("📊", "لوحتي", "نظرة عامة")
    guide(ROLES[role]["ar"] + " — " + "① راجع مهامك من القائمة أعلاه<br>② استخدم «بلاغ» لإبلاغ المدير")
    WID = wid()
    tot = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=?", (WID,)) or {}).get("c",0)
    nw  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND status='جديد'", (WID,)) or {}).get("c",0)
    ip  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND production_status='جاري الإنتاج'", (WID,)) or {}).get("c",0)
    dn  = (qone("SELECT COUNT(*) c FROM orders WHERE workspace_id=? AND status IN ('مكتمل','تم التسليم')", (WID,)) or {}).get("c",0)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي",tot); c2.metric("جديدة",nw); c3.metric("جاري",ip); c4.metric("مكتملة",dn)
    st.markdown("---")
    rows = qall("SELECT order_number,customer_name,description,quantity,status,created_at FROM orders WHERE workspace_id=? ORDER BY id DESC LIMIT 10", (WID,))
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "order_number":"الأوردر","customer_name":"العميل","description":"الوصف",
            "quantity":"الكمية","status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    init_db()

    # ── GATEKEEPER — blocks everything until login ──
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
    elif role == "admin" and active == "📊 الرئيسية": pg_admin_dash()
    elif role == "admin" and active == "👥 الفريق":   pg_team()
    elif role == "admin" and active == "📋 الأوردرات": show_orders("admin", title="جميع الأوردرات")
    elif role == "admin" and active == "💰 المالية":   pg_financial()
    elif role == "admin" and active == "🚨 البلاغات":  pg_all_incidents()
    elif role == "admin" and active == "🗺️ المندوبون": pg_agent_reports()
    elif role == "admin" and active == "💬 المحادثة":  pg_chat()
    elif role == "admin" and active == "📞 الدعم الفني": pg_support()

    # ── SALES ──────────────────────────────────────────────────────────────
    elif role == "sales" and active == "📊 الرئيسية":     pg_sales_dash()
    elif active == "➕ أوردر جديد":                        pg_add_order()
    elif active == "📋 أوردراتي":                          show_orders("sales", uid_filter=st.session_state["uid"], title="أوردراتي")
    elif active == "🖼️ معاينة التصاميم":                   pg_sales_design_preview()
    elif role == "sales" and active == "💰 تقريري":        pg_financial()

    # ── DESIGN ─────────────────────────────────────────────────────────────
    elif role == "design" and active == "📊 الرئيسية": pg_generic_dash(role)
    elif active == "🎨 التصميم":                        pg_design()

    # ── PURCHASE ───────────────────────────────────────────────────────────
    elif role == "purchase" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "📦 طلبات الشراء":                      pg_purchase_manage()

    # ── PRODUCTION ─────────────────────────────────────────────────────────
    elif role == "production" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "🖨️ الإنتاج":                             pg_production()
    elif role == "production" and active == "📋 الأوردرات": show_orders("production", title="الأوردرات")

    # ── AGENT ──────────────────────────────────────────────────────────────
    elif role == "agent" and active == "📊 الرئيسية":  pg_generic_dash(role)
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


# ─────────────────────────────────────────────────────────────────────────────
#  SUPABASE MIGRATION GUIDE
# ─────────────────────────────────────────────────────────────────────────────
"""
══════════════════════════════════════════════════════════════════
  SUPABASE MIGRATION — كيف تنقل قاعدة البيانات إلى السحابة
══════════════════════════════════════════════════════════════════

الخطوة 1: أنشئ مشروعاً مجانياً على https://supabase.com

الخطوة 2: ثبّت المكتبة:
    pip install supabase

الخطوة 3: في الملف، استبدل دوال SQLite بالدوال التالية:

    from supabase import create_client
    SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
    SUPABASE_KEY = "YOUR_ANON_KEY"          # من Settings > API
    supa = create_client(SUPABASE_URL, SUPABASE_KEY)

    # بدلاً من qall():
    def qall_sb(table, filters={}):
        q = supa.table(table).select("*")
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute().data

    # بدلاً من qrun():
    def qrun_sb(table, data):
        return supa.table(table).insert(data).execute()

الخطوة 4: الملفات (التصاميم) — استخدم Supabase Storage:
    supa.storage.from_("designs").upload(filename, file_bytes)
    url = supa.storage.from_("designs").get_public_url(filename)

الخطوة 5: استمرارية البيانات محققة تلقائياً عبر Supabase PostgreSQL.
     كل تحديث للكود لا يمسّ قاعدة البيانات السحابية.

الخطوة 6: للمصادقة المتقدمة:
    supa.auth.sign_in_with_password({"email": e, "password": p})

══════════════════════════════════════════════════════════════════
  GOOGLE PLAY READINESS
══════════════════════════════════════════════════════════════════
الخيار الأسهل: نشر التطبيق على Streamlit Cloud أو Railway،
ثم تغليفه بـ Progressive Web App (PWA) باستخدام أداة مثل:
    https://bubblewrap.io  أو  https://capacitorjs.com
مما يتيح رفعه على Google Play كـ Trusted Web Activity.
══════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    main()
