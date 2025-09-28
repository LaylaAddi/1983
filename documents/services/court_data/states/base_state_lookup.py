# documents/services/court_data/states/base_state_lookup.py
"""
Robust base class for state-specific court lookup services
Designed to handle all 50 states with various complexity levels
"""

from typing import Dict, Optional, List, Tuple
from abc import ABC, abstractmethod

class BaseStateLookup(ABC):
    """Base class that all state-specific court lookup services inherit from"""
    
    def __init__(self):
        self.districts = self._load_districts()
        self.city_mappings = self._load_city_mappings()
        self.county_mappings = self._load_county_mappings()
        self.geographic_patterns = self._load_geographic_patterns()
    
    @abstractmethod
    def _load_districts(self) -> Dict:
        """Load district court data for this state"""
        pass
    
    def _load_city_mappings(self) -> Dict:
        """Load direct city-to-district mappings"""
        return {}
    
    def _load_county_mappings(self) -> Dict:
        """Load county-to-district mappings"""
        return {}
    
    def _load_geographic_patterns(self) -> Dict:
        """Load geographic keyword patterns for fallback matching"""
        return {}
    
    def lookup_court(self, city: str, county: Optional[str] = None) -> Dict:
        """Main lookup method with multiple fallback strategies"""
        city = city.strip().title()
        county = county.strip().title() if county else None
        
        # Strategy 1: Exact city match
        result = self._try_city_match(city)
        if result:
            return self._build_result(result[0], result[1], 'high')
        
        # Strategy 2: County match
        if county:
            result = self._try_county_match(county)
            if result:
                return self._build_result(result[0], result[1], 'high')
        
        # Strategy 3: Geographic pattern match
        result = self._try_geographic_match(city)
        if result:
            return self._build_result(result[0], result[1], 'medium')
        
        # Strategy 4: Default fallback
        result = self._get_default_district()
        return self._build_result(result[0], result[1], 'low')
    
    def _try_city_match(self, city: str) -> Optional[Tuple[str, str]]:
        """Try exact city name match"""
        return self.city_mappings.get(city)
    
    def _try_county_match(self, county: str) -> Optional[Tuple[str, str]]:
        """Try county name match"""
        result = self.county_mappings.get(county)
        if result:
            return result
        
        county_base = county.replace(' County', '')
        return self.county_mappings.get(county_base)
    
    def _try_geographic_match(self, city: str) -> Optional[Tuple[str, str]]:
        """Try geographic pattern matching"""
        city_lower = city.lower()
        
        for district_name, pattern_info in self.geographic_patterns.items():
            keywords = pattern_info.get('keywords', [])
            if any(keyword in city_lower for keyword in keywords):
                division = pattern_info.get('default_division')
                return (district_name, division)
        
        return None
    
    def _get_default_district(self) -> Tuple[str, str]:
        """Get default district when all else fails"""
        districts = list(self.districts['districts'].keys())
        first_district = districts[0]
        first_division = self.districts['districts'][first_district]['divisions'][0]
        return (first_district, first_division)
    
    def _build_result(self, district: str, division: str, confidence: str) -> Dict:
        """Build the standardized result dictionary"""
        return {
            'success': True,
            'district': district,
            'division': division,
            'state_name': self.districts['name'],
            'confidence': confidence,
            'formatted_court': self._format_court_name(district, division)
        }
    
    def _format_court_name(self, district: str, division: str) -> str:
        """Format the court name for display in legal documents"""
        return f"UNITED STATES DISTRICT COURT\n{district.upper()}\n{division.upper()} DIVISION"
    
    def get_all_districts(self) -> List[Dict]:
        """Get all districts for this state"""
        districts = []
        for district_name, district_info in self.districts['districts'].items():
            districts.append({
                'name': district_name,
                'divisions': district_info['divisions'],
                'counties': district_info.get('counties', []),
                'major_cities': district_info.get('major_cities', [])
            })
        return districts
    