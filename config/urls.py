from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/accounts/", include("accounts.urls")),
    path("api/microcredits/", include("microcredits.urls")),
    path("api/repayments/", include("repayments.urls")),
    path("api/insurance/", include("insurance.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/support/", include("support.urls")),
    path("chat/", TemplateView.as_view(template_name="chat.html"), name="chat-page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
