from django.db import models



class Permission(models.Model):

    ACTION_CHOICES = [
        ("view", "View"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("export", "Export"),
        ("import", "Import"),
    ]

    module = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    action = models.CharField(max_length=20,choices=ACTION_CHOICES)
    code = models.CharField(max_length=200,unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "module",
            "resource",
            "action"
        ]

    def __str__(self):
        return self.code