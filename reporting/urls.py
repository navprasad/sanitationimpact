from django.conf.urls import include, url
from rest_framework import routers

from reporting.views import RecordingViewSet, TicketViewSet

router = routers.DefaultRouter()
router.register(r'recording', RecordingViewSet)
router.register(r'ticket', TicketViewSet)

urlpatterns = [
    # url(r'^sample/', sample.view, name='sample_name'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
