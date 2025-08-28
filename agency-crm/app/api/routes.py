from flask import jsonify, request, current_app
from app.api import api_bp
from app.models import Company, Brand, ClientContact, Invoice, StatusUpdate, PlanningInfo, db
from app.api_auth import require_api_key
from datetime import datetime
import requests
import json

@api_bp.route('/companies', methods=['GET'])
@require_api_key
def get_companies():
    """Get all companies"""
    companies = Company.query.filter_by(status='active').all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'vat_code': c.vat_code,
        'registration_number': c.registration_number,
        'address': c.address,
        'agency_fees': c.agency_fees,
        'parent_company_id': c.parent_company_id,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in companies])

@api_bp.route('/companies/<int:company_id>', methods=['GET'])
@require_api_key
def get_company(company_id):
    """Get specific company details"""
    company = Company.query.get_or_404(company_id)
    return jsonify({
        'id': company.id,
        'name': company.name,
        'vat_code': company.vat_code,
        'registration_number': company.registration_number,
        'address': company.address,
        'agency_fees': company.agency_fees,
        'parent_company_id': company.parent_company_id,
        'brands': [{'id': b.id, 'name': b.name} for b in company.brands],
        'created_at': company.created_at.isoformat() if company.created_at else None
    })

@api_bp.route('/brands', methods=['GET'])
@require_api_key
def get_brands():
    """Get all brands"""
    brands = Brand.query.filter_by(status='active').all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'company_id': b.company_id,
        'company_name': b.company.name,
        'created_at': b.created_at.isoformat() if b.created_at else None
    } for b in brands])

@api_bp.route('/brands/<int:brand_id>', methods=['GET'])
@require_api_key
def get_brand(brand_id):
    """Get specific brand details"""
    brand = Brand.query.get_or_404(brand_id)
    return jsonify({
        'id': brand.id,
        'name': brand.name,
        'company_id': brand.company_id,
        'company_name': brand.company.name,
        'contacts': [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone': c.phone
        } for c in brand.contacts],
        'subbrands': [{'id': s.id, 'name': s.name} for s in brand.subbrands],
        'created_at': brand.created_at.isoformat() if brand.created_at else None
    })

