"""
Serviço de API de Nutrição - Integração exclusiva com USDA FoodData Central
Usa apenas a API oficial do USDA para dados nutricionais precisos
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class FoodData:
    """Estrutura padronizada para dados de alimentos"""
    name: str
    calories_per_100g: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    sugar_g: float
    saturated_fat_g: float
    source: str
    description: str = ""

class NutritionAPI:
    """Serviço de API de nutrição usando exclusivamente USDA FoodData Central"""
    
    def __init__(self):
        # API USDA FoodData Central (oficial e gratuita)
        self.usda_api_key = os.getenv('USDA_API_KEY', 'DEMO_KEY')
        
        # Base URL
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"
        
        # Cache local para reduzir chamadas de API
        self.food_cache = {}
        
        logger.info(f"API USDA inicializada com chave: {self.usda_api_key[:10]}...")
    
    def search_food(self, food_name: str) -> Optional[FoodData]:
        """Busca dados de um alimento usando exclusivamente a API USDA"""
        try:
            # 1. Verificar cache local
            cache_key = food_name.lower().strip()
            if cache_key in self.food_cache:
                logger.info(f"Alimento '{food_name}' encontrado no cache")
                return self.food_cache[cache_key]
            
            # 2. Buscar na API USDA FoodData Central
            usda_result = self._search_usda_api(food_name)
            if usda_result:
                logger.info(f"Alimento '{food_name}' encontrado na API USDA")
                self.food_cache[cache_key] = usda_result
                return usda_result
            
            logger.warning(f"Alimento '{food_name}' não encontrado na API USDA")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar alimento '{food_name}': {str(e)}")
            return None
    
    def _search_usda_api(self, food_name: str) -> Optional[FoodData]:
        """Busca na API do USDA FoodData Central"""
        try:
            # Buscar alimentos
            search_url = f"{self.usda_base_url}/foods/search"
            params = {
                'query': food_name,
                'api_key': self.usda_api_key,
                'pageSize': 5,
                'dataType': ['Foundation', 'SR Legacy']
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            foods = data.get('foods', [])
            
            if not foods:
                return None
            
            # Pegar o primeiro resultado mais relevante
            food = foods[0]
            food_nutrients = food.get('foodNutrients', [])
            
            # Extrair nutrientes principais
            nutrients = {}
            for nutrient in food_nutrients:
                nutrient_name = nutrient.get('nutrientName', '').lower()
                nutrient_value = nutrient.get('value', 0)
                
                if 'energy' in nutrient_name or 'calorie' in nutrient_name:
                    nutrients['calories'] = nutrient_value
                elif 'protein' in nutrient_name:
                    nutrients['protein'] = nutrient_value
                elif 'carbohydrate' in nutrient_name and 'by difference' in nutrient_name:
                    nutrients['carbs'] = nutrient_value
                elif 'fat' in nutrient_name and 'total' in nutrient_name:
                    nutrients['fat'] = nutrient_value
                elif 'fiber' in nutrient_name:
                    nutrients['fiber'] = nutrient_value
                elif 'sodium' in nutrient_name:
                    nutrients['sodium'] = nutrient_value
                elif 'sugar' in nutrient_name and 'total' in nutrient_name:
                    nutrients['sugar'] = nutrient_value
                elif 'saturated' in nutrient_name:
                    nutrients['saturated_fat'] = nutrient_value
            
            return FoodData(
                name=food.get('description', food_name),
                calories_per_100g=nutrients.get('calories', 0),
                protein_g=nutrients.get('protein', 0),
                carbs_g=nutrients.get('carbs', 0),
                fat_g=nutrients.get('fat', 0),
                fiber_g=nutrients.get('fiber', 0),
                sodium_mg=nutrients.get('sodium', 0),
                sugar_g=nutrients.get('sugar', 0),
                saturated_fat_g=nutrients.get('saturated_fat', 0),
                source="USDA_API",
                description=f"Dados da API USDA FoodData Central"
            )
            
        except Exception as e:
            logger.error(f"Erro na API USDA para '{food_name}': {str(e)}")
            return None
    
    def get_multiple_foods(self, food_list: List[str]) -> Dict[str, FoodData]:
        """Busca dados de múltiplos alimentos"""
        results = {}
        for food_name in food_list:
            food_data = self.search_food(food_name)
            if food_data:
                results[food_name] = food_data
        return results
    
    def calculate_meal_nutrition(self, meal_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula nutrição total de uma refeição
        meal_items: Lista de {'food': nome_do_alimento, 'quantity_g': quantidade_em_gramas}
        """
        total_nutrition = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
            'sodium_mg': 0,
            'sugar_g': 0,
            'saturated_fat_g': 0
        }
        
        for item in meal_items:
            food_name = item.get('food', '')
            quantity_g = item.get('quantity_g', 0)
            
            food_data = self.search_food(food_name)
            if food_data:
                # Calcular proporção (quantidade / 100g)
                proportion = quantity_g / 100.0
                
                total_nutrition['calories'] += food_data.calories_per_100g * proportion
                total_nutrition['protein_g'] += food_data.protein_g * proportion
                total_nutrition['carbs_g'] += food_data.carbs_g * proportion
                total_nutrition['fat_g'] += food_data.fat_g * proportion
                total_nutrition['fiber_g'] += food_data.fiber_g * proportion
                total_nutrition['sodium_mg'] += food_data.sodium_mg * proportion
                total_nutrition['sugar_g'] += food_data.sugar_g * proportion
                total_nutrition['saturated_fat_g'] += food_data.saturated_fat_g * proportion
        
        return total_nutrition
    
    def suggest_food_alternatives(self, original_food: str, target_macros: Dict[str, float]) -> List[FoodData]:
        """Sugere alternativas de alimentos baseado em macros desejados"""
        # Esta função pode ser expandida para usar ML ou regras mais sofisticadas
        alternatives = []
        
        # Por enquanto, busca variações do alimento original
        original_data = self.search_food(original_food)
        if not original_data:
            return alternatives
        
        # Buscar variações (ex: "chicken" -> "grilled chicken", "roasted chicken")
        variations = [
            f"grilled {original_food}",
            f"roasted {original_food}",
            f"baked {original_food}",
            f"steamed {original_food}",
            f"fresh {original_food}"
        ]
        
        for variation in variations:
            alt_data = self.search_food(variation)
            if alt_data and alt_data.name != original_data.name:
                alternatives.append(alt_data)
        
        return alternatives[:3]  # Retornar até 3 alternativas

# Instância global do serviço
nutrition_service = NutritionAPI()

def get_food_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
    """Função helper para buscar nutrição de um alimento"""
    food_data = nutrition_service.search_food(food_name)
    if food_data:
        return {
            'name': food_data.name,
            'calories_per_100g': food_data.calories_per_100g,
            'protein_g': food_data.protein_g,
            'carbs_g': food_data.carbs_g,
            'fat_g': food_data.fat_g,
            'fiber_g': food_data.fiber_g,
            'sodium_mg': food_data.sodium_mg,
            'sugar_g': food_data.sugar_g,
            'saturated_fat_g': food_data.saturated_fat_g,
            'source': food_data.source,
            'description': food_data.description
        }
    return None
