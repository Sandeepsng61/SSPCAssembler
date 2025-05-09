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
            // If no components are selected, reset power indicator
            updateEstimatedWattage(0);
            return;
        }

        // Prepare data for API request
        const data = {};
        try {
            for (const category in selectedComponents) {
                if (selectedComponents[category] && selectedComponents[category].id) {
                    data[category] = selectedComponents[category].id;
                }
            }
            
            if (Object.keys(data).length === 0) {
                hideCompatibilityIssues();
                updateEstimatedWattage(0);
                return;
            }
            
            // Check compatibility via API
            fetch('/api/check-compatibility', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Always check if data and expected fields exist
                if (data) {
                    // Show compatibility issues if there are any
                    if (data.issues && data.issues.length > 0 && data.compatible === false) {
                        showCompatibilityIssues(data.issues);
                    } else if (data.issues && data.issues.length > 0) {
                        // Show warnings even if system is considered compatible
                        showCompatibilityIssues(data.issues);
                    } else {
                        hideCompatibilityIssues();
                    }
                    
                    // Update power estimate if available
                    if (typeof data.estimated_wattage === 'number') {
                        updateEstimatedWattage(data.estimated_wattage);
                    }
                } else {
                    // Handle empty response
                    hideCompatibilityIssues();
                }
            })
            .catch(error => {
                console.error('Error checking compatibility:', error);
                // Handle error gracefully - don't show any error to user but reset compatibility display
                hideCompatibilityIssues();
                
                // Default estimated wattage to sum of visible component TDPs if available
                let fallbackWattage = 0;
                
                // Check if we can get CPU TDP
                if (selectedComponents.cpu) {
                    const cpuCard = document.querySelector(`.component-item.selected[data-category="cpu"]`);
                    if (cpuCard) {
                        const cpuName = cpuCard.querySelector('.card-title').textContent;
                        if (cpuName.includes('i9') || cpuName.includes('Ryzen 9')) {
                            fallbackWattage += 125;
                        } else if (cpuName.includes('i7') || cpuName.includes('Ryzen 7')) {
                            fallbackWattage += 95;
                        } else if (cpuName.includes('i5') || cpuName.includes('Ryzen 5')) {
                            fallbackWattage += 65;
                        } else {
                            fallbackWattage += 50;
                        }
                    }
                }
                
                // Check if we can get GPU TDP
                if (selectedComponents.gpu) {
                    const gpuCard = document.querySelector(`.component-item.selected[data-category="gpu"]`);
                    if (gpuCard) {
                        const gpuName = gpuCard.querySelector('.card-title').textContent.toLowerCase();
                        if (gpuName.includes('rtx 40')) {
                            fallbackWattage += 300;
                        } else if (gpuName.includes('rtx 30')) {
                            fallbackWattage += 250;
                        } else {
                            fallbackWattage += 150;
                        }
                    }
                }
                
                // Add base power for other components
                fallbackWattage += 100;
                
                // Update wattage display with fallback value
                updateEstimatedWattage(fallbackWattage);
            });
        } catch (error) {
            console.error('Error preparing compatibility check:', error);
            hideCompatibilityIssues();
            updateEstimatedWattage(0);
        }
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

    // Update estimated wattage with enhanced power consumption indicator
    function updateEstimatedWattage(wattage) {
        if (estimatedWattageElement) {
            estimatedWattageElement.textContent = wattage;

            // Calculate percentage for 1200W max scale
            const maxWattage = 1200;
            const percentage = Math.min((wattage / maxWattage) * 100, 100);

            wattageBarElement.style.width = `${percentage}%`;
            wattageBarElement.setAttribute('aria-valuenow', wattage);
            
            // Get DOM elements for PSU recommendation
            const psuRecommendation = document.getElementById('psu-recommendation');
            const psuRecommendationText = document.getElementById('psu-recommendation-text');
            const suggestedPsu = document.getElementById('suggested-psu');
            const suggestedPsuText = document.getElementById('suggested-psu-text');
            
            // Change color gradient based on power consumption levels
            if (wattage > 1000) {
                // Red: Very high consumption
                wattageBarElement.className = 'progress-bar bg-danger';
                
                // Show warning for high power consumption
                if (psuRecommendation && psuRecommendationText) {
                    psuRecommendation.style.display = 'block';
                    psuRecommendationText.textContent = 'High Power Consumption! Choose a PSU with higher wattage and efficiency rating.';
                    
                    // Suggest a compatible PSU
                    suggestCompatiblePsu(wattage);
                }
            } else if (wattage > 700) {
                // Orange: High consumption
                wattageBarElement.className = 'progress-bar bg-warning';
                wattageBarElement.style.backgroundColor = '#fd7e14'; // Bootstrap orange
                
                if (psuRecommendation && psuRecommendationText) {
                    psuRecommendation.style.display = 'block';
                    psuRecommendationText.textContent = 'High power usage. Ensure you select an appropriate PSU.';
                    
                    // Suggest a compatible PSU
                    suggestCompatiblePsu(wattage);
                }
            } else if (wattage > 400) {
                // Yellow: Moderate consumption
                wattageBarElement.className = 'progress-bar bg-warning';
                
                if (psuRecommendation && psuRecommendationText) {
                    psuRecommendation.style.display = 'none';
                    
                    // Suggest a compatible PSU
                    suggestCompatiblePsu(wattage);
                }
            } else {
                // Green: Low/efficient consumption
                wattageBarElement.className = 'progress-bar bg-success';
                
                if (psuRecommendation && psuRecommendationText) {
                    psuRecommendation.style.display = 'none';
                    
                    if (wattage > 0) {
                        // Suggest a compatible PSU
                        suggestCompatiblePsu(wattage);
                    } else {
                        // Hide suggestion if no components selected
                        if (suggestedPsu) {
                            suggestedPsu.style.display = 'none';
                        }
                    }
                }
            }
        }
    }
    
    // Suggest a compatible PSU based on total wattage
    function suggestCompatiblePsu(wattage) {
        const suggestedPsu = document.getElementById('suggested-psu');
        const suggestedPsuText = document.getElementById('suggested-psu-text');
        
        if (!suggestedPsu || !suggestedPsuText) return;
        
        // Calculate recommended PSU wattage (add 20% headroom)
        const recommendedWattage = Math.ceil(wattage * 1.2 / 50) * 50; // Round up to nearest 50W
        
        // Determine efficiency rating suggestion based on power usage
        let efficiencyRating = "80+ Bronze";
        if (wattage > 800) {
            efficiencyRating = "80+ Gold or Platinum";
        } else if (wattage > 500) {
            efficiencyRating = "80+ Gold";
        } else if (wattage > 300) {
            efficiencyRating = "80+ Silver";
        }
        
        // Display suggestion
        suggestedPsu.style.display = 'block';
        suggestedPsuText.innerHTML = `Recommended PSU: <strong>${recommendedWattage}W</strong> with <strong>${efficiencyRating}</strong> efficiency rating.`;
        
        // Check if a PSU is selected
        if (selectedComponents.psu) {
            // Get the selected PSU from the DOM to check its wattage
            const selectedPsuCard = document.querySelector(`.component-item.selected[data-category="psu"]`);
            if (selectedPsuCard) {
                const psuName = selectedPsuCard.querySelector('.card-title').textContent;
                
                // Extract wattage from PSU name if possible (rough estimation)
                const wattMatch = psuName.match(/(\d+)W/);
                if (wattMatch && parseInt(wattMatch[1]) < recommendedWattage) {
                    suggestedPsuText.innerHTML += ` <span class="text-danger">Your selected PSU may be insufficient!</span>`;
                }
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

    // Component search functionality - improved implementation
    function initializeSearchFunctionality() {
        const componentSearchInputs = document.querySelectorAll('.component-search');
        
        if (componentSearchInputs.length > 0) {
            componentSearchInputs.forEach(input => {
                input.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase().trim();
                    // Find the closest tab-pane or card-body - parent container of the components
                    const container = this.closest('.tab-pane, .card-body');
                    
                    if (!container) {
                        console.error('Could not find component container');
                        return;
                    }
                    
                    const componentCards = container.querySelectorAll('.component-card');
                    let hasVisibleCards = false;
                    
                    componentCards.forEach(card => {
                        const title = card.querySelector('.card-title');
                        const description = card.querySelector('.card-text.small');
                        
                        if (!title || !description) {
                            console.warn('Component card is missing title or description elements');
                            return;
                        }
                        
                        const titleText = title.textContent.toLowerCase();
                        const descText = description.textContent.toLowerCase();
                        
                        if (titleText.includes(searchTerm) || descText.includes(searchTerm)) {
                            card.style.display = 'block';
                            hasVisibleCards = true;
                        } else {
                            card.style.display = 'none';
                        }
                    });
                    
                    // No results alert handling
                    let noResultsAlert = container.querySelector('.no-results-alert');
                    
                    if (!hasVisibleCards && searchTerm !== '') {
                        if (!noResultsAlert) {
                            noResultsAlert = document.createElement('div');
                            noResultsAlert.className = 'alert alert-info no-results-alert';
                            noResultsAlert.textContent = 'No components found matching your search.';
                            this.parentElement.insertAdjacentElement('afterend', noResultsAlert);
                        } else {
                            noResultsAlert.style.display = 'block';
                        }
                    } else if (noResultsAlert) {
                        noResultsAlert.style.display = 'none';
                    }
                });
            });
        }
    }
    
    // Initialize search on page load
    initializeSearchFunctionality();
    
    // Re-initialize search after any tab change to ensure it works in all tabs
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tabButton => {
        tabButton.addEventListener('shown.bs.tab', function() {
            // Small delay to ensure DOM is ready
            setTimeout(initializeSearchFunctionality, 100);
        });
    });
});
