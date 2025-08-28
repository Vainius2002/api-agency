from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models import Company, Brand, ClientContact, StatusUpdate, Agreement, Invoice, KeyMeeting, BrandTeam
from sqlalchemy import desc
from datetime import datetime, timedelta

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    # Get all active brands with their data
    active_brands = Brand.query.filter_by(status='active').all()
    brands_data = []
    
    for brand in active_brands:
        # Get key responsible person
        key_responsible = None
        for team_member in brand.team_members:
            if team_member.is_key_responsible:
                key_responsible = team_member.team_member
                break
        
        # Check for service and data agreements
        company_agreements = Agreement.query.filter_by(company_id=brand.company_id).all()
        has_service_agreement = any(ag.type == 'service' and (not ag.valid_until or ag.valid_until >= datetime.now().date()) for ag in company_agreements)
        has_data_agreement = any(ag.type == 'data' and (not ag.valid_until or ag.valid_until >= datetime.now().date()) for ag in company_agreements)
        
        # Get last status update
        last_update = StatusUpdate.query.filter_by(brand_id=brand.id).order_by(desc(StatusUpdate.date)).first()
        if last_update:
            days_since_update = (datetime.now().date() - last_update.date).days
            update_overdue = days_since_update > 14
            last_evaluation = last_update.evaluation
        else:
            days_since_update = None
            update_overdue = True
            last_evaluation = None
        
        # Get last invoice
        last_invoice = Invoice.query.filter_by(brand_id=brand.id).order_by(desc(Invoice.invoice_date)).first()
        if last_invoice:
            last_invoice_date = last_invoice.invoice_date
            last_invoice_amount = last_invoice.total_amount
        else:
            last_invoice_date = None
            last_invoice_amount = None
        
        # Get last key meeting
        last_meeting = KeyMeeting.query.filter_by(brand_id=brand.id).order_by(desc(KeyMeeting.date)).first()
        if last_meeting:
            days_since_meeting = (datetime.now().date() - last_meeting.date).days
            meeting_overdue = days_since_meeting > 30
        else:
            days_since_meeting = None
            meeting_overdue = True
        
        brands_data.append({
            'brand': brand,
            'key_responsible': key_responsible,
            'has_service_agreement': has_service_agreement,
            'has_data_agreement': has_data_agreement,
            'days_since_update': days_since_update,
            'update_overdue': update_overdue,
            'last_evaluation': last_evaluation,
            'last_invoice_date': last_invoice_date,
            'last_invoice_amount': last_invoice_amount,
            'days_since_meeting': days_since_meeting,
            'meeting_overdue': meeting_overdue
        })
    
    # Sort brands by company name and then brand name
    brands_data.sort(key=lambda x: (x['brand'].company.name, x['brand'].name))
    
    return render_template('dashboard/index.html',
                         brands_data=brands_data)