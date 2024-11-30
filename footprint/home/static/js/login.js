/*login.js*/ 
/* comtroll password visibility toggle text in login page  */
document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById('toggle-password');

  togglePassword.addEventListener('click', () => {
      // Toggle password visibility
      if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          togglePassword.textContent = 'Hide'; // Change text to "Hide"
      } else {
          passwordInput.type = 'password';
          togglePassword.textContent = 'Show'; // Change text to "Show"
      }
  });
});