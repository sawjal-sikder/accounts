from rest_framework import serializers

from accounts.models import AccountGroup


class GroupSerializer(serializers.ModelSerializer):

    organization = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = AccountGroup
        fields = [
            "id",
            "organization",
            "name",
            "code",
            "group_type",
            "parent",
            "description",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate_code(self, value):
        """
        Check whether the group code already exists
        within the current user's organization.

        If it exists, return the complete existing
        group details in the validation error.
        """

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return value

        organization = getattr(
            request.user,
            "organization",
            None,
        )

        if not organization:
            raise serializers.ValidationError(
                "User is not associated with an organization."
            )

        queryset = AccountGroup.objects.filter(
            organization=organization,
            code=value,
        )

        # Exclude current object during update
        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        existing_group = queryset.first()

        if existing_group:
            raise serializers.ValidationError({
                "message": (
                    "A group with this code already exists "
                    "in your organization."
                ),
                "existing_group": GroupSerializer(
                    existing_group,
                    context=self.context,
                ).data,
            })

        return value

    def validate_parent(self, parent):
        """
        Make sure the selected parent group
        belongs to the same organization.
        """

        if parent is None:
            return parent

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return parent

        organization = getattr(
            request.user,
            "organization",
            None,
        )

        if not organization:
            raise serializers.ValidationError(
                "User is not associated with an organization."
            )

        if parent.organization_id != organization.id:
            raise serializers.ValidationError(
                "Parent group must belong to your organization."
            )

        # Prevent a group from being its own parent
        if self.instance and parent.pk == self.instance.pk:
            raise serializers.ValidationError(
                "A group cannot be its own parent."
            )

        return parent

    def validate(self, attrs):
        """
        Validate group type against parent group type.
        """

        parent = attrs.get("parent")

        if parent:
            group_type = attrs.get(
                "group_type",
                getattr(
                    self.instance,
                    "group_type",
                    None,
                ),
            )

            if parent.group_type != group_type:
                raise serializers.ValidationError({
                    "parent": (
                        "Parent group must have the same "
                        "group type as the child group."
                    )
                })

        return attrs

    def to_representation(self, instance):
        """
        Return parent as an object instead of only parent ID.
        """

        representation = super().to_representation(
            instance
        )

        representation["parent"] = (
            {
                "id": instance.parent.id,
                "name": instance.parent.name,
                "code": instance.parent.code,
            }
            if instance.parent
            else None
        )

        return representation
