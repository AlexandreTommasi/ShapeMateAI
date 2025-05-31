import os
from dotenv import load_dotenv
from fatsecret import Fatsecret
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis do .env
load_dotenv()

# Obter as credenciais da API
CONSUMER_KEY = os.getenv("FATSECRET_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("FATSECRET_CONSUMER_SECRET")

# Verificação básica
if not CONSUMER_KEY or not CONSUMER_SECRET:
    raise ValueError("FATSECRET_CONSUMER_KEY ou FATSECRET_CONSUMER_SECRET não encontrados no .env")

# Instanciar a API
fs = Fatsecret(CONSUMER_KEY, CONSUMER_SECRET)

def search_foods(nome: str):
    """
    Busca alimentos por nome ou palavra-chave.
    """
    try:
        resultado = fs.foods_search(nome)
        return resultado.get('foods', {}).get('food', [])
    except Exception as e:
        logger.error(f"Erro ao buscar alimento '{nome}': {e}")
        return []

def get_food_data(food_id: int):
    """
    Retorna os dados brutos de um alimento pelo ID.
    """
    try:
        return fs.food_get(food_id)
    except Exception as e:
        logger.error(f"Erro ao obter dados do alimento ID {food_id}: {e}")
        return {}

def get_nutrients_by_food_id(food_id: int):
    """
    Retorna os principais nutrientes de um alimento.
    """
    data = get_food_data(food_id)
    servings = data.get("food", {}).get("servings", {}).get("serving", {})

    # Pode vir como lista ou dict
    if isinstance(servings, list):
        serving = servings[0]
    else:
        serving = servings

    return {
        "calorias": serving.get("calories"),
        "proteina": serving.get("protein"),
        "carboidrato": serving.get("carbohydrate"),
        "gordura": serving.get("fat"),
        "porcao": serving.get("serving_description"),
        "tamanho_porção": serving.get("metric_serving_amount"),
        "unidade": serving.get("metric_serving_unit")
    }

def analyze_food_nutrition(food_id: int):
    """
    Analisa a composição nutricional resumida do alimento.
    """
    nutrientes = get_nutrients_by_food_id(food_id)
    return {
        "Calorias": f"{nutrientes['calorias']} kcal",
        "Proteínas": f"{nutrientes['proteina']} g",
        "Carboidratos": f"{nutrientes['carboidrato']} g",
        "Gorduras": f"{nutrientes['gordura']} g",
        "Porção": nutrientes['porcao']
    }

def compare_foods(food_id1: int, food_id2: int):
    """
    Compara dois alimentos pelos seus nutrientes principais.
    """
    n1 = get_nutrients_by_food_id(food_id1)
    n2 = get_nutrients_by_food_id(food_id2)

    return {
        "alimento_1": n1,
        "alimento_2": n2
    }
