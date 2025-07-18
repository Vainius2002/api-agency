#!/usr/bin/env python
"""Update database for birthday management"""

from app import create_app, db
from sqlalchemy import text
from datetime import datetime

app = create_app()

with app.app_context():
    print("Updating database for birthday management...")
    
    with db.engine.connect() as conn:
        # Check existing columns in client_contacts
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('client_contacts')]
        
        # Add birthday_month column if it doesn't exist
        if 'birthday_month' not in columns:
            print("Adding birthday_month column...")
            conn.execute(text('ALTER TABLE client_contacts ADD COLUMN birthday_month INTEGER'))
            conn.commit()
        
        # Add birthday_day column if it doesn't exist
        if 'birthday_day' not in columns:
            print("Adding birthday_day column...")
            conn.execute(text('ALTER TABLE client_contacts ADD COLUMN birthday_day INTEGER'))
            conn.commit()
        
        # Migrate existing birthday data
        print("Migrating existing birthday data...")
        result = conn.execute(text('SELECT id, birthday FROM client_contacts WHERE birthday IS NOT NULL'))
        for row in result:
            if row.birthday:
                # Parse the date string
                try:
                    date_obj = datetime.strptime(str(row.birthday), '%Y-%m-%d')
                    conn.execute(text(
                        'UPDATE client_contacts SET birthday_month = :month, birthday_day = :day WHERE id = :id'
                    ), {'month': date_obj.month, 'day': date_obj.day, 'id': row.id})
                except:
                    pass
        conn.commit()
    
    # Create gifts table
    print("Creating gifts table...")
    db.create_all()
    
    print("Database updated successfully!")
    print("- Added birthday_month and birthday_day columns")
    print("- Created gifts table")
    print("- Migrated existing birthday data")