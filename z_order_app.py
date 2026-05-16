"""
╔══════════════════════════════════════════════════════════════════════════╗
║   Z-ORDER V2  ·  Built for Organized Teams  ·  v2.0  FINAL            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Developer  : Abdulrahman Fallah  ©  2026                              ║
║  Backend    : Supabase  (PostgreSQL · Auth · Storage)                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  pip install streamlit requests pandas                                  ║
║  streamlit run z_order_app.py                                           ║
║                                                                         ║
║  Platform Super-Admin (built-in):                                       ║
║    Email    : admin@zorder.iq    Password : Admin@2025                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import streamlit as st
import hashlib, datetime, random, string, base64, requests, uuid, os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# ── Page config (first Streamlit call) ───────────────────────────────────────
st.set_page_config(
    page_title="Z-ORDER | Built for Organized Teams",
    page_icon="https://raw.githubusercontent.com/abdullrhmanback-cloud/Z-ORDER-APP/refs/heads/main/IMG_5574.PNG",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
DEVELOPER     = "Abdulrahman Fallah"
APP_NAME      = "Z-ORDER V2"
APP_TAGLINE   = "Built for Organized Teams"
APP_VER       = "2.0"
YEAR          = "2026"
SUPPORT_WA    = "https://wa.me/9647768723110"
SUPPORT_PHONE = "+964 776 872 3110"

# Supabase
SUPA_URL    = "https://iiytcythowpemjxcxfsf.supabase.co"
SUPA_KEY    = "sb_publishable_0cJhgmY3C3Q5KfdVp6R0aQ_3t0gvuuz"
REST        = f"{SUPA_URL}/rest/v1"
AUTH        = f"{SUPA_URL}/auth/v1"
STORE       = f"{SUPA_URL}/storage/v1"
BUCKET      = "designs"

# ── SMTP Email Config — loaded from Streamlit Secrets ────────────────────────
# In .streamlit/secrets.toml:
#   SMTP_SERVER   = "smtp.gmail.com"
#   SMTP_PORT     = 587
#   SENDER_EMAIL  = "abdullrhmanback@gmail.com"
#   SENDER_PASSWORD = "cnyv mmrh wktl yrwb"
try:
    SMTP_SERVER      = st.secrets["SMTP_SERVER"]
    SMTP_PORT        = int(st.secrets["SMTP_PORT"])
    SENDER_EMAIL     = st.secrets["SENDER_EMAIL"]
    SENDER_PASSWORD  = st.secrets["SENDER_PASSWORD"]
except Exception:
    # Fallback defaults — override via Streamlit Secrets in production
    SMTP_SERVER      = "smtp.gmail.com"
    SMTP_PORT        = 587
    SENDER_EMAIL     = "abdullrhmanback@gmail.com"
    SENDER_PASSWORD  = "cnyv mmrh wktl yrwb"

RH = {          # REST headers
    "apikey":        SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

# Platform super-admin (hard-coded, NOT in database)
SA_EMAIL = "admin@zorder.iq"
SA_PASS  = "Admin@2025"

# Roles
ROLES = {
    "superadmin": {"ar":"المشرف العام",   "icon":"⭐","clr":"#ffd166"},
    "admin":      {"ar":"مدير الشركة",    "icon":"🛡️","clr":"#e8a020"},
    "sales":      {"ar":"المبيعات",        "icon":"💼","clr":"#3b82f6"},
    "design":     {"ar":"التصميم",         "icon":"🎨","clr":"#a855f7"},
    "purchase":   {"ar":"المشتريات",       "icon":"📦","clr":"#22c55e"},
    "production": {"ar":"الإنتاج",         "icon":"🖨️","clr":"#ff6b35"},
    "agent":      {"ar":"مندوب مبيعات",   "icon":"🗺️","clr":"#06b6d4"},
}

ROLE_PAGES = {
    "superadmin": ["📊 لوحة التحكم","🏢 الشركات","👥 المستخدمون","📈 الإحصائيات"],
    "admin":      ["📊 الرئيسية","👥 الفريق","📋 الأوردرات","💰 المالية",
                   "🔔 الإشعارات","🚨 البلاغات","🗺️ المندوبون","💬 المحادثة","📞 تواصل معنا"],
    "sales":      ["📊 الرئيسية","➕ أوردر جديد","📋 أوردراتي","🖼️ التصاميم",
                   "💰 تقريري","📦 طلب شراء","🔔 إشعاراتي","💬 المحادثة","🚨 بلاغ"],
    "design":     ["📊 الرئيسية","🎨 التصميم","🖼️ Mockup للمبيعات","🔔 إشعاراتي","💬 المحادثة","📦 طلب شراء","🚨 بلاغ"],
    "purchase":   ["📊 الرئيسية","📦 طلبات الشراء","💬 المحادثة","🚨 بلاغ"],
    "production": ["📊 الرئيسية","🖨️ الإنتاج","📋 الأوردرات","🔔 إشعاراتي","💬 المحادثة","📦 طلب شراء","🚨 بلاغ"],
    "agent":      ["📊 الرئيسية","➕ أوردر ميداني","🗺️ زيارة جديدة","📋 زياراتي","💬 المحادثة","🚨 بلاغ"],
}

# Order status progression (for notifications)
STATUS_FLOW = ["جديد","قيد التصميم","جاهز للطباعة","جاري الإنتاج","جاهز للتسليم","تم التسليم"]

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS  — Dark Gold · Mobile-First · Android Ready
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
:root{
  --bg0:#060708;--bg1:#0a0c11;--bg2:#0e1118;--bg3:#13161f;
  --bg4:#181c27;--bg5:#1d2230;
  --bdr:#1a1f2e;--bdr2:#232a3d;
  --gold:#e8a020;--g2:#ffd166;--acc2:#ff6b35;
  --blue:#3b82f6;--grn:#22c55e;--red:#ef4444;--pur:#a855f7;--cy:#06b6d4;
  --t1:#f0f2f8;--t2:#8590a8;--t3:#3a4258;
  --r:10px;--r2:14px;--r3:20px;
  --sh:0 4px 24px rgba(0,0,0,.5);
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{
  font-family:'IBM Plex Sans Arabic',sans-serif !important;
  background:var(--bg0) !important;color:var(--t1) !important;direction:rtl !important;}
section[data-testid="stSidebar"]{display:none !important;}
[data-testid="collapsedControl"]{display:none !important;}
.stApp{background:var(--bg0) !important;}
.main .block-container{padding:0 !important;max-width:100% !important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg1);}
::-webkit-scrollbar-thumb{background:var(--bg5);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--gold);}

/* ─ Inputs ─ */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,
.stSelectbox>div>div,.stNumberInput>div>div>input{
  background:var(--bg3) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r) !important;color:var(--t1) !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;font-size:.9rem !important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
  border-color:var(--gold) !important;box-shadow:0 0 0 3px rgba(232,160,32,.12) !important;}

/* ─ Buttons ─ */
.stButton>button{
  background:linear-gradient(135deg,var(--gold),var(--acc2)) !important;
  color:#06070a !important;font-weight:700 !important;border:none !important;
  border-radius:var(--r) !important;padding:.6rem 1.2rem !important;
  min-height:46px !important;width:100% !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;
  transition:transform .15s,box-shadow .18s !important;cursor:pointer;}
.stButton>button:hover{transform:translateY(-2px) !important;
  box-shadow:0 8px 24px rgba(232,160,32,.38) !important;}
.stButton>button:active{transform:translateY(0) !important;}

/* ─ Tabs ─ */
.stTabs [data-baseweb="tab-list"]{background:var(--bg3) !important;
  border-radius:var(--r) !important;gap:3px !important;padding:4px !important;
  border:1px solid var(--bdr) !important;overflow-x:auto !important;flex-wrap:nowrap !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:var(--t2) !important;
  border-radius:7px !important;font-size:.82rem !important;border:none !important;white-space:nowrap !important;}
.stTabs [aria-selected="true"]{background:var(--bg5) !important;color:var(--gold) !important;
  border-bottom:2px solid var(--gold) !important;}

/* ─ Metrics ─ */
[data-testid="stMetric"]{background:var(--bg2) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r2) !important;padding:.85rem 1rem !important;}
[data-testid="stMetricLabel"]{color:var(--t2) !important;font-size:.71rem !important;}
[data-testid="stMetricValue"]{color:var(--gold) !important;
  font-family:'JetBrains Mono',monospace !important;font-size:1.25rem !important;}

/* ─ Expanders ─ */
.streamlit-expanderHeader{background:var(--bg2) !important;border:1px solid var(--bdr2) !important;
  border-radius:var(--r) !important;font-size:.88rem !important;}
.streamlit-expanderContent{background:var(--bg1) !important;border:1px solid var(--bdr2) !important;
  border-top:none !important;}

/* ─ Tables ─ */
.stDataFrame,[data-testid="stDataFrame"],iframe[title="st.dataframe"]{
  width:100% !important;border-radius:var(--r) !important;
  border:1px solid var(--bdr) !important;overflow-x:auto !important;}

/* ─ File uploader ─ */
[data-testid="stFileUploader"]{background:var(--bg3) !important;
  border:1.5px dashed var(--bdr2) !important;border-radius:var(--r) !important;}
.stAlert{background:var(--bg2) !important;border-radius:var(--r) !important;}
hr{border-color:var(--bdr) !important;margin:.85rem 0 !important;}

/* ═══ COMPONENT LIBRARY ═══════════════════════════════════════════════════ */

/* ─ Top bar ─ */
.topbar{position:sticky;top:0;z-index:999;background:var(--bg1);
  border-bottom:1px solid var(--bdr);padding:.48rem 1.1rem;
  display:flex;align-items:center;gap:.6rem;overflow-x:auto;flex-wrap:nowrap;}
.zlogo{font-family:'JetBrains Mono',monospace;font-size:1.3rem;font-weight:700;
  color:var(--gold);letter-spacing:-.06em;line-height:1;white-space:nowrap;flex-shrink:0;}
.zlogo .sep{color:var(--t3);}
.zlogo .tag{font-family:'IBM Plex Sans Arabic',sans-serif;font-size:.56rem;
  font-weight:400;color:var(--t3);display:block;margin-top:1px;}
.uchip{display:flex;align-items:center;gap:.42rem;background:var(--bg3);
  border:1px solid var(--bdr2);border-radius:999px;padding:.28rem .7rem .28rem .32rem;
  white-space:nowrap;flex-shrink:0;margin-right:auto;}
.uav{width:26px;height:26px;background:linear-gradient(135deg,var(--gold),var(--acc2));
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.7rem;font-weight:700;color:#06070a;flex-shrink:0;}

/* ─ Notification bell ─ */
.notif-bell{position:relative;display:inline-flex;align-items:center;
  justify-content:center;cursor:pointer;flex-shrink:0;}
.notif-count{position:absolute;top:-4px;right:-4px;background:var(--red);
  color:#fff;border-radius:999px;font-size:.58rem;font-weight:700;
  min-width:16px;height:16px;display:flex;align-items:center;justify-content:center;
  padding:0 3px;}

/* ─ Page content ─ */
.pw{padding:1rem 1.3rem 7rem;max-width:1280px;margin:0 auto;}

/* ─ Page header ─ */
.ph{display:flex;align-items:center;gap:.7rem;margin-bottom:1.1rem;}
.ph-icon{font-size:1.5rem;background:var(--bg2);border:1px solid var(--bdr2);
  border-radius:var(--r);width:46px;height:46px;display:flex;
  align-items:center;justify-content:center;flex-shrink:0;}
.ph h2{font-size:1.1rem;font-weight:700;color:var(--t1);margin:0;}
.ph p{font-size:.72rem;color:var(--t3);margin:0;}

/* ─ Cards ─ */
.card{background:var(--bg2);border:1px solid var(--bdr2);border-radius:var(--r2);
  padding:.95rem 1.15rem;margin-bottom:.6rem;transition:border-color .2s,transform .12s;}
.card:hover{border-color:var(--gold);transform:translateY(-1px);}
.icard{background:linear-gradient(135deg,rgba(232,160,32,.07),rgba(255,107,53,.04));
  border:1px solid rgba(232,160,32,.2);border-right:3px solid var(--gold);
  border-radius:var(--r2);padding:.8rem 1.05rem;margin-bottom:.85rem;
  font-size:.81rem;color:var(--t2);line-height:1.82;}

/* ─ Notification card ─ */
.notif-item{display:flex;align-items:flex-start;gap:.6rem;
  background:var(--bg2);border:1px solid var(--bdr2);border-radius:var(--r);
  padding:.7rem .9rem;margin-bottom:.5rem;}
.notif-item.unread{border-color:rgba(232,160,32,.3);background:rgba(232,160,32,.05);}
.notif-dot{width:8px;height:8px;border-radius:50%;background:var(--gold);
  flex-shrink:0;margin-top:5px;}
.notif-dot.read{background:var(--t3);}

/* ─ Status badge pills ─ */
.badge{display:inline-flex;align-items:center;gap:3px;padding:.16rem .55rem;
  border-radius:999px;font-size:.62rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;}
.b-new   {background:rgba(59,130,246,.14);color:#60a5fa;border:1px solid rgba(59,130,246,.25);}
.b-des   {background:rgba(168,85,247,.14); color:#c084fc;border:1px solid rgba(168,85,247,.25);}
.b-rdy   {background:rgba(34,197,94,.14);  color:#4ade80;border:1px solid rgba(34,197,94,.25);}
.b-prt   {background:rgba(255,107,53,.14); color:#fb923c;border:1px solid rgba(255,107,53,.25);}
.b-del   {background:rgba(6,182,212,.12);  color:#06b6d4;border:1px solid rgba(6,182,212,.2);}
.b-done  {background:rgba(34,197,94,.1);   color:#16a34a;border:1px solid rgba(34,197,94,.2);}
.b-pend  {background:rgba(251,191,36,.12); color:#fbbf24;border:1px solid rgba(251,191,36,.2);}
.b-appr  {background:rgba(34,197,94,.12);  color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-rej   {background:rgba(239,68,68,.12);  color:#ef4444;border:1px solid rgba(239,68,68,.2);}
.b-sev-lo{background:rgba(34,197,94,.12);  color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-sev-md{background:rgba(251,191,36,.12); color:#fbbf24;border:1px solid rgba(251,191,36,.2);}
.b-sev-hi{background:rgba(239,68,68,.12);  color:#ef4444;border:1px solid rgba(239,68,68,.2);}
.b-abuy  {background:rgba(34,197,94,.12);  color:#22c55e;border:1px solid rgba(34,197,94,.2);}
.b-apot  {background:rgba(59,130,246,.12); color:#3b82f6;border:1px solid rgba(59,130,246,.2);}
.b-ano   {background:rgba(239,68,68,.12);  color:#ef4444;border:1px solid rgba(239,68,68,.2);}

/* ─ Progress tracker ─ */
.tracker{display:flex;align-items:center;gap:0;margin:.5rem 0;}
.tr-step{flex:1;text-align:center;font-size:.6rem;color:var(--t3);position:relative;}
.tr-step::before{content:"";display:block;width:20px;height:20px;border-radius:50%;
  background:var(--bg4);border:2px solid var(--bdr2);margin:0 auto .25rem;}
.tr-step::after{content:"";position:absolute;top:9px;right:50%;
  width:100%;height:2px;background:var(--bdr2);z-index:-1;}
.tr-step:last-child::after{display:none;}
.tr-step.done::before{background:var(--gold);border-color:var(--gold);}
.tr-step.done::after{background:var(--gold);}
.tr-step.active::before{background:rgba(232,160,32,.2);border-color:var(--gold);}

/* ─ Support card ─ */
.support-card{background:linear-gradient(135deg,rgba(34,197,94,.06),rgba(6,182,212,.04));
  border:1px solid rgba(34,197,94,.2);border-radius:var(--r2);
  padding:1.5rem 1.4rem;text-align:center;}
.wa-btn{display:inline-flex;align-items:center;gap:.5rem;background:#25D366;
  color:#fff !important;padding:.65rem 1.5rem;border-radius:var(--r);
  font-weight:700;text-decoration:none;font-size:.9rem;margin-top:.75rem;transition:opacity .2s;}
.wa-btn:hover{opacity:.85;}

/* ─ Chat ─ */
.chat-wrap{display:flex;flex-direction:column;gap:.5rem;
  margin-bottom:1rem;max-height:400px;overflow-y:auto;padding:.3rem;}
.bubble{max-width:76%;padding:.52rem .82rem;border-radius:var(--r2);
  font-size:.84rem;line-height:1.5;}
.bubble.me   {background:rgba(232,160,32,.15);border:1px solid rgba(232,160,32,.2);align-self:flex-start;}
.bubble.other{background:var(--bg3);border:1px solid var(--bdr2);align-self:flex-end;}
.bubble .bn  {font-size:.62rem;font-weight:700;color:var(--gold);margin-bottom:2px;}
.bubble .bt  {font-size:.58rem;color:var(--t3);margin-top:3px;}

/* ─ Auth screens ─ */
.logo-big{font-family:'JetBrains Mono',monospace;font-size:2.3rem;font-weight:700;
  color:var(--gold);letter-spacing:-.07em;text-align:center;line-height:1;}
.logo-big .sep{color:var(--t3);}
.logo-tag{text-align:center;font-size:.7rem;color:var(--t3);
  letter-spacing:.12em;text-transform:uppercase;margin-top:.35rem;}
.auth-box{background:var(--bg2);border:1px solid var(--bdr2);
  border-radius:var(--r3);padding:1.75rem 1.5rem;}

/* ─ Step bar ─ */
.sbar{display:flex;gap:.4rem;margin-bottom:1.1rem;}
.sbr{flex:1;height:4px;border-radius:2px;background:var(--bdr2);}
.sbr.done{background:var(--gold);}
.sbr.act{background:linear-gradient(90deg,var(--gold),var(--acc2));}

/* ─ Nav selectbox ─ */
.nav-sel .stSelectbox>div>div{background:var(--bg2) !important;
  border:1px solid var(--gold) !important;font-weight:600 !important;
  font-size:.86rem !important;border-radius:var(--r) !important;}

/* ─ Section label ─ */
.sec{font-size:.66rem;font-weight:700;color:var(--t3);
  text-transform:uppercase;letter-spacing:.1em;margin:.8rem 0 .4rem;}

/* ─ Footer ─ */
.footer{position:fixed;bottom:0;left:0;right:0;background:var(--bg1);
  border-top:1px solid var(--bdr);padding:.42rem 1.1rem;
  display:flex;align-items:center;justify-content:space-between;
  font-size:.64rem;color:var(--t3);z-index:9999;gap:.35rem;flex-wrap:wrap;}
.footer .hi{color:var(--gold);font-weight:600;}

/* ─ Order form summary box ─ */
.order-summary{background:var(--bg3);border:1px solid var(--bdr2);border-radius:var(--r2);
  padding:1rem;margin-top:.75rem;}
.order-summary table{width:100%;border-collapse:collapse;}
.order-summary td{padding:.3rem .4rem;font-size:.84rem;}
.order-summary td:last-child{text-align:left;color:var(--gold);font-weight:600;
  font-family:'JetBrains Mono',monospace;}
.order-summary .total-row td{border-top:1px solid var(--bdr2);font-weight:700;
  font-size:.95rem;padding-top:.55rem;}

/* ═══ MOBILE ≤ 768px — Comprehensive Responsive Fix ═══════════════════ */
@media(max-width:768px){

  /* ── Content padding ── */
  .pw{padding:.5rem .3rem 7rem !important;}

  /* ── Page header smaller ── */
  .ph-icon{width:32px;height:32px;font-size:1rem;}
  .ph h2{font-size:.9rem;}
  .ph p{font-size:.66rem;}

  /* ── ALL columns stack vertically — core fix ── */
  [data-testid="column"]{
    width:100% !important;
    flex:0 0 100% !important;
    min-width:100% !important;
    padding:2px 0 !important;
  }

  /* ── Buttons: full width, touch-friendly ── */
  .stButton>button{
    font-size:.82rem !important;
    min-height:50px !important;
    margin-bottom:4px !important;
    padding:.55rem .7rem !important;
  }

  /* ── Inputs larger touch targets ── */
  .stTextInput>div>div>input,
  .stTextArea>div>div>textarea,
  .stSelectbox>div>div,
  .stNumberInput>div>div>input{
    font-size:.9rem !important;
    padding:.55rem .7rem !important;
  }

  /* ── Metrics compact ── */
  [data-testid="stMetricValue"]{font-size:.95rem !important;}
  [data-testid="stMetric"]{padding:.65rem .75rem !important;}

  /* ── Tables: horizontal scroll on mobile ── */
  .stDataFrame,[data-testid="stDataFrame"],iframe[title="st.dataframe"]{
    overflow-x:auto !important;
    display:block !important;
    width:100% !important;
    font-size:.76rem !important;
  }

  /* ── Top bar ── */
  .topbar{
    padding:.38rem .45rem !important;
    gap:.4rem !important;
  }
  .zlogo{font-size:1.05rem !important;}
  .zlogo .tag{display:none !important;}   /* hide tagline on small screens */
  .uchip{padding:.22rem .55rem .22rem .28rem !important;}

  /* ── Footer ── */
  .footer{font-size:.55rem !important;padding:.28rem .45rem !important;}

  /* ── Chat bubbles ── */
  .bubble{max-width:94% !important;}

  /* ── Order summary table ── */
  .order-summary{padding:.65rem .5rem !important;}
  .order-summary td{font-size:.75rem !important;padding:.22rem .3rem !important;}

  /* ── Auth box ── */
  .auth-box{padding:1.2rem .9rem !important;}
  .logo-big{font-size:1.75rem !important;}

  /* ── Expanders ── */
  .streamlit-expanderHeader{font-size:.82rem !important;}

  /* ── Tabs: horizontal scroll ── */
  .stTabs [data-baseweb="tab-list"]{
    overflow-x:auto !important;
    flex-wrap:nowrap !important;
    -webkit-overflow-scrolling:touch !important;
  }
  .stTabs [data-baseweb="tab"]{
    font-size:.72rem !important;
    padding:.3rem .45rem !important;
    white-space:nowrap !important;
  }

  /* ── Nav selectbox ── */
  .nav-sel .stSelectbox>div>div{font-size:.8rem !important;}

  /* ── Status tracker: hide connector lines on mobile ── */
  .tracker{flex-wrap:wrap;gap:.3rem;}
  .tr-step::after{display:none;}

  /* ── Notification items ── */
  .notif-item{padding:.55rem .7rem !important;}

  /* ── Cards ── */
  .card{padding:.75rem .85rem !important;}
}

/* ═══ SMALL PHONES ≤ 380px ═══════════════════════════════════════════════ */
@media(max-width:380px){
  .pw{padding:.4rem .2rem 7rem !important;}
  .ph h2{font-size:.82rem;}
  .stButton>button{font-size:.76rem !important;}
  .zlogo{font-size:.95rem !important;}
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PWA + AUDIO NOTIFICATIONS + BADGE API + @MENTION TAGGING
#  Injected once via st.components — works on Android Chrome & iOS Safari PWA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<!-- PWA Manifest (inline) — Z ORDER icon + name -->
<link rel="manifest" href="data:application/manifest+json,{
  &quot;name&quot;: &quot;Z ORDER&quot;,
  &quot;short_name&quot;: &quot;Z ORDER&quot;,
  &quot;start_url&quot;: &quot;/&quot;,
  &quot;display&quot;: &quot;standalone&quot;,
  &quot;background_color&quot;: &quot;#060708&quot;,
  &quot;theme_color&quot;: &quot;#e8a020&quot;,
  &quot;icons&quot;: [
    {
      &quot;src&quot;: &quot;https://raw.githubusercontent.com/abdullrhmanback-cloud/Z-ORDER-APP/refs/heads/main/IMG_5574.PNG&quot;,
      &quot;sizes&quot;: &quot;192x192&quot;,
      &quot;type&quot;: &quot;image/png&quot;,
      &quot;purpose&quot;: &quot;any maskable&quot;
    },
    {
      &quot;src&quot;: &quot;https://raw.githubusercontent.com/abdullrhmanback-cloud/Z-ORDER-APP/refs/heads/main/IMG_5574.PNG&quot;,
      &quot;sizes&quot;: &quot;512x512&quot;,
      &quot;type&quot;: &quot;image/png&quot;,
      &quot;purpose&quot;: &quot;any maskable&quot;
    }
  ]
}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Z ORDER">
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/abdullrhmanback-cloud/Z-ORDER-APP/refs/heads/main/IMG_5574.PNG">
<meta name="theme-color" content="#e8a020">

<script>
// ── Audio Notification (beep on new order/message) ──────────────────────────
function zPlayBeep(freq=880, dur=180) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain= ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.frequency.value = freq;
    osc.type = 'sine';
    gain.gain.setValueAtTime(0.5, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur/1000);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + dur/1000);
  } catch(e) {}
}
window.zPlayBeep = zPlayBeep;

// ── Request browser notification permission on load ──────────────────────────
function zRequestNotifPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then(p => {
      if (p === 'granted') console.log('[Z-ORDER] Notifications granted');
    });
  }
}
zRequestNotifPermission();

// ── Show browser push notification ──────────────────────────────────────────
function zShowNotif(title, body) {
  zPlayBeep();
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, { body: body, icon: '/favicon.ico', badge: '/favicon.ico' });
  }
}
window.zShowNotif = zShowNotif;

// ── App Badging API (Android/Desktop PWA) ───────────────────────────────────
function zSetBadge(count) {
  if ('setAppBadge' in navigator) {
    if (count > 0) navigator.setAppBadge(count).catch(()=>{});
    else           navigator.clearAppBadge().catch(()=>{});
  }
}
window.zSetBadge = zSetBadge;

// ── @mention detector in chat ────────────────────────────────────────────────
// Called from Python via streamlit.js bridge when a chat message is sent.
// Scans message for @role tags and triggers a notification.
function zCheckMention(message, currentRole) {
  const roles = ['المبيعات','التصميم','الإنتاج','المشتريات','مندوب','مدير','admin','sales','design','production','purchase'];
  for (const r of roles) {
    if (message.includes('@' + r)) {
      zShowNotif('تاغ جديد في المحادثة', `تم تاغ ${r}: ${message.substring(0,60)}`);
      break;
    }
  }
}
window.zCheckMention = zCheckMention;

// ── Service Worker registration (for offline PWA) ───────────────────────────
if ('serviceWorker' in navigator) {
  const swCode = `
    self.addEventListener('fetch', e => {});
    self.addEventListener('push', e => {
      const data = e.data ? e.data.json() : {};
      self.registration.showNotification(data.title || 'Z-ORDER', {
        body: data.body || '',
        icon: '/favicon.ico'
      });
    });
  `;
  const blob = new Blob([swCode], {type:'application/javascript'});
  const url  = URL.createObjectURL(blob);
  navigator.serviceWorker.register(url).catch(()=>{});
}
</script>
""", unsafe_allow_html=True)



