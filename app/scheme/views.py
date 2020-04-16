from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from app.response import BoxResponse
from app.views import ObjectAPIView
from core.models import Box
from scheme.serializers import FiberSerializer, SplitterSerializer, InputPigTailSerializer, InputPigTailPostSerializer, \
    OutputPigTailSerializer, InputPigTailPutSerializer, OutputPigTailPostSerializer, OutputPigTailPutSerializer, \
    SplitterPostSerializer, SplitterPutSerializer, FiberPostSerializer, FiberPutSerializer


class FiberList(ObjectAPIView):

    def get(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        fibers = box.inbox_fiber
        serializer = FiberSerializer(fibers, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        request.data['box_id'] = pk
        request.data['from_node']['box_id'] = pk
        request.data['to_node']['box_id'] = pk

        serializer = FiberPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return BoxResponse(box)


class Fiber(ObjectAPIView):

    def put(self, request, pk, fiber_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        fiber = get_object_or_404(box.inbox_fiber.all(), id=fiber_pk)
        if 'from_node' in request.data.keys():
            request.data['from_node']['box_id'] = pk
        if 'to_node' in request.data.keys():
            request.data['to_node']['box_id'] = pk
        update_serializer = FiberPutSerializer(instance=fiber, data=request.data)
        if update_serializer.is_valid(raise_exception=True):
            update_serializer.save()
        return BoxResponse(box)

    def delete(self, request, pk, fiber_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        fiber = get_object_or_404(box.inbox_fiber.all(), id=fiber_pk)
        fiber.delete()
        return BoxResponse(box)


class SplitterList(ObjectAPIView):

    def get(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        splitters = box.inbox_splitter
        serializer = SplitterSerializer(splitters, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        request.data['box_id'] = pk
        serializer = SplitterPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return BoxResponse(box)


class Splitter(ObjectAPIView):

    def put(self, request, pk, splitter_lbl):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        splitter = get_object_or_404(box.inbox_splitter.all(), label=splitter_lbl)
        update_serializer = SplitterPutSerializer(instance=splitter, data=request.data)
        if update_serializer.is_valid(raise_exception=True):
            update_serializer.save()
        return BoxResponse(box)

    def delete(self, request, pk, splitter_lbl):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        splitter = get_object_or_404(box.inbox_splitter.all(), label=splitter_lbl)
        splitter.delete()
        return BoxResponse(box)


class InputPigTailList(ObjectAPIView):

    def get(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtails = box.inbox_input
        serializer = InputPigTailSerializer(pigtails, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        request.data['box_id'] = pk
        serializer = InputPigTailPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return BoxResponse(box)


class InputPigTail(ObjectAPIView):

    def put(self, request, pk, input_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtail = get_object_or_404(box.inbox_input.all(), input=input_pk)
        update_serializer = InputPigTailPutSerializer(instance=pigtail, data=request.data)
        if update_serializer.is_valid(raise_exception=True):
            update_serializer.save()
        return BoxResponse(box)

    def delete(self, request, pk, input_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtail = get_object_or_404(box.inbox_input.all(), input=input_pk)
        pigtail.delete()
        return BoxResponse(box)


class OutputPigTailList(ObjectAPIView):

    def get(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtails = box.inbox_output
        serializer = OutputPigTailSerializer(pigtails, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        request.data['box_id'] = pk
        serializer = OutputPigTailPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return BoxResponse(box)


class OutputPigTail(ObjectAPIView):

    def put(self, request, pk, output_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtail = get_object_or_404(box.inbox_output.all(), output=output_pk)
        update_serializer = OutputPigTailPutSerializer(instance=pigtail, data=request.data)
        if update_serializer.is_valid(raise_exception=True):
            update_serializer.save()
        return BoxResponse(box)

    def delete(self, request, pk, output_pk):
        box = get_object_or_404(Box.objects.all(), pk=pk)
        pigtail = get_object_or_404(box.inbox_output.all(), output=output_pk)
        pigtail.delete()
        return BoxResponse(box)
