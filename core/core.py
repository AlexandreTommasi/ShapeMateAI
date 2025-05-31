# agent/core.py
from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import json
import uuid

from config.settings import API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from agent.nutritionist.nutritionist_prompts import SYSTEM_PROMPT as NUTRITIONIST_PROMPT
from core.memory import ConversationMemory
from utils.cost_tracker import CostTracker
from agent.nutritionist.user_profile import UserProfile

# Inicializa o rastreador de custos
cost_tracker = CostTracker(model_name=MODEL_NAME)

# Modelo LLM 
llm = ChatOpenAI(
    model_name=MODEL_NAME,
    openai_api_key=API_KEY,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    openai_api_base="https://api.deepseek.com/v1",
)

# Definimos o tipo do estado como um dicionário para compatibilidade com LangGraph
class ConversationStateDict(TypedDict, total=False):
    memory: ConversationMemory
    current_step: str
    user_message: str
    ai_response: str
    cost_info: Dict[str, Any]
    user_id: str
    user_profile: Dict[str, Any]
    is_first_interaction: bool

# Nó para processar a entrada do usuário
def process_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """Processa a mensagem do usuário e atualiza o estado."""
    user_message = state["user_message"]
    is_first_interaction = len(state["memory"].get_message_history()) <= 1
    
    # Carregar perfil do usuário se disponível
    user_profile = None
    if "user_id" in state:
        user_profile = UserProfile.load_profile(state["user_id"])
    
    # Adicionar mensagem à memória
    state["memory"].add_user_message(user_message)
    
    # Atualizar estado
    new_state = state.copy()
    new_state["current_step"] = "generate_response"
    new_state["is_first_interaction"] = is_first_interaction
    new_state["user_profile"] = user_profile or {}
    
    return new_state

# Nó para gerar a resposta do nutricionista
def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Gera uma resposta baseada no histórico da conversa."""
    message_history = state["memory"].get_message_history()
    
    # Adicionar informações do perfil do usuário ao contexto se disponível
    if state["user_profile"]:
        profile = state["user_profile"]
        profile_context = f"Contexto do usuário: {json.dumps(profile, indent=2, ensure_ascii=False)}"
        
        message_history = message_history.copy()
        message_history.insert(1, SystemMessage(content=profile_context))
    
    # Calcular tokens de entrada para rastreamento de custos
    input_text = " ".join([msg.content for msg in message_history])
    input_tokens = cost_tracker.estimate_tokens(input_text)
    
    # Gerar resposta
    response = llm.invoke(message_history)
    ai_response = response.content
    
    # Adicionar resposta à memória
    state["memory"].add_ai_message(ai_response)
    
    # Calcular custo
    output_tokens = cost_tracker.estimate_tokens(ai_response)
    cost_info = cost_tracker.calculate_cost(input_tokens, output_tokens)
    
    # Atualizar estado
    new_state = state.copy()
    new_state["ai_response"] = ai_response
    new_state["current_step"] = "end"
    new_state["cost_info"] = cost_info
    
    return new_state

# Função para construir o grafo conversacional
def build_conversation_graph():
    """Constrói um grafo de conversa para o nutricionista."""
    # Inicializar grafo
    workflow = StateGraph(ConversationStateDict)
    
    # Definir nós
    workflow.add_node("process_input", process_input)
    workflow.add_node("generate_response", generate_response)
    
    # Definir transições
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Definir ponto de entrada
    workflow.set_entry_point("process_input")
    
    # Compilar grafo
    compiled_graph = workflow.compile()
    
    return compiled_graph, ConversationMemory(NUTRITIONIST_PROMPT)

# Função para criar um agente nutricionista
def create_nutritionist_agent():
    """Cria um agente nutricionista."""
    graph, memory = build_conversation_graph()
    
    def chat_agent(message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Função que processa uma mensagem e retorna a resposta.
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário para acessar seu perfil (opcional)
        """
        # Gerar um ID de usuário se não for fornecido
        if user_id is None:
            user_id = str(uuid.uuid4())
            
        # Estado inicial
        state = {
            "memory": memory,
            "current_step": "process_input",
            "user_message": message,
            "is_first_interaction": len(memory.get_message_history()) <= 1,
            "user_id": user_id,
        }
        
        # Executa o grafo conversacional
        result = graph.invoke(state)
        
        # Retorna o resultado final
        return {
            "response": result["ai_response"],
            "cost": result["cost_info"],
            "user_id": user_id
        }
    
    return chat_agent