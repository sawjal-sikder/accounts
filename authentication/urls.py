from django.urls import path
from authentication.views.login import LoginView
from authentication.views.user import UserCreateView, UserListView , UserRetrieveUpdateDestroyView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/list/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
]