def _h(pw: str) -> str:
    """SHA-256 hash."""
    return hashlib.sha256(pw.encode()).hexdigest()

def _ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

def _today() -> str:
    return datetime.date.today().isoformat()

# ── Generic CRUD ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def _get_cached(table, filters_json, order, limit):
    """Cached read — call _get() which wraps this."""
    import json
    filters = json.loads(filters_json) if filters_json else {}
    params  = {"limit": limit}
    if order: params["order"] = order
    for k, v in filters.items():
        if   v is None:          params[k] = "is.null"
        elif isinstance(v, bool):params[k] = f"eq.{'true' if v else 'false'}"
        else:                    params[k] = f"eq.{v}"
    try:
        r = requests.get(f"{REST}/{table}", headers=RH, params=params, timeout=10)
        if r.status_code == 200: return r.json()
    except Exception: pass
    return []


def _get(table, filters=None, order=None, limit=500, single=False):
    import json
    fj   = json.dumps(filters or {}, sort_keys=True)
    rows = _get_cached(table, fj, order or "", limit)
    if single: return rows[0] if rows else None
    return rows


def _post(table, data):
    """
    Insert a row into a Supabase table.
    Returns the inserted row dict on success, None on failure.
    Logs the REAL Supabase error message — never swallows it silently.
    """
    try:
        r = requests.post(f"{REST}/{table}", headers=RH, json=data, timeout=10)
        if r.status_code in (200, 201):
            d = r.json()
            _get_cached.clear()
            return d[0] if isinstance(d, list) and d else d
        # ── Expose real error from Supabase in the return value ──────────────
        # Caller decides whether to show it — we don't call st.error() here
        # because _post is used inside _complete_reg which has its own handling.
        return {"__error__": True,
                "__status__": r.status_code,
                "__msg__": r.text}
    except requests.exceptions.Timeout:
        return {"__error__": True, "__status__": 0,
                "__msg__": "انتهت مهلة الاتصال بـ Supabase (timeout)."}
    except requests.exceptions.ConnectionError:
        return {"__error__": True, "__status__": 0,
                "__msg__": "تعذّر الاتصال بـ Supabase. تحقق من الإنترنت."}
    except Exception as e:
        return {"__error__": True, "__status__": 0, "__msg__": str(e)}


def _post_ok(result) -> bool:
    """Returns True if _post() succeeded (result is a real row, not an error dict)."""
    if result is None: return False
    if isinstance(result, dict) and result.get("__error__"): return False
    return True


def _post_err(result) -> str:
    """Extracts human-readable error from a failed _post() result."""
    if result is None: return "لم يُرجع Supabase أي استجابة."
    if isinstance(result, dict) and result.get("__error__"):
        status = result.get("__status__", "?")
        msg    = result.get("__msg__", "")
        # Parse Supabase JSON error if possible
        try:
            import json
            err_json = json.loads(msg)
            detail   = err_json.get("message") or err_json.get("details") or msg
        except Exception:
            detail = msg[:300]
        return f"[HTTP {status}] {detail}"
    return ""


def _patch(table, match, data):
    params = {k: f"eq.{v}" for k, v in match.items()}
    try:
        r = requests.patch(f"{REST}/{table}", headers=RH, json=data,
                           params=params, timeout=10)
        if r.status_code in (200, 204):
            _get_cached.clear()
            return True
        st.error(f"خطأ تحديث: {r.text[:180]}")
    except Exception as e:
        st.error(f"خطأ: {e}")
    return False


def _count(table, filters=None) -> int:
    params = {"select": "id"}
    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"
    h = {**RH, "Prefer": "count=exact", "Range": "0-0"}
    try:
        r = requests.get(f"{REST}/{table}", headers=h, params=params, timeout=8)
        cr = r.headers.get("Content-Range", "")
        if "/" in cr: return int(cr.split("/")[1])
    except Exception: pass
    return 0

# ── Supabase Auth helpers ──────────────────────────────────────────────────────

def _auth_reset_password(email: str) -> bool:
    """
    Trigger Supabase Auth password-reset email.
    Works when Supabase Auth is configured with the user's real email.
    For our custom users table we also store a reset_token approach as fallback.
    """
    try:
        r = requests.post(
            f"{AUTH}/recover",
            headers={"apikey": SUPA_KEY, "Content-Type": "application/json"},
            json={"email": email},
            timeout=10,
        )
        return r.status_code in (200, 204)
    except Exception:
        return False


