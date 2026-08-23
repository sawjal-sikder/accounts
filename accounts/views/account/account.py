from rest_framework import permissions
from rest_framework import generics
from drf_spectacular.utils import extend_schema

from accounts.models import Account
from accounts.serializers.account.account import AccountSerializer
from config.pagination import CustomPagination

@extend_schema(tags=['Accounts'])
class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


@extend_schema(tags=['Accounts'])
class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]