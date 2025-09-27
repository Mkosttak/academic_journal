from django.urls import path
from django.shortcuts import redirect
from .views import (
    MakaleListView, MakaleDetailView, MakaleCreateView, MakalelerimView,
    MakaleUpdateView, MakaleDeleteView, check_author_view, MakaleEkleRedirectView,
    update_article_order, get_articles_for_ordering
)

urlpatterns = [
    # Public URLs - makale_list artık sayilar sayfasına yönlendiriliyor
    path('', lambda request: redirect('sayilar'), name='makale_list'),
    path('detay/<slug:slug>/', MakaleDetailView.as_view(), name='makale_detail'),
    path('makale-ekle/', MakaleEkleRedirectView.as_view(), name='makale_ekle_redirect'),
    path('yeni-ekle/', MakaleCreateView.as_view(), name='makale_ekle'),
    path('makalelerim/', MakalelerimView.as_view(), name='makalelerim'),
    path('duzenle/<slug:slug>/', MakaleUpdateView.as_view(), name='makale_duzenle'),
    path('sil/<slug:slug>/', MakaleDeleteView.as_view(), name='makale_sil'),
    path('check-author/', check_author_view, name='check_author'),
    
    # Admin sıralama URL'leri
    path('admin/siralama/<int:dergi_sayisi_id>/', get_articles_for_ordering, name='get_articles_for_ordering'),
    path('admin/siralama-guncelle/', update_article_order, name='update_article_order'),
]
