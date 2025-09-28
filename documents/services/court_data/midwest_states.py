# documents/services/court_data/midwest_states.py
"""
Federal district court data for Midwestern United States
"""

MIDWEST_DISTRICTS = {
    'IL': {
        'name': 'Illinois',
        'districts': {
            'Northern District of Illinois': {
                'divisions': ['Chicago', 'Rockford'],
                'counties': ['Cook', 'DuPage', 'Grundy', 'Kane', 'Kendall', 'Lake', 'LaSalle', 'McHenry', 'Will', 'Boone', 'Carroll', 'DeKalb', 'Jo Daviess', 'Lee', 'Ogle', 'Stephenson', 'Whiteside', 'Winnebago']
            },
            'Central District of Illinois': {
                'divisions': ['Springfield', 'Peoria', 'Rock Island', 'Urbana'],
                'counties': ['Adams', 'Brown', 'Bureau', 'Cass', 'Champaign', 'Christian', 'Coles', 'Cumberland', 'DeWitt', 'Douglas', 'Edgar', 'Ford', 'Fulton', 'Greene', 'Hancock', 'Henderson', 'Henry', 'Iroquois', 'Kankakee', 'Knox', 'Livingston', 'Logan', 'McDonough', 'McLean', 'Macon', 'Marshall', 'Mason', 'Menard', 'Mercer', 'Morgan', 'Moultrie', 'Peoria', 'Piatt', 'Pike', 'Putnam', 'Rock Island', 'Sangamon', 'Schuyler', 'Scott', 'Shelby', 'Stark', 'Tazewell', 'Vermilion', 'Warren', 'Woodford']
            },
            'Southern District of Illinois': {
                'divisions': ['East St. Louis', 'Benton'],
                'counties': ['Alexander', 'Bond', 'Calhoun', 'Clark', 'Clay', 'Clinton', 'Crawford', 'Edwards', 'Effingham', 'Fayette', 'Franklin', 'Gallatin', 'Hamilton', 'Hardin', 'Jackson', 'Jasper', 'Jefferson', 'Jersey', 'Johnson', 'Lawrence', 'Macoupin', 'Madison', 'Marion', 'Massac', 'Monroe', 'Montgomery', 'Perry', 'Pope', 'Pulaski', 'Randolph', 'Richland', 'Saline', 'St. Clair', 'Union', 'Wabash', 'Washington', 'Wayne', 'White', 'Williamson']
            }
        }
    },
    'OH': {
        'name': 'Ohio',
        'districts': {
            'Northern District of Ohio': {
                'divisions': ['Cleveland', 'Akron', 'Toledo', 'Youngstown'],
                'counties': ['Allen', 'Ashland', 'Ashtabula', 'Crawford', 'Cuyahoga', 'Defiance', 'Erie', 'Fulton', 'Geauga', 'Hancock', 'Hardin', 'Henry', 'Huron', 'Lake', 'Lorain', 'Lucas', 'Mahoning', 'Marion', 'Medina', 'Mercer', 'Ottawa', 'Paulding', 'Portage', 'Putnam', 'Richland', 'Sandusky', 'Seneca', 'Stark', 'Summit', 'Trumbull', 'Van Wert', 'Wayne', 'Williams', 'Wood', 'Wyandot']
            },
            'Southern District of Ohio': {
                'divisions': ['Columbus', 'Cincinnati', 'Dayton'],
                'counties': ['Adams', 'Athens', 'Auglaize', 'Belmont', 'Brown', 'Butler', 'Carroll', 'Champaign', 'Clark', 'Clermont', 'Clinton', 'Columbiana', 'Coshocton', 'Darke', 'Delaware', 'Fairfield', 'Fayette', 'Franklin', 'Gallia', 'Greene', 'Guernsey', 'Hamilton', 'Harrison', 'Highland', 'Hocking', 'Holmes', 'Jackson', 'Jefferson', 'Knox', 'Lawrence', 'Licking', 'Logan', 'Madison', 'Meigs', 'Miami', 'Monroe', 'Montgomery', 'Morgan', 'Morrow', 'Muskingum', 'Noble', 'Pickaway', 'Pike', 'Preble', 'Ross', 'Scioto', 'Shelby', 'Tuscarawas', 'Union', 'Vinton', 'Warren', 'Washington']
            }
        }
    },
    'MI': {
        'name': 'Michigan',
        'districts': {
            'Eastern District of Michigan': {
                'divisions': ['Detroit', 'Ann Arbor', 'Bay City', 'Flint', 'Port Huron'],
                'counties': ['Genesee', 'Lapeer', 'Livingston', 'Macomb', 'Monroe', 'Oakland', 'St. Clair', 'Sanilac', 'Shiawassee', 'Tuscola', 'Washtenaw', 'Wayne', 'Lenawee', 'Hillsdale', 'Jackson', 'Ingham', 'Eaton', 'Barry', 'Calhoun', 'Kalamazoo', 'Van Buren', 'Berrien', 'Cass', 'St. Joseph', 'Branch', 'Huron', 'Saginaw', 'Bay', 'Midland', 'Gratiot', 'Clinton', 'Ionia', 'Kent', 'Ottawa', 'Allegan', 'Montcalm', 'Mecosta', 'Isabella', 'Clare', 'Gladwin', 'Arenac']
                },
            'Western District of Michigan': {
                'divisions': ['Grand Rapids', 'Kalamazoo', 'Marquette'],
                'counties': ['Alcona', 'Alger', 'Alpena', 'Antrim', 'Baraga', 'Benzie', 'Charlevoix', 'Cheboygan', 'Chippewa', 'Crawford', 'Delta', 'Dickinson', 'Emmet', 'Gogebic', 'Grand Traverse', 'Houghton', 'Iosco', 'Iron', 'Kalkaska', 'Keweenaw', 'Lake', 'Leelanau', 'Luce', 'Mackinac', 'Manistee', 'Marquette', 'Mason', 'Menominee', 'Missaukee', 'Newaygo', 'Oceana', 'Ontonagon', 'Osceola', 'Oscoda', 'Otsego', 'Presque Isle', 'Roscommon', 'Schoolcraft', 'Wexford']
            }
        }
    },
    'IN': {
        'name': 'Indiana',
        'districts': {
            'Northern District of Indiana': {
                'divisions': ['Fort Wayne', 'South Bend', 'Hammond'],
                'counties': ['Adams', 'Allen', 'Benton', 'Blackford', 'Carroll', 'Cass', 'DeKalb', 'Elkhart', 'Fulton', 'Grant', 'Huntington', 'Jasper', 'Jay', 'Kosciusko', 'LaGrange', 'Lake', 'LaPorte', 'Marshall', 'Miami', 'Newton', 'Noble', 'Porter', 'Pulaski', 'St. Joseph', 'Starke', 'Steuben', 'Wabash', 'Wells', 'White', 'Whitley']
            },
            'Southern District of Indiana': {
                'divisions': ['Indianapolis', 'Terre Haute', 'Evansville', 'New Albany'],
                'counties': ['Bartholomew', 'Boone', 'Brown', 'Clark', 'Clay', 'Clinton', 'Crawford', 'Daviess', 'Dearborn', 'Decatur', 'Delaware', 'Dubois', 'Fayette', 'Floyd', 'Fountain', 'Franklin', 'Gibson', 'Greene', 'Hamilton', 'Hancock', 'Harrison', 'Hendricks', 'Henry', 'Howard', 'Jackson', 'Jefferson', 'Jennings', 'Johnson', 'Knox', 'Lawrence', 'Madison', 'Marion', 'Martin', 'Monroe', 'Montgomery', 'Morgan', 'Ohio', 'Orange', 'Owen', 'Parke', 'Perry', 'Pike', 'Posey', 'Putnam', 'Randolph', 'Ripley', 'Rush', 'Scott', 'Shelby', 'Spencer', 'Sullivan', 'Switzerland', 'Tippecanoe', 'Tipton', 'Union', 'Vanderburgh', 'Vermillion', 'Vigo', 'Warren', 'Warrick', 'Washington', 'Wayne']
            }
        }
    },
    'WI': {
        'name': 'Wisconsin',
        'districts': {
            'Eastern District of Wisconsin': {
                'divisions': ['Milwaukee', 'Green Bay'],
                'counties': ['Brown', 'Calumet', 'Dodge', 'Door', 'Fond du Lac', 'Forest', 'Green Lake', 'Kenosha', 'Kewaunee', 'Langlade', 'Manitowoc', 'Marinette', 'Marquette', 'Menominee', 'Milwaukee', 'Oconto', 'Outagamie', 'Ozaukee', 'Racine', 'Shawano', 'Sheboygan', 'Walworth', 'Washington', 'Waukesha', 'Waupaca', 'Waushara', 'Winnebago']
            },
            'Western District of Wisconsin': {
                'divisions': ['Madison'],
                'counties': ['Adams', 'Ashland', 'Barron', 'Bayfield', 'Buffalo', 'Burnett', 'Chippewa', 'Clark', 'Columbia', 'Crawford', 'Dane', 'Douglas', 'Dunn', 'Eau Claire', 'Florence', 'Grant', 'Green', 'Iowa', 'Iron', 'Jackson', 'Jefferson', 'Juneau', 'La Crosse', 'Lafayette', 'Lincoln', 'Marathon', 'Monroe', 'Oneida', 'Pepin', 'Pierce', 'Polk', 'Portage', 'Price', 'Richland', 'Rock', 'Rusk', 'Sauk', 'Sawyer', 'St. Croix', 'Taylor', 'Trempealeau', 'Vernon', 'Vilas', 'Washburn', 'Wood']
            }
        }
    },
    'IA': {
        'name': 'Iowa',
        'districts': {
            'Northern District of Iowa': {
                'divisions': ['Cedar Rapids', 'Sioux City'],
                'counties': ['Allamakee', 'Black Hawk', 'Bremer', 'Buchanan', 'Butler', 'Cerro Gordo', 'Chickasaw', 'Clayton', 'Delaware', 'Dubuque', 'Fayette', 'Floyd', 'Franklin', 'Grundy', 'Hamilton', 'Hancock', 'Hardin', 'Howard', 'Humboldt', 'Jackson', 'Jones', 'Linn', 'Marshall', 'Mitchell', 'O\'Brien', 'Pocahontas', 'Tama', 'Webster', 'Winnebago', 'Winneshiek', 'Worth', 'Wright']
            },
            'Southern District of Iowa': {
                'divisions': ['Des Moines', 'Davenport'],
                'counties': ['Adair', 'Adams', 'Appanoose', 'Audubon', 'Benton', 'Boone', 'Calhoun', 'Carroll', 'Cass', 'Cedar', 'Clarke', 'Clinton', 'Crawford', 'Dallas', 'Davis', 'Decatur', 'Des Moines', 'Fremont', 'Greene', 'Guthrie', 'Harrison', 'Henry', 'Iowa', 'Jasper', 'Jefferson', 'Johnson', 'Keokuk', 'Lee', 'Louisa', 'Lucas', 'Madison', 'Mahaska', 'Marion', 'Mills', 'Monroe', 'Montgomery', 'Muscatine', 'Page', 'Polk', 'Pottawattamie', 'Poweshiek', 'Ringgold', 'Scott', 'Shelby', 'Story', 'Taylor', 'Union', 'Van Buren', 'Wapello', 'Warren', 'Washington', 'Wayne']
            }
        }
    },
    'MN': {
        'name': 'Minnesota',
        'districts': {
            'District of Minnesota': {
                'divisions': ['Minneapolis', 'St. Paul', 'Duluth', 'Fergus Falls'],
                'counties': ['All Minnesota Counties']
            }
        }
    },
    'MO': {
        'name': 'Missouri',
        'districts': {
            'Eastern District of Missouri': {
                'divisions': ['St. Louis', 'Cape Girardeau', 'Hannibal'],
                'counties': ['Adair', 'Audrain', 'Bollinger', 'Boone', 'Butler', 'Callaway', 'Cape Girardeau', 'Carter', 'Chariton', 'Clark', 'Cole', 'Crawford', 'Dent', 'Dunklin', 'Franklin', 'Gasconade', 'Howard', 'Iron', 'Jefferson', 'Knox', 'Lewis', 'Lincoln', 'Linn', 'Macon', 'Madison', 'Maries', 'Marion', 'Miller', 'Mississippi', 'Monroe', 'Montgomery', 'New Madrid', 'Osage', 'Pemiscot', 'Perry', 'Phelps', 'Pike', 'Pulaski', 'Ralls', 'Randolph', 'Reynolds', 'Ripley', 'Scott', 'Shannon', 'Shelby', 'St. Charles', 'St. Francois', 'St. Louis', 'Ste. Genevieve', 'Stoddard', 'Warren', 'Washington', 'Wayne']
            },
            'Western District of Missouri': {
                'divisions': ['Kansas City', 'St. Joseph', 'Jefferson City', 'Springfield', 'Joplin'],
                'counties': ['Andrew', 'Atchison', 'Barry', 'Barton', 'Bates', 'Benton', 'Buchanan', 'Caldwell', 'Camden', 'Cass', 'Cedar', 'Christian', 'Clay', 'Clinton', 'Cooper', 'Dade', 'Dallas', 'Daviess', 'DeKalb', 'Douglas', 'Gentry', 'Greene', 'Grundy', 'Harrison', 'Henry', 'Hickory', 'Holt', 'Howell', 'Jackson', 'Jasper', 'Johnson', 'Lafayette', 'Lawrence', 'Livingston', 'McDonald', 'Mercer', 'Moniteau', 'Morgan', 'Newton', 'Nodaway', 'Oregon', 'Ozark', 'Petis', 'Platte', 'Polk', 'Putnam', 'Ray', 'Saline', 'Stone', 'Sullivan', 'Taney', 'Texas', 'Vernon', 'Webster', 'Worth', 'Wright']
            }
        }
    },
    'ND': {
        'name': 'North Dakota',
        'districts': {
            'District of North Dakota': {
                'divisions': ['Bismarck', 'Fargo', 'Grand Forks', 'Minot'],
                'counties': ['All North Dakota Counties']
            }
        }
    },
    'SD': {
        'name': 'South Dakota',
        'districts': {
            'District of South Dakota': {
                'divisions': ['Sioux Falls', 'Rapid City', 'Aberdeen', 'Pierre'],
                'counties': ['All South Dakota Counties']
            }
        }
    },
    'NE': {
        'name': 'Nebraska',
        'districts': {
            'District of Nebraska': {
                'divisions': ['Omaha', 'Lincoln', 'North Platte'],
                'counties': ['All Nebraska Counties']
            }
        }
    },
    'KS': {
        'name': 'Kansas',
        'districts': {
            'District of Kansas': {
                'divisions': ['Kansas City', 'Topeka', 'Wichita'],
                'counties': ['All Kansas Counties']
            }
        }
    }
}