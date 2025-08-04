"""
Core system for ShapeMateAI
Main orchestrator for agent configurations and task management
"""

from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Tipos de agentes disponíveis no sistema"""
    NUTRITIONIST = "nutritionist"
    DAILY_ASSISTANT = "daily_assistant"


class TaskType(Enum):
    """Tipos de tarefas que os agentes podem executar"""
    # Nutritionist tasks
    CONSULTATION = "consultation"
    JSON_GENERATION = "json_generation"
    MEAL_PLANNING = "meal_planning" 
    PDF_GENERATION = "pdf_generation"
    
    # Daily Assistant tasks
    DAILY_SUPPORT = "daily_support"
    SHOPPING_LIST = "shopping_list"
    DIET_SUBSTITUTION = "diet_substitution"
    MENU_ANALYSIS = "menu_analysis"
    MEAL_SUGGESTION = "meal_suggestion"


class TaskPriority(Enum):
    """Prioridades das tarefas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class AgentState(TypedDict):
    """Estado compartilhado entre os nós do grafo do agente"""
    messages: List[BaseMessage]
    user_id: str
    session_id: str
    agent_type: str
    task_type: str
    user_profile: Dict[str, Any]
    context: Dict[str, Any]
    tools_used: List[str]
    confidence_score: float
    next_action: Optional[str]


@dataclass
class TaskConfig:
    """Configuração de uma tarefa específica"""
    task_type: TaskType
    priority: TaskPriority
    required_context: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    max_iterations: int = 10
    timeout_seconds: int = 300
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    fallback_strategy: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração para dicionário"""
        return {
            'task_type': self.task_type.value,
            'priority': self.priority.value,
            'required_context': self.required_context,
            'tools_required': self.tools_required,
            'max_iterations': self.max_iterations,
            'timeout_seconds': self.timeout_seconds,
            'success_criteria': self.success_criteria,
            'fallback_strategy': self.fallback_strategy
        }


@dataclass
class AgentConfig:
    """Configuração específica de um agente"""
    agent_type: AgentType
    name: str
    description: str
    system_prompt: str
    supported_tasks: List[TaskType] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    max_context_length: int = 8000
    specialized_prompts: Dict[str, str] = field(default_factory=dict)
    personality_traits: Dict[str, Any] = field(default_factory=dict)
    contexts: Dict[str, str] = field(default_factory=dict)
    task_keywords: Dict[str, List[str]] = field(default_factory=dict)
    context_mapping: Dict[str, List[str]] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    error_responses: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração para dicionário"""
        return {
            'agent_type': self.agent_type.value,
            'name': self.name,
            'description': self.description,
            'system_prompt': self.system_prompt,
            'supported_tasks': [task.value for task in self.supported_tasks],
            'tools': self.tools,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'max_context_length': self.max_context_length,
            'specialized_prompts': self.specialized_prompts,
            'personality_traits': self.personality_traits,
            'contexts': self.contexts,
            'task_keywords': self.task_keywords,
            'context_mapping': self.context_mapping,
            'confidence_scores': self.confidence_scores,
            'error_responses': self.error_responses
        }


