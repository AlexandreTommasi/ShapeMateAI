# agent/memory.py
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class ConversationMemory:
    """Classe para gerenciar o histórico da conversa."""
    
    def __init__(self, system_prompt: str):
        """Inicializa com um prompt de sistema."""
        self.messages: List[BaseMessage] = [SystemMessage(content=system_prompt)]
    
    def add_user_message(self, message: str) -> None:
        """Adiciona uma mensagem do usuário ao histórico."""
        self.messages.append(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Adiciona uma mensagem do AI ao histórico."""
        self.messages.append(AIMessage(content=message))
    
    def get_message_history(self) -> List[BaseMessage]:
        """Retorna todo o histórico de mensagens."""
        return self.messages
    
    def get_last_n_messages(self, n: int) -> List[BaseMessage]:
        """Retorna as últimas n mensagens."""
        return self.messages[-n:] if n < len(self.messages) else self.messages
    
    def clear(self) -> None:
        """Limpa o histórico, mantendo apenas o prompt de sistema."""
        system_prompt = next((msg for msg in self.messages if isinstance(msg, SystemMessage)), None)
        self.messages = [system_prompt] if system_prompt else []