# agent/nutritionist/user_profile.py
"""
Módulo para gerenciar perfis de usuários para o agente nutricionista.
Permite armazenar e recuperar informações do cadastro do cliente.
"""

from typing import Dict, Any, Optional
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Diretório para armazenar os perfis de usuário
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "user_profiles")

# Garantir que o diretório exista
os.makedirs(PROFILES_DIR, exist_ok=True)

class UserProfile:
    """
    Classe para gerenciar o perfil do usuário com informações do cadastro.
    """
    
    @staticmethod
    def save_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Salva o perfil do usuário com informações do cadastro.
        
        Args:
            user_id: ID único do usuário
            profile_data: Dicionário com informações do perfil
            
        Returns:
            True se o perfil foi salvo com sucesso, False caso contrário
        """
        try:
            # Adicionar timestamp de criação/atualização
            profile_data['updated_at'] = datetime.now().isoformat()
            
            profile_path = os.path.join(PROFILES_DIR, f"{user_id}.json")
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Perfil do usuário {user_id} salvo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar perfil do usuário {user_id}: {e}")
            return False
    
    @staticmethod
    def load_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Carrega o perfil do usuário com informações do cadastro.
        
        Args:
            user_id: ID único do usuário
            
        Returns:
            Dicionário com informações do perfil ou None se não encontrado
        """
        profile_path = os.path.join(PROFILES_DIR, f"{user_id}.json")
        
        if not os.path.exists(profile_path):
            logger.warning(f"Perfil do usuário {user_id} não encontrado")
            return None
            
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            logger.info(f"Perfil do usuário {user_id} carregado com sucesso")
            return profile_data
            
        except Exception as e:
            logger.error(f"Erro ao carregar perfil do usuário {user_id}: {e}")
            return None
    
    @staticmethod
    def update_profile(user_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Atualiza informações específicas do perfil do usuário.
        
        Args:
            user_id: ID único do usuário
            new_data: Dicionário com novas informações para atualizar
            
        Returns:
            True se o perfil foi atualizado com sucesso, False caso contrário
        """
        profile_data = UserProfile.load_profile(user_id)
        
        if not profile_data:
            # Se o perfil não existe, cria um novo
            return UserProfile.save_profile(user_id, new_data)
            
        # Atualizar dados existentes com novos dados
        profile_data.update(new_data)
        profile_data['updated_at'] = datetime.now().isoformat()
        
        return UserProfile.save_profile(user_id, profile_data)
    
    @staticmethod
    def get_all_profiles() -> Dict[str, Dict[str, Any]]:
        """
        Obtém todos os perfis de usuários cadastrados.
        
        Returns:
            Dicionário com IDs de usuários e seus respectivos perfis
        """
        all_profiles = {}
        
        try:
            for filename in os.listdir(PROFILES_DIR):
                if filename.endswith('.json'):
                    user_id = filename.split('.')[0]
                    profile = UserProfile.load_profile(user_id)
                    if profile:
                        all_profiles[user_id] = profile
            
            return all_profiles
            
        except Exception as e:
            logger.error(f"Erro ao obter todos os perfis: {e}")
            return {}
            
    @staticmethod
    def create_sample_profile(user_id: str) -> Dict[str, Any]:
        """
        Cria um perfil de exemplo para um novo usuário.
        
        Args:
            user_id: ID único do usuário
            
        Returns:
            Dicionário com o perfil de exemplo criado
        """
        sample_profile = {
            "personal_info": {
                "name": "Usuário",
                "age": 30,
                "gender": "não informado",
                "height": 170,  # cm
                "weight": 70,   # kg
                "email": "usuario@exemplo.com"
            },
            "health_info": {
                "activity_level": "moderado",  # sedentário, leve, moderado, intenso, muito ativo
                "health_conditions": [],
                "allergies": [],
                "intolerances": []
            },
            "diet_preferences": {
                "dietary_restrictions": [],  # vegetariano, vegano, sem glúten, etc.
                "disliked_foods": [],
                "preferred_foods": [],
                "meal_frequency": 5  # número de refeições por dia
            },
            "goals": {
                "primary_goal": "saúde geral",  # emagrecimento, hipertrofia, etc.
                "target_weight": None,
                "weekly_weight_change": None,  # kg por semana
                "calorie_target": 2000
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar o perfil de exemplo
        UserProfile.save_profile(user_id, sample_profile)
        
        return sample_profile