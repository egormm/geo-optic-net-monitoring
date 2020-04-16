import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Box
from geoserver.serializers import BoxSerializer

BOX_URL = reverse('geoserver:box-list')


def detail_url(box_id):
    """Return recipe detail URL"""
    return reverse('geoserver:box-detail', args=[box_id])


def sample_box(user, **params):
    """Create and return a sample box object"""
    defaults = {
        'name': 'Sample box',
        'point': Point([100, 500])
    }
    defaults.update(params)

    return Box.objects.create(user=user, **defaults)


class PublicBoxApiTests(object):
    """Test unauthenticated box API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BOX_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBoxApiTests(TestCase):
    """Test authenticated box API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testPassword123'
        )
        self.client.force_authenticate(self.user)

    def test_create_basic_box(self):
        """Test creating box"""
        payload = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    40.175027841704186,
                    55.13228026082042
                ]
            },
            "properties": {
                "name": "тестовая",

            }
        }
        res = self.client.post(
            BOX_URL,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Box.objects.count(), 1)
        box = Box.objects.get(id=res.data['id'])
        self.assertEqual(payload['properties']['name'], getattr(box, 'name'))
        self.assertEqual(
            tuple(payload['geometry']['coordinates']),
            getattr(box, 'point').coords
        )

    def test_view_box_detail(self):
        """Test viewing a box detail"""
        box = sample_box(user=self.user)

        url = detail_url(box.id)
        res = self.client.get(url)

        serializer = BoxSerializer(box)
        self.assertEqual(res.data, serializer.data)
