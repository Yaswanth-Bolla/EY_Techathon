# EY Resource Management System

A comprehensive web application for managing organizational resources, departments, and users.

## Features

### User Management
- Multiple user roles: Master Admin, Organization Admin, Department Admin, and Regular Users
- Secure user authentication and authorization
- User profile management with profile pictures

### Department Management
- Hierarchical department structure
- Department head assignment
- Sub-department creation and management
- Resource allocation to departments

### Resource Management
- Track and manage various types of resources
- Resource assignment to users and departments
- Resource status tracking
- Resource usage history

### Admin Dashboard
- Role-specific dashboards with relevant statistics
- User activity monitoring
- Resource utilization tracking
- Department performance metrics

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Password Security**: Bcrypt

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_database.py
```

## Default Admin Credentials

- **Email**: master@example.com
- **Password**: admin123

## Project Structure

```
EY/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── init_db.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       └── dashboard.html
├── requirements.txt
└── README.md
```

## User Roles and Permissions

1. **Master Admin**
   - Full system access
   - Create/manage organization admins
   - View system-wide statistics
   - Manage all departments and resources

2. **Organization Admin**
   - Manage department admins
   - Create/manage departments
   - View organization-wide statistics
   - Manage resources within their organization

3. **Department Admin**
   - Manage users within their department
   - Assign resources to users
   - View department statistics
   - Manage department resources

4. **Regular User**
   - View assigned resources
   - Update profile information
   - View department information

## Security Features

- Password hashing using Bcrypt
- CSRF protection on all forms
- Role-based access control
- Secure session management
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
