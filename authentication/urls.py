from django.urls import path
from authentication.views.login import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
]