def _auth_update_password(access_token: str, new_password: str) -> bool:
    """Update password via Supabase Auth (used after OTP verification)."""
    try:
        r = requests.put(
            f"{AUTH}/user",
            headers={"apikey": SUPA_KEY,
                     "Authorization": f"Bearer {access_token}",
                     "Content-Type": "application/json"},
            json={"password": new_password},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False

# ── Storage ────────────────────────────────────────────────────────────────────

def _upload(file_bytes: bytes, filename: str,
            ctype: str = "application/octet-stream",
            subfolder: str = "") -> tuple:
    """
    Upload to Supabase Storage bucket.
    Uses UUID-based filename to avoid InvalidKey errors from Arabic/special chars.
    Returns (public_url, storage_path) tuple.  Both empty strings on failure.
    """
    # Extract original extension and build a safe UUID-based name
    _, ext = os.path.splitext(filename)
    ext    = ext.lower() if ext else ""
    uid    = str(uuid.uuid4()).replace("-", "")
    safe   = f"{uid}{ext}"                       # e.g. "a3f9...b2.pdf"
    path   = f"{subfolder}/{safe}" if subfolder else safe
    url    = f"{STORE}/object/{BUCKET}/{path}"
    h      = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}",
              "Content-Type": ctype, "x-upsert": "true"}
    try:
        r = requests.post(url, headers=h, data=file_bytes, timeout=60)
        if r.status_code in (200, 201):
            public_url = f"{STORE}/object/public/{BUCKET}/{path}"
            return public_url, path              # ← return both URL and path
        st.error(f"⚠️ رفع الملف: {r.text[:180]}")
    except Exception as e:
        st.error(f"⚠️ رفع: {e}")
    return "", ""


