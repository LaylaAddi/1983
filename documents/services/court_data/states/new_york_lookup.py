# documents/services/court_data/states/new_york_lookup.py
"""
New York state-specific court lookup service
"""

from typing import Dict
from .base_state_lookup import BaseStateLookup

class NewYorkStateLookup(BaseStateLookup):
    """New York federal district court lookup service"""
    
    def _load_districts(self) -> Dict:
        """Load New York federal district court data"""
        return {
            'name': 'New York',
            'districts': {
                'Southern District of New York': {
                    'divisions': ['Manhattan', 'White Plains'],
                    'counties': ['New York', 'Bronx', 'Westchester', 'Rockland', 'Putnam', 'Orange', 'Dutchess', 'Sullivan'],
                    'major_cities': ['Manhattan', 'New York', 'Bronx', 'Yonkers', 'White Plains', 'New Rochelle', 'Mount Vernon', 'Newburgh', 'Poughkeepsie'],
                    'geographic_region': 'south'
                },
                'Eastern District of New York': {
                    'divisions': ['Brooklyn', 'Central Islip'],
                    'counties': ['Kings', 'Queens', 'Richmond', 'Nassau', 'Suffolk'],
                    'major_cities': ['Brooklyn', 'Queens', 'Staten Island', 'Hempstead', 'Huntington', 'Babylon', 'Islip'],
                    'geographic_region': 'east'
                },
                'Northern District of New York': {
                    'divisions': ['Albany', 'Syracuse', 'Utica', 'Binghamton', 'Watertown'],
                    'counties': ['Albany', 'Broome', 'Cayuga', 'Chenango', 'Clinton', 'Columbia', 'Cortland', 'Delaware', 'Essex', 'Franklin', 'Fulton', 'Greene', 'Hamilton', 'Herkimer', 'Jefferson', 'Lewis', 'Madison', 'Montgomery', 'Oneida', 'Onondaga', 'Oswego', 'Otsego', 'Rensselaer', 'St. Lawrence', 'Saratoga', 'Schenectady', 'Schoharie', 'Tioga', 'Tompkins', 'Warren', 'Washington'],
                    'major_cities': ['Albany', 'Syracuse', 'Utica', 'Binghamton', 'Watertown', 'Ithaca', 'Cortland', 'Auburn', 'Rome', 'Plattsburgh', 'Troy', 'Schenectady'],
                    'geographic_region': 'north'
                },
                'Western District of New York': {
                    'divisions': ['Buffalo', 'Rochester'],
                    'counties': ['Allegany', 'Cattaraugus', 'Chautauqua', 'Chemung', 'Erie', 'Genesee', 'Livingston', 'Monroe', 'Niagara', 'Ontario', 'Orleans', 'Schuyler', 'Seneca', 'Steuben', 'Wayne', 'Wyoming', 'Yates'],
                    'major_cities': ['Buffalo', 'Rochester', 'Elmira', 'Olean', 'Jamestown', 'Batavia', 'Geneseo', 'Hornell', 'Lockport', 'Niagara Falls', 'Alfred'],
                    'geographic_region': 'west'
                }
            }
        }
    
    def _load_city_mappings(self) -> Dict:
        """Load New York city-to-district mappings"""
        return {
            # Western District cities
            'Alfred': ('Western District of New York', 'Buffalo'),
            'Buffalo': ('Western District of New York', 'Buffalo'),
            'Rochester': ('Western District of New York', 'Rochester'),
            'Elmira': ('Western District of New York', 'Rochester'),
            'Olean': ('Western District of New York', 'Buffalo'),
            'Jamestown': ('Western District of New York', 'Buffalo'),
            'Batavia': ('Western District of New York', 'Rochester'),
            'Geneseo': ('Western District of New York', 'Rochester'),
            'Hornell': ('Western District of New York', 'Rochester'),
            'Lockport': ('Western District of New York', 'Buffalo'),
            'Niagara Falls': ('Western District of New York', 'Buffalo'),
            'Wellsville': ('Western District of New York', 'Buffalo'),
            'Cuba': ('Western District of New York', 'Buffalo'),
            'Bath': ('Western District of New York', 'Rochester'),
            'Corning': ('Western District of New York', 'Rochester'),
            'Salamanca': ('Western District of New York', 'Buffalo'),
            'Dunkirk': ('Western District of New York', 'Buffalo'),
            'Fredonia': ('Western District of New York', 'Buffalo'),
            'North Tonawanda': ('Western District of New York', 'Buffalo'),
            'Canandaigua': ('Western District of New York', 'Rochester'),
            'Geneva': ('Western District of New York', 'Rochester'),
            'Penn Yan': ('Western District of New York', 'Rochester'),
            'Watkins Glen': ('Western District of New York', 'Rochester'),
            
            # Northern District cities
            'Albany': ('Northern District of New York', 'Albany'),
            'Syracuse': ('Northern District of New York', 'Syracuse'),
            'Utica': ('Northern District of New York', 'Utica'),
            'Binghamton': ('Northern District of New York', 'Binghamton'),
            'Watertown': ('Northern District of New York', 'Watertown'),
            'Ithaca': ('Northern District of New York', 'Binghamton'),
            'Cortland': ('Northern District of New York', 'Syracuse'),
            'Auburn': ('Northern District of New York', 'Syracuse'),
            'Rome': ('Northern District of New York', 'Utica'),
            'Plattsburgh': ('Northern District of New York', 'Watertown'),
            'Troy': ('Northern District of New York', 'Albany'),
            'Schenectady': ('Northern District of New York', 'Albany'),
            'Oneonta': ('Northern District of New York', 'Binghamton'),
            'Oswego': ('Northern District of New York', 'Syracuse'),
            'Fulton': ('Northern District of New York', 'Syracuse'),
            'Glens Falls': ('Northern District of New York', 'Albany'),
            'Saratoga Springs': ('Northern District of New York', 'Albany'),
            'Amsterdam': ('Northern District of New York', 'Albany'),
            'Johnstown': ('Northern District of New York', 'Albany'),
            'Massena': ('Northern District of New York', 'Watertown'),
            'Potsdam': ('Northern District of New York', 'Watertown'),
            'Canton': ('Northern District of New York', 'Watertown'),
            
            # Eastern District cities
            'Brooklyn': ('Eastern District of New York', 'Brooklyn'),
            'Queens': ('Eastern District of New York', 'Brooklyn'),
            'Staten Island': ('Eastern District of New York', 'Brooklyn'),
            'Central Islip': ('Eastern District of New York', 'Central Islip'),
            'Hempstead': ('Eastern District of New York', 'Central Islip'),
            'Huntington': ('Eastern District of New York', 'Central Islip'),
            'Babylon': ('Eastern District of New York', 'Central Islip'),
            'Islip': ('Eastern District of New York', 'Central Islip'),
            'Riverhead': ('Eastern District of New York', 'Central Islip'),
            'Patchogue': ('Eastern District of New York', 'Central Islip'),
            'Bay Shore': ('Eastern District of New York', 'Central Islip'),
            'Brentwood': ('Eastern District of New York', 'Central Islip'),
            'Levittown': ('Eastern District of New York', 'Central Islip'),
            'Freeport': ('Eastern District of New York', 'Central Islip'),
            'Long Beach': ('Eastern District of New York', 'Central Islip'),
            'Glen Cove': ('Eastern District of New York', 'Central Islip'),
            
            # Southern District cities
            'Manhattan': ('Southern District of New York', 'Manhattan'),
            'New York': ('Southern District of New York', 'Manhattan'),
            'Bronx': ('Southern District of New York', 'Manhattan'),
            'White Plains': ('Southern District of New York', 'White Plains'),
            'Yonkers': ('Southern District of New York', 'White Plains'),
            'New Rochelle': ('Southern District of New York', 'White Plains'),
            'Mount Vernon': ('Southern District of New York', 'White Plains'),
            'Newburgh': ('Southern District of New York', 'White Plains'),
            'Poughkeepsie': ('Southern District of New York', 'White Plains'),
            'Scarsdale': ('Southern District of New York', 'White Plains'),
            'Mamaroneck': ('Southern District of New York', 'White Plains'),
            'Rye': ('Southern District of New York', 'White Plains'),
            'Tarrytown': ('Southern District of New York', 'White Plains'),
            'Peekskill': ('Southern District of New York', 'White Plains'),
            'Middletown': ('Southern District of New York', 'White Plains'),
            'Kingston': ('Southern District of New York', 'White Plains'),
            'Spring Valley': ('Southern District of New York', 'White Plains'),
            'Nyack': ('Southern District of New York', 'White Plains'),
        }
    
    def _load_county_mappings(self) -> Dict:
        """Load New York county-to-district mappings"""
        return {
            # Western District counties
            'Allegany': ('Western District of New York', 'Buffalo'),
            'Cattaraugus': ('Western District of New York', 'Buffalo'),
            'Chautauqua': ('Western District of New York', 'Buffalo'),
            'Chemung': ('Western District of New York', 'Rochester'),
            'Erie': ('Western District of New York', 'Buffalo'),
            'Genesee': ('Western District of New York', 'Rochester'),
            'Livingston': ('Western District of New York', 'Rochester'),
            'Monroe': ('Western District of New York', 'Rochester'),
            'Niagara': ('Western District of New York', 'Buffalo'),
            'Ontario': ('Western District of New York', 'Rochester'),
            'Orleans': ('Western District of New York', 'Rochester'),
            'Schuyler': ('Western District of New York', 'Rochester'),
            'Seneca': ('Western District of New York', 'Rochester'),
            'Steuben': ('Western District of New York', 'Rochester'),
            'Wayne': ('Western District of New York', 'Rochester'),
            'Wyoming': ('Western District of New York', 'Buffalo'),
            'Yates': ('Western District of New York', 'Rochester'),
            
            # Northern District counties
            'Albany': ('Northern District of New York', 'Albany'),
            'Broome': ('Northern District of New York', 'Binghamton'),
            'Cayuga': ('Northern District of New York', 'Syracuse'),
            'Chenango': ('Northern District of New York', 'Binghamton'),
            'Clinton': ('Northern District of New York', 'Watertown'),
            'Columbia': ('Northern District of New York', 'Albany'),
            'Cortland': ('Northern District of New York', 'Syracuse'),
            'Delaware': ('Northern District of New York', 'Binghamton'),
            'Essex': ('Northern District of New York', 'Watertown'),
            'Franklin': ('Northern District of New York', 'Watertown'),
            'Fulton': ('Northern District of New York', 'Utica'),
            'Greene': ('Northern District of New York', 'Albany'),
            'Hamilton': ('Northern District of New York', 'Utica'),
            'Herkimer': ('Northern District of New York', 'Utica'),
            'Jefferson': ('Northern District of New York', 'Watertown'),
            'Lewis': ('Northern District of New York', 'Utica'),
            'Madison': ('Northern District of New York', 'Syracuse'),
            'Montgomery': ('Northern District of New York', 'Utica'),
            'Oneida': ('Northern District of New York', 'Utica'),
            'Onondaga': ('Northern District of New York', 'Syracuse'),
            'Oswego': ('Northern District of New York', 'Syracuse'),
            'Otsego': ('Northern District of New York', 'Binghamton'),
            'Rensselaer': ('Northern District of New York', 'Albany'),
            'St. Lawrence': ('Northern District of New York', 'Watertown'),
            'Saratoga': ('Northern District of New York', 'Albany'),
            'Schenectady': ('Northern District of New York', 'Albany'),
            'Schoharie': ('Northern District of New York', 'Binghamton'),
            'Tioga': ('Northern District of New York', 'Binghamton'),
            'Tompkins': ('Northern District of New York', 'Binghamton'),
            'Warren': ('Northern District of New York', 'Albany'),
            'Washington': ('Northern District of New York', 'Albany'),
            
            # Eastern District counties
            'Kings': ('Eastern District of New York', 'Brooklyn'),
            'Queens': ('Eastern District of New York', 'Brooklyn'),
            'Richmond': ('Eastern District of New York', 'Brooklyn'),
            'Nassau': ('Eastern District of New York', 'Central Islip'),
            'Suffolk': ('Eastern District of New York', 'Central Islip'),
            
            # Southern District counties
            'New York': ('Southern District of New York', 'Manhattan'),
            'Bronx': ('Southern District of New York', 'Manhattan'),
            'Westchester': ('Southern District of New York', 'White Plains'),
            'Rockland': ('Southern District of New York', 'White Plains'),
            'Putnam': ('Southern District of New York', 'White Plains'),
            'Orange': ('Southern District of New York', 'White Plains'),
            'Dutchess': ('Southern District of New York', 'White Plains'),
            'Sullivan': ('Southern District of New York', 'White Plains'),
        }
    
    def _load_geographic_patterns(self) -> Dict:
        """Load New York geographic patterns for fallback matching"""
        return {
            'Western District of New York': {
                'keywords': ['west', 'buffalo', 'rochester', 'finger', 'lake', 'allegany', 'cattaraugus'],
                'default_division': 'Buffalo'
            },
            'Northern District of New York': {
                'keywords': ['north', 'albany', 'syracuse', 'utica', 'adirondack', 'capital', 'central'],
                'default_division': 'Albany'
            },
            'Eastern District of New York': {
                'keywords': ['long', 'island', 'brooklyn', 'queens', 'suffolk', 'nassau', 'islip'],
                'default_division': 'Brooklyn'
            },
            'Southern District of New York': {
                'keywords': ['manhattan', 'bronx', 'westchester', 'nyc', 'new york city', 'metro'],
                'default_division': 'Manhattan'
            }
        }
    
    def _get_default_district(self):
        """Default to Southern District for New York (most common)"""
        return ('Southern District of New York', 'Manhattan')