from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Detail, Order
from order.serializers import OrderStatusUpdateSerializer, \
    OrderStatusRetrieveSerializer, OrderSerializer, \
    DetailSerializer, OrderDetailRetrieveSerializer


class BaseOrderAttrViewSet(viewsets.ModelViewSet):
    """Base ViewSet for user owned order attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(order__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class DetailViewSet(BaseOrderAttrViewSet):
    """Manage pizza order in the database"""
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """Manage orders in the database"""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the orders for the authenticated user"""
        detail = self.request.query_params.get('detail')
        queryset = self.queryset
        if detail:
            detail_ids = self._params_to_ints(detail)
            queryset = queryset.filter(detail__id__in=detail_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return OrderDetailRetrieveSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new order"""
        serializer.save(user=self.request.user)


class OrderRetrieveUpdateStatusView(viewsets.ModelViewSet):
    """
    View to get or update a specific order detail.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()

    def get_serializer_class(self):
        method = self.request.method
        serializer_class = OrderStatusRetrieveSerializer
        if method == 'PUT':
            serializer_class = OrderStatusUpdateSerializer
        return serializer_class
