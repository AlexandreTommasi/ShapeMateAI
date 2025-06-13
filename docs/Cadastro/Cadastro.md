# Sistema de Cadastro - ShapeMateAI

## Conceito Geral
O cadastro do ShapeMateAI é um **formulário interativo e divertido** que coleta apenas as informações essenciais de forma envolvente, pergunta por pergunta, criando uma experiência agradável para o usuário.

**IMPORTANTE:** O fluxo começa com a criação da conta (e-mail e senha), depois coleta as informações do perfil.

---

## Filosofia do Cadastro

### 🎯 **Objetivos**
- **Rápido**: Máximo 2-3 minutos para completar
- **Divertido**: Interface dinâmica com feedback positivo
- **Essencial**: Apenas dados necessários para o nutricionista
- **Progressivo**: Uma pergunta por vez, com barra de progresso
- **Seguro**: Criação de conta primeiro, depois perfil

### 🚫 **O que NÃO é**
- Questionário longo e chato
- Formulário tradicional com campos estáticos
- Coleta excessiva de dados
- Interface complexa

---

## Fluxo de Perguntas (8 Etapas)

### **1. Boas-vindas** 🎉
```
Tela: "Oi! Bem-vindo(a) ao ShapeMateAI! 🌟"
Texto: "Vamos criar sua conta e começar sua jornada rumo à saúde!"
Botão: "Vamos Começar!"
```

### **2. Criação da Conta - E-mail** 📧
```
Tela: "Primeiro, vamos criar sua conta!"
Pergunta: "Qual seu e-mail?"
Input: Campo de e-mail com validação em tempo real
Validação: Verificar se e-mail já existe
Feedback: "E-mail válido! ✅" ou "Este e-mail já está cadastrado"
```

### **3. Criação da Conta - Senha** 🔒
```
Tela: "Agora crie uma senha segura!"
Pergunta: "Escolha uma senha:"
Inputs: 
- Senha (mínimo 6 caracteres)
- Confirmar senha
Indicador: Barra de força da senha
Feedback: "Senha criada com sucesso! 🔐"
```

### **4. Informações Pessoais - Nome** 👤
```
Tela: "Agora vamos te conhecer melhor!"
Pergunta: "Como você gostaria de ser chamado(a)?"
Input: Campo de texto simples
Feedback: "Prazer te conhecer, [Nome]! 😊"
```

### **5. Informações Básicas** 📊
```
Tela: "Alguns dados básicos sobre você:"
Perguntas em sequência:
- "Qual sua idade?" (seletor ou input numérico)
- "Sexo:" (botões: Masculino/Feminino/Prefiro não dizer)
Feedback: "Perfeito! Já estamos quase lá! 🚀"
```

### **6. Medidas Corporais** ⚖️
```
Tela: "Agora vamos aos números!"
Perguntas:
- "Seu peso atual:" (slider + input em kg)
- "Sua altura:" (slider + input em cm)
Feedback: "Dados registrados! 📈"
Nota: O TMB será calculado pelo Nutrion durante a consulta
```

### **7. Objetivo Principal** 🎯
```
Tela: "Qual é seu grande objetivo?"
Opções (cards clicáveis):
- 🔥 "Emagrecer"
- 💪 "Ganhar músculo" 
- ⚖️ "Manter peso"
- 🌟 "Ter mais energia"
- 🏥 "Cuidar da saúde"
Feedback: "Objetivo definido! Vamos alcançá-lo juntos! 💪"
```

### **8. Atividade Física** 🏃‍♀️
```
Tela: "Como anda sua movimentação?"
Opções (cards visuais):
- 🛋️ "Sedentário (pouco ou nenhum exercício)"
- 🚶 "Leve (1-3 dias/semana)"
- 🏃 "Moderado (3-5 dias/semana)"
- 🏋️ "Intenso (6-7 dias/semana)"
- 🔥 "Muito intenso (2x por dia)"
Feedback: "Anotado! Isso vai ajudar muito no seu plano! 📋"
```

### **9. Restrições Alimentares** 🚫
```
Tela: "Tem alguma restrição alimentar?"
Formato: Checkboxes + campo "Outros"
Opções principais:
□ Nenhuma restrição
□ Diabetes
□ Hipertensão
□ Alergia (especificar)
□ Intolerância à lactose
□ Vegetariano/Vegano
□ Outros: [campo de texto]
Feedback: "Entendido! Vamos respeitar suas necessidades! ✅"
```

### **10. Finalização** 🎊
```
Tela: "Parabéns! Conta criada com sucesso!"
Resumo dos dados + botão "Confirmar"
Mensagem: "Sua conta foi criada! Agora você está pronto para conhecer o Nutrion, 
seu novo parceiro nutricional! 🥗✨"
Botão: "Entrar no ShapeMateAI!"
```

---

## Especificações Técnicas

### 🎨 **Interface e UX**

#### **Elementos Visuais**
- **Barra de Progresso**: 10 etapas claramente marcadas
- **Animações Suaves**: Transições entre perguntas
- **Feedback Visual**: Checkmarks, emojis, cores vibrantes
- **Responsivo**: Funciona bem em mobile e desktop

#### **Interações**
- **Navegação**: Botões "Próximo" e "Voltar"
- **Validação em Tempo Real**: Campos obrigatórios destacados
- **Salvamento Automático**: Progresso salvo a cada etapa
- **Confirmação Visual**: Cada resposta confirmada com feedback positivo

