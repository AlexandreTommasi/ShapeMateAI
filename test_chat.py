"""
Teste simples do chat com o agente nutricionista
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.core import CoreAgentSystem, AgentType, TaskType, TaskPriority
from core.agents.nutritionist_agent import create_nutritionist_agent

# Carregar variáveis de ambiente
load_dotenv()


def main():
    """Função principal do teste de chat"""
    print("=== Teste do Chat ShapeMateAI ===")
    print("Digite 'sair' para encerrar\n")
    
    # Inicializar sistema
    core_system = CoreAgentSystem()
    
    # Registrar agente nutricionista
    nutritionist_agent = create_nutritionist_agent()
    core_system.register_agent(nutritionist_agent)
    
    # Dados de exemplo do usuário
    user_profile = {
        'age': 30,
        'weight': 70,
        'height': 175,
        'gender': 'female',
        'activity_level': 'moderate',
        'goal': 'maintain',
        'dietary_restrictions': [],
        'food_allergies': []
    }
    
    user_id = "test_user_001"
    session_id = "session_001"
    
    # Criar configuração do sistema
    system_config = core_system.create_system_config(
        agent_type=AgentType.NUTRITIONIST,
        task_type=TaskType.CONSULTATION,
        user_id=user_id,
        session_id=session_id,
        priority=TaskPriority.MEDIUM
    )
    
    print(f"Agente nutricionista '{nutritionist_agent.config.name}' ativo!")
    print(f"Perfil: {user_profile['age']} anos, {user_profile['weight']}kg, {user_profile['height']}cm")
    print("Como posso ajudar com sua nutrição hoje?\n")
    
    # Loop de chat
    while True:
        try:
            # Entrada do usuário
            user_input = input("Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\nObrigado por usar o ShapeMateAI! Até logo! 👋")
                break
            
            if not user_input:
                continue
            
            # Processar mensagem
            print("\nNutricionista: ", end="", flush=True)
            
            result = core_system.process_user_message(
                user_id=user_id,
                session_id=session_id,
                message=user_input,
                user_profile=user_profile
            )
            
            if result['success']:
                print(result['response'])
                if result.get('confidence_score'):
                    print(f"\n[Confiança: {result['confidence_score']:.1%}]")
            else:
                print(f"Erro: {result.get('error', 'Erro desconhecido')}")
                print(result.get('response', 'Tente novamente.'))
            
            print()  # Linha em branco para separar
            
        except KeyboardInterrupt:
            print("\n\nEncerrando chat... Até logo! 👋")
            break
        except Exception as e:
            print(f"\nErro inesperado: {str(e)}")
            print("Tente novamente ou digite 'sair' para encerrar.\n")


if __name__ == "__main__":
    main()
