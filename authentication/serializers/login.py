from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class LoginSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        return {
            "message": "Login successful",
            "user_details": {
                "email": self.user.email,
                "username": self.user.username,
                "organization": self.user.organization.name if self.user.organization else None,
                "role": self.user.role,
            },
            "refresh": data['refresh'],
            "access": data['access'],
        }