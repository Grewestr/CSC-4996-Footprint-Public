document.addEventListener('DOMContentLoaded', function () {
    // Wait for the DOM to be fully loaded before running any scripts

    // Toggle visibility for sections when their headings are clicked
    const sections = document.querySelectorAll('section');

    sections.forEach(function (section) {
        // Find the section heading for each section
        const heading = section.querySelector('.section-heading');

        // If the heading exists, add a click event listener to toggle the section's visibility
        if (heading) {
            heading.addEventListener('click', function () {
                // Toggle the 'open' class for the section, showing or hiding its content
                section.classList.toggle('open');
                
                // Set the aria-expanded attribute for accessibility, indicating if the section is expanded or collapsed
                const isExpanded = section.classList.contains('open');
                heading.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');

                // Smoothly scroll the section into view if it has been expanded
                if (isExpanded) {
                    section.scrollIntoView({ behavior: 'smooth' });
                }
            });

            // Set the initial aria-expanded attribute to false (collapsed)
            heading.setAttribute('aria-expanded', false);
        } else {
            // Log a warning if no heading is found in the section 
            console.warn('No .section-heading found in section:', section);
        }
    });

    // Scroll to the top of the page when the logo is clicked
    const logoLink = document.querySelector('.logo-link');
    if (logoLink) {
        logoLink.addEventListener('click', function (event) {
            // Prevent the default link behavior
            event.preventDefault();

            // Smoothly scroll to the top of the page
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    } else {
        // Log a warning if the logo link element is not found 
        console.warn('Logo link element not found.');
    }
});
