from django.contrib import admin
from django.urls import path, include
from .views import main
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

User = get_user_model()

api_v1_urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("authentication/", include("authentication.urls")),
    path("organizations/", include("organization.urls")),
]

urlpatterns = [
    # API Endpoints
    path("", main),
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_urlpatterns)),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Unregister the Group and User models from the admin site
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass