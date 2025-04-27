// Variáveis globais
let sessionId = null;
let totalInteractions = 0;
let totalInputTokens = 0;
let totalOutputTokens = 0;
let totalCost = 0;
let userToken = null;
let userId = null;
let currentMode = 'nutricionista'; // Modo fixo: nutricionista

// Elementos da interface
const chatArea = document.getElementById('chatArea');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newSessionBtn = document.getElementById('newSessionBtn');
const endSessionBtn = document.getElementById('endSessionBtn');
const typingIndicator = document.getElementById('typingIndicator');

// Elementos de informação de custo
const inputTokensEl = document.getElementById('inputTokens');
const outputTokensEl = document.getElementById('outputTokens');
const lastCostEl = document.getElementById('lastCost');
const totalInteractionsEl = document.getElementById('totalInteractions');
const totalTokensEl = document.getElementById('totalTokens');
const totalCostEl = document.getElementById('totalCost');

// Elementos do modal de resumo
const sessionDurationEl = document.getElementById('sessionDuration');
const sessionInteractionsEl = document.getElementById('sessionInteractions');
const sessionInputTokensEl = document.getElementById('sessionInputTokens');
const sessionOutputTokensEl = document.getElementById('sessionOutputTokens');
const sessionTotalCostEl = document.getElementById('sessionTotalCost');

// Instância do modal para resumo da sessão
const sessionSummaryModal = new bootstrap.Modal(document.getElementById('sessionSummaryModal'));

// Verificar autenticação antes de inicializar
function checkAuth() {
    userToken = localStorage.getItem('token');
    userId = localStorage.getItem('user_id');

    if (!userToken) {
        // Redirecionar para a página de login se não estiver autenticado
        window.location.href = 'login.html';
        return false;
    }

    // Verificar validade do token
    return fetch('/api/check-session', {
        headers: {
            'Authorization': userToken
        }
    })
    .then(response => {
        if (!response.ok) {
            // Token inválido, redirecionar para login
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
            window.location.href = 'login.html';
            return false;
        }
        return true;
    })
    .catch(error => {
        console.error('Erro ao verificar sessão:', error);
        return false;
    });
}

// Função para fazer logout
function logout() {
    if (userToken) {
        fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Authorization': userToken
            }
        })
        .then(() => {
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
            window.location.href = 'login.html';
        })
        .catch(error => {
            console.error('Erro ao fazer logout:', error);
        });
    } else {
        window.location.href = 'login.html';
    }
}

// Inicializar a aplicação
async function init() {
    // Verificar autenticação primeiro
    const isAuthenticated = await checkAuth();
    
    if (!isAuthenticated) {
        return; // Não continuar se não estiver autenticado
    }

    // Criar uma nova sessão ao iniciar
    await createSession();
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    
    newSessionBtn.addEventListener('click', createSession);
    endSessionBtn.addEventListener('click', endSession);
    
    // Adicionar botão de logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

// Criar uma nova sessão
async function createSession() {
    try {
        const response = await fetch('/api/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': userToken
            }
        });
        
        const data = await response.json();
        sessionId = data.session_id;
        
        // Resetar as estatísticas
        totalInteractions = 0;
        totalInputTokens = 0;
        totalOutputTokens = 0;
        totalCost = 0;
        
        // Limpar o chat
        chatArea.innerHTML = '';
        
        // Adicionar mensagem inicial com o nome Nutrion
        addMessage('Olá! Sou o Nutrion, seu assistente nutricional inteligente do ShapeMateAI. Como posso ajudar você hoje com questões relacionadas à alimentação e nutrição?', 'assistant');
        
        // Atualizar interface
        updateCostInfo();
        
    } catch (error) {
        console.error('Erro ao criar sessão:', error);
        alert('Erro ao criar sessão. Verifique o console para mais detalhes.');
    }
}

