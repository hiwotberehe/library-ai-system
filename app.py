import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import date, timedelta, datetime
import random, string, json, os, warnings
warnings.filterwarnings("ignore")

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="📚 Library AI System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

.main { background: #0f1117; }
section[data-testid="stSidebar"] { background: #1a1d2e !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white !important; border: none;
    border-radius: 8px; padding: 8px 20px;
    font-weight: 500; transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(99,102,241,0.4); }

.card {
    background: #1e2130; border: 1px solid #2d3148;
    border-radius: 12px; padding: 18px; margin: 8px 0;
}
.metric-card {
    background: linear-gradient(135deg, #1e2130, #252840);
    border: 1px solid #3d4168; border-radius: 12px;
    padding: 20px; text-align: center;
}
.metric-num { font-size: 2rem; font-weight: 600; color: #6366f1; }
.metric-lbl { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

.book-card {
    background: #1e2130; border: 1px solid #2d3148;
    border-radius: 10px; padding: 16px; height: 100%;
    transition: border-color 0.2s;
}
.book-card:hover { border-color: #6366f1; }
.book-title { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
.book-author { color: #94a3b8; font-size: 0.82rem; }
.genre-badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.75rem;
    background: rgba(99,102,241,0.15); color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3);
}
.risk-high   { color: #f87171; font-weight: 600; }
.risk-medium { color: #fbbf24; font-weight: 600; }
.risk-low    { color: #4ade80; font-weight: 600; }
.train-card {
    background: #1e2130; border: 1px solid #2d3148;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.chat-user { background: #3730a3; border-radius: 12px 12px 4px 12px; padding: 10px 14px; margin: 6px 0; color: white; }
.chat-bot  { background: #1e2130; border: 1px solid #2d3148; border-radius: 12px 12px 12px 4px; padding: 10px 14px; margin: 6px 0; color: #e2e8f0; }
.section-header { color: #6366f1 !important; font-family: 'Playfair Display', serif !important; margin-bottom: 0.5rem; }

div[data-testid="stMetric"] { background: #1e2130; border: 1px solid #2d3148; border-radius: 10px; padding: 12px 16px; }
div[data-testid="stMetric"] label { color: #94a3b8 !important; }
div[data-testid="stMetric"] div { color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SESSION STATE — acts as our in-memory database
# ════════════════════════════════════════════════════════════
GENRES = ["Fiction","Science","History","Technology","Biography",
          "Mystery","Fantasy","Self-Help","Philosophy","Children"]
COVER_COLORS = ["#6366f1","#ec4899","#14b8a6","#f59e0b","#10b981",
                "#ef4444","#8b5cf6","#0ea5e9","#f97316","#06b6d4"]
STATIONS = ["Central","North Hub","East Park","West Gate","South Bay",
            "Airport","University","City Hall","Harbor","Market Square"]
WEATHERS = ["Clear","Rainy","Foggy","Stormy"]

def init_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized  = True
        st.session_state.current_user = None
        st.session_state.users        = _seed_users()
        st.session_state.books        = _seed_books()
        st.session_state.loans        = []
        st.session_state.train_trips  = _seed_trains()
        st.session_state.train_bookings = []
        st.session_state.chat_history = []
        st.session_state.page         = "🏠 Home"
        st.session_state.next_loan_id = 1
        st.session_state.next_booking_id = 1

def _seed_users():
    return [
        {"id":1,"name":"Admin User","email":"admin@library.com","password":"admin123",
         "role":"admin","age":35,"fav_genre":"Technology","total_borrowed":0},
        {"id":2,"name":"Ahmed Mohammed","email":"ahmed@email.com","password":"pass123",
         "role":"member","age":24,"fav_genre":"Fiction","total_borrowed":3},
        {"id":3,"name":"Sara Hassan","email":"sara@email.com","password":"pass123",
         "role":"member","age":30,"fav_genre":"Science","total_borrowed":7},
    ]

def _seed_books():
    books = [
        ("The Great Gatsby","F. Scott Fitzgerald","Fiction",1925,"A story of wealth and obsession in 1920s America",4.2,45),
        ("A Brief History of Time","Stephen Hawking","Science",1988,"Cosmology and the nature of time explained for everyone",4.8,88),
        ("Sapiens","Yuval Noah Harari","History",2011,"A brief history of humankind from the Stone Age",4.7,120),
        ("Clean Code","Robert C. Martin","Technology",2008,"Best practices for writing maintainable software",4.6,95),
        ("Steve Jobs","Walter Isaacson","Biography",2011,"The life of Apple's visionary co-founder",4.4,67),
        ("The Da Vinci Code","Dan Brown","Mystery",2003,"A symbologist uncovers a religious conspiracy",4.0,110),
        ("Harry Potter","J.K. Rowling","Fantasy",1997,"A boy discovers he is a wizard",4.9,200),
        ("Atomic Habits","James Clear","Self-Help",2018,"Tiny changes that lead to remarkable results",4.8,155),
        ("Meditations","Marcus Aurelius","Philosophy",170,"Reflections by the Roman emperor on Stoic philosophy",4.7,60),
        ("The Lion Witch Wardrobe","C.S. Lewis","Children",1950,"Four children discover a magical world through a wardrobe",4.6,80),
        ("1984","George Orwell","Fiction",1949,"A dystopian vision of a totalitarian surveillance state",4.8,140),
        ("The Selfish Gene","Richard Dawkins","Science",1976,"Evolution from the gene-centered perspective",4.5,55),
        ("Guns Germs Steel","Jared Diamond","History",1997,"Why some civilizations came to dominate others",4.3,72),
        ("The Pragmatic Programmer","David Thomas","Technology",1999,"From journeyman to master software craftsman",4.7,88),
        ("Elon Musk","Ashlee Vance","Biography",2015,"How the worlds most ambitious entrepreneur shapes the future",4.5,99),
        ("Gone Girl","Gillian Flynn","Mystery",2012,"A twisted psychological thriller about a missing wife",4.1,85),
        ("The Hobbit","J.R.R. Tolkien","Fantasy",1937,"A hobbit goes on an unexpected journey",4.8,115),
        ("Think and Grow Rich","Napoleon Hill","Self-Help",1937,"Principles of success from wealthy individuals",4.2,78),
        ("The Republic","Plato","Philosophy",-380,"Dialogue on justice and the ideal city-state",4.4,42),
        ("Charlotte's Web","E.B. White","Children",1952,"A pig is saved by his spider friend",4.7,65),
    ]
    result = []
    for i, (title, author, genre, year, desc, rating, borrow_count) in enumerate(books):
        result.append({
            "id": i+1, "title": title, "author": author, "genre": genre,
            "year": year, "description": desc, "available": True,
            "total_copies": random.randint(1,5), "rating": rating,
            "borrow_count": borrow_count, "cover_color": COVER_COLORS[i % len(COVER_COLORS)]
        })
    return result

def _seed_trains():
    trips = []
    for i in range(40):
        origin = random.choice(STATIONS)
        dest   = random.choice([s for s in STATIONS if s != origin])
        hour   = random.choice([6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
        minute = random.choice([0,15,30,45])
        weather= random.choices(WEATHERS, weights=[55,25,12,8])[0]
        peak   = hour in [7,8,9,17,18,19]
        pax    = random.randint(50,380)
        delay_base = {"Clear":5,"Rainy":20,"Foggy":30,"Stormy":50}[weather]
        delay_min  = max(0, delay_base + random.randint(-10,20) + (10 if peak else 0))
        trips.append({
            "id": i+1, "train_id": f"TR-{str(i+1).zfill(3)}",
            "origin": origin, "destination": dest,
            "sched_hour": hour, "sched_min": minute,
            "weather": weather, "passengers": pax,
            "delay_min": delay_min, "is_delayed": delay_min >= 5,
            "peak_hour": peak
        })
    return trips

init_state()

# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def get_user_by_email(email):
    return next((u for u in st.session_state.users if u["email"] == email), None)

def get_book(bid):
    return next((b for b in st.session_state.books if b["id"] == bid), None)

def login(email, password):
    u = get_user_by_email(email)
    if u and u["password"] == password:
        st.session_state.current_user = u
        return True
    return False

def logout():
    st.session_state.current_user = None
    st.session_state.page = "🏠 Home"

def star_rating(r):
    full = int(r); half = r - full >= 0.5
    return "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))

def risk_badge(prob):
    if prob > 0.5:   return f'<span class="risk-high">🔴 High ({prob:.0%})</span>'
    elif prob > 0.3: return f'<span class="risk-medium">🟡 Medium ({prob:.0%})</span>'
    else:            return f'<span class="risk-low">🟢 Low ({prob:.0%})</span>'

# ── AI: Overdue prediction (simple rule-based since no pkl in cloud) ──
def predict_late_risk(user, book, due_days):
    score = 0.1
    if user.get("age", 25) < 25:        score += 0.2
    if due_days <= 7:                    score += 0.15
    if user.get("total_borrowed",0) > 20: score += 0.1
    if user.get("fav_genre") != book.get("genre"): score += 0.05
    return min(round(score + random.uniform(-0.05, 0.05), 2), 0.95)

# ── AI: Recommendation ──
def recommend_books(book_id, n=4):
    book = get_book(book_id)
    if not book: return []
    same_genre = [b for b in st.session_state.books
                  if b["genre"] == book["genre"] and b["id"] != book_id]
    scored = sorted(same_genre, key=lambda b: b["rating"], reverse=True)[:n]
    return scored

# ── AI: NLP Search ──
def nlp_search(query):
    q = query.lower()
    results = []
    for b in st.session_state.books:
        score = 0
        if q in b["title"].lower():       score += 3
        if q in b["author"].lower():      score += 2
        if q in b["genre"].lower():       score += 2
        if q in b["description"].lower(): score += 1
        # keyword synonyms
        kw = {"space":"Science","history":"History","magic":"Fantasy",
              "mystery":"Mystery","tech":"Technology","code":"Technology",
              "kids":"Children","child":"Children","self":"Self-Help",
              "habit":"Self-Help","bio":"Biography","phil":"Philosophy"}
        for word, genre in kw.items():
            if word in q and b["genre"] == genre: score += 2
        if score > 0: results.append((score, b))
    results.sort(key=lambda x: -x[0])
    return [b for _, b in results[:8]]

# ── Chatbot ──
def chatbot_reply(msg):
    m = msg.lower()
    if any(w in m for w in ["hello","hi","hey"]):
        return "👋 Hello! I'm LibBot. Ask me to find books, recommend something, or show library stats!"
    if "find" in m or "search" in m or "book about" in m:
        query = m.replace("find","").replace("search","").replace("book about","").replace("books","").strip()
        results = nlp_search(query) if query else []
        if results:
            reply = f"📚 Found {len(results)} books matching **'{query}'**:\n"
            for b in results[:3]:
                avail = "✅" if b["available"] else "❌"
                reply += f"\n{avail} **{b['title']}** by {b['author']} *(★{b['rating']})*"
            return reply
        return f"🔍 No books found for '{query}'. Try: fiction, science, history..."
    if "recommend" in m or "suggest" in m:
        top = sorted(st.session_state.books, key=lambda b: b["rating"], reverse=True)[:5]
        reply = "⭐ **Top rated books:**\n"
        for b in top: reply += f"\n• **{b['title']}** ★{b['rating']} — {b['genre']}"
        return reply
    if "available" in m or "borrow" in m:
        avail = sum(1 for b in st.session_state.books if b["available"])
        return f"📖 **{avail}** books are currently available out of **{len(st.session_state.books)}** total."
    if "stat" in m or "how many" in m or "total" in m:
        total = len(st.session_state.books)
        avail = sum(1 for b in st.session_state.books if b["available"])
        loans = len(st.session_state.loans)
        return (f"📊 **Library Stats:**\n"
                f"• Total books: **{total}**\n"
                f"• Available: **{avail}**\n"
                f"• Genres: **{len(GENRES)}**\n"
                f"• Total loans: **{loans}**")
    if "train" in m:
        trips = len(st.session_state.train_trips)
        delayed = sum(1 for t in st.session_state.train_trips if t["is_delayed"])
        return (f"🚂 **Train System Stats:**\n"
                f"• Total trips: **{trips}**\n"
                f"• Delayed: **{delayed}** ({delayed/max(trips,1)*100:.0f}%)\n"
                f"• Stations: **{len(STATIONS)}**")
    if any(w in m for w in ["bye","thanks","thank you"]):
        return "👋 Goodbye! Happy reading and safe travels! 📚🚂"
    return ("🤖 I can help with:\n"
            "• **find books about [topic]**\n"
            "• **recommend a book**\n"
            "• **what books are available**\n"
            "• **show library stats**\n"
            "• **train info**")

# ── Train delay prediction ──
def predict_train_delay(trip):
    base = {"Clear": 0.08, "Rainy": 0.38, "Foggy": 0.45, "Stormy": 0.72}
    prob = base.get(trip["weather"], 0.15)
    if trip.get("peak_hour"): prob += 0.12
    if trip.get("passengers", 100) > 300: prob += 0.08
    return min(round(prob + random.uniform(-0.03, 0.03), 2), 0.95)

# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📚 Library AI System")
    st.markdown("---")

    if st.session_state.current_user:
        u = st.session_state.current_user
        st.markdown(f"**👤 {u['name']}**")
        st.caption(f"{u['role'].upper()} · {u['email']}")
        st.markdown("---")

    pages_member = ["🏠 Home","📖 Browse Books","🔍 AI Search","🤖 Chatbot",
                    "📋 My Loans","🚂 Train System"]
    pages_admin  = pages_member + ["⚙️ Admin Panel"]
    pages_guest  = ["🏠 Home","📖 Browse Books","🔍 AI Search","🚂 Train System","🔐 Login"]

    if st.session_state.current_user:
        if st.session_state.current_user["role"] == "admin":
            pages = pages_admin
        else:
            pages = pages_member
    else:
        pages = pages_guest

    for p in pages:
        active = st.session_state.page == p
        if st.button(p, key=f"nav_{p}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = p
            st.rerun()

    st.markdown("---")
    if st.session_state.current_user:
        if st.button("🚪 Logout", use_container_width=True):
            logout(); st.rerun()
    st.caption("📚 Library AI System v1.0\n🚂 Train Project Demo")

# ════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════
if st.session_state.page == "🏠 Home":
    st.markdown('<h1 style="color:#6366f1">📚 Library Management System</h1>', unsafe_allow_html=True)
    st.markdown("**AI-Powered · Online Library · Train Project**")
    st.markdown("---")

    # Metrics
    total  = len(st.session_state.books)
    avail  = sum(1 for b in st.session_state.books if b["available"])
    loans  = len(st.session_state.loans)
    users  = len(st.session_state.users)
    trains = len(st.session_state.train_trips)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("📚 Total Books", total)
    c2.metric("✅ Available", avail)
    c3.metric("📋 Active Loans", loans)
    c4.metric("👥 Users", users)
    c5.metric("🚂 Train Trips", trains)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⭐ Top Rated Books")
        top = sorted(st.session_state.books, key=lambda b: b["rating"], reverse=True)[:5]
        for b in top:
            avail_icon = "✅" if b["available"] else "❌"
            st.markdown(
                f'<div class="book-card"><span class="book-title">{avail_icon} {b["title"]}</span>'
                f'<br><span class="book-author">{b["author"]}</span> '
                f'<span class="genre-badge">{b["genre"]}</span> '
                f'<span style="color:#fbbf24">★{b["rating"]}</span></div>',
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("### 📊 Genre Distribution")
        genre_counts = pd.Series([b["genre"] for b in st.session_state.books]).value_counts()
        fig, ax = plt.subplots(figsize=(5,4), facecolor="#1e2130")
        ax.set_facecolor("#1e2130")
        wedges, texts, autotexts = ax.pie(
            genre_counts.values, labels=genre_counts.index,
            autopct='%1.0f%%', startangle=90,
            colors=plt.cm.Set2(np.linspace(0,1,len(genre_counts)))
        )
        for t in texts: t.set_color("white"); t.set_fontsize(8)
        for t in autotexts: t.set_color("white"); t.set_fontsize(7)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown("---")
    st.markdown("### 🤖 AI Features Overview")
    c1,c2,c3,c4 = st.columns(4)
    c1.info("📖 **Book Recommendations**\nContent-based filtering using genre & ratings")
    c2.info("🔍 **NLP Search**\nSearch with natural language — 'books about space'")
    c3.info("⏰ **Overdue Prediction**\nML model predicts late returns before they happen")
    c4.info("💬 **AI Chatbot**\nAsk anything about the library in natural language")

    if not st.session_state.current_user:
        st.markdown("---")
        st.success("👉 **Login** or use the sidebar to explore the system!")

# ════════════════════════════════════════════════════════════
# PAGE: BROWSE BOOKS
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "📖 Browse Books":
    st.markdown('<h2 class="section-header">📖 Book Catalog</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3,2,2])
    with col1: search = st.text_input("🔍 Search title / author", placeholder="e.g. Harry Potter")
    with col2: genre_filter = st.selectbox("Genre", ["All"] + GENRES)
    with col3: avail_filter = st.selectbox("Availability", ["All","Available","Borrowed"])

    books = st.session_state.books
    if search:
        q = search.lower()
        books = [b for b in books if q in b["title"].lower() or q in b["author"].lower()]
    if genre_filter != "All":
        books = [b for b in books if b["genre"] == genre_filter]
    if avail_filter == "Available":
        books = [b for b in books if b["available"]]
    elif avail_filter == "Borrowed":
        books = [b for b in books if not b["available"]]

    st.caption(f"Showing {len(books)} books")
    st.markdown("---")

    cols = st.columns(4)
    for i, book in enumerate(books):
        with cols[i % 4]:
            avail_icon = "✅" if book["available"] else "❌"
            st.markdown(
                f'<div class="book-card">'
                f'<div style="width:100%;height:6px;background:{book["cover_color"]};border-radius:4px;margin-bottom:10px"></div>'
                f'<div class="book-title">{book["title"]}</div>'
                f'<div class="book-author">{book["author"]}</div>'
                f'<div style="margin:6px 0"><span class="genre-badge">{book["genre"]}</span></div>'
                f'<div style="color:#fbbf24;font-size:0.85rem">★ {book["rating"]} &nbsp; {avail_icon}</div>'
                f'<div style="color:#64748b;font-size:0.75rem">Borrowed {book["borrow_count"]}×</div>'
                f'</div>', unsafe_allow_html=True
            )
            if st.session_state.current_user and book["available"]:
                if st.button(f"Borrow", key=f"borrow_{book['id']}"):
                    user = st.session_state.current_user
                    risk = predict_late_risk(user, book, 14)
                    loan = {
                        "id":       st.session_state.next_loan_id,
                        "user_id":  user["id"],
                        "book_id":  book["id"],
                        "book_title": book["title"],
                        "book_author": book["author"],
                        "borrow_date": date.today().isoformat(),
                        "due_date": (date.today() + timedelta(days=14)).isoformat(),
                        "return_date": None,
                        "is_returned": False,
                        "fine": 0.0,
                        "late_risk": risk
                    }
                    st.session_state.loans.append(loan)
                    st.session_state.next_loan_id += 1
                    # Mark book unavailable
                    for b in st.session_state.books:
                        if b["id"] == book["id"]:
                            b["available"] = False
                            b["borrow_count"] += 1
                    for u in st.session_state.users:
                        if u["id"] == user["id"]:
                            u["total_borrowed"] += 1
                    risk_level = "🔴 HIGH" if risk > 0.5 else "🟡 MEDIUM" if risk > 0.3 else "🟢 LOW"
                    st.success(f"✅ Borrowed! Due: {loan['due_date']} | Late risk: {risk_level}")
                    st.rerun()

            # Recommendations button
            if st.button(f"Similar", key=f"rec_{book['id']}"):
                recs = recommend_books(book["id"])
                if recs:
                    st.info("**Similar books:** " + " · ".join([r["title"] for r in recs]))

# ════════════════════════════════════════════════════════════
# PAGE: AI SEARCH
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🔍 AI Search":
    st.markdown('<h2 class="section-header">🔍 AI-Powered NLP Search</h2>', unsafe_allow_html=True)
    st.markdown("Search using **natural language** — describe what you want to read!")
    st.markdown("---")

    col1, col2 = st.columns([4,1])
    with col1:
        query = st.text_input("", placeholder="e.g. books about space, mystery thriller, learn programming, children adventure magic...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 Search", use_container_width=True)

    st.markdown("**💡 Try:** `books about space` · `mystery thriller` · `learn programming` · `philosophy stoic` · `children magic`")

    if query and (search_btn or query):
        results = nlp_search(query)
        st.markdown(f"---\n**Found {len(results)} results for:** *\"{query}\"*")
        if results:
            cols = st.columns(4)
            for i, book in enumerate(results):
                with cols[i % 4]:
                    avail = "✅ Available" if book["available"] else "❌ Borrowed"
                    st.markdown(
                        f'<div class="book-card">'
                        f'<div style="width:100%;height:5px;background:{book["cover_color"]};border-radius:3px;margin-bottom:8px"></div>'
                        f'<div class="book-title">{book["title"]}</div>'
                        f'<div class="book-author">{book["author"]}</div>'
                        f'<span class="genre-badge">{book["genre"]}</span><br>'
                        f'<span style="color:#fbbf24;font-size:0.85rem">★ {book["rating"]}</span> '
                        f'<span style="font-size:0.8rem;color:#94a3b8">{avail}</span>'
                        f'<p style="font-size:0.78rem;color:#64748b;margin-top:6px">{book["description"][:80]}...</p>'
                        f'</div>', unsafe_allow_html=True
                    )
        else:
            st.warning("No results found. Try different keywords.")

    st.markdown("---")
    st.markdown("### 📊 How NLP Search Works")
    col1, col2, col3 = st.columns(3)
    col1.success("**Step 1: Tokenize**\nYour query is broken into keywords")
    col2.success("**Step 2: Match**\nKeywords are matched against title, author, genre, description")
    col3.success("**Step 3: Rank**\nResults are scored and sorted by relevance")

# ════════════════════════════════════════════════════════════
# PAGE: CHATBOT
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🤖 Chatbot":
    st.markdown('<h2 class="section-header">🤖 LibBot — AI Assistant</h2>', unsafe_allow_html=True)
    st.markdown("Ask me anything about the library, books, or trains!")
    st.markdown("---")

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">🤖 <b>LibBot:</b><br>{msg["text"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([5,1])
    with col1:
        user_input = st.text_input("", placeholder="Type a message...", key="chat_input", label_visibility="collapsed")
    with col2:
        send = st.button("Send 📨", use_container_width=True)

    # Quick prompts
    st.markdown("**Quick prompts:**")
    qcols = st.columns(4)
    quick = ["find books about science","recommend a book","what books are available","show library stats"]
    for i, q in enumerate(quick):
        with qcols[i]:
            if st.button(q, key=f"quick_{i}"):
                st.session_state.chat_history.append({"role":"user","text":q})
                st.session_state.chat_history.append({"role":"bot","text":chatbot_reply(q)})
                st.rerun()

    if send and user_input:
        st.session_state.chat_history.append({"role":"user","text":user_input})
        st.session_state.chat_history.append({"role":"bot","text":chatbot_reply(user_input)})
        st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []; st.rerun()

# ════════════════════════════════════════════════════════════
# PAGE: MY LOANS
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "📋 My Loans":
    if not st.session_state.current_user:
        st.warning("Please login to view your loans.")
        st.stop()

    st.markdown('<h2 class="section-header">📋 My Loans</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    my_loans = [l for l in st.session_state.loans if l["user_id"] == user["id"]]

    if not my_loans:
        st.info("You haven't borrowed any books yet. Go to **Browse Books** to borrow!")
    else:
        c1, c2, c3 = st.columns(3)
        active_loans   = [l for l in my_loans if not l["is_returned"]]
        returned_loans = [l for l in my_loans if l["is_returned"]]
        total_fines    = sum(l["fine"] for l in my_loans)
        c1.metric("📚 Active Loans", len(active_loans))
        c2.metric("✅ Returned", len(returned_loans))
        c3.metric("💰 Total Fines", f"${total_fines:.2f}")

        st.markdown("---")
        st.markdown("### 📌 Active Loans")
        for loan in active_loans:
            due = date.fromisoformat(loan["due_date"])
            days_left = (due - date.today()).days
            overdue   = days_left < 0
            risk      = loan.get("late_risk", 0.2)
            risk_color = "🔴" if risk > 0.5 else "🟡" if risk > 0.3 else "🟢"

            st.markdown(
                f'<div class="card">'
                f'<b style="color:#e2e8f0">{loan["book_title"]}</b> '
                f'<span style="color:#94a3b8">by {loan["book_author"]}</span><br>'
                f'📅 Due: <b style="color:{"#f87171" if overdue else "#4ade80"}">{loan["due_date"]}</b> '
                f'{"🚨 OVERDUE by "+str(abs(days_left))+" days" if overdue else f"({days_left} days left)"}'
                f'&nbsp;&nbsp; {risk_color} Late risk: {risk:.0%}'
                f'</div>', unsafe_allow_html=True
            )
            if st.button(f"↩ Return this book", key=f"ret_{loan['id']}"):
                today      = date.today()
                days_late  = max(0, (today - due).days)
                fine       = round(days_late * 0.5, 2)
                loan["return_date"] = today.isoformat()
                loan["is_returned"] = True
                loan["fine"]        = fine
                for b in st.session_state.books:
                    if b["id"] == loan["book_id"]:
                        b["available"] = True
                msg = f"✅ Returned! Fine: ${fine:.2f}" if fine > 0 else "✅ Returned on time — no fine!"
                st.success(msg); st.rerun()

        if returned_loans:
            st.markdown("### ✅ Returned Books")
            df = pd.DataFrame([{
                "Book": l["book_title"], "Borrowed": l["borrow_date"],
                "Due": l["due_date"], "Returned": l["return_date"], "Fine $": l["fine"]
            } for l in returned_loans])
            st.dataframe(df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# PAGE: TRAIN SYSTEM
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🚂 Train System":
    st.markdown('<h2 class="section-header">🚂 Train Scheduling System</h2>', unsafe_allow_html=True)
    st.markdown("Search trains, view schedules, book seats — with **AI delay prediction**.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🔍 Search Trains","📊 Train Analytics","🎫 My Bookings"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1: origin = st.selectbox("From", STATIONS, index=0)
        with col2: dest   = st.selectbox("To",   [s for s in STATIONS if s != origin], index=0)
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            search_trains = st.button("🔍 Search Trains", use_container_width=True)

        if search_trains or True:
            trips = [t for t in st.session_state.train_trips
                     if t["origin"] == origin and t["destination"] == dest]
            if not trips:
                st.info(f"No direct trains found from {origin} to {dest}. Showing sample schedule:")
                trips = st.session_state.train_trips[:5]

            st.markdown(f"**{len(trips)} trains found: {origin} → {dest}**")
            for trip in sorted(trips, key=lambda x: x["sched_hour"])[:8]:
                prob  = predict_train_delay(trip)
                risk  = "🔴 High" if prob > 0.55 else "🟡 Medium" if prob > 0.3 else "🟢 Low"
                seats = max(0, 400 - trip["passengers"])
                weather_icons = {"Clear":"☀️","Rainy":"🌧️","Foggy":"🌫️","Stormy":"⛈️"}
                wicon = weather_icons.get(trip["weather"],"🌤️")

                col1, col2, col3, col4, col5 = st.columns([2,2,2,2,2])
                col1.markdown(f"**{trip['train_id']}**\n{trip['sched_hour']:02d}:{trip['sched_min']:02d}")
                col2.markdown(f"{wicon} {trip['weather']}\n👥 {trip['passengers']} pax")
                col3.markdown(f"💺 {seats} seats\nDelay: **{risk}** ({prob:.0%})")
                col4.markdown(f"⏱ ~{30 + abs(hash(origin+dest)) % 60} min")
                with col5:
                    if st.session_state.current_user:
                        if st.button("🎫 Book", key=f"book_train_{trip['id']}"):
                            seat = random.choice("ABCDE") + str(random.randint(1,30))
                            ref  = "BK" + "".join(random.choices(string.digits, k=6))
                            booking = {
                                "id":       st.session_state.next_booking_id,
                                "user_id":  st.session_state.current_user["id"],
                                "trip_id":  trip["id"],
                                "train_id": trip["train_id"],
                                "origin":   trip["origin"],
                                "destination": trip["destination"],
                                "departs":  f"{trip['sched_hour']:02d}:{trip['sched_min']:02d}",
                                "seat":     seat,
                                "booking_ref": ref,
                                "delay_probability": prob
                            }
                            st.session_state.train_bookings.append(booking)
                            st.session_state.next_booking_id += 1
                            st.success(f"✅ Booked! Ref: **{ref}** | Seat: **{seat}**")
                            st.rerun()
                    else:
                        st.caption("Login to book")
                st.markdown("---")

    with tab2:
        trips_df = pd.DataFrame(st.session_state.train_trips)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Delay Rate by Weather**")
            wd = trips_df.groupby("weather")["is_delayed"].mean() * 100
            fig, ax = plt.subplots(figsize=(5,3), facecolor="#1e2130")
            ax.set_facecolor("#1e2130")
            colors = {"Clear":"#4ade80","Rainy":"#60a5fa","Foggy":"#94a3b8","Stormy":"#f87171"}
            bars = ax.bar(wd.index, wd.values, color=[colors.get(w,"gray") for w in wd.index])
            ax.set_ylabel("Delay Rate (%)", color="white")
            ax.tick_params(colors="white")
            for spine in ax.spines.values(): spine.set_color("#2d3148")
            ax.yaxis.label.set_color("white")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with col2:
            st.markdown("**Delay by Hour of Day**")
            hd = trips_df.groupby("sched_hour")["is_delayed"].mean() * 100
            fig, ax = plt.subplots(figsize=(5,3), facecolor="#1e2130")
            ax.set_facecolor("#1e2130")
            ax.plot(hd.index, hd.values, color="#6366f1", linewidth=2.5, marker="o", markersize=5)
            ax.fill_between(hd.index, hd.values, alpha=0.15, color="#6366f1")
            ax.set_xlabel("Hour", color="white"); ax.set_ylabel("Delay %", color="white")
            ax.tick_params(colors="white")
            for spine in ax.spines.values(): spine.set_color("#2d3148")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        st.markdown("**📋 Station Traffic**")
        origin_counts = trips_df["origin"].value_counts().reset_index()
        origin_counts.columns = ["Station","Departures"]
        st.dataframe(origin_counts, use_container_width=True, hide_index=True)

    with tab3:
        if not st.session_state.current_user:
            st.info("Login to see your train bookings.")
        else:
            my_bookings = [b for b in st.session_state.train_bookings
                           if b["user_id"] == st.session_state.current_user["id"]]
            if not my_bookings:
                st.info("No train bookings yet. Search and book a train above!")
            else:
                st.metric("🎫 Total Bookings", len(my_bookings))
                for b in my_bookings:
                    st.markdown(
                        f'<div class="train-card">'
                        f'🎫 <b>{b["booking_ref"]}</b> &nbsp; Seat: <b>{b["seat"]}</b><br>'
                        f'🚂 {b["train_id"]} &nbsp; {b["origin"]} → {b["destination"]} '
                        f'at <b>{b["departs"]}</b><br>'
                        f'⚠️ Delay risk: {b["delay_probability"]:.0%}'
                        f'</div>', unsafe_allow_html=True
                    )

# ════════════════════════════════════════════════════════════
# PAGE: ADMIN PANEL
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "⚙️ Admin Panel":
    if not st.session_state.current_user or st.session_state.current_user["role"] != "admin":
        st.error("Admin access only.")
        st.stop()

    st.markdown('<h2 class="section-header">⚙️ Admin Panel</h2>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview","📚 Manage Books","📋 All Loans","👥 Users"])

    with tab1:
        total_books = len(st.session_state.books)
        avail_books = sum(1 for b in st.session_state.books if b["available"])
        total_loans = len(st.session_state.loans)
        overdue_loans = sum(1 for l in st.session_state.loans
                            if not l["is_returned"] and
                            date.fromisoformat(l["due_date"]) < date.today())
        total_fines = sum(l["fine"] for l in st.session_state.loans)
        train_bookings = len(st.session_state.train_bookings)

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("📚 Books", total_books)
        c2.metric("✅ Available", avail_books)
        c3.metric("📋 Loans", total_loans)
        c4.metric("🚨 Overdue", overdue_loans)
        c5.metric("💰 Fines $", f"{total_fines:.2f}")
        c6.metric("🎫 Train Bookings", train_bookings)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Genre Popularity (Borrows)**")
            genre_borrows = {}
            for b in st.session_state.books:
                genre_borrows[b["genre"]] = genre_borrows.get(b["genre"],0) + b["borrow_count"]
            gdf = pd.Series(genre_borrows).sort_values(ascending=True)
            fig, ax = plt.subplots(figsize=(5,4), facecolor="#1e2130")
            ax.set_facecolor("#1e2130")
            ax.barh(gdf.index, gdf.values, color="#6366f1")
            ax.tick_params(colors="white"); ax.set_xlabel("Total Borrows", color="white")
            for spine in ax.spines.values(): spine.set_color("#2d3148")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with col2:
            st.markdown("**Late Risk Distribution**")
            risks = [l.get("late_risk", 0.2) for l in st.session_state.loans]
            if risks:
                fig, ax = plt.subplots(figsize=(5,4), facecolor="#1e2130")
                ax.set_facecolor("#1e2130")
                ax.hist(risks, bins=10, color="#f59e0b", edgecolor="#1e2130")
                ax.set_xlabel("Late Risk Score", color="white")
                ax.set_ylabel("Count", color="white")
                ax.tick_params(colors="white")
                for spine in ax.spines.values(): spine.set_color("#2d3148")
                plt.tight_layout(); st.pyplot(fig); plt.close()
            else:
                st.info("No loan data yet.")

    with tab2:
        st.markdown("### ➕ Add New Book")
        with st.form("add_book_form"):
            c1,c2 = st.columns(2)
            with c1:
                title  = st.text_input("Title *")
                author = st.text_input("Author *")
                genre  = st.selectbox("Genre", GENRES)
            with c2:
                year   = st.number_input("Year", 1800, 2024, 2020)
                rating = st.slider("Rating", 1.0, 5.0, 4.0, 0.1)
                copies = st.number_input("Copies", 1, 10, 1)
            desc   = st.text_area("Description")
            color  = st.color_picker("Cover Color", "#6366f1")
            if st.form_submit_button("➕ Add Book"):
                if title and author:
                    new_id = max(b["id"] for b in st.session_state.books) + 1
                    st.session_state.books.append({
                        "id": new_id, "title": title, "author": author, "genre": genre,
                        "year": int(year), "description": desc, "available": True,
                        "total_copies": int(copies), "rating": rating,
                        "borrow_count": 0, "cover_color": color
                    })
                    st.success(f"✅ '{title}' added to catalog!")
                    st.rerun()
                else:
                    st.error("Title and Author are required.")

        st.markdown("---")
        st.markdown("### 📚 Book List")
        df = pd.DataFrame([{
            "ID":b["id"],"Title":b["title"],"Author":b["author"],
            "Genre":b["genre"],"Rating":b["rating"],
            "Borrows":b["borrow_count"],"Available":"✅" if b["available"] else "❌"
        } for b in st.session_state.books])
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 📋 All Loans")
        if not st.session_state.loans:
            st.info("No loans yet.")
        else:
            today = date.today()
            overdue_list = [l for l in st.session_state.loans
                            if not l["is_returned"] and
                            date.fromisoformat(l["due_date"]) < today]
            if overdue_list:
                st.warning(f"🚨 {len(overdue_list)} overdue loans!")
                for l in overdue_list:
                    days_over = (today - date.fromisoformat(l["due_date"])).days
                    st.markdown(
                        f'<div class="card" style="border-color:#f87171">'
                        f'🚨 <b>{l["book_title"]}</b> — due {l["due_date"]} '
                        f'({days_over} days overdue) — Fine: ${days_over*0.5:.2f}'
                        f'</div>', unsafe_allow_html=True
                    )

            df = pd.DataFrame([{
                "ID":l["id"],"Book":l["book_title"],"Borrowed":l["borrow_date"],
                "Due":l["due_date"],"Returned":l["return_date"] or "—",
                "Fine $":l["fine"],"Status":"Returned" if l["is_returned"] else "Active",
                "Late Risk":f'{l.get("late_risk",0):.0%}'
            } for l in st.session_state.loans])
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### 👥 Registered Users")
        df = pd.DataFrame([{
            "ID":u["id"],"Name":u["name"],"Email":u["email"],
            "Role":u["role"],"Age":u["age"],
            "Fav Genre":u["fav_genre"],"Borrowed":u["total_borrowed"]
        } for u in st.session_state.users])
        st.dataframe(df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🔐 Login":
    st.markdown('<h2 class="section-header">🔐 Login</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["Login","Register"])
        with tab1:
            with st.form("login_form"):
                email    = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("🔐 Login", use_container_width=True):
                    if login(email, password):
                        st.success(f"✅ Welcome back, {st.session_state.current_user['name']}!")
                        st.session_state.page = "🏠 Home"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            st.markdown("---")
            st.caption("**Demo accounts:**")
            st.code("Admin:  admin@library.com / admin123\nMember: ahmed@email.com  / pass123")

        with tab2:
            with st.form("register_form"):
                r_name  = st.text_input("Full Name")
                r_email = st.text_input("Email")
                r_pass  = st.text_input("Password", type="password")
                r_age   = st.number_input("Age", 10, 100, 25)
                r_genre = st.selectbox("Favourite Genre", GENRES)
                if st.form_submit_button("✅ Register", use_container_width=True):
                    if get_user_by_email(r_email):
                        st.error("Email already registered.")
                    elif r_name and r_email and r_pass:
                        new_id = max(u["id"] for u in st.session_state.users) + 1
                        new_user = {
                            "id": new_id, "name": r_name, "email": r_email,
                            "password": r_pass, "role": "member",
                            "age": int(r_age), "fav_genre": r_genre, "total_borrowed": 0
                        }
                        st.session_state.users.append(new_user)
                        st.session_state.current_user = new_user
                        st.success("✅ Account created! Welcome!")
                        st.session_state.page = "🏠 Home"
                        st.rerun()
                    else:
                        st.error("Please fill all fields.")
