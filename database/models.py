"""
Modelos de banco de dados para ShapeMateAI
Gerencia usuários e perfis conforme especificação do cadastro
"""

import sqlite3
import bcrypt
import uuid
from datetime import datetime
import os


class Database:
    def __init__(self, db_path="database/shapemate.db"):
        self.db_path = db_path
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários (autenticação)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de perfis de usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                primary_goal TEXT NOT NULL,
                activity_level TEXT NOT NULL,
                dietary_restrictions TEXT,
                health_conditions TEXT,
                other_notes TEXT,
                profile_completed BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de sessões de chat (para futuro uso com o nutricionista)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de mensagens do chat
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL, -- 'user' ou 'assistant'
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_email_exists(self, email):
        """Verifica se o email já existe no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def create_user(self, email, password):
        """Cria um novo usuário e retorna o user_id"""
        if self.check_email_exists(email):
            return None, "E-mail já cadastrado"
        
        # Gerar hash da senha
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
                (user_id, email, password_hash)
            )
            conn.commit()
            conn.close()
            return user_id, "Usuário criado com sucesso"
        except Exception as e:
            conn.close()
            return None, f"Erro ao criar usuário: {str(e)}"
    
    def create_user_profile(self, user_id, profile_data):
        """Cria o perfil do usuário"""
        profile_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_profiles 
                (id, user_id, name, age, gender, weight, height, primary_goal, 
                 activity_level, dietary_restrictions, health_conditions, other_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile_id, user_id, profile_data['name'], profile_data['age'],
                profile_data['gender'], profile_data['weight'], profile_data['height'],
                profile_data['primary_goal'], profile_data['activity_level'],
                profile_data.get('dietary_restrictions', ''),
                profile_data.get('health_conditions', ''),
                profile_data.get('other_notes', '')
            ))
            
            conn.commit()
            conn.close()
            return profile_id, "Perfil criado com sucesso"
        except Exception as e:
            conn.close()
            return None, f"Erro ao criar perfil: {str(e)}"
    
    def authenticate_user(self, email, password):
        """Autentica um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
            return result[0]  # Retorna user_id
        return None
    
    def get_user_profile(self, user_id):
        """Obtém o perfil completo do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.email, p.name, p.age, p.gender, p.weight, p.height,
                   p.primary_goal, p.activity_level, p.dietary_restrictions,
                   p.health_conditions, p.other_notes, p.profile_completed
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'email': result[0],
                'name': result[1],
                'age': result[2],
                'gender': result[3],
                'weight': result[4],
                'height': result[5],
                'primary_goal': result[6],
                'activity_level': result[7],
                'dietary_restrictions': result[8],
                'health_conditions': result[9],
                'other_notes': result[10],
                'profile_completed': result[11]
            }
        return None
    
    def create_chat_session(self, user_id, session_name=None):
        """Cria uma nova sessão de chat para o usuário"""
        session_id = str(uuid.uuid4())
        if not session_name:
            session_name = f"Chat {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_sessions (id, user_id, session_name)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, session_name))
            
            conn.commit()
            conn.close()
            return session_id, "Sessão criada com sucesso"
        except Exception as e:
            conn.close()
            return None, f"Erro ao criar sessão: {str(e)}"
    
    def save_chat_message(self, session_id, message_type, content):
        """Salva uma mensagem no chat"""
        message_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_messages (id, session_id, message_type, content)
                VALUES (?, ?, ?, ?)
            ''', (message_id, session_id, message_type, content))
            
            # Atualiza a última atividade da sessão
            cursor.execute('''
                UPDATE chat_sessions 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return message_id, "Mensagem salva com sucesso"
        except Exception as e:
            conn.close()
            return None, f"Erro ao salvar mensagem: {str(e)}"
    
    def get_chat_history(self, session_id):
        """Obtém o histórico de mensagens de uma sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return [{'type': msg[0], 'content': msg[1], 'timestamp': msg[2]} for msg in messages]
    
    def get_user_sessions(self, user_id):
        """Obtém todas as sessões de chat de um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_name, created_at, last_activity, is_active
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY last_activity DESC
        ''', (user_id,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        return [{'id': s[0], 'name': s[1], 'created_at': s[2], 
                'last_activity': s[3], 'is_active': s[4]} for s in sessions]
