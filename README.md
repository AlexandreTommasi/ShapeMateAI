# README.md
'''
# Agente Conversacional com LangGraph

Um agente de IA conversacional simples inspirado no ChatGPT, construído com LangGraph e LangChain.

## Estrutura do Projeto

```
conversational_agent/
├── main.py             # Ponto de entrada e interface do agente
├── agent/              # Módulos do agente
│   ├── __init__.py
│   ├── core.py         # Lógica principal e grafo do agente
│   ├── memory.py       # Gerenciamento de memória da conversa
│   └── prompts.py      # Templates de prompts
├── config/             # Configurações
│   ├── __init__.py
│   └── settings.py     # Configurações do agente e API
└── README.md           # Documentação
```

## Instalação

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install langchain langchain-openai langgraph python-dotenv
   ```
3. Crie um arquivo `.env` na raiz do projeto com sua chave da OpenAI:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```

## Uso

### Como Biblioteca

```python
from main import ConversationalAgent

# Criar o agente
agent = ConversationalAgent()

# Iniciar a sessão
welcome_message = agent.start_session()
print(welcome_message)

# Enviar mensagens
response = agent.process_message("Olá, como vai você?")
print(response)

# Encerrar a sessão
agent.end_session()
```

### Interface de Linha de Comando

Para usar a interface de linha de comando integrada:

```
python main.py
```

Digite "sair", "exit", "quit" ou "tchau" para encerrar a conversa.

## Personalização

Você pode personalizar o agente modificando:

- O prompt de sistema em `prompts.py`
- O modelo de linguagem em `settings.py`
- A temperatura e outros parâmetros para ajustar o estilo das respostas
- A estrutura do grafo em `core.py` para adicionar mais funcionalidades

## Recursos

O agente mantém um histórico completo da conversa e usa esse contexto para gerar respostas mais relevantes e coerentes. Ele é construído com um fluxo simples de processamento de entrada e geração de resposta, mas pode ser facilmente estendido para incluir mais capacidades.
'''