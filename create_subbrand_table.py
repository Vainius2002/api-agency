from app import create_app, db
from app.models import Subbrand

app = create_app()

with app.app_context():
    # Create the subbrand table
    db.create_all()
    print("Subbrand table created successfully!")