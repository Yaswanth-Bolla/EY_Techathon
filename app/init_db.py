from app import create_app, db, bcrypt
from app.models import User, Department, Resource, Facility
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()

        # Create initial departments
        departments = {
            'IT': {
                'name': 'IT Department',
                'description': 'Information Technology',
                'sub_departments': [
                    {'name': 'Software Development', 'description': 'Software Development Team'},
                    {'name': 'Infrastructure', 'description': 'IT Infrastructure Team'},
                    {'name': 'Support', 'description': 'IT Support Team'}
                ]
            },
            'HR': {
                'name': 'HR Department',
                'description': 'Human Resources',
                'sub_departments': [
                    {'name': 'Recruitment', 'description': 'Talent Acquisition Team'},
                    {'name': 'Training', 'description': 'Learning and Development'},
                    {'name': 'Employee Relations', 'description': 'HR Operations'}
                ]
            },
            'Finance': {
                'name': 'Finance Department',
                'description': 'Finance and Accounting',
                'sub_departments': [
                    {'name': 'Accounting', 'description': 'General Accounting'},
                    {'name': 'Payroll', 'description': 'Payroll Management'},
                    {'name': 'Treasury', 'description': 'Treasury Management'}
                ]
            },
            'Operations': {
                'name': 'Operations Department',
                'description': 'Operations Management',
                'sub_departments': [
                    {'name': 'Quality Control', 'description': 'Quality Assurance'},
                    {'name': 'Logistics', 'description': 'Supply Chain'},
                    {'name': 'Facilities', 'description': 'Facility Management'}
                ]
            }
        }

        # Create master admin
        master_admin = User(
            username='masteradmin',
            email='master@example.com',
            role='MASTER_ADMIN',
            join_date=datetime.utcnow()
        )
        master_admin.set_password('admin123')
        db.session.add(master_admin)
        db.session.commit()

        # Create and store departments with their admins
        dept_objects = {}
        for main_dept_key, main_dept_data in departments.items():
            # Create main department
            main_dept = Department(
                name=main_dept_data['name'],
                description=main_dept_data['description']
            )
            db.session.add(main_dept)
            db.session.commit()
            dept_objects[main_dept_key] = main_dept

            # Create organization admin for each main department
            org_admin = User(
                username=f'orgadmin_{main_dept_key.lower()}',
                email=f'org_{main_dept_key.lower()}@example.com',
                role='ORG_ADMIN',
                department_id=main_dept.id,
                join_date=datetime.utcnow()
            )
            org_admin.set_password('admin123')
            db.session.add(org_admin)
            db.session.commit()

            # Create sub-departments and their admins
            for sub_dept_data in main_dept_data['sub_departments']:
                sub_dept = Department(
                    name=sub_dept_data['name'],
                    description=sub_dept_data['description'],
                    parent_id=main_dept.id
                )
                db.session.add(sub_dept)
                db.session.commit()

                # Create department admin
                dept_admin = User(
                    username=f"deptadmin_{sub_dept_data['name'].lower().replace(' ', '_')}",
                    email=f"dept_{sub_dept_data['name'].lower().replace(' ', '_')}@example.com",
                    role='DEPT_ADMIN',
                    department_id=sub_dept.id,
                    manager_id=org_admin.id,
                    join_date=datetime.utcnow()
                )
                dept_admin.set_password('admin123')
                db.session.add(dept_admin)
                db.session.commit()

                # Set department head
                sub_dept.head_id = dept_admin.id
                db.session.commit()

                # Create some regular users for each sub-department
                for i in range(1, 4):
                    user = User(
                        username=f"user_{sub_dept_data['name'].lower().replace(' ', '_')}_{i}",
                        email=f"user_{sub_dept_data['name'].lower().replace(' ', '_')}_{i}@example.com",
                        role='USER',
                        department_id=sub_dept.id,
                        manager_id=dept_admin.id,
                        join_date=datetime.utcnow()
                    )
                    user.set_password('user123')
                    db.session.add(user)
                db.session.commit()

        # Create resources for each department
        resource_types = {
            'IT': ['Laptop', 'Desktop', 'Server', 'Network Equipment'],
            'HR': ['Training Room', 'Interview Room', 'HR Software License'],
            'Finance': ['Financial Software', 'Accounting System', 'Payment Terminal'],
            'Operations': ['Vehicle', 'Warehouse Space', 'Equipment']
        }

        for dept_key, types in resource_types.items():
            dept = dept_objects[dept_key]
            for type_ in types:
                for i in range(1, 4):
                    resource = Resource(
                        name=f'{type_} {i}',
                        type=type_,
                        status='available',
                        department_id=dept.id
                    )
                    db.session.add(resource)
        db.session.commit()

        # Create facilities for each department
        facility_types = {
            'IT': ['Server Room', 'Development Lab', 'Tech Hub'],
            'HR': ['Training Center', 'Interview Room', 'Conference Room'],
            'Finance': ['Secure Room', 'Meeting Room', 'Archive'],
            'Operations': ['Warehouse', 'Loading Dock', 'Control Room']
        }

        for dept_key, types in facility_types.items():
            dept = dept_objects[dept_key]
            for type_ in types:
                facility = Facility(
                    name=f'{dept_key} {type_}',
                    type=type_,
                    capacity=20,
                    location=f'Floor {dept.id}',
                    department_id=dept.id,
                    status='available'
                )
                db.session.add(facility)
        db.session.commit()

if __name__ == '__main__':
    init_db()
