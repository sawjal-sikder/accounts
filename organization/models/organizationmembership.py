from django.db import models
from django.conf import settings
from organization.models.organization import Organization 


class OrganizationMembership(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.organization.name}"