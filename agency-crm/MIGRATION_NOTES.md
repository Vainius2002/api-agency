# Migration Notes for Subbrand Feature

## Overview
This update adds subbrand functionality and Excel export features to the Agency CRM system.

## New Features
1. **Subbrands**: Brands can now have multiple subbrands (display-only information)
2. **Excel Export**: Added export functionality for:
   - Brands (including subbrands)
   - Contacts
   - Companies

## Database Migration Instructions

### For New Installations
No action needed - the database will be created with all necessary tables.

### For Existing Installations
Run the following command to add the subbrands table:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install new dependency
pip install -r requirements.txt

# Run the migration script
python create_subbrand_table.py
```

### Manual Migration (if needed)
If the above script doesn't work, you can manually create the table:

```sql
CREATE TABLE subbrands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    brand_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands (id)
);
```

## Verification
To verify the migration was successful:

```bash
python check_subbrand_table.py
```

This will confirm if the subbrands table exists in your database.