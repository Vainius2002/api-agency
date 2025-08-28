#!/usr/bin/env python
"""Update planning_info table with new columns"""

from app import create_app, db
from sqlalchemy import text
from datetime import datetime

app = create_app()

with app.app_context():
    print("Updating planning_info table...")
    
    with db.engine.connect() as conn:
        # Check existing columns
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('planning_info')]
        
        # Add created_at column if it doesn't exist
        if 'created_at' not in columns:
            print("Adding created_at column...")
            conn.execute(text('ALTER TABLE planning_info ADD COLUMN created_at DATETIME'))
            # Set default value for existing records
            conn.execute(text('UPDATE planning_info SET created_at = :now WHERE created_at IS NULL'), 
                        {'now': datetime.utcnow()})
            conn.commit()
        
        # Add created_by_id column if it doesn't exist
        if 'created_by_id' not in columns:
            print("Adding created_by_id column...")
            conn.execute(text('ALTER TABLE planning_info ADD COLUMN created_by_id INTEGER'))
            # Set a default user ID for existing records (1 for the first user)
            conn.execute(text('UPDATE planning_info SET created_by_id = 1 WHERE created_by_id IS NULL'))
            conn.commit()
        
        # Remove updated_at column if it exists (we don't use it anymore)
        if 'updated_at' in columns:
            print("Note: updated_at column exists but is no longer used")
    
    print("Planning info table updated successfully!")