@dataclass
class SystemConfig:
    """Configuração do sistema principal"""
    agent_config: AgentConfig
    task_config: TaskConfig
    session_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if self.task_config.task_type not in self.agent_config.supported_tasks:
            raise ValueError(
                f"Task type {self.task_config.task_type.value} not supported by "
                f"agent type {self.agent_config.agent_type.value}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração para dicionário"""
        return {
            'agent_config': self.agent_config.to_dict(),
            'task_config': self.task_config.to_dict(),
            'session_config': self.session_config
        }


class BaseAgent(ABC):
    """Classe base abstrata para todos os agentes"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Configure LLM based on available API keys
        api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No API key found. Please set DEEPSEEK_API_KEY or OPENAI_API_KEY in your .env file")
        
        # Use DeepSeek if available, otherwise fallback to OpenAI
        if os.getenv('DEEPSEEK_API_KEY'):
            self.llm = ChatOpenAI(
                model=config.model_name.replace('gpt-', 'deepseek-') if 'gpt-' in config.model_name else 'deepseek-chat',
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                openai_api_key=os.getenv('DEEPSEEK_API_KEY'),
                openai_api_base="https://api.deepseek.com/v1"
            )
        else:
            self.llm = ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Não utiliza grafo - processamento direto"""
        pass
    
    @abstractmethod
    def process_message(self, state: AgentState) -> AgentState:
        """Processa uma mensagem do usuário"""
        pass
    
    def get_system_message(self, task_type: Optional[TaskType] = None) -> SystemMessage:
        """Obtém a mensagem do sistema para o agente"""
        system_prompt = self.config.system_prompt
        
        # Adicionar prompt especializado se disponível
        if task_type and task_type.value in self.config.specialized_prompts:
            specialized_prompt = self.config.specialized_prompts[task_type.value]
            system_prompt = f"{system_prompt}\n\n{specialized_prompt}"
        
        return SystemMessage(content=system_prompt)
    
    def prepare_messages_with_context(self, state: AgentState) -> List[BaseMessage]:
        """Prepara as mensagens incluindo contexto do sistema"""
        messages = []
        
        # Adicionar mensagem do sistema se não existir
        has_system_message = any(isinstance(msg, SystemMessage) for msg in state['messages'])
        if not has_system_message:
            task_type = TaskType(state['task_type']) if state['task_type'] else None
            system_msg = self.get_system_message(task_type)
            messages.append(system_msg)
        
        # Adicionar contexto do usuário se disponível
        if state['user_profile']:
            profile_context = self._format_user_profile(state['user_profile'])
            if profile_context:
                context_msg = SystemMessage(content=f"Contexto do usuário: {profile_context}")
                messages.append(context_msg)
        
        # Adicionar mensagens da conversa
        messages.extend(state['messages'])
        
        return messages
    
    def _format_user_profile(self, user_profile: Dict[str, Any]) -> str:
        """Formata o perfil do usuário para contexto"""
        if not user_profile:
            return ""
        
        profile_parts = []
        
        # Informações básicas
        if 'name' in user_profile:
            profile_parts.append(f"Nome: {user_profile['name']}")
        
        if 'age' in user_profile:
            profile_parts.append(f"Idade: {user_profile['age']} anos")
        
        if 'primary_goal' in user_profile:
            goal = user_profile['primary_goal'].replace('_', ' ').title()
            profile_parts.append(f"Objetivo principal: {goal}")
        
        if 'activity_level' in user_profile:
            activity = user_profile['activity_level'].replace('_', ' ').title()
            profile_parts.append(f"Nível de atividade: {activity}")
        
        if 'dietary_restrictions' in user_profile and user_profile['dietary_restrictions']:
            profile_parts.append(f"Restrições alimentares: {user_profile['dietary_restrictions']}")
        
        return "; ".join(profile_parts)


class CoreAgentSystem:
    """Sistema principal de gerenciamento de agentes"""
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.system_configs: Dict[str, SystemConfig] = {}
        # Sistema de memória para conversas
        self.conversation_memory: Dict[str, List[BaseMessage]] = {}
        self.memory_limits: Dict[str, int] = {}
        # Config loader para carregar configurações de tasks (temporariamente desabilitado)
        # self.config_loader = get_config_loader()
        # Sistema de compartilhamento de dados entre agentes
        self.shared_user_data: Dict[str, Dict[str, Any]] = {}
        
    def _get_memory_key(self, user_id: str, session_id: str) -> str:
        """Gera chave única para memória da sessão"""
        return f"{user_id}:{session_id}"
    
    def _get_conversation_memory(self, user_id: str, session_id: str) -> List[BaseMessage]:
        """Obtém o histórico de conversas para uma sessão"""
        memory_key = self._get_memory_key(user_id, session_id)
        return self.conversation_memory.get(memory_key, [])
    
    def _add_to_memory(self, user_id: str, session_id: str, message: BaseMessage):
        """Adiciona uma mensagem à memória da sessão"""
        memory_key = self._get_memory_key(user_id, session_id)
        
        if memory_key not in self.conversation_memory:
            self.conversation_memory[memory_key] = []
        
        self.conversation_memory[memory_key].append(message)
        
        # Aplicar limite de memória (sliding window)
        max_messages = self.memory_limits.get(memory_key, 20)
        if len(self.conversation_memory[memory_key]) > max_messages:
            # Manter mensagem do sistema + últimas N mensagens
            system_messages = [msg for msg in self.conversation_memory[memory_key] if isinstance(msg, SystemMessage)]
            recent_messages = [msg for msg in self.conversation_memory[memory_key] if not isinstance(msg, SystemMessage)][-max_messages:]
            self.conversation_memory[memory_key] = system_messages + recent_messages
    
    def _set_memory_limit(self, user_id: str, session_id: str, limit: int):
        """Define o limite de memória para uma sessão"""
        memory_key = self._get_memory_key(user_id, session_id)
        self.memory_limits[memory_key] = limit
    
    def update_shared_user_data(self, user_id: str, data_type: str, data: Dict[str, Any]):
        """Atualiza dados compartilhados entre agentes para um usuário"""
        if user_id not in self.shared_user_data:
            self.shared_user_data[user_id] = {}
        
        self.shared_user_data[user_id][data_type] = {
            'data': data,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'agent_source': data.get('source_agent', 'unknown')
        }
        
        logger.info(f"Updated shared data for user {user_id}: {data_type}")
    
    def get_shared_user_data(self, user_id: str, data_type: Optional[str] = None) -> Dict[str, Any]:
        """Obtém dados compartilhados para um usuário"""
        if user_id not in self.shared_user_data:
            return {}
        
        if data_type:
            return self.shared_user_data[user_id].get(data_type, {})
        
        return self.shared_user_data[user_id]
    
    def clear_session_memory(self, user_id: str, session_id: str):
        """Limpa a memória de uma sessão específica"""
        memory_key = self._get_memory_key(user_id, session_id)
        if memory_key in self.conversation_memory:
            del self.conversation_memory[memory_key]
        if memory_key in self.memory_limits:
            del self.memory_limits[memory_key]
        
    def register_agent(self, agent: BaseAgent):
        """Registra um agente no sistema"""
        self.agents[agent.config.agent_type] = agent
        logger.info(f"Agent {agent.config.name} registered successfully")
    
    def create_system_config(
        self,
        agent_type: AgentType,
        task_type: TaskType,
        user_id: str,
        session_id: str,
        **kwargs
    ) -> SystemConfig:
        """Cria uma configuração de sistema para uma sessão específica"""
        
        if agent_type not in self.agents:
            raise ValueError(f"Agent type {agent_type.value} not registered")
        
        agent_config = self.agents[agent_type].config
        
        # Carregar configuração da tarefa específica do agente
        # Temporariamente desabilitado devido a importação circular
        # try:
        #     task_config_data = self.config_loader.load_task_config(task_type, agent_type)
        #     
        #     # Criar TaskConfig com dados carregados + overrides
        #     task_config = TaskConfig(
        #         task_type=task_type,
        #         priority=kwargs.get('priority', TaskPriority(task_config_data.get('priority', 'MEDIUM'))),
        #         required_context=kwargs.get('required_context', task_config_data.get('required_context', [])),
        #         tools_required=kwargs.get('tools_required', task_config_data.get('tools_required', [])),
        #         max_iterations=kwargs.get('max_iterations', task_config_data.get('max_iterations', 10)),
        #         timeout_seconds=kwargs.get('timeout_seconds', task_config_data.get('timeout_seconds', 300)),
        #         success_criteria=task_config_data.get('success_criteria', {}),
        #         fallback_strategy=task_config_data.get('fallback_strategy')
        #     )
        # except Exception as e:
        #     logger.warning(f"Failed to load task config for {agent_type.value}/{task_type.value}: {e}")
        #     # Fallback para configuração padrão
        task_config = TaskConfig(
            task_type=task_type,
            priority=kwargs.get('priority', TaskPriority.MEDIUM),
                required_context=kwargs.get('required_context', []),
                tools_required=kwargs.get('tools_required', []),
                max_iterations=kwargs.get('max_iterations', 10),
                timeout_seconds=kwargs.get('timeout_seconds', 300)
            )
        
        # Configuração da sessão
        session_config = {
            'user_id': user_id,
            'session_id': session_id,
            'created_at': kwargs.get('created_at'),
            'max_context_messages': kwargs.get('max_context_messages', 20),
            'memory_strategy': kwargs.get('memory_strategy', 'sliding_window')
        }
        
        system_config = SystemConfig(
            agent_config=agent_config,
            task_config=task_config,
            session_config=session_config
        )
        
        # Armazenar configuração
        config_key = f"{user_id}:{session_id}"
        self.system_configs[config_key] = system_config
        
        # Configurar limite de memória
        memory_limit = kwargs.get('max_context_messages', 20)
        self._set_memory_limit(user_id, session_id, memory_limit)
        
        return system_config
    
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Obtém um agente específico"""
        return self.agents.get(agent_type)
    
    def get_system_config(self, user_id: str, session_id: str) -> Optional[SystemConfig]:
        """Obtém a configuração do sistema para uma sessão"""
        config_key = f"{user_id}:{session_id}"
        return self.system_configs.get(config_key)
    
    def create_agent_state(
        self,
        user_id: str,
        session_id: str,
        message: str,
        user_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> AgentState:
        """Cria o estado inicial do agente com histórico de conversas"""
        
        config = self.get_system_config(user_id, session_id)
        if not config:
            raise ValueError(f"No system config found for {user_id}:{session_id}")
        
        # Obter histórico de conversas da memória
        conversation_history = self._get_conversation_memory(user_id, session_id)
        
        # Adicionar mensagem atual
        current_message = HumanMessage(content=message)
        
        # Combinar histórico + mensagem atual
        all_messages = conversation_history + [current_message]
        
        return AgentState(
            messages=all_messages,
            user_id=user_id,
            session_id=session_id,
            agent_type=config.agent_config.agent_type.value,
            task_type=config.task_config.task_type.value,
            user_profile=user_profile,
            context=context or {},
            tools_used=[],
            confidence_score=0.0,
            next_action=None
        )
    
    def process_user_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        user_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Processa uma mensagem do usuário através do sistema de agentes com memória"""
        
        try:
            # Obter configuração do sistema
            config = self.get_system_config(user_id, session_id)
            if not config:
                raise ValueError(f"No system config found for {user_id}:{session_id}")
            
            # Obter agente
            agent = self.get_agent(config.agent_config.agent_type)
            if not agent:
                raise ValueError(f"Agent {config.agent_config.agent_type.value} not found")
            
            # Adicionar dados compartilhados ao contexto
            shared_data = self.get_shared_user_data(user_id)
            if context is None:
                context = {}
            context['shared_agent_data'] = shared_data
            
            # Adicionar mensagem do usuário à memória
            user_message = HumanMessage(content=message)
            self._add_to_memory(user_id, session_id, user_message)
            
            # Criar estado do agente (já inclui histórico)
            state = self.create_agent_state(
                user_id, session_id, message, user_profile, context
            )
            
            # Processar mensagem através do agente
            result_state = agent.process_message(state)
            
            # Extrair resposta e adicionar à memória
            if result_state['messages']:
                last_message = result_state['messages'][-1]
                if isinstance(last_message, AIMessage):
                    # Adicionar resposta do agente à memória
                    self._add_to_memory(user_id, session_id, last_message)
                    
                    return {
                        'success': True,
                        'response': last_message.content,
                        'confidence_score': result_state.get('confidence_score', 0.0),
                        'tools_used': result_state.get('tools_used', []),
                        'next_action': result_state.get('next_action'),
                        'memory_size': len(self._get_conversation_memory(user_id, session_id)),
                        'show_option_buttons': result_state.get('show_option_buttons', False),
                        'is_decision_point': result_state.get('is_decision_point', False),
                        'current_phase': result_state.get('current_phase', ''),
                        'diet_generated': result_state.get('diet_generated', False)
                    }
            
            return {
                'success': False,
                'error': 'No response generated',
                'response': 'Desculpe, não consegui processar sua mensagem.'
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Desculpe, ocorreu um erro ao processar sua mensagem.'
            }
    
    def list_available_agents(self) -> List[Dict[str, Any]]:
        """Lista todos os agentes disponíveis"""
        return [
            {
                'type': agent.config.agent_type.value,
                'name': agent.config.name,
                'description': agent.config.description,
                'supported_tasks': [task.value for task in agent.config.supported_tasks]
            }
            for agent in self.agents.values()
        ]
    
    def get_agent_capabilities(self, agent_type: AgentType) -> Dict[str, Any]:
        """Obtém as capacidades de um agente específico"""
        agent = self.get_agent(agent_type)
        if not agent:
            return {}
        
        return {
            'name': agent.config.name,
            'description': agent.config.description,
            'supported_tasks': [task.value for task in agent.config.supported_tasks],
            'tools': agent.config.tools,
            'personality_traits': agent.config.personality_traits
        }
    
    def get_session_memory_info(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Obtém informações sobre a memória de uma sessão"""
        memory_key = self._get_memory_key(user_id, session_id)
        memory = self.conversation_memory.get(memory_key, [])
        
        return {
            'total_messages': len(memory),
            'memory_limit': self.memory_limits.get(memory_key, 20),
            'system_messages': len([msg for msg in memory if isinstance(msg, SystemMessage)]),
            'user_messages': len([msg for msg in memory if isinstance(msg, HumanMessage)]),
            'assistant_messages': len([msg for msg in memory if isinstance(msg, AIMessage)])
        }
    
    def get_conversation_summary(self, user_id: str, session_id: str, last_n: int = 5) -> List[Dict[str, Any]]:
        """Obtém um resumo das últimas N mensagens da conversa"""
        memory = self._get_conversation_memory(user_id, session_id)
        
        # Filtrar apenas mensagens de conversa (excluir SystemMessage)
        conversation_messages = [msg for msg in memory if not isinstance(msg, SystemMessage)]
        
        # Pegar últimas N mensagens
        recent_messages = conversation_messages[-last_n:] if last_n > 0 else conversation_messages
        
        summary = []
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                summary.append({
                    'type': 'user',
                    'content': msg.content,
                    'timestamp': getattr(msg, 'timestamp', None)
                })
            elif isinstance(msg, AIMessage):
                summary.append({
                    'type': 'assistant',
                    'content': msg.content,
                    'timestamp': getattr(msg, 'timestamp', None)
                })
        
        return summary


# Instância global do sistema
core_system = CoreAgentSystem()


def get_core_system() -> CoreAgentSystem:
    """Obtém a instância global do sistema de agentes"""
    return core_system
