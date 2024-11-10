document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("changePasswordModal");
    const changePasswordButton = document.getElementById("changePasswordButton");
    const closeModal = document.getElementById("closeModal");
    const cancelButton = document.getElementById("cancelButton");
    const submitButton = document.getElementById("submitPasswordChange");
  
    const currentPasswordInput = document.getElementById("current_password");
    const newPasswordInput = document.getElementById("new_password");
    const retypePasswordInput = document.getElementById("retype_password");
  
    const requirementsBox = document.querySelector('.password-requirements');
    const lengthRequirement = document.getElementById('length');
    const uppercaseRequirement = document.getElementById('uppercase');
    const lowercaseRequirement = document.getElementById('lowercase');
    const passwordMatchError = document.getElementById('password-match-error');
  
    // Automatically open the modal if the server says so (based on the 'open' class)
    if (modal.classList.contains('open')) {
        modal.style.display = "block";
    }
  
    // Open modal
    changePasswordButton.onclick = function() {
        modal.style.display = "block";
    };
  
    // Close modal on 'X' click or cancel button click
    closeModal.onclick = function() {
        modal.style.display = "none";
    };
  
    cancelButton.onclick = function() {
        modal.style.display = "none";
    };
  
    // Show password requirements when the new password field is focused
    newPasswordInput.addEventListener('focus', function() {
        requirementsBox.style.display = 'block';
    });
  
    // Hide password requirements when clicking outside the new password field
    newPasswordInput.addEventListener('blur', function() {
        setTimeout(() => {
            requirementsBox.style.display = 'none';
        }, 200);
    });
  
    // Validate password in real-time as the user types
    newPasswordInput.addEventListener('input', function() {
        const password = newPasswordInput.value;
  
        // Validate length
        if (password.length >= 8) {
            lengthRequirement.classList.add('met');
            lengthRequirement.querySelector('i').className = 'check-mark';
        } else {
            lengthRequirement.classList.remove('met');
            lengthRequirement.querySelector('i').className = 'x-mark';
        }
  
        // Validate uppercase letter
        if (/[A-Z]/.test(password)) {
            uppercaseRequirement.classList.add('met');
            uppercaseRequirement.querySelector('i').className = 'check-mark';
        } else {
            uppercaseRequirement.classList.remove('met');
            uppercaseRequirement.querySelector('i').className = 'x-mark';
        }
  
        // Validate lowercase letter
        if (/[a-z]/.test(password)) {
            lowercaseRequirement.classList.add('met');
            lowercaseRequirement.querySelector('i').className = 'check-mark';
        } else {
            lowercaseRequirement.classList.remove('met');
            lowercaseRequirement.querySelector('i').className = 'x-mark';
        }
  
        // Enable or disable the submit button based on password validity and matching
        validatePasswords();
    });
  
    // Validate if the new password and retype password match
    retypePasswordInput.addEventListener('input', function() {
        validatePasswords();
    });
  
    // Validate the matching passwords
    function validatePasswords() {
        const newPassword = newPasswordInput.value;
        const retypePassword = retypePasswordInput.value;
  
        const isPasswordMatching = newPassword === retypePassword;
  
        if (isPasswordMatching) {
            passwordMatchError.style.display = 'none';
        } else {
            passwordMatchError.style.display = 'block';
        }
  
        // Enable the submit button only if all criteria are met and passwords match
        if (newPassword.length >= 8 && /[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) && isPasswordMatching) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }
  });