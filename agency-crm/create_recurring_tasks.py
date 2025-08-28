#!/usr/bin/env python
"""Create tables for recurring tasks"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating recurring tasks tables...")
    
    with db.engine.connect() as conn:
        # Create task_templates table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name)
            )
        '''))
        
        # Create brand_tasks table (tasks assigned to brands)
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS brand_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_id INTEGER NOT NULL,
                task_template_id INTEGER NOT NULL,
                frequency VARCHAR(20) NOT NULL,
                start_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by_id INTEGER NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands (id),
                FOREIGN KEY (task_template_id) REFERENCES task_templates (id),
                FOREIGN KEY (created_by_id) REFERENCES users (id),
                UNIQUE(brand_id, task_template_id)
            )
        '''))
        
        # Create task_completions table (track when tasks are completed)
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_task_id INTEGER NOT NULL,
                completion_date DATE NOT NULL,
                completed_by_id INTEGER NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_task_id) REFERENCES brand_tasks (id),
                FOREIGN KEY (completed_by_id) REFERENCES users (id)
            )
        '''))
        
        # Insert default task templates
        default_tasks = [
            ('Client day meeting', 'Regular client day meeting', True),
            ('Invoices', 'Send invoices to client', True),
            ('Results presentation meeting', 'Present campaign/project results', True),
            ('Monitoring', 'Regular monitoring activities', True),
            ('Media landscape', 'Media landscape analysis and presentation', True),
            ('Media news presentation', 'Present latest media news and updates', True),
            ('Media strategy presentation', 'Present media strategy', True)
        ]
        
        for name, description, is_default in default_tasks:
            conn.execute(text('''
                INSERT OR IGNORE INTO task_templates (name, description, is_default)
                VALUES (:name, :description, :is_default)
            '''), {'name': name, 'description': description, 'is_default': is_default})
        
        conn.commit()
    
    print("Database updated successfully!")
    print("- Created task_templates table")
    print("- Created brand_tasks table")
    print("- Created task_completions table")
    print("- Added default task templates")