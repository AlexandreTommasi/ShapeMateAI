"""
Ferramentas administrativas para o ShapeMateAI
Script para gerenciar contas de usuários no banco de dados
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.services import get_database_service
import sqlite3

class AdminTools:
    """Ferramentas administrativas para gerenciar usuários"""
    
    def __init__(self):
        self.db_service = get_database_service()
        self.db_path = self.db_service.db_path
    
    def list_users(self):
        """Lista todos os usuários cadastrados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.email, u.created_at, p.name, p.age, p.weight, p.height
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("❌ Nenhum usuário encontrado no banco de dados.")
            return []
        
        print("\n📋 USUÁRIOS CADASTRADOS:")
        print("=" * 80)
        print(f"{'ID':<8} {'EMAIL':<25} {'NOME':<20} {'CRIADO EM':<20}")
        print("-" * 80)
        
        for user in users:
            user_id = user[0][:8] + "..." if len(user[0]) > 8 else user[0]
            email = user[1]
            created_at = user[2]
            name = user[3] if user[3] else "N/A"
            
            print(f"{user_id:<8} {email:<25} {name:<20} {created_at:<20}")
        
        print("=" * 80)
        return users
    
    def delete_user_by_email(self, email):
        """Remove um usuário pelo email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se o usuário existe
            cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ Usuário com email '{email}' não encontrado.")
                return False
            
            user_id = user[0]
            
            # Confirmar exclusão
            print(f"\n⚠️  ATENÇÃO: Você está prestes a EXCLUIR permanentemente:")
            print(f"   📧 Email: {user[1]}")
            print(f"   🆔 ID: {user_id}")
            
            confirm = input("\n❓ Confirma a exclusão? Digite 'CONFIRMAR' para continuar: ")
            
            if confirm != "CONFIRMAR":
                print("❌ Operação cancelada.")
                return False
            
            # Excluir em ordem (devido às foreign keys)
            cursor.execute("DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id = ?)", (user_id,))
            cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            
            print(f"✅ Usuário '{email}' foi removido com sucesso!")
            print(f"   🗑️ Dados removidos: conta, perfil, sessões de chat e mensagens")
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao excluir usuário: {str(e)}")
            return False
        finally:
            conn.close()
    
    def delete_user_by_id(self, user_id):
        """Remove um usuário pelo ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se o usuário existe
            cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ Usuário com ID '{user_id}' não encontrado.")
                return False
            
            return self.delete_user_by_email(user[0])
            
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {str(e)}")
            return False
        finally:
            conn.close()
    
    def clear_all_users(self):
        """Remove TODOS os usuários (usar com cuidado!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Contar usuários
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                print("❌ Não há usuários para remover.")
                return False
            
            print(f"\n⚠️⚠️⚠️  ATENÇÃO MÁXIMA ⚠️⚠️⚠️")
            print(f"Você está prestes a EXCLUIR TODOS os {user_count} usuários!")
            print(f"Esta ação é IRREVERSÍVEL!")
            
            confirm1 = input("\n❓ Digite 'EXCLUIR TODOS' para continuar: ")
            if confirm1 != "EXCLUIR TODOS":
                print("❌ Operação cancelada.")
                return False
            
            confirm2 = input("❓ Tem certeza ABSOLUTA? Digite 'SIM TENHO CERTEZA': ")
            if confirm2 != "SIM TENHO CERTEZA":
                print("❌ Operação cancelada.")
                return False
            
            # Excluir tudo em ordem
            cursor.execute("DELETE FROM chat_messages")
            cursor.execute("DELETE FROM chat_sessions")
            cursor.execute("DELETE FROM user_profiles")
            cursor.execute("DELETE FROM users")
            
            conn.commit()
            
            print(f"✅ Todos os {user_count} usuários foram removidos!")
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao excluir usuários: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_database_stats(self):
        """Mostra estatísticas do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            profile_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chat_sessions")
            session_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            message_count = cursor.fetchone()[0]
            
            print("\n📊 ESTATÍSTICAS DO BANCO DE DADOS:")
            print("=" * 40)
            print(f"👥 Usuários: {user_count}")
            print(f"📋 Perfis: {profile_count}")
            print(f"💬 Sessões de Chat: {session_count}")
            print(f"💭 Mensagens: {message_count}")
            print("=" * 40)
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {str(e)}")
        finally:
            conn.close()


def main():
    """Menu principal das ferramentas administrativas"""
    admin = AdminTools()
    
    print("🔧 FERRAMENTAS ADMINISTRATIVAS - ShapeMateAI")
    print("=" * 50)
    
    while True:
        print("\n📋 OPÇÕES DISPONÍVEIS:")
        print("1. 📋 Listar todos os usuários")
        print("2. 📊 Ver estatísticas do banco")
        print("3. 🗑️ Remover usuário por email")
        print("4. 🗑️ Remover usuário por ID")
        print("5. ☢️ Remover TODOS os usuários")
        print("0. 🚪 Sair")
        
        choice = input("\n❓ Digite sua opção: ").strip()
        
        if choice == "0":
            print("👋 Até logo!")
            break
        elif choice == "1":
            admin.list_users()
        elif choice == "2":
            admin.get_database_stats()
        elif choice == "3":
            email = input("\n📧 Digite o email do usuário: ").strip()
            if email:
                admin.delete_user_by_email(email)
            else:
                print("❌ Email não pode estar vazio.")
        elif choice == "4":
            user_id = input("\n🆔 Digite o ID do usuário: ").strip()
            if user_id:
                admin.delete_user_by_id(user_id)
            else:
                print("❌ ID não pode estar vazio.")
        elif choice == "5":
            admin.clear_all_users()
        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
