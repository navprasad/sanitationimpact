from django.conf.urls import include, url
from rest_framework import routers

from manager.views import ManagerViewSet, ViewManagers, AddManager

router = routers.DefaultRouter()
router.register(r'manager', ManagerViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^view/$', ViewManagers.as_view(), name='view_managers'),
    url(r'^add/$', AddManager.as_view(), name='add_manager'),
]
