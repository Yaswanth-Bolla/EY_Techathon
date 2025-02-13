from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Department, Team, Project, Process, InternalDependency, ExternalDependency, ProcessInput, ProcessOutput, ImpactAssessment

def init_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='ADMIN',
            join_date=datetime.utcnow()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        # Create department managers first
        dept_managers = {}
        for i in range(1, 4):
            manager = User(
                username=f'manager_{i}',
                email=f'manager_{i}@example.com',
                role='MANAGER',
                join_date=datetime.utcnow()
            )
            manager.set_password('password')
            db.session.add(manager)
            dept_managers[i] = manager
        db.session.commit()

        # Create main departments
        departments = {
            'Technology': ['Software Development', 'Infrastructure', 'Data Science'],
            'Finance': ['Accounting', 'Investment', 'Risk Management'],
            'HR': ['Recruitment', 'Training', 'Employee Relations']
        }

        dept_count = 1
        for dept_name, subdepts in departments.items():
            # Create main department with its manager
            dept = Department(
                name=dept_name,
                description=f'{dept_name} Department',
                department_type='department',
                head_id=dept_managers[dept_count].id
            )
            db.session.add(dept)
            db.session.commit()

            # Create subdepartment managers
            subdept_managers = []
            for i in range(len(subdepts)):
                manager = User(
                    username=f'{dept_name.lower()}_manager_{i+1}',
                    email=f'{dept_name.lower()}_manager_{i+1}@example.com',
                    role='MANAGER',
                    department_id=dept.id,
                    join_date=datetime.utcnow()
                )
                manager.set_password('password')
                db.session.add(manager)
                subdept_managers.append(manager)
            db.session.commit()

            # Create subdepartments with their managers
            for i, subdept_name in enumerate(subdepts):
                subdept = Department(
                    name=subdept_name,
                    description=f'{subdept_name} Sub-Department',
                    department_type='subdepartment',
                    parent_id=dept.id,
                    head_id=subdept_managers[i].id
                )
                db.session.add(subdept)
                db.session.commit()

                # Create team leaders
                team_leaders = []
                for j in range(2):  # 2 teams per subdepartment
                    leader = User(
                        username=f'{subdept_name.lower()}_leader_{j+1}'.replace(' ', '_'),
                        email=f'{subdept_name.lower()}_leader_{j+1}@example.com'.replace(' ', '_'),
                        role='TEAM_LEADER',
                        department_id=subdept.id,
                        join_date=datetime.utcnow()
                    )
                    leader.set_password('password')
                    db.session.add(leader)
                    team_leaders.append(leader)
                db.session.commit()

                # Create teams with their leaders
                for j in range(2):  # 2 teams per subdepartment
                    team = Team(
                        name=f'{subdept_name} Team {j+1}',
                        description=f'Team working on {subdept_name} Team {j+1}',
                        department_id=subdept.id,
                        leader_id=team_leaders[j].id
                    )
                    db.session.add(team)
                    db.session.commit()

                    # Create projects for each team
                    for k in range(2):  # 2 projects per team
                        project = Project(
                            name=f'{team.name} Project {k+1}',
                            description=f'Project {k+1} for {team.name}',
                            team_id=team.id,
                            start_date=datetime.utcnow(),
                            end_date=datetime.utcnow() + timedelta(days=180),
                            status='active'
                        )
                        db.session.add(project)
                    db.session.commit()

            dept_count += 1

        # Create sample BIA processes
        processes = [
            {
                'name': 'Financial Reporting',
                'department': 'Finance',
                'description': 'Monthly and quarterly financial reporting process',
                'rto_hours': 24,
                'criticality_level': 'Critical',
                'internal_deps': ['Accounting', 'Investment'],
                'external_deps': [
                    {'vendor': 'SAP', 'service': 'ERP System', 'contact': 'support@sap.com'},
                    {'vendor': 'Oracle', 'service': 'Database', 'contact': 'support@oracle.com'}
                ],
                'inputs': [
                    {'name': 'Transaction Data', 'type': 'Data', 'desc': 'Daily transaction records'},
                    {'name': 'Bank Statements', 'type': 'Document', 'desc': 'Monthly bank reconciliation'}
                ],
                'outputs': [
                    {'name': 'Financial Statements', 'type': 'Report', 'desc': 'Monthly P&L and Balance Sheet'},
                    {'name': 'Compliance Reports', 'type': 'Document', 'desc': 'Regulatory compliance reports'}
                ]
            },
            {
                'name': 'Data Center Operations',
                'department': 'Technology',
                'description': 'Core infrastructure and server management',
                'rto_hours': 4,
                'criticality_level': 'Critical',
                'internal_deps': ['Infrastructure', 'Software Development'],
                'external_deps': [
                    {'vendor': 'AWS', 'service': 'Cloud Infrastructure', 'contact': 'enterprise@aws.com'},
                    {'vendor': 'Cisco', 'service': 'Network Equipment', 'contact': 'support@cisco.com'}
                ],
                'inputs': [
                    {'name': 'System Logs', 'type': 'Data', 'desc': 'Server and network logs'},
                    {'name': 'Backup Data', 'type': 'Data', 'desc': 'Daily system backups'}
                ],
                'outputs': [
                    {'name': 'Uptime Reports', 'type': 'Report', 'desc': 'System availability metrics'},
                    {'name': 'Incident Reports', 'type': 'Document', 'desc': 'Security and system incidents'}
                ]
            },
            {
                'name': 'Employee Onboarding',
                'department': 'HR',
                'description': 'New employee onboarding and orientation process',
                'rto_hours': 48,
                'criticality_level': 'Medium',
                'internal_deps': ['Training', 'Employee Relations'],
                'external_deps': [
                    {'vendor': 'Workday', 'service': 'HR System', 'contact': 'support@workday.com'},
                    {'vendor': 'DocuSign', 'service': 'Document Signing', 'contact': 'support@docusign.com'}
                ],
                'inputs': [
                    {'name': 'Employee Details', 'type': 'Data', 'desc': 'New hire information'},
                    {'name': 'Policy Documents', 'type': 'Document', 'desc': 'Company policies and procedures'}
                ],
                'outputs': [
                    {'name': 'Employee Records', 'type': 'Document', 'desc': 'Completed onboarding documents'},
                    {'name': 'Access Cards', 'type': 'Equipment', 'desc': 'Building and system access'}
                ]
            }
        ]

        # Add processes to database
        for proc_data in processes:
            # Create process
            dept = Department.query.filter_by(name=proc_data['department']).first()
            process = Process(
                name=proc_data['name'],
                department_id=dept.id,
                description=proc_data['description'],
                rto_hours=proc_data['rto_hours'],
                criticality_level=proc_data['criticality_level']
            )
            db.session.add(process)
            db.session.flush()  # Get process ID

            # Add internal dependencies
            for dep_name in proc_data['internal_deps']:
                dep_dept = Department.query.filter_by(name=dep_name).first()
                if dep_dept:
                    dep = InternalDependency(
                        process_id=process.id,
                        dependent_department_id=dep_dept.id,
                        description=f'Dependency on {dep_name}'
                    )
                    db.session.add(dep)

            # Add external dependencies
            for ext_dep in proc_data['external_deps']:
                dep = ExternalDependency(
                    process_id=process.id,
                    vendor_name=ext_dep['vendor'],
                    service_description=ext_dep['service'],
                    contact_info=ext_dep['contact']
                )
                db.session.add(dep)

            # Add inputs
            for input_data in proc_data['inputs']:
                input_item = ProcessInput(
                    process_id=process.id,
                    name=input_data['name'],
                    description=input_data['desc'],
                    resource_type=input_data['type']
                )
                db.session.add(input_item)

            # Add outputs
            for output_data in proc_data['outputs']:
                output_item = ProcessOutput(
                    process_id=process.id,
                    name=output_data['name'],
                    description=output_data['desc'],
                    deliverable_type=output_data['type']
                )
                db.session.add(output_item)

            # Add impact assessment
            impact = ImpactAssessment(
                process_id=process.id,
                financial_impact=4 if proc_data['criticality_level'] == 'Critical' else 2,
                operational_impact=4 if proc_data['criticality_level'] == 'Critical' else 3,
                legal_impact=3,
                reputational_impact=3,
                notes=f'Impact assessment for {proc_data["name"]}'
            )
            db.session.add(impact)

        db.session.commit()

        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