def _storage_delete(storage_path: str) -> bool:
    """
    Delete a file from Supabase Storage by its storage path.
    storage_path is the path inside the bucket (not the full URL).
    """
    if not storage_path:
        return False
    url = f"{STORE}/object/{BUCKET}/{storage_path}"
    h   = {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"}
    try:
        r = requests.delete(url, headers=h, timeout=15)
        return r.status_code in (200, 204)
    except Exception:
        return False


def _dl_btn(url: str, label="⬇️ تحميل"):
    if not url: st.caption("لا يوجد ملف"); return
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            fname = url.split("/")[-1]
            st.download_button(label, r.content, file_name=fname, use_container_width=True)
            return
    except Exception: pass
    st.markdown(f'<a href="{url}" target="_blank" style="color:var(--gold)">🔗 فتح الملف</a>',
                unsafe_allow_html=True)

# ── Notifications helper ───────────────────────────────────────────────────────

def _push_notification(workspace_id: int, title: str, body: str,
                        target_roles: list = None, order_id: int = None):
    """Insert a notification row (read by target roles in same workspace)."""
    _post("notifications", {
        "workspace_id": workspace_id,
        "title":        title,
        "body":         body,
        "target_roles": ",".join(target_roles) if target_roles else "all",
        "order_id":     order_id,
        "is_read":      False,
    })

# ── Business helpers ───────────────────────────────────────────────────────────

def wid() -> int:
    return st.session_state.get("workspace_id", 0)

def _order_no() -> str:
    n = _count("orders", {"workspace_id": wid()})
    return f"ZO-{datetime.date.today().strftime('%y%m%d')}-{n+1:04d}"

def _gen_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def _build_email_html(otp: str, mode: str = "verify") -> str:
    """Build professional HTML email body. mode: 'verify' | 'reset'"""
    if mode == "reset":
        title   = "إعادة تعيين كلمة المرور"
        desc    = "استخدم الرمز التالي لإعادة تعيين كلمة مرورك:"
        clr     = "#ef4444"
        footer_note = "إذا لم تطلب إعادة التعيين، تجاهل هذا الإيميل."
    else:
        title   = "رمز التحقق الخاص بك"
        desc    = "لإتمام التسجيل في Z-ORDER، استخدم رمز التحقق التالي:"
        clr     = "#e8a020"
        footer_note = "إذا لم تطلب التسجيل في Z-ORDER، تجاهل هذا الإيميل."

    return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0a0c11;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:2rem 1rem;">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#0e1118;border-radius:14px;border:1px solid #232a3d;
                    max-width:480px;width:100%;">
        <tr>
          <td style="padding:2rem;text-align:center;border-bottom:1px solid #1a1f2e;">
            <span style="font-family:monospace;font-size:2rem;font-weight:700;color:#e8a020;">
              Z-ORDER
            </span><br>
            <span style="font-size:.72rem;color:#8590a8;letter-spacing:.12em;">
              BUILT FOR ORGANIZED TEAMS
            </span>
          </td>
        </tr>
        <tr>
          <td style="padding:2rem;">
            <p style="font-size:1.05rem;font-weight:600;color:#f0f2f8;margin:0 0 .5rem">
              {title}
            </p>
            <p style="color:#8590a8;font-size:.88rem;margin:0 0 1.5rem">
              {desc}
            </p>
            <div style="background:#13161f;border:1px solid #232a3d;border-radius:10px;
                        padding:1.5rem;text-align:center;margin-bottom:1.5rem;">
              <span style="font-family:monospace;font-size:2.6rem;font-weight:700;
                           letter-spacing:.4em;color:{clr};">{otp}</span>
            </div>
            <p style="color:#8590a8;font-size:.78rem;margin:0 0 .4rem">
              ⏰ الرمز صالح لمدة جلسة العمل الحالية فقط.
            </p>
            <p style="color:#3a4258;font-size:.72rem;margin:0">
              {footer_note}
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:1rem 2rem;border-top:1px solid #1a1f2e;text-align:center;">
            <span style="color:#3a4258;font-size:.68rem;">
              Developed by Abdulrahman Fallah &nbsp;·&nbsp; Z-ORDER © 2026
            </span>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_verification_email(user_email: str, code: str) -> bool:
    """
    Send OTP verification code via Gmail SMTP (smtplib).
    Uses st.secrets for credentials — no external API keys needed.
    The OTP code is NEVER displayed in the UI.
    Subject: Z-ORDER | رمز التحقق الخاص بك
    Returns True on success, False on failure (logs error to console).
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Z-ORDER | رمز التحقق الخاص بك"
        msg["From"]    = f"Z-ORDER <{SENDER_EMAIL}>"
        msg["To"]      = user_email

        # Plain text fallback
        plain = (
            f"Z-ORDER | رمز التحقق الخاص بك\n\n"
            f"رمز التحقق الخاص بك هو: {code}\n\n"
            f"الرمز صالح لمدة جلسة العمل الحالية فقط.\n"
            f"إذا لم تطلب التسجيل، تجاهل هذا الإيميل.\n\n"
            f"Developed by Abdulrahman Fallah · Z-ORDER © 2026"
        )
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(_build_email_html(code, "verify"), "html", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [user_email], msg.as_string())
        return True

    except smtplib.SMTPAuthenticationError:
        print("[Z-ORDER SMTP] Authentication failed — check SENDER_EMAIL / SENDER_PASSWORD in secrets.")
        return False
    except smtplib.SMTPException as e:
        print(f"[Z-ORDER SMTP] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[Z-ORDER SMTP] Unexpected error: {e}")
        return False


def send_reset_email(user_email: str, code: str) -> bool:
    """
    Send password-reset OTP via Gmail SMTP.
    Subject: Z-ORDER | رمز إعادة تعيين كلمة المرور
    The OTP code is NEVER displayed in the UI.
    Returns True on success, False on failure.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Z-ORDER | رمز إعادة تعيين كلمة المرور"
        msg["From"]    = f"Z-ORDER <{SENDER_EMAIL}>"
        msg["To"]      = user_email

        plain = (
            f"Z-ORDER | إعادة تعيين كلمة المرور\n\n"
            f"رمز إعادة التعيين: {code}\n\n"
            f"الرمز صالح لمدة جلسة العمل الحالية فقط.\n"
            f"إذا لم تطلب إعادة التعيين، تجاهل هذا الإيميل."
        )
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(_build_email_html(code, "reset"), "html", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [user_email], msg.as_string())
        return True

    except smtplib.SMTPAuthenticationError:
        print("[Z-ORDER SMTP] Auth error on reset email.")
        return False
    except Exception as e:
        print(f"[Z-ORDER SMTP] Reset email error: {e}")
        return False

STATUS_BADGE_MAP = {
    "جديد":             ("b-new", "🔵 جديد"),
    "قيد التصميم":      ("b-des", "🎨 تصميم"),
    "جاهز للطباعة":    ("b-rdy", "🟢 جاهز"),
    "جاري الإنتاج":    ("b-prt", "🟠 إنتاج"),
    "جاهز للتسليم":    ("b-del", "📦 تسليم"),
    "تم التسليم":      ("b-done","✅ مكتمل"),
}
SEV_MAP  = {"منخفض":("b-sev-lo","🟢"),"متوسط":("b-sev-md","🟡"),"عالي":("b-sev-hi","🔴")}
AGT_MAP  = {"اشترى":("b-abuy","✅"),"محتمل":("b-apot","🔵"),"لن يشتري":("b-ano","❌")}

def bdg(k, m=None):
    m = m or STATUS_BADGE_MAP
    c, l = m.get(k, ("b-pend", k))
    return f'<span class="badge {c}">{l}</span>'

def hdr(icon, title, sub=""):
    st.markdown(f'<div class="ph"><div class="ph-icon">{icon}</div>'
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

def _sbar(total, done):
    bars = "".join(
        f'<div class="sbr {"done" if i < done else "act" if i == done else ""}"></div>'
        for i in range(total))
    st.markdown(f'<div class="sbar">{bars}</div>', unsafe_allow_html=True)

def _status_tracker(current_status: str):
    steps = STATUS_FLOW
    cur   = steps.index(current_status) if current_status in steps else 0
    html  = '<div class="tracker">'
    for i, s in enumerate(steps):
        cls = "done" if i < cur else ("active" if i == cur else "")
        html += f'<div class="tr-step {cls}">{s}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def show_orders(role, uid_filter=None, title="الأوردرات"):
    hdr("📋", title)
    hide_price = role not in ("admin","sales","superadmin")
    filters = {"workspace_id": wid()}
    if uid_filter: filters["created_by_id"] = uid_filter
    rows = _get("orders", filters=filters, order="id.desc")
    if not rows: st.info("لا توجد أوردرات."); return
    sts = ["الكل"] + sorted({r.get("status","") for r in rows})
    sel = st.selectbox("الحالة", sts, key=f"o_{role}_{uid_filter}")
    if sel != "الكل": rows = [r for r in rows if r.get("status") == sel]
    cols = ["order_number","customer_name","paper_type","size","quantity",
            "total_price","paid","remaining","status","created_at"]
    if not hide_price:
        show = [c for c in cols if c in (pd.DataFrame(rows).columns if rows else [])]
    else:
        show = [c for c in cols if c not in ("total_price","paid","remaining")]
    lbl  = {"order_number":"الأوردر","customer_name":"العميل","paper_type":"الورق",
             "size":"القياس","quantity":"الكمية","total_price":"السعر الكلي",
             "paid":"المدفوع","remaining":"المتبقي","status":"الحالة","created_at":"التاريخ"}
    df = pd.DataFrame(rows)
    ok = [c for c in show if c in df.columns]
    st.dataframe(df[ok].rename(columns=lbl), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH FLOW
# ══════════════════════════════════════════════════════════════════════════════

def auth_screen() -> bool:
    """Returns True when session is authenticated. Shows auth UI otherwise."""
    if st.session_state.get("auth"):
        return True

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="logo-big">Z<span class="sep">-</span>ORDER</div>'
            f'<div class="logo-tag">{APP_TAGLINE}</div>'
            f'<div style="text-align:center;color:var(--t3);font-size:.62rem;margin-top:.3rem">'
            f'v{APP_VER} · Android Edition</div>',
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        scr = st.session_state.get("scr", "login")

        # ── LOGIN ─────────────────────────────────────────────────────────────
        if scr == "login":
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            idn = st.text_input("📧 الإيميل أو اسم المستخدم",
                                placeholder="admin@zorder.iq", key="li_i")
            pw  = st.text_input("🔒 كلمة المرور", type="password", key="li_p")
            btn = st.button("دخول ←", key="li_b")
            st.markdown('</div>', unsafe_allow_html=True)

            # Forgot password link
            fp_col, _ = st.columns([1,2])
            if fp_col.button("🔑 نسيت كلمة المرور؟", key="fp_lnk"):
                st.session_state["scr"] = "forgot"; st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 إنشاء حساب شركة جديد", key="go_reg"):
                st.session_state["scr"] = "r1"; st.rerun()

            if btn:
                _do_login(idn.strip(), pw.strip())

        # ── FORGOT PASSWORD ───────────────────────────────────────────────────
        elif scr == "forgot":
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">إعادة تعيين كلمة المرور</div>', unsafe_allow_html=True)
            st.info("💡 سيتم إرسال رابط إعادة التعيين لبريدك الإلكتروني عبر Supabase Auth. "
                    "إذا كنت مستخدماً داخلياً، سيظهر رمز OTP هنا.")
            fp_email = st.text_input("📧 الإيميل المسجّل", key="fp_em")
            col1, col2 = st.columns(2)
            send = col1.button("📨 إرسال رابط الإعادة", key="fp_send")
            st.markdown('</div>', unsafe_allow_html=True)

            if col2.button("← رجوع", key="fp_back"):
                st.session_state["scr"] = "login"; st.rerun()

            if send:
                if not fp_email.strip():
                    st.error("يرجى إدخال الإيميل.")
                else:
                    em   = fp_email.strip().lower()
                    user = _get("users", {"email": em}, single=True)
                    if user:
                        otp = _gen_otp()
                        with st.spinner("جاري إرسال رمز إعادة التعيين..."):
                            email_sent = send_reset_email(em, otp)
                        # Store OTP in session — never in UI
                        st.session_state["reset_email"] = em
                        st.session_state["reset_otp"]   = otp
                        st.session_state["scr"]         = "reset_otp"
                        if email_sent:
                            st.success(f"✅ تم إرسال رمز إعادة التعيين إلى **{em}**")
                        else:
                            st.warning("⚠️ تعذّر إرسال الإيميل. "
                                       "سيُرسل الرمز مجدداً عند المحاولة التالية.")
                        st.rerun()
                    else:
                        # Always show success to avoid user enumeration
                        st.success("✅ إذا كان الإيميل مسجّلاً، ستصلك رسالة قريباً.")

        # ── RESET OTP ─────────────────────────────────────────────────────────
        elif scr == "reset_otp":
            _sbar(2, 0)
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">الخطوة 1 — تأكيد الهوية</div>', unsafe_allow_html=True)
            # ── OTP is NEVER shown here — sent only to email ──────────────────
            st.markdown(
                f'<div style="background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2);'
                f'border-radius:var(--r);padding:.75rem 1rem;margin-bottom:.75rem;'
                f'font-size:.84rem;color:var(--t2);">'
                f'📨 تم إرسال رمز إعادة التعيين إلى:<br>'
                f'<b style="color:var(--gold)">{st.session_state.get("reset_email","")}</b><br>'
                f'<span style="font-size:.74rem;color:var(--t3);">'
                f'يرجى التحقق من صندوق الوارد وصندوق Spam</span>'
                f'</div>',
                unsafe_allow_html=True)
            otp_in = st.text_input("🔑 أدخل الرمز (6 أرقام)", key="ro_in",
                                   max_chars=6, placeholder="······")
            ok_btn = st.button("تحقق ←", key="ro_ok")
            # Resend option
            if st.button("📨 إعادة إرسال الرمز", key="ro_resend"):
                new_otp = _gen_otp()
                with st.spinner("جاري الإرسال..."):
                    ok = send_reset_email(st.session_state.get("reset_email",""), new_otp)
                if ok:
                    st.session_state["reset_otp"] = new_otp
                    st.success("✅ تم إرسال رمز جديد.")
                else:
                    st.error("❌ فشل الإرسال.")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("← رجوع", key="ro_back"):
                st.session_state["scr"] = "forgot"; st.rerun()
            if ok_btn:
                if otp_in.strip() != st.session_state.get("reset_otp",""):
                    st.error("❌ الرمز غير صحيح. تحقق من بريدك الإلكتروني.")
                else:
                    st.session_state["scr"] = "reset_pw"; st.rerun()

        # ── NEW PASSWORD ──────────────────────────────────────────────────────
        elif scr == "reset_pw":
            _sbar(2, 1)
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">الخطوة 2 — كلمة المرور الجديدة</div>', unsafe_allow_html=True)
            p1 = st.text_input("🔒 كلمة المرور الجديدة", type="password", key="rp1")
            p2 = st.text_input("🔒 تأكيد كلمة المرور",   type="password", key="rp2")
            save = st.button("💾 حفظ كلمة المرور", key="rp_save")
            st.markdown('</div>', unsafe_allow_html=True)

            if save:
                if not p1 or p1 != p2:
                    st.error("كلمتا المرور غير متطابقتين أو فارغتين.")
                elif len(p1) < 6:
                    st.error("كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
                else:
                    em = st.session_state.get("reset_email","")
                    ok = _patch("users", {"email": em}, {"password": _h(p1)})
                    if ok:
                        st.success("✅ تم تغيير كلمة المرور! يمكنك الآن تسجيل الدخول.")
                        for k in ("scr","reset_email","reset_otp"):
                            st.session_state.pop(k, None)
                        st.session_state["scr"] = "login"; st.rerun()
                    else:
                        st.error("❌ فشل تحديث كلمة المرور.")

        # ── REGISTER STEP 1 ───────────────────────────────────────────────────
        elif scr == "r1":
            _sbar(3, 0)
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">الخطوة 1 — معلومات الشركة</div>', unsafe_allow_html=True)
            cn  = st.text_input("🏢 اسم الشركة *", key="r1cn")
            em  = st.text_input("📧 إيميل المدير *", placeholder="you@company.com", key="r1em")
            pw1 = st.text_input("🔒 كلمة المرور *", type="password", key="r1p1")
            pw2 = st.text_input("🔒 التأكيد *",     type="password", key="r1p2")
            nxt = st.button("التالي ←", key="r1nx")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("← رجوع لتسجيل الدخول", key="r1bk"):
                st.session_state["scr"] = "login"; st.rerun()

            if nxt:
                errs = []
                if not all([cn.strip(),em.strip(),pw1]): errs.append("جميع الحقول مطلوبة.")
                if pw1 and pw1!=pw2:                     errs.append("كلمتا المرور غير متطابقتين.")
                if pw1 and len(pw1)<6:                   errs.append("كلمة المرور 6 أحرف على الأقل.")
                for e in errs: st.error(e)
                if not errs:
                    existing = _get("users", {"email": em.strip().lower()}, single=True)
                    if existing:
                        st.error("❌ هذا الإيميل مسجّل بالفعل.")
                    else:
                        otp = _gen_otp()
                        # ── Send OTP via Resend — NEVER display on screen ────
                        with st.spinner("جاري إرسال رمز التحقق إلى بريدك الإلكتروني..."):
                            sent = send_verification_email(em.strip().lower(), otp)
                        st.session_state.update(
                            r_cn=cn.strip(), r_em=em.strip().lower(),
                            r_pw=pw1, r_otp=otp, scr="r_otp")
                        if sent:
                            st.success(f"✅ تم إرسال رمز التحقق إلى **{em.strip()}**\n\n"
                                       f"يرجى التحقق من بريدك الإلكتروني (وصندوق Spam).")
                        else:
                            # Resend failed — warn but continue (OTP still in session)
                            st.warning("⚠️ تعذّر إرسال الإيميل. "
                                       "يرجى التواصل مع الدعم الفني أو المحاولة لاحقاً.")
                        st.rerun()

        # ── REGISTER OTP ──────────────────────────────────────────────────────
        elif scr == "r_otp":
            _sbar(3, 1)
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">الخطوة 2 — تأكيد الهوية</div>', unsafe_allow_html=True)
            # ── OTP is NEVER shown here — sent only to email ──────────────────
            st.markdown(
                f'<div style="background:rgba(232,160,32,.08);border:1px solid rgba(232,160,32,.2);'
                f'border-radius:var(--r);padding:.75rem 1rem;margin-bottom:.75rem;'
                f'font-size:.84rem;color:var(--t2);">'
                f'📨 تم إرسال رمز التحقق إلى:<br>'
                f'<b style="color:var(--gold)">{st.session_state.get("r_em","")}</b><br>'
                f'<span style="font-size:.74rem;color:var(--t3);">'
                f'يرجى التحقق من صندوق الوارد وصندوق Spam</span>'
                f'</div>',
                unsafe_allow_html=True)
            oi  = st.text_input("🔑 أدخل رمز التحقق (6 أرقام)", key="rO",
                                max_chars=6, placeholder="······")
            v   = st.button("تحقق والمتابعة ←", key="rOv")
            # Resend OTP option
            if st.button("📨 إعادة إرسال الرمز", key="rOresend"):
                new_otp = _gen_otp()
                with st.spinner("جاري إعادة الإرسال..."):
                    ok = send_verification_email(st.session_state.get("r_em",""), new_otp)
                if ok:
                    st.session_state["r_otp"] = new_otp
                    st.success("✅ تم إرسال رمز جديد إلى بريدك.")
                else:
                    st.error("❌ فشل إعادة الإرسال. تحقق من الاتصال.")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("← رجوع", key="rObk"):
                st.session_state["scr"] = "r1"; st.rerun()
            if v:
                if oi.strip() != st.session_state.get("r_otp",""):
                    st.error("❌ الرمز غير صحيح. تحقق من بريدك الإلكتروني.")
                else:
                    st.session_state["scr"] = "r2"; st.rerun()

        # ── REGISTER STEP 2 ───────────────────────────────────────────────────
        elif scr == "r2":
            _sbar(3, 2)
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown('<div class="sec">الخطوة 3 — معلومات حساب المدير</div>', unsafe_allow_html=True)
            fn  = st.text_input("👤 الاسم الكامل للمدير *", key="r2fn")
            un  = st.text_input("🏷️ اسم المستخدم *",
                                placeholder="مثال: ahmed_manager", key="r2un")
            # No plan selection — system is fully open
            fin = st.button("✅ إنشاء الحساب", key="r2cr")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("← رجوع", key="r2bk"):
                st.session_state["scr"] = "r_otp"; st.rerun()
            if fin:
                if not all([fn.strip(), un.strip()]):
                    st.error("يرجى تعبئة جميع الحقول.")
                else:
                    _complete_reg(
                        fn.strip(),
                        un.strip().lower(),
                        st.session_state["r_cn"],
                        st.session_state["r_em"],
                        st.session_state["r_pw"],
                        # No plan argument
                    )

        st.markdown(
            f'<div style="text-align:center;margin-top:1rem;color:var(--t3);font-size:.62rem">'
            f'Developed by <b style="color:var(--gold)">{DEVELOPER}</b></div>',
            unsafe_allow_html=True)

    return False


def _do_login(idn: str, pw: str):
    # Platform super-admin (never stored in DB)
    if idn.lower() in (SA_EMAIL, "superadmin", "admin"):
        if pw == SA_PASS:
            st.session_state.update(
                auth=True, uid=0, uname=DEVELOPER,
                role="superadmin", workspace_id=0, workspace_name="Z-ORDER Platform")
            st.rerun(); return
        st.error("❌ كلمة المرور غير صحيحة."); return

    pw_h = _h(pw)
    user = (_get("users", {"email":   idn.lower(), "password": pw_h, "is_active": True}, single=True)
         or _get("users", {"username": idn.lower(), "password": pw_h, "is_active": True}, single=True))

    if not user:
        st.error("❌ بيانات غير صحيحة أو الحساب موقوف."); return

    ws_id, ws_name = user.get("workspace_id", 0), ""
    if ws_id:
        ws = _get("workspaces", {"id": ws_id}, single=True)
        ws_name = ws.get("name","") if ws else ""

    st.session_state.update(
        auth=True, uid=user["id"], uname=user["full_name"],
        role=user["role"], workspace_id=ws_id, workspace_name=ws_name)
    for k in ("scr","r_cn","r_em","r_pw","r_otp"):
        st.session_state.pop(k, None)
    st.rerun()


def _complete_reg(full_name, username, company, email, pw):
    """
    Register a new admin + workspace.
    Strategy:
      1. Build slug from company name (alphanumeric only).
      2. SELECT workspace by slug — if found, reuse its id.
      3. If NOT found, INSERT new workspace and get the new id.
      4. INSERT user linked to that workspace_id.
      5. Full try/except + real error display at every step.
    No plan field — system is fully open.
    """
    import re
    # Build a safe slug: Arabic letters map to their transliterated equivalents aren't
    # needed — we just strip non-alphanumeric and use the result; unique per company name.
    slug = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF]", "-", company.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-") or "ws"

    try:
        # ── Step 1: check if workspace (slug) already exists ─────────────────
        existing_ws = _get("workspaces", {"slug": slug}, single=True)

        if existing_ws and isinstance(existing_ws, dict) and "id" in existing_ws:
            # Reuse existing workspace — don't duplicate
            ws_id   = existing_ws["id"]
            ws_name = existing_ws.get("name", company)
        else:
            # ── Step 2: create new workspace ─────────────────────────────────
            ws_result = _post("workspaces", {
                "name":      company.strip(),
                "slug":      slug,
                "is_active": True,
                # No "plan" field — system is open
            })

            # Guard: check for error or missing id
            if ws_result is None:
                st.error("❌ لم يُرجع Supabase أي استجابة عند إنشاء الشركة. تحقق من الاتصال.")
                return
            if isinstance(ws_result, dict) and ws_result.get("__error__"):
                err = _post_err(ws_result)
                st.error(f"❌ فشل إنشاء الشركة.\n\nالخطأ الحقيقي من Supabase:\n`{err}`")
                return
            if not isinstance(ws_result, dict) or "id" not in ws_result:
                st.error(f"❌ استجابة غير متوقعة من Supabase: `{ws_result}`")
                return

            ws_id   = ws_result["id"]
            ws_name = company.strip()

        # ── Step 3: create admin user ─────────────────────────────────────────
        user_result = _post("users", {
            "workspace_id": ws_id,
            "full_name":    full_name,
            "username":     username,
            "email":        email,
            "password":     _h(pw),
            "role":         "admin",
            "created_by":   0,
            "is_active":    True,
        })

        if user_result is None:
            st.error("❌ لم يُرجع Supabase أي استجابة عند إنشاء المستخدم.")
            return
        if isinstance(user_result, dict) and user_result.get("__error__"):
            err = _post_err(user_result)
            st.error(f"❌ فشل إنشاء الحساب.\n\nالخطأ الحقيقي من Supabase:\n`{err}`")
            return
        if not isinstance(user_result, dict) or "id" not in user_result:
            st.error(f"❌ استجابة غير متوقعة للمستخدم: `{user_result}`")
            return

        # ── Step 4: success ───────────────────────────────────────────────────
        st.success(
            f"🎉 تم إنشاء حسابك بنجاح!\n\n"
            f"**الشركة:** {ws_name}\n"
            f"**اسم المستخدم:** {username}\n\n"
            f"سجّل دخولك الآن بالإيميل أو اسم المستخدم.")
        for k in ("scr","r_cn","r_em","r_pw","r_otp"):
            st.session_state.pop(k, None)
        st.session_state["scr"] = "login"
        st.rerun()

    except KeyError as ke:
        st.error(f"❌ خطأ برمجي (KeyError): المفتاح `{ke}` غير موجود في الاستجابة. "
                 f"تأكد من وجود جميع أعمدة جدول workspaces في Supabase.")
    except Exception as ex:
        st.error(f"❌ خطأ غير متوقع أثناء التسجيل: `{type(ex).__name__}: {ex}`")

# ══════════════════════════════════════════════════════════════════════════════
#  TOP NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════

def top_nav() -> str:
    role  = st.session_state["role"]
    uname = st.session_state["uname"]
    wsn   = st.session_state.get("workspace_name","")
    ri    = ROLES.get(role, {"ar":role,"icon":"👤","clr":"#e8a020"})
    init  = "".join(w[0] for w in uname.split()[:2]).upper() or "?"
    pages = ROLE_PAGES.get(role, [])

    # Unread notifications count
    if role != "superadmin":
        notifs = _get("notifications", {"workspace_id":wid(),"is_read":False},
                      order="id.desc", limit=50)
        my_role_notifs = [n for n in notifs
                          if n.get("target_roles","all") in ("all", role)
                          or role in n.get("target_roles","")]
        n_count = len(my_role_notifs)
    else:
        n_count = 0

    # ── App Badging API — updates icon badge on Android/Desktop PWA ──────────
    st.markdown(
        f'<script>if(window.zSetBadge) window.zSetBadge({n_count});</script>',
        unsafe_allow_html=True)

    bell_html = ""
    if n_count:
        bell_html = (f'<div class="notif-bell" style="padding:.15rem .35rem">'
                     f'🔔<span class="notif-count">{n_count}</span></div>')

    st.markdown(
        f'<div class="topbar">'
        f'<div class="zlogo">Z<span class="sep">-</span>ORDER'
        f'<span class="tag">{APP_TAGLINE}</span></div>'
        f'{bell_html}'
        f'<div class="uchip" style="margin-right:auto">'
        f'<div class="uav">{init}</div>'
        f'<div style="display:flex;flex-direction:column;gap:0">'
        f'<span style="font-size:.74rem;font-weight:600;color:var(--t1);line-height:1.2">{uname}</span>'
        f'<span style="font-size:.59rem;color:{ri["clr"]}">{ri["icon"]} {ri["ar"]}'
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
                               key="ns", label_visibility="collapsed")
        st.session_state["page"] = active
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if st.button("خروج 🚪", key="lo"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    return active

# ══════════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS PAGE
# ══════════════════════════════════════════════════════════════════════════════

def pg_notifications():
    role = st.session_state["role"]
    hdr("🔔","الإشعارات","تنبيهات تغييرات الحالة والمهام")
    WID = wid()
    all_n = _get("notifications",{"workspace_id":WID},order="id.desc",limit=80)
    my_n  = [n for n in all_n
             if n.get("target_roles","all") in ("all",role)
             or role in n.get("target_roles","")]

    if not my_n:
        st.info("📭 لا توجد إشعارات."); return

    unread = [n for n in my_n if not n.get("is_read")]
    read   = [n for n in my_n if  n.get("is_read")]

    if unread:
        if st.button("✅ تحديد الكل كمقروء", key="mark_all"):
            for n in unread:
                _patch("notifications", {"id": n["id"]}, {"is_read": True})
            _get_cached.clear(); st.rerun()

    def _render_notifs(lst):
        for n in lst:
            rdcls = "unread" if not n.get("is_read") else ""
            dot   = "notif-dot" if not n.get("is_read") else "notif-dot read"
            st.markdown(
                f'<div class="notif-item {rdcls}">'
                f'<div class="{dot}"></div>'
                f'<div><div style="font-size:.85rem;font-weight:600;color:var(--t1)">{n.get("title","")}</div>'
                f'<div style="font-size:.78rem;color:var(--t2);margin-top:2px">{n.get("body","")}</div>'
                f'<div style="font-size:.62rem;color:var(--t3);margin-top:4px">{str(n.get("created_at",""))[:16]}</div>'
                f'</div></div>',
                unsafe_allow_html=True)
            if not n.get("is_read"):
                if st.button("قراءة", key=f"rd_{n['id']}"):
                    _patch("notifications",{"id":n["id"]},{"is_read":True})
                    _get_cached.clear(); st.rerun()

    t1,t2 = st.tabs([f"🔴 غير مقروءة ({len(unread)})",f"✅ مقروءة ({len(read)})"])
    with t1: _render_notifs(unread) if unread else st.success("🎉 لا توجد إشعارات جديدة!")
    with t2: _render_notifs(read)   if read   else st.info("لا توجد إشعارات مقروءة.")

# ══════════════════════════════════════════════════════════════════════════════
#  SUPER-ADMIN PAGES
# ══════════════════════════════════════════════════════════════════════════════

def pg_sa_dash():
    hdr("⭐","لوحة تحكم المنصة","إحصائيات جميع الشركات المشتركة")
    guide(f"① أنت {DEVELOPER} — رؤية شاملة للمنصة<br>"
          "② أنشئ شركات وامنح الأدمن حساباتهم<br>"
          "③ لا أحد سواك يصل لهذه اللوحة")
    ws_all = _get("workspaces", order="id.desc")
    u_all  = _get("users")
    o_all  = _get("orders")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("الشركات",     len(ws_all))
    c2.metric("المستخدمون", len(u_all))
    c3.metric("الأوردرات",   len(o_all))
    rev = sum(float(o.get("total_price",0) or 0) for o in o_all
              if o.get("status") == "تم التسليم")
    c4.metric("الإيراد الكلي (د.ع)", f"{rev:,.0f}")
    st.markdown("---")
    t1,t2 = st.tabs(["🏢 الشركات","📈 الأكثر نشاطاً"])
    with t1:
        if ws_all:
            df = pd.DataFrame(ws_all)
            if "is_active" in df.columns:
                df["is_active"] = df["is_active"].map({True:"✅",False:"🚫",1:"✅",0:"🚫"})
            st.dataframe(df[["id","name","plan","is_active","created_at"]].rename(columns={
                "id":"#","name":"الشركة","plan":"الخطة","is_active":"نشطة","created_at":"التاريخ"
            }), use_container_width=True, hide_index=True)
    with t2:
        stats = []
        for ws in ws_all:
            wo  = [o for o in o_all if o.get("workspace_id") == ws["id"]]
            rev = sum(float(o.get("total_price",0) or 0) for o in wo if o.get("status")=="تم التسليم")
            stats.append({"الشركة":ws["name"],"الأوردرات":len(wo),"إيراد (د.ع)":f"{rev:,.0f}"})
        stats.sort(key=lambda x: x["الأوردرات"], reverse=True)
        if stats: st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)


def pg_sa_companies():
    hdr("🏢","إدارة الشركات","أضف شركات وأنشئ مديريها")
    ws_all = _get("workspaces", order="id.asc")
    if ws_all:
        df = pd.DataFrame(ws_all)
        if "is_active" in df.columns:
            df["is_active"] = df["is_active"].map({True:"✅",False:"🚫",1:"✅",0:"🚫"})
        st.dataframe(df[["id","name","slug","plan","is_active","created_at"]].rename(columns={
            "id":"#","name":"الشركة","slug":"Slug","plan":"الخطة",
            "is_active":"نشطة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)
    st.markdown("---")
    st.markdown('<div class="sec">➕ شركة جديدة + مديرها</div>', unsafe_allow_html=True)
    with st.form("add_ws", clear_on_submit=True):
        c1,c2 = st.columns(2)
        wn = c1.text_input("اسم الشركة *"); pl = c2.selectbox("الخطة",["starter","pro","enterprise"])
        st.markdown('<div class="sec">بيانات مدير الشركة</div>', unsafe_allow_html=True)
        c3,c4 = st.columns(2)
        afn = c3.text_input("اسم المدير *"); aun = c4.text_input("اسم المستخدم *")
        c5,c6 = st.columns(2)
        aem = c5.text_input("إيميل المدير *"); apw = c6.text_input("كلمة المرور *", type="password")
        sub = st.form_submit_button("✅ إنشاء", use_container_width=True)
    if sub:
        if not all([wn,afn,aun,aem,apw]): st.error("جميع الحقول مطلوبة.")
        else:
            slug = "".join(c if c.isalnum() else "-" for c in wn.lower())
            ws   = _post("workspaces",{"name":wn.strip(),"slug":slug,"plan":pl,"is_active":True})
            if ws:
                u = _post("users",{"workspace_id":ws["id"],"full_name":afn.strip(),
                                   "username":aun.strip().lower(),"email":aem.strip().lower(),
                                   "password":_h(apw),"role":"admin","created_by":0,"is_active":True})
                if u: st.success(f"✅ تم إنشاء **{wn}** والمدير **{afn}**!"); st.rerun()


def pg_sa_users():
    hdr("👥","جميع المستخدمين","عرض عبر كل الشركات")
    rows = _get("users", order="workspace_id.asc,id.asc")
    if rows:
        df = pd.DataFrame(rows)[["id","workspace_id","full_name","username","email","role","is_active","created_at"]]
        df["is_active"] = df["is_active"].map({True:"✅",False:"🚫",1:"✅",0:"🚫"})
        st.dataframe(df.rename(columns={"id":"#","workspace_id":"WS","full_name":"الاسم",
                                        "username":"المستخدم","email":"الإيميل","role":"الدور",
                                        "is_active":"نشط","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


def pg_sa_stats():
    hdr("📈","الإحصائيات التفصيلية","مقارنة أداء الشركات")
    ws_all = _get("workspaces"); o_all = _get("orders")
    if not ws_all: st.info("لا توجد شركات."); return
    data = []
    for ws in ws_all:
        wo   = [o for o in o_all if o.get("workspace_id")==ws["id"]]
        rev  = sum(float(o.get("total_price",0) or 0) for o in wo if o.get("status")=="تم التسليم")
        done = sum(1 for o in wo if o.get("status")=="تم التسليم")
        data.append({"الشركة":ws["name"],"الأوردرات":len(wo),"مكتملة":done,
                     "نسبة الإنجاز":f"{done/len(wo)*100:.0f}%" if wo else "0%",
                     "إيراد (د.ع)":f"{rev:,.0f}"})
    data.sort(key=lambda x: x["الأوردرات"], reverse=True)
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
#  WORKSPACE ADMIN PAGES
# ══════════════════════════════════════════════════════════════════════════════

def pg_admin_dash():
    hdr("🛡️","لوحة المدير","إحصائيات شركتك")
    guide("① راقب الأوردرات والمالية اليومية<br>"
          "② راجع طلبات الشراء والبلاغات والإشعارات<br>"
          "③ أضف فريقك من «الفريق»")
    WID   = wid(); today = _today()
    orders = _get("orders",{"workspace_id":WID})
    tot  = len(orders)
    tod  = sum(1 for o in orders if str(o.get("created_at","")).startswith(today))
    dn   = sum(1 for o in orders if o.get("status")=="تم التسليم")
    tv   = sum(float(o.get("total_price",0) or 0) for o in orders)
    rv   = sum(float(o.get("paid",0) or 0) for o in orders)
    rem  = sum(float(o.get("remaining",0) or 0) for o in orders)
    prs  = _get("purchase_requests",{"workspace_id":WID,"status":"قيد المراجعة"})
    irs  = _get("incident_reports",  {"workspace_id":WID,"status":"مفتوح"})
    usr  = _get("users",             {"workspace_id":WID,"is_active":True})
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("أوردرات اليوم",tod); c2.metric("مكتملة/إجمالي",f"{dn}/{tot}")
    c3.metric("إجمالي القيمة (د.ع)",f"{tv:,.0f}"); c4.metric("طلبات شراء معلقة",len(prs))
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("إجمالي المدفوع (د.ع)",f"{rv:,.0f}"); c6.metric("المتبقي (د.ع)",f"{rem:,.0f}")
    c7.metric("بلاغات مفتوحة",len(irs));              c8.metric("موظفون نشطون",len(usr))
    st.markdown("---")
    t1,t2,t3 = st.tabs(["📋 آخر الأوردرات","📦 طلبات الشراء","🚨 البلاغات"])
    with t1:
        last = sorted(orders,key=lambda x:x.get("id",0),reverse=True)[:12]
        if last:
            df = pd.DataFrame(last)[["order_number","customer_name","total_price","paid","remaining","status","created_at"]]
            st.dataframe(df.rename(columns={"order_number":"الأوردر","customer_name":"العميل",
                                            "total_price":"السعر","paid":"المدفوع","remaining":"المتبقي",
                                            "status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.info("لا توجد أوردرات.")
    with t2:
        if prs:
            df = pd.DataFrame(prs)[["requester_name","department","item_name","quantity","urgency","status","created_at"]]
            st.dataframe(df.rename(columns={"requester_name":"الموظف","department":"القسم",
                                            "item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية",
                                            "status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.info("لا توجد طلبات.")
    with t3:
        if irs:
            df = pd.DataFrame(irs)[["reporter_name","department","description","severity","status","created_at"]]
            st.dataframe(df.rename(columns={"reporter_name":"المبلّغ","department":"القسم",
                                            "description":"الوصف","severity":"الخطورة",
                                            "status":"الحالة","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)
        else: st.success("🎉 لا بلاغات!")


def pg_team():
    hdr("👥","إدارة الفريق","أضف أعضاء الفريق وحدد صلاحياتهم")
    guide("① أنت المدير — الوحيد الذي يضيف موظفين لشركتك<br>"
          "② كل موظف يرى فقط بيانات شركتك — عزل تام<br>"
          "③ يمكن تعطيل أي حساب من هنا")
    WID  = wid()
    rows = _get("users",{"workspace_id":WID},order="id.asc")
    if rows:
        df = pd.DataFrame(rows)[["id","full_name","username","email","role","is_active","created_at"]]
        df["is_active"] = df["is_active"].map({True:"✅ نشط",False:"🚫 موقوف",1:"✅ نشط",0:"🚫 موقوف"})
        st.dataframe(df.rename(columns={"id":"#","full_name":"الاسم","username":"المستخدم",
                                        "email":"الإيميل","role":"الدور","is_active":"الحالة",
                                        "created_at":"التاريخ"}),
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
        p2 = c6.text_input("التأكيد *",     type="password")
        ok = st.form_submit_button("✅ إضافة", use_container_width=True)
    if ok:
        errs=[]
        if not all([fn,un,em,p1]): errs.append("جميع الحقول مطلوبة.")
        if p1 and p1!=p2:          errs.append("كلمتا المرور غير متطابقتين.")
        if p1 and len(p1)<6:       errs.append("كلمة المرور 6 أحرف على الأقل.")
        for e in errs: st.error(e)
        if not errs:
            res = _post("users",{"workspace_id":WID,"full_name":fn.strip(),
                                 "username":un.strip().lower(),"email":em.strip().lower(),
                                 "password":_h(p1),"role":rl,
                                 "created_by":st.session_state["uid"],"is_active":True})
            if res: st.success(f"✅ تم إضافة **{fn}**!"); st.rerun()
            else:   st.error("❌ اسم المستخدم أو الإيميل مستخدم بالفعل.")
    st.markdown("---")
    st.markdown('<div class="sec">🔄 تفعيل / تعطيل</div>', unsafe_allow_html=True)
    emp = [u for u in (rows or []) if u.get("role") != "admin"]
    if emp:
        opts  = {f"{u['id']} — {u['full_name']} ({u['username']})":u["id"] for u in emp}
        label = st.selectbox("الموظف", list(opts.keys()))
        ut    = opts[label]
        ca,cb,_ = st.columns([1,1,3])
        if ca.button("✅ تفعيل",  key="act"):  _patch("users",{"id":ut},{"is_active":True});  st.rerun()
        if cb.button("🚫 تعطيل", key="dact"): _patch("users",{"id":ut},{"is_active":False}); st.rerun()
    else: st.info("لا يوجد موظفون بعد.")


def pg_support():
    hdr("📞","تواصل معنا","فريق دعم Z-ORDER")
    st.markdown(
        f'<div class="support-card">'
        f'<div style="font-size:2rem;margin-bottom:.5rem">🛎️</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:var(--t1)">فريق دعم Z-ORDER</div>'
        f'<div style="color:var(--t2);font-size:.84rem;margin:.35rem 0">نحن هنا لمساعدتك</div>'
        f'<div style="font-size:.94rem;color:var(--gold);font-weight:600;margin:.5rem 0">📞 {SUPPORT_PHONE}</div>'
        f'<a class="wa-btn" href="{SUPPORT_WA}" target="_blank">'
        f'<span style="font-size:1.1rem">💬</span> تواصل عبر واتساب</a>'
        f'</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;color:var(--t3);font-size:.76rem">'
        f'Developed by <b style="color:var(--gold)">{DEVELOPER}</b> · {APP_NAME} v{APP_VER}</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SALES PAGES
# ══════════════════════════════════════════════════════════════════════════════

def pg_sales_dash():
    hdr("📊","لوحتي","أوردراتك وإحصائياتك")
    guide("① أضف أوردراً من «أوردر جديد» — النموذج الكامل<br>"
          "② السعر والمبلغ المدفوع سري — لا يظهر لباقي الأقسام<br>"
          "③ معاينة التصاميم من «التصاميم»")
    uid  = st.session_state["uid"]; WID = wid()
    orders = _get("orders",{"workspace_id":WID,"created_by_id":uid})
    tot  = len(orders)
    dn   = sum(1 for o in orders if o.get("status")=="تم التسليم")
    tv   = sum(float(o.get("total_price",0) or 0) for o in orders)
    rem  = sum(float(o.get("remaining",0)  or 0) for o in orders)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي أوردراتي",tot); c2.metric("مُسلَّمة",dn)
    c3.metric("إجمالي القيمة (د.ع)",f"{tv:,.0f}"); c4.metric("المتبقي (د.ع)",f"{rem:,.0f}")
    st.markdown("---")
    show_orders("sales", uid_filter=uid, title="أوردراتي الأخيرة")


def pg_add_order():
    hdr("➕","أوردر جديد — Z-ORDER V2","أدخل تفاصيل الطلب يدوياً بحرية كاملة")

    with st.form("new_order_v2", clear_on_submit=True):

        # ── بيانات العميل ─────────────────────────────────────────────────
        st.markdown('<div class="sec">👤 بيانات العميل</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        cust  = c1.text_input("اسم العميل *",     placeholder="مثال: أحمد محمد")
        phone = c2.text_input("رقم الهاتف",       placeholder="مثال: 07901234567")

        # ── تفاصيل الطلب ──────────────────────────────────────────────────
        st.markdown('<div class="sec">🖨️ تفاصيل الطلب</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        qty_txt  = c3.text_input("الكمية *",
                                  placeholder="مثال: 500 كارت، 3 أمتار، 10 لفات")
        size_txt = c4.text_input("القياس",
                                  placeholder="مثال: A4، 50×70 سم، 90×50 مم")

        biz = st.text_input("النشاط التجاري",
                             placeholder="مثال: مطعم، محل ملابس، شركة إنشاء")

        desc = st.text_area("التفاصيل",
                             placeholder="ألوان الطباعة، عدد الوجوه، نوع الورق، ملاحظات...",
                             height=100)

        # ── التسعير والدفع (نصي حر) ────────────────────────────────────────
        st.markdown('<div class="sec">💰 التسعير والدفع (د.ع)</div>', unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        total_p_txt = c5.text_input(
            "السعر الكلي (د.ع) *",
            placeholder="مثال: 25,000 د.ع",
            help="اكتب السعر بحرية مع رمز العملة إن أردت"
        )
        paid_txt = c6.text_input(
            "المبلغ المدفوع (د.ع)",
            placeholder="مثال: 10,000 د.ع",
            help="المبلغ الذي دفعه العميل مقدماً"
        )

        # ── التاريخ ────────────────────────────────────────────────────────
        st.markdown('<div class="sec">📅 التاريخ</div>', unsafe_allow_html=True)
        order_date = st.date_input(
            "تاريخ الطلب",
            value=datetime.date.today(),
            help="تاريخ استلام الطلب — الافتراضي هو اليوم"
        )

        sub = st.form_submit_button("✅ حفظ الأوردر", use_container_width=True)

    # ── معالجة الإرسال ─────────────────────────────────────────────────────
    if sub:
        errors = []
        if not cust.strip():       errors.append("اسم العميل مطلوب.")
        if not qty_txt.strip():    errors.append("الكمية مطلوبة.")
        if not total_p_txt.strip(): errors.append("السعر الكلي مطلوب.")

        if errors:
            for e in errors: st.error(e)
        else:
            ono = _order_no()
            res = _post("orders", {
                "workspace_id":    wid(),
                "order_number":    ono,
                "customer_name":   cust.strip(),
                "customer_phone":  phone.strip(),
                "quantity":        qty_txt.strip(),
                "size":            size_txt.strip(),
                "paper_type":      biz.strip(),
                "description":     desc.strip(),
                "total_price":     total_p_txt.strip(),   # نصي مع العملة
                "paid":            paid_txt.strip(),       # نصي مع العملة
                "remaining":       "",                     # يُحسب يدوياً أو يُترك فارغاً
                "delivery_date":   str(order_date),
                "created_by_id":   st.session_state["uid"],
                "created_by_name": st.session_state["uname"],
                "status":          "جديد",
                "design_status":   "قيد الانتظار",
                "production_status":"قيد الانتظار",
                "delivered":       False,
            })

            if res:
                _push_notification(
                    wid(),
                    f"أوردر جديد: {ono}",
                    f"العميل: {cust.strip()} | الكمية: {qty_txt.strip()}",
                    target_roles=["design"],
                    order_id=res.get("id"),
                )
                st.success(f"✅ تم حفظ الأوردر **{ono}** بنجاح!")

                # ملخص الأوردر
                st.markdown(
                    f'<div class="order-summary"><table>'
                    f'<tr><td>رقم الأوردر</td><td>{ono}</td></tr>'
                    f'<tr><td>العميل</td><td>{cust.strip()}</td></tr>'
                    f'<tr><td>الهاتف</td><td>{phone.strip() or "—"}</td></tr>'
                    f'<tr><td>الكمية</td><td>{qty_txt.strip()}</td></tr>'
                    f'<tr><td>القياس</td><td>{size_txt.strip() or "—"}</td></tr>'
                    f'<tr><td>النشاط التجاري</td><td>{biz.strip() or "—"}</td></tr>'
                    f'<tr><td>التاريخ</td><td>{order_date}</td></tr>'
                    f'<tr class="total-row"><td>السعر الكلي</td><td>{total_p_txt.strip()}</td></tr>'
                    f'<tr><td>المدفوع</td><td>{paid_txt.strip() or "—"}</td></tr>'
                    f'</table></div>',
                    unsafe_allow_html=True,
                )


def pg_sales_preview():
    hdr("🖼️","معاينة التصاميم","ملفات التصميم المرفوعة قبل الطباعة")
    guide("① شاهد التصميم وحمّله للتأكد قبل إرساله للإنتاج<br>"
          "② الملفات محفوظة في Supabase Storage")
    rows = _get("orders",{"workspace_id":wid(),"design_status":"مكتمل"},order="id.desc")
    if not rows: st.info("لا توجد تصاميم مكتملة بعد."); return
    for r in rows:
        with st.expander(f"🎨 {r.get('order_number','')} — {r.get('customer_name','')}"):
            c1,c2 = st.columns(2)
            c1.markdown(f"**الورق:** {r.get('paper_type','')} · {r.get('size','')}")
            c1.markdown(f"**الكمية:** {r.get('quantity','')}")
            c2.markdown(f"**صمّمه:** {r.get('design_by','—')}")
            c2.markdown(f"**تاريخ التصميم:** {str(r.get('design_updated','—'))[:16]}")
            if r.get("design_notes"):
                st.markdown(f"**ملاحظات:** {r['design_notes']}")
            st.markdown("---")
            fu = r.get("design_file_url","") or r.get("design_link","")
            if fu:
                _dl_btn(fu,"⬇️ تحميل ملف التصميم")
                ext = fu.split(".")[-1].lower()
                if ext in ["png","jpg","jpeg","webp"]:
                    try:
                        rr = requests.get(fu, timeout=15)
                        if rr.status_code == 200:
                            st.image(rr.content, use_container_width=True)
                    except Exception: pass
            else: st.caption("لا يوجد ملف بعد.")

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def pg_design():
    hdr("🎨","قسم التصميم","ارفع ملف التصميم لكل أوردر")
    guide("① الملف يُرفع مباشرة لـ Supabase Storage — محفوظ للأبد<br>"
          "② بعد الرفع يتحول الأوردر إلى «جاهز للطباعة» ويصل إشعار للإنتاج<br>"
          "③ يمكن لقسم المبيعات معاينة الملف من «التصاميم»")
    WID  = wid()
    rows = _get("orders",{"workspace_id":WID},order="id.desc")
    pend = [r for r in rows if r.get("design_status")=="قيد الانتظار"]
    done = [r for r in rows if r.get("design_status")=="مكتمل"]

    t1,t2 = st.tabs([f"⏳ قيد الانتظار ({len(pend)})", f"✅ مكتملة ({len(done)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد مهام تصميم معلقة!")
        for r in pend:
            with st.expander(f"🔷 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**الورق:** {r.get('paper_type','')} · {r.get('size','')}")
                c1.markdown(f"**الكمية:** {r.get('quantity','')}")
                c2.markdown(f"**التاريخ:** {str(r.get('created_at',''))[:16]}")
                c2.markdown(f"**أضافه:** {r.get('created_by_name','')}")
                if r.get("description"):
                    st.markdown(f"**الوصف:** {r.get('description','')}")
                st.markdown("---")
                upld  = st.file_uploader("📎 رفع ملف التصميم *",
                                          key=f"du_{r['id']}",
                                          type=["pdf","png","jpg","jpeg","ai","psd","svg","eps","zip","cdr"])
                dl    = st.text_input("🔗 أو رابط التصميم",
                                      value=r.get("design_link","") or "", key=f"dl_{r['id']}")
                notes = st.text_area("📝 ملاحظات للإنتاج",
                                     value=r.get("design_notes","") or "",
                                     key=f"dn_{r['id']}", height=65)
                if st.button("✅ تأكيد رفع التصميم", key=f"dok_{r['id']}"):
                    file_url   = ""
                    store_path = r.get("design_storage_path","") or ""
                    if upld:
                        with st.spinner("جاري رفع الملف إلى Supabase Storage..."):
                            file_url, store_path = _upload(
                                upld.read(),
                                upld.name,
                                upld.type or "application/octet-stream",
                                subfolder="designs",
                            )
                    else:
                        file_url = r.get("design_file_url","") or ""
                    link = dl.strip() or r.get("design_link","")
                    if not file_url and not link:
                        st.error("⚠️ يجب رفع ملف أو إدخال رابط التصميم.")
                    else:
                        _patch("orders",{"id":r["id"]},{
                            "design_status":        "مكتمل",
                            "design_file_url":      file_url,
                            "design_storage_path":  store_path,
                            "design_link":          link,
                            "design_notes":         notes.strip(),
                            "design_updated":       _ts(),
                            "design_by":            st.session_state["uname"],
                            "status":               "جاهز للطباعة",
                        })
                        _push_notification(WID,
                                           f"تصميم جاهز: {r.get('order_number','')}",
                                           f"العميل: {r.get('customer_name','')} — يمكنكم البدء بالطباعة",
                                           target_roles=["production"],
                                           order_id=r["id"])
                        st.success("✅ تم رفع التصميم! إشعار أُرسل لقسم الإنتاج.")
                        _get_cached.clear(); st.rerun()

    with t2:
        if not done: st.info("لا توجد تصاميم مكتملة.")
        for r in done:
            co1, co2, co3 = st.columns([3, 1, 1])
            with co1:
                st.markdown(
                    f'<div class="card"><b>{r.get("order_number","")}</b> — {r.get("customer_name","")}'
                    f'&nbsp;{bdg("جاهز للطباعة")}'
                    f'<br><small style="color:var(--t3)">🗓 {str(r.get("design_updated","—"))[:16]}'
                    f' | 👤 {r.get("design_by","—")}</small></div>',
                    unsafe_allow_html=True)
            with co2:
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu: _dl_btn(fu,"⬇️ تحميل")
            with co3:
                # زر الحذف — يحذف الملف من Storage والسجل من DB
                if st.button("🗑️ حذف", key=f"del_ds_{r['id']}",
                             help="يحذف ملف التصميم من Storage ويحذف الطلب نهائياً"):
                    sp = r.get("design_storage_path","")
                    if sp: _storage_delete(sp)
                    # delete order row
                    try:
                        requests.delete(f"{REST}/orders",
                                        headers=RH,
                                        params={"id": f"eq.{r['id']}"}, timeout=10)
                    except Exception: pass
                    _get_cached.clear()
                    st.success("✅ تم حذف الطلب والملف من Storage.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCTION PAGE
# ══════════════════════════════════════════════════════════════════════════════

def pg_production():
    hdr("🖨️","قسم الإنتاج — Z-ORDER V2","نفّذ الأوردرات الجاهزة")
    guide("① الأوردر يظهر هنا فقط بعد رفع التصميم<br>"
          "② حمّل ملف التصميم واطبع<br>"
          "③ 'إتمام الطباعة وحذف الملف' يُكمل الطلب ويحذف الملف فيزيائياً من Storage لتوفير المساحة")
    WID   = wid()
    rows  = _get("orders",{"workspace_id":WID},order="id.desc")
    ready  = [r for r in rows if r.get("design_status")=="مكتمل" and r.get("production_status")=="قيد الانتظار"]
    prting = [r for r in rows if r.get("production_status")=="جاري الإنتاج"]
    done   = [r for r in rows if r.get("production_status")=="مكتمل"]

    t1,t2,t3 = st.tabs([f"🟢 جاهز ({len(ready)})",f"🟠 جاري ({len(prting)})",f"✅ مكتمل ({len(done)})"])

    def _complete_and_delete(order_row, pn=""):
        """Mark order as done AND delete design file from Storage."""
        _patch("orders",{"id":order_row["id"]},{
            "production_status":"مكتمل",
            "production_notes":pn,
            "production_updated":_ts(),
            "production_by":st.session_state["uname"],
            "status":"جاهز للتسليم",
            "design_file_url":"",          # clear URL from record
            "design_storage_path":"",      # clear path from record
        })
        # Delete file physically from Storage
        sp = order_row.get("design_storage_path","")
        if sp:
            deleted = _storage_delete(sp)
            if deleted:
                st.success("🗑️ ملف التصميم حُذف من Storage — تم توفير المساحة.")
        _push_notification(WID,
                           f"جاهز للتسليم: {order_row.get('order_number','')}",
                           f"العميل: {order_row.get('customer_name','')}",
                           target_roles=["admin","sales","agent"],
                           order_id=order_row["id"])
        _get_cached.clear()

    with t1:
        if not ready: st.info("⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم.")
        for r in ready:
            with st.expander(f"🟢 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                c1,c2 = st.columns(2)
                c1.markdown(f"**النشاط:** {r.get('paper_type','')} · {r.get('size','')}")
                c1.markdown(f"**الكمية:** {r.get('quantity','')}")
                c2.markdown(f"**ملاحظات التصميم:** {r.get('design_notes','—')}")
                c2.markdown(f"**صمّمه:** {r.get('design_by','—')}")

                # زر تحميل الملف
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu: _dl_btn(fu,"⬇️ تحميل ملف التصميم للطباعة")

                pn = st.text_area("📝 ملاحظات الإنتاج", key=f"pn_{r['id']}", height=55)

                col1, col2, col3 = st.columns(3)
                if col1.button("▶️ بدء الطباعة", key=f"st_{r['id']}"):
                    _patch("orders",{"id":r["id"]},{
                        "production_status":"جاري الإنتاج","production_notes":pn,
                        "production_updated":_ts(),"production_by":st.session_state["uname"],
                        "status":"جاري الإنتاج"})
                    _push_notification(WID,f"بدأت طباعة: {r.get('order_number','')}",
                                       f"العميل: {r.get('customer_name','')}",
                                       target_roles=["admin","sales"],order_id=r["id"])
                    _get_cached.clear(); st.success("▶️ بدأ الإنتاج!"); st.rerun()

                if col2.button("✅ إتمام مباشر", key=f"fi_{r['id']}"):
                    _complete_and_delete(r, pn)
                    st.success("✅ اكتمل — إشعار أُرسل!"); st.rerun()

                # زر أحمر: إتمام الطباعة وحذف الملف فيزيائياً
                st.markdown(
                    '<style>.del-btn button{background:linear-gradient(135deg,#ef4444,#b91c1c)'
                    '!important;}</style><div class="del-btn">',
                    unsafe_allow_html=True)
                if col3.button("🗑️ إتمام وحذف الملف", key=f"delprt_{r['id']}",
                               help="يُكمل الطلب ويحذف ملف التصميم نهائياً من Storage"):
                    _complete_and_delete(r, pn)
                    st.success("✅ مكتمل — الملف حُذف من Storage لتوفير المساحة!"); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        if not prting: st.info("لا توجد طباعة جارية.")
        for r in prting:
            with st.expander(f"🟠 {r.get('order_number','')}  —  {r.get('customer_name','')}"):
                st.markdown(f"**النشاط:** {r.get('paper_type','')} · {r.get('size','')} | **الكمية:** {r.get('quantity','')}")
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu: _dl_btn(fu,"⬇️ تحميل")

                col1, col2 = st.columns(2)
                if col1.button("✅ تحديد كمكتمل", key=f"fn_{r['id']}"):
                    _patch("orders",{"id":r["id"]},{
                        "production_status":"مكتمل","production_updated":_ts(),
                        "status":"جاهز للتسليم"})
                    _push_notification(WID,f"جاهز للتسليم: {r.get('order_number','')}",
                                       f"العميل: {r.get('customer_name','')}",
                                       target_roles=["admin","sales","agent"],order_id=r["id"])
                    _get_cached.clear(); st.success("✅ مكتمل!"); st.rerun()

                st.markdown(
                    '<style>.del-btn2 button{background:linear-gradient(135deg,#ef4444,#b91c1c)'
                    '!important;}</style><div class="del-btn2">',
                    unsafe_allow_html=True)
                if col2.button("🗑️ إتمام وحذف الملف", key=f"delprt2_{r['id']}",
                               help="يُكمل الطلب ويحذف ملف التصميم نهائياً من Storage"):
                    _complete_and_delete(r)
                    st.success("✅ مكتمل — الملف حُذف من Storage!"); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        if not done: st.info("لا توجد أوردرات مكتملة.")
        for r in done:
            file_deleted = not bool(r.get("design_file_url","") or r.get("design_storage_path",""))
            st.markdown(
                f'<div class="card"><b>{r.get("order_number","")}</b> — {r.get("customer_name","")}'
                f'&nbsp;{bdg(r.get("status","مكتمل"))}'
                f'&nbsp;{"🗑️ <small style=\"color:var(--t3)\">ملف محذوف</small>" if file_deleted else ""}'
                f'<br><small style="color:var(--t3)">اكتمل: {str(r.get("production_updated","—"))[:16]}'
                f' | {r.get("production_by","—")}</small></div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED PAGES (Purchase · Agent · Chat · Incidents · Financial)
# ══════════════════════════════════════════════════════════════════════════════

def pg_purchase_submit():
    hdr("📦","طلب شراء","اطلب مواد من قسم المشتريات")
    with st.form("pur", clear_on_submit=True):
        c1,c2 = st.columns(2)
        item  = c1.text_input("اسم الصنف *",  placeholder="حبر أسود، ورق A3...")
        qty   = c2.text_input("الكمية *",      placeholder="5 علب...")
        urg   = st.selectbox("الأولوية", ["عادي","عاجل","طارئ"])
        notes = st.text_area("ملاحظات", height=65)
        sub   = st.form_submit_button("📤 إرسال", use_container_width=True)
    if sub:
        if not item.strip() or not qty.strip(): st.error("يرجى تحديد الصنف والكمية.")
        else:
            role = st.session_state["role"]
            res  = _post("purchase_requests",{
                "workspace_id":wid(),"requester_id":st.session_state["uid"],
                "requester_name":st.session_state["uname"],"department":ROLES[role]["ar"],
                "item_name":item.strip(),"quantity":qty.strip(),
                "urgency":urg,"notes":notes.strip(),"status":"قيد المراجعة"})
            if res:
                _push_notification(wid(),f"طلب شراء جديد: {item.strip()}",
                                   f"من {st.session_state['uname']} | {urg}",
                                   target_roles=["purchase","admin"])
                st.success("✅ تم إرسال طلب الشراء!")
    st.markdown("---")
    rows = _get("purchase_requests",{"workspace_id":wid(),"requester_id":st.session_state["uid"]},
                order="id.desc",limit=10)
    if rows:
        df = pd.DataFrame(rows)[["item_name","quantity","urgency","status","created_at"]]
        st.dataframe(df.rename(columns={"item_name":"الصنف","quantity":"الكمية",
                                        "urgency":"الأولوية","status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)
    else: st.info("لم تقدم أي طلب بعد.")


def pg_purchase_manage():
    hdr("📦","إدارة طلبات الشراء","راجع وأدر جميع الطلبات")
    WID  = wid()
    rows = _get("purchase_requests",{"workspace_id":WID},order="id.desc")
    rows = sorted(rows, key=lambda r: {"طارئ":0,"عاجل":1,"عادي":2}.get(r.get("urgency","عادي"),2))
    pend = [r for r in rows if r.get("status")=="قيد المراجعة"]
    rest = [r for r in rows if r.get("status")!="قيد المراجعة"]
    t1,t2 = st.tabs([f"⏳ قيد المراجعة ({len(pend)})", f"📋 السجل ({len(rest)})"])
    with t1:
        if not pend: st.success("🎉 لا توجد طلبات معلقة!")
        for r in pend:
            uc = {"طارئ":"var(--red)","عاجل":"var(--acc2)","عادي":"var(--t2)"}.get(r.get("urgency","عادي"),"var(--t2)")
            with st.expander(f"📦 {r.get('item_name','')} — {r.get('requester_name','')} [{r.get('department','')}]"):
                st.markdown(
                    f"**الصنف:** {r.get('item_name','')} | **الكمية:** {r.get('quantity','')}"
                    f"<br>**الأولوية:** <span style='color:{uc}'>{r.get('urgency','')}</span>"
                    f" | **التاريخ:** {str(r.get('created_at',''))[:16]}"
                    f"{'<br>**ملاحظات:** '+r.get('notes','') if r.get('notes') else ''}",
                    unsafe_allow_html=True)
                col1,col2 = st.columns(2)
                if col1.button("✅ موافقة", key=f"app_{r['id']}"):
                    _patch("purchase_requests",{"id":r["id"]},
                           {"status":"موافق عليه","reviewed_by":st.session_state["uname"],"reviewed_at":_ts()})
                    st.success("✅ موافق."); _get_cached.clear(); st.rerun()
                if col2.button("❌ رفض", key=f"rej_{r['id']}"):
                    _patch("purchase_requests",{"id":r["id"]},
                           {"status":"مرفوض","reviewed_by":st.session_state["uname"],"reviewed_at":_ts()})
                    st.warning("تم الرفض."); _get_cached.clear(); st.rerun()
    with t2:
        if not rest: st.info("لا يوجد سجل.")
        else:
            df = pd.DataFrame(rest)[["requester_name","department","item_name",
                                     "quantity","urgency","status","reviewed_by","created_at"]]
            st.dataframe(df.rename(columns={"requester_name":"الموظف","department":"القسم",
                                            "item_name":"الصنف","quantity":"الكمية","urgency":"الأولوية",
                                            "status":"الحالة","reviewed_by":"راجعه","created_at":"التاريخ"}),
                         use_container_width=True, hide_index=True)


def pg_agent_new():
    hdr("🗺️","تسجيل زيارة عميل","وثّق زيارتك الميدانية")
    with st.form("av", clear_on_submit=True):
        cust  = st.text_input("👤 اسم العميل / المحل *")
        loc   = st.text_input("📍 العنوان", placeholder="الشارع، الحي، المدينة")
        vs    = st.selectbox("📊 حالة العميل", ["محتمل","اشترى","لن يشتري"])
        notes = st.text_area("📝 ملاحظات", height=65)
        img   = st.file_uploader("📸 صورة المحل أو الوصل",
                                  type=["jpg","jpeg","png","webp"],
                                  help="يُرفع إلى Supabase Storage")
        sub   = st.form_submit_button("✅ حفظ الزيارة", use_container_width=True)
    if sub:
        if not cust.strip(): st.error("يرجى إدخال اسم العميل.")
        else:
            img_url = ""
            if img:
                with st.spinner("رفع الصورة..."):
                    img_url, _ = _upload(img.read(),
                                         img.name,
                                         img.type or "image/jpeg",
                                         subfolder="agents")
            res = _post("agent_visits",{
                "workspace_id":wid(),"agent_id":st.session_state["uid"],
                "agent_name":st.session_state["uname"],"customer_name":cust.strip(),
                "location":loc.strip(),"visit_status":vs,"notes":notes.strip(),"image_path":img_url})
            if res: st.success(f"✅ تم تسجيل زيارة **{cust.strip()}**!")


def pg_agent_my():
    hdr("📋","زياراتي","سجل زياراتك")
    rows = _get("agent_visits",
                {"workspace_id":wid(),"agent_id":st.session_state["uid"]},order="id.desc")
    if not rows: st.info("لم تسجّل أي زيارة بعد."); return
    for r in rows:
        c, l = AGT_MAP.get(r.get("visit_status","محتمل"),("b-apot","🔵"))
        ih = ""
        ip = r.get("image_path","")
        if ip and ip.startswith("http"):
            try:
                ir = requests.get(ip, timeout=10)
                if ir.status_code == 200:
                    b64 = base64.b64encode(ir.content).decode()
                    ct  = ir.headers.get("content-type","image/jpeg")
                    ih  = (f'<br><img src="data:{ct};base64,{b64}" '
                           f'style="max-width:100%;max-height:150px;border-radius:8px;'
                           f'margin-top:.35rem;object-fit:cover">')
            except Exception: pass
        st.markdown(
            f'<div class="card"><b>{r.get("customer_name","")}</b>'
            f'&nbsp;<span class="badge {c}">{l}</span>'
            f'<br><small style="color:var(--t2)">📍 {r.get("location","—")} | 🗓 {str(r.get("visited_at",""))[:16]}</small>'
            f'{"<br><small>"+r.get("notes","")+"</small>" if r.get("notes") else ""}'
            f'{ih}</div>', unsafe_allow_html=True)


def pg_agent_reports():
    hdr("🗺️","تقارير المندوبين","أداء فريق المبيعات الميداني")
    visits = _get("agent_visits",{"workspace_id":wid()})
    if not visits: st.info("لا توجد زيارات."); return
    ag = {}
    for v in visits:
        n = v.get("agent_name","")
        ag.setdefault(n,{"الزيارات":0,"اشترى":0,"محتمل":0,"لن يشتري":0,"آخر زيارة":""})
        ag[n]["الزيارات"]+=1
        vs = v.get("visit_status","محتمل")
        ag[n][vs] = ag[n].get(vs,0)+1
        if str(v.get("visited_at","")) > ag[n]["آخر زيارة"]:
            ag[n]["آخر زيارة"] = str(v.get("visited_at",""))[:16]
    st.dataframe(pd.DataFrame([{"المندوب":k,**v} for k,v in ag.items()]),
                 use_container_width=True, hide_index=True)


def pg_chat():
    hdr("💬","محادثة الفريق — Z-ORDER V2","معزولة لشركتك · يدعم @تاغ الأقسام")
    guide("① اكتب @المبيعات أو @التصميم أو @الإنتاج لإرسال إشعار للقسم المعني<br>"
          "② الأصوات والإشعارات تعمل على المتصفح وتطبيق PWA<br>"
          "③ المحادثة معزولة — لا يراها موظفو شركات أخرى")
    WID = wid(); uid = st.session_state["uid"]

    # ── إشعار صوتي للرسائل الجديدة (يُشغَّل عبر JS bridge) ──────────────────
    st.markdown(
        '<script>if(window.zPlayBeep) window.zPlayBeep(660,120);</script>',
        unsafe_allow_html=True)

    with st.form("cf", clear_on_submit=True):
        msg  = st.text_input(
            "✍️ اكتب رسالتك...",
            placeholder="مثال: @التصميم ملف الكارت جاهز للمراجعة")
        sent = st.form_submit_button("إرسال ←", use_container_width=True)

    if sent and msg.strip():
        _post("chat_messages",{"workspace_id":WID,"sender_id":uid,
                               "sender_name":st.session_state["uname"],
                               "sender_role":st.session_state["role"],
                               "message":msg.strip()})

        # ── @mention detection → push notification to tagged role ──────────
        MENTION_MAP = {
            "@المبيعات":  "sales",    "@sales":    "sales",
            "@التصميم":   "design",   "@design":   "design",
            "@الإنتاج":   "production","@production":"production",
            "@المشتريات": "purchase", "@purchase": "purchase",
            "@المندوب":   "agent",    "@agent":    "agent",
            "@المدير":    "admin",    "@admin":    "admin",
        }
        tagged_roles = []
        for tag, role in MENTION_MAP.items():
            if tag in msg:
                tagged_roles.append(role)
        if tagged_roles:
            _push_notification(
                WID,
                f"📢 تاغ من {st.session_state['uname']}",
                msg.strip()[:100],
                target_roles=tagged_roles,
            )
            # trigger browser notification via JS
            st.markdown(
                f'<script>if(window.zCheckMention) '
                f'window.zCheckMention({repr(msg.strip())}, '
                f'{repr(st.session_state["role"])});</script>',
                unsafe_allow_html=True)

        _get_cached.clear(); st.rerun()

    msgs = _get("chat_messages",{"workspace_id":WID},order="id.desc",limit=60)
    msgs.reverse()
    if not msgs: st.info("لا توجد رسائل. ابدأ المحادثة!"); return
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for m in msgs:
        is_me = m.get("sender_id") == uid
        ri    = ROLES.get(m.get("sender_role",""),{"clr":"#e8a020"})
        cls   = "me" if is_me else "other"
        st.markdown(
            f'<div class="bubble {cls}">'
            f'<div class="bn" style="color:{ri["clr"]}">'
            f'{m.get("sender_name","")} · {ROLES.get(m.get("sender_role",""),{"ar":""})["ar"]}</div>'
            f'{m.get("message","")}'
            f'<div class="bt">{str(m.get("sent_at",""))[:16]}</div>'
            f'</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


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
            res = _post("incident_reports",{
                "workspace_id":wid(),"reporter_id":st.session_state["uid"],
                "reporter_name":st.session_state["uname"],"department":ROLES[role]["ar"],
                "description":desc.strip(),"severity":sev,"status":"مفتوح"})
            if res:
                _push_notification(wid(),f"بلاغ {sev}: من {ROLES[role]['ar']}",
                                   desc.strip()[:80],target_roles=["admin"])
                st.success("✅ تم إرسال البلاغ للمدير!")
    rows = _get("incident_reports",{"workspace_id":wid(),"reporter_id":st.session_state["uid"]},
                order="id.desc",limit=8)
    if rows:
        df = pd.DataFrame(rows)[["description","severity","status","created_at"]]
        st.dataframe(df.rename(columns={"description":"الوصف","severity":"الخطورة",
                                        "status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)


def pg_all_incidents():
    hdr("🚨","بلاغات الأعطال","جميع البلاغات الواردة")
    rows = _get("incident_reports",{"workspace_id":wid()},order="id.desc")
    if not rows: st.success("🎉 لا توجد بلاغات!"); return
    op = [r for r in rows if r.get("status")=="مفتوح"]
    rs = [r for r in rows if r.get("status")!="مفتوح"]
    t1,t2 = st.tabs([f"🔴 مفتوحة ({len(op)})",f"✅ محلولة ({len(rs)})"])
    for tab,lst in [(t1,op),(t2,rs)]:
        with tab:
            if not lst: st.info("لا توجد."); continue
            for r in lst:
                sc,sl = SEV_MAP.get(r.get("severity","متوسط"),("b-sev-md","🟡"))
                with st.expander(f'{sl} {r.get("severity","")}  —  {r.get("department","")}  —  {str(r.get("created_at",""))[:16]}'):
                    st.markdown(f"**المبلّغ:** {r.get('reporter_name','')}<br>**الوصف:** {r.get('description','')}",
                                unsafe_allow_html=True)
                    if r.get("status")=="مفتوح":
                        if st.button("✅ محلول", key=f"rs_{r['id']}"):
                            _patch("incident_reports",{"id":r["id"]},
                                   {"status":"محلول","resolved_at":_ts()})
                            _get_cached.clear(); st.rerun()
                    else: st.caption(f"تم الحل: {str(r.get('resolved_at',''))[:16]}")


def pg_financial():
    hdr("💰","التقارير المالية","للمبيعات ومدير الشركة فقط")
    WID   = wid()
    rows  = _get("orders",{"workspace_id":WID},order="id.desc")
    tv    = sum(float(o.get("total_price",0) or 0) for o in rows)
    paid  = sum(float(o.get("paid",0)        or 0) for o in rows)
    rem   = sum(float(o.get("remaining",0)   or 0) for o in rows)
    cnt   = len(rows)
    avg   = tv/cnt if cnt else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي القيمة (د.ع)",  f"{tv:,.0f}")
    c2.metric("إجمالي المدفوع (د.ع)", f"{paid:,.0f}")
    c3.metric("إجمالي المتبقي (د.ع)", f"{rem:,.0f}")
    c4.metric("متوسط الأوردر (د.ع)",  f"{avg:,.0f}")
    st.markdown("---")
    if not rows: st.info("لا توجد أوردرات."); return
    df = pd.DataFrame(rows)[["order_number","customer_name","paper_type","size",
                              "quantity","total_price","paid","remaining","status","delivery_date","created_at"]]
    st.dataframe(df.rename(columns={
        "order_number":"الأوردر","customer_name":"العميل","paper_type":"الورق","size":"القياس",
        "quantity":"الكمية","total_price":"السعر الكلي","paid":"المدفوع","remaining":"المتبقي",
        "status":"الحالة","delivery_date":"التسليم","created_at":"التاريخ"
    }), use_container_width=True, hide_index=True)
    ws_name = st.session_state.get("workspace_name","")
    header  = (f"Z-ORDER — تقرير مالي\nWorkspace: {ws_name}\n"
               f"Developed by: {DEVELOPER}\nتاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    st.download_button("⬇️ تصدير CSV",
        (header+df.to_csv(index=False)).encode("utf-8-sig"),
        file_name=f"zorder_financial_{datetime.date.today()}.csv",
        mime="text/csv", use_container_width=True)


def pg_generic_dash(role):
    hdr("📊","لوحتي","نظرة عامة")
    WID   = wid()
    rows  = _get("orders",{"workspace_id":WID})
    tot   = len(rows)
    nw    = sum(1 for o in rows if o.get("status")=="جديد")
    ip    = sum(1 for o in rows if o.get("production_status")=="جاري الإنتاج")
    dn    = sum(1 for o in rows if o.get("status")=="تم التسليم")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي",tot); c2.metric("جديدة",nw); c3.metric("جاري",ip); c4.metric("مُسلَّمة",dn)
    st.markdown("---")
    recent = sorted(rows,key=lambda x:x.get("id",0),reverse=True)[:10]
    if recent:
        df = pd.DataFrame(recent)[["order_number","customer_name","paper_type","size","quantity","status","created_at"]]
        st.dataframe(df.rename(columns={"order_number":"الأوردر","customer_name":"العميل",
                                        "paper_type":"الورق","size":"القياس","quantity":"الكمية",
                                        "status":"الحالة","created_at":"التاريخ"}),
                     use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN: MOCKUP UPLOAD — visible to sales only for approval
# ══════════════════════════════════════════════════════════════════════════════

def pg_design_mockup():
    hdr("🖼️","رفع Mockup للمراجعة","ارفع صورة Mockup للتصميم — تظهر لقسم المبيعات فقط للاعتماد")
    guide("① ارفع صورة Mockup لكل أوردر (PNG/JPG/WEBP)<br>"
          "② الصورة تُخزَّن في Supabase Storage وتظهر للمبيعات فقط<br>"
          "③ المبيعات تعتمد أو ترفض من «التصاميم»")
    WID  = wid()
    rows = _get("orders", {"workspace_id": WID}, order="id.desc")
    # Show orders that have no mockup yet or already have one
    for r in rows:
        with st.expander(f"🖼️ {r.get('order_number','')} — {r.get('customer_name','')} "
                         f"{'✅ Mockup موجود' if r.get('mockup_url') else ''}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**الكمية:** {r.get('quantity','')}")
            c1.markdown(f"**الحالة:** {r.get('status','')}")

            # Show existing mockup
            existing = r.get("mockup_url","")
            if existing:
                try:
                    rr = requests.get(existing, timeout=10)
                    if rr.status_code == 200:
                        c2.image(rr.content, caption="Mockup الحالي", use_container_width=True)
                except Exception:
                    c2.markdown(f'[🔗 فتح Mockup]({existing})')

            st.markdown("---")
            mock_file = st.file_uploader(
                "📸 ارفع صورة Mockup",
                key=f"mock_{r['id']}",
                type=["png","jpg","jpeg","webp"],
                help="صورة المنتج النهائي للمراجعة"
            )
            if st.button("⬆️ رفع Mockup للمراجعة", key=f"mock_up_{r['id']}"):
                if not mock_file:
                    st.error("يرجى اختيار صورة أولاً.")
                else:
                    with st.spinner("جاري رفع Mockup..."):
                        mock_url, mock_path = _upload(
                            mock_file.read(),
                            mock_file.name,
                            mock_file.type or "image/png",
                            subfolder="mockups",
                        )
                    if mock_url:
                        _patch("orders", {"id": r["id"]}, {
                            "mockup_url":  mock_url,
                            "mockup_path": mock_path,
                            "mockup_status": "قيد المراجعة",
                        })
                        _push_notification(
                            WID,
                            f"Mockup جديد للمراجعة: {r.get('order_number','')}",
                            f"العميل: {r.get('customer_name','')} — يرجى المراجعة والاعتماد",
                            target_roles=["sales", "admin"],
                            order_id=r["id"],
                        )
                        _get_cached.clear()
                        st.success("✅ تم رفع Mockup! إشعار أُرسل لقسم المبيعات للمراجعة.")
                        st.rerun()
                    else:
                        st.error("❌ فشل الرفع. تحقق من الاتصال بـ Supabase Storage.")


# ── Update sales preview to show mockup approval ─────────────────────────────
def pg_sales_preview_v2():
    hdr("🖼️","التصاميم والـ Mockup","راجع واعتمد ملفات التصميم والـ Mockup")
    WID  = wid()
    rows = _get("orders", {"workspace_id": WID}, order="id.desc")

    t1, t2 = st.tabs(["🖼️ Mockup للاعتماد", "📁 ملفات التصميم"])

    with t1:
        mock_rows = [r for r in rows if r.get("mockup_url")]
        if not mock_rows:
            st.info("لا توجد Mockups للمراجعة بعد.")
        for r in mock_rows:
            status_color = {
                "قيد المراجعة": "var(--gold)",
                "معتمد":        "var(--grn)",
                "مرفوض":        "var(--red)",
            }.get(r.get("mockup_status",""), "var(--t2)")
            with st.expander(
                f"🖼️ {r.get('order_number','')} — {r.get('customer_name','')} "
                f"[{r.get('mockup_status','—')}]"
            ):
                st.markdown(
                    f"<span style='color:{status_color};font-weight:700'>"
                    f"{r.get('mockup_status','—')}</span>",
                    unsafe_allow_html=True)

                # Show mockup image
                mu = r.get("mockup_url","")
                if mu:
                    try:
                        rr = requests.get(mu, timeout=15)
                        if rr.status_code == 200:
                            st.image(rr.content, use_container_width=True)
                    except Exception:
                        st.markdown(f'[🔗 فتح Mockup]({mu})')

                st.markdown("---")
                col1, col2 = st.columns(2)
                if col1.button("✅ اعتماد Mockup", key=f"mock_appr_{r['id']}"):
                    _patch("orders", {"id": r["id"]}, {"mockup_status": "معتمد"})
                    _push_notification(WID, f"✅ Mockup معتمد: {r.get('order_number','')}",
                                       f"المبيعات اعتمدت التصميم",
                                       target_roles=["design"], order_id=r["id"])
                    _get_cached.clear(); st.success("✅ تم اعتماد Mockup!"); st.rerun()
                if col2.button("❌ رفض Mockup", key=f"mock_rej_{r['id']}"):
                    _patch("orders", {"id": r["id"]}, {"mockup_status": "مرفوض"})
                    _push_notification(WID, f"❌ Mockup مرفوض: {r.get('order_number','')}",
                                       f"يرجى التعديل وإعادة الرفع",
                                       target_roles=["design"], order_id=r["id"])
                    _get_cached.clear(); st.warning("تم الرفض — إشعار أُرسل للمصمم."); st.rerun()

    with t2:
        design_rows = [r for r in rows if r.get("design_status") == "مكتمل"]
        if not design_rows:
            st.info("لا توجد ملفات تصميم مكتملة بعد.")
        for r in design_rows:
            with st.expander(f"🎨 {r.get('order_number','')} — {r.get('customer_name','')}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الكمية:** {r.get('quantity','')}")
                c2.markdown(f"**صمّمه:** {r.get('design_by','—')}")
                fu = r.get("design_file_url","") or r.get("design_link","")
                if fu:
                    _dl_btn(fu, "⬇️ تحميل ملف التصميم")
                    ext = fu.split(".")[-1].lower()
                    if ext in ["png","jpg","jpeg","webp"]:
                        try:
                            rr = requests.get(fu, timeout=15)
                            if rr.status_code == 200:
                                st.image(rr.content, use_container_width=True)
                        except Exception: pass
                else:
                    st.caption("لا يوجد ملف بعد.")


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT: FIELD ORDER — مندوب يرفع أوردر من الميدان
# ══════════════════════════════════════════════════════════════════════════════

def pg_agent_order():
    hdr("➕","أوردر ميداني","أدخل طلب العميل مباشرة من الميدان")
    guide("① أدخل تفاصيل الطلب كما يطلبها العميل في الميدان<br>"
          "② الأوردر يصل فوراً للوحة التحكم وقسم التصميم<br>"
          "③ يمكنك إرفاق صورة للطلب المكتوب أو العينة")

    with st.form("agent_order_form", clear_on_submit=True):
        st.markdown('<div class="sec">👤 بيانات العميل</div>', unsafe_allow_html=True)
        cust  = st.text_input("اسم العميل / المحل *", placeholder="مثال: محل أحمد للملابس")
        phone = st.text_input("رقم الهاتف",           placeholder="مثال: 07901234567")
        loc   = st.text_input("📍 الموقع / العنوان",  placeholder="مثال: شارع الكندي، بغداد")

        st.markdown('<div class="sec">🖨️ تفاصيل الطلب</div>', unsafe_allow_html=True)
        qty_txt  = st.text_input("الكمية *",      placeholder="مثال: 500 كارت، 2 بنر")
        size_txt = st.text_input("القياس",         placeholder="مثال: A4، 80×60 سم")
        biz      = st.text_input("النشاط التجاري", placeholder="مثال: محل ملابس، مطعم")
        desc     = st.text_area("التفاصيل",        placeholder="ألوان، ملاحظات، نوع الورق...", height=80)

        st.markdown('<div class="sec">💰 السعر (إن وُجد)</div>', unsafe_allow_html=True)
        price_txt = st.text_input("السعر الكلي (د.ع)", placeholder="مثال: 35,000 د.ع")

        # صورة الطلب المكتوب أو العينة
        st.markdown('<div class="sec">📸 صورة الطلب (اختياري)</div>', unsafe_allow_html=True)
        order_img = st.file_uploader("ارفع صورة الطلب أو العينة",
                                     type=["jpg","jpeg","png","webp"],
                                     help="صورة الطلب المكتوب أو عينة العميل")

        sub = st.form_submit_button("✅ إرسال الأوردر للمكتب", use_container_width=True)

    if sub:
        if not cust.strip() or not qty_txt.strip():
            st.error("اسم العميل والكمية مطلوبان.")
        else:
            img_url = ""
            if order_img:
                with st.spinner("رفع صورة الطلب..."):
                    img_url, _ = _upload(
                        order_img.read(),
                        order_img.name,
                        order_img.type or "image/jpeg",
                        subfolder="agent_orders",
                    )

            ono = _order_no()
            res = _post("orders", {
                "workspace_id":    wid(),
                "order_number":    ono,
                "customer_name":   cust.strip(),
                "customer_phone":  phone.strip(),
                "quantity":        qty_txt.strip(),
                "size":            size_txt.strip(),
                "paper_type":      biz.strip(),
                "description":     (desc.strip() +
                                    (f"\n📍 الموقع: {loc.strip()}" if loc.strip() else "") +
                                    (f"\n👤 أضافه المندوب: {st.session_state['uname']}" ) ),
                "total_price":     price_txt.strip(),
                "paid":            "",
                "remaining":       "",
                "delivery_date":   str(datetime.date.today()),
                "created_by_id":   st.session_state["uid"],
                "created_by_name": f"مندوب: {st.session_state['uname']}",
                "status":          "جديد",
                "design_status":   "قيد الانتظار",
                "production_status":"قيد الانتظار",
                "delivered":       False,
                # Store agent image in mockup_url field for visibility
                "mockup_url":      img_url,
            })

            if res and isinstance(res, dict) and "id" in res:
                _push_notification(
                    wid(),
                    f"📍 أوردر ميداني جديد: {ono}",
                    f"المندوب {st.session_state['uname']} | العميل: {cust.strip()} | {qty_txt.strip()}",
                    target_roles=["admin", "sales", "design"],
                    order_id=res["id"],
                )
                st.success(
                    f"✅ تم إرسال الأوردر **{ono}** للمكتب!\n\n"
                    f"العميل: {cust.strip()} | الكمية: {qty_txt.strip()}")
            else:
                st.error(f"❌ فشل الإرسال: {_post_err(res) if res else 'لا استجابة من Supabase'}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # 1. Auth gate — nothing renders until logged in
    if not auth_screen():
        footer(); return

    role   = st.session_state["role"]
    active = top_nav()

    st.markdown('<div class="pw">', unsafe_allow_html=True)

    # ── SUPER-ADMIN ──────────────────────────────────────────────────────────
    if   role == "superadmin" and active == "📊 لوحة التحكم":  pg_sa_dash()
    elif role == "superadmin" and active == "🏢 الشركات":       pg_sa_companies()
    elif role == "superadmin" and active == "👥 المستخدمون":    pg_sa_users()
    elif role == "superadmin" and active == "📈 الإحصائيات":    pg_sa_stats()

    # ── ADMIN ────────────────────────────────────────────────────────────────
    elif role == "admin" and active == "📊 الرئيسية":  pg_admin_dash()
    elif role == "admin" and active == "👥 الفريق":    pg_team()
    elif role == "admin" and active == "📋 الأوردرات": show_orders("admin",title="جميع الأوردرات")
    elif role == "admin" and active == "💰 المالية":   pg_financial()
    elif role == "admin" and active == "🔔 الإشعارات": pg_notifications()
    elif role == "admin" and active == "🚨 البلاغات":  pg_all_incidents()
    elif role == "admin" and active == "🗺️ المندوبون": pg_agent_reports()
    elif role == "admin" and active == "💬 المحادثة":  pg_chat()
    elif role == "admin" and active == "📞 تواصل معنا": pg_support()

    # ── SALES ────────────────────────────────────────────────────────────────
    elif role == "sales" and active == "📊 الرئيسية":    pg_sales_dash()
    elif active == "➕ أوردر جديد":                       pg_add_order()
    elif active == "📋 أوردراتي":
        show_orders("sales", uid_filter=st.session_state["uid"], title="أوردراتي")
    elif active == "🖼️ التصاميم":                         pg_sales_preview_v2()   # updated
    elif role == "sales" and active == "💰 تقريري":       pg_financial()
    elif role == "sales" and active == "🔔 إشعاراتي":     pg_notifications()

    # ── DESIGN ───────────────────────────────────────────────────────────────
    elif role == "design" and active == "📊 الرئيسية":           pg_generic_dash(role)
    elif active == "🎨 التصميم":                                  pg_design()
    elif role == "design" and active == "🖼️ Mockup للمبيعات":    pg_design_mockup()
    elif role == "design" and active == "🔔 إشعاراتي":           pg_notifications()

    # ── PURCHASE ─────────────────────────────────────────────────────────────
    elif role == "purchase" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "📦 طلبات الشراء":                      pg_purchase_manage()

    # ── PRODUCTION ───────────────────────────────────────────────────────────
    elif role == "production" and active == "📊 الرئيسية":  pg_generic_dash(role)
    elif active == "🖨️ الإنتاج":                             pg_production()
    elif role == "production" and active == "📋 الأوردرات": show_orders("production",title="الأوردرات")
    elif role == "production" and active == "🔔 إشعاراتي":  pg_notifications()

    # ── AGENT ────────────────────────────────────────────────────────────────
    elif role == "agent" and active == "📊 الرئيسية":   pg_generic_dash(role)
    elif role == "agent" and active == "➕ أوردر ميداني": pg_agent_order()     # NEW
    elif active == "🗺️ زيارة جديدة":                    pg_agent_new()
    elif active == "📋 زياراتي":                         pg_agent_my()

    # ── SHARED ───────────────────────────────────────────────────────────────
    elif active == "📦 طلب شراء":  pg_purchase_submit()
    elif active == "🚨 بلاغ":       pg_incident_submit()
    elif active == "💬 المحادثة":   pg_chat()

    else:
        st.warning(f"الصفحة «{active}» غير متاحة.")

    st.markdown('</div>', unsafe_allow_html=True)
    footer()


if __name__ == "__main__":
    main()
