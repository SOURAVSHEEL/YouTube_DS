"""
Helper module for managing YouTube channel IDs
"""

# Predefined Data Science/ML/Programming Channel IDs
DATA_SCIENCE_CHANNELS = {
    'Krish Naik': 'UCNU_lfiiWBdtULKOw6X0Dig',
    'Data Professor': 'UCh3RpsDV8pS_fXJ6NBX4fhQ',
    'CodeWithHarry': 'UCeVMnSShP_Iviwkknt83cww',
    '3Blue1Brown': 'UCYO_jab_esuFRV4b17AJtAw',
    'StatQuest': 'UCtYLUTtgS3k1Fg4y5tAhLbw',
    'sentdex': 'UCfzlCWGWYyIQ0aLC5w48gBQ',
    'CS Dojo': 'UCxX9wt5FWQUAAz4UrysqK9A',
    'Corey Schafer': 'UCCezIgC97PvUuR4_gbFUs5g',
    'Two Minute Papers': 'UCbfYPyITQ-7l4upoX8nvctg',
    'Simplilearn': 'UCsvqVGtbbyHaMoevxPAq9Fg',
    'edureka!': 'UCkw4JCwteGrDHIsyIIKo4tQ',
    'Joma Tech': 'UCV0qA-eDDICsRR9rPcnG7tw',
    'Ken Jee': 'UCiT9RITQ9PW6BhXK0y2jaeg',
    'Tech With Tim': 'UC4JX40jDee_tINbkjycV4Sg',
    'Data School': 'UCnVzApLJE2ljPZSeQylSEyg'
}

def get_all_channel_ids():
    """Return list of all predefined channel IDs"""
    return list(DATA_SCIENCE_CHANNELS.values())

def get_channel_name_by_id(channel_id):
    """Get channel name by ID"""
    for name, id in DATA_SCIENCE_CHANNELS.items():
        if id == channel_id:
            return name
    return "Unknown Channel"

def search_channel_by_name(name):
    """Search for channel ID by name"""
    name_lower = name.lower()
    for channel_name, channel_id in DATA_SCIENCE_CHANNELS.items():
        if name_lower in channel_name.lower():
            return channel_id
    return None
