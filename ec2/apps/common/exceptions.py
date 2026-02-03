from rest_framework.exceptions import APIException


class NASConnectionError(APIException):
    status_code = 502
    default_detail = "NAS storage service is unavailable."
    default_code = "nas_connection_error"


class QuotaExceededError(APIException):
    status_code = 413
    default_detail = "Storage quota exceeded."
    default_code = "quota_exceeded"


class SecurityCheckFailed(APIException):
    status_code = 422
    default_detail = "File did not pass security checks."
    default_code = "security_check_failed"
