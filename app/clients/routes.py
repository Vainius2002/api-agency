import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from wtforms import SelectField
from wtforms.validators import DataRequired
from app.clients import bp
from app.clients.forms import (CompanyForm, AgreementForm, BrandForm, ClientContactForm, 
                              BrandTeamForm, PlanningInfoForm, CommitmentForm, 
                              StatusUpdateForm, MediaGroupForm, KeyMeetingForm, KeyLinkForm, GiftForm)
from app.models import (Company, Agreement, Brand, ClientContact, BrandTeam, 
                       PlanningInfo, Commitment, StatusUpdate, MediaGroup, User,
                       KeyMeeting, KeyLink, PlanningAttachment, MeetingAttachment, Gift)
from app import db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/companies')
@login_required
def companies():
    companies = Company.query.order_by(Company.name).all()
    return render_template('clients/companies.html', companies=companies)

@bp.route('/company/new', methods=['GET', 'POST'])
@login_required
def new_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            vat_code=form.vat_code.data,
            address=form.address.data,
            bank_account=form.bank_account.data,
            agency_fees=form.agency_fees.data,
            status=form.status.data
        )
        db.session.add(company)
        db.session.commit()
        flash('Company created successfully!', 'success')
        return redirect(url_for('clients.company_detail', company_id=company.id))
    return render_template('clients/company_form.html', form=form, title='New Company')

@bp.route('/company/<int:company_id>')
@login_required
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('clients/company_detail.html', company=company, datetime=datetime)

