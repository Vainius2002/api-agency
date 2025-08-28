from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import APIKey, Webhook, db
from app.api_auth import generate_api_key, hash_api_key
import secrets
from datetime import datetime

@api_bp.route('/keys', methods=['GET'])
@login_required
def manage_api_keys():
    """View and manage API keys"""
    api_keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return render_template('api/api_keys.html', api_keys=api_keys)

@api_bp.route('/keys/create', methods=['POST'])
@login_required
def create_api_key():
    """Create a new API key"""
    name = request.form.get('name', 'Unnamed Key')
    
    # Generate new API key
    raw_key = generate_api_key()
    hashed_key = hash_api_key(raw_key)
    
    # Save to database
    api_key = APIKey(
        name=name,
        key_hash=hashed_key,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(api_key)
    db.session.commit()
    
    flash(f'API Key created: {raw_key} (Save this key, it won\'t be shown again!)', 'warning')
    return redirect(url_for('api.manage_api_keys'))

@api_bp.route('/keys/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_api_key(key_id):
    """Toggle API key active status"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    api_key.is_active = not api_key.is_active
    db.session.commit()
    
    status = 'activated' if api_key.is_active else 'deactivated'
    flash(f'API Key {api_key.name} {status}', 'success')
    return redirect(url_for('api.manage_api_keys'))

@api_bp.route('/keys/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    db.session.delete(api_key)
    db.session.commit()
    
    flash(f'API Key {api_key.name} deleted', 'success')
    return redirect(url_for('api.manage_api_keys'))

@api_bp.route('/webhooks', methods=['GET'])
@login_required
def manage_webhooks():
    """View and manage webhooks"""
    webhooks = Webhook.query.filter_by(user_id=current_user.id).all()
    return render_template('api/webhooks.html', webhooks=webhooks)

@api_bp.route('/webhooks/create', methods=['POST'])
@login_required
def create_webhook():
    """Create a new webhook"""
    name = request.form.get('name', 'Unnamed Webhook')
    url = request.form.get('url')
    events = request.form.getlist('events')
    
    if not url:
        flash('Webhook URL is required', 'error')
        return redirect(url_for('api.manage_webhooks'))
    
    # Generate webhook secret
    secret = secrets.token_urlsafe(32)
    
    webhook = Webhook(
        name=name,
        url=url,
        secret=secret,
        events=events,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(webhook)
    db.session.commit()
    
    flash(f'Webhook created with secret: {secret} (Save this secret!)', 'warning')
    return redirect(url_for('api.manage_webhooks'))

@api_bp.route('/webhooks/<int:webhook_id>/toggle', methods=['POST'])
@login_required
def toggle_webhook(webhook_id):
    """Toggle webhook active status"""
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=current_user.id).first_or_404()
    webhook.is_active = not webhook.is_active
    db.session.commit()
    
    status = 'activated' if webhook.is_active else 'deactivated'
    flash(f'Webhook {webhook.name} {status}', 'success')
    return redirect(url_for('api.manage_webhooks'))

@api_bp.route('/webhooks/<int:webhook_id>/delete', methods=['POST'])
@login_required
def delete_webhook(webhook_id):
    """Delete a webhook"""
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=current_user.id).first_or_404()
    db.session.delete(webhook)
    db.session.commit()
    
    flash(f'Webhook {webhook.name} deleted', 'success')
    return redirect(url_for('api.manage_webhooks'))