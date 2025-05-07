/**
 * Enhanced modals.js
 * This file handles all modal-related functionality with strict control over event propagation
 * to prevent the modal flickering issues.
 */

// Immediately create a global store for modal instances
window.modalStore = {};

// Wait until the DOM is fully loaded before attaching handlers
document.addEventListener('DOMContentLoaded', function() {
    // Disable all default Bootstrap modal behavior for view buttons
    disableDefaultBootstrapModalBehavior();
    
    // Set up proper global modal event delegation
    setupModalEventDelegation();
    
    // Initialize all modal instances that exist in the DOM at page load
    initializeExistingModals();
});

/**
 * Disable default Bootstrap modal behavior for all view buttons
 * This prevents the automatic showing/hiding that causes flickering
 */
function disableDefaultBootstrapModalBehavior() {
    // Find all modal trigger buttons
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    
    modalTriggers.forEach(trigger => {
        if (trigger.classList.contains('btn-view') || trigger.classList.contains('view-btn')) {
            // Override the data-bs-toggle attribute to prevent Bootstrap's built-in behavior
            // Store original value for reference
            trigger.setAttribute('data-original-toggle', trigger.getAttribute('data-bs-toggle'));
            trigger.removeAttribute('data-bs-toggle');
        }
    });
}

/**
 * Set up global event delegation for modal events
 * This is more efficient than attaching events to individual buttons
 */
function setupModalEventDelegation() {
    // Use event delegation for all modal-related actions
    document.addEventListener('click', function(event) {
        // Find if the clicked element or any of its parents are view buttons
        const viewButton = event.target.closest('.btn-view, .view-btn');
        if (viewButton) {
            event.preventDefault();
            event.stopPropagation();
            
            // Get modal attributes
            const modalId = viewButton.getAttribute('data-bs-target') || 
                           viewButton.getAttribute('data-target');
            const url = viewButton.getAttribute('data-url');
            
            if (modalId && url) {
                openModalWithContent(modalId, url);
            }
            return;
        }
        
        // Check for modal close buttons
        const closeButton = event.target.closest('[data-bs-dismiss="modal"]');
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            if (modal) {
                // Get existing modal instance or create new one
                const modalInstance = getModalInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    }, true); // Use capture phase to ensure we catch events before Bootstrap
    
    // Attach reset handlers to all modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            if (modal.getAttribute('data-reset-on-close') === 'true') {
                resetModal(modal);
            }
        });
    });
}

/**
 * Initialize all modals that exist on page load to avoid recreating them
 */
function initializeExistingModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        if (modal.id) {
            getModalInstance(modal);
        }
    });
}

/**
 * Open a modal and load content into it
 * @param {string} modalId - The ID of the modal to open including the # prefix
 * @param {string} url - The URL to fetch content from
 */
function openModalWithContent(modalId, url) {
    // Ensure modalId has # prefix
    if (!modalId.startsWith('#')) {
        modalId = '#' + modalId;
    }
    
    const modal = document.querySelector(modalId);
    if (!modal) return;
    
    const contentContainer = modal.querySelector('.modal-body');
    if (!contentContainer) return;
    
    // Get modal instance (creates if needed)
    const modalInstance = getModalInstance(modal);
    
    // Show modal with loading spinner first
    modalInstance.show();
    
    // Set loading state
    setModalLoading(contentContainer);
    
    // Add query parameter to indicate this is for modal view
    const modalUrl = url.includes('?') ? `${url}&modal=1` : `${url}?modal=1`;
    
    // Use a timeout to ensure modal is fully visible before loading content
    // This helps prevent flickering
    setTimeout(() => {
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
            contentContainer.innerHTML = html;
            contentContainer.setAttribute('data-loaded', 'true');
            
            // Initialize any Bootstrap components in the loaded content
            if (typeof initBootstrapComponents === 'function') {
                initBootstrapComponents(contentContainer);
            }
        })
        .catch(error => {
            contentContainer.innerHTML = `<div class="alert alert-danger">Error loading content: ${error.message}</div>`;
            console.error('Error loading modal content:', error);
        });
    }, 100);
}

/**
 * Get or create a Bootstrap modal instance
 * @param {HTMLElement} modal - The modal element
 * @returns {object} Bootstrap modal instance
 */
function getModalInstance(modal) {
    if (!modal || !modal.id) return null;
    
    // Check if we already have this modal instance
    if (!window.modalStore[modal.id]) {
        // Create new instance
        window.modalStore[modal.id] = new bootstrap.Modal(modal, {
            backdrop: 'static', // Prevent closing on backdrop click to avoid flicker issues
            keyboard: false     // Prevent closing with escape key
        });
    }
    
    return window.modalStore[modal.id];
}

/**
 * Set modal content to loading state
 * @param {HTMLElement} container - The modal body container
 */
function setModalLoading(container) {
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    container.removeAttribute('data-loaded');
}

/**
 * Reset modal content
 * @param {HTMLElement} modal - The modal element
 */
function resetModal(modal) {
    const contentContainer = modal.querySelector('.modal-body');
    if (contentContainer) {
        setModalLoading(contentContainer);
    }
}

/**
 * Handle a specific modal open request (can be called directly)
 * @param {string} modalId - Modal ID with # prefix
 * @param {string} url - URL to load content from
 */
function handleModalOpen(modalId, url) {
    openModalWithContent(modalId, url);
}

/**
 * Load content into a specific modal that's already open
 * @param {string} modalId - Modal ID with # prefix 
 * @param {string} url - URL to load content from
 */
function loadModalContent(modalId, url) {
    if (!modalId.startsWith('#')) {
        modalId = '#' + modalId;
    }
    
    const modal = document.querySelector(modalId);
    if (!modal) return;
    
    const contentContainer = modal.querySelector('.modal-body');
    if (!contentContainer) return;
    
    // Set loading state
    setModalLoading(contentContainer);
    
    // Add query parameter to indicate this is for modal view
    const modalUrl = url.includes('?') ? `${url}&modal=1` : `${url}?modal=1`;
    
    // Fetch and load content
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
        contentContainer.innerHTML = html;
        contentContainer.setAttribute('data-loaded', 'true');
        
        // Initialize any Bootstrap components in the loaded content
        if (typeof initBootstrapComponents === 'function') {
            initBootstrapComponents(contentContainer);
        }
    })
    .catch(error => {
        contentContainer.innerHTML = `<div class="alert alert-danger">Error loading content: ${error.message}</div>`;
        console.error('Error loading modal content:', error);
    });
}