// Enviar mensagem para o servidor
async function sendMessage() {
    const message = messageInput.value.trim();
    
    // Verificar se a mensagem não está vazia
    if (message === '') return;
    
    // Limpar a caixa de entrada
    messageInput.value = '';
    
    // Mostrar a mensagem do usuário no chat
    addMessage(message, 'user');
    
    // Adicionar mensagem de carregamento temporária
    const loadingMessageId = addLoadingMessage();
    
    // Mostrar indicador de digitação
    toggleTypingIndicator(true);
    
    try {
        // Enviar a mensagem para o servidor
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': userToken
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                user_id: userId
            })
        });
        
        const data = await response.json();
        
        // Remover mensagem de carregamento
        removeLoadingMessage(loadingMessageId);
        
        // Esconder indicador de digitação
        toggleTypingIndicator(false);
        
        // Mostrar a resposta do assistente (Nutrion)
        addMessage(data.response, 'assistant');
        
        // Atualizar informações de custo
        updateCostInfoWithResponse(data.cost);
        
    } catch (error) {
        // Remover mensagem de carregamento
        removeLoadingMessage(loadingMessageId);
        
        // Esconder indicador de digitação
        toggleTypingIndicator(false);
        
        console.error('Erro ao enviar mensagem:', error);
        addMessage('Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.', 'assistant');
    }
}

// Adicionar uma mensagem de carregamento temporária
function addLoadingMessage() {
    const messageId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = messageId;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Criar a animação de carregamento
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-animation';
    loadingDiv.innerHTML = `
        <div class="loading-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(contentDiv);
    
    chatArea.appendChild(messageDiv);
    
    // Rolar para a última mensagem
    chatArea.scrollTop = chatArea.scrollHeight;
    
    return messageId;
}

// Remover mensagem de carregamento
function removeLoadingMessage(messageId) {
    const loadingMessage = document.getElementById(messageId);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Encerrar a sessão atual
async function endSession() {
    if (!sessionId) return;
    
    try {
        const response = await fetch(`/api/session/${sessionId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': userToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar modal com resumo da sessão
            displaySessionSummary(data.summary);
            sessionId = null;
            
            // Criar uma nova sessão automaticamente
            await createSession();
        }
    } catch (error) {
        console.error('Erro ao encerrar sessão:', error);
        alert('Erro ao encerrar sessão. Verifique o console para mais detalhes.');
    }
}

// Adicionar mensagem ao chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Processar markdown no texto (se for mensagem do assistente)
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
    
    chatArea.appendChild(messageDiv);
    
    // Rolar para a última mensagem
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Mostrar/ocultar indicador de digitação
function toggleTypingIndicator(show) {
    if (show) {
        typingIndicator.classList.remove('d-none');
    } else {
        typingIndicator.classList.add('d-none');
    }
}

// Atualizar informações de custo com a resposta recebida
function updateCostInfoWithResponse(cost) {
    // Atualizar contadores totais
    totalInteractions++;
    totalInputTokens += cost.input_tokens || 0;
    totalOutputTokens += cost.output_tokens || 0;
    totalCost += cost.total_cost_usd || 0;
    
    // Atualizar elementos da última interação
    inputTokensEl.textContent = cost.input_tokens || 0;
    outputTokensEl.textContent = cost.output_tokens || 0;
    lastCostEl.textContent = `$${(cost.total_cost_usd || 0).toFixed(6)}`;
    
    // Atualizar elementos da sessão atual
    updateCostInfo();
}

// Atualizar as informações de custo na interface
function updateCostInfo() {
    totalInteractionsEl.textContent = totalInteractions;
    totalTokensEl.textContent = totalInputTokens + totalOutputTokens;
    totalCostEl.textContent = `$${totalCost.toFixed(6)}`;
}

// Exibir o resumo da sessão no modal
function displaySessionSummary(summary) {
    sessionDurationEl.textContent = `${summary.session_duration_seconds.toFixed(1)} segundos`;
    sessionInteractionsEl.textContent = summary.total_requests;
    sessionInputTokensEl.textContent = summary.total_input_tokens;
    sessionOutputTokensEl.textContent = summary.total_output_tokens;
    sessionTotalCostEl.textContent = `$${summary.total_cost_usd.toFixed(6)}`;
    
    // Mostrar o modal
    sessionSummaryModal.show();
}

// Inicializar ao carregar a página
document.addEventListener('DOMContentLoaded', init);