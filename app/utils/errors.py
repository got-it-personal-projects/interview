def error_response(msg, **kwargs):
    response = {
        "error": {
            "message": msg
        }
    }

    for k, v in kwargs.values():
        response["error"][k] = v

    return response
