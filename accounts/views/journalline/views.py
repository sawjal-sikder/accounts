from rest_framework import generics, permissions,status,filters
from rest_framework.response import Response

from accounts.models.journalline import JournalLine
from accounts.serializers.journalline.serializers import JournalLineSerializer

from drf_spectacular.utils import extend_schema
from config.pagination import CustomPagination

@extend_schema(tags=["Journal Line"])
class JournalListCreateView(generics.ListCreateAPIView):
    queryset = JournalLine.objects.all()
    serializer_class = JournalLineSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['account__name', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


    
@extend_schema(tags=["Journal Line"])
class JournalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JournalLine.objects.all()
    serializer_class = JournalLineSerializer
    permission_classes = [permissions.IsAuthenticated]

        
    def perform_destroy(self, instance):
        instance.delete()
        
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {
                "message": "Journal line deleted successfully"
            },
            status=status.HTTP_200_OK
        )