### 📱 **Comportamento por Tipo de Input**

#### **Campos de Autenticação**
- E-mail: Validação de formato + verificação de duplicatas em tempo real
- Senha: Mínimo 6 caracteres, indicador de força, confirmação obrigatória
- Confirmação: Deve ser igual à senha

#### **Campos de Texto**
- Nome: Validação de caracteres
- Outros: Campo aberto com limite de caracteres

#### **Campos Numéricos**
- Idade: 15-100 anos (slider + input)
- Peso: 30-300kg (slider + input)
- Altura: 100-220cm (slider + input)

#### **Seleções**
- Sexo: Botões de rádio estilizados
- Objetivo: Cards grandes e clicáveis
- Atividade: Cards com ícones e descrições
- Restrições: Checkboxes com ícones

### 🔧 **Funcionalidades Especiais**

#### **Validação de E-mail em Tempo Real**
```javascript
// Verificar se e-mail já existe
async function checkEmailExists(email) {
    const response = await fetch('/api/check-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    const data = await response.json();
    return data.exists;
}
```

#### **Indicador de Força da Senha**
```javascript
// Calcular força da senha
function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    return strength;
}
```

#### **Validações**
- Campos obrigatórios claramente marcados
- E-mail único no sistema
- Senha e confirmação devem ser iguais
- Mensagens de erro amigáveis
- Não permitir avanço sem preencher obrigatórios

#### **Salvamento de Progresso**
- LocalStorage para não perder dados
- Possibilidade de sair e voltar depois
- Recuperação automática em caso de problema

---

## Fluxo de Dados

### 📊 **Estrutura dos Dados Coletados**
```json
{
  "account_creation": {
    "email": "string",
    "password": "string (será hasheada)",
    "timestamp": "2025-06-12T10:30:00Z"
  },
  "user_profile": {
    "user_id": "uuid-gerado-após-criar-conta",
    "personal_info": {
      "name": "string",
      "age": "number",
      "gender": "string"
    },
    "body_metrics": {
      "weight": "number (kg)",
      "height": "number (cm)",
      "tmb": "number (calculado pelo Nutrion posteriormente)"
    },
    "goals": {
      "primary_goal": "string",
      "activity_level": "string"
    },
    "restrictions": {
      "dietary_restrictions": ["array"],
      "health_conditions": ["array"],
      "other_notes": "string"
    },
    "profile_completed": true
  }
}
```

### 🔄 **Integração com o Sistema**
1. **Etapas 2-3**: Criação da conta (usuário criado no banco)
2. **Etapas 4-9**: Criação do perfil (dados salvos linked ao user_id)
3. **Etapa 10**: Login automático + redirecionamento
4. **Pós-cadastro**: Usuário logado e pronto para primeira consulta
5. **TMB**: Será calculado pelo Nutrion durante a anamnese

---

## Mensagens e Textos

### 🎭 **Tom da Comunicação**
- **Acolhedor**: "Bem-vindo(a) ao ShapeMateAI!"
- **Motivador**: "Vamos alcançar seus objetivos juntos!"
- **Informal**: "Como você gostaria de ser chamado(a)?"
- **Positivo**: "Perfeito!", "Excelente!", "Quase lá!"
- **Seguro**: "Seus dados estão protegidos! 🔐"

### 📝 **Exemplos de Feedback**
- **Progresso**: "3 de 10 concluído - você está indo muito bem! 🌟"
- **Validação**: "Dados salvos com sucesso! ✅"
- **Erro**: "Ops! Parece que esquecemos de algo aqui 😊"
- **E-mail existente**: "Este e-mail já está cadastrado. Que tal fazer login? 🤔"
- **Finalização**: "Conta criada! Bem-vindo(a) ao ShapeMateAI! 🎉"

---

## Objetivos de Conversão

### 🎯 **Métricas de Sucesso**
- **Taxa de Conclusão**: >80% dos usuários completam o cadastro
- **Tempo Médio**: 3-4 minutos por cadastro completo
- **Abandono por Etapa**: <10% em qualquer etapa
- **Satisfação**: Feedback positivo na primeira impressão

### 🚀 **Próximos Passos Após Cadastro**
1. Login automático (sem precisar inserir e-mail/senha novamente)
2. Redirecionamento para dashboard ou primeira consulta
3. Boas-vindas personalizadas com o nome do usuário
4. Início da jornada nutricional com o Nutrion

---

## Considerações de Implementação

### 🛠️ **Tecnologias Sugeridas**
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ou React)
- **Validação**: JavaScript nativo + validação backend
- **Armazenamento**: LocalStorage (temporário) + SQLite (permanente)
- **Responsividade**: CSS Grid/Flexbox
- **Segurança**: bcrypt para hash de senhas

### 🔒 **Segurança e Privacidade**
- Hash das senhas com bcrypt antes de salvar
- Validação de dados no frontend e backend
- Verificação de e-mail único em tempo real
- LGPD compliance
- Sessão automática após cadastro
- Opção de exclusão de dados

### 📋 **Ordem de Implementação**
1. **Etapas 1-3**: Sistema de criação de conta
2. **Etapas 4-6**: Coleta de dados pessoais básicos
3. **Etapas 7-9**: Coleta de objetivos e restrições
4. **Etapa 10**: Finalização e login automático
5. **Integração**: Conexão com o sistema de consultas

O cadastro deve ser a porta de entrada perfeita para uma experiência incrível com o ShapeMateAI! 🚀