"""
URL configuration for academic_journal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from articles.views import MakaleDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Kullanıcı işlemleriyle ilgili URL'leri 'users' uygulamasına yönlendir
    path('kullanici/', include('users.urls')),
    
    # Makalelerle ilgili URL'leri 'articles' uygulamasına yönlendir
    path('makaleler/', include('articles.urls')),
    
    # Dergi sayısı altında makale detayları için özel URL
    path('sayilar/<slug:dergi_slug>/<slug:makale_slug>/', MakaleDetailView.as_view(), name='makale_detail_with_journal'),
    
    # Diğer sayfalar (Anasayfa, Hakkında, İletişim vs.) için 'pages' uygulamasını kullan
    # 'pages' uygulamasındaki URL'leri ana dizinden çağıracağımız için path boş olacak
    path('dashboard/', include('dashboard.urls')),
    path('', include('pages.urls')),
]

# Geliştirme ortamında medya dosyalarını sunmak için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
