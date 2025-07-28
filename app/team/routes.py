from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.team import bp
from app.models import User
from app import db
from app.auth.forms import RegistrationForm
from wtforms import PasswordField
from wtforms.validators import Optional, ValidationError

class TeamMemberForm(RegistrationForm):
    password = PasswordField('Password', validators=[Optional()])
    password2 = PasswordField('Repeat Password', validators=[Optional()])
    
    def __init__(self, user=None, *args, **kwargs):
        super(TeamMemberForm, self).__init__(*args, **kwargs)
        self.user = user
        if user:
            self.submit.label.text = 'Update Team Member'
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            # If editing, allow the same email for the current user
            if self.user and self.user.id == user.id:
                return
            raise ValidationError('Please use a different email address.')

@bp.route('/')
@login_required
def index():
    team_members = User.query.order_by(User.last_name).all()
    return render_template('team/index.html', team_members=team_members)

@bp.route('/<int:user_id>')
@login_required
def member_detail(user_id):
    member = User.query.get_or_404(user_id)
    return render_template('team/member_detail.html', member=member)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_member():
    form = TeamMemberForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            birthday=form.birthday.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Team member created successfully!', 'success')
        return redirect(url_for('team.member_detail', user_id=user.id))
    return render_template('team/member_form.html', form=form, title='New Team Member')

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(user_id):
    member = User.query.get_or_404(user_id)
    form = TeamMemberForm(user=member)
    
    if form.validate_on_submit():
        member.email = form.email.data
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.phone = form.phone.data
        member.birthday = form.birthday.data
        member.role = form.role.data
        
        if form.password.data:
            member.set_password(form.password.data)
        
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('team.member_detail', user_id=member.id))
    
    elif request.method == 'GET':
        form.email.data = member.email
        form.first_name.data = member.first_name
        form.last_name.data = member.last_name
        form.phone.data = member.phone
        form.birthday.data = member.birthday
        form.role.data = member.role
    
    return render_template('team/member_form.html', form=form, title='Edit Team Member', member=member)

@bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(user_id):
    member = User.query.get_or_404(user_id)
    if member.id == current_user.id:
        flash('You cannot deactivate your own account!', 'error')
    else:
        member.is_active = not member.is_active
        db.session.commit()
        status = 'activated' if member.is_active else 'deactivated'
        flash(f'Team member {status} successfully!', 'success')
    return redirect(url_for('team.index'))