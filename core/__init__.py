"""
Core module initialization
Exports main classes and functions for the ShapeMateAI agent system
"""

# Core system components
from .core import (
    AgentType,
    TaskType,
    TaskPriority,
    AgentState,
    TaskConfig,
    AgentConfig,
    SystemConfig,
    BaseAgent,
    CoreAgentSystem,
    get_core_system
)

# Configuration management
from .config_loader import (
    ConfigLoader,
    ConfigurationError,
    get_config_loader
)

__all__ = [
    # Enums
    'AgentType',
    'TaskType', 
    'TaskPriority',
    
    # Core types
    'AgentState',
    'TaskConfig',
    'AgentConfig',
    'SystemConfig',
    
    # Base classes
    'BaseAgent',
    'CoreAgentSystem',
    
    # System functions
    'get_core_system',
    
    # Configuration
    'ConfigLoader',
    'ConfigurationError',
    'get_config_loader'
]

# Version info
__version__ = "1.0.0"
__author__ = "ShapeMateAI Team"
