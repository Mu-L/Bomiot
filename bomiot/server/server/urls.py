import importlib.util
import os
from django.urls import path, include, re_path
from django.contrib.staticfiles.views import serve
from django.views.static import serve as static_serve
from django.conf import settings
from bomiot.server.server import views
from django.urls import resolve, Resolver404
from bomiot.server.core.scheduler import sm
from bomiot.server.core.observer import ob
from bomiot.server.core.server_monitor import start_monitoring
import logging

logger = logging.getLogger(__name__)


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
    """Include {app_path}.urls under /<last_segment>/ if the module exists.
    Uses find_spec to avoid importing the module at discovery time.
    Guards include(...) because include will import the module and may raise.
    """
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

    # Guard against duplicate prefix registration
    prefix_key = f'{url_prefix}/'
    if prefix_key in _mounted_prefixes:
        return

    include_path = f'{app_path}.urls'

    # Existence check WITHOUT importing module (avoid executing top-level code)
    spec = importlib.util.find_spec(include_path)
    if spec is None:
        logger.debug("URLs module not resolvable for %s, skipping include", include_path)
        return

    # Now attempt to include (this may import the module); guard with try/except
    try:
        urlpatterns.append(path(prefix_key, include(include_path)))
        # record mounted prefix only after successful include
        _mounted_prefixes.add(prefix_key)
        logger.debug("Included URLs for %s at prefix %s", include_path, prefix_key)
    except Exception:
        logger.exception("Failed to include URLs for %s — skipping this app", include_path)
        # don't re-raise; continue with other apps

# Mirror INSTALLED_APPS exactly: same order, same set of apps.
for _app in settings.INSTALLED_APPS:
    _register_app_urls(_app)

if os.environ.get('IS_LAN', 'false') == 'true':
    views.init_bomiot()