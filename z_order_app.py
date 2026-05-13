"""
╔══════════════════════════════════════════════════════════════════════╗
║          Z-ORDER  —  SaaS-Ready Print Workflow Platform             ║
║          نظام إدارة مطبعة متكامل وقابل للتوسع التجاري              ║
╠══════════════════════════════════════════════════════════════════════╣
║  Developer : Abdulrahman Fallah                                     ║
║  Version   : 2.0.0                                                  ║
║  Stack     : Python · Streamlit · SQLite3                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  التشغيل لأول مرة:                                                  ║
║    pip install streamlit pillow                                     ║
║    streamlit run z_order_app.py                                     ║
║                                                                      ║
║  حساب المدير الافتراضي:                                             ║
║    Email    : admin@zorder.iq                                       ║
║    Password : Admin@2025                                            ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import sqlite3
import hashlib
import datetime
import os
import base64
import pandas as pd
from pathlib import Path

# ══════════════════════════════════════════════
#  APP CONFIG
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="Z-Order | منصة إدارة المطبعة",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEVELOPER  = "Abdulrahman Fallah"
APP_NAME   = "Z-Order"
APP_VER    = "2.0.0"
DB_PATH    = "z_order.db"
UPLOAD_DIR = Path("z_order_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ROLES = {
    "admin":      {"label": "المدير العام",    "icon": "🛡️"},
    "sales":      {"label": "المبيعات",         "icon": "💼"},
    "design":     {"label": "التصميم",          "icon": "🎨"},
    "purchase":   {"label": "المشتريات",        "icon": "📦"},
    "production": {"label": "الإنتاج",          "icon": "🖨️"},
    "agent":      {"label": "مندوب مبيعات",    "icon": "🗺️"},
}

# ══════════════════════════════════════════════
#  GLOBAL CSS — Dark Industrial / Mobile-First
# ══════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg0:#07080a; --bg1:#0e1015; --bg2:#141720; --bg3:#1b1f2c;
  --bg4:#222739; --border:#252a38; --border2:#2e3447;
  --acc:#e8a020; --acc2:#ff6b35; --acc3:#ffd166;
  --blue:#3b82f6; --green:#22c55e; --red:#ef4444;
  --purple:#a855f7; --cyan:#06b6d4;
  --t1:#eef0f4; --t2:#8b95a8; --t3:#454e63;
  --r:10px; --r2:16px;
  --shadow:0 4px 24px rgba(0,0,0,0.4);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans Arabic', sans-serif !important;
  background: var(--bg0) !important;
  color: var(--t1) !important;
  direction: rtl;
}

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg1); }
::-webkit-scrollbar-thumb { background:var(--bg4); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--acc); }

section[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-left: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--t1) !important; }

.stApp { background: var(--bg0) !important; }
.main .block-container {
  padding: 1.5rem 1.5rem 5rem !important;
  max-width: 1400px !important;
}

.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div,
.stNumberInput>div>div>input {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  color: var(--t1) !important;
  font-family: 'IBM Plex Sans Arabic', sans-serif !important;
}

.stButton>button {
  background: linear-gradient(135deg,var(--acc),var(--acc2)) !important;
  color:#07080a !important;
  font-weight:700 !important;
  border:none !important;
  border-radius:var(--r) !important;
  padding:.55rem 1.3rem !important;
  font-family:'IBM Plex Sans Arabic',sans-serif !important;
  transition:all .2s !important;
  width:100%;
}
.stButton>button:hover {
  transform:translateY(-2px) !important;
  box-shadow:0 6px 24px rgba(232,160,32,.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
  background:var(--bg2) !important;
  border-radius:var(--r) !important;
  gap:4px !important; padding:4px !important;
  border:1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background:transparent !important;
  color:var(--t2) !important;
  border-radius:8px !important;
  font-weight:500 !important;
  border:none !important;
}
.stTabs [aria-selected="true"] {
  background:var(--bg4) !important;
  color:var(--acc) !important;
  border-bottom:2px solid var(--acc) !important;
}

[data-testid="stMetric"] {
  background:var(--bg2) !important;
  border:1px solid var(--border2) !important;
  border-radius:var(--r2) !important;
  padding:1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color:var(--t2) !important; font-size:.78rem !important; }
[data-testid="stMetricValue"] {
  color:var(--acc) !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:1.5rem !important;
}

.streamlit-expanderHeader {
  background:var(--bg2) !important;
  border:1px solid var(--border2) !important;
  border-radius:var(--r) !important;
  color:var(--t1) !important;
}
.streamlit-expanderContent {
  background:var(--bg1) !important;
  border:1px solid var(--border2) !important;
  border-top:none !important;
  border-radius:0 0 var(--r) var(--r) !important;
}

.stDataFrame { border-radius:var(--r) !important; border:1px solid var(--border) !important; }
.stAlert { background:var(--bg2) !important; border-radius:var(--r) !important; }
[data-testid="stFileUploader"] {
  background:var(--bg2) !important;
  border:1px dashed var(--border2) !important;
  border-radius:var(--r) !important;
}
hr { border-color:var(--border) !important; margin:1.25rem 0 !important; }

/* ── CUSTOM COMPONENTS ── */

.z-logo {
  font-family:'JetBrains Mono',monospace;
  font-size:1.9rem; font-weight:700;
  color:var(--acc); letter-spacing:-.06em; line-height:1;
}
.z-logo .dash { color:var(--t3); }

.page-header {
  display:flex; align-items:center; gap:.75rem; margin-bottom:1.5rem;
}
.page-icon {
  font-size:1.8rem;
  background:var(--bg2); border:1px solid var(--border2);
  border-radius:var(--r); width:52px; height:52px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.page-title-text h2 { font-size:1.35rem; font-weight:700; margin:0; color:var(--t1); }
.page-title-text p  { font-size:.82rem; color:var(--t3); margin:0; }

.card {
  background:var(--bg2); border:1px solid var(--border2);
  border-radius:var(--r2); padding:1.2rem 1.4rem;
  margin-bottom:.85rem; transition:border-color .2s,transform .15s;
}
.card:hover { border-color:var(--acc); transform:translateY(-1px); }

.badge {
  display:inline-flex; align-items:center; gap:4px;
  padding:.18rem .6rem; border-radius:999px;
  font-size:.7rem; font-weight:700;
  letter-spacing:.04em; text-transform:uppercase;
}
.b-new      { background:rgba(59,130,246,.15); color:#60a5fa; border:1px solid rgba(59,130,246,.25); }
.b-design   { background:rgba(168,85,247,.15);  color:#c084fc; border:1px solid rgba(168,85,247,.25); }
.b-purchase { background:rgba(232,160,32,.15);  color:#fbbf24; border:1px solid rgba(232,160,32,.25); }
.b-ready    { background:rgba(34,197,94,.15);   color:#4ade80; border:1px solid rgba(34,197,94,.25); }
.b-printing { background:rgba(255,107,53,.15);  color:#fb923c; border:1px solid rgba(255,107,53,.25); }
.b-done     { background:rgba(34,197,94,.1);    color:#16a34a; border:1px solid rgba(34,197,94,.2); }
.b-agent-buy { background:rgba(34,197,94,.12);  color:#22c55e; border:1px solid rgba(34,197,94,.2); }
.b-agent-pot { background:rgba(59,130,246,.12); color:#3b82f6; border:1px solid rgba(59,130,246,.2); }
.b-agent-no  { background:rgba(239,68,68,.12);  color:#ef4444; border:1px solid rgba(239,68,68,.2); }

.guide-box {
  background:var(--bg3); border-right:3px solid var(--acc);
  border-radius:0 var(--r) var(--r) 0; padding:1rem 1.25rem;
  margin-bottom:1.25rem; font-size:.86rem; color:var(--t2); line-height:1.8;
}

.footer {
  position:fixed; bottom:0; left:0; right:0;
  background:var(--bg1); border-top:1px solid var(--border);
  padding:.5rem 1.5rem;
  display:flex; align-items:center; justify-content:space-between;
  font-size:.72rem; color:var(--t3); z-index:999;
}
.footer .brand { color:var(--acc); font-weight:600; }

.user-chip {
  display:flex; align-items:center; gap:.6rem;
  background:var(--bg3); border:1px solid var(--border2);
  border-radius:999px; padding:.4rem .9rem .4rem .5rem; margin-bottom:1rem;
}
.user-avatar {
  width:32px; height:32px;
  background:linear-gradient(135deg,var(--acc),var(--acc2));
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:.8rem; font-weight:700; color:#07080a; flex-shrink:0;
}

@media(max-width:640px){
  .main .block-container { padding:1rem .75rem 5rem !important; }
  [data-testid="stMetricValue"] { font-size:1.1rem !important; }
  .page-icon { width:40px; height:40px; font-size:1.3rem; }
  .page-title-text h2 { font-size:1.1rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS companies (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        type       TEXT DEFAULT 'print_shop',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name  TEXT NOT NULL,
        email      TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL,
        role       TEXT NOT NULL,
        company_id INTEGER DEFAULT 1,
        is_active  INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number      TEXT UNIQUE NOT NULL,
        customer_name     TEXT NOT NULL,
        description       TEXT NOT NULL,
        quantity          INTEGER NOT NULL,
        price             REAL NOT NULL,
        company_id        INTEGER DEFAULT 1,
        created_at        TEXT DEFAULT (datetime('now','localtime')),
        created_by_id     INTEGER,
        created_by_name   TEXT,
        status            TEXT DEFAULT 'New',
        design_status     TEXT DEFAULT 'Pending',
        design_link       TEXT DEFAULT '',
        design_file_path  TEXT DEFAULT '',
        design_notes      TEXT DEFAULT '',
        design_updated    TEXT DEFAULT '',
        design_by         TEXT DEFAULT '',
        purchase_status   TEXT DEFAULT 'Pending',
        purchase_notes    TEXT DEFAULT '',
        purchase_updated  TEXT DEFAULT '',
        production_status TEXT DEFAULT 'Pending',
        production_notes  TEXT DEFAULT '',
        production_updated TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS agent_visits (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id      INTEGER,
        agent_name    TEXT,
        customer_name TEXT NOT NULL,
        location_text TEXT DEFAULT '',
        lat           REAL DEFAULT 0,
        lng           REAL DEFAULT 0,
        status        TEXT DEFAULT 'potential',
        notes         TEXT DEFAULT '',
        image_path    TEXT DEFAULT '',
        visited_at    TEXT DEFAULT (datetime('now','localtime'))
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

    try:
        c.execute("INSERT OR IGNORE INTO companies (id,name) VALUES (1,'Z-Order Print Shop')")
    except Exception:
        pass

    try:
        c.execute("""INSERT INTO users (full_name,email,password,role,company_id)
                     VALUES (?,?,?,?,?)""",
                  ("المدير العام", "admin@zorder.iq", hash_pw("Admin@2025"), "admin", 1))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()


def db_fetchall(query, params=()):
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_fetchone(query, params=()):
    conn = get_conn()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None


def db_execute(query, params=()):
    conn = get_conn()
    cur = conn.execute(query, params)
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return lid


def gen_order_no():
    row = db_fetchone("SELECT COUNT(*) c FROM orders")
    count = row["c"] if row else 0
    today = datetime.date.today().strftime("%y%m%d")
    return f"ZO-{today}-{count+1:04d}"


def update_order_status(order_id):
    o = db_fetchone("SELECT design_status,purchase_status,production_status FROM orders WHERE id=?", (order_id,))
    if not o:
        return
    ds, ps, prs = o["design_status"], o["purchase_status"], o["production_status"]
    if   prs == "Done":                    s = "Completed"
    elif prs == "Printing":               s = "In Production"
    elif ds == "Done" and ps == "Ready":  s = "Ready for Production"
    elif ds == "Done":                    s = "Design Done"
    elif ps == "Ready":                   s = "Materials Ready"
    else:                                 s = "New"
    db_execute("UPDATE orders SET status=? WHERE id=?", (s, order_id))


# ══════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════

STATUS_MAP = {
    "New":                  ("b-new",      "🔵 جديد"),
    "Design Done":          ("b-design",   "🟣 تصميم جاهز"),
    "Materials Ready":      ("b-purchase", "🟡 مواد جاهزة"),
    "Ready for Production": ("b-ready",    "🟢 جاهز للإنتاج"),
    "In Production":        ("b-printing", "🟠 تحت الطباعة"),
    "Completed":            ("b-done",     "✅ مكتمل"),
}
AGENT_STATUS_MAP = {
    "bought":    ("b-agent-buy", "✅ اشترى"),
    "potential": ("b-agent-pot", "🔵 محتمل"),
    "no":        ("b-agent-no",  "❌ لن يشتري"),
}
SEV_MAP = {
    "low":    ("b-ready",    "🟢 منخفض"),
    "medium": ("b-purchase", "🟡 متوسط"),
    "high":   ("b-printing", "🔴 عالي"),
}


def badge(key, maps=None):
    if maps is None:
        maps = STATUS_MAP
    cls, label = maps.get(key, ("b-new", key))
    return f'<span class="badge {cls}">{label}</span>'


def page_header(icon, title, sub=""):
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-icon">{icon}</div>'
        f'<div class="page-title-text"><h2>{title}</h2><p>{sub}</p></div>'
        f'</div>', unsafe_allow_html=True)


GUIDES = {
    "sales": """
