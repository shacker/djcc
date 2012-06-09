from django.db import models
import datetime
        
class Story(models.Model):
    """
    System-wide news announcements
    """
    
    headline = models.CharField(max_length=120)
    slug = models.SlugField()
    pubdate = models.DateTimeField(blank=True, default=datetime.datetime.now)
    body = models.TextField(help_text="Story content.")
    published = models.BooleanField(default=True)
    modified = models.DateTimeField(blank=True, default=datetime.datetime.now)
    
    class Meta:
        verbose_name_plural = "News"  

    def __unicode__(self):
        return self.headline;

        