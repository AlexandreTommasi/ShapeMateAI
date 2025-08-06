"""
Servidor Web Flask para ShapeMateAI
Interface web para cadastro e interação com usuários
Integrado com sistema de agentes Langgraph
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_cors import CORS
import sys
import os
import logging
from werkzeug.utils import secure_filename

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Adicionar diretório atual ao path para importações locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from register.registration import RegistrationSystem
from database.services import get_database_service
from database.config import GENDER_DISPLAY, GOAL_DISPLAY, ACTIVITY_LEVEL_DISPLAY

# Importar sistema de agentes real
from core.core import CoreAgentSystem, AgentType, TaskType, TaskPriority, BaseAgent, AgentConfig
from core.config_loader import get_config_loader

# Importar utilitários
from utils.diet_manager.diet_storage import diet_manager
from utils.pdf_generator import process_uploaded_diet

# Classe de agente Daily Assistant simples
class SimpleDailyAssistantAgent(BaseAgent):
    """Agente Daily Assistant simplificado para web"""
    
    def __init__(self):
        config_loader = get_config_loader()
        config = config_loader.load_agent_config(AgentType.DAILY_ASSISTANT)
        super().__init__(config)
    
    def process_message(self, state):
        """Processa mensagem usando o novo sistema de memória"""
        try:
            # Usar o novo método para preparar mensagens com contexto
            messages_with_context = self.prepare_messages_with_context(state)
            
            # Usar LLM diretamente com todo o histórico
            response = self.llm.invoke(messages_with_context)
            
            # Adicionar resposta ao estado
            from langchain_core.messages import AIMessage
            state['messages'].append(AIMessage(content=response.content))
            state['confidence_score'] = 0.9
            
            return state
            
        except Exception as e:
            logger.error(f"Error in SimpleDailyAssistantAgent: {str(e)}")
            from langchain_core.messages import AIMessage
            state['messages'].append(AIMessage(content="Desculpe, ocorreu um erro ao processar sua mensagem."))
            state['confidence_score'] = 0.1
            return state

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'shapemate_secret_key_2025'  # Em produção, usar variável de ambiente
CORS(app)

# Configuração de upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Inicializar sistemas
registration_system = RegistrationSystem()
db_service = get_database_service()

# Inicializar sistema de agentes real
core_system = CoreAgentSystem()
nutritionist_agent = None
daily_assistant_agent = None
nutritionist_available = False
daily_assistant_available = False

try:
    # Importar o agente nutricionista atualizado
    from core.agents.nutritionist_agent import NutritionistAgent
    
    # Criar e registrar agente nutricionista com fluxo estruturado
    print("🔧 Creating NutritionistAgent...")
    nutritionist_agent = NutritionistAgent()
    print("✅ NutritionistAgent created successfully")
    
    core_system.register_agent(nutritionist_agent)
    nutritionist_available = True
    print("✅ Agente nutricionista registrado com sucesso")
    logger.info("✅ Agente nutricionista registrado com sucesso")
except Exception as e:
    print(f"❌ Erro crítico ao inicializar agente nutricionista: {e}")
    logger.error(f"❌ Erro crítico ao inicializar agente nutricionista: {e}")
    nutritionist_available = False
    nutritionist_agent = None

try:
    # Criar e registrar agente daily assistant
    daily_assistant_agent = SimpleDailyAssistantAgent()
    core_system.register_agent(daily_assistant_agent)
    daily_assistant_available = True
    logger.info("✅ Agente daily assistant registrado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro crítico ao inicializar agente daily assistant: {e}")
    daily_assistant_available = False
    daily_assistant_agent = None

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_login(f):
    """Decorator para rotas que requerem login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function




