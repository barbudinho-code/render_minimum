"""
URL configuration for the public post application.

Routes:
    /                - Public post listing (newest first)
    /post/<id>/     - Individual post view (public posts only)
    /submit/        - Post submission form
    /confirm/<pk>/<token>/  - Confirmation page
    /confirm/<pk>/<token>/confirm/ - Confirm endpoint
    /review/<pk>/<token>/  - Moderation review page
    /review/<pk>/<token>/accept/   - Accept moderation decision
    /review/<pk>/<token>/reject/   - Reject moderation decision
    /account/login/ - User login (optional, for email notifications)
    /account/logout/ - User logout
    /health/        - Health check endpoint for monitoring

All confirmation and moderation links are built from PUBLIC_BASE_URL.
Never use Host header to build trusted links.
"""

from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    # Public post listing.
    path("", views.public_post_list, name="post_list"),

    # Individual post view (public posts only).
    path("post/<int:pk>/", views.public_post_detail, name="post_detail"),

    # Post submission form.
    path("submit/", views.submit_post, name="submit"),

    # Confirmation flow.
    path(
        "confirm/<int:pk>/<str:token>/",
        views.confirmation_page,
        name="confirmation_page",
    ),
    path(
        "confirm/<int:pk>/<str:token>/confirm/",
        views.confirm_post,
        name="confirm",
    ),

    # Moderation review flow.
    path(
        "review/<int:pk>/<str:token>/",
        views.moderation_page,
        name="moderation_page",
    ),
    path(
        "review/<int:pk>/<str:token>/accept/",
        views.accept_moderation,
        name="moderation_accept",
    ),
    path(
        "review/<int:pk>/<str:token>/reject/",
        views.reject_moderation,
        name="moderation_reject",
    ),

    # Account/authentication views (optional, for email notifications).
    path("account/login/", TemplateView.as_view(template_name="accounts/login.html"), name="account_login"),
    path(
        "account/logout/",
        views.logout_view,
        name="account_logout",
    ),

    # Health check endpoint.
    path(
        "health/",
        views.health_check,
        name="health",
    ),
]
