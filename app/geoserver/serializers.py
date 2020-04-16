import itertools
from json import dumps

from django.contrib.gis.geos import Point, LineString
from netaddr import EUI, IPAddress
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from core.models import Box, Wire, Client
from scheme.serializers import SchemeSerializer, InternalSchemeSerializer
from scheme.utils import get_img


def box_list_view():
    boxes = Box.objects.filter(type_of_box="regular")
    serializer_data = BoxSerializer(boxes, many=True).data
    clients = Box.objects.filter(type_of_box="client")
    serializer_data['features'].extend(ClientBoxSerializer(clients, many=True).data['features'])
    return serializer_data


class BoxValidator:
    def validate_lat(self, value):
        if value > 90 or value < -90:
            raise serializers.ValidationError("Latitude should be from -90 to 90")
        return value

    def validate_lng(self, value):
        if value > 180 or value < -180:
            raise serializers.ValidationError("Latitude should be from -90 to 90")
        return value

    def validate_mac(self, value):
        if value == '':
            return -1
        try:
            mac = EUI(value)
        except Exception as e:
            raise serializers.ValidationError(e)
        return int(mac)

    # TODO: migrate to netaddet valide_ipv4, ipv6 and mac
    def validate_ip(self, value):
        if value == '':
            return -1
        try:
            ip = IPAddress(value)
        except Exception as e:
            raise serializers.ValidationError(e)
        return int(ip)

    def validate(self, attrs):
        if attrs.get("type_of_box", "regular") == "regular":
            for key in ("mac", "ip"):
                if key in attrs.keys():
                    raise serializers.ValidationError("Wrong key %s for regular box" % key)
        return attrs


class BoxSerializer(GeoFeatureModelSerializer):
    """Serializer for box objects"""

    class Meta:
        model = Box
        geo_field = 'point'
        id_field = False
        fields = ('id', 'name', 'description', 'type_of_box')
        read_only_fields = ('id',)


class ClientBoxSerializer(GeoFeatureModelSerializer):
    """Serializer for box objects"""
    online = serializers.SerializerMethodField()

    class Meta:
        model = Box
        geo_field = 'point'
        id_field = False
        fields = ('id', 'name', 'description', 'type_of_box', 'online')
        read_only_fields = ('id',)

    def get_online(self, obj):
        if obj.client is not None:
            return obj.client.online
        return False


class BoxExtendedSerializer(GeoFeatureModelSerializer):
    """Serializer for box objects"""
    scheme = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    related_wires = serializers.SerializerMethodField()

    class Meta:
        model = Box
        geo_field = 'point'
        id_field = False
        fields = ('id', 'name', 'description', 'type_of_box', 'scheme', 'image', 'related_wires')
        read_only_fields = ('id',)

    def get_scheme(self, obj):
        return SchemeSerializer(obj).data

    def get_image(self, obj):
        return get_img(InternalSchemeSerializer(obj).data)

    def get_related_wires(self, obj):
        return [el['id'] for el in itertools.chain(obj.input_wires.values(), obj.output_wires.values())]


class ClientBoxExtendedSerializer(GeoFeatureModelSerializer):
    """Serializer for box objects"""
    mac = serializers.SerializerMethodField()
    ip = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    class Meta:
        model = Box
        geo_field = 'point'
        id_field = False
        fields = ('id', 'name', 'description', 'type_of_box', 'online', 'ip', 'mac')
        read_only_fields = ('id',)

    def get_mac(self, obj):
        if obj.client is not None and obj.client.mac is not None:
            # TODO: try-catch with logging
            return str(EUI(obj.client.mac))
        return ''

    def get_ip(self, obj):
        if obj.client is not None and obj.client.ip is not None:
            # TODO: try-catch with logging
            return str(IPAddress(obj.client.ip))
        return ''

    def get_online(self, obj):
        if obj.client is not None:
            return obj.client.online
        return False


class PostBoxSerializer(serializers.Serializer, BoxValidator):
    """Serializer for creating boxes from regular JSON"""
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    type_of_box = serializers.ChoiceField(choices=('regular', 'client'), required=False, default='regular')
    mac = serializers.CharField(max_length=64, required=False, allow_blank=True)
    ip = serializers.CharField(max_length=32, required=False, allow_blank=True)

    def create(self, validated_data):
        lat = validated_data.pop('lat', None)
        lng = validated_data.pop('lng', None)
        point = Point(lng, lat)
        validated_data['point'] = point
        mac = validated_data.pop('mac', None)
        ip = validated_data.pop('ip', None)
        if mac and mac != -1:
            client = Client.objects.get_or_create(mac=mac)[0]
            if ip and ip != -1:
                client.ip = ip
                client.save()
            validated_data['client'] = client
        box = Box.objects.create(**validated_data)
        box.save()
        return box


class PutBoxSerializer(serializers.Serializer, BoxValidator):
    """Serializer for creating boxes from regular JSON"""
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    type_of_box = serializers.ChoiceField(choices=('regular', 'client'), required=False)
    mac = serializers.CharField(max_length=64, required=False, allow_blank=True)
    ip = serializers.CharField(max_length=32, required=False, allow_blank=True)

    def update(self, instance: Box, validated_data):
        point = instance.point
        if 'lng' in validated_data:
            point.y = validated_data.pop('lng')
        if 'lat' in validated_data:
            point.y = validated_data.pop('lat')
        mac = validated_data.pop('mac', None)
        ip = validated_data.pop('ip', None)
        if mac:
            if mac == -1:
                instance.client = None
            else:
                client = Client.objects.get_or_create(mac=mac)[0]
                if ip:
                    if ip == -1:
                        client.ip = None
                    else:
                        client.ip = ip
                client.save()
                instance.client = client
        if ip and instance.client is not None:
            if ip == -1:
                instance.client.ip = None
            else:
                instance.client.ip = ip
        for name, arg in validated_data.items():
            setattr(instance, name, arg)
        instance.save()
        return instance


class WireSerializer(GeoFeatureModelSerializer):
    """Serilizer for wire objects"""

    class Meta:
        model = Wire
        geo_field = 'path'
        id_field = False
        fields = ('id', 'start', 'end', 'path')
        read_only_fields = ('id',)


class PostWireSerializer(serializers.Serializer):
    """Serializer for creating wires from 2 ids and array"""
    start_id = serializers.IntegerField()
    end_id = serializers.IntegerField()
    path = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            max_length=2,
            min_length=2))
    description = serializers.CharField(required=False)

    def create(self, validated_data):
        validated_data['start'] = Box.objects.get(id=validated_data.pop('start_id', None))
        validated_data['end'] = Box.objects.get(id=validated_data.pop('end_id', None))
        mid_path = list(map(tuple, validated_data['path']))
        validated_data['path'] = LineString(validated_data['start'].point.coords,
                                            *mid_path,
                                            validated_data['end'].point.coords)
        wire = Wire.objects.create(**validated_data)
        wire.save()
        return wire

    @staticmethod
    def validate_pk(value):
        if not Box.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Requested box doesn't exists")

    def validate_start_id(self, value):
        self.validate_pk(value)
        return value

    def validate_end_id(self, value):
        self.validate_pk(value)
        return value


class MapSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "wires": WireSerializer(instance.wires, many=True).data,
            "boxes": box_list_view()
        }


class MapStringSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "wires": dumps(WireSerializer(instance.wires, many=True).data),
            "boxes": dumps(box_list_view())
        }
