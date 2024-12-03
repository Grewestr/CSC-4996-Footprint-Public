document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("changePasswordModal");
    const changePasswordButton = document.getElementById("changePasswordButton");
    const closeModal = document.getElementById("closeModal");
    const submitButton = document.getElementById("setPasswordButton");

    const currentPasswordInput = document.getElementById("current_password");
    const newPasswordInput = document.getElementById("new_password");
    const retypePasswordInput = document.getElementById("retype_password");
    
    // Error messages
    const passwordMatchError = document.getElementById('password-match-error');

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

            // Hide all messages
            document.querySelectorAll('.message').forEach(msg => {
                msg.style.display = 'none'; // Hide all message elements
            });

             // Clear input fields
            currentPasswordInput.value = '';
            newPasswordInput.value = '';
            retypePasswordInput.value = '';
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
        if (currentPasswordInput.type === 'password') {  
            currentPasswordInput.type = 'text'; 
            currentTogglePassword.src = currentTogglePassword.getAttribute('data-eye-show'); 
        } else { 
            currentPasswordInput.type = 'password'; 
            currentTogglePassword.src = currentTogglePassword.getAttribute('data-eye-hide'); 
        }
    });

    // Same as currentTogglePassword
    newTogglePassword?.addEventListener('click', () => {
        if (newPasswordInput.type === 'password') {
            newPasswordInput.type = 'text';
            newTogglePassword.src = newTogglePassword.getAttribute('data-eye-show'); 
        } else {
            newPasswordInput.type = 'password';
            newTogglePassword.src = newTogglePassword.getAttribute('data-eye-hide'); 
        }
    });

    // Same as currentTogglePassword
    retypeTogglePassword?.addEventListener('click', () => {
        if (retypePasswordInput.type === 'password') {
            retypePasswordInput.type = 'text';
            retypeTogglePassword.src = retypeTogglePassword.getAttribute('data-eye-show'); 
        } else {
            retypePasswordInput.type = 'password';
            retypeTogglePassword.src = retypeTogglePassword.getAttribute('data-eye-hide'); 
        }
    });

    changePasswordButton.onclick = () => toggleModal(true);
    closeModal.onclick = () => toggleModal(false);

    // Display password requirements when focused
    newPasswordInput.addEventListener('focus', () => requirementsBox.style.display = 'block');
    
    // Hide requirements with a slight delay
    newPasswordInput.addEventListener('blur', () => setTimeout(() => requirementsBox.style.display = 'none', 200));
    
    // Real-time validation of password criteria
    newPasswordInput.addEventListener('input', updateRequirements);
    retypePasswordInput.addEventListener('input', validateRetypedPassword);
});

