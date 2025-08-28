#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Company, Brand, ClientContact, MediaGroup

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Company': Company, 'Brand': Brand, 
            'ClientContact': ClientContact, 'MediaGroup': MediaGroup}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default media groups if they don't exist
        if MediaGroup.query.count() == 0:
            default_groups = ['TV3 Group', 'M-1 Group', 'LRT', 'Radio Center', 'Clear Channel']
            for group_name in default_groups:
                mg = MediaGroup(name=group_name)
                db.session.add(mg)
            db.session.commit()
            print("Default media groups created.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)