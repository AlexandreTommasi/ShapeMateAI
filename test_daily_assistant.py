#!/usr/bin/env python3
"""
Teste do Assistente do Dia-a-Dia
"""

from core.core import core_system, AgentType, TaskType, TaskPriority
from core.agents.daily_assistant_agent import DailyAssistantAgent

def test_daily_assistant():
    """Testa funcionalidades do assistente diário"""
    
    print("🏠 Testando Assistente do Dia-a-Dia...")
    
    try:
        # Registrar agente
        daily_agent = DailyAssistantAgent()
        core_system.register_agent(daily_agent)
        print("✅ Assistente registrado")
        
        # Criar configuração de sistema
        config = core_system.create_system_config(
            agent_type=AgentType.DAILY_ASSISTANT,
            task_type=TaskType.CONSULTATION,
            user_id='test_user',
            session_id='daily_test_session',
            priority=TaskPriority.MEDIUM
        )
        print("✅ Sistema configurado")
        
        # Teste 1: Substituição de alimento
        print("\n🔄 Teste 1: Substituição de alimento")
        result1 = core_system.process_user_message(
            user_id='test_user',
            session_id='daily_test_session',
            message='Posso trocar arroz por quinoa na minha dieta?',
            user_profile={'goal': 'lose_weight', 'dietary_restrictions': 'none'}
        )
        
        if result1['success']:
            print(f"   Resposta: {result1['response'][:150]}...")
            print("✅ Substituição processada com sucesso!")
        else:
            print(f"   Erro: {result1.get('error')}")
        
        # Teste 2: Análise de cardápio
        print("\n📋 Teste 2: Análise de cardápio")
        result2 = core_system.process_user_message(
            user_id='test_user',
            session_id='daily_test_session',
            message='Vou almoçar num restaurante. O cardápio tem frango grelhado, lasanha e salada. O que posso pedir?',
            user_profile={'goal': 'lose_weight', 'dietary_restrictions': 'none'}
        )
        
        if result2['success']:
            print(f"   Resposta: {result2['response'][:150]}...")
            print("✅ Análise de cardápio realizada!")
        else:
            print(f"   Erro: {result2.get('error')}")
        
        # Teste 3: Lista de compras
        print("\n🛒 Teste 3: Lista de compras")
        result3 = core_system.process_user_message(
            user_id='test_user',
            session_id='daily_test_session',
            message='Preciso de uma lista de compras para a semana',
            user_profile={'goal': 'maintain', 'dietary_restrictions': 'lactose_intolerant'}
        )
        
        if result3['success']:
            print(f"   Resposta: {result3['response'][:150]}...")
            print("✅ Lista de compras gerada!")
        else:
            print(f"   Erro: {result3.get('error')}")
        
        # Teste 4: Receitas
        print("\n👩‍🍳 Teste 4: Busca de receitas")
        result4 = core_system.process_user_message(
            user_id='test_user',
            session_id='daily_test_session',
            message='Tenho frango e brócolis em casa. Que receita posso fazer?',
            user_profile={'goal': 'gain_muscle', 'dietary_restrictions': 'none'}
        )
        
        if result4['success']:
            print(f"   Resposta: {result4['response'][:150]}...")
            print("✅ Receitas sugeridas!")
        else:
            print(f"   Erro: {result4.get('error')}")
        
        # Verificar memória
        memory_info = core_system.get_session_memory_info('test_user', 'daily_test_session')
        print(f"\n🧠 Memória da sessão: {memory_info}")
        
        # Resumo da conversa
        summary = core_system.get_conversation_summary('test_user', 'daily_test_session', 4)
        print(f"\n📋 Resumo das últimas interações:")
        for i, msg in enumerate(summary[-4:], 1):
            print(f"   {i}. [{msg['type']}]: {msg['content'][:60]}...")
        
        print("\n🎯 Todos os testes do Assistente do Dia-a-Dia concluídos!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_daily_assistant()
