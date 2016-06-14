from django.conf.urls import include, url
from rest_framework import routers

from administration.views import AdminViewSet, ProblemCategoryViewSet, ProblemViewSet, ToiletViewSet,\
    ViewManagers, AddManager, ViewManager, DeleteManager, EditManager,\
    ViewProviders, AddProvider, ViewProvider, DeleteProvider,\
    ViewToilets, AddToilet, DeleteToilet

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'problem-category', ProblemCategoryViewSet)
router.register(r'problem', ProblemViewSet)
router.register(r'toilet', ToiletViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^view_managers/$', ViewManagers.as_view(), name='view_managers'),
    url(r'^view_manager/(?P<manager_id>\d+)/$', ViewManager.as_view(), name='view_manager'),
    url(r'^add_manager/$', AddManager.as_view(), name='add_manager'),
    url(r'^edit_manager/(?P<manager_id>\d+)/$', EditManager.as_view(), name='edit_manager'),
    url(r'^delete_manager/(?P<manager_id>\d+)/$', DeleteManager.as_view(), name='delete_manager'),

    url(r'^view_providers/$', ViewProviders.as_view(), name='view_providers'),
    url(r'^view_provider/(?P<provider_id>\d+)/$', ViewProvider.as_view(), name='view_provider'),
    url(r'^add_provider/$', AddProvider.as_view(), name='add_provider'),
    url(r'^delete_provider/(?P<provider_id>\d+)/$', DeleteProvider.as_view(), name='delete_provider'),

    url(r'^view_toilets/$', ViewToilets.as_view(), name='view_toilets'),
    url(r'^add_toilet/$', AddToilet.as_view(), name='add_toilet'),
    url(r'^delete_toilet/(?P<toilet_id>\d+)/$', DeleteToilet.as_view(), name='delete_toilet'),
]
