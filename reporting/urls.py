from django.conf.urls import include, url
from rest_framework import routers

from reporting.views import RecordingViewSet, TicketViewSet, IsValidToilet, ReportProblem

router = routers.DefaultRouter()
router.register(r'recording', RecordingViewSet)
router.register(r'ticket', TicketViewSet)

urlpatterns = [
    url(r'^is_valid_toilet/$', IsValidToilet.as_view(), name='is_valid_toilet'),
    url(r'^report_problem/$', ReportProblem.as_view(), name='report_problem'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
