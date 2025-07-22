"""
Sistema de Cadastro para ShapeMateAI
Ponto de entrada para o processo de cadastro de usuários
"""

import sys
import os

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.services import get_database_service
from database.schemas import ValidationError
from database.config import GENDER_DISPLAY, GOAL_DISPLAY, ACTIVITY_LEVEL_DISPLAY


class RegistrationSystem:
    """Sistema de cadastro de usuários"""
    
    def __init__(self):
        self.db_service = get_database_service()
    
    def get_form_options(self):
        """Retorna as opções para os formulários"""
        return {
            'genders': GENDER_DISPLAY,
            'goals': GOAL_DISPLAY,
            'activity_levels': ACTIVITY_LEVEL_DISPLAY
        }
    
    def register_new_user(self, user_data):
        """
        Registra um novo usuário completo
        
        Args:
            user_data: Dicionário com todos os dados do usuário
            
        Returns:
            dict: Resultado da operação com success, message e user_id (se sucesso)
        """
        try:
            # Separar dados de login e perfil
            email = user_data.get('email')
            password = user_data.get('password')
            
            profile_data = {
                'name': user_data.get('name'),
                'age': user_data.get('age'),
                'gender': user_data.get('gender'),
                'weight': user_data.get('weight'),
                'height': user_data.get('height'),
                'primary_goal': user_data.get('primary_goal'),
                'activity_level': user_data.get('activity_level'),
                'dietary_restrictions': user_data.get('dietary_restrictions', ''),
                'health_conditions': user_data.get('health_conditions', ''),
                'other_notes': user_data.get('other_notes', '')
            }
            
            # Registrar usuário
            user_id, message = self.db_service.register_user(email, password, profile_data)
            
            if user_id:
                return {
                    'success': True,
                    'message': message,
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'message': message
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Erro interno: {str(e)}"
            }
    
    def authenticate_user(self, email, password):
        """
        Autentica um usuário
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            dict: Resultado da autenticação
        """
        try:
            user_data, message = self.db_service.login_user(email, password)
            
            if user_data:
                return {
                    'success': True,
                    'message': message,
                    'user_data': user_data
                }
            else:
                return {
                    'success': False,
                    'message': message
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Erro interno: {str(e)}"
            }
    
    def check_system_health(self):
        """Verifica se o sistema está funcionando"""
        return self.db_service.check_database_health()


def main():
    """Função principal para testes do sistema"""
    print("=== Sistema de Cadastro ShapeMateAI ===")
    
    registration = RegistrationSystem()
    
    # Verificar saúde do sistema
    is_healthy, health_message = registration.check_system_health()
    print(f"Status do sistema: {health_message}")
    
    if not is_healthy:
        print("Sistema não está funcionando corretamente!")
        return
    
    # Exemplo de uso
    print("\nSistema pronto para receber cadastros!")
    print("Use a interface web para interagir com o sistema.")


if __name__ == "__main__":
    main()
