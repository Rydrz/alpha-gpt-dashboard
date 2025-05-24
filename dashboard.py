import streamlit as st
st.set_page_config(page_title="Alpha GPT - Dashboard", layout="wide")

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import streamlit_authenticator as stauth
import numpy as np

# === Chargement des variables d’environnement ===
load_dotenv()

# === Fonctions de base ===

def get_connection():
    return psycopg2.connect(os.getenv("POSTGRES_URL"))

def fetch_latest_decisions(limit=100):
    conn = get_connection()
    df = pd.read_sql(f'''
        SELECT *
        FROM decision_log
        ORDER BY timestamp DESC
        LIMIT {limit};
    ''', conn)
    conn.close()
    return df

def fetch_decision_stats():
    conn = get_connection()
    df = pd.read_sql('''
        SELECT decision, COUNT(*) AS total
        FROM decision_log
        GROUP BY decision
        ORDER BY total DESC;
    ''', conn)
    conn.close()
    return df

def get_dashboard_kpis():
    conn = get_connection()
    df = pd.read_sql("SELECT decision, timestamp FROM decision_log", conn)
    conn.close()

    total = len(df)
    buy = len(df[df["decision"] == "BUY"])
    sell = len(df[df["decision"] == "SELL"])
    hold = len(df[df["decision"] == "HOLD"])
    last_date = df["timestamp"].max() if not df.empty else "Aucune"

    return total, buy, sell, hold, last_date

def get_decision_trends(start_date=None, end_date=None):
    conn = get_connection()
    df = pd.read_sql("SELECT decision, timestamp FROM decision_log", conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # Appliquer les filtres
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]

    trends = df.groupby(["date", "decision"]).size().unstack(fill_value=0)
    return trends

def build_daily_summary():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM decision_log", conn)
    conn.close()

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    if "pnl" not in df.columns:
        np.random.seed(42)
        df["pnl"] = np.random.uniform(-10, 10, size=len(df)).round(2)  # simulation

    summary = df.groupby("date").agg(
        BUY=('decision', lambda x: (x == 'BUY').sum()),
        SELL=('decision', lambda x: (x == 'SELL').sum()),
        HOLD=('decision', lambda x: (x == 'HOLD').sum()),
        Performance=('pnl', 'sum'),
    ).reset_index()

    return summary, df

def get_global_stats():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM decision_log", conn)
    conn.close()

    if df.empty:
        return 0, 0, 0, 0, 0.0

    total = len(df)
    buy = (df["decision"] == "BUY").sum()
    sell = (df["decision"] == "SELL").sum()
    hold = (df["decision"] == "HOLD").sum()

    if "pnl" not in df.columns:
        np.random.seed(42)
        df["pnl"] = np.random.uniform(-10, 10, size=len(df)).round(2)

    performance = df["pnl"].sum()

    return total, buy, sell, hold, performance

# === Authentification ===
names = ["Admin"]
usernames = [os.getenv("APP_USERNAME")]
passwords = [os.getenv("APP_PASSWORD")]
cookie_key = os.getenv("APP_COOKIE_KEY")
cookie_name = "alpha_gpt_dashboard"

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    {"usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]}
    }},
    cookie_name,
    cookie_key,
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("🔐 Connexion", "main")

if authentication_status is False:
    st.error("Mot de passe incorrect.")
    st.stop()
elif authentication_status is None:
    st.warning("Veuillez entrer vos identifiants.")
    st.stop()

# === Interface principale ===
st.title("📊 Alpha GPT - Historique des décisions")

# === Statistiques globales ===
total, buy, sell, hold, perf = get_global_stats()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📊 Total", total)
col2.metric("🟢 BUY", buy)
col3.metric("🔴 SELL", sell)
col4.metric("⚪ HOLD", hold)
col5.metric("💰 Performance totale", f"{perf:.2f} €")

# === KPIs principaux ===
total, buy, sell, hold, last_date = get_dashboard_kpis()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📊 Total", total)
col2.metric("🟢 BUY", buy)
col3.metric("🔴 SELL", sell)
col4.metric("⚪ HOLD", hold)
col5.metric("🕒 Dernière décision", str(last_date)[:16])

# === Filtres de date ===
st.subheader("📅 Évolution quotidienne des décisions")
col_start, col_end = st.columns(2)

with col_start:
    start_date = st.date_input("📆 Date de début", value=None)
with col_end:
    end_date = st.date_input("📆 Date de fin", value=None)

trends_df = get_decision_trends(start_date, end_date)

trends_df = get_decision_trends()

if not trends_df.empty:
    st.line_chart(trends_df)
else:
    st.info("Pas encore assez de données pour afficher une tendance.")

st.subheader("📆 Journal des décisions par jour")

summary_df, full_df = build_daily_summary()

if summary_df.empty:
    st.info("Aucune donnée disponible.")
else:
    for _, row in summary_df.iterrows():
        perf = row["Performance"]
        perf_color = "🟢" if perf > 0 else "🔴" if perf < 0 else "⚪"
        header = f"{row['date']} - 🟢 {row['BUY']} | 🔴 {row['SELL']} | ⚪ {row['HOLD']} | {perf_color} {perf} €"

        with st.expander(header):
            details = full_df[full_df["timestamp"].dt.date == row['date']]
            st.dataframe(details[["timestamp", "decision", "pnl"]])

# Affichage des statistiques
st.subheader("📈 Répartition des décisions")
stats_df = fetch_decision_stats()
st.bar_chart(stats_df.set_index("decision"))

# Affichage des logs
st.subheader("📝 Dernières décisions enregistrées")
latest_df = fetch_latest_decisions()
st.dataframe(latest_df)
