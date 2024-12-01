document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("changePasswordModal");
    const changePasswordButton = document.getElementById("changePasswordButton");
    const closeModal = document.getElementById("closeModal");
    const submitButton = document.getElementById("setPasswordButton");

    const currentPasswordInput = document.getElementById("current_password");
    const newPasswordInput = document.getElementById("new_password");
    const retypePasswordInput = document.getElementById("retype_password");
    
    // Messages
    const passwordMatchError = document.getElementById('password-match-error');
    const currentPasswordError = document.getElementById('change_password_current_error');
    const generalError = document.getElementById('change_password_general_error');
    const changeSuccess = document.getElementById('change_password_success');

    // Toggle password to show/hide icon
    const currentTogglePassword = document.getElementById('current-toggle-password');
    const newTogglePassword = document.getElementById('new-toggle-password');
    const retypeTogglePassword = document.getElementById('retype-toggle-password');

    // Retype password requirements
    const requirementsBox = document.querySelector('.password-requirements');
    const lengthRequirement = document.getElementById('length');
    const uppercaseRequirement = document.getElementById('uppercase');
    const lowercaseRequirement = document.getElementById('lowercase');

    // Function to show or hide modal
    function toggleModal(show) {
        modal.style.display = show ? "block" : "none";
        if (!show) {
            // Reset UI states when modal is closed
            passwordMatchError.style.display = "none";
            requirementsBox.style.display = "none";
            document.querySelectorAll('.message').forEach(msg => {
                msg.style.display = 'none'; // Hide all message elements
            });
        }
    }

    function updateRequirements() {
        const password = newPasswordInput.value;
        lengthRequirement.classList.toggle('met', password.length >= 8);
        lengthRequirement.querySelector('i').className = password.length >= 8 ? 'check-mark' : 'x-mark';

        uppercaseRequirement.classList.toggle('met', /[A-Z]/.test(password));
        uppercaseRequirement.querySelector('i').className = /[A-Z]/.test(password) ? 'check-mark' : 'x-mark';

        lowercaseRequirement.classList.toggle('met', /[a-z]/.test(password));
        lowercaseRequirement.querySelector('i').className = /[a-z]/.test(password) ? 'check-mark' : 'x-mark';
    }

    function validateRetypedPassword() {
        const newPassword = newPasswordInput.value;
        const retypePassword = retypePasswordInput.value;
        const isPasswordMatching = newPassword === retypePassword;
        if (isPasswordMatching) { // If passwords match
            retypePasswordInput.style.borderColor = '';
            passwordMatchError.style.display = 'none';
        } else { // Display error if they don't
            retypePasswordInput.style.borderColor = 'red';
            passwordMatchError.style.display = 'block';
        }

        // Disable submit button if at least one criteria isn't false
        submitButton.disabled = !isPasswordMatching ||
                                newPassword.length < 8 ||
                                !/[A-Z]/.test(newPassword) ||
                                !/[a-z]/.test(newPassword);
    }

    // Event handlers for button clicks
    currentTogglePassword?.addEventListener('click', () => {
        if (currentPasswordInput.type === 'password') {  // If hiding password
            currentPasswordInput.type = 'text'; // Convert to text
            currentTogglePassword.src = currentTogglePassword.getAttribute('data-eye-show'); // Show eye icon
        } else { // If already showing password
            currentPasswordInput.type = 'password'; // Change back to password
            currentTogglePassword.src = currentTogglePassword.getAttribute('data-eye-hide'); // Change to eye show icon
        }
    });

    // Same as currentTogglePassword
    newTogglePassword?.addEventListener('click', () => {
        if (newPasswordInput.type === 'password') {
            newPasswordInput.type = 'text';
            newTogglePassword.src = newTogglePassword.getAttribute('data-eye-show'); // Show eye icon
        } else {
            newPasswordInput.type = 'password';
            newTogglePassword.src = newTogglePassword.getAttribute('data-eye-hide'); // Change to eye show icon
        }
    });

    // Same as currentTogglePassword
    retypeTogglePassword?.addEventListener('click', () => {
        if (retypePasswordInput.type === 'password') {
            retypePasswordInput.type = 'text';
            retypeTogglePassword.src = retypeTogglePassword.getAttribute('data-eye-show'); // Show eye icon
        } else {
            retypePasswordInput.type = 'password';
            retypeTogglePassword.src = retypeTogglePassword.getAttribute('data-eye-hide'); // Change to eye show icon
        }
    });

    changePasswordButton.onclick = () => toggleModal(true);
    closeModal.onclick = () => toggleModal(false);

    // Display password requirements when focused
    newPasswordInput.addEventListener('focus', () => requirementsBox.style.display = 'block');
    
    // Hide requirements with a slight delay for better user experience
    newPasswordInput.addEventListener('blur', () => setTimeout(() => requirementsBox.style.display = 'none', 200));
    
    // Real-time validation of password criteria
    newPasswordInput.addEventListener('input', updateRequirements);
    retypePasswordInput.addEventListener('input', validateRetypedPassword);
});

