from rest_framework.response import Response


def success_response(data=None, message="", meta=None, status=200):
    return Response(
        {
            "success": True,
            "data": data if data is not None else {},
            "message": message,
            "meta": meta or {},
        },
        status=status,
    )


def error_response(code, message, details=None, status=400):
    return Response(
        {
            "success": False,
            "code": code,
            "message": message,
            "details": details or {},
        },
        status=status,
    )
