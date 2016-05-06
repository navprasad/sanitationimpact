from django.conf.urls import include, url
from django.conf.urls.static import static
from msanitation import settings

import administration.urls
import manager.urls
import provider.urls
import reporting.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from msanitation.views import Login, DashBoard, LogOut

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', LogOut.as_view(), name='logout'),
    url(r'^dashboard/$', DashBoard.as_view(), name='dashboard'),
    url(r'^administration/', include(administration.urls)),
    url(r'^manager/', include(manager.urls)),
    url(r'^provider/', include(provider.urls)),
    url(r'^reporting/', include(reporting.urls)),
    url(r'^$', Login.as_view(), name='login_'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
