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
    path('chart-of-accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('chart-of-accounts/<int:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
]


# urls for Journal app
from accounts.views.journal.views import JournalListCreateView, JournalRetrieveUpdateDestroyView, JournalDetailView
journal_urlpatterns = [
    path('journals/', JournalListCreateView.as_view(), name='journal-list-create'),
    path('journals/<int:pk>/', JournalRetrieveUpdateDestroyView.as_view(), name='journal-retrieve-update-destroy'),
    path('journals/<int:pk>/detail/', JournalDetailView.as_view(), name='journal-detail'),
]

# urls for Journal Line app
from accounts.views.journalline.views import JournalListCreateView, JournalRetrieveUpdateDestroyView
journal_line_urlpatterns = [
    path('journal-lines/', JournalListCreateView.as_view(), name='journal-line-list-create'),
    path('journal-lines/<int:pk>/', JournalRetrieveUpdateDestroyView.as_view(), name='journal-line-retrieve-update-destroy'),
]

urlpatterns = [
    *group_urlpatterns,
    *account_urlpatterns,
    *journal_urlpatterns,
    *journal_line_urlpatterns,
]