@app.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Página de login"""
    return render_template('auth/login.html')


@app.route('/register')
def register():
    """Página de cadastro"""
    # Obter opções para os formulários
    form_options = registration_system.get_form_options()
    return render_template('auth/register.html', options=form_options)


@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário logado"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    
    # Verificar se o usuário tem dieta
    user_id = session['user_id']
    has_diet = False
    
    try:
        # Verificar se tem dieta no diet_manager
        user_diets = diet_manager.get_user_diet_list(user_id)
        if user_diets and len(user_diets) > 0:
            has_diet = True
    except Exception as e:
        logging.error(f"Erro ao verificar dieta do usuário: {e}")
        has_diet = False
    
    # Adicionar informação à sessão
    session['has_diet'] = has_diet
    
    return render_template('shared/dashboard.html', user=user_data, has_diet=has_diet)


@app.route('/chat')
@app.route('/chat/<agent>')
def chat(agent=None):
    """Página de chat com os agentes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    
    # Define qual template usar baseado no agente
    if agent == 'daily_assistant':
        return render_template('daily_assistant/chat.html', user=user_data, 
                             assistant_available=daily_assistant_available)
    else:
        # Default para nutritionist - usar o template principal do chat
        return render_template('nutritionist/chat.html', user=user_data)


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
            
            # Adicionar mensagem de boas-vindas do nutricionista
            if nutritionist_available and nutritionist_agent:
                try:
                    user_data = session.get('user_data', {})
                    user_name = user_data.get('name', user_data.get('full_name'))
                    
                    # Usar método do agente real para gerar boas-vindas
                    if user_name:
                        welcome_message = f"Olá, {user_name}! 👋 Sou seu nutricionista virtual do ShapeMateAI. Como posso ajudar você hoje com sua alimentação e nutrição?"
                    else:
                        welcome_message = "Olá! 👋 Sou seu nutricionista virtual do ShapeMateAI. Estou aqui para ajudar com orientações nutricionais personalizadas. Como posso ajudar você hoje?"
                    
                    # Salvar mensagem de boas-vindas
                    welcome_msg_id, _ = db_service.save_message_to_chat(
                        session_id, 'assistant', welcome_message
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': message,
                        'session_id': session_id,
                        'welcome_message': welcome_message,
                        'nutritionist_available': True
                    })
                except Exception as e:
                    logger.error(f"Erro ao gerar mensagem de boas-vindas: {e}")
                    return jsonify({
                        'success': False,
                        'message': f'Erro ao inicializar nutricionista: {str(e)}'
                    }), 500
            else:
                # Nutricionista não disponível
                return jsonify({
                    'success': False,
                    'message': 'Serviço de nutricionista não disponível'
                }), 503
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
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'success': False, 'message': 'Mensagem não pode estar vazia'}), 400
        
        # Salvar mensagem do usuário
        user_msg_id, result_message = db_service.save_message_to_chat(
            session_id, 'user', user_message
        )
        
        if not user_msg_id:
            return jsonify({'success': False, 'message': result_message}), 400
        
        # Processar mensagem com o nutricionista real
        if nutritionist_available and nutritionist_agent:
            try:
                # Obter perfil do usuário
                user_data = session.get('user_data', {})
                user_id = session['user_id']
                
                # Criar configuração do sistema para esta sessão
                system_config = core_system.create_system_config(
                    agent_type=AgentType.NUTRITIONIST,
                    task_type=TaskType.CONSULTATION,
                    user_id=user_id,
                    session_id=session_id,
                    priority=TaskPriority.MEDIUM
                )
                
                # Processar mensagem através do sistema de agentes
                result = core_system.process_user_message(
                    user_id=user_id,
                    session_id=session_id,
                    message=user_message,
                    user_profile=user_data
                )
                
                if result['success']:
                    # Salvar resposta do nutricionista
                    bot_msg_id, bot_result = db_service.save_message_to_chat(
                        session_id, 'assistant', result['response']
                    )
                    
                    return jsonify({
                        'success': True,
                        'message': 'Mensagem processada com sucesso',
                        'user_message_id': user_msg_id,
                        'bot_message_id': bot_msg_id,
                        'current_message': result['response'],
                        'confidence': result.get('confidence_score', 0.9),
                        'show_option_buttons': result.get('show_option_buttons', False),
                        'is_decision_point': result.get('is_decision_point', False),
                        'current_phase': result.get('current_phase', ''),
                        'diet_generated': result.get('diet_generated', False)
                    })
                else:
                    # Se falhou, retornar erro para tentar novamente
                    return jsonify({
                        'success': False,
                        'message': 'Erro ao processar mensagem com a IA'
                    }), 500
                    
            except Exception as e:
                logger.error(f"Erro no processamento com nutricionista: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Erro técnico no processamento: {str(e)}'
                }), 500
        else:
            # Nutricionista não disponível
            return jsonify({
                'success': False,
                'message': 'Serviço de nutricionista não disponível no momento'
            }), 503
            
    except Exception as e:
        logger.error(f"Erro geral no chat: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao processar mensagem: {str(e)}'
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
        'message': message,
        'nutritionist_available': nutritionist_available
    })


