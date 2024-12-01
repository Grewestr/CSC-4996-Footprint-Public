/*login.js*/ 
/* comtroll password visibility toggle text in login page  */
document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById('toggle-password');

  togglePassword.addEventListener('click', () => {
      // Toggle password visibility
      if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          togglePassword.src = togglePassword.getAttribute('data-eye-show'); // Change to show eye icon
      } else {
          passwordInput.type = 'password';
          togglePassword.src = togglePassword.getAttribute('data-eye-hide'); // Change hide eye icon
      }
  });
});