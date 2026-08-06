from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.db import DatabaseError
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    custom exception handler for DRF
    :param exc: exception
    :param context: context information
    :return: Response
    """
    # use DRF's default exception handler to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict) and 'login' in response.data:
            response = Response(response.data, status=status.HTTP_200_OK)
        else:
            response.data['status_code'] = response.status_code
            response = Response(response.data, status=response.status_code)
    else:
        # handle the exception
        print(exc, DatabaseError)
        if isinstance(exc, DatabaseError):
            response = Response({'msg': 'A database error occurred.'})
        else:
            # handle other exceptions
            # response = Response({'msg': 'An unknown error occurred.'})
            pass

    return response
