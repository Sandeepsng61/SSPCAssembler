/**
 * Custom Modal Implementation
 * This completely replaces Bootstrap's modal functionality with our own implementation
 * to prevent any flickering issues.
 */

// Store for active modals
const customModalStore = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Convert all existing modals to our custom implementation
    convertExistingModals();
    
    // Set up global click handler for modal triggers
    setupModalTriggers();
});

/**
 * Convert all existing Bootstrap modals to our custom implementation
 */
function convertExistingModals() {
    // Find all modal elements
    const modalElements = document.querySelectorAll('.modal');
    
    modalElements.forEach(modalElement => {
        const modalId = modalElement.id;
        if (!modalId) return;
        
        // Disable Bootstrap modal behavior
        modalElement.classList.add('custom-modal');
        modalElement.classList.remove('fade');
        
        // Store modal reference
        customModalStore[modalId] = {
            element: modalElement,
            isOpen: false,
            content: modalElement.querySelector('.modal-body'),
            isLoading: false
        };
        
        // Add custom close handlers
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            // Remove Bootstrap attributes
            button.removeAttribute('data-bs-dismiss');
            
            // Add our custom close handler
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                hideModal(modalId);
            });
        });
        
        // Add backdrop click handler
        modalElement.addEventListener('click', function(e) {
            // Only close if backdrop is clicked (not modal content)
            if (e.target === modalElement) {
                hideModal(modalId);
            }
        });
        
        // Add keyboard handler for Escape
        modalElement.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideModal(modalId);
            }
        });
    });
}

/**
 * Set up click handlers for modal triggers
 */
function setupModalTriggers() {
    // Remove all Bootstrap modal triggers and replace with our own
    document.querySelectorAll('[data-bs-toggle="modal"], [data-target^="#"], [data-bs-target^="#"]').forEach(trigger => {
        // Skip if already processed
        if (trigger.hasAttribute('data-custom-modal-processed')) return;
        
        // Skip non-view buttons (keep delete/confirmation modals using Bootstrap)
        if (!trigger.classList.contains('btn-view') && !trigger.classList.contains('view-btn')) return;
        
        // Mark as processed
        trigger.setAttribute('data-custom-modal-processed', 'true');
        
        // Get target modal
        const targetId = trigger.getAttribute('data-bs-target') || 
                         trigger.getAttribute('data-target');
        
        if (!targetId) return;
        
        // Remove Bootstrap attributes
        trigger.removeAttribute('data-bs-toggle');
        trigger.removeAttribute('data-toggle');
        
        // Add custom click handler
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const url = trigger.getAttribute('data-url');
            const modalId = targetId.replace('#', '');
            
            if (url) {
                showModalWithContent(modalId, url);
            } else {
                showModal(modalId);
            }
        });
    });
}

/**
 * Show a modal
 * @param {string} modalId - ID of the modal to show
 */
function showModal(modalId) {
    const modal = customModalStore[modalId];
    if (!modal) return;
    
    // Prevent body scrolling
    document.body.classList.add('overflow-hidden');
    
    // Show modal with proper styling
    modal.element.style.display = 'block';
    modal.element.classList.add('show');
    modal.element.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    
    // Show backdrop if not already present
    if (!document.querySelector('.modal-backdrop')) {
        const backdrop = document.createElement('div');
        backdrop.classList.add('custom-modal-backdrop');
        document.body.appendChild(backdrop);
    }
    
    // Mark as open
    modal.isOpen = true;
    
    // Focus the modal for keyboard navigation
    modal.element.setAttribute('tabindex', '-1');
    modal.element.focus();
    
    // Trigger custom open event
    const openEvent = new CustomEvent('modal:opened', { detail: { modalId } });
    document.dispatchEvent(openEvent);
}

/**
 * Hide a modal
 * @param {string} modalId - ID of the modal to hide
 */
function hideModal(modalId) {
    const modal = customModalStore[modalId];
    if (!modal || !modal.isOpen) return;
    
    // Hide modal
    modal.element.style.display = 'none';
    modal.element.classList.remove('show');
    
    // Allow body scrolling again
    document.body.classList.remove('overflow-hidden');
    
    // Remove backdrop
    const backdrop = document.querySelector('.custom-modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
    
    // Mark as closed
    modal.isOpen = false;
    
    // Reset content if reset-on-close is true
    if (modal.element.getAttribute('data-reset-on-close') === 'true') {
        setModalToLoading(modalId);
    }
    
    // Trigger custom close event
    const closeEvent = new CustomEvent('modal:closed', { detail: { modalId } });
    document.dispatchEvent(closeEvent);
}

/**
 * Show a modal and load content into it
 * @param {string} modalId - ID of the modal to show
 * @param {string} url - URL to fetch content from
 */
function showModalWithContent(modalId, url) {
    const modal = customModalStore[modalId];
    if (!modal) return;
    
    // Show modal first with loading indicator
    showModal(modalId);
    setModalToLoading(modalId);
    
    // Add query parameter to indicate this is for modal view
    const modalUrl = url.includes('?') ? `${url}&modal=1` : `${url}?modal=1`;
    
    // Fetch content
    fetch(modalUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        setModalContent(modalId, html);
    })
    .catch(error => {
        setModalContent(modalId, `<div class="alert alert-danger">Error loading content: ${error.message}</div>`);
        console.error('Error loading modal content:', error);
    });
}

/**
 * Set modal body to loading state
 * @param {string} modalId - ID of the modal
 */
function setModalToLoading(modalId) {
    const modal = customModalStore[modalId];
    if (!modal || !modal.content) return;
    
    modal.content.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    modal.isLoading = true;
}

/**
 * Set content of a modal
 * @param {string} modalId - ID of the modal
 * @param {string} html - HTML content to set
 */
function setModalContent(modalId, html) {
    const modal = customModalStore[modalId];
    if (!modal || !modal.content) return;
    
    modal.content.innerHTML = html;
    modal.isLoading = false;
    
    // Initialize any Bootstrap components in new content
    if (typeof initBootstrapComponents === 'function') {
        initBootstrapComponents(modal.content);
    }
}

// Add custom modal styles
function addCustomModalStyles() {
    if (document.getElementById('custom-modal-styles')) return;
    
    const styleEl = document.createElement('style');
    styleEl.id = 'custom-modal-styles';
    styleEl.textContent = `
        .custom-modal {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1055;
            width: 100%;
            height: 100%;
            overflow-x: hidden;
            overflow-y: auto;
            outline: 0;
            display: none;
        }
        
        .custom-modal.show {
            display: flex !important;
            align-items: center;
            justify-content: center;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .custom-modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1050;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.5);
        }
    `;
    
    document.head.appendChild(styleEl);
}

// Call style addition
addCustomModalStyles();

// Export functions for external use
window.customModal = {
    show: showModal,
    hide: hideModal,
    showWithContent: showModalWithContent,
    setContent: setModalContent,
    setToLoading: setModalToLoading
};