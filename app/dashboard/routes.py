from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models import Company, Brand, ClientContact, StatusUpdate
from sqlalchemy import desc

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    total_companies = Company.query.filter_by(status='active').count()
    total_brands = Brand.query.filter_by(status='active').count()
    total_contacts = ClientContact.query.filter_by(status='active').count()
    
    recent_updates = StatusUpdate.query.order_by(desc(StatusUpdate.created_at)).limit(10).all()
    
    risk_brands = []
    for update in StatusUpdate.query.filter_by(evaluation='risk').order_by(desc(StatusUpdate.created_at)).all():
        if update.brand not in risk_brands:
            risk_brands.append(update.brand)
        if len(risk_brands) >= 5:
            break
    
    return render_template('dashboard/index.html',
                         total_companies=total_companies,
                         total_brands=total_brands,
                         total_contacts=total_contacts,
                         recent_updates=recent_updates,
                         risk_brands=risk_brands)