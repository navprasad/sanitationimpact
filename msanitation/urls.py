from django.conf.urls import include, url

import administration.urls
import manager.urls
import provider.urls
import reporting.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^administration/', include(administration.urls)),
    url(r'^manager/', include(manager.urls)),
    url(r'^provider/', include(provider.urls)),
    url(r'^reporting/', include(reporting.urls)),
]
