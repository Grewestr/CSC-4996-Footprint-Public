/*signup.js*/ 
/* comtroll password visibility toggle text in signup page  */


document.addEventListener('DOMContentLoaded', () => {
  // Toggle for signup password
  const signupPasswordInput = document.getElementById('signup-password');
  const signupTogglePassword = document.getElementById('toggle-signup-password');

  signupTogglePassword?.addEventListener('click', () => {
      if (signupPasswordInput.type === 'password') {
          signupPasswordInput.type = 'text';
          signupTogglePassword.textContent = 'Hide';
      } else {
          signupPasswordInput.type = 'password';
          signupTogglePassword.textContent = 'Show';
      }
  });

  // Toggle for retyped password
  const signupPasswordConfirmInput = document.getElementById('signup-password-confirm');
  const signupToggleRetypedPassword = document.getElementById('toggle-signup-retyped-password');

  signupToggleRetypedPassword?.addEventListener('click', () => {
      if (signupPasswordConfirmInput.type === 'password') {
          signupPasswordConfirmInput.type = 'text';
          signupToggleRetypedPassword.textContent = 'Hide';
      } else {
          signupPasswordConfirmInput.type = 'password';
          signupToggleRetypedPassword.textContent = 'Show';
      }
  });

  // Password match validation
  const passwordMatchError = document.getElementById('password-match-error');

  signupPasswordConfirmInput.addEventListener('input', () => {
      if (signupPasswordConfirmInput.value !== signupPasswordInput.value) {
          passwordMatchError.style.display = 'block';
      } else {
          passwordMatchError.style.display = 'none';
      }
  });
});