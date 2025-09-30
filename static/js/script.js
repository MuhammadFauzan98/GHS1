// Enhanced JavaScript for better interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            navLinks.classList.toggle('active');
            
            // Animate hamburger icon
            const spans = this.querySelectorAll('span');
            if (this.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    }
    
    // Close mobile menu when clicking on a link
    const navLinksItems = document.querySelectorAll('.nav-links a');
    navLinksItems.forEach(link => {
        link.addEventListener('click', function() {
            if (navLinks.classList.contains('active')) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                
                const spans = hamburger.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    });
    
    // Close flash messages
    const closeButtons = document.querySelectorAll('.close-btn, .close-alert');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                this.parentElement.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message, .alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 300);
        }, 5000);
    });
    
    // Smooth scrolling for anchor links
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
    
    // Form validation enhancement (exclude upload forms)
    const forms = document.querySelectorAll('form:not(.upload-form):not(#loginForm)');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // File input enhancement for non-upload forms
    const fileInputs = document.querySelectorAll('input[type="file"]:not(#photos):not(#pdf)');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'No file chosen';
            console.log('Selected file:', fileName);
        });
    });
    
    // ============================
    // UPLOAD FORM SPECIFIC HANDLING
    // ============================
    
    // Photo Upload Form Handling
    const photoUploadForm = document.getElementById('photoUploadForm');
    if (photoUploadForm) {
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('photos');
        const filePreviews = document.getElementById('filePreviews');
        const submitBtn = photoUploadForm.querySelector('.btn-upload');
        
        // Basic file preview functionality
        if (fileUploadArea && fileInput) {
            fileUploadArea.addEventListener('click', function() {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', function() {
                filePreviews.innerHTML = '';
                
                if (fileInput.files.length) {
                    Array.from(fileInput.files).forEach((file) => {
                        // Basic validation
                        if (!file.type.startsWith('image/')) {
                            alert(`File "${file.name}" is not an image. Please select image files only.`);
                            return;
                        }
                        
                        if (file.size > 16 * 1024 * 1024) {
                            alert(`File "${file.name}" exceeds 16MB limit. Please choose a smaller file.`);
                            return;
                        }
                        
                        // Simple preview
                        const preview = document.createElement('div');
                        preview.className = 'file-preview';
                        preview.innerHTML = `
                            <div class="file-details">
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${formatFileSize(file.size)}</span>
                            </div>
                        `;
                        filePreviews.appendChild(preview);
                    });
                }
            });
        }
        
        // Simple form submission - just show loading
        photoUploadForm.addEventListener('submit', function() {
            if (this.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            }
        });
    }
    
    // PYQP Upload Form Handling
    const pyqpUploadForm = document.getElementById('pyqpUploadForm');
    if (pyqpUploadForm) {
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('pdf');
        const filePreview = document.getElementById('filePreview');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const removeFileBtn = document.getElementById('removeFile');
        const submitBtn = pyqpUploadForm.querySelector('.btn-upload');
        
        // Basic file handling
        if (fileUploadArea && fileInput) {
            fileUploadArea.addEventListener('click', function() {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', function() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    
                    // Basic validation
                    if (file.type !== 'application/pdf') {
                        alert('Please select a PDF file.');
                        fileInput.value = '';
                        return;
                    }
                    
                    if (file.size > 16 * 1024 * 1024) {
                        alert('File size exceeds 16MB limit. Please choose a smaller file.');
                        fileInput.value = '';
                        return;
                    }
                    
                    // Show file info
                    fileName.textContent = file.name;
                    fileSize.textContent = formatFileSize(file.size);
                    
                    fileUploadArea.style.display = 'none';
                    if (filePreview) filePreview.style.display = 'flex';
                }
            });
            
            if (removeFileBtn) {
                removeFileBtn.addEventListener('click', function() {
                    fileInput.value = '';
                    if (filePreview) filePreview.style.display = 'none';
                    fileUploadArea.style.display = 'block';
                });
            }
        }
        
        // Custom subject field
        const subjectSelect = document.getElementById('subject');
        const customSubjectLabel = document.getElementById('customSubjectLabel');
        const customSubjectInput = document.getElementById('custom_subject');
        
        if (subjectSelect && customSubjectLabel && customSubjectInput) {
            subjectSelect.addEventListener('change', function() {
                if (this.value === 'Other') {
                    customSubjectLabel.style.display = 'block';
                    customSubjectInput.style.display = 'block';
                    customSubjectInput.required = true;
                } else {
                    customSubjectLabel.style.display = 'none';
                    customSubjectInput.style.display = 'none';
                    customSubjectInput.required = false;
                }
            });
        }
        
        // Simple form submission
        pyqpUploadForm.addEventListener('submit', function() {
            if (this.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            }
        });
    }
    
    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const submitBtn = loginForm.querySelector('.btn-auth');
        
        loginForm.addEventListener('submit', function() {
            // Only show processing if form is valid
            if (this.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    }
    
    // Add CSS animation for slideOut
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        /* Navigation dropdown for mobile */
        @media (max-width: 768px) {
            .nav-dropdown-menu {
                display: none;
                position: static;
                opacity: 1;
                visibility: visible;
                transform: none;
                box-shadow: none;
                background: transparent;
                padding: 0;
                margin-top: 10px;
            }
            
            .nav-dropdown.active .nav-dropdown-menu {
                display: block;
            }
            
            .nav-dropdown-menu li {
                margin: 5px 0;
            }
            
            .nav-dropdown-menu a {
                padding: 8px 15px;
                border-radius: 5px;
            }
        }
        
        /* Loading spinner */
        .fa-spinner {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // Navbar background on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.backdropFilter = 'blur(10px)';
            } else {
                navbar.style.background = 'var(--white)';
                navbar.style.backdropFilter = 'none';
            }
        }
    });
    
    // Mobile dropdown functionality
    const dropdownToggles = document.querySelectorAll('.nav-dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const dropdown = this.parentElement;
                dropdown.classList.toggle('active');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const dropdowns = document.querySelectorAll('.nav-dropdown');
            dropdowns.forEach(dropdown => {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
        }
    });
    
    // Add loading states to buttons (excluding upload and login forms)
    const submitButtons = document.querySelectorAll('button[type="submit"]:not(.btn-upload):not(.btn-auth)');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable button after 5 seconds (fallback)
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 5000);
            }
        });
    });
});

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function to validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Utility function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.innerHTML = `
        ${message}
        <button class="close-btn">&times;</button>
    `;
    
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    flashContainer.appendChild(notification);
    
    // Add close functionality
    notification.querySelector('.close-btn').addEventListener('click', function() {
        notification.remove();
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// Clear form functions for upload pages
function clearForm() {
    // Determine which form we're clearing
    const photoForm = document.getElementById('photoUploadForm');
    const pyqpForm = document.getElementById('pyqpUploadForm');
    
    if (photoForm) {
        photoForm.reset();
        const filePreviews = document.getElementById('filePreviews');
        if (filePreviews) filePreviews.innerHTML = '';
        const fileInput = document.getElementById('photos');
        if (fileInput) fileInput.value = '';
        
        // Re-enable submit button
        const submitBtn = document.querySelector('.btn-upload');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Photos';
        }
    }
    
    if (pyqpForm) {
        pyqpForm.reset();
        const fileUploadArea = document.getElementById('fileUploadArea');
        const filePreview = document.getElementById('filePreview');
        const customSubjectLabel = document.getElementById('customSubjectLabel');
        const customSubjectInput = document.getElementById('custom_subject');
        
        if (fileUploadArea) fileUploadArea.style.display = 'block';
        if (filePreview) filePreview.style.display = 'none';
        if (customSubjectLabel) customSubjectLabel.style.display = 'none';
        if (customSubjectInput) customSubjectInput.style.display = 'none';
        
        // Re-enable submit button
        const submitBtn = document.querySelector('.btn-upload');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Question Paper';
        }
    }
}

// Drag and drop functionality (optional enhancement)
function initializeDragAndDrop() {
    const fileUploadAreas = document.querySelectorAll('.file-upload-area');
    
    fileUploadAreas.forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                const fileInput = this.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.files = e.dataTransfer.files;
                    
                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            }
        });
    });
}

// Initialize drag and drop when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDragAndDrop);