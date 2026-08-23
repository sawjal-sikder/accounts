from django.urls import path

# urls for group app
from accounts.views.group.group import GroupListCreateView
group_urlpatterns = [
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
]



urlpatterns = [
    *group_urlpatterns,
]