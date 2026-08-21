from django.contrib import admin

from accounts.admin.group import *
from accounts.admin.account import *
from accounts.admin.journal import *
from accounts.admin.journalline import *

admin.site.site_header = "Administration"
admin.site.site_title = "Administration"
admin.site.index_title = "Administration"
