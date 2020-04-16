from collections import namedtuple
from hashlib import md5

from rest_framework.response import Response

from app.utils import query_bool_to_py
from core.models import Wire, Box
from geoserver.serializers import MapSerializer, MapStringSerializer, BoxExtendedSerializer, \
    ClientBoxExtendedSerializer


class MapResponse(Response):
    def __init__(self, query_params=None):
        super().__init__()
        as_string = False
        if query_params is not None and 'as_string' in query_params.keys():
            as_string = query_bool_to_py(query_params['as_string'])
        WireBox = namedtuple('WireBox', ('wires', 'boxes'))
        mapWireBox = WireBox(wires=Wire.objects.all(), boxes=Box.objects.all())
        if as_string:
            serializer = MapStringSerializer
        else:
            serializer = MapSerializer
        self.data = serializer(instance=mapWireBox).data
        self.add_hash(as_string)

    def add_hash(self, as_string):
        h = md5()
        if as_string:
            for element in self.data.values():
                h.update(element.encode())
        else:
            for element in self.data.values():
                for sub_element in sorted(element['features'], key=lambda x: x['properties']['id']):
                    h.update(str(sub_element).encode())
        self.data['message_hash'] = h.hexdigest()


class BoxResponse(Response):
    def __init__(self, box: Box):
        super().__init__()
        if box.type_of_box == 'regular':
            serializer = BoxExtendedSerializer
        elif box.type_of_box == 'client':
            serializer = ClientBoxExtendedSerializer
        else:
            raise ValueError("Unregistered type of box %s" % box.type_of_box)
        self.data = serializer(instance=box).data
