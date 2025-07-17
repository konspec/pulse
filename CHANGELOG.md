## v0.5.2 (2025-07-17)

### Fix

- **customers**: migrate related name field in CustomerLedgerEntry model
- **customers**: fix return type of __str__ method of Customer class

## v0.5.1 (2025-07-10)

### Fix

- **customers**: fix related name on CustomerLedgerEntry model

## v0.5.0 (2025-07-10)

### Feat

- **core**: update base template

## v0.4.0 (2025-07-10)

### Feat

- **customers**: add management command to load customer ledger entries
- **customers**: add admin for CustomerLedgerEntry with read-only permissions
- **customers**: add CustomerLedgerEntry model to customers app

## v0.3.0 (2025-07-10)

### Feat

- **customers**: refactor customer loading command with ERP integration
- **common**: add loguru logger to Odyn client initialization
- **config**: add logging configuration to settings.py
- **customers**: add scaffold for load_customers management command
- **common**: add ERP client utility for Odyn integration
- **config**: add ERP credentials to environment and settings
- **customers**: restrict all admin permissions for Customer model
- **customers**: add basic Customer model with admin and history tracking
- **customers**: install customers app
- **customers**: scaffold the customers app with django-admin

### Fix

- **customers**: increase Customer code field length to 20 characters

## v0.2.0 (2025-07-09)

### Feat

- **users**: add login and logout views
- **users**: add a basic protected index view
- **config**: add crispy_forms and Tailwind support to settings
- **users**: add custom admin for CustomUser model
- **users**: add custom user model with email authentication

### Fix

- **users**: update app config name to 'apps.users'

### Refactor

- **settings**: group and clean settings with comments for clarity
