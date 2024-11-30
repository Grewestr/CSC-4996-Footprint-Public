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

// Get references to the elements
// const editProfileButton = document.getElementById('editProfileButton');
// const saveCancelButtons = document.getElementById('saveCancelButtons');
// const firstNameDisplay = document.getElementById('firstNameDisplay');
// const firstNameInput = document.getElementById('firstNameInput');
// const emailDisplay = document.getElementById('emailDisplay');
// const lastNameDisplay = document.getElementById('lastNameDisplay');
// const lastNameInput = document.getElementById('lastNameInput');
// const emailInput = document.getElementById('emailInput');
// const departmentDisplay = document.getElementById('departmentDisplay');
// const departmentInput = document.getElementById('departmentInput');

// // Add event listener to the Edit Profile button
// editProfileButton.addEventListener('click', function() {
//     // Show input fields and hide display
//     firstNameDisplay.style.display = 'none';
//     firstNameInput.style.display = 'block';
//     lastNameDisplay.style.display = 'none';
//     lastNameInput.style.display = 'block';
//     emailDisplay.style.display = 'none';
//     emailInput.style.display = 'block';
//     departmentDisplay.style.display = 'none';
//     departmentInput.style.display = 'block';

//     // Show save and cancel buttons
//     editProfileButton.style.display = 'none';
//     saveCancelButtons.style.display = 'block'; // Show save/cancel buttons
// });

// document.getElementById('saveChangesButton').addEventListener('click', async function () {
//     const newFirstName = firstNameInput.value;
//     const newLastName = lastNameInput.value;
//     const newEmail = emailInput.value;
//     const newDepartment = departmentInput.value;

//     const formData = new FormData();
//     formData.append('first_name', newFirstName);
//     formData.append('last_name', newLastName);
//     formData.append('email', newEmail);
//     formData.append('department_name', newDepartment);

//     try {
//         const response = await fetch('/edit_profile/', {
//             method: 'POST',
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest',
//             },
//             body: formData,
//         });

//         console.log('Raw Response:', response);

//         if (response.redirected) {
//             console.log('Redirected to:', response.url);
//             window.location.href = response.url;
//             return;
//         }

//         const text = await response.text();
//         console.log('Response Text:', text);

//         try {
//             const result = JSON.parse(text);
//             if (result.success) {
//                 alert(result.message || 'Profile updated successfully!');
//                 // Handle success...
//             } else {
//                 alert(result.message || 'An error occurred.');
//             }
//         } catch (jsonError) {
//             console.error('JSON Parse Error:', jsonError);
//             alert('Failed to parse JSON response.');
//         }
//     } catch (error) {
//         console.error('Request Error:', error);
//         alert('An unexpected error occurred.');
//     }
// });

// document.getElementById('cancelEditButton').addEventListener('click', function() {
//     // Hide input fields and show display fields
//     firstNameDisplay.style.display = 'block';
//     firstNameInput.style.display = 'none';
//     lastNameDisplay.style.display = 'block';
//     lastNameInput.style.display = 'none';
//     emailInput.style.display = 'none';
//     departmentInput.style.display = 'none';
//     emailDisplay.style.display = 'block';
//     departmentDisplay.style.display = 'block';

//     // Hide save/cancel buttons
//     saveCancelButtons.style.display = 'none';
//     editProfileButton.style.display = 'block';
// });
