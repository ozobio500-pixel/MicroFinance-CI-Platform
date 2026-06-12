from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClient
from notifications.services import notify_user

from .models import InsuranceProduct, InsuranceSubscription
from .serializers import (
    InsuranceProductSerializer,
    InsuranceSubscriptionSerializer,
    SubscribeSerializer,
)


class InsuranceProductListView(generics.ListAPIView):
    queryset = InsuranceProduct.objects.filter(is_active=True)
    serializer_class = InsuranceProductSerializer


class InsuranceSubscribeView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub = serializer.create_subscription(request.user)
        notify_user(
            request.user,
            "Souscription confirmée",
            f"Police {sub.policy_number} valide jusqu'au {sub.end_date}.",
            "insurance_subscribed",
        )
        return Response(
            InsuranceSubscriptionSerializer(sub).data,
            status=status.HTTP_201_CREATED,
        )


class MyPoliciesView(generics.ListAPIView):
    serializer_class = InsuranceSubscriptionSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return InsuranceSubscription.objects.filter(
            client=self.request.user,
            status=InsuranceSubscription.Status.ACTIVE,
        ).select_related("product")
