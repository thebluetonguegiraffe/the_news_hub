TIME_EXPRESSIONS = {
    # Relative day references
    'yesterday': (-2, -1),
    'today': (-1, 0),
    'the day before yesterday': (-3, -2),
    'day before yesterday': (-4, -3),
    
    # Week-based references
    'last week': (-14, -7),  # From 2 weeks ago to 1 week ago
    'this week': (-7, 0),    # From 7 days ago to today
    'a week ago': (-12, -7),
    'week ago': (-12, -7),
    'two weeks ago': (-21, -14),  # Range around 2 weeks ago
    'fortnight ago': (-21, -14),
    
    # Month-based references  
    'last month': (-60, -30),  # From 2 months ago to 1 month ago
    'this month': (-30, 0),    # From 30 days ago to today
    'a month ago': (-35, -30),
    'month ago': (-35, -30),
    'two months ago': (-90, -60),   # Range around 2 months ago
    'three months ago': (-120, -90), # Range around 3 months ago
    
    # Year-based references
    'last year': (-730, -365),  # From 2 years ago to 1 year ago
    'this year': (-365, 0),     # From 365 days ago to today
    'a year ago': (-365, -360),
    'year ago': (-365, -360),
    'two years ago': (-1095, -730),  # Range around 2 years ago
    
    # Recent time references
    'just now': (0, 0),
    'right now': (0, 0),
    'currently': (0, 0),
    'presently': (0, 0),
    'at the moment': 0,
    'recently': (-7, 0),     # From 7 days ago to today
    'lately': (-14, 0),      # From 2 weeks ago to today
    'not long ago': (-7, 0), # From 7 days ago to today
    'a while ago': (-60, -7), # From 2 months ago to 1 week ago
    'some time ago': (-120, -30), # From 4 months ago to 1 month ago
    'long ago': (-730, -365),     # From 2 years ago to 1 year ago
    
    # Specific day references (past only)
    'few days ago': (-5, -1),      # 1 to 5 days ago
    'several days ago': (-7, -3),  # 3 to 7 days ago
    'couple days ago': (-3, -1),   # 1 to 3 days ago
    'couple of days ago': (-3, -1),
    
    # Weekend references
    'last weekend': (-14, -7),  # Previous weekend period
    'this weekend': (-7, 0),    # This week's weekend (recent)
    
    # Season references (past seasons only)
    'last spring': (-365, -275),  # Last year's spring period
    'last summer': (-275, -185),  # Last year's summer period
    'last fall': (-185, -95),     # Last year's fall period
    'last autumn': (-185, -95),
    'last winter': (-95, -5),     # Last winter period
}

NUMERIC_TIME_PATTERNS = {
    r'(\d+)\s*days?\s*ago': lambda x: -int(x),
    r'(\d+)\s*weeks?\s*ago': lambda x: -int(x) * 7,
    r'(\d+)\s*months?\s*ago': lambda x: -int(x) * 30,
    r'(\d+)\s*years?\s*ago': lambda x: -int(x) * 365,
}