# ShapeMateAI - Sistema Expandido

## 🚀 Novas Funcionalidades

### 🤖 Dois Agentes IA Especializados

#### 1. **Nutricionista IA** - Consultas Profissionais
- **Foco**: Consultas completas, criação de planos alimentares, PDF/JSON das dietas
- **Acesso**: `/chat` 
- **Tasks**:
  - `CONSULTATION` - Coleta completa de dados do cliente
  - `MEAL_PLANNING` - Planejamento detalhado das refeições  
  - `PDF_GENERATION` - Criação do JSON/PDF com dieta personalizada

#### 2. **Assistente Diário** - Acompanhamento no Dia a Dia
- **Foco**: Suporte diário, substituições, listas de compras, análise de cardápios
- **Acesso**: `/daily-assistant`
- **Tasks**:
  - `DAILY_SUPPORT` - Auxílio diário e acompanhamento da dieta
  - `SHOPPING_LIST` - Criação de lista de supermercado
  - `DIET_SUBSTITUTION` - Substituições conforme pedidos do usuário
  - `MENU_ANALYSIS` - Análise de cardápios para melhores escolhas
  - `MEAL_SUGGESTION` - Sugestões de refeições

### 📋 Páginas de Gerenciamento

#### 🍎 **Minha Dieta** (`/diet`)
- Visualizar dieta atual criada pelo nutricionista
- Upload de PDF de dietas externas
- Processamento automático de PDFs com IA
- Exibição organizada de planos de refeições
- Informações nutricionais detalhadas

#### 🛒 **Lista de Compras** (`/shopping-list`)
- Criação automática baseada na dieta
- Listas personalizadas
- Organização por categorias
- Marcar itens como comprados
- Múltiplas listas simultâneas

#### 📦 **Estoque em Casa** (`/inventory`)
- Gerenciar itens que você tem em casa
- Categorização automática
- Controle de validade
- Integração com assistente diário
- Estatísticas do estoque

## 🔄 Sistema de Comunicação Entre Agentes

### **Dados Compartilhados**
- Os agentes compartilham informações sobre o usuário
- Nutricionista → Daily Assistant: dados da consulta, dieta criada
- Daily Assistant → Nutricionista: feedback diário, dificuldades

### **Fluxo de Trabalho**
1. **Consulta com Nutricionista**: Coleta dados e cria dieta
2. **Dados salvos** no sistema compartilhado
3. **Daily Assistant** acessa automaticamente as informações
4. **Acompanhamento contínuo** com ambos agentes atualizados

## 🛠️ Estrutura Técnica

### **Novos Utilitários**
```
utils/
├── pdf_processor/          # Processamento de PDFs
│   ├── diet_extractor.py   # Extração inteligente de dietas
│   └── __init__.py
├── diet_manager/           # Gerenciamento de dietas
│   ├── diet_storage.py     # Armazenamento e busca
│   └── __init__.py
└── inventory_manager/      # Gestão de estoque (futuro)
```

### **Banco de Dados Expandido**
- `user_diets` - Armazenamento de dietas
- `shopping_lists` - Listas de compras
- `home_inventory` - Estoque doméstico

### **APIs REST**
```
# Daily Assistant
POST /api/daily-assistant/start
POST /api/daily-assistant/message

# Dieta
POST /api/diet/upload

# Lista de Compras  
POST /api/shopping-list/create
GET  /api/shopping-list/{id}

# Estoque
POST /api/inventory/update
```

## 🎨 Interface Atualizada

### **Navegação Reorganizada**
- **Agentes IA**: Nutricionista e Assistente Diário
- **Minha Nutrição**: Dieta, Lista de Compras, Estoque

### **Design Consistente**
- Cores diferenciadas por agente (Azul: Nutricionista, Verde: Daily Assistant)
- Interface responsiva
- Modals para uploads e edições
- Indicadores visuais de status

## 🚦 Como Usar

### **1. Primeiro Contato**
1. Faça cadastro/login
2. Converse com o **Nutricionista** para criar sua dieta
3. Acesse **Minha Dieta** para ver o resultado

### **2. Dia a Dia**
1. Use o **Assistente Diário** para suporte contínuo
2. Crie **Listas de Compras** baseadas na sua dieta
3. Gerencie seu **Estoque** para melhor planejamento

### **3. Upload de Dieta Externa**
1. Acesse **Minha Dieta**
2. Clique em "Carregar Dieta PDF"
3. O sistema extrai automaticamente as informações
4. Revise e confirme os dados extraídos

## 🔮 Recursos Futuros
- Sincronização com aplicativos de delivery
- Integração com wearables
- Análise de fotos de refeições
- Relatórios de progresso automáticos
- Alertas de validade de alimentos

---

## 🏃‍♂️ Para Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python web/app.py
```

**Acesse**: http://localhost:5000

---

*Sistema desenvolvido para fornecer suporte nutricional completo com IA avançada* 🤖🥗
