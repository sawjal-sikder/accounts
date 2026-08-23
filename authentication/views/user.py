from rest_framework import generics, permissions, filters
from django.contrib.auth import get_user_model
from config.pagination import CustomPagination
from authentication.serializers.user import CreateUserSerializer, UserSerializer
from drf_spectacular.utils import extend_schema
User = get_user_model()

@extend_schema(tags=["User"])
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAdminUser]

    
   
@extend_schema(tags=["User"])
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'username', 'phone']
    
    
@extend_schema(tags=["User"])
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]