from django.urls import path
from authentication.views.login import LoginView
from authentication.views.user import UserCreateListView, UserRetrieveUpdateDestroyView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserCreateListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
]