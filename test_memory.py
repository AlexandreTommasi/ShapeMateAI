#!/usr/bin/env python3
"""
Teste do sistema de memória dos agentes
"""

from core.core import core_system, AgentType, TaskType, TaskPriority
from web.app import SimpleNutritionistAgent

def test_memory_system():
    """Testa se o sistema de memória está funcionando"""
    
    print("🧠 Testando sistema de memória...")
    
    try:
        # Registrar agente
        agent = SimpleNutritionistAgent()
        core_system.register_agent(agent)
        print("✅ Agente registrado")
        
        # Criar configuração de sistema
        config = core_system.create_system_config(
            agent_type=AgentType.NUTRITIONIST,
            task_type=TaskType.CONSULTATION,
            user_id='test_user',
            session_id='test_session',
            priority=TaskPriority.MEDIUM
        )
        print("✅ Sistema configurado")
        
        # Primeira mensagem
        result1 = core_system.process_user_message(
            user_id='test_user',
            session_id='test_session',
            message='Olá, me chamo João e tenho 25 anos',
            user_profile={'name': 'João', 'age': 25}
        )
        
        print("📝 Primeira mensagem processada")
        memory_info = core_system.get_session_memory_info('test_user', 'test_session')
        print(f"   Memória: {memory_info}")
        
        if result1['success']:
            print(f"   Resposta: {result1['response'][:100]}...")
        else:
            print(f"   Erro: {result1.get('error')}")
        
        # Segunda mensagem - teste de memória
        result2 = core_system.process_user_message(
            user_id='test_user',
            session_id='test_session',
            message='Qual é meu nome?',
            user_profile={'name': 'João', 'age': 25}
        )
        
        print("🧠 Segunda mensagem processada (teste de memória)")
        memory_info = core_system.get_session_memory_info('test_user', 'test_session')
        print(f"   Memória: {memory_info}")
        
        if result2['success']:
            print(f"   Resposta: {result2['response'][:100]}...")
            # Verificar se a IA lembrou do nome
            if 'João' in result2['response'] or 'joão' in result2['response']:
                print("✅ IA LEMBROU DO NOME! Sistema de memória funcionando!")
            else:
                print("❌ IA não lembrou do nome. Verificar implementação.")
        else:
            print(f"   Erro: {result2.get('error')}")
        
        # Resumo da conversa
        summary = core_system.get_conversation_summary('test_user', 'test_session', 5)
        print("\n📋 Resumo da conversa:")
        for i, msg in enumerate(summary, 1):
            print(f"   {i}. [{msg['type']}]: {msg['content'][:50]}...")
        
        print("\n🎯 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_system()
