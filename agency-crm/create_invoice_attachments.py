#!/usr/bin/env python
"""
Create invoice_attachments table for supporting multiple files per invoice.
This script migrates existing single-file invoices to the new structure.
"""
import os
import sys
from app import create_app, db
from app.models import Invoice, InvoiceAttachment
from sqlalchemy import text

app = create_app()
app.app_context().push()

def create_invoice_attachments_table():
    """Create the invoice_attachments table and migrate existing data."""
    
    print("Creating invoice_attachments table...")
    
    # Create the new table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS invoice_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        filename VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
    );
    """
    
    # Create index for faster queries
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_invoice_attachments_invoice_id 
    ON invoice_attachments (invoice_id);
    """
    
    try:
        # Execute SQL commands
        db.session.execute(text(create_table_sql))
        db.session.execute(text(create_index_sql))
        db.session.commit()
        print("✓ invoice_attachments table created successfully")
        
        # Migrate existing invoice files to attachments
        print("\nMigrating existing invoice files...")
        invoices_with_files = Invoice.query.filter(Invoice.file_path.isnot(None)).all()
        
        migrated_count = 0
        for invoice in invoices_with_files:
            # Check if already migrated
            existing_attachment = InvoiceAttachment.query.filter_by(
                invoice_id=invoice.id,
                file_path=invoice.file_path
            ).first()
            
            if not existing_attachment and invoice.file_path:
                attachment = InvoiceAttachment(
                    invoice_id=invoice.id,
                    filename=invoice.filename or 'Invoice File',
                    file_path=invoice.file_path
                )
                db.session.add(attachment)
                migrated_count += 1
        
        db.session.commit()
        print(f"✓ Migrated {migrated_count} existing invoice files to attachments")
        
        print("\n✅ Database migration completed successfully!")
        print("\nNote: The filename and file_path columns in the invoices table are kept for backward compatibility.")
        print("New invoices will use the invoice_attachments table for multiple file support.")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_invoice_attachments_table()