📌 <b>مهامك كقسم مبيعات:</b><br>
① إضافة أوردر جديد بكل تفاصيله (العميل، الوصف، الكمية، السعر)<br>
② متابعة حالة أوردراتك في الجدول<br>
③ الاطلاع على التقارير المالية<br>
⚠️ السعر والتقارير المالية سرية ولا تظهر لباقي الأقسام
    """,
    "design": """
📌 <b>مهامك كقسم تصميم:</b><br>
① مراجعة الأوردرات الجديدة الواردة من المبيعات<br>
② رفع ملف التصميم أو إضافة رابطه<br>
③ تغيير حالة التصميم إلى (Done) بعد الانتهاء<br>
④ الإنتاج لن يبدأ إلا بعد إتمام التصميم والمشتريات معاً
    """,
    "purchase": """
📌 <b>مهامك كقسم مشتريات:</b><br>
① مراجعة الأوردرات وتحديد المواد المطلوبة<br>
② تأكيد توفر المواد بالضغط على (Materials Ready)<br>
③ الإنتاج يبدأ فقط بعد تأكيد التصميم + المشتريات
    """,
    "production": """
📌 <b>مهامك كقسم إنتاج:</b><br>
① انتظر الأوردرات التي اكتملت فيها التصميم والمشتريات<br>
② حمّل ملف التصميم قبل الطباعة<br>
③ ابدأ الطباعة وعند الانتهاء غيّر الحالة إلى (Done)
    """,
    "agent": """
