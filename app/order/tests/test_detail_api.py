from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Detail, Order

from order.serializers import DetailSerializer

DETAIL_URL = reverse('order:detail-list')


class PublicDetailApiTests(TestCase):
    """Test the publicly available pizza order API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving pizza order"""
        res = self.client.get(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDetailApiTests(TestCase):
    """Test the authorized user pizza detail API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@mahsa.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_detail(self):
        """Test retrieving pizza detail"""
        Detail.objects.create(user=self.user, flavour=1, size=1, quantity=1)
        Detail.objects.create(user=self.user, flavour=2, size=2, quantity=1)

        res = self.client.get(DETAIL_URL)

        detail = Detail.objects.all().order_by('-id')
        serializer = DetailSerializer(detail, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_limited_to_user(self):
        """Test that pizza detail returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@mahsa.com',
            'testpass'
        )
        Detail.objects.create(user=user2, flavour=1,
                              size=2, quantity=1)
        detail = Detail.objects.create(user=self.user, flavour=3,
                                       size=3, quantity=1)

        res = self.client.get(DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['flavour'], detail.flavour)

    def test_create_detail_successful(self):
        """Test creating a new pizza detail"""
        payload = {'flavour': 1,
                   'size': 1,
                   'quantity': 1
                   }
        self.client.post(DETAIL_URL, payload)

        exists = Detail.objects.filter(
            user=self.user,
            flavour=payload['flavour'],
            size=payload['size'],
            quantity=payload['quantity']
        ).exists()
        self.assertTrue(exists)

    def test_retrieve_detail_assigned_to_order(self):
        """Test filtering pizza detail by those assigned to recipes"""
        detail1 = Detail.objects.create(user=self.user, flavour=1,
                                        size=1, quantity=1)
        detail2 = Detail.objects.create(user=self.user, flavour=2,
                                        size=2, quantity=2)
        order = Order.objects.create(
            user=self.user,
            name='pizza',
            phone='09395679308',
            address='address',
            status=1
        )
        order.detail.add(detail1)

        res = self.client.get(DETAIL_URL, {'assigned_only': 1})

        serializer1 = DetailSerializer(detail1)
        serializer2 = DetailSerializer(detail2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_detail_assigned_unique(self):
        """Test filtering pizza detail by assigned returns unique items"""
        detail = Detail.objects.create(user=self.user, flavour=1,
                                       size=2, quantity=1)
        Detail.objects.create(user=self.user, flavour=2,
                              size=3, quantity=3)
        order1 = Order.objects.create(
            user=self.user,
            name='pizza',
            phone='09395679309',
            address='address1',
            status=1
        )
        order1.detail.add(detail)
        order2 = Order.objects.create(
            user=self.user,
            name='pizza',
            phone='09395679310',
            address='address',
            status=1
        )
        order2.detail.add(detail)

        res = self.client.get(DETAIL_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
