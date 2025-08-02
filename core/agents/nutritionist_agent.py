"""
Nutritionist Agent implementation using Langgraph
Specialized agent for nutritional consultations and meal planning
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Langgraph imports (with fallback)
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import os
import sys

# Adicionar o diretório pai ao path para permitir importações relativas
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core import BaseAgent, AgentConfig, AgentState, AgentType, TaskType
from config_loader import get_config_loader

logger = logging.getLogger(__name__)


class NutritionistAgent(BaseAgent):
    """Agente especializado em nutrição e planejamento alimentar"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            # Carregar configuração padrão
            config_loader = get_config_loader()
            config = config_loader.load_agent_config(AgentType.NUTRITIONIST)
        
        super().__init__(config)
        
        # Ferramentas específicas do nutricionista
        self.nutrition_tools = {
            'calorie_calculator': self._calculate_calories,
            'macro_calculator': self._calculate_macros,
            'meal_planner': self._create_meal_plan,
            'nutrition_analyzer': self._analyze_nutrition,
            'health_assessor': self._assess_health_status
        }
    
    def _build_graph(self):
        """Constrói o grafo de estados do agente nutricionista"""
        if not LANGGRAPH_AVAILABLE:
            logger.warning("Langgraph not available, using simple processing")
            self.graph = None
            return
            
        workflow = StateGraph(AgentState)
        
        # Nós do grafo
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("assess_health", self._assess_health)
        workflow.add_node("plan_nutrition", self._plan_nutrition)
        workflow.add_node("provide_consultation", self._provide_consultation)
        workflow.add_node("educate_user", self._educate_user)
        workflow.add_node("finalize_response", self._finalize_response)
        
        # Ponto de entrada
        workflow.set_entry_point("analyze_input")
        
        # Transições condicionais
        workflow.add_conditional_edges(
            "analyze_input",
            self._route_based_on_input,
            {
                "health_assessment": "assess_health",
                "meal_planning": "plan_nutrition",
                "consultation": "provide_consultation",
                "education": "educate_user"
            }
        )
        
        # Transições para finalização
        workflow.add_edge("assess_health", "finalize_response")
        workflow.add_edge("plan_nutrition", "finalize_response")
        workflow.add_edge("provide_consultation", "finalize_response")
        workflow.add_edge("educate_user", "finalize_response")
        workflow.add_edge("finalize_response", END)
        
        self.graph = workflow.compile()
    
    def process_message(self, state: AgentState) -> AgentState:
        """Processa uma mensagem usando o novo sistema de memória"""
        try:
            # Preparar mensagens com contexto (inclui sistema + perfil do usuário)
            messages_with_context = self.prepare_messages_with_context(state)
            
            # Se langgraph não estiver disponível, usar processamento direto com LLM
            if not LANGGRAPH_AVAILABLE or self.graph is None:
                return self._process_with_llm(state, messages_with_context)
            
            # Atualizar state com mensagens preparadas
            state['messages'] = messages_with_context
            
            # Executar o grafo
            result = self.graph.invoke(state)
            return result
            
        except Exception as e:
            logger.error(f"Error processing message in NutritionistAgent: {str(e)}")
            # Resposta de fallback
            error_response = AIMessage(
                content="Desculpe, ocorreu um erro ao processar sua solicitação. "
                       "Por favor, tente reformular sua pergunta ou entre em contato com o suporte."
            )
            state['messages'].append(error_response)
            state['confidence_score'] = 0.1
            return state
    
    def _process_with_llm(self, state: AgentState, messages: List[BaseMessage]) -> AgentState:
        """Processa mensagem diretamente com a LLM usando histórico completo"""
        try:
            # Fazer chamada direta para a LLM com todas as mensagens
            response = self.llm.invoke(messages)
            
            # Adicionar resposta ao estado
            state['messages'].append(response)
            state['confidence_score'] = 0.9
            state['tools_used'] = ['llm_direct']
            
            return state
            
        except Exception as e:
            logger.error(f"Error in LLM processing: {str(e)}")
            error_response = AIMessage(
                content="Desculpe, não consegui processar sua solicitação sobre nutrição no momento. "
                       "Tente novamente ou reformule sua pergunta."
            )
            state['messages'].append(error_response)
            state['confidence_score'] = 0.1
            return state
    
    def _simple_nutrition_process(self, state: AgentState) -> AgentState:
        """Processamento simples do nutricionista sem langgraph"""
        try:
            user_message = state['messages'][-1].content if state['messages'] else ""
            user_profile = state.get('user_profile', {})
            
            # Análise simples do tipo de consulta
            if any(word in user_message.lower() for word in ['plano', 'cardápio', 'dieta', 'menu']):
                # Planejamento alimentar
                response = self._simple_meal_planning(user_profile)
            elif any(word in user_message.lower() for word in ['saúde', 'peso', 'imc', 'avaliação']):
                # Avaliação de saúde
                response = self._simple_health_assessment(user_profile)
            else:
                # Consulta geral
                response = self._simple_consultation(user_message, user_profile)
            
            state['messages'].append(AIMessage(content=response))
            state['confidence_score'] = 0.8
            return state
            
        except Exception as e:
            logger.error(f"Error in simple nutrition processing: {str(e)}")
            error_response = AIMessage(
                content="Desculpe, não consegui processar sua solicitação sobre nutrição no momento."
            )
            state['messages'].append(error_response)
            state['confidence_score'] = 0.1
            return state
    
    def _simple_meal_planning(self, user_profile: Dict[str, Any]) -> str:
        """Planejamento alimentar simplificado"""
        calories = self._calculate_calories(user_profile)
        if calories:
            return f"""Com base no seu perfil, suas necessidades calóricas diárias são aproximadamente {calories} kcal.

Aqui está uma sugestão básica de plano alimentar:

**Café da manhã ({int(calories * 0.25)} kcal):**
- Aveia com frutas vermelhas e 1 colher de mel
- 1 copo de leite desnatado ou bebida vegetal

**Almoço ({int(calories * 0.35)} kcal):**
- Salada verde variada
- 150g de proteína magra (frango, peixe ou leguminosas)
- 1 porção de carboidrato integral (arroz, quinoa)
- Vegetais refogados

**Lanche ({int(calories * 0.10)} kcal):**
- 1 fruta da estação
- Punhado de castanhas

**Jantar ({int(calories * 0.30)} kcal):**
- Sopa de legumes ou salada
- Proteína magra grelhada
- Vegetais no vapor

Lembre-se de beber pelo menos 2 litros de água por dia!"""
        else:
            return """Para criar um plano alimentar personalizado, preciso de mais informações sobre você:
- Idade, peso e altura
- Nível de atividade física
- Objetivos (perder peso, ganhar massa muscular, manter peso)
- Restrições alimentares

Pode compartilhar essas informações comigo?"""
    
    def _simple_health_assessment(self, user_profile: Dict[str, Any]) -> str:
        """Avaliação de saúde simplificada"""
        weight = user_profile.get('weight')
        height = user_profile.get('height')
        
        if weight and height:
            height_m = height / 100
            imc = weight / (height_m ** 2)
            
            if imc < 18.5:
                categoria = "abaixo do peso"
                recomendacao = "É importante aumentar a ingestão calórica de forma saudável."
            elif imc < 25:
                categoria = "peso normal"
                recomendacao = "Continue mantendo uma alimentação equilibrada."
            elif imc < 30:
                categoria = "sobrepeso"
                recomendacao = "Considere reduzir a ingestão calórica e aumentar a atividade física."
            else:
                categoria = "obesidade"
                recomendacao = "É recomendável buscar orientação profissional para um plano de emagrecimento."
            
            return f"""**Avaliação Nutricional:**

Seu IMC é {imc:.1f}, o que indica {categoria}.

{recomendacao}

**Recomendações gerais:**
- Mantenha uma alimentação variada e colorida
- Prefira alimentos naturais e minimamente processados
- Pratique atividade física regularmente
- Beba bastante água
- Tenha horários regulares para as refeições

Lembre-se: esta é uma avaliação básica. Para um acompanhamento completo, consulte um nutricionista presencialmente."""
        else:
            return """Para fazer uma avaliação nutricional adequada, preciso conhecer seu peso e altura atuais.

Também seria útil saber:
- Sua idade
- Nível de atividade física
- Objetivos de saúde
- Histórico de saúde relevante

Pode me fornecer essas informações?"""
    
    def _simple_consultation(self, user_message: str, user_profile: Dict[str, Any]) -> str:
        """Consulta nutricional simplificada"""
        prompt = f"""Como nutricionista, responda à seguinte pergunta de forma clara e útil:

Pergunta: {user_message}

Perfil do usuário: {user_profile}

Responda de forma profissional, empática e baseada em evidências científicas."""
        
        try:
            messages = [
                SystemMessage(content=self.config.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "Desculpe, não consegui processar sua pergunta no momento. Tente novamente ou reformule sua questão."
    
    def _analyze_input(self, state: AgentState) -> AgentState:
        """Analisa a entrada do usuário para determinar o tipo de solicitação"""
        user_message = state['messages'][-1].content if state['messages'] else ""
        
        # Categorizar a solicitação
        keywords_mapping = {
            'health_assessment': ['saúde', 'avaliação', 'status', 'condição', 'problema'],
            'meal_planning': ['plano', 'cardápio', 'refeição', 'dieta', 'menu'],
            'consultation': ['consulta', 'orientação', 'ajuda', 'dúvida', 'pergunta'],
            'education': ['aprender', 'explicar', 'ensinar', 'informação', 'conhecimento']
        }
        
        # Determinar categoria baseada em palavras-chave
        category_scores = {}
        for category, keywords in keywords_mapping.items():
            score = sum(1 for keyword in keywords if keyword.lower() in user_message.lower())
            category_scores[category] = score
        
        # Categoria com maior pontuação
        best_category = max(category_scores, key=category_scores.get)
        state['context']['input_category'] = best_category
        state['context']['category_confidence'] = category_scores[best_category] / len(keywords_mapping[best_category])
        
        return state
    
    def _route_based_on_input(self, state: AgentState) -> str:
        """Determina o próximo nó baseado na análise da entrada"""
        category = state['context'].get('input_category', 'consultation')
        return category
    
    def _assess_health(self, state: AgentState) -> AgentState:
        """Realiza avaliação de saúde do usuário"""
        user_profile = state.get('user_profile', {})
        
        # Coletar dados relevantes para avaliação
        health_data = {
            'age': user_profile.get('age'),
            'weight': user_profile.get('weight'),
            'height': user_profile.get('height'),
            'activity_level': user_profile.get('activity_level'),
            'health_conditions': user_profile.get('health_conditions', []),
            'medications': user_profile.get('medications', [])
        }
        
        # Calcular IMC se dados disponíveis
        if health_data['weight'] and health_data['height']:
            height_m = health_data['height'] / 100  # converter para metros
            imc = health_data['weight'] / (height_m ** 2)
            health_data['imc'] = round(imc, 2)
            
            # Classificar IMC
            if imc < 18.5:
                health_data['imc_category'] = 'Abaixo do peso'
            elif imc < 25:
                health_data['imc_category'] = 'Peso normal'
            elif imc < 30:
                health_data['imc_category'] = 'Sobrepeso'
            else:
                health_data['imc_category'] = 'Obesidade'
        
        state['context']['health_assessment'] = health_data
        
        # Gerar resposta personalizada
        assessment_prompt = self._create_health_assessment_prompt(health_data)
        response = self._generate_llm_response(state, assessment_prompt)
        
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('health_assessor')
        state['confidence_score'] = 0.85
        
        return state
    
    def _plan_nutrition(self, state: AgentState) -> AgentState:
        """Cria plano nutricional personalizado"""
        user_profile = state.get('user_profile', {})
        
        # Calcular necessidades calóricas
        calories = self._calculate_calories(user_profile)
        macros = self._calculate_macros(calories, user_profile)
        
        # Criar plano de refeições
        meal_plan = self._create_meal_plan(user_profile, calories, macros)
        
        state['context']['nutrition_plan'] = {
            'daily_calories': calories,
            'macros': macros,
            'meal_plan': meal_plan
        }
        
        # Gerar resposta personalizada
        planning_prompt = self._create_meal_planning_prompt(state['context']['nutrition_plan'])
        response = self._generate_llm_response(state, planning_prompt)
        
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].extend(['calorie_calculator', 'macro_calculator', 'meal_planner'])
        state['confidence_score'] = 0.9
        
        return state
    
    def _provide_consultation(self, state: AgentState) -> AgentState:
        """Fornece consulta nutricional geral"""
        user_message = state['messages'][-1].content
        user_profile = state.get('user_profile', {})
        
        # Criar prompt de consulta personalizado
        consultation_prompt = self._create_consultation_prompt(user_message, user_profile)
        response = self._generate_llm_response(state, consultation_prompt)
        
        state['messages'].append(AIMessage(content=response))
        state['confidence_score'] = 0.8
        
        return state
    
    def _educate_user(self, state: AgentState) -> AgentState:
        """Fornece informações educativas sobre nutrição"""
        user_message = state['messages'][-1].content
        
        # Criar prompt educativo
        education_prompt = self._create_education_prompt(user_message)
        response = self._generate_llm_response(state, education_prompt)
        
        state['messages'].append(AIMessage(content=response))
        state['confidence_score'] = 0.75
        
        return state
    
    def _finalize_response(self, state: AgentState) -> AgentState:
        """Finaliza a resposta e define próximas ações"""
        # Adicionar recomendações de acompanhamento se apropriado
        if state['context'].get('nutrition_plan'):
            state['next_action'] = 'schedule_followup'
        elif state['context'].get('health_assessment'):
            state['next_action'] = 'recommend_consultation'
        
        return state
    
    def _generate_llm_response(self, state: AgentState, prompt: str) -> str:
        """Gera resposta usando o LLM"""
        try:
            messages = [
                SystemMessage(content=self.config.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "Desculpe, não consegui processar sua solicitação no momento."
    
    # Ferramentas específicas do nutricionista
    def _calculate_calories(self, user_profile: Dict[str, Any]) -> Optional[int]:
        """Calcula necessidades calóricas diárias"""
        try:
            age = user_profile.get('age')
            weight = user_profile.get('weight')
            height = user_profile.get('height')
            gender = user_profile.get('gender')
            activity_level = user_profile.get('activity_level', 'moderate')
            
            if not all([age, weight, height, gender]):
                return None
            
            # Fórmula de Harris-Benedict revisada
            if gender.lower() == 'male':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
            # Fatores de atividade
            activity_factors = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725,
                'very_active': 1.9
            }
            
            factor = activity_factors.get(activity_level, 1.55)
            daily_calories = int(bmr * factor)
            
            return daily_calories
            
        except Exception as e:
            logger.error(f"Error calculating calories: {str(e)}")
            return None
    
    def _calculate_macros(self, calories: int, user_profile: Dict[str, Any]) -> Dict[str, int]:
        """Calcula distribuição de macronutrientes"""
        goal = user_profile.get('goal', 'maintain')
        
        # Distribuições baseadas no objetivo
        macro_distributions = {
            'lose_weight': {'protein': 0.3, 'carbs': 0.4, 'fat': 0.3},
            'gain_muscle': {'protein': 0.25, 'carbs': 0.45, 'fat': 0.3},
            'maintain': {'protein': 0.2, 'carbs': 0.5, 'fat': 0.3}
        }
        
        distribution = macro_distributions.get(goal, macro_distributions['maintain'])
        
        # Calcular gramas de cada macronutriente
        protein_g = int((calories * distribution['protein']) / 4)  # 4 cal/g
        carbs_g = int((calories * distribution['carbs']) / 4)      # 4 cal/g
        fat_g = int((calories * distribution['fat']) / 9)          # 9 cal/g
        
        return {
            'protein': protein_g,
            'carbs': carbs_g,
            'fat': fat_g
        }
    
    def _create_meal_plan(self, user_profile: Dict[str, Any], calories: int, macros: Dict[str, int]) -> Dict[str, Any]:
        """Cria plano de refeições básico"""
        # Plano simplificado - em implementação real, seria mais complexo
        return {
            'breakfast': {
                'calories': int(calories * 0.25),
                'suggestions': ['Aveia com frutas', 'Ovos mexidos com torrada integral']
            },
            'lunch': {
                'calories': int(calories * 0.35),
                'suggestions': ['Salada com proteína', 'Prato balanceado com legumes']
            },
            'dinner': {
                'calories': int(calories * 0.30),
                'suggestions': ['Peixe grelhado com vegetais', 'Frango com quinoa']
            },
            'snacks': {
                'calories': int(calories * 0.10),
                'suggestions': ['Frutas', 'Castanhas', 'Iogurte natural']
            }
        }
    
    def _analyze_nutrition(self, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa valor nutricional de alimentos"""
        # Implementação básica - expandir conforme necessário
        return {'analysis': 'Análise nutricional em desenvolvimento'}
    
    def _assess_health_status(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia status de saúde baseado nos dados fornecidos"""
        # Implementação básica - expandir conforme necessário
        return {'status': 'Avaliação de saúde em desenvolvimento'}
    
    def _create_health_assessment_prompt(self, health_data: Dict[str, Any]) -> str:
        """Cria prompt para avaliação de saúde"""
        return f"""
        Com base nos dados do usuário:
        - Idade: {health_data.get('age', 'não informado')}
        - Peso: {health_data.get('weight', 'não informado')} kg
        - Altura: {health_data.get('height', 'não informado')} cm
        - IMC: {health_data.get('imc', 'não calculado')} ({health_data.get('imc_category', '')})
        - Nível de atividade: {health_data.get('activity_level', 'não informado')}
        
        Forneça uma avaliação nutricional personalizada e recomendações gerais de saúde.
        Seja empático, profissional e baseie-se em evidências científicas.
        """
    
    def _create_meal_planning_prompt(self, nutrition_plan: Dict[str, Any]) -> str:
        """Cria prompt para planejamento de refeições"""
        return f"""
        Baseado no plano nutricional calculado:
        - Calorias diárias: {nutrition_plan.get('daily_calories')} kcal
        - Proteínas: {nutrition_plan['macros'].get('protein')}g
        - Carboidratos: {nutrition_plan['macros'].get('carbs')}g
        - Gorduras: {nutrition_plan['macros'].get('fat')}g
        
        Crie um plano de refeições detalhado e personalizado.
        Inclua sugestões práticas e opções variadas.
        """
    
    def _create_consultation_prompt(self, user_message: str, user_profile: Dict[str, Any]) -> str:
        """Cria prompt para consulta geral"""
        return f"""
        Pergunta do usuário: {user_message}
        
        Perfil do usuário: {user_profile}
        
        Forneça uma resposta profissional e personalizada como nutricionista.
        Considere o perfil do usuário em sua resposta.
        """
    
    def _create_education_prompt(self, user_message: str) -> str:
        """Cria prompt para educação nutricional"""
        return f"""
        Tópico solicitado: {user_message}
        
        Forneça informações educativas sobre nutrição de forma clara e acessível.
        Base sua resposta em evidências científicas e seja didático.
        """


def create_nutritionist_agent() -> NutritionistAgent:
    """Factory function para criar instância do agente nutricionista"""
    return NutritionistAgent()
