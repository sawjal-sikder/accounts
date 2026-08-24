# Role-Based Access Control (RBAC) System

This document outlines the design, schema, and interaction workflows of the multi-tenant Role-Based Access Control (RBAC) system implemented in the `organization` module.

---

## 1. Architectural Overview

The RBAC system is designed with **multi-tenancy** at its core. Permissions and Roles are scoped to a specific `Organization`, ensuring strict logical isolation between different tenants. A user can belong to multiple organizations and hold different roles in each.

### Core Architecture Concept
```
   [User] ──(via OrganizationMembership)── [Organization]
                   │
                   ▼ (UserRole)
                [Role] ──(RolePermission)── [Permission]
```

---

## 2. Entity-Relationship Schema

The access control system consists of six main models:

### 1. `Organization`
The tenant entity. All operations, roles, and memberships reside within an organization.
* **Fields**: `name`, `logo`, `address`, `phone`, `email`, `website`, `tin`, `bin`, `trade_license`, `vat_registration_number`.

### 2. `OrganizationMembership`
Connects a `User` to an `Organization`. Represents a user's presence within a tenant.
* **Fields**:
  * `user` (FK to `AUTH_USER_MODEL`)
  * `organization` (FK to `Organization`)
  * `is_owner` (Boolean): If `True`, the user bypasses all standard permission checks for this organization (super-admin privilege for that tenant).
  * `is_active` (Boolean): Controls if the membership is active.
* **Constraint**: Unique combination of `user` and `organization`.

### 3. `Role`
A logical grouping of permissions scoped to an organization.
* **Fields**:
  * `organization` (FK to `Organization`)
  * `name` (CharField): E.g., "Accountant", "Manager", "Viewer".
  * `description` (TextField)
  * `is_active` (Boolean)
* **Constraint**: Unique combination of `organization` and `name`.

### 4. `Permission`
A global registry of discrete actions. These are defined system-wide and are not scoped to a single organization (they are shared across all tenants).
* **Fields**:
  * `module` (CharField): E.g., `accounts`, `authentication`.
  * `resource` (CharField): E.g., `account`, `journal`, `membership`.
  * `action` (CharField, choices):
    * `view`
    * `create`
    * `update`
    * `delete`
    * `approve`
    * `reject`
    * `export`
    * `import`
  * `code` (CharField, unique): System identifier formatted as `module:resource:action` (e.g., `accounts:journal:approve`).
  * `description` (TextField)
  * `is_active` (Boolean)

### 5. `RolePermission`
Maps `Role` to `Permission` in a many-to-many relationship.
* **Fields**:
  * `role` (FK to `Role`)
  * `permission` (FK to `Permission`)
* **Constraint**: Unique combination of `role` and `permission`.

### 6. `UserRole`
Assigns a `Role` to an `OrganizationMembership`.
* **Fields**:
  * `membership` (FK to `OrganizationMembership`)
  * `role` (FK to `Role`)
  * `is_active` (Boolean)
* **Constraint**: Unique combination of `membership` and `role`.

---

## 3. Permission Interaction & Resolution Workflow

When a user attempts to perform an action (e.g., creating a journal line in organization `X`), the system must verify their permissions using the following evaluation hierarchy:

### Step-by-Step Resolution Algorithm

```flow
[Request to access resource in Organization X]
                   │
                   ▼
       Is there an active Membership 
         for User in Organization X?
         ├── No  ──► [DENIED (403)]
         └── Yes
               │
               ▼
         Is membership.is_owner == True?
         ├── Yes ──► [GRANTED (Bypass standard checks)]
         └── No
               │
               ▼
         Fetch all active Roles associated 
         with the User's Membership (via UserRole).
               │
               ▼
         Does any active Role map to an active Permission 
         where permission.code == required_permission_code?
         ├── Yes ──► [GRANTED]
         └── No  ──► [DENIED (403)]
```

---

## 4. Implementation Reference (Django)

Below is an idiomatic Python/Django implementation pattern of a dynamic permission checker and a reusable DRF Permission class.

### 1. Verification Helper Method

This method can be added to the `OrganizationMembership` model or implemented as a utility function:

```python
# organization/utils.py or organization/models/organizationmembership.py

from organization.models.userrole import UserRole
from organization.models.rolepermission import RolePermission

def has_tenant_permission(user, organization_id, required_permission_code):
    """
    Checks if a user has a specific permission within a given organization.
    """
    from organization.models.organizationmembership import OrganizationMembership

    # 1. Check membership and active status
    try:
        membership = OrganizationMembership.objects.get(
            user=user,
            organization_id=organization_id,
            is_active=True
        )
    except OrganizationMembership.DoesNotExist:
        return False

    # 2. Owner bypasses all permission checks
    if membership.is_owner:
        return True

    # 3. Query through UserRole -> Role -> RolePermission -> Permission
    return UserRole.objects.filter(
        membership=membership,
        is_active=True,
        role__is_active=True,
        role__role_permissions__permission__code=required_permission_code,
        role__role_permissions__permission__is_active=True
    ).exists()
```

### 2. Django Rest Framework (DRF) Custom Permission Class

To secure views automatically, we can use a custom permission class that extracts the organization context (e.g., from the URL kwargs or headers):

```python
# organization/permissions.py

from rest_framework import permissions
from organization.models.organizationmembership import OrganizationMembership
from organization.models.userrole import UserRole

class HasOrganizationPermission(permissions.BasePermission):
    """
    Custom permission class for DRF.
    Requires view to specify 'required_permission_code'.
    Extracts 'organization_id' from URL path parameters.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Extract permission code defined on the view
        permission_code = getattr(view, "required_permission_code", None)
        if not permission_code:
            # If no code is specified, fall back to authenticated-only or deny
            return False

        # Extract organization_id from URL kwargs (e.g., /api/v1/organizations/<id>/...)
        organization_id = view.kwargs.get("organization_id") or view.kwargs.get("pk")
        if not organization_id:
            return False

        # Verify permission
        try:
            membership = OrganizationMembership.objects.get(
                user=request.user,
                organization_id=organization_id,
                is_active=True
            )
        except OrganizationMembership.DoesNotExist:
            return False

        if membership.is_owner:
            return True

        return UserRole.objects.filter(
            membership=membership,
            is_active=True,
            role__is_active=True,
            role__role_permissions__permission__code=permission_code,
            role__role_permissions__permission__is_active=True
        ).exists()
```

### 3. Securing views in DRF

```python
# accounts/views/account.py

from rest_framework import generics
from organization.permissions import HasOrganizationPermission
from accounts.models import Account
from accounts.serializers import AccountSerializer

class AccountCreateView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [HasOrganizationPermission]
    required_permission_code = "accounts:account:create"
```

---

## 5. Performance Optimization Strategy

Because permission checks happen on every API request, the resolution query should be highly optimized:

1. **Database Indexing**:
   - Django handles indexing on `ForeignKey` fields automatically.
   - The unique constraints on `OrganizationMembership(user, organization)`, `Role(organization, name)`, `RolePermission(role, permission)`, and `UserRole(membership, role)` act as composite indexes, making lookups exceptionally fast.

2. **Select Related / Prefetching**:
   - When retrieving membership information in authentication handlers, use `select_related('organization')` and `prefetch_related('user_roles__role__role_permissions__permission')` to load the permissions mapping in a single database query.

3. **Caching**:
   - For high-throughput environments, the user's active permissions per organization can be cached in **Redis** with a key schema like `user:{user_id}:org:{org_id}:permissions`.
   - The cache should be invalidated whenever `RolePermission` or `UserRole` mappings are modified.
