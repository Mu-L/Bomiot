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
    path('core/', include('bomiot.server.core.urls')),
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

project_path = join(settings.WORKING_SPACE, 'greaterwms')
exclude_dirs = {
    '__pycache__', 'static', 'media', 'templates', 'language',
    'migrations', 'tests', 'test', 'docs', 'documentation'
}

# Collect candidate app directories
url_candidates = []
if isdir(project_path):
    # Development environment: scan filesystem
    root_path = Path(project_path)
    url_candidates = [p.name for p in root_path.iterdir() if p.is_dir() and p.name not in exclude_dirs]
else:
    # Packaged environment: read from compiled registry
    try:
        from greaterwms._apps_registry import APPS
        url_candidates = [app for app in APPS if app not in exclude_dirs]
    except ImportError:
        pass

# Register URLs for each app
for app_name in url_candidates:
    try:
        include_path = f'greaterwms.{app_name}.urls'
        # Use importlib to verify module exists (works in both dev and packaged)
        urls_module = importlib.import_module(include_path)
        if not hasattr(urls_module, 'urlpatterns'):
            continue
        url_pattern = f'{app_name}/'
        if any(pattern.pattern.regex.pattern.startswith(url_pattern) for pattern in urlpatterns):
            continue
        urlpatterns.append(
            path(url_pattern, include(include_path))
        )
    except ImportError:
        continue
    except Exception:
        import traceback
        traceback.print_exc()
        continue

if os.environ.get('IS_LAN', 'false') == 'true':
    views.init_bomiot()