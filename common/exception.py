import logging

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ErrorDetail

from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict


logger = logging.getLogger(__name__)


class InsightHubException(APIException):
    """
    Exception class to throw Exceptions
    """

    status_code = 400
    default_code = "error"
    default_detail = "Error Occurred"
    default_info = None

    def __init__(self, code, detail, status_code, info=None):
        super().__init__(detail=detail, code=code)
        self.code = code if code else self.default_code
        self.info = info
        self.status_code = status_code


class InsightHubExceptionHandler:
    """
    Exception Handler class to handle and report API exceptions
    """

    @classmethod
    def is_path_whitelisted(cls, context):
        # Example: skip logging or custom formatting for specific paths
        request = context.get("request")
        path = request.path if request else ""
        whitelist = []  # ["/health", "/metrics"] # whitelistable paths
        return any(path.startswith(p) for p in whitelist)

    @classmethod
    def handle(cls, exc, context):
        response = exception_handler(exc, context)
        if cls.is_path_whitelisted(context=context):
            try:
                if response is not None and isinstance(exc, InsightHubException):
                    return cls._handle_api_exception(exc, response)

                if response is not None and isinstance(exc, APIException):
                    return cls._handle_inbuilt_api_exception(exc, response)

            except Exception as e:
                logger.error(
                    f"Exception occurred while parsing API exception: {str(e)}"
                )

        return response

    @classmethod
    def _handle_api_exception(cls, exc, response):
        error_code = getattr(exc, "code", cls.default_code)
        error_message = str(getattr(exc, "detail", cls.default_detail))

        error_data = {
            "code": error_code,
            "message": error_message,
        }

        # Optionally include additional info (if you want)
        if hasattr(exc, "info") and exc.info:
            error_data["info"] = exc.info

        return Response(
            data=[error_data],
            status=getattr(exc, "status_code", response.status_code),
            headers=getattr(response, "headers", None),
        )

    @classmethod
    def flatten_error_detail(cls, error_detail, parent_key=""):
        flat_errors = {}

        for key, value in error_detail.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, dict):
                flat_errors.update(cls.flatten_error_detail(value, full_key))
            else:
                # handle list of errors under the same field
                flat_errors[full_key] = value if isinstance(value, list) else [value]

        return flat_errors

    @classmethod
    def _handle_inbuilt_api_exception(cls, exc, response):
        error_detail = getattr(exc, "detail", None)
        errors_data = []

        if not error_detail:
            return Response(
                data=errors_data, status=response.status_code, headers=response.headers
            )

        # Case 1: List of errors
        if isinstance(error_detail, list):
            for error in error_detail:
                errors_data.append(
                    {"code": getattr(error, "code", "error"), "message": str(error)}
                )

        # Case 2: Single ErrorDetail instance
        elif isinstance(error_detail, ErrorDetail):
            errors_data.append(
                {"code": error_detail.code, "message": str(error_detail)}
            )

        # Case 3: Dict (field-specific validation errors)
        elif isinstance(error_detail, dict):
            flat_errors = cls.flatten_error_detail(error_detail)
            for field, value in flat_errors.items():
                if isinstance(value, list):
                    for error in value:
                        errors_data.append(
                            {
                                "field": field,
                                "code": getattr(error, "code", "error"),
                                "message": str(error),
                            }
                        )
                elif isinstance(value, ErrorDetail):
                    errors_data.append(
                        {"field": field, "code": value.code, "message": str(value)}
                    )

        # Case 4: ReturnDict (from DRF serializers)
        elif isinstance(error_detail, ReturnDict):
            for field, detail in error_detail.items():
                if isinstance(detail, list):
                    for error in detail:
                        errors_data.append(
                            {
                                "field": field,
                                "code": getattr(error, "code", "error"),
                                "message": str(error),
                            }
                        )
                elif isinstance(detail, ErrorDetail):
                    errors_data.append(
                        {"field": field, "code": detail.code, "message": str(detail)}
                    )

        return Response(
            data=errors_data,
            status=response.status_code,
            headers=response.headers,
        )


def standard_api_exception_handler(exc, context):
    """
    Exception Handler function that invokes the HelixBeat standard API exception handler

    Args:
        exc:
        context:

    Returns:

    """
    return InsightHubExceptionHandler.handle(exc, context)
