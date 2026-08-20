from django.db import models



class Journal(models.Model):
    date = models.DateField()
    reference = models.CharField(max_length=100,blank=True)
    description = models.TextField(blank=True)
    is_posted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Journal #{self.id} - {self.date}"