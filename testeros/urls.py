from django.conf.urls import url
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^$', views.home, name='home'),
    url(r'^.*/ajax/$', views.ajax_view, name='ajax'),
    url(r'^isocompare/$', views.isocompare, name='isocompare'),
    url(r'^packages/$', views.packages, name='packages'),
    url(r'^stapelip/$', views.stapelip, name='stapelip'),

    url(r'^stapelip/download/$', views.download, name='download'),
    url(r'^tests/download/$', views.download, name='download'),
    url(r'^testing/download/$', views.download, name='download'),

    url(r'^tests/$', views.tests, name='tests'),
    url(r'^scanner/$', views.scanner, name='scanner'),

    url(r'^testing/$', views.testing, name='testing'),
    url('^testing/test/(?P<journal_id>\d+)/$', views.testing_test, name='testing_test'),
    url(r'^repomanager/$', views.repomanager, name='repomanager'),
    url(r'^repoinfo/$', views.repoinfo, name='repoinfo'),
    url(r'^repolog/$', views.repolog, name='repolog'),

    url(r'^buildiso/$', views.buildiso, name='buildiso'),
    url(r'^buildisolog/$', views.buildisolog, name='buildisolog'),


    url(r'^settings/$', views.settings, name='settings'),
]
