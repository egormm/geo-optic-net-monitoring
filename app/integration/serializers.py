from netaddr import IPAddress, EUI
from rest_framework import serializers


class MessageSerializer(serializers.BaseSerializer):
    TRUE_VALUES = {
        't', 'T',
        'y', 'Y', 'yes', 'YES',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    }
    FALSE_VALUES = {
        'f', 'F',
        'n', 'N', 'no', 'NO',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    }

    def to_internal_value(self, data):
        return {
            "online": self.validate_online(data.get("Status")),
            "ip": self.validate_ip(data.get("IP")),
        }

    def update(self, instance, validated_data):
        instance.ip = validated_data.get('ip', instance.ip)
        old_status = instance.online
        new_status = validated_data.get('online', old_status)
        if new_status != old_status:
            print(f"Changed status for client({instance.id}) "
                  f"with mac {EUI(instance.mac)} "
                  f"from {old_status} to {new_status}")
        instance.online = new_status
        instance.save()
        return instance

    def validate_online(self, value):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        raise serializers.ValidationError("Wrong value for NewStatus")

    def validate_ip(self, value):
        try:
            return IPAddress(value)
        except Exception as e:
            raise serializers.ValidationError(e)
