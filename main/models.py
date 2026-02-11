from django.db import models

class Songs(models.Model):
    title = models.CharField(max_length=255)  # Song name
    artist = models.CharField(max_length=255)  # Artist name
    album = models.CharField(max_length=255, blank=True, null=True)  # Album name
    duration = models.IntegerField()  # Duration in seconds
    mp3_url = models.URLField()  # URL for the MP3 file
    album_art = models.ImageField(upload_to='album_art/', blank=True, null=True)  # Store album cover

    def __str__(self):
        return f"{self.title} by {self.artist}"