@bp.route('/company/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(company=company)
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.vat_code = form.vat_code.data
        company.address = form.address.data
        company.bank_account = form.bank_account.data
        company.agency_fees = form.agency_fees.data
        company.status = form.status.data
        company.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Company updated successfully!', 'success')
        return redirect(url_for('clients.company_detail', company_id=company.id))
    
    elif request.method == 'GET':
        form.name.data = company.name
        form.vat_code.data = company.vat_code
        form.address.data = company.address
        form.bank_account.data = company.bank_account
        form.agency_fees.data = company.agency_fees
        form.status.data = company.status
    
    return render_template('clients/company_form.html', form=form, title='Edit Company', company=company)

@bp.route('/company/<int:company_id>/agreement', methods=['GET', 'POST'])
@login_required
def upload_agreement(company_id):
    company = Company.query.get_or_404(company_id)
    form = AgreementForm()
    
    if form.validate_on_submit():
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{company_id}_{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(file_path)
            
            agreement = Agreement(
                company_id=company_id,
                type=form.type.data,
                filename=form.file.data.filename,
                file_path=filename,
                valid_until=form.valid_until.data,
                uploaded_by_id=current_user.id
            )
            db.session.add(agreement)
            db.session.commit()
            flash('Agreement uploaded successfully!', 'success')
            return redirect(url_for('clients.company_detail', company_id=company_id))
    
    return render_template('clients/upload_agreement.html', form=form, company=company)

@bp.route('/brands')
@login_required
def brands():
    brands = Brand.query.join(Company).order_by(Company.name, Brand.name).all()
    return render_template('clients/brands.html', brands=brands)

@bp.route('/brand/new', methods=['GET', 'POST'])
@login_required
def new_brand():
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand(
            name=form.name.data,
            company_id=form.company_id.data,
            status=form.status.data
        )
        db.session.add(brand)
        db.session.commit()
        flash('Brand created successfully!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand.id))
    return render_template('clients/brand_form.html', form=form, title='New Brand')

@bp.route('/brand/<int:brand_id>')
@login_required
def brand_detail(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    return render_template('clients/brand_detail.html', brand=brand)

@bp.route('/brand/<int:brand_id>/team', methods=['GET', 'POST'])
@login_required
def assign_team(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = BrandTeamForm()
    
    if form.validate_on_submit():
        BrandTeam.query.filter_by(brand_id=brand_id).delete()
        
        key_responsible_id = int(form.key_responsible_id.data) if form.key_responsible_id.data and form.key_responsible_id.data != '0' else None
        
        for user_id in form.team_members.data:
            assignment = BrandTeam(
                brand_id=brand_id,
                team_member_id=user_id,
                is_key_responsible=(user_id == key_responsible_id)
            )
            db.session.add(assignment)
        
        db.session.commit()
        flash('Team assigned successfully!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand_id))
    
    elif request.method == 'GET':
        current_assignments = BrandTeam.query.filter_by(brand_id=brand_id).all()
        form.team_members.data = [a.team_member_id for a in current_assignments]
        key_responsible = next((a for a in current_assignments if a.is_key_responsible), None)
        if key_responsible:
            form.key_responsible_id.data = key_responsible.team_member_id
    
    return render_template('clients/assign_team.html', form=form, brand=brand)

@bp.route('/brand/<int:brand_id>/planning', methods=['GET', 'POST'])
@login_required
def planning_info(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = PlanningInfoForm()
    
    if form.validate_on_submit():
        planning = PlanningInfo(
            brand_id=brand_id,
            comments=form.comments.data,
            kpis='',  # Keep empty for backward compatibility
            created_by_id=current_user.id
        )
        db.session.add(planning)
        db.session.flush()  # Get planning ID before handling attachments
        
        # Handle file attachments
        if form.attachments.data:
            for file in form.attachments.data:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"planning_{planning.id}_{timestamp}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    attachment = PlanningAttachment(
                        planning_info_id=planning.id,
                        filename=file.filename,
                        file_path=filename
                    )
                    db.session.add(attachment)
        
        db.session.commit()
        flash('Planning information added!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand_id))
    
    planning_records = brand.planning_info
    return render_template('clients/planning_info.html', form=form, brand=brand, planning_records=planning_records)

@bp.route('/brand/<int:brand_id>/status', methods=['GET', 'POST'])
@login_required
def add_status_update(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = StatusUpdateForm()
    
    if form.validate_on_submit():
        update = StatusUpdate(
            brand_id=brand_id,
            date=form.date.data,
            comment=form.comment.data,
            evaluation=form.evaluation.data,
            created_by_id=current_user.id
        )
        db.session.add(update)
        db.session.commit()
        flash('Status update added!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand_id))
    
    return render_template('clients/status_update.html', form=form, brand=brand)

@bp.route('/contacts')
@login_required
def contacts():
    contacts = ClientContact.query.order_by(ClientContact.last_name, ClientContact.first_name).all()
    return render_template('clients/contacts.html', contacts=contacts)

@bp.route('/contact/new', methods=['GET', 'POST'])
@bp.route('/brand/<int:brand_id>/contact/new', methods=['GET', 'POST'])
@login_required
def new_contact(brand_id=None):
    form = ClientContactForm()
    
    # If coming from a brand page, pre-select that brand
    if brand_id and request.method == 'GET':
        brand = Brand.query.get_or_404(brand_id)
        form.brands.data = [brand_id]
    
    if form.validate_on_submit():
        contact = ClientContact(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            linkedin_url=form.linkedin_url.data,
            birthday_month=form.birthday_month.data if form.birthday_month.data != 0 else None,
            birthday_day=form.birthday_day.data,
            responsibility_description=form.responsibility_description.data,
            should_get_gift=form.should_get_gift.data,
            receive_newsletter=form.receive_newsletter.data,
            status=form.status.data
        )
        
        for brand_id in form.brands.data:
            brand = Brand.query.get(brand_id)
            if brand:
                contact.brands.append(brand)
        
        db.session.add(contact)
        db.session.commit()
        flash('Contact created successfully!', 'success')
        
        # If created from brand page, redirect back to brand
        if brand_id:
            return redirect(url_for('clients.brand_detail', brand_id=brand_id))
        return redirect(url_for('clients.contact_detail', contact_id=contact.id))
    
    return render_template('clients/contact_form.html', form=form, title='New Contact', brand_id=brand_id)

@bp.route('/contact/<int:contact_id>')
@login_required
def contact_detail(contact_id):
    contact = ClientContact.query.get_or_404(contact_id)
    return render_template('clients/contact_detail.html', contact=contact)

@bp.route('/contact/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = ClientContact.query.get_or_404(contact_id)
    form = ClientContactForm(contact=contact)
    
    if form.validate_on_submit():
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.email = form.email.data
        contact.phone = form.phone.data
        contact.linkedin_url = form.linkedin_url.data
        contact.birthday_month = form.birthday_month.data if form.birthday_month.data != 0 else None
        contact.birthday_day = form.birthday_day.data
        contact.responsibility_description = form.responsibility_description.data
        contact.should_get_gift = form.should_get_gift.data
        contact.receive_newsletter = form.receive_newsletter.data
        contact.status = form.status.data
        
        contact.brands.clear()
        for brand_id in form.brands.data:
            brand = Brand.query.get(brand_id)
            if brand:
                contact.brands.append(brand)
        
        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('clients.contact_detail', contact_id=contact.id))
    
    elif request.method == 'GET':
        form.first_name.data = contact.first_name
        form.last_name.data = contact.last_name
        form.email.data = contact.email
        form.phone.data = contact.phone
        form.linkedin_url.data = contact.linkedin_url
        form.birthday_month.data = contact.birthday_month or 0
        form.birthday_day.data = contact.birthday_day
        form.responsibility_description.data = contact.responsibility_description
        form.should_get_gift.data = contact.should_get_gift
        form.receive_newsletter.data = contact.receive_newsletter
        form.status.data = contact.status
        form.brands.data = [b.id for b in contact.brands]
    
    return render_template('clients/contact_form.html', form=form, title='Edit Contact', contact=contact)

@bp.route('/company/<int:company_id>/commitment', methods=['GET', 'POST'])
@login_required
def add_commitment(company_id):
    company = Company.query.get_or_404(company_id)
    form = CommitmentForm()
    
    if form.validate_on_submit():
        commitment = Commitment(
            company_id=company_id,
            media_group_id=form.media_group_id.data,
            year=form.year.data,
            amount=form.amount.data,
            currency=form.currency.data
        )
        db.session.add(commitment)
        try:
            db.session.commit()
            flash('Commitment added successfully!', 'success')
        except:
            db.session.rollback()
            flash('A commitment for this media group and year already exists!', 'error')
        return redirect(url_for('clients.company_detail', company_id=company_id))
    
    return render_template('clients/commitment_form.html', form=form, company=company)

@bp.route('/media-groups')
@login_required
def media_groups():
    media_groups = MediaGroup.query.order_by(MediaGroup.name).all()
    return render_template('clients/media_groups.html', media_groups=media_groups)

@bp.route('/media-group/new', methods=['GET', 'POST'])
@login_required
def new_media_group():
    form = MediaGroupForm()
    if form.validate_on_submit():
        media_group = MediaGroup(name=form.name.data)
        db.session.add(media_group)
        try:
            db.session.commit()
            flash('Media group created successfully!', 'success')
            return redirect(url_for('clients.media_groups'))
        except:
            db.session.rollback()
            flash('A media group with this name already exists!', 'error')
    
    return render_template('clients/media_group_form.html', form=form, title='New Media Group')

@bp.route('/brand/<int:brand_id>/meeting', methods=['GET', 'POST'])
@login_required
def add_meeting(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = KeyMeetingForm()
    
    if form.validate_on_submit():
        meeting = KeyMeeting(
            brand_id=brand_id,
            date=form.date.data,
            comment=form.comment.data,
            created_by_id=current_user.id
        )
        db.session.add(meeting)
        db.session.flush()
        
        # Handle file attachments
        if form.attachments.data:
            for file in form.attachments.data:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"meeting_{meeting.id}_{timestamp}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    attachment = MeetingAttachment(
                        meeting_id=meeting.id,
                        filename=file.filename,
                        file_path=filename
                    )
                    db.session.add(attachment)
        
        db.session.commit()
        flash('Meeting added successfully!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand_id))
    
    return render_template('clients/meeting_form.html', form=form, brand=brand)

@bp.route('/brand/<int:brand_id>/link', methods=['GET', 'POST'])
@login_required
def add_link(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = KeyLinkForm()
    
    if form.validate_on_submit():
        link = KeyLink(
            brand_id=brand_id,
            url=form.url.data,
            comment=form.comment.data,
            created_by_id=current_user.id
        )
        db.session.add(link)
        db.session.commit()
        flash('Link added successfully!', 'success')
        return redirect(url_for('clients.brand_detail', brand_id=brand_id))
    
    return render_template('clients/link_form.html', form=form, brand=brand)

@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/birthdays')
@login_required
def birthdays():
    # Get current month and next 2 months
    today = datetime.now()
    current_month = today.month
    
    # Get contacts with birthdays in the next 3 months
    upcoming_contacts = []
    for i in range(3):
        month = ((current_month - 1 + i) % 12) + 1
        contacts = ClientContact.query.filter(
            ClientContact.birthday_month == month,
            ClientContact.should_get_gift == True,
            ClientContact.status == 'active'
        ).order_by(ClientContact.birthday_day).all()
        
        for contact in contacts:
            # Check if gift already logged this year
            current_year_gift = Gift.query.filter_by(
                contact_id=contact.id, 
                year=today.year
            ).first()
            
            contact_info = {
                'contact': contact,
                'month': month,
                'current_year_gift': current_year_gift
            }
            upcoming_contacts.append(contact_info)
    
    # Sort by month and day
    upcoming_contacts.sort(key=lambda x: (x['month'], x['contact'].birthday_day or 0))
    
    return render_template('clients/birthdays.html', upcoming_contacts=upcoming_contacts, current_year=today.year)

@bp.route('/contact/<int:contact_id>/gift', methods=['GET', 'POST'])
@login_required
def add_gift(contact_id):
    contact = ClientContact.query.get_or_404(contact_id)
    form = GiftForm()
    
    # Pre-fill current year
    if request.method == 'GET':
        form.year.data = datetime.now().year
    
    if form.validate_on_submit():
        # Check if gift already exists for this year
        existing_gift = Gift.query.filter_by(
            contact_id=contact_id,
            year=form.year.data
        ).first()
        
        if existing_gift:
            flash('A gift has already been recorded for this contact in this year!', 'error')
        else:
            gift = Gift(
                contact_id=contact_id,
                year=form.year.data,
                gift_description=form.gift_description.data,
                gift_value=form.gift_value.data,
                sent_date=form.sent_date.data,
                notes=form.notes.data,
                created_by_id=current_user.id
            )
            db.session.add(gift)
            db.session.commit()
            flash('Gift recorded successfully!', 'success')
            return redirect(url_for('clients.birthdays'))
    
    # Get gift history for this contact
    gifts = Gift.query.filter_by(contact_id=contact_id).order_by(Gift.year.desc()).all()
    
    return render_template('clients/gift_form.html', form=form, contact=contact, gifts=gifts)

@bp.route('/status-updates')
@login_required
def status_updates():
    # Get filter parameters
    brand_id = request.args.get('brand_id', type=int)
    evaluation = request.args.get('evaluation')
    
    # Build query
    query = StatusUpdate.query.join(Brand).join(Company)
    
    if brand_id:
        query = query.filter(StatusUpdate.brand_id == brand_id)
    if evaluation:
        query = query.filter(StatusUpdate.evaluation == evaluation)
    
    # Get all status updates ordered by date
    updates = query.order_by(StatusUpdate.date.desc()).all()
    
    # Get all brands for filter dropdown
    brands = Brand.query.join(Company).order_by(Company.name, Brand.name).all()
    
    return render_template('clients/status_updates.html', 
                         updates=updates, 
                         brands=brands,
                         selected_brand_id=brand_id,
                         selected_evaluation=evaluation)

@bp.route('/status-update/new', methods=['GET', 'POST'])
@login_required
def new_status_update():
    # Create a custom form class with brand_id field
    class StatusUpdateFormWithBrand(StatusUpdateForm):
        brand_id = SelectField('Brand', coerce=int, validators=[DataRequired()])
    
    form = StatusUpdateFormWithBrand()
    
    # Add brand choices to form
    brands = Brand.query.join(Company).order_by(Company.name, Brand.name).all()
    form.brand_id.choices = [(b.id, f"{b.name} ({b.company.name})") for b in brands]
    
    if form.validate_on_submit():
        update = StatusUpdate(
            brand_id=form.brand_id.data,
            date=form.date.data,
            comment=form.comment.data,
            evaluation=form.evaluation.data,
            created_by_id=current_user.id
        )
        db.session.add(update)
        db.session.commit()
        flash('Status update added successfully!', 'success')
        return redirect(url_for('clients.status_updates'))
    
    # Set default date to today
    if request.method == 'GET':
        form.date.data = datetime.now().date()
    
    return render_template('clients/status_update_form.html', form=form, title='New Status Update')