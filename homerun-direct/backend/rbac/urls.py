from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from rbac.views import GoogleAuthViewSet,CustomLoginView,CustomPasswordResetView,CustomPasswordResetConfirmView
router = DefaultRouter()
router.register(r"google-auth", GoogleAuthViewSet, basename="google-auth")

urlpatterns = [
    path("auth/login/", CustomLoginView.as_view(), name="custom-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/social/", include("allauth.socialaccount.urls")),
    path("auth/social/<str:provider>/", OAuth2LoginView.as_view(), name="social_login"),

    path("auth/forgot-password/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("auth/reset-password/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    
    path("auth/google-auth/direct/", GoogleAuthViewSet.as_view({'post': 'create'}), name="google_auth_direct"),

    # Include router paths
    path("", include(router.urls)),
]
