document.addEventListener("DOMContentLoaded", function() {
  const firstNameInput = document.getElementById('signup-firstname');
  const lastNameInput = document.getElementById('signup-lastname');
  const submitButton = document.getElementById('submit-button');
  
  function validateName(input, errorElementId) {
      const nameRegex = /^[a-zA-Z]+$/;  // Regular expression to allow only letters
      const errorElement = document.getElementById(errorElementId);
      
      if (!nameRegex.test(input.value)) {
          input.style.borderColor = 'red';
          errorElement.style.display = 'block';
          submitButton.disabled = true; // Disable the submit button
      } else {
          input.style.borderColor = ''; // Reset border color
          errorElement.style.display = 'none';
          submitButton.disabled = false; // Enable the submit button
      }
  }

  firstNameInput.addEventListener('input', function() {
      validateName(firstNameInput, 'first-name-error');
  });

  lastNameInput.addEventListener('input', function() {
      validateName(lastNameInput, 'last-name-error');
  });
});
