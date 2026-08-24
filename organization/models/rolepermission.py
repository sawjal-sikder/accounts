from django.db import models
from organization.models.permission import Permission
from organization.models.role import Role


class RolePermission(models.Model):

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission"
            )
        ]

    def __str__(self):
        return (
            f"{self.role.name} → "
            f"{self.permission.code}"
        )