"""
Módulo de banco de dados do ShapeMateAI
Contém todas as funcionalidades relacionadas ao banco de dados SQLite
"""

from .models import Database
from .schemas import UserSchema, ProfileSchema, ChatSchema, ValidationError
from .config import *

__all__ = ['Database', 'UserSchema', 'ProfileSchema', 'ChatSchema', 'ValidationError']
