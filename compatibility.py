def check_compatibility(components):
    """
    Check compatibility between different PC components
    
    Args:
        components: Dictionary of components (key=category, value=product object)
    
    Returns:
        dict: Contains 'compatible' boolean and 'issues' list
    """
    issues = []
    compatible = True
    
    # CPU and Motherboard socket compatibility
    if 'cpu' in components and 'motherboard' in components:
        cpu = components['cpu']
        motherboard = components['motherboard']
        
        cpu_socket = cpu.specs.get('socket')
        mb_socket = motherboard.specs.get('socket')
        
        if cpu_socket and mb_socket and cpu_socket != mb_socket:
            issues.append(f"CPU socket ({cpu_socket}) is not compatible with motherboard socket ({mb_socket}).")
            compatible = False
    
    # RAM and Motherboard compatibility
    if 'ram' in components and 'motherboard' in components:
        ram = components['ram']
        motherboard = components['motherboard']
        
        ram_type = ram.specs.get('type')
        mb_ram_type = motherboard.specs.get('ram_type')
        
        if ram_type and mb_ram_type and ram_type != mb_ram_type:
            issues.append(f"RAM type ({ram_type}) is not compatible with motherboard RAM type ({mb_ram_type}).")
            compatible = False
    
    # Case and Motherboard form factor compatibility
    if 'case' in components and 'motherboard' in components:
        case = components['case']
        motherboard = components['motherboard']
        
        case_form_factors = case.specs.get('supported_form_factors', [])
        mb_form_factor = motherboard.specs.get('form_factor')
        
        if case_form_factors and mb_form_factor and mb_form_factor not in case_form_factors:
            issues.append(f"Motherboard form factor ({mb_form_factor}) is not supported by the case ({', '.join(case_form_factors)}).")
            compatible = False
    
    # GPU and Case compatibility (length)
    if 'gpu' in components and 'case' in components:
        gpu = components['gpu']
        case = components['case']
        
        gpu_length = gpu.specs.get('length')
        case_max_gpu_length = case.specs.get('max_gpu_length')
        
        if gpu_length and case_max_gpu_length and float(gpu_length) > float(case_max_gpu_length):
            issues.append(f"GPU length ({gpu_length}mm) exceeds the maximum supported by the case ({case_max_gpu_length}mm).")
            compatible = False
    
    # Power supply wattage check
    if 'psu' in components:
        psu = components['psu']
        psu_wattage = psu.specs.get('wattage')
        
        if psu_wattage:
            required_wattage = calculate_power_consumption(components)
            
            if int(psu_wattage) < required_wattage:
                issues.append(f"Power supply wattage ({psu_wattage}W) is not sufficient for the estimated power consumption ({required_wattage}W).")
                compatible = False
            elif int(psu_wattage) < required_wattage * 1.2:  # 20% headroom for power fluctuations
                issues.append(f"Power supply wattage ({psu_wattage}W) is close to the estimated power consumption ({required_wattage}W). Consider a higher wattage PSU for stability.")
    
    return {
        'compatible': compatible,
        'issues': issues
    }


def calculate_power_consumption(components):
    """
    Calculate estimated power consumption of the selected components
    
    Args:
        components: Dictionary of components (key=category, value=product object)
    
    Returns:
        int: Estimated power consumption in watts
    """
    total_wattage = 0
    
    # CPU power consumption
    if 'cpu' in components:
        cpu = components['cpu']
        cpu_tdp = cpu.specs.get('tdp')
        
        if cpu_tdp:
            total_wattage += int(cpu_tdp)
        else:
            # Default values based on category
            if 'i9' in cpu.name.lower() or 'ryzen 9' in cpu.name.lower():
                total_wattage += 125
            elif 'i7' in cpu.name.lower() or 'ryzen 7' in cpu.name.lower():
                total_wattage += 95
            elif 'i5' in cpu.name.lower() or 'ryzen 5' in cpu.name.lower():
                total_wattage += 65
            else:
                total_wattage += 50
    
    # GPU power consumption
    if 'gpu' in components:
        gpu = components['gpu']
        gpu_tdp = gpu.specs.get('tdp')
        
        if gpu_tdp:
            total_wattage += int(gpu_tdp)
        else:
            # Default values based on category
            if 'rtx 3090' in gpu.name.lower() or 'rtx 3080' in gpu.name.lower() or 'rx 6900' in gpu.name.lower():
                total_wattage += 320
            elif 'rtx 3070' in gpu.name.lower() or 'rx 6800' in gpu.name.lower():
                total_wattage += 220
            elif 'rtx 3060' in gpu.name.lower() or 'rx 6700' in gpu.name.lower():
                total_wattage += 170
            else:
                total_wattage += 120
    
    # RAM power consumption
    if 'ram' in components:
        # Approximate RAM power usage based on typical values
        ram = components['ram']
        ram_capacity = ram.specs.get('capacity')
        
        if ram_capacity:
            # Estimate about 3W per 8GB of RAM
            total_wattage += int(int(ram_capacity) / 8 * 3)
        else:
            # Default value if we can't determine
            total_wattage += 5
    
    # Storage power consumption
    if 'storage' in components:
        storage = components['storage']
        storage_type = storage.specs.get('type')
        
        if storage_type:
            if storage_type.lower() == 'hdd':
                total_wattage += 7
            elif storage_type.lower() in ['ssd', 'nvme', 'sata_ssd']:
                total_wattage += 3
        else:
            total_wattage += 5
    
    # Motherboard power consumption (fixed approximation)
    if 'motherboard' in components:
        total_wattage += 15
    
    # Cooling power consumption
    if 'cooling' in components:
        cooling = components['cooling']
        cooling_type = cooling.specs.get('type')
        
        if cooling_type:
            if cooling_type.lower() == 'air':
                total_wattage += 5
            elif cooling_type.lower() == 'aio':
                total_wattage += 10
        else:
            total_wattage += 5
    
    # Add some wattage for other components and peripherals
    total_wattage += 30
    
    return total_wattage
