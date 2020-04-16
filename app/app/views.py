from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication import BearerTokenAuthentication


class ObjectAPIView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        # At first we need to check if exception happened,
        # it means that response have already processed
        if hasattr(response, 'exception') and not response.exception:
            response.data = {'success': True,
                             'data': response.data}
        return super().finalize_response(request, response,
                                         *args, **kwargs)


class Ping(APIView):

    def get(self, *args, **kwargs):
        return Response("pong")
