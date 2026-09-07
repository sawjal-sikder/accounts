from django.db import models
from organization.models.organizationmembership import OrganizationMembership
from organization.models.role import Role



class UserRole(models.Model):
    """A user's role within an organization."""

    membership = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.CASCADE,
        related_name="user_roles"
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "role"],
                name="unique_membership_role"
            )
        ]

    def __str__(self):
        return (
            f"{self.membership.user.username} - "
            f"{self.role.name}"
        )