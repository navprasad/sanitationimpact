from django.conf.urls import include, url
from rest_framework import routers

from manager.views import ManagerViewSet, ManagerProfile, IsValidManager, IsValidManagerPinCode

router = routers.DefaultRouter()
router.register(r'manager', ManagerViewSet)

urlpatterns = [
    url(r'^api/is_valid_manager/$', IsValidManager.as_view(), name='is_valid_manager'),
    url(r'^api/is_valid_manager_pin_code/$', IsValidManagerPinCode.as_view(), name='is_valid_manager_pin_code'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^(?P<pk>\d+)/$', ManagerProfile.as_view(), name='manager_profile'),
]
