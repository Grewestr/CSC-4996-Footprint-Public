document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("changePasswordModal");
    const changePasswordButton = document.getElementById("changePasswordButton");
    const closeModal = document.getElementById("closeModal");
    const cancelButton = document.getElementById("cancelButton");
    const submitButton = document.getElementById("submitPasswordChange");

    const newPasswordInput = document.getElementById("new_password");
    const retypePasswordInput = document.getElementById("retype_password");
    const passwordMatchError = document.getElementById('password-match-error');

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
        }
    }

    // Event handlers for button clicks
    changePasswordButton.onclick = () => toggleModal(true);
    closeModal.onclick = () => toggleModal(false);
    cancelButton.onclick = () => toggleModal(false);

    // Display password requirements when focused
    newPasswordInput.addEventListener('focus', () => requirementsBox.style.display = 'block');
    // Hide requirements with a slight delay for better user experience
    newPasswordInput.addEventListener('blur', () => setTimeout(() => requirementsBox.style.display = 'none', 200));

    // Real-time validation of password criteria
    newPasswordInput.addEventListener('input', updateRequirements);
    retypePasswordInput.addEventListener('input', validatePasswords);

    function updateRequirements() {
        const password = newPasswordInput.value;
        lengthRequirement.classList.toggle('met', password.length >= 8);
        lengthRequirement.querySelector('i').className = password.length >= 8 ? 'check-mark' : 'x-mark';

        uppercaseRequirement.classList.toggle('met', /[A-Z]/.test(password));
        uppercaseRequirement.querySelector('i').className = /[A-Z]/.test(password) ? 'check-mark' : 'x-mark';

        lowercaseRequirement.classList.toggle('met', /[a-z]/.test(password));
        lowercaseRequirement.querySelector('i').className = /[a-z]/.test(password) ? 'check-mark' : 'x-mark';

        validatePasswords();
    }

    function validatePasswords() {
        const newPassword = newPasswordInput.value;
        const retypePassword = retypePasswordInput.value;
        const isPasswordMatching = newPassword === retypePassword;
        passwordMatchError.style.display = isPasswordMatching ? 'none' : 'block';

        submitButton.disabled = !isPasswordMatching ||
                                newPassword.length < 8 ||
                                !/[A-Z]/.test(newPassword) ||
                                !/[a-z]/.test(newPassword);
    }
});
