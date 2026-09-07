from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.serializers.login import LoginSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Authentication'])
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer