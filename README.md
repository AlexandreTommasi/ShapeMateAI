# ShapeMateAI 🍎💪

**ShapeMateAI** é uma plataforma de assistência nutricional inteligente que utiliza Inteligência Artificial para fornecer orientações nutricionais personalizadas.

## Visão Geral

O ShapeMateAI funciona por meio de um agente de conversação AI especializado em nutrição, chamado **Nutrion**, que pode:
- Conversar naturalmente com usuários sobre temas relacionados à nutrição
- Adaptar suas respostas com base no perfil do usuário
- Rastrear custos e uso de tokens da API

## Funcionalidades Atuais

### 🤖 Agente Nutrion
- Conversação em linguagem natural sobre nutrição e alimentação
- Integração com perfis de usuário para respostas personalizadas
- Arquitetura modular baseada em grafos de conversa (LangGraph)

### 👤 Gerenciamento de Perfil de Usuário
- Coleta de dados durante o cadastro (informações pessoais, saúde e preferências alimentares)
- Armazenamento local de perfis de usuários em formato JSON
- Respostas personalizadas com base no perfil do usuário

### 💻 Interface Web
- Interface intuitiva para interação com o Nutrion
- Sistema de cadastro e login
- Rastreamento de custos e uso de tokens

## Tecnologias Utilizadas

- **Backend**: Python, LangChain, LangGraph
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **API de IA**: DeepSeek API
- **Armazenamento**: JSON local

## Próximas Etapas

- Integração com APIs de dados nutricionais
- Refinamento dos prompts para melhor qualidade de resposta
- Adição de ferramentas de monitoramento de progresso
- Expansão para assistente de bem-estar geral

## Como Iniciar

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure sua chave de API no arquivo `config/settings.py`
4. Execute o servidor:
   ```
   python web/server.py
   ```
5. Acesse `http://localhost:5000` em seu navegador

## Equipe

Desenvolvido pela Equipe ShapeMate para a FETIN 2025.