"""
Nutritionist Agent - Sem fallbacks, totalmente baseado em LLM e APIs
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

logger = logging.getLogger(__name__)

try:
    from core.core import BaseAgent, AgentConfig, AgentState, AgentType, TaskType
    from core.config_loader import get_config_loader
    from utils.nutrition_api import NutritionAPI
    from utils.pdf_generator import create_diet_pdf
    from utils.diet_manager.diet_storage import DietManager
    from utils.nutrition_cache import FoodCache

except ImportError as e:
    logger.error(f"Erro ao importar dependências: {e}")
    raise


class NutritionistAgent(BaseAgent):
    """Agente nutricionista sem fallbacks - LLM + APIs apenas"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config_loader = get_config_loader()
            config = config_loader.load_agent_config(AgentType.NUTRITIONIST)
        super().__init__(config)
        
        # Serviços especializados
        self.nutrition_api = NutritionAPI()
        self.diet_manager = DietManager()
        self.food_cache = FoodCache(fetcher=self._fetch_food_nutrition)
        self.config_loader = get_config_loader()
        # Carregar configs de task para consulta e criação de dieta
        try:
            self.consultation_task = self.config_loader.load_task_config(TaskType.CONSULTATION, AgentType.NUTRITIONIST)
        except Exception:
            self.consultation_task = None
        try:
            self.diet_creation_task = self.config_loader.load_task_config(TaskType.DIET_CREATION, AgentType.NUTRITIONIST)
        except Exception:
            self.diet_creation_task = None
    
    def process_message(self, state: AgentState) -> AgentState:
        """Processa mensagem baseado na task atual"""
        task_type = state.get('task_type', '')
        
        if task_type == TaskType.DIET_CREATION.value:
            return self._handle_diet_creation(state)
        else:
            # Default: consultation
            return self._handle_consultation(state)
    
    def _handle_consultation(self, state: AgentState) -> AgentState:
        """Gerencia consulta estruturada usando apenas LLM"""
        user_message = state['messages'][-1].content if state['messages'] else ""
        consultation_state = state.get('consultation_state') or state.get('context', {}).get('consultation_state')
        
        # Inicializar consulta se necessário
        if not consultation_state:
            consultation_state = self._initialize_consultation(state)
            state['consultation_state'] = consultation_state
        
        # Processar resposta do usuário
        if user_message.strip():
            consultation_state = self._process_user_response(consultation_state, user_message)
            state['consultation_state'] = consultation_state
        
        # Determinar próxima ação
        if consultation_state.get('consultation_completed'):
            state['show_option_buttons'] = True
            state['is_decision_point'] = True
            state['current_phase'] = 'consultation_completed'
        else:
            state['show_option_buttons'] = False
            state['is_decision_point'] = False
            state['current_phase'] = consultation_state.get('current_phase', 'consultation_in_progress')
        
        # Adicionar resposta do agente
        if consultation_state.get('last_response'):
            response = AIMessage(content=consultation_state['last_response'])
            state['messages'].append(response)
        
        state['confidence_score'] = 0.9
        state['tools_used'] = ['consultation']
        
        return state
    
    def _handle_diet_creation(self, state: AgentState) -> AgentState:
        """Gera dieta usando LLM + APIs - sem fallbacks"""
        consultation_state = state.get('consultation_state') or state.get('context', {}).get('consultation_state')
        if not consultation_state:
            raise ValueError("Dados da consulta não encontrados")
        
        # 1. LLM calcula TMB e necessidades nutricionais
        nutritional_data = self._llm_calculate_nutritional_needs(consultation_state)
        
        # 2. LLM seleciona alimentos baseado nas preferências coletadas
        selected_foods = self._llm_select_foods(consultation_state, nutritional_data)
        
        # 3. API USDA busca dados nutricionais
        nutrition_database = self._fetch_nutrition_data_usda(selected_foods)
        normalized_nutrition_db = self._normalize_nutrition_db(nutrition_database)
        # 3.1 Mapa EN->PT
        en_to_pt = self._build_food_translation_map(nutrition_database)
        
        # 4. LLM gera estrutura completa da dieta
        diet_json = self._llm_generate_diet_structure(
            consultation_state, 
            nutritional_data, 
            nutrition_database
        )
        # Garantir base nutricional padronizada para cálculos de porções
        diet_json['nutritional_database'] = normalized_nutrition_db
        # 4.1 Pós-processamento: traduzir e calibrar quantidades
        diet_json = self._postprocess_diet_structure(diet_json, en_to_pt)
        # 4.1.1 Garantir semana completa
        diet_json = self._ensure_full_week(diet_json)
        
        # Enriquecer metadados da fonte
        try:
            diet_json.setdefault('nutrition_data_source', {})
            diet_json['nutrition_data_source']['foods_analyzed'] = len(normalized_nutrition_db)
            diet_json['nutrition_data_source']['primary_source'] = 'USDA FoodData Central API'
            diet_json['nutrition_data_source']['last_updated'] = datetime.now().isoformat()
        except Exception:
            pass

        # 5. Gerar PDF
        pdf_path = create_diet_pdf(diet_json)
        diet_json['pdf_path'] = pdf_path
        diet_json['pdf_generated'] = True
        
        # 6. Salvar no banco
        user_id = state.get('user_profile', {}).get('user_id')
        if user_id:
            diet_id = self.diet_manager.save_diet(
                user_id=user_id,
                diet_data=diet_json,
                diet_name=f"Dieta Personalizada - {diet_json.get('patient_info', {}).get('name', 'Paciente')}",
                source="nutritionist_ai"
            )
            diet_json['diet_id'] = diet_id
            
            # Conceder acesso ao nutricionista por 30 dias
            try:
                from database.models import Database
                db = Database()
                db.grant_nutritionist_access(user_id, days=30)
            except Exception as e:
                print(f"Erro ao conceder acesso ao nutricionista: {e}")
        
        # 7. LLM gera mensagem de despedida
        farewell_message = self._llm_generate_farewell_message(diet_json)
        
        # Atualizar estado
        state['generated_diet'] = diet_json
        state['diet_generated'] = True
        state['current_phase'] = 'diet_completed'
        state['confidence_score'] = 0.95
        state['tools_used'] = ['diet_creation', 'usda_api', 'pdf_generation']
        
        response = AIMessage(content=farewell_message)
        state['messages'].append(response)
        
        return state

    def _build_food_translation_map(self, nutrition_database: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Gera mapa EN->PT usando LLM para nomes de alimentos, com fallback simples."""
        en_names = list(nutrition_database.keys())
        # Tentar traduzir via LLM
        try:
            llm_map = self._llm_translate_food_names(en_names)
            # Normalizar chaves como vieram na base
            result: Dict[str, str] = {}
            for en in en_names:
                translated = llm_map.get(en) or llm_map.get(en.lower()) or llm_map.get(en.title())
                result[en] = translated or en.title()
            return result
        except Exception:
            # Fallback: título simples
            return {en: en.title() for en in en_names}

    def _llm_translate_food_names(self, en_names: List[str]) -> Dict[str, str]:
        """Usa o LLM para traduzir uma lista de nomes de alimentos EN->PT-BR.
        Retorna um dicionário {name_en: name_pt}.
        """
        # Montar contexto em português para garantir linguagem e formato
        names_str = json.dumps(en_names, ensure_ascii=False)
        context = f"""
        {self.config.system_prompt}

        Você deve atuar como um tradutor de nomes de alimentos do inglês para o português do Brasil.
        Receba uma lista JSON de nomes em inglês e devolva APENAS um JSON mapeando cada nome original para a tradução natural em pt-BR.
        Mantenha o sentido culinário comum (ex.: 'chicken breast' -> 'Peito de Frango', 'white rice' -> 'Arroz Branco').
        Não inclua explicações. Responda apenas com o JSON.

        Lista de entrada: {names_str}
        """
        response = self.llm.invoke([SystemMessage(content=context)])
        content = response.content.strip()
        # Extrair JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                return json.loads(content[start:end])
            raise

    def _postprocess_diet_structure(self, diet: Dict[str, Any], en_to_pt: Dict[str, str]) -> Dict[str, Any]:
        """Traduz nomes para PT e calibra porções com base no target kcal por refeição."""
        nutrition_db = diet.get('nutritional_database') or {}

        def kcal_per_100g(name_en: str) -> float:
            data = nutrition_db.get(name_en) or nutrition_db.get(name_en.lower()) or {}
            # Suporta dois formatos: {per_100g: {kcal: ...}} ou {calories_per_100g: ...}
            per100 = data.get('per_100g') or {}
            val = per100.get('kcal', None)
            if val is None:
                val = data.get('calories_per_100g', 0)
            try:
                return float(val)
            except Exception:
                return 0.0

        weekly_menu = diet.get('weekly_menu') or {}
        for _, day in weekly_menu.items():
            if not isinstance(day, dict):
                continue
            for _, meal in day.items():
                if not isinstance(meal, dict):
                    continue
                target = float(meal.get('target_kcal') or 0)
                options = meal.get('options') or []
                for option in options:
                    items = option.get('items') or []
                    # traduzir nomes
                    for it in items:
                        name_en = it.get('name_en') or it.get('name') or ''
                        if name_en:
                            it['name_en'] = name_en
                            it['name_pt'] = en_to_pt.get(name_en, name_en.title())
                    # calcular kcal atual
                    def compute_totals() -> float:
                        kcal_total = 0.0
                        for it2 in items:
                            name_en2 = it2.get('name_en')
                            portion = float(it2.get('portion_grams') or it2.get('quantity_g') or 0)
                            k100 = kcal_per_100g(name_en2)
                            item_kcal = round(k100 * (portion / 100.0), 1) if portion > 0 else 0.0
                            it2['kcal'] = item_kcal
                            kcal_total += k100 * (portion / 100.0)
                        return round(kcal_total, 1)

                    current_kcal = compute_totals()
                    if target > 0 and current_kcal > 0:
                        scale = max(0.5, min(1.5, target / current_kcal))
                        for it3 in items:
                            portion = float(it3.get('portion_grams') or it3.get('quantity_g') or 0)
                            if portion <= 0:
                                continue
                            new_portion = round(portion * scale)
                            name_en3 = (it3.get('name_en') or '').lower()
                            if any(k in name_en3 for k in ['rice', 'beans', 'bread', 'oat']):
                                new_portion = min(max(new_portion, 40), 90)
                            elif any(k in name_en3 for k in ['chicken', 'beef', 'fish', 'salmon', 'tuna', 'egg']):
                                new_portion = min(max(new_portion, 70), 140)
                            elif any(k in name_en3 for k in ['banana', 'apple', 'orange', 'fruit']):
                                new_portion = min(max(new_portion, 80), 160)
                            elif any(k in name_en3 for k in ['lettuce', 'tomato', 'cucumber', 'broccoli', 'spinach', 'carrot']):
                                new_portion = min(max(new_portion, 40), 120)
                            it3['portion_grams'] = int(new_portion)

                        new_kcal = compute_totals()
                        lower, upper = target * 0.93, target * 1.07
                        if not (lower <= new_kcal <= upper) and new_kcal > 0:
                            # ajuste fino em carboidrato principal
                            for it4 in items:
                                name_en4 = (it4.get('name_en') or '').lower()
                                if any(k in name_en4 for k in ['rice', 'bread', 'oat', 'potato', 'quinoa', 'beans']):
                                    k100 = kcal_per_100g(it4.get('name_en'))
                                    if k100 <= 0:
                                        continue
                                    diff = target - new_kcal
                                    delta_g = int(round((diff / k100) * 100))
                                    it4['portion_grams'] = max(30, int(it4.get('portion_grams', 0)) + delta_g)
                                    break
                        # atualizar totais
                    option['totals'] = option.get('totals') or {}
                    option['totals']['kcal'] = compute_totals()

        diet.setdefault('nutrition_data_source', {})
        diet['nutrition_data_source']['language'] = 'pt-BR'
        return diet

    def _ensure_full_week(self, diet: Dict[str, Any]) -> Dict[str, Any]:
        """Garante que weekly_menu tenha as 7 chaves de dias. Se faltar, replica a estrutura do primeiro disponível.
        Mantém a estrutura com target_kcal e options para compatibilidade com PDF/UI.
        """
        weekly = diet.get('weekly_menu') or {}
        if not isinstance(weekly, dict):
            return diet
        day_order = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        # selecionar um dia base para replicar
        base_day = None
        for k in day_order:
            if k in weekly and isinstance(weekly[k], dict):
                base_day = weekly[k]
                break
        if not base_day and weekly:
            # pega o primeiro valor do dict
            for _, v in weekly.items():
                if isinstance(v, dict):
                    base_day = v
                    break
        if not base_day:
            return diet
        # preencher dias faltantes
        for d in day_order:
            if d not in weekly:
                # cópia rasa suficiente para exibição; não mutar referências do base original
                import copy
                weekly[d] = copy.deepcopy(base_day)
        diet['weekly_menu'] = {d: weekly[d] for d in day_order}
        return diet

    # =====================
    # Consulta estruturada (para rotas web)
    # =====================

    def start_structured_consultation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia a consulta estruturada com base no YAML de consultation"""
        # Estado básico
        consultation_state: Dict[str, Any] = {
            'user_data': user_data or {},
            'consultation_id': f"consultation_{user_data.get('user_id', 'unknown')}_{int(time.time())}",
            'created_at': datetime.now().isoformat(),
            'current_question': 1,
            'total_questions': 18,
            'answers': {},
            'conversation_history': [],
            'current_phase': 'greeting',
            'consultation_completed': False,
            'ready_for_summary': False
        }

        # Mensagem de boas-vindas personalizada via LLM
        welcome_message = self._llm_generate_welcome_message(user_data)
        consultation_state['last_response'] = welcome_message
        consultation_state['last_response_content'] = welcome_message
        consultation_state['current_phase'] = 'greeting'
        consultation_state['conversation_history'].append({
            'role': 'assistant',
            'message': welcome_message,
            'timestamp': datetime.now().isoformat()
        })
        return consultation_state

    def continue_structured_consultation(self, consultation_state: Dict[str, Any], user_response: str) -> Dict[str, Any]:
        """Continua a consulta estruturada com registro da resposta do usuário e próxima pergunta/sumário"""
        if not consultation_state:
            raise ValueError("Consulta não inicializada")

        # Registrar resposta atual
        current_q = consultation_state.get('current_question', 1)
        consultation_state.setdefault('answers', {})
        consultation_state['answers'][f'question_{current_q}'] = user_response
        consultation_state['conversation_history'].append({
            'role': 'user',
            'message': user_response,
            'timestamp': datetime.now().isoformat()
        })

        # Avançar contador
        consultation_state['current_question'] = current_q + 1

        # Se completou as 18 perguntas, gerar resumo e habilitar decisão
        if consultation_state['current_question'] > consultation_state['total_questions']:
            consultation_state['consultation_completed'] = True
            consultation_state['current_phase'] = 'consultation_summary'
            summary_message = self._llm_generate_consultation_summary(consultation_state)
            consultation_state['last_response'] = summary_message
            consultation_state['last_response_content'] = summary_message
            consultation_state['ready_for_summary'] = True
            consultation_state['conversation_history'].append({
                'role': 'assistant',
                'message': summary_message,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Próxima pergunta - usar LLM para gerar pergunta natural
            consultation_state['current_phase'] = self._determine_phase(
                consultation_state['current_question'], consultation_state['total_questions']
            )
            next_message = self._llm_generate_natural_question(consultation_state, user_response)
            consultation_state['last_response'] = next_message
            consultation_state['last_response_content'] = next_message
            consultation_state['conversation_history'].append({
                'role': 'assistant',
                'message': next_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Debug log para verificar o progresso
            logger.info(f"Consulta progresso: Pergunta {consultation_state['current_question']}/{consultation_state['total_questions']} - Fase: {consultation_state['current_phase']}")

        return consultation_state
    
    def _initialize_consultation(self, state: AgentState) -> Dict[str, Any]:
        """Inicializa consulta usando LLM"""
        user_data = state.get('user_profile', {})
        
        consultation_state = {
            'user_data': user_data,
            'consultation_id': f"consultation_{user_data.get('user_id', 'unknown')}_{int(time.time())}",
            'created_at': datetime.now().isoformat(),
            'current_question': 1,
            'total_questions': 18,
            'answers': {},
            'conversation_history': [],
            'current_phase': 'greeting',
            'consultation_completed': False
        }
        
        # LLM gera primeira pergunta
        initial_message = self._llm_generate_consultation_question(consultation_state)
        consultation_state['last_response'] = initial_message
        consultation_state['conversation_history'].append({
            'role': 'assistant',
            'message': initial_message,
            'timestamp': datetime.now().isoformat()
        })
        
        return consultation_state
    
    def _process_user_response(self, consultation_state: Dict[str, Any], user_response: str) -> Dict[str, Any]:
        """Processa resposta usando LLM"""
        # Registrar resposta
        current_q = consultation_state['current_question']
        consultation_state['answers'][f'question_{current_q}'] = user_response
        consultation_state['conversation_history'].append({
            'role': 'user',
            'message': user_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Avançar pergunta
        consultation_state['current_question'] += 1
        
        # Verificar se consulta foi concluída
        if consultation_state['current_question'] > consultation_state['total_questions']:
            consultation_state['consultation_completed'] = True
            consultation_state['current_phase'] = 'summary'
            # LLM gera resumo
            summary_message = self._llm_generate_consultation_summary(consultation_state)
            consultation_state['last_response'] = summary_message
        else:
            # LLM gera próxima pergunta
            next_message = self._llm_generate_consultation_question(consultation_state)
            consultation_state['last_response'] = next_message
        
        consultation_state['conversation_history'].append({
            'role': 'assistant',
            'message': consultation_state['last_response'],
            'timestamp': datetime.now().isoformat()
        })
        
        return consultation_state
    
    def _llm_generate_consultation_question(self, consultation_state: Dict[str, Any]) -> str:
        """LLM gera pergunta da consulta"""
        task_config = self.consultation_task or self.config_loader.load_task_config(TaskType.CONSULTATION, AgentType.NUTRITIONIST)
        
        current_q = consultation_state['current_question']
        conversation_history = consultation_state.get('conversation_history', [])
        
        context = f"""
        {self.config.system_prompt}
        
        {task_config.specialized_prompts.get('consultation_flow', '')}
        
        Situação atual:
        - Pergunta {current_q} de {consultation_state['total_questions']}
        - Dados do usuário: {consultation_state.get('user_data', {})}
        - Histórico: {json.dumps(conversation_history[-4:], ensure_ascii=False)}
        
        Gere APENAS a próxima pergunta apropriada. Uma pergunta por vez, linguagem natural.
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        return response.content.strip()

    def _llm_generate_welcome_message(self, user_data: Dict[str, Any]) -> str:
        """LLM gera mensagem de boas-vindas personalizada e natural"""
        context = f"""
        {self.config.system_prompt}
        
        Você é um nutricionista profissional, caloroso e motivador. Está iniciando uma consulta nutricional personalizada.
        
        Dados do paciente: {user_data}
        
        Gere uma mensagem de boas-vindas NATURAL e ACOLHEDORA que:
        - Seja muito calorosa e profissional
        - Mencione o nome do paciente se disponível
        - Se apresente como nutricionista
        - Explique que vai ajudar a criar uma dieta personalizada
        - Transmita confiança, motivação e otimismo
        - Seja natural, como um nutricionista real falaria
        - Não seja robótica ou formal demais
        - Use emojis discretos se apropriado (1-2 no máximo)
        - Termine fazendo a primeira pergunta sobre rotina de sono de forma natural
        
        Use linguagem natural e acolhedora, como um nutricionista conversaria com um paciente.
        
        Exemplo de tom:
        "Olá [nome]! 👋 Que prazer te conhecer! Sou o Nutrion, seu nutricionista virtual. Estou aqui para te ajudar a criar uma dieta totalmente personalizada que vai te ajudar a alcançar seus objetivos! Vamos conversar um pouco sobre sua rotina para que eu possa entender melhor como você vive e criar o plano perfeito para você. Para começar, me conta: como é seu horário de sono? Que horas você costuma acordar e dormir?"
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        return response.content.strip()
    
    def _llm_generate_natural_question(self, consultation_state: Dict[str, Any], user_response: str) -> str:
        """LLM gera pergunta natural baseada na resposta anterior e contexto"""
        task_config = self.consultation_task or self.config_loader.load_task_config(TaskType.CONSULTATION, AgentType.NUTRITIONIST)
        current_q = consultation_state.get('current_question', 1)
        conversation_history = consultation_state.get('conversation_history', [])
        
        # Mapeamento das perguntas base para orientar o LLM
        questions_base = {
            1: "rotina de sono (horário de acordar e dormir)",
            2: "horário de trabalho ou estudo",
            3: "prática de atividade física",
            4: "tipo de atividade física",
            5: "frequência semanal de exercícios",
            6: "duração dos treinos",
            7: "café da manhã",
            8: "lanche da manhã",
            9: "almoço",
            10: "lanche da tarde",
            11: "jantar",
            12: "ceia",
            13: "hidratação",
            14: "preferências alimentares",
            15: "aversões alimentares",
            16: "alimentação nos finais de semana",
            17: "desafios na alimentação",
            18: "tempo para organização alimentar"
        }
        
        context = f"""
        {self.config.system_prompt}
        
        Você é um nutricionista profissional conduzindo uma consulta nutricional personalizada.
        
        Situação atual:
        - Pergunta {current_q} de 18
        - Fase: {consultation_state.get('current_phase', 'consultation')}
        - Tópico atual: {questions_base.get(current_q, 'informações gerais')}
        
        Resposta anterior do paciente: "{user_response}"
        
        Histórico recente da conversa:
        {json.dumps(conversation_history[-3:], ensure_ascii=False)}
        
        Gere a próxima pergunta de forma NATURAL e HUMANA:
        - Use a resposta anterior para contextualizar e mostrar que entendeu
        - Seja caloroso e profissional
        - Faça uma pergunta específica sobre o tópico atual
        - Use linguagem natural, como um nutricionista real falaria
        - Não seja robótica ou formal
        - Mostre que está prestando atenção na resposta anterior
        - Seja motivador e acolhedor
        - Use expressões como "Entendo!", "Ótimo!", "Que bom!", "Perfeito!", "Legal!", "Excelente!"
        - Evite linguagem muito formal ou técnica
        - Seja mais conversacional e menos interrogativo
        
        Exemplos de tom:
        - "Entendo! E sobre [próximo tópico], como é sua rotina?"
        - "Ótimo! Agora me conta: [próxima pergunta]"
        - "Que bom! E [próximo tópico], como funciona para você?"
        - "Legal! E [próximo tópico], como é para você?"
        - "Perfeito! Agora vamos falar sobre [próximo tópico]..."
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        return response.content.strip()
    
    def _structured_generate_next_question(self, consultation_state: Dict[str, Any]) -> str:
        """Método legado - mantido para compatibilidade"""
        return self._llm_generate_natural_question(consultation_state, "")
    
    def _llm_generate_consultation_summary(self, consultation_state: Dict[str, Any]) -> str:
        """LLM gera resumo da consulta de forma natural e motivadora"""
        task_config = self.consultation_task or self.config_loader.load_task_config(TaskType.CONSULTATION, AgentType.NUTRITIONIST)
        
        context = f"""
        {self.config.system_prompt}
        
        Você é um nutricionista profissional que acabou de concluir uma consulta nutricional personalizada.
        
        Dados coletados da consulta: {consultation_state.get('answers', {})}
        Dados do paciente: {consultation_state.get('user_data', {})}
        
        Gere um resumo NATURAL e MOTIVADOR da consulta que:
        - Seja caloroso e profissional
        - Resuma os principais pontos coletados (rotina, objetivos, preferências)
        - Demonstre que entendeu o perfil do paciente
        - Transmita confiança e otimismo
        - Seja natural, como um nutricionista real falaria
        - Termine perguntando se o paciente gostaria de gerar sua dieta personalizada
        - Use linguagem acolhedora e motivadora
        
        Exemplo de tom: "Perfeito! Agora que conheço melhor sua rotina e objetivos, posso criar uma dieta totalmente personalizada para você. Gostaria que eu gere seu plano alimentar?"
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        return response.content.strip()

    def _determine_phase(self, question_index: int, total_questions: int) -> str:
        """Determina a fase atual da consulta conforme mapeamento do YAML e UI"""
        if question_index <= 0:
            return 'greeting'
        if 1 <= question_index <= 6:
            return 'routine_assessment'
        if 7 <= question_index <= 12:
            return 'eating_habits_mapping'
        if 13 <= question_index <= 16:
            return 'preferences_collection'
        if 17 <= question_index <= total_questions:
            return 'practical_constraints'
        return 'consultation_summary'
    
    def _llm_calculate_nutritional_needs(self, consultation_state: Dict[str, Any]) -> Dict[str, Any]:
        """LLM calcula TMB e necessidades nutricionais"""
        context = f"""
        {self.config.system_prompt}
        
        COMANDO: nutritional_calculations_handler
        
        Dados da consulta: {consultation_state.get('answers', {})}
        Dados do usuário: {consultation_state.get('user_data', {})}
        
        Calcule TMB, calorias meta e distribuição de macronutrientes.
        Retorne APENAS JSON válido com a estrutura completa de cálculos nutricionais.
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        
        # Parse JSON da resposta
        try:
            return json.loads(response.content.strip())
        except json.JSONDecodeError:
            # Tentar extrair JSON do conteúdo
            content = response.content.strip()
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end]
            
            return json.loads(content)
    
    def _llm_select_foods(self, consultation_state: Dict[str, Any], nutritional_data: Dict[str, Any]) -> List[str]:
        """LLM seleciona alimentos baseado nas preferências"""
        context = f"""
        {self.config.system_prompt}
        
        COMANDO: food_selection_handler
        
        Consulta: {consultation_state.get('answers', {})}
        Necessidades nutricionais: {nutritional_data}
        
        Selecione 25-30 alimentos variados em INGLÊS para API USDA.
        Use nomes simples e comuns que existem na base USDA.
        
        IMPORTANTE:
        - Use nomes em inglês (ex: "chicken breast", "rice", "apple")
        - Evite nomes complexos ou específicos
        - Foque em alimentos básicos e acessíveis
        - Considere as preferências do usuário da consulta
        
        Retorne APENAS lista JSON: ["food1", "food2", ...]
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        
        # Parse lista JSON
        try:
            return json.loads(response.content.strip())
        except json.JSONDecodeError:
            content = response.content.strip()
            if '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                return json.loads(content[start:end])
            raise
    
    def _fetch_nutrition_data_usda(self, food_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """Busca dados na API USDA - sem fallbacks"""
        nutrition_database = {}
        
        for food_name in food_list:
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
                    'source': food_data.source
                }
            else:
                # Se não encontrar na API, falha
                raise RuntimeError(f"Alimento '{food_name}' não encontrado na API USDA")
        
        return nutrition_database

    def _normalize_nutrition_db(self, nutrition_database: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Converte base USDA para formato { food: { per_100g: {kcal, protein_g, ...} } }"""
        out: Dict[str, Any] = {}
        for name_en, data in nutrition_database.items():
            try:
                out[name_en] = {
                    'per_100g': {
                        'kcal': float(data.get('calories_per_100g') or 0),
                        'protein_g': float(data.get('protein_g') or 0),
                        'carbs_g': float(data.get('carbs_g') or 0),
                        'fat_g': float(data.get('fat_g') or 0),
                    }
                }
            except Exception:
                continue
        return out
    
    def _llm_generate_diet_structure(self, consultation_state: Dict[str, Any], 
                                   nutritional_data: Dict[str, Any], 
                                   nutrition_database: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """LLM gera estrutura completa da dieta"""
        task_config = self.config_loader.load_task_config(TaskType.DIET_CREATION, AgentType.NUTRITIONIST)
        
        context = f"""
        {self.config.system_prompt}
        
        {task_config.specialized_prompts.get('creation_intro', '')}
        {task_config.specialized_prompts.get('json_structure_requirements', '')}
        
        Dados da consulta: {consultation_state.get('answers', {})}
        Dados do usuário: {consultation_state.get('user_data', {})}
        Cálculos nutricionais: {nutritional_data}
        Base de dados USDA: {nutrition_database}
        
        REGRAS CRÍTICAS PARA QUANTIDADES REALISTAS:
        1. QUANTIDADES POR REFEIÇÃO (em gramas):
           - Arroz/feijão: 50-80g por refeição
           - Carne/frango/peixe: 80-120g por refeição
           - Ovos: 1-2 unidades (50-100g)
           - Pão: 30-50g por refeição
           - Frutas: 100-150g por porção
           - Legumes: 50-100g por refeição
           - Aveia: 30-50g por refeição
           - Iogurte: 150-200g por refeição
        
        2. NOMES EM PORTUGUÊS:
           - Use nomes em português para exibição
           - Ex: "Peito de Frango" em vez de "chicken breast"
           - Ex: "Arroz Branco" em vez de "white rice"
           - Ex: "Maçã" em vez de "apple"
        
        3. ESTRUTURA OBRIGATÓRIA:
           - patient_info (obrigatório)
           - nutritional_calculations (obrigatório)
           - weekly_menu (obrigatório)
           - shopping_list (obrigatório)
           - nutrition_data_source (obrigatório)
           - nutritional_database (obrigatório)
        
        IMPORTANTE: Gere APENAS JSON válido sem comentários ou explicações.
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        
        # Parse JSON da resposta
        try:
            return json.loads(response.content.strip())
        except json.JSONDecodeError:
            content = response.content.strip()
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end]
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                content = content[start:end]
            
            return json.loads(content)
    
    def _llm_generate_farewell_message(self, diet_json: Dict[str, Any]) -> str:
        """LLM gera mensagem de despedida com resumo detalhado da dieta"""
        patient_info = diet_json.get('patient_info', {})
        nutritional_calculations = diet_json.get('nutritional_calculations', {})
        weekly_menu = diet_json.get('weekly_menu', {})
        shopping_list = diet_json.get('shopping_list', [])
        
        # Extrair dados principais
        patient_name = patient_info.get('name', 'Paciente')
        tmb = nutritional_calculations.get('tmb', 0) or nutritional_calculations.get('tmb_kcal', 0)
        calories_goal = nutritional_calculations.get('calories_goal', 0) or nutritional_calculations.get('daily_target_kcal', 0)
        macros = nutritional_calculations.get('macros', {}) or nutritional_calculations.get('macronutrients', {})
        if isinstance(macros, dict) and 'carbohydrates' in macros and isinstance(macros['carbohydrates'], dict):
            macros = {
                'protein_g': macros.get('proteins', {}).get('grams_per_day', 0),
                'carbs_g': macros.get('carbohydrates', {}).get('grams_per_day', 0),
                'fat_g': macros.get('fats', {}).get('grams_per_day', 0)
            }
        
        # Criar resumo dos alimentos principais
        main_foods = []
        if shopping_list and isinstance(shopping_list, list):
            main_foods = [item.get('food', '') for item in shopping_list[:10]]  # Primeiros 10 alimentos
        
        context = f"""
        {self.config.system_prompt}
        
        A dieta foi criada com sucesso para: {patient_info}
        Dados nutricionais: {nutritional_calculations}
        
        Gere uma mensagem de despedida profissional e motivadora que inclua:
        
        1. PARABÉNS E MOTIVAÇÃO:
        - Parabenize {patient_name} pelo compromisso com a saúde
        - Transmita confiança e otimismo
        
        2. RESUMO DA DIETA (FORMATADO):
        - TMB: {tmb} kcal/dia
        - Meta calórica: {calories_goal} kcal/dia
        - Proteínas: {macros.get('protein_g', 0)}g
        - Carboidratos: {macros.get('carbs_g', 0)}g
        - Gorduras: {macros.get('fat_g', 0)}g
        
        3. PRINCIPAIS ALIMENTOS INCLUÍDOS:
        {', '.join(main_foods) if main_foods else 'Alimentos variados e nutritivos'}
        
        4. ORIENTAÇÕES:
        - Seguir a dieta por 30 dias
        - Retornar para reavaliação no próximo mês
        - Para dúvidas diárias, usar o Assistente do Dia a Dia
        - Dieta disponível na aba "Minha Dieta" do dashboard
        
        Use formatação clara com emojis e estrutura organizada.
        """
        
        response = self.llm.invoke([SystemMessage(content=context)])
        return response.content.strip()
    
    def _fetch_food_nutrition(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Helper para cache - sem fallbacks"""
        food_data = self.nutrition_api.search_food(food_name)
        if food_data:
            return {
                'calories_per_100g': food_data.calories_per_100g,
                'protein_g': food_data.protein_g,
                'carbs_g': food_data.carbs_g,
                'fat_g': food_data.fat_g
            }
        return None


def create_nutritionist_agent() -> NutritionistAgent:
    """Factory function para criar agente nutricionista"""
    return NutritionistAgent()