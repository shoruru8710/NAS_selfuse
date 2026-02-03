from django.urls import path

from . import views

app_name = "coins"

urlpatterns = [
    path("balance/", views.CoinBalanceView.as_view(), name="balance"),
    path("transactions/", views.CoinTransactionListView.as_view(), name="transactions"),
]
