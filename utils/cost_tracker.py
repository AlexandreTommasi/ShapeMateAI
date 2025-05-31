# utils/cost_tracker.py
from typing import Dict, Any, Optional, List
import time
import json
import os
from datetime import datetime

# Preços por 1000 tokens (em USD) - Configuração para o DeepSeek
# Valores aproximados, ajuste conforme necessário
PRICING = {
    "deepseek-chat": {
        "input": 0.0020,  # $0.0020 por 1000 tokens de entrada
        "output": 0.0080   # $0.0080 por 1000 tokens de saída
    }
}

class CostTracker:
    """Classe para rastrear os custos das chamadas de API."""
    
    def __init__(self, model_name: str, log_file: str = "api_costs.json"):
        """Inicializa o rastreador de custos.
        
        Args:
            model_name: Nome do modelo usado
            log_file: Arquivo para registrar os custos
        """
        self.model_name = model_name
        self.log_file = log_file
        self.session_start = time.time()
        self.session_costs = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
        """Calcula o custo de uma chamada à API.
        
        Args:
            input_tokens: Quantidade de tokens de entrada
            output_tokens: Quantidade de tokens de saída
            
        Returns:
            Dicionário com detalhes do custo
        """
        model_pricing = PRICING.get(self.model_name, {"input": 0.0020, "output": 0.0080})
        
        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]
        total_cost = input_cost + output_cost
        
        # Atualiza os totais da sessão
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost
        
        cost_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": self.model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost
        }
        
        self.session_costs.append(cost_info)
        self._log_cost(cost_info)
        
        return cost_info
    
    def estimate_tokens(self, text: str) -> int:
        """Estima a quantidade de tokens em um texto.
        
        Esta é uma estimativa simples. Para maior precisão,
        considere usar bibliotecas como tiktoken.
        
        Args:
            text: Texto para estimar tokens
            
        Returns:
            Número estimado de tokens
        """
        # Estimativa simples: 1 token ~= 4 caracteres em inglês
        # Para português, pode ser um pouco diferente
        return len(text) // 3
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retorna um resumo dos custos da sessão atual."""
        return {
            "session_duration_seconds": time.time() - self.session_start,
            "total_requests": len(self.session_costs),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": self.total_cost
        }
    
    def _log_cost(self, cost_info: Dict[str, Any]) -> None:
        """Registra informações de custo no arquivo de log."""
        try:
            # Cria o diretório logs se não existir
            os.makedirs("logs", exist_ok=True)
            log_path = os.path.join("logs", self.log_file)
            
            # Lê registros existentes ou cria uma lista vazia
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []
                
            # Adiciona o novo registro
            logs.append(cost_info)
            
            # Salva de volta no arquivo
            with open(log_path, "w") as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Erro ao registrar custo: {e}")
            
    def format_cost_message(self, cost_info: Dict[str, Any]) -> str:
        """Formata uma mensagem de custo para exibição ao usuário."""
        return (
            f"\n--- Informações de Custo ---\n"
            f"Tokens de entrada: {cost_info['input_tokens']}\n"
            f"Tokens de saída: {cost_info['output_tokens']}\n"
            f"Custo total: ${cost_info['total_cost_usd']:.6f} USD\n"
            f"------------------------"
        )