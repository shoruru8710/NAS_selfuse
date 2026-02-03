import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Log all API requests for audit purposes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000

        logger.info(
            "%s %s %s %.1fms user=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            getattr(request.user, "email", "anonymous"),
        )
        return response
