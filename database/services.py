"""
Serviços do banco de dados para ShapeMateAI
Camada de serviço que abstrai operações complexas do banco
"""

from .models import Database
from .schemas import UserSchema, ProfileSchema, ChatSchema, ValidationError
from .config import DB_PATH
import os


class DatabaseService:
    """Serviço principal para operações do banco de dados"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.db = Database(self.db_path)
    
    def register_user(self, email, password, profile_data):
        """
        Registra um novo usuário completo (dados de login + perfil)
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            profile_data: Dicionário com dados do perfil
            
        Returns:
            tuple: (user_id, message) em caso de sucesso, (None, error_message) em caso de erro
        """
        try:
            # Validar dados do usuário
            user_data = UserSchema.validate_user_data(email, password)
            
            # Validar dados do perfil
            validated_profile = ProfileSchema.validate_profile_data(profile_data)
            
            # Criar usuário
            user_id, message = self.db.create_user(user_data['email'], user_data['password'])
            if not user_id:
                return None, message
            
            # Criar perfil
            profile_id, profile_message = self.db.create_user_profile(user_id, validated_profile)
            if not profile_id:
                # Se falhou ao criar perfil, deveria idealmente remover o usuário
                # Por simplicidade, vamos apenas retornar o erro
                return None, f"Usuário criado mas erro no perfil: {profile_message}"
            
            return user_id, "Cadastro realizado com sucesso!"
            
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro interno: {str(e)}"
    
    def login_user(self, email, password):
        """
        Autentica usuário e retorna dados do perfil
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            tuple: (user_data, message) em caso de sucesso, (None, error_message) em caso de erro
        """
        try:
            # Validar formato do email
            email = UserSchema.validate_email(email)
            
            # Autenticar
            user_id = self.db.authenticate_user(email, password)
            if not user_id:
                return None, "Email ou senha incorretos"
            
            # Buscar perfil completo
            profile = self.db.get_user_profile(user_id)
            if not profile:
                return None, "Erro ao carregar dados do usuário"
            
            profile['user_id'] = user_id
            return profile, "Login realizado com sucesso!"
            
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro interno: {str(e)}"
    
    def update_user_profile(self, user_id, profile_data):
        """
        Atualiza perfil do usuário (funcionalidade futura)
        
        Args:
            user_id: ID do usuário
            profile_data: Novos dados do perfil
            
        Returns:
            tuple: (success, message)
        """
        # Esta funcionalidade pode ser implementada no futuro
        return False, "Funcionalidade não implementada ainda"
    
    def create_chat_session_for_user(self, user_id, session_name=None):
        """
        Cria uma nova sessão de chat para o usuário
        
        Args:
            user_id: ID do usuário
            session_name: Nome da sessão (opcional)
            
        Returns:
            tuple: (session_id, message) em caso de sucesso, (None, error_message) em caso de erro
        """
        try:
            session_id, message = self.db.create_chat_session(user_id, session_name)
            return session_id, message
        except Exception as e:
            return None, f"Erro ao criar sessão: {str(e)}"
    
    def save_message_to_chat(self, session_id, message_type, content):
        """
        Salva mensagem no chat
        
        Args:
            session_id: ID da sessão
            message_type: 'user' ou 'assistant'
            content: Conteúdo da mensagem
            
        Returns:
            tuple: (message_id, message) em caso de sucesso, (None, error_message) em caso de erro
        """
        try:
            # Validar dados da mensagem
            validated_type = ChatSchema.validate_message_type(message_type)
            validated_content = ChatSchema.validate_message_content(content)
            
            message_id, message = self.db.save_chat_message(session_id, validated_type, validated_content)
            return message_id, message
            
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erro ao salvar mensagem: {str(e)}"
    
    def get_user_chat_history(self, session_id):
        """
        Obtém histórico de mensagens de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            list: Lista de mensagens ou lista vazia em caso de erro
        """
        try:
            return self.db.get_chat_history(session_id)
        except Exception as e:
            print(f"Erro ao obter histórico: {str(e)}")
            return []
    
    def get_user_sessions_list(self, user_id):
        """
        Obtém lista de sessões do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            list: Lista de sessões ou lista vazia em caso de erro
        """
        try:
            return self.db.get_user_sessions(user_id)
        except Exception as e:
            print(f"Erro ao obter sessões: {str(e)}")
            return []
    
    def check_database_health(self):
        """
        Verifica se o banco de dados está funcionando corretamente
        
        Returns:
            tuple: (is_healthy, message)
        """
        try:
            # Tenta fazer uma operação simples no banco
            conn = self.db.init_database()
            return True, "Banco de dados funcionando corretamente"
        except Exception as e:
            return False, f"Erro no banco de dados: {str(e)}"


# Instância global do serviço (singleton)
_db_service = None

def get_database_service():
    """
    Retorna a instância singleton do serviço de banco de dados
    
    Returns:
        DatabaseService: Instância do serviço
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
