# ShapeMateAI

## Objetivo Geral
O **ShapeMateAI** é um sistema inteligente com o objetivo de facilitar a criação e o acompanhamento de dietas personalizadas, utilizando inteligência artificial. O projeto conta com dois agentes principais: um **Nutricionista Virtual** e um **Assistente de Dia-a-Dia**, que trabalham juntos para proporcionar uma experiência completa de nutrição.

---

## Agente 1 - **Nutricionista Virtual**

### Objetivo:
Simular uma consulta com um nutricionista, oferecendo uma dieta personalizada de acordo com as necessidades do cliente.

### Fluxo da Consulta:
1. **Coleta de Informações**: 
   O agente começa coletando informações essenciais do cliente, como:
   - Peso, altura, idade, etc.
   - Nível de atividade física (sedentário, moderadamente ativo, ativo).
   
2. **Objetivo do Cliente**: 
   O nutricionista virtual pergunta sobre os objetivos do cliente, como:
   - Perder peso, ganhar massa muscular, manter o peso, entre outros.

3. **Preferências Alimentares**:
   - O agente coleta as preferências alimentares do cliente, incluindo alimentos que ele costuma consumir.
   - Oferece opções e alternativas para adaptar a dieta, além de permitir trocas conforme o gosto pessoal.
   - Pergunta sobre o orçamento disponível para alimentação, garantindo que a dieta esteja dentro da capacidade financeira do cliente.

4. **Geração da Dieta**:
   Com as informações coletadas, o nutricionista virtual gera a dieta personalizada do cliente, incluindo:
   - Os alimentos recomendados.
   - A quantidade de cada alimento (porção).
   - O valor médio de cada item para controle financeiro.
   - O cálculo dos macronutrientes (proteínas, carboidratos, gorduras, etc.).

---

## Agente 2 - **Assistente do Dia-a-Dia**

### Objetivo:
Ajudar o cliente no dia a dia, oferecendo suporte para ajustes rápidos e avaliações constantes, sempre alinhando a alimentação às metas estabelecidas.

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

---

## Projeção de Resultados

### Objetivo:
A IA pode também projetar como o cliente estará após alguns meses de dieta, fornecendo uma visualização realista do seu progresso. Isso ajudará a manter o cliente motivado, ao mostrar o impacto da dieta ao longo do tempo.

---

## Ideias de Realização

### **Objetivo Final**:
Criar um **aplicativo inteligente** que facilite a vida do usuário, utilizando IA para personalizar, adaptar e acompanhar a dieta de forma simples e eficiente.

### **Tecnologias Utilizadas**:
- **Back-End**: Python.
- **Front-End**: Em processo de definição (preciso decidir a tecnologia de front-end).
- **Biblioteca para Orquestração dos Agentes**: LangGraph.
- **Modelo de IA**: DeepSeek.

---

### Observações Finais:
Essa ideia visa tornar o processo de nutrição mais acessível e personalizado, utilizando IA para oferecer soluções práticas e viáveis para o dia a dia dos usuários. A proposta é que o sistema seja fácil de usar, com informações claras, sugestões realistas e suporte contínuo.
