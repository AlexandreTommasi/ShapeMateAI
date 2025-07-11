"""
Configurações do banco de dados para ShapeMateAI
Define constantes e configurações específicas do banco
"""

import os

# Configurações do banco de dados
DB_NAME = "shapemate.db"
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# Configurações de backup
BACKUP_DIR = os.path.join(DB_DIR, "backups")
BACKUP_ENABLED = True
BACKUP_FREQUENCY_HOURS = 24

# Configurações de segurança
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT_HOURS = 24

# Configurações de validação
MAX_TEXT_LENGTH = 500
MAX_MESSAGE_LENGTH = 2000

# Mapeamentos para exibição
GENDER_DISPLAY = {
    'masculino': 'Masculino',
    'feminino': 'Feminino',
    'outro': 'Outro'
}

GOAL_DISPLAY = {
    'perda_peso': 'Perda de peso',
    'ganho_massa_muscular': 'Ganho de massa muscular',
    'manutencao_peso': 'Manutenção de peso',
    'melhora_saude_geral': 'Melhora da saúde geral',
    'aumento_energia': 'Aumento de energia',
    'outro': 'Outro objetivo'
}

ACTIVITY_LEVEL_DISPLAY = {
    'sedentario': 'Sedentário (pouco ou nenhum exercício)',
    'leve': 'Leve (exercício leve/esporte 1-3 dias/semana)',
    'moderado': 'Moderado (exercício moderado/esporte 3-5 dias/semana)',
    'intenso': 'Intenso (exercício intenso/esporte 6-7 dias/semana)',
    'muito_intenso': 'Muito intenso (exercício muito intenso, trabalho físico)'
}

# Constantes para o banco
TABLE_USERS = "users"
TABLE_USER_PROFILES = "user_profiles"
TABLE_CHAT_SESSIONS = "chat_sessions"
TABLE_CHAT_MESSAGES = "chat_messages"
