from rest_framework import generics, permissions,status,filters
from rest_framework.response import Response
from accounts.models.journal import Journal
from accounts.serializers.journal.serializers import JournalSerializer, JournalDetailSerializer
from drf_spectacular.utils import extend_schema

from config.pagination import CustomPagination

@extend_schema(tags=["Journal"])
class JournalListCreateView(generics.ListCreateAPIView):
    serializer_class = JournalSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Journal.objects.filter(
            is_active=True,
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
            updated_by=self.request.user
        )
        
    
@extend_schema(tags=["Journal"])
class JournalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JournalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Journal.objects.filter(
            is_active=True,
            organization=self.request.user.organization
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {
                "message": "Journal deleted successfully"
            },
            status=status.HTTP_200_OK
        )

@extend_schema(tags=["Journal"])
class JournalDetailView(generics.RetrieveAPIView):
    serializer_class = JournalDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Journal.objects.filter(
            is_active=True,
            organization=self.request.user.organization
        )