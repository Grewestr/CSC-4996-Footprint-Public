document.addEventListener('DOMContentLoaded', function() {
    const youtubeLinkInput = document.getElementById('youtube_link');
    const videoPreview = document.getElementById('video-preview');
    const youtubeVideo = document.getElementById('youtube-video');
    const processingSpeedButtons = document.querySelectorAll('.speed-button');
    const estimatedTimeText = document.getElementById('estimated-time').querySelector('span');
    const processingSpeedInput = document.getElementById('processing_speed');
    const clearQueueButton = document.getElementById('clear-queue-button');
    const queueTable = document.getElementById('queue-table');
    const noUploadsMessage = document.getElementById('no-uploads-message');
    const uploadForm = document.querySelector('.upload-form'); // Form to handle new uploads
    const checkStatusUrl = "{% url 'check_job_status' %}";


    
    queueTable.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-button')) {
            const row = event.target.closest('tr');
            const jobId = row.getAttribute('data-job-id');

            if (jobId) {
                // Send AJAX POST request to delete the job
                fetch('{% url "delete_upload_view" %}', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({ job_id: jobId }).toString()
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the row from the queue table
                        row.remove();
                        console.log(`Job ${jobId} deleted successfully.`);
                    } else {
                        console.error(`Failed to delete job: ${data.message}`);
                    }
                })
                .catch(error => console.error('Error deleting job:', error));
            }
        }
    });
    // Update video preview when the YouTube link changes
    youtubeLinkInput.addEventListener('input', function() {
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
        button.addEventListener('click', function() {
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

    // AJAX form submission to update queue without page reload
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission

        // Gather form data
        const formData = {
            feed_name: document.getElementById('feed_name').value,
            youtube_link: youtubeLinkInput.value,
            processing_speed: processingSpeedInput.value,
            csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value
        };

        // Send AJAX POST request to the server
        fetch(uploadForm.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(formData).toString()
        })
        .then(response => {
            if (!response.ok) {
                // If the response is not OK (e.g., a 404 or 500), log an error but don’t show an alert
                console.error("Error: Response not OK", response.status, response.statusText);
                return Promise.reject(new Error("Server error"));
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Add the new upload to the queue table dynamically
                const newRow = document.createElement('tr');
                newRow.setAttribute('data-job-id', data.upload.job_id);  // Set job ID for easy reference
                newRow.innerHTML = `
                    <td>${data.upload.feed_name}</td>
                    <td>${data.upload.processing_speed}</td>
                    <td class="status-cell">${data.upload.status}</td>
                    <td>${data.upload.uploaded_at}</td>
                `;
                queueTable.querySelector('tbody').prepend(newRow);

                // Show the queue table if it was hidden
                queueTable.style.display = 'table';
                noUploadsMessage.style.display = 'none';
            } else {
                // If data.success is false, just log the error and don’t show an alert
                console.error("Server responded with an error message:", data.message);
            }
        })
        .catch(error => {
            // Only log the error, don’t show an alert
            console.error("Fetch error:", error);
        });
    });

    function updateQueueStatus() {
        fetch(checkStatusUrl)
            .then(response => {
                if (!response.ok) {
                    console.error("Status check error:", response.status, response.statusText);
                    return Promise.reject(new Error("Server error"));
                }
                return response.json();
            })
            .then(data => {
                data.uploads.forEach(upload => {
                    const row = document.querySelector(`#queue-table tr[data-job-id="${upload.job_id}"]`);
                    if (row) {
                        row.querySelector(".status-cell").innerText = upload.status;
                        console.log(`Updated status for job ${upload.job_id} to ${upload.status}`);
                    }
                });
            })
            .catch(error => console.error("Error fetching job statuses:", error));
    }
    
    // Poll every 5 seconds to check for updated job statuses
    setInterval(updateQueueStatus, 5000);
});