from django.conf.urls import include, url
from rest_framework import routers

from administration.views import AdminViewSet, ProblemCategoryViewSet, ProblemViewSet, ToiletViewSet, TicketView,\
    ToiletView, ProblemView, UserView, ViewManagers, AddManager, ViewProviders, AddProvider, ViewManager

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'problem-category', ProblemCategoryViewSet)
router.register(r'problem', ProblemViewSet)
router.register(r'toilet', ToiletViewSet)

urlpatterns = [
    # url(r'^sample/', sample.view, name='sample_name'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^ticket/$', TicketView.as_view(), name='ticket_view'),
    url(r'^toilet/$', ToiletView.as_view(), name='toilet_view'),
    url(r'^problem/$', ProblemView.as_view(), name='problem_view'),
    url(r'^user/$', UserView.as_view(), name='user_view'),

    url(r'^view_managers/$', ViewManagers.as_view(), name='view_managers'),
    url(r'^view_manager/(?P<manager_id>\d+)/$', ViewManager.as_view(), name='view_manager'),
    url(r'^add_manager/$', AddManager.as_view(), name='add_manager'),
    url(r'^view_providers/$', ViewProviders.as_view(), name='view_providers'),
    url(r'^add_provider/$', AddProvider.as_view(), name='add_provider'),
]
