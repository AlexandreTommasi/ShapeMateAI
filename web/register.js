// register.js - Script para gerenciar o registro e coleta de dados do perfil

document.addEventListener('DOMContentLoaded', function() {
    // Referências aos elementos do formulário
    const allSteps = document.querySelectorAll('.step-form');
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const registerButton = document.getElementById('register-btn');
    const successModal = document.getElementById('success-modal');
    
    // Radio e checkbox condicionais
    const activityYes = document.getElementById('activity-yes');
    const activityNo = document.getElementById('activity-no');
    const activityDetails = document.getElementById('activity-details');
    
    // Opções "Outro" que revelam campos de texto
    const diseaseOther = document.getElementById('disease-other');
    const diseaseOtherText = document.getElementById('disease-other-text');
    const allergyOther = document.getElementById('allergy-other');
    const allergyOtherText = document.getElementById('allergy-other-text');
    const familyOther = document.getElementById('family-other'); 
    const familyOtherText = document.getElementById('family-other-text');
    
    // Opções mutuamente exclusivas
    const diseaseNone = document.getElementById('disease-none');
    const allergyNone = document.getElementById('allergy-none');
    const familyNone = document.getElementById('family-none');
    
    // Controles para opções mutuamente exclusivas
    setupMutuallyExclusiveOptions('diseases', diseaseNone);
    setupMutuallyExclusiveOptions('allergies', allergyNone);
    setupMutuallyExclusiveOptions('family-diseases', familyNone);
    
    // Configure opções "Outros" para mostrar campos adicionais
    setupOtherOption(diseaseOther, diseaseOtherText);
    setupOtherOption(allergyOther, allergyOtherText);
    setupOtherOption(familyOther, familyOtherText);
    
    // Mostrar/esconder detalhes de atividade física
    if (activityYes && activityNo && activityDetails) {
        activityYes.addEventListener('change', function() {
            activityDetails.style.display = this.checked ? 'block' : 'none';
        });
        
        activityNo.addEventListener('change', function() {
            activityDetails.style.display = this.checked ? 'none' : 'block';
        });
    }
    
    // Navegação entre etapas
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentStep = parseInt(this.getAttribute('data-next')) - 1;
            const nextStep = parseInt(this.getAttribute('data-next'));
            
            // Validar o formulário atual
            if (validateStep(currentStep)) {
                // Esconder etapa atual e mostrar próxima
                document.getElementById(`form-step${currentStep}`).classList.remove('active');
                document.getElementById(`form-step${nextStep}`).classList.add('active');
                
                // Atualizar indicadores de progresso
                progressSteps[currentStep-1].classList.add('completed');
                progressSteps[nextStep-1].classList.add('active');
            }
        });
    });
    
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentStep = parseInt(this.getAttribute('data-prev')) + 1;
            const prevStep = parseInt(this.getAttribute('data-prev'));
            
            // Esconder etapa atual e mostrar anterior
            document.getElementById(`form-step${currentStep}`).classList.remove('active');
            document.getElementById(`form-step${prevStep}`).classList.add('active');
            
            // Atualizar indicadores de progresso
            progressSteps[currentStep-1].classList.remove('active');
            progressSteps[prevStep-1].classList.add('active');
        });
    });
    
    // Botão de registro
    if (registerButton) {
        registerButton.addEventListener('click', function() {
            // Validar a última etapa
            if (validateStep(6)) {
                registerUser();
            }
        });
    }
    
    // Função para validar cada etapa
    function validateStep(stepNumber) {
        const currentForm = document.getElementById(`form-step${stepNumber}`);
        const requiredInputs = currentForm.querySelectorAll('[required]');
        let isValid = true;
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
                
                // Remover classe de erro quando o campo for preenchido
                input.addEventListener('input', function() {
                    if (this.value.trim()) {
                        this.classList.remove('error');
                    }
                }, { once: true });
            } else {
                input.classList.remove('error');
            }
        });
        
        // Validações específicas por etapa
        if (stepNumber === 1) {
            // Validar email, senha e confirmação de senha
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm-password');
            
            // Validar formato de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                isValid = false;
                email.classList.add('error');
                showError(email, 'Por favor, digite um email válido');
            }
            
            // Validar complexidade da senha
            if (password.value.length < 8) {
                isValid = false;
                password.classList.add('error');
                showError(password, 'A senha deve ter pelo menos 8 caracteres');
            }
            
            // Validar confirmação de senha
            if (password.value !== confirmPassword.value) {
                isValid = false;
                confirmPassword.classList.add('error');
                showError(confirmPassword, 'As senhas não conferem');
            }
        }
        
        return isValid;
    }
    
    // Função para mostrar mensagem de erro
    function showError(input, message) {
        // Remove mensagens de erro anteriores
        const parent = input.parentElement;
        const errorMessage = parent.querySelector('.error-message');
        if (errorMessage) {
            parent.removeChild(errorMessage);
        }
        
        // Adiciona nova mensagem de erro
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        parent.appendChild(error);
    }
    
    // Configura campos mutuamente exclusivos
    function setupMutuallyExclusiveOptions(name, noneOption) {
        const options = document.querySelectorAll(`input[name="${name}"]`);
        
        noneOption.addEventListener('change', function() {
            if (this.checked) {
                // Se "nenhuma" for selecionado, desmarcar as outras opções
                options.forEach(option => {
                    if (option !== this) {
                        option.checked = false;
                    }
                });
            }
        });
        
        // Para as outras opções, desmarcar "nenhuma" se alguma for selecionada
        options.forEach(option => {
            if (option !== noneOption) {
                option.addEventListener('change', function() {
                    if (this.checked) {
                        noneOption.checked = false;
                    }
                });
            }
        });
    }
    
    // Configura opções "Outros" para mostrar campos de texto adicionais
    function setupOtherOption(otherOption, textField) {
        otherOption.addEventListener('change', function() {
            textField.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Função para registrar o usuário
    function registerUser() {
        // Coletar todos os dados do formulário
        const userData = {
            // Informações da conta
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            
            // Perfil para o modelo do agente
            profile: {
                personal_info: {
                    name: document.getElementById('name').value,
                    age: parseInt(document.getElementById('age').value),
                    gender: document.getElementById('gender').value,
                    height: parseInt(document.getElementById('height').value),
                    weight: parseFloat(document.getElementById('weight').value),
                    email: document.getElementById('email').value,
                },
                health_info: {
                    activity_level: getActivityLevel(),
                    health_conditions: getSelectedValues('diseases'),
                    allergies: getSelectedValues('allergies'),
                    intolerances: [], // Estamos coletando junto com alergias
                    medications: document.getElementById('medications').value,
                    surgeries: document.getElementById('surgeries').value
                },
                diet_preferences: {
                    dietary_restrictions: getDietaryRestrictions(),
                    preferred_foods: getPreferredFoods(),
                    disliked_foods: getDislikedFoods(),
                    meal_frequency: parseInt(document.getElementById('meal-frequency').value),
                    typical_diet: document.getElementById('daily-diet').value,
                    meal_source: getRadioValue('meal-source'),
                    water_consumption: document.getElementById('water-consumption').value
                },
                lifestyle: {
                    daily_routine: document.getElementById('daily-routine').value,
                    physical_activity: getRadioValue('physical-activity') === 'sim',
                    activity_details: getActivityDetails(),
                    stress_level: document.getElementById('stress-level').value,
                    sleep_quality: document.getElementById('sleep-quality').value,
                    family_history: getSelectedValues('family-diseases'),
                    food_relationship: document.getElementById('food-relationship').value,
                    cooking_willingness: getRadioValue('cooking-willingness'),
                    additional_info: document.getElementById('additional-info').value
                },
                goals: {
                    primary_goal: document.getElementById('goal').value,
                    // Calculamos o peso alvo com base no IMC ideal e altura
                    target_weight: calculateTargetWeight(
                        parseInt(document.getElementById('height').value),
                        document.getElementById('goal').value
                    ),
                    // Calculamos a meta calórica com base nos dados fornecidos
                    calorie_target: calculateCalorieTarget(
                        parseInt(document.getElementById('age').value),
                        document.getElementById('gender').value,
                        parseInt(document.getElementById('height').value),
                        parseFloat(document.getElementById('weight').value),
                        getActivityLevel(),
                        document.getElementById('goal').value
                    )
                }
            }
        };
        
        // Enviar dados para a API
        fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao registrar usuário');
            }
            return response.json();
        })
        .then(data => {
            console.log('Registro bem-sucedido:', data);
            
            // Mostrar modal de sucesso
            successModal.style.display = 'block';
            
            // Armazenar ID do usuário no localStorage
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_email', userData.email);
            
            // Redirecionar para o dashboard após 2 segundos
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 2000);
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao registrar. Por favor, tente novamente.');
        });
    }
    
    // Funções auxiliares para coletar dados do formulário
    function getSelectedValues(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
        const values = Array.from(checkboxes).map(cb => cb.value);
        
        // Verificar se há opção "outro" selecionada
        const otherCheckbox = document.getElementById(`${name.split('-')[0]}-other`);
        const otherTextField = document.getElementById(`${name.split('-')[0]}-other-text`);
        
        if (otherCheckbox && otherCheckbox.checked && otherTextField) {
            const otherInput = otherTextField.querySelector('input');
            if (otherInput && otherInput.value) {
                values.push(otherInput.value);
            }
        }
        
        return values.filter(value => value !== 'outro' && value !== 'nenhuma');
    }
    
    function getRadioValue(name) {
        const radio = document.querySelector(`input[name="${name}"]:checked`);
        return radio ? radio.value : '';
    }
    
    function getActivityLevel() {
        if (getRadioValue('physical-activity') === 'não') {
            return 'sedentário';
        }
        
        const frequency = document.getElementById('activity-frequency').value;
        const intensity = document.getElementById('activity-intensity').value;
        
        if (intensity === 'intensa' || intensity === 'muito_intensa') {
            if (frequency === '5-6' || frequency === 'daily') {
                return 'muito ativo';
            }
            return 'intenso';
        } else if (intensity === 'moderada') {
            if (frequency === '5-6' || frequency === 'daily') {
                return 'intenso';
            }
            return 'moderado';
        } else {
            if (frequency === '1-2') {
                return 'leve';
            }
            return 'moderado';
        }
    }
    
    function getActivityDetails() {
        if (getRadioValue('physical-activity') === 'não') {
            return null;
        }
        
        return {
            frequency: document.getElementById('activity-frequency').value,
            intensity: document.getElementById('activity-intensity').value,
            type: document.getElementById('activity-type').value
        };
    }
    
    function getDietaryRestrictions() {
        // Podemos inferir restrições alimentares a partir das alergias e intolerâncias
        const allergies = getSelectedValues('allergies');
        const restrictions = [];
        
        if (allergies.includes('lactose')) {
            restrictions.push('sem lactose');
        }
        if (allergies.includes('gluten')) {
            restrictions.push('sem glúten');
        }
        
        // Adicionar mais inferências conforme necessário
        
        return restrictions;
    }
    
    function getDislikedFoods() {
        const dislikedText = document.getElementById('disliked-foods').value;
        if (!dislikedText.trim()) return [];
        
        // Dividir o texto por vírgulas ou quebras de linha
        return dislikedText.split(/[,\n]/).map(item => item.trim()).filter(item => item);
    }
    
    function getPreferredFoods() {
        // Poderíamos ter um campo específico para alimentos preferidos
        // Como não temos, podemos deixar vazio por enquanto
        return [];
    }
    
    function calculateTargetWeight(height, goal) {
        // Cálculo simplificado baseado no IMC ideal
        // IMC ideal médio = 22
        const heightMeters = height / 100;
        let targetIMC = 22; // IMC padrão para saúde geral
        
        // Ajustar IMC com base no objetivo
        if (goal === 'emagrecimento') {
            targetIMC = 21;
        } else if (goal === 'hipertrofia') {
            targetIMC = 24;
        }
        
        // Peso = IMC * altura²
        return Math.round(targetIMC * heightMeters * heightMeters);
    }
    
    function calculateCalorieTarget(age, gender, height, weight, activityLevel, goal) {
        // Implementar fórmula de Harris-Benedict para metabolismo basal
        let bmr = 0;
        
        if (gender === 'masculino') {
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
        } else {
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
        }
        
        // Fator de atividade
        let activityFactor = 1.2; // Sedentário
        if (activityLevel === 'leve') {
            activityFactor = 1.375;
        } else if (activityLevel === 'moderado') {
            activityFactor = 1.55;
        } else if (activityLevel === 'intenso') {
            activityFactor = 1.725;
        } else if (activityLevel === 'muito ativo') {
            activityFactor = 1.9;
        }
        
        // Calorias de manutenção
        let maintenanceCalories = bmr * activityFactor;
        
        // Ajustar com base no objetivo
        if (goal === 'emagrecimento') {
            return Math.round(maintenanceCalories * 0.85); // Déficit de 15%
        } else if (goal === 'hipertrofia') {
            return Math.round(maintenanceCalories * 1.15); // Superávit de 15%
        }
        
        return Math.round(maintenanceCalories);
    }
});