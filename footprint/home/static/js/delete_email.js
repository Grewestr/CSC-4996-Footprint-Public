// Wait for the DOM to fully load before executing the script
document.addEventListener("DOMContentLoaded", function() {
    // Get references to DOM elements related to the delete email modal
    const modal = document.getElementById("deleteEmailModal"); // The delete email modal
    const deleteEmailButton = document.getElementById("deleteEmailButton"); // Button to open the delete modal
    const closeModal = document.getElementById("closeDeleteModal"); // Close button in the modal
    const submitButton = document.getElementById("submitDeleteEmail"); // Submit button in the modal
    const currentPasswordInput = document.getElementById("delete-current-password"); // Input field for the current password
    const passwordError = document.getElementById("delete-password-error"); // Element for displaying password-related errors
    const deleteTogglePassword = document.getElementById("delete-toggle-password"); // For toggle show/hide password

    // Function to validate inputs and enable/disable the submit button
    function validateInputs() {
        // Disable the submit button if the current password input is empty
        submitButton.disabled = !currentPasswordInput.value;
    }

    // Attach an event listener to the current password input field to validate inputs on change
    currentPasswordInput.addEventListener("input", validateInputs);

    // Toggle show/hide password using eye icon
    deleteTogglePassword?.addEventListener('click', () => {
        if (currentPasswordInput.type === 'password') {  // If hiding password
            currentPasswordInput.type = 'text'; // Convert to text
            deleteTogglePassword.src = deleteTogglePassword.getAttribute('data-eye-show'); // Show eye icon
        } else { // If already showing password
            currentPasswordInput.type = 'password'; // Change back to password
            deleteTogglePassword.src = deleteTogglePassword.getAttribute('data-eye-hide'); // Change to eye show icon
        }
    });

    // Event listener to show the modal when the delete email button is clicked
    deleteEmailButton.onclick = function() {
        modal.style.display = "block"; // Display the modal
    };

    // Event listener to hide the modal and reset errors when the close button is clicked
    closeModal.onclick = function() {
        modal.style.display = "none"; // Hide the modal
        passwordError.style.display = "none"; // Hide the error message
    };

    // Parse URL parameters to check the state of the modal and handle errors
    const urlParams = new URLSearchParams(window.location.search); // Get URL parameters
    const modalState = urlParams.get('modal'); // Get the 'modal' parameter value
    const errorType = urlParams.get('error'); // Get the 'error' parameter value

    // Check if the modal state is set to 'open' in the URL parameters
    if (modalState === 'open') {
        modal.style.display = "block"; // Display the modal

        // Display appropriate error messages if an error type is provided
        if (errorType) {
            const errorMessages = {
                password_or_email_incorrect: "Incorrect password.", // Error message for incorrect password
                user_not_found: "No user found.", // Error message for user not found
                general_error: "An error occurred. Please try again." // General error message
            };

            // Display the error message or a default error message for unknown error types
            passwordError.textContent = errorMessages[errorType] || "An unknown error occurred.";
            passwordError.style.display = "block"; // Show the error message
        }
    }
});
