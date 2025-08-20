# ShapeMateAI

## Objetivo Geral
O **ShapeMateAI** é um sistema inteligente com o objetivo de facilitar a criação e o acompanhamento de dietas personalizadas, utilizando inteligência artificial. O projeto conta com um **Sistema de Cadastro Interativo** e dois agentes principais: um **Nutricionista Virtual (Nutrion)** e um **Assistente de Dia-a-Dia**, que trabalham juntos para proporcionar uma experiência completa de nutrição.

---

## Sistema de Cadastro Interativo

### Conceito:
O cadastro do ShapeMateAI é um **formulário progressivo e divertido** que substitui questionários tradicionais por uma experiência envolvente, coletando apenas informações essenciais para o **Nutricionista Virtual**.

### Características Principais:
- **Rápido**: 3-4 minutos para completar
- **Progressivo**: Uma pergunta por vez com barra de progresso (10 etapas)
- **Seguro**: Criação de conta primeiro, perfil depois
- **Inteligente**: Validação em tempo real e feedback positivo

### Fluxo do Cadastro:

#### **Etapa 1-3: Criação da Conta**
1. **Boas-vindas** - Apresentação motivadora do sistema
2. **E-mail** - Validação em tempo real para e-mails únicos
3. **Senha** - Criação segura com indicador de força

#### **Etapa 4-6: Dados Pessoais**
4. **Nome** - Como gostaria de ser chamado
5. **Informações Básicas** - Idade e sexo
6. **Medidas Corporais** - Peso e altura (sem cálculo de IMC)

#### **Etapa 7-9: Perfil Nutricional**
7. **Objetivo Principal** - Cards visuais para seleção
8. **Atividade Física** - Nível de exercícios atual
9. **Restrições Alimentares** - Checkboxes para alergias/condições

#### **Etapa 10: Finalização**
- Login automático
- Redirecionamento para primeira consulta com o Nutrion

### Tecnologia do Cadastro:
- **Frontend**: HTML5, CSS3, JavaScript responsivo
- **Backend**: Python com Flask
- **Banco de Dados**: SQLite com tabelas relacionais
- **Segurança**: Senhas hasheadas com bcrypt
- **UX**: Validação em tempo real e salvamento automático

### Estrutura de Dados:
```
users: id, email, password_hash, name, profile_completed
user_profiles: user_id, age, gender, weight, height, goals, activity_level, tmb
dietary_restrictions: user_id, restriction_type, description
user_sessions: session_id, user_id, expires_at
```

---

## Agente 1 - **Nutricionista Virtual (Nutrion)** 🥗✨

### Identidade:
O **Nutrion** é um nutricionista profissional com personalidade alegre e motivadora, que combina conhecimento científico com uma abordagem divertida e acessível.

### Personalidade:
- **Profissional Alegre**: Seriedade técnica com leveza e entusiasmo
- **Motivador**: Celebra conquistas e transforma desafios em oportunidades
- **Realista**: Considera orçamento, tempo e limitações do usuário
- **Cientificamente Embasado**: Orientações baseadas em evidências

### Linguagem Característica:
- *"Que máximo!"*, *"Uhuuul!"*, *"Vamos nessa jornada juntos!"*
- *"Calma, vamos por partes e vai dar tudo certo!"*
- *"Porque nutrição boa não precisa quebrar o cofrinho!"*

### Funcionamento:
- Recebe dados básicos do cadastro
- Conduz **anamnese simplificada** focada no essencial:
  1. Objetivo do usuário
  2. Rotina de refeições  
  3. Preferências alimentares
  4. Restrições (se houver)
- Calcula **TMB** baseado nos dados coletados
- Gera dieta personalizada considerando orçamento e praticidade

### Utilização de Tools:
- **API Nutricional**: USDA para dados precisos de alimentos
- **Calculadora TMB**: Cálculo de taxa metabólica basal
- **Gerador de Dietas**: Criação de planos alimentares personalizados
- **Sistema de Custos**: Estimativa de preços para controle orçamentário

---

## Agente 2 - **Assistente do Dia-a-Dia**

### Objetivo:
Fornecer suporte contínuo no cotidiano, facilitando a manutenção da dieta através de substituições inteligentes e análises práticas.

### Funcionamento:
- Monitora aderência à dieta estabelecida
- Avalia compatibilidade de substituições alimentares
- Analisa cardápios externos (restaurantes, eventos)
- Gera listas de compras inteligentes
- Sugere receitas baseadas em ingredientes disponíveis

