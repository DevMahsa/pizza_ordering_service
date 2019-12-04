from rest_framework import serializers

from core.models import Order, Detail
from order.validators import UniqueUpdateStatusValidator


class DetailSerializer(serializers.ModelSerializer):
    """Serializer for detail objects"""

    class Meta:
        model = Detail
        fields = ('id', 'flavour', 'size', 'quantity')
        read_only_fields = ('id',)

    def get_size(self, obj):
        return obj.get_size_display()

    def get_flavour(self, obj):
        return obj.get_flavour_display()

    def get_quantity(self, obj):
        return obj.get_quantity_display()


class OrderSerializer(serializers.ModelSerializer):
    """Serialize a order"""
    detail = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Detail.objects.all()
    )

    class Meta:
        model = Order
        fields = (
            'id', 'name', 'detail', 'status',
            'phone', 'address'
        )
        read_only_fields = ('id',)

    def get_status(self, obj):
        return obj.get_status_display()

    validators = [
        UniqueUpdateStatusValidator(),
    ]


class OrderDetailRetrieveSerializer(OrderSerializer):
    """Serialize a order detail"""
    detail = DetailSerializer(many=True, read_only=True)


class OrderStatusRetrieveSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
        )

    def get_status(self, obj):
        return obj.get_status_display()


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'status',
        )

    def get_status(self, obj):
        return obj.get_status_display()
