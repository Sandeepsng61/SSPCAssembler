"""
This file contains location data for India
"""

# Indian states and their cities
STATES_CITIES = {
    "andhra_pradesh": {
        "name": "Andhra Pradesh",
        "cities": [
            {"id": "ap_vizag", "name": "Visakhapatnam"},
            {"id": "ap_vijayawada", "name": "Vijayawada"},
            {"id": "ap_guntur", "name": "Guntur"},
            {"id": "ap_nellore", "name": "Nellore"},
            {"id": "ap_kurnool", "name": "Kurnool"}
        ],
        "pincodes": {
            "ap_vizag": {"ranges": ["530001-530018", "530020-530028"], "names": ["Vizag Main", "Vizag East", "Vizag West"]},
            "ap_vijayawada": {"ranges": ["520001-520012"], "names": ["Vijayawada Central", "Vijayawada North", "Vijayawada South"]},
            "ap_guntur": {"ranges": ["522001-522020"], "names": ["Guntur Main", "Guntur East", "Guntur West"]},
            "ap_nellore": {"ranges": ["524001-524005"], "names": ["Nellore Main", "Nellore Town"]},
            "ap_kurnool": {"ranges": ["518001-518006"], "names": ["Kurnool Main", "Kurnool Town"]}
        }
    },
    "telangana": {
        "name": "Telangana",
        "cities": [
            {"id": "ts_hyderabad", "name": "Hyderabad"},
            {"id": "ts_warangal", "name": "Warangal"},
            {"id": "ts_nizamabad", "name": "Nizamabad"},
            {"id": "ts_karimnagar", "name": "Karimnagar"},
            {"id": "ts_khammam", "name": "Khammam"}
        ],
        "pincodes": {
            "ts_hyderabad": {"ranges": ["500001-500096"], "names": ["Hyderabad Central", "Secunderabad", "Hitech City", "Gachibowli"]},
            "ts_warangal": {"ranges": ["506001-506013"], "names": ["Warangal Main", "Hanamkonda"]},
            "ts_nizamabad": {"ranges": ["503001-503003"], "names": ["Nizamabad Main"]},
            "ts_karimnagar": {"ranges": ["505001-505004"], "names": ["Karimnagar Main"]},
            "ts_khammam": {"ranges": ["507001-507003"], "names": ["Khammam Main"]}
        }
    },
    "maharashtra": {
        "name": "Maharashtra",
        "cities": [
            {"id": "mh_mumbai", "name": "Mumbai"},
            {"id": "mh_pune", "name": "Pune"},
            {"id": "mh_nagpur", "name": "Nagpur"},
            {"id": "mh_nashik", "name": "Nashik"},
            {"id": "mh_aurangabad", "name": "Aurangabad"}
        ],
        "pincodes": {
            "mh_mumbai": {"ranges": ["400001-400104"], "names": ["Mumbai Central", "Andheri", "Bandra", "Borivali", "Dadar"]},
            "mh_pune": {"ranges": ["411001-411056"], "names": ["Pune Central", "Kothrud", "Hadapsar", "Hinjewadi"]},
            "mh_nagpur": {"ranges": ["440001-440036"], "names": ["Nagpur Central", "Nagpur West"]},
            "mh_nashik": {"ranges": ["422001-422013"], "names": ["Nashik Main", "Nashik Road"]},
            "mh_aurangabad": {"ranges": ["431001-431005"], "names": ["Aurangabad Main"]}
        }
    },
    "tamil_nadu": {
        "name": "Tamil Nadu",
        "cities": [
            {"id": "tn_chennai", "name": "Chennai"},
            {"id": "tn_coimbatore", "name": "Coimbatore"},
            {"id": "tn_madurai", "name": "Madurai"},
            {"id": "tn_salem", "name": "Salem"},
            {"id": "tn_trichy", "name": "Tiruchirappalli"}
        ],
        "pincodes": {
            "tn_chennai": {"ranges": ["600001-600119"], "names": ["Chennai Central", "Adyar", "Anna Nagar", "T Nagar", "Velachery"]},
            "tn_coimbatore": {"ranges": ["641001-641045"], "names": ["Coimbatore Central", "RS Puram", "Peelamedu"]},
            "tn_madurai": {"ranges": ["625001-625020"], "names": ["Madurai Main", "Madurai North", "Madurai South"]},
            "tn_salem": {"ranges": ["636001-636016"], "names": ["Salem Main", "Salem Junction"]},
            "tn_trichy": {"ranges": ["620001-620020"], "names": ["Trichy Main", "Srirangam"]}
        }
    },
    "karnataka": {
        "name": "Karnataka",
        "cities": [
            {"id": "ka_bangalore", "name": "Bengaluru"},
            {"id": "ka_mysore", "name": "Mysuru"},
            {"id": "ka_hubli", "name": "Hubli-Dharwad"},
            {"id": "ka_mangalore", "name": "Mangaluru"},
            {"id": "ka_belgaum", "name": "Belagavi"}
        ],
        "pincodes": {
            "ka_bangalore": {"ranges": ["560001-560103"], "names": ["Bangalore Central", "Whitefield", "Electronic City", "Jayanagar", "Koramangala"]},
            "ka_mysore": {"ranges": ["570001-570029"], "names": ["Mysore Main", "Mysore North", "Mysore South"]},
            "ka_hubli": {"ranges": ["580001-580032"], "names": ["Hubli Main", "Dharwad"]},
            "ka_mangalore": {"ranges": ["575001-575015"], "names": ["Mangalore Main", "Mangalore Port"]},
            "ka_belgaum": {"ranges": ["590001-590016"], "names": ["Belgaum Main", "Belgaum Camp"]}
        }
    },
    "delhi": {
        "name": "Delhi",
        "cities": [
            {"id": "dl_new_delhi", "name": "New Delhi"},
            {"id": "dl_north_delhi", "name": "North Delhi"},
            {"id": "dl_south_delhi", "name": "South Delhi"},
            {"id": "dl_east_delhi", "name": "East Delhi"},
            {"id": "dl_west_delhi", "name": "West Delhi"}
        ],
        "pincodes": {
            "dl_new_delhi": {"ranges": ["110001-110024"], "names": ["Connaught Place", "Parliament Street", "India Gate", "Chanakyapuri"]},
            "dl_north_delhi": {"ranges": ["110031-110040"], "names": ["Model Town", "Civil Lines", "Delhi University"]},
            "dl_south_delhi": {"ranges": ["110025-110030", "110049-110080"], "names": ["Green Park", "Saket", "Defence Colony", "Hauz Khas"]},
            "dl_east_delhi": {"ranges": ["110090-110099"], "names": ["Shahdara", "Patparganj", "Mayur Vihar"]},
            "dl_west_delhi": {"ranges": ["110041-110048"], "names": ["Rajouri Garden", "Janakpuri", "Dwarka"]}
        }
    }
}

