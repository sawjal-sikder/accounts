from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import generics
from accounts.models import AccountGroup
from accounts.serializers.group.group import GroupSerializer
from drf_spectacular.utils import extend_schema
from config.pagination import CustomPagination


@extend_schema(tags=["Account Groups"])
class GroupListCreateView(generics.ListCreateAPIView):

    serializer_class = GroupSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Return only active groups
        belonging to the logged-in user's organization.
        """

        organization = getattr(
            self.request.user,
            "organization",
            None,
        )

        if not organization:
            return AccountGroup.objects.none()

        return AccountGroup.objects.filter(
            organization=organization,
            is_active=True,
        ).select_related(
            "organization",
            "parent",
            "created_by",
            "updated_by",
        )

    def perform_create(self, serializer):
        """
        Automatically assign organization
        and audit users.
        """

        organization = getattr(
            self.request.user,
            "organization",
            None,
        )

        if not organization:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({
                "organization": (
                    "User is not associated with an organization."
                )
            })

        serializer.save(
            organization=organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
    
    
@extend_schema(tags=['Account Groups'])
class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AccountGroup.objects.filter(
            is_active=True,
            organization=self.request.user.organization
        )
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {
                "message": "Account deleted successfully"
            },
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)