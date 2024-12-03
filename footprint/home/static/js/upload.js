document.addEventListener('DOMContentLoaded', function () {
    // Get the URLs from the data attributes
    const deleteUploadUrl = document.body.getAttribute('data-delete-url');
    const checkStatusUrl = document.body.getAttribute('data-check-status-url');

    const youtubeLinkInput = document.getElementById('youtube_link');
    const videoPreview = document.getElementById('video-preview');
    const youtubeVideo = document.getElementById('youtube-video');
    const processingSpeedButtons = document.querySelectorAll('.speed-button');
    const estimatedTimeText = document.getElementById('estimated-time').querySelector('span');
    const processingSpeedInput = document.getElementById('processing_speed');
    const clearQueueButton = document.getElementById('clear-queue-button');
    const queueTable = document.getElementById('queue-table');
    const noUploadsMessage = document.getElementById('no-uploads-message');
    const uploadForm = document.querySelector('.upload-form');
    const refreshButton = document.getElementById('refresh-button'); // Get the refresh button

    // Refresh Button Event Listener
    if (refreshButton) {
        refreshButton.addEventListener('click', function () {
            window.location.reload(); // Force reload the page
        });
    } else {
        console.error('Refresh button not found.');
    }

    // Update video preview when the YouTube link changes
    youtubeLinkInput.addEventListener('input', function () {
        const url = youtubeLinkInput.value;
        const videoId = extractYouTubeVideoID(url);
        if (videoId) {
            youtubeVideo.src = `https://www.youtube.com/embed/${videoId}`;
            videoPreview.style.display = 'block';
        } else {
            youtubeVideo.src = '';
            videoPreview.style.display = 'none';
        }
    });

    // Add event listeners to speed buttons
    processingSpeedButtons.forEach(button => {
        button.addEventListener('click', function () {
            processingSpeedButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const speed = button.getAttribute('data-speed');
            processingSpeedInput.value = speed;

            let timeText = '';
            if (speed === '1') {
                timeText = 'Long';
            } else if (speed === '5') {
                timeText = 'Moderate';
            } else if (speed === '10') {
                timeText = 'Short';
            }
            estimatedTimeText.textContent = timeText;
        });
    });

    // Function to extract YouTube video ID from URL
    function extractYouTubeVideoID(url) {
        const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&\n?#]+)/;
        const match = url.match(regex);
        return match ? match[1] : null;
    }

    // Queue Table Delete Button Listener
    queueTable.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-button')) {
            const row = event.target.closest('tr');
            const jobId = row.getAttribute('data-job-id');
            const deleteUploadUrl = row.getAttribute('data-delete-upload-url');

            if (jobId && deleteUploadUrl) {
                fetch(deleteUploadUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ job_id: jobId }).toString(),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        row.remove(); // Remove the row from the table
                    } else {
                        console.error(`Failed to delete job: ${data.message}`);
                    }
                })
                .catch(error => console.error('Error deleting job:', error));
            } else {
                console.error('Job ID or Delete URL is missing.');
            }
        }
    });

    // Upload Form Submission
    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new URLSearchParams({
            feed_name: document.getElementById('feed_name').value,
            youtube_link: document.getElementById('youtube_link').value,
            processing_speed: document.getElementById('processing_speed').value,
            csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value
        });

        fetch(uploadForm.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        })
        .finally(() => {
            window.location.reload(); 
        });
    });

    // Function to periodically update the queue status
    function updateQueueStatus() {
        fetch(checkStatusUrl)
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => console.error("Error updating queue status:", error));
    }

    // Poll every 5 seconds
    setInterval(updateQueueStatus, 5000);
});
