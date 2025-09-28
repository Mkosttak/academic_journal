from django.urls import path
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from . import views

@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /media/",
        "",
        "Sitemap: {}/sitemap.xml".format(request.build_absolute_uri('/')),
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('', views.MonitoringDashboardView.as_view(), name='monitoring_dashboard'),
    path('api/', views.monitoring_api, name='monitoring_api'),
]
