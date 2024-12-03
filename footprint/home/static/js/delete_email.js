document.addEventListener("DOMContentLoaded", function() {
    // Get references to DOM elements related to the delete email modal
    const modal = document.getElementById("deleteEmailModal"); 
    const deleteEmailButton = document.getElementById("deleteEmailButton"); 
    const closeModal = document.getElementById("closeDeleteModal"); 
    const submitButton = document.getElementById("submitDeleteEmail"); 
    const currentPasswordInput = document.getElementById("delete-current-password"); 
    const passwordError = document.getElementById("delete-password-error"); 
    const deleteTogglePassword = document.getElementById("delete-toggle-password");

    // Function to validate inputs and enable/disable the submit button
    function validateInputs() {
        // Disable the submit button if the current password input is empty
        submitButton.disabled = !currentPasswordInput.value;
    }

    // Attach an event listener to the current password input field to validate inputs on change
    currentPasswordInput.addEventListener("input", validateInputs);

    // Toggle show/hide password using eye icon
    deleteTogglePassword?.addEventListener('click', () => {
        if (currentPasswordInput.type === 'password') {  
            currentPasswordInput.type = 'text'; 
            deleteTogglePassword.src = deleteTogglePassword.getAttribute('data-eye-show'); 
        } else { 
            currentPasswordInput.type = 'password'; 
            deleteTogglePassword.src = deleteTogglePassword.getAttribute('data-eye-hide'); 
        }
    });

    // Event listener to show the modal when the delete email button is clicked
    deleteEmailButton.onclick = function() {
        modal.style.display = "block"; 
    };

    // Event listener to hide the modal and reset errors when the close button is clicked
    closeModal.onclick = function() {
        modal.style.display = "none"; 
        passwordError.style.display = "none"; 
    };

    // Parse URL parameters to check the state of the modal and handle errors
    const urlParams = new URLSearchParams(window.location.search); 
    const modalState = urlParams.get('modal'); 
    const errorType = urlParams.get('error'); 

    // Check if the modal state is set to 'open' in the URL parameters
    if (modalState === 'open') {
        modal.style.display = "block"; 

        // Display appropriate error messages if an error type is provided
        if (errorType) {
            const errorMessages = {
                password_or_email_incorrect: "Incorrect password.", 
                user_not_found: "No user found.", 
                general_error: "An error occurred. Please try again." 
            };

            // Display the error message or a default error message for unknown error types
            passwordError.textContent = errorMessages[errorType] || "An unknown error occurred.";
            passwordError.style.display = "block"; 
        }
    }
});