📌 <b>مهامك كمندوب مبيعات:</b><br>
① سجّل زيارة كل عميل مع صورة المحل وموقعه<br>
② حدّد حالة العميل: اشترى / محتمل / لن يشتري<br>
③ المدير يتابع أداءك من لوحة التحكم
    """,
    "admin": """
📌 <b>صلاحيات المدير العام:</b><br>
① الاطلاع على إحصائيات النظام بالكامل<br>
② إدارة المستخدمين وإضافة موظفين جدد<br>
③ مراجعة بلاغات الأعطال من جميع الأقسام<br>
④ الاطلاع على تقارير المندوبين والتقارير المالية
    """,
}


def guide_box(role_key):
    text = GUIDES.get(role_key, "")
    if text:
        with st.expander("💡 كيف يعمل هذا القسم؟", expanded=False):
            st.markdown(f'<div class="guide-box">{text}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        f'<div class="footer">'
        f'<span>🖨️ <span class="brand">{APP_NAME}</span> v{APP_VER}</span>'
        f'<span>Developed by <span class="brand">{DEVELOPER}</span></span>'
        f'<span style="color:var(--t3)">© {datetime.date.today().year}</span>'
        f'</div>', unsafe_allow_html=True)


def save_upload(uploaded_file, subfolder="designs") -> str:
    if not uploaded_file:
        return ""
    d = UPLOAD_DIR / subfolder
    d.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._-")
    path = d / f"{ts}_{safe}"
    path.write_bytes(uploaded_file.read())
    return str(path)


def download_btn(file_path: str, label="⬇️ تحميل الملف"):
    p = Path(file_path)
    if p.exists():
        st.download_button(label, p.read_bytes(), file_name=p.name, use_container_width=True)
    else:
        st.caption("⚠️ الملف غير موجود")


def show_orders_table(role, filter_by_user_id=None):
    hide_price = role not in ("admin", "sales")
    query = "SELECT * FROM orders"
    params = []
    if filter_by_user_id:
        query += " WHERE created_by_id=?"
        params.append(filter_by_user_id)
    query += " ORDER BY id DESC"
    rows = db_fetchall(query, params)
    if not rows:
        st.info("لا توجد أوردرات بعد.")
        return
    statuses = ["الكل"] + list({r["status"] for r in rows})
    sel = st.selectbox("📌 فلتر الحالة", statuses, key=f"f_{role}_{filter_by_user_id}")
    if sel != "الكل":
        rows = [r for r in rows if r["status"] == sel]
    cols = ["order_number","customer_name","description","quantity","status",
            "design_status","purchase_status","production_status","created_at"]
    if not hide_price:
        cols.insert(4, "price")
    labels = {
        "order_number":"رقم الأوردر","customer_name":"العميل","description":"الوصف",
        "quantity":"الكمية","price":"السعر","status":"الحالة",
        "design_status":"التصميم","purchase_status":"المشتريات",
        "production_status":"الإنتاج","created_at":"التاريخ",
    }
    df = pd.DataFrame(rows)
    existing = [c for c in cols if c in df.columns]
    st.dataframe(df[existing].rename(columns=labels), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════

def page_login():
    st.markdown('<div style="max-width:460px;margin:3rem auto;">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="text-align:center;margin-bottom:2rem">'
        f'<div class="z-logo">Z<span class="dash">-</span>Order</div>'
        f'<div style="color:var(--t3);font-size:.85rem;margin-top:.4rem">Print Workflow Platform</div>'
        f'</div>', unsafe_allow_html=True)

    tab_in, tab_up = st.tabs(["🔑  تسجيل الدخول", "📝  إنشاء حساب"])

    with tab_in:
        email = st.text_input("📧 الإيميل", placeholder="you@company.com", key="li_email")
        pw    = st.text_input("🔒 كلمة المرور", type="password", key="li_pw")
        if st.button("دخول →", key="li_btn"):
            user = db_fetchone(
                "SELECT * FROM users WHERE email=? AND password=? AND is_active=1",
                (email.strip().lower(), hash_pw(pw))
            )
            if user:
                st.session_state.update({
                    "uid": user["id"], "uname": user["full_name"],
                    "email": user["email"], "role": user["role"],
                    "company_id": user["company_id"],
                })
                st.rerun()
            else:
                st.error("❌ بيانات غير صحيحة أو الحساب غير نشط.")

    with tab_up:
        name    = st.text_input("👤 الاسم الكامل", key="su_name")
        su_em   = st.text_input("📧 الإيميل", key="su_email")
        su_role = st.selectbox("🏢 القسم الوظيفي",
                                ["sales","design","purchase","production","agent"],
                                format_func=lambda r: f"{ROLES[r]['icon']} {ROLES[r]['label']}",
                                key="su_role")
        su_pw  = st.text_input("🔒 كلمة المرور", type="password", key="su_pw")
        su_pw2 = st.text_input("🔒 تأكيد كلمة المرور", type="password", key="su_pw2")
        if st.button("إنشاء الحساب →", key="su_btn"):
            if not all([name, su_em, su_pw]):
                st.error("يرجى تعبئة جميع الحقول.")
            elif su_pw != su_pw2:
                st.error("كلمتا المرور غير متطابقتين.")
            elif len(su_pw) < 6:
                st.error("كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
            else:
                try:
                    db_execute(
                        "INSERT INTO users(full_name,email,password,role) VALUES(?,?,?,?)",
                        (name.strip(), su_em.strip().lower(), hash_pw(su_pw), su_role)
                    )
                    st.success("✅ تم إنشاء الحساب! سجّل دخولك الآن.")
                except sqlite3.IntegrityError:
                    st.error("❌ هذا الإيميل مسجل بالفعل.")

    st.markdown(
        f'<div style="text-align:center;margin-top:2rem;color:var(--t3);font-size:.72rem">'
        f'Developed by <b style="color:var(--acc)">{DEVELOPER}</b>'
        f'&nbsp;|&nbsp;{APP_NAME} v{APP_VER}'
        f'</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════

PAGES_BY_ROLE = {
    "admin":      ["📊 لوحة المدير",      "📋 كل الأوردرات",    "💰 التقارير المالية",
                   "🗺️ تقارير المندوبين",  "🚨 بلاغات الأعطال",  "👥 إدارة المستخدمين"],
    "sales":      ["📊 لوحتي",            "➕ أوردر جديد",      "📋 أوردراتي",
                   "💰 التقارير المالية",  "🚨 بلاغ خلل"],
    "design":     ["📊 لوحتي",            "🎨 مهام التصميم",    "📋 كل الأوردرات",    "🚨 بلاغ خلل"],
    "purchase":   ["📊 لوحتي",            "📦 المواد",          "📋 كل الأوردرات",    "🚨 بلاغ خلل"],
    "production": ["📊 لوحتي",            "🖨️ الإنتاج",        "📋 كل الأوردرات",    "🚨 بلاغ خلل"],
    "agent":      ["📊 لوحتي",            "🗺️ تسجيل زيارة",    "📋 زياراتي",         "🚨 بلاغ خلل"],
}


def sidebar():
    role  = st.session_state["role"]
    uname = st.session_state["uname"]
    rinfo = ROLES.get(role, {"label": role, "icon": "👤"})
    initials = "".join(w[0] for w in uname.split()[:2]).upper() or "U"

    st.sidebar.markdown(
        f'<div style="padding:.5rem 0 .25rem">'
        f'<div class="z-logo">Z<span class="dash">-</span>Order</div>'
        f'<div style="color:var(--t3);font-size:.72rem">Print Workflow Platform</div>'
        f'</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f'<div class="user-chip">'
        f'<div class="user-avatar">{initials}</div>'
        f'<div><div style="font-size:.82rem;font-weight:600">{uname}</div>'
        f'<div style="font-size:.68rem;color:var(--acc)">{rinfo["icon"]} {rinfo["label"]}</div></div>'
        f'</div>', unsafe_allow_html=True)

    pages = PAGES_BY_ROLE.get(role, [])
    page  = st.sidebar.radio("", pages, label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f'<div style="font-size:.68rem;color:var(--t3);text-align:center;line-height:1.8">'
        f'Developed by<br><b style="color:var(--acc)">{DEVELOPER}</b>'
        f'</div>', unsafe_allow_html=True)

    if st.sidebar.button("🚪 تسجيل الخروج"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    return page


# ══════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════

def page_dashboard():
    role = st.session_state["role"]
    page_header("📊", "لوحة التحكم", "نظرة عامة على الأوردرات")
    guide_box(role)

    total  = (db_fetchone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    new_   = (db_fetchone("SELECT COUNT(*) c FROM orders WHERE status='New'") or {}).get("c", 0)
    inprod = (db_fetchone("SELECT COUNT(*) c FROM orders WHERE production_status='Printing'") or {}).get("c", 0)
    done   = (db_fetchone("SELECT COUNT(*) c FROM orders WHERE production_status='Done'") or {}).get("c", 0)

    if role in ("admin", "sales"):
        rev    = (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE production_status='Done'") or {}).get("s", 0)
        total_v= (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders") or {}).get("s", 0)
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("إجمالي", total)
        c2.metric("جديدة",  new_)
        c3.metric("طباعة",  inprod)
        c4.metric("مكتملة", done)
        c5.metric("إيراد (د.ع)",  f"{rev:,.0f}")
        c6.metric("إجمالي القيمة", f"{total_v:,.0f}")
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("إجمالي", total)
        c2.metric("جديدة",  new_)
        c3.metric("طباعة",  inprod)
        c4.metric("مكتملة", done)

    st.markdown("---")
    st.markdown("**آخر ١٠ أوردرات**")
    rows = db_fetchall(
        "SELECT order_number,customer_name,description,quantity,status,created_at "
        "FROM orders ORDER BY id DESC LIMIT 10"
    )
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "order_number":"رقم الأوردر","customer_name":"العميل",
            "description":"الوصف","quantity":"الكمية",
            "status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


def page_admin_dashboard():
    page_header("🛡️", "لوحة المدير العام", "إحصائيات حية وإدارة شاملة")
    guide_box("admin")

    today    = datetime.date.today().isoformat()
    total    = (db_fetchone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    today_o  = (db_fetchone("SELECT COUNT(*) c FROM orders WHERE created_at LIKE ?", (f"{today}%",)) or {}).get("c", 0)
    done     = (db_fetchone("SELECT COUNT(*) c FROM orders WHERE production_status='Done'") or {}).get("c", 0)
    rev      = (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE production_status='Done'") or {}).get("s", 0)
    total_v  = (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders") or {}).get("s", 0)
    open_r   = (db_fetchone("SELECT COUNT(*) c FROM incident_reports WHERE status='open'") or {}).get("c", 0)
    agents   = (db_fetchone("SELECT COUNT(DISTINCT agent_id) c FROM agent_visits WHERE visited_at LIKE ?", (f"{today}%",)) or {}).get("c", 0)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("أوردرات اليوم",       today_o)
    c2.metric(f"مكتملة / إجمالي",   f"{done}/{total}")
    c3.metric("إيراد المكتمل (د.ع)", f"{rev:,.0f}")
    c4.metric("بلاغات مفتوحة",       open_r)

    c5,c6 = st.columns(2)
    c5.metric("إجمالي قيمة الأوردرات", f"{total_v:,.0f} د.ع")
    c6.metric("مندوبون نشطون اليوم",   agents)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 الأوردرات الحديثة", "🗺️ أداء المندوبين", "🚨 آخر البلاغات"])

    with tab1:
        rows = db_fetchall("SELECT order_number,customer_name,quantity,status,created_at FROM orders ORDER BY id DESC LIMIT 15")
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "order_number":"رقم الأوردر","customer_name":"العميل",
                "quantity":"الكمية","status":"الحالة","created_at":"التاريخ"
            }), use_container_width=True, hide_index=True)

    with tab2:
        rows = db_fetchall("""
            SELECT agent_name,COUNT(*) visits,
                   SUM(CASE WHEN status='bought'    THEN 1 ELSE 0 END) bought,
                   SUM(CASE WHEN status='potential' THEN 1 ELSE 0 END) potential,
                   SUM(CASE WHEN status='no'        THEN 1 ELSE 0 END) lost
            FROM agent_visits GROUP BY agent_id ORDER BY visits DESC
        """)
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "agent_name":"المندوب","visits":"الزيارات",
                "bought":"اشترى","potential":"محتمل","lost":"لن يشتري"
            }), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد زيارات بعد.")

    with tab3:
        rows = db_fetchall("SELECT reporter_name,department,description,severity,status,created_at FROM incident_reports ORDER BY id DESC LIMIT 10")
        if rows:
            st.dataframe(pd.DataFrame(rows).rename(columns={
                "reporter_name":"المبلّغ","department":"القسم",
                "description":"الوصف","severity":"الخطورة",
                "status":"الحالة","created_at":"التاريخ"
            }), use_container_width=True, hide_index=True)
        else:
            st.success("🎉 لا توجد بلاغات مفتوحة!")


def page_add_order():
    page_header("➕", "إضافة أوردر جديد", "أدخل تفاصيل طلب العميل")
    guide_box("sales")
    with st.form("add_order", clear_on_submit=True):
        c1, c2 = st.columns(2)
        customer    = c1.text_input("👤 اسم العميل *")
        quantity    = c2.number_input("📦 الكمية *", min_value=1, value=1)
        description = st.text_area("📝 وصف الطلب *", placeholder="تفاصيل الطباعة، المقاس، الورق...")
        c3, _ = st.columns(2)
        price  = c3.number_input("💰 السعر (د.ع) *", min_value=0.0, step=500.0)
        sub    = st.form_submit_button("✅ حفظ الأوردر")
    if sub:
        if not customer or not description or price <= 0:
            st.error("يرجى تعبئة جميع الحقول.")
        else:
            ono = gen_order_no()
            db_execute(
                """INSERT INTO orders(order_number,customer_name,description,quantity,price,
                   created_by_id,created_by_name) VALUES(?,?,?,?,?,?,?)""",
                (ono, customer.strip(), description.strip(), quantity, price,
                 st.session_state["uid"], st.session_state["uname"])
            )
            st.success(f"✅ تم إضافة الأوردر **{ono}** بنجاح!")


def page_design_tasks():
    page_header("🎨", "مهام التصميم", "رفع التصاميم وتحديث الحالة")
    guide_box("design")

    rows    = db_fetchall("SELECT * FROM orders ORDER BY id DESC")
    pending = [r for r in rows if r["design_status"] == "Pending"]
    done    = [r for r in rows if r["design_status"] == "Done"]

    tab1, tab2 = st.tabs([f"⏳ قيد الانتظار ({len(pending)})", f"✅ مكتملة ({len(done)})"])

    with tab1:
        if not pending:
            st.success("🎉 لا توجد مهام تصميم معلقة!")
        for r in pending:
            with st.expander(f"🔷 {r['order_number']} — {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**التاريخ:** {r['created_at']}")
                c2.markdown(f"**بواسطة:** {r['created_by_name']}")
                st.markdown("---")
                dl   = st.text_input("🔗 رابط التصميم", value=r["design_link"] or "", key=f"dl_{r['id']}")
                upld = st.file_uploader("📎 رفع ملف التصميم", key=f"du_{r['id']}",
                                         type=["pdf","png","jpg","ai","psd","svg","eps"])
                notes= st.text_area("📝 ملاحظات", value=r["design_notes"] or "", key=f"dn_{r['id']}", height=70)
                if st.button("✅ تحديث → Design Done", key=f"dbtn_{r['id']}"):
                    fp = save_upload(upld, "designs") if upld else (r["design_file_path"] or "")
                    if not dl.strip() and not fp:
                        st.error("يرجى رفع ملف أو إدخال رابط التصميم.")
                    else:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        db_execute("""UPDATE orders SET design_status='Done',design_link=?,
                            design_file_path=?,design_notes=?,design_updated=?,design_by=? WHERE id=?""",
                            (dl.strip(), fp, notes.strip(), now, st.session_state["uname"], r["id"]))
                        update_order_status(r["id"])
                        st.success("✅ تم تحديث التصميم!")
                        st.rerun()

    with tab2:
        if not done:
            st.info("لا توجد تصاميم مكتملة.")
        for r in done:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{badge("Design Done")}'
                f'<br><small style="color:var(--t3)">🔗 {r["design_link"] or "—"}'
                f' &nbsp;|&nbsp; 🗓 {r["design_updated"]}</small></div>',
                unsafe_allow_html=True)
            if r.get("design_file_path"):
                download_btn(r["design_file_path"], "⬇️ تحميل ملف التصميم")


def page_purchase():
    page_header("📦", "متابعة المواد", "تأكيد توفر مواد الأوردرات")
    guide_box("purchase")

    rows    = db_fetchall("SELECT * FROM orders ORDER BY id DESC")
    pending = [r for r in rows if r["purchase_status"] == "Pending"]
    ready   = [r for r in rows if r["purchase_status"] == "Ready"]

    tab1, tab2 = st.tabs([f"⏳ قيد التوفير ({len(pending)})", f"✅ جاهزة ({len(ready)})"])

    with tab1:
        if not pending:
            st.success("🎉 جميع المواد جاهزة!")
        for r in pending:
            with st.expander(f"📦 {r['order_number']} — {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**حالة التصميم:** {r['design_status']}")
                notes = st.text_area("📝 ملاحظات", value=r["purchase_notes"] or "",
                                     key=f"pn_{r['id']}", height=70)
                if st.button("✅ تأكيد توفر المواد", key=f"pbtn_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    db_execute("UPDATE orders SET purchase_status='Ready',purchase_notes=?,purchase_updated=? WHERE id=?",
                               (notes.strip(), now, r["id"]))
                    update_order_status(r["id"])
                    st.success("✅ تم تأكيد المواد!")
                    st.rerun()

    with tab2:
        if not ready:
            st.info("لا توجد مواد جاهزة بعد.")
        for r in ready:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{badge("Materials Ready")}'
                f'<br><small style="color:var(--t3)">🗓 {r["purchase_updated"]}</small></div>',
                unsafe_allow_html=True)


def page_production():
    page_header("🖨️", "الإنتاج والطباعة", "تنفيذ الأوردرات الجاهزة فقط")
    guide_box("production")

    rows      = db_fetchall("SELECT * FROM orders ORDER BY id DESC")
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
        if not available:
            st.info("⏳ لا توجد أوردرات جاهزة. انتظر إتمام التصميم والمواد.")
        for r in available:
            with st.expander(f"🟢 {r['order_number']} — {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c1.markdown(f"**الكمية:** {r['quantity']}")
                c2.markdown(f"**رابط التصميم:** {r['design_link'] or '—'}")
                if r.get("design_file_path"):
                    download_btn(r["design_file_path"], "⬇️ تحميل ملف التصميم")
                notes = st.text_area("📝 ملاحظات", key=f"pron_{r['id']}", height=60)
                col1, col2 = st.columns(2)
                if col1.button("▶️ بدء الطباعة", key=f"start_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    db_execute("UPDATE orders SET production_status='Printing',production_notes=?,production_updated=? WHERE id=?",
                               (notes, now, r["id"]))
                    update_order_status(r["id"])
                    st.success("▶️ بدأت الطباعة!")
                    st.rerun()
                if col2.button("✅ إتمام مباشر", key=f"fin2_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    db_execute("UPDATE orders SET production_status='Done',production_notes=?,production_updated=? WHERE id=?",
                               (notes, now, r["id"]))
                    update_order_status(r["id"])
                    st.success("✅ اكتمل!")
                    st.rerun()

    with tab2:
        if not printing:
            st.info("لا توجد طباعة جارية.")
        for r in printing:
            with st.expander(f"🟠 {r['order_number']} — {r['customer_name']}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**الوصف:** {r['description']}")
                c2.markdown(f"**الكمية:** {r['quantity']}")
                if r.get("design_file_path"):
                    download_btn(r["design_file_path"])
                if st.button("✅ تحديد كـ مكتمل", key=f"fin_{r['id']}"):
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    db_execute("UPDATE orders SET production_status='Done',production_updated=? WHERE id=?", (now, r["id"]))
                    update_order_status(r["id"])
                    st.success("✅ اكتمل!")
                    st.rerun()

    with tab3:
        if not completed:
            st.info("لا توجد أوردرات مكتملة بعد.")
        for r in completed:
            st.markdown(
                f'<div class="card"><b>{r["order_number"]}</b> — {r["customer_name"]}'
                f'&nbsp;{badge("Completed")}'
                f'<br><small style="color:var(--t3)">اكتمل: {r["production_updated"]}</small></div>',
                unsafe_allow_html=True)

    with tab4:
        if not with_file:
            st.info("لا توجد ملفات مرفوعة.")
        for r in with_file:
            c1, c2 = st.columns([3,1])
            c1.markdown(f"**{r['order_number']}** — {r['customer_name']}")
            with c2:
                download_btn(r["design_file_path"], "⬇️")


def page_agent_new_visit():
    page_header("🗺️", "تسجيل زيارة عميل", "سجّل بيانات الزيارة الميدانية")
    guide_box("agent")
    with st.form("agent_visit", clear_on_submit=True):
        customer = st.text_input("👤 اسم العميل / المحل *")
        location = st.text_input("📍 الموقع (العنوان)", placeholder="مثال: شارع المتنبي، بغداد")
        c1, c2  = st.columns(2)
        lat      = c1.number_input("خط العرض (Lat)", value=33.3406, format="%.6f")
        lng      = c2.number_input("خط الطول (Lng)", value=44.4009, format="%.6f")
        vstatus  = st.selectbox("📊 حالة العميل",
                                 ["potential","bought","no"],
                                 format_func=lambda s: {"bought":"✅ اشترى","potential":"🔵 محتمل","no":"❌ لن يشتري"}[s])
        notes    = st.text_area("📝 ملاحظات", height=80)
        image    = st.file_uploader("📸 صورة المحل (اختياري)", type=["jpg","jpeg","png","webp"])
        sub      = st.form_submit_button("✅ حفظ الزيارة")
    if sub:
        if not customer:
            st.error("يرجى إدخال اسم العميل.")
        else:
            ip = save_upload(image, "agent_images") if image else ""
            db_execute("""INSERT INTO agent_visits(agent_id,agent_name,customer_name,
                location_text,lat,lng,status,notes,image_path) VALUES(?,?,?,?,?,?,?,?,?)""",
                (st.session_state["uid"], st.session_state["uname"],
                 customer.strip(), location.strip(), lat, lng, vstatus, notes.strip(), ip))
            st.success(f"✅ تم تسجيل الزيارة للعميل **{customer}**!")


def page_agent_visits():
    page_header("📋", "زياراتي", "سجل زياراتك الميدانية")
    uid  = st.session_state["uid"]
    rows = db_fetchall("SELECT * FROM agent_visits WHERE agent_id=? ORDER BY id DESC", (uid,))
    if not rows:
        st.info("لم تسجّل أي زيارة بعد.")
        return
    for r in rows:
        cls, lbl = AGENT_STATUS_MAP.get(r["status"], ("b-new", r["status"]))
        img_html = ""
        if r.get("image_path") and Path(r["image_path"]).exists():
            img_data = base64.b64encode(Path(r["image_path"]).read_bytes()).decode()
            ext = Path(r["image_path"]).suffix.lstrip(".") or "jpeg"
            img_html = f'<br><img src="data:image/{ext};base64,{img_data}" style="max-width:220px;border-radius:8px;margin-top:.5rem">'
        st.markdown(
            f'<div class="card">'
            f'<b>{r["customer_name"]}</b>&nbsp;<span class="badge {cls}">{lbl}</span>'
            f'<br><small style="color:var(--t2)">📍 {r["location_text"] or "—"}&nbsp;|&nbsp;🗓 {r["visited_at"]}</small>'
            f'{"<br><small>"+r["notes"]+"</small>" if r["notes"] else ""}'
            f'{img_html}</div>', unsafe_allow_html=True)


def page_agent_report():
    page_header("🗺️", "تقارير المندوبين", "إحصائيات الزيارات الميدانية")
    rows = db_fetchall("""
        SELECT agent_name,COUNT(*) visits,
               SUM(CASE WHEN status='bought'    THEN 1 ELSE 0 END) bought,
               SUM(CASE WHEN status='potential' THEN 1 ELSE 0 END) potential,
               SUM(CASE WHEN status='no'        THEN 1 ELSE 0 END) lost,
               MAX(visited_at) last_visit
        FROM agent_visits GROUP BY agent_id ORDER BY visits DESC
    """)
    if not rows:
        st.info("لا توجد زيارات بعد.")
    else:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "agent_name":"المندوب","visits":"الزيارات","bought":"اشترى",
            "potential":"محتمل","lost":"لن يشتري","last_visit":"آخر زيارة"
        }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**كل الزيارات**")
    all_v = db_fetchall("SELECT agent_name,customer_name,location_text,status,notes,visited_at FROM agent_visits ORDER BY id DESC")
    if all_v:
        st.dataframe(pd.DataFrame(all_v).rename(columns={
            "agent_name":"المندوب","customer_name":"العميل","location_text":"الموقع",
            "status":"الحالة","notes":"ملاحظات","visited_at":"التاريخ"
        }), use_container_width=True, hide_index=True)


def page_submit_incident():
    role = st.session_state["role"]
    page_header("🚨", "بلاغ خلل أو نقص", "أبلغ عن أي عطل أو نقص في القسم")
    with st.form("incident", clear_on_submit=True):
        desc = st.text_area("📝 وصف المشكلة *",
                             placeholder="مثال: نقص حبر الطباعة، عطل في الطابعة رقم 2، نقص ورق A4...")
        sev  = st.selectbox("⚠️ درجة الخطورة",
                             ["low","medium","high"],
                             format_func=lambda s: {"low":"🟢 منخفض","medium":"🟡 متوسط","high":"🔴 عالي"}[s])
        sub  = st.form_submit_button("📤 إرسال البلاغ")
    if sub:
        if not desc.strip():
            st.error("يرجى كتابة وصف المشكلة.")
        else:
            db_execute("""INSERT INTO incident_reports(reporter_id,reporter_name,department,description,severity)
                VALUES(?,?,?,?,?)""",
                (st.session_state["uid"], st.session_state["uname"],
                 ROLES[role]["label"], desc.strip(), sev))
            st.success("✅ تم إرسال البلاغ! سيراجعه المدير قريباً.")

    st.markdown("---")
    st.markdown("**بلاغاتك السابقة**")
    rows = db_fetchall(
        "SELECT description,severity,status,created_at FROM incident_reports "
        "WHERE reporter_id=? ORDER BY id DESC LIMIT 10",
        (st.session_state["uid"],)
    )
    if rows:
        st.dataframe(pd.DataFrame(rows).rename(columns={
            "description":"الوصف","severity":"الخطورة","status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بلاغات سابقة.")


def page_all_incidents():
    page_header("🚨", "بلاغات الأعطال", "جميع البلاغات الواردة")
    rows = db_fetchall("SELECT * FROM incident_reports ORDER BY id DESC")
    if not rows:
        st.success("🎉 لا توجد بلاغات مفتوحة!")
        return

    open_r    = [r for r in rows if r["status"] == "open"]
    resolved  = [r for r in rows if r["status"] == "resolved"]
    tab1, tab2 = st.tabs([f"🔴 مفتوحة ({len(open_r)})", f"✅ محلولة ({len(resolved)})"])

    for tab, flist in [(tab1, open_r), (tab2, resolved)]:
        with tab:
            if not flist:
                st.info("لا توجد بلاغات في هذه الفئة.")
            for r in flist:
                sev_cls, sev_lbl = SEV_MAP.get(r["severity"], ("b-new", r["severity"]))
                with st.expander(f"{sev_lbl} — {r['department']} — {r['created_at'][:16]}"):
                    st.markdown(f"**المبلّغ:** {r['reporter_name']}")
                    st.markdown(f"**الوصف:** {r['description']}")
                    if r["status"] == "open":
                        if st.button("✅ تحديد كـ محلول", key=f"res_{r['id']}"):
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            db_execute("UPDATE incident_reports SET status='resolved',resolved_at=? WHERE id=?",
                                       (now, r["id"]))
                            st.success("تم تحديث البلاغ.")
                            st.rerun()


def page_financial():
    page_header("💰", "التقارير المالية", "ملخص مالي — للمبيعات والمدير فقط")
    total_v = (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders") or {}).get("s", 0)
    rev     = (db_fetchone("SELECT COALESCE(SUM(price),0) s FROM orders WHERE production_status='Done'") or {}).get("s", 0)
    count   = (db_fetchone("SELECT COUNT(*) c FROM orders") or {}).get("c", 0)
    avg     = (total_v / count) if count else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي قيمة الأوردرات", f"{total_v:,.0f} د.ع")
    c2.metric("إيرادات المكتملة",       f"{rev:,.0f} د.ع")
    c3.metric("قيد التنفيذ",            f"{total_v-rev:,.0f} د.ع")
    c4.metric("متوسط قيمة الأوردر",     f"{avg:,.0f} د.ع")

    st.markdown("---")
    rows = db_fetchall("SELECT order_number,customer_name,quantity,price,status,created_at FROM orders ORDER BY id DESC")
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df.rename(columns={
            "order_number":"رقم الأوردر","customer_name":"العميل",
            "quantity":"الكمية","price":"السعر (د.ع)",
            "status":"الحالة","created_at":"التاريخ"
        }), use_container_width=True, hide_index=True)

        header_txt = (
            f"Z-Order — تقرير مالي\n"
            f"Developed by: {DEVELOPER}\n"
            f"تاريخ الاستخراج: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        )
        csv = (header_txt + df.to_csv(index=False)).encode("utf-8-sig")
        st.download_button("⬇️ تصدير CSV", csv,
                           file_name=f"z_order_report_{datetime.date.today()}.csv",
                           mime="text/csv", use_container_width=True)


def page_user_management():
    page_header("👥", "إدارة المستخدمين", "عرض الحسابات وإضافة موظفين جدد")
    rows = db_fetchall("SELECT id,full_name,email,role,is_active,created_at FROM users ORDER BY id")
    st.dataframe(pd.DataFrame(rows).rename(columns={
        "id":"#","full_name":"الاسم","email":"الإيميل",
        "role":"الدور","is_active":"نشط","created_at":"تاريخ الإنشاء"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**➕ إضافة مستخدم جديد**")
    with st.form("add_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name  = c1.text_input("الاسم الكامل")
        email = c2.text_input("الإيميل")
        c3, c4 = st.columns(2)
        role  = c3.selectbox("الدور", list(ROLES.keys()),
                              format_func=lambda r: f"{ROLES[r]['icon']} {ROLES[r]['label']}")
        pw    = c4.text_input("كلمة المرور", type="password")
        sub   = st.form_submit_button("إضافة")
    if sub:
        if not all([name, email, pw]):
            st.error("يرجى تعبئة جميع الحقول.")
        else:
            try:
                db_execute("INSERT INTO users(full_name,email,password,role) VALUES(?,?,?,?)",
                           (name.strip(), email.strip().lower(), hash_pw(pw), role))
                st.success(f"✅ تم إضافة '{name}'.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ الإيميل مستخدم بالفعل.")

    st.markdown("---")
    st.markdown("**🔄 تعطيل / تفعيل مستخدم**")
    uid_t = st.number_input("رقم المستخدم (ID)", min_value=2, value=2, step=1)
    col1, col2 = st.columns(2)
    if col1.button("✅ تفعيل"):
        db_execute("UPDATE users SET is_active=1 WHERE id=?", (uid_t,))
        st.success("تم التفعيل.")
        st.rerun()
    if col2.button("🚫 تعطيل"):
        db_execute("UPDATE users SET is_active=0 WHERE id=?", (uid_t,))
        st.warning("تم التعطيل.")
        st.rerun()


# ══════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════

def main():
    init_db()

    if "role" not in st.session_state:
        page_login()
        return

    role = st.session_state["role"]
    page = sidebar()

    if page in ("📊 لوحتي",):
        if role == "admin":
            page_admin_dashboard()
        else:
            page_dashboard()

    elif page == "📊 لوحة المدير":
        page_admin_dashboard()

    elif page == "➕ أوردر جديد":
        page_add_order()

    elif page == "📋 أوردراتي":
        page_header("📋", "أوردراتي", "")
        guide_box("sales")
        show_orders_table(role, filter_by_user_id=st.session_state["uid"])

    elif page == "📋 كل الأوردرات":
        page_header("📋", "جميع الأوردرات", "")
        show_orders_table(role)

    elif page == "🎨 مهام التصميم":
        page_design_tasks()

    elif page == "📦 المواد":
        page_purchase()

    elif page == "🖨️ الإنتاج":
        page_production()

    elif page == "🗺️ تسجيل زيارة":
        page_agent_new_visit()

    elif page == "📋 زياراتي":
        page_agent_visits()

    elif page == "🗺️ تقارير المندوبين":
        page_agent_report()

    elif page == "🚨 بلاغ خلل":
        page_submit_incident()

    elif page == "🚨 بلاغات الأعطال":
        page_all_incidents()

    elif page == "💰 التقارير المالية":
        if role in ("admin", "sales"):
            page_financial()
        else:
            st.error("🚫 ليس لديك صلاحية الوصول.")

    elif page == "👥 إدارة المستخدمين":
        if role == "admin":
            page_user_management()
        else:
            st.error("🚫 ليس لديك صلاحية الوصول.")

    footer()


if __name__ == "__main__":
    main()