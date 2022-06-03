def ok(json):
    return json, 200


def created(json):
    return json, 201


def bad_request(json):
    return json, 400


def unauthorized(json):
    return json, 401


def forbidden(json):
    return json, 403


def not_found(json):
    return json, 404


def internal_server_error(json):
    return json, 500
