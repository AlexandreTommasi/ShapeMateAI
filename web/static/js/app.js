// ShapeMateAI JavaScript Application

// Global app configuration
const ShapeMateApp = {
    version: '1.0.0',
    debug: true,
    apiBaseUrl: '/api',
    
    // Initialize the application
    init() {
        this.setupEventListeners();
        this.setupFormValidations();
        this.setupAnimations();
        console.log('ShapeMateAI App initialized');
    },

    // Setup global event listeners
    setupEventListeners() {
        // Global logout function
        window.logout = this.logout.bind(this);
        
        // Setup CSRF protection for all AJAX requests
        this.setupCSRF();
        
        // Setup toast notifications
        this.setupToasts();
    },

    // Setup form validations
    setupFormValidations() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    // Setup animations
    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe all cards for animation
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    },

    // Setup CSRF protection
    setupCSRF() {
        // Add CSRF token to all AJAX requests if needed
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            // Configure default headers for fetch requests
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
                return originalFetch(url, options);
            };
        }
    },

    // Setup toast notifications
    setupToasts() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toastContainer')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
    },

    // Utility functions
    utils: {
        // Show loading state on button
        showButtonLoading(button, text = 'Carregando...') {
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
            
            return () => {
                button.disabled = false;
                button.innerHTML = originalText;
            };
        },

        // Format date
        formatDate(date) {
            return new Date(date).toLocaleDateString('pt-BR');
        },

        // Format time
        formatTime(date) {
            return new Date(date).toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // Calculate BMI
        calculateBMI(weight, height) {
            const bmi = weight / (height * height);
            let classification = '';
            
            if (bmi < 18.5) classification = 'Abaixo do peso';
            else if (bmi < 25) classification = 'Peso normal';
            else if (bmi < 30) classification = 'Sobrepeso';
            else classification = 'Obesidade';
            
            return {
                value: bmi.toFixed(1),
                classification: classification
            };
        },

        // Validate email
        validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },

    // Notification system
    notifications: {
        show(message, type = 'info', duration = 5000) {
            const toastContainer = document.getElementById('toastContainer');
            const toastId = 'toast-' + Date.now();
            
            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;
            
            toastContainer.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: duration
            });
            
            bsToast.show();
            
            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        },

        success(message, duration) {
            this.show(message, 'success', duration);
        },

        error(message, duration) {
            this.show(message, 'danger', duration);
        },

        warning(message, duration) {
            this.show(message, 'warning', duration);
        },

        info(message, duration) {
            this.show(message, 'info', duration);
        }
    },

    // API helper functions
    api: {
        async request(endpoint, options = {}) {
            const url = `${ShapeMateApp.apiBaseUrl}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const mergedOptions = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, mergedOptions);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'Erro na requisição');
                }
                
                return data;
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        },

        async get(endpoint) {
            return this.request(endpoint, { method: 'GET' });
        },

        async post(endpoint, data) {
            return this.request(endpoint, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        async put(endpoint, data) {
            return this.request(endpoint, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        async delete(endpoint) {
            return this.request(endpoint, { method: 'DELETE' });
        }
    },

    // Logout function
    async logout() {
        if (confirm('Deseja realmente sair?')) {
            try {
                await this.api.post('/logout');
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout error:', error);
                // Force logout even if API fails
                window.location.href = '/login';
            }
        }
    },

    // Form helpers
    forms: {
        // Serialize form data to object
        serialize(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            return data;
        },

        // Reset form and remove validation classes
        reset(form) {
            form.reset();
            form.classList.remove('was-validated');
            
            // Remove validation classes from all fields
            const fields = form.querySelectorAll('.form-control, .form-select');
            fields.forEach(field => {
                field.classList.remove('is-valid', 'is-invalid');
            });
        },

        // Add validation feedback to field
        addFeedback(field, message, isValid = false) {
            const feedbackClass = isValid ? 'valid-feedback' : 'invalid-feedback';
            const fieldClass = isValid ? 'is-valid' : 'is-invalid';
            
            // Remove existing feedback
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            // Add new feedback
            const feedback = document.createElement('div');
            feedback.className = feedbackClass;
            feedback.textContent = message;
            
            field.classList.remove('is-valid', 'is-invalid');
            field.classList.add(fieldClass);
            field.parentNode.appendChild(feedback);
        }
    },

    // Local storage helpers
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                console.error('Storage set error:', error);
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.error('Storage remove error:', error);
            }
        },

        clear() {
            try {
                localStorage.clear();
            } catch (error) {
                console.error('Storage clear error:', error);
            }
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    ShapeMateApp.init();
});

// Global error handler
window.addEventListener('error', (event) => {
    if (ShapeMateApp.debug) {
        console.error('Global error:', event.error);
    }
});

// Make ShapeMateApp globally available
window.ShapeMateApp = ShapeMateApp;
