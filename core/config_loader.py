"""
Configuration loader for agent and task configurations
Manages loading and validation of configurations from files or database
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .core import (
    AgentConfig, TaskConfig, SystemConfig, AgentType, TaskType, TaskPriority
)

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exceção para erros de configuração"""
    pass


class ConfigLoader:
    """Carregador de configurações para agentes e tarefas"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Sempre usar o diretório raiz do projeto
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent  # Volta 2 níveis: core -> raiz
            self.config_dir = project_root / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # Não criar diretórios automaticamente - devem existir na pasta raiz
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Diretório de configuração não encontrado: {self.config_dir}")
        
        # Diretórios específicos
        self.agents_dir = self.config_dir / "agents"
        self.tasks_dir = self.config_dir / "tasks"
        self.templates_dir = self.config_dir / "templates"
        
        # Verificar se diretórios existem (não criar automaticamente)
        if not self.agents_dir.exists():
            raise FileNotFoundError(f"Diretório de agentes não encontrado: {self.agents_dir}")
        if not self.tasks_dir.exists():
            self.tasks_dir.mkdir(exist_ok=True)  # Apenas tasks pode ser criado se necessário
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(exist_ok=True)  # Apenas templates pode ser criado se necessário
    
    def load_agent_config(self, agent_type: AgentType) -> AgentConfig:
        """Carrega configuração de um agente específico"""
        config_file = self.agents_dir / f"{agent_type.value}.yaml"
        
        if not config_file.exists():
            # Criar configuração padrão se não existir
            default_config = self._create_default_agent_config(agent_type)
            self.save_agent_config(default_config)
            return default_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            return self._dict_to_agent_config(config_data)
            
        except Exception as e:
            logger.error(f"Error loading agent config for {agent_type.value}: {str(e)}")
            raise ConfigurationError(f"Failed to load agent config: {str(e)}")
    
    def save_agent_config(self, config: AgentConfig):
        """Salva configuração de um agente"""
        config_file = self.agents_dir / f"{config.agent_type.value}.yaml"
        
        try:
            config_dict = config.to_dict()
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                
            logger.info(f"Agent config saved: {config.agent_type.value}")
            
        except Exception as e:
            logger.error(f"Error saving agent config: {str(e)}")
            raise ConfigurationError(f"Failed to save agent config: {str(e)}")
    
    def load_task_config(self, task_type: TaskType) -> TaskConfig:
        """Carrega configuração de uma tarefa específica"""
        config_file = self.tasks_dir / f"{task_type.value}.yaml"
        
        if not config_file.exists():
            # Criar configuração padrão se não existir
            default_config = self._create_default_task_config(task_type)
            self.save_task_config(default_config)
            return default_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            return self._dict_to_task_config(config_data)
            
        except Exception as e:
            logger.error(f"Error loading task config for {task_type.value}: {str(e)}")
            raise ConfigurationError(f"Failed to load task config: {str(e)}")
    
    def save_task_config(self, config: TaskConfig):
        """Salva configuração de uma tarefa"""
        config_file = self.tasks_dir / f"{config.task_type.value}.yaml"
        
        try:
            config_dict = config.to_dict()
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                
            logger.info(f"Task config saved: {config.task_type.value}")
            
        except Exception as e:
            logger.error(f"Error saving task config: {str(e)}")
            raise ConfigurationError(f"Failed to save task config: {str(e)}")
    
    def load_system_template(self, template_name: str) -> Dict[str, Any]:
        """Carrega template de configuração do sistema"""
        template_file = self.templates_dir / f"{template_name}.yaml"
        
        if not template_file.exists():
            raise ConfigurationError(f"Template {template_name} not found")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            raise ConfigurationError(f"Failed to load template: {str(e)}")
    
    def list_available_configs(self) -> Dict[str, List[str]]:
        """Lista todas as configurações disponíveis"""
        return {
            'agents': [f.stem for f in self.agents_dir.glob("*.yaml")],
            'tasks': [f.stem for f in self.tasks_dir.glob("*.yaml")],
            'templates': [f.stem for f in self.templates_dir.glob("*.yaml")]
        }
    
    def _dict_to_agent_config(self, config_data: Dict[str, Any]) -> AgentConfig:
        """Converte dicionário para AgentConfig"""
        try:
            return AgentConfig(
                agent_type=AgentType(config_data['agent_type']),
                name=config_data['name'],
                description=config_data['description'],
                system_prompt=config_data['system_prompt'],
                supported_tasks=[TaskType(task) for task in config_data.get('supported_tasks', [])],
                tools=config_data.get('tools', []),
                model_name=config_data.get('model_name', 'deepseek-chat'),
                temperature=config_data.get('temperature', 0.7),
                max_tokens=config_data.get('max_tokens', 2000),
                max_context_length=config_data.get('max_context_length', 8000),
                specialized_prompts=config_data.get('specialized_prompts', {}),
                personality_traits=config_data.get('personality_traits', {})
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required field in agent config: {e}")
    
    def _dict_to_task_config(self, config_data: Dict[str, Any]) -> TaskConfig:
        """Converte dicionário para TaskConfig"""
        try:
            return TaskConfig(
                task_type=TaskType(config_data['task_type']),
                priority=TaskPriority(config_data.get('priority', TaskPriority.MEDIUM.value)),
                required_context=config_data.get('required_context', []),
                tools_required=config_data.get('tools_required', []),
                max_iterations=config_data.get('max_iterations', 10),
                timeout_seconds=config_data.get('timeout_seconds', 300),
                success_criteria=config_data.get('success_criteria', {}),
                fallback_strategy=config_data.get('fallback_strategy')
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required field in task config: {e}")
    
    def _create_default_agent_config(self, agent_type: AgentType) -> AgentConfig:
        """Cria configuração padrão para um agente"""
        default_configs = {
            AgentType.NUTRITIONIST: {
                'name': 'Nutricionista Virtual',
                'description': 'Especialista em nutrição e planejamento alimentar',
                'system_prompt': '''Você é um nutricionista virtual especializado e experiente. 
                Seu objetivo é fornecer orientações nutricionais personalizadas, criar planos alimentares 
                e educar os usuários sobre hábitos alimentares saudáveis.
                
                Características:
                - Empático e compreensivo
                - Baseado em evidências científicas
                - Focado na saúde e bem-estar do usuário
                - Capaz de adaptar recomendações ao perfil individual
                
                Sempre considere o perfil do usuário, suas metas, restrições alimentares e preferências.''',
                'supported_tasks': [
                    TaskType.CONSULTATION,
                    TaskType.MEAL_PLANNING,
                    TaskType.HEALTH_ASSESSMENT,
                    TaskType.GOAL_SETTING,
                    TaskType.EDUCATION
                ],
                'personality_traits': {
                    'empathy': 0.9,
                    'professionalism': 0.95,
                    'patience': 0.9,
                    'encouraging': 0.8
                }
            },
            AgentType.FITNESS_TRAINER: {
                'name': 'Personal Trainer Virtual',
                'description': 'Especialista em exercícios físicos e condicionamento',
                'system_prompt': '''Você é um personal trainer virtual qualificado e motivador.
                Seu objetivo é criar programas de exercícios personalizados e motivar os usuários
                a alcançarem seus objetivos de fitness.''',
                'supported_tasks': [
                    TaskType.CONSULTATION,
                    TaskType.WORKOUT_PLANNING,
                    TaskType.GOAL_SETTING,
                    TaskType.PROGRESS_TRACKING
                ]
            }
        }
        
        config_data = default_configs.get(agent_type, {})
        if not config_data:
            config_data = {
                'name': f'Agente {agent_type.value}',
                'description': f'Agente especializado em {agent_type.value}',
                'system_prompt': f'Você é um assistente especializado em {agent_type.value}.',
                'supported_tasks': [TaskType.CONSULTATION]
            }
        
        return AgentConfig(
            agent_type=agent_type,
            name=config_data['name'],
            description=config_data['description'],
            system_prompt=config_data['system_prompt'],
            supported_tasks=config_data.get('supported_tasks', []),
            personality_traits=config_data.get('personality_traits', {})
        )
    
    def _create_default_task_config(self, task_type: TaskType) -> TaskConfig:
        """Cria configuração padrão para uma tarefa"""
        default_configs = {
            TaskType.CONSULTATION: {
                'priority': TaskPriority.HIGH,
                'required_context': ['user_profile', 'health_data'],
                'max_iterations': 5,
                'timeout_seconds': 180
            },
            TaskType.MEAL_PLANNING: {
                'priority': TaskPriority.MEDIUM,
                'required_context': ['user_profile', 'dietary_preferences', 'health_goals'],
                'tools_required': ['nutrition_calculator', 'recipe_database'],
                'max_iterations': 8,
                'timeout_seconds': 300
            },
            TaskType.WORKOUT_PLANNING: {
                'priority': TaskPriority.MEDIUM,
                'required_context': ['user_profile', 'fitness_level', 'equipment_access'],
                'tools_required': ['exercise_database', 'fitness_calculator'],
                'max_iterations': 6,
                'timeout_seconds': 240
            }
        }
        
        config_data = default_configs.get(task_type, {})
        
        return TaskConfig(
            task_type=task_type,
            priority=TaskPriority(config_data.get('priority', TaskPriority.MEDIUM.value)),
            required_context=config_data.get('required_context', []),
            tools_required=config_data.get('tools_required', []),
            max_iterations=config_data.get('max_iterations', 10),
            timeout_seconds=config_data.get('timeout_seconds', 300)
        )


# Instância global do carregador de configurações
config_loader = ConfigLoader()


def get_config_loader() -> ConfigLoader:
    """Obtém a instância global do carregador de configurações"""
    return config_loader
