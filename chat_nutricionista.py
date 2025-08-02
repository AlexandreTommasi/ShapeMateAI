"""
Chat com Agente Nutricionista - ShapeMateAI
Versão simplificada para testes
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Carregar variáveis de ambiente
load_dotenv()


class NutritionistChat:
    """Chat simplificado com o agente nutricionista"""
    
    def __init__(self):
        # Verificar API key
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("❌ DEEPSEEK_API_KEY não encontrada no arquivo .env")
        
        # Configurar LLM
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            temperature=0.7,
            max_tokens=2000,
            openai_api_key=self.api_key,
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        # Prompt do sistema 
        self.system_prompt = """Você é um nutricionista virtual qualificado e empático.

SUAS FUNÇÕES:
- Fornecer orientações nutricionais personalizadas
- Criar planos alimentares baseados no perfil do usuário
- Calcular necessidades calóricas e macronutrientes
- Avaliar IMC e status nutricional
- Orientar sobre alimentação saudável
- Adaptar recomendações para objetivos específicos

INSTRUÇÕES:
- Seja sempre empático e acolhedor
- Base suas respostas em evidências científicas
- Considere o perfil individual de cada usuário
- Ofereça soluções práticas e aplicáveis
- Calcule IMC quando altura e peso estiverem disponíveis
- Sugira calorias diárias quando possível
- Inclua exemplos de refeições quando relevante

CÁLCULOS ÚTEIS:
- IMC = peso (kg) / altura (m)²
- TMB (feminino) = 447,593 + (9,247 × peso) + (3,098 × altura cm) - (4,330 × idade)
- TMB (masculino) = 88,362 + (13,397 × peso) + (4,799 × altura cm) - (5,677 × idade)
- Fatores de atividade: sedentário (1.2), leve (1.375), moderado (1.55), ativo (1.725), muito ativo (1.9)

