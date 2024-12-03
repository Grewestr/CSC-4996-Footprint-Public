// JavaScript to handle real-time validation
document.addEventListener('DOMContentLoaded', function() {
  const passwordInput = document.getElementById('signup-password');
  const requirementsBox = document.querySelector('.password-requirements');

  // Show the requirements box when the password field is focused
  passwordInput.addEventListener('focus', function() {
      requirementsBox.style.display = 'block';
  });

  // Hide the requirements box when clicking outside the password field
  passwordInput.addEventListener('blur', function() {
      setTimeout(() => {
          requirementsBox.style.display = 'none';
      }, 200);
  });

  passwordInput.addEventListener('input', function() {
      const password = passwordInput.value;

      // Validate length
      const lengthRequirement = document.getElementById('length');
      if (password.length >= 8) {
          lengthRequirement.classList.add('met');
          lengthRequirement.querySelector('i').className = 'check-mark';
      } else {
          lengthRequirement.classList.remove('met');
          lengthRequirement.querySelector('i').className = 'x-mark';
      }

      // Validate uppercase letter
      const uppercaseRequirement = document.getElementById('uppercase');
      if (/[A-Z]/.test(password)) {
          uppercaseRequirement.classList.add('met');
          uppercaseRequirement.querySelector('i').className = 'check-mark';
      } else {
          uppercaseRequirement.classList.remove('met');
          uppercaseRequirement.querySelector('i').className = 'x-mark';
      }

      // Validate lowercase letter
      const lowercaseRequirement = document.getElementById('lowercase');
      if (/[a-z]/.test(password)) {
          lowercaseRequirement.classList.add('met');
          lowercaseRequirement.querySelector('i').className = 'check-mark';
      } else {
          lowercaseRequirement.classList.remove('met');
          lowercaseRequirement.querySelector('i').className = 'x-mark';
      }
  });
});