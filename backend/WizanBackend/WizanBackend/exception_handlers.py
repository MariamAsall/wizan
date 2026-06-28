from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler


def custom_exception_handler(exc, context):
    """
    DRF exception handler wrapper.

    django-ratelimit raises django_ratelimit.exceptions.Ratelimited
    (a subclass of Django's PermissionDenied) when a rate limit is hit.
    DRF's default handler would turn that into a generic 403. We intercept
    it here and return a proper 429 with a Retry-After header instead.
    """
    if isinstance(exc, Ratelimited):
        return Response(
            {
                "error": "rate_limited",
                "detail": "Too many requests. Please slow down and try again shortly.",
            },
            status=429,
            headers={"Retry-After": "60"},
        )

    return drf_default_exception_handler(exc, context)
