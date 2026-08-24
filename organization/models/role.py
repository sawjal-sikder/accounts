from django.db import models
from organization.models.organization import Organization


class Role(models.Model):
    """A role within an organization."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_organization_role_name"
            )
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"