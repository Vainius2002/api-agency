from app.api.routes import trigger_webhooks

def notify_company_created(company):
    """Notify when a company is created"""
    trigger_webhooks('company.created', {
        'id': company.id,
        'name': company.name,
        'vat_code': company.vat_code,
        'registration_number': company.registration_number,
        'created_at': company.created_at.isoformat() if company.created_at else None
    })

def notify_company_updated(company):
    """Notify when a company is updated"""
    trigger_webhooks('company.updated', {
        'id': company.id,
        'name': company.name,
        'vat_code': company.vat_code,
        'registration_number': company.registration_number,
        'updated_at': company.updated_at.isoformat() if company.updated_at else None
    })

def notify_brand_created(brand):
    """Notify when a brand is created"""
    trigger_webhooks('brand.created', {
        'id': brand.id,
        'name': brand.name,
        'company_id': brand.company_id,
        'company_name': brand.company.name,
        'created_at': brand.created_at.isoformat() if brand.created_at else None
    })

def notify_brand_updated(brand):
    """Notify when a brand is updated"""
    trigger_webhooks('brand.updated', {
        'id': brand.id,
        'name': brand.name,
        'company_id': brand.company_id,
        'company_name': brand.company.name
    })

def notify_contact_created(contact):
    """Notify when a contact is created"""
    print(f"🔔 WEBHOOK TRIGGER: Contact created - {contact.first_name} {contact.last_name} ({contact.email})")
    
    # Include brands data for proper matching in NewBusiness
    brands_data = []
    for brand in contact.brands:
        brands_data.append({
            'id': brand.id,
            'name': brand.name
        })
        print(f"   - Associated with brand: {brand.name}")
    
    webhook_data = {
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone': contact.phone,
        'brands': brands_data,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    }
    
    print(f"📤 Sending webhook data: {webhook_data}")
    trigger_webhooks('contact.created', webhook_data)

def notify_contact_updated(contact):
    """Notify when a contact is updated"""
    print(f"🔄 WEBHOOK TRIGGER: Contact updated - {contact.first_name} {contact.last_name} ({contact.email})")
    
    # Include brands data for proper matching in NewBusiness
    brands_data = []
    for brand in contact.brands:
        brands_data.append({
            'id': brand.id,
            'name': brand.name
        })
        print(f"   - Associated with brand: {brand.name}")
    
    from datetime import datetime
    
    webhook_data = {
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone': contact.phone,
        'brands': brands_data,
        'updated_at': datetime.utcnow().isoformat()
    }
    
    print(f"📤 Sending contact update webhook data: {webhook_data}")
    trigger_webhooks('contact.updated', webhook_data)

def notify_invoice_created(invoice):
    """Notify when an invoice is created"""
    trigger_webhooks('invoice.created', {
        'id': invoice.id,
        'brand_id': invoice.brand_id,
        'brand_name': invoice.brand.name,
        'company_id': invoice.company_id,
        'company_name': invoice.company.name,
        'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        'total_amount': float(invoice.total_amount) if invoice.total_amount else 0,
        'created_at': invoice.created_at.isoformat() if invoice.created_at else None
    })

def notify_status_update_created(status_update):
    """Notify when a status update is created"""
    trigger_webhooks('status_update.created', {
        'id': status_update.id,
        'brand_id': status_update.brand_id,
        'brand_name': status_update.brand.name,
        'update_text': status_update.update_text,
        'created_by': f"{status_update.created_by.first_name} {status_update.created_by.last_name}",
        'created_at': status_update.created_at.isoformat() if status_update.created_at else None
    })