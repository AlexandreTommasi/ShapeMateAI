"""
Daily Assistant Agent implementation
Specialized agent for daily nutrition support, food substitutions and practical guidance
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
import re

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

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.core import BaseAgent, AgentConfig, AgentState, AgentType, TaskType
from core.config_loader import get_config_loader

logger = logging.getLogger(__name__)


class DailyAssistantAgent(BaseAgent):
    """Agente especializado em suporte nutricional diário e substituições alimentares"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            # Carregar configuração padrão do arquivo YAML
            config_loader = get_config_loader()
            config = config_loader.load_agent_config(AgentType.DAILY_ASSISTANT)
        
        super().__init__(config)
        
        # Ferramentas específicas do assistente diário
        self.daily_tools = {
            'food_substitution': self._analyze_food_substitution,
            'menu_analyzer': self._analyze_restaurant_menu,
            'shopping_list_generator': self._generate_shopping_list,
            'recipe_finder': self._find_compatible_recipes,
            'equivalence_calculator': self._calculate_food_equivalences,
            'diet_adherence_checker': self._check_diet_adherence
        }
        
        # Base de dados de substituições alimentares
        self.substitution_database = self._load_substitution_database()
        
        # Categorias de análise de cardápios
        self.menu_categories = {
            'very_compatible': 'Totalmente compatível com sua dieta',
            'compatible_with_adjustments': 'Compatível com pequenos ajustes',
            'partially_compatible': 'Parcialmente compatível - cuidado com as porções',
            'not_recommended': 'Não recomendado para sua dieta atual'
        }
    
    def _build_graph(self):
        """Constrói o grafo de estados do assistente diário"""
        if not LANGGRAPH_AVAILABLE:
            logger.warning("Langgraph not available, using simple processing")
            self.graph = None
            return
            
        workflow = StateGraph(AgentState)
        
        # Nós do grafo
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("handle_substitution", self._handle_substitution)
        workflow.add_node("analyze_menu", self._analyze_menu)
        workflow.add_node("generate_shopping_list", self._generate_shopping_list_node)
        workflow.add_node("find_recipes", self._find_recipes_node)
        workflow.add_node("check_adherence", self._check_adherence_node)
        workflow.add_node("provide_general_support", self._provide_general_support)
        workflow.add_node("finalize_response", self._finalize_response)
        
        # Ponto de entrada
        workflow.set_entry_point("analyze_request")
        
        # Transições condicionais
        workflow.add_conditional_edges(
            "analyze_request",
            self._route_based_on_request,
            {
                "substitution": "handle_substitution",
                "menu_analysis": "analyze_menu",
                "shopping_list": "generate_shopping_list",
                "recipe_search": "find_recipes",
                "adherence_check": "check_adherence",
                "general_support": "provide_general_support"
            }
        )
        
        # Transições para finalização
        for node in ["handle_substitution", "analyze_menu", "generate_shopping_list", 
                    "find_recipes", "check_adherence", "provide_general_support"]:
            workflow.add_edge(node, "finalize_response")
        
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
            logger.error(f"Erro crítico no DailyAssistantAgent: {str(e)}")
            # Propagar erro em vez de fallback
            raise RuntimeError(f"Falha no processamento da mensagem: {str(e)}") from e
    
    def _process_with_llm(self, state: AgentState, messages: List[BaseMessage]) -> AgentState:
        """Processa mensagem diretamente com a LLM usando histórico completo"""
        try:
            # Analisar tipo de solicitação
            request_type = self._detect_request_type(state['messages'][-1].content)
            
            # Processar baseado no tipo de solicitação
            if request_type == 'substitution':
                response = self._handle_substitution_simple(state)
            elif request_type == 'menu_analysis':
                response = self._handle_menu_analysis_simple(state)
            elif request_type == 'shopping_list':
                response = self._handle_shopping_list_simple(state)
            elif request_type == 'recipe_search':
                response = self._handle_recipe_search_simple(state)
            else:
                # Usar LLM diretamente para casos gerais
                llm_response = self.llm.invoke(messages)
                response = llm_response.content
            
            # Adicionar resposta ao estado
            state['messages'].append(AIMessage(content=response))
            state['confidence_score'] = 0.9
            state['tools_used'] = [request_type]
            
            return state
            
        except Exception as e:
            logger.error(f"Error in LLM processing: {str(e)}")
            error_response = AIMessage(
                content="Desculpe, não consegui processar sua solicitação no momento. "
                       "Tente novamente ou reformule sua pergunta."
            )
            state['messages'].append(error_response)
            state['confidence_score'] = 0.1
            return state
    
    def _detect_request_type(self, message: str) -> str:
        """Detecta o tipo de solicitação do usuário"""
        message_lower = message.lower()
        
        # Palavras-chave para substituições
        substitution_keywords = ['substituir', 'trocar', 'substituto', 'no lugar de', 'em vez de', 'posso usar']
        if any(keyword in message_lower for keyword in substitution_keywords):
            return 'substitution'
        
        # Palavras-chave para análise de cardápio
        menu_keywords = ['cardápio', 'menu', 'restaurante', 'pode comer', 'posso pedir']
        if any(keyword in message_lower for keyword in menu_keywords):
            return 'menu_analysis'
        
        # Palavras-chave para lista de compras
        shopping_keywords = ['lista de compras', 'comprar', 'mercado', 'ingredientes']
        if any(keyword in message_lower for keyword in shopping_keywords):
            return 'shopping_list'
        
        # Palavras-chave para receitas
        recipe_keywords = ['receita', 'como fazer', 'preparar', 'cozinhar']
        if any(keyword in message_lower for keyword in recipe_keywords):
            return 'recipe_search'
        
        return 'general_support'
    
    def _handle_substitution_simple(self, state: AgentState) -> str:
        """Maneja substituições alimentares de forma simplificada"""
        user_message = state['messages'][-1].content
        user_profile = state.get('user_profile', {})
        
        # Extrair alimentos mencionados
        foods_mentioned = self._extract_foods_from_text(user_message)
        
        if not foods_mentioned:
            return """Para ajudar com substituições, preciso saber quais alimentos você quer substituir. 

Por exemplo:
- "Posso trocar arroz por quinoa?"
- "O que usar no lugar de açúcar?"
- "Tenho apenas frango, posso substituir o peixe da dieta?"

Qual alimento você gostaria de substituir?"""
        
        # Gerar sugestões de substituição
        substitutions = []
        for food in foods_mentioned:
            suggestions = self._get_substitution_suggestions(food, user_profile)
            if suggestions:
                substitutions.extend(suggestions)
        
        if substitutions:
            response = "🔄 **Substituições Sugeridas:**\n\n"
            for i, sub in enumerate(substitutions[:3], 1):  # Limitar a 3 sugestões
                response += f"**{i}. {sub['original']} → {sub['substitute']}**\n"
                response += f"✅ {sub['reason']}\n"
                response += f"📊 {sub['nutritional_info']}\n\n"
            
            response += "💡 **Dica:** Sempre mantenha as porções adequadas à sua dieta!"
            return response
        else:
            return f"""Não encontrei substituições específicas para os alimentos mencionados. 

Mas posso ajudar com:
- Proteínas: frango ↔ peixe ↔ ovos ↔ leguminosas
- Carboidratos: arroz ↔ quinoa ↔ batata-doce
- Gorduras saudáveis: azeite ↔ abacate ↔ castanhas

Pode ser mais específico sobre qual alimento quer substituir?"""
    
    def _handle_menu_analysis_simple(self, state: AgentState) -> str:
        """Analisa cardápios de forma simplificada"""
        user_message = state['messages'][-1].content
        user_profile = state.get('user_profile', {})
        
        # Simular análise de cardápio
        return """📋 **Análise de Cardápio**

Para analisar um cardápio específico, compartilhe comigo:

1. **Nome do restaurante** (se possível)
2. **Pratos disponíveis** que te interessam
3. **Seu objetivo atual** (manter peso, emagrecer, etc.)

**Dicas gerais para escolhas em restaurantes:**

✅ **Boas opções:**
- Grelhados (frango, peixe, carne magra)
- Saladas com proteína
- Vegetais refogados ou no vapor
- Pratos com quinoa ou arroz integral

⚠️ **Cuidado com:**
- Frituras e empanados
- Molhos cremosos
- Pratos muito calóricos
- Bebidas açucaradas

Compartilhe o cardápio que você quer analisar e te ajudo a escolher as melhores opções! 🍽️"""
    
    def _handle_shopping_list_simple(self, state: AgentState) -> str:
        """Gera listas de compras simplificadas"""
        user_profile = state.get('user_profile', {})
        
        # Lista básica baseada no perfil
        basic_list = {
            'Proteínas': ['Frango', 'Ovos', 'Peixe', 'Feijão/Lentilha'],
            'Carboidratos': ['Arroz integral', 'Aveia', 'Batata-doce', 'Quinoa'],
            'Vegetais': ['Brócolis', 'Cenoura', 'Espinafre', 'Tomate'],
            'Frutas': ['Banana', 'Maçã', 'Frutas vermelhas', 'Abacate'],
            'Gorduras saudáveis': ['Azeite extra virgem', 'Castanhas', 'Sementes'],
            'Temperos': ['Alho', 'Cebola', 'Ervas finas', 'Limão']
        }
        
        response = "🛒 **Lista de Compras Inteligente**\n\n"
        
        for category, items in basic_list.items():
            response += f"**{category}:**\n"
            for item in items:
                response += f"• {item}\n"
            response += "\n"
        
        response += """💡 **Dicas de compra:**
- Prefira produtos da estação (mais baratos e frescos)
- Compre proteínas em promoção e congele
- Varie as cores dos vegetais para mais nutrientes
- Leia sempre os rótulos dos industrializados

Quer uma lista personalizada para sua dieta específica? Me conte seus objetivos e preferências! 🎯"""
        
        return response
    
    def _handle_recipe_search_simple(self, state: AgentState) -> str:
        """Busca receitas compatíveis de forma simplificada"""
        user_message = state['messages'][-1].content
        user_profile = state.get('user_profile', {})
        
        # Receitas básicas saudáveis
        recipes = [
            {
                'name': 'Frango Grelhado com Legumes',
                'prep_time': '25 min',
                'ingredients': 'Peito de frango, brócolis, cenoura, azeite, alho',
                'calories': '~350 kcal'
            },
            {
                'name': 'Salada Completa',
                'prep_time': '15 min', 
                'ingredients': 'Mix de folhas, tomate, pepino, grão-de-bico, azeite',
                'calories': '~280 kcal'
            },
            {
                'name': 'Omelete Nutritiva',
                'prep_time': '10 min',
                'ingredients': '2 ovos, espinafre, tomate, queijo branco',
                'calories': '~220 kcal'
            }
        ]
        
        response = "👩‍🍳 **Receitas Compatíveis com sua Dieta**\n\n"
        
        for recipe in recipes:
            response += f"**{recipe['name']}** ({recipe['prep_time']})\n"
            response += f"🥘 Ingredientes: {recipe['ingredients']}\n"
            response += f"⚡ {recipe['calories']}\n\n"
        
        response += """🔍 **Para receitas específicas:**
- Me diga que ingredientes você tem em casa
- Qual refeição você quer preparar (café, almoço, jantar)
- Se tem alguma restrição alimentar
- Quanto tempo tem disponível

Assim posso sugerir receitas mais personalizadas! 🎯"""
        
        return response
    
    def _load_substitution_database(self) -> Dict[str, List[Dict[str, str]]]:
        """Carrega base de dados de substituições alimentares"""
        return {
            'arroz': [
                {'substitute': 'quinoa', 'ratio': '1:1', 'reason': 'Mais proteína e fibras'},
                {'substitute': 'batata-doce', 'ratio': '100g:80g', 'reason': 'Menor índice glicêmico'},
                {'substitute': 'couve-flor refogada', 'ratio': '1:1', 'reason': 'Muito menos carboidratos'}
            ],
            'açúcar': [
                {'substitute': 'mel', 'ratio': '1:0.7', 'reason': 'Menos processado, mais antioxidantes'},
                {'substitute': 'tâmaras', 'ratio': '1 colher:2 tâmaras', 'reason': 'Fibras e minerais'},
                {'substitute': 'stevia', 'ratio': '1:0.1', 'reason': 'Zero calorias, natural'}
            ],
            'farinha de trigo': [
                {'substitute': 'farinha de aveia', 'ratio': '1:1', 'reason': 'Mais fibras e proteínas'},
                {'substitute': 'farinha de amêndoas', 'ratio': '1:0.8', 'reason': 'Low carb, gorduras boas'},
                {'substitute': 'farinha de coco', 'ratio': '1:0.3', 'reason': 'Muito menos carboidratos'}
            ]
        }
    
    def _extract_foods_from_text(self, text: str) -> List[str]:
        """Extrai nomes de alimentos do texto"""
        # Lista básica de alimentos comuns
        common_foods = [
            'arroz', 'feijão', 'frango', 'carne', 'peixe', 'ovo', 'ovos',
            'açúcar', 'sal', 'óleo', 'azeite', 'leite', 'queijo', 'pão',
            'farinha', 'batata', 'macarrão', 'massa', 'banana', 'maçã'
        ]
        
        text_lower = text.lower()
        found_foods = []
        
        for food in common_foods:
            if food in text_lower:
                found_foods.append(food)
        
        return found_foods
    
    def _get_substitution_suggestions(self, food: str, user_profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """Obtém sugestões de substituição para um alimento"""
        substitutions = self.substitution_database.get(food, [])
        
        # Formatar sugestões
        formatted_suggestions = []
        for sub in substitutions:
            formatted_suggestions.append({
                'original': food,
                'substitute': sub['substitute'],
                'reason': sub['reason'],
                'nutritional_info': f"Proporção: {sub['ratio']}"
            })
        
        return formatted_suggestions
    
    # Métodos do grafo (para quando Langgraph estiver disponível)
    def _analyze_request(self, state: AgentState) -> AgentState:
        """Analisa o tipo de solicitação do usuário"""
        user_message = state['messages'][-1].content if state['messages'] else ""
        
        request_type = self._detect_request_type(user_message)
        state['context']['request_type'] = request_type
        
        return state
    
    def _route_based_on_request(self, state: AgentState) -> str:
        """Determina o próximo nó baseado no tipo de solicitação"""
        request_type = state['context'].get('request_type', 'general_support')
        
        route_mapping = {
            'substitution': 'substitution',
            'menu_analysis': 'menu_analysis', 
            'shopping_list': 'shopping_list',
            'recipe_search': 'recipe_search',
            'adherence_check': 'adherence_check'
        }
        
        return route_mapping.get(request_type, 'general_support')
    
    def _handle_substitution(self, state: AgentState) -> AgentState:
        """Maneja substituições alimentares (versão completa)"""
        # Implementação completa para quando usar Langgraph
        response = self._handle_substitution_simple(state)
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('food_substitution')
        state['confidence_score'] = 0.9
        return state
    
    def _analyze_menu(self, state: AgentState) -> AgentState:
        """Analisa cardápios de restaurantes (versão completa)"""
        response = self._handle_menu_analysis_simple(state)
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('menu_analyzer')
        state['confidence_score'] = 0.85
        return state
    
    def _generate_shopping_list_node(self, state: AgentState) -> AgentState:
        """Gera lista de compras (versão completa)"""
        response = self._handle_shopping_list_simple(state)
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('shopping_list_generator')
        state['confidence_score'] = 0.8
        return state
    
    def _find_recipes_node(self, state: AgentState) -> AgentState:
        """Busca receitas compatíveis (versão completa)"""
        response = self._handle_recipe_search_simple(state)
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('recipe_finder')
        state['confidence_score'] = 0.8
        return state
    
    def _check_adherence_node(self, state: AgentState) -> AgentState:
        """Verifica aderência à dieta"""
        response = "📊 **Verificação de Aderência à Dieta** em desenvolvimento..."
        state['messages'].append(AIMessage(content=response))
        state['tools_used'].append('diet_adherence_checker')
        state['confidence_score'] = 0.7
        return state
    
    def _provide_general_support(self, state: AgentState) -> AgentState:
        """Fornece suporte geral"""
        # Usar LLM para resposta geral
        messages_with_context = self.prepare_messages_with_context(state)
        response = self.llm.invoke(messages_with_context)
        state['messages'].append(AIMessage(content=response.content))
        state['confidence_score'] = 0.8
        return state
    
    def _finalize_response(self, state: AgentState) -> AgentState:
        """Finaliza a resposta"""
        # Adicionar sugestões de próximas ações se apropriado
        if 'substitution' in state.get('tools_used', []):
            state['next_action'] = 'track_substitution_success'
        elif 'menu_analyzer' in state.get('tools_used', []):
            state['next_action'] = 'follow_up_meal_choice'
        
        return state
    
    # Ferramentas específicas (versões básicas)
    def _analyze_food_substitution(self, original_food: str, available_foods: List[str], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa compatibilidade de substituições alimentares"""
        return {'status': 'Análise de substituição em desenvolvimento'}
    
    def _analyze_restaurant_menu(self, menu_items: List[str], user_diet: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa cardápio de restaurante"""
        return {'status': 'Análise de cardápio em desenvolvimento'}
    
    def _generate_shopping_list(self, diet_plan: Dict[str, Any], preferences: Dict[str, Any]) -> List[str]:
        """Gera lista de compras baseada na dieta"""
        return ['Lista de compras em desenvolvimento']
    
    def _find_compatible_recipes(self, available_ingredients: List[str], dietary_restrictions: List[str]) -> List[Dict[str, Any]]:
        """Encontra receitas compatíveis"""
        return [{'status': 'Busca de receitas em desenvolvimento'}]
    
    def _calculate_food_equivalences(self, food1: str, food2: str) -> Dict[str, Any]:
        """Calcula equivalências nutricionais entre alimentos"""
        return {'status': 'Cálculo de equivalências em desenvolvimento'}
    
    def _check_diet_adherence(self, meals_log: List[Dict[str, Any]], diet_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica aderência à dieta"""
        return {'status': 'Verificação de aderência em desenvolvimento'}


def create_daily_assistant_agent() -> DailyAssistantAgent:
    """Factory function para criar instância do assistente diário"""
    return DailyAssistantAgent()
