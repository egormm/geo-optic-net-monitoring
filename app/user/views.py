from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from app.views import ObjectAPIView
from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView, ObjectAPIView):
    """Create a new user in the system"""
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken, ObjectAPIView):
    """Create a new auth token for the user"""
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView, ObjectAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user
