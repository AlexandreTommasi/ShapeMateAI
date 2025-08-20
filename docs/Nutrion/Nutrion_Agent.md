## Nutrion — Agente Nutricionista

### Propósito
O Nutrion conduz uma consulta estruturada, coleta as informações essenciais do usuário e, ao final, gera uma dieta personalizada. A orquestração é feita por LLM e a obtenção de dados nutricionais é automatizada via API USDA.

---

## Visão Geral do Fluxo

- **consultation**: perguntas sequenciais definidas em YAML; ao concluir, a UI exibe o botão “Gerar dieta”.
- **diet_creation**: cálculos nutricionais (LLM) → seleção de alimentos (LLM) → busca na USDA (automática) → montagem da dieta (LLM) → PDF e salvamento.

---

## Arquitetura e Arquivos

- `core/agents/nutritionist_agent.py`
  - `process_message` decide a task ativa (`consultation` | `diet_creation`).
  - `_handle_consultation` conduz as perguntas/respostas e sinaliza conclusão.
  - `_handle_diet_creation` orquestra cálculos, USDA, estrutura de dieta, PDF e persistência.
- Serviços
  - `utils.nutrition_api.NutritionAPI` (USDA)
  - `utils.nutrition_cache.FoodCache` (cache de alimentos)
  - `utils.diet_manager.diet_storage.DietManager` (persistência)
  - `utils.pdf_generator.create_diet_pdf` (PDF)
- Configurações (YAML)
  - `config/agents/nutritionist.yaml`
  - `config/tasks/nutritionist/consultation.yaml`
  - `config/tasks/nutritionist/diet_creation.yaml`

---

## Contrato de Estado (Backend ↔ UI)

- `state.task_type`: `"consultation" | "diet_creation"`
- `state.messages`: histórico do chat (`HumanMessage`, `AIMessage`)
- `state.user_profile`: inclui `user_id`
- `state.consultation_state`:
  - `consultation_id`, `created_at`
  - `current_question`, `total_questions`
  - `answers` (mapa `key -> resposta`)
  - `conversation_history`
  - `consultation_completed` (bool)
  - `current_phase` (`greeting | in_progress | summary`)
  - `last_response`
- Sinalização para UI:
  - `show_option_buttons` (exibir “Gerar dieta” no fim da consulta)
  - `is_decision_point`
- Após dieta:
  - `generated_diet` (JSON)
  - `diet_generated` (bool)
  - `tools_used`, `confidence_score`

Exemplo ao finalizar consulta:
```json
{
  "consultation_state": {
    "consultation_completed": true,
    "current_phase": "summary"
  },
  "show_option_buttons": true,
  "is_decision_point": true
}
```

---

## Configuração por YAML

### Agente (`config/agents/nutritionist.yaml`)
- Define `system_prompt`, persona, parâmetros do LLM e guardrails.

### Task: consultation (`config/tasks/nutritionist/consultation.yaml`)
Sugestão de estrutura:
```yaml
task: consultation
total_questions: 18
questions:
  - id: 1
    key: objetivo
    text: "Qual é o seu objetivo principal? (ex.: emagrecimento, ganho de massa, manutenção)"
    type: single_select
    options: ["emagrecimento", "ganho_massa", "manutencao"]
    required: true
  - id: 2
    key: rotina_refeicoes
    text: "Quantas refeições você costuma fazer por dia?"
    type: number
    min: 1
    max: 10
    required: true
  # ...
prompts:
  consultation_intro: |
    Você é um nutricionista profissional, motivador e acessível.
  consultation_summary_instructions: |
    Gere um resumo claro dos dados coletados e pergunte se deseja gerar a dieta.
```

Regras:
- `questions` define a ordem; `key` mapeia a resposta em `answers`.
- `type` e validações guiam UI/validação.
- `total_questions` deve refletir o total em `questions`.

### Task: diet_creation (`config/tasks/nutritionist/diet_creation.yaml`)
Sugestão de estrutura:
```yaml
task: diet_creation
prompts:
  creation_intro: |
    Gere uma dieta realista, prática e dentro do orçamento.
  nutritional_calculations_handler: |
    Calcule TMB, calorias meta e distribuição de macros. Retorne APENAS JSON.
  food_selection_handler: |
    Gere 25-30 alimentos em inglês, compatíveis com preferências/objetivo. Retorne APENAS lista JSON.
  json_structure: |
    Retorne APENAS JSON com:
    {
      "patient_info": {"name": "...", "age": 30, "sex": "F"},
      "targets": {"tmb": 1600, "calories_goal": 2000, "macros": {"protein_g": 140, "carbs_g": 200, "fat_g": 67}},
      "days": [
        {"day": 1, "meals": [ {"name": "Café da manhã", "items": [{"food": "Oats", "quantity_g": 40, "calories": 150, "protein_g": 5, "carbs_g": 27, "fat_g": 3}] , "totals": {"calories": 350, "protein_g": 20, "carbs_g": 45, "fat_g": 10}} ],
         "totals": {"calories": 2000, "protein_g": 140, "carbs_g": 200, "fat_g": 67}}
      ],
      "shopping_list": [{"food": "Chicken breast", "quantity_g": 1400}],
      "tips": ["Beba água", "Sono de qualidade"],
      "metadata": {"source": "nutritionist_ai", "version": "1.0.0"}
    }
options:
  strict_usda: true
  max_usda_retries: 0
```

---

## Comportamento das Tasks

### Consultation
- Inicializa `consultation_state` com `current_question = 1`.
- A cada resposta: registra em `answers[key]`, avança pergunta e envia a próxima.
- Ao final: marca `consultation_completed = true`, gera resumo (LLM) e habilita “Gerar dieta”.

### Diet Creation (subetapas)
1. Cálculos nutricionais (LLM):
```json
{"tmb": 1680, "calories_goal": 2100, "macros": {"protein_g": 150, "carbs_g": 200, "fat_g": 70}}
```
2. Seleção de alimentos (LLM): lista JSON de 25–30 itens em inglês.
3. Dados nutricionais (USDA): `NutritionAPI.search_food` por item; sem fallback.
4. Estrutura da dieta (LLM): JSON válido conforme `json_structure`.
5. PDF e persistência: `create_diet_pdf` e `DietManager.save_diet`.

---

## Integrações e Operacionais

- **USDA**: dados por 100 g; normalizar nomes em inglês; logar falhas por item.
- **Cache**: `FoodCache` reduz latência/custo e estabiliza respostas.
- **Logs**: início/fim da consulta; itens USDA consultados; validação do JSON; custo LLM.

---

## Erros e Decisões

- Item não encontrado na USDA: falhar explicitamente; ajustar seleção ou API.
- JSON inválido do LLM: extrair bloco, revalidar; se persistir, retornar erro claro para retry.
- Dados críticos ausentes: solicitar pergunta focada adicional antes de gerar dieta.

---

## Segurança e Privacidade

- Não registrar dados sensíveis em logs.
- Armazenar apenas o necessário para a dieta e acompanhamento.

---

## Roadmap Enxuto

1) Ler perguntas do `consultation.yaml` e conduzir fluxo completo na UI.
2) Implementar subetapas da `diet_creation` (LLM + USDA + PDF + DB) com logs e cache.
3) Expor progresso granular para a UI durante a geração da dieta.
4) Testes de ponta a ponta: 18 perguntas → dieta válida → PDF → persistência.


