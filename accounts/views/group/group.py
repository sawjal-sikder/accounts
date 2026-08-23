from rest_framework import permissions
from rest_framework import generics
from accounts.models import AccountGroup
from accounts.serializers.group.group import GroupSerializer
from drf_spectacular.utils import extend_schema
from config.pagination import CustomPagination


@extend_schema(tags=['Account Groups'])
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = AccountGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    
@extend_schema(tags=['Account Groups'])
class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]