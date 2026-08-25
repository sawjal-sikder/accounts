from rest_framework import permissions, status
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from accounts.models import Account
from accounts.serializers.account.account import AccountSerializer
from config.pagination import CustomPagination

@extend_schema(tags=['Accounts'])
class AccountListCreateView(generics.ListCreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Account.objects.filter(
            is_active=True,
            group__organization=self.request.user.organization
        ).select_related("group__organization")
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user, 
            updated_by=self.request.user
            )



@extend_schema(tags=["Accounts"])
class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(
            is_active=True,
            group__organization=self.request.user.organization
        ).select_related("group__organization")

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