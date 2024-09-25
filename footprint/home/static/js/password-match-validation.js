// password-match-validation.js

document.addEventListener("DOMContentLoaded", function () {
  const passwordInput = document.getElementById('signup-password');
  const passwordConfirmInput = document.getElementById('signup-password-confirm');
  const submitButton = document.getElementById('submit-button');

  function validatePasswordMatch() {
      const passwordMatchError = document.getElementById('password-match-error');

      if (passwordInput.value !== passwordConfirmInput.value) {
          passwordConfirmInput.style.borderColor = 'red';
          passwordMatchError.style.display = 'block';
          submitButton.disabled = true; // Disable the submit button
      } else {
          passwordConfirmInput.style.borderColor = ''; // Reset border color
          passwordMatchError.style.display = 'none';
          submitButton.disabled = false; // Enable the submit button
      }
  }

  // Listen for changes in the password input fields
  passwordInput.addEventListener('input', validatePasswordMatch);
  passwordConfirmInput.addEventListener('input', validatePasswordMatch);
});
