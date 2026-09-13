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
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Return groups belonging to the logged-in user's organization.

        Optional filter:
            ?is_active=true
            ?is_active=false

        If is_active is not provided, return both active and inactive groups.
        """

        organization = getattr(
            self.request.user,
            "organization",
            None,
        )

        if not organization:
            return AccountGroup.objects.none()

        queryset = AccountGroup.objects.filter(
            organization=organization,
        ).select_related(
            "organization",
            "parent",
            "created_by",
            "updated_by",
        )

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        return queryset

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
            # is_active=True,
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