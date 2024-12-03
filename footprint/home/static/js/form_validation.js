"form_validation.js"

document.addEventListener("DOMContentLoaded", function () {
    const firstNameInput = document.getElementById('signup-firstname');
    const lastNameInput = document.getElementById('signup-lastname');
    const passwordInput = document.getElementById('signup-password');
    const passwordConfirmInput = document.getElementById('signup-password-confirm');
    const submitButton = document.getElementById('submit-button');

    function validateName(input, errorElementId) {
        const nameRegex = /^[a-zA-Z]+$/;  
        const errorElement = document.getElementById(errorElementId);
        
        if (!nameRegex.test(input.value)) {
            input.style.borderColor = 'red';
            errorElement.style.display = 'block';
            return false; // Invalid name
        } else {
            input.style.borderColor = ''; // Reset border color
            errorElement.style.display = 'none';
            return true; // Valid name
        }
    }

    function validatePasswordMatch() {
        const passwordMatchError = document.getElementById('password-match-error');
        
        if (passwordInput.value !== passwordConfirmInput.value) {
            passwordConfirmInput.style.borderColor = 'red';
            passwordMatchError.style.display = 'block';
            return false; // Passwords don't match
        } else {
            passwordConfirmInput.style.borderColor = ''; // Reset border color
            passwordMatchError.style.display = 'none';
            return true; // Passwords match
        }
    }

    function checkFormValidity() {
        const isFirstNameValid = validateName(firstNameInput, 'first-name-error');
        const isLastNameValid = validateName(lastNameInput, 'last-name-error');
        const isPasswordValid = validatePasswordMatch();
        
        // Enable submit button only if all validations pass
        if (isFirstNameValid && isLastNameValid && isPasswordValid) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }

    // Add event listeners for inputs
    firstNameInput.addEventListener('input', checkFormValidity);
    lastNameInput.addEventListener('input', checkFormValidity);
    passwordInput.addEventListener('input', checkFormValidity);
    passwordConfirmInput.addEventListener('input', checkFormValidity);
});