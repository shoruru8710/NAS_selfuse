from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/files/", include("apps.files.urls")),
    path("api/search/", include("apps.search.urls")),
    path("api/coins/", include("apps.coins.urls")),
]
