document.addEventListener("DOMContentLoaded", function() {
    const dropdowns = document.querySelectorAll(".dropdown-btn");

    dropdowns.forEach(button => {
        button.addEventListener("click", function() {
            // Toggle the 'active' class to show or hide the dropdown content
            this.classList.toggle("active");

            // Find the dropdown content corresponding to this button
            const content = this.nextElementSibling;

            // Toggle the dropdown display
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    });
});
