from datetime import datetime


def build_response(status_code: int, message: str, path: str = "", data=None, errors=None):
    return {
        "status_code": status_code,
        "message": message,
        "path": path,
        "data": data,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    }
