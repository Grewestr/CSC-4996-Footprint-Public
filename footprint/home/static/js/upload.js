// upload.js

document.addEventListener('DOMContentLoaded', function() {
    const youtubeLinkInput = document.getElementById('youtube_link');
    const videoPreview = document.getElementById('video-preview');
    const youtubeVideo = document.getElementById('youtube-video');
    const processingSpeedSelect = document.getElementById('processing_speed');
    const estimatedTimeText = document.getElementById('estimated-time').querySelector('span');

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

    // Update estimated processing time based on selected speed
    processingSpeedSelect.addEventListener('change', function() {
        const speed = processingSpeedSelect.value;
        let timeText = '';
        if (speed === 'slow') {
            timeText = 'Long';
        } else if (speed === 'medium') {
            timeText = 'Moderate';
        } else if (speed === 'fast') {
            timeText = 'Short';
        }
        estimatedTimeText.textContent = timeText;
    });

    // Function to extract YouTube video ID from URL
    function extractYouTubeVideoID(url) {
        const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&\n?#]+)/;
        const match = url.match(regex);
        return match ? match[1] : null;
    }
});
