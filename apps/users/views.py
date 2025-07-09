import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .forms import CustomLoginForm

logger = logging.getLogger(__name__)

# Message constants
SUCCESS_LOGIN_MSG = "Welcome back, {name}!"
FAIL_LOGIN_MSG = "Invalid email or password. Please try again."
SUCCESS_LOGOUT_MSG = "You have been logged out successfully, {name}."


class SafeRedirectMixin:
    """Mixin for handling secure redirects in authentication views."""

    @staticmethod
    def get_safe_redirect_url(request, fallback_url=None):
        """Get a safe redirect URL from request parameters."""
        next_url = get_next_url(request)
        fallback_url = fallback_url or settings.LOGIN_REDIRECT_URL

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return next_url

        return fallback_url

    @staticmethod
    def is_safe_url(url, request):
        """Check if URL is safe for redirect."""
        if not url:
            return False

        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in ["http", "https"]:
            logger.warning("Blocked unsafe redirect with scheme: %s", parsed.scheme)
            return False

        return url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()})


def get_next_url(request):
    """Unified logic to get 'next' from POST or GET."""
    return request.POST.get("next") or request.GET.get("next") or ""


@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Custom login view with secure redirect and messages."""
    if request.user.is_authenticated:
        redirect_url = SafeRedirectMixin.get_safe_redirect_url(request)
        return HttpResponseRedirect(redirect_url)

    next_url = get_next_url(request)

    if request.method == "POST":
        return handle_login_post(request, next_url)

    form = CustomLoginForm(request)
    return render(request, "users/login.html", {"form": form, "next": next_url})


def handle_login_post(request, next_url):
    """Handle login POST request."""
    form = CustomLoginForm(request, data=request.POST)

    if form.is_valid():
        user = form.get_user()
        login(request, user)

        redirect_url = SafeRedirectMixin.get_safe_redirect_url(request)
        messages.success(request, SUCCESS_LOGIN_MSG.format(name=user.get_full_name() or user.email))

        return HttpResponseRedirect(redirect_url)

    messages.error(request, FAIL_LOGIN_MSG)
    return render(request, "users/login.html", {"form": form, "next": next_url})


@never_cache
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Custom logout view with optional confirmation."""
    if request.method == "POST" or not getattr(settings, "LOGOUT_REQUIRES_POST", False):
        user_name = request.user.get_full_name() or request.user.email if request.user.is_authenticated else "User"

        logout(request)
        messages.info(request, SUCCESS_LOGOUT_MSG.format(name=user_name))

        redirect_url = SafeRedirectMixin.get_safe_redirect_url(
            request, fallback_url=getattr(settings, "LOGOUT_REDIRECT_URL", "/")
        )
        return HttpResponseRedirect(redirect_url)

    return render(request, "users/logout_confirm.html", {"user": request.user})
