"""
Nutritionist Agent - Sistema baseado em YAML e APIs reais de nutrição
"""

from typing import Dict, Any, List, Optional
import logging
import json
import time
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.core import BaseAgent, AgentConfig, AgentState, AgentType, TaskType
from core.config_loader import get_config_loader
from utils.nutrition_api import NutritionAPI
from utils.pdf_generator import create_diet_pdf
from utils.diet_manager.diet_storage import DietManager

logger = logging.getLogger(__name__)


class NutritionistAgent(BaseAgent):
    """Agente nutricionista baseado em configurações YAML e context prompts científicos"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config_loader = get_config_loader()
            config = config_loader.load_agent_config(AgentType.NUTRITIONIST)
        
        super().__init__(config)
        
        # Inicializar API de nutrição USDA
        self.nutrition_api = NutritionAPI()
        
        # Inicializar gerenciador de dietas
        self.diet_manager = DietManager()
        
        # Context prompts científicos disponíveis diretamente do config YAML
        self.available_contexts = config.contexts
    
    def process_message(self, state: AgentState) -> AgentState:
        """Processa mensagem usando consulta estruturada para nutricionista"""
        try:
            # 1. Verificar se já tem consulta ativa
            consultation_state = state.get('consultation_state')
            user_message = state['messages'][-1].content if state['messages'] else ""
            
            # 2. Se não tem consulta ativa, iniciar uma nova
            if not consultation_state:
                user_data = state.get('user_profile', {})
                consultation_state = self.start_structured_consultation(user_data)
                state['consultation_state'] = consultation_state
            
            # 3. Continuar consulta estruturada
            consultation_result = self.continue_structured_consultation(consultation_state, user_message)
            
            # 4. Atualizar estado principal com resultado da consulta
            state['consultation_state'] = consultation_result
            
            # 5. Criar mensagem de resposta
            if consultation_result.get('last_response_content'):
                response = AIMessage(content=consultation_result['last_response_content'])
                state['messages'].append(response)
            
            # 6. Transferir informações importantes para o estado principal
            state['confidence_score'] = 0.9
            state['show_option_buttons'] = consultation_result.get('show_option_buttons', False)
            state['is_decision_point'] = consultation_result.get('is_decision_point', False)
            state['current_phase'] = consultation_result.get('current_phase', '')
            state['diet_generated'] = consultation_result.get('diet_generated', False)
            state['tools_used'] = ['structured_consultation']
            
            return state
            
        except Exception as e:
            logger.error(f"Error in NutritionistAgent.process_message: {str(e)}")
            return self._handle_error(state, str(e))
    
    def _determine_task_type(self, state: AgentState) -> str:
        """Determina tipo de task baseado na configuraÃ§Ã£o YAML e mensagem do usuÃ¡rio"""
        try:
            # Buscar configuraÃ§Ã£o de keywords do YAML - sem fallback
            task_keywords = self.config.task_keywords
            if not task_keywords:
                raise ValueError("ConfiguraÃ§Ã£o task_keywords nÃ£o encontrada no YAML")
            
            if not state.get('messages'):
                return 'consultation'
            
            user_message = state['messages'][-1].content.lower()
            
            # Calcular scores para cada tipo de task
            task_scores = {}
            for task_type, keywords in task_keywords.items():
                score = sum(1 for keyword in keywords if keyword in user_message)
                task_scores[task_type] = score
            
            # Retornar task type com maior score ou default
            best_task = max(task_scores, key=task_scores.get, default='consultation')
            return best_task if task_scores[best_task] > 0 else 'consultation'
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao determinar task type: {str(e)}")
            raise RuntimeError(f"Falha na determinaÃ§Ã£o do tipo de tarefa: {str(e)}") from e
    
    def _get_required_contexts(self, task_type: str) -> List[str]:
        """Busca contexts necessÃ¡rios da configuraÃ§Ã£o YAML"""
        try:
            # Mapear task types para contexts - sem fallback
            context_mapping = self.config.context_mapping
            if not context_mapping:
                raise ValueError("ConfiguraÃ§Ã£o context_mapping nÃ£o encontrada no YAML")
            
            contexts = context_mapping.get(task_type)
            if contexts is None:
                raise ValueError(f"Task type '{task_type}' nÃ£o encontrado na configuraÃ§Ã£o context_mapping")
            
            return contexts
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao buscar contexts necessÃ¡rios: {str(e)}")
            raise RuntimeError(f"Falha na busca de contexts para task '{task_type}': {str(e)}") from e
    
    def _calculate_confidence(self, task_type: str) -> float:
        """Calcula confianÃ§a baseado no tipo de task"""
        try:
            confidence_scores = self.config.confidence_scores
            if not confidence_scores:
                raise ValueError("ConfiguraÃ§Ã£o confidence_scores nÃ£o encontrada no YAML")
            
            confidence = confidence_scores.get(task_type)
            if confidence is None:
                raise ValueError(f"Confidence score para task '{task_type}' nÃ£o encontrado na configuraÃ§Ã£o")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao calcular confidence: {str(e)}")
            raise RuntimeError(f"Falha no cÃ¡lculo de confianÃ§a para task '{task_type}': {str(e)}") from e
    
    def _handle_error(self, state: AgentState, error_message: str) -> AgentState:
        """Manipula erros baseado na configuraÃ§Ã£o YAML - sem fallbacks"""
        try:
            # Buscar mensagens de erro da configuraÃ§Ã£o YAML
            error_responses = self.config.error_responses
            if not error_responses:
                raise ValueError("ConfiguraÃ§Ã£o de error_responses nÃ£o encontrada no YAML")
            
            error_response = AIMessage(content=error_responses.get('default'))
            state['messages'].append(error_response)
            state['confidence_score'] = 0.0
            state['error'] = error_message
            
            logger.error(f"Erro tratado no agente nutricionista: {error_message}")
            return state
            
        except Exception as config_error:
            # Se atÃ© o tratamento de erro falha, propagar erro crÃ­tico
            logger.critical(f"Falha crÃ­tica no tratamento de erro: {config_error}")
            raise RuntimeError(f"Sistema de erro falhou: {config_error}") from config_error

    def start_structured_consultation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia consulta estruturada baseada nos dados do usuÃ¡rio"""
        try:
            # Criar estado inicial (apenas dados serializÃ¡veis)
            initial_state = {
                'user_data': user_data,
                'conversation_history': [],
                'current_phase': 'greeting',
                'collected_data': {},
                'consultation_id': f"consultation_{user_data.get('user_id', 'unknown')}_{int(time.time())}",
                'created_at': datetime.now().isoformat(),
                'ready_for_summary': False
            }
            
            # Gerar mensagem inicial usando configuração do YAML
            context_prompt = f"""
            {self.config.system_prompt}
            
            Dados do usuário: {user_data}
            Fase: greeting
            Comando: consultation_handler
            """
            
            # Usar LLM para gerar saudação inicial
            response = self.llm.invoke([SystemMessage(content=context_prompt)])
            
            # Adicionar primeira mensagem ao histÃ³rico (somente dados serializÃ¡veis)
            initial_state['conversation_history'].append({
                'role': 'assistant',
                'message': response.content,
                'timestamp': datetime.now().isoformat()
            })
            
            # NÃ£o adicionar objetos AIMessage ao estado - apenas conteÃºdo serializÃ¡vel
            initial_state['last_response_content'] = response.content
            
            return initial_state
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao inicializar consulta estruturada: {str(e)}")
            # Propagar o erro em vez de fallback
            raise RuntimeError(f"Falha na inicializaÃ§Ã£o da consulta: {str(e)}") from e

    def continue_structured_consultation(self, consultation_state: Dict[str, Any], user_response: str) -> Dict[str, Any]:
        """Continua a consulta estruturada com a resposta do usuÃ¡rio"""
        try:
            # Adicionar resposta do usuÃ¡rio ao histÃ³rico
            consultation_state['conversation_history'].append({
                'role': 'user', 
                'message': user_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Verificar se o usuário quer gerar a dieta final (PDF)
            if 'gerar' in user_response.lower() and 'dieta' in user_response.lower():
                return self._handle_final_diet_generation(consultation_state)
            
            # Construir contexto da conversa para o LLM
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['message']}" 
                for msg in consultation_state['conversation_history']
            ])
            
            # Preparar prompt para continuação usando configuração do YAML
            continuation_prompt = f"""
            {self.config.system_prompt}
            
            Dados do usuário: {consultation_state.get('user_data', {})}
            Fase atual: {consultation_state.get('current_phase', 'consultation')}
            
            Histórico da conversa:
            {conversation_context}
            
            Comando: consultation_handler
            """
            
            # Gerar resposta do agente
            response = self.llm.invoke([SystemMessage(content=continuation_prompt)])
            
            # Adicionar resposta ao histÃ³rico
            consultation_state['conversation_history'].append({
                'role': 'assistant',
                'message': response.content,
                'timestamp': datetime.now().isoformat()
            })
            
            # Atualizar campos serializÃ¡veis
            consultation_state['last_response_content'] = response.content
            consultation_state['updated_at'] = datetime.now().isoformat()
            
            # Verificar se estÃ¡ em ponto de decisÃ£o baseado no estado da conversa
            conversation_length = len(consultation_state['conversation_history'])
            last_messages = [msg['message'].lower() for msg in consultation_state['conversation_history'][-4:] if msg['role'] == 'user']
            
            # Verificar se coletou informaÃ§Ãµes suficientes
            has_routine_info = any('refeiÃ§Ã£o' in msg or 'como' in msg or 'cafÃ©' in msg or 'almoÃ§o' in msg for msg in last_messages)
            has_preference_info = any('gosta' in msg or 'fruta' in msg or 'verdura' in msg for msg in last_messages)
            has_context_info = any('tempo' in msg or 'rotina' in msg or 'desafio' in msg for msg in last_messages)
            
            # Determinar fase atual baseado no conteÃºdo
            if conversation_length > 10 and has_routine_info and has_preference_info and has_context_info:
                consultation_state['current_phase'] = 'diet_preview_generation'
                consultation_state['ready_for_diet_preview'] = True
                
                # Se chegou na fase de preview da dieta, gerar preview completo
                if consultation_state.get('ready_for_diet_preview', False):
                    # Gerar preview da dieta com dados reais da API
                    diet_preview = self._generate_diet_preview(consultation_state)
                    consultation_state['diet_preview'] = diet_preview
                    
                    # Gerar resposta mostrando a dieta completa
                    response_content = self._format_diet_preview_response(diet_preview)
                    
                    # Substituir a última resposta com o preview da dieta
                    consultation_state['conversation_history'][-1] = {
                        'role': 'assistant',
                        'message': response_content,
                        'timestamp': datetime.now().isoformat()
                    }
                    consultation_state['last_response_content'] = response_content
                    consultation_state['show_diet_action_buttons'] = True
                    
            elif conversation_length > 6 and has_routine_info and not has_preference_info:
                consultation_state['current_phase'] = 'food_preferences_mapping'
            elif conversation_length > 4 and not has_routine_info:
                consultation_state['current_phase'] = 'eating_routine_assessment'
            
            return consultation_state
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao continuar consulta: {str(e)}")
            raise RuntimeError(f"Falha na continuaÃ§Ã£o da consulta: {str(e)}") from e

    def generate_diet_json(self, consultation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Gera JSON estruturado com a dieta seguindo ordem correta: preferências → API → organização → JSON"""
        try:
            logger.info("🍎 Iniciando processo de geração de dieta personalizada...")
            
            # 1. Extrair dados básicos da consulta
            user_data = consultation_state.get('user_data', {})
            conversation_history = consultation_state.get('conversation_history', [])
            
            # 2. LLM calcula TMB e necessidades nutricionais baseado no contexto
            nutritional_calculations = self._llm_calculate_nutritional_needs(user_data, conversation_history)
            
            # Separar dados antropométricos dos cálculos
            anthropometric_data = nutritional_calculations.get('anthropometric_data', {})
            tmb_calculations = {k: v for k, v in nutritional_calculations.items() if k != 'anthropometric_data'}
            
            logger.info(f"📊 LLM calculou TMB: {tmb_calculations.get('tmb_kcal')} kcal | Meta diária: {tmb_calculations.get('daily_target_kcal')} kcal")
            
            # 3. Extrair preferências alimentares do usuário
            user_food_preferences = self._extract_food_preferences_from_conversation(conversation_history)
            
            # 4. LLM seleciona grupos de alimentos baseado nas preferências
            selected_food_groups = self._llm_select_food_groups(user_food_preferences, tmb_calculations, conversation_history)
            
            logger.info(f"🥗 LLM selecionou {len(selected_food_groups)} grupos alimentares")
            
            # 5. Buscar dados nutricionais na API USDA para alimentos selecionados
            nutritional_database = self._fetch_nutrition_data_for_selected_foods(selected_food_groups)
            
            logger.info(f"🔍 Dados nutricionais obtidos para {len(nutritional_database)} alimentos via USDA API")
            
            # 6. Organizar dados em estrutura de dieta
            structured_diet = self._organize_diet_structure(
                anthropometric_data, 
                tmb_calculations, 
                nutritional_database, 
                user_food_preferences,
                conversation_history
            )
            
            logger.info("✅ Dieta estruturada com sucesso - pronta para PDF")
            
            return structured_diet
                
        except Exception as e:
            logger.error(f"Erro crítico ao gerar JSON da dieta: {str(e)}")
            raise RuntimeError(f"Falha na geração do JSON da dieta: {str(e)}") from e

    def _llm_select_food_groups(self, user_preferences: Dict[str, Any], tmb_calculations: Dict[str, Any], conversation_history: List[Dict[str, Any]]) -> List[str]:
        """LLM seleciona grupos de alimentos baseado nas preferências do usuário e necessidades nutricionais"""
        try:
            # Preparar contexto da conversa
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['message']}" 
                for msg in conversation_history
            ])
            
            # Contexto completo para LLM
            context_data = {
                'user_preferences': user_preferences,
                'nutritional_needs': tmb_calculations,
                'conversation_history': conversation_context
            }
            
            # Prompt limpo - apenas contexto
            selection_prompt = f"""
            {self.config.system_prompt}
            
            CONTEXTO ATUAL:
            {json.dumps(context_data, indent=2, ensure_ascii=False)}
            
            Comando: food_selection_handler
            """
            
            # Invocar LLM
            response = self.llm.invoke([SystemMessage(content=selection_prompt)])
            
            # Parsear resposta
            try:
                selected_foods = json.loads(response.content.strip())
                if isinstance(selected_foods, list):
                    logger.info(f"✅ LLM selecionou {len(selected_foods)} alimentos")
                    return selected_foods
                else:
                    raise ValueError("Resposta não é uma lista")
            except (json.JSONDecodeError, ValueError):
                # Tentar extrair JSON do texto
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                selected_foods = json.loads(content.strip())
                return selected_foods
                
        except Exception as e:
            logger.error(f"Erro na seleção de alimentos pela LLM: {e}")
            # SEM FALLBACK - propagar erro
            raise RuntimeError(f"Falha na seleção de alimentos: {str(e)}") from e

    def _fetch_nutrition_data_for_selected_foods(self, selected_foods: List[str]) -> Dict[str, Any]:
        """Busca dados nutricionais na API USDA para os alimentos selecionados"""
        try:
            logger.info(f"🔍 Buscando dados nutricionais para {len(selected_foods)} alimentos na API USDA...")
            
            nutrition_database = {}
            successful_searches = 0
            failed_searches = []
            
            for food_name in selected_foods:
                try:
                    food_data = self.nutrition_api.search_food(food_name)
                    if food_data:
                        nutrition_database[food_name] = {
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
                        successful_searches += 1
                        logger.info(f"✅ {food_name}: {food_data.calories_per_100g} kcal/100g")
                    else:
                        failed_searches.append(food_name)
                        logger.warning(f"❌ Dados não encontrados: {food_name}")
                        
                except Exception as e:
                    failed_searches.append(food_name)
                    logger.error(f"❌ Erro ao buscar {food_name}: {str(e)}")
            
            logger.info(f"📊 API USDA: {successful_searches} sucessos, {len(failed_searches)} falhas")
            
            if failed_searches:
                logger.warning(f"Alimentos não encontrados: {failed_searches}")
            
            return nutrition_database
            
        except Exception as e:
            logger.error(f"Erro crítico ao buscar dados nutricionais: {str(e)}")
            return {}

    def _organize_diet_structure(self, anthropometric_data: Dict[str, Any], tmb_calculations: Dict[str, Any], 
                               nutritional_database: Dict[str, Any], user_preferences: Dict[str, Any],
                               conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Organiza todos os dados em uma estrutura de dieta completa para PDF"""
        try:
            logger.info("📋 Organizando estrutura final da dieta...")
            
            # Extrair nome do usuário
            user_name = anthropometric_data.get('name') or 'Paciente'
            if not user_name or user_name == 'Paciente':
                # Tentar extrair do histórico da conversa
                for msg in conversation_history:
                    if msg['role'] == 'user' and ('me chamo' in msg['message'].lower() or 'meu nome' in msg['message'].lower()):
                        # Extrair nome da mensagem
                        words = msg['message'].split()
                        for i, word in enumerate(words):
                            if word.lower() in ['chamo', 'nome'] and i + 1 < len(words):
                                user_name = words[i + 1].replace(',', '').replace('.', '')
                                break
                        break
            
            # Estrutura completa da dieta
            diet_structure = {
                'generated_at': datetime.now().isoformat(),
                'diet_id': f"diet_{int(time.time())}",
                
                # Informações do paciente
                'patient_info': {
                    'name': user_name,
                    'age': anthropometric_data.get('age_years', 'Não informado'),
                    'gender': anthropometric_data.get('gender', 'Não informado'),
                    'weight_kg': anthropometric_data.get('weight_kg', 'Não informado'),
                    'height_cm': anthropometric_data.get('height_cm', 'Não informado'),
                    'activity_level': anthropometric_data.get('activity_level', 'Moderadamente ativo'),
                    'primary_objective': anthropometric_data.get('primary_objective', 'Manutenção')
                },
                
                # Cálculos nutricionais
                'nutritional_calculations': {
                    'tmb_kcal': tmb_calculations.get('tmb_kcal', 1800),
                    'daily_target_kcal': tmb_calculations.get('daily_target_kcal', 2200),
                    'objective_adjustment': tmb_calculations.get('objective_adjustment', 'Manutenção'),
                    'macronutrients': tmb_calculations.get('macronutrient_distribution', {}),
                    'activity_factor': tmb_calculations.get('activity_factor', 1.55)
                },
                
                # Menu semanal organizado
                'weekly_menu': self._create_weekly_menu(nutritional_database, tmb_calculations),
                
                # Dados da API USDA
                'nutrition_data_source': {
                    'primary_source': 'USDA FoodData Central API',
                    'foods_analyzed': len(nutritional_database),
                    'api_status': 'Dados coletados em tempo real',
                    'last_updated': datetime.now().isoformat()
                },
                
                # Banco de dados nutricional completo
                'nutritional_database': nutritional_database
            }
            
            logger.info("✅ Estrutura da dieta organizada com sucesso")
            return diet_structure
            
        except Exception as e:
            logger.error(f"Erro ao organizar estrutura da dieta: {str(e)}")
            raise RuntimeError(f"Falha na organização da dieta: {str(e)}") from e

    def _create_weekly_menu(self, nutritional_database: Dict[str, Any], tmb_calculations: Dict[str, Any]) -> Dict[str, Any]:
        """Cria menu semanal baseado nos alimentos disponíveis"""
        try:
            daily_kcal = tmb_calculations.get('daily_target_kcal', 2200)
            
            # Distribuição de calorias por refeição
            meal_distribution = {
                'breakfast': 0.25,    # 25%
                'morning_snack': 0.10, # 10%
                'lunch': 0.35,        # 35%
                'afternoon_snack': 0.10, # 10%
                'dinner': 0.20        # 20%
            }
            
            # Categorizar alimentos
            food_categories = {
                'proteins': [],
                'carbohydrates': [],
                'vegetables': [],
                'fruits': [],
                'dairy': [],
                'fats': []
            }
            
            for food_name, food_data in nutritional_database.items():
                protein_ratio = food_data.get('protein_g', 0) / 100
                carb_ratio = food_data.get('carbs_g', 0) / 100
                
                if protein_ratio > 0.15:  # >15% proteína
                    food_categories['proteins'].append(food_name)
                elif carb_ratio > 0.20:   # >20% carboidrato
                    food_categories['carbohydrates'].append(food_name)
                elif 'milk' in food_name or 'yogurt' in food_name:
                    food_categories['dairy'].append(food_name)
                elif any(fruit in food_name for fruit in ['apple', 'banana', 'orange']):
                    food_categories['fruits'].append(food_name)
                elif any(veg in food_name for veg in ['broccoli', 'spinach', 'tomato']):
                    food_categories['vegetables'].append(food_name)
                else:
                    food_categories['fats'].append(food_name)
            
            # Criar menu para 7 dias
            weekly_menu = {}
            days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            
            for day in days:
                daily_menu = {}
                for meal, percentage in meal_distribution.items():
                    meal_kcal = daily_kcal * percentage
                    daily_menu[meal] = {
                        'target_kcal': round(meal_kcal),
                        'foods': self._select_foods_for_meal(food_categories, meal, meal_kcal)
                    }
                weekly_menu[day] = daily_menu
            
            return weekly_menu
            
        except Exception as e:
            logger.error(f"Erro ao criar menu semanal: {e}")
            return {}

    def _select_foods_for_meal(self, food_categories: Dict[str, List], meal_type: str, target_kcal: float) -> List[Dict[str, Any]]:
        """Seleciona alimentos apropriados para uma refeição específica"""
        try:
            selected_foods = []
            
            if meal_type == 'breakfast':
                # Café da manhã: laticínios, frutas, carboidratos
                if food_categories['dairy']:
                    selected_foods.append({'food': food_categories['dairy'][0], 'portion': '200ml'})
                if food_categories['fruits']:
                    selected_foods.append({'food': food_categories['fruits'][0], 'portion': '1 unidade'})
                if food_categories['carbohydrates']:
                    selected_foods.append({'food': food_categories['carbohydrates'][0], 'portion': '30g'})
                    
            elif meal_type in ['lunch', 'dinner']:
                # Refeições principais: proteína, carboidrato, vegetais
                if food_categories['proteins']:
                    selected_foods.append({'food': food_categories['proteins'][0], 'portion': '150g'})
                if food_categories['carbohydrates']:
                    selected_foods.append({'food': food_categories['carbohydrates'][0], 'portion': '100g'})
                if food_categories['vegetables']:
                    selected_foods.append({'food': food_categories['vegetables'][0], 'portion': '100g'})
                    
            else:  # lanches
                # Lanches: frutas, laticínios
                if food_categories['fruits']:
                    selected_foods.append({'food': food_categories['fruits'][0], 'portion': '1 unidade'})
                if food_categories['dairy']:
                    selected_foods.append({'food': food_categories['dairy'][0], 'portion': '150ml'})
            
            return selected_foods
            
        except Exception as e:
            logger.error(f"Erro ao selecionar alimentos para {meal_type}: {e}")
            return []

    def _extract_food_preferences_from_conversation(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai preferências alimentares da conversa usando LLM"""
        try:
            # Preparar contexto da conversa
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['message']}" 
                for msg in conversation_history
            ])
            
            # Prompt limpo - apenas contexto
            extraction_prompt = f"""
            {self.config.system_prompt}
            
            CONTEXTO ATUAL:
            {conversation_context}
            
            Comando: food_preferences_extraction_handler
            """
            
            # Invocar LLM
            response = self.llm.invoke([SystemMessage(content=extraction_prompt)])
            
            try:
                preferences = json.loads(response.content.strip())
                logger.info(f"Preferências extraídas: {len(preferences.get('liked_foods', []))} alimentos preferidos")
                return preferences
            except json.JSONDecodeError:
                # Tentar extrair JSON do texto
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                preferences = json.loads(content.strip())
                return preferences
            
        except Exception as e:
            logger.error(f"Erro ao extrair preferências alimentares: {str(e)}")
            # SEM FALLBACK - propagar erro  
            raise RuntimeError(f"Falha na extração de preferências: {str(e)}") from e

    def _generate_diet_preview(self, consultation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Gera preview completo da dieta com dados reais da API USDA"""
        try:
            logger.info("🍎 Gerando preview completo da dieta...")
            
            # 1. Extrair dados básicos da consulta
            user_data = consultation_state.get('user_data', {})
            conversation_history = consultation_state.get('conversation_history', [])
            
            # 2. LLM calcula TMB e necessidades nutricionais baseado no contexto
            nutritional_calculations = self._llm_calculate_nutritional_needs(user_data, conversation_history)
            
            # Separar dados antropométricos dos cálculos
            anthropometric_data = nutritional_calculations.get('anthropometric_data', {})
            tmb_calculations = {k: v for k, v in nutritional_calculations.items() if k != 'anthropometric_data'}
            
            logger.info(f"📊 LLM calculou TMB: {tmb_calculations.get('tmb_kcal')} kcal | Meta diária: {tmb_calculations.get('daily_target_kcal')} kcal")
            
            # 3. Extrair preferências alimentares do usuário
            user_food_preferences = self._extract_food_preferences_from_conversation(conversation_history)
            
            # 4. LLM seleciona grupos de alimentos baseado nas preferências
            selected_food_groups = self._llm_select_food_groups(user_food_preferences, tmb_calculations, conversation_history)
            
            logger.info(f"🥗 LLM selecionou {len(selected_food_groups)} grupos alimentares")
            
            # 5. Buscar dados nutricionais na API USDA para alimentos selecionados
            nutritional_database = self._fetch_nutrition_data_for_selected_foods(selected_food_groups)
            
            logger.info(f"🔍 Dados nutricionais obtidos para {len(nutritional_database)} alimentos via USDA API")
            
            # 6. Organizar dados em estrutura de preview
            diet_preview = {
                'anthropometric_data': anthropometric_data,
                'tmb_calculations': tmb_calculations,
                'nutritional_database': nutritional_database,
                'user_food_preferences': user_food_preferences,
                'weekly_menu': self._create_weekly_menu(nutritional_database, tmb_calculations),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("✅ Preview da dieta gerado com sucesso")
            
            return diet_preview
                
        except Exception as e:
            logger.error(f"Erro crítico ao gerar preview da dieta: {str(e)}")
            raise RuntimeError(f"Falha na geração do preview da dieta: {str(e)}") from e

    def _format_diet_preview_response(self, diet_preview: Dict[str, Any]) -> str:
        """Formata o preview da dieta para exibição no chat"""
        try:
            anthropometric = diet_preview['anthropometric_data']
            tmb = diet_preview['tmb_calculations']
            weekly_menu = diet_preview['weekly_menu']
            
            # Construir resposta formatada
            response = f"""🎯 **SUA DIETA PERSONALIZADA ESTÁ PRONTA!**

👤 **SEUS DADOS NUTRICIONAIS:**
• Nome: {anthropometric.get('name', 'Paciente')}
• TMB (Taxa Metabólica Basal): {tmb.get('tmb_kcal', 0):.1f} kcal
• Gasto Energético Total: {tmb.get('get_kcal', 0):.1f} kcal  
• Meta Diária: {tmb.get('daily_target_kcal', 0):.1f} kcal
• Objetivo: {tmb.get('objective_adjustment', 'Manutenção')}

📊 **DISTRIBUIÇÃO DE MACRONUTRIENTES:**
• Carboidratos: {tmb.get('macronutrient_distribution', {}).get('carbohydrates', {}).get('grams_per_day', 0):.1f}g ({tmb.get('macronutrient_distribution', {}).get('carbohydrates', {}).get('kcal_per_day', 0):.0f} kcal)
• Proteínas: {tmb.get('macronutrient_distribution', {}).get('proteins', {}).get('grams_per_day', 0):.1f}g ({tmb.get('macronutrient_distribution', {}).get('proteins', {}).get('kcal_per_day', 0):.0f} kcal)
• Gorduras: {tmb.get('macronutrient_distribution', {}).get('fats', {}).get('grams_per_day', 0):.1f}g ({tmb.get('macronutrient_distribution', {}).get('fats', {}).get('kcal_per_day', 0):.0f} kcal)

🍽️ **EXEMPLO DO SEU CARDÁPIO (Segunda-feira):**"""

            # Adicionar menu de segunda-feira como exemplo
            if 'Segunda' in weekly_menu:
                segunda_menu = weekly_menu['Segunda']
                for meal_name, meal_data in segunda_menu.items():
                    meal_names = {
                        'breakfast': '☀️ Café da Manhã',
                        'morning_snack': '🥤 Lanche da Manhã', 
                        'lunch': '🍽️ Almoço',
                        'afternoon_snack': '🍎 Lanche da Tarde',
                        'dinner': '🌙 Jantar'
                    }
                    
                    response += f"\n\n{meal_names.get(meal_name, meal_name.title())} - Meta: {meal_data.get('target_kcal', 0)} kcal"
                    
                    for food_item in meal_data.get('foods', []):
                        food_name = food_item.get('food', '')
                        portion = food_item.get('portion', '')
                        response += f"\n• {food_name} - {portion}"

            response += f"""

💡 **POR QUE ESSA DIETA FOI CRIADA ASSIM:**
• Baseada no seu TMB calculado cientificamente
• Alimentos selecionados respeitando suas preferências
• Dados nutricionais precisos da API USDA FoodData Central
• Distribuição de macros adequada para seu objetivo
• Cardápio completo para toda a semana

✅ **PRÓXIMOS PASSOS:**
Você pode gerar o PDF completo da sua dieta ou solicitar modificações específicas.

AÇÃO_DIETA_PRONTA"""

            return response
            
        except Exception as e:
            logger.error(f"Erro ao formatar preview da dieta: {str(e)}")
            return "❌ Erro ao formatar a dieta. Tente novamente."

    def _handle_final_diet_generation(self, consultation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Gera a dieta final em PDF usando o preview já criado"""
        try:
            # Verificar se tem preview da dieta
            diet_preview = consultation_state.get('diet_preview')
            if not diet_preview:
                # Se não tem preview, criar primeiro
                diet_preview = self._generate_diet_preview(consultation_state)
                consultation_state['diet_preview'] = diet_preview
            
            # Converter preview para formato completo de dieta
            diet_json = self._convert_preview_to_full_diet(diet_preview)
            
            # GERAR PDF DA DIETA
            try:
                pdf_path = create_diet_pdf(diet_json)
                logger.info(f"✅ PDF da dieta gerado: {pdf_path}")
                diet_json['pdf_path'] = pdf_path
                diet_json['pdf_generated'] = True
            except Exception as pdf_error:
                logger.error(f"Erro ao gerar PDF: {pdf_error}")
                raise RuntimeError(f"Falha na geração do PDF: {str(pdf_error)}") from pdf_error
            
            # SALVAR DIETA NO BANCO DE DADOS
            try:
                user_id = consultation_state.get('user_data', {}).get('user_id')
                if user_id:
                    patient_name = diet_json.get('patient_info', {}).get('name', 'Paciente')
                    diet_name = f"Dieta Personalizada - {patient_name}"
                    
                    diet_id = self.diet_manager.save_diet(
                        user_id=int(user_id),
                        diet_data=diet_json,
                        diet_name=diet_name,
                        source="nutritionist_ai"
                    )
                    
                    logger.info(f"✅ Dieta salva no banco de dados com ID: {diet_id}")
                    diet_json['diet_id'] = diet_id
                    diet_json['saved_to_database'] = True
                else:
                    raise ValueError("user_id não encontrado")
                    
            except Exception as db_error:
                logger.error(f"Erro ao salvar dieta no banco: {db_error}")
                raise RuntimeError(f"Falha ao salvar no banco: {str(db_error)}") from db_error
            
            # Salvar JSON no estado da consulta
            consultation_state['generated_diet'] = diet_json
            consultation_state['diet_generated_at'] = datetime.now().isoformat()
            consultation_state['current_phase'] = 'diet_generated'
            
            # Gerar resposta confirmando a criação
            response_content = f"""🎉 **DIETA GERADA COM SUCESSO!**

✅ Sua dieta personalizada foi criada e salva!
📄 PDF gerado e disponível para download
💾 Dados salvos no seu perfil

🏠 Redirecionando para o dashboard em alguns segundos..."""

            consultation_state['conversation_history'].append({
                'role': 'assistant',
                'message': response_content,
                'timestamp': datetime.now().isoformat()
            })
            consultation_state['last_response_content'] = response_content
            consultation_state['updated_at'] = datetime.now().isoformat()
            
            return consultation_state
            
        except Exception as e:
            logger.error(f"Erro ao gerar dieta final: {str(e)}")
            raise RuntimeError(f"Falha na geração da dieta final: {str(e)}") from e

    def _convert_preview_to_full_diet(self, diet_preview: Dict[str, Any]) -> Dict[str, Any]:
        """Converte o preview da dieta para o formato completo necessário para PDF"""
        try:
            anthropometric_data = diet_preview['anthropometric_data']
            tmb_calculations = diet_preview['tmb_calculations']
            nutritional_database = diet_preview['nutritional_database']
            
            # Estrutura completa da dieta para PDF
            diet_structure = {
                'generated_at': datetime.now().isoformat(),
                'diet_id': f"diet_{int(time.time())}",
                
                # Informações do paciente
                'patient_info': {
                    'name': anthropometric_data.get('name', 'Paciente'),
                    'age': anthropometric_data.get('age_years', 'Não informado'),
                    'gender': anthropometric_data.get('gender', 'Não informado'),
                    'weight_kg': anthropometric_data.get('weight_kg', 'Não informado'),
                    'height_cm': anthropometric_data.get('height_cm', 'Não informado'),
                    'activity_level': anthropometric_data.get('activity_level', 'Moderadamente ativo'),
                    'primary_objective': anthropometric_data.get('primary_objective', 'Manutenção')
                },
                
                # Cálculos nutricionais
                'nutritional_calculations': {
                    'tmb_kcal': tmb_calculations.get('tmb_kcal', 1800),
                    'daily_target_kcal': tmb_calculations.get('daily_target_kcal', 2200),
                    'objective_adjustment': tmb_calculations.get('objective_adjustment', 'Manutenção'),
                    'macronutrients': tmb_calculations.get('macronutrient_distribution', {}),
                    'activity_factor': tmb_calculations.get('activity_factor', 1.55)
                },
                
                # Menu semanal
                'weekly_menu': diet_preview['weekly_menu'],
                
                # Dados da API USDA
                'nutrition_data_source': {
                    'primary_source': 'USDA FoodData Central API',
                    'foods_analyzed': len(nutritional_database),
                    'api_status': 'Dados coletados em tempo real',
                    'last_updated': datetime.now().isoformat()
                },
                
                # Banco de dados nutricional completo
                'nutritional_database': nutritional_database
            }
            
            return diet_structure
            
        except Exception as e:
            logger.error(f"Erro ao converter preview para dieta completa: {str(e)}")
            raise RuntimeError(f"Falha na conversão da dieta: {str(e)}") from e

    def _llm_calculate_nutritional_needs(self, user_data: Dict[str, Any], conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LLM calcula TMB, calorias e macronutrientes baseado no contexto da conversa"""
        try:
            # Preparar contexto da conversa
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['message']}" 
                for msg in conversation_history
            ])
            
            # Contexto completo para LLM
            context_data = {
                'user_profile': user_data,
                'conversation_history': conversation_context
            }
            
            # Prompt limpo - apenas contexto
            calculation_prompt = f"""
            {self.config.system_prompt}
            
            CONTEXTO ATUAL:
            {json.dumps(context_data, indent=2, ensure_ascii=False)}
            
            Comando: nutritional_calculations_handler
            """
            
            # Invocar LLM
            response = self.llm.invoke([SystemMessage(content=calculation_prompt)])
            
            # Parsear resposta
            try:
                calculations = json.loads(response.content.strip())
                logger.info(f"✅ LLM calculou necessidades nutricionais com sucesso")
                return calculations
            except (json.JSONDecodeError, ValueError):
                # Tentar extrair JSON do texto
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                calculations = json.loads(content.strip())
                return calculations
                
        except Exception as e:
            logger.error(f"Erro nos cálculos nutricionais pela LLM: {e}")
            # SEM FALLBACK - propagar erro
            raise RuntimeError(f"Falha nos cálculos nutricionais: {str(e)}") from e

    

    def generate_diet_pdf_data(self, diet_json: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados estruturados para geração de PDF"""
        try:
            # Estruturar dados para o PDF
            pdf_data = {
                'title': 'Plano Alimentar Personalizado',
                'subtitle': f"Elaborado para {diet_json.get('patient_info', {}).get('name', 'Paciente')}",
                'patient_section': diet_json.get('patient_info', {}),
                'nutritional_section': diet_json.get('nutritional_plan', {}),
                'menu_section': diet_json.get('weekly_menu', {}),
                'shopping_section': diet_json.get('shopping_list', {}),
                'guidance_section': diet_json.get('practical_guidance', {}),
                'recommendations_section': diet_json.get('recommendations', {}),
                'generated_date': datetime.now().strftime("%d/%m/%Y"),
                'generated_by': 'Nutrion - Nutricionista Virtual ShapeMateAI'
            }
            
            return pdf_data
            
        except Exception as e:
            logger.error(f"Erro crÃ­tico ao preparar dados para PDF: {str(e)}")
            raise RuntimeError(f"Falha na preparaÃ§Ã£o dos dados para PDF: {str(e)}") from e

    def _get_response_for_command(self, command_name: str, consultation_state: Dict[str, Any]) -> str:
        """Gera resposta baseada em comando YAML específico"""
        try:
            # Buscar comando específico nas configurações YAML
            command_prompts = getattr(self.config, 'command_prompts', {})
            if not command_prompts or command_name not in command_prompts:
                raise ValueError(f"Comando '{command_name}' não encontrado na configuração YAML")
            
            # Preparar contexto para o comando
            user_data = consultation_state.get('user_data', {})
            conversation_history = consultation_state.get('conversation_history', [])
            
            # Construir contexto da consulta
            consultation_context = "\n".join([
                f"{msg['role']}: {msg['message']}" 
                for msg in conversation_history
            ])
            
            # Preparar prompt usando comando específico do YAML
            command_prompt = f"""
            {self.config.system_prompt}
            
            Dados do usuário: {user_data}
            Histórico da consulta: {consultation_context}
            
            Comando específico: {command_name}
            
            {command_prompts[command_name]}
            """
            
            # Gerar resposta usando LLM
            response = self.llm.invoke([SystemMessage(content=command_prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Erro ao processar comando '{command_name}': {str(e)}")
            return f"Desculpe, houve um erro ao processar sua solicitação. Vamos tentar novamente?"


def create_nutritionist_agent() -> NutritionistAgent:
    """Factory function para criar instÃ¢ncia do agente nutricionista"""
    return NutritionistAgent()
