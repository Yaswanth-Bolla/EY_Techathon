# Business Continuity Management System

A comprehensive web application for managing business continuity planning, including Business Impact Analysis (BIA), resource management, and facility tracking.

## Features

### User Management
- User registration and authentication
- Role-based access control (Admin and User roles)
- Profile management with avatar support
- Password reset functionality

### Department Management
- Create and manage departments
- Track department heads and members
- Department-specific resource allocation

### Resource Management
- Track IT and non-IT resources
- Resource allocation to departments
- Resource status monitoring
- CSV import support for bulk resource updates

### Facility Management
- Track office locations and facilities
- Monitor facility status and capacity
- Manage facility-specific resources
- Link facilities to departments

### Business Impact Analysis (BIA)
- Comprehensive BIA dashboard with key metrics:
  - Total processes count
  - Critical processes count
  - Average Recovery Time Objective (RTO)
  - Impact distribution across criticality levels
- Process management:
  - Add and edit business processes
  - Assign processes to departments
  - Set RTO and criticality levels
  - Track internal and external dependencies
  - Document process inputs and outputs
- Impact Assessment:
  - Rate impacts on 4 dimensions:
    - Financial Impact
    - Operational Impact
    - Legal Impact
    - Reputational Impact
  - Add detailed impact notes
- Advanced filtering:
  - Filter processes by department
  - Filter by criticality level
- Export functionality:
  - Export BIA data to Excel
  - Comprehensive reports including process details and impact assessments

## BIA Metrics Calculation

### Dashboard Metrics

1. **Total Processes**
   - Simple count of all processes in the system
   ```python
   total_processes = Process.query.count()
   ```

2. **Critical Processes**
   - Count of processes with criticality level "Critical"
   ```python
   critical_processes = Process.query.filter_by(criticality_level='Critical').count()
   ```

3. **Average RTO (Recovery Time Objective)**
   - Mean of RTO hours across all processes
   - Null RTOs are excluded from calculation
   ```python
   processes = Process.query.filter(Process.rto_hours.isnot(None)).all()
   avg_rto = sum(p.rto_hours for p in processes) / len(processes) if processes else 0
   ```

4. **Impact Distribution**
   - Count of processes by criticality level
   ```python
   impact_distribution = {
       'Critical': Process.query.filter_by(criticality_level='Critical').count(),
       'High': Process.query.filter_by(criticality_level='High').count(),
       'Medium': Process.query.filter_by(criticality_level='Medium').count(),
       'Low': Process.query.filter_by(criticality_level='Low').count()
   }
   ```

### Impact Assessment Scoring

Each process is evaluated on four impact dimensions:

1. **Financial Impact (0-4)**
   - 0: No financial impact
   - 1: Minor impact (<$10,000)
   - 2: Moderate impact ($10,000-$100,000)
   - 3: Major impact ($100,000-$1,000,000)
   - 4: Severe impact (>$1,000,000)

2. **Operational Impact (0-4)**
   - 0: No operational disruption
   - 1: Minor disruption (few hours)
   - 2: Moderate disruption (1-2 days)
   - 3: Major disruption (3-5 days)
   - 4: Severe disruption (>5 days)

3. **Legal Impact (0-4)**
   - 0: No legal implications
   - 1: Minor regulatory issues
   - 2: Moderate compliance violations
   - 3: Major legal liabilities
   - 4: Severe legal consequences

4. **Reputational Impact (0-4)**
   - 0: No reputational impact
   - 1: Minor local impact
   - 2: Moderate local/minor national impact
   - 3: Major national impact
   - 4: Severe national/international impact

### Criticality Level Determination

Process criticality is determined based on the highest impact score:

```python
def determine_criticality(impact_assessment):
    max_impact = max(
        impact_assessment.financial_impact,
        impact_assessment.operational_impact,
        impact_assessment.legal_impact,
        impact_assessment.reputational_impact
    )
    
    if max_impact == 4:
        return 'Critical'
    elif max_impact == 3:
        return 'High'
    elif max_impact == 2:
        return 'Medium'
    else:
        return 'Low'
```

### Recovery Time Objective (RTO)

RTO is measured in hours and represents the maximum acceptable time for restoring a business process after a disruption. The RTO value helps in:

1. **Priority Setting**
   - Critical processes (RTO < 24 hours)
   - High priority processes (RTO 24-72 hours)
   - Medium priority processes (RTO 73-168 hours)
   - Low priority processes (RTO > 168 hours)

2. **Resource Allocation**
   - Processes with shorter RTOs receive priority for resource allocation
   - Used to determine backup and redundancy requirements

3. **Recovery Strategy**
   - Influences the selection of recovery strategies
   - Determines required investment in business continuity measures

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bcms.git
cd bcms
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
python init_db.py  # Adds initial data
```

5. Run the application:
```bash
flask run
```

## Dependencies

- Flask - Web framework
- Flask-SQLAlchemy - Database ORM
- Flask-Login - User authentication
- Flask-WTF - Form handling
- Flask-Migrate - Database migrations
- Pandas - Data processing and Excel export
- Pillow - Image processing
- openpyxl - Excel file handling
- Werkzeug - Password hashing and utilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
