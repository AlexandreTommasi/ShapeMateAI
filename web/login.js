// login.js - Funcionalidade da página de login
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o usuário já está autenticado
    fetch('/api/check-session', {
        headers: {
            'Authorization': localStorage.getItem('token')
        }
    })
    .then(response => {
        if (response.ok) {
            // Usuário já está logado, redirecionar para a interface principal
            window.location.href = 'index.html';
        }
    })
    .catch(error => {
        console.error('Erro ao verificar autenticação:', error);
    });

    // Referências aos elementos DOM
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const loginError = document.getElementById('loginError');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    
    // Toggle para mostrar/ocultar senha
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Alterna o ícone
        const eyeIcon = this.querySelector('i');
        eyeIcon.classList.toggle('fa-eye');
        eyeIcon.classList.toggle('fa-eye-slash');
    });
    
    // Manipulador de envio do formulário de login
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Obter valores dos campos
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        
        // Desabilitar o botão de login e mostrar indicador de carregamento
        const submitButton = loginForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Entrando...';
        
        // Ocultar mensagens de erro anteriores
        loginError.classList.add('d-none');
        
        // Enviar dados para o servidor usando a rota correta (/api/login)
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar o botão
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
            
            if (data.token) {
                // Salvar token no localStorage
                localStorage.setItem('token', data.token);
                localStorage.setItem('user_id', data.user_id);
                
                // Salvar preferência de "lembrar de mim" se marcado
                const rememberMe = document.getElementById('rememberMe').checked;
                if (rememberMe) {
                    const userData = { email: email };
                    localStorage.setItem('rememberedUser', JSON.stringify(userData));
                } else {
                    localStorage.removeItem('rememberedUser');
                }
                
                // Login bem-sucedido - redirecionamos para a interface principal
                window.location.href = 'index.html';
            } else {
                // Login falhou - mostrar mensagem de erro
                loginError.classList.remove('d-none');
                loginError.textContent = data.message || 'Credenciais inválidas. Por favor, tente novamente.';
            }
        })
        .catch(error => {
            console.error('Erro ao fazer login:', error);
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
            
            loginError.classList.remove('d-none');
            loginError.textContent = 'Erro ao conectar ao servidor. Por favor, tente novamente mais tarde.';
        });
    });
    
    // Manipulador de envio do formulário de recuperação de senha
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Obter o email para recuperação
            const recoveryEmail = document.getElementById('recoveryEmail').value.trim();
            
            // Simular envio (para fins de demonstração)
            alert(`Um link de recuperação foi enviado para ${recoveryEmail}. Por favor, verifique seu email.`);
            
            // Fechar o modal
            const forgotPasswordModal = bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal'));
            forgotPasswordModal.hide();
        });
    }
    
    // Verificar se há um token de "lembrar de mim" armazenado
    const rememberedUser = localStorage.getItem('rememberedUser');
    if (rememberedUser) {
        try {
            const userData = JSON.parse(rememberedUser);
            emailInput.value = userData.email || '';
            document.getElementById('rememberMe').checked = true;
        } catch (error) {
            console.error('Erro ao recuperar dados de usuário lembrado:', error);
            localStorage.removeItem('rememberedUser');
        }
    }
});