Sempre personalize suas resposas com base no perfil fornecido."""
    
    def chat(self, user_message: str, user_profile: Dict[str, Any] = None) -> str:
        """Processa mensagem do usuário"""
        try:
            # Criar contexto com perfil
            context = self._build_context(user_message, user_profile or {})
            
            # Criar mensagens
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=context)
            ]
            
            # Gerar resposta
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Erro ao processar mensagem: {str(e)}"
    
    def _build_context(self, message: str, profile: Dict[str, Any]) -> str:
        """Constrói contexto estruturado"""
        context_parts = [f"PERGUNTA: {message}"]
        
        if profile:
            profile_info = []
            for key, value in profile.items():
                if value is not None and value != "":
                    formatted_key = key.replace('_', ' ').title()
                    profile_info.append(f"- {formatted_key}: {value}")
            
            if profile_info:
                context_parts.append(f"PERFIL DO USUÁRIO:\n" + "\n".join(profile_info))
        
        return "\n\n".join(context_parts)


def main():
    """Interface de chat principal"""
    print("🥗 === SHAPEMATE AI - NUTRICIONISTA VIRTUAL === 🥗")
    print("Digite 'sair' para encerrar")
    print("Digite 'perfil' para alterar seu perfil")
    print("-" * 50)
    
    try:
        chat_agent = NutritionistChat()
        print("✅ Conexão estabelecida com o nutricionista virtual!")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return
    
    # Perfil padrão
    user_profile = {
        'name': 'Usuário',
        'age': None,
        'weight': None,
        'height': None,
        'gender': None,
        'activity_level': None,
        'goal': None,
        'dietary_restrictions': None,
        'allergies': None
    }
    
    print(f"\n👋 Olá! Sou seu nutricionista virtual.")
    print("Para um atendimento personalizado, vou precisar conhecer um pouco sobre você.")
    print("Vamos começar? (ou digite sua pergunta diretamente)\n")
    
    while True:
        try:
            user_input = input("💬 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit', 'tchau']:
                print("\n🌟 Obrigado por usar o ShapeMateAI!")
                print("Lembre-se: alimentação saudável é um investimento na sua saúde! 💚")
                break
            
            if user_input.lower() == 'perfil':
                update_profile(user_profile)
                continue
            
            if not user_input:
                print("💭 Digite sua pergunta ou 'perfil' para atualizar seus dados.")
                continue
            
            # Processar mensagem
            print("\n🥗 Nutricionista: ", end="", flush=True)
            
            response = chat_agent.chat(user_input, user_profile)
            print(response)
            print("\n" + "-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando... Cuide-se bem!")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")


def update_profile(profile: Dict[str, Any]):
    """Atualiza perfil do usuário"""
    print("\n📋 === ATUALIZAÇÃO DE PERFIL ===")
    print("Pressione Enter para manter o valor atual")
    
    # Nome
    current_name = profile.get('name', 'Usuário')
    new_name = input(f"Nome [{current_name}]: ").strip()
    if new_name:
        profile['name'] = new_name
    
    # Idade
    current_age = profile.get('age', '')
    new_age = input(f"Idade [{current_age}]: ").strip()
    if new_age:
        try:
            profile['age'] = int(new_age)
        except ValueError:
            print("⚠️ Idade inválida. Mantendo valor anterior.")
    
    # Peso
    current_weight = profile.get('weight', '')
    new_weight = input(f"Peso em kg [{current_weight}]: ").strip()
    if new_weight:
        try:
            profile['weight'] = float(new_weight)
        except ValueError:
            print("⚠️ Peso inválido. Mantendo valor anterior.")
    
    # Altura
    current_height = profile.get('height', '')
    new_height = input(f"Altura em cm [{current_height}]: ").strip()
    if new_height:
        try:
            profile['height'] = float(new_height)
        except ValueError:
            print("⚠️ Altura inválida. Mantendo valor anterior.")
    
    # Gênero
    current_gender = profile.get('gender', '')
    new_gender = input(f"Gênero (M/F) [{current_gender}]: ").strip().upper()
    if new_gender in ['M', 'F', 'MASCULINO', 'FEMININO']:
        profile['gender'] = 'masculino' if new_gender in ['M', 'MASCULINO'] else 'feminino'
    
    # Nível de atividade
    print("\nNível de atividade:")
    print("1 - Sedentário | 2 - Leve | 3 - Moderado | 4 - Ativo | 5 - Muito ativo")
    current_activity = profile.get('activity_level', '')
    activity_input = input(f"Escolha (1-5) [{current_activity}]: ").strip()
    
    activity_map = {
        '1': 'sedentário', '2': 'leve', '3': 'moderado', 
        '4': 'ativo', '5': 'muito ativo'
    }
    if activity_input in activity_map:
        profile['activity_level'] = activity_map[activity_input]
    
    # Objetivo
    print("\nObjetivo:")
    print("1 - Perder peso | 2 - Manter peso | 3 - Ganhar peso | 4 - Ganhar massa muscular")
    current_goal = profile.get('goal', '')
    goal_input = input(f"Escolha (1-4) [{current_goal}]: ").strip()
    
    goal_map = {
        '1': 'perder peso', '2': 'manter peso', 
        '3': 'ganhar peso', '4': 'ganhar massa muscular'
    }
    if goal_input in goal_map:
        profile['goal'] = goal_map[goal_input]
    
    # Restrições
    current_restrictions = profile.get('dietary_restrictions', '')
    new_restrictions = input(f"Restrições alimentares [{current_restrictions}]: ").strip()
    if new_restrictions:
        profile['dietary_restrictions'] = new_restrictions
    
    # Alergias
    current_allergies = profile.get('allergies', '')
    new_allergies = input(f"Alergias alimentares [{current_allergies}]: ").strip()
    if new_allergies:
        profile['allergies'] = new_allergies
    
    print("\n✅ Perfil atualizado com sucesso!")
    print("-" * 50)


if __name__ == "__main__":
    main()
