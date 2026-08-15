from typing import Any


def success_response(message: str, data: Any) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str) -> dict:
    return {
        "success": False,
        "message": message,
        "data": {},
    }