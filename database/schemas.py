"""
Schemas e validações para os dados do ShapeMateAI
Define as estruturas de dados e validações para usuários e perfis
"""

import re
from datetime import datetime


class ValidationError(Exception):
    """Exceção personalizada para erros de validação"""
    pass


class UserSchema:
    """Schema para validação de dados de usuário"""
    
    @staticmethod
    def validate_email(email):
        """Valida formato do email"""
        if not email:
            raise ValidationError("Email é obrigatório")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Formato de email inválido")
        
        return email.lower().strip()
    
    @staticmethod
    def validate_password(password):
        """Valida senha (mínimo 6 caracteres)"""
        if not password:
            raise ValidationError("Senha é obrigatória")
        
        if len(password) < 6:
            raise ValidationError("Senha deve ter pelo menos 6 caracteres")
        
        return password
    
    @classmethod
    def validate_user_data(cls, email, password):
        """Valida dados completos do usuário"""
        return {
            'email': cls.validate_email(email),
            'password': cls.validate_password(password)
        }


class ProfileSchema:
    """Schema para validação de dados do perfil"""
    
    VALID_GENDERS = ['masculino', 'feminino', 'outro']
    VALID_GOALS = [
        'perda_peso', 'ganho_massa_muscular', 'manutencao_peso', 
        'melhora_saude_geral', 'aumento_energia', 'outro'
    ]
    VALID_ACTIVITY_LEVELS = [
        'sedentario', 'leve', 'moderado', 'intenso', 'muito_intenso'
    ]
    
    @staticmethod
    def validate_name(name):
        """Valida nome (obrigatório, mínimo 2 caracteres)"""
        if not name or not name.strip():
            raise ValidationError("Nome é obrigatório")
        
        name = name.strip()
        if len(name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres")
        
        return name
    
    @staticmethod
    def validate_age(age):
        """Valida idade (deve ser número entre 13 e 120)"""
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValidationError("Idade deve ser um número válido")
        
        if age < 13 or age > 120:
            raise ValidationError("Idade deve estar entre 13 e 120 anos")
        
        return age
    
    @staticmethod
    def validate_gender(gender):
        """Valida gênero"""
        if not gender:
            raise ValidationError("Gênero é obrigatório")
        
        gender = gender.lower().strip()
        if gender not in ProfileSchema.VALID_GENDERS:
            raise ValidationError(f"Gênero deve ser um dos: {', '.join(ProfileSchema.VALID_GENDERS)}")
        
        return gender
    
    @staticmethod
    def validate_weight(weight):
        """Valida peso (deve ser número positivo)"""
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            raise ValidationError("Peso deve ser um número válido")
        
        if weight <= 0 or weight > 1000:
            raise ValidationError("Peso deve estar entre 0.1 kg e 1000 kg")
        
        return weight
    
    @staticmethod
    def validate_height(height):
        """Valida altura (deve ser número positivo em metros)"""
        try:
            height = float(height)
        except (ValueError, TypeError):
            raise ValidationError("Altura deve ser um número válido")
        
        if height <= 0 or height > 3.0:
            raise ValidationError("Altura deve estar entre 0.1m e 3.0m")
        
        return height
    
    @staticmethod
    def validate_primary_goal(goal):
        """Valida objetivo principal"""
        if not goal:
            raise ValidationError("Objetivo principal é obrigatório")
        
        goal = goal.lower().strip()
        if goal not in ProfileSchema.VALID_GOALS:
            raise ValidationError(f"Objetivo deve ser um dos: {', '.join(ProfileSchema.VALID_GOALS)}")
        
        return goal
    
    @staticmethod
    def validate_activity_level(level):
        """Valida nível de atividade"""
        if not level:
            raise ValidationError("Nível de atividade é obrigatório")
        
        level = level.lower().strip()
        if level not in ProfileSchema.VALID_ACTIVITY_LEVELS:
            raise ValidationError(f"Nível de atividade deve ser um dos: {', '.join(ProfileSchema.VALID_ACTIVITY_LEVELS)}")
        
        return level
    
    @staticmethod
    def validate_optional_text(text, max_length=500):
        """Valida campos de texto opcionais"""
        if not text:
            return ""
        
        text = text.strip()
        if len(text) > max_length:
            raise ValidationError(f"Texto deve ter no máximo {max_length} caracteres")
        
        return text
    
    @classmethod
    def validate_profile_data(cls, profile_data):
        """Valida dados completos do perfil"""
        validated_data = {
            'name': cls.validate_name(profile_data.get('name')),
            'age': cls.validate_age(profile_data.get('age')),
            'gender': cls.validate_gender(profile_data.get('gender')),
            'weight': cls.validate_weight(profile_data.get('weight')),
            'height': cls.validate_height(profile_data.get('height')),
            'primary_goal': cls.validate_primary_goal(profile_data.get('primary_goal')),
            'activity_level': cls.validate_activity_level(profile_data.get('activity_level')),
            'dietary_restrictions': cls.validate_optional_text(profile_data.get('dietary_restrictions', '')),
            'health_conditions': cls.validate_optional_text(profile_data.get('health_conditions', '')),
            'other_notes': cls.validate_optional_text(profile_data.get('other_notes', ''))
        }
        
        return validated_data


class ChatSchema:
    """Schema para validação de dados de chat"""
    
    @staticmethod
    def validate_message_content(content):
        """Valida conteúdo da mensagem"""
        if not content or not content.strip():
            raise ValidationError("Conteúdo da mensagem é obrigatório")
        
        content = content.strip()
        if len(content) > 2000:
            raise ValidationError("Mensagem deve ter no máximo 2000 caracteres")
        
        return content
    
    @staticmethod
    def validate_message_type(message_type):
        """Valida tipo da mensagem"""
        valid_types = ['user', 'assistant']
        if message_type not in valid_types:
            raise ValidationError(f"Tipo de mensagem deve ser um dos: {', '.join(valid_types)}")
        
        return message_type
