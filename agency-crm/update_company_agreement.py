#!/usr/bin/env python
"""Update database for agency fees and agreement valid until date"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating database for agency fees and agreement validity...")
    
    with db.engine.connect() as conn:
        # Check existing columns in companies
        inspector = db.inspect(db.engine)
        company_columns = [col['name'] for col in inspector.get_columns('companies')]
        
        # Add agency_fees column to companies if it doesn't exist
        if 'agency_fees' not in company_columns:
            print("Adding agency_fees column to companies...")
            conn.execute(text('ALTER TABLE companies ADD COLUMN agency_fees TEXT'))
            conn.commit()
        
        # Check existing columns in agreements
        agreement_columns = [col['name'] for col in inspector.get_columns('agreements')]
        
        # Add valid_until column to agreements if it doesn't exist
        if 'valid_until' not in agreement_columns:
            print("Adding valid_until column to agreements...")
            conn.execute(text('ALTER TABLE agreements ADD COLUMN valid_until DATE'))
            conn.commit()
    
    print("Database updated successfully!")
    print("- Added agency_fees column to companies")
    print("- Added valid_until column to agreements")