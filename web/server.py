#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ShapeMateAI Web Server - Nutricionista Virtual
"""
import os
import json
import uuid
import secrets
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# Importar o agente do ShapeMateAI
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.core import create_nutritionist_agent
from agent.nutritionist.user_profile import UserProfile

# Inicialização do app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# Chave secreta para sessão
app.secret_key = secrets.token_hex(16)

# Caminho para a pasta de perfis de usuário
USERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_profiles")
os.makedirs(USERS_DIR, exist_ok=True)

# Estrutura para armazenamento temporário de usuários (em produção, usar um BD real)
users_db = {}

# Estrutura para armazenamento temporário de sessões ativas
active_sessions = {}

# Criar instância do agente nutricionista
nutritionist_agent = create_nutritionist_agent()

@app.route('/')
def index():
    """Renderiza a página inicial"""
    return app.send_static_file('index.html')

# Novo endpoint para criar sessões
@app.route('/api/session', methods=['POST'])
def create_session():
    """
    Endpoint para criar uma nova sessão de chat.
    """
    # Gerar um novo ID de sessão
    session_id = str(uuid.uuid4())
    
    # Registrar a nova sessão
    active_sessions[session_id] = {
        'created_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat(),
        'total_requests': 0,
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'total_cost_usd': 0
    }
    
    return jsonify({
        'session_id': session_id,
        'created_at': active_sessions[session_id]['created_at']
    })

# Novo endpoint para finalizar sessões
@app.route('/api/session/<session_id>', methods=['DELETE'])
def end_session(session_id):
    """
    Endpoint para encerrar uma sessão de chat existente.
    """
    # Verificar se a sessão existe
    if session_id not in active_sessions:
        return jsonify({
            'success': False,
            'message': 'Sessão não encontrada'
        }), 404
    
    # Obter dados da sessão antes de removê-la
    session_data = active_sessions[session_id]
    
    # Calcular a duração da sessão
    start_time = datetime.fromisoformat(session_data['created_at'])
    end_time = datetime.now()
    duration_seconds = (end_time - start_time).total_seconds()
    
    # Preparar o resumo da sessão
    summary = {
        'session_id': session_id,
        'created_at': session_data['created_at'],
        'ended_at': end_time.isoformat(),
        'session_duration_seconds': duration_seconds,
        'total_requests': session_data['total_requests'],
        'total_input_tokens': session_data['total_input_tokens'],
        'total_output_tokens': session_data['total_output_tokens'],
        'total_cost_usd': session_data['total_cost_usd']
    }
    
    # Remover a sessão
    del active_sessions[session_id]
    
    return jsonify({
        'success': True,
        'message': 'Sessão encerrada com sucesso',
        'summary': summary
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint para processar mensagens do chat e obter respostas do nutricionista.
    """
    data = request.json
    message = data.get('message', '')
    user_id = data.get('user_id', None)
    session_id = data.get('session_id', None)
    
    # Validar sessão se fornecida
    if session_id and session_id not in active_sessions:
        return jsonify({
            'error': 'Sessão inválida ou expirada'
        }), 401
    
    # Se não temos um ID de usuário, gerar um novo
    if not user_id:
        user_id = str(uuid.uuid4())
    
    # Usar o agente nutricionista
    result = nutritionist_agent(message, user_id=user_id)
    
    # Atualizar estatísticas da sessão, se uma sessão foi fornecida
    if session_id and session_id in active_sessions:
        session = active_sessions[session_id]
        session['last_activity'] = datetime.now().isoformat()
        session['total_requests'] += 1
        session['total_input_tokens'] += result['cost'].get('input_tokens', 0)
        session['total_output_tokens'] += result['cost'].get('output_tokens', 0)
        session['total_cost_usd'] += result['cost'].get('total_cost_usd', 0)
    
    return jsonify({
        'response': result['response'],
        'cost': result['cost'],
        'user_id': result['user_id']
    })

