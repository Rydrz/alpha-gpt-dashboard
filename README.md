# 🤖 Alpha GPT – Bot de Trading IA

## 📌 Description

Alpha GPT est un agent IA de trading crypto connecté à KuCoin, conçu pour prendre des décisions intelligentes (BUY / SELL / HOLD) en fonction :
- d’analyses techniques,
- d’informations macroéconomiques,
- de sentiments extraits de l’actualité.

Il enregistre toutes ses décisions dans une base PostgreSQL distante et fournit un dashboard complet via Streamlit.

---

## 🚀 Fonctionnalités principales

- 🔍 Analyse des signaux économiques, news et tendance du marché
- 📊 Tableau de bord sécurisé (authentification) via Streamlit
- 🧠 Sauvegarde automatique des décisions
- 📅 Journal quotidien avec détail des performances
- ☁️ Hébergement Railway + GitHub

---

## 🛠 Déploiement

### 1. Cloner le dépôt

```bash
git clone https://github.com/ton-utilisateur/alpha-gpt-dashboard.git
cd alpha-gpt-dashboard
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer le fichier `.env`

```dotenv
POSTGRES_URL=...
APP_USERNAME=admin
APP_PASSWORD=...
APP_COOKIE_KEY=...
```

### 4. Initialiser la base de données

```bash
psql -h <host> -U <user> -d <database> -f setup.sql
```

OU via DBeaver : ouvrir `setup.sql` et cliquer sur ▶

---

## 📊 Lancer le dashboard Streamlit

```bash
streamlit run dashboard.py
```

Dashboard accessible avec login (défini dans `.env`) :
- Username : admin
- Password : (défini dans APP_PASSWORD)

---

## 📂 Structure du projet

```
Alpha GPT/
├── dashboard.py
├── orchestrateur.py
├── modules/
│   └── data_collectors.py
├── data/
├── logs/
├── setup.sql
├── requirements.txt
└── README.md
```

---

## 📅 Suivi automatique quotidien

À chaque exécution, l’agent enregistre :

- Nombre total de décisions
- Répartition BUY / SELL / HOLD
- Performance simulée ou réelle
- Données stockées dans `daily_summary` (PostgreSQL)

---

## 📆 Dernière mise à jour
2025-05-24