@app.route('/api/nutritionist/status')
def api_nutritionist_status():
    """API para verificar status do nutricionista"""
    return jsonify({
        'available': nutritionist_available,
        'service': 'DeepSeek AI' if nutritionist_available else 'Indisponível',
        'features': [
            'Orientações nutricionais personalizadas',
            'Cálculos de IMC e necessidades calóricas',
            'Planejamento de refeições',
            'Avaliação nutricional'
        ] if nutritionist_available else []
    })


# =================== APIS DO FLUXO ESTRUTURADO ===================

@app.route('/api/nutritionist/consultation/start', methods=['POST'])
def api_start_structured_consultation():
    """API para iniciar consulta estruturada com o Nutrion"""
    print("🚀 API START CONSULTATION CALLED")
    
    if 'user_id' not in session:
        print("❌ User not authenticated")
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not nutritionist_available or not nutritionist_agent:
        print(f"❌ Nutritionist not available: {nutritionist_available}, agent: {nutritionist_agent}")
        return jsonify({'success': False, 'message': 'Nutricionista não disponível'}), 503
    
    try:
        user_data = session.get('user_data', {})
        user_id = session['user_id']
        print(f"📋 User data: {user_data}")
        
        # Verificar se já existe uma consulta em andamento
        if 'consultation_state' in session:
            consultation_state = session['consultation_state']
            # Verificar se tem mensagem válida
            if consultation_state.get('conversation_history'):
                last_message = consultation_state['conversation_history'][-1]['message']
                print(f"📨 Returning existing consultation with message: {last_message[:100]}...")
                return jsonify({
                    'success': True,
                    'consultation_state': consultation_state,
                    'current_message': last_message,
                    'current_phase': consultation_state.get('current_phase', 'greeting'),
                    'message': 'Consulta em andamento recuperada'
                })
        
        # Iniciar nova consulta estruturada
        print("🆕 Starting new structured consultation")
        consultation_state = nutritionist_agent.start_structured_consultation(user_data)
        print(f"✅ Consultation state created: {consultation_state.keys()}")
        
        # Salvar estado na sessão
        session['consultation_state'] = consultation_state
        
        # Obter primeira mensagem
        first_message = consultation_state.get('last_response_content') or consultation_state['conversation_history'][-1]['message']
        print(f"📨 First message: {first_message[:100]}...")
        
        return jsonify({
            'success': True,
            'consultation_state': consultation_state,
            'current_message': first_message,
            'current_phase': consultation_state.get('current_phase', 'greeting')
        })
        
    except Exception as e:
        print(f"❌ Error starting consultation: {e}")
        logger.error(f"Erro ao iniciar consulta estruturada: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar consulta: {str(e)}'
        }), 500


