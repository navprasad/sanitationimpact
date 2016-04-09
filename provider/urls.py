from django.conf.urls import include, url
from rest_framework import routers

from provider.views import ProviderViewSet

router = routers.DefaultRouter()
router.register(r'provider', ProviderViewSet)

urlpatterns = [
    # url(r'^sample/', sample.view, name='sample_name'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
