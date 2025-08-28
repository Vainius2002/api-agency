#!/usr/bin/env python
"""Create API-related tables for agency-crm"""

import sqlite3
from datetime import datetime

def create_api_tables():
    conn = sqlite3.connect('instance/agency_crm.db')
    cursor = conn.cursor()
    
    # Create API Keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            key_hash VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            permissions TEXT DEFAULT '{"read": true, "write": false, "delete": false}',
            created_at DATETIME,
            last_used_at DATETIME,
            use_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create Webhooks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            url VARCHAR(500) NOT NULL,
            secret VARCHAR(64) NOT NULL,
            events TEXT DEFAULT '[]',
            is_active BOOLEAN DEFAULT 1,
            user_id INTEGER NOT NULL,
            created_at DATETIME,
            last_triggered_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create Webhook Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            webhook_id INTEGER NOT NULL,
            event VARCHAR(100) NOT NULL,
            payload TEXT,
            response_status INTEGER,
            response_body TEXT,
            created_at DATETIME,
            FOREIGN KEY (webhook_id) REFERENCES webhooks (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("API tables created successfully in agency-crm")

if __name__ == '__main__':
    create_api_tables()