// Get references to the elements
const editProfileButton = document.getElementById('editProfileButton');
const saveCancelButtons = document.getElementById('saveCancelButtons');
const firstNameDisplay = document.getElementById('firstNameDisplay');
const firstNameInput = document.getElementById('firstNameInput');
const emailDisplay = document.getElementById('emailDisplay');
const lastNameDisplay = document.getElementById('lastNameDisplay');
const lastNameInput = document.getElementById('lastNameInput');
const emailInput = document.getElementById('emailInput');
const departmentDisplay = document.getElementById('departmentDisplay');
const departmentInput = document.getElementById('departmentInput');

// Add event listener to the Edit Profile button
editProfileButton.addEventListener('click', function() {
    // Show input fields and hide display
    firstNameDisplay.style.display = 'none';
    firstNameInput.style.display = 'block';
    lastNameDisplay.style.display = 'none';
    lastNameInput.style.display = 'block';
    emailDisplay.style.display = 'none';
    emailInput.style.display = 'block';
    departmentDisplay.style.display = 'none';
    departmentInput.style.display = 'block';

    // Show save and cancel buttons
    editProfileButton.style.display = 'none';
    saveCancelButtons.style.display = 'block'; // Show save/cancel buttons
});

document.getElementById('saveChangesButton').addEventListener('click', function() {
    // Get values from input fields
    const newFirstName = document.getElementById('firstNameInput').value;
    const newLastName = document.getElementById('lastNameInput').value;
    const newEmail = document.getElementById('emailInput').value;
    const newDepartment = document.getElementById('departmentInput').value;

    // Update the display fields with new values
    document.getElementById('firstNameDisplay').textContent = newFirstName;
    document.getElementById('lastNameDisplay').textContent = newLastName;
    document.getElementById('emailDisplay').textContent = newEmail;
    document.getElementById('departmentDisplay').textContent = newDepartment;

    // Hide input fields and show display fields
    firstNameDisplay.style.display = 'block';
    firstNameInput.style.display = 'none';
    lastNameDisplay.style.display = 'block';
    lastNameInput.style.display = 'none';
    emailInput.style.display = 'none';
    departmentInput.style.display = 'none';
    emailDisplay.style.display = 'block';
    departmentDisplay.style.display = 'block';

    // Hide save/cancel buttons
    document.getElementById('saveCancelButtons').style.display = 'none';
    document.getElementById('editProfileButton').style.display = 'block';
    
    // Submit form to update database
    document.getElementById('editProfileForm').submit();
});

document.getElementById('cancelEditButton').addEventListener('click', function() {
    // Hide input fields and show display fields
    firstNameDisplay.style.display = 'block';
    firstNameInput.style.display = 'none';
    lastNameDisplay.style.display = 'block';
    lastNameInput.style.display = 'none';
    emailInput.style.display = 'none';
    departmentInput.style.display = 'none';
    emailDisplay.style.display = 'block';
    departmentDisplay.style.display = 'block';

    // Hide save/cancel buttons
    document.getElementById('saveCancelButtons').style.display = 'none';
    document.getElementById('editProfileButton').style.display = 'block';
});