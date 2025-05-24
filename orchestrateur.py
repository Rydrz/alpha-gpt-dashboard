# orchestrateur.py

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
from modules.gpt_client import query_gpt_agent  # 🔗 Appel GPT réel
from modules.kucoin_client import place_market_order, get_balance
from dotenv import load_dotenv
load_dotenv()
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"



# Initialisation du logger
logging.basicConfig(
    filename="logs/orchestrator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === ÉTAPE 1 : COLLECTE DES DONNÉES ===
def get_market_data() -> Dict[str, Any]:
    logging.info("Récupération des données marché...")
    return {"BTC": {"open": 65000, "close": 65500, "volume": 1250}}  # Placeholder

def get_macro_news() -> str:
    logging.info("Récupération des actualités macro...")
    return "Inflation US au-dessus des attentes. Réaction attendue de la Fed."

def get_sentiment_data() -> Dict[str, Any]:
    logging.info("Récupération des données de sentiment...")
    return {"fear_greed": 34, "mentions": {"BTC": 1500}}

# === ÉTAPE 2 : APPELS AUX AGENTS GPT ===
def call_gpt_agent(agent_name: str, prompt: str) -> str:
    logging.info(f"Appel de l'agent GPT : {agent_name}")
    try:
        return query_gpt_agent(agent_name, prompt)
    except Exception as e:
        logging.error(f"Erreur lors de l'appel à {agent_name} : {e}")
        return f"Erreur avec {agent_name} : {str(e)}"

# === ÉTAPE 3 : SYNTHÈSE STRATÉGIQUE ===
def analyse_globale():
    market_data = get_market_data()
    news_data = get_macro_news()
    sentiment_data = get_sentiment_data()

    res_news = call_gpt_agent("NewsMacroGPT", news_data)
    res_sentiment = call_gpt_agent("SentimentGPT", json.dumps(sentiment_data))
    res_tech = call_gpt_agent("TechGPT", json.dumps(market_data))

    synthese = f"NEWS:\n{res_news}\n\nSENTIMENT:\n{res_sentiment}\n\nTECH:\n{res_tech}"
    decision = call_gpt_agent("StratègeGPT", synthese)

    logging.info(f"Décision stratégique : {decision}")
    return decision

# === ÉTAPE 4 : LOGGING FINAL ===
def log_decision(decision: str):
    with open("data/decision_log.csv", "a") as f:
        f.write(f"{datetime.now()},{decision}\n")

# === ÉTAPE 5 : EXÉCUTION D'UN TRADE SI NÉCESSAIRE ===
from modules.kucoin_client import place_market_order, get_balance

def executer_trade(decision: str):
    decision = decision.upper()

    if decision.startswith("BUY") or decision.startswith("SELL"):
        try:
            parts = decision.split()
            action = parts[0]     # 'BUY' ou 'SELL'
            asset = parts[1]      # 'BTC', 'ETH', etc.
            symbol = f"{asset}/USDT"
            usdt_dispo = get_balance("USDT")

            if action == "BUY":
                montant_usdt = min(50, usdt_dispo)
                if montant_usdt < 10:
                    logging.warning("❌ Fonds insuffisants pour BUY.")
                    return
                amount = round(montant_usdt / 50000, 5)

                if SIMULATION_MODE:
                    logging.info(f"🧪 [SIMULATION] BUY {amount} {asset}")
                else:
                    place_market_order(symbol, "buy", amount)

            elif action == "SELL":
                amount = 0.001

                if SIMULATION_MODE:
                    logging.info(f"🧪 [SIMULATION] SELL {amount} {asset}")
                else:
                    place_market_order(symbol, "sell", amount)

        except Exception as e:
            logging.error(f"Erreur d’exécution du trade : {e}")
    else:
        logging.info("Aucun trade exécuté (HOLD ou décision non reconnue).")

# === MAIN LOOP ===
if __name__ == "__main__":
    logging.info("Lancement de l'orchestrateur IA de trading crypto...")
    decision = analyse_globale()
    log_decision(decision)
    executer_trade(decision)
    logging.info("Exécution terminée.")
