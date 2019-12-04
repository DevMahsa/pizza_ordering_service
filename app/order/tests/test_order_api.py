from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Order, Detail

from order.serializers import OrderSerializer, OrderDetailRetrieveSerializer

ORDER_URL = reverse('order:order-list')


def detail_url(order_id):
    """Return order detail URL"""
    return reverse('order:order-detail', args=[order_id])


def sample_detail(user, flavour=1, size=1, quantity=1):
    """Create and return a sample detail"""
    return Detail.objects.create(user=user, flavour=flavour,
                                 size=size, quantity=quantity)


def sample_order(user, **params):
    """Create and return a sample order"""
    defaults = {
        'name': 'pizza',
        'phone': '9395679312',
        'address': 'address',
    }
    defaults.update(params)

    return Order.objects.create(user=user, **defaults)


class PublicOrderApiTests(TestCase):
    """Test unauthenticated order API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrderApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@mahsa.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_order(self):
        """Test retrieving a list of orders"""
        order = sample_order(user=self.user)
        order.detail.add(sample_detail(user=self.user))

        res = self.client.get(ORDER_URL)

        orders = Order.objects.all().order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_order_limited_to_user(self):
        """Test retrieving orders for user"""
        user2 = get_user_model().objects.create_user(
            'other@mahsa.com',
            'password123'
        )
        sample_order(user=user2)
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.filter(user=self.user)
        serializer = OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_order_detail(self):
        """Test viewing a recipe detail"""
        order = sample_order(user=self.user)
        order.detail.add(sample_detail(user=self.user))

        url = detail_url(order.id)
        res = self.client.get(url)

        serializer = OrderDetailRetrieveSerializer(order)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_order(self):
        """Test creating recipe"""
        payload = {
            'name': 'pizza',
            'phone': '9396579202',
            'address': 'address'

        }
        res = self.client.post(ORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(order, key))

    def test_create_order_with_detail(self):
        """Test creating a recipe with detail"""
        detail1 = sample_detail(user=self.user, flavour=2,
                                size=1, quantity=3)
        detail2 = sample_detail(user=self.user, flavour=1,
                                size=3, quantity=3)
        payload = {
            'detail': [detail1.id, detail2.id],
            'name': 'pizza',
            'phone': '9396579302',
            'address': 'address'
        }
        res = self.client.post(ORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data['id'])
        details = order.detail.all()
        self.assertEqual(details.count(), 2)
        self.assertIn(detail1, details)
        self.assertIn(detail2, details)

    def test_partial_update_order(self):
        """Test updating a recipe with patch"""
        order = sample_order(user=self.user)
        order.detail.add(sample_detail(user=self.user))
        new_detail = sample_detail(user=self.user,
                                   flavour=1, size=2, quantity=3)

        payload = {'name': 'pizza', 'status': 1,
                   'phone': '982188973140', 'address': 'address',
                   'detail': [new_detail.id]}
        url = detail_url(order.id)
        self.client.patch(url, payload)
        order.refresh_from_db()
        self.assertEqual(order.name, payload['name'])
        self.assertEqual(order.status, payload['status'])
        self.assertEqual(order.phone, payload['phone'])
        self.assertEqual(order.address, payload['address'])
        detail = order.detail.all()
        self.assertEqual(len(detail), 1)
        self.assertIn(new_detail, detail)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        order = sample_order(user=self.user)
        order.detail.add(sample_detail(user=self.user))
        payload = {
            'name': 'pizza',
            'phone': '9396579302',
            'address': 'address'

        }
        url = detail_url(order.id)
        self.client.put(url, payload)

        order.refresh_from_db()
        self.assertEqual(order.name, payload['name'])
        self.assertEqual(order.phone, payload['phone'])
        self.assertEqual(order.address, payload['address'])
        detail = order.detail.all()
        self.assertEqual(len(detail), 0)

    def test_filter_order_by_detail(self):
        """Test returning orders with specific detail"""
        order1 = sample_order(user=self.user, name='pizza', status=1,
                              phone='982188973148', address='address')
        order2 = sample_order(user=self.user, name='pizza', status=1,
                              phone='982188973150', address='address')
        detail1 = sample_detail(user=self.user, flavour=1, size=2, quantity=3)
        detail2 = sample_detail(user=self.user, flavour=2, size=3, quantity=1)
        order1.detail.add(detail1)
        order2.detail.add(detail2)
        order3 = sample_order(user=self.user, name='pizza', status=1,
                              phone='982188972050', address='address')

        res = self.client.get(
            ORDER_URL,
            {'detail': f'{detail1.id},{detail2.id}'}
        )

        serializer1 = OrderSerializer(order1)
        serializer2 = OrderSerializer(order2)
        serializer3 = OrderSerializer(order3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
