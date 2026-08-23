from django.urls import path

# urls for group app
from accounts.views.group.group import GroupListCreateView, GroupRetrieveUpdateDestroyView
group_urlpatterns = [
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(), name='group-retrieve-update-destroy'),
]

# urls for Accounts app
from accounts.views.account.account import AccountListCreateView, AccountRetrieveUpdateDestroyView
account_urlpatterns = [
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<int:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
]


# urls for Organization app
from accounts.views.organization.views import OrganizationListCreateView, OrganizationRetrieveUpdateDestroyView
organization_urlpatterns = [
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('organizations/<int:pk>/', OrganizationRetrieveUpdateDestroyView.as_view(), name='organization-retrieve-update-destroy'),
]


urlpatterns = [
    *group_urlpatterns,
    *account_urlpatterns,
    *organization_urlpatterns,
]