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