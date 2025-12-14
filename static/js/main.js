// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
});

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;
        
        inputs.forEach(function(input) {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#e74c3c';
            } else {
                input.style.borderColor = '#ddd';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('请填写所有必填项');
        }
    });
}

// Auto-uppercase code input
document.addEventListener('DOMContentLoaded', function() {
    const codeInput = document.getElementById('code');
    if (codeInput) {
        codeInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }
});

// Set default datetime for create task form
document.addEventListener('DOMContentLoaded', function() {
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    
    if (startTimeInput && endTimeInput) {
        const now = new Date();
        const later = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2 hours later
        
        const formatDateTime = function(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        };
        
        if (!startTimeInput.value) {
            startTimeInput.value = formatDateTime(now);
        }
        if (!endTimeInput.value) {
            endTimeInput.value = formatDateTime(later);
        }
        
        // Validate end time is after start time
        endTimeInput.addEventListener('change', function() {
            if (startTimeInput.value && endTimeInput.value) {
                if (new Date(endTimeInput.value) <= new Date(startTimeInput.value)) {
                    alert('结束时间必须晚于开始时间');
                    endTimeInput.value = '';
                }
            }
        });
    }
});

// Confirm before exporting records
document.addEventListener('DOMContentLoaded', function() {
    const exportLinks = document.querySelectorAll('a[href*="export_records"]');
    exportLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('确定要导出签到记录吗？')) {
                e.preventDefault();
            }
        });
    });
});

// Table sorting functionality
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort(function(a, b) {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        return aText.localeCompare(bText);
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

// Password confirmation validation
document.addEventListener('DOMContentLoaded', function() {
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordInput = document.getElementById('password');
    
    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            if (passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity('两次输入的密码不一致');
            } else {
                confirmPasswordInput.setCustomValidity('');
            }
        });
    }
});
