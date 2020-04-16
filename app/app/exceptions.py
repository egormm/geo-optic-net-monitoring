from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        details = response.data.copy()
        response.data.clear()

        response.data['success'] = False
        response.data['error'] = {
            "code": response.status_code,
            "message": response.reason_phrase,
        }
        if len(details):
            response.data['error'].update({"details": details})

    return response