@app.route('/api/nutritionist/consultation/respond', methods=['POST'])
def api_respond_structured_consultation():
    """API para responder na consulta estruturada"""
    print("🗣️ API RESPOND CONSULTATION CALLED")
    
    if 'user_id' not in session:
        print("❌ User not authenticated")
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not nutritionist_available or not nutritionist_agent:
        print(f"❌ Nutritionist not available: {nutritionist_available}, agent: {nutritionist_agent}")
        return jsonify({'success': False, 'message': 'Nutricionista não disponível'}), 503
    
    try:
        data = request.get_json()
        print(f"📨 Received data: {data}")
        
        if not data or 'response' not in data:
            print("❌ Missing response field")
            return jsonify({'success': False, 'message': 'Resposta é obrigatória'}), 400
        
        user_response = data['response'].strip()
        if not user_response:
            print("❌ Empty response")
            return jsonify({'success': False, 'message': 'Resposta não pode estar vazia'}), 400
        
        # Verificar se existe consulta em andamento
        if 'consultation_state' not in session:
            print("❌ No consultation in progress")
            return jsonify({'success': False, 'message': 'Nenhuma consulta em andamento'}), 400
        
        consultation_state = session['consultation_state']
        print(f"📋 Current consultation state keys: {consultation_state.keys()}")
        
        # Continuar consulta estruturada
        print("🔄 Continuing structured consultation...")
        updated_state = nutritionist_agent.continue_structured_consultation(
            consultation_state, user_response
        )
        
        # Atualizar estado na sessão
        session['consultation_state'] = updated_state
        print("✅ Session updated with new state")
        
        # Obter última mensagem do agente
        latest_message = updated_state['conversation_history'][-1]['message']
        print(f"📨 Latest message: {latest_message[:100]}...")
        
        # Verificar se chegou ao ponto de decisão
        is_decision_point = updated_state.get('ready_for_summary', False)
        show_buttons = 'summary_and_decision' in updated_state['current_phase']
        
        response_data = {
            'success': True,
            'consultation_state': updated_state,
            'current_message': latest_message,
            'current_phase': updated_state['current_phase'],
            'is_decision_point': is_decision_point,
            'show_action_buttons': show_buttons,
            'diet_generated': updated_state.get('current_phase') == 'diet_generated'
        }
        print(f"✅ Sending response: success={response_data['success']}, message_length={len(latest_message)}, diet_generated={response_data['diet_generated']}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in respond consultation: {e}")
        logger.error(f"Erro ao responder consulta estruturada: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao processar resposta: {str(e)}'
        }), 500


@app.route('/api/nutritionist/consultation/action', methods=['POST'])
def api_consultation_action():
    """API para executar ação na consulta (gerar dieta ou adicionar informações)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'success': False, 'message': 'Ação é obrigatória'}), 400
        
        action = data['action'].lower()
        consultation_state = session.get('consultation_state', {})
        
        if action == 'generate_diet':
            # NOVA FUNCIONALIDADE: Gerar dieta real usando agente com TMB
            try:
                # Verificar se o agente nutricionista está disponível
                if not nutritionist_available or not nutritionist_agent:
                    return jsonify({
                        'success': False,
                        'message': 'Sistema de geração de dietas não disponível'
                    }), 503
                
                # Gerar dieta usando o agente nutricionista
                diet_json = nutritionist_agent.generate_diet_json(consultation_state)
                
                # Salvar dieta para o usuário (aqui você pode implementar salvamento no banco)
                user_id = session['user_id']
                
                # Mensagem de sucesso com detalhes dos cálculos
                tmb_info = diet_json.get('tmb_calculations', {})
                patient_info = diet_json.get('patient_info', {})
                
                success_message = f"""🎉 **DIETA PERSONALIZADA CRIADA COM SUCESSO!** 

Uhuuul! Sua dieta personalizada está pronta! ✨

## 📊 **SEUS CÁLCULOS NUTRICIONAIS:**
- **TMB (Taxa Metabólica Basal):** {tmb_info.get('tmb_kcal', 'N/A')} kcal
- **Gasto Energético Total:** {tmb_info.get('get_kcal', 'N/A')} kcal  
- **Meta Calórica Diária:** {tmb_info.get('daily_target_kcal', 'N/A')} kcal
- **Estratégia:** {tmb_info.get('objective_adjustment', 'Personalizada')}

## 🎯 **SEU PLANO PERSONALIZADO:**
Baseei tudo nas suas preferências, objetivos e estilo de vida. Considerando que você:
- **Objetivo:** {patient_info.get('primary_objective', 'Melhoria da saúde')}
- **Nível de Atividade:** {patient_info.get('activity_level', 'Personalizado')}
- **Preferências:** {', '.join(patient_info.get('food_preferences', [])[:3])}

## 📋 **O QUE VOCÊ TERÁ:**
🍽️ **Cardápio semanal completo** com horários
🛒 **Lista de compras inteligente**  
📊 **Valores nutricionais detalhados**
🔄 **Opções de substituições**
⚖️ **Controle de macronutrientes**

Sua dieta já está disponível na área "Minhas Dietas" do dashboard!

