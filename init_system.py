"""
Script de inicialização do ShapeMateAI
Use este script para inicializar e testar o sistema
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.services import get_database_service
from register.registration import RegistrationSystem


def check_system_requirements():
    """Verifica se todas as dependências estão instaladas"""
    missing_packages = []
    
    try:
        import flask
        import flask_cors
        import bcrypt
        import sqlite3
    except ImportError as e:
        missing_packages.append(str(e).split("'")[1])
    
    if missing_packages:
        print("❌ Pacotes faltando:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstale com: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True


def initialize_database():
    """Inicializa o banco de dados"""
    try:
        print("🗃️  Inicializando banco de dados...")
        db_service = get_database_service()
        is_healthy, message = db_service.check_database_health()
        
        if is_healthy:
            print("✅ Banco de dados inicializado com sucesso")
            return True
        else:
            print(f"❌ Erro no banco de dados: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")
        return False


def test_registration_system():
    """Testa o sistema de cadastro"""
    try:
        print("🧪 Testando sistema de cadastro...")
        registration = RegistrationSystem()
        
        # Testar dados de formulário
        form_options = registration.get_form_options()
        
        if form_options and 'genders' in form_options:
            print("✅ Sistema de cadastro funcionando")
            print(f"   - {len(form_options['genders'])} opções de gênero")
            print(f"   - {len(form_options['goals'])} objetivos disponíveis")
            print(f"   - {len(form_options['activity_levels'])} níveis de atividade")
            return True
        else:
            print("❌ Erro no sistema de cadastro")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar cadastro: {str(e)}")
        return False


def show_system_info():
    """Mostra informações sobre o sistema"""
    print("\n" + "="*50)
    print("🚀 SHAPEMATE AI - SISTEMA DE CADASTRO")
    print("="*50)
    print("📁 Estrutura do projeto:")
    print("   ├── database/         (Banco de dados SQLite)")
    print("   ├── register/         (Sistema de cadastro)")
    print("   ├── web/             (Interface web)")
    print("   ├── pyproject.toml   (Configuração uv/pip)")
    print("   └── requirements.txt (Dependências legacy)")
    print()
    print("🌐 Para iniciar o servidor web:")
    print("   cd web")
    print("   python app.py")
    print()
    print("🔗 Acesse: http://localhost:5000")
    print("="*50)


def create_test_user():
    """Cria um usuário de teste"""
    try:
        print("👤 Criando usuário de teste...")
        registration = RegistrationSystem()
        
        test_data = {
            'email': 'teste@shapemate.ai',
            'password': '123456',
            'name': 'Usuário Teste',
            'age': 25,
            'gender': 'masculino',
            'weight': 70.0,
            'height': 1.75,
            'primary_goal': 'perda_peso',
            'activity_level': 'moderado',
            'dietary_restrictions': 'Nenhuma',
            'health_conditions': '',
            'other_notes': 'Usuário criado para testes do sistema'
        }
        
        result = registration.register_new_user(test_data)
        
        if result['success']:
            print("✅ Usuário de teste criado com sucesso!")
            print("   📧 Email: teste@shapemate.ai")
            print("   🔑 Senha: 123456")
            return True
        else:
            if "já cadastrado" in result['message']:
                print("ℹ️  Usuário de teste já existe")
                print("   📧 Email: teste@shapemate.ai")
                print("   🔑 Senha: 123456")
                return True
            else:
                print(f"❌ Erro ao criar usuário: {result['message']}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {str(e)}")
        return False


def main():
    """Função principal"""
    show_system_info()
    
    print("🔍 Verificando sistema...")
    
    # Verificar dependências
    if not check_system_requirements():
        return
    
    # Inicializar banco
    if not initialize_database():
        return
    
    # Testar sistema de cadastro
    if not test_registration_system():
        return
    
    # Criar usuário de teste
    create_test_user()
    
    print("\n✅ Sistema inicializado com sucesso!")
    print("🚀 Execute 'python web/app.py' para iniciar o servidor")


if __name__ == "__main__":
    main()
