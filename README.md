# 📚 Library Management System — AI + Train Project
### Deployed on Streamlit Cloud

---

## 🚀 Deploy to Streamlit Cloud (Step-by-Step)

### Step 1 — Push code to GitHub
```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "Library AI System - Streamlit"
git remote add origin https://github.com/YOUR_USERNAME/library-ai-streamlit
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repo: `library-ai-streamlit`
5. Branch: `main`
6. Main file path: `app.py`
7. Click **"Deploy!"**
8. Wait ~2 minutes → your app is LIVE! 🎉

### Step 3 — Get your live URL
Your app will be live at:
```
https://YOUR_USERNAME-library-ai-streamlit-app-XXXXX.streamlit.app
```

---

## 🗂 Project Structure
```
library-ai-streamlit/
├── app.py              ← Main Streamlit app (ALL pages)
├── requirements.txt    ← Python packages
├── README.md           ← This file
└── ml_models/          ← (Optional) Place .pkl files from Colab here
    ├── overdue_model.pkl
    ├── overdue_scaler.pkl
    ├── tfidf_recommender.pkl
    └── train_delay_model.pkl
```

---

## 🤖 Features
| Feature | Description |
|---------|-------------|
| 📖 Book Catalog | Browse, search, filter 20+ books |
| 🔐 Auth | Login / Register with roles (Admin / Member) |
| 📋 Borrow & Return | Issue books, track due dates, calculate fines |
| 🔍 NLP Search | Natural language: "books about space" |
| 🤖 Chatbot | Ask LibBot anything about the library |
| ⏰ Overdue Prediction | AI predicts late returns at borrow time |
| 🚂 Train System | Search routes, book seats, delay prediction |
| ⚙️ Admin Panel | Full dashboard, manage books, view all loans |

---

## 🔑 Demo Login Credentials
```
Admin:   admin@library.com  /  admin123
Member:  ahmed@email.com    /  pass123
Member:  sara@email.com     /  pass123
```

---

## 🧠 Adding Real AI Models (from Colab)
1. Run the `Library_AI_Train_System.ipynb` notebook in Google Colab
2. Download the `.pkl` files from Colab
3. Create a `ml_models/` folder in your project
4. Place the `.pkl` files there
5. Commit and push to GitHub → Streamlit redeploys automatically

---

## 📦 Packages Used
- `streamlit` — UI framework
- `pandas` + `numpy` — data handling
- `matplotlib` + `seaborn` — charts
- `scikit-learn` + `xgboost` — ML models
- `joblib` — model loading
