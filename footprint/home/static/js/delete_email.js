document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("deleteEmailModal");
    const deleteEmailButton = document.getElementById("deleteEmailButton");
    const closeModal = document.getElementById("closeDeleteModal");
    const cancelButton = document.getElementById("cancelDeleteButton");
    const submitButton = document.getElementById("submitDeleteEmail");
  
    const emailInput = document.getElementById("delete-email");
    const currentPasswordInput = document.getElementById("delete-current-password");
    const passwordError = document.getElementById("delete-password-error");
  
    // Open modal
    deleteEmailButton.onclick = function() {
        modal.style.display = "block";
    };
  
    // Close modal on 'X' click or cancel button click
    closeModal.onclick = function() {
        modal.style.display = "none";
    };
  
    cancelButton.onclick = function() {
        modal.style.display = "none";
    };
  
    // Enable the submit button only if both fields are filled
    function validateInputs() {
        const email = emailInput.value;
        const currentPassword = currentPasswordInput.value;
  
        if (email && currentPassword) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    }
  
    emailInput.addEventListener("input", validateInputs);
    currentPasswordInput.addEventListener("input", validateInputs);
  
    // Check for query parameter to reopen modal and show error if needed
    const urlParams = new URLSearchParams(window.location.search);
    const deleteError = urlParams.get('delete_error');
  
    if (deleteError) {
        modal.style.display = "block";  // Only open the modal if there's an error
        passwordError.style.display = "block";  // Show the error message in the modal
    }
  });