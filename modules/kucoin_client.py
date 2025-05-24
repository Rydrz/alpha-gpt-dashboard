# modules/kucoin_client.py

import os
import ccxt
from dotenv import load_dotenv
import logging

# Chargement des variables d’environnement (.env)
load_dotenv()

# Initialisation du logger local
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# === Initialisation du client KuCoin ===
def init_kucoin():
    return ccxt.kucoin({
        'apiKey': os.getenv("KUCOIN_API_KEY"),
        'secret': os.getenv("KUCOIN_SECRET_KEY"),
        'password': os.getenv("KUCOIN_PASSPHRASE"),
        'enableRateLimit': True
    })

# === Placer un ordre de marché ===
def place_market_order(symbol: str, side: str, amount: float):
    """
    Place un ordre de marché.

    Args:
        symbol (str): Paire à trader (ex: 'BTC/USDT')
        side (str): 'buy' ou 'sell'
        amount (float): Quantité à trader (ex: 0.001)
    """
    kucoin = init_kucoin()
    try:
        order = kucoin.create_market_order(symbol=symbol, side=side, amount=amount)
        logger.info(f"✅ Ordre {side.upper()} placé sur {symbol} pour {amount} unités.")
        return order
    except Exception as e:
        logger.error(f"❌ Erreur lors du placement de l'ordre : {e}")
        return None

# === Obtenir le solde disponible ===
def get_balance(asset: str = 'USDT') -> float:
    """
    Récupère le solde disponible d’un actif donné.

    Args:
        asset (str): Nom de l’actif (par défaut 'USDT')

    Returns:
        float: Montant disponible
    """
    kucoin = init_kucoin()
    try:
        balance = kucoin.fetch_balance()
        return balance['free'].get(asset, 0.0)
    except Exception as e:
        logger.error(f"❌ Erreur de récupération du solde : {e}")
        return 0.0
