from django.urls import path, include
from rest_framework.routers import DefaultRouter

from order import views

router = DefaultRouter()
router.register('detail', views.DetailViewSet)
router.register('order', views.OrderViewSet)

app_name = 'order'

urlpatterns = [
    path('', include(router.urls)),
    path(
        'order/<int:pk>/status',
        views.OrderRetrieveUpdateStatusView.as_view({
            'get': 'retrieve',
            'put': 'update'
        }),
        name='retrieve-update-order-status'
    ),

    path(
        'detail/<int:pk>',
        views.DetailViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'

        }),
        name='update-order-details'
    ),

]
