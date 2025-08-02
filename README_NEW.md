# ShapeMateAI - Sistema de Nutrição Inteligente

Sistema completo de cadastro e chat nutricional com IA, desenvolvido em Python com Flask e SQLite.

## 🎯 Funcionalidades

### ✅ Implementadas
- **Sistema de Cadastro Completo**: Registro de usuários com perfil nutricional detalhado
- **Autenticação Segura**: Login com hash de senhas usando bcrypt
- **Banco de Dados SQLite**: Estrutura organizada para usuários, perfis e chat
- **Interface Web Moderna**: Design responsivo com Bootstrap 5
- **Validações Completas**: Validação de dados tanto no frontend quanto backend
- **Sistema de Chat**: Interface preparada para integração com nutricionista IA

### 🚧 Em Desenvolvimento
- **Nutricionista IA**: Integração com sistema de IA para orientações nutricionais
- **Planos Alimentares**: Geração automática de cardápios personalizados
- **Acompanhamento**: Sistema de progresso e métricas

## 📁 Estrutura do Projeto

```
ShapeMateAI/
├── database/                 # Módulo de banco de dados
│   ├── __init__.py          # Inicialização do módulo
│   ├── models.py            # Modelos de dados (Database class)
│   ├── schemas.py           # Validações e schemas
│   ├── services.py          # Serviços de banco de dados
│   └── config.py            # Configurações do banco
├── register/               # Sistema de cadastro
│   └── registration.py      # Sistema de registro
├── web/                     # Interface web
│   ├── app.py              # Servidor Flask principal
│   ├── templates/          # Templates HTML
│   │   ├── base.html       # Template base
│   │   ├── login.html      # Página de login
│   │   ├── register.html   # Página de cadastro
│   │   ├── dashboard.html  # Dashboard do usuário
│   │   ├── chat.html       # Interface de chat
│   │   └── error.html      # Página de erro
│   └── static/             # Arquivos estáticos
│       ├── css/style.css   # Estilos customizados
│       └── js/app.js       # JavaScript da aplicação
├── agent/                  # (Existente) Agente nutricional
├── api/                    # (Existente) APIs externas
├── config/                 # (Existente) Configurações
├── core/                   # (Existente) Core do sistema
├── docs/                   # Documentação
├── utils/                  # Utilitários
├── init_system.py          # Script de inicialização
├── pyproject.toml          # Configuração do projeto (uv/pip)
├── requirements.txt        # Dependências Python (legacy)
└── README.md              # Este arquivo
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recomendado) ou pip

### 2. Instalação do uv (recomendado)

#### Windows (PowerShell)
```powershell
# Instalar uv
irm https://astral.sh/uv/install.ps1 | iex

# Ou via pip
pip install uv
```

#### macOS/Linux
```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

### 3. Configuração do Ambiente

#### Com uv (Recomendado)
```bash
# Criar e ativar ambiente virtual
uv venv

# Ativar o ambiente
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Instalar dependências
uv pip install -e .

# Ou instalar dependências de desenvolvimento
uv pip install -e ".[dev,test]"
```

#### Com pip (Alternativo)
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar o ambiente
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Inicialização do Sistema
```bash
python init_system.py
```

Este script irá:
- ✅ Verificar dependências
- 🗃️ Inicializar banco de dados SQLite
- 🧪 Testar sistema de cadastro
- 👤 Criar usuário de teste

### 5. Executar o Servidor Web

#### Método 1: Script direto
```bash
cd web
python app.py
```

#### Método 2: Com uv (se configurado com scripts)
```bash
# Primeiro sincronizar dependências
uv sync

# Depois executar o servidor
uv run shapemate-web
```

#### Método 3: Módulo Python
```bash
python -m web.app
```

### 6. Acessar o Sistema
Abra seu navegador e acesse: `http://localhost:5000`

## 👤 Usuário de Teste

O sistema cria automaticamente um usuário para testes:
- **Email**: `teste@shapemate.ai`
- **Senha**: `123456`

## 🛠️ Comandos Úteis com uv

### Gerenciamento de Dependências
```bash
# Adicionar nova dependência
uv add package-name

# Adicionar dependência de desenvolvimento
uv add --dev package-name

# Remover dependência
uv remove package-name

# Atualizar dependências
uv lock --upgrade

# Sincronizar ambiente com pyproject.toml
uv sync
```

### Execução de Scripts
```bash
# Inicializar sistema
uv run python init_system.py

# Executar testes (quando implementados)
uv run pytest

# Executar formatação de código
uv run black .

# Executar linting
uv run flake8 .
```

### Informações do Ambiente
```bash
# Ver dependências instaladas
uv pip list

# Ver informações do projeto
uv show

# Ver árvore de dependências
uv tree
```

## 📋 Funcionalidades do Cadastro

### Dados Coletados (conforme especificação):
1. **Dados de Acesso**
   - Email (único, validado)
   - Senha (mínimo 6 caracteres, hash bcrypt)

2. **Dados Pessoais**
   - Nome completo
   - Idade (13-120 anos)
   - Gênero (masculino/feminino/outro)

3. **Dados Físicos**
   - Peso (kg, com validação)
   - Altura (metros, com validação)
   - Cálculo automático de IMC

4. **Objetivos**
   - Objetivo principal (perda de peso, ganho de massa, etc.)
   - Nível de atividade física

5. **Informações de Saúde (Opcionais)**
   - Restrições alimentares
   - Condições de saúde
   - Outras observações

## 🔧 APIs Disponíveis

### Autenticação
- `POST /api/register` - Cadastro de usuário
- `POST /api/login` - Login
- `POST /api/logout` - Logout
- `GET /api/profile` - Dados do perfil

### Chat (Preparado para IA)
- `POST /api/chat/start` - Iniciar sessão de chat
- `POST /api/chat/message` - Enviar mensagem
- `GET /api/chat/history` - Histórico de mensagens

### Sistema
- `GET /api/system/health` - Status do sistema

## 🎨 Interface Web

### Design
- **Bootstrap 5**: Framework CSS moderno
- **Font Awesome**: Ícones vetoriais
- **Design Responsivo**: Funciona em desktop e mobile
- **Animações Suaves**: Transições e efeitos visuais

### Páginas
- **Login**: Autenticação de usuários
- **Cadastro**: Formulário multi-etapas com validação
- **Dashboard**: Visão geral do perfil e ações rápidas
- **Chat**: Interface preparada para nutricionista IA

## 🗄️ Banco de Dados

### Tabelas SQLite
1. **users**: Dados de autenticação
2. **user_profiles**: Perfil nutricional completo
3. **chat_sessions**: Sessões de chat
4. **chat_messages**: Mensagens do chat

### Segurança
- Senhas hasheadas com bcrypt
- Validação de dados em múltiplas camadas
- IDs únicos UUID para todas as entidades

## 🔮 Próximos Passos

### Integração Nutricionista IA
- [ ] Conectar com agente nutritional existente
- [ ] Implementar geração de planos alimentares
- [ ] Sistema de recomendações personalizadas

### Funcionalidades Avançadas
- [ ] Upload de fotos de refeições
- [ ] Análise nutricional de alimentos
- [ ] Gráficos de progresso
- [ ] Notificações e lembretes

### Melhorias Técnicas
- [ ] Cache Redis
- [ ] API rate limiting
- [ ] Logs estruturados
- [ ] Testes automatizados

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Execute `python init_system.py` para diagnóstico
3. Consulte os logs do servidor Flask

## 📄 Licença

Projeto desenvolvido para fins educacionais - ShapeMateAI 2025
