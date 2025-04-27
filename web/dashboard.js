// dashboard.js - Funcionalidades da página principal
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o usuário está autenticado
    fetch('/api/check_auth')
        .then(response => {
            if (!response.ok) {
                throw new Error('Não autenticado');
            }
            return response.json();
        })
        .then(data => {
            if (data.authenticated) {
                // Atualizar o nome do usuário na interface
                const welcomeText = document.querySelector('.dashboard-header h4');
                if (welcomeText) {
                    welcomeText.innerHTML = `<i class="fas fa-hand-sparkles me-2"></i> Bem-vindo, ${data.user.name}!`;
                }
                
                // Configurar logout
                setupLogout();
                
                // Inicializar componentes do dashboard
                initDashboardComponents();
            } else {
                // Redirecionar para a página de login
                window.location.href = 'login.html';
            }
        })
        .catch(error => {
            console.error('Erro de autenticação:', error);
            window.location.href = 'login.html';
        });
    
    // Configurar funcionalidade de logout
    function setupLogout() {
        const logoutLink = document.querySelector('a[href="login.html"]');
        if (logoutLink) {
            logoutLink.addEventListener('click', function(e) {
                e.preventDefault();
                
                fetch('/api/logout', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = 'login.html';
                    }
                })
                .catch(error => {
                    console.error('Erro ao fazer logout:', error);
                    window.location.href = 'login.html';
                });
            });
        }
    }
    
    // Inicializar componentes do dashboard
    function initDashboardComponents() {
        // ========== CHAT DOS ASSISTENTES ==========
        
        // Referências aos elementos do chat do Nutricionista
        const nutriChatArea = document.getElementById('nutriChatArea');
        const nutriMessageInput = document.getElementById('nutriMessageInput');
        const nutriSendBtn = document.getElementById('nutriSendBtn');
        const nutriTypingIndicator = document.getElementById('nutriTypingIndicator');
        const clearNutriChat = document.getElementById('clearNutriChat');
        
        // Referências aos elementos do chat do Assistente
        const assistChatArea = document.getElementById('assistChatArea');
        const assistMessageInput = document.getElementById('assistMessageInput');
        const assistSendBtn = document.getElementById('assistSendBtn');
        const assistTypingIndicator = document.getElementById('assistTypingIndicator');
        const clearAssistChat = document.getElementById('clearAssistChat');
        
        // Funcionalidade de envio para o Nutricionista
        if (nutriSendBtn) {
            nutriSendBtn.addEventListener('click', function() {
                sendMessage(nutriMessageInput, nutriChatArea, nutriTypingIndicator, 'nutricionista');
            });
            
            nutriMessageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage(nutriMessageInput, nutriChatArea, nutriTypingIndicator, 'nutricionista');
                }
            });
            
            clearNutriChat.addEventListener('click', function() {
                clearChat(nutriChatArea, 'nutricionista');
            });
        }
        
        // Funcionalidade de envio para o Assistente
        if (assistSendBtn) {
            assistSendBtn.addEventListener('click', function() {
                sendMessage(assistMessageInput, assistChatArea, assistTypingIndicator, 'assistente');
            });
            
            assistMessageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage(assistMessageInput, assistChatArea, assistTypingIndicator, 'assistente');
                }
            });
            
            clearAssistChat.addEventListener('click', function() {
                clearChat(assistChatArea, 'assistente');
            });
        }
        
        // Função para enviar mensagem
        function sendMessage(inputElement, chatAreaElement, typingIndicator, agentType) {
            const message = inputElement.value.trim();
            if (message === '') return;
            
            // Limpar input
            inputElement.value = '';
            
            // Adicionar mensagem do usuário
            addMessage(message, 'user', chatAreaElement);
            
            // Mostrar indicador de digitação
            toggleTypingIndicator(true, typingIndicator);
            
            // Chamar a API para obter resposta do assistente
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message, 
                    agent_type: agentType,
                    session_id: localStorage.getItem('conversation_session_id') || 'default'
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na comunicação com o servidor');
                }
                return response.json();
            })
            .then(data => {
                // Esconder o indicador de digitação
                toggleTypingIndicator(false, typingIndicator);
                
                // Adicionar resposta do assistente
                addMessage(data.response, 'assistant', chatAreaElement);
                
                // Atualizar os contadores de tokens e custo, se existirem
                if (data.cost && document.getElementById('inputTokens')) {
                    document.getElementById('inputTokens').innerText = data.cost.input_tokens;
                    document.getElementById('outputTokens').innerText = data.cost.output_tokens;
                    document.getElementById('lastCost').innerText = `$${data.cost.total_cost_usd.toFixed(6)}`;
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                toggleTypingIndicator(false, typingIndicator);
                
                // Resposta de fallback em caso de erro
                let errorResponse;
                if (agentType === 'nutricionista') {
                    errorResponse = getSimulatedNutritionistResponse(message);
                } else {
                    errorResponse = getSimulatedAssistantResponse(message);
                }
                addMessage(errorResponse, 'assistant', chatAreaElement);
            });
        }
        
        // Função para adicionar mensagem ao chat
        function addMessage(text, sender, chatAreaElement) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Processar markdown na mensagem do assistente
            if (sender === 'assistant') {
                contentDiv.innerHTML = marked.parse(text);
            } else {
                contentDiv.innerText = text;
            }
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.innerText = new Date().toLocaleTimeString();
            
            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(timeDiv);
            
            chatAreaElement.appendChild(messageDiv);
            
            // Rolar para a última mensagem
            chatAreaElement.scrollTop = chatAreaElement.scrollHeight;
        }
        
        // Mostrar ou ocultar indicador de digitação
        function toggleTypingIndicator(show, indicatorElement) {
            if (show) {
                indicatorElement.classList.remove('d-none');
            } else {
                indicatorElement.classList.add('d-none');
            }
        }
        
        // Limpar o chat e adicionar mensagem inicial
        function clearChat(chatAreaElement, agentType) {
            chatAreaElement.innerHTML = '';
            
            let welcomeMessage;
            if (agentType === 'nutricionista') {
                welcomeMessage = `Olá! Sou seu nutricionista virtual. Como posso ajudar você com sua alimentação hoje?

Estou aqui para:
- Criar um plano alimentar personalizado
- Calcular suas necessidades calóricas
- Ajustar sua dieta com base nos seus objetivos
- Responder dúvidas sobre nutrição`;
            } else {
                welcomeMessage = `Olá! Sou seu assistente do dia-a-dia. Como posso ajudar você hoje?

Estou aqui para:
- Sugerir substituições para ingredientes da sua dieta
- Analisar cardápios de restaurantes
- Sugerir receitas com os ingredientes que você tem em casa
- Oferecer dicas para se manter na dieta`;
            }
            
            addMessage(welcomeMessage, 'assistant', chatAreaElement);
        }
        
        // Respostas simuladas do nutricionista (fallback)
        function getSimulatedNutritionistResponse(query) {
            query = query.toLowerCase();
            
            if (query.includes('caloria') || query.includes('calorias')) {
                return "Com base no seu perfil (32 anos, 175cm, 76.2kg, moderadamente ativo), sua necessidade calórica diária é de aproximadamente **2500 kcal** para manutenção do peso.\n\nPara atingir seu objetivo de 73kg, recomendo um déficit moderado de 300-500 calorias, resultando em 2000-2200 kcal por dia.\n\nLembre-se que esta é uma estimativa e podemos ajustar conforme seu progresso.";
            }
            
            if (query.includes('proteína') || query.includes('proteina') || query.includes('proteínas')) {
                return "A quantidade de proteína recomendada para você é de aproximadamente **1.8g por kg de peso corporal**, considerando seu objetivo de preservação de massa muscular durante a perda de peso.\n\nIsso significa cerca de **137g de proteína por dia** (para 76.2kg).\n\nBoas fontes de proteína incluem:\n- Peito de frango (26g/100g)\n- Atum em água (25g/100g)\n- Queijo cottage (11g/100g)\n- Ovos (6g por unidade)\n- Tofu (8g/100g)";
            }
            
            if (query.includes('cardápio') || query.includes('refeição') || query.includes('refeições') || query.includes('plano')) {
                return "Posso criar um plano alimentar personalizado para você. Um exemplo de cardápio para seu objetivo seria:\n\n**Café da manhã** (400 kcal):\n- 2 ovos mexidos\n- 2 fatias de pão integral\n- 1/2 abacate\n\n**Lanche** (200 kcal):\n- 200g de iogurte grego\n- 1 banana\n\n**Almoço** (600 kcal):\n- 120g de peito de frango\n- 4 colheres de arroz integral\n- Brócolis e salada à vontade\n\n**Pré-treino** (200 kcal):\n- 1 maçã\n- 1 colher de pasta de amendoim\n\n**Jantar** (500 kcal):\n- 150g de peixe\n- Legumes grelhados\n- Batata doce (100g)";
            }
            
            // Resposta padrão
            return "Obrigado por compartilhar essa informação. Com base no seu histórico e objetivos, podemos trabalhar juntos para ajustar sua dieta e alcançar seus objetivos de saúde.\n\nVocê tem alguma dúvida específica sobre nutrição ou gostaria que eu preparasse um plano alimentar personalizado?";
        }
        
        // Respostas simuladas do assistente (fallback)
        function getSimulatedAssistantResponse(query) {
            query = query.toLowerCase();
            
            if (query.includes('restaurante') || query.includes('cardápio')) {
                return "Para manter sua dieta ao comer fora, recomendo:\n\n1. **Escolha pratos grelhados, assados ou cozidos** em vez de fritos\n2. **Peça molhos e temperos à parte** para controlar a quantidade\n3. **Comece com uma salada** para ajudar a controlar o apetite\n4. **Divida sobremesas** se quiser um pequeno prazer\n\nDica: Muitos restaurantes têm opções saudáveis marcadas no cardápio com símbolos especiais.";
            }
            
            if (query.includes('substituir') || query.includes('trocar')) {
                return "Claro! Aqui estão algumas substituições saudáveis que você pode fazer:\n\n- **Em vez de óleo**: use azeite de oliva, óleo de coco ou abacate amassado\n- **Em vez de açúcar**: use stévia, eritritol ou frutas maduras\n- **Em vez de pão branco**: escolha pão integral, pão de fermentação natural ou wraps de alface\n- **Em vez de macarrão**: experimente abobrinha em fitas, macarrão de arroz integral ou macarrão de legumes\n\nEssas substituições mantêm o sabor enquanto aumentam o valor nutricional!";
            }
            
            if (query.includes('receita') || query.includes('cozinhar')) {
                return "Com base nos itens que você tem em casa (ovos, leite e banana), sugiro esta receita rápida:\n\n**Panqueca de Banana Fit**\n\n*Ingredientes:*\n- 2 ovos\n- 1 banana madura\n- Canela a gosto\n- 1 colher de chá de óleo de coco\n\n*Modo de Preparo:*\n1. Amasse a banana e misture com os ovos batidos\n2. Adicione uma pitada de canela\n3. Aqueça uma frigideira com um pouco de óleo de coco\n4. Despeje pequenas porções da mistura\n5. Vire quando formar bolhas\n\nPronto! Uma refeição nutritiva com aproximadamente 240kcal e 14g de proteína.";
            }
            
            // Resposta padrão
            return "Obrigado pela sua mensagem! Estou aqui para ajudar com substituições na sua dieta, análise de cardápios ou sugestões de receitas com o que você tem em casa. Como posso ajudar especificamente hoje?";
        }

        // ========== TABS DE NAVEGAÇÃO ==========
        
        // Salva a última tab ativa no localStorage para persistir entre visitas
        const mainTabs = document.getElementById('mainTabs');
        if (mainTabs) {
            const tabLinks = mainTabs.querySelectorAll('.nav-link');
            
            // Recupera a última tab ativa
            const lastActiveTab = localStorage.getItem('lastActiveTab');
            if (lastActiveTab) {
                const tab = document.getElementById(lastActiveTab);
                if (tab) {
                    // Ativa a última tab usada
                    const tabTrigger = new bootstrap.Tab(tab);
                    tabTrigger.show();
                }
            }
            
            // Salva a escolha da tab no localStorage
            tabLinks.forEach(function(tabLink) {
                tabLink.addEventListener('shown.bs.tab', function(event) {
                    localStorage.setItem('lastActiveTab', event.target.id);
                });
            });
        }
    }
});