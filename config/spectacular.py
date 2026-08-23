SPECTACULAR_SETTINGS = {
    'TITLE': 'Accounts API',
    'DESCRIPTION': 'API documentation for Accounts',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    "TAGS": [
        # for authentication endpoints
        {"name": "Authentication", "description": "Authentication endpoints", "x-order": 1},
        {"name": "User", "description": "User management endpoints", "x-order": 5},
        {"name": "Organization", "description": "Organization management endpoints", "x-order": 6},

        # for account group endpoints
        {"name": "Account Groups", "description": "Endpoints for managing account groups", "x-order": 10},

        # for account endpoints
        {"name": "Accounts", "description": "Endpoints for managing accounts", "x-order": 20},
    ]
}
