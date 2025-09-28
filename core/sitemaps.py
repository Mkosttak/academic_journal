from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from articles.models import Makale, DergiSayisi

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['anasayfa', 'sayilar', 'editorler', 'iletisim']

    def location(self, item):
        return reverse(item)

class MakaleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Makale.objects.filter(goster_makaleler_sayfasinda=True)

    def lastmod(self, obj):
        return obj.guncellenme_tarihi

    def location(self, obj):
        return f'/makaleler/detay/{obj.slug}/'

class DergiSayisiSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return DergiSayisi.objects.filter(yayinlandi_mi=True)

    def lastmod(self, obj):
        return obj.olusturulma_tarihi

    def location(self, obj):
        return f'/sayilar/{obj.slug}/'
