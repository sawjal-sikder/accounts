from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class LoginSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        return {
            "message": "Login successful",
            "user_details": {
                "email": self.user.email,
                "full_name": self.user.username,
            },
            "refresh": data['refresh'],
            "access": data['access'],
        }