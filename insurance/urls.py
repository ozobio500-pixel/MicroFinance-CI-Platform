from django.urls import path

from .views import InsuranceProductListView, InsuranceSubscribeView, MyPoliciesView

urlpatterns = [
    path("products/", InsuranceProductListView.as_view(), name="insurance-products"),
    path("subscribe/", InsuranceSubscribeView.as_view(), name="insurance-subscribe"),
    path("my-policies/", MyPoliciesView.as_view(), name="my-policies"),
]
