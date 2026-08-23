from rest_framework import generics, permissions,filters
from drf_spectacular.utils import extend_schema
from accounts.models import Organization
from accounts.serializers.organization.serializers import OrganizationSerializer

@extend_schema(tags=["Organization"])
class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    
@extend_schema(tags=["Organization"])
class OrganizationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]