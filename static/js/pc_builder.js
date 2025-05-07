document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const componentItems = document.querySelectorAll('.component-item');
    const componentSearchInputs = document.querySelectorAll('.component-search');
    const resetBuildButton = document.getElementById('reset-build');
    const addAllToCartButton = document.getElementById('add-all-to-cart');
    const totalPriceElement = document.getElementById('total-price');
    const buildProgressElement = document.getElementById('build-progress');
    const selectedCountElement = document.getElementById('selected-count');
    const totalCountElement = document.getElementById('total-count');
    const estimatedWattageElement = document.getElementById('estimated-wattage');
    const wattageBarElement = document.getElementById('wattage-bar');
    const recommendedPsuElement = document.getElementById('recommended-psu');
    const compatibilityCardElement = document.getElementById('compatibility-card');
    const compatibilityIssuesElement = document.getElementById('compatibility-issues');
    
    // Store selected components
    let selectedComponents = {};
    let totalWattage = 0;
    let totalPrice = 0;
    
    // Currency formatter
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    });
    
    // Initialize component items click event
    componentItems.forEach(item => {
        item.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const category = this.dataset.category;
            const price = parseFloat(this.dataset.price);
            
            // Remove selected class from other items in the same category
            document.querySelectorAll(`.component-item[data-category="${category}"]`).forEach(el => {
                el.classList.remove('selected');
            });
            
            // Add selected class to clicked item
            this.classList.add('selected');
            
            // Update selected component
            selectedComponents[category] = {
                id: productId,
                price: price
            };
            
            // Update UI
            updateComponentStatus(category, true);
            updateTotalPrice();
            updateBuildProgress();
            checkCompatibility();
        });
    });
    
    // Reset build
    if (resetBuildButton) {
        resetBuildButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset your build? All selected components will be cleared.')) {
                // Clear selected components
                selectedComponents = {};
                
                // Reset UI
                componentItems.forEach(item => {
                    item.classList.remove('selected');
                });
                
                document.querySelectorAll('.component-status').forEach(status => {
                    status.innerHTML = '<i class="fas fa-plus-circle text-muted"></i>';
                });
                
                document.querySelectorAll('.selected-component-name').forEach(el => {
                    el.textContent = '';
                });
                
                // Update counters and prices
                updateTotalPrice();
                updateBuildProgress();
                updateEstimatedWattage(0);
                
                // Hide compatibility issues
                hideCompatibilityIssues();
            }
        });
    }
    
    // Add all to cart
    if (addAllToCartButton) {
        addAllToCartButton.addEventListener('click', function() {
            // Check if any component is selected
            if (Object.keys(selectedComponents).length === 0) {
                alert('Please select at least one component to add to cart.');
                return;
            }
            
            // Create a form to submit selected components
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/add-all-to-cart';
            
            // Add selected components as form fields
            for (const category in selectedComponents) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = `components[${category}]`;
                input.value = selectedComponents[category].id;
                form.appendChild(input);
            }
            
            // Add form to document and submit
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Update component status in the sidebar
    function updateComponentStatus(category, selected) {
        const statusElement = document.getElementById(`${category}-status`);
        if (statusElement) {
            if (selected) {
                statusElement.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
            } else {
                statusElement.innerHTML = '<i class="fas fa-plus-circle text-muted"></i>';
            }
        }
        
        // Update component name in the header
        const nameElement = document.querySelector(`#${category} .selected-component-name`);
        if (nameElement) {
            const selectedItem = document.querySelector(`.component-item.selected[data-category="${category}"]`);
            if (selectedItem) {
                const title = selectedItem.querySelector('.card-title').textContent;
                nameElement.textContent = title;
            } else {
                nameElement.textContent = '';
            }
        }
    }
    
    // Update total price
    function updateTotalPrice() {
        totalPrice = 0;
        
        for (const category in selectedComponents) {
            totalPrice += selectedComponents[category].price;
        }
        
        if (totalPriceElement) {
            totalPriceElement.textContent = formatter.format(totalPrice);
        }
    }
    
    // Update build progress
    function updateBuildProgress() {
        const selectedCount = Object.keys(selectedComponents).length;
        const totalCount = parseInt(totalCountElement.textContent);
        const progressPercentage = (selectedCount / totalCount) * 100;
        
        buildProgressElement.style.width = `${progressPercentage}%`;
        buildProgressElement.setAttribute('aria-valuenow', progressPercentage);
        
        selectedCountElement.textContent = selectedCount;
    }
    
    // Check compatibility of selected components
    function checkCompatibility() {
        if (Object.keys(selectedComponents).length < 2) {
            hideCompatibilityIssues();
            return;
        }
        
        // Prepare data for API request
        const data = {};
        for (const category in selectedComponents) {
            data[category] = selectedComponents[category].id;
        }
        
        // Check compatibility via API
        fetch('/api/check-compatibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (!data.compatible && data.issues.length > 0) {
                showCompatibilityIssues(data.issues);
            } else {
                hideCompatibilityIssues();
            }
            
            updateEstimatedWattage(data.estimated_wattage);
        })
        .catch(error => {
            console.error('Error checking compatibility:', error);
        });
    }
    
    // Show compatibility issues
    function showCompatibilityIssues(issues) {
        compatibilityCardElement.style.display = 'block';
        compatibilityIssuesElement.innerHTML = '';
        
        issues.forEach(issue => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-warning mb-2';
            alert.textContent = issue;
            compatibilityIssuesElement.appendChild(alert);
        });
    }
    
    // Hide compatibility issues
    function hideCompatibilityIssues() {
        compatibilityCardElement.style.display = 'none';
        compatibilityIssuesElement.innerHTML = '';
    }
    
    // Update estimated wattage
    function updateEstimatedWattage(wattage) {
        if (estimatedWattageElement) {
            estimatedWattageElement.textContent = wattage;
            
            // Update wattage bar
            const recommendedPsu = parseInt(recommendedPsuElement.textContent);
            const percentage = (wattage / recommendedPsu) * 100;
            
            wattageBarElement.style.width = `${percentage}%`;
            wattageBarElement.setAttribute('aria-valuenow', percentage);
            
            // Change color based on wattage percentage
            if (percentage > 80) {
                wattageBarElement.className = 'progress-bar bg-danger';
            } else if (percentage > 60) {
                wattageBarElement.className = 'progress-bar bg-warning';
            } else {
                wattageBarElement.className = 'progress-bar bg-success';
            }
        }
    }
    
    // Handle component tab changes (for storage and cooling)
    const storageTabs = document.querySelectorAll('#storage-tabs button');
    if (storageTabs.length > 0) {
        storageTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const target = document.querySelector(this.dataset.bsTarget);
                if (target) {
                    document.querySelectorAll('#storage .tab-pane').forEach(pane => {
                        pane.classList.remove('show', 'active');
                    });
                    target.classList.add('show', 'active');
                }
            });
        });
    }
    
    const coolingTabs = document.querySelectorAll('#cooling-tabs button');
    if (coolingTabs.length > 0) {
        coolingTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const target = document.querySelector(this.dataset.bsTarget);
                if (target) {
                    document.querySelectorAll('#cooling .tab-pane').forEach(pane => {
                        pane.classList.remove('show', 'active');
                    });
                    target.classList.add('show', 'active');
                }
            });
        });
    }
    
    // Smooth scroll to component sections
    const categoryLinks = document.querySelectorAll('.category-link');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Component search functionality
    if (componentSearchInputs.length > 0) {
        componentSearchInputs.forEach(input => {
            input.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                const componentCards = this.closest('.tab-pane, .card-body').querySelectorAll('.component-card');
                
                componentCards.forEach(card => {
                    const title = card.querySelector('.card-title').textContent.toLowerCase();
                    const description = card.querySelector('.card-text.small').textContent.toLowerCase();
                    
                    if (title.includes(searchTerm) || description.includes(searchTerm)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // Check if no results found
                const visibleCards = Array.from(componentCards).filter(card => card.style.display !== 'none');
                const noResultsAlert = this.closest('.tab-pane, .card-body').querySelector('.no-results-alert');
                
                if (visibleCards.length === 0 && searchTerm !== '') {
                    // If no alert exists, create one
                    if (!noResultsAlert) {
                        const alert = document.createElement('div');
                        alert.className = 'alert alert-info no-results-alert';
                        alert.textContent = 'No components found matching your search.';
                        this.parentElement.insertAdjacentElement('afterend', alert);
                    } else {
                        noResultsAlert.style.display = 'block';
                    }
                } else if (noResultsAlert) {
                    noResultsAlert.style.display = 'none';
                }
            });
        });
    }
});
