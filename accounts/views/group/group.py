from rest_framework import permissions
from rest_framework import generics
from accounts.models import AccountGroup
from accounts.serializers.group.group import GroupSerializer

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = AccountGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]