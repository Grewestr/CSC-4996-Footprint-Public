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

    // Clear Queue functionality
    clearQueueButton.addEventListener('click', function() {
        if (queueTable) {
            queueTable.style.display = 'none'; // Hide the queue table
        }
        noUploadsMessage.style.display = 'block'; // Show the "No videos in the queue" message
    });

    // Reset Queue visibility on new upload
    uploadForm.addEventListener('submit', function() {
        if (queueTable) {
            queueTable.style.display = 'table'; // Show the queue table
        }
        noUploadsMessage.style.display = 'none'; // Hide the "No videos in the queue" message
    });
});
