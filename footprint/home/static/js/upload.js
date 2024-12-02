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
    queueTable.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-button')) {
            const row = event.target.closest('tr');
            const jobId = row.getAttribute('data-job-id');
            const deleteUploadUrl = row.getAttribute('data-delete-upload-url'); // Get delete URL from the attribute
    
            console.log('Job ID:', jobId);
            console.log('Delete URL:', deleteUploadUrl); // Log to verify it's correct
    
            if (jobId && deleteUploadUrl) {
                // Perform the delete request
                fetch(deleteUploadUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ job_id: jobId }).toString(),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        row.remove(); // Remove the row from the table
                        console.log(`Job ${jobId} deleted successfully.`);
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
    
    

    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission
    
        // Gather form data
        const formData = new URLSearchParams({
            feed_name: document.getElementById('feed_name').value,
            youtube_link: document.getElementById('youtube_link').value,
            processing_speed: document.getElementById('processing_speed').value,
            csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value
        });
    
        // Send AJAX POST request to the server
        fetch(uploadForm.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const queueTableBody = document.querySelector('#queue-table tbody');
                const newRow = document.createElement('tr');
    
                newRow.setAttribute('data-job-id', data.upload.job_id); // Set the job ID
                newRow.innerHTML = `
                    <td>
                        <a href="${data.upload.youtube_link}" target="_blank">${data.upload.feed_name}</a> <!-- Add hyperlink -->
                    </td>
                    <td>${data.upload.status}</td> <!-- Status -->
                    <td>${data.upload.uploaded_at}</td> <!-- Formatted time -->
                    <td>
                        <button type="button" class="delete-button" data-job-id="${data.upload.job_id}">Delete</button>
                    </td>
                `;
    
                queueTableBody.prepend(newRow); // Add the new row to the top of the table
                console.log(`New upload added: ${data.upload.feed_name}`);
            } else {
                console.error(`Failed to add upload: ${data.message}`);
            }
        })
        .catch(error => console.error('Error adding upload:', error));
    });
    
    

    // Function to periodically update the queue status
    function updateQueueStatus() {
        fetch(checkStatusUrl)
            .then(response => response.json())
            .then(data => {
                // Handle the updated queue and history here
                console.log(data);
            })
            .catch(error => console.error("Error updating queue status:", error));
    }

    // Poll every 5 seconds
    setInterval(updateQueueStatus, 5000);
});
