# modules/gpt_client.py

import os
import openai
import logging
from dotenv import load_dotenv
from time import sleep

# Charger les variables d'environnement (.env)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration du logger local
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def query_gpt_agent(agent_name: str, prompt: str, model: str = "gpt-4", retries: int = 3, delay: float = 2.0) -> str:
    """
    Envoie un prompt à un agent GPT personnalisé, avec gestion des erreurs et tentative automatique.
    
    Args:
        agent_name (str): Nom logique de l'agent GPT (ex: StratègeGPT)
        prompt (str): Contenu à analyser ou traiter par l'agent
        model (str): Modèle OpenAI utilisé (par défaut: gpt-4)
        retries (int): Nombre de tentatives en cas d’échec
        delay (float): Temps d’attente entre les tentatives (secondes)

    Returns:
        str: Réponse textuelle de l’agent
    """
    for attempt in range(retries):
        try:
            logger.info(f"📤 Envoi à {agent_name} (essai {attempt + 1}/{retries})")

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"Tu es {agent_name}, un agent IA expert et structuré."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4  # Favorise les réponses stables
            )
            return response["choices"][0]["message"]["content"]

        except openai.error.OpenAIError as e:
            logger.warning(f"⚠️ Erreur avec {agent_name} : {str(e)}")
            if attempt < retries - 1:
                sleep(delay)
            else:
                raise RuntimeError(f"❌ Échec de l'appel à {agent_name} après {retries} tentatives.") from e
