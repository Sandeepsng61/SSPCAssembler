/**
 * Location handler for cascading dropdowns and PIN code lookup
 * 
 * This script handles the dynamic loading of states and cities
 * for the checkout form, as well as PIN code validation.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Location script loaded - version 2');
    
    // Get the form elements - use querySelector as a more reliable method
    const countrySelect = document.querySelector('select#country');
    const stateSelect = document.querySelector('select#state');
    const citySelect = document.querySelector('select#city');
    const pincodeInput = document.querySelector('input#zipcode');
    const postOfficeInfoDiv = document.getElementById('post-office-info');
    
    console.log('Form elements found:', {
        countrySelect: countrySelect ? 'Found' : 'Not found',
        stateSelect: stateSelect ? 'Found' : 'Not found',
        citySelect: citySelect ? 'Found' : 'Not found',
        pincodeInput: pincodeInput ? 'Found' : 'Not found'
    });
    
    // Initialize only if we have the state dropdown (which is required)
    if (stateSelect) {
        // Debug that we're starting initialization
        console.log('State select found - initializing cascading dropdowns');
        
        // Load states immediately
        loadStates();
        
        // Add event listeners for the dropdowns
        if (countrySelect) {
            console.log('Setting up country change listener');
            countrySelect.addEventListener('change', loadStates);
        }
        
        // Always set up the state change listener since it's our main dropdown
        console.log('Setting up state change listener');
        stateSelect.addEventListener('change', loadCities);
        
        if (citySelect) {
            console.log('Setting up city change listener');
            citySelect.addEventListener('change', handleCityChange);
        }
        
        if (pincodeInput) {
            console.log('Setting up pincode blur listener');
            pincodeInput.addEventListener('blur', lookupPostOffices);
        }
    } else {
        console.error('Could not find state select element - cascading dropdowns will not work');
    }
    
    /**
     * Load states for the selected country
     */
    function loadStates() {
        console.log('Loading states...');
        
        // Show loading indicator
        stateSelect.innerHTML = '<option value="">Loading states...</option>';
        stateSelect.disabled = true;
        
        if (citySelect) {
            citySelect.innerHTML = '<option value="">Select City</option>';
            citySelect.disabled = true;
        }
        
        // For now, we only have India, so this function just gets all states
        fetch('/api/states')
            .then(response => {
                console.log('States API response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(states => {
                console.log('States loaded:', states);
                
                // Clear current options and enable dropdown
                stateSelect.innerHTML = '<option value="">Select State</option>';
                stateSelect.disabled = false;
                
                if (citySelect) {
                    citySelect.innerHTML = '<option value="">Select City</option>';
                    citySelect.disabled = true; // Keep disabled until a state is selected
                }
                
                // Check if we have states data
                if (!states || states.length === 0) {
                    console.warn('No states returned from API');
                    return;
                }
                
                // Add new options
                states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state.id;
                    option.textContent = state.name;
                    stateSelect.appendChild(option);
                });
                
                console.log('States loaded successfully, options added:', states.length);
                
                // Trigger city loading if a state is already selected
                if (stateSelect.value) {
                    if (citySelect) citySelect.disabled = false;
                    loadCities();
                }
            })
            .catch(error => {
                console.error('Error loading states:', error);
                
                // Reset dropdowns on error
                stateSelect.innerHTML = '<option value="">Error loading states</option>';
                stateSelect.disabled = false;
                
                if (citySelect) {
                    citySelect.innerHTML = '<option value="">Select City</option>';
                    citySelect.disabled = true;
                }
            });
    }
    
    /**
     * Load cities for the selected state
     */
    function loadCities() {
        const stateId = stateSelect.value;
        
        // Debug the selected state
        console.log('Loading cities for state:', stateId);
        
        if (!stateId) {
            console.warn('No state selected, cannot load cities');
            return;
        }
        
        // Show loading indicator for better UX
        if (citySelect) {
            citySelect.innerHTML = '<option value="">Loading cities...</option>';
            citySelect.disabled = true;
        }
        
        // Make the API request with the state ID
        fetch(`/api/cities/${stateId}`)
            .then(response => {
                console.log('Cities API response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(cities => {
                console.log('Cities loaded:', cities);
                
                // Make sure we still have the citySelect element
                if (!citySelect) {
                    console.error('City select element no longer exists');
                    return;
                }
                
                // Clear and enable the dropdown
                citySelect.innerHTML = '<option value="">Select City</option>';
                citySelect.disabled = false;
                
                // Check if we have cities data
                if (!cities || cities.length === 0) {
                    console.warn('No cities returned for state:', stateId);
                    return;
                }
                
                // Add new options
                cities.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.id;
                    option.textContent = city.name;
                    citySelect.appendChild(option);
                });
                
                console.log('Cities loaded successfully, options added:', cities.length);
                
                // If a city is already selected, trigger pincode loading
                if (citySelect.value) {
                    handleCityChange();
                }
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                
                // Reset the city dropdown on error
                if (citySelect) {
                    citySelect.innerHTML = '<option value="">Error loading cities</option>';
                    citySelect.disabled = false;
                }
            });
    }
    
    /**
     * Handle city selection change
     */
    function handleCityChange() {
        const stateId = stateSelect.value;
        const cityId = citySelect.value;
        
        if (!stateId || !cityId) return;
        
        // Clear the pincode field if the user changed the city
        pincodeInput.value = '';
        hidePostOfficeInfo();
    }
    
    /**
     * Lookup post offices based on PIN code
     */
    function lookupPostOffices() {
        const stateId = stateSelect.value;
        const cityId = citySelect.value;
        const pincode = pincodeInput.value.trim();
        
        if (!stateId || !cityId || !pincode) {
            hidePostOfficeInfo();
            return;
        }
        
        fetch(`/api/postoffices/${stateId}/${cityId}/${pincode}`)
            .then(response => response.json())
            .then(postOffices => {
                if (postOffices && postOffices.length > 0) {
                    displayPostOfficeInfo(postOffices);
                } else {
                    showInvalidPincode();
                }
            })
            .catch(error => {
                console.error('Error looking up post offices:', error);
                hidePostOfficeInfo();
            });
    }
    
    /**
     * Display post office information
     */
    function displayPostOfficeInfo(postOffices) {
        if (!postOfficeInfoDiv) return;
        
        let html = '<div class="mt-2 p-2 border border-success rounded bg-light">';
        html += '<p class="mb-1 text-success"><i class="fas fa-check-circle me-2"></i> Valid PIN code</p>';
        
        if (postOffices.length > 0) {
            html += '<p class="mb-1 small">Serving post offices:</p>';
            html += '<ul class="mb-0 small">';
            postOffices.forEach(office => {
                html += `<li>${office}</li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        
        postOfficeInfoDiv.innerHTML = html;
        postOfficeInfoDiv.style.display = 'block';
    }
    
    /**
     * Show invalid pincode message
     */
    function showInvalidPincode() {
        if (!postOfficeInfoDiv) return;
        
        const html = `
            <div class="mt-2 p-2 border border-danger rounded bg-light">
                <p class="mb-0 text-danger">
                    <i class="fas fa-exclamation-circle me-2"></i> 
                    Invalid PIN code for selected city
                </p>
            </div>
        `;
        
        postOfficeInfoDiv.innerHTML = html;
        postOfficeInfoDiv.style.display = 'block';
    }
    
    /**
     * Hide post office information
     */
    function hidePostOfficeInfo() {
        if (postOfficeInfoDiv) {
            postOfficeInfoDiv.style.display = 'none';
        }
    }
});