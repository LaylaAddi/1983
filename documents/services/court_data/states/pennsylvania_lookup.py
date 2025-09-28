# documents/services/court_data/states/pennsylvania_lookup.py
"""
Pennsylvania state-specific court lookup service
"""

from typing import Dict
from .base_state_lookup import BaseStateLookup

class PennsylvaniaStateLookup(BaseStateLookup):
    """Pennsylvania federal district court lookup service"""
    
    def _load_districts(self) -> Dict:
        """Load Pennsylvania federal district court data"""
        return {
            'name': 'Pennsylvania',
            'districts': {
                'Eastern District of Pennsylvania': {
                    'divisions': ['Philadelphia', 'Reading', 'Allentown'],
                    'counties': ['Berks', 'Bucks', 'Chester', 'Delaware', 'Lancaster', 'Lehigh', 'Montgomery', 'Northampton', 'Philadelphia', 'Schuylkill'],
                    'major_cities': ['Philadelphia', 'Reading', 'Allentown', 'Bethlehem', 'Chester', 'Norristown', 'Lancaster', 'Easton'],
                    'geographic_region': 'east'
                },
                'Middle District of Pennsylvania': {
                    'divisions': ['Scranton', 'Wilkes-Barre', 'Williamsport', 'Harrisburg'],
                    'counties': ['Adams', 'Bradford', 'Carbon', 'Centre', 'Clinton', 'Columbia', 'Cumberland', 'Dauphin', 'Franklin', 'Fulton', 'Huntingdon', 'Juniata', 'Lackawanna', 'Lebanon', 'Luzerne', 'Lycoming', 'Mifflin', 'Monroe', 'Montour', 'Northumberland', 'Perry', 'Pike', 'Snyder', 'Sullivan', 'Susquehanna', 'Tioga', 'Union', 'Wayne', 'Wyoming', 'York'],
                    'major_cities': ['Harrisburg', 'Scranton', 'Wilkes-Barre', 'Williamsport', 'York', 'Lebanon', 'State College', 'Hazleton'],
                    'geographic_region': 'central'
                },
                'Western District of Pennsylvania': {
                    'divisions': ['Pittsburgh', 'Erie', 'Johnstown'],
                    'counties': ['Allegheny', 'Armstrong', 'Beaver', 'Bedford', 'Blair', 'Butler', 'Cambria', 'Cameron', 'Clarion', 'Clearfield', 'Crawford', 'Elk', 'Erie', 'Fayette', 'Forest', 'Greene', 'Indiana', 'Jefferson', 'Lawrence', 'McKean', 'Mercer', 'Potter', 'Somerset', 'Venango', 'Warren', 'Washington', 'Westmoreland'],
                    'major_cities': ['Pittsburgh', 'Erie', 'Johnstown', 'Altoona', 'Clarion', 'Oil City', 'Warren', 'Bradford', 'DuBois', 'Indiana', 'Greensburg'],
                    'geographic_region': 'west'
                }
            }
        }
    
    def _load_city_mappings(self) -> Dict:
        """Load Pennsylvania city-to-district mappings"""
        return {
            # Eastern District cities
            'Philadelphia': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Reading': ('Eastern District of Pennsylvania', 'Reading'),
            'Allentown': ('Eastern District of Pennsylvania', 'Allentown'),
            'Bethlehem': ('Eastern District of Pennsylvania', 'Allentown'),
            'Chester': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Norristown': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Lancaster': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Easton': ('Eastern District of Pennsylvania', 'Allentown'),
            'Upper Darby': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Levittown': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Bristol': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'West Chester': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Coatesville': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Pottstown': ('Eastern District of Pennsylvania', 'Reading'),
            'Phoenixville': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'King of Prussia': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Doylestown': ('Eastern District of Pennsylvania', 'Philadelphia'),
            
            # Middle District cities
            'Harrisburg': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Scranton': ('Middle District of Pennsylvania', 'Scranton'),
            'Wilkes-Barre': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'Williamsport': ('Middle District of Pennsylvania', 'Williamsport'),
            'York': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Lebanon': ('Middle District of Pennsylvania', 'Harrisburg'),
            'State College': ('Middle District of Pennsylvania', 'Williamsport'),
            'Hazleton': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'Bloomsburg': ('Middle District of Pennsylvania', 'Williamsport'),
            'Sunbury': ('Middle District of Pennsylvania', 'Williamsport'),
            'Lewistown': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Carlisle': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Chambersburg': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Gettysburg': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Waynesboro': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Jim Thorpe': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'Stroudsburg': ('Middle District of Pennsylvania', 'Scranton'),
            'Pottsville': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            
            # Western District cities
            'Pittsburgh': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Erie': ('Western District of Pennsylvania', 'Erie'),
            'Johnstown': ('Western District of Pennsylvania', 'Johnstown'),
            'Altoona': ('Western District of Pennsylvania', 'Johnstown'),
            'Clarion': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Oil City': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Warren': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Bradford': ('Western District of Pennsylvania', 'Pittsburgh'),
            'DuBois': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Indiana': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Greensburg': ('Western District of Pennsylvania', 'Pittsburgh'),
            'New Castle': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Butler': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Washington': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Uniontown': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Connellsville': ('Western District of Pennsylvania', 'Pittsburgh'),
            'McKeesport': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Monessen': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Jeannette': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Latrobe': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Somerset': ('Western District of Pennsylvania', 'Johnstown'),
            'Bedford': ('Western District of Pennsylvania', 'Johnstown'),
            'Huntingdon': ('Western District of Pennsylvania', 'Johnstown'),
            'Bellefonte': ('Western District of Pennsylvania', 'Johnstown'),
            'Franklin': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Titusville': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Meadville': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Sharon': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Hermitage': ('Western District of Pennsylvania', 'Pittsburgh'),
            'St Marys': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Ridgway': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Clearfield': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Punxsutawney': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Brookville': ('Western District of Pennsylvania', 'Pittsburgh'),
        }
    
    def _load_county_mappings(self) -> Dict:
        """Load Pennsylvania county-to-district mappings"""
        return {
            # Eastern District counties
            'Berks': ('Eastern District of Pennsylvania', 'Reading'),
            'Bucks': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Chester': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Delaware': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Lancaster': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Lehigh': ('Eastern District of Pennsylvania', 'Allentown'),
            'Montgomery': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Northampton': ('Eastern District of Pennsylvania', 'Allentown'),
            'Philadelphia': ('Eastern District of Pennsylvania', 'Philadelphia'),
            'Schuylkill': ('Eastern District of Pennsylvania', 'Reading'),
            
            # Middle District counties
            'Adams': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Bradford': ('Middle District of Pennsylvania', 'Williamsport'),
            'Carbon': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'Centre': ('Middle District of Pennsylvania', 'Williamsport'),
            'Clinton': ('Middle District of Pennsylvania', 'Williamsport'),
            'Columbia': ('Middle District of Pennsylvania', 'Williamsport'),
            'Cumberland': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Dauphin': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Franklin': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Fulton': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Huntingdon': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Juniata': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Lackawanna': ('Middle District of Pennsylvania', 'Scranton'),
            'Lebanon': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Luzerne': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'Lycoming': ('Middle District of Pennsylvania', 'Williamsport'),
            'Mifflin': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Monroe': ('Middle District of Pennsylvania', 'Scranton'),
            'Montour': ('Middle District of Pennsylvania', 'Williamsport'),
            'Northumberland': ('Middle District of Pennsylvania', 'Williamsport'),
            'Perry': ('Middle District of Pennsylvania', 'Harrisburg'),
            'Pike': ('Middle District of Pennsylvania', 'Scranton'),
            'Snyder': ('Middle District of Pennsylvania', 'Williamsport'),
            'Sullivan': ('Middle District of Pennsylvania', 'Williamsport'),
            'Susquehanna': ('Middle District of Pennsylvania', 'Scranton'),
            'Tioga': ('Middle District of Pennsylvania', 'Williamsport'),
            'Union': ('Middle District of Pennsylvania', 'Williamsport'),
            'Wayne': ('Middle District of Pennsylvania', 'Scranton'),
            'Wyoming': ('Middle District of Pennsylvania', 'Wilkes-Barre'),
            'York': ('Middle District of Pennsylvania', 'Harrisburg'),
            
            # Western District counties
            'Allegheny': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Armstrong': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Beaver': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Bedford': ('Western District of Pennsylvania', 'Johnstown'),
            'Blair': ('Western District of Pennsylvania', 'Johnstown'),
            'Butler': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Cambria': ('Western District of Pennsylvania', 'Johnstown'),
            'Cameron': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Clarion': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Clearfield': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Crawford': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Elk': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Erie': ('Western District of Pennsylvania', 'Erie'),
            'Fayette': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Forest': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Greene': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Indiana': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Jefferson': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Lawrence': ('Western District of Pennsylvania', 'Pittsburgh'),
            'McKean': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Mercer': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Potter': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Somerset': ('Western District of Pennsylvania', 'Johnstown'),
            'Venango': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Warren': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Washington': ('Western District of Pennsylvania', 'Pittsburgh'),
            'Westmoreland': ('Western District of Pennsylvania', 'Pittsburgh'),
        }
    
    def _load_geographic_patterns(self) -> Dict:
        """Load Pennsylvania geographic patterns for fallback matching"""
        return {
            'Eastern District of Pennsylvania': {
                'keywords': ['east', 'philadelphia', 'philly', 'reading', 'allentown', 'lehigh', 'delaware', 'chester'],
                'default_division': 'Philadelphia'
            },
            'Middle District of Pennsylvania': {
                'keywords': ['central', 'middle', 'harrisburg', 'scranton', 'wilkes', 'capital', 'anthracite'],
                'default_division': 'Harrisburg'
            },
            'Western District of Pennsylvania': {
                'keywords': ['west', 'pittsburgh', 'erie', 'johnstown', 'allegheny', 'steel', 'coal'],
                'default_division': 'Pittsburgh'
            }
        }
    
    def _get_default_district(self):
        """Default to Eastern District for Pennsylvania (largest population)"""
        return ('Eastern District of Pennsylvania', 'Philadelphia')