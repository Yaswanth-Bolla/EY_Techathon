document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('department');
    const subdepartmentSelect = document.getElementById('subdepartment');
    const teamSelect = document.getElementById('team');
    const projectSelect = document.getElementById('project');

    // Function to update select options
    async function updateSelect(selectElement, url, defaultText) {
        try {
            // Clear current options
            selectElement.innerHTML = '';
            
            if (!url) {
                // If no URL provided, show default text
                const option = new Option(defaultText, '0');
                selectElement.add(option);
                return;
            }

            // Fetch data
            const response = await fetch(url);
            const items = await response.json();

            // Add default option
            const defaultOption = new Option(defaultText, '0');
            selectElement.add(defaultOption);

            // Add options
            items.forEach(item => {
                const option = new Option(item.name, item.id);
                selectElement.add(option);
            });
        } catch (error) {
            console.error('Error fetching data:', error);
            // Add error option
            selectElement.innerHTML = '';
            const errorOption = new Option('Error loading options', '0');
            selectElement.add(errorOption);
        }
    }

    // Update subdepartments when department selection changes
    departmentSelect.addEventListener('change', function() {
        const departmentId = this.value;
        updateSelect(
            subdepartmentSelect,
            departmentId !== '0' ? `/get_subdepartments/${departmentId}` : null,
            'Select Department First'
        );
        // Reset dependent dropdowns
        updateSelect(teamSelect, null, 'Select Sub-Department First');
        updateSelect(projectSelect, null, 'Select Team First');
    });

    // Update teams when subdepartment selection changes
    subdepartmentSelect.addEventListener('change', function() {
        const subdepartmentId = this.value;
        updateSelect(
            teamSelect,
            subdepartmentId !== '0' ? `/get_teams/${subdepartmentId}` : null,
            'Select Sub-Department First'
        );
        // Reset dependent dropdown
        updateSelect(projectSelect, null, 'Select Team First');
    });

    // Update projects when team selection changes
    teamSelect.addEventListener('change', function() {
        const teamId = this.value;
        updateSelect(
            projectSelect,
            teamId !== '0' ? `/get_projects/${teamId}` : null,
            'Select Team First'
        );
    });

    // Initialize dropdowns
    updateSelect(subdepartmentSelect, null, 'Select Department First');
    updateSelect(teamSelect, null, 'Select Sub-Department First');
    updateSelect(projectSelect, null, 'Select Team First');
});
