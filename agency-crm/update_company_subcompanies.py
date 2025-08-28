#!/usr/bin/env python
"""Update database for registration number and subcompanies"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating database for registration number and subcompanies...")
    
    with db.engine.connect() as conn:
        # Check existing columns in companies
        inspector = db.inspect(db.engine)
        company_columns = [col['name'] for col in inspector.get_columns('companies')]
        
        # Add registration_number column to companies if it doesn't exist
        if 'registration_number' not in company_columns:
            print("Adding registration_number column to companies...")
            conn.execute(text('ALTER TABLE companies ADD COLUMN registration_number VARCHAR(100)'))
            conn.commit()
        
        # Add parent_company_id for subcompanies
        if 'parent_company_id' not in company_columns:
            print("Adding parent_company_id column to companies...")
            conn.execute(text('ALTER TABLE companies ADD COLUMN parent_company_id INTEGER REFERENCES companies(id)'))
            conn.commit()
        
        # Create invoices table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                invoice_date DATE NOT NULL,
                short_info TEXT,
                filename VARCHAR(255),
                file_path VARCHAR(500),
                total_amount DECIMAL(12, 2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_id INTEGER NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands (id),
                FOREIGN KEY (company_id) REFERENCES companies (id),
                FOREIGN KEY (created_by_id) REFERENCES users (id)
            )
        '''))
        conn.commit()
    
    print("Database updated successfully!")
    print("- Added registration_number column to companies")
    print("- Added parent_company_id column for subcompanies")
    print("- Created invoices table")