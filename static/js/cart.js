document.addEventListener('DOMContentLoaded', function() {
    // Quantity increment/decrement buttons
    const decrementButtons = document.querySelectorAll('.quantity-decrement');
    const incrementButtons = document.querySelectorAll('.quantity-increment');
    const quantityInputs = document.querySelectorAll('.cart-quantity-input');
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    const emptyCartButton = document.getElementById('empty-cart-button');
    
    // Handle quantity decrement
    decrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.closest('.quantity-control').querySelector('.cart-quantity-input');
            let value = parseInt(input.value);
            if (value > 1) {
                value--;
                input.value = value;
                updateCart(input);
            }
        });
    });
    
    // Handle quantity increment
    incrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.closest('.quantity-control').querySelector('.cart-quantity-input');
            let value = parseInt(input.value);
            const max = parseInt(input.getAttribute('max'));
            if (value < max) {
                value++;
                input.value = value;
                updateCart(input);
            }
        });
    });
    
    // Handle manual quantity input
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            const min = parseInt(this.getAttribute('min'));
            const max = parseInt(this.getAttribute('max'));
            
            if (isNaN(value) || value < min) {
                value = min;
            } else if (value > max) {
                value = max;
            }
            
            this.value = value;
            updateCart(this);
        });
    });
    
    // Handle remove item
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            document.getElementById(`remove-form-${productId}`).submit();
        });
    });
    
    // Confirm empty cart
    if (emptyCartButton) {
        emptyCartButton.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to empty your cart?')) {
                e.preventDefault();
            }
        });
    }
    
    // Update cart via AJAX
    function updateCart(input) {
        const productId = input.dataset.productId;
        const quantity = input.value;
        const formData = new FormData();
        
        formData.append('product_id', productId);
        formData.append('quantity', quantity);
        
        fetch('/update-cart', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                // Reset to previous value
                location.reload();
            } else {
                // Update UI
                const itemRow = input.closest('.cart-item');
                const itemTotal = itemRow.querySelector('.item-total');
                
                // Format the currency
                const formatter = new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    minimumFractionDigits: 2
                });
                
                // Update item total
                itemTotal.textContent = formatter.format(data.item_total);
                
                // Update cart total
                document.getElementById('cart-total').textContent = formatter.format(data.cart_total);
            }
        })
        .catch(error => {
            console.error('Error updating cart:', error);
            alert('Failed to update cart. Please try again.');
        });
    }
});