@api_bp.route('/contacts', methods=['GET'])
@require_api_key
def get_contacts():
    """Get all contacts"""
    contacts = ClientContact.query.all()
    return jsonify([{
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'email': c.email,
        'phone': c.phone,
        'linkedin_url': c.linkedin_url,
        'birthday': c.birthday.isoformat() if c.birthday else None,
        'brands': [{'id': b.id, 'name': b.name} for b in c.brands],
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in contacts])

@api_bp.route('/invoices', methods=['GET'])
@require_api_key
def get_invoices():
    """Get invoices with optional filtering"""
    brand_id = request.args.get('brand_id', type=int)
    company_id = request.args.get('company_id', type=int)
    
    query = Invoice.query
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    invoices = query.order_by(Invoice.invoice_date.desc()).all()
    return jsonify([{
        'id': i.id,
        'brand_id': i.brand_id,
        'brand_name': i.brand.name,
        'company_id': i.company_id,
        'company_name': i.company.name,
        'invoice_date': i.invoice_date.isoformat() if i.invoice_date else None,
        'total_amount': float(i.total_amount) if i.total_amount else 0,
        'short_info': i.short_info,
        'created_at': i.created_at.isoformat() if i.created_at else None
    } for i in invoices])

@api_bp.route('/status-updates', methods=['GET'])
@require_api_key
def get_status_updates():
    """Get recent status updates"""
    limit = request.args.get('limit', 50, type=int)
    brand_id = request.args.get('brand_id', type=int)
    
    query = StatusUpdate.query
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    
    updates = query.order_by(StatusUpdate.created_at.desc()).limit(limit).all()
    return jsonify([{
        'id': u.id,
        'brand_id': u.brand_id,
        'brand_name': u.brand.name,
        'update_text': u.update_text,
        'created_by': f"{u.created_by.first_name} {u.created_by.last_name}",
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in updates])

@api_bp.route('/planning-info', methods=['GET'])
@require_api_key
def get_planning_info():
    """Get planning information for brands"""
    brand_id = request.args.get('brand_id', type=int)
    
    query = PlanningInfo.query
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    
    planning = query.order_by(PlanningInfo.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'brand_id': p.brand_id,
        'brand_name': p.brand.name,
        'budget': float(p.budget) if p.budget else 0,
        'planning_period': p.planning_period,
        'planning_status': p.planning_status,
        'planning_info': p.planning_info,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in planning])

# Webhook trigger function
def trigger_webhooks(event, data):
    """Trigger webhooks for a specific event"""
    from app.models import Webhook, WebhookLog
    import hashlib
    
    print(f"🔍 TRIGGER WEBHOOKS: Event '{event}' triggered")
    
    # Get all active webhooks and filter in Python since JSON array queries are complex
    active_webhooks = Webhook.query.filter(Webhook.is_active == True).all()
    webhooks = []
    for webhook in active_webhooks:
        if event in webhook.events:
            webhooks.append(webhook)
    
    print(f"📋 Found {len(webhooks)} active webhooks for event '{event}'")
    
    for webhook in webhooks:
        print(f"📡 Calling webhook: {webhook.url}")
        try:
            payload = json.dumps(data)
            signature = hashlib.sha256(
                f"{webhook.secret}{payload}".encode()
            ).hexdigest()
            
            response = requests.post(
                webhook.url,
                json=data,
                headers={
                    'X-Webhook-Event': event,
                    'X-Webhook-Signature': signature
                },
                timeout=10
            )
            
            print(f"✅ Webhook response: {response.status_code} - {response.text[:200]}")
            
            # Log the webhook call
            log = WebhookLog(
                webhook_id=webhook.id,
                event=event,
                payload=data,
                response_status=response.status_code,
                response_body=response.text[:1000]  # Limit response body size
            )
            db.session.add(log)
            
            webhook.last_triggered_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            # Log failed webhook
            log = WebhookLog(
                webhook_id=webhook.id,
                event=event,
                payload=data,
                response_status=0,
                response_body=str(e)[:1000]
            )
            db.session.add(log)
            db.session.commit()

@api_bp.route('/webhook/newbusiness', methods=['POST'])
def webhook_newbusiness():
    """Receive webhooks from NewBusiness for contact updates"""
    from flask import current_app
    import hashlib
    
    # Verify signature if configured
    signature = request.headers.get('X-Webhook-Signature')
    event = request.headers.get('X-Webhook-Event')
    data = request.json
    
    print(f"🔔 INCOMING WEBHOOK from NewBusiness: {event}")
    print(f"📦 Data: {data}")
    
    # For now, we'll add signature verification later
    # Let's focus on handling the contact update
    
    try:
        if event == 'contact.updated':
            # Update contact in Agency CRM
            update_agency_contact(data)
            return jsonify({'status': 'received'}), 200
        else:
            print(f"⚠️ Unknown event type: {event}")
            return jsonify({'error': 'Unknown event type'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Webhook processing error: {str(e)}")
        print(f"❌ Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def update_agency_contact(contact_data):
    """Update existing contact in Agency CRM from NewBusiness data"""
    from app.models import ClientContact, Brand
    
    agency_crm_id = contact_data.get('id')
    email = contact_data.get('email')
    first_name = contact_data.get('first_name', '')
    last_name = contact_data.get('last_name', '')
    
    print(f"🔍 Looking for contact: {first_name} {last_name} ({email}) [CRM ID: {agency_crm_id}]")
    
    contact = None
    
    # First try: Agency CRM ID match (if available)
    if agency_crm_id:
        contact = ClientContact.query.get(agency_crm_id)
        if contact:
            print(f"🎯 Found contact by Agency CRM ID {agency_crm_id}: {contact.first_name} {contact.last_name}")
    
    # Second try: Email match (for contacts that originated in NewBusiness)
    if not contact and email:
        contact = ClientContact.query.filter_by(email=email).first()
        if contact:
            print(f"📧 Found contact by email: {email}")
    
    # Third try: Name match (if email was changed)
    if not contact and first_name and last_name:
        contact = ClientContact.query.filter_by(
            first_name=first_name,
            last_name=last_name
        ).first()
        if contact:
            print(f"👤 Found contact by name: {first_name} {last_name}")
    
    if contact:
        print(f"🔄 Updating contact: {contact.first_name} {contact.last_name}")
        
        # Update contact information
        contact.first_name = contact_data.get('first_name', contact.first_name)
        contact.last_name = contact_data.get('last_name', contact.last_name)
        contact.email = contact_data.get('email', contact.email)
        contact.phone = contact_data.get('phone', contact.phone)
        contact.linkedin_url = contact_data.get('linkedin_url', contact.linkedin_url)
        
        print(f"📝 Updated contact information")
        
        # Handle brand relationships - clear and rebuild
        contact.brands = []  # Clear existing relationships
        
        for brand_data in contact_data.get('brands', []):
            advertiser_name = brand_data['name']
            print(f"🔍 Mapping advertiser '{advertiser_name}' to brand...")
            
            brand = None
            
            # Method 1: Try exact brand name match
            brand = Brand.query.filter(Brand.name.ilike(f"%{advertiser_name}%")).first()
            if brand:
                print(f"✅ Found by brand name: {brand.name}")
            
            # Method 2: Try company name match (advertiser name matches brand's company name)
            if not brand:
                brand = Brand.query.join(Brand.company).filter(
                    Brand.company.has(name=advertiser_name)
                ).first()
                if brand:
                    print(f"✅ Found by company name: {brand.name} (Company: {brand.company.name})")
            
            # Method 3: Try partial company name match
            if not brand:
                from app.models import Company
                # Extract key words from advertiser name for partial matching
                key_words = advertiser_name.replace(',', '').replace('UAB', '').replace('LT', '').strip()
                brand = Brand.query.join(Company).filter(
                    Company.name.ilike(f"%{key_words}%")
                ).first()
                if brand:
                    print(f"✅ Found by partial company match: {brand.name} (Company: {brand.company.name})")
            
            # Method 4: Try brand name partial match with key words
            if not brand:
                key_words = advertiser_name.split()[0]  # Take first word
                brand = Brand.query.filter(Brand.name.ilike(f"%{key_words}%")).first()
                if brand:
                    print(f"✅ Found by partial brand match: {brand.name}")
            
            if brand:
                contact.brands.append(brand)
                print(f"🔗 Added brand relationship: {brand.name}")
            else:
                print(f"❌ Could not map advertiser '{advertiser_name}' to any brand")
        
        db.session.commit()
        print(f"✅ Contact updated successfully in Agency CRM")
        
    else:
        print(f"❌ Contact not found - cannot sync from NewBusiness")
        print(f"   Searched by: ID={agency_crm_id}, Email={email}, Name={first_name} {last_name}")
        
        # Optionally create new contact in Agency CRM
        # For now, let's just log that we couldn't find it

# Make sure trigger_webhooks is available from other modules
__all__ = ['trigger_webhooks']