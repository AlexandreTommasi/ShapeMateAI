# agent/nutritionist/__init__.py
"""
Pacote do agente nutricionista do ShapeMateAI.
"""

from agents.nutritionist.nutritionist_prompts import SYSTEM_PROMPT, get_prompt



# Importar a classe de perfil de usuário
from agents.nutritionist.user_profile import UserProfile