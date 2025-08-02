#!/usr/bin/env python3
"""
Teste rápido para verificar carregamento das configurações
"""
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core import AgentType
from core.config_loader import get_config_loader

def test_config_loading():
    print("=== Teste de Carregamento de Configurações ===")
    
    try:
        config_loader = get_config_loader()
        print("✅ Config loader criado com sucesso")
        
        # Testar carregamento do nutricionista
        print("\n🔍 Testando carregamento do Nutricionista...")
        nutritionist_config = config_loader.load_agent_config(AgentType.NUTRITIONIST)
        print(f"✅ Nutricionista carregado: {nutritionist_config.name}")
        print(f"   Tarefas suportadas: {[task.value for task in nutritionist_config.supported_tasks]}")
        
        # Testar carregamento do daily assistant
        print("\n🔍 Testando carregamento do Daily Assistant...")
        daily_config = config_loader.load_agent_config(AgentType.DAILY_ASSISTANT)
        print(f"✅ Daily Assistant carregado: {daily_config.name}")
        print(f"   Tarefas suportadas: {[task.value for task in daily_config.supported_tasks]}")
        
        print("\n🎉 Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config_loading()
    exit(0 if success else 1)
