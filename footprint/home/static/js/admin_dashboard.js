
// Work in progress, did not fully impliment
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('click', function () {
            // Toggle Open
            this.classList.toggle('open');
        });

    });
});
