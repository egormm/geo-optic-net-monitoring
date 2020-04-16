from netaddr import IPAddress, EUI
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from app.response import MapResponse, BoxResponse
from app.views import ObjectAPIView
from core.models import Box, Wire, Client
from .serializers import (WireSerializer,
                          PostBoxSerializer,
                          PostWireSerializer,
                          PutBoxSerializer,
                          box_list_view)


class Map(ObjectAPIView):
    """APIView to get and post box objects"""

    def get(self, request):
        return MapResponse(request.query_params)


class BoxList(ObjectAPIView):
    """APIView to get and post box objects"""

    def get(self, request):
        return Response(box_list_view())

    def post(self, request):
        serializer = PostBoxSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return MapResponse(request.query_params)
        raise ValidationError(detail=serializer.errors)


class BoxDetail(ObjectAPIView):

    def get(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        return BoxResponse(box)

    def put(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        serializer = PutBoxSerializer(box, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return MapResponse(request.query_params)

    def delete(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        box.delete()
        return MapResponse(request.query_params)


class WireList(ObjectAPIView):
    """APIView to get and post wire objects"""

    def get(self, request):
        wires = Wire.objects.all()
        serializer = WireSerializer(wires, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostWireSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return MapResponse(request.query_params)
        raise ValidationError(serializer.errors)


class WireDetail(ObjectAPIView):

    def get(self, request, pk):
        wire = get_object_or_404(Wire.objects.all(), pk=pk)
        serializer = WireSerializer(wire)
        return Response(serializer.data)

    def put(self, request, pk):
        raise NotImplementedError("Need additional serializer for updating")
        # wire = self.get_object(pk)
        # serializer = WireSerializer(wire, data=request.data)
        # if serializer.is_valid():
        #     serializer.save(user=request.user)
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        wire = get_object_or_404(Wire.objects.all(), pk=pk)
        wire.delete()
        return MapResponse(request.query_params)


class ClientList(ObjectAPIView):

    def get(self, request):
        return Response({
            "ip": sorted(map(lambda x: str(IPAddress(x)),
                             Client.objects.filter(connected_box__isnull=True).values_list('ip', flat=True))),
            "mac": sorted(map(lambda x: str(EUI(x)),
                              Client.objects.filter(connected_box__isnull=True).values_list('mac', flat=True))),
        }
        )
