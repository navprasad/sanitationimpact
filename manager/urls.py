from django.conf.urls import include, url
from rest_framework import routers

from manager.views import ManagerViewSet

router = routers.DefaultRouter()
router.register(r'manager', ManagerViewSet)

urlpatterns = [
    # url(r'^sample/', sample.view, name='sample_name'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
