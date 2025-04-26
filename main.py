# main.py
from agent.core import build_conversation_graph
from agent.memory import ConversationMemory
from agent.prompts import SYSTEM_PROMPT, GREETING_PROMPT
from typing import Dict, Any

class ConversationalAgent:
    """Classe principal do agente conversacional."""
    
    def __init__(self):
        """Inicializa o agente com seu grafo e memória."""
        self.graph = build_conversation_graph()
        self.memory = ConversationMemory(SYSTEM_PROMPT)
        self.session_active = False
    
    def start_session(self) -> str:
        """Inicia uma nova sessão de conversa."""
        self.session_active = True
        # Retornamos uma mensagem de boas-vindas
        return GREETING_PROMPT
    
    def process_message(self, user_message: str) -> str:
        """Processa uma mensagem do usuário e retorna a resposta."""
        if not self.session_active:
            self.start_session()
        
        # Estado inicial para o grafo
        initial_state = {
            "memory": self.memory,
            "user_message": user_message,
            "ai_response": "",
            "current_step": "process_input",
            "should_continue": True
        }
        
        # Executamos o grafo
        final_state = self.graph.invoke(initial_state)
        
        # Retornamos a resposta
        return final_state["ai_response"]
    
    def end_session(self) -> str:
        """Encerra a sessão atual."""
        self.session_active = False
        self.memory.clear()
        return "Sessão encerrada. Obrigado pela conversa!"


# Exemplo de uso em uma interface de linha de comando
def cli_interface():
    """Interface de linha de comando simples para o agente."""
    agent = ConversationalAgent()
    print(agent.start_session())
    
    while True:
        user_input = input("\nVocê: ")
        
        if user_input.lower() in ["sair", "exit", "quit", "tchau"]:
            print("\nAssistente:", agent.end_session())
            break
        
        response = agent.process_message(user_input)
        print("\nAssistente:", response)

if __name__ == "__main__":
    cli_interface()