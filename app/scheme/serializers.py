from itertools import chain

from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from rest_framework import status

from app.utils import get_fields_list
from core.models import Box, Fiber, Wire, InputPigTail, OutputPigTail, Splitter


class SchemeSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        if not isinstance(instance, Box):
            raise TypeError("Wrong type of instance passed for schema serializing")
        inputs = get_fields_list(instance.inbox_input.all(), 'input.id')
        outputs = get_fields_list(instance.inbox_output.all(), 'output.id')
        splitters = get_fields_list(instance.inbox_splitter.all(), 'label')
        fibers = get_fields_list(instance.inbox_fiber.all(), 'id')
        return {
            "inputs": inputs,
            "outputs": outputs,
            "splitters": splitters,
            "fibers": fibers
        }


class InternalSchemeSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        if not isinstance(instance, Box):
            raise TypeError("Wrong type of instance passed for schema serializing")
        inputs = list(map(dict, InputPigTailSerializer(instance.inbox_input.all(), many=True).data))
        outputs = list(map(dict, OutputPigTailSerializer(instance.inbox_output.all(), many=True).data))
        splitters = list(map(dict, SplitterSerializer(instance.inbox_splitter.all(), many=True).data))
        fibers = list(map(dict, FiberSerializer(instance.inbox_fiber.all(), many=True).data))
        return {
            "inputs": inputs,
            "outputs": outputs,
            "splitters": splitters,
            "fibers": fibers
        }


class NodeSchemeValidator:
    @staticmethod
    def validated_value(objects: QuerySet):
        if len(objects) > 1:
            raise serializers.ValidationError("Required constraint is broken")
        elif len(objects) == 1:
            return objects[0]


class SplitterSerializer(serializers.ModelSerializer):
    node_id = serializers.CharField(source='label')

    class Meta:
        model = Splitter
        fields = '__all__'


class SplitterSchemeSerializer(SplitterSerializer):
    node_type = serializers.ReadOnlyField(default="splitters")

    class Meta(SplitterSerializer.Meta):
        fields = ['node_id', 'node_type']


class SplitterPostSchemeSerializer(SplitterSchemeSerializer):
    box_id = serializers.IntegerField(min_value=0, required=True)

    class Meta(SplitterSchemeSerializer.Meta):
        fields = ['node_id', 'node_type', "box_id"]

    def to_internal_value(self, data):
        objects = Splitter.objects.filter(label=data['node_id'], box=data['box_id'])
        return NodeSchemeValidator.validated_value(objects)


class SplitterPostSerializer(serializers.Serializer):
    box_id = serializers.IntegerField(min_value=0, required=True)
    n_terminals = serializers.IntegerField(min_value=0, required=False)

    def create(self, validated_data):
        box = Box.objects.get(pk=validated_data.pop('box_id'))
        ipt = Splitter.objects.create(box=box, **validated_data)
        ipt.save()
        return ipt


class SplitterPutSerializer(serializers.Serializer):
    n_terminals = serializers.IntegerField(min_value=0, required=True)

    def validate_n_terminals(self, value):
        if self.instance.outputs.count() > value:
            raise serializers.ValidationError(
                "Current splitter is already connected with more fibers than the requested value")
        return value

    def update(self, instance, validated_data):
        instance.n_terminals = validated_data.get('n_terminals', instance.n_terminals)
        return instance


class InputPigTailSerializer(serializers.ModelSerializer):
    node_id = serializers.SerializerMethodField()

    class Meta:
        model = InputPigTail
        fields = '__all__'

    def get_node_id(self, obj):
        return str(obj.input.id)


class InputPigTailSchemeSerializer(InputPigTailSerializer):
    node_type = serializers.ReadOnlyField(default="inputs")

    class Meta(InputPigTailSerializer.Meta):
        fields = ['node_id', 'node_type']


class InputPigTailPostSchemeSerializer(InputPigTailSchemeSerializer):
    box_id = serializers.IntegerField(min_value=0, required=True)

    class Meta(InputPigTailSchemeSerializer.Meta):
        fields = ['node_id', 'node_type', "box_id"]

    def to_internal_value(self, data):
        objects = InputPigTail.objects.filter(input=data['node_id'], box=data['box_id'])
        return NodeSchemeValidator.validated_value(objects)


class InputPigTailPostSerializer(serializers.Serializer):
    box_id = serializers.IntegerField(min_value=0, required=True)
    node_id = serializers.IntegerField(min_value=0, required=True)
    n_terminals = serializers.IntegerField(min_value=0, required=False)

    def validate_node_id(self, value):
        if not Wire.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Requested wire doesn't exists")
        return value

    def validate(self, attrs):
        wire = Wire.objects.get(pk=attrs['node_id'])
        box = Box.objects.get(pk=attrs['box_id'])
        if wire not in chain(box.output_wires.reverse(), box.input_wires.reverse()):
            raise serializers.ValidationError("Requested wire doesn't connected to requested box",
                                              status.HTTP_406_NOT_ACCEPTABLE)
        if InputPigTail.objects.filter(input=wire, box=box).exists():
            raise serializers.ValidationError("Requested input is already exists", status.HTTP_409_CONFLICT)
        return attrs

    def create(self, validated_data):
        wire = Wire.objects.get(pk=validated_data.pop('node_id'))
        box = Box.objects.get(pk=validated_data.pop('box_id'))
        ipt = InputPigTail.objects.create(input=wire, box=box, **validated_data)
        ipt.save()
        return ipt


