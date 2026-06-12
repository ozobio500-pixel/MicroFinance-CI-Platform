from django.urls import path

from .views import ClientRepaymentHistoryView, InstallmentListView, RecordPaymentView

urlpatterns = [
    path("installments/", InstallmentListView.as_view(), name="installment-list"),
    path("history/", ClientRepaymentHistoryView.as_view(), name="repayment-history"),
    path("installments/<int:pk>/pay/", RecordPaymentView.as_view(), name="record-payment"),
]
