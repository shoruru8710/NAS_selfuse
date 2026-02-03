from rest_framework import generics, permissions

from .models import CoinBalance, CoinTransaction
from .serializers import CoinBalanceSerializer, CoinTransactionSerializer


class CoinBalanceView(generics.RetrieveAPIView):
    serializer_class = CoinBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        balance, _ = CoinBalance.objects.get_or_create(user=self.request.user)
        return balance


class CoinTransactionListView(generics.ListAPIView):
    serializer_class = CoinTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CoinTransaction.objects.filter(user=self.request.user)
