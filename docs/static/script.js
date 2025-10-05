// Simple tab navigation functions
function openTab(button, tabName) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(function(content) {
        content.classList.remove('active');
    });

    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // Show the selected tab content
    const tabElement = document.getElementById(tabName);
    if (tabElement) {
        tabElement.classList.add('active');
    }

    // Add active class to the clicked button
    if (button) {
        button.classList.add('active');
    }
}

function openSubTab(button, subTabName) {
    // Hide all sub-tab content
    const subTabContents = document.querySelectorAll('.sub-tab-content');
    subTabContents.forEach(function(content) {
        content.classList.remove('active');
    });

    // Remove active class from all sub-tab buttons
    const subTabButtons = document.querySelectorAll('.sub-tab-button');
    subTabButtons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // Show the selected sub-tab content
    const subTabElement = document.getElementById(subTabName);
    if (subTabElement) {
        subTabElement.classList.add('active');
    }

    // Add active class to the clicked button
    if (button) {
        button.classList.add('active');
    }
}

// Clock function
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
});

function updateClock() {
    try {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const timeString = hours + ':' + minutes + ':' + seconds;

        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        const dateString = now.toLocaleDateString('fr-FR', options);

        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');

        if (timeElement) {
            timeElement.textContent = timeString;
        }
        if (dateElement) {
            dateElement.textContent = dateString;
        }

        console.log('Clock updated:', timeString, dateString);
    } catch (error) {
        console.error('Error updating clock:', error);
    }
}

// Placeholder functions for other features
function getStudentDashboard() {
    const studentId = document.getElementById('dashboard-student-id').value;
    if (!studentId) {
        alert('Veuillez entrer un ID étudiant');
        return;
    }
    // Add fetch logic here
    console.log('Getting dashboard for student:', studentId);
}

function checkGraduationEligibility() {
    const studentId = document.getElementById('graduation-student-id').value;
    if (!studentId) {
        alert('Veuillez entrer un ID étudiant');
        return;
    }
    // Add fetch logic here
    console.log('Checking graduation for student:', studentId);
}

// Add other functions as needed