# List of all Indian states for dropdown
STATES = [
    # States with detailed city data from STATES_CITIES
    {"id": state_id, "name": state_data["name"]}
    for state_id, state_data in STATES_CITIES.items()
]

# Add all other Indian states and union territories
additional_states = [
    {"id": "arunachal_pradesh", "name": "Arunachal Pradesh"},
    {"id": "assam", "name": "Assam"},
    {"id": "bihar", "name": "Bihar"},
    {"id": "chhattisgarh", "name": "Chhattisgarh"},
    {"id": "goa", "name": "Goa"},
    {"id": "gujarat", "name": "Gujarat"},
    {"id": "haryana", "name": "Haryana"},
    {"id": "himachal_pradesh", "name": "Himachal Pradesh"},
    {"id": "jharkhand", "name": "Jharkhand"},
    {"id": "karnataka", "name": "Karnataka"},
    {"id": "kerala", "name": "Kerala"},
    {"id": "madhya_pradesh", "name": "Madhya Pradesh"},
    {"id": "maharashtra", "name": "Maharashtra"},
    {"id": "manipur", "name": "Manipur"},
    {"id": "meghalaya", "name": "Meghalaya"},
    {"id": "mizoram", "name": "Mizoram"},
    {"id": "nagaland", "name": "Nagaland"},
    {"id": "odisha", "name": "Odisha"},
    {"id": "punjab", "name": "Punjab"},
    {"id": "rajasthan", "name": "Rajasthan"},
    {"id": "sikkim", "name": "Sikkim"},
    {"id": "tamil_nadu", "name": "Tamil Nadu"},
    {"id": "tripura", "name": "Tripura"},
    {"id": "uttarakhand", "name": "Uttarakhand"},
    {"id": "uttar_pradesh", "name": "Uttar Pradesh"},
    {"id": "west_bengal", "name": "West Bengal"},
    {"id": "delhi", "name": "Delhi"},
    {"id": "jammu_kashmir", "name": "Jammu & Kashmir"},
    {"id": "ladakh", "name": "Ladakh"},
    {"id": "puducherry", "name": "Puducherry"},
    {"id": "andaman_nicobar", "name": "Andaman & Nicobar Islands"},
    {"id": "chandigarh", "name": "Chandigarh"},
    {"id": "dadra_nagar_haveli", "name": "Dadra & Nagar Haveli & Daman & Diu"},
    {"id": "lakshadweep", "name": "Lakshadweep"}
]

# Add only states that aren't already in the list
state_ids = {state["id"] for state in STATES}
for state in additional_states:
    if state["id"] not in state_ids:
        STATES.append(state)

# Sort states alphabetically by name
STATES.sort(key=lambda x: x["name"])

def get_state_name(state_id):
    """Get state name from state ID"""
    # First check in the detailed STATES_CITIES dictionary
    state_data = STATES_CITIES.get(state_id)
    if state_data:
        return state_data.get("name")
    
    # If not found, check in the complete STATES list
    for state in STATES:
        if state["id"] == state_id:
            return state["name"]
    
    return None

def get_cities(state_id):
    """Get cities for a state"""
    state_data = STATES_CITIES.get(state_id)
    if not state_data:
        # For states without detailed city data, return an empty list
        # This is OK since we've changed city to be a text input rather than a dropdown
        return []
    return state_data.get("cities", [])

def get_city_name(state_id, city_id):
    """Get city name from state ID and city ID"""
    state_data = STATES_CITIES.get(state_id)
    if not state_data:
        return None
    
    for city in state_data.get("cities", []):
        if city["id"] == city_id:
            return city["name"]
    return None

def get_pincodes(state_id, city_id):
    """Get pincodes for a city"""
    state_data = STATES_CITIES.get(state_id)
    if not state_data:
        return None
    
    pincode_data = state_data.get("pincodes", {}).get(city_id)
    return pincode_data if pincode_data else None

def get_postoffices(state_id, city_id, pincode=None):
    """Get post offices for a city or a specific pincode"""
    pincode_data = get_pincodes(state_id, city_id)
    if not pincode_data:
        return []
    
    # Return all post offices for the city
    if pincode is None:
        return pincode_data.get("names", [])
    
    # Check if pincode is in any of the ranges
    for pincode_range in pincode_data.get("ranges", []):
        if "-" in pincode_range:
            start, end = pincode_range.split("-")
            if int(start) <= int(pincode) <= int(end):
                return pincode_data.get("names", [])
    
    return []