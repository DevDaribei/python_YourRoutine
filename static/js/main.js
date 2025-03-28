// Toggle sidebar on mobile
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('#sidebarCollapse');
    const sidebar = document.querySelector('#sidebar');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Handle form submissions
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

    // Handle assessment sliders
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

    // Handle activity modal
    const addEventBtn = document.querySelector('#addEventBtn');
    const eventModal = document.querySelector('#eventModal');
    
    if (addEventBtn && eventModal) {
        addEventBtn.addEventListener('click', function() {
            eventModal.classList.add('show');
        });

        const closeBtn = eventModal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                eventModal.classList.remove('show');
            });
        }

        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === eventModal) {
                eventModal.classList.remove('show');
            }
        });
    }

    // Handle time input validation
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

    // Handle category color updates
    const categorySelect = document.querySelector('#category');
    const activityCard = document.querySelector('.activity-card');
    
    if (categorySelect && activityCard) {
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

    // Handle assessment form submission
    const assessmentForm = document.querySelector('#assessmentForm');
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

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

// Notification system
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Handle language change
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