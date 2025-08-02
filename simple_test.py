"""
Teste direto e simples do agente nutricionista
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importações diretas
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI


class SimpleNutritionistAgent:
    """Agente nutricionista simplificado para teste"""
    
    def __init__(self):
        # Configurar LLM
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY não encontrada no .env")
        
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            temperature=0.7,
            max_tokens=2000,
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        self.system_prompt = """Você é um nutricionista virtual especializado e experiente. 
        Seu objetivo é fornecer orientações nutricionais personalizadas, criar planos alimentares 
        e educar os usuários sobre hábitos alimentares saudáveis.
        
        Características:
        - Empático e compreensivo
        - Baseado em evidências científicas
        - Focado na saúde e bem-estar do usuário
        - Capaz de adaptar recomendações ao perfil individual
        
        Sempre considere o perfil do usuário, suas metas, restrições alimentares e preferências.
        Seja prático e ofereça soluções aplicáveis ao dia a dia."""
    
    def process_message(self, user_message: str, user_profile: Dict[str, Any] = None) -> str:
        """Processa uma mensagem do usuário"""
        try:
            # Criar contexto
            context = self._create_context(user_message, user_profile or {})
            
            # Gerar resposta
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=context)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"Erro ao processar mensagem: {str(e)}"
    
    def _create_context(self, user_message: str, user_profile: Dict[str, Any]) -> str:
        """Cria contexto estruturado"""
        context_parts = [f"PERGUNTA DO USUÁRIO: {user_message}"]
        
        if user_profile:
            user_info = []
            for key, value in user_profile.items():
                if value:
                    user_info.append(f"{key.replace('_', ' ').title()}: {value}")
            
            if user_info:
                context_parts.append(f"PERFIL DO USUÁRIO:\n" + "\n".join(user_info))
        
        return "\n\n".join(context_parts)


def main():
    """Função principal do teste"""
    print("=== Teste Simples do Nutricionista ===")
    print("Digite 'sair' para encerrar\n")
    
    try:
        agent = SimpleNutritionistAgent()
        print("✅ Nutricionista conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # Perfil de exemplo
    user_profile = {
        'age': 30,
        'weight': '70 kg',
        'height': '175 cm',
        'gender': 'feminino',
        'activity_level': 'moderado',
        'goal': 'manter peso'
    }
    
    print(f"Perfil: {user_profile}")
    print("\nComo posso ajudar com sua nutrição?\n")
    
    while True:
        try:
            user_input = input("Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\nObrigado por usar o ShapeMateAI! Até logo! 👋")
                break
            
            if not user_input:
                continue
            
            print("\nNutricionista: ", end="", flush=True)
            response = agent.process_message(user_input, user_profile)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nEncerrando... Até logo! 👋")
            break
        except Exception as e:
            print(f"\nErro: {e}")


if __name__ == "__main__":
    main()