@app.route('/api/register', methods=['POST'])
def register():
    """
    Endpoint para registrar novos usuários com perfil completo.
    """
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    profile = data.get('profile', {})
    
    # Validações básicas
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    # Verificar se o usuário já existe
    for user_id, user_data in users_db.items():
        if user_data.get('email') == email:
            return jsonify({'message': 'Este email já está em uso'}), 409
    
    # Gerar ID único para o usuário
    user_id = str(uuid.uuid4())
    
    # Em produção, faríamos hash da senha antes de armazenar
    users_db[user_id] = {
        'email': email,
        'password': password,  # Apenas para testes! Em produção, usar bcrypt ou similar
        'created_at': datetime.now().isoformat()
    }
    
    # Gerar token de sessão
    session_token = secrets.token_hex(16)
    active_sessions[session_token] = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat()
    }
    
    # Salvar o perfil do usuário
    if profile:
        success = UserProfile.save_profile(user_id, profile)
        if not success:
            return jsonify({'message': 'Erro ao salvar perfil do usuário'}), 500
    
    return jsonify({
        'message': 'Usuário registrado com sucesso',
        'user_id': user_id,
        'token': session_token
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint para login de usuários.
    """
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    # Validações básicas
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    # Verificar credenciais
    user_id = None
    for uid, user_data in users_db.items():
        if user_data.get('email') == email and user_data.get('password') == password:
            user_id = uid
            break
    
    if not user_id:
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    # Gerar token de sessão
    session_token = secrets.token_hex(16)
    active_sessions[session_token] = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat()
    }
    
    # Carregar perfil do usuário, se existir
    profile = UserProfile.load_profile(user_id)
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user_id': user_id,
        'token': session_token,
        'has_profile': profile is not None
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """
    Endpoint para obter o perfil do usuário.
    """
    token = request.headers.get('Authorization')
    if not token or token not in active_sessions:
        return jsonify({'message': 'Não autorizado'}), 401
    
    user_id = active_sessions[token]['user_id']
    profile = UserProfile.load_profile(user_id)
    
    if not profile:
        return jsonify({'message': 'Perfil não encontrado'}), 404
    
    return jsonify(profile)

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """
    Endpoint para atualizar o perfil do usuário.
    """
    token = request.headers.get('Authorization')
    if not token or token not in active_sessions:
        return jsonify({'message': 'Não autorizado'}), 401
    
    user_id = active_sessions[token]['user_id']
    profile_data = request.json
    
    success = UserProfile.update_profile(user_id, profile_data)
    
    if not success:
        return jsonify({'message': 'Erro ao atualizar perfil'}), 500
    
    return jsonify({'message': 'Perfil atualizado com sucesso'})

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Endpoint para logout de usuários.
    """
    token = request.headers.get('Authorization')
    
    if token and token in active_sessions:
        del active_sessions[token]
    
    return jsonify({'message': 'Logout realizado com sucesso'})

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """
    Endpoint para verificar se uma sessão é válida.
    """
    token = request.headers.get('Authorization')
    
    if not token or token not in active_sessions:
        return jsonify({'valid': False}), 401
    
    return jsonify({
        'valid': True,
        'user_id': active_sessions[token]['user_id']
    })

# Rota para carregar mock de usuários para testes
@app.route('/api/load-test-users', methods=['POST'])
def load_test_users():
    """
    Endpoint para carregar usuários de teste.
    ATENÇÃO: Apenas para desenvolvimento!
    """
    if request.remote_addr != '127.0.0.1':
        return jsonify({'message': 'Não autorizado'}), 403
    
    test_users = [
        {
            'email': 'teste@exemplo.com',
            'password': 'senha123',
            'profile': {
                'personal_info': {
                    'name': 'Usuário Teste',
                    'age': 30,
                    'gender': 'masculino',
                    'height': 175,
                    'weight': 70
                },
                'health_info': {
                    'activity_level': 'moderado',
                    'health_conditions': [],
                    'allergies': [],
                    'intolerances': ['lactose']
                },
                'diet_preferences': {
                    'dietary_restrictions': [],
                    'disliked_foods': ['brócolis', 'couve-flor'],
                    'preferred_foods': ['frango', 'arroz', 'feijão'],
                    'meal_frequency': 4
                },
                'goals': {
                    'primary_goal': 'hipertrofia',
                    'target_weight': 75,
                    'calorie_target': 2500
                }
            }
        }
    ]
    
    for user in test_users:
        user_id = str(uuid.uuid4())
        users_db[user_id] = {
            'email': user['email'],
            'password': user['password'],
            'created_at': datetime.now().isoformat()
        }
        
        if 'profile' in user:
            UserProfile.save_profile(user_id, user['profile'])
    
    return jsonify({'message': f'{len(test_users)} usuário(s) de teste carregados com sucesso'})

def create_test_user():
    """
    Cria um usuário de teste para desenvolvimento.
    Esta função é chamada automaticamente quando o servidor é iniciado e não há usuários.
    """
    test_user = {
        'email': 'teste@exemplo.com',
        'password': 'senha123',
        'profile': {
            'personal_info': {
                'name': 'Usuário Teste',
                'age': 30,
                'gender': 'masculino',
                'height': 175,
                'weight': 70
            },
            'health_info': {
                'activity_level': 'moderado',
                'health_conditions': [],
                'allergies': [],
                'intolerances': ['lactose']
            },
            'diet_preferences': {
                'dietary_restrictions': [],
                'disliked_foods': ['brócolis', 'couve-flor'],
                'preferred_foods': ['frango', 'arroz', 'feijão'],
                'meal_frequency': 4
            },
            'goals': {
                'primary_goal': 'hipertrofia',
                'target_weight': 75,
                'calorie_target': 2500
            }
        }
    }
    
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        'email': test_user['email'],
        'password': test_user['password'],
        'created_at': datetime.now().isoformat()
    }
    
    if 'profile' in test_user:
        UserProfile.save_profile(user_id, test_user['profile'])
    
    print(f"Usuário de teste criado com sucesso: {test_user['email']}")

if __name__ == '__main__':
    # Criar um usuário de teste ao iniciar o servidor se não houver usuários
    if len(users_db) == 0:
        create_test_user()
    
    app.run(debug=True, host='0.0.0.0', port=5000)