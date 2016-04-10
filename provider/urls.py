from django.conf.urls import include, url
from rest_framework import routers

from provider.views import IsValidProvider, IsValidProviderPinCode, ProviderViewSet

router = routers.DefaultRouter()
router.register(r'provider', ProviderViewSet)

urlpatterns = [
    url(r'^is_valid_provider/$', IsValidProvider.as_view(), name='is_valid_provider'),
    url(r'^is_valid_provider_pin_code/$', IsValidProviderPinCode.as_view(), name='is_valid_provider_pin_code'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
