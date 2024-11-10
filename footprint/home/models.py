from django.db import models

class VideoUpload(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    youtube_link = models.URLField()
    processing_speed = models.CharField(max_length=10)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user_email = models.EmailField(null=True, blank=True)  # Allows null values for existing rows

    def __str__(self):
        return f"{self.youtube_link} - {self.status}"
