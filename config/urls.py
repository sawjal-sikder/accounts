from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import Group, User

urlpatterns = [
    path("", admin.site.urls),
    path("admin/", admin.site.urls),
]

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass