from django.db import models


class Journal(models.Model):
    date = models.DateField()

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(blank=True)
    is_posted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Journal #{self.id} - {self.date}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # First save to generate ID
        super().save(*args, **kwargs)

        # Generate reference after ID exists
        if is_new and not self.reference:
            self.reference = f"JRN-{self.date.strftime('%Y-%m-%d')}-{self.id}"
            super().save(update_fields=["reference"])