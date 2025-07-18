#!/usr/bin/env python
"""Add responsibility_description column to client_contacts table"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Check if column already exists
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('client_contacts')]
    
    if 'responsibility_description' not in columns:
        print("Adding responsibility_description column to client_contacts table...")
        
        # Add the new column
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE client_contacts ADD COLUMN responsibility_description TEXT'))
            conn.commit()
        
        print("Column added successfully!")
    else:
        print("Column already exists, skipping.")

print("Database update complete!")