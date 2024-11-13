document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("deleteEmailModal");
    const deleteEmailButton = document.getElementById("deleteEmailButton");
    const closeModal = document.getElementById("closeDeleteModal");
    const cancelButton = document.getElementById("cancelDeleteButton");
    const submitButton = document.getElementById("submitDeleteEmail");
    const emailInput = document.getElementById("delete-email");
    const currentPasswordInput = document.getElementById("delete-current-password");
    const passwordError = document.getElementById("delete-password-error");
  
    function validateInputs() {
        submitButton.disabled = !(emailInput.value && currentPasswordInput.value);
    }
  
    emailInput.addEventListener("input", validateInputs);
    currentPasswordInput.addEventListener("input", validateInputs);
  
    deleteEmailButton.onclick = function() {
        modal.style.display = "block";
    };
  
    closeModal.onclick = function() {
        modal.style.display = "none";
        passwordError.style.display = "none";
    };
  
    cancelButton.onclick = function() {
        modal.style.display = "none";
        passwordError.style.display = "none";
    };

    const urlParams = new URLSearchParams(window.location.search);
    const modalState = urlParams.get('modal');
    const errorType = urlParams.get('error');
    const inputtedEmail = urlParams.get('email'); // Get the email parameter from the URL

    if (modalState === 'open') {
        modal.style.display = "block";
        if (errorType) {
            const errorMessages = {
                email_or_password_missing: "Please provide both email and password.",
                email_mismatch: "The email you entered does not match your account.",
                password_or_email_incorrect: "Incorrect password.",
                user_not_found: "No user found with that email.",
                general_error: "An error occurred. Please try again."
            };
            passwordError.textContent = errorMessages[errorType] || "An unknown error occurred.";
            passwordError.style.display = "block";
        }
        if (inputtedEmail) {
            emailInput.value = inputtedEmail; // Set the email input to the passed email value
        }
    }
});
