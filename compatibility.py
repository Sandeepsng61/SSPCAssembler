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
          
      # Check CPU generation compatibility with motherboard chipset
      cpu_gen = cpu.specs.get('generation')
      mb_chipset = motherboard.specs.get('chipset')
      
      if cpu_gen and mb_chipset:
          # Intel CPU and motherboard compatibility
          if 'Intel' in cpu.name and ('Intel' in motherboard.name or 'Z' in mb_chipset or 'H' in mb_chipset or 'B' in mb_chipset):
              # Example: 12th/13th gen Intel requires 600/700 series chipsets
              cpu_gen_num = None
              if cpu_gen.isdigit():
                  cpu_gen_num = int(cpu_gen)
              elif 'th' in cpu_gen:
                  try:
                      cpu_gen_num = int(cpu_gen.replace('th', ''))
                  except ValueError:
                      pass
                  
              if cpu_gen_num:
                  chipset_series = None
                  if mb_chipset[0] in ['Z', 'H', 'B'] and mb_chipset[1:].isdigit():
                      chipset_series = int(mb_chipset[1:])
                  
                  if chipset_series:
                      # Check for major compatibility issues
                      if cpu_gen_num >= 12 and chipset_series < 600:
                          issues.append(f"CPU generation ({cpu_gen}) may not be compatible with motherboard chipset ({mb_chipset}).")
                          compatible = False
                      elif cpu_gen_num <= 10 and chipset_series >= 500:
                          issues.append(f"CPU generation ({cpu_gen}) may not be compatible with newer motherboard chipset ({mb_chipset}).")
                          compatible = False
          
          # AMD CPU and motherboard compatibility
          elif 'AMD' in cpu.name or 'Ryzen' in cpu.name:
              # Ryzen compatibility checks
              if 'Ryzen' in cpu.name:
                  ryzen_gen = None
                  if 'Ryzen 3' in cpu.name or 'Ryzen 5' in cpu.name or 'Ryzen 7' in cpu.name or 'Ryzen 9' in cpu.name:
                      # Extract generation from name
                      if '5000' in cpu.name or '5XXX' in cpu.name:
                          ryzen_gen = 5  # 5000 series
                      elif '3000' in cpu.name or '3XXX' in cpu.name:
                          ryzen_gen = 3  # 3000 series
                      
                  if ryzen_gen and mb_chipset:
                      if ryzen_gen >= 5 and 'A320' in mb_chipset:
                          issues.append(f"Ryzen 5000 series CPU may not be compatible with older A320 chipset motherboard.")
                          compatible = False
                      elif ryzen_gen >= 3 and 'A320' in mb_chipset:
                          issues.append(f"Ryzen 3000 series CPU may require a BIOS update to work with A320 chipset motherboard.")

  # RAM and Motherboard compatibility
  if 'ram' in components and 'motherboard' in components:
      ram = components['ram']
      motherboard = components['motherboard']

      # Check RAM type compatibility (DDR4 vs DDR5)
      ram_type = ram.specs.get('type')
      mb_ram_type = motherboard.specs.get('ram_type')

      if ram_type and mb_ram_type and ram_type != mb_ram_type:
          issues.append(f"RAM type ({ram_type}) is not compatible with motherboard RAM type ({mb_ram_type}).")
          compatible = False
          
      # Check RAM speed compatibility
      ram_speed = ram.specs.get('speed')
      mb_max_ram_speed = motherboard.specs.get('max_ram_speed')
      
      if ram_speed and mb_max_ram_speed:
          try:
              ram_speed_val = int(ram_speed.replace('MHz', '').strip())
              mb_max_ram_speed_val = int(mb_max_ram_speed.replace('MHz', '').strip())
              
              if ram_speed_val > mb_max_ram_speed_val:
                  issues.append(f"RAM speed ({ram_speed}) exceeds maximum supported by motherboard ({mb_max_ram_speed}). RAM will run at slower speeds.")
          except (ValueError, AttributeError):
              pass
              
      # Check RAM capacity compatibility
      ram_capacity = ram.specs.get('capacity')
      mb_max_ram_capacity = motherboard.specs.get('max_ram_capacity')
      
      if ram_capacity and mb_max_ram_capacity:
          try:
              ram_capacity_val = int(ram_capacity.replace('GB', '').strip())
              mb_max_ram_capacity_val = int(mb_max_ram_capacity.replace('GB', '').strip())
              
              if ram_capacity_val > mb_max_ram_capacity_val:
                  issues.append(f"RAM capacity ({ram_capacity}) exceeds maximum supported by motherboard ({mb_max_ram_capacity}).")
                  compatible = False
          except (ValueError, AttributeError):
              pass

  # Case and Motherboard form factor compatibility
  if 'case' in components and 'motherboard' in components:
      case = components['case']
      motherboard = components['motherboard']

      case_form_factors = case.specs.get('supported_form_factors', [])
      mb_form_factor = motherboard.specs.get('form_factor')

      if case_form_factors and mb_form_factor and mb_form_factor not in case_form_factors:
          issues.append(f"Motherboard form factor ({mb_form_factor}) is not supported by the case ({', '.join(case_form_factors)}).")
          compatible = False

  # GPU and Case compatibility (length and width)
  if 'gpu' in components and 'case' in components:
      gpu = components['gpu']
      case = components['case']

      # Check GPU length compatibility
      gpu_length = gpu.specs.get('length')
      case_max_gpu_length = case.specs.get('max_gpu_length')

      if gpu_length and case_max_gpu_length:
          try:
              gpu_length_val = float(gpu_length)
              case_max_gpu_length_val = float(case_max_gpu_length)
              
              if gpu_length_val > case_max_gpu_length_val:
                  issues.append(f"GPU length ({gpu_length}mm) exceeds the maximum supported by the case ({case_max_gpu_length}mm).")
                  compatible = False
          except (ValueError, TypeError):
              pass
      
      # Check GPU width/height compatibility for clearance
      gpu_width = gpu.specs.get('width') or gpu.specs.get('height')
      case_max_gpu_width = case.specs.get('max_gpu_width') or case.specs.get('max_gpu_height')
      
      if gpu_width and case_max_gpu_width:
          try:
              gpu_width_val = float(gpu_width)
              case_max_gpu_width_val = float(case_max_gpu_width)
              
              if gpu_width_val > case_max_gpu_width_val:
                  issues.append(f"GPU width/height ({gpu_width}mm) exceeds the maximum clearance supported by the case ({case_max_gpu_width}mm).")
                  compatible = False
          except (ValueError, TypeError):
              pass

  # AIO Cooler and Case compatibility
  if any(k for k in components if k == 'cooling') and 'case' in components:
      cooling = components.get('cooling')
      case = components['case']
      
      cooling_type = cooling.specs.get('type') if cooling else None
      
      if cooling_type and cooling_type.lower() == 'aio':
          # Check AIO radiator size compatibility with case
          aio_size = cooling.specs.get('radiator_size')
          case_supported_radiators = case.specs.get('supported_radiator_sizes', [])
          
          if aio_size and case_supported_radiators:
              if aio_size not in case_supported_radiators:
                  issues.append(f"AIO radiator size ({aio_size}) is not supported by the case. Supported sizes: {', '.join(case_supported_radiators)}.")
                  compatible = False

  # Power supply wattage check
  if 'psu' in components:
      psu = components['psu']
      psu_wattage = psu.specs.get('wattage')

      if psu_wattage:
          required_wattage = calculate_power_consumption(components)
          
          try:
              psu_wattage_val = int(psu_wattage)
              
              if psu_wattage_val < required_wattage:
                  issues.append(f"Power supply wattage ({psu_wattage}W) is not sufficient for the estimated power consumption ({required_wattage}W).")
                  compatible = False
              elif psu_wattage_val < required_wattage * 1.2:  # 20% headroom for power fluctuations
                  issues.append(f"Power supply wattage ({psu_wattage}W) is close to the estimated power consumption ({required_wattage}W). Consider a higher wattage PSU for stability.")
          except (ValueError, TypeError):
              pass
              
      # PSU form factor compatibility with case
      psu_form_factor = psu.specs.get('form_factor')
      
      if 'case' in components:
          case = components['case']
          case_psu_form_factors = case.specs.get('supported_psu_form_factors', [])
          
          if psu_form_factor and case_psu_form_factors and psu_form_factor not in case_psu_form_factors:
              issues.append(f"PSU form factor ({psu_form_factor}) is not compatible with the case. Supported PSU types: {', '.join(case_psu_form_factors)}.")
              compatible = False

  # Check for required but missing components
  essential_components = ['cpu', 'motherboard', 'ram', 'storage', 'psu', 'case']
  missing_components = [comp for comp in essential_components if comp not in components]
  
  if missing_components and len(components) >= 2:  # Only show warning if user has started selecting components
      issues.append(f"Missing essential components: {', '.join(missing_components)}. Complete your build for a functional PC.")

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

      try:
          if cpu_tdp:
              if isinstance(cpu_tdp, str):
                  # Handle cases where TDP is stored as a string
                  cpu_tdp = cpu_tdp.replace('W', '').strip()
              total_wattage += int(float(cpu_tdp))
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
      except (ValueError, TypeError, AttributeError):
          # Fallback if we cannot parse the TDP
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

      try:
          if gpu_tdp:
              if isinstance(gpu_tdp, str):
                  # Handle cases where TDP is stored as a string
                  gpu_tdp = gpu_tdp.replace('W', '').strip()
              total_wattage += int(float(gpu_tdp))
          else:
              # Default values based on category (newer GPUs included)
              gpu_name = gpu.name.lower()
              # NVIDIA RTX 40 series
              if 'rtx 4090' in gpu_name:
                  total_wattage += 450
              elif 'rtx 4080' in gpu_name:
                  total_wattage += 350
              elif 'rtx 4070' in gpu_name:
                  total_wattage += 285
              elif 'rtx 4060' in gpu_name:
                  total_wattage += 170
              # NVIDIA RTX 30 series
              elif 'rtx 3090' in gpu_name:
                  total_wattage += 350
              elif 'rtx 3080' in gpu_name:
                  total_wattage += 320
              elif 'rtx 3070' in gpu_name:
                  total_wattage += 220
              elif 'rtx 3060' in gpu_name:
                  total_wattage += 170
              # AMD RX 6000 and 7000 series
              elif 'rx 7900' in gpu_name:
                  total_wattage += 355
              elif 'rx 7800' in gpu_name:
                  total_wattage += 285
              elif 'rx 7700' in gpu_name:
                  total_wattage += 245
              elif 'rx 6900' in gpu_name:
                  total_wattage += 300
              elif 'rx 6800' in gpu_name:
                  total_wattage += 250
              elif 'rx 6700' in gpu_name:
                  total_wattage += 200
              elif 'rx 6600' in gpu_name:
                  total_wattage += 130
              else:
                  total_wattage += 150  # Default for unknown/older GPUs
      except (ValueError, TypeError, AttributeError):
          # Fallback for any parsing errors
          total_wattage += 180  # Safe middle value for unknown GPUs

  # RAM power consumption
  if 'ram' in components:
      # Approximate RAM power usage based on typical values
      ram = components['ram']
      ram_capacity = ram.specs.get('capacity')
      ram_type = ram.specs.get('type', '').lower()

      try:
          if ram_capacity:
              if isinstance(ram_capacity, str):
                  # Extract numeric value from string like "32GB"
                  ram_capacity = ram_capacity.replace('GB', '').strip()
              
              ram_capacity_val = int(float(ram_capacity))
              
              # DDR5 draws more power than DDR4
              if ram_type and 'ddr5' in ram_type:
                  # Estimate about 4W per 8GB for DDR5
                  total_wattage += int(ram_capacity_val / 8 * 4)
              else:
                  # Estimate about 3W per 8GB for DDR4 and older
                  total_wattage += int(ram_capacity_val / 8 * 3)
          else:
              # Default value if we can't determine
              total_wattage += 8
      except (ValueError, TypeError, AttributeError):
          # Fallback for any parsing errors
          total_wattage += 8

  # Storage power consumption (handle multiple storage devices)
  storage_wattage = 0
  
  for category in components:
      if category == 'storage' or category in ['nvme', 'ssd', 'hdd']:
          storage = components[category]
          storage_type = storage.specs.get('type', '').lower() if hasattr(storage, 'specs') else ''
          
          # Determine storage type from category if not in specs
          if not storage_type and category in ['nvme', 'ssd', 'hdd']:
              storage_type = category
          
          try:
              if storage_type:
                  if 'hdd' in storage_type:
                      storage_wattage += 7  # HDDs consume more power
                  elif 'nvme' in storage_type:
                      storage_wattage += 4  # NVMe can draw more power when active
                  elif 'ssd' in storage_type or 'sata' in storage_type:
                      storage_wattage += 3  # SATA SSDs are efficient
                  else:
                      storage_wattage += 5  # Unknown storage type
              else:
                  # Try to guess from the name
                  storage_name = storage.name.lower() if hasattr(storage, 'name') else ''
                  if 'hdd' in storage_name or 'hard drive' in storage_name:
                      storage_wattage += 7
                  elif 'nvme' in storage_name or 'm.2' in storage_name:
                      storage_wattage += 4
                  elif 'ssd' in storage_name:
                      storage_wattage += 3
                  else:
                      storage_wattage += 5
          except (ValueError, TypeError, AttributeError):
              storage_wattage += 5
  
  # Add storage wattage to total
  total_wattage += max(storage_wattage, 5)  # At least 5W for storage

  # Motherboard power consumption (based on form factor and features)
  if 'motherboard' in components:
      motherboard = components['motherboard']
      mb_form_factor = motherboard.specs.get('form_factor', '').lower() if hasattr(motherboard, 'specs') else ''
      
      try:
          if mb_form_factor:
              if 'eatx' in mb_form_factor:
                  total_wattage += 25  # E-ATX boards draw more power
              elif 'atx' in mb_form_factor:
                  total_wattage += 20  # Standard ATX
              elif 'micro' in mb_form_factor or 'matx' in mb_form_factor:
                  total_wattage += 15  # Micro ATX
              elif 'mini' in mb_form_factor or 'itx' in mb_form_factor:
                  total_wattage += 10  # Mini ITX
              else:
                  total_wattage += 20  # Unknown form factor
          else:
              total_wattage += 20  # Default value
      except (ValueError, TypeError, AttributeError):
          total_wattage += 20

  # Cooling power consumption
  if 'cooling' in components:
      cooling = components['cooling']
      cooling_type = cooling.specs.get('type', '').lower() if hasattr(cooling, 'specs') else ''
      
      try:
          if cooling_type:
              if 'air' in cooling_type:
                  # Air coolers vary based on size/fans
                  if hasattr(cooling, 'name'):
                      if '120mm' in cooling.name.lower():
                          total_wattage += 3
                      elif '140mm' in cooling.name.lower():
                          total_wattage += 4
                      elif '240mm' in cooling.name.lower() or 'dual' in cooling.name.lower():
                          total_wattage += 6
                      else:
                          total_wattage += 5
                  else:
                      total_wattage += 5
              elif 'aio' in cooling_type or 'liquid' in cooling_type or 'water' in cooling_type:
                  # AIO power depends on radiator size
                  radiator_size = cooling.specs.get('radiator_size', '')
                  if '360' in str(radiator_size):
                      total_wattage += 15
                  elif '280' in str(radiator_size):
                      total_wattage += 12
                  elif '240' in str(radiator_size):
                      total_wattage += 10
                  elif '120' in str(radiator_size):
                      total_wattage += 7
                  else:
                      total_wattage += 10
              else:
                  total_wattage += 8
          else:
              # Try to determine from name
              if hasattr(cooling, 'name'):
                  cooling_name = cooling.name.lower()
                  if 'aio' in cooling_name or 'liquid' in cooling_name or 'water' in cooling_name:
                      total_wattage += 10
                  else:
                      total_wattage += 5
              else:
                  total_wattage += 8
      except (ValueError, TypeError, AttributeError):
          total_wattage += 8

  # Case fans power consumption
  if 'case' in components:
      case = components['case']
      case_fans = case.specs.get('included_fans')
      
      try:
          if case_fans and isinstance(case_fans, int):
              # Estimate 2W per fan
              total_wattage += case_fans * 2
          elif case_fans and isinstance(case_fans, str) and case_fans.isdigit():
              total_wattage += int(case_fans) * 2
          else:
              # Assume 2 fans if not specified
              total_wattage += 4
      except (ValueError, TypeError, AttributeError):
          total_wattage += 4

  # Add power for peripherals and other components
  # USB devices, RGB lighting, extra fans, etc.
  total_wattage += 30

  return total_wattage
