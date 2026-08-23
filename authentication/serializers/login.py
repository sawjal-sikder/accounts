from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class LoginSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        return {
            "message": "Login successful",
            "user_details": {
                "email": self.user.email,
                "username": self.user.username,
                "is_active": self.user.is_active,
                "is_staff": self.user.is_staff,
                "is_superuser": self.user.is_superuser,
            },
            "refresh": data['refresh'],
            "access": data['access'],
        }