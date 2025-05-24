import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# === Authentification simple ===
import streamlit_authenticator as stauth

# Création de l'authentificateur
names = ["Admin"]
usernames = ["admin"]
passwords = ["alphaGPT2025"]  # mot de passe à modifier

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    {"usernames": {"admin": {"name": "Admin", "password": hashed_passwords[0]}}},
    "alpha_gpt_dashboard",  # nom de cookie
    "abcdef123456",          # clé de signature (change-la si tu veux)
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("🔐 Connexion", "main")

if authentication_status is False:
    st.error("Mot de passe incorrect.")
elif authentication_status is None:
    st.warning("Veuillez entrer vos identifiants.")
    st.stop()
else:
    # === Interface principale du dashboard ===
    st.set_page_config(page_title="Alpha GPT - Dashboard", layout="wide")
    st.title("📊 Alpha GPT - Historique des décisions")

    # Affichage des statistiques
    st.subheader("Répartition des décisions")
    stats_df = fetch_decision_stats()
    st.bar_chart(stats_df.set_index("decision"))

    # Affichage des logs
    st.subheader("📝 Dernières décisions enregistrées")
    latest_df = fetch_latest_decisions()
    st.dataframe(latest_df)

# Charger .env pour accéder à POSTGRES_URL
load_dotenv()

# Connexion PostgreSQL
def get_connection():
    return psycopg2.connect(os.getenv("POSTGRES_URL"))

# Lecture des 100 dernières décisions
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

# Statistiques par type de décision
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

