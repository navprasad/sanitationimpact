from django.conf.urls import include, url
from rest_framework import routers

from reporting.views import RecordingViewSet, TicketViewSet, IsValidToilet, IsValidProviderTicket, ReportProblem, \
    ReportFix, DownloadAudio, GetAudioURL

router = routers.DefaultRouter()
router.register(r'recording', RecordingViewSet)
router.register(r'ticket', TicketViewSet)

urlpatterns = [
    url(r'^api/is_valid_toilet/$', IsValidToilet.as_view(), name='is_valid_toilet'),
    url(r'^api/is_valid_provider_ticket/$', IsValidProviderTicket.as_view(), name='is_valid_provider_ticket'),
    url(r'^api/report_problem/$', ReportProblem.as_view(), name='report_problem'),
    url(r'^api/report_fix/$', ReportFix.as_view(), name='report_fix'),
    url(r'^api/download_audio/$', DownloadAudio.as_view(), name='download_audio'),
    url(r'^api/get_audio_url/$', GetAudioURL.as_view(), name='get_audio_url'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
