from django.db import models
from django.conf import settings


class Journal(models.Model):
    date = models.DateField()
    reference = models.CharField(max_length=100,blank=True)
    description = models.TextField(blank=True)
    is_posted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="journals_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="journals_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Journal #{self.id} - {self.date}"