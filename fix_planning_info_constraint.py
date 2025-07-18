#!/usr/bin/env python
"""Remove UNIQUE constraint from planning_info.brand_id"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Fixing planning_info table constraints...")
    
    with db.engine.connect() as conn:
        # SQLite doesn't support dropping constraints directly, 
        # so we need to recreate the table without the constraint
        
        # Step 1: Rename the old table
        print("Renaming old table...")
        conn.execute(text('ALTER TABLE planning_info RENAME TO planning_info_old'))
        conn.commit()
        
        # Step 2: Create new table without unique constraint
        print("Creating new table without UNIQUE constraint...")
        conn.execute(text('''
            CREATE TABLE planning_info (
                id INTEGER PRIMARY KEY,
                brand_id INTEGER NOT NULL,
                comments TEXT,
                kpis TEXT,
                created_at DATETIME,
                created_by_id INTEGER NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands (id),
                FOREIGN KEY (created_by_id) REFERENCES users (id)
            )
        '''))
        conn.commit()
        
        # Step 3: Copy data from old table to new table
        print("Copying data to new table...")
        conn.execute(text('''
            INSERT INTO planning_info (id, brand_id, comments, kpis, created_at, created_by_id)
            SELECT id, brand_id, comments, kpis, created_at, created_by_id
            FROM planning_info_old
        '''))
        conn.commit()
        
        # Step 4: Drop old table
        print("Dropping old table...")
        conn.execute(text('DROP TABLE planning_info_old'))
        conn.commit()
        
    print("Planning info table fixed successfully!")
    print("The UNIQUE constraint on brand_id has been removed.")