class InputPigTailPutSerializer(serializers.Serializer):
    n_terminals = serializers.IntegerField(min_value=0, required=True)

    def validate_n_terminals(self, value):
        if self.instance.terminals.count() > value:
            raise serializers.ValidationError(
                "Current input is already connected with more fibers than the requested value")
        return value

    def update(self, instance, validated_data):
        instance.n_terminals = validated_data.get('n_terminals', instance.n_terminals)
        instance.save()
        return instance


class OutputPigTailSerializer(serializers.ModelSerializer):
    node_id = serializers.SerializerMethodField()

    class Meta:
        model = OutputPigTail
        fields = '__all__'

    def get_node_id(self, obj):
        return str(obj.output.id)


class OutputPigTailSchemeSerializer(OutputPigTailSerializer):
    node_type = serializers.ReadOnlyField(default="outputs")

    class Meta(OutputPigTailSerializer.Meta):
        fields = ['node_id', 'node_type']


class OutputPigTailPostSchemeSerializer(OutputPigTailSchemeSerializer):
    box_id = serializers.IntegerField(min_value=0, required=True)

    class Meta(OutputPigTailSchemeSerializer.Meta):
        fields = ['node_id', 'node_type', "box_id"]

    def to_internal_value(self, data):
        objects = OutputPigTail.objects.filter(output=data['node_id'], box=data['box_id'])
        return NodeSchemeValidator.validated_value(objects)


class OutputPigTailPostSerializer(serializers.Serializer):
    box_id = serializers.IntegerField(min_value=0, required=True)
    node_id = serializers.IntegerField(min_value=0, required=True)
    n_terminals = serializers.IntegerField(min_value=0, required=False)

    def validate_node_id(self, value):
        if not Wire.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Requested wire doesn't exists")
        return value

    def validate(self, attrs):
        wire = Wire.objects.get(pk=attrs['node_id'])
        box = Box.objects.get(pk=attrs['box_id'])
        if wire not in chain(box.output_wires.reverse(), box.input_wires.reverse()):
            raise serializers.ValidationError("Requested wire doesn't connected to requested box",
                                              status.HTTP_406_NOT_ACCEPTABLE)
        if OutputPigTail.objects.filter(output=wire, box=box).exists():
            raise serializers.ValidationError("Requested output is already exists", status.HTTP_409_CONFLICT)
        return attrs

    def create(self, validated_data):
        wire = Wire.objects.get(pk=validated_data.pop('node_id'))
        box = Box.objects.get(pk=validated_data.pop('box_id'))
        ipt = OutputPigTail.objects.create(output=wire, box=box, **validated_data)
        ipt.save()
        return ipt


class OutputPigTailPutSerializer(serializers.Serializer):
    n_terminals = serializers.IntegerField(min_value=0, required=True)

    def validate_n_terminals(self, value):
        if self.instance.terminals.count() > value:
            raise serializers.ValidationError(
                "Current output is already connected with more fibers than the requested value")
        return value

    def update(self, instance, validated_data):
        instance.n_terminals = validated_data.get('n_terminals', instance.n_terminals)
        instance.save()
        return instance


class NodeField(GenericRelatedField):
    def get_deserializer_for_data(self, value):
        serializers = list(filter(
            lambda x: x.get_fields().get('node_type').default == value['node_type'],
            self.serializers.values()))
        l = len(serializers)
        if l < 1:
            raise ImproperlyConfigured(
                'Could not determine a valid serializer for value %r.' % value)
        elif l > 1:
            raise ImproperlyConfigured(
                'There were multiple serializers found for value %r.' % value)
        return serializers[0]

    def to_internal_value(self, data):
        try:
            serializer = self.get_deserializer_for_data(data)
        except ImproperlyConfigured as e:
            raise serializers.ValidationError(e)
        return serializer.to_internal_value(data)


class FiberSerializer(serializers.ModelSerializer):
    from_node = NodeField({
        InputPigTail: InputPigTailSchemeSerializer(),
        Splitter: SplitterSchemeSerializer(),
    }, source='start_object')

    to_node = NodeField({
        OutputPigTail: OutputPigTailSchemeSerializer(),
        Splitter: SplitterSchemeSerializer(),
    }, source='end_object')

    class Meta:
        model = Fiber
        fields = '__all__'

    def validate_color(self, value):
        # TODO: check in graphviz color scheme
        return value


class FiberPostSerializer(FiberSerializer):
    box_id = serializers.IntegerField(min_value=0, required=True)
    from_node = NodeField({
        InputPigTail: InputPigTailPostSchemeSerializer(),
        Splitter: SplitterPostSchemeSerializer(),
    }, source='start_object')

    to_node = NodeField({
        OutputPigTail: OutputPigTailPostSchemeSerializer(),
        Splitter: SplitterPostSchemeSerializer(),
    }, source='end_object')

    class Meta(FiberSerializer.Meta):
        fields = ["from_node", "to_node", "color", "box_id"]

    def validate(self, attrs):
        if not (bool(attrs['start_object']) and bool(attrs['end_object'])):
            raise serializers.ValidationError("Both of ends of fiber are required")
        return attrs


class FiberPutSerializer(FiberSerializer):
    from_node = NodeField({
        InputPigTail: InputPigTailPostSchemeSerializer(),
        Splitter: SplitterPostSchemeSerializer(),
    }, source='start_object', required=False)

    to_node = NodeField({
        OutputPigTail: OutputPigTailPostSchemeSerializer(),
        Splitter: SplitterPostSchemeSerializer(),
    }, source='end_object', required=False)

    class Meta(FiberSerializer.Meta):
        extra_kwargs = {"color": {"required": False}}

    def update(self, instance, validated_data):
        instance.start_object = validated_data.get('start_object', instance.start_object)
        instance.end_object = validated_data.get('end_object', instance.end_object)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        return instance