Estou aqui sempre que precisar de ajustes! Vamos nessa jornada juntos! 💪"""

                # Limpar estado da consulta
                if 'consultation_state' in session:
                    del session['consultation_state']
                
                return jsonify({
                    'success': True,
                    'action': 'diet_generated',
                    'message': success_message,
                    'diet_data': diet_json,
                    'redirect_to': 'dashboard'
                })
                
            except Exception as diet_error:
                logger.error(f"Erro ao gerar dieta: {diet_error}")
                return jsonify({
                    'success': False,
                    'message': f'Erro ao gerar dieta personalizada: {str(diet_error)}'
                }), 500
            
        elif action == 'add_information':
            # Voltar para coleta de informações adicionais
            consultation_state['current_phase'] = 'additional_information_gathering'
            session['consultation_state'] = consultation_state
            
            return jsonify({
                'success': True,
                'action': 'continue_consultation',
                'message': 'Continuando coleta de informações...',
                'consultation_state': consultation_state
            })
        else:
            return jsonify({'success': False, 'message': 'Ação inválida'}), 400
            
    except Exception as e:
        logger.error(f"Erro ao executar ação da consulta: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao executar ação: {str(e)}'
        }), 500


@app.route('/api/nutritionist/consultation/reset', methods=['POST'])
def api_reset_consultation():
    """API para resetar/limpar consulta estruturada"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Limpar estado da consulta
        if 'consultation_state' in session:
            del session['consultation_state']
        
        return jsonify({
            'success': True,
            'message': 'Consulta resetada com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao resetar consulta: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao resetar consulta: {str(e)}'
        }), 500


# Error handlers

@app.errorhandler(404)
def not_found(error):
    return render_template('shared/error.html', 
                         error_code=404, 
                         error_message="Página não encontrada"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('shared/error.html', 
                         error_code=500, 
                         error_message="Erro interno do servidor"), 500


# ==========================================
# NOVAS ROTAS - DAILY ASSISTANT E FUNCIONALIDADES
# ==========================================

@app.route('/daily-assistant')
def daily_assistant():
    """Página do chat com Daily Assistant"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar se o usuário tem dieta antes de permitir acesso
    user_id = session['user_id']
    has_diet = False
    
    try:
        user_diets = diet_manager.get_user_diet_list(user_id)
        if user_diets and len(user_diets) > 0:
            has_diet = True
    except Exception as e:
        logging.error(f"Erro ao verificar dieta do usuário: {e}")
        has_diet = False
    
    # Se não tem dieta, redirecionar para dashboard com mensagem
    if not has_diet:
        return redirect(url_for('dashboard'))
    
    user_data = session.get('user_data', {})
    return render_template('daily_assistant/chat.html', user=user_data, 
                         assistant_available=daily_assistant_available)

@app.route('/diet')
def diet_view():
    """Página para visualizar a dieta"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    user_id = session['user_id']
    
    # Buscar dieta ativa do usuário
    diet = diet_manager.get_user_diet(user_id)
    
    return render_template('nutritionist/diet_view.html', user=user_data, diet=diet)

@app.route('/api/diet/download-pdf')
@require_login
def download_diet_pdf():
    """Baixa o PDF da dieta do usuário"""
    try:
        user_id = session['user_id']
        user_data = session.get('user_data', {})
        
        # Buscar dieta ativa do usuário
        diet = diet_manager.get_user_diet(user_id)
        
        if not diet:
            return jsonify({'error': 'Nenhuma dieta encontrada'}), 404
        
        # Verificar se o PDF existe
        pdf_path = diet.get('pdf_path')
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF não encontrado'}), 404
        
        # Enviar arquivo PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"dieta_{user_data.get('name', 'paciente')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Erro ao baixar PDF da dieta: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/shopping-list')
def shopping_list():
    """Página de listas de compras"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    user_id = session['user_id']
    
    # Buscar listas do usuário
    shopping_lists = diet_manager.get_shopping_lists(user_id)
    
    return render_template('management/shopping_list.html', user=user_data, shopping_lists=shopping_lists)

@app.route('/inventory')
def inventory():
    """Página do estoque em casa"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    user_id = session['user_id']
    
    # Buscar estoque do usuário
    inventory_items = diet_manager.get_inventory(user_id)
    
    return render_template('management/inventory.html', user=user_data, inventory=inventory_items)

# ==========================================
# APIs PARA DAILY ASSISTANT
# ==========================================

@app.route('/api/daily-assistant/start', methods=['POST'])
@require_login
def start_daily_assistant_session():
    """Inicia uma sessão com o Daily Assistant"""
    try:
        user_id = session['user_id']
        session_id = f"daily_assistant_{user_id}_{__import__('time').time()}"
        
        # Criar configuração do sistema para Daily Assistant
        system_config = core_system.create_system_config(
            agent_type=AgentType.DAILY_ASSISTANT,
            task_type=TaskType.DAILY_SUPPORT,
            user_id=str(user_id),
            session_id=session_id,
            priority=TaskPriority.MEDIUM
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Sessão iniciada com Daily Assistant'
        })
        
    except Exception as e:
        logger.error(f"Erro ao iniciar sessão Daily Assistant: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao iniciar sessão'
        }), 500

