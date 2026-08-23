from rest_framework import permissions
from rest_framework import generics
from accounts.models import AccountGroup
from accounts.serializers.group.group import GroupSerializer
from drf_spectacular.utils import extend_schema
from config.pagination import CustomPagination


@extend_schema(tags=['Account Groups'])
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = AccountGroup.objects.filter(is_active=True)
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user, 
            updated_by=self.request.user
            )
    
    
@extend_schema(tags=['Account Groups'])
class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountGroup.objects.filter(is_active=True)
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)