from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime
import secrets
import hashlib

def generate_api_key():
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def require_api_key(f):
    """Decorator to require API key for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        
        # Check for API key in headers
        if 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']
        # Also check in query parameters as fallback
        elif 'api_key' in request.args:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'No API key provided'}), 401
        
        # Import here to avoid circular imports
        from app.models import APIKey
        
        # Hash the provided key and check against database
        hashed_key = hash_api_key(api_key)
        api_key_record = APIKey.query.filter_by(
            key_hash=hashed_key, 
            is_active=True
        ).first()
        
        if not api_key_record:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Update last used timestamp
        api_key_record.last_used_at = datetime.utcnow()
        api_key_record.use_count += 1
        
        from app import db
        db.session.commit()
        
        # Add API key record to request context
        request.api_key = api_key_record
        
        return f(*args, **kwargs)
    
    return decorated_function

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature for security"""
    expected = hashlib.sha256(
        f"{secret}{payload}".encode()
    ).hexdigest()
    return secrets.compare_digest(expected, signature)