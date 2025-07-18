# Agency Customer Success Management System

A professional CRM system built for media agencies to manage client relationships, brands, teams, and campaigns.

## Features

- **Team Management**: Manage agency team members with different roles (Management, Project Manager, Campaign Manager, ATL Planner, Digital Trafficer, etc.)
- **Client Companies**: Store company information including VAT code, address, bank account details
- **Document Management**: Upload and manage agreements (PDF files)
- **Brand Management**: Manage multiple brands per company
- **Contact Management**: Track client contacts with gift preferences and newsletter subscriptions
- **Team Assignment**: Assign team members to brands with key responsible person designation
- **Planning Information**: Add planning comments and KPIs for brands
- **Commitments**: Track yearly media commitments by company and media group
- **Status Updates**: Monitor brand health with status evaluations (Perfect/Medium/Risk)
- **Dashboard**: Overview of all activities and risk indicators

## Installation

1. Clone the repository:
```bash
cd agency_crm
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

5. Access the application at `http://localhost:5000`

## First Time Setup

1. Register a new user account
2. Login with your credentials
3. Start by creating Media Groups (Admin > Media Groups)
4. Add your first company
5. Create brands for the company
6. Add client contacts
7. Assign team members to brands

## Database Schema

The system uses SQLite with the following main entities:
- Users (Team members)
- Companies
- Brands
- Client Contacts
- Agreements
- Media Groups
- Commitments
- Planning Information
- Status Updates

## Security

- User authentication with password hashing
- Session management
- File upload restrictions (PDF only)
- Form validation and CSRF protection

## Technologies

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Tailwind CSS
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **File Uploads**: Werkzeug