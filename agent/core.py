# agent/core.py
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from config.settings import API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from agent.prompts import SYSTEM_PROMPT
from agent.memory import ConversationMemory

# Modelo LLM
llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=API_KEY,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS
)

# Estado do grafo conversacional
class ConversationState:
    """Classe que representa o estado da conversa no grafo."""
    
    def __init__(self):
        self.memory = ConversationMemory(SYSTEM_PROMPT)
        self.current_step = "process_input"
        self.user_message = ""
        self.ai_response = ""
        self.should_continue = True

# Nó para processar a entrada do usuário
def process_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """Processa a mensagem do usuário e atualiza o estado."""
    # Extraímos a mensagem do usuário do estado
    user_message = state["user_message"]
    
    # Adicionamos à memória
    state["memory"].add_user_message(user_message)
    
    return {
        **state,
        "current_step": "generate_response"
    }

# Nó para gerar a resposta do assistente
def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Gera uma resposta baseada no histórico da conversa."""
    # Obtemos o histórico completo
    message_history = state["memory"].get_message_history()
    
    # Enviamos para o LLM
    response = llm.invoke(message_history)
    
    # Extraímos o conteúdo da resposta
    ai_response = response.content
    
    # Atualizamos o estado
    state["memory"].add_ai_message(ai_response)
    state["ai_response"] = ai_response
    state["current_step"] = END
    
    return state

# Função para construir o grafo conversacional
def build_conversation_graph():
    """Constrói e retorna o grafo de conversa."""
    # Inicializamos o grafo
    graph = StateGraph(ConversationState)
    
    # Adicionamos os nós
    graph.add_node("process_input", process_input)
    graph.add_node("generate_response", generate_response)
    
    # Definimos as conexões
    graph.add_edge("process_input", "generate_response")
    graph.add_edge("generate_response", END)
    
    # Definimos o nó inicial
    graph.set_entry_point("process_input")
    
    # Compilamos o grafo
    return graph.compile()