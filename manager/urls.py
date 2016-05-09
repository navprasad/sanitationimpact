from django.conf.urls import include, url
from rest_framework import routers

from manager.views import ManagerViewSet, ManagerProfile

router = routers.DefaultRouter()
router.register(r'manager', ManagerViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^(?P<pk>\d+)/$', ManagerProfile.as_view(), name='manager_profile'),
]
