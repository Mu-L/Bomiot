import importlib.metadata
import importlib.util
import os
from os import listdir
from os.path import join, isdir, exists, isfile
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.views import serve
from django.views.static import serve as static_serve
from django.conf import settings
from bomiot.server.server import views
from bomiot.server.server.pkgcheck import pkg_check, cwd_check, ignore_pkg, ignore_cwd
from configparser import ConfigParser
from pathlib import Path
from django.urls import resolve, Resolver404
from bomiot.server.core.scheduler import sm
from bomiot.server.core.observer import ob
from bomiot.server.core.server_monitor import start_monitoring


def url_exists(url_data):
    try:
        resolve(url_data)
        return True
    except Resolver404:
        return False

def return_static(request, path, insecure=True, **kwargs):
    return serve(request, path, insecure, **kwargs)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.IndexTemplateView.as_view()),
    path('test/', views.test),
    path('bomiot_test/', views.bomiot_test),
    path('projectlist/', views.ProjectList),
    path('login/', views.logins, name='login'),
    path('logout/', views.logouts, name='logout'),
    path('checktoken/', views.check_token, name='check_token'),
    path('md/<str:mddocs>', views.mdurl, name='markdown'),
]

urlpatterns += [
    path('favicon.ico', views.favicon, name='favicon'),
    re_path('^css/.*$', views.statics, name='css'),
    re_path('^js/.*$', views.statics, name='js'),
    re_path('^assets/.*$', views.statics, name='assets'),
    re_path('^statics/.*$', views.statics, name='statics'),
    re_path('^fonts/.*$', views.statics, name='fonts'),
    re_path('^icons/.*$', views.statics, name='icons'),
    re_path(r'^static/(?P<path>.*)$', return_static, name='static'),
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += [
    path('.well-known/appspecific/com.chrome.devtools.json', views.google),
]

# Third-party / Django core apps that never carry project URLs to mount.
# Everything else (bomiot.*, greaterwms.*, discovered plugins) is a candidate.
_SKIP_URL_APPS = frozenset({
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_filters',
    'rest_framework',
    'django_apscheduler',
})

# Prefixes of project-local apps we want to auto-mount URLs for.
# (Matches the INSTALLED_APPS discovery source of truth: BASE bomiot.server.core
#  + runtime_discover_bomiot_apps discovered greaterwms.* packages.)
_APP_PREFIXES = ('bomiot.', 'greaterwms.')

_mounted_prefixes = set()

def _register_app_urls(app_path):
    """Include {app_path}.urls under /<last_segment>/ if the module exists."""
    if app_path in _SKIP_URL_APPS:
        return
    if not app_path.startswith(_APP_PREFIXES):
        return

    segments = app_path.split('.')
    if not segments:
        return
    url_prefix = segments[-1]
    if not url_prefix:
        return

    # Guard against duplicate prefix registration (different apps colliding
    # on the same last-segment name, or core being added twice).
    prefix_key = f'{url_prefix}/'
    if prefix_key in _mounted_prefixes:
        return
    _mounted_prefixes.add(prefix_key)

    include_path = f'{app_path}.urls'
    try:
        urls_module = importlib.import_module(include_path)
    except ImportError:
        # app has no urls.py — totally normal, skip silently
        return
    except Exception:
        import traceback
        traceback.print_exc()
        return

    if not hasattr(urls_module, 'urlpatterns'):
        return

    urlpatterns.append(
        path(prefix_key, include(include_path))
    )

# Mirror INSTALLED_APPS exactly: same order, same set of apps.
# (INSTALLED_APPS already incorporates CI-generated discovered_apps.py,
#  runtime_discover_bomiot_apps fallback, and _unique_preserve_order de-duplication.)
for _app in settings.INSTALLED_APPS:
    _register_app_urls(_app)

if os.environ.get('IS_LAN', 'false') == 'true':
    views.init_bomiot()