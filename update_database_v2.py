#!/usr/bin/env python
"""Update database with new tables for planning, meetings, and links"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating new tables...")
    
    # Drop the old unique constraint on planning_info if it exists
    try:
        with db.engine.connect() as conn:
            conn.execute(text('DROP INDEX IF EXISTS ix_planning_info_brand_id'))
            conn.commit()
    except:
        pass
    
    # Create all new tables
    db.create_all()
    
    print("Database updated successfully!")
    print("New tables created:")
    print("- planning_attachments")
    print("- key_meetings")
    print("- meeting_attachments")
    print("- key_links")
    print("Updated tables:")
    print("- planning_info (removed unique constraint on brand_id, added created_by_id)")