#!/usr/bin/env python
# terminal_chat.py
"""
Interface de terminal para conversar com o nutricionista virtual do ShapeMateAI.
"""

import sys
import os
import time
from datetime import datetime

# Adicionamos a pasta atual ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.memory import ConversationMemory
from agent.nutritionist.nutritionist_prompts import SYSTEM_PROMPT as NUTRITIONIST_PROMPT
from core.core import llm, cost_tracker

# Definir cores para melhor visualização no terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Exibe o cabeçalho da aplicação no terminal."""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.BLUE}=" * 80)
    print(f"                           SHAPEMATE AI - NUTRICIONISTA VIRTUAL")
    print(f"=" * 80)
    
    print(f"\n{Colors.YELLOW}Conversando com: {Colors.BOLD}Nutricionista Virtual{Colors.ENDC}")
    print("\nO nutricionista pode ajudar com:")
    print("- Criação de planos alimentares personalizados")
    print("- Cálculo de necessidades calóricas")
    print("- Ajustes de dieta baseados em seus objetivos")
    print("- Resposta a dúvidas sobre nutrição")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}=" * 80 + f"{Colors.ENDC}\n")

def format_message(sender, message):
    """Formata a mensagem para exibição no terminal."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if sender == "AI":
        prefix = f"{Colors.GREEN}[{timestamp}] AI:{Colors.ENDC}"
    else:
        prefix = f"{Colors.YELLOW}[{timestamp}] Você:{Colors.ENDC}"
    
    return f"{prefix} {message}"

def get_welcome_message():
    """Retorna a mensagem de boas-vindas do nutricionista."""
    return "Olá! Sou seu nutricionista virtual. Como posso ajudar você com sua alimentação hoje?"

def main():
    """Função principal que executa o chat no terminal."""
    # Inicializa a memória da conversa com o prompt do nutricionista
    memory = ConversationMemory(NUTRITIONIST_PROMPT)
    
    # Exibe o cabeçalho e a mensagem de boas-vindas
    print_header()
    welcome_message = get_welcome_message()
    print(format_message("AI", welcome_message))
    memory.add_ai_message(welcome_message)
    
    # Loop principal da conversa
    while True:
        # Obtém a entrada do usuário
        user_input = input(f"\n{Colors.YELLOW}Você:{Colors.ENDC} ")
        
        # Verifica se o usuário quer sair
        if user_input.lower() in ["sair", "exit", "quit", "q"]:
            # Exibe estatísticas de custo ao sair
            summary = cost_tracker.get_session_summary()
            print(f"\n{Colors.BLUE}Resumo da sessão:{Colors.ENDC}")
            print(f"- Tokens de entrada: {summary['total_input_tokens']}")
            print(f"- Tokens de saída: {summary['total_output_tokens']}")
            print(f"- Custo estimado: ${summary['total_cost_usd']:.6f} USD")
            print(f"\n{Colors.BLUE}Obrigado por usar o ShapeMateAI!{Colors.ENDC}")
            break
        
        # Verifica se o usuário quer limpar o chat
        if user_input.lower() in ["limpar", "clear", "cls"]:
            memory = ConversationMemory(NUTRITIONIST_PROMPT)
            print_header()
            welcome_message = get_welcome_message()
            print(format_message("AI", welcome_message))
            memory.add_ai_message(welcome_message)
            continue
        
        # Adiciona a mensagem do usuário à memória
        memory.add_user_message(user_input)
        
        # Exibe um indicador de "digitando..."
        print(f"\n{Colors.BLUE}Processando resposta...{Colors.ENDC}")
        
        # Obtém o histórico da conversa
        message_history = memory.get_message_history()
        
        # Estima os tokens de entrada
        input_text = " ".join([msg.content for msg in message_history])
        input_tokens = cost_tracker.estimate_tokens(input_text)
        
        try:
            # Gera a resposta usando o LLM
            start_time = time.time()
            response = llm.invoke(message_history)
            ai_response = response.content
            response_time = time.time() - start_time
            
            # Limpa a linha do "processando..."
            print("\033[A\033[K", end="")
            
            # Exibe a resposta
            print(format_message("AI", ai_response))
            
            # Adiciona a resposta à memória
            memory.add_ai_message(ai_response)
            
            # Estima os tokens de saída e calcula o custo
            output_tokens = cost_tracker.estimate_tokens(ai_response)
            cost_info = cost_tracker.calculate_cost(input_tokens, output_tokens)
            
            # Exibe informações sobre tokens e custo (opcional, comentado por padrão)
            # print(f"\n{Colors.BLUE}Info: {input_tokens} tokens entrada, {output_tokens} tokens saída, ${cost_info['total_cost_usd']:.6f} USD, {response_time:.2f}s{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.RED}Erro ao processar resposta: {str(e)}{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BLUE}Chat encerrado pelo usuário. Obrigado por usar o ShapeMateAI!{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Erro inesperado: {str(e)}{Colors.ENDC}")