@app.route('/api/daily-assistant/message', methods=['POST'])
@require_login
def daily_assistant_message():
    """Processa mensagem do Daily Assistant"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Mensagem não pode estar vazia'
            }), 400
        
        if not daily_assistant_available:
            return jsonify({
                'success': False,
                'message': 'Daily Assistant não está disponível no momento'
            }), 503
        
        try:
            # Obter dados do usuário
            user_data = session.get('user_data', {})
            user_id = session['user_id']
            session_id = f"daily_assistant_{user_id}"
            
            # Salvar mensagem do usuário
            user_msg_id, user_result = db_service.save_message_to_chat(
                session_id, 'user', user_message
            )
            
            if not user_result:
                logger.warning("Falha ao salvar mensagem do usuário")
            
            # Criar configuração do sistema para esta sessão
            system_config = core_system.create_system_config(
                agent_type=AgentType.DAILY_ASSISTANT,
                task_type=TaskType.DAILY_SUPPORT,
                user_id=str(user_id),
                session_id=session_id,
                priority=TaskPriority.MEDIUM
            )
            
            # Processar mensagem através do sistema de agentes
            result = core_system.process_user_message(
                user_id=str(user_id),
                session_id=session_id,
                message=user_message,
                user_profile=user_data
            )
            
            if result['success']:
                # Salvar resposta do assistente
                bot_msg_id, bot_result = db_service.save_message_to_chat(
                    session_id, 'assistant', result['response']
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Mensagem processada com sucesso',
                    'response': result['response']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('error', 'Erro ao processar mensagem')
                }), 500
                
        except Exception as agent_error:
            logger.error(f"Erro no Daily Assistant: {agent_error}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do assistente'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro na API Daily Assistant: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/api/shopping-list/create', methods=['POST'])
@require_login
def create_shopping_list_api():
    """Cria uma nova lista de compras"""
    try:
        data = request.get_json()
        list_name = data.get('list_name', '')
        source = data.get('source', 'custom')
        custom_items = data.get('custom_items', [])
        
        user_id = session['user_id']
        
        if source == 'diet':
            # Criar lista baseada na dieta
            diet = diet_manager.get_user_diet(user_id)
            if diet:
                list_id = diet_manager.create_shopping_list(user_id, diet['id'])
            else:
                return jsonify({
                    'success': False,
                    'message': 'Você não possui uma dieta ativa'
                }), 400
        else:
            # Criar lista personalizada
            list_id = diet_manager.create_shopping_list(
                user_id=user_id,
                custom_items=custom_items
            )
        
        return jsonify({
            'success': True,
            'message': 'Lista criada com sucesso',
            'list_id': list_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar lista de compras: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/api/inventory/update', methods=['POST'])
@require_login  
def update_inventory_api():
    """Atualiza item no estoque"""
    try:
        data = request.get_json()
        item_name = data.get('item_name', '').strip()
        quantity = data.get('quantity', '').strip()
        unit = data.get('unit', 'unidade')
        category = data.get('category', 'outros')
        expiration_date = data.get('expiration_date')
        
        if not item_name or not quantity:
            return jsonify({
                'success': False,
                'message': 'Nome do item e quantidade são obrigatórios'
            }), 400
        
        user_id = session['user_id']
        
        diet_manager.update_inventory_item(
            user_id=user_id,
            item_name=item_name,
            quantity=quantity,
            unit=unit,
            category=category,
            expiration_date=expiration_date
        )
        
        return jsonify({
            'success': True,
            'message': 'Item atualizado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar estoque: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


def run_app():
    """Function to run the app for uv script"""
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


if __name__ == '__main__':
    run_app()
