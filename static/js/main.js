/**
 * Este arquivo contém o código JavaScript principal da aplicação
 * Ele é responsável por gerenciar todas as interações do usuário e funcionalidades dinâmicas
 */

/**
 * Ponto de entrada principal do código JavaScript
 * O evento DOMContentLoaded garante que o código só será executado
 * depois que toda a página HTML estiver carregada
 */
document.addEventListener('DOMContentLoaded', function() {
    /**
     * Gerenciamento da barra lateral em dispositivos móveis
     * Permite mostrar/esconder a barra lateral ao clicar no botão
     */
    const toggleBtn = document.querySelector('#sidebarCollapse');
    const sidebar = document.querySelector('#sidebar');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    /**
     * Gerenciamento de envio de formulários
     * Adiciona um indicador de carregamento ao botão de submit
     * e desabilita o botão para evitar envios duplicados
     */
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            }
        });
    });

    /**
     * Gerenciamento dos sliders de autoavaliação
     * Atualiza o valor exibido ao lado do slider quando o usuário o move
     */
    const sliders = document.querySelectorAll('.assessment-slider');
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const value = this.value;
            const output = this.nextElementSibling;
            if (output) {
                output.textContent = value;
            }
        });
    });

    /**
     * Gerenciamento do modal de atividades
     * Controla a exibição e fechamento do modal de adição de atividades
     */
    const addEventBtn = document.querySelector('#addEventBtn');
    const eventModal = document.querySelector('#eventModal');
    
    if (addEventBtn && eventModal) {
        // Abre o modal ao clicar no botão de adicionar
        addEventBtn.addEventListener('click', function() {
            eventModal.classList.add('show');
        });

        // Fecha o modal ao clicar no botão de fechar
        const closeBtn = eventModal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                eventModal.classList.remove('show');
            });
        }

        // Fecha o modal ao clicar fora dele
        window.addEventListener('click', function(e) {
            if (e.target === eventModal) {
                eventModal.classList.remove('show');
            }
        });
    }

    /**
     * Validação dos campos de entrada de tempo
     * Garante que o horário de término seja posterior ao horário de início
     */
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const startTime = document.querySelector('#start_time');
            const endTime = document.querySelector('#end_time');
            
            if (startTime && endTime) {
                const start = new Date(`1970-01-01T${startTime.value}`);
                const end = new Date(`1970-01-01T${endTime.value}`);
                
                if (end <= start) {
                    alert('End time must be after start time');
                    endTime.value = '';
                }
            }
        });
    });

    /**
     * Gerenciamento das cores das categorias
     * Atualiza as cores e ícones do card de atividade baseado na categoria selecionada
     */
    const categorySelect = document.querySelector('#category');
    const activityCard = document.querySelector('.activity-card');
    
    if (categorySelect && activityCard) {
        // Define as cores e ícones para cada categoria
        const categoryColors = {
            'leisure': { bg: '#FFF3E0', border: '#FF9800', icon: '🎮' },
            'career': { bg: '#E3F2FD', border: '#2196F3', icon: '💼' },
            'health': { bg: '#E8F5E9', border: '#4CAF50', icon: '💪' },
            'relationships': { bg: '#FCE4EC', border: '#E91E63', icon: '❤️' },
            'personal_development': { bg: '#F3E5F5', border: '#9C27B0', icon: '🎯' },
            'finances': { bg: '#E0F2F1', border: '#009688', icon: '💰' },
            'spirituality': { bg: '#EDE7F6', border: '#673AB7', icon: '🧘' },
            'contribution': { bg: '#FBE9E7', border: '#FF5722', icon: '🤝' }
        };

        // Atualiza as cores e ícone quando uma categoria é selecionada
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            const colors = categoryColors[category];
            if (colors) {
                activityCard.style.backgroundColor = colors.bg;
                activityCard.style.borderLeftColor = colors.border;
                const icon = activityCard.querySelector('.card-category i');
                if (icon) {
                    icon.textContent = colors.icon;
                }
            }
        });
    }

    /**
     * Gerenciamento do envio do formulário de autoavaliação
     * Envia os dados para o servidor e mostra notificações de sucesso/erro
     */
    const assessmentForm = document.querySelector('#assessmentForm');
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Coleta os dados do formulário
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            // Envia os dados para o servidor
            fetch('/save_assessment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('success', 'Assessment saved successfully!');
                } else {
                    showNotification('error', 'Error saving assessment');
                }
            })
            .catch(error => {
                showNotification('error', 'Error saving assessment');
                console.error('Error:', error);
            });
        });
    }
});

/**
 * Sistema de notificações
 * Cria e exibe notificações temporárias na tela
 * @param {string} type - Tipo da notificação (success, error, etc)
 * @param {string} message - Mensagem a ser exibida
 */
function showNotification(type, message) {
    // Cria o elemento da notificação
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Adiciona a notificação ao início do container
    const container = document.querySelector('.container-fluid');
    container.insertBefore(notification, container.firstChild);
    
    // Remove a notificação após 5 segundos
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Função para mudar o idioma da aplicação
 * Envia uma requisição ao servidor para alterar o idioma
 * e recarrega a página para aplicar as mudanças
 * @param {string} lang - Código do idioma (pt, en, etc)
 */
function changeLanguage(lang) {
    fetch('/change_language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: lang })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
} 