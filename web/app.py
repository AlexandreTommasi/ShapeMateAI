"""
Servidor Web Flask para ShapeMateAI
Interface web para cadastro e interação com usuários
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from register.registration import RegistrationSystem
from database.services import get_database_service
from database.config import GENDER_DISPLAY, GOAL_DISPLAY, ACTIVITY_LEVEL_DISPLAY

app = Flask(__name__)
app.secret_key = 'shapemate_secret_key_2025'  # Em produção, usar variável de ambiente
CORS(app)

# Inicializar sistemas
registration_system = RegistrationSystem()
db_service = get_database_service()


@app.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Página de login"""
    return render_template('login.html')


@app.route('/register')
def register():
    """Página de cadastro"""
    # Obter opções para os formulários
    form_options = registration_system.get_form_options()
    return render_template('register.html', options=form_options)


@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário logado"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    return render_template('dashboard.html', user=user_data)


@app.route('/chat')
def chat():
    """Página de chat com o nutricionista"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    return render_template('chat.html', user=user_data)


# API Routes

@app.route('/api/register', methods=['POST'])
def api_register():
    """API para registrar novo usuário"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Registrar usuário
        result = registration_system.register_new_user(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    """API para autenticar usuário"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        # Autenticar usuário
        result = registration_system.authenticate_user(data['email'], data['password'])
        
        if result['success']:
            # Salvar dados na sessão
            session['user_id'] = result['user_data']['user_id']
            session['user_data'] = result['user_data']
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API para fazer logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})


@app.route('/api/profile')
def api_profile():
    """API para obter dados do perfil do usuário logado"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    user_data = session.get('user_data', {})
    return jsonify({'success': True, 'user_data': user_data})


@app.route('/api/chat/start', methods=['POST'])
def api_start_chat():
    """API para iniciar nova sessão de chat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        session_id, message = db_service.create_chat_session_for_user(user_id)
        
        if session_id:
            session['current_chat_session'] = session_id
            return jsonify({
                'success': True,
                'message': message,
                'session_id': session_id
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar chat: {str(e)}'
        }), 500


@app.route('/api/chat/message', methods=['POST'])
def api_send_message():
    """API para enviar mensagem no chat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        session_id = session.get('current_chat_session')
        
        if not session_id:
            return jsonify({'success': False, 'message': 'Nenhuma sessão de chat ativa'}), 400
        
        if not data or 'message' not in data:
            return jsonify({'success': False, 'message': 'Mensagem é obrigatória'}), 400
        
        # Salvar mensagem do usuário
        message_id, result_message = db_service.save_message_to_chat(
            session_id, 'user', data['message']
        )
        
        if message_id:
            # Aqui seria integrado o sistema do nutricionista (futuro)
            # Por enquanto, apenas confirma o recebimento
            return jsonify({
                'success': True,
                'message': 'Mensagem enviada com sucesso',
                'message_id': message_id
            })
        else:
            return jsonify({'success': False, 'message': result_message}), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar mensagem: {str(e)}'
        }), 500


@app.route('/api/chat/history')
def api_chat_history():
    """API para obter histórico do chat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        session_id = session.get('current_chat_session')
        
        if not session_id:
            return jsonify({'success': False, 'message': 'Nenhuma sessão de chat ativa'}), 400
        
        history = db_service.get_user_chat_history(session_id)
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter histórico: {str(e)}'
        }), 500


@app.route('/api/system/health')
def api_system_health():
    """API para verificar saúde do sistema"""
    is_healthy, message = registration_system.check_system_health()
    return jsonify({
        'healthy': is_healthy,
        'message': message
    })


# Error handlers

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Página não encontrada"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Erro interno do servidor"), 500


if __name__ == '__main__':
    print("=== ShapeMateAI Web Server ===")
    
    # Verificar saúde do sistema antes de iniciar
    is_healthy, health_message = registration_system.check_system_health()
    print(f"Status do sistema: {health_message}")
    
    if not is_healthy:
        print("AVISO: Sistema não está funcionando corretamente!")
        print("Verifique o banco de dados e dependências.")
    
    print("Iniciando servidor web...")
    print("Acesse: http://localhost:5000")
    print("Ctrl+C para parar o servidor")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
