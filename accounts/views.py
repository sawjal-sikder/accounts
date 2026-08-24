from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
import os

@user_passes_test(lambda u: u.is_active and u.is_staff, login_url="/admin/login/")
def database_backup_view(request):
    db_path = settings.DATABASES["default"]["NAME"]
    db_path_str = str(db_path)

    if not os.path.exists(db_path_str):
        raise Http404("Database file not found.")

    return FileResponse(
        open(db_path_str, "rb"),
        as_attachment=True,
        filename="db_backup.sqlite3",
    )