### Utilização de Tools:
- **Sistema de Substituições**: Ferramenta para avaliar trocas de ingredientes mantendo valor nutricional
- **Analisador de Cardápios**: Tool para análise de menus externos
- **Gerador de Listas de Compras**: Criação automática de listas baseadas na dieta
- **Buscador de Receitas**: Integração com APIs de receitas para sugestões personalizadas
- **Calculadora de Equivalências**: Tool para ajustar quantidades em substituições

### Funcionalidades:
1. **Substituições de Alimentos**:
   O assistente permite que o cliente faça substituições na dieta de acordo com os ingredientes disponíveis em casa. Por exemplo:
   - Se o cliente tiver apenas os ingredientes para fazer strogonoff, ele poderá informar ao assistente, que avaliará se essa substituição é compatível com a dieta e informará se é possível ou não, além de sugerir ajustes nas quantidades.

2. **Análise de Cardápios de Restaurantes**:
   - O cliente pode enviar cardápios de restaurantes, e o assistente verifica se as opções oferecidas no cardápio se encaixam na dieta do cliente.
   - O assistente também ajuda a identificar pratos alternativos dentro das opções do cardápio, para manter a dieta do cliente dentro dos parâmetros necessários.

3. **Listas de Compras**:
   - O assistente também pode gerar listas de compras personalizadas, baseadas na dieta do cliente, garantindo que ele tenha os ingredientes certos em casa.
   - Ele pode também sugerir compras alternativas e mais baratas, caso algum item não esteja disponível ou seja caro.

4. **Receitas da Internet**:
   - O assistente pode buscar receitas online e analisar se elas se encaixam na dieta personalizada do cliente, sugerindo ajustes conforme necessário.

### Fluxo de Funcionamento:
1. Recebe solicitação do cliente (substituição, análise, lista, etc.)
2. Acessa dieta personalizada do banco de dados
3. Processa solicitação usando tools específicas
4. Calcula impactos nutricionais
5. Fornece resposta/sugestão ajustada
6. Atualiza histórico de interações

---

## Projeção de Resultados

### Objetivo:
A IA pode também projetar como o cliente estará após alguns meses de dieta, fornecendo uma visualização realista do seu progresso. Isso ajudará a manter o cliente motivado, ao mostrar o impacto da dieta ao longo do tempo.

---

## Banco de Dados SQLite

### Estrutura Principal:
- **users**: Contas de login (e-mail, senha, dados básicos)
- **user_profiles**: Perfis nutricionais completos
- **dietary_restrictions**: Restrições e alergias alimentares  
- **diets**: Dietas criadas pelo Nutrion (armazenadas como JSON)
- **user_sessions**: Controle de sessões de login

### Características:
- **Segurança**: Senhas hasheadas com bcrypt
- **Relacionais**: Foreign keys para integridade dos dados
- **Escalável**: Estrutura preparada para crescimento
- **Local**: SQLite para desenvolvimento, PostgreSQL para produção

### Funcionalidades:
- Verificação de e-mail único em tempo real
- Autenticação segura com sessões
- Perfis incompletos podem ser retomados
- TMB calculado e armazenado pelo Nutrion
- Histórico de dietas e atualizações

---

## Fluxo Completo do Sistema

### 1. **Cadastro** (3-4 minutos)
- Usuário cria conta com e-mail e senha
- Completa perfil básico de forma interativa
- Login automático após finalização

### 2. **Primeira Consulta com Nutrion**
- Nutrion recebe dados do cadastro
- Conduz anamnese simples e divertida
- Calcula TMB e necessidades nutricionais
- Gera dieta personalizada

### 3. **Acompanhamento Diário**
- Assistente ajuda com substituições
- Análise de cardápios externos
- Listas de compras inteligentes
- Sugestões de receitas

### 4. **Evolução Contínua**
- Atualizações da dieta conforme progresso
- Retornos agendados com o Nutrion
- Projeções de resultados motivadoras

---

## Interface e Tecnologias

### **Stack Tecnológico:**
- **Backend**: Python + Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco**: SQLite (desenvolvimento) + PostgreSQL (produção)
- **IA**: DeepSeek com LangGraph para orquestração
- **APIs**: FatSecret para dados nutricionais
- **Segurança**: bcrypt para senhas, sessões com expiração

### **Interface Principal:**
- **Chat Integrado**: Conversa natural com o Nutrion
- **Dashboard**: Acompanhamento da dieta e progresso
- **Cadastro Progressivo**: 10 etapas interativas
- **Sistema de Login**: Autenticação segura e sessões

### **Objetivo Final:**
Criar um **website inteligente** que facilite a vida do usuário, utilizando IA para personalizar, adaptar e acompanhar a dieta de forma simples, divertida e sustentável, respeitando sempre as limitações de orçamento e tempo do usuário. 🚀