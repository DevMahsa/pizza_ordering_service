from rest_framework import serializers

from core.models import Order


class UniqueUpdateStatusValidator(object):
    instance = None
    status_not_permited = [3, 4, 5]

    def set_context(self, serializer):
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, 'instance', None)

    def __call__(self, attrs):
        """
        It should not be possible to update an order for
        some statutes of delivery (e.g. delivered).
        """
        order = self.instance or Order
        if order.status in self.status_not_permited:
            raise serializers.ValidationError({
                'Sorry':
                    (
                        u'This order is `{status}` and cannot be '
                        u'updated at this moment'
                    ).format(
                        status=order.get_status_display()
                    )
            })
