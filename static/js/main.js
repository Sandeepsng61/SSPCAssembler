// Main JavaScript file for PC Assembler website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initBootstrapComponents();
    
    // Setup cart quantity update handlers
    setupCartQuantityHandlers();
    
    // Handle newsletter subscription
    setupNewsletterForm();
    
    // Add animation effects for cards
    setupCardAnimations();
});

/**
 * Initialize Bootstrap components
 * @param {HTMLElement} container - Optional container to scope component initialization
 */
function initBootstrapComponents(container = document) {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(container.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        // Remove any existing tooltip instance to prevent duplicates
        const existingTooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
        if (existingTooltip) {
            existingTooltip.dispose();
        }
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(container.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        // Remove any existing popover instance to prevent duplicates
        const existingPopover = bootstrap.Popover.getInstance(popoverTriggerEl);
        if (existingPopover) {
            existingPopover.dispose();
        }
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup cart quantity update handlers
 */
function setupCartQuantityHandlers() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form && form.getAttribute('data-ajax') === 'true') {
                updateCartItemQuantity(form, this.value);
            }
        });
    });
}

// Modal handling is now completely in modals.js

/**
 * Function to update cart item quantity via AJAX
 */
function updateCartItemQuantity(form, quantity) {
    const productId = form.querySelector('input[name="product_id"]').value;
    const url = form.getAttribute('action');
    
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Update the item total
        const itemRow = form.closest('tr');
        if (itemRow) {
            const itemTotalEl = itemRow.querySelector('.item-total');
            if (itemTotalEl) {
                itemTotalEl.textContent = '₹' + data.item_total.toFixed(2);
            }
        }
        
        // Update the cart total
        const cartTotalEl = document.getElementById('cart-total');
        if (cartTotalEl) {
            cartTotalEl.textContent = '₹' + data.cart_total.toFixed(2);
        }
    })
    .catch(error => {
        console.error('Error updating cart:', error);
        alert('Error updating cart. Please try again.');
    });
}

/**
 * Setup newsletter form
 */
function setupNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            
            if (emailInput && emailInput.value) {
                // Show success message (in a real app, this would submit to a backend)
                alert('Thank you for subscribing to our newsletter!');
                emailInput.value = '';
            } else {
                alert('Please enter a valid email address.');
            }
        });
    }
}

/**
 * Setup card animations
 */
function setupCardAnimations() {
    const animatedCards = document.querySelectorAll('.card');
    if (animatedCards.length > 0) {
        window.addEventListener('scroll', function() {
            animatedCards.forEach(card => {
                if (isElementInViewport(card) && !card.classList.contains('animated')) {
                    card.classList.add('animated');
                }
            });
        });
        
        // Trigger once on page load
        setTimeout(function() {
            window.dispatchEvent(new Event('scroll'));
        }, 100);
    }
}

/**
 * Utility function to check if element is in viewport
 */
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Product view button handling is now in modals.js
