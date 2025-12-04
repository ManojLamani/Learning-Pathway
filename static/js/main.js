// Main JavaScript File for LMS

// Auto-dismiss messages after 5 seconds with smooth animation
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'all 0.4s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                message.remove();
            }, 400);
        }, 5000);
    });
});

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--danger-color)';
                } else {
                    field.style.borderColor = 'var(--border-color)';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    }
}

// Quiz timer
function startQuizTimer(durationMinutes, displayElement) {
    let totalSeconds = durationMinutes * 60;
    
    const timer = setInterval(function() {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        displayElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (totalSeconds <= 0) {
            clearInterval(timer);
            alert('Time is up! Submitting quiz...');
            document.getElementById('quiz-form').submit();
        }
        
        totalSeconds--;
    }, 1000);
}

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Dynamic search/filter for course lists
function filterCourses() {
    const searchInput = document.getElementById('course-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const courseCards = document.querySelectorAll('.course-card');
            
            courseCards.forEach(function(card) {
                const title = card.querySelector('.course-title').textContent.toLowerCase();
                const description = card.querySelector('.course-description').textContent.toLowerCase();
                
                if (title.includes(filter) || description.includes(filter)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    filterCourses();
});

// Password strength indicator for registration
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password1"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const requirements = document.querySelectorAll('.password-requirements li');
            
            if (requirements.length > 0) {
                // Check length
                if (password.length >= 8) {
                    requirements[0].classList.add('valid');
                } else {
                    requirements[0].classList.remove('valid');
                }
                
                // Check for number or symbol
                if (/[0-9!@#$%^&*]/.test(password)) {
                    requirements[1].classList.add('valid');
                } else {
                    requirements[1].classList.remove('valid');
                }
                
                // Check for lowercase and uppercase
                if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
                    requirements[2].classList.add('valid');
                } else {
                    requirements[2].classList.remove('valid');
                }
            }
        });
    }
});

// Add loading state to buttons on form submit
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner"></span> Loading...';
            }
        });
    });
});

// Card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card, .feature-card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
