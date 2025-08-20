"""
Serviço de API de Nutrição - Integração exclusiva com USDA FoodData Central
Sem fallbacks - falha se API não estiver disponível
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import time

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class FoodData:
    """Estrutura padronizada para dados de alimentos da USDA"""
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
    fdc_id: Optional[str] = None
    description: str = ""

class USDAAPIError(Exception):
    """Exceção específica para erros da API USDA"""
    pass

class NutritionAPI:
    """Serviço de nutrição usando exclusivamente USDA FoodData Central - sem fallbacks"""
    
    def __init__(self):
        # API USDA FoodData Central
        self.usda_api_key = os.getenv('USDA_API_KEY')
        if not self.usda_api_key:
            raise ValueError("USDA_API_KEY não encontrada no arquivo .env")
        
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"
        
        # Configurações de request
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 1  # segundos
        
        logger.info(f"NutritionAPI inicializada com chave USDA: {self.usda_api_key[:10]}...")
    
    def search_food(self, food_name: str) -> Optional[FoodData]:
        """
        Busca dados de um alimento na API USDA
        Retorna None se não encontrar, levanta exceção se API falhar
        """
        if not food_name or not food_name.strip():
            raise ValueError("Nome do alimento não pode estar vazio")
        
        food_name = food_name.strip().lower()
        
        for attempt in range(self.max_retries):
            try:
                return self._search_usda_with_retry(food_name, attempt + 1)
            except USDAAPIError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Falha final na busca de '{food_name}' após {self.max_retries} tentativas: {e}")
                    raise
                else:
                    logger.warning(f"Tentativa {attempt + 1} falhou para '{food_name}': {e}")
                    time.sleep(self.retry_delay * (attempt + 1))
        
        return None
    
    def _search_usda_with_retry(self, food_name: str, attempt: int) -> Optional[FoodData]:
        """Executa busca na API USDA com retry logic"""
        try:
            # Buscar alimentos
            search_url = f"{self.usda_base_url}/foods/search"
            params = {
                'query': food_name,
                'api_key': self.usda_api_key,
                'pageSize': 5,
                'dataType': ['Foundation', 'SR Legacy'],
                'sortBy': 'score',
                'sortOrder': 'desc'
            }
            
            logger.debug(f"Buscando '{food_name}' na USDA API (tentativa {attempt})")
            
            response = requests.get(search_url, params=params, timeout=self.timeout)
            
            # Verificar resposta HTTP
            if response.status_code == 429:
                raise USDAAPIError(f"Rate limit da API USDA atingido")
            elif response.status_code == 401:
                raise USDAAPIError(f"Chave de API USDA inválida")
            elif response.status_code == 503:
                raise USDAAPIError(f"API USDA temporariamente indisponível")
            elif not response.ok:
                raise USDAAPIError(f"Erro HTTP {response.status_code}: {response.text}")
            
            # Parse da resposta
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise USDAAPIError(f"Resposta JSON inválida da API USDA: {e}")
            
            foods = data.get('foods', [])
            if not foods:
                logger.info(f"Alimento '{food_name}' não encontrado na API USDA")
                return None
            
            # Processar primeiro resultado (mais relevante)
            food = foods[0]
            return self._parse_food_data(food, food_name)
            
        except requests.exceptions.Timeout:
            raise USDAAPIError(f"Timeout na conexão com API USDA")
        except requests.exceptions.ConnectionError:
            raise USDAAPIError(f"Erro de conexão com API USDA")
        except requests.exceptions.RequestException as e:
            raise USDAAPIError(f"Erro na requisição para API USDA: {e}")
    
    def _parse_food_data(self, food_data: Dict[str, Any], original_query: str) -> FoodData:
        """Extrai e valida dados nutricionais do resultado da API USDA"""
        try:
            food_nutrients = food_data.get('foodNutrients', [])
            
            # Mapeamento de nutrientes USDA
            nutrient_map = {
                'energy': ['energy', 'calories', 'kilocalories'],
                'protein': ['protein'],
                'carbs': ['carbohydrate', 'total carbohydrate'],
                'fat': ['total lipid', 'fat', 'total fat'],
                'fiber': ['fiber', 'dietary fiber'],
                'sodium': ['sodium'],
                'sugar': ['sugars', 'total sugars'],
                'saturated_fat': ['saturated', 'saturated fat']
            }
            
            # Extrair nutrientes
            nutrients = {}
            energy_kcal_value = None
            for nutrient in food_nutrients:
                nutrient_name = nutrient.get('nutrientName', '').lower()
                nutrient_value = nutrient.get('value', 0)
                unit_name = (nutrient.get('unitName') or '').lower()
                
                # Mapear nutriente
                for key, keywords in nutrient_map.items():
                    if any(keyword in nutrient_name for keyword in keywords):
                        # Energia pode aparecer em kcal e kJ -> priorizar kcal
                        if key == 'energy':
                            try:
                                if 'kj' in unit_name:
                                    candidate = float(nutrient_value) / 4.184  # converter kJ -> kcal
                                else:
                                    candidate = float(nutrient_value)
                            except Exception:
                                candidate = float(nutrient_value) or 0.0
                            # Prioriza primeiro valor em kcal; se ainda não definido, aceita o convertido
                            if energy_kcal_value is None or ('kj' not in unit_name):
                                energy_kcal_value = candidate
                        else:
                            if key not in nutrients:  # Pegar primeira ocorrência
                                nutrients[key] = nutrient_value
                        break
            
            # Ajustar energia calculada e validar dados essenciais
            if energy_kcal_value is None:
                logger.warning(f"Nutriente 'energy' não encontrado para '{original_query}'")
                energy_kcal_value = 0.0
            required_nutrients = ['protein', 'carbs', 'fat']
            for nutrient in required_nutrients:
                if nutrient not in nutrients:
                    logger.warning(f"Nutriente '{nutrient}' não encontrado para '{original_query}'")
                    nutrients[nutrient] = 0.0
            
            # Criar objeto FoodData
            food_data_obj = FoodData(
                name=food_data.get('description', original_query),
                calories_per_100g=float(energy_kcal_value),
                protein_g=float(nutrients.get('protein', 0)),
                carbs_g=float(nutrients.get('carbs', 0)),
                fat_g=float(nutrients.get('fat', 0)),
                fiber_g=float(nutrients.get('fiber', 0)),
                sodium_mg=float(nutrients.get('sodium', 0)),
                sugar_g=float(nutrients.get('sugar', 0)),
                saturated_fat_g=float(nutrients.get('saturated_fat', 0)),
                source="USDA_API",
                fdc_id=str(food_data.get('fdcId', '')),
                description=f"Dados da API USDA FoodData Central (FDC ID: {food_data.get('fdcId', 'N/A')})"
            )
            
            logger.info(f"✅ Dados extraídos para '{original_query}': {food_data_obj.calories_per_100g} kcal/100g")
            
            return food_data_obj
            
        except Exception as e:
            raise USDAAPIError(f"Erro ao processar dados nutricionais para '{original_query}': {e}")
    
    def get_multiple_foods(self, food_list: List[str]) -> Dict[str, FoodData]:
        """
        Busca dados de múltiplos alimentos
        Falha se qualquer alimento não for encontrado
        """
        if not food_list:
            raise ValueError("Lista de alimentos não pode estar vazia")
        
        results = {}
        failed_foods = []
        
        logger.info(f"Buscando dados para {len(food_list)} alimentos na API USDA")
        
        for food_name in food_list:
            try:
                food_data = self.search_food(food_name)
                if food_data:
                    results[food_name] = food_data
                else:
                    failed_foods.append(food_name)
            except USDAAPIError as e:
                logger.error(f"Erro ao buscar '{food_name}': {e}")
                failed_foods.append(food_name)
        
        if failed_foods:
            raise USDAAPIError(
                f"Falha ao obter dados para {len(failed_foods)} alimentos: {failed_foods}. "
                f"Total obtidos: {len(results)}/{len(food_list)}"
            )
        
        logger.info(f"✅ Dados obtidos para todos os {len(results)} alimentos solicitados")
        return results
    
    def calculate_meal_nutrition(self, meal_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula nutrição total de uma refeição
        meal_items: Lista de {'food': nome_do_alimento, 'quantity_g': quantidade_em_gramas}
        """
        if not meal_items:
            raise ValueError("Lista de itens da refeição não pode estar vazia")
        
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
            
            if not food_name or quantity_g <= 0:
                raise ValueError(f"Item inválido na refeição: {item}")
            
            # Buscar dados do alimento
            food_data = self.search_food(food_name)
            if not food_data:
                raise USDAAPIError(f"Dados nutricionais não encontrados para '{food_name}'")
            
            # Calcular proporção (quantidade / 100g)
            proportion = quantity_g / 100.0
            
            # Calcular valores proporcionais
            total_nutrition['calories'] += food_data.calories_per_100g * proportion
            total_nutrition['protein_g'] += food_data.protein_g * proportion
            total_nutrition['carbs_g'] += food_data.carbs_g * proportion
            total_nutrition['fat_g'] += food_data.fat_g * proportion
            total_nutrition['fiber_g'] += food_data.fiber_g * proportion
            total_nutrition['sodium_mg'] += food_data.sodium_mg * proportion
            total_nutrition['sugar_g'] += food_data.sugar_g * proportion
            total_nutrition['saturated_fat_g'] += food_data.saturated_fat_g * proportion
        
        # Arredondar valores
        for key in total_nutrition:
            total_nutrition[key] = round(total_nutrition[key], 2)
        
        return total_nutrition
    
    def validate_api_connection(self) -> bool:
        """
        Valida se a API USDA está funcionando
        Levanta exceção se não conseguir conectar
        """
        try:
            # Teste simples com alimento comum
            test_result = self.search_food("banana")
            if test_result:
                logger.info("✅ Conexão com API USDA validada com sucesso")
                return True
            else:
                raise USDAAPIError("API USDA conectou mas não retornou dados para teste")
        except Exception as e:
            raise USDAAPIError(f"Falha na validação da API USDA: {e}")
    
    def get_api_status(self) -> Dict[str, Any]:
        """Retorna status atual da API"""
        try:
            self.validate_api_connection()
            return {
                'status': 'operational',
                'base_url': self.usda_base_url,
                'api_key_configured': bool(self.usda_api_key),
                'last_check': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'base_url': self.usda_base_url,
                'api_key_configured': bool(self.usda_api_key),
                'last_check': time.time()
            }


# Instância global do serviço
nutrition_service = NutritionAPI()

def get_food_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
    """Função helper para buscar nutrição de um alimento"""
    try:
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
                'fdc_id': food_data.fdc_id,
                'description': food_data.description
            }
        return None
    except USDAAPIError as e:
        logger.error(f"Erro ao buscar nutrição para '{food_name}': {e}")
        raise