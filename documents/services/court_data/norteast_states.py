# documents/services/court_data/northeast_states.py
"""
Federal district court data for Northeastern United States
"""

NORTHEAST_DISTRICTS = {
    'PA': {
        'name': 'Pennsylvania',
        'districts': {
            'Eastern District of Pennsylvania': {
                'divisions': ['Philadelphia', 'Reading', 'Allentown'],
                'counties': ['Berks', 'Bucks', 'Chester', 'Delaware', 'Lancaster', 'Lehigh', 'Montgomery', 'Northampton', 'Philadelphia', 'Schuylkill']
            },
            'Middle District of Pennsylvania': {
                'divisions': ['Scranton', 'Wilkes-Barre', 'Williamsport', 'Harrisburg'],
                'counties': ['Adams', 'Bradford', 'Carbon', 'Centre', 'Clinton', 'Columbia', 'Cumberland', 'Dauphin', 'Franklin', 'Fulton', 'Huntingdon', 'Juniata', 'Lackawanna', 'Lebanon', 'Luzerne', 'Lycoming', 'Mifflin', 'Monroe', 'Montour', 'Northumberland', 'Perry', 'Pike', 'Snyder', 'Sullivan', 'Susquehanna', 'Tioga', 'Union', 'Wayne', 'Wyoming', 'York']
            },
            'Western District of Pennsylvania': {
                'divisions': ['Pittsburgh', 'Erie', 'Johnstown'],
                'counties': ['Allegheny', 'Armstrong', 'Beaver', 'Bedford', 'Blair', 'Butler', 'Cambria', 'Cameron', 'Clarion', 'Clearfield', 'Crawford', 'Elk', 'Erie', 'Fayette', 'Forest', 'Greene', 'Indiana', 'Jefferson', 'Lawrence', 'McKean', 'Mercer', 'Potter', 'Somerset', 'Venango', 'Warren', 'Washington', 'Westmoreland']
            }
        }
    },
    'NY': {
        'name': 'New York',
        'districts': {
            'Southern District of New York': {
                'divisions': ['Manhattan', 'White Plains'],
                'counties': ['New York', 'Bronx', 'Westchester', 'Rockland', 'Putnam', 'Orange', 'Dutchess', 'Sullivan']
            },
            'Eastern District of New York': {
                'divisions': ['Brooklyn', 'Central Islip'],
                'counties': ['Kings', 'Queens', 'Richmond', 'Nassau', 'Suffolk']
            },
            'Northern District of New York': {
                'divisions': ['Albany', 'Syracuse', 'Utica', 'Binghamton', 'Watertown'],
                'counties': ['Albany', 'Broome', 'Cayuga', 'Chenango', 'Clinton', 'Columbia', 'Cortland', 'Delaware', 'Essex', 'Franklin', 'Fulton', 'Greene', 'Hamilton', 'Herkimer', 'Jefferson', 'Lewis', 'Madison', 'Montgomery', 'Oneida', 'Onondaga', 'Oswego', 'Otsego', 'Rensselaer', 'St. Lawrence', 'Saratoga', 'Schenectady', 'Schoharie', 'Tioga', 'Tompkins', 'Warren', 'Washington']
            },
            'Western District of New York': {
                'divisions': ['Buffalo', 'Rochester'],
                'counties': ['Allegany', 'Cattaraugus', 'Chautauqua', 'Chemung', 'Erie', 'Genesee', 'Livingston', 'Monroe', 'Niagara', 'Ontario', 'Orleans', 'Schuyler', 'Seneca', 'Steuben', 'Wayne', 'Wyoming', 'Yates']
            }
        }
    },
    'NJ': {
        'name': 'New Jersey',
        'districts': {
            'District of New Jersey': {
                'divisions': ['Newark', 'Trenton', 'Camden'],
                'counties': ['All New Jersey Counties']
            }
        }
    },
    'CT': {
        'name': 'Connecticut',
        'districts': {
            'District of Connecticut': {
                'divisions': ['Hartford', 'New Haven', 'Bridgeport'],
                'counties': ['All Connecticut Counties']
            }
        }
    },
    'MA': {
        'name': 'Massachusetts',
        'districts': {
            'District of Massachusetts': {
                'divisions': ['Boston', 'Worcester', 'Springfield'],
                'counties': ['All Massachusetts Counties']
            